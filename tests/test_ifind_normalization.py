from __future__ import annotations

import json
import os
import stat
import tempfile
from pathlib import Path

import pytest

from ashare_premarket.providers.ifind_http import IfindProviderError
from ashare_premarket.providers.ifind_normalization import (
    IfindNormalizedBatch,
    flatten_ifind_tables,
    normalize_ifind_payload,
    write_ifind_normalized_bundle,
)


ROOT = Path(__file__).resolve().parents[1]


def _daily_payload() -> dict[str, object]:
    return {
        "errorcode": 0,
        "tables": [
            {
                "thscode": ["000333.SZ", "600036.SH"],
                "time": ["2026-07-01", "2026-07-01"],
                "open": [75.0, 42.0],
                "high": [77.0, 43.0],
                "low": [74.0, 41.5],
                "close": [76.0, 42.5],
                "volume": [1000, 2000],
                "ignored_vendor_field": ["never-persist", "never-persist"],
            }
        ],
    }


def test_ifind_table_explosion_supports_vector_and_scalar_fields() -> None:
    rows = flatten_ifind_tables(
        {"tables": [{"thscode": ["000333.SZ", "600036.SH"], "unit": "CNY"}]}
    )
    assert rows == [
        {"thscode": "000333.SZ", "unit": "CNY"},
        {"thscode": "600036.SH", "unit": "CNY"},
    ]


def test_ifind_daily_normalization_is_pit_safe_deterministic_and_drops_unmapped_raw_fields() -> (
    None
):
    kwargs = {
        "module_id": "daily_market_and_calendar",
        "payload": _daily_payload(),
        "field_mapping": {
            "thscode": "symbol",
            "time": "trade_date",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
        },
        "source_function": "cmd_history_quotation",
        "available_at": "2026-07-02T00:30:00+08:00",
        "decision_cutoff": "2026-07-02T08:00:00+08:00",
        "request_descriptor": {
            "codes": ["000333.SZ", "600036.SH"],
            "indicator_set": "daily_ohlcv_v1",
        },
        "quality_flags": ["BOUNDED_FIXTURE", "ENTITLEMENT_NOT_LIVE_VALIDATED"],
        "static_fields": {"adjustment_mode": "qfq"},
    }
    first = normalize_ifind_payload(**kwargs)
    second = normalize_ifind_payload(**kwargs)

    assert first == second
    assert first.normalized_checksum == second.normalized_checksum
    assert [row["symbol"] for row in first.rows] == ["000333.SZ", "600036.SH"]
    assert first.rows[0]["available_at"] == "2026-07-01T16:30:00Z"
    assert "ignored_vendor_field" not in first.rows[0]
    assert first.rows[0]["provider_id"] == "ifind"
    assert first.rows[0]["license_storage_class"] == "paid_provider_local_only"
    assert first.manifest()["raw_payload_persisted"] is False


def test_ifind_normalizer_rejects_post_cutoff_rows_invalid_ohlc_and_duplicates() -> (
    None
):
    common = {
        "module_id": "daily_market_and_calendar",
        "field_mapping": {
            "thscode": "symbol",
            "time": "trade_date",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
        },
        "source_function": "cmd_history_quotation",
        "request_descriptor": {"probe": "fixture"},
        "static_fields": {"adjustment_mode": "qfq"},
    }
    with pytest.raises(IfindProviderError, match="decision cutoff"):
        normalize_ifind_payload(
            **common,
            payload=_daily_payload(),
            available_at="2026-07-02T09:00:00+08:00",
            decision_cutoff="2026-07-02T08:00:00+08:00",
        )

    invalid = _daily_payload()
    invalid["tables"][0]["high"][0] = 70.0  # type: ignore[index]
    with pytest.raises(IfindProviderError, match="OHLC"):
        normalize_ifind_payload(
            **common,
            payload=invalid,
            available_at="2026-07-02T00:00:00Z",
            decision_cutoff="2026-07-02T08:00:00Z",
        )

    duplicate = _daily_payload()
    duplicate["tables"][0]["thscode"][1] = "000333.SZ"  # type: ignore[index]
    with pytest.raises(IfindProviderError, match="duplicate primary keys"):
        normalize_ifind_payload(
            **common,
            payload=duplicate,
            available_at="2026-07-02T00:00:00Z",
            decision_cutoff="2026-07-02T08:00:00Z",
        )


def test_ifind_bundle_writer_is_external_normalized_and_immutable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Keep this fixture outside the repository even when a validation profile
    # places pytest's --basetemp under outputs/local. The production contract
    # intentionally rejects every paid-data root beneath the Git checkout.
    with tempfile.TemporaryDirectory(
        prefix="ashare-ifind-paid-data-"
    ) as temporary_directory:
        data_root = (Path(temporary_directory) / "paid-data").resolve()
        monkeypatch.setenv("ASHARE_PREMARKET_DATA_ROOT", str(data_root))
        batch = normalize_ifind_payload(
            module_id="daily_market_and_calendar",
            payload=_daily_payload(),
            field_mapping={"thscode": "symbol", "time": "trade_date", "close": "close"},
            source_function="cmd_history_quotation",
            available_at="2026-07-02T00:00:00Z",
            decision_cutoff="2026-07-02T08:00:00Z",
            request_descriptor={"probe": "fixture"},
            static_fields={"adjustment_mode": "qfq"},
        )
        manifest_path = write_ifind_normalized_bundle(ROOT, batch, "fixture-daily-v1")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        rows_text = (manifest_path.parent / "rows.jsonl").read_text(encoding="utf-8")

        assert data_root in manifest_path.parents
        assert manifest["row_count"] == 2
        assert manifest["raw_payload_persisted"] is False
        assert manifest["credentials_persisted"] is False
        assert "ignored_vendor_field" not in rows_text
        assert stat.S_IMODE(os.stat(manifest_path.parent).st_mode) == 0o700
        assert stat.S_IMODE(os.stat(manifest_path).st_mode) == 0o600
        assert (
            stat.S_IMODE(os.stat(manifest_path.parent / "rows.jsonl").st_mode) == 0o600
        )
        with pytest.raises(IfindProviderError, match="cannot be overwritten"):
            write_ifind_normalized_bundle(ROOT, batch, "fixture-daily-v1")


def test_ifind_normalizer_enforces_canonical_field_and_temporal_contracts() -> None:
    common = {
        "module_id": "pit_fundamentals_and_valuation",
        "payload": {
            "tables": [
                {
                    "thscode": ["000333.SZ"],
                    "metric": ["roe"],
                    "report_period": ["2026-03-31"],
                    "announcement_date": ["2026-04-30"],
                    "revision_at": ["2026-04-30T08:00:00Z"],
                    "value": [18.5],
                }
            ]
        },
        "field_mapping": {
            "thscode": "symbol",
            "metric": "metric_id",
            "report_period": "report_period",
            "announcement_date": "announcement_date",
            "revision_at": "revision_at",
            "value": "value",
        },
        "source_function": "basic_data_service",
        "available_at": "2026-04-30T09:00:00Z",
        "decision_cutoff": "2026-04-30T10:00:00Z",
        "request_descriptor": {"indicator_set": "pit_fundamentals_v1"},
        "static_fields": {"unit": "percent", "currency": "NOT_APPLICABLE"},
    }
    batch = normalize_ifind_payload(**common)
    assert batch.rows[0]["value"] == 18.5
    assert batch.rows[0]["data_cutoff"] == "2026-04-30T10:00:00Z"
    assert batch.rows[0]["normalized_checksum"] == batch.normalized_checksum

    invalid_mapping = dict(common)
    invalid_mapping["field_mapping"] = {
        **common["field_mapping"],
        "value": "raw_provider_blob",
    }
    with pytest.raises(IfindProviderError, match="canonical module schema"):
        normalize_ifind_payload(**invalid_mapping)

    future_revision = json.loads(json.dumps(common["payload"]))
    future_revision["tables"][0]["revision_at"][0] = "2026-04-30T09:30:00Z"
    with pytest.raises(
        IfindProviderError, match="revision_at is after provider availability"
    ):
        normalize_ifind_payload(**{**common, "payload": future_revision})

    midnight_boundary = json.loads(json.dumps(common["payload"]))
    midnight_boundary["tables"][0]["revision_at"][0] = "2026-04-29T11:10:00-05:00"
    boundary = normalize_ifind_payload(
        **{
            **common,
            "payload": midnight_boundary,
            "available_at": "2026-04-29T11:30:00-05:00",
            "decision_cutoff": "2026-04-30T01:00:00Z",
        }
    )
    assert boundary.rows[0]["announcement_date"] == "2026-04-30"


def test_ifind_nested_schema_drift_returns_stable_type_failure() -> None:
    with pytest.raises(IfindProviderError) as exc:
        normalize_ifind_payload(
            module_id="corporate_events_and_announcements",
            payload={
                "tables": [
                    {
                        "thscode": ["000333.SZ"],
                        "event_id": [["unexpected", "nested"]],
                        "event_type": ["announcement"],
                        "ctime": ["2026-07-02T09:00:00+08:00"],
                    }
                ]
            },
            field_mapping={
                "thscode": "symbol",
                "event_id": "event_id",
                "event_type": "event_type",
                "ctime": "publication_time",
            },
            source_function="report_query",
            available_at="2026-07-02T09:05:00+08:00",
            decision_cutoff="2026-07-02T10:00:00+08:00",
            request_descriptor={"report_type": "901"},
        )
    assert exc.value.failure_code == "IFIND_COLUMN_TYPE_MISMATCH"


def test_ifind_bundle_writer_rejects_untrusted_module_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ASHARE_PREMARKET_DATA_ROOT", str(tmp_path / "paid-data"))
    forged = IfindNormalizedBatch(
        module_id="../../escape",
        source_function="cmd_history_quotation",
        request_digest="0" * 64,
        rows=(),
        normalized_checksum="0" * 64,
    )
    with pytest.raises(IfindProviderError, match="outside the governed data contract"):
        write_ifind_normalized_bundle(ROOT, forged, "forged-v1")


def test_ifind_calendar_grain_timezone_and_numeric_contracts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calendar = normalize_ifind_payload(
        module_id="daily_market_and_calendar",
        payload={"tables": [{"time": ["2026-07-01", "2026-07-02"]}]},
        field_mapping={"time": "trade_date"},
        static_fields={"market_code": "212001", "is_trading_day": True},
        source_function="get_trade_dates",
        available_at="2026-07-02T18:00:00+08:00",
        decision_cutoff="2026-07-03T08:00:00+08:00",
        request_descriptor={"market_code": "212001", "offset": -1},
    )
    assert [row["trade_date"] for row in calendar.rows] == ["2026-07-01", "2026-07-02"]
    assert all(
        "symbol" not in row and "adjustment_mode" not in row for row in calendar.rows
    )

    with pytest.raises(IfindProviderError, match="TIMEZONE_REQUIRED"):
        normalize_ifind_payload(
            module_id="corporate_events_and_announcements",
            payload={
                "tables": [
                    {
                        "thscode": ["000333.SZ"],
                        "event_id": ["e1"],
                        "event_type": ["announcement"],
                        "ctime": ["2026-07-02 09:00:00"],
                    }
                ]
            },
            field_mapping={
                "thscode": "symbol",
                "event_id": "event_id",
                "event_type": "event_type",
                "ctime": "publication_time",
            },
            source_function="report_query",
            available_at="2026-07-02T09:05:00+08:00",
            decision_cutoff="2026-07-02T10:00:00+08:00",
            request_descriptor={"report_type": "901"},
        )

    localized = normalize_ifind_payload(
        module_id="corporate_events_and_announcements",
        payload={
            "tables": [
                {
                    "thscode": ["000333.SZ"],
                    "event_id": ["e1"],
                    "event_type": ["announcement"],
                    "ctime": ["2026-07-02 09:00:00"],
                }
            ]
        },
        field_mapping={
            "thscode": "symbol",
            "event_id": "event_id",
            "event_type": "event_type",
            "ctime": "publication_time",
        },
        source_function="report_query",
        available_at="2026-07-02T09:05:00+08:00",
        decision_cutoff="2026-07-02T10:00:00+08:00",
        request_descriptor={"report_type": "901"},
        naive_timezone="Asia/Shanghai",
    )
    assert localized.rows[0]["publication_time"] == "2026-07-02T01:00:00Z"

    invalid_value = {
        "tables": [
            {
                "series": ["macro-1"],
                "period": ["2026-06-30"],
                "release": ["2026-07-01"],
                "revision": ["2026-07-01T01:00:00Z"],
                "value": ["inf"],
            }
        ]
    }
    with pytest.raises(IfindProviderError, match="must be finite"):
        normalize_ifind_payload(
            module_id="macro_and_edb",
            payload=invalid_value,
            field_mapping={
                "series": "series_id",
                "period": "observation_period",
                "release": "release_date",
                "revision": "revision_at",
                "value": "value",
            },
            static_fields={"unit": "index"},
            source_function="edb_service",
            available_at="2026-07-01T02:00:00Z",
            decision_cutoff="2026-07-01T03:00:00Z",
            request_descriptor={"series": "macro-1"},
        )

    monkeypatch.delenv("ASHARE_PREMARKET_DATA_ROOT", raising=False)
    with pytest.raises(IfindProviderError, match="explicit external"):
        write_ifind_normalized_bundle(ROOT, calendar, "calendar-v1")


def test_ifind_industry_membership_and_share_domains_fail_closed() -> None:
    with pytest.raises(IfindProviderError, match="effective_from is after"):
        normalize_ifind_payload(
            module_id="industry_and_constituents",
            payload={
                "tables": [
                    {
                        "thscode": ["000333.SZ"],
                        "industry": ["CI005001"],
                        "version": ["citics-v1"],
                        "start": ["2026-07-10"],
                        "end": ["9999-12-31"],
                    }
                ]
            },
            field_mapping={
                "thscode": "symbol",
                "industry": "industry_code",
                "version": "classification_version",
                "start": "effective_from",
                "end": "effective_to",
            },
            source_function="data_pool",
            available_at="2026-07-01T10:00:00+08:00",
            decision_cutoff="2026-07-02T08:00:00+08:00",
            request_descriptor={"classification": "citics-v1"},
        )

    with pytest.raises(IfindProviderError, match="free-float shares exceed"):
        normalize_ifind_payload(
            module_id="security_master",
            payload={
                "tables": [
                    {
                        "thscode": ["000333.SZ"],
                        "asof": ["2026-07-01"],
                        "free_float": [120.0],
                        "float": [100.0],
                        "total": [200.0],
                    }
                ]
            },
            field_mapping={
                "thscode": "symbol",
                "asof": "as_of_date",
                "free_float": "free_float_shares",
                "float": "float_shares",
                "total": "total_shares",
            },
            source_function="basic_data_service",
            available_at="2026-07-01T18:00:00+08:00",
            decision_cutoff="2026-07-02T08:00:00+08:00",
            request_descriptor={"indicator_set": "security_master_v1"},
        )

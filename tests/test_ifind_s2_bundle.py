from __future__ import annotations

import hashlib
import json
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Callable

import pytest

from ashare_premarket.providers.ifind_s2 import (
    IFIND_S2_ACCEPTANCE_STATE,
    IFIND_S2_STAGE_ID,
    ifind_s2_request_digest,
)
from ashare_premarket.providers.ifind_s2_bundle import (
    IFIND_S2_BUNDLE_ROW_COUNT,
    load_ifind_s2_accepted_bundle,
)


ROOT = Path(__file__).resolve().parents[1]
BUNDLE_ID = "ifind-s2-20260812-test-v01"
DECISION_TIMESTAMP = "2026-07-10T08:00:00Z"
CUTOFF_DATE = "2026-07-10"
SYMBOLS = ("002475.SZ", "600487.SH")
COMPANIES = {"002475.SZ": "立讯精密", "600487.SH": "亨通光电"}


def _governed_dates() -> list[str]:
    current = date.fromisoformat(CUTOFF_DATE)
    values = []
    while len(values) < 120:
        if current.weekday() < 5:
            values.append(current.isoformat())
        current -= timedelta(days=1)
    return list(reversed(values))


def _digest_json(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _finalize_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], str]:
    checksum_rows = []
    for row in rows:
        value = dict(row)
        value.pop("normalized_checksum", None)
        checksum_rows.append(value)
    checksum = _digest_json(checksum_rows)
    finalized = [{**row, "normalized_checksum": checksum} for row in checksum_rows]
    return finalized, checksum


def _security_rows(symbol: str) -> list[dict[str, Any]]:
    return [
        {
            "symbol": symbol,
            "as_of_date": CUTOFF_DATE,
            "listing_date": "2010-09-15" if symbol == "002475.SZ" else "2003-08-22",
            "entity_name": COMPANIES[symbol],
            "trading_status": "正常交易",
            "total_shares": 7737819806.0,
            "float_shares": 7600000000.0,
            "industry_name": "电子",
            "provider_id": "ifind",
            "source_function": "get_stock_info",
            "request_digest": ifind_s2_request_digest("get_stock_info", symbol),
            "schema_version": "ifind-normalized-v1",
            "available_at": "2026-07-10T07:00:00Z",
            "data_cutoff": DECISION_TIMESTAMP,
            "license_storage_class": "paid_provider_local_only",
            "quality_flags": "S2_TYPED_PROVIDER_SCHEMA",
        }
    ]


def _market_rows(symbol: str) -> list[dict[str, Any]]:
    governed_dates = _governed_dates()
    return [
        {
            "symbol": symbol,
            "trade_date": trade_date,
            "open": 10.0,
            "high": 11.0,
            "low": 9.0,
            "close": 10.5,
            "volume": 1000.0,
            "amount": 10500.0,
            "turnover": 1.2,
            "adjustment_mode": "qfq",
            "provider_id": "ifind",
            "source_function": "get_stock_performance",
            "request_digest": ifind_s2_request_digest(
                "get_stock_performance", symbol, cutoff_date=CUTOFF_DATE
            ),
            "schema_version": "ifind-normalized-v1",
            "available_at": "2026-07-10T07:00:00Z",
            "data_cutoff": DECISION_TIMESTAMP,
            "license_storage_class": "paid_provider_local_only",
            "quality_flags": "GOVERNED_CALENDAR_ALIGNED;S2_TYPED_PROVIDER_SCHEMA",
        }
        for trade_date in governed_dates
    ]


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(
            json.dumps(
                row,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )
    os.chmod(path, 0o600)


def _write_manifest(fixture: dict[str, Any]) -> None:
    manifest_path = fixture["bundle_root"] / "manifest.json"
    manifest_path.write_text(
        json.dumps(fixture["manifest"], ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    os.chmod(manifest_path, 0o600)
    fixture["status"]["bundle_manifest_sha256"] = _sha256(manifest_path)


def _accepted_bundle(tmp_path: Path) -> dict[str, Any]:
    repository_root = (tmp_path / "fixture-repository").resolve()
    calendar_path = repository_root / "configs/project/trading_calendar.csv"
    calendar_path.parent.mkdir(parents=True)
    calendar_path.write_text(
        "date,is_trading_day,session_note\n"
        + "".join(f"{value},true,fixture\n" for value in _governed_dates()),
        encoding="utf-8",
    )
    data_root = (tmp_path / "licensed-data").resolve()
    bundle_root = data_root / "normalized" / "ifind" / "s2_acceptance" / BUNDLE_ID
    bundle_root.mkdir(parents=True)
    os.chmod(bundle_root, 0o700)
    artifacts = []
    for symbol in SYMBOLS:
        for module_id, build_rows in (
            ("security_master", _security_rows),
            ("daily_market_and_calendar", _market_rows),
        ):
            rows, normalized_checksum = _finalize_rows(build_rows(symbol))
            file_name = f"{module_id}__{symbol.replace('.', '_')}.jsonl"
            path = bundle_root / file_name
            _write_jsonl(path, rows)
            artifacts.append(
                {
                    "file": file_name,
                    "module_id": module_id,
                    "symbol": symbol,
                    "provider_id": "ifind",
                    "source_function": (
                        "get_stock_info"
                        if module_id == "security_master"
                        else "get_stock_performance"
                    ),
                    "schema_version": "ifind-normalized-v1",
                    "license_storage_class": "paid_provider_local_only",
                    "request_digest": rows[0]["request_digest"],
                    "row_count": len(rows),
                    "symbol_count": 1,
                    "date_min": (
                        rows[0]["as_of_date"]
                        if module_id == "security_master"
                        else rows[0]["trade_date"]
                    ),
                    "date_max": (
                        rows[-1]["as_of_date"]
                        if module_id == "security_master"
                        else rows[-1]["trade_date"]
                    ),
                    "normalized_checksum": normalized_checksum,
                    "file_sha256": _sha256(path),
                    "raw_payload_persisted": False,
                    "credentials_persisted": False,
                    "recommendation_outputs_created": False,
                    "trading_outputs_created": False,
                }
            )
    fixture: dict[str, Any] = {
        "repository_root": repository_root,
        "data_root": data_root,
        "bundle_root": bundle_root,
        "manifest": {
            "bundle_id": BUNDLE_ID,
            "provider_id": "ifind",
            "stage_id": IFIND_S2_STAGE_ID,
            "acceptance_state": IFIND_S2_ACCEPTANCE_STATE,
            "license_storage_class": "paid_provider_local_only",
            "symbols": list(SYMBOLS),
            "data_call_count": 4,
            "retries_per_request": 0,
            "decision_timestamp": DECISION_TIMESTAMP,
            "cutoff_date": CUTOFF_DATE,
            "raw_payload_persisted": False,
            "credentials_persisted": False,
            "artifacts": artifacts,
        },
        "status": {
            "status": "PASS",
            "acceptance_state": IFIND_S2_ACCEPTANCE_STATE,
            "data_call_count": 4,
            "normalized_row_count": IFIND_S2_BUNDLE_ROW_COUNT,
            "bundle_id": BUNDLE_ID,
            "bundle_persisted": True,
            "live_handshake_verified": True,
            "input_schemas_verified": True,
            "provider_schema_accepted": True,
            "canonical_accepted": True,
            "raw_payload_persisted": False,
            "credential_exposed": False,
        },
    }
    _write_manifest(fixture)
    return fixture


def _descriptor(fixture: dict[str, Any], module_id: str, symbol: str) -> dict[str, Any]:
    return next(
        value
        for value in fixture["manifest"]["artifacts"]
        if value["module_id"] == module_id and value["symbol"] == symbol
    )


def _reseal_artifact(
    fixture: dict[str, Any],
    module_id: str,
    symbol: str,
    mutate: Callable[[list[dict[str, Any]]], None],
    *,
    recompute_normalized_checksum: bool = True,
) -> None:
    descriptor = _descriptor(fixture, module_id, symbol)
    path = fixture["bundle_root"] / descriptor["file"]
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    mutate(rows)
    if recompute_normalized_checksum:
        rows, checksum = _finalize_rows(rows)
        descriptor["normalized_checksum"] = checksum
    date_field = "as_of_date" if module_id == "security_master" else "trade_date"
    dates = sorted({str(row[date_field]) for row in rows})
    descriptor["date_min"] = dates[0]
    descriptor["date_max"] = dates[-1]
    _write_jsonl(path, rows)
    descriptor["file_sha256"] = _sha256(path)
    _write_manifest(fixture)


def _load(fixture: dict[str, Any]):
    return load_ifind_s2_accepted_bundle(
        fixture["repository_root"],
        fixture["status"],
        environ={"ASHARE_PREMARKET_DATA_ROOT": str(fixture["data_root"])},
    )


def test_loads_only_fully_anchored_accepted_bundle(tmp_path: Path) -> None:
    fixture = _accepted_bundle(tmp_path)

    result = _load(fixture)

    assert result.accepted is True
    assert result.safe_status["normalized_row_count"] == 242
    assert result.safe_status["artifact_count"] == 4
    assert result.safe_status["symbols"] == list(SYMBOLS)
    assert result.safe_status["canonical_accepted"] is True
    assert result.safe_status["network_accessed"] is False
    assert result.safe_status["keychain_accessed"] is False
    assert len(result.rows) == 242
    assert len(result.rows_for_module("security_master")) == 2
    assert len(result.rows_for_module("daily_market_and_calendar")) == 240
    assert {
        row["adjustment_mode"]
        for row in result.rows_for_module("daily_market_and_calendar")
    } == {"qfq"}


def test_missing_explicit_data_root_fails_closed(tmp_path: Path) -> None:
    fixture = _accepted_bundle(tmp_path)

    result = load_ifind_s2_accepted_bundle(ROOT, fixture["status"], environ={})

    assert result.rows == ()
    assert result.safe_status["status"] == "BLOCKED"
    assert result.safe_status["failure_code"] == "IFIND_STORAGE_ROOT_ENV_REQUIRED"
    assert result.safe_status["normalized_row_count"] == 0


def test_blocked_status_never_reads_a_bundle(tmp_path: Path) -> None:
    fixture = _accepted_bundle(tmp_path)
    fixture["status"].update(
        {
            "status": "BLOCKED",
            "canonical_accepted": False,
            "provider_schema_accepted": False,
        }
    )

    result = load_ifind_s2_accepted_bundle(ROOT, fixture["status"], environ={})

    assert result.rows == ()
    assert result.safe_status["failure_code"] == "IFIND_S2_BUNDLE_STATUS_NOT_ACCEPTED"
    assert result.safe_status["bundle_id"] is None


def test_data_root_inside_repository_is_rejected(tmp_path: Path) -> None:
    fixture = _accepted_bundle(tmp_path)

    result = load_ifind_s2_accepted_bundle(
        tmp_path,
        fixture["status"],
        environ={"ASHARE_PREMARKET_DATA_ROOT": str(fixture["data_root"])},
    )

    assert result.rows == ()
    assert result.safe_status["failure_code"] == "IFIND_STORAGE_POLICY_VIOLATION"


def test_manifest_anchor_and_artifact_hash_tampering_fail_closed(
    tmp_path: Path,
) -> None:
    fixture = _accepted_bundle(tmp_path)
    fixture["status"]["bundle_manifest_sha256"] = "0" * 64
    result = _load(fixture)
    assert result.rows == ()
    assert (
        result.safe_status["failure_code"] == "IFIND_S2_BUNDLE_MANIFEST_HASH_MISMATCH"
    )

    fixture = _accepted_bundle(tmp_path / "second")
    descriptor = _descriptor(fixture, "security_master", "002475.SZ")
    path = fixture["bundle_root"] / descriptor["file"]
    with path.open("ab") as handle:
        handle.write(b" ")
    result = _load(fixture)
    assert result.rows == ()
    assert (
        result.safe_status["failure_code"] == "IFIND_S2_BUNDLE_ARTIFACT_HASH_MISMATCH"
    )


def test_normalized_checksum_tampering_fails_even_when_transport_is_resealed(
    tmp_path: Path,
) -> None:
    fixture = _accepted_bundle(tmp_path)

    _reseal_artifact(
        fixture,
        "daily_market_and_calendar",
        "002475.SZ",
        lambda rows: rows[0].__setitem__("close", 10.25),
        recompute_normalized_checksum=False,
    )
    result = _load(fixture)

    assert result.rows == ()
    assert (
        result.safe_status["failure_code"]
        == "IFIND_S2_BUNDLE_NORMALIZED_CHECKSUM_MISMATCH"
    )


def test_resealed_non_governed_calendar_is_rejected(tmp_path: Path) -> None:
    fixture = _accepted_bundle(tmp_path)
    first = date.fromisoformat(_market_rows(SYMBOLS[0])[0]["trade_date"])
    replacement = first - timedelta(days=1)
    while replacement.weekday() < 5:
        replacement -= timedelta(days=1)

    for symbol in SYMBOLS:
        _reseal_artifact(
            fixture,
            "daily_market_and_calendar",
            symbol,
            lambda rows, value=replacement.isoformat(): rows[0].__setitem__(
                "trade_date", value
            ),
        )

    result = _load(fixture)

    assert result.rows == ()
    assert result.safe_status["failure_code"] == "IFIND_S2_BUNDLE_CALENDAR_MISMATCH"


def test_resealed_request_digest_and_mixed_availability_are_rejected(
    tmp_path: Path,
) -> None:
    fixture = _accepted_bundle(tmp_path)
    descriptor = _descriptor(fixture, "daily_market_and_calendar", "002475.SZ")
    arbitrary_digest = "0" * 64
    _reseal_artifact(
        fixture,
        "daily_market_and_calendar",
        "002475.SZ",
        lambda rows: [
            row.__setitem__("request_digest", arbitrary_digest) for row in rows
        ],
    )
    descriptor["request_digest"] = arbitrary_digest
    _write_manifest(fixture)

    result = _load(fixture)
    assert result.rows == ()
    assert result.safe_status["failure_code"] == (
        "IFIND_S2_BUNDLE_ARTIFACT_CONTRACT_MISMATCH"
    )

    fixture = _accepted_bundle(tmp_path / "availability")
    _reseal_artifact(
        fixture,
        "daily_market_and_calendar",
        "002475.SZ",
        lambda rows: rows[0].__setitem__("available_at", "2026-07-10T06:59:00Z"),
    )
    result = _load(fixture)
    assert result.rows == ()
    assert result.safe_status["failure_code"] == "IFIND_S2_BUNDLE_ROW_TIME_INVALID"


@pytest.mark.parametrize(
    ("corruption", "failure_code"),
    [
        ("qfq", "IFIND_S2_BUNDLE_ROW_CONTENT_INVALID"),
        ("primary_key", "IFIND_S2_BUNDLE_PRIMARY_KEY_INVALID"),
        ("schema", "IFIND_S2_BUNDLE_ROW_SCHEMA_MISMATCH"),
        ("license", "IFIND_S2_BUNDLE_ROW_CONTRACT_MISMATCH"),
    ],
)
def test_schema_qfq_primary_key_and_license_corruption_fail_closed(
    tmp_path: Path, corruption: str, failure_code: str
) -> None:
    fixture = _accepted_bundle(tmp_path)

    def mutate(rows: list[dict[str, Any]]) -> None:
        if corruption == "qfq":
            rows[0]["adjustment_mode"] = "hfq"
        elif corruption == "primary_key":
            rows[-1]["trade_date"] = rows[-2]["trade_date"]
        elif corruption == "schema":
            rows[0].pop("provider_id")
        else:
            rows[0]["license_storage_class"] = "unreviewed"

    _reseal_artifact(
        fixture,
        "daily_market_and_calendar",
        "002475.SZ",
        mutate,
    )
    result = _load(fixture)

    assert result.rows == ()
    assert result.safe_status["status"] == "BLOCKED"
    assert result.safe_status["failure_code"] == failure_code
    assert result.safe_status["normalized_row_count"] == 0


def test_artifact_symlink_is_rejected(tmp_path: Path) -> None:
    fixture = _accepted_bundle(tmp_path)
    descriptor = _descriptor(fixture, "security_master", "002475.SZ")
    artifact = fixture["bundle_root"] / descriptor["file"]
    outside = fixture["data_root"] / "outside.jsonl"
    outside.write_bytes(artifact.read_bytes())
    os.chmod(outside, 0o600)
    artifact.unlink()
    try:
        artifact.symlink_to(outside)
    except (NotImplementedError, OSError):
        pytest.skip("symlinks are unavailable on this platform")

    result = _load(fixture)

    assert result.rows == ()
    assert result.safe_status["failure_code"] == "IFIND_S2_BUNDLE_SYMLINK_REJECTED"

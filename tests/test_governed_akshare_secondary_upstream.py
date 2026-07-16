from __future__ import annotations

import json
import csv
import hashlib
from copy import deepcopy
from pathlib import Path

import pandas as pd
import pytest

from ashare_premarket.core.io import write_csv, write_json
from ashare_premarket.daily_refresh.goal_daily_incremental_evidence_refresh01 import (
    CANONICAL_FIELDS,
    CANONICAL_MARKET,
    REFRESH_ROOT,
    materialize_bounded_canonical_evidence,
)
from ashare_premarket.dashboard.repositories.snapshot_repository import CommittedEvidenceStore
from ashare_premarket.providers.akshare_provider import ProviderResult, tencent_symbol
from ashare_premarket.providers.governed_stock_history import (
    CORPORATE_ACTION_FIXTURE_PATH,
    POLICY_PATH,
    audit_qfq_corporate_action_event,
    compare_cross_source_rows,
    run_governed_stock_history_batch,
    audit_cross_source_fixture,
    validate_operational_field_contract,
)
from ashare_premarket.providers.schema_normalization import normalize_stock_ohlcv_schema, normalize_tencent_stock_ohlcv_schema


def _root(tmp_path: Path, *, production_fixture: bool = False) -> Path:
    repo = Path(__file__).resolve().parents[1]
    source = repo / POLICY_PATH
    target = tmp_path / POLICY_PATH
    target.parent.mkdir(parents=True)
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    fixture_source = repo / "configs/providers/fixtures/eastmoney_tencent_consistency_v1.csv"
    fixture_target = tmp_path / "configs/providers/fixtures/eastmoney_tencent_consistency_v1.csv"
    fixture_target.parent.mkdir(parents=True)
    fixture_target.write_bytes(fixture_source.read_bytes())
    corporate_source = repo / CORPORATE_ACTION_FIXTURE_PATH
    corporate_target = tmp_path / CORPORATE_ACTION_FIXTURE_PATH
    corporate_target.parent.mkdir(parents=True, exist_ok=True)
    corporate_target.write_bytes(corporate_source.read_bytes())
    return tmp_path


def _result(symbol: str, date: str, *, failure: str = "", close: float = 10.0) -> ProviderResult:
    passed = not failure
    rows = (
        [{
            "trade_date": date,
            "symbol": symbol,
            "open": close,
            "high": close,
            "low": close,
            "close": close,
            "volume": 100.0,
            "amount": None,
            "quality_flags": "SOURCE_BACKED;TENCENT_AMOUNT_UNAVAILABLE",
        }]
        if passed
        else []
    )
    return ProviderResult(
        rows=rows,
        attempt={
            "provider_id": "akshare",
            "function_name": "fixture",
            "symbol": symbol,
            "status": "PASS" if passed else "FAIL",
            "failure_class": "PROVIDER_OK" if passed else failure,
            "rows_returned": len(rows),
            "schema_valid": passed,
            "attempt_ts": "2026-07-15T00:00:00.000+00:00",
            "akshare_version": "1.18.64-test-fixture",
            "request_parameters": "{}",
        },
    )


@pytest.mark.parametrize(
    ("canonical", "provider"),
    [("600036.SH", "sh600036"), ("000002.SZ", "sz000002"), ("300015.SZ", "sz300015"), ("430047.BJ", "bj430047")],
)
def test_tencent_symbol_mapping(canonical: str, provider: str) -> None:
    assert tencent_symbol(canonical) == provider


@pytest.mark.parametrize("symbol", ["000002", "usAAPL", "000002.HK", "bad.SZ"])
def test_tencent_symbol_mapping_rejects_invalid_contract(symbol: str) -> None:
    with pytest.raises(ValueError, match="unsupported_canonical_symbol"):
        tencent_symbol(symbol)


def test_tencent_normalizer_preserves_proven_volume_semantics_and_does_not_invent_amount() -> None:
    frame = pd.DataFrame([{"date": "2026-07-14", "open": 3.03, "close": 3.05, "high": 3.05, "low": 2.99, "amount": 838587}])
    rows, valid, notes = normalize_tencent_stock_ohlcv_schema(frame, "000002.SZ")
    assert valid
    assert rows[0]["volume"] == 838587
    assert rows[0]["amount"] is None
    assert rows[0]["amount_semantics"] == "unavailable_from_stock_zh_a_hist_tx"
    assert "amount_unavailable" in notes


def test_tencent_normalizer_fails_closed_on_missing_or_duplicate_required_fields() -> None:
    missing = pd.DataFrame([{"date": "2026-07-14", "open": 3.03, "close": 3.05, "high": 3.05, "low": 2.99}])
    assert normalize_tencent_stock_ohlcv_schema(missing, "000002.SZ")[1] is False
    duplicate = pd.DataFrame(
        [
            {"date": "2026-07-14", "open": 3, "close": 3, "high": 3, "low": 3, "amount": 1},
            {"date": "2026-07-14", "open": 3, "close": 3, "high": 3, "low": 3, "amount": 1},
        ]
    )
    assert normalize_tencent_stock_ohlcv_schema(duplicate, "000002.SZ")[1] is False


def test_primary_normalizer_does_not_turn_missing_amount_into_observed_zero() -> None:
    rows, valid, _ = normalize_stock_ohlcv_schema(
        [{"日期": "2026-07-14", "开盘": 3.03, "最高": 3.05, "最低": 2.99, "收盘": 3.05, "成交量": 838587}],
        "000002.SZ",
    )
    assert valid
    assert rows[0]["amount"] is None
    assert "AMOUNT_UNAVAILABLE" in rows[0]["quality_flags"]


def test_complete_primary_is_selected_and_secondary_is_never_called(tmp_path: Path) -> None:
    secondary_calls: list[str] = []

    def primary(symbol: str, start: str, end: str, adjustment: str, enabled: bool) -> ProviderResult:
        return _result(symbol, start)

    def secondary(symbol: str, start: str, end: str, adjustment: str, enabled: bool) -> ProviderResult:
        secondary_calls.append(symbol)
        return _result(symbol, start)

    run = run_governed_stock_history_batch(
        _root(tmp_path), {"000002.SZ", "600036.SH"}, "2026-07-14", True, primary_loader=primary, secondary_loader=secondary, sleep=lambda _: None
    )
    assert run["state"] == "PRIMARY_SELECTED"
    assert run["selected_upstream_source"] == "East Money"
    assert run["full_coverage"] is True
    assert secondary_calls == []


def test_approved_primary_endpoint_failure_discards_partial_batch_and_reacquires_all_symbols(tmp_path: Path) -> None:
    secondary_calls: list[str] = []

    def primary(symbol: str, start: str, end: str, adjustment: str, enabled: bool) -> ProviderResult:
        return _result(symbol, start, failure="BROWSER_NET_EMPTY_RESPONSE") if symbol == "600036.SH" else _result(symbol, start, close=9)

    def secondary(symbol: str, start: str, end: str, adjustment: str, enabled: bool) -> ProviderResult:
        secondary_calls.append(symbol)
        return _result(symbol, start, close=10)

    run = run_governed_stock_history_batch(
        _root(tmp_path), {"000002.SZ", "600036.SH"}, "2026-07-14", True, primary_loader=primary, secondary_loader=secondary, sleep=lambda _: None
    )
    assert run["state"] == "SECONDARY_SELECTED"
    assert run["secondary_activation"]["reason"] == "APPROVED_PRIMARY_ENDPOINT_FAILURE"
    assert run["discarded_primary_row_count"] == 1
    assert secondary_calls == ["000002.SZ", "600036.SH"]
    assert {row["upstream_source"] for row in run["selected_rows"]} == {"Tencent"}
    assert run["secondary_batch"]["source_consistency_result"] == "PASS"
    assert run["source_consistency_result"]["status"] == "PASS"
    assert [attempt["request_sequence"] for attempt in run["all_attempts"]] == [1, 2, 3, 4]
    assert [attempt["batch_request_sequence"] for attempt in run["all_attempts"]] == [1, 2, 1, 2]


def test_qfq_production_fixture_allows_complete_secondary_while_hfq_finding_is_nonblocking(tmp_path: Path) -> None:
    def primary(symbol: str, start: str, end: str, adjustment: str, enabled: bool) -> ProviderResult:
        return _result(symbol, start, failure="BROWSER_NET_EMPTY_RESPONSE")

    def secondary(symbol: str, start: str, end: str, adjustment: str, enabled: bool) -> ProviderResult:
        return _result(symbol, start)

    run = run_governed_stock_history_batch(
        _root(tmp_path, production_fixture=True),
        {"000002.SZ", "000333.SZ"},
        "2026-07-14",
        True,
        primary_loader=primary,
        secondary_loader=secondary,
        sleep=lambda _: None,
    )

    assert run["secondary_activation"]["activated"] is True
    assert run["secondary_activation"]["reason"] == "APPROVED_PRIMARY_ENDPOINT_FAILURE"
    assert run["secondary_batch"]["accepted_symbol_count"] == 2
    assert run["secondary_batch"]["source_consistency_result"] == "PASS"
    assert run["source_consistency_result"]["status"] == "PASS"
    assert run["source_consistency_result"]["production_adjustment_policy"] == "qfq_only"
    assert run["source_consistency_result"]["hfq_research_audit"]["status"] == "BLOCKED"
    assert run["source_consistency_result"]["hfq_research_audit"]["production_gate_effect"] == "NON_BLOCKING_RESEARCH_ONLY"
    assert run["state"] == "SECONDARY_SELECTED"
    assert len(run["selected_rows"]) == 2
    assert run["selected_upstream_source"] == "Tencent"
    assert len(run["selected_batch_checksum"]) == 64
    assert run["full_coverage"] is True
    assert run["no_per_symbol_mixing"] is True


@pytest.mark.parametrize("failure", ["TLS_SSL_FAILURE", "EXTERNAL_PROXY_ENVIRONMENT_FAILURE", "MISSING_EXACT_T_MINUS_ONE_ROW", "ZERO_ROWS_RETURNED"])
def test_local_unapproved_or_ambiguous_failures_never_activate_secondary(tmp_path: Path, failure: str) -> None:
    secondary_calls: list[str] = []

    def primary(symbol: str, start: str, end: str, adjustment: str, enabled: bool) -> ProviderResult:
        return _result(symbol, start, failure=failure)

    def secondary(symbol: str, start: str, end: str, adjustment: str, enabled: bool) -> ProviderResult:
        secondary_calls.append(symbol)
        return _result(symbol, start)

    run = run_governed_stock_history_batch(
        _root(tmp_path), {"000002.SZ"}, "2026-07-14", True, primary_loader=primary, secondary_loader=secondary, sleep=lambda _: None
    )
    assert run["state"] == "PRIMARY_BLOCKED_SECONDARY_NOT_APPROVED"
    assert run["selected_rows"] == []
    assert secondary_calls == []


def test_secondary_incomplete_fails_closed_without_primary_secondary_mixing(tmp_path: Path) -> None:
    def primary(symbol: str, start: str, end: str, adjustment: str, enabled: bool) -> ProviderResult:
        return _result(symbol, start, failure="CONNECTION_RESET") if symbol == "600036.SH" else _result(symbol, start)

    def secondary(symbol: str, start: str, end: str, adjustment: str, enabled: bool) -> ProviderResult:
        return _result(symbol, start, failure="ZERO_ROWS_RETURNED") if symbol == "000002.SZ" else _result(symbol, start)

    run = run_governed_stock_history_batch(
        _root(tmp_path), {"000002.SZ", "600036.SH"}, "2026-07-14", True, primary_loader=primary, secondary_loader=secondary, sleep=lambda _: None
    )
    assert run["state"] == "SECONDARY_BLOCKED"
    assert run["selected_rows"] == []
    assert run["full_coverage"] is False
    assert run["discarded_primary_row_count"] == 1


def test_mixed_approved_and_local_primary_failure_does_not_activate_secondary(tmp_path: Path) -> None:
    secondary_calls: list[str] = []

    def primary(symbol: str, start: str, end: str, adjustment: str, enabled: bool) -> ProviderResult:
        failure = "CONNECTION_RESET" if symbol == "000002.SZ" else "TLS_SSL_FAILURE"
        return _result(symbol, start, failure=failure)

    def secondary(symbol: str, start: str, end: str, adjustment: str, enabled: bool) -> ProviderResult:
        secondary_calls.append(symbol)
        return _result(symbol, start)

    run = run_governed_stock_history_batch(
        _root(tmp_path), {"000002.SZ", "600036.SH"}, "2026-07-14", True, primary_loader=primary, secondary_loader=secondary, sleep=lambda _: None
    )
    assert run["state"] == "PRIMARY_BLOCKED_SECONDARY_NOT_APPROVED"
    assert run["secondary_activation"]["approved_failure_count"] == 1
    assert run["secondary_activation"]["unapproved_or_local_failure_count"] == 1
    assert secondary_calls == []


def test_loader_exception_is_recorded_as_local_defect_and_never_fails_over(tmp_path: Path) -> None:
    def primary(symbol: str, start: str, end: str, adjustment: str, enabled: bool) -> ProviderResult:
        raise ValueError(f"unsupported_canonical_symbol:{symbol}")

    run = run_governed_stock_history_batch(
        _root(tmp_path), {"bad.SZ"}, "2026-07-14", True, primary_loader=primary, sleep=lambda _: None
    )
    assert run["state"] == "PRIMARY_BLOCKED_SECONDARY_NOT_APPROVED"
    assert run["all_attempts"][0]["failure_class"] == "SYMBOL_NORMALIZATION_FAILED"
    assert run["all_attempts"][0]["exception_type"] == "ValueError"


def test_cross_source_tolerance_boundary_and_just_outside() -> None:
    policy = json.loads((Path(__file__).resolve().parents[1] / POLICY_PATH).read_text(encoding="utf-8"))
    tolerance = policy["cross_source_tolerances"]
    primary = [{"trade_date": "2026-07-14", "symbol": "000002.SZ", "open": 3.03, "high": 3.05, "low": 2.99, "close": 3.05, "volume": 838587}]
    at_boundary = [{**primary[0], "close": 3.06}]
    just_outside = [{**primary[0], "close": 3.060001}]
    assert compare_cross_source_rows(primary, at_boundary, tolerance)["status"] == "PASS"
    assert compare_cross_source_rows(primary, just_outside, tolerance)["status"] == "BLOCKED"


def test_cross_source_duplicate_and_date_mismatch_fail_closed() -> None:
    tolerance = {"ohlc_absolute_cny": 0.01, "ohlc_relative": 0.0, "volume_absolute_provider_units": 0}
    row = {"trade_date": "2026-07-14", "symbol": "000002.SZ", "open": 3, "high": 3, "low": 3, "close": 3, "volume": 1}
    assert compare_cross_source_rows([row, row], [row], tolerance)["reason"] == "DUPLICATE_SOURCE_KEY"
    assert compare_cross_source_rows([row], [{**row, "trade_date": "2026-07-11"}], tolerance)["reason"] == "SOURCE_KEY_COVERAGE_MISMATCH"


def test_versioned_live_fixture_passes_ohlcv_volume_and_amount_semantic_contract() -> None:
    repo = Path(__file__).resolve().parents[1]
    fixture_path = repo / "configs/providers/fixtures/eastmoney_tencent_consistency_v1.csv"
    with fixture_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    overlap = [row for row in rows if row["fixture_id"] == "current_overlap_20260714"]
    primary = [
        {"trade_date": row["evidence_date"], "symbol": row["symbol"], **{field: float(row[field]) for field in ("open", "high", "low", "close", "volume")}}
        for row in overlap
        if row["source"] == "East Money"
    ]
    secondary = [
        {"trade_date": row["evidence_date"], "symbol": row["symbol"], **{field: float(row[field]) for field in ("open", "high", "low", "close", "volume")}}
        for row in overlap
        if row["source"] == "Tencent"
    ]
    policy = json.loads((repo / POLICY_PATH).read_text(encoding="utf-8"))
    assert compare_cross_source_rows(primary, secondary, policy["cross_source_tolerances"])["status"] == "PASS"
    for row in overlap:
        if row["source"] == "Tencent":
            assert row["monetary_amount"] == ""
            assert row["semantic_status"] == "akshare_amount_is_volume_true_amount_not_exported"
        else:
            assert row["monetary_amount"]
    for left, right in zip(
        sorted((row for row in overlap if row["source"] == "East Money"), key=lambda row: row["symbol"]),
        sorted((row for row in overlap if row["source"] == "Tencent"), key=lambda row: row["symbol"]),
    ):
        amount_difference = abs(float(left["monetary_amount"]) - float(right["diagnostic_raw_monetary_amount_cny"]))
        assert amount_difference <= policy["cross_source_tolerances"]["diagnostic_monetary_amount_absolute_cny"]


def test_versioned_qfq_corporate_action_fixture_covers_sse_szse_and_required_universe(tmp_path: Path) -> None:
    result = audit_cross_source_fixture(_root(tmp_path, production_fixture=True))
    assert result["status"] == "PASS"
    assert result["ohlcv_volume_result"] == "PASS"
    assert result["adjustment_result"] == "PASS"
    assert result["qfq_exchange_coverage"] == ["SSE", "SZSE"]
    assert result["qfq_required_universe_event_result"] == "PASS"
    assert {event["evidence_method"] for event in result["qfq_corporate_action_events"]} == {
        "GOVERNED_AUTHORITATIVE_TERMS_TRIANGULATION"
    }
    assert all(event["primary_corporate_action_evidence_status"] == "PRIMARY_CORPORATE_ACTION_EVIDENCE_UNAVAILABLE" for event in result["qfq_corporate_action_events"])
    assert all(event["qfq_formula_result"] == "PASS" for event in result["qfq_corporate_action_events"])
    assert all(event["qfq_continuity"]["status"] == "PASS" for event in result["qfq_corporate_action_events"])
    assert result["hfq_runtime_enabled"] is False
    assert result["hfq_research_audit"]["status"] == "BLOCKED"
    assert result["hfq_research_audit"]["production_gate_effect"] == "NON_BLOCKING_RESEARCH_ONLY"
    assert result["amount_semantics_result"] == "PASS"
    assert len(result["fixture_checksum"]) == 64
    assert len(result["corporate_action_fixture_checksum"]) == 64


def test_direct_qfq_corporate_overlap_is_preferred_when_available() -> None:
    repo = Path(__file__).resolve().parents[1]
    fixture = json.loads((repo / CORPORATE_ACTION_FIXTURE_PATH).read_text(encoding="utf-8"))
    policy = json.loads((repo / POLICY_PATH).read_text(encoding="utf-8"))
    event = deepcopy(fixture["events"][0])
    event["primary_corporate_action_evidence_status"] = "AVAILABLE"
    event["primary_qfq_rows"] = deepcopy(event["tencent_qfq_rows"])
    result = audit_qfq_corporate_action_event(event, fixture, policy)
    assert result["status"] == "PASS"
    assert result["evidence_method"] == "DIRECT_QFQ_OVERLAP"
    assert result["direct_qfq_overlap"]["status"] == "PASS"


def test_primary_corporate_rows_cannot_be_absent_without_approved_unavailable_classification() -> None:
    repo = Path(__file__).resolve().parents[1]
    fixture = json.loads((repo / CORPORATE_ACTION_FIXTURE_PATH).read_text(encoding="utf-8"))
    policy = json.loads((repo / POLICY_PATH).read_text(encoding="utf-8"))
    event = deepcopy(fixture["events"][0])
    event["primary_corporate_action_evidence_status"] = "UNKNOWN"
    result = audit_qfq_corporate_action_event(event, fixture, policy)
    assert result["status"] == "BLOCKED"
    assert "PRIMARY_EVIDENCE_MISSING_WITHOUT_APPROVED_CLASSIFICATION" in result["failure_reasons"]


def test_qfq_formula_and_continuity_tolerances_fail_just_outside_declared_boundaries() -> None:
    repo = Path(__file__).resolve().parents[1]
    fixture = json.loads((repo / CORPORATE_ACTION_FIXTURE_PATH).read_text(encoding="utf-8"))
    policy = json.loads((repo / POLICY_PATH).read_text(encoding="utf-8"))
    formula_failure = deepcopy(fixture["events"][1])
    tolerance = fixture["tolerances"]["formula_price_absolute_cny"]
    expected = formula_failure["tencent_unadjusted_rows"][0]["open"] - formula_failure["terms"]["effective_cash_per_share"]
    formula_failure["tencent_qfq_rows"][0]["open"] = expected + tolerance + 0.000001
    formula_result = audit_qfq_corporate_action_event(formula_failure, fixture, policy)
    assert formula_result["status"] == "BLOCKED"
    assert "QFQ_FORMULA_TOLERANCE_EXCEEDED:open" in formula_result["failure_reasons"]

    continuity_failure = deepcopy(fixture["events"][0])
    continuity_failure["tencent_qfq_rows"][1]["close"] += 0.02
    continuity_result = audit_qfq_corporate_action_event(continuity_failure, fixture, policy)
    assert continuity_result["status"] == "BLOCKED"
    assert "QFQ_CONTINUITY_TOLERANCE_EXCEEDED" in continuity_result["failure_reasons"]


def test_amount_null_is_distinct_from_observed_zero_and_amount_consumers_fail_closed() -> None:
    row = {
        "trade_date": "2026-07-14",
        "symbol": "000002.SZ",
        "open": 3.03,
        "high": 3.05,
        "low": 2.99,
        "close": 3.05,
        "volume": 838587,
        "amount": None,
        "quality_flags": "SOURCE_BACKED;TENCENT_AMOUNT_UNAVAILABLE",
    }
    nullable = validate_operational_field_contract([row])
    required = validate_operational_field_contract([row], require_amount=True)
    zero = validate_operational_field_contract([{**row, "amount": 0.0, "quality_flags": "SOURCE_BACKED"}], require_amount=True)
    assert nullable["status"] == "PASS"
    assert nullable["amount_null_count"] == 1
    assert nullable["amount_observed_zero_count"] == 0
    assert required["status"] == "BLOCKED"
    assert required["failure_reasons"] == ["MISSING_REQUIRED_AMOUNT:2026-07-14:000002.SZ"]
    assert zero["status"] == "PASS"
    assert zero["amount_null_count"] == 0
    assert zero["amount_observed_zero_count"] == 1


def test_stale_tencent_row_blocks_secondary_selection(tmp_path: Path) -> None:
    def primary(symbol: str, start: str, end: str, adjustment: str, enabled: bool) -> ProviderResult:
        return _result(symbol, start, failure="BROWSER_NET_EMPTY_RESPONSE")

    def stale_secondary(symbol: str, start: str, end: str, adjustment: str, enabled: bool) -> ProviderResult:
        return _result(symbol, "2026-07-11")

    run = run_governed_stock_history_batch(
        _root(tmp_path), {"000002.SZ"}, "2026-07-14", True, primary_loader=primary, secondary_loader=stale_secondary, sleep=lambda _: None
    )
    assert run["state"] == "SECONDARY_BLOCKED"
    assert run["selected_rows"] == []
    assert run["secondary_batch"]["pit_result"] == "BLOCKED"


def test_missing_provenance_blocks_complete_batch(tmp_path: Path) -> None:
    def incomplete_provenance(symbol: str, start: str, end: str, adjustment: str, enabled: bool) -> ProviderResult:
        result = _result(symbol, start)
        result.attempt["akshare_version"] = ""
        return result

    run = run_governed_stock_history_batch(
        _root(tmp_path), {"000002.SZ"}, "2026-07-14", True, primary_loader=incomplete_provenance, sleep=lambda _: None
    )
    assert run["selected_rows"] == []
    assert run["primary_batch"]["provenance_result"] == "BLOCKED"
    assert run["state"] == "PRIMARY_BLOCKED_SECONDARY_NOT_APPROVED"


def test_identical_run_is_idempotent_at_normalized_batch_boundary(tmp_path: Path) -> None:
    def primary(symbol: str, start: str, end: str, adjustment: str, enabled: bool) -> ProviderResult:
        return _result(symbol, start)

    root = _root(tmp_path)
    first = run_governed_stock_history_batch(root, {"000002.SZ", "600036.SH"}, "2026-07-14", True, primary_loader=primary, sleep=lambda _: None)
    second = run_governed_stock_history_batch(root, {"000002.SZ", "600036.SH"}, "2026-07-14", True, primary_loader=primary, sleep=lambda _: None)
    assert first["selected_batch_checksum"] == second["selected_batch_checksum"]
    assert first["selected_rows"] == second["selected_rows"]
    assert first["selected_upstream_source"] == second["selected_upstream_source"] == "East Money"


def test_bounded_canonical_commitment_reconstructs_ignored_full_materialization(tmp_path: Path) -> None:
    def canonical_row(trade_date: str, symbol: str, close: str) -> dict[str, str]:
        row = {field: "" for field in CANONICAL_FIELDS}
        row.update(
            {
                "trade_date": trade_date,
                "symbol": symbol,
                "canonical_close": close,
                "canonical_return_1d": "0.01",
                "source_provider": "akshare",
                "risk_model_eligible": "true",
                "research_only": "true",
                "not_trading_advice": "true",
                "not_for_execution": "true",
            }
        )
        return row

    base = [canonical_row("2026-07-13", "000002.SZ", "3.00")]
    delta = [canonical_row("2026-07-14", "000002.SZ", "3.03")]
    full_relative = f"{REFRESH_ROOT}/2026-07-15/canonical_market_data.csv"
    full_path = tmp_path / full_relative
    legacy_base_fields = [field for field in CANONICAL_FIELDS if field not in {"provider_timestamp", "pit_available_date"}]
    write_csv(
        tmp_path / CANONICAL_MARKET,
        [{field: row[field] for field in legacy_base_fields} for row in base],
        legacy_base_fields,
    )
    write_csv(full_path, [*base, *delta], CANONICAL_FIELDS)
    full_checksum = hashlib.sha256(full_path.read_bytes()).hexdigest()

    commitment = materialize_bounded_canonical_evidence(
        tmp_path,
        "2026-07-15",
        "2026-07-14",
        [*base, *delta],
    )
    assert commitment["canonical_delta_row_count"] == 1
    full_path.unlink()

    snapshot_dir = tmp_path / "outputs/research/premarket_position_management/2026-07-15"
    evidence = snapshot_dir / "evidence.csv"
    write_csv(evidence, [{"status": "PASS"}])
    write_json(
        snapshot_dir / "manifest.json",
        {
            "snapshot_date": "2026-07-15",
            "expected_previous_trading_date": "2026-07-14",
            "canonical_evidence_path": full_relative,
            "canonical_evidence_checksum": full_checksum,
            "checksums": {"evidence.csv": hashlib.sha256(evidence.read_bytes()).hexdigest()},
        },
    )
    store = CommittedEvidenceStore(tmp_path)
    verified, failures = store.verify_snapshot("2026-07-15")
    assert verified is True
    assert failures == []
    assert [row["trade_date"] for row in store.canonical_rows("2026-07-15")] == ["2026-07-13", "2026-07-14"]

    delta_path = tmp_path / str(commitment["canonical_delta_path"])
    delta_path.write_text(delta_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    verified, failures = CommittedEvidenceStore(tmp_path).verify_snapshot("2026-07-15")
    assert verified is False
    assert failures == ["canonical_evidence:DELTA_CHECKSUM_MISMATCH"]

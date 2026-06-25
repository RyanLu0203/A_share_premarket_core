from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.review_diagnostics.goal08b import (
    ALLOWED_LABELS,
    CALIBRATION_WARNINGS,
    DIAGNOSTIC_PATH,
    FORBIDDEN_OUTPUT_FIELD_NAMES,
    MANIFEST_PATH,
    OUTPUT_FIELDS,
    PROVIDER_WARNINGS,
    WEAK_RANK_WARNINGS,
    audit_goal08b_recommendation_diagnostics_prototype,
    forbidden_goal08b_output_fields,
    run_goal08b_recommendation_diagnostics_prototype,
)

ROOT = Path(__file__).resolve().parents[1]


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def _codes(value: str) -> set[str]:
    if not value or value == "none":
        return set()
    return {item for item in value.split(";") if item and item != "none"}


def test_goal08b_runner_is_deterministic_and_audit_passes() -> None:
    assert run_goal08b_recommendation_diagnostics_prototype(ROOT)
    first = (ROOT / DIAGNOSTIC_PATH).read_text(encoding="utf-8")
    assert run_goal08b_recommendation_diagnostics_prototype(ROOT)
    second = (ROOT / DIAGNOSTIC_PATH).read_text(encoding="utf-8")
    assert first == second
    assert audit_goal08b_recommendation_diagnostics_prototype(ROOT)


def test_goal08b_outputs_non_actionable_trade_date_symbol_diagnostics() -> None:
    assert run_goal08b_recommendation_diagnostics_prototype(ROOT)
    rows = _rows(DIAGNOSTIC_PATH)
    source_rows = _rows("outputs/risk_overlay/goal07b_review_only_risk_overlay.csv")
    assert rows
    assert len(rows) == len(source_rows) == 100
    assert list(rows[0].keys()) == OUTPUT_FIELDS
    assert len({(row["trade_date"], row["symbol"]) for row in rows}) == len(rows)
    assert {row["diagnostic_mode"] for row in rows} == {"review_only"}
    assert {row["actionability_status"] for row in rows} == {"never_actionable"}
    assert {row["actionability_blocked"] for row in rows} == {"true"}
    assert {row["non_actionable_disclaimer"] for row in rows} == {
        "diagnostic_only_not_investment_advice_not_trade_instruction"
    }
    assert {row["recommendation_diagnostic_label"] for row in rows} <= ALLOWED_LABELS


def test_goal08b_propagates_prior_warnings_without_action_fields() -> None:
    assert run_goal08b_recommendation_diagnostics_prototype(ROOT)
    rows = _rows(DIAGNOSTIC_PATH)
    assert not forbidden_goal08b_output_fields(list(rows[0].keys()))
    for forbidden in FORBIDDEN_OUTPUT_FIELD_NAMES:
        assert forbidden not in rows[0]

    for row in rows:
        warnings = _codes(row["warning_propagation_codes"])
        reasons = _codes(row["blocked_reason_codes"])
        if row["risk_severity"] == "HIGH":
            assert row["recommendation_diagnostic_label"] == "blocked_high_risk"
            assert "high_risk_severity" in reasons
        if CALIBRATION_WARNINGS & warnings:
            assert "calibration_warning_blocks_threshold_logic" in reasons
        if WEAK_RANK_WARNINGS & warnings:
            assert "weak_rank_signal_blocks_score_conversion" in reasons
        if PROVIDER_WARNINGS & warnings:
            assert row["provider_concentration_disclosure"] == "provider_concentration_warning_propagated"


def test_goal08b_manifest_and_workflow_keep_downstream_locked() -> None:
    assert run_goal08b_recommendation_diagnostics_prototype(ROOT)
    manifest = _json(MANIFEST_PATH)
    workflow = _workflow()
    assert manifest["status"] == "PASS_WITH_WARNINGS"
    assert manifest["mode"] == "review_only"
    assert manifest["output_grain"] == "trade_date + symbol"
    assert manifest["diagnostic_row_count"] == 100
    assert manifest["diagnostic_rows_generated"] is True
    assert manifest["recommendation_diagnostics_rows_generated"] is True
    assert manifest["non_actionable"] is True
    assert manifest["deterministic_rules_only"] is True
    assert manifest["actionability_status_values"] == ["never_actionable"]
    for key in [
        "actionable_recommendation_rows_generated",
        "recommendation_rows_generated",
        "buy_sell_hold_outputs_generated",
        "target_prices_generated",
        "expected_returns_for_action_generated",
        "position_sizing_generated",
        "portfolio_weights_generated",
        "dashboard_generated",
        "paper_trading_enabled",
        "live_trading_enabled",
        "broker_integration_enabled",
        "production_model_behavior_created",
        "database_writes_created",
        "signal_backtests_run",
        "portfolio_backtests_run",
        "cost_slippage_outputs_created",
        "factor_mining_outputs_created",
        "local_lake_files_created",
        "dqn_rl_outputs_created",
        "downstream_stages_unlocked_by_this_goal",
    ]:
        assert manifest[key] is False
    assert workflow["goal08b_recommendation_review_only_prototype"]["status"] == "implemented_review_only"
    assert workflow["goal08b_recommendation_review_only_prototype"]["implemented_in_repo"] == "true"
    for workflow_id in [
        "position_band_recommendation",
        "dashboard_daily_report",
        "paper_trading_journal",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
        "signal_backtest",
        "portfolio_backtest",
        "cost_slippage_sensitivity",
        "failure_attribution",
        "production_hardening",
    ]:
        assert workflow[workflow_id]["status"] == "locked_future"


def test_goal08b_creates_no_forbidden_downstream_directories() -> None:
    assert run_goal08b_recommendation_diagnostics_prototype(ROOT)
    for rel in [
        "outputs/recommendations",
        "outputs/positions",
        "outputs/dashboard",
        "outputs/paper_trading",
        "outputs/live_trading",
        "outputs/backtests",
        "outputs/factors",
        "data/lake",
        "local_data",
    ]:
        assert not (ROOT / rel).exists()

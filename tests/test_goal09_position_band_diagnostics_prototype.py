from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.review_diagnostics.goal09 import (
    ALLOWED_POSITION_BAND_LABELS,
    DIAGNOSTIC_PATH,
    FORBIDDEN_OUTPUT_FIELD_NAMES,
    MANIFEST_PATH,
    OUTPUT_FIELDS,
    audit_goal09_position_band_diagnostics_prototype,
    forbidden_goal09_output_fields,
    run_goal09_position_band_diagnostics_prototype,
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


def test_goal09_runner_is_deterministic_and_audit_passes() -> None:
    assert run_goal09_position_band_diagnostics_prototype(ROOT)
    first = (ROOT / DIAGNOSTIC_PATH).read_text(encoding="utf-8")
    assert run_goal09_position_band_diagnostics_prototype(ROOT)
    second = (ROOT / DIAGNOSTIC_PATH).read_text(encoding="utf-8")
    assert first == second
    assert audit_goal09_position_band_diagnostics_prototype(ROOT)


def test_goal09_outputs_review_only_position_band_diagnostics() -> None:
    assert run_goal09_position_band_diagnostics_prototype(ROOT)
    rows = _rows(DIAGNOSTIC_PATH)
    source_rows = _rows("outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv")
    assert rows
    assert len(rows) == len(source_rows) == 100
    assert list(rows[0].keys()) == OUTPUT_FIELDS
    assert len({(row["trade_date"], row["symbol"]) for row in rows}) == len(rows)
    assert {row["diagnostic_mode"] for row in rows} == {"review_only"}
    assert {row["position_actionability_status"] for row in rows} == {"never_actionable"}
    assert {row["position_actionability_blocked"] for row in rows} == {"true"}
    assert {row["recommendation_actionability_status"] for row in rows} == {"never_actionable"}
    assert {row["position_band_diagnostic_label"] for row in rows} <= ALLOWED_POSITION_BAND_LABELS
    assert {row["position_band_status"] for row in rows} == {"diagnostic_blocked_no_position_instruction"}


def test_goal09_propagates_warnings_and_blocks_high_risk() -> None:
    assert run_goal09_position_band_diagnostics_prototype(ROOT)
    rows = _rows(DIAGNOSTIC_PATH)
    assert not forbidden_goal09_output_fields(list(rows[0].keys()))
    for forbidden in FORBIDDEN_OUTPUT_FIELD_NAMES:
        assert forbidden not in rows[0]
    for row in rows:
        warnings = _codes(row["propagated_warning_codes"])
        reasons = _codes(row["blocked_reason_codes"])
        assert warnings
        assert row["risk_severity"] == "HIGH"
        assert row["position_band_diagnostic_label"] == "blocked_high_risk"
        assert "high_risk_severity_blocks_position_band" in reasons
        assert "inherited_recommendation_never_actionable" in reasons
        assert "future_position_diagnostics_non_actionable_policy" in reasons


def test_goal09_manifest_and_workflow_keep_execution_locked() -> None:
    assert run_goal09_position_band_diagnostics_prototype(ROOT)
    manifest = _json(MANIFEST_PATH)
    workflow = _workflow()
    assert manifest["status"] == "PASS_WITH_WARNINGS"
    assert manifest["mode"] == "review_only"
    assert manifest["output_grain"] == "trade_date + symbol"
    assert manifest["position_band_diagnostic_row_count"] == 100
    assert manifest["position_band_diagnostics_rows_generated"] is True
    assert manifest["non_actionable"] is True
    assert manifest["position_actionability_status_values"] == ["never_actionable"]
    assert manifest["deterministic_rules_only"] is True
    assert manifest["high_risk_blocking_enforced"] is True
    for key in [
        "position_rows_generated",
        "actual_position_sizing_generated",
        "portfolio_weights_generated",
        "target_weights_generated",
        "order_quantities_generated",
        "capital_allocation_amounts_generated",
        "buy_sell_hold_outputs_generated",
        "target_prices_generated",
        "expected_returns_for_action_generated",
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
        "optimization_used",
        "learned_policy_used",
        "downstream_stages_unlocked_by_this_goal",
    ]:
        assert manifest[key] is False
    goal09 = workflow["position_band_recommendation"]
    assert goal09["status"] == "implemented_review_only"
    assert goal09["implemented_in_repo"] == "true"
    for workflow_id in [
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
        assert workflow[workflow_id]["implemented_in_repo"] == "false"


def test_goal09_creates_no_forbidden_execution_outputs() -> None:
    assert run_goal09_position_band_diagnostics_prototype(ROOT)
    for rel in [
        "outputs/recommendations",
        "outputs/positions",
        "outputs/position_band",
        "outputs/position_bands",
        "outputs/portfolio",
        "outputs/orders",
        "outputs/dashboard",
        "outputs/paper_trading",
        "outputs/live_trading",
        "outputs/backtests",
        "outputs/factors",
        "data/lake",
        "local_data",
    ]:
        assert not (ROOT / rel).exists()

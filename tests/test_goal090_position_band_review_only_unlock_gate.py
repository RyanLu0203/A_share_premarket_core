from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.contract_design.goal090 import (
    GOAL09_ALLOWED_NEXT,
    GOAL09_ELIGIBLE_STATUS,
    MANIFEST_PATH,
    audit_goal090_position_band_review_only_unlock_gate,
    forbidden_goal090_source_fields,
    run_goal090_position_band_review_only_unlock_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal090_runner_is_unlock_only_and_deterministic() -> None:
    assert run_goal090_position_band_review_only_unlock_gate(ROOT)
    first = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert run_goal090_position_band_review_only_unlock_gate(ROOT)
    second = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert first == second
    assert audit_goal090_position_band_review_only_unlock_gate(ROOT)


def test_goal090_marks_goal09_future_review_only_not_implemented() -> None:
    assert run_goal090_position_band_review_only_unlock_gate(ROOT)
    workflow = _workflow()
    assert workflow["goal090_position_band_review_only_unlock_gate"]["status"] == "implemented_review_only"
    assert workflow["goal090_position_band_review_only_unlock_gate"]["implemented_in_repo"] == "true"
    goal09 = workflow["position_band_recommendation"]
    assert goal09["status"] == GOAL09_ELIGIBLE_STATUS
    assert goal09["implemented_in_repo"] == "false"
    assert goal09["allowed_next_action"] == GOAL09_ALLOWED_NEXT
    assert goal09["depends_on"] == "goal090_position_band_review_only_unlock_gate"
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


def test_goal090_uses_goal08b_evidence_without_position_fields() -> None:
    assert run_goal090_position_band_review_only_unlock_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    goal08b_rows = _rows("outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv")
    assert manifest["status"] == "PASS_WITH_WARNINGS"
    assert manifest["mode"] == "review_only_unlock_gate"
    assert manifest["goal090_unlock_status"] == "eligible_for_future_review_only_prototype"
    assert manifest["goal09_implemented_by_this_gate"] is False
    assert manifest["goal09_implemented_in_repo"] is False
    assert manifest["goal08b_row_count"] == len(goal08b_rows) == 100
    assert manifest["goal08b_output_grain"] == "trade_date + symbol"
    assert manifest["goal08b_actionability_status_values"] == ["never_actionable"]
    assert manifest["goal08b_non_actionable_preserved"] is True
    assert manifest["high_risk_actionability_block_preserved"] is True
    assert manifest["goal08b_warnings_propagate_to_future_position_band_diagnostics"] is True
    assert "outputs/audits/goal08b_recommendation_diagnostics_manifest.json" in manifest["evidence_inputs"]
    assert "outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv" in manifest["evidence_inputs"]
    assert not forbidden_goal090_source_fields(list(goal08b_rows[0].keys()))


def test_goal090_generates_no_position_or_downstream_outputs() -> None:
    assert run_goal090_position_band_review_only_unlock_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    for key in [
        "position_band_diagnostics_rows_generated",
        "position_rows_generated",
        "position_sizing_generated",
        "portfolio_construction_generated",
        "portfolio_weights_generated",
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
        "data_coverage_expanded",
        "live_calculation_outputs_used",
        "downstream_stages_unlocked_by_this_gate",
    ]:
        assert manifest[key] is False
    for rel in [
        "outputs/positions",
        "outputs/position",
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

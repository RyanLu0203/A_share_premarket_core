from __future__ import annotations

import copy
import csv
import json
from pathlib import Path

from ashare_premarket.risk_overlay.goal07b import (
    SEVERITY_LEVELS,
    audit_goal07b_risk_overlay_calculation_prototype,
    evaluate_goal07b_calculation,
    forbidden_goal07b_output_fields,
    load_goal07b_input_bundle,
    run_goal07b_risk_overlay_calculation_prototype,
)

ROOT = Path(__file__).resolve().parents[1]


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal07b_runner_is_deterministic_and_review_only() -> None:
    assert run_goal07b_risk_overlay_calculation_prototype(ROOT)
    first = (ROOT / "outputs/risk_overlay/goal07b_review_only_risk_overlay.csv").read_text(encoding="utf-8")
    assert run_goal07b_risk_overlay_calculation_prototype(ROOT)
    second = (ROOT / "outputs/risk_overlay/goal07b_review_only_risk_overlay.csv").read_text(encoding="utf-8")
    assert first == second
    assert audit_goal07b_risk_overlay_calculation_prototype(ROOT)


def test_goal07b_consumes_only_approved_review_only_inputs() -> None:
    assert run_goal07b_risk_overlay_calculation_prototype(ROOT)
    manifest = json.loads((ROOT / "outputs/audits/goal07b_risk_overlay_calculation_manifest.json").read_text(encoding="utf-8"))
    assert manifest["mode"] == "review_only"
    assert manifest["calculation_type"] == "risk_overlay_diagnostic"
    assert "outputs/samples/stage6c_source_backed_engineering_panel_sample.csv" in manifest["input_artifacts"]
    assert "outputs/audits/goal07b0_unlock_gate_manifest.json" in manifest["input_artifacts"]
    assert not (set(manifest["input_fields_used"]) & set(manifest["excluded_future_or_label_fields"]))
    assert manifest["live_data_fetched"] is False
    assert manifest["database_writes_performed"] is False
    assert manifest["future_information_used"] is False


def test_goal07b_missing_required_input_contract_fails_safely() -> None:
    bundle = load_goal07b_input_bundle(ROOT)
    modified = copy.deepcopy(bundle)
    modified["stage6c_sample_rows"][0].pop("provider_mode")
    result = evaluate_goal07b_calculation(modified)
    assert result["status"] == "FAIL"
    assert "stage6c_required_field_missing:provider_mode" in result["failures"]
    assert result["risk_overlay_rows"] == []


def test_goal07b_outputs_trade_date_symbol_grain_and_bounded_severity() -> None:
    assert run_goal07b_risk_overlay_calculation_prototype(ROOT)
    rows = _rows("outputs/risk_overlay/goal07b_review_only_risk_overlay.csv")
    assert rows
    grain = {(row["trade_date"], row["symbol"]) for row in rows}
    assert len(grain) == len(rows)
    assert {row["risk_severity"] for row in rows} <= SEVERITY_LEVELS
    assert {row["risk_severity"] for row in rows} == {"HIGH"}


def test_goal07b_warning_propagation_rule_trace_and_state_are_non_actionable() -> None:
    assert run_goal07b_risk_overlay_calculation_prototype(ROOT)
    rows = _rows("outputs/risk_overlay/goal07b_review_only_risk_overlay.csv")
    first = rows[0]
    assert "calibration_not_reliable_for_thresholding" in first["warning_propagation"]
    assert "selected_score_variant_weak_rank_signal" in first["warning_propagation"]
    assert "calibration_warning_minimum_warning_state" in first["risk_rule_trace"]
    assert first["risk_state"] == "model_warning"
    assert first["risk_transition_diagnostic"] == "not_evaluated->model_warning"
    assert first["non_actionable"] == "true"
    assert first["recommendation_generated"] == "false"
    assert first["position_generated"] == "false"


def test_goal07b_rejects_forbidden_schema_fields() -> None:
    forbidden = forbidden_goal07b_output_fields(
        [
            "recommendation",
            "target_position",
            "position_size",
            "portfolio_weight",
            "order",
            "broker",
            "dashboard_decision",
            "production_signal",
            "backtest_return",
            "dqn",
            "rl_policy",
        ]
    )
    assert set(forbidden) == {
        "recommendation",
        "target_position",
        "position_size",
        "portfolio_weight",
        "order",
        "broker",
        "dashboard_decision",
        "production_signal",
        "backtest_return",
        "dqn",
        "rl_policy",
    }
    assert forbidden_goal07b_output_fields(["trade_date", "recommendation_generated", "position_generated"]) == []


def test_goal07b_workflow_status_and_downstream_locks() -> None:
    assert run_goal07b_risk_overlay_calculation_prototype(ROOT)
    workflow = _workflow()
    assert workflow["goal07b_risk_overlay_calculation"]["status"] == "implemented_review_only"
    assert workflow["goal07b_risk_overlay_calculation"]["implemented_in_repo"] == "true"
    assert workflow["goal08a_recommendation_contract_design_gate"]["status"] in {"locked_future", "implemented_design_only"}
    if workflow["goal08a_recommendation_contract_design_gate"]["status"] == "implemented_design_only":
        assert workflow["goal08a_recommendation_contract_design_gate"]["implemented_in_repo"] == "true"
    assert workflow["goal08b_recommendation_review_only_prototype"]["status"] in {"locked_future", "future_review_only"}
    assert workflow["goal08b_recommendation_review_only_prototype"]["implemented_in_repo"] == "false"
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


def test_goal07b_outputs_no_forbidden_downstream_artifacts() -> None:
    assert run_goal07b_risk_overlay_calculation_prototype(ROOT)
    for rel in [
        "outputs/recommendations",
        "outputs/positions",
        "outputs/dashboard",
        "outputs/paper_trading",
        "outputs/live_trading",
        "outputs/backtests",
        "outputs/factors",
    ]:
        assert not (ROOT / rel).exists()
    manifest = json.loads((ROOT / "outputs/audits/goal07b_risk_overlay_calculation_manifest.json").read_text(encoding="utf-8"))
    assert manifest["recommendation_generated"] is False
    assert manifest["position_generated"] is False
    assert manifest["dashboard_generated"] is False
    assert manifest["paper_live_trading_generated"] is False
    assert manifest["trading_generated"] is False
    assert manifest["production_generated"] is False
    assert manifest["backtest_generated"] is False
    assert manifest["factor_mining_generated"] is False
    assert manifest["dqn_rl_generated"] is False

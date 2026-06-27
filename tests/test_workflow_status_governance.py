from __future__ import annotations

import csv
from pathlib import Path

from ashare_premarket.validation.workflow_status import run_workflow_status_audit


ROOT = Path(__file__).resolve().parents[1]


def _workflow_rows() -> list[dict[str, str]]:
    with (ROOT / "configs/project/workflow_status.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_workflow_status_contract_exists_and_has_required_statuses() -> None:
    rows = _workflow_rows()
    statuses = {row["status"] for row in rows}
    assert "implemented_active" in statuses
    assert "implemented_review_only" in statuses
    assert "implemented_design_only" in statuses
    assert "implemented_infrastructure_only" in statuses
    assert "locked_future" in statuses
    assert "deleted_from_active_mainline" in statuses


def test_goal06c_is_review_only_and_downstream_are_not_implemented_active() -> None:
    rows = {row["workflow_id"]: row for row in _workflow_rows()}
    assert rows["goal06c_expanded_validation_ranking"]["status"] == "implemented_review_only"
    assert rows["goal06d_model_comparison_calibration"]["status"] == "implemented_review_only"
    assert rows["goal06d_model_comparison_calibration"]["allowed_next_action"] == "fix_goal06d_model_stability_or_calibration_warnings"
    assert rows["goal07a_risk_overlay_design"]["status"] == "implemented_design_only"
    assert rows["goal07b0_risk_overlay_review_only_unlock_gate"]["status"] == "implemented_review_only"
    assert rows["goal07b_risk_overlay_calculation"]["status"] == "implemented_review_only"
    assert rows["goal07b_risk_overlay_calculation"]["implemented_in_repo"] == "true"
    assert rows["goal08a_recommendation_contract_design_gate"]["status"] == "implemented_design_only"
    assert rows["goal08a_recommendation_contract_design_gate"]["implemented_in_repo"] == "true"
    assert rows["goal_storage01_local_research_lake_hardening_gate"]["status"] == "implemented_infrastructure_only"
    assert rows["goal_storage01_local_research_lake_hardening_gate"]["implemented_in_repo"] == "true"
    assert rows["goal08b0_recommendation_review_only_unlock_gate"]["status"] == "implemented_review_only"
    assert rows["goal08b0_recommendation_review_only_unlock_gate"]["implemented_in_repo"] == "true"
    assert rows["goal08b_recommendation_review_only_prototype"]["status"] == "implemented_review_only"
    assert rows["goal08b_recommendation_review_only_prototype"]["implemented_in_repo"] == "true"
    assert rows["goal090_position_band_review_only_unlock_gate"]["status"] == "implemented_review_only"
    assert rows["goal090_position_band_review_only_unlock_gate"]["implemented_in_repo"] == "true"
    assert rows["position_band_recommendation"]["status"] == "implemented_review_only"
    assert rows["position_band_recommendation"]["implemented_in_repo"] == "true"
    assert rows["goal091_position_band_warning_dashboard_readiness_gate"]["status"] == "implemented_review_only"
    assert rows["goal091_position_band_warning_dashboard_readiness_gate"]["implemented_in_repo"] == "true"
    assert rows["goal_v1_integrity01_artifact_lineage_structure_gate"]["status"] == "implemented_infrastructure_only"
    assert rows["goal_v1_integrity01_artifact_lineage_structure_gate"]["implemented_in_repo"] == "true"
    assert rows["goal_v1_integrity01_artifact_lineage_structure_gate"]["depends_on"] == "goal091_position_band_warning_dashboard_readiness_gate"
    assert rows["goal10a_backtest_contract_design_gate"]["status"] == "implemented_design_only"
    assert rows["goal10a_backtest_contract_design_gate"]["implemented_in_repo"] == "true"
    assert rows["goal10a_backtest_contract_design_gate"]["depends_on"] == "goal_v1_integrity01_artifact_lineage_structure_gate"
    assert rows["goal10b_backtest_review_only_validation_gate"]["status"] == "implemented_review_only"
    assert rows["goal10b_backtest_review_only_validation_gate"]["implemented_in_repo"] == "true"
    assert rows["goal10b_backtest_review_only_validation_gate"]["depends_on"] == "goal10a_backtest_contract_design_gate"
    assert rows["goal10b1_backtest_coverage_repair_gate"]["status"] == "implemented_review_only"
    assert rows["goal10b1_backtest_coverage_repair_gate"]["implemented_in_repo"] == "true"
    assert rows["goal10b1_backtest_coverage_repair_gate"]["depends_on"] == "goal10b_backtest_review_only_validation_gate"
    assert rows["goal_data_label01_forward_return_label_coverage_expansion"]["status"] == "implemented_review_only"
    assert rows["goal_data_label01_forward_return_label_coverage_expansion"]["implemented_in_repo"] == "true"
    assert rows["goal_data_label01_forward_return_label_coverage_expansion"]["depends_on"] == "goal10b1_backtest_coverage_repair_gate"
    assert rows["goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"]["status"] == "implemented_review_only"
    assert rows["goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"]["implemented_in_repo"] == "true"
    assert rows["goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"]["depends_on"] == "goal_data_label01_forward_return_label_coverage_expansion"
    assert rows["goal10b2_recommendation_backtest_revalidation"]["status"] == "implemented_review_only"
    assert rows["goal10b2_recommendation_backtest_revalidation"]["implemented_in_repo"] == "true"
    assert rows["goal10b2_recommendation_backtest_revalidation"]["depends_on"] == "goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"
    assert rows["goal10c_backtest_cost_slippage_sensitivity_gate"]["status"] == "implemented_review_only"
    assert rows["goal10c_backtest_cost_slippage_sensitivity_gate"]["implemented_in_repo"] == "true"
    assert rows["goal10c_backtest_cost_slippage_sensitivity_gate"]["depends_on"] == "goal10b2_recommendation_backtest_revalidation"
    for workflow_id in ["goal10d_backtest_failure_attribution_gate"]:
        assert rows[workflow_id]["status"] == "locked_future"
        assert rows[workflow_id]["implemented_in_repo"] == "false"
    assert rows["dashboard_daily_report"]["status"] == "locked_future"
    assert rows["dashboard_daily_report"]["implemented_in_repo"] == "false"
    assert rows["dashboard_daily_report"]["depends_on"] == "goal_v1_integrity01_artifact_lineage_structure_gate"
    assert rows["dqn_rl_mainline"]["status"] == "deleted_from_active_mainline"


def test_workflow_status_audit_passes() -> None:
    assert run_workflow_status_audit(ROOT)

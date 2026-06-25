from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.contract_design.goal091 import (
    AUDIT_PATH,
    CONFIG_PATH,
    DASHBOARD_FORBIDDEN_FIELD_NAMES,
    MANIFEST_PATH,
    WARNING_CLASSIFICATION,
    audit_goal091_position_band_warning_dashboard_readiness_gate,
    run_goal091_position_band_warning_dashboard_readiness_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal091_runner_is_deterministic_and_audit_passes() -> None:
    assert run_goal091_position_band_warning_dashboard_readiness_gate(ROOT)
    first = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert run_goal091_position_band_warning_dashboard_readiness_gate(ROOT)
    second = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert first == second
    assert audit_goal091_position_band_warning_dashboard_readiness_gate(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")


def test_goal091_classifies_goal09_warnings_for_future_dashboard_contract() -> None:
    assert run_goal091_position_band_warning_dashboard_readiness_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    policy = _json(CONFIG_PATH)
    assert manifest["status"] == "PASS_WITH_WARNINGS"
    assert manifest["warning_classification"] == WARNING_CLASSIFICATION
    assert policy["warning_classification"] == WARNING_CLASSIFICATION
    assert manifest["dashboard_blocking_banner_warning_codes"] == [
        "calibration_not_reliable_for_thresholding",
        "selected_score_variant_weak_rank_signal",
        "target_horizon_calibration_warning",
        "weak_target_horizon_rank_signal",
    ]
    assert manifest["provider_concentration_banner_warning_codes"] == [
        "provider_source_concentration_disclosed",
        "single_provider_mode_akshare_direct",
    ]
    assert manifest["row_level_and_summary_warning_codes"] == ["feature_sign_instability_bounded"]
    assert set(manifest["row_level_warning_codes_required"]) == set(WARNING_CLASSIFICATION)
    assert set(manifest["warning_codes_preventing_action_oriented_display"]) == set(WARNING_CLASSIFICATION)


def test_goal091_confirms_goal09_non_actionable_inputs_and_dashboard_eligibility_only() -> None:
    assert run_goal091_position_band_warning_dashboard_readiness_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    workflow = _workflow()
    assert manifest["goal09_status_confirmed"] is True
    assert manifest["goal09_non_actionable_confirmed"] is True
    assert manifest["goal09_output_grain"] == "trade_date + symbol"
    assert manifest["goal09_row_count"] == 100
    assert manifest["position_actionability_status_values"] == ["never_actionable"]
    assert manifest["future_dashboard_contract_design_gate_may_be_requested"] is True
    assert manifest["goal_dashboard00_request_status"] == "eligible_for_explicit_design_only_contract_gate"
    assert manifest["dashboard_daily_report_status_after_goal091"] == "locked_future"
    assert manifest["dashboard_design_only_eligibility_only"] is True
    assert manifest["dashboard_implemented_by_this_goal"] is False
    assert workflow["goal091_position_band_warning_dashboard_readiness_gate"]["status"] == "implemented_review_only"
    assert workflow["dashboard_daily_report"]["status"] == "locked_future"
    assert workflow["dashboard_daily_report"]["implemented_in_repo"] == "false"


def test_goal091_future_dashboard_contract_blocks_actionable_surfaces() -> None:
    assert run_goal091_position_band_warning_dashboard_readiness_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    assert set(manifest["future_dashboard_forbidden_fields"]) == DASHBOARD_FORBIDDEN_FIELD_NAMES
    for key in [
        "future_dashboard_review_only_required",
        "future_dashboard_never_actionable_required",
        "future_dashboard_non_actionable_disclaimers_required",
        "future_dashboard_may_use_only_audited_goal07b_goal08b_goal09_diagnostics",
        "future_dashboard_top_n_candidate_display_blocked",
        "future_dashboard_buy_candidate_display_blocked",
        "future_dashboard_position_candidate_display_blocked",
        "future_dashboard_actionable_language_blocked",
        "future_dashboard_forbidden_fields_blocked",
    ]:
        assert manifest[key] is True
    for key in [
        "dashboard_outputs_generated",
        "dashboard_files_generated",
        "html_generated",
        "streamlit_generated",
        "frontend_code_generated",
        "visual_reports_generated",
        "new_recommendation_rows_generated",
        "new_position_rows_generated",
        "actual_position_sizing_generated",
        "portfolio_weights_generated",
        "target_weights_generated",
        "order_quantities_generated",
        "buy_sell_hold_outputs_generated",
        "target_prices_generated",
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
        "downstream_execution_unlocked_by_this_goal",
    ]:
        assert manifest[key] is False


def test_goal091_generates_no_dashboard_or_new_row_outputs() -> None:
    assert run_goal091_position_band_warning_dashboard_readiness_gate(ROOT)
    assert not (ROOT / "outputs/dashboard").exists()
    assert not (ROOT / "outputs/dashboards").exists()
    assert not (ROOT / "outputs/visual_reports").exists()
    assert not (ROOT / "outputs/frontend").exists()
    assert len(_rows("outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv")) == 100
    assert len(_rows("outputs/position/goal09_review_only_position_band_diagnostics.csv")) == 100

from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.io import read_csv, write_csv, write_text

ALLOWED_STATUSES = {
    "implemented_active",
    "implemented_review_only",
    "implemented_design_only",
    "implemented_infrastructure_only",
    "implemented_research_only",
    "future_review_only",
    "future_design_only",
    "locked_future",
    "planned_locked",
    "not_started",
    "deleted_from_active_mainline",
}

DOWNSTREAM_LOCKED_IDS = {
    "signal_backtest",
    "portfolio_backtest",
    "cost_slippage_sensitivity",
    "paper_trading_journal",
    "failure_attribution",
    "dashboard_daily_report",
    "production_hardening",
    "broker_live_trading",
    "production_db_writes",
    "production_model_promotion",
    "goal10d_backtest_failure_attribution_gate",
    "goal_data_panel02_evaluation_panel_gate",
    "goal_rec_tiering01_recommendation_score_tiering_gate",
    "goal10b4_recommendation_backtest_revalidation",
    "goal_position_band_validation01_position_band_validation_gate",
}

GOAL07B_WORKFLOW_ID = "goal07b_risk_overlay_calculation"
GOAL07B_ALLOWED_STATUSES = {"locked_future", "future_review_only", "implemented_review_only"}
GOAL08A_WORKFLOW_ID = "goal08a_recommendation_contract_design_gate"
GOAL08A_ALLOWED_STATUSES = {"locked_future", "implemented_design_only"}
GOAL_STORAGE01_WORKFLOW_ID = "goal_storage01_local_research_lake_hardening_gate"
GOAL08B0_WORKFLOW_ID = "goal08b0_recommendation_review_only_unlock_gate"
GOAL08B_WORKFLOW_ID = "goal08b_recommendation_review_only_prototype"
GOAL08B_ALLOWED_STATUSES = {"locked_future", "future_review_only", "implemented_review_only"}
GOAL08B_ALLOWED_NEXT = "await_explicit_goal08b_review_only_recommendation_diagnostics_prototype"
GOAL08B_IMPLEMENTED_ALLOWED_NEXT = "request_explicit_goal09_position_band_review_only_unlock_or_fix_goal08b_warnings"
GOAL090_WORKFLOW_ID = "goal090_position_band_review_only_unlock_gate"
GOAL09_WORKFLOW_ID = "position_band_recommendation"
GOAL09_ALLOWED_STATUSES = {"locked_future", "future_review_only", "implemented_review_only"}
GOAL09_ALLOWED_NEXT = "await_explicit_goal09_position_band_diagnostics_prototype"
GOAL09_IMPLEMENTED_ALLOWED_NEXT = "fix_goal09_position_band_warnings_before_any_downstream_request"
GOAL091_WORKFLOW_ID = "goal091_position_band_warning_dashboard_readiness_gate"
GOAL091_ALLOWED_NEXT = "request_explicit_goal_dashboard00_contract_design_gate"
GOAL_V1_INTEGRITY01_WORKFLOW_ID = "goal_v1_integrity01_artifact_lineage_structure_gate"
GOAL_V1_INTEGRITY01_ALLOWED_NEXT = "request_explicit_goal_dashboard00_contract_design_gate"
GOAL10A_WORKFLOW_ID = "goal10a_backtest_contract_design_gate"
GOAL10A_ALLOWED_NEXT = "request_explicit_goal10b_review_only_backtest_validation_gate_or_fix_goal10a_warnings"
GOAL10B_WORKFLOW_ID = "goal10b_backtest_review_only_validation_gate"
GOAL10B_ALLOWED_NEXT = "fix_goal10b_backtest_warnings_before_goal10c_request"
GOAL10B1_WORKFLOW_ID = "goal10b1_backtest_coverage_repair_gate"
GOAL10B1_ALLOWED_NEXT = "request_future_data_label_coverage_expansion_gate_or_fix_goal10b1_warnings"
GOAL_DATA_LABEL01_WORKFLOW_ID = "goal_data_label01_forward_return_label_coverage_expansion"
GOAL_DATA_LABEL01_ALLOWED_NEXT = "request_goal_v1_diagnostic_coverage02_multi_symbol_expansion_or_fix_data_label_warnings"
GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID = "goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"
GOAL_V1_DIAGNOSTIC_COVERAGE02_ALLOWED_NEXT = "request_goal10b2_recommendation_backtest_revalidation_or_fix_diagnostic_coverage_warnings"
GOAL10B2_WORKFLOW_ID = "goal10b2_recommendation_backtest_revalidation"
GOAL10B2_ALLOWED_NEXT = "request_goal10c_cost_slippage_sensitivity_or_fix_goal10b2_warnings"
GOAL10C_WORKFLOW_ID = "goal10c_backtest_cost_slippage_sensitivity_gate"
GOAL10C_ALLOWED_NEXT = "request_goal10d_failure_attribution_or_fix_goal10c_warnings"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
GOAL_DATA_PROVIDER02A_WORKFLOW_ID = "goal_data_provider02a_multi_provider_capability_probe"
GOAL_DATA_PROVIDER02A_ALLOWED_NEXT = "request_goal_data_provider02b_source_backed_panel_build_or_fix_provider02a_warnings"
GOAL_DATA_PROVIDER02A1_WORKFLOW_ID = "goal_data_provider02a1_network_opt_in_provider_smoke_test"
GOAL_DATA_PROVIDER02A1_ALLOWED_NEXT = "request_goal_data_provider02b_source_backed_panel_build_or_fix_provider02a1_warnings"
GOAL_DATA_PROVIDER02B_WORKFLOW_ID = "goal_data_provider02b_provider_selection_gate"
GOAL_DATA_PROVIDER02B_ALLOWED_NEXT = "request_goal_v1_diagnostic_coverage03_or_fix_provider02b_warnings"
GOAL_DATA_PANEL02_WORKFLOW_ID = "goal_data_panel02_evaluation_panel_gate"
GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID = "goal_v1_diagnostic_coverage03_multi_provider_diagnostics"
GOAL_V1_DIAGNOSTIC_COVERAGE03_ALLOWED_NEXT = "request_goal10b3_recommendation_revalidation_or_fix_dc03_tiering_warnings"
GOAL10B3_WORKFLOW_ID = "goal10b3_recommendation_backtest_revalidation"
GOAL10B3_ALLOWED_NEXT = "fix_goal10b3_revalidation_warnings_before_position_band_validation"
GOAL_RISK_TIERING01_WORKFLOW_ID = "goal_risk_tiering01_risk_severity_numeric_score_gate"
GOAL_RISK_TIERING01_ALLOWED_NEXT_WEAK = "repair_goal_risk_tiering01_rules_before_goal_rec_tiering01"
GOAL_RISK_TIERING01_ALLOWED_NEXT_AVAILABLE = "request_goal_rec_tiering01_recommendation_score_tiering_gate"
GOAL_RISK_TIERING011_WORKFLOW_ID = "goal_risk_tiering011_downside_risk_repair_gate"
GOAL_RISK_TIERING011_ALLOWED_NEXT_WEAK = "review_deterministic_downside_risk_rules_before_goal_rec_tiering01"
GOAL_RISK_TIERING011_ALLOWED_NEXT_AVAILABLE = "request_goal_rec_tiering01_recommendation_score_tiering_gate"
GOAL_QUANT_RESEARCH01_WORKFLOW_ID = "goal_quant_research01_factor_research_lab_gate"
GOAL_QUANT_RESEARCH01_ALLOWED_NEXT_WEAK = "request_goal_alpha_factor_candidate01_before_recommendation_tiering"
GOAL_QUANT_RESEARCH01_ALLOWED_NEXT_AVAILABLE = "request_explicit_goal_rec_tiering01_after_research_candidate_review"
GOAL_REC_TIERING01_WORKFLOW_ID = "goal_rec_tiering01_recommendation_score_tiering_gate"
GOAL10B4_WORKFLOW_ID = "goal10b4_recommendation_backtest_revalidation"
POSITION_BAND_VALIDATION_WORKFLOW_ID = "goal_position_band_validation01_position_band_validation_gate"

REQUIRED_ACTIVE_IDS = {
    "project_operating_system",
    "universe_symbol_governance",
    "data_provider_source_health",
    "context_contract_layers",
    "pit_signal_store",
    "label_builder",
    "benchmark_contract",
    "feature_label_merge",
    "leakage_audit",
    "stage6a_repair_panel",
    "goal06a_baseline_scoring",
    "goal06b_supervised_baseline_gate",
    "validation_verification_diagnostics",
    "safety_gate",
    "adapter_audit",
}


def run_workflow_status_audit(root: Path) -> bool:
    status_path = root / "configs/project/workflow_status.csv"
    rows = read_csv(status_path) if status_path.exists() else []
    failures: list[str] = []
    warnings: list[str] = []

    if not status_path.exists():
        failures.append("workflow_status file is missing")
    if rows:
        failures.extend(_validate_rows(rows))
    else:
        failures.append("workflow_status file has no rows")

    readme = _read(root / "README.md")
    full_roadmap = _read(root / "docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md")
    active_doc = _read(root / "docs/architecture/ACTIVE_WORKFLOW_THROUGH_GOAL06B.md")

    if "## Active Workflow" not in readme or "```mermaid" not in readme:
        failures.append("README does not contain an Active Workflow Mermaid diagram")
    if "-." not in full_roadmap:
        failures.append("full roadmap does not contain dotted future arrows")
    active_mermaid = _first_mermaid_block(active_doc)
    if "GOAL-06C" in active_mermaid:
        failures.append("active workflow doc shows GOAL-06C in active workflow")
    if "GOAL-09 Position-Band Diagnostics" not in full_roadmap or "implemented_review_only" not in full_roadmap:
        failures.append("full roadmap does not label GOAL-09 position-band diagnostics as implemented_review_only")
    if "GOAL-10A Backtest Contract Design" not in full_roadmap or "implemented_design_only" not in full_roadmap:
        failures.append("full roadmap does not label GOAL-10A backtest contract design as implemented_design_only")
    if "GOAL-10B Recommendation Diagnostics Backtest" not in full_roadmap or "implemented_review_only" not in full_roadmap:
        failures.append("full roadmap does not label GOAL-10B recommendation diagnostics backtest as implemented_review_only")
    if "GOAL-10B.1 Coverage Repair Gate" not in full_roadmap or "implemented_review_only" not in full_roadmap:
        failures.append("full roadmap does not label GOAL-10B.1 coverage repair gate as implemented_review_only")
    if "GOAL-DATA-LABEL-01 Forward-Return Label Coverage" not in full_roadmap or "implemented_review_only" not in full_roadmap:
        failures.append("full roadmap does not label GOAL-DATA-LABEL-01 forward-return label coverage as implemented_review_only")
    if "GOAL-DATA-PROVIDER-02A Multi-Provider Capability Probe" not in full_roadmap or "implemented_review_only" not in full_roadmap:
        failures.append("full roadmap does not label GOAL-DATA-PROVIDER-02A provider capability probe as implemented_review_only")
    if "GOAL-DATA-PROVIDER-02A.1 Network Opt-In Provider Smoke Test" not in full_roadmap or "implemented_review_only" not in full_roadmap:
        failures.append("full roadmap does not label GOAL-DATA-PROVIDER-02A.1 network opt-in smoke test as implemented_review_only")
    if "DQN/RL Optional Research Benchmark" not in full_roadmap or "deleted_from_active_mainline" not in full_roadmap:
        failures.append("full roadmap does not label DQN/RL as deleted_from_active_mainline")
    if "GOAL-RISK-TIERING-01 Risk Severity Numeric Score Tiering" not in full_roadmap or "implemented_review_only" not in full_roadmap:
        failures.append("full roadmap does not label GOAL-RISK-TIERING-01 risk tiering as implemented_review_only")
    if "GOAL-RISK-TIERING-01.1 Downside Risk Repair" not in full_roadmap or "implemented_review_only" not in full_roadmap:
        failures.append("full roadmap does not label GOAL-RISK-TIERING-01.1 downside risk repair as implemented_review_only")
    if "GOAL-QUANT-RESEARCH-01 Factor Research Lab" not in full_roadmap or "implemented_research_only" not in full_roadmap:
        failures.append("full roadmap does not label GOAL-QUANT-RESEARCH-01 factor research lab as implemented_research_only")

    by_id = {row["workflow_id"]: row for row in rows}
    goal06c = by_id.get("goal06c_expanded_validation_ranking", {})
    goal06c5 = by_id.get("goal06c5_engineering_data_coverage_storage_panel_expansion", {})
    goal06c6 = by_id.get("goal06c6_source_backed_engineering_pilot_bundle", {})
    goal06c6a = by_id.get("goal06c6a_scoped_finance_network_failure_taxonomy", {})
    goal06c7 = by_id.get("goal06c7_provider_ladder_browser_assisted_engineering_data_base_expansion", {})
    goal06c_status = goal06c.get("status")
    goal06c5_status = goal06c5.get("status")
    goal06c6_status = goal06c6.get("status")
    goal06c6a_status = goal06c6a.get("status")
    goal06c7_status = goal06c7.get("status")
    goal06d = by_id.get("goal06d_model_comparison_calibration", {})
    goal06d1 = by_id.get("goal06d1_calibration_stability_warning_repair", {})
    goal06d_status = goal06d.get("status")
    goal06d1_status = goal06d1.get("status")
    goal06d_readiness = _read(root / "outputs/audits/goal06d_readiness_report.md")
    goal06d1_readiness = _read(root / "outputs/audits/goal06d1_readiness_report.md")
    goal06c7_readiness = _read(root / "outputs/audits/goal06c7_readiness_report.md")
    goal06c7_engineering_pilot_pass = _goal06c7_engineering_pilot_pass(goal06c7_readiness)
    if goal06c_status not in {"future_review_only", "implemented_review_only"}:
        failures.append("GOAL-06C block must be future_review_only or implemented_review_only")
    if goal06c_status == "implemented_review_only":
        readiness = _read(root / "outputs/audits/stage6c_readiness_report.md")
        if "GOAL-06C Expanded Validation Readiness: PASS" not in readiness:
            failures.append("GOAL-06C is implemented_review_only without a PASS/PASS_WITH_WARNINGS readiness report")
        if "implemented_review_only" not in full_roadmap:
            failures.append("full roadmap does not label GOAL-06C as implemented_review_only")
    elif "next_allowed_goal_review_only" not in goal06c.get("allowed_next_action", ""):
        failures.append("next allowed goal is not clearly GOAL-06C review-only expanded validation")
    if goal06c5_status != "implemented_review_only":
        failures.append("GOAL-06C.5 must be implemented_review_only")
    else:
        readiness = _read(root / "outputs/audits/engineering_panel_readiness_report.md")
        if "Engineering Panel Readiness: PASS_WITH_WARNINGS" not in readiness and "Engineering Panel Readiness: PASS" not in readiness:
            failures.append("GOAL-06C.5 is implemented_review_only without a PASS/PASS_WITH_WARNINGS engineering panel readiness report")
        goal06d_blocked = "GOAL-06D allowed to proceed: false" in readiness
        goal06d_review_only_after_pilot = "GOAL-06D allowed to proceed: true" in readiness and goal06c7_engineering_pilot_pass
        if not goal06d_blocked and not goal06d_review_only_after_pilot:
            failures.append("GOAL-06C.5 must keep GOAL-06D blocked unless GOAL-06C.7 proves engineering_pilot readiness")
        if "GOAL-06C.5" not in full_roadmap:
            failures.append("full roadmap does not include GOAL-06C.5")
    if goal06c6_status != "implemented_review_only":
        failures.append("GOAL-06C.6 must be implemented_review_only")
    else:
        readiness = _read(root / "outputs/audits/goal06c6_readiness_report.md")
        if "GOAL-06C.6 Source-Backed Engineering Pilot Bundle Readiness:" not in readiness:
            failures.append("GOAL-06C.6 is implemented_review_only without a readiness report")
        if "Default GOAL-06C.6 AKShare provider ingestion used no browser automation" not in readiness:
            failures.append("GOAL-06C.6 readiness report must state the default AKShare path did not use browser automation")
        if "GOAL-06C.6" not in full_roadmap:
            failures.append("full roadmap does not include GOAL-06C.6")
    if goal06c6a_status != "implemented_review_only":
        failures.append("GOAL-06C.6A must be implemented_review_only")
    else:
        summary = _read(root / "outputs/audits/provider_failure_summary.md")
        network_report = _read(root / "outputs/audits/goal06c6_network_isolation_report.md")
        taxonomy_report = _read(root / "outputs/audits/goal06c6_failure_taxonomy_report.md")
        if "GOAL-06C.6A Network Isolation and Failure Taxonomy Readiness:" not in summary:
            failures.append("GOAL-06C.6A is implemented_review_only without a provider failure summary")
        if "System proxy inheritance allowed: `false`" not in network_report:
            failures.append("GOAL-06C.6A network report must prove proxy inheritance is not allowed")
        if "NETWORK_ERROR" in taxonomy_report:
            failures.append("GOAL-06C.6A taxonomy report must not use generic NETWORK_ERROR")
        if "GOAL-06C.6A" not in full_roadmap:
            failures.append("full roadmap does not include GOAL-06C.6A")
    if goal06c7_status != "implemented_review_only":
        failures.append("GOAL-06C.7 must be implemented_review_only")
    else:
        readiness = goal06c7_readiness
        browser_audit = _read(root / "outputs/audits/browser_assisted_provider_audit.md")
        cleanliness = _read(root / "outputs/audits/workflow_cleanliness_audit.md")
        if "GOAL-06C.7 Engineering Data Base Expansion Readiness:" not in readiness:
            failures.append("GOAL-06C.7 is implemented_review_only without a readiness report")
        if "Browser assisted project default: `false`" not in browser_audit:
            failures.append("GOAL-06C.7 browser audit must prove browser-assisted provider is disabled by default")
        if "Workflow Cleanliness Audit:" not in cleanliness:
            failures.append("GOAL-06C.7 workflow cleanliness audit is missing")
        if "GOAL-06C.7" not in full_roadmap:
            failures.append("full roadmap does not include GOAL-06C.7")
    if goal06d_status == "future_review_only":
        if "engineering_pilot" not in goal06d.get("allowed_next_action", ""):
            failures.append("GOAL-06D future row must wait for GOAL-06C.7 engineering_pilot readiness")
    elif goal06d_status == "implemented_review_only":
        if not _goal06d_readiness_implemented(goal06d_readiness):
            failures.append("GOAL-06D is implemented_review_only without PASS/PASS_WITH_WARNINGS readiness evidence")
        expected_next = (
            "prepare_goal07a_risk_overlay_design_only"
            if "GOAL-06D Model Comparison Calibration Readiness: PASS\n" in goal06d_readiness
            else "fix_goal06d_model_stability_or_calibration_warnings"
        )
        if goal06d.get("allowed_next_action") != expected_next:
            failures.append("GOAL-06D allowed_next_action does not match readiness status")
    else:
        failures.append("GOAL-06D must be future_review_only or implemented_review_only")
    if goal06d1:
        if goal06d1_status != "implemented_review_only":
            failures.append("GOAL-06D.1 must be implemented_review_only when present")
        if not _goal06d1_readiness_implemented(goal06d1_readiness):
            failures.append("GOAL-06D.1 is implemented_review_only without PASS/PASS_WITH_WARNINGS readiness evidence")
        if goal06d1.get("allowed_next_action") not in {
            "prepare_goal07a_risk_overlay_design_only",
            "proceed_to_goal07a_design_only_with_warnings",
            "continue_goal06d_warning_repair",
        }:
            failures.append("GOAL-06D.1 allowed_next_action is invalid")
    v2_factor = by_id.get("v2_factor_research_upgrade", {})
    if v2_factor and v2_factor.get("status") != "planned_locked":
        failures.append("V2 factor research upgrade must remain planned_locked")
    goal07a = by_id.get("goal07a_risk_overlay_design", {})
    goal07a_status = goal07a.get("status")
    goal07a_readiness = _read(root / "outputs/audits/goal07a_readiness_report.md")
    goal07a1 = by_id.get("goal07a1_risk_overlay_design_review_unlock_readiness", {})
    goal07a1_status = goal07a1.get("status")
    goal07a1_readiness = _read(root / "outputs/audits/goal07a1_design_review_report.md")
    goal07b0 = by_id.get("goal07b0_risk_overlay_review_only_unlock_gate", {})
    goal07b0_status = goal07b0.get("status")
    goal07b0_report = _read(root / "outputs/audits/goal07b0_unlock_gate_report.md")
    goal07b0_audit = _read(root / "outputs/audits/goal07b0_unlock_gate_audit_report.md")
    goal07b = by_id.get(GOAL07B_WORKFLOW_ID, {})
    goal07b_status = goal07b.get("status")
    goal07b_report = _read(root / "outputs/audits/goal07b_risk_overlay_calculation_report.md")
    goal07b_manifest = _read(root / "outputs/audits/goal07b_risk_overlay_calculation_manifest.json")
    goal07b_audit = _read(root / "outputs/audits/goal07b_risk_overlay_calculation_audit.md")
    goal08a = by_id.get(GOAL08A_WORKFLOW_ID, {})
    goal08a_status = goal08a.get("status")
    goal08a_report = _read(root / "outputs/audits/goal08a_recommendation_contract_design_report.md")
    goal08a_manifest = _read(root / "outputs/audits/goal08a_recommendation_contract_design_manifest.json")
    goal08a_audit = _read(root / "outputs/audits/goal08a_recommendation_contract_design_audit.md")
    goal_storage01 = by_id.get(GOAL_STORAGE01_WORKFLOW_ID, {})
    goal_storage01_status = goal_storage01.get("status")
    goal_storage01_report = _read(root / "outputs/audits/goal_storage01_local_research_lake_hardening_report.md")
    goal_storage01_manifest = _read(root / "outputs/audits/goal_storage01_local_research_lake_hardening_manifest.json")
    goal_storage01_audit = _read(root / "outputs/audits/goal_storage01_local_research_lake_hardening_audit.md")
    goal08b0 = by_id.get(GOAL08B0_WORKFLOW_ID, {})
    goal08b0_status = goal08b0.get("status")
    goal08b0_report = _read(root / "outputs/audits/goal08b0_recommendation_review_only_unlock_report.md")
    goal08b0_manifest = _read(root / "outputs/audits/goal08b0_recommendation_review_only_unlock_manifest.json")
    goal08b0_audit = _read(root / "outputs/audits/goal08b0_recommendation_review_only_unlock_audit.md")
    goal08b = by_id.get(GOAL08B_WORKFLOW_ID, {})
    goal08b_status = goal08b.get("status")
    goal08b_report = _read(root / "outputs/audits/goal08b_recommendation_diagnostics_report.md")
    goal08b_manifest = _read(root / "outputs/audits/goal08b_recommendation_diagnostics_manifest.json")
    goal08b_audit = _read(root / "outputs/audits/goal08b_recommendation_diagnostics_audit.md")
    goal090 = by_id.get(GOAL090_WORKFLOW_ID, {})
    goal090_status = goal090.get("status")
    goal090_report = _read(root / "outputs/audits/goal090_position_band_review_only_unlock_report.md")
    goal090_manifest = _read(root / "outputs/audits/goal090_position_band_review_only_unlock_manifest.json")
    goal090_audit = _read(root / "outputs/audits/goal090_position_band_review_only_unlock_audit.md")
    goal09 = by_id.get(GOAL09_WORKFLOW_ID, {})
    goal09_status = goal09.get("status")
    goal09_report = _read(root / "outputs/audits/goal09_position_band_diagnostics_report.md")
    goal09_manifest = _read(root / "outputs/audits/goal09_position_band_diagnostics_manifest.json")
    goal09_audit = _read(root / "outputs/audits/goal09_position_band_diagnostics_audit.md")
    goal091 = by_id.get(GOAL091_WORKFLOW_ID, {})
    goal091_status = goal091.get("status")
    goal091_report = _read(root / "outputs/audits/goal091_dashboard_readiness_report.md")
    goal091_manifest = _read(root / "outputs/audits/goal091_dashboard_readiness_manifest.json")
    goal091_audit = _read(root / "outputs/audits/goal091_dashboard_readiness_audit.md")
    goal_v1_integrity01 = by_id.get(GOAL_V1_INTEGRITY01_WORKFLOW_ID, {})
    goal_v1_integrity01_status = goal_v1_integrity01.get("status")
    goal_v1_integrity01_report = _read(root / "outputs/audits/goal_v1_integrity01_artifact_lineage_structure_report.md")
    goal_v1_integrity01_manifest = _read(root / "outputs/audits/goal_v1_integrity01_artifact_lineage_structure_manifest.json")
    goal_v1_integrity01_audit = _read(root / "outputs/audits/goal_v1_integrity01_artifact_lineage_structure_audit.md")
    goal10a = by_id.get(GOAL10A_WORKFLOW_ID, {})
    goal10a_status = goal10a.get("status")
    goal10a_report = _read(root / "outputs/audits/goal10a_backtest_contract_design_report.md")
    goal10a_manifest = _read(root / "outputs/audits/goal10a_backtest_contract_design_manifest.json")
    goal10a_audit = _read(root / "outputs/audits/goal10a_backtest_contract_design_audit.md")
    goal10b = by_id.get(GOAL10B_WORKFLOW_ID, {})
    goal10b_status = goal10b.get("status")
    goal10b_report = _read(root / "outputs/audits/goal10b_recommendation_backtest_report.md")
    goal10b_manifest = _read(root / "outputs/audits/goal10b_recommendation_backtest_manifest.json")
    goal10b_audit = _read(root / "outputs/audits/goal10b_recommendation_backtest_audit.md")
    goal10b1 = by_id.get(GOAL10B1_WORKFLOW_ID, {})
    goal10b1_status = goal10b1.get("status")
    goal10b1_report = _read(root / "outputs/audits/goal10b1_backtest_coverage_repair_report.md")
    goal10b1_manifest = _read(root / "outputs/audits/goal10b1_backtest_coverage_repair_manifest.json")
    goal10b1_audit = _read(root / "outputs/audits/goal10b1_backtest_coverage_repair_audit.md")
    goal_data_label01 = by_id.get(GOAL_DATA_LABEL01_WORKFLOW_ID, {})
    goal_data_label01_status = goal_data_label01.get("status")
    goal_data_label01_report = _read(root / "outputs/audits/goal_data_label01_forward_return_label_coverage_report.md")
    goal_data_label01_manifest = _read(root / "outputs/audits/goal_data_label01_forward_return_label_coverage_manifest.json")
    goal_data_label01_audit = _read(root / "outputs/audits/goal_data_label01_forward_return_label_coverage_audit.md")
    goal_v1_diagnostic_coverage02 = by_id.get(GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID, {})
    goal_v1_diagnostic_coverage02_status = goal_v1_diagnostic_coverage02.get("status")
    goal_v1_diagnostic_coverage02_report = _read(root / "outputs/audits/goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_report.md")
    goal_v1_diagnostic_coverage02_manifest = _read(root / "outputs/audits/goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_manifest.json")
    goal_v1_diagnostic_coverage02_audit = _read(root / "outputs/audits/goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_audit.md")
    goal10b2 = by_id.get(GOAL10B2_WORKFLOW_ID, {})
    goal10b2_status = goal10b2.get("status")
    goal10b2_report = _read(root / "outputs/audits/goal10b2_recommendation_backtest_revalidation_report.md")
    goal10b2_manifest = _read(root / "outputs/audits/goal10b2_recommendation_backtest_revalidation_manifest.json")
    goal10b2_audit = _read(root / "outputs/audits/goal10b2_recommendation_backtest_revalidation_audit.md")
    goal10c = by_id.get(GOAL10C_WORKFLOW_ID, {})
    goal10c_status = goal10c.get("status")
    goal10c_report = _read(root / "outputs/audits/goal10c_cost_slippage_sensitivity_report.md")
    goal10c_manifest = _read(root / "outputs/audits/goal10c_cost_slippage_sensitivity_manifest.json")
    goal10c_audit = _read(root / "outputs/audits/goal10c_cost_slippage_sensitivity_audit.md")
    goal_data_provider02a = by_id.get(GOAL_DATA_PROVIDER02A_WORKFLOW_ID, {})
    goal_data_provider02a_status = goal_data_provider02a.get("status")
    goal_data_provider02a_report = _read(root / "outputs/audits/goal_data_provider02a_multi_provider_capability_probe_report.md")
    goal_data_provider02a_manifest = _read(root / "outputs/audits/goal_data_provider02a_multi_provider_capability_probe_manifest.json")
    goal_data_provider02a_audit = _read(root / "outputs/audits/goal_data_provider02a_multi_provider_capability_probe_audit.md")
    goal_data_provider02a1 = by_id.get(GOAL_DATA_PROVIDER02A1_WORKFLOW_ID, {})
    goal_data_provider02a1_status = goal_data_provider02a1.get("status")
    goal_data_provider02a1_report = _read(root / "outputs/audits/goal_data_provider02a1_network_smoke_test_report.md")
    goal_data_provider02a1_manifest = _read(root / "outputs/audits/goal_data_provider02a1_network_smoke_test_manifest.json")
    goal_data_provider02a1_audit = _read(root / "outputs/audits/goal_data_provider02a1_network_smoke_test_audit.md")
    goal_data_provider02b = by_id.get(GOAL_DATA_PROVIDER02B_WORKFLOW_ID, {})
    goal_data_provider02b_status = goal_data_provider02b.get("status")
    goal_data_provider02b_report = _read(root / "outputs/audits/goal_data_provider02b_source_backed_panel_report.md")
    goal_data_provider02b_manifest = _read(root / "outputs/audits/goal_data_provider02b_source_backed_panel_manifest.json")
    goal_data_provider02b_audit = _read(root / "outputs/audits/goal_data_provider02b_source_backed_panel_audit.md")
    goal_data_panel02 = by_id.get(GOAL_DATA_PANEL02_WORKFLOW_ID, {})
    goal_v1_diagnostic_coverage03 = by_id.get(GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID, {})
    goal_v1_diagnostic_coverage03_status = goal_v1_diagnostic_coverage03.get("status")
    goal_v1_diagnostic_coverage03_report = _read(root / "outputs/audits/goal_v1_diagnostic_coverage03_source_backed_diagnostics_report.md")
    goal_v1_diagnostic_coverage03_manifest = _read(root / "outputs/audits/goal_v1_diagnostic_coverage03_source_backed_diagnostics_manifest.json")
    goal_v1_diagnostic_coverage03_audit = _read(root / "outputs/audits/goal_v1_diagnostic_coverage03_source_backed_diagnostics_audit.md")
    goal10b3 = by_id.get(GOAL10B3_WORKFLOW_ID, {})
    goal10b3_status = goal10b3.get("status")
    goal10b3_report = _read(root / "outputs/audits/goal10b3_dc03_recommendation_revalidation_report.md")
    goal10b3_manifest = _read(root / "outputs/audits/goal10b3_dc03_recommendation_revalidation_manifest.json")
    goal10b3_audit = _read(root / "outputs/audits/goal10b3_dc03_recommendation_revalidation_audit.md")
    goal_risk_tiering01 = by_id.get(GOAL_RISK_TIERING01_WORKFLOW_ID, {})
    goal_risk_tiering01_status = goal_risk_tiering01.get("status")
    goal_risk_tiering01_report = _read(root / "outputs/audits/goal_risk_tiering01_risk_tiering_report.md")
    goal_risk_tiering01_manifest = _read(root / "outputs/audits/goal_risk_tiering01_risk_tiering_manifest.json")
    goal_risk_tiering01_audit = _read(root / "outputs/audits/goal_risk_tiering01_risk_tiering_audit.md")
    goal_risk_tiering011 = by_id.get(GOAL_RISK_TIERING011_WORKFLOW_ID, {})
    goal_risk_tiering011_status = goal_risk_tiering011.get("status")
    goal_risk_tiering011_report = _read(root / "outputs/audits/goal_risk_tiering011_downside_risk_repair_report.md")
    goal_risk_tiering011_manifest = _read(root / "outputs/audits/goal_risk_tiering011_downside_risk_repair_manifest.json")
    goal_risk_tiering011_audit = _read(root / "outputs/audits/goal_risk_tiering011_downside_risk_repair_audit.md")
    goal_quant_research01 = by_id.get(GOAL_QUANT_RESEARCH01_WORKFLOW_ID, {})
    goal_quant_research01_status = goal_quant_research01.get("status")
    goal_quant_research01_report = _read(root / "outputs/audits/goal_quant_research01_factor_research_lab_report.md")
    goal_quant_research01_manifest = _read(root / "outputs/audits/goal_quant_research01_factor_research_lab_manifest.json")
    goal_quant_research01_audit = _read(root / "outputs/audits/goal_quant_research01_factor_research_lab_audit.md")
    goal_rec_tiering01 = by_id.get(GOAL_REC_TIERING01_WORKFLOW_ID, {})
    goal10b4 = by_id.get(GOAL10B4_WORKFLOW_ID, {})
    position_band_validation = by_id.get(POSITION_BAND_VALIDATION_WORKFLOW_ID, {})
    goal10d = by_id.get(GOAL10D_WORKFLOW_ID, {})
    goal08b0_evidence_ready = bool(goal08b0) and goal08b0_status == "implemented_review_only" and _goal08b0_readiness_implemented(goal08b0_report) and "Status: `PASS`" in goal08b0_audit
    goal08b_evidence_ready = bool(goal08b) and goal08b_status == "implemented_review_only" and _goal08b_readiness_implemented(goal08b_report) and "Status: `PASS`" in goal08b_audit
    goal090_evidence_ready = bool(goal090) and goal090_status == "implemented_review_only" and _goal090_readiness_implemented(goal090_report) and "Status: `PASS`" in goal090_audit
    goal09_evidence_ready = bool(goal09) and goal09_status == "implemented_review_only" and _goal09_readiness_implemented(goal09_report) and "Status: `PASS`" in goal09_audit
    goal091_evidence_ready = bool(goal091) and goal091_status == "implemented_review_only" and _goal091_readiness_implemented(goal091_report) and "Status: `PASS`" in goal091_audit
    goal_v1_integrity01_evidence_ready = (
        bool(goal_v1_integrity01)
        and goal_v1_integrity01_status == "implemented_infrastructure_only"
        and _goal_v1_integrity01_readiness_implemented(goal_v1_integrity01_report)
        and "Status: `PASS`" in goal_v1_integrity01_audit
    )
    goal10b_evidence_ready = (
        bool(goal10b)
        and goal10b_status == "implemented_review_only"
        and _goal10b_readiness_implemented(goal10b_report)
        and "Status: `PASS`" in goal10b_audit
    )
    goal10b1_evidence_ready = (
        bool(goal10b1)
        and goal10b1_status == "implemented_review_only"
        and _goal10b1_readiness_implemented(goal10b1_report)
        and "Status: `PASS`" in goal10b1_audit
    )
    goal_data_label01_evidence_ready = (
        bool(goal_data_label01)
        and goal_data_label01_status == "implemented_review_only"
        and _goal_data_label01_readiness_implemented(goal_data_label01_report)
        and "Status: `PASS`" in goal_data_label01_audit
    )
    goal_v1_diagnostic_coverage02_evidence_ready = (
        bool(goal_v1_diagnostic_coverage02)
        and goal_v1_diagnostic_coverage02_status == "implemented_review_only"
        and _goal_v1_diagnostic_coverage02_readiness_implemented(goal_v1_diagnostic_coverage02_report)
        and "Status: `PASS`" in goal_v1_diagnostic_coverage02_audit
    )
    goal10b2_evidence_ready = (
        bool(goal10b2)
        and goal10b2_status == "implemented_review_only"
        and _goal10b2_readiness_implemented(goal10b2_report)
        and "Status: `PASS`" in goal10b2_audit
    )
    goal10c_evidence_ready = (
        bool(goal10c)
        and goal10c_status == "implemented_review_only"
        and _goal10c_readiness_implemented(goal10c_report)
        and "Status: `PASS`" in goal10c_audit
    )
    goal_data_provider02a_evidence_ready = (
        bool(goal_data_provider02a)
        and goal_data_provider02a_status == "implemented_review_only"
        and _goal_data_provider02a_readiness_implemented(goal_data_provider02a_report)
        and "Status: `PASS`" in goal_data_provider02a_audit
    )
    goal_data_provider02a1_evidence_ready = (
        bool(goal_data_provider02a1)
        and goal_data_provider02a1_status == "implemented_review_only"
        and _goal_data_provider02a1_readiness_implemented(goal_data_provider02a1_report)
        and "Status: `PASS`" in goal_data_provider02a1_audit
    )
    goal_data_provider02b_evidence_ready = (
        bool(goal_data_provider02b)
        and goal_data_provider02b_status == "implemented_review_only"
        and _goal_data_provider02b_readiness_implemented(goal_data_provider02b_report)
        and "Status: `PASS`" in goal_data_provider02b_audit
    )
    goal_v1_diagnostic_coverage03_evidence_ready = (
        bool(goal_v1_diagnostic_coverage03)
        and goal_v1_diagnostic_coverage03_status == "implemented_review_only"
        and _goal_v1_diagnostic_coverage03_readiness_implemented(goal_v1_diagnostic_coverage03_report)
        and "Status: `PASS`" in goal_v1_diagnostic_coverage03_audit
    )
    goal10b3_evidence_ready = (
        bool(goal10b3)
        and goal10b3_status == "implemented_review_only"
        and _goal10b3_readiness_implemented(goal10b3_report)
        and "Status: `PASS`" in goal10b3_audit
    )
    goal_risk_tiering01_evidence_ready = (
        bool(goal_risk_tiering01)
        and goal_risk_tiering01_status == "implemented_review_only"
        and _goal_risk_tiering01_readiness_implemented(goal_risk_tiering01_report)
        and "Status: `PASS`" in goal_risk_tiering01_audit
    )
    goal_risk_tiering011_evidence_ready = (
        bool(goal_risk_tiering011)
        and goal_risk_tiering011_status == "implemented_review_only"
        and _goal_risk_tiering011_readiness_implemented(goal_risk_tiering011_report)
        and "Status: `PASS`" in goal_risk_tiering011_audit
    )
    goal_quant_research01_evidence_ready = (
        bool(goal_quant_research01)
        and goal_quant_research01_status == "implemented_research_only"
        and _goal_quant_research01_readiness_implemented(goal_quant_research01_report)
        and "Status: `PASS`" in goal_quant_research01_audit
    )
    goal10c_expected_dependency = (
        GOAL10B2_WORKFLOW_ID
        if goal_data_label01_evidence_ready
        else GOAL10B1_WORKFLOW_ID
        if goal10b1_evidence_ready
        else GOAL10B_WORKFLOW_ID
    )
    if goal07a_status == "future_design_only":
        if goal07a.get("allowed_next_action") not in {
            "prepare_design_only_after_goal06d1_warning_repair",
            "block_goal07b_until_goal07a_pass",
        }:
            failures.append("GOAL-07A future row has invalid allowed_next_action")
    elif goal07a_status == "implemented_design_only":
        if not _goal07a_readiness_implemented(goal07a_readiness):
            failures.append("GOAL-07A is implemented_design_only without PASS/PASS_WITH_WARNINGS readiness evidence")
        if goal07a.get("allowed_next_action") not in {
            "prepare_goal07b_risk_overlay_calculation_prototype_after_explicit_unlock",
            "prepare_goal07b_design_review_or_fix_goal07a_warnings",
        }:
            failures.append("GOAL-07A implemented design row has invalid allowed_next_action")
        required_goal07a_audits = [
            "outputs/audits/goal07a_allowed_input_contract_audit.md",
            "outputs/audits/goal07a_output_schema_audit.md",
            "outputs/audits/goal07a_risk_rule_catalog_audit.md",
            "outputs/audits/goal07a_state_machine_audit.md",
            "outputs/audits/goal07a_upstream_warning_mapping_audit.md",
            "outputs/audits/goal07a_governance_boundary_audit.md",
            "outputs/audits/goal07a_boundary_lock_audit.md",
            "outputs/audits/goal07a_v2_factor_lock_audit.md",
        ]
        for audit_path in required_goal07a_audits:
            if "Status: `PASS`" not in _read(root / audit_path):
                failures.append(f"GOAL-07A audit is missing or not PASS: {audit_path}")
    else:
        failures.append("GOAL-07A must be future_design_only or implemented_design_only")
    if goal07a1:
        if goal07a1_status != "implemented_review_only":
            failures.append("GOAL-07A.1 must be implemented_review_only when present")
        if not _goal07a1_readiness_implemented(goal07a1_readiness):
            failures.append("GOAL-07A.1 is implemented_review_only without PASS/PASS_WITH_WARNINGS design review evidence")
        if (
            "GOAL-07B remains: locked_future" not in goal07a1_readiness
            and "GOAL-07B remains: future_review_only" not in goal07a1_readiness
            and "GOAL-07B remains: implemented_review_only" not in goal07a1_readiness
        ):
            failures.append("GOAL-07A.1 report must keep GOAL-07B locked, future_review_only eligible, or implemented_review_only")
        if goal07a1.get("allowed_next_action") not in {
            "request_explicit_goal07b_review_only_unlock",
            "repair_goal07a_design_review_warnings_before_goal07b",
            "block_goal07b_due_to_boundary_violation",
        }:
            failures.append("GOAL-07A.1 allowed_next_action is invalid")
        required_goal07a1_audits = [
            "outputs/audits/goal07a1_input_contract_readiness_audit.md",
            "outputs/audits/goal07a1_forbidden_schema_overlap_audit.md",
            "outputs/audits/goal07a1_rule_convertibility_audit.md",
            "outputs/audits/goal07a1_state_machine_review_audit.md",
            "outputs/audits/goal07a1_boundary_lock_audit.md",
        ]
        for audit_path in required_goal07a1_audits:
            if "Status: `PASS`" not in _read(root / audit_path):
                failures.append(f"GOAL-07A.1 audit is missing or not PASS: {audit_path}")
    if goal07b0:
        if goal07b0_status != "implemented_review_only":
            failures.append("GOAL-07B.0 must be implemented_review_only when present")
        if not _goal07b0_readiness_implemented(goal07b0_report):
            failures.append("GOAL-07B.0 is implemented_review_only without PASS/PASS_WITH_WARNINGS unlock evidence")
        if "Status: `PASS`" not in goal07b0_audit:
            failures.append("GOAL-07B.0 unlock audit report is missing or not PASS")
        if goal07b0.get("allowed_next_action") not in {
            "future_goal07b_review_only_calculation_prototype_may_be_requested",
            "repair_goal07b0_unlock_blockers",
        }:
            failures.append("GOAL-07B.0 allowed_next_action is invalid")
    if goal07b_status not in GOAL07B_ALLOWED_STATUSES:
        failures.append("GOAL-07B must be locked_future, future_review_only, or implemented_review_only")
    if goal07b_status == "future_review_only":
        if not goal07b0 or goal07b0_status != "implemented_review_only":
            failures.append("GOAL-07B future_review_only status requires GOAL-07B.0 implemented_review_only gate")
        if not _goal07b0_readiness_implemented(goal07b0_report):
            failures.append("GOAL-07B future_review_only status lacks GOAL-07B.0 PASS/PASS_WITH_WARNINGS evidence")
        if goal07b.get("implemented_in_repo") != "false":
            failures.append("GOAL-07B future_review_only must not be marked implemented")
        if goal07b.get("allowed_next_action") != "await_explicit_goal07b_review_only_calculation_prototype":
            failures.append("GOAL-07B future_review_only allowed_next_action is invalid")
    elif goal07b_status == "implemented_review_only":
        if not _goal07b_readiness_implemented(goal07b_report):
            failures.append("GOAL-07B implemented_review_only lacks PASS/PASS_WITH_WARNINGS calculation evidence")
        if "Status: `PASS`" not in goal07b_audit:
            failures.append("GOAL-07B calculation audit report is missing or not PASS")
        if '"mode": "review_only"' not in goal07b_manifest:
            failures.append("GOAL-07B manifest must state review_only mode")
        for required_false in [
            '"recommendation_generated": false',
            '"position_generated": false',
            '"dashboard_generated": false',
            '"paper_live_trading_generated": false',
            '"trading_generated": false',
            '"production_generated": false',
            '"backtest_generated": false',
            '"factor_mining_generated": false',
            '"dqn_rl_generated": false',
        ]:
            if required_false not in goal07b_manifest:
                failures.append(f"GOAL-07B manifest missing false boundary flag: {required_false}")
        if goal07b.get("implemented_in_repo") != "true":
            failures.append("GOAL-07B implemented_review_only must be marked implemented")
        if goal07b.get("allowed_next_action") != "prepare_goal08a_recommendation_contract_design_gate_or_fix_goal07b_warnings":
            failures.append("GOAL-07B implemented_review_only allowed_next_action is invalid")
    elif goal07b_status == "locked_future" and goal07b.get("implemented_in_repo") == "true":
        failures.append("GOAL-07B locked_future must not be marked implemented")

    if goal08a_status not in GOAL08A_ALLOWED_STATUSES:
        failures.append("GOAL-08A must be locked_future or implemented_design_only")
    if goal08a_status == "implemented_design_only":
        if not _goal08a_readiness_implemented(goal08a_report):
            failures.append("GOAL-08A implemented_design_only lacks PASS/PASS_WITH_WARNINGS design evidence")
        if "Status: `PASS`" not in goal08a_audit:
            failures.append("GOAL-08A design audit report is missing or not PASS")
        for required_false in [
            '"recommendation_rows_generated": false',
            '"buy_sell_hold_outputs_generated": false',
            '"target_prices_generated": false',
            '"position_sizing_generated": false',
            '"portfolio_construction_generated": false',
            '"dashboard_generated": false',
            '"paper_trading_enabled": false',
            '"live_trading_enabled": false',
            '"broker_integration_enabled": false',
            '"production_model_behavior_created": false',
            '"database_writes_created": false',
            '"backtests_run": false',
            '"factor_mining_outputs_created": false',
            '"dqn_rl_outputs_created": false',
            '"actionable_outputs_generated": false',
        ]:
            if required_false not in goal08a_manifest:
                failures.append(f"GOAL-08A manifest missing false boundary flag: {required_false}")
        for required_text in [
            '"mode": "design_only"',
            '"input_grain": "trade_date + symbol"',
            '"future_schema_row_count": 0',
            '"high_risk_severity_blocks_actionable_output": true',
            '"goal08b_status_after_goal08a": "locked_future"',
        ]:
            if required_text not in goal08a_manifest:
                failures.append(f"GOAL-08A manifest missing required design marker: {required_text}")
        if goal08a.get("implemented_in_repo") != "true":
            failures.append("GOAL-08A implemented_design_only must be marked implemented")
        if goal08a.get("allowed_next_action") not in {
            "request_explicit_goal08b_review_only_prototype_or_fix_goal08a_warnings",
            "repair_goal08a_design_gate_blockers",
        }:
            failures.append("GOAL-08A implemented design row has invalid allowed_next_action")
        if goal08b_evidence_ready:
            if goal08b.get("implemented_in_repo") != "true":
                failures.append("GOAL-08B implemented diagnostics must be marked implemented")
        elif goal08b.get("implemented_in_repo") != "false":
            failures.append("GOAL-08A must not mark GOAL-08B implemented without GOAL-08B evidence")
        elif goal08b0_evidence_ready:
            if goal08b.get("status") != "future_review_only":
                failures.append("GOAL-08B must be future_review_only after GOAL-08B.0 evidence")
        elif goal08b.get("status") != "locked_future":
            failures.append("GOAL-08A must keep GOAL-08B locked_future until GOAL-08B.0 passes")
    elif goal08a_status == "locked_future" and goal08a.get("implemented_in_repo") == "true":
        failures.append("GOAL-08A locked_future must not be marked implemented")

    if goal_storage01:
        if goal_storage01_status != "implemented_infrastructure_only":
            failures.append("GOAL-STORAGE-01 must be implemented_infrastructure_only when present")
        if not _goal_storage01_readiness_implemented(goal_storage01_report):
            failures.append("GOAL-STORAGE-01 lacks PASS local research lake hardening evidence")
        if "Status: `PASS`" not in goal_storage01_audit:
            failures.append("GOAL-STORAGE-01 audit report is missing or not PASS")
        for required_false in [
            '"source_coverage_expanded": false',
            '"symbol_coverage_expanded": false',
            '"full_market_fetch_performed": false',
            '"live_data_fetch_performed": false',
            '"raw_provider_payloads_committed": false',
            '"duckdb_or_parquet_files_committed": false',
            '"recommendation_rows_generated": false',
            '"buy_sell_hold_outputs_generated": false',
            '"position_sizing_generated": false',
            '"portfolio_construction_generated": false',
            '"dashboard_generated": false',
            '"paper_trading_enabled": false',
            '"live_trading_enabled": false',
            '"broker_integration_enabled": false',
            '"production_model_behavior_created": false',
            '"database_writes_created": false',
            '"backtests_run": false',
            '"factor_mining_outputs_created": false',
            '"dqn_rl_outputs_created": false',
            '"workflow_downstream_unlocked": false',
        ]:
            if required_false not in goal_storage01_manifest:
                failures.append(f"GOAL-STORAGE-01 manifest missing false boundary flag: {required_false}")
        for required_text in [
            '"mode": "infrastructure_only"',
            '"workflow_status_after_pass": "implemented_infrastructure_only"',
            '"goal08b_status_after_goal_storage01": "locked_future"',
            '"goal08b_implemented_by_this_gate": false',
            '"goal08b_unlocked_by_this_gate": false',
            '"fallback_default_documentation_only": true',
            '"local_data_root_materialized_by_this_gate": false',
            '"local_data_files_created": false',
            '"tracked_forbidden_artifact_count": 0',
        ]:
            if required_text not in goal_storage01_manifest:
                failures.append(f"GOAL-STORAGE-01 manifest missing required infrastructure marker: {required_text}")
        if goal_storage01.get("implemented_in_repo") != "true":
            failures.append("GOAL-STORAGE-01 implemented infrastructure row must be marked implemented")
        if goal_storage01.get("allowed_next_action") not in {
            "request_explicit_goal08b_review_only_prototype_or_fix_storage_hardening_warnings",
            "repair_storage_hardening_blockers",
        }:
            failures.append("GOAL-STORAGE-01 allowed_next_action is invalid")
        if goal08b_evidence_ready:
            if goal08b.get("implemented_in_repo") != "true":
                failures.append("GOAL-08B implemented diagnostics must be marked implemented")
        elif goal08b.get("implemented_in_repo") != "false":
            failures.append("GOAL-STORAGE-01 must not mark GOAL-08B implemented without GOAL-08B evidence")
        elif goal08b0_evidence_ready:
            if goal08b.get("status") != "future_review_only":
                failures.append("GOAL-08B must be future_review_only after GOAL-08B.0 evidence")
        elif goal08b.get("status") != "locked_future":
            failures.append("GOAL-STORAGE-01 must keep GOAL-08B locked_future until GOAL-08B.0 passes")

    if goal08b0:
        if goal08b0_status != "implemented_review_only":
            failures.append("GOAL-08B.0 must be implemented_review_only when present")
        if not _goal08b0_readiness_implemented(goal08b0_report):
            failures.append("GOAL-08B.0 lacks PASS/PASS_WITH_WARNINGS unlock evidence")
        if "Status: `PASS`" not in goal08b0_audit:
            failures.append("GOAL-08B.0 unlock audit report is missing or not PASS")
        for required_false in [
            '"recommendation_diagnostics_rows_generated": false',
            '"recommendation_rows_generated": false',
            '"buy_sell_hold_outputs_generated": false',
            '"target_prices_generated": false',
            '"position_sizing_generated": false',
            '"portfolio_construction_generated": false',
            '"dashboard_generated": false',
            '"paper_trading_enabled": false',
            '"live_trading_enabled": false',
            '"broker_integration_enabled": false',
            '"production_model_behavior_created": false',
            '"database_writes_created": false',
            '"backtests_run": false',
            '"factor_mining_outputs_created": false',
            '"dqn_rl_outputs_created": false',
            '"actionable_outputs_generated": false',
            '"local_lake_files_created": false',
            '"data_coverage_expanded": false',
            '"live_calculation_outputs_used": false',
            '"downstream_stages_unlocked_by_this_gate": false',
        ]:
            if required_false not in goal08b0_manifest:
                failures.append(f"GOAL-08B.0 manifest missing false boundary flag: {required_false}")
        for required_text in [
            '"mode": "review_only_unlock_gate"',
            '"goal08b0_unlock_status": "eligible_for_future_review_only_prototype"',
            '"goal08b_implemented_by_this_gate": false',
            '"future_goal08b_input_contract_ready": true',
            '"high_risk_actionability_block_preserved": true',
            '"goal07b_warnings_propagate_to_future_diagnostics": true',
            '"future_recommendation_diagnostics_non_actionable_required": true',
            '"storage_prerequisite_ready": true',
        ]:
            if required_text not in goal08b0_manifest:
                failures.append(f"GOAL-08B.0 manifest missing required unlock marker: {required_text}")
        if goal08b0.get("implemented_in_repo") != "true":
            failures.append("GOAL-08B.0 implemented review-only row must be marked implemented")
        if goal08b0.get("allowed_next_action") not in {
            GOAL08B_ALLOWED_NEXT,
            GOAL08B_IMPLEMENTED_ALLOWED_NEXT,
            "repair_goal08b0_unlock_blockers",
        }:
            failures.append("GOAL-08B.0 allowed_next_action is invalid")

    if goal08b_status not in GOAL08B_ALLOWED_STATUSES:
        failures.append("GOAL-08B must be locked_future, future_review_only, or implemented_review_only")
    if goal08b_status == "future_review_only":
        if goal08b.get("implemented_in_repo") != "false":
            failures.append("GOAL-08B future_review_only must not be marked implemented")
        if not goal08b0_evidence_ready:
            failures.append("GOAL-08B future_review_only status requires GOAL-08B.0 PASS/PASS_WITH_WARNINGS evidence")
        if goal08b.get("allowed_next_action") != GOAL08B_ALLOWED_NEXT:
            failures.append("GOAL-08B future_review_only allowed_next_action is invalid")
        if goal08b.get("depends_on") != GOAL08B0_WORKFLOW_ID:
            failures.append("GOAL-08B future_review_only must depend on GOAL-08B.0")
    elif goal08b_status == "implemented_review_only":
        if not goal08b_evidence_ready:
            failures.append("GOAL-08B implemented_review_only status requires GOAL-08B PASS/PASS_WITH_WARNINGS evidence")
        if goal08b.get("implemented_in_repo") != "true":
            failures.append("GOAL-08B implemented_review_only must be marked implemented")
        if goal08b.get("allowed_next_action") != GOAL08B_IMPLEMENTED_ALLOWED_NEXT:
            failures.append("GOAL-08B implemented_review_only allowed_next_action is invalid")
        if goal08b.get("depends_on") != GOAL08B0_WORKFLOW_ID:
            failures.append("GOAL-08B implemented_review_only must depend on GOAL-08B.0")
        for required_text in [
            '"mode": "review_only"',
            '"output_grain": "trade_date + symbol"',
            '"diagnostic_rows_generated": true',
            '"recommendation_diagnostics_rows_generated": true',
            '"non_actionable": true',
            '"actionability_status_values": [',
            '"never_actionable"',
            '"actionable_recommendation_rows_generated": false',
            '"recommendation_rows_generated": false',
            '"buy_sell_hold_outputs_generated": false',
            '"target_prices_generated": false',
            '"expected_returns_for_action_generated": false',
            '"position_sizing_generated": false',
            '"portfolio_weights_generated": false',
            '"dashboard_generated": false',
            '"paper_trading_enabled": false',
            '"live_trading_enabled": false',
            '"broker_integration_enabled": false',
            '"production_model_behavior_created": false',
            '"database_writes_created": false',
            '"signal_backtests_run": false',
            '"portfolio_backtests_run": false',
            '"cost_slippage_outputs_created": false',
            '"factor_mining_outputs_created": false',
            '"local_lake_files_created": false',
            '"dqn_rl_outputs_created": false',
            '"downstream_stages_unlocked_by_this_goal": false',
        ]:
            if required_text not in goal08b_manifest:
                failures.append(f"GOAL-08B manifest missing required diagnostic marker: {required_text}")
    elif goal08b_status == "locked_future" and goal08b0_evidence_ready:
        failures.append("GOAL-08B should be future_review_only after GOAL-08B.0 evidence")

    if goal090:
        if goal090_status != "implemented_review_only":
            failures.append("GOAL-09.0 must be implemented_review_only when present")
        if not _goal090_readiness_implemented(goal090_report):
            failures.append("GOAL-09.0 lacks PASS/PASS_WITH_WARNINGS unlock evidence")
        if "Status: `PASS`" not in goal090_audit:
            failures.append("GOAL-09.0 unlock audit report is missing or not PASS")
        for required_false in [
            '"position_band_diagnostics_rows_generated": false',
            '"position_rows_generated": false',
            '"position_sizing_generated": false',
            '"portfolio_construction_generated": false',
            '"portfolio_weights_generated": false',
            '"buy_sell_hold_outputs_generated": false',
            '"target_prices_generated": false',
            '"expected_returns_for_action_generated": false',
            '"dashboard_generated": false',
            '"paper_trading_enabled": false',
            '"live_trading_enabled": false',
            '"broker_integration_enabled": false',
            '"production_model_behavior_created": false',
            '"database_writes_created": false',
            '"signal_backtests_run": false',
            '"portfolio_backtests_run": false',
            '"cost_slippage_outputs_created": false',
            '"factor_mining_outputs_created": false',
            '"local_lake_files_created": false',
            '"dqn_rl_outputs_created": false',
            '"data_coverage_expanded": false',
            '"live_calculation_outputs_used": false',
            '"downstream_stages_unlocked_by_this_gate": false',
        ]:
            if required_false not in goal090_manifest:
                failures.append(f"GOAL-09.0 manifest missing false boundary flag: {required_false}")
        for required_text in [
            '"mode": "review_only_unlock_gate"',
            '"goal090_unlock_status": "eligible_for_future_review_only_prototype"',
            '"goal09_implemented_by_this_gate": false',
            '"future_position_band_diagnostics_non_actionable_required": true',
            '"goal08b_diagnostics_valid": true',
            '"goal08b_non_actionable_preserved": true',
            '"goal08b_actionability_status_never_actionable": true',
            '"high_risk_actionability_block_preserved": true',
        ]:
            if required_text not in goal090_manifest:
                failures.append(f"GOAL-09.0 manifest missing required unlock marker: {required_text}")
        if '"goal09_target_status": "future_review_only"' not in goal090_manifest and '"goal09_target_status": "implemented_review_only"' not in goal090_manifest:
            failures.append("GOAL-09.0 manifest missing valid GOAL-09 target status marker")
        if '"goal09_implemented_in_repo": false' not in goal090_manifest and '"goal09_implemented_in_repo": true' not in goal090_manifest:
            failures.append("GOAL-09.0 manifest missing GOAL-09 implemented-in-repo marker")
        if goal090.get("implemented_in_repo") != "true":
            failures.append("GOAL-09.0 implemented review-only row must be marked implemented")
        if goal090.get("allowed_next_action") not in {GOAL09_ALLOWED_NEXT, "repair_goal090_unlock_blockers"}:
            failures.append("GOAL-09.0 allowed_next_action is invalid")

    if goal09_status not in GOAL09_ALLOWED_STATUSES:
        failures.append("GOAL-09 position-band diagnostics must be locked_future, future_review_only, or implemented_review_only")
    if goal09_status == "future_review_only":
        if goal09.get("implemented_in_repo") != "false":
            failures.append("GOAL-09 future_review_only must not be marked implemented")
        if not goal090_evidence_ready:
            failures.append("GOAL-09 future_review_only status requires GOAL-09.0 PASS/PASS_WITH_WARNINGS evidence")
        if goal09.get("allowed_next_action") != GOAL09_ALLOWED_NEXT:
            failures.append("GOAL-09 future_review_only allowed_next_action is invalid")
        if goal09.get("depends_on") != GOAL090_WORKFLOW_ID:
            failures.append("GOAL-09 future_review_only must depend on GOAL-09.0")
    elif goal09_status == "locked_future":
        if goal09.get("implemented_in_repo") == "true":
            failures.append("GOAL-09 locked_future must not be marked implemented")
        if goal090_evidence_ready:
            failures.append("GOAL-09 should be future_review_only after GOAL-09.0 evidence")
    elif goal09_status == "implemented_review_only":
        if goal09.get("implemented_in_repo") != "true":
            failures.append("GOAL-09 implemented_review_only must be marked implemented")
        if not goal09_evidence_ready:
            failures.append("GOAL-09 implemented_review_only status requires GOAL-09 PASS/PASS_WITH_WARNINGS evidence")
        if goal09.get("allowed_next_action") != GOAL09_IMPLEMENTED_ALLOWED_NEXT:
            failures.append("GOAL-09 implemented_review_only allowed_next_action is invalid")
        if goal09.get("depends_on") != GOAL090_WORKFLOW_ID:
            failures.append("GOAL-09 implemented_review_only must depend on GOAL-09.0")
        for required_true in [
            '"mode": "review_only"',
            '"output_type": "position_band_diagnostic"',
            '"output_grain": "trade_date + symbol"',
            '"position_band_diagnostics_rows_generated": true',
            '"non_actionable": true',
            '"position_actionability_status_values": [',
            '"never_actionable"',
            '"deterministic_rules_only": true',
            '"goal08b_actionability_status_never_actionable_enforced": true',
            '"high_risk_blocking_enforced": true',
            '"goal08b_warning_codes_propagated": true',
            '"goal07b_risk_warning_codes_propagated": true',
            '"future_position_band_diagnostics_non_actionable_required": true',
        ]:
            if required_true not in goal09_manifest:
                failures.append(f"GOAL-09 manifest missing required diagnostic marker: {required_true}")
        for required_false in [
            '"position_rows_generated": false',
            '"actual_position_sizing_generated": false',
            '"portfolio_construction_generated": false',
            '"portfolio_weights_generated": false',
            '"target_weights_generated": false',
            '"order_quantities_generated": false',
            '"capital_allocation_amounts_generated": false',
            '"buy_sell_hold_outputs_generated": false',
            '"target_prices_generated": false',
            '"expected_returns_for_action_generated": false',
            '"actionable_recommendation_rows_generated": false',
            '"dashboard_generated": false',
            '"paper_trading_enabled": false',
            '"live_trading_enabled": false',
            '"broker_integration_enabled": false',
            '"production_model_behavior_created": false',
            '"database_writes_created": false',
            '"signal_backtests_run": false',
            '"portfolio_backtests_run": false',
            '"cost_slippage_outputs_created": false',
            '"factor_mining_outputs_created": false',
            '"local_lake_files_created": false',
            '"dqn_rl_outputs_created": false',
            '"optimization_used": false',
            '"learned_policy_used": false',
            '"downstream_stages_unlocked_by_this_goal": false',
        ]:
            if required_false not in goal09_manifest:
                failures.append(f"GOAL-09 manifest missing false boundary flag: {required_false}")

    if goal091:
        if goal091_status != "implemented_review_only":
            failures.append("GOAL-09.1 must be implemented_review_only when present")
        if not _goal091_readiness_implemented(goal091_report):
            failures.append("GOAL-09.1 lacks PASS/PASS_WITH_WARNINGS dashboard readiness evidence")
        if "Status: `PASS`" not in goal091_audit:
            failures.append("GOAL-09.1 dashboard readiness audit report is missing or not PASS")
        if not goal09_evidence_ready:
            failures.append("GOAL-09.1 requires GOAL-09 implemented_review_only evidence")
        if goal091.get("implemented_in_repo") != "true":
            failures.append("GOAL-09.1 implemented review-only row must be marked implemented")
        if goal091.get("allowed_next_action") != GOAL091_ALLOWED_NEXT:
            failures.append("GOAL-09.1 allowed_next_action is invalid")
        if goal091.get("depends_on") != GOAL09_WORKFLOW_ID:
            failures.append("GOAL-09.1 must depend on GOAL-09")
        for required_text in [
            '"mode": "review_readiness_only"',
            '"goal09_status_confirmed": true',
            '"goal09_non_actionable_confirmed": true',
            '"goal09_output_grain": "trade_date + symbol"',
            '"position_actionability_status_values": [',
            '"never_actionable"',
            '"future_dashboard_contract_design_gate_may_be_requested": true',
            '"goal_dashboard00_request_status": "eligible_for_explicit_design_only_contract_gate"',
            '"dashboard_daily_report_status_after_goal091": "locked_future"',
            '"dashboard_design_only_eligibility_only": true',
            '"dashboard_implemented_by_this_goal": false',
            '"future_dashboard_review_only_required": true',
            '"future_dashboard_never_actionable_required": true',
            '"future_dashboard_non_actionable_disclaimers_required": true',
            '"future_dashboard_may_use_only_audited_goal07b_goal08b_goal09_diagnostics": true',
            '"future_dashboard_top_n_candidate_display_blocked": true',
            '"future_dashboard_actionable_language_blocked": true',
            '"future_dashboard_forbidden_fields_blocked": true',
        ]:
            if required_text not in goal091_manifest:
                failures.append(f"GOAL-09.1 manifest missing required readiness marker: {required_text}")
        for warning_code in [
            "calibration_not_reliable_for_thresholding",
            "target_horizon_calibration_warning",
            "weak_target_horizon_rank_signal",
            "selected_score_variant_weak_rank_signal",
            "single_provider_mode_akshare_direct",
            "provider_source_concentration_disclosed",
            "feature_sign_instability_bounded",
        ]:
            if warning_code not in goal091_manifest:
                failures.append(f"GOAL-09.1 manifest missing warning classification: {warning_code}")
        for required_false in [
            '"dashboard_outputs_generated": false',
            '"dashboard_files_generated": false',
            '"html_generated": false',
            '"streamlit_generated": false',
            '"frontend_code_generated": false',
            '"visual_reports_generated": false',
            '"new_recommendation_rows_generated": false',
            '"new_position_rows_generated": false',
            '"actual_position_sizing_generated": false',
            '"portfolio_weights_generated": false',
            '"target_weights_generated": false',
            '"order_quantities_generated": false',
            '"buy_sell_hold_outputs_generated": false',
            '"target_prices_generated": false',
            '"paper_trading_enabled": false',
            '"live_trading_enabled": false',
            '"broker_integration_enabled": false',
            '"production_model_behavior_created": false',
            '"database_writes_created": false',
            '"signal_backtests_run": false',
            '"portfolio_backtests_run": false',
            '"cost_slippage_outputs_created": false',
            '"factor_mining_outputs_created": false',
            '"local_lake_files_created": false',
            '"dqn_rl_outputs_created": false',
            '"downstream_execution_unlocked_by_this_goal": false',
        ]:
            if required_false not in goal091_manifest:
                failures.append(f"GOAL-09.1 manifest missing false boundary flag: {required_false}")
        dashboard = by_id.get("dashboard_daily_report", {})
        if dashboard.get("status") != "locked_future" or dashboard.get("implemented_in_repo") != "false":
            failures.append("Dashboard / Daily Report UI must remain locked_future after GOAL-09.1")

    if goal_v1_integrity01:
        if goal_v1_integrity01_status != "implemented_infrastructure_only":
            failures.append("GOAL-V1-INTEGRITY-01 must be implemented_infrastructure_only when present")
        if not _goal_v1_integrity01_readiness_implemented(goal_v1_integrity01_report):
            failures.append("GOAL-V1-INTEGRITY-01 lacks PASS/PASS_WITH_WARNINGS artifact-lineage evidence")
        if "Status: `PASS`" not in goal_v1_integrity01_audit:
            failures.append("GOAL-V1-INTEGRITY-01 artifact-lineage audit report is missing or not PASS")
        if not goal091_evidence_ready:
            failures.append("GOAL-V1-INTEGRITY-01 requires GOAL-09.1 implemented_review_only evidence")
        if goal_v1_integrity01.get("implemented_in_repo") != "true":
            failures.append("GOAL-V1-INTEGRITY-01 infrastructure row must be marked implemented")
        if goal_v1_integrity01.get("allowed_next_action") != GOAL_V1_INTEGRITY01_ALLOWED_NEXT:
            failures.append("GOAL-V1-INTEGRITY-01 allowed_next_action is invalid")
        if goal_v1_integrity01.get("depends_on") != GOAL091_WORKFLOW_ID:
            failures.append("GOAL-V1-INTEGRITY-01 must depend on GOAL-09.1")
        for required_text in [
            '"mode": "infrastructure_integrity_only"',
            '"canonical_artifact_lineage_verified": true',
            '"source_of_truth_docs_synchronized": true',
            '"workflow_status_synchronized": true',
            '"future_dashboard_may_read_only_canonical_outputs_and_audit_metadata": true',
            '"future_dashboard_forbidden_source_inputs_blocked": true',
            '"forbidden_field_names_absent_from_diagnostic_outputs": true',
            '"forbidden_field_names_absent_from_future_dashboard_required_fields": true',
            '"goal08b_rows_never_actionable": true',
            '"goal09_rows_never_actionable": true',
            '"goal091_warning_classifications_available": true',
            '"dashboard_daily_report_locked_future": true',
            '"dashboard_daily_report_status_after_goal_v1_integrity01": "locked_future"',
            '"goal_dashboard00_request_status": "eligible_for_explicit_design_only_contract_gate"',
        ]:
            if required_text not in goal_v1_integrity01_manifest:
                failures.append(f"GOAL-V1-INTEGRITY-01 manifest missing required marker: {required_text}")
        for required_false in [
            '"dashboard_outputs_generated": false',
            '"dashboard_files_generated": false',
            '"html_generated": false',
            '"streamlit_generated": false',
            '"frontend_code_generated": false',
            '"visual_reports_generated": false',
            '"new_risk_rows_generated": false',
            '"new_recommendation_rows_generated": false',
            '"new_position_rows_generated": false',
            '"diagnostic_output_schemas_changed": false',
            '"actual_position_sizing_generated": false',
            '"portfolio_construction_generated": false',
            '"portfolio_weights_generated": false',
            '"target_weights_generated": false',
            '"order_quantities_generated": false',
            '"buy_sell_hold_outputs_generated": false',
            '"target_prices_generated": false',
            '"paper_trading_enabled": false',
            '"live_trading_enabled": false',
            '"broker_integration_enabled": false',
            '"production_model_behavior_created": false',
            '"database_writes_created": false',
            '"signal_backtests_run": false',
            '"portfolio_backtests_run": false',
            '"cost_slippage_outputs_created": false',
            '"factor_mining_outputs_created": false',
            '"local_lake_files_created": false',
            '"dqn_rl_outputs_created": false',
            '"large_refactor_performed": false',
            '"downstream_execution_unlocked_by_this_goal": false',
        ]:
            if required_false not in goal_v1_integrity01_manifest:
                failures.append(f"GOAL-V1-INTEGRITY-01 manifest missing false boundary flag: {required_false}")
        dashboard = by_id.get("dashboard_daily_report", {})
        if dashboard.get("status") != "locked_future" or dashboard.get("implemented_in_repo") != "false":
            failures.append("Dashboard / Daily Report UI must remain locked_future after GOAL-V1-INTEGRITY-01")
        if dashboard.get("depends_on") != GOAL_V1_INTEGRITY01_WORKFLOW_ID:
            failures.append("Dashboard / Daily Report UI must depend on GOAL-V1-INTEGRITY-01 after the integrity gate exists")

    if goal10a:
        if goal10a_status != "implemented_design_only":
            failures.append("GOAL-10A must be implemented_design_only when present")
        if not _goal10a_readiness_implemented(goal10a_report):
            failures.append("GOAL-10A lacks PASS/PASS_WITH_WARNINGS backtest contract design evidence")
        if "Status: `PASS`" not in goal10a_audit:
            failures.append("GOAL-10A backtest contract audit report is missing or not PASS")
        if not goal_v1_integrity01_evidence_ready:
            failures.append("GOAL-10A requires GOAL-V1-INTEGRITY-01 implemented_infrastructure_only evidence")
        if goal10a.get("implemented_in_repo") != "true":
            failures.append("GOAL-10A design row must be marked implemented")
        if goal10a.get("allowed_next_action") != GOAL10A_ALLOWED_NEXT:
            failures.append("GOAL-10A allowed_next_action is invalid")
        if goal10a.get("depends_on") != GOAL_V1_INTEGRITY01_WORKFLOW_ID:
            failures.append("GOAL-10A must depend on GOAL-V1-INTEGRITY-01")
        for required_text in [
            '"mode": "design_only"',
            '"design_only_contracts_written": true',
            '"goal08b_inputs_never_actionable": true',
            '"goal09_inputs_never_actionable": true',
            '"t_plus_1_required": true',
            '"no_lookahead_required": true',
            '"benchmark_leakage_forbidden": true',
            '"cost_slippage_sensitivity_defined_not_run": true',
            '"suspended_limit_missing_policy_defined": true',
            '"goal10b_status_after_goal10a": "locked_future"',
            '"goal10c_status_after_goal10a": "locked_future"',
            '"goal10d_status_after_goal10a": "locked_future"',
            '"dashboard_daily_report_status_after_goal10a": "locked_future"',
        ]:
            if required_text not in goal10a_manifest:
                failures.append(f"GOAL-10A manifest missing required marker: {required_text}")
        for required_false in [
            '"backtests_run": false',
            '"backtest_rows_generated": false',
            '"backtest_performance_rows_generated": false',
            '"equity_curves_generated": false',
            '"portfolio_returns_generated": false',
            '"portfolio_construction_generated": false',
            '"portfolio_weights_generated": false',
            '"position_sizing_generated": false',
            '"order_quantities_generated": false',
            '"buy_sell_hold_outputs_generated": false',
            '"target_prices_generated": false',
            '"recommendation_rows_generated": false',
            '"new_recommendation_rows_generated": false',
            '"new_position_rows_generated": false',
            '"dashboard_outputs_generated": false',
            '"dashboard_files_generated": false',
            '"html_generated": false',
            '"streamlit_generated": false',
            '"frontend_code_generated": false',
            '"visual_reports_generated": false',
            '"paper_trading_enabled": false',
            '"live_trading_enabled": false',
            '"broker_integration_enabled": false',
            '"production_model_behavior_created": false',
            '"database_writes_created": false',
            '"new_data_fetched": false',
            '"data_panel_expanded": false',
            '"local_lake_files_created": false',
            '"factor_mining_outputs_created": false',
            '"dqn_rl_outputs_created": false',
            '"downstream_execution_unlocked_by_this_goal": false',
        ]:
            if required_false not in goal10a_manifest:
                failures.append(f"GOAL-10A manifest missing false boundary flag: {required_false}")
        if goal10b_evidence_ready:
            if goal10b.get("implemented_in_repo") != "true":
                failures.append("GOAL-10B implemented diagnostics must be marked implemented")
            if goal10b.get("depends_on") != GOAL10A_WORKFLOW_ID:
                failures.append("GOAL-10B must depend on GOAL-10A")
        else:
            if goal10b.get("status") != "locked_future":
                failures.append("GOAL-10B must remain locked_future until GOAL-10B evidence exists")
            if goal10b.get("implemented_in_repo") != "false":
                failures.append("GOAL-10B must not be implemented without GOAL-10B evidence")
            if goal10b.get("depends_on") != GOAL10A_WORKFLOW_ID:
                failures.append("GOAL-10B dependency is invalid")
        _validate_goal10b2_goal10c_state_after_diagnostic_chain(
            failures,
            goal10b2,
            goal10c,
            goal10d,
            goal10b2_evidence_ready,
            goal10c_evidence_ready,
            context="GOAL-10A",
        )
        for forbidden_path in [
            "outputs/backtests",
            "outputs/equity_curves",
            "outputs/portfolio_returns",
        ]:
            if (root / forbidden_path).exists():
                failures.append(f"GOAL-10A forbidden output path exists: {forbidden_path}")
        failures.extend(f"Unexpected GOAL-10B backtest output path exists: {path}" for path in _unexpected_goal10b_backtest_outputs(root))

    if goal10b:
        if goal10b_status != "implemented_review_only":
            failures.append("GOAL-10B must be implemented_review_only when present after its explicit request")
        if not _goal10b_readiness_implemented(goal10b_report):
            failures.append("GOAL-10B lacks PASS/PASS_WITH_WARNINGS recommendation diagnostics backtest evidence")
        if "Status: `PASS`" not in goal10b_audit:
            failures.append("GOAL-10B recommendation diagnostics backtest audit report is missing or not PASS")
        if not _goal10a_readiness_implemented(goal10a_report):
            failures.append("GOAL-10B requires GOAL-10A implemented_design_only evidence")
        if goal10b.get("implemented_in_repo") != "true":
            failures.append("GOAL-10B review-only row must be marked implemented")
        if goal10b.get("allowed_next_action") != GOAL10B_ALLOWED_NEXT:
            failures.append("GOAL-10B allowed_next_action is invalid")
        if goal10b.get("depends_on") != GOAL10A_WORKFLOW_ID:
            failures.append("GOAL-10B must depend on GOAL-10A")
        for required_text in [
            '"mode": "review_only"',
            '"review_only_backtest_diagnostics_generated": true',
            '"forward_return_diagnostics_generated": true',
            '"diagnostic_rows_generated": true',
            '"goal08b_inputs_never_actionable": true',
            '"t_plus_1_alignment_applied": true',
            '"no_lookahead_contract_followed": true',
            '"goal10b_workflow_status_after_goal10b": "implemented_review_only"',
            '"goal10c_status_after_goal10b": "locked_future"',
            '"goal10d_status_after_goal10b": "locked_future"',
            '"dashboard_daily_report_status_after_goal10b": "locked_future"',
            '"signal_backtest_status_after_goal10b": "locked_future"',
            '"portfolio_backtest_status_after_goal10b": "locked_future"',
            '"cost_slippage_sensitivity_status_after_goal10b": "locked_future"',
        ]:
            if required_text not in goal10b_manifest:
                failures.append(f"GOAL-10B manifest missing required marker: {required_text}")
        for required_false in [
            '"buy_sell_hold_outputs_generated": false',
            '"target_prices_generated": false',
            '"position_sizing_generated": false',
            '"actual_position_sizing_generated": false',
            '"order_quantities_generated": false',
            '"target_weights_generated": false',
            '"portfolio_weights_generated": false',
            '"portfolio_returns_generated": false',
            '"equity_curves_generated": false',
            '"portfolio_construction_generated": false',
            '"dashboard_outputs_generated": false',
            '"dashboard_files_generated": false',
            '"html_generated": false',
            '"streamlit_generated": false',
            '"frontend_code_generated": false',
            '"visual_reports_generated": false',
            '"paper_trading_enabled": false',
            '"live_trading_enabled": false',
            '"broker_integration_enabled": false',
            '"production_model_behavior_created": false',
            '"database_writes_created": false',
            '"backtests_run": false',
            '"backtest_execution_run": false',
            '"backtest_performance_rows_generated": false',
            '"signal_backtests_run": false',
            '"portfolio_backtests_run": false',
            '"cost_slippage_outputs_created": false',
            '"new_data_fetched": false',
            '"data_panel_expanded": false',
            '"provider_ingestion_modified": false',
            '"local_lake_files_created": false',
            '"factor_mining_outputs_created": false',
            '"dqn_rl_outputs_created": false',
            '"downstream_execution_unlocked_by_this_goal": false',
        ]:
            if required_false not in goal10b_manifest:
                failures.append(f"GOAL-10B manifest missing false boundary flag: {required_false}")
        _validate_goal10b2_goal10c_state_after_diagnostic_chain(
            failures,
            goal10b2,
            goal10c,
            goal10d,
            goal10b2_evidence_ready,
            goal10c_evidence_ready,
            context="GOAL-10B",
        )
        _validate_locked_execution_downstream(failures, by_id, context="GOAL-10B")
        failures.extend(f"Unexpected GOAL-10B backtest output path exists: {path}" for path in _unexpected_goal10b_backtest_outputs(root))

    if goal10b1:
        if goal10b1_status != "implemented_review_only":
            failures.append("GOAL-10B.1 must be implemented_review_only when present after its explicit request")
        if not _goal10b1_readiness_implemented(goal10b1_report):
            failures.append("GOAL-10B.1 lacks PASS/PASS_WITH_WARNINGS coverage repair evidence")
        if "Status: `PASS`" not in goal10b1_audit:
            failures.append("GOAL-10B.1 coverage repair audit report is missing or not PASS")
        if not _goal10b_readiness_implemented(goal10b_report):
            failures.append("GOAL-10B.1 requires GOAL-10B implemented_review_only evidence")
        if goal10b1.get("implemented_in_repo") != "true":
            failures.append("GOAL-10B.1 review-only row must be marked implemented")
        if goal10b1.get("allowed_next_action") != GOAL10B1_ALLOWED_NEXT:
            failures.append("GOAL-10B.1 allowed_next_action is invalid")
        if goal10b1.get("depends_on") != GOAL10B_WORKFLOW_ID:
            failures.append("GOAL-10B.1 must depend on GOAL-10B")
        for required_text in [
            '"mode": "review_only"',
            '"repair_decision": "coverage_repair_not_possible_with_current_artifacts"',
            '"review_only_coverage_repair_diagnostics_generated": true',
            '"label_source_coverage_audited": true',
            '"recommendation_distribution_audited": true',
            '"used_existing_artifacts_only": true',
            '"repaired_snapshot_generated": false',
            '"repaired_group_metrics_generated": false',
            '"goal10b1_workflow_status_after_goal10b1": "implemented_review_only"',
            '"goal10c_status_after_goal10b1": "locked_future"',
            '"goal10d_status_after_goal10b1": "locked_future"',
            '"dashboard_daily_report_status_after_goal10b1": "locked_future"',
            '"signal_backtest_status_after_goal10b1": "locked_future"',
            '"portfolio_backtest_status_after_goal10b1": "locked_future"',
            '"cost_slippage_sensitivity_status_after_goal10b1": "locked_future"',
        ]:
            if required_text not in goal10b1_manifest:
                failures.append(f"GOAL-10B.1 manifest missing required marker: {required_text}")
        for required_false in [
            '"new_data_fetched": false',
            '"data_panel_expanded": false',
            '"provider_ingestion_modified": false',
            '"goal08b_rows_created": false',
            '"goal08b_rows_overwritten": false',
            '"goal09_rows_created": false',
            '"goal09_rows_overwritten": false',
            '"buy_sell_hold_outputs_generated": false',
            '"target_prices_generated": false',
            '"position_sizing_generated": false',
            '"actual_position_sizing_generated": false',
            '"portfolio_weights_generated": false',
            '"portfolio_returns_generated": false',
            '"equity_curves_generated": false',
            '"portfolio_construction_generated": false',
            '"dashboard_outputs_generated": false',
            '"dashboard_files_generated": false',
            '"html_generated": false',
            '"streamlit_generated": false',
            '"frontend_code_generated": false',
            '"visual_reports_generated": false',
            '"paper_trading_enabled": false',
            '"live_trading_enabled": false',
            '"broker_integration_enabled": false',
            '"production_model_behavior_created": false',
            '"database_writes_created": false',
            '"backtests_run": false',
            '"backtest_execution_run": false',
            '"backtest_performance_rows_generated": false',
            '"signal_backtests_run": false',
            '"portfolio_backtests_run": false',
            '"cost_slippage_outputs_created": false',
            '"local_lake_files_created": false',
            '"factor_mining_outputs_created": false',
            '"dqn_rl_outputs_created": false',
            '"downstream_execution_unlocked_by_this_goal": false',
        ]:
            if required_false not in goal10b1_manifest:
                failures.append(f"GOAL-10B.1 manifest missing false boundary flag: {required_false}")
        _validate_goal10b2_goal10c_state_after_diagnostic_chain(
            failures,
            goal10b2,
            goal10c,
            goal10d,
            goal10b2_evidence_ready,
            goal10c_evidence_ready,
            context="GOAL-10B.1",
        )
        _validate_locked_execution_downstream(failures, by_id, context="GOAL-10B.1")
        failures.extend(f"Unexpected GOAL-10B.1 backtest output path exists: {path}" for path in _unexpected_goal10b_backtest_outputs(root))

    if goal_data_label01:
        if goal_data_label01_status != "implemented_review_only":
            failures.append("GOAL-DATA-LABEL-01 must be implemented_review_only when present after its explicit request")
        if not _goal_data_label01_readiness_implemented(goal_data_label01_report):
            failures.append("GOAL-DATA-LABEL-01 lacks PASS/PASS_WITH_WARNINGS forward-return label coverage evidence")
        if "Status: `PASS`" not in goal_data_label01_audit:
            failures.append("GOAL-DATA-LABEL-01 label coverage audit report is missing or not PASS")
        if not _goal10b1_readiness_implemented(goal10b1_report):
            failures.append("GOAL-DATA-LABEL-01 requires GOAL-10B.1 implemented_review_only evidence")
        if goal_data_label01.get("implemented_in_repo") != "true":
            failures.append("GOAL-DATA-LABEL-01 review-only row must be marked implemented")
        if goal_data_label01.get("allowed_next_action") != GOAL_DATA_LABEL01_ALLOWED_NEXT:
            failures.append("GOAL-DATA-LABEL-01 allowed_next_action is invalid")
        if goal_data_label01.get("depends_on") != GOAL10B1_WORKFLOW_ID:
            failures.append("GOAL-DATA-LABEL-01 must depend on GOAL-10B.1")
        for required_text in [
            '"mode": "review_only_label_coverage_expansion"',
            '"forward_return_label_coverage_expanded": true',
            '"forward_return_20d_labels_generated": true',
            '"used_committed_source_samples_only": true',
            '"label_rows_generated": true',
            '"diagnostic_join_ready": false',
            '"goal_v1_diagnostic_coverage02_status_after_goal_data_label01": "locked_future"',
            '"goal10b2_status_after_goal_data_label01": "locked_future"',
            '"goal10c_status_after_goal_data_label01": "locked_future"',
            '"goal10d_status_after_goal_data_label01": "locked_future"',
            '"dashboard_daily_report_status_after_goal_data_label01": "locked_future"',
        ]:
            if required_text not in goal_data_label01_manifest:
                failures.append(f"GOAL-DATA-LABEL-01 manifest missing required marker: {required_text}")
        for required_false in [
            '"new_data_fetched": false',
            '"network_ingestion_run": false',
            '"provider_ingestion_modified": false',
            '"local_bundle_files_committed": false',
            '"local_lake_files_created": false',
            '"raw_provider_payloads_committed": false',
            '"goal07b_rows_created": false',
            '"goal08b_rows_created": false',
            '"goal09_rows_created": false',
            '"recommendation_rows_generated": false',
            '"position_rows_generated": false',
            '"buy_sell_hold_outputs_generated": false',
            '"target_prices_generated": false',
            '"position_sizing_generated": false',
            '"portfolio_weights_generated": false',
            '"portfolio_returns_generated": false',
            '"equity_curves_generated": false',
            '"dashboard_outputs_generated": false',
            '"dashboard_files_generated": false',
            '"html_generated": false',
            '"streamlit_generated": false',
            '"frontend_code_generated": false',
            '"paper_trading_enabled": false',
            '"live_trading_enabled": false',
            '"broker_integration_enabled": false',
            '"production_model_behavior_created": false',
            '"database_writes_created": false',
            '"backtests_run": false',
            '"backtest_performance_rows_generated": false',
            '"signal_backtests_run": false',
            '"portfolio_backtests_run": false',
            '"cost_slippage_outputs_created": false',
            '"factor_mining_outputs_created": false',
            '"dqn_rl_outputs_created": false',
            '"downstream_execution_unlocked_by_this_goal": false',
        ]:
            if required_false not in goal_data_label01_manifest:
                failures.append(f"GOAL-DATA-LABEL-01 manifest missing false boundary flag: {required_false}")
        if goal_v1_diagnostic_coverage02_evidence_ready:
            if goal_v1_diagnostic_coverage02.get("implemented_in_repo") != "true":
                failures.append("GOAL-V1-DIAGNOSTIC-COVERAGE-02 implemented diagnostics must be marked implemented")
            if goal_v1_diagnostic_coverage02.get("depends_on") != GOAL_DATA_LABEL01_WORKFLOW_ID:
                failures.append("GOAL-V1-DIAGNOSTIC-COVERAGE-02 dependency is invalid after GOAL-DATA-LABEL-01")
        else:
            if goal_v1_diagnostic_coverage02.get("status") != "locked_future":
                failures.append("GOAL-V1-DIAGNOSTIC-COVERAGE-02 must remain locked_future after GOAL-DATA-LABEL-01 until its evidence exists")
            if goal_v1_diagnostic_coverage02.get("implemented_in_repo") != "false":
                failures.append("GOAL-V1-DIAGNOSTIC-COVERAGE-02 must not be implemented after GOAL-DATA-LABEL-01 without evidence")
            if goal_v1_diagnostic_coverage02.get("depends_on") != GOAL_DATA_LABEL01_WORKFLOW_ID:
                failures.append("GOAL-V1-DIAGNOSTIC-COVERAGE-02 dependency is invalid after GOAL-DATA-LABEL-01")
        _validate_goal10b2_goal10c_state_after_diagnostic_chain(
            failures,
            goal10b2,
            goal10c,
            goal10d,
            goal10b2_evidence_ready,
            goal10c_evidence_ready,
            context="GOAL-DATA-LABEL-01",
        )
        _validate_locked_execution_downstream(failures, by_id, context="GOAL-DATA-LABEL-01")

    if goal_v1_diagnostic_coverage02:
        if goal_v1_diagnostic_coverage02_status == "implemented_review_only":
            if not goal_v1_diagnostic_coverage02_evidence_ready:
                failures.append("GOAL-V1-DIAGNOSTIC-COVERAGE-02 lacks PASS/PASS_WITH_WARNINGS multi-symbol diagnostic evidence")
            if goal_v1_diagnostic_coverage02.get("implemented_in_repo") != "true":
                failures.append("GOAL-V1-DIAGNOSTIC-COVERAGE-02 review-only row must be marked implemented")
            if goal_v1_diagnostic_coverage02.get("allowed_next_action") != GOAL_V1_DIAGNOSTIC_COVERAGE02_ALLOWED_NEXT:
                failures.append("GOAL-V1-DIAGNOSTIC-COVERAGE-02 allowed_next_action is invalid")
            if goal_v1_diagnostic_coverage02.get("depends_on") != GOAL_DATA_LABEL01_WORKFLOW_ID:
                failures.append("GOAL-V1-DIAGNOSTIC-COVERAGE-02 must depend on GOAL-DATA-LABEL-01")
            for required_text in [
                '"mode": "review_only_multi_symbol_diagnostic_coverage_expansion"',
                '"multi_symbol_diagnostics_generated": true',
                '"risk_diagnostics_rows_generated": true',
                '"recommendation_diagnostics_rows_generated": true',
                '"position_band_diagnostics_rows_generated": true',
                '"keys_match_across_risk_recommendation_position": true',
                '"approved_symbols_only": true',
                '"used_committed_stage6c_evidence_only": true',
                '"canonical_goal07b_goal08b_goal09_preserved": true',
                '"forward_return_20d_available": false',
                '"multi_horizon_backtest_ready": false',
                '"goal_v1_diagnostic_coverage02_status_after_gate": "implemented_review_only"',
                '"goal10b2_status_after_goal_v1_diagnostic_coverage02": "locked_future"',
                '"goal10c_status_after_goal_v1_diagnostic_coverage02": "locked_future"',
                '"goal10d_status_after_goal_v1_diagnostic_coverage02": "locked_future"',
                '"dashboard_daily_report_status_after_goal_v1_diagnostic_coverage02": "locked_future"',
            ]:
                if required_text not in goal_v1_diagnostic_coverage02_manifest:
                    failures.append(f"GOAL-V1-DIAGNOSTIC-COVERAGE-02 manifest missing required marker: {required_text}")
            for required_false in [
                '"new_data_fetched": false',
                '"network_ingestion_run": false',
                '"provider_ingestion_modified": false',
                '"data_panel_expanded": false',
                '"local_bundle_files_committed": false',
                '"local_lake_files_created": false',
                '"raw_provider_payloads_committed": false',
                '"canonical_goal07b_rows_created": false',
                '"canonical_goal08b_rows_created": false',
                '"canonical_goal09_rows_created": false',
                '"recommendation_rows_generated": false',
                '"actionable_recommendation_rows_generated": false',
                '"position_rows_generated": false',
                '"buy_sell_hold_outputs_generated": false',
                '"target_prices_generated": false',
                '"position_sizing_generated": false',
                '"portfolio_weights_generated": false',
                '"portfolio_returns_generated": false',
                '"equity_curves_generated": false',
                '"dashboard_outputs_generated": false',
                '"dashboard_files_generated": false',
                '"html_generated": false',
                '"streamlit_generated": false',
                '"frontend_code_generated": false',
                '"paper_trading_enabled": false',
                '"live_trading_enabled": false',
                '"broker_integration_enabled": false',
                '"production_model_behavior_created": false',
                '"database_writes_created": false',
                '"backtests_run": false',
                '"backtest_performance_rows_generated": false',
                '"signal_backtests_run": false',
                '"portfolio_backtests_run": false',
                '"cost_slippage_outputs_created": false',
                '"factor_mining_outputs_created": false',
                '"dqn_rl_outputs_created": false',
                '"downstream_execution_unlocked_by_this_goal": false',
            ]:
                if required_false not in goal_v1_diagnostic_coverage02_manifest:
                    failures.append(f"GOAL-V1-DIAGNOSTIC-COVERAGE-02 manifest missing false boundary flag: {required_false}")
        elif goal_v1_diagnostic_coverage02_status == "locked_future":
            if goal_v1_diagnostic_coverage02.get("implemented_in_repo") != "false":
                failures.append("GOAL-V1-DIAGNOSTIC-COVERAGE-02 locked_future row must not be marked implemented")
            if goal_v1_diagnostic_coverage02.get("depends_on") != GOAL_DATA_LABEL01_WORKFLOW_ID:
                failures.append("GOAL-V1-DIAGNOSTIC-COVERAGE-02 locked_future row must depend on GOAL-DATA-LABEL-01")
        else:
            failures.append("GOAL-V1-DIAGNOSTIC-COVERAGE-02 must be locked_future or implemented_review_only")
        _validate_goal10b2_goal10c_state_after_diagnostic_chain(
            failures,
            goal10b2,
            goal10c,
            goal10d,
            goal10b2_evidence_ready,
            goal10c_evidence_ready,
            context="GOAL-V1-DIAGNOSTIC-COVERAGE-02",
        )

    if goal10b2:
        if goal10b2_status == "implemented_review_only":
            if not goal10b2_evidence_ready:
                failures.append("GOAL-10B.2 lacks PASS/PASS_WITH_WARNINGS revalidation evidence")
            if goal10b2.get("implemented_in_repo") != "true":
                failures.append("GOAL-10B.2 review-only row must be marked implemented")
            if goal10b2.get("allowed_next_action") != GOAL10B2_ALLOWED_NEXT:
                failures.append("GOAL-10B.2 allowed_next_action is invalid")
            if goal10b2.get("depends_on") != GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID:
                failures.append("GOAL-10B.2 must depend on GOAL-V1-DIAGNOSTIC-COVERAGE-02")
            for required_text in [
                '"mode": "review_only_recommendation_backtest_revalidation"',
                '"review_only_revalidation_generated": true',
                '"multi_symbol_revalidation_generated": true',
                '"used_goal_v1_diagnostic_coverage02_only": true',
                '"goal_v1_diagnostic_coverage02_inputs_never_actionable": true',
                '"goal10b2_workflow_status_after_goal10b2": "implemented_review_only"',
                '"goal10c_status_after_goal10b2": "locked_future"',
                '"goal10d_status_after_goal10b2": "locked_future"',
                '"dashboard_daily_report_status_after_goal10b2": "locked_future"',
            ]:
                if required_text not in goal10b2_manifest:
                    failures.append(f"GOAL-10B.2 manifest missing required marker: {required_text}")
            for required_false in [
                '"buy_sell_hold_outputs_generated": false',
                '"target_prices_generated": false',
                '"position_sizing_generated": false',
                '"portfolio_weights_generated": false',
                '"portfolio_returns_generated": false',
                '"equity_curves_generated": false',
                '"dashboard_outputs_generated": false',
                '"dashboard_files_generated": false',
                '"html_generated": false',
                '"streamlit_generated": false',
                '"frontend_code_generated": false',
                '"paper_trading_enabled": false',
                '"live_trading_enabled": false',
                '"broker_integration_enabled": false',
                '"production_model_behavior_created": false',
                '"database_writes_created": false',
                '"backtests_run": false',
                '"backtest_performance_rows_generated": false',
                '"signal_backtests_run": false',
                '"portfolio_backtests_run": false',
                '"local_lake_files_created": false',
                '"factor_mining_outputs_created": false',
                '"dqn_rl_outputs_created": false',
                '"downstream_execution_unlocked_by_this_goal": false',
            ]:
                if required_false not in goal10b2_manifest:
                    failures.append(f"GOAL-10B.2 manifest missing false boundary flag: {required_false}")
        elif goal10b2_status == "locked_future":
            if goal10b2.get("implemented_in_repo") != "false":
                failures.append("GOAL-10B.2 locked_future row must not be marked implemented")
            if goal10b2.get("depends_on") != GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID:
                failures.append("GOAL-10B.2 locked_future row must depend on GOAL-V1-DIAGNOSTIC-COVERAGE-02")
        else:
            failures.append("GOAL-10B.2 must be locked_future or implemented_review_only")

    if goal10c:
        if goal10c_status == "implemented_review_only":
            if not goal10c_evidence_ready:
                failures.append("GOAL-10C lacks PASS/PASS_WITH_WARNINGS cost/slippage evidence")
            if not goal10b2_evidence_ready:
                failures.append("GOAL-10C requires GOAL-10B.2 implemented_review_only evidence")
            if goal10c.get("implemented_in_repo") != "true":
                failures.append("GOAL-10C review-only row must be marked implemented")
            if goal10c.get("allowed_next_action") != GOAL10C_ALLOWED_NEXT:
                failures.append("GOAL-10C allowed_next_action is invalid")
            if goal10c.get("depends_on") != GOAL10B2_WORKFLOW_ID:
                failures.append("GOAL-10C must depend on GOAL-10B.2")
            for required_text in [
                '"mode": "review_only_position_band_cost_slippage_sensitivity"',
                '"review_only_cost_slippage_sensitivity_generated": true',
                '"position_band_sensitivity_generated": true',
                '"goal10b2_inputs_ready": true',
                '"dc02_position_inputs_never_actionable": true',
                '"goal10c_workflow_status_after_goal10c": "implemented_review_only"',
                '"goal10d_status_after_goal10c": "locked_future"',
                '"dashboard_daily_report_status_after_goal10c": "locked_future"',
            ]:
                if required_text not in goal10c_manifest:
                    failures.append(f"GOAL-10C manifest missing required marker: {required_text}")
            for required_false in [
                '"buy_sell_hold_outputs_generated": false',
                '"target_prices_generated": false',
                '"position_sizing_generated": false',
                '"portfolio_weights_generated": false',
                '"portfolio_returns_generated": false',
                '"equity_curves_generated": false',
                '"dashboard_outputs_generated": false',
                '"dashboard_files_generated": false',
                '"html_generated": false',
                '"streamlit_generated": false',
                '"frontend_code_generated": false',
                '"paper_trading_enabled": false',
                '"live_trading_enabled": false',
                '"broker_integration_enabled": false',
                '"production_model_behavior_created": false',
                '"database_writes_created": false',
                '"backtests_run": false',
                '"backtest_performance_rows_generated": false',
                '"signal_backtests_run": false',
                '"portfolio_backtests_run": false',
                '"local_lake_files_created": false',
                '"factor_mining_outputs_created": false',
                '"dqn_rl_outputs_created": false',
                '"downstream_execution_unlocked_by_this_goal": false',
            ]:
                if required_false not in goal10c_manifest:
                    failures.append(f"GOAL-10C manifest missing false boundary flag: {required_false}")
        elif goal10c_status == "locked_future":
            if goal10c.get("implemented_in_repo") != "false":
                failures.append("GOAL-10C locked_future row must not be marked implemented")
            if goal10c.get("depends_on") != GOAL10B2_WORKFLOW_ID:
                failures.append("GOAL-10C locked_future row must depend on GOAL-10B.2")
        else:
            failures.append("GOAL-10C must be locked_future or implemented_review_only")
    if goal_data_provider02a:
        if goal_data_provider02a_status != "implemented_review_only":
            failures.append("GOAL-DATA-PROVIDER-02A must be implemented_review_only when present after its explicit request")
        if not goal_data_provider02a_evidence_ready:
            failures.append("GOAL-DATA-PROVIDER-02A lacks PASS/PASS_WITH_WARNINGS provider capability probe evidence")
        if not goal10c_evidence_ready:
            failures.append("GOAL-DATA-PROVIDER-02A requires GOAL-10C implemented_review_only evidence")
        if goal_data_provider02a.get("implemented_in_repo") != "true":
            failures.append("GOAL-DATA-PROVIDER-02A review-only row must be marked implemented")
        if goal_data_provider02a.get("allowed_next_action") != GOAL_DATA_PROVIDER02A_ALLOWED_NEXT:
            failures.append("GOAL-DATA-PROVIDER-02A allowed_next_action is invalid")
        if goal_data_provider02a.get("depends_on") != GOAL10C_WORKFLOW_ID:
            failures.append("GOAL-DATA-PROVIDER-02A must depend on GOAL-10C")
        for required_text in [
            '"mode": "review_only_multi_provider_capability_probe"',
            '"review_only_capability_probe_generated": true',
            '"all_required_providers_represented": true',
            '"network_disabled_by_default_supported": true',
            '"tushare_env_only_policy_enforced": true',
            '"qstock_backtest_strategy_modules_not_used": true',
            '"yfinance_auxiliary_not_primary": true',
            '"local_import_fallback_recorded": true',
            '"goal_data_provider02a_workflow_status_after_gate": "implemented_review_only"',
            '"goal_data_provider02b_status_after_goal_data_provider02a": "locked_future"',
            '"goal_data_panel02_status_after_goal_data_provider02a": "locked_future"',
            '"goal_v1_diagnostic_coverage03_status_after_goal_data_provider02a": "locked_future"',
            '"goal10b3_status_after_goal_data_provider02a": "locked_future"',
            '"goal10d_status_after_goal_data_provider02a": "locked_future"',
            '"dashboard_daily_report_status_after_goal_data_provider02a": "locked_future"',
        ]:
            if required_text not in goal_data_provider02a_manifest:
                failures.append(f"GOAL-DATA-PROVIDER-02A manifest missing required marker: {required_text}")
        for required_provider in [
            '"tushare_pro"',
            '"baostock"',
            '"akshare"',
            '"efinance"',
            '"qstock"',
            '"yfinance"',
            '"local_import"',
        ]:
            if required_provider not in goal_data_provider02a_manifest:
                failures.append(f"GOAL-DATA-PROVIDER-02A manifest missing provider marker: {required_provider}")
        for required_false in [
            '"final_evaluation_panel_created": false',
            '"evaluation_panel_created": false',
            '"recommendation_diagnostics_run": false',
            '"position_band_diagnostics_run": false',
            '"backtests_run": false',
            '"goal10b3_run": false',
            '"goal10c_rerun_by_this_goal": false',
            '"buy_sell_hold_outputs_generated": false',
            '"target_prices_generated": false',
            '"position_sizing_generated": false',
            '"order_quantities_generated": false',
            '"portfolio_weights_generated": false',
            '"portfolio_returns_generated": false',
            '"equity_curves_generated": false',
            '"dashboard_outputs_generated": false',
            '"dashboard_files_generated": false',
            '"html_generated": false',
            '"streamlit_generated": false',
            '"frontend_code_generated": false',
            '"visual_reports_generated": false',
            '"paper_trading_enabled": false',
            '"live_trading_enabled": false',
            '"broker_integration_enabled": false',
            '"production_db_writes_created": false',
            '"production_model_behavior_created": false',
            '"local_lake_files_created": false',
            '"factor_mining_outputs_created": false',
            '"dqn_rl_outputs_created": false',
            '"raw_provider_payloads_committed": false',
            '"provider_tokens_committed": false',
            '"secrets_logged": false',
            '"approved_universe_expanded": false',
            '"source_backed_panel_materialized": false',
            '"downstream_execution_unlocked_by_this_goal": false',
        ]:
            if required_false not in goal_data_provider02a_manifest:
                failures.append(f"GOAL-DATA-PROVIDER-02A manifest missing false boundary flag: {required_false}")
        provider02a_downstream_rows = [
            (GOAL_DATA_PANEL02_WORKFLOW_ID, goal_data_panel02),
        ]
        if not goal_v1_diagnostic_coverage03_evidence_ready:
            provider02a_downstream_rows.insert(1, (GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID, goal_v1_diagnostic_coverage03))
        if not goal_data_provider02b_evidence_ready:
            provider02a_downstream_rows.insert(0, (GOAL_DATA_PROVIDER02B_WORKFLOW_ID, goal_data_provider02b))
        for workflow_id, row in provider02a_downstream_rows:
            if row.get("status") != "locked_future":
                failures.append(f"{workflow_id} must remain locked_future after GOAL-DATA-PROVIDER-02A")
            if row.get("implemented_in_repo") != "false":
                failures.append(f"{workflow_id} must not be implemented after GOAL-DATA-PROVIDER-02A")
        if goal10b3_evidence_ready:
            if goal10b3.get("status") != "implemented_review_only" or goal10b3.get("implemented_in_repo") != "true":
                failures.append("GOAL-10B.3 valid evidence must be preserved after GOAL-DATA-PROVIDER-02A")
        else:
            if goal10b3.get("status") != "locked_future":
                failures.append(f"{GOAL10B3_WORKFLOW_ID} must remain locked_future after GOAL-DATA-PROVIDER-02A")
            if goal10b3.get("implemented_in_repo") != "false":
                failures.append(f"{GOAL10B3_WORKFLOW_ID} must not be implemented after GOAL-DATA-PROVIDER-02A")
        _validate_locked_execution_downstream(failures, by_id, context="GOAL-DATA-PROVIDER-02A")
    if goal_data_provider02a1:
        if goal_data_provider02a1_status != "implemented_review_only":
            failures.append("GOAL-DATA-PROVIDER-02A.1 must be implemented_review_only when present after its explicit request")
        if not goal_data_provider02a1_evidence_ready:
            failures.append("GOAL-DATA-PROVIDER-02A.1 lacks PASS/PASS_WITH_WARNINGS network smoke-test evidence")
        if not goal_data_provider02a_evidence_ready:
            failures.append("GOAL-DATA-PROVIDER-02A.1 requires GOAL-DATA-PROVIDER-02A implemented_review_only evidence")
        if goal_data_provider02a1.get("implemented_in_repo") != "true":
            failures.append("GOAL-DATA-PROVIDER-02A.1 review-only row must be marked implemented")
        if goal_data_provider02a1.get("allowed_next_action") != GOAL_DATA_PROVIDER02A1_ALLOWED_NEXT:
            failures.append("GOAL-DATA-PROVIDER-02A.1 allowed_next_action is invalid")
        if goal_data_provider02a1.get("depends_on") != GOAL_DATA_PROVIDER02A_WORKFLOW_ID:
            failures.append("GOAL-DATA-PROVIDER-02A.1 must depend on GOAL-DATA-PROVIDER-02A")
        for required_text in [
            '"mode": "review_only_network_opt_in_provider_smoke_test"',
            '"review_only_network_smoke_test_generated": true',
            '"all_required_providers_represented": true',
            '"network_disabled_by_default_supported": true',
            '"network_live_access_only_when_opted_in": true',
            '"tushare_env_only_policy_enforced": true',
            '"qstock_backtest_strategy_modules_not_used": true',
            '"yfinance_auxiliary_not_primary": true',
            '"local_import_fallback_recorded": true',
            '"provider_tokens_never_persisted": true',
            '"raw_payloads_never_persisted": true',
            '"goal_data_provider02a1_workflow_status_after_gate": "implemented_review_only"',
            '"goal_data_provider02b_status_after_goal_data_provider02a1": "locked_future"',
            '"goal_data_panel02_status_after_goal_data_provider02a1": "locked_future"',
            '"goal_v1_diagnostic_coverage03_status_after_goal_data_provider02a1": "locked_future"',
            '"goal10b3_status_after_goal_data_provider02a1": "locked_future"',
            '"goal10d_status_after_goal_data_provider02a1": "locked_future"',
            '"dashboard_daily_report_status_after_goal_data_provider02a1": "locked_future"',
        ]:
            if required_text not in goal_data_provider02a1_manifest:
                failures.append(f"GOAL-DATA-PROVIDER-02A.1 manifest missing required marker: {required_text}")
        for required_provider in [
            '"tushare_pro"',
            '"baostock"',
            '"akshare"',
            '"efinance"',
            '"qstock"',
            '"yfinance"',
            '"local_import"',
        ]:
            if required_provider not in goal_data_provider02a1_manifest:
                failures.append(f"GOAL-DATA-PROVIDER-02A.1 manifest missing provider marker: {required_provider}")
        for required_false in [
            '"final_evaluation_panel_created": false',
            '"evaluation_panel_created": false',
            '"recommendation_diagnostics_run": false',
            '"position_band_diagnostics_run": false',
            '"backtests_run": false',
            '"goal10b3_run": false',
            '"goal10c_rerun_by_this_goal": false',
            '"buy_sell_hold_outputs_generated": false',
            '"target_prices_generated": false',
            '"position_sizing_generated": false',
            '"order_quantities_generated": false',
            '"portfolio_weights_generated": false',
            '"portfolio_returns_generated": false',
            '"equity_curves_generated": false',
            '"dashboard_outputs_generated": false',
            '"dashboard_files_generated": false',
            '"html_generated": false',
            '"streamlit_generated": false',
            '"frontend_code_generated": false',
            '"visual_reports_generated": false',
            '"paper_trading_enabled": false',
            '"live_trading_enabled": false',
            '"broker_integration_enabled": false',
            '"production_db_writes_created": false',
            '"production_model_behavior_created": false',
            '"local_lake_files_created": false',
            '"factor_mining_outputs_created": false',
            '"dqn_rl_outputs_created": false',
            '"raw_provider_payloads_committed": false',
            '"provider_tokens_committed": false',
            '"secrets_logged": false',
            '"approved_universe_expanded": false',
            '"source_backed_panel_materialized": false',
            '"smoke_test_data_treated_as_final_panel_evidence": false',
            '"downstream_execution_unlocked_by_this_goal": false',
        ]:
            if required_false not in goal_data_provider02a1_manifest:
                failures.append(f"GOAL-DATA-PROVIDER-02A.1 manifest missing false boundary flag: {required_false}")
        provider02a1_downstream_rows = [
            (GOAL_DATA_PANEL02_WORKFLOW_ID, goal_data_panel02),
        ]
        if not goal_v1_diagnostic_coverage03_evidence_ready:
            provider02a1_downstream_rows.insert(1, (GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID, goal_v1_diagnostic_coverage03))
        if not goal_data_provider02b_evidence_ready:
            provider02a1_downstream_rows.insert(0, (GOAL_DATA_PROVIDER02B_WORKFLOW_ID, goal_data_provider02b))
        for workflow_id, row in provider02a1_downstream_rows:
            if row.get("status") != "locked_future":
                failures.append(f"{workflow_id} must remain locked_future after GOAL-DATA-PROVIDER-02A.1")
            if row.get("implemented_in_repo") != "false":
                failures.append(f"{workflow_id} must not be implemented after GOAL-DATA-PROVIDER-02A.1")
        if goal10b3_evidence_ready:
            if goal10b3.get("status") != "implemented_review_only" or goal10b3.get("implemented_in_repo") != "true":
                failures.append("GOAL-10B.3 valid evidence must be preserved after GOAL-DATA-PROVIDER-02A.1")
        else:
            if goal10b3.get("status") != "locked_future":
                failures.append(f"{GOAL10B3_WORKFLOW_ID} must remain locked_future after GOAL-DATA-PROVIDER-02A.1")
            if goal10b3.get("implemented_in_repo") != "false":
                failures.append(f"{GOAL10B3_WORKFLOW_ID} must not be implemented after GOAL-DATA-PROVIDER-02A.1")
        if goal_data_provider02b.get("depends_on") != GOAL_DATA_PROVIDER02A1_WORKFLOW_ID:
            failures.append("GOAL-DATA-PROVIDER-02B must depend on GOAL-DATA-PROVIDER-02A.1 after the smoke test gate")
        _validate_locked_execution_downstream(failures, by_id, context="GOAL-DATA-PROVIDER-02A.1")
    if goal_data_provider02b:
        if goal_data_provider02b_status != "implemented_review_only":
            failures.append("GOAL-DATA-PROVIDER-02B must be implemented_review_only when present after its explicit request")
        if not goal_data_provider02b_evidence_ready:
            failures.append("GOAL-DATA-PROVIDER-02B lacks PASS/PASS_WITH_WARNINGS source-backed panel evidence")
        if not goal_data_provider02a1_evidence_ready:
            failures.append("GOAL-DATA-PROVIDER-02B requires GOAL-DATA-PROVIDER-02A.1 implemented_review_only evidence")
        if goal_data_provider02b.get("implemented_in_repo") != "true":
            failures.append("GOAL-DATA-PROVIDER-02B review-only row must be marked implemented")
        if goal_data_provider02b.get("allowed_next_action") != GOAL_DATA_PROVIDER02B_ALLOWED_NEXT:
            failures.append("GOAL-DATA-PROVIDER-02B allowed_next_action is invalid")
        if goal_data_provider02b.get("depends_on") != GOAL_DATA_PROVIDER02A1_WORKFLOW_ID:
            failures.append("GOAL-DATA-PROVIDER-02B must depend on GOAL-DATA-PROVIDER-02A.1")
        for required_text in [
            '"mode": "review_only_source_backed_evaluation_panel_build_gate"',
            '"source_backed_evaluation_panel_created": true',
            '"review_only_panel_generated": true',
            '"panel_contract_status": "source_backed_evaluation_panel_ready_for_dc03"',
            '"row_count": 6000',
            '"unique_symbols": 50',
            '"unique_trade_dates": 120',
            '"universe_mode": "provider_panel_candidate_universe_review_only"',
            '"approved_universe_expanded": false',
            '"goal_data_provider02b_workflow_status_after_gate": "implemented_review_only"',
            '"goal_data_panel02_status_after_goal_data_provider02b": "locked_future"',
            '"goal_v1_diagnostic_coverage03_status_after_goal_data_provider02b": "locked_future"',
            '"goal10b3_status_after_goal_data_provider02b": "locked_future"',
            '"goal10d_status_after_goal_data_provider02b": "locked_future"',
            '"dashboard_daily_report_status_after_goal_data_provider02b": "locked_future"',
            '"raw_payloads_never_persisted": true',
            '"provider_tokens_never_persisted": true',
            '"yfinance_auxiliary_not_primary": true',
        ]:
            if required_text not in goal_data_provider02b_manifest:
                failures.append(f"GOAL-DATA-PROVIDER-02B manifest missing required marker: {required_text}")
        for required_false in [
            '"recommendation_diagnostics_run": false',
            '"position_band_diagnostics_run": false',
            '"backtests_run": false',
            '"goal_v1_diagnostic_coverage03_run": false',
            '"goal10b3_run": false',
            '"goal10c_rerun_by_this_goal": false',
            '"buy_sell_hold_outputs_generated": false',
            '"target_prices_generated": false',
            '"position_sizing_generated": false',
            '"order_quantities_generated": false',
            '"portfolio_weights_generated": false',
            '"portfolio_returns_generated": false',
            '"equity_curves_generated": false',
            '"dashboard_outputs_generated": false',
            '"dashboard_files_generated": false',
            '"html_generated": false',
            '"streamlit_generated": false',
            '"frontend_code_generated": false',
            '"visual_reports_generated": false',
            '"paper_trading_enabled": false',
            '"live_trading_enabled": false',
            '"broker_integration_enabled": false',
            '"production_db_writes_created": false',
            '"production_model_behavior_created": false',
            '"local_lake_files_created": false',
            '"factor_mining_outputs_created": false',
            '"dqn_rl_outputs_created": false',
            '"raw_provider_payloads_committed": false',
            '"provider_tokens_committed": false',
            '"secrets_logged": false',
            '"downstream_execution_unlocked_by_this_goal": false',
            '"goal_data_panel02_workflow_implemented_by_this_goal": false',
        ]:
            if required_false not in goal_data_provider02b_manifest:
                failures.append(f"GOAL-DATA-PROVIDER-02B manifest missing false boundary flag: {required_false}")
        for workflow_id, row in [
            (GOAL_DATA_PANEL02_WORKFLOW_ID, goal_data_panel02),
        ]:
            if row.get("status") != "locked_future":
                failures.append(f"{workflow_id} must remain locked_future after GOAL-DATA-PROVIDER-02B")
            if row.get("implemented_in_repo") != "false":
                failures.append(f"{workflow_id} must not be implemented after GOAL-DATA-PROVIDER-02B")
        if goal10b3_evidence_ready:
            if goal10b3.get("status") != "implemented_review_only" or goal10b3.get("implemented_in_repo") != "true":
                failures.append("GOAL-10B.3 valid evidence must be preserved after GOAL-DATA-PROVIDER-02B")
        else:
            if goal10b3.get("status") != "locked_future":
                failures.append(f"{GOAL10B3_WORKFLOW_ID} must remain locked_future after GOAL-DATA-PROVIDER-02B")
            if goal10b3.get("implemented_in_repo") != "false":
                failures.append(f"{GOAL10B3_WORKFLOW_ID} must not be implemented after GOAL-DATA-PROVIDER-02B")
        if not goal_v1_diagnostic_coverage03_evidence_ready:
            if goal_v1_diagnostic_coverage03.get("status") != "locked_future":
                failures.append(f"{GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID} must remain locked_future after GOAL-DATA-PROVIDER-02B")
            if goal_v1_diagnostic_coverage03.get("implemented_in_repo") != "false":
                failures.append(f"{GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID} must not be implemented after GOAL-DATA-PROVIDER-02B")
        _validate_locked_execution_downstream(failures, by_id, context="GOAL-DATA-PROVIDER-02B")
    if goal_v1_diagnostic_coverage03:
        if goal_v1_diagnostic_coverage03_status != "implemented_review_only":
            failures.append("GOAL-V1-DIAGNOSTIC-COVERAGE-03 must be implemented_review_only when present after its explicit request")
        if not goal_v1_diagnostic_coverage03_evidence_ready:
            failures.append("GOAL-V1-DIAGNOSTIC-COVERAGE-03 lacks PASS/PASS_WITH_WARNINGS source-backed diagnostic evidence")
        if not goal_data_provider02b_evidence_ready:
            failures.append("GOAL-V1-DIAGNOSTIC-COVERAGE-03 requires GOAL-DATA-PROVIDER-02B implemented_review_only evidence")
        if goal_v1_diagnostic_coverage03.get("implemented_in_repo") != "true":
            failures.append("GOAL-V1-DIAGNOSTIC-COVERAGE-03 review-only row must be marked implemented")
        if goal_v1_diagnostic_coverage03.get("allowed_next_action") != GOAL_V1_DIAGNOSTIC_COVERAGE03_ALLOWED_NEXT:
            failures.append("GOAL-V1-DIAGNOSTIC-COVERAGE-03 allowed_next_action is invalid")
        if goal_v1_diagnostic_coverage03.get("depends_on") != GOAL_DATA_PROVIDER02B_WORKFLOW_ID:
            failures.append("GOAL-V1-DIAGNOSTIC-COVERAGE-03 must depend on GOAL-DATA-PROVIDER-02B")
        for required_text in [
            '"mode": "review_only_source_backed_multi_symbol_diagnostics_gate"',
            '"primary_input_artifact": "outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv"',
            '"risk_diagnostic_row_count": 6000',
            '"recommendation_diagnostic_row_count": 6000',
            '"position_band_diagnostic_row_count": 6000',
            '"unique_symbols": 50',
            '"unique_trade_dates": 120',
            '"duplicate_trade_date_symbol_keys": 0',
            '"keys_match_across_diagnostic_families": true',
            '"canonical_goal07b_goal08b_goal09_preserved": true',
            '"goal_v1_diagnostic_coverage03_status_after_gate": "implemented_review_only"',
            '"goal10b3_status_after_goal_v1_diagnostic_coverage03": "locked_future"',
            '"goal10d_status_after_goal_v1_diagnostic_coverage03": "locked_future"',
            '"dashboard_daily_report_status_after_goal_v1_diagnostic_coverage03": "locked_future"',
        ]:
            if required_text not in goal_v1_diagnostic_coverage03_manifest:
                failures.append(f"GOAL-V1-DIAGNOSTIC-COVERAGE-03 manifest missing required marker: {required_text}")
        for required_false in [
            '"goal10b3_run": false',
            '"goal10c_run": false',
            '"buy_sell_hold_outputs_generated": false',
            '"target_prices_generated": false',
            '"actual_position_sizes_generated": false',
            '"position_sizing_generated": false',
            '"target_weights_generated": false',
            '"portfolio_weights_generated": false',
            '"order_quantities_generated": false',
            '"portfolio_returns_generated": false',
            '"equity_curves_generated": false',
            '"dashboard_outputs_generated": false',
            '"dashboard_files_generated": false',
            '"html_generated": false',
            '"streamlit_generated": false',
            '"frontend_code_generated": false',
            '"visual_reports_generated": false',
            '"trading_outputs_generated": false',
            '"broker_outputs_generated": false',
            '"production_outputs_generated": false',
            '"local_lake_files_created": false',
            '"factor_mining_outputs_created": false',
            '"dqn_rl_outputs_created": false',
            '"new_provider_data_fetched": false',
            '"demo_fixture_used_as_primary_evidence": false',
            '"diagnostic_group_variation_fabricated": false',
            '"downstream_execution_unlocked_by_this_goal": false',
        ]:
            if required_false not in goal_v1_diagnostic_coverage03_manifest:
                failures.append(f"GOAL-V1-DIAGNOSTIC-COVERAGE-03 manifest missing false boundary flag: {required_false}")
        if goal_data_panel02.get("status") != "locked_future" or goal_data_panel02.get("implemented_in_repo") != "false":
            failures.append("GOAL-DATA-PANEL-02 must remain locked_future after GOAL-V1-DIAGNOSTIC-COVERAGE-03")
        if goal10b3_evidence_ready:
            if goal10b3.get("status") != "implemented_review_only" or goal10b3.get("implemented_in_repo") != "true":
                failures.append("GOAL-10B.3 valid evidence must be preserved after GOAL-V1-DIAGNOSTIC-COVERAGE-03")
        elif goal10b3.get("status") != "locked_future" or goal10b3.get("implemented_in_repo") != "false":
            failures.append("GOAL-10B.3 must remain locked_future after GOAL-V1-DIAGNOSTIC-COVERAGE-03 unless valid GOAL-10B.3 evidence exists")
        if goal10b3.get("depends_on") != GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID:
            failures.append("GOAL-10B.3 must depend on GOAL-V1-DIAGNOSTIC-COVERAGE-03")
        _validate_locked_execution_downstream(failures, by_id, context="GOAL-V1-DIAGNOSTIC-COVERAGE-03")
    if goal10b3:
        if goal10b3_evidence_ready:
            if not goal_v1_diagnostic_coverage03_evidence_ready:
                failures.append("GOAL-10B.3 requires GOAL-V1-DIAGNOSTIC-COVERAGE-03 implemented_review_only evidence")
            if goal10b3.get("status") != "implemented_review_only":
                failures.append("GOAL-10B.3 must be implemented_review_only when valid evidence exists")
            if goal10b3.get("implemented_in_repo") != "true":
                failures.append("GOAL-10B.3 review-only row must be marked implemented")
            if goal10b3.get("allowed_next_action") != GOAL10B3_ALLOWED_NEXT:
                failures.append("GOAL-10B.3 allowed_next_action is invalid")
            if goal10b3.get("depends_on") != GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID:
                failures.append("GOAL-10B.3 must depend on GOAL-V1-DIAGNOSTIC-COVERAGE-03")
            for required_text in [
                '"mode": "review_only_dc03_recommendation_revalidation_gate"',
                '"input_snapshot_row_count": 6000',
                '"unique_symbols": 50',
                '"unique_trade_dates": 120',
                '"recommendation_group_variation_available": true',
                '"group_imbalance_warning": true',
                '"small_blocked_group_warning": true',
                '"actionability_all_never_actionable_review_only": true',
                '"position_outputs_not_evaluated_in_goal10b3": true',
                '"goal10d_status_after_goal10b3": "locked_future"',
                '"dashboard_daily_report_status_after_goal10b3": "locked_future"',
                '"portfolio_backtest_status_after_goal10b3": "locked_future"',
                '"recommendation_revalidation_signal_weak_or_unreliable": true',
            ]:
                if required_text not in goal10b3_manifest:
                    failures.append(f"GOAL-10B.3 manifest missing required marker: {required_text}")
            for required_false in [
                '"buy_sell_hold_outputs_generated": false',
                '"target_prices_generated": false',
                '"position_sizing_generated": false',
                '"target_weights_generated": false',
                '"portfolio_weights_generated": false',
                '"order_quantities_generated": false',
                '"portfolio_returns_generated": false',
                '"equity_curves_generated": false',
                '"dashboard_outputs_generated": false',
                '"dashboard_files_generated": false',
                '"html_generated": false',
                '"streamlit_generated": false',
                '"frontend_code_generated": false',
                '"visual_reports_generated": false',
                '"backtests_run": false',
                '"backtest_execution_run": false',
                '"local_lake_files_created": false',
                '"factor_mining_outputs_created": false',
                '"dqn_rl_outputs_created": false',
                '"goal10b_one_symbol_evidence_used": false',
                '"goal10b2_eight_row_evidence_used": false',
                '"dc02_evidence_used": false',
                '"outputs_samples_used": false',
                '"diagnostic_group_variation_fabricated": false',
                '"downstream_execution_unlocked_by_this_goal": false',
            ]:
                if required_false not in goal10b3_manifest:
                    failures.append(f"GOAL-10B.3 manifest missing false boundary flag: {required_false}")
        else:
            if goal10b3.get("status") != "locked_future" or goal10b3.get("implemented_in_repo") != "false":
                failures.append("GOAL-10B.3 must remain locked_future until valid GOAL-10B.3 evidence exists")
    if goal_risk_tiering01:
        if goal_risk_tiering01_evidence_ready:
            if not goal10b3_evidence_ready:
                failures.append("GOAL-RISK-TIERING-01 requires GOAL-10B.3 implemented_review_only evidence")
            if goal_risk_tiering01.get("status") != "implemented_review_only":
                failures.append("GOAL-RISK-TIERING-01 must be implemented_review_only when valid evidence exists")
            if goal_risk_tiering01.get("implemented_in_repo") != "true":
                failures.append("GOAL-RISK-TIERING-01 review-only row must be marked implemented")
            if goal_risk_tiering01.get("allowed_next_action") not in {
                GOAL_RISK_TIERING01_ALLOWED_NEXT_WEAK,
                GOAL_RISK_TIERING01_ALLOWED_NEXT_AVAILABLE,
            }:
                failures.append("GOAL-RISK-TIERING-01 allowed_next_action is invalid")
            if goal_risk_tiering01.get("depends_on") != GOAL10B3_WORKFLOW_ID:
                failures.append("GOAL-RISK-TIERING-01 must depend on GOAL-10B.3")
            for required_text in [
                '"mode": "review_only_risk_severity_numeric_score_tiering_gate"',
                '"risk_tiered_row_count": 6000',
                '"unique_symbols": 50',
                '"unique_trade_dates": 120',
                '"score_construction_excludes_future_returns": true',
                '"future_returns_used_only_for_post_hoc_evaluation": true',
                '"no_lookahead_score_construction_check": true',
                '"risk_bucket_variation_available": true',
                '"original_dc03_medium_rows": 5990',
                '"original_dc03_high_rows": 10',
                '"goal_rec_tiering01_status_after_goal_risk_tiering01": "locked_future"',
                '"goal10b4_status_after_goal_risk_tiering01": "locked_future"',
                '"position_band_validation_status_after_goal_risk_tiering01": "locked_future"',
                '"goal10d_status_after_goal_risk_tiering01": "locked_future"',
                '"dashboard_daily_report_status_after_goal_risk_tiering01": "locked_future"',
                '"portfolio_backtest_status_after_goal_risk_tiering01": "locked_future"',
            ]:
                if required_text not in goal_risk_tiering01_manifest:
                    failures.append(f"GOAL-RISK-TIERING-01 manifest missing required marker: {required_text}")
            if (
                '"signal_classification": "risk_tiering_signal_available"' not in goal_risk_tiering01_manifest
                and '"signal_classification": "risk_tiering_signal_weak_or_unreliable"' not in goal_risk_tiering01_manifest
                and '"signal_classification": "risk_tiering_not_evaluable"' not in goal_risk_tiering01_manifest
            ):
                failures.append("GOAL-RISK-TIERING-01 manifest missing signal classification")
            for required_false in [
                '"goal07b_outputs_overwritten": false',
                '"dc03_risk_diagnostics_overwritten": false',
                '"recommendation_outputs_created": false',
                '"goal08b_recommendation_rows_created": false',
                '"goal09_position_band_rows_created": false',
                '"position_outputs_created": false',
                '"buy_sell_hold_outputs_generated": false',
                '"target_prices_generated": false',
                '"actual_position_sizing_generated": false',
                '"order_quantities_generated": false',
                '"target_weights_generated": false',
                '"portfolio_weights_generated": false',
                '"portfolio_returns_generated": false',
                '"equity_curves_generated": false',
                '"dashboard_outputs_generated": false',
                '"dashboard_files_generated": false',
                '"html_generated": false',
                '"streamlit_generated": false',
                '"frontend_code_generated": false',
                '"visual_reports_generated": false',
                '"backtests_run": false',
                '"backtest_execution_run": false',
                '"signal_backtests_run": false',
                '"portfolio_backtests_run": false',
                '"goal10b4_run": false',
                '"position_band_validation_run": false',
                '"new_provider_data_fetched": false',
                '"local_lake_files_created": false',
                '"factor_mining_outputs_created": false',
                '"dqn_rl_outputs_created": false',
                '"outputs_samples_used": false',
                '"demo_fixture_used_as_primary_evidence": false',
                '"future_returns_used_in_score": false',
                '"score_weights_tuned_to_forward_returns": false',
                '"downstream_execution_unlocked_by_this_goal": false',
                '"goal_rec_tiering01_unlocked_by_this_goal": false',
                '"goal10b4_unlocked_by_this_goal": false',
                '"goal10d_unlocked_by_this_goal": false',
            ]:
                if required_false not in goal_risk_tiering01_manifest:
                    failures.append(f"GOAL-RISK-TIERING-01 manifest missing false boundary flag: {required_false}")
            for workflow_id, row, expected_dependency in [
                (
                    GOAL_REC_TIERING01_WORKFLOW_ID,
                    goal_rec_tiering01,
                    GOAL_QUANT_RESEARCH01_WORKFLOW_ID
                    if goal_quant_research01
                    else GOAL_RISK_TIERING011_WORKFLOW_ID
                    if goal_risk_tiering011
                    else GOAL_RISK_TIERING01_WORKFLOW_ID,
                ),
                (GOAL10B4_WORKFLOW_ID, goal10b4, GOAL_REC_TIERING01_WORKFLOW_ID),
                (POSITION_BAND_VALIDATION_WORKFLOW_ID, position_band_validation, GOAL10B4_WORKFLOW_ID),
            ]:
                if row.get("status") != "locked_future":
                    failures.append(f"{workflow_id} must remain locked_future after GOAL-RISK-TIERING-01")
                if row.get("implemented_in_repo") != "false":
                    failures.append(f"{workflow_id} must not be implemented after GOAL-RISK-TIERING-01")
                if row.get("depends_on") != expected_dependency:
                    failures.append(f"{workflow_id} dependency is invalid after GOAL-RISK-TIERING-01")
            _validate_locked_execution_downstream(failures, by_id, context="GOAL-RISK-TIERING-01")
        else:
            if goal_risk_tiering01.get("status") != "locked_future" or goal_risk_tiering01.get("implemented_in_repo") != "false":
                failures.append("GOAL-RISK-TIERING-01 must remain locked_future until valid evidence exists")
    if goal_risk_tiering011:
        if goal_risk_tiering011_evidence_ready:
            if not goal_risk_tiering01_evidence_ready:
                failures.append("GOAL-RISK-TIERING-01.1 requires GOAL-RISK-TIERING-01 implemented_review_only evidence")
            if goal_risk_tiering011.get("status") != "implemented_review_only":
                failures.append("GOAL-RISK-TIERING-01.1 must be implemented_review_only when valid evidence exists")
            if goal_risk_tiering011.get("implemented_in_repo") != "true":
                failures.append("GOAL-RISK-TIERING-01.1 review-only row must be marked implemented")
            if goal_risk_tiering011.get("allowed_next_action") not in {
                GOAL_RISK_TIERING011_ALLOWED_NEXT_WEAK,
                GOAL_RISK_TIERING011_ALLOWED_NEXT_AVAILABLE,
            }:
                failures.append("GOAL-RISK-TIERING-01.1 allowed_next_action is invalid")
            if goal_risk_tiering011.get("depends_on") != GOAL_RISK_TIERING01_WORKFLOW_ID:
                failures.append("GOAL-RISK-TIERING-01.1 must depend on GOAL-RISK-TIERING-01")
            for required_text in [
                '"mode": "review_only_risk_score_directionality_downside_repair_gate"',
                '"downside_risk_row_count": 6000',
                '"unique_symbols": 50',
                '"unique_trade_dates": 120',
                '"score_construction_excludes_future_returns": true',
                '"future_returns_used_only_for_post_hoc_evaluation": true',
                '"no_lookahead_score_construction_check": true',
                '"component_reconstruction_available": true',
                '"downside_bucket_variation_available": true',
                '"original_high_bucket_volatility_momentum_dominated": true',
                '"volatility_momentum_separated_from_downside_score": true',
                '"goal_rec_tiering01_status_after_goal_risk_tiering011": "locked_future"',
                '"goal10b4_status_after_goal_risk_tiering011": "locked_future"',
                '"position_band_validation_status_after_goal_risk_tiering011": "locked_future"',
                '"goal10d_status_after_goal_risk_tiering011": "locked_future"',
                '"dashboard_daily_report_status_after_goal_risk_tiering011": "locked_future"',
                '"portfolio_backtest_status_after_goal_risk_tiering011": "locked_future"',
            ]:
                if required_text not in goal_risk_tiering011_manifest:
                    failures.append(f"GOAL-RISK-TIERING-01.1 manifest missing required marker: {required_text}")
            if (
                '"signal_classification": "downside_risk_tiering_signal_available"' not in goal_risk_tiering011_manifest
                and '"signal_classification": "downside_risk_tiering_signal_weak_or_unreliable"' not in goal_risk_tiering011_manifest
                and '"signal_classification": "downside_risk_tiering_not_evaluable"' not in goal_risk_tiering011_manifest
            ):
                failures.append("GOAL-RISK-TIERING-01.1 manifest missing signal classification")
            for required_false in [
                '"goal_risk_tiering01_outputs_overwritten": false',
                '"dc03_risk_diagnostics_overwritten": false',
                '"recommendation_outputs_created": false',
                '"goal08b_recommendation_rows_created": false',
                '"goal09_position_band_rows_created": false',
                '"position_outputs_created": false',
                '"buy_sell_hold_outputs_generated": false',
                '"target_prices_generated": false',
                '"actual_position_sizing_generated": false',
                '"order_quantities_generated": false',
                '"target_weights_generated": false',
                '"portfolio_weights_generated": false',
                '"portfolio_returns_generated": false',
                '"equity_curves_generated": false',
                '"dashboard_outputs_generated": false',
                '"dashboard_files_generated": false',
                '"html_generated": false',
                '"streamlit_generated": false',
                '"frontend_code_generated": false',
                '"visual_reports_generated": false',
                '"backtests_run": false',
                '"backtest_execution_run": false',
                '"signal_backtests_run": false',
                '"portfolio_backtests_run": false',
                '"goal_rec_tiering01_run": false',
                '"goal10b4_run": false',
                '"position_band_validation_run": false',
                '"new_provider_data_fetched": false',
                '"local_lake_files_created": false',
                '"factor_mining_outputs_created": false',
                '"dqn_rl_outputs_created": false',
                '"outputs_samples_used": false',
                '"demo_fixture_used_as_primary_evidence": false',
                '"future_returns_used_in_score": false',
                '"score_weights_tuned_to_forward_returns": false',
                '"downstream_execution_unlocked_by_this_goal": false',
                '"goal_rec_tiering01_unlocked_by_this_goal": false',
                '"goal10b4_unlocked_by_this_goal": false',
                '"goal10d_unlocked_by_this_goal": false',
            ]:
                if required_false not in goal_risk_tiering011_manifest:
                    failures.append(f"GOAL-RISK-TIERING-01.1 manifest missing false boundary flag: {required_false}")
            for workflow_id, row, expected_dependency in [
                (
                    GOAL_REC_TIERING01_WORKFLOW_ID,
                    goal_rec_tiering01,
                    GOAL_QUANT_RESEARCH01_WORKFLOW_ID if goal_quant_research01 else GOAL_RISK_TIERING011_WORKFLOW_ID,
                ),
                (GOAL10B4_WORKFLOW_ID, goal10b4, GOAL_REC_TIERING01_WORKFLOW_ID),
                (POSITION_BAND_VALIDATION_WORKFLOW_ID, position_band_validation, GOAL10B4_WORKFLOW_ID),
            ]:
                if row.get("status") != "locked_future":
                    failures.append(f"{workflow_id} must remain locked_future after GOAL-RISK-TIERING-01.1")
                if row.get("implemented_in_repo") != "false":
                    failures.append(f"{workflow_id} must not be implemented after GOAL-RISK-TIERING-01.1")
                if row.get("depends_on") != expected_dependency:
                    failures.append(f"{workflow_id} dependency is invalid after GOAL-RISK-TIERING-01.1")
            _validate_locked_execution_downstream(failures, by_id, context="GOAL-RISK-TIERING-01.1")
        else:
            if goal_risk_tiering011.get("status") != "locked_future" or goal_risk_tiering011.get("implemented_in_repo") != "false":
                failures.append("GOAL-RISK-TIERING-01.1 must remain locked_future until valid evidence exists")
    if goal_quant_research01:
        if goal_quant_research01_evidence_ready:
            if not goal_risk_tiering011_evidence_ready:
                failures.append("GOAL-QUANT-RESEARCH-01 requires GOAL-RISK-TIERING-01.1 implemented_review_only evidence")
            if goal_quant_research01.get("status") != "implemented_research_only":
                failures.append("GOAL-QUANT-RESEARCH-01 must be implemented_research_only when valid evidence exists")
            if goal_quant_research01.get("implemented_in_repo") != "true":
                failures.append("GOAL-QUANT-RESEARCH-01 research-only row must be marked implemented")
            if goal_quant_research01.get("allowed_next_action") not in {
                GOAL_QUANT_RESEARCH01_ALLOWED_NEXT_WEAK,
                GOAL_QUANT_RESEARCH01_ALLOWED_NEXT_AVAILABLE,
            }:
                failures.append("GOAL-QUANT-RESEARCH-01 allowed_next_action is invalid")
            if goal_quant_research01.get("depends_on") != GOAL_RISK_TIERING011_WORKFLOW_ID:
                failures.append("GOAL-QUANT-RESEARCH-01 must depend on GOAL-RISK-TIERING-01.1")
            for required_text in [
                '"mode": "research_only_factor_research_lab_and_score_validity_gate"',
                '"factor_count": 11',
                '"source_panel_row_count": 6000',
                '"factor_evaluation_row_count": 66000',
                '"future_returns_used_only_for_posthoc_evaluation": true',
                '"no_lookahead_validation_passed": true',
                '"trial_registry_created": true',
                '"anti_overfitting_policy_recorded": true',
                '"goal_rec_tiering01_locked_future": true',
                '"goal10b4_locked_future": true',
                '"position_band_validation_locked_future": true',
                '"goal10d_locked_future": true',
                '"dashboard_daily_report_locked_future": true',
                '"portfolio_backtest_locked_future": true',
            ]:
                if required_text not in goal_quant_research01_manifest:
                    failures.append(f"GOAL-QUANT-RESEARCH-01 manifest missing required marker: {required_text}")
            if (
                '"overall_score_validity_status": "no_factor_ready_for_rec_tiering"' not in goal_quant_research01_manifest
                and '"overall_score_validity_status": "factor_candidate_for_rec_tiering_available"' not in goal_quant_research01_manifest
            ):
                failures.append("GOAL-QUANT-RESEARCH-01 manifest missing score validity status")
            for required_false in [
                '"recommendation_outputs_created": false',
                '"goal08b_recommendation_rows_created": false',
                '"goal09_position_band_rows_created": false',
                '"goal_rec_tiering01_run": false',
                '"goal10b4_run": false',
                '"position_band_validation_run": false',
                '"goal10d_run": false',
                '"buy_sell_hold_outputs_generated": false',
                '"target_prices_generated": false',
                '"actual_position_sizing_generated": false',
                '"target_weights_generated": false',
                '"portfolio_weights_generated": false',
                '"order_quantities_generated": false',
                '"portfolio_returns_generated": false',
                '"equity_curves_generated": false',
                '"dashboard_outputs_generated": false',
                '"html_generated": false',
                '"streamlit_generated": false',
                '"frontend_code_generated": false',
                '"visual_reports_generated": false',
                '"trading_outputs_created": false',
                '"broker_outputs_created": false',
                '"production_outputs_created": false',
                '"local_lake_outputs_created": false',
                '"factor_mining_outputs_created": false',
                '"dqn_rl_outputs_created": false',
                '"live_provider_fetches_run": false',
                '"future_returns_used_in_score_construction": false',
                '"production_predictive_validity_claimed": false',
            ]:
                if required_false not in goal_quant_research01_manifest:
                    failures.append(f"GOAL-QUANT-RESEARCH-01 manifest missing false boundary flag: {required_false}")
            for workflow_id, row, expected_dependency in [
                (GOAL_REC_TIERING01_WORKFLOW_ID, goal_rec_tiering01, GOAL_QUANT_RESEARCH01_WORKFLOW_ID),
                (GOAL10B4_WORKFLOW_ID, goal10b4, GOAL_REC_TIERING01_WORKFLOW_ID),
                (POSITION_BAND_VALIDATION_WORKFLOW_ID, position_band_validation, GOAL10B4_WORKFLOW_ID),
            ]:
                if row.get("status") != "locked_future":
                    failures.append(f"{workflow_id} must remain locked_future after GOAL-QUANT-RESEARCH-01")
                if row.get("implemented_in_repo") != "false":
                    failures.append(f"{workflow_id} must not be implemented after GOAL-QUANT-RESEARCH-01")
                if row.get("depends_on") != expected_dependency:
                    failures.append(f"{workflow_id} dependency is invalid after GOAL-QUANT-RESEARCH-01")
            _validate_locked_execution_downstream(failures, by_id, context="GOAL-QUANT-RESEARCH-01")
        else:
            if goal_quant_research01.get("status") != "locked_future" or goal_quant_research01.get("implemented_in_repo") != "false":
                failures.append("GOAL-QUANT-RESEARCH-01 must remain locked_future until valid evidence exists")
    if goal10d.get("status") != "locked_future":
        failures.append("GOAL-10D must remain locked_future after GOAL-10C")
    if goal10d.get("implemented_in_repo") != "false":
        failures.append("GOAL-10D must not be implemented after GOAL-10C")
    if goal10d.get("depends_on") != GOAL10C_WORKFLOW_ID:
        failures.append("GOAL-10D must depend on GOAL-10C")
    _validate_locked_execution_downstream(failures, by_id, context="GOAL-10C")

    status = "PASS" if not failures else "BLOCKED"
    table_rows = [_status_table_row(row) for row in rows]
    write_csv(
        root / "outputs/audits/workflow_status_table.csv",
        table_rows,
        [
            "workflow_id",
            "display_name",
            "status",
            "diagram_edge_type",
            "can_promote_now",
            "promotion_blocker",
            "next_required_goal",
        ],
    )
    write_text(
        root / "outputs/audits/workflow_status_audit.md",
        "\n".join(
            [
                "# Workflow Status Audit",
                "",
                f"Workflow Status Audit: {status}",
                "",
                f"Rows checked: `{len(rows)}`",
                f"Failures: `{len(failures)}`",
                f"Warnings: `{len(warnings)}`",
                "",
                f"GOAL-06C status: `{goal06c_status or 'missing'}`.",
                f"GOAL-06C.5 status: `{goal06c5_status or 'missing'}`.",
                f"GOAL-06C.6 status: `{goal06c6_status or 'missing'}`.",
                f"GOAL-06C.6A status: `{goal06c6a_status or 'missing'}`.",
                f"GOAL-06C.7 status: `{goal06c7_status or 'missing'}`.",
                f"GOAL-06D status: `{goal06d_status or 'missing'}`.",
                f"GOAL-06D allowed next action: `{goal06d.get('allowed_next_action', 'missing')}`.",
                f"GOAL-06D.1 status: `{goal06d1_status or 'missing'}`.",
                f"GOAL-06D.1 allowed next action: `{goal06d1.get('allowed_next_action', 'missing')}`.",
                f"V2 factor research status: `{v2_factor.get('status', 'missing')}`.",
                f"GOAL-07A status: `{goal07a_status or 'missing'}`.",
                f"GOAL-07A.1 status: `{goal07a1_status or 'missing'}`.",
                f"GOAL-07B.0 status: `{goal07b0_status or 'missing'}`.",
                f"GOAL-07B status: `{goal07b_status or 'missing'}`.",
                f"GOAL-08A status: `{goal08a_status or 'missing'}`.",
                f"GOAL-STORAGE-01 status: `{goal_storage01_status or 'missing'}`.",
                f"GOAL-08B.0 status: `{goal08b0_status or 'missing'}`.",
                f"GOAL-08B status: `{goal08b_status or 'missing'}`.",
                f"GOAL-09.0 status: `{goal090_status or 'missing'}`.",
                f"GOAL-09 status: `{goal09_status or 'missing'}`.",
                f"GOAL-09.1 status: `{goal091_status or 'missing'}`.",
                f"GOAL-V1-INTEGRITY-01 status: `{goal_v1_integrity01_status or 'missing'}`.",
                f"GOAL-10A status: `{goal10a_status or 'missing'}`.",
                f"GOAL-10B status: `{goal10b_status or 'missing'}`.",
                f"GOAL-10B.1 status: `{goal10b1_status or 'missing'}`.",
                f"GOAL-DATA-LABEL-01 status: `{goal_data_label01_status or 'missing'}`.",
                f"GOAL-V1-DIAGNOSTIC-COVERAGE-02 status: `{goal_v1_diagnostic_coverage02.get('status', 'missing')}`.",
                f"GOAL-10B.2 status: `{goal10b2.get('status', 'missing')}`.",
                f"GOAL-10C status: `{goal10c.get('status', 'missing')}`.",
                f"GOAL-DATA-PROVIDER-02A status: `{goal_data_provider02a.get('status', 'missing')}`.",
                f"GOAL-DATA-PROVIDER-02A.1 status: `{goal_data_provider02a1.get('status', 'missing')}`.",
                f"GOAL-DATA-PROVIDER-02B status: `{goal_data_provider02b.get('status', 'missing')}`.",
                f"GOAL-DATA-PANEL-02 status: `{goal_data_panel02.get('status', 'missing')}`.",
                f"GOAL-V1-DIAGNOSTIC-COVERAGE-03 status: `{goal_v1_diagnostic_coverage03.get('status', 'missing')}`.",
                f"GOAL-10B.3 status: `{goal10b3.get('status', 'missing')}`.",
                f"GOAL-RISK-TIERING-01 status: `{goal_risk_tiering01.get('status', 'missing')}`.",
                f"GOAL-RISK-TIERING-01.1 status: `{goal_risk_tiering011.get('status', 'missing')}`.",
                f"GOAL-QUANT-RESEARCH-01 status: `{goal_quant_research01.get('status', 'missing')}`.",
                f"GOAL-REC-TIERING-01 status: `{goal_rec_tiering01.get('status', 'missing')}`.",
                f"GOAL-10B.4 status: `{goal10b4.get('status', 'missing')}`.",
                f"GOAL-POSITION-BAND-VALIDATION-01 status: `{position_band_validation.get('status', 'missing')}`.",
                f"GOAL-10D status: `{goal10d.get('status', 'missing')}`.",
                "GOAL-06D may be `implemented_review_only` only with PASS/PASS_WITH_WARNINGS readiness evidence; GOAL-07A may be `implemented_design_only` only with design-only evidence; GOAL-07B may be `future_review_only` only after GOAL-07B.0 evidence and `implemented_review_only` only with a PASS/PASS_WITH_WARNINGS diagnostic-only calculation report; GOAL-08A may be `implemented_design_only` only with names-only contract evidence and zero recommendation rows; GOAL-STORAGE-01 may be `implemented_infrastructure_only` only with local research lake hardening evidence; GOAL-08B may be `future_review_only` eligible only after GOAL-08B.0 evidence and `implemented_review_only` only with a PASS/PASS_WITH_WARNINGS non-actionable diagnostic report; GOAL-09 may be `future_review_only` eligible only after GOAL-09.0 evidence and `implemented_review_only` only with a PASS/PASS_WITH_WARNINGS non-actionable position-band diagnostic report; GOAL-09.1 may be `implemented_review_only` only with PASS/PASS_WITH_WARNINGS warning review and dashboard-readiness evidence; GOAL-V1-INTEGRITY-01 may be `implemented_infrastructure_only` only with PASS/PASS_WITH_WARNINGS artifact-lineage and structure evidence; GOAL-10A may be `implemented_design_only` only with PASS/PASS_WITH_WARNINGS backtest contract design evidence; GOAL-10B may be `implemented_review_only` only with PASS/PASS_WITH_WARNINGS non-actionable recommendation diagnostics backtest evidence; GOAL-10B.1 may be `implemented_review_only` only with PASS/PASS_WITH_WARNINGS coverage repair diagnostic evidence; GOAL-DATA-LABEL-01 may be `implemented_review_only` only with PASS/PASS_WITH_WARNINGS forward-return label coverage evidence; GOAL-V1-DIAGNOSTIC-COVERAGE-02 may be `implemented_review_only` only with PASS/PASS_WITH_WARNINGS multi-symbol non-actionable diagnostic evidence; GOAL-DATA-PROVIDER-02A may be `implemented_review_only` only with PASS/PASS_WITH_WARNINGS provider capability probe evidence; GOAL-DATA-PROVIDER-02A.1 may be `implemented_review_only` only with PASS/PASS_WITH_WARNINGS network opt-in smoke-test evidence; GOAL-RISK-TIERING-01 may be `implemented_review_only` only with PASS/PASS_WITH_WARNINGS non-actionable risk tiering evidence; GOAL-RISK-TIERING-01.1 may be `implemented_review_only` only with PASS/PASS_WITH_WARNINGS non-actionable downside-risk repair evidence; GOAL-QUANT-RESEARCH-01 may be `implemented_research_only` only with PASS/PASS_WITH_WARNINGS research-only factor lab evidence.",
                "GOAL-06C and later are not represented as `implemented_active`.",
                "GOAL-07B risk overlay diagnostics, GOAL-08B recommendation diagnostics, GOAL-09 position-band diagnostics, GOAL-09.1 dashboard-readiness warning review, GOAL-10B recommendation diagnostics backtest, GOAL-10B.1 coverage repair diagnostics, GOAL-DATA-LABEL-01 forward-return label coverage, GOAL-V1-DIAGNOSTIC-COVERAGE-02 multi-symbol diagnostic coverage, GOAL-DATA-PROVIDER-02A provider capability metadata, GOAL-DATA-PROVIDER-02A.1 provider smoke-test metadata, and GOAL-QUANT-RESEARCH-01 factor validity diagnostics are non-actionable/research-only when implemented; GOAL-V1-INTEGRITY-01 is infrastructure-only artifact-lineage governance; GOAL-10A is design-only backtest contract governance. Actual positions, dashboard output, paper/live trading, production, portfolio backtests, performance rows, factor-mining, broker, local-lake, and DQN/RL remain locked or deleted from active mainline.",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
                "## Warnings",
                *[f"- {warning}" for warning in warnings],
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/audits/workflow_diagram_update_report.md",
        "\n".join(
            [
                "# Workflow Diagram Update Report",
                "",
                "Status: `PASS`" if status == "PASS" else "Status: `BLOCKED`",
                "",
                "Updated diagrams are governed by `configs/project/workflow_status.csv`.",
                "Solid arrows represent `implemented_active` workflow through GOAL-06B.",
                "Dotted arrows represent future, design-only, locked, not-started, or deleted-from-mainline workflow blocks.",
                "Workflow promotion requires a readiness report, passing validation/verification, status-file update, diagram update, and downstream-lock review.",
                "",
            ]
        ),
    )
    return status == "PASS"


def _validate_rows(rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    by_id = {row["workflow_id"]: row for row in rows}
    missing_active = sorted(REQUIRED_ACTIVE_IDS - set(by_id))
    if missing_active:
        failures.append(f"missing implemented active rows: {missing_active}")
    for row in rows:
        workflow_id = row["workflow_id"]
        status = row["status"]
        if status not in ALLOWED_STATUSES:
            failures.append(f"{workflow_id} has invalid status `{status}`")
        if workflow_id in REQUIRED_ACTIVE_IDS and status != "implemented_active":
            failures.append(f"{workflow_id} must be implemented_active")
        if workflow_id.startswith("goal06c") or workflow_id.startswith("goal06d"):
            if status == "implemented_active":
                failures.append(f"{workflow_id} is incorrectly implemented_active")
        if workflow_id == "v2_factor_research_upgrade" and status != "planned_locked":
            failures.append("v2_factor_research_upgrade must remain planned_locked")
        if workflow_id == GOAL07B_WORKFLOW_ID:
            if status not in GOAL07B_ALLOWED_STATUSES:
                failures.append("goal07b_risk_overlay_calculation must be locked_future, future_review_only, or implemented_review_only")
            if row["implemented_in_repo"] == "true" and status != "implemented_review_only":
                failures.append("goal07b_risk_overlay_calculation must be implemented only when implemented_review_only")
        if workflow_id == GOAL08A_WORKFLOW_ID:
            if status not in GOAL08A_ALLOWED_STATUSES:
                failures.append("goal08a_recommendation_contract_design_gate must be locked_future or implemented_design_only")
            if row["implemented_in_repo"] == "true" and status != "implemented_design_only":
                failures.append("goal08a_recommendation_contract_design_gate must be implemented only when implemented_design_only")
        if workflow_id == GOAL_STORAGE01_WORKFLOW_ID:
            if status != "implemented_infrastructure_only":
                failures.append("goal_storage01_local_research_lake_hardening_gate must be implemented_infrastructure_only")
            if row["implemented_in_repo"] != "true":
                failures.append("goal_storage01_local_research_lake_hardening_gate must be marked implemented")
        if workflow_id == GOAL08B0_WORKFLOW_ID:
            if status != "implemented_review_only":
                failures.append("goal08b0_recommendation_review_only_unlock_gate must be implemented_review_only")
            if row["implemented_in_repo"] != "true":
                failures.append("goal08b0_recommendation_review_only_unlock_gate must be marked implemented")
        if workflow_id == GOAL08B_WORKFLOW_ID:
            if status not in GOAL08B_ALLOWED_STATUSES:
                failures.append("goal08b_recommendation_review_only_prototype must be locked_future, future_review_only, or implemented_review_only")
            if status == "implemented_review_only":
                if row["implemented_in_repo"] != "true":
                    failures.append("goal08b_recommendation_review_only_prototype implemented_review_only must be marked implemented")
            elif row["implemented_in_repo"] != "false":
                failures.append("goal08b_recommendation_review_only_prototype must not be implemented without GOAL-08B diagnostics evidence")
        if workflow_id == GOAL090_WORKFLOW_ID:
            if status != "implemented_review_only":
                failures.append("goal090_position_band_review_only_unlock_gate must be implemented_review_only")
            if row["implemented_in_repo"] != "true":
                failures.append("goal090_position_band_review_only_unlock_gate must be marked implemented")
        if workflow_id == GOAL09_WORKFLOW_ID:
            if status not in GOAL09_ALLOWED_STATUSES:
                failures.append("position_band_recommendation must be locked_future, future_review_only, or implemented_review_only")
            if status == "implemented_review_only":
                if row["implemented_in_repo"] != "true":
                    failures.append("position_band_recommendation implemented_review_only must be marked implemented")
            elif row["implemented_in_repo"] != "false":
                failures.append("position_band_recommendation must not be implemented without GOAL-09 diagnostics evidence")
        if workflow_id == GOAL091_WORKFLOW_ID:
            if status != "implemented_review_only":
                failures.append("goal091_position_band_warning_dashboard_readiness_gate must be implemented_review_only")
            if row["implemented_in_repo"] != "true":
                failures.append("goal091_position_band_warning_dashboard_readiness_gate must be marked implemented")
            if row["allowed_next_action"] != GOAL091_ALLOWED_NEXT:
                failures.append("goal091_position_band_warning_dashboard_readiness_gate allowed_next_action is invalid")
        if workflow_id == GOAL_V1_INTEGRITY01_WORKFLOW_ID:
            if status != "implemented_infrastructure_only":
                failures.append("goal_v1_integrity01_artifact_lineage_structure_gate must be implemented_infrastructure_only")
            if row["implemented_in_repo"] != "true":
                failures.append("goal_v1_integrity01_artifact_lineage_structure_gate must be marked implemented")
            if row["allowed_next_action"] != GOAL_V1_INTEGRITY01_ALLOWED_NEXT:
                failures.append("goal_v1_integrity01_artifact_lineage_structure_gate allowed_next_action is invalid")
            if row["depends_on"] != GOAL091_WORKFLOW_ID:
                failures.append("goal_v1_integrity01_artifact_lineage_structure_gate must depend on GOAL-09.1")
        if workflow_id == GOAL10A_WORKFLOW_ID:
            if status != "implemented_design_only":
                failures.append("goal10a_backtest_contract_design_gate must be implemented_design_only")
            if row["implemented_in_repo"] != "true":
                failures.append("goal10a_backtest_contract_design_gate must be marked implemented")
            if row["allowed_next_action"] != GOAL10A_ALLOWED_NEXT:
                failures.append("goal10a_backtest_contract_design_gate allowed_next_action is invalid")
            if row["depends_on"] != GOAL_V1_INTEGRITY01_WORKFLOW_ID:
                failures.append("goal10a_backtest_contract_design_gate must depend on GOAL-V1-INTEGRITY-01")
        if workflow_id == GOAL10B_WORKFLOW_ID:
            if status != "implemented_review_only":
                failures.append("goal10b_backtest_review_only_validation_gate must be implemented_review_only")
            if row["implemented_in_repo"] != "true":
                failures.append("goal10b_backtest_review_only_validation_gate must be marked implemented")
            if row["allowed_next_action"] != GOAL10B_ALLOWED_NEXT:
                failures.append("goal10b_backtest_review_only_validation_gate allowed_next_action is invalid")
            if row["depends_on"] != GOAL10A_WORKFLOW_ID:
                failures.append("goal10b_backtest_review_only_validation_gate must depend on GOAL-10A")
        if workflow_id == GOAL10B1_WORKFLOW_ID:
            if status != "implemented_review_only":
                failures.append("goal10b1_backtest_coverage_repair_gate must be implemented_review_only")
            if row["implemented_in_repo"] != "true":
                failures.append("goal10b1_backtest_coverage_repair_gate must be marked implemented")
            if row["allowed_next_action"] != GOAL10B1_ALLOWED_NEXT:
                failures.append("goal10b1_backtest_coverage_repair_gate allowed_next_action is invalid")
            if row["depends_on"] != GOAL10B_WORKFLOW_ID:
                failures.append("goal10b1_backtest_coverage_repair_gate must depend on GOAL-10B")
        if workflow_id == GOAL_DATA_LABEL01_WORKFLOW_ID:
            if status != "implemented_review_only":
                failures.append("goal_data_label01_forward_return_label_coverage_expansion must be implemented_review_only")
            if row["implemented_in_repo"] != "true":
                failures.append("goal_data_label01_forward_return_label_coverage_expansion must be marked implemented")
            if row["allowed_next_action"] != GOAL_DATA_LABEL01_ALLOWED_NEXT:
                failures.append("goal_data_label01_forward_return_label_coverage_expansion allowed_next_action is invalid")
            if row["depends_on"] != GOAL10B1_WORKFLOW_ID:
                failures.append("goal_data_label01_forward_return_label_coverage_expansion must depend on GOAL-10B.1")
        if workflow_id == GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID:
            if status not in {"locked_future", "implemented_review_only"}:
                failures.append("goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion must be locked_future or implemented_review_only")
            if status == "implemented_review_only":
                if row["implemented_in_repo"] != "true":
                    failures.append("goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion implemented_review_only must be marked implemented")
                if row["allowed_next_action"] != GOAL_V1_DIAGNOSTIC_COVERAGE02_ALLOWED_NEXT:
                    failures.append("goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion allowed_next_action is invalid")
            elif row["implemented_in_repo"] != "false":
                failures.append("goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion must not be marked implemented without diagnostic evidence")
            if row["depends_on"] != GOAL_DATA_LABEL01_WORKFLOW_ID:
                failures.append("goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion must depend on GOAL-DATA-LABEL-01")
        if workflow_id == GOAL10B2_WORKFLOW_ID:
            if status not in {"locked_future", "implemented_review_only"}:
                failures.append("goal10b2_recommendation_backtest_revalidation must be locked_future or implemented_review_only")
            if status == "implemented_review_only":
                if row["implemented_in_repo"] != "true":
                    failures.append("goal10b2_recommendation_backtest_revalidation implemented_review_only must be marked implemented")
                if row["allowed_next_action"] != GOAL10B2_ALLOWED_NEXT:
                    failures.append("goal10b2_recommendation_backtest_revalidation allowed_next_action is invalid")
            elif row["implemented_in_repo"] != "false":
                failures.append("goal10b2_recommendation_backtest_revalidation must not be marked implemented without evidence")
            if row["depends_on"] != GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID:
                failures.append("goal10b2_recommendation_backtest_revalidation must depend on GOAL-V1-DIAGNOSTIC-COVERAGE-02")
        if workflow_id == GOAL10C_WORKFLOW_ID:
            if status not in {"locked_future", "implemented_review_only"}:
                failures.append("goal10c_backtest_cost_slippage_sensitivity_gate must be locked_future or implemented_review_only")
            if status == "implemented_review_only":
                if row["implemented_in_repo"] != "true":
                    failures.append("goal10c_backtest_cost_slippage_sensitivity_gate implemented_review_only must be marked implemented")
                if row["allowed_next_action"] != GOAL10C_ALLOWED_NEXT:
                    failures.append("goal10c_backtest_cost_slippage_sensitivity_gate allowed_next_action is invalid")
            elif row["implemented_in_repo"] != "false":
                failures.append("goal10c_backtest_cost_slippage_sensitivity_gate must not be marked implemented without evidence")
            if row["depends_on"] != GOAL10B2_WORKFLOW_ID:
                failures.append("goal10c_backtest_cost_slippage_sensitivity_gate dependency is invalid")
        if workflow_id == GOAL_DATA_PROVIDER02A_WORKFLOW_ID:
            if status != "implemented_review_only":
                failures.append("goal_data_provider02a_multi_provider_capability_probe must be implemented_review_only")
            if row["implemented_in_repo"] != "true":
                failures.append("goal_data_provider02a_multi_provider_capability_probe must be marked implemented")
            if row["allowed_next_action"] != GOAL_DATA_PROVIDER02A_ALLOWED_NEXT:
                failures.append("goal_data_provider02a_multi_provider_capability_probe allowed_next_action is invalid")
            if row["depends_on"] != GOAL10C_WORKFLOW_ID:
                failures.append("goal_data_provider02a_multi_provider_capability_probe must depend on GOAL-10C")
        if workflow_id == GOAL_DATA_PROVIDER02A1_WORKFLOW_ID:
            if status != "implemented_review_only":
                failures.append("goal_data_provider02a1_network_opt_in_provider_smoke_test must be implemented_review_only")
            if row["implemented_in_repo"] != "true":
                failures.append("goal_data_provider02a1_network_opt_in_provider_smoke_test must be marked implemented")
            if row["allowed_next_action"] != GOAL_DATA_PROVIDER02A1_ALLOWED_NEXT:
                failures.append("goal_data_provider02a1_network_opt_in_provider_smoke_test allowed_next_action is invalid")
            if row["depends_on"] != GOAL_DATA_PROVIDER02A_WORKFLOW_ID:
                failures.append("goal_data_provider02a1_network_opt_in_provider_smoke_test must depend on GOAL-DATA-PROVIDER-02A")
        if workflow_id == GOAL_DATA_PROVIDER02B_WORKFLOW_ID:
            if status not in {"locked_future", "implemented_review_only"}:
                failures.append("goal_data_provider02b_provider_selection_gate must be locked_future or implemented_review_only")
            if status == "implemented_review_only":
                if row["implemented_in_repo"] != "true":
                    failures.append("goal_data_provider02b_provider_selection_gate implemented_review_only must be marked implemented")
                if row["allowed_next_action"] != GOAL_DATA_PROVIDER02B_ALLOWED_NEXT:
                    failures.append("goal_data_provider02b_provider_selection_gate allowed_next_action is invalid")
            elif row["implemented_in_repo"] != "false":
                failures.append("goal_data_provider02b_provider_selection_gate must remain unimplemented while locked_future")
            if row["depends_on"] != GOAL_DATA_PROVIDER02A1_WORKFLOW_ID:
                failures.append("goal_data_provider02b_provider_selection_gate must depend on GOAL-DATA-PROVIDER-02A.1")
        if workflow_id == GOAL_DATA_PANEL02_WORKFLOW_ID:
            if status != "locked_future" or row["implemented_in_repo"] != "false":
                failures.append("goal_data_panel02_evaluation_panel_gate must remain locked_future and unimplemented")
            if row["depends_on"] != GOAL_DATA_PROVIDER02B_WORKFLOW_ID:
                failures.append("goal_data_panel02_evaluation_panel_gate must depend on GOAL-DATA-PROVIDER-02B")
        if workflow_id == GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID:
            if status not in {"locked_future", "implemented_review_only"}:
                failures.append("goal_v1_diagnostic_coverage03_multi_provider_diagnostics must be locked_future or implemented_review_only")
            if status == "implemented_review_only":
                if row["implemented_in_repo"] != "true":
                    failures.append("goal_v1_diagnostic_coverage03_multi_provider_diagnostics implemented_review_only must be marked implemented")
                if row["allowed_next_action"] != GOAL_V1_DIAGNOSTIC_COVERAGE03_ALLOWED_NEXT:
                    failures.append("goal_v1_diagnostic_coverage03_multi_provider_diagnostics allowed_next_action is invalid")
                if row["depends_on"] != GOAL_DATA_PROVIDER02B_WORKFLOW_ID:
                    failures.append("goal_v1_diagnostic_coverage03_multi_provider_diagnostics implemented row must depend on GOAL-DATA-PROVIDER-02B")
            else:
                if row["implemented_in_repo"] != "false":
                    failures.append("goal_v1_diagnostic_coverage03_multi_provider_diagnostics must remain unimplemented while locked_future")
                if row["depends_on"] not in {GOAL_DATA_PANEL02_WORKFLOW_ID, GOAL_DATA_PROVIDER02B_WORKFLOW_ID}:
                    failures.append("goal_v1_diagnostic_coverage03_multi_provider_diagnostics locked row has invalid dependency")
        if workflow_id == GOAL10B3_WORKFLOW_ID:
            if status not in {"locked_future", "implemented_review_only"}:
                failures.append("goal10b3_recommendation_backtest_revalidation must be locked_future or implemented_review_only")
            if status == "implemented_review_only":
                if row["implemented_in_repo"] != "true":
                    failures.append("goal10b3_recommendation_backtest_revalidation implemented_review_only must be marked implemented")
                if row["allowed_next_action"] != GOAL10B3_ALLOWED_NEXT:
                    failures.append("goal10b3_recommendation_backtest_revalidation allowed_next_action is invalid")
                if row["depends_on"] != GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID:
                    failures.append("goal10b3_recommendation_backtest_revalidation implemented row must depend on GOAL-V1-DIAGNOSTIC-COVERAGE-03")
            else:
                if row["implemented_in_repo"] != "false":
                    failures.append("goal10b3_recommendation_backtest_revalidation must remain unimplemented while locked_future")
                if row["depends_on"] != GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID:
                    failures.append("goal10b3_recommendation_backtest_revalidation locked row must depend on GOAL-V1-DIAGNOSTIC-COVERAGE-03")
        if workflow_id == GOAL_RISK_TIERING01_WORKFLOW_ID:
            if status not in {"locked_future", "implemented_review_only"}:
                failures.append("goal_risk_tiering01_risk_severity_numeric_score_gate must be locked_future or implemented_review_only")
            if status == "implemented_review_only":
                if row["implemented_in_repo"] != "true":
                    failures.append("goal_risk_tiering01_risk_severity_numeric_score_gate implemented_review_only must be marked implemented")
                if row["allowed_next_action"] not in {GOAL_RISK_TIERING01_ALLOWED_NEXT_WEAK, GOAL_RISK_TIERING01_ALLOWED_NEXT_AVAILABLE}:
                    failures.append("goal_risk_tiering01_risk_severity_numeric_score_gate allowed_next_action is invalid")
                if row["depends_on"] != GOAL10B3_WORKFLOW_ID:
                    failures.append("goal_risk_tiering01_risk_severity_numeric_score_gate implemented row must depend on GOAL-10B.3")
            else:
                if row["implemented_in_repo"] != "false":
                    failures.append("goal_risk_tiering01_risk_severity_numeric_score_gate must remain unimplemented while locked_future")
                if row["depends_on"] != GOAL10B3_WORKFLOW_ID:
                    failures.append("goal_risk_tiering01_risk_severity_numeric_score_gate locked row must depend on GOAL-10B.3")
        if workflow_id == GOAL_RISK_TIERING011_WORKFLOW_ID:
            if status not in {"locked_future", "implemented_review_only"}:
                failures.append("goal_risk_tiering011_downside_risk_repair_gate must be locked_future or implemented_review_only")
            if status == "implemented_review_only":
                if row["implemented_in_repo"] != "true":
                    failures.append("goal_risk_tiering011_downside_risk_repair_gate implemented_review_only must be marked implemented")
                if row["allowed_next_action"] not in {GOAL_RISK_TIERING011_ALLOWED_NEXT_WEAK, GOAL_RISK_TIERING011_ALLOWED_NEXT_AVAILABLE}:
                    failures.append("goal_risk_tiering011_downside_risk_repair_gate allowed_next_action is invalid")
                if row["depends_on"] != GOAL_RISK_TIERING01_WORKFLOW_ID:
                    failures.append("goal_risk_tiering011_downside_risk_repair_gate implemented row must depend on GOAL-RISK-TIERING-01")
            else:
                if row["implemented_in_repo"] != "false":
                    failures.append("goal_risk_tiering011_downside_risk_repair_gate must remain unimplemented while locked_future")
                if row["depends_on"] != GOAL_RISK_TIERING01_WORKFLOW_ID:
                    failures.append("goal_risk_tiering011_downside_risk_repair_gate locked row must depend on GOAL-RISK-TIERING-01")
        if workflow_id == GOAL_QUANT_RESEARCH01_WORKFLOW_ID:
            if status not in {"locked_future", "implemented_research_only"}:
                failures.append("goal_quant_research01_factor_research_lab_gate must be locked_future or implemented_research_only")
            if status == "implemented_research_only":
                if row["implemented_in_repo"] != "true":
                    failures.append("goal_quant_research01_factor_research_lab_gate implemented_research_only must be marked implemented")
                if row["allowed_next_action"] not in {GOAL_QUANT_RESEARCH01_ALLOWED_NEXT_WEAK, GOAL_QUANT_RESEARCH01_ALLOWED_NEXT_AVAILABLE}:
                    failures.append("goal_quant_research01_factor_research_lab_gate allowed_next_action is invalid")
                if row["depends_on"] != GOAL_RISK_TIERING011_WORKFLOW_ID:
                    failures.append("goal_quant_research01_factor_research_lab_gate implemented row must depend on GOAL-RISK-TIERING-01.1")
            else:
                if row["implemented_in_repo"] != "false":
                    failures.append("goal_quant_research01_factor_research_lab_gate must remain unimplemented while locked_future")
                if row["depends_on"] != GOAL_RISK_TIERING011_WORKFLOW_ID:
                    failures.append("goal_quant_research01_factor_research_lab_gate locked row must depend on GOAL-RISK-TIERING-01.1")
        if workflow_id == GOAL_REC_TIERING01_WORKFLOW_ID:
            if status != "locked_future" or row["implemented_in_repo"] != "false":
                failures.append("goal_rec_tiering01_recommendation_score_tiering_gate must remain locked_future and unimplemented")
            expected_risk_dependency = (
                GOAL_QUANT_RESEARCH01_WORKFLOW_ID
                if GOAL_QUANT_RESEARCH01_WORKFLOW_ID in by_id
                else GOAL_RISK_TIERING011_WORKFLOW_ID
                if GOAL_RISK_TIERING011_WORKFLOW_ID in by_id
                else GOAL_RISK_TIERING01_WORKFLOW_ID
            )
            if row["depends_on"] != expected_risk_dependency:
                failures.append("goal_rec_tiering01_recommendation_score_tiering_gate must depend on the latest quant or risk-tiering repair gate")
        if workflow_id == GOAL10B4_WORKFLOW_ID:
            if status != "locked_future" or row["implemented_in_repo"] != "false":
                failures.append("goal10b4_recommendation_backtest_revalidation must remain locked_future and unimplemented")
            if row["depends_on"] != GOAL_REC_TIERING01_WORKFLOW_ID:
                failures.append("goal10b4_recommendation_backtest_revalidation must depend on GOAL-REC-TIERING-01")
        if workflow_id == POSITION_BAND_VALIDATION_WORKFLOW_ID:
            if status != "locked_future" or row["implemented_in_repo"] != "false":
                failures.append("goal_position_band_validation01_position_band_validation_gate must remain locked_future and unimplemented")
            if row["depends_on"] != GOAL10B4_WORKFLOW_ID:
                failures.append("goal_position_band_validation01_position_band_validation_gate must depend on GOAL-10B.4")
        if workflow_id == GOAL10D_WORKFLOW_ID:
            if status != "locked_future":
                failures.append("goal10d_backtest_failure_attribution_gate must remain locked_future")
            if row["implemented_in_repo"] != "false":
                failures.append("goal10d_backtest_failure_attribution_gate must not be marked implemented")
            if row["depends_on"] != GOAL10C_WORKFLOW_ID:
                failures.append("goal10d_backtest_failure_attribution_gate must depend on GOAL-10C")
        if workflow_id in DOWNSTREAM_LOCKED_IDS and status != "locked_future":
            failures.append(f"{workflow_id} must remain locked_future")
        if workflow_id == "dqn_rl_mainline" and status != "deleted_from_active_mainline":
            failures.append("dqn_rl_mainline must remain deleted_from_active_mainline")
        if row["implemented_in_repo"] == "true" and status not in {"implemented_active", "implemented_review_only", "implemented_design_only", "implemented_infrastructure_only", "implemented_research_only"}:
            failures.append(f"{workflow_id} is marked implemented but has future/deleted status")
    return failures


def _status_table_row(row: dict[str, str]) -> dict[str, object]:
    status = row["status"]
    if status == "implemented_active":
        edge_type = "solid"
        can_promote = False
        blocker = "already implemented active"
    elif status == "implemented_review_only":
        edge_type = "dotted_review_only"
        can_promote = False
        blocker = "already implemented review-only"
    elif status == "implemented_design_only":
        edge_type = "dotted_design_only"
        can_promote = False
        blocker = "already implemented design-only; calculation remains locked"
    elif status == "implemented_infrastructure_only":
        edge_type = "dotted_infrastructure_only"
        can_promote = False
        blocker = "already implemented infrastructure-only; downstream execution remains locked"
    elif status == "implemented_research_only":
        edge_type = "dotted_research_only"
        can_promote = False
        blocker = "already implemented research-only; downstream execution remains locked"
    elif row["workflow_id"] == GOAL07B_WORKFLOW_ID and status == "future_review_only":
        edge_type = "dotted_review_only_eligible"
        can_promote = False
        blocker = "eligible only for a future explicit review-only prototype; not implemented"
    elif row["workflow_id"] == GOAL08B_WORKFLOW_ID and status == "future_review_only":
        edge_type = "dotted_review_only_eligible"
        can_promote = False
        blocker = "eligible only for a future explicit non-actionable diagnostics prototype; not implemented"
    elif row["workflow_id"] == GOAL09_WORKFLOW_ID and status == "future_review_only":
        edge_type = "dotted_review_only_eligible"
        can_promote = False
        blocker = "eligible only for a future explicit non-actionable position-band diagnostics prototype; not implemented"
    elif status == "deleted_from_active_mainline":
        edge_type = "dotted_side_note"
        can_promote = False
        blocker = "deleted from active mainline; explicit optional research goal required"
    else:
        edge_type = "dotted"
        can_promote = False
        blocker = "requires readiness report PASS/PASS_WITH_WARNINGS plus validation, verification, workflow_status, docs, and PROJECT_STATE updates"
    if row["workflow_id"] == "goal06c_expanded_validation_ranking":
        next_goal = "GOAL-06C.5 engineering data foundation"
    elif row["workflow_id"] == "goal06c5_engineering_data_coverage_storage_panel_expansion":
        next_goal = "GOAL-06C.6 source-backed engineering pilot bundle gate"
    elif row["workflow_id"] == "goal06c6_source_backed_engineering_pilot_bundle":
        next_goal = "GOAL-06C.6A scoped failure taxonomy then GOAL-06C.7 provider ladder"
    elif row["workflow_id"] == "goal06c6a_scoped_finance_network_failure_taxonomy":
        next_goal = "GOAL-06C.7 provider ladder engineering data base expansion"
    elif row["workflow_id"] == "goal06c7_provider_ladder_browser_assisted_engineering_data_base_expansion":
        next_goal = "GOAL-06D review-only after provider-ladder engineering_pilot"
    elif row["workflow_id"] == "goal06d_model_comparison_calibration":
        next_goal = "Fix GOAL-06D warnings before GOAL-07A design-only preparation"
    elif row["workflow_id"] == "goal06d1_calibration_stability_warning_repair":
        next_goal = "GOAL-07A design-only preparation with warnings bounded"
    elif row["workflow_id"] == "goal07a_risk_overlay_design":
        next_goal = "GOAL-07B only after explicit future unlock; currently locked"
    elif row["workflow_id"] == "goal07a1_risk_overlay_design_review_unlock_readiness":
        next_goal = "GOAL-07B.0 explicit review-only unlock gate"
    elif row["workflow_id"] == "goal07b0_risk_overlay_review_only_unlock_gate":
        next_goal = "GOAL-07B future review-only calculation prototype may be requested separately"
    elif row["workflow_id"] == GOAL07B_WORKFLOW_ID:
        next_goal = "GOAL-08A design-only contract gate and GOAL-STORAGE-01 may be maintained before GOAL-08B.0 eligibility"
    elif row["workflow_id"] == "goal08a_recommendation_contract_design_gate":
        next_goal = "GOAL-STORAGE-01 hardening, then GOAL-08B.0 review-only unlock eligibility"
    elif row["workflow_id"] == GOAL_STORAGE01_WORKFLOW_ID:
        next_goal = "GOAL-08B.0 can mark eligibility only; storage hardening does not implement recommendations"
    elif row["workflow_id"] == GOAL08B0_WORKFLOW_ID:
        next_goal = "GOAL-08B future non-actionable diagnostics prototype may be requested separately"
    elif row["workflow_id"] == GOAL08B_WORKFLOW_ID:
        next_goal = "GOAL-09 position-band review-only unlock may be requested separately only after GOAL-08B diagnostics evidence"
    elif row["workflow_id"] == GOAL090_WORKFLOW_ID:
        next_goal = "GOAL-09 future non-actionable position-band diagnostics prototype may be requested separately"
    elif row["workflow_id"] == GOAL09_WORKFLOW_ID:
        next_goal = "Fix GOAL-09 review-only warnings before any future downstream unlock request; actual positions remain locked"
    elif row["workflow_id"] == GOAL091_WORKFLOW_ID:
        next_goal = "GOAL-V1-INTEGRITY-01 artifact-lineage integrity gate before any future dashboard design contract request"
    elif row["workflow_id"] == GOAL_V1_INTEGRITY01_WORKFLOW_ID:
        next_goal = "GOAL-10A is the current design-only successor; dashboard output remains locked"
    elif row["workflow_id"] == GOAL10A_WORKFLOW_ID:
        next_goal = "GOAL-10B review-only recommendation diagnostics backtest is the only implemented successor; production backtests remain locked"
    elif row["workflow_id"] == GOAL10B_WORKFLOW_ID:
        next_goal = "GOAL-10B.1 coverage and group-variation repair gate diagnoses current GOAL-10B warnings before any future GOAL-10C request"
    elif row["workflow_id"] == GOAL10B1_WORKFLOW_ID:
        next_goal = "GOAL-DATA-LABEL-01 and GOAL-V1-DIAGNOSTIC-COVERAGE-02 provide bounded label and diagnostic coverage before B2/C"
    elif row["workflow_id"] == GOAL_DATA_LABEL01_WORKFLOW_ID:
        next_goal = "GOAL-V1-DIAGNOSTIC-COVERAGE-02 diagnostic coverage is implemented; GOAL-10B.2 may be preserved when its evidence exists"
    elif row["workflow_id"] == GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID:
        next_goal = "GOAL-10B.2 recommendation revalidation is the review-only successor when explicitly implemented"
    elif row["workflow_id"] == GOAL10B2_WORKFLOW_ID:
        next_goal = "GOAL-10C cost/slippage sensitivity may proceed only as review-only diagnostics"
    elif row["workflow_id"] == GOAL10C_WORKFLOW_ID:
        next_goal = "GOAL-DATA-PROVIDER-02A may probe provider capability only; GOAL-10D remains locked"
    elif row["workflow_id"] == GOAL_DATA_PROVIDER02A_WORKFLOW_ID:
        next_goal = "GOAL-DATA-PROVIDER-02A.1 network opt-in smoke test may run only with explicit environment gates"
    elif row["workflow_id"] == GOAL_DATA_PROVIDER02A1_WORKFLOW_ID:
        next_goal = "GOAL-DATA-PROVIDER-02B source-backed panel build is implemented review-only when evidence exists"
    elif row["workflow_id"] == GOAL_DATA_PROVIDER02B_WORKFLOW_ID:
        next_goal = "GOAL-DATA-PANEL-02 evaluation panel remains locked until explicit panel promotion"
    elif row["workflow_id"] == GOAL_DATA_PANEL02_WORKFLOW_ID:
        next_goal = "GOAL-DATA-PANEL-02 remains locked; GOAL-V1-DIAGNOSTIC-COVERAGE-03 uses separate 02B source-backed evidence"
    elif row["workflow_id"] == GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID:
        next_goal = "GOAL-10B.3 DC03 recommendation revalidation is implemented review-only when valid evidence exists"
    elif row["workflow_id"] == GOAL10B3_WORKFLOW_ID:
        next_goal = "GOAL-RISK-TIERING-01 risk severity numeric score tiering is implemented review-only when valid evidence exists"
    elif row["workflow_id"] == GOAL_RISK_TIERING01_WORKFLOW_ID:
        next_goal = "Run or preserve GOAL-RISK-TIERING-01.1 downside-risk repair before GOAL-REC-TIERING-01"
    elif row["workflow_id"] == GOAL_RISK_TIERING011_WORKFLOW_ID:
        next_goal = "Run or preserve GOAL-QUANT-RESEARCH-01 factor research lab before GOAL-REC-TIERING-01"
    elif row["workflow_id"] == GOAL_QUANT_RESEARCH01_WORKFLOW_ID:
        next_goal = "Review score validity classifications before any explicit GOAL-REC-TIERING-01 request"
    elif row["workflow_id"] == GOAL_REC_TIERING01_WORKFLOW_ID:
        next_goal = "Remain locked until explicit GOAL-REC-TIERING-01 request after quant research evidence is accepted"
    elif row["workflow_id"] == GOAL10B4_WORKFLOW_ID:
        next_goal = "Remain locked until GOAL-REC-TIERING-01 passes and an explicit GOAL-10B.4 request is made"
    elif row["workflow_id"] == POSITION_BAND_VALIDATION_WORKFLOW_ID:
        next_goal = "Remain locked until GOAL-10B.4 passes and an explicit position-band validation request is made"
    elif row["workflow_id"] == GOAL10D_WORKFLOW_ID:
        next_goal = "Remain locked until an explicit GOAL-10D failure attribution gate is requested"
    elif row["workflow_id"] == "dashboard_daily_report":
        next_goal = "Remain locked until an explicit GOAL-DASHBOARD-00 design-only contract/layout gate is requested and passes"
    elif row["workflow_id"] == "v2_factor_research_upgrade":
        next_goal = "No action until V1 complete and explicit V2 goal is approved"
    else:
        next_goal = row["stage_or_goal"]
    return {
        "workflow_id": row["workflow_id"],
        "display_name": row["display_name"],
        "status": status,
        "diagram_edge_type": edge_type,
        "can_promote_now": can_promote,
        "promotion_blocker": blocker,
        "next_required_goal": next_goal,
    }


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _goal06c7_engineering_pilot_pass(readiness: str) -> bool:
    return (
        "GOAL-06C.7 Engineering Data Base Expansion Readiness: PASS" in readiness
        and "Panel tier: `engineering_pilot`" in readiness
        and "GOAL-06D allowed to proceed: true" in readiness
        and "GOAL-06D mode: review_only" in readiness
    )


def _goal06d_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-06D Model Comparison Calibration Readiness: PASS" in readiness
        or "GOAL-06D Model Comparison Calibration Readiness: PASS_WITH_WARNINGS" in readiness
    )


def _goal06d1_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-06D.1 Calibration Stability Warning Repair Readiness: PASS" in readiness
        or "GOAL-06D.1 Calibration Stability Warning Repair Readiness: PASS_WITH_WARNINGS" in readiness
    )


def _goal07a_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-07A Risk Overlay Design Readiness: PASS" in readiness
        or "GOAL-07A Risk Overlay Design Readiness: PASS_WITH_WARNINGS" in readiness
    )


def _goal07a1_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-07A.1 Risk Overlay Design Review: PASS" in readiness
        or "GOAL-07A.1 Risk Overlay Design Review: PASS_WITH_WARNINGS" in readiness
    )


def _goal07b0_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-07B.0 Risk Overlay Review-Only Unlock Gate: PASS" in readiness
        or "GOAL-07B.0 Risk Overlay Review-Only Unlock Gate: PASS_WITH_WARNINGS" in readiness
    )


def _goal07b_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-07B Risk Overlay Calculation Prototype: PASS" in readiness
        or "GOAL-07B Risk Overlay Calculation Prototype: PASS_WITH_WARNINGS" in readiness
    )


def _goal08a_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-08A Recommendation Contract Design Gate: PASS" in readiness
        or "GOAL-08A Recommendation Contract Design Gate: PASS_WITH_WARNINGS" in readiness
    )


def _goal_storage01_readiness_implemented(readiness: str) -> bool:
    return "GOAL-STORAGE-01 Local Research Lake Hardening Gate: PASS" in readiness


def _goal08b0_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-08B.0 Recommendation Review-Only Unlock Gate: PASS" in readiness
        or "GOAL-08B.0 Recommendation Review-Only Unlock Gate: PASS_WITH_WARNINGS" in readiness
    )


def _goal08b_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-08B Recommendation Diagnostics Prototype: PASS" in readiness
        or "GOAL-08B Recommendation Diagnostics Prototype: PASS_WITH_WARNINGS" in readiness
    )


def _goal090_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-09.0 Position-Band Review-Only Unlock Gate: PASS" in readiness
        or "GOAL-09.0 Position-Band Review-Only Unlock Gate: PASS_WITH_WARNINGS" in readiness
    )


def _goal09_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-09 Position-Band Diagnostics Prototype: PASS" in readiness
        or "GOAL-09 Position-Band Diagnostics Prototype: PASS_WITH_WARNINGS" in readiness
    )


def _goal091_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-09.1 Position-Band Warning Review and Dashboard Readiness Gate: PASS" in readiness
        or "GOAL-09.1 Position-Band Warning Review and Dashboard Readiness Gate: PASS_WITH_WARNINGS" in readiness
    )


def _goal_v1_integrity01_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-V1-INTEGRITY-01 Artifact Lineage and Structure Gate: PASS" in readiness
        or "GOAL-V1-INTEGRITY-01 Artifact Lineage and Structure Gate: PASS_WITH_WARNINGS" in readiness
    )


def _goal10a_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-10A Backtest Contract Design Gate: PASS" in readiness
        or "GOAL-10A Backtest Contract Design Gate: PASS_WITH_WARNINGS" in readiness
    )


def _goal10b_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-10B Recommendation Diagnostics Backtest Review-Only: PASS" in readiness
        or "GOAL-10B Recommendation Diagnostics Backtest Review-Only: PASS_WITH_WARNINGS" in readiness
    )


def _goal10b1_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-10B.1 Backtest Coverage and Group Variation Repair Gate: PASS" in readiness
        or "GOAL-10B.1 Backtest Coverage and Group Variation Repair Gate: PASS_WITH_WARNINGS" in readiness
    )


def _goal_data_label01_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-DATA-LABEL-01 Forward-Return Label Coverage Expansion: PASS" in readiness
        or "GOAL-DATA-LABEL-01 Forward-Return Label Coverage Expansion: PASS_WITH_WARNINGS" in readiness
    )


def _goal_v1_diagnostic_coverage02_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-V1-DIAGNOSTIC-COVERAGE-02 Multi-Symbol Diagnostics Expansion: PASS" in readiness
        or "GOAL-V1-DIAGNOSTIC-COVERAGE-02 Multi-Symbol Diagnostics Expansion: PASS_WITH_WARNINGS" in readiness
    )


def _goal10b2_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-10B.2 Recommendation Backtest Revalidation: PASS" in readiness
        or "GOAL-10B.2 Recommendation Backtest Revalidation: PASS_WITH_WARNINGS" in readiness
    )


def _goal10c_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-10C Cost / Slippage Sensitivity Gate: PASS" in readiness
        or "GOAL-10C Cost / Slippage Sensitivity Gate: PASS_WITH_WARNINGS" in readiness
    )


def _goal_data_provider02a_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-DATA-PROVIDER-02A Multi-Provider Capability Probe Gate: PASS" in readiness
        or "GOAL-DATA-PROVIDER-02A Multi-Provider Capability Probe Gate: PASS_WITH_WARNINGS" in readiness
    )


def _goal_data_provider02a1_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-DATA-PROVIDER-02A.1 Network Opt-In Provider Smoke Test Gate: PASS" in readiness
        or "GOAL-DATA-PROVIDER-02A.1 Network Opt-In Provider Smoke Test Gate: PASS_WITH_WARNINGS" in readiness
    )


def _goal_data_provider02b_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-DATA-PROVIDER-02B Source-Backed Evaluation Panel Build Gate: PASS" in readiness
        or "GOAL-DATA-PROVIDER-02B Source-Backed Evaluation Panel Build Gate: PASS_WITH_WARNINGS" in readiness
    )


def _goal_v1_diagnostic_coverage03_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-V1-DIAGNOSTIC-COVERAGE-03 Source-Backed Multi-Symbol Diagnostics Gate: PASS" in readiness
        or "GOAL-V1-DIAGNOSTIC-COVERAGE-03 Source-Backed Multi-Symbol Diagnostics Gate: PASS_WITH_WARNINGS" in readiness
    )


def _goal10b3_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-10B.3 DC03 Recommendation Revalidation Gate: PASS" in readiness
        or "GOAL-10B.3 DC03 Recommendation Revalidation Gate: PASS_WITH_WARNINGS" in readiness
    )


def _goal_risk_tiering01_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-RISK-TIERING-01 Risk Severity Numeric Score Tiering Gate: PASS" in readiness
        or "GOAL-RISK-TIERING-01 Risk Severity Numeric Score Tiering Gate: PASS_WITH_WARNINGS" in readiness
    )


def _goal_risk_tiering011_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-RISK-TIERING-01.1 Downside Risk Repair Gate: PASS" in readiness
        or "GOAL-RISK-TIERING-01.1 Downside Risk Repair Gate: PASS_WITH_WARNINGS" in readiness
    )


def _goal_quant_research01_readiness_implemented(readiness: str) -> bool:
    return (
        "GOAL-QUANT-RESEARCH-01 Factor Research Lab: PASS" in readiness
        or "GOAL-QUANT-RESEARCH-01 Factor Research Lab: PASS_WITH_WARNINGS" in readiness
    )


def _validate_goal10b2_goal10c_state_after_diagnostic_chain(
    failures: list[str],
    goal10b2: dict[str, str],
    goal10c: dict[str, str],
    goal10d: dict[str, str],
    goal10b2_evidence_ready: bool,
    goal10c_evidence_ready: bool,
    *,
    context: str,
) -> None:
    if goal10b2_evidence_ready:
        if goal10b2.get("status") != "implemented_review_only":
            failures.append(f"GOAL-10B.2 valid evidence must be preserved after {context}")
        if goal10b2.get("implemented_in_repo") != "true":
            failures.append(f"GOAL-10B.2 implemented flag must be preserved after {context}")
    else:
        if goal10b2.get("status") != "locked_future":
            failures.append(f"GOAL-10B.2 must remain locked_future after {context} until its evidence exists")
        if goal10b2.get("implemented_in_repo") != "false":
            failures.append(f"GOAL-10B.2 must not be implemented after {context} without evidence")
    if goal10b2.get("depends_on") != GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID:
        failures.append(f"GOAL-10B.2 dependency is invalid after {context}")

    if goal10c_evidence_ready:
        if goal10c.get("status") != "implemented_review_only":
            failures.append(f"GOAL-10C valid evidence must be preserved after {context}")
        if goal10c.get("implemented_in_repo") != "true":
            failures.append(f"GOAL-10C implemented flag must be preserved after {context}")
    else:
        if goal10c.get("status") != "locked_future":
            failures.append(f"GOAL-10C must remain locked_future after {context} until its evidence exists")
        if goal10c.get("implemented_in_repo") != "false":
            failures.append(f"GOAL-10C must not be implemented after {context} without evidence")
    if goal10c.get("depends_on") != GOAL10B2_WORKFLOW_ID:
        failures.append(f"GOAL-10C dependency is invalid after {context}")

    if goal10d.get("status") != "locked_future":
        failures.append(f"GOAL-10D must remain locked_future after {context}")
    if goal10d.get("implemented_in_repo") != "false":
        failures.append(f"GOAL-10D must not be implemented after {context}")
    if goal10d.get("depends_on") != GOAL10C_WORKFLOW_ID:
        failures.append(f"GOAL-10D dependency is invalid after {context}")


def _validate_locked_execution_downstream(failures: list[str], by_id: dict[str, dict[str, str]], *, context: str) -> None:
    for workflow_id in [
        "dashboard_daily_report",
        "signal_backtest",
        "portfolio_backtest",
        "cost_slippage_sensitivity",
        "paper_trading_journal",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
    ]:
        row = by_id.get(workflow_id, {})
        if row.get("status") != "locked_future":
            failures.append(f"{workflow_id} must remain locked_future after {context}")
        if row.get("implemented_in_repo") != "false":
            failures.append(f"{workflow_id} must not be implemented after {context}")


def _unexpected_goal10b_backtest_outputs(root: Path) -> list[str]:
    path = root / "outputs/backtest"
    if not path.exists():
        return []
    allowed = {
        "outputs/backtest/goal10b_recommendation_backtest_input_snapshot.csv",
        "outputs/backtest/goal10b_recommendation_group_metrics.csv",
        "outputs/backtest/goal10b_risk_severity_group_metrics.csv",
        "outputs/backtest/goal10b_warning_group_metrics.csv",
        "outputs/backtest/goal10b_ic_rank_ic_summary.csv",
        "outputs/backtest/goal10b1_coverage_repair_diagnostic_summary.csv",
        "outputs/backtest/goal10b1_recommendation_distribution_audit.csv",
        "outputs/backtest/goal10b1_label_source_coverage_audit.csv",
        "outputs/backtest/goal10b1_repaired_backtest_input_snapshot.csv",
        "outputs/backtest/goal10b1_repaired_recommendation_group_metrics.csv",
        "outputs/backtest/goal10b2_revalidation_input_snapshot.csv",
        "outputs/backtest/goal10b2_recommendation_status_metrics.csv",
        "outputs/backtest/goal10b2_symbol_metrics.csv",
        "outputs/backtest/goal10b2_horizon_coverage.csv",
        "outputs/backtest/goal10b3_dc03_revalidation_input_snapshot.csv",
        "outputs/backtest/goal10b3_recommendation_group_metrics.csv",
        "outputs/backtest/goal10b3_risk_severity_group_metrics.csv",
        "outputs/backtest/goal10b3_symbol_metrics.csv",
        "outputs/backtest/goal10b3_horizon_coverage.csv",
        "outputs/backtest/goal10b3_group_imbalance_diagnostics.csv",
        "outputs/backtest/goal_risk_tiering01_risk_tier_forward_return_metrics.csv",
        "outputs/backtest/goal_risk_tiering011_downside_risk_forward_return_metrics.csv",
        "outputs/backtest/goal10c_position_band_input_snapshot.csv",
        "outputs/backtest/goal10c_cost_slippage_sensitivity.csv",
        "outputs/backtest/goal10c_position_band_group_metrics.csv",
    }
    return [
        str(item.relative_to(root))
        for item in sorted(path.glob("*"))
        if str(item.relative_to(root)) not in allowed
    ]


def _first_mermaid_block(text: str) -> str:
    marker = "```mermaid"
    start = text.find(marker)
    if start == -1:
        return ""
    start += len(marker)
    end = text.find("```", start)
    if end == -1:
        return text[start:]
    return text[start:end]

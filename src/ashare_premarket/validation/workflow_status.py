from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.io import read_csv, write_csv, write_text

ALLOWED_STATUSES = {
    "implemented_active",
    "implemented_review_only",
    "implemented_design_only",
    "implemented_infrastructure_only",
    "future_review_only",
    "future_design_only",
    "locked_future",
    "planned_locked",
    "not_started",
    "deleted_from_active_mainline",
}

DOWNSTREAM_LOCKED_IDS = {
    "position_band_recommendation",
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
    if "Position-Band Recommendation" not in full_roadmap or "locked_future" not in full_roadmap:
        failures.append("full roadmap does not label position-band recommendation as locked_future")
    if "DQN/RL Optional Research Benchmark" not in full_roadmap or "deleted_from_active_mainline" not in full_roadmap:
        failures.append("full roadmap does not label DQN/RL as deleted_from_active_mainline")

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
    goal08b0_evidence_ready = bool(goal08b0) and goal08b0_status == "implemented_review_only" and _goal08b0_readiness_implemented(goal08b0_report) and "Status: `PASS`" in goal08b0_audit
    goal08b_evidence_ready = bool(goal08b) and goal08b_status == "implemented_review_only" and _goal08b_readiness_implemented(goal08b_report) and "Status: `PASS`" in goal08b_audit
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
                "GOAL-06D may be `implemented_review_only` only with PASS/PASS_WITH_WARNINGS readiness evidence; GOAL-07A may be `implemented_design_only` only with design-only readiness evidence; GOAL-07B may be `future_review_only` only after GOAL-07B.0 evidence and `implemented_review_only` only with a PASS/PASS_WITH_WARNINGS diagnostic-only calculation report; GOAL-08A may be `implemented_design_only` only with names-only contract evidence and zero recommendation rows; GOAL-STORAGE-01 may be `implemented_infrastructure_only` only with local research lake hardening evidence; GOAL-08B may be `future_review_only` eligible only after GOAL-08B.0 evidence and `implemented_review_only` only with a PASS/PASS_WITH_WARNINGS non-actionable diagnostic report.",
                "GOAL-06C and later are not represented as `implemented_active`.",
                "GOAL-07B risk overlay diagnostics and GOAL-08B recommendation diagnostics are review-only when implemented; position, dashboard, paper/live trading, production, backtest, factor-mining, broker, local-lake, and DQN/RL remain locked or deleted from active mainline.",
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
        if workflow_id in DOWNSTREAM_LOCKED_IDS and status != "locked_future":
            failures.append(f"{workflow_id} must remain locked_future")
        if workflow_id == "dqn_rl_mainline" and status != "deleted_from_active_mainline":
            failures.append("dqn_rl_mainline must remain deleted_from_active_mainline")
        if row["implemented_in_repo"] == "true" and status not in {"implemented_active", "implemented_review_only", "implemented_design_only", "implemented_infrastructure_only"}:
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
    elif row["workflow_id"] == GOAL07B_WORKFLOW_ID and status == "future_review_only":
        edge_type = "dotted_review_only_eligible"
        can_promote = False
        blocker = "eligible only for a future explicit review-only prototype; not implemented"
    elif row["workflow_id"] == GOAL08B_WORKFLOW_ID and status == "future_review_only":
        edge_type = "dotted_review_only_eligible"
        can_promote = False
        blocker = "eligible only for a future explicit non-actionable diagnostics prototype; not implemented"
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

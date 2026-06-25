from __future__ import annotations

import subprocess
from pathlib import Path

from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.review_diagnostics.goal09 import (
    DIAGNOSTIC_PATH as GOAL09_DIAGNOSTIC_PATH,
    MANIFEST_PATH as GOAL09_MANIFEST_PATH,
    goal09_valid_position_band_diagnostics_evidence,
)
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-09.1"
GOAL_NAME = "GOAL-09.1-POSITION-BAND-WARNING-REVIEW-AND-DASHBOARD-READINESS-GATE"
MODE = "review_readiness_only"
WORKFLOW_ID = "goal091_position_band_warning_dashboard_readiness_gate"
GOAL09_WORKFLOW_ID = "position_band_recommendation"
DASHBOARD_WORKFLOW_ID = "dashboard_daily_report"
DASHBOARD00_ALLOWED_NEXT = "request_explicit_goal_dashboard00_contract_design_gate"
DASHBOARD_LOCKED_NEXT = "remain_locked_until_explicit_goal_dashboard00_contract_design_gate"
PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

CONFIG_PATH = "configs/dashboard/goal091_dashboard_readiness_warning_policy.yaml"
DOC_PATH = "docs/dashboard/GOAL091_POSITION_BAND_WARNING_REVIEW_AND_DASHBOARD_READINESS.md"
REPORT_PATH = "outputs/audits/goal091_dashboard_readiness_report.md"
MANIFEST_PATH = "outputs/audits/goal091_dashboard_readiness_manifest.json"
AUDIT_PATH = "outputs/audits/goal091_dashboard_readiness_audit.md"

WORKFLOW_PRODUCES_ARTIFACTS = ";".join([CONFIG_PATH, DOC_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH])
WORKFLOW_PRIMARY_DOCS = f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md"
WORKFLOW_PRIMARY_SCRIPTS = "scripts/run_goal091_position_band_warning_dashboard_readiness_gate.py;scripts/audit_goal091_position_band_warning_dashboard_readiness_gate.py"
WORKFLOW_PRIMARY_OUTPUTS = f"{REPORT_PATH};{MANIFEST_PATH};{AUDIT_PATH}"
WORKFLOW_NOTES = "Review/readiness-only warning classification and future dashboard contract eligibility gate; no dashboard files, visual reports, recommendation rows, position rows, trading, production, backtest, factor-mining, broker, local-lake, or DQN/RL output."

GOAL07B_REPORT_PATH = "outputs/audits/goal07b_risk_overlay_calculation_report.md"
GOAL07B_AUDIT_PATH = "outputs/audits/goal07b_risk_overlay_calculation_audit.md"
GOAL07B_MANIFEST_PATH = "outputs/audits/goal07b_risk_overlay_calculation_manifest.json"
GOAL07B_ROWS_PATH = "outputs/risk_overlay/goal07b_review_only_risk_overlay.csv"
GOAL08A_REPORT_PATH = "outputs/audits/goal08a_recommendation_contract_design_report.md"
GOAL08A_AUDIT_PATH = "outputs/audits/goal08a_recommendation_contract_design_audit.md"
GOAL08A_MANIFEST_PATH = "outputs/audits/goal08a_recommendation_contract_design_manifest.json"
STORAGE01_REPORT_PATH = "outputs/audits/goal_storage01_local_research_lake_hardening_report.md"
STORAGE01_AUDIT_PATH = "outputs/audits/goal_storage01_local_research_lake_hardening_audit.md"
STORAGE01_MANIFEST_PATH = "outputs/audits/goal_storage01_local_research_lake_hardening_manifest.json"
GOAL08B0_REPORT_PATH = "outputs/audits/goal08b0_recommendation_review_only_unlock_report.md"
GOAL08B0_AUDIT_PATH = "outputs/audits/goal08b0_recommendation_review_only_unlock_audit.md"
GOAL08B0_MANIFEST_PATH = "outputs/audits/goal08b0_recommendation_review_only_unlock_manifest.json"
GOAL08B_REPORT_PATH = "outputs/audits/goal08b_recommendation_diagnostics_report.md"
GOAL08B_AUDIT_PATH = "outputs/audits/goal08b_recommendation_diagnostics_audit.md"
GOAL08B_MANIFEST_PATH = "outputs/audits/goal08b_recommendation_diagnostics_manifest.json"
GOAL08B_ROWS_PATH = "outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv"
GOAL090_REPORT_PATH = "outputs/audits/goal090_position_band_review_only_unlock_report.md"
GOAL090_AUDIT_PATH = "outputs/audits/goal090_position_band_review_only_unlock_audit.md"
GOAL090_MANIFEST_PATH = "outputs/audits/goal090_position_band_review_only_unlock_manifest.json"
GOAL09_REPORT_PATH = "outputs/audits/goal09_position_band_diagnostics_report.md"
GOAL09_AUDIT_PATH = "outputs/audits/goal09_position_band_diagnostics_audit.md"

WARNING_CLASSIFICATION = {
    "calibration_not_reliable_for_thresholding": "dashboard_blocking_banner",
    "target_horizon_calibration_warning": "dashboard_blocking_banner",
    "weak_target_horizon_rank_signal": "dashboard_blocking_banner",
    "selected_score_variant_weak_rank_signal": "dashboard_blocking_banner",
    "single_provider_mode_akshare_direct": "provider_concentration_banner",
    "provider_source_concentration_disclosed": "provider_concentration_banner",
    "feature_sign_instability_bounded": "row_level_and_summary_warning",
}

DASHBOARD_FORBIDDEN_FIELD_NAMES = {
    "buy",
    "sell",
    "hold",
    "buy_sell_hold",
    "target_price",
    "expected_return_action",
    "expected_return_for_action",
    "position_size",
    "position_weight",
    "portfolio_weight",
    "target_weight",
    "order_quantity",
    "trade_action",
    "execution_action",
    "capital_allocation",
}

DOWNSTREAM_LOCKED_IDS = [
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
]

FORBIDDEN_OUTPUT_DIRS = [
    "outputs/dashboard",
    "outputs/dashboards",
    "outputs/visual_reports",
    "outputs/frontend",
    "outputs/recommendations",
    "outputs/positions",
    "outputs/position_sizing",
    "outputs/position_weights",
    "outputs/orders",
    "outputs/trading",
    "outputs/paper_trading",
    "outputs/live_trading",
    "outputs/backtests",
    "outputs/factors",
    "outputs/dqn",
    "outputs/rl",
]

LOCAL_LAKE_PATHS = [
    "data/raw",
    "data/bundles",
    "data/lake",
    "data/metadata",
    "data/exports",
    "local_data",
    "local_data_lake",
]

FORBIDDEN_TRACKED_SUFFIXES = {
    ".arrow",
    ".csv.gz",
    ".db",
    ".duckdb",
    ".feather",
    ".h5",
    ".html",
    ".ipynb",
    ".joblib",
    ".log",
    ".npy",
    ".npz",
    ".onnx",
    ".parquet",
    ".payload",
    ".pkl",
    ".pt",
    ".pth",
    ".raw",
    ".sqlite",
    ".sqlite3",
    ".zip",
}

FALSE_BOUNDARY_KEYS = [
    "dashboard_outputs_generated",
    "dashboard_files_generated",
    "html_generated",
    "streamlit_generated",
    "frontend_code_generated",
    "visual_reports_generated",
    "new_recommendation_rows_generated",
    "new_position_rows_generated",
    "actual_position_sizing_generated",
    "portfolio_construction_generated",
    "portfolio_weights_generated",
    "target_weights_generated",
    "order_quantities_generated",
    "capital_allocation_amounts_generated",
    "buy_sell_hold_outputs_generated",
    "target_prices_generated",
    "expected_returns_for_action_generated",
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
    "downstream_execution_unlocked_by_this_goal",
]


def run_goal091_position_band_warning_dashboard_readiness_gate(root: Path) -> bool:
    bundle = load_goal091_dashboard_readiness_bundle(root)
    result = evaluate_goal091_dashboard_readiness(bundle)
    _write_policy(root, result)
    _write_outputs(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal091_position_band_warning_dashboard_readiness_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal091_position_band_warning_dashboard_readiness_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    policy = _read_json(root / CONFIG_PATH)
    workflow = _workflow_rows(root)
    failures: list[str] = []

    if not _report_pass_or_warn(report, "GOAL-09.1 Position-Band Warning Review and Dashboard Readiness Gate:"):
        failures.append("goal091_report_not_pass_or_warn")
    if manifest.get("goal") != GOAL_NAME:
        failures.append("manifest_goal_invalid")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_invalid")
    if manifest.get("goal09_status_confirmed") is not True:
        failures.append("manifest_goal09_status_not_confirmed")
    if manifest.get("goal09_non_actionable_confirmed") is not True:
        failures.append("manifest_goal09_non_actionable_not_confirmed")
    if manifest.get("goal09_output_grain") != "trade_date + symbol":
        failures.append("manifest_goal09_grain_invalid")
    if manifest.get("position_actionability_status_values") != ["never_actionable"]:
        failures.append("manifest_position_actionability_values_invalid")
    if manifest.get("future_dashboard_contract_design_gate_may_be_requested") is not True:
        failures.append("manifest_dashboard00_request_not_allowed")
    if manifest.get("dashboard_daily_report_status_after_goal091") != "locked_future":
        failures.append("manifest_dashboard_not_locked_future")
    if manifest.get("dashboard_implemented_by_this_goal") is not False:
        failures.append("manifest_dashboard_implemented_by_goal091_not_false")
    if manifest.get("dashboard_design_only_eligibility_only") is not True:
        failures.append("manifest_dashboard_design_only_eligibility_not_true")
    if manifest.get("warning_classification") != WARNING_CLASSIFICATION:
        failures.append("manifest_warning_classification_invalid")
    if sorted(manifest.get("warning_codes_reviewed", [])) != sorted(WARNING_CLASSIFICATION):
        failures.append("manifest_warning_codes_reviewed_invalid")
    if set(manifest.get("warning_codes_preventing_action_oriented_display", [])) != set(WARNING_CLASSIFICATION):
        failures.append("manifest_action_oriented_block_codes_invalid")
    if set(manifest.get("row_level_warning_codes_required", [])) != set(WARNING_CLASSIFICATION):
        failures.append("manifest_row_level_codes_invalid")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"manifest_{key}_not_false")
    for key in [
        "future_dashboard_review_only_required",
        "future_dashboard_never_actionable_required",
        "future_dashboard_non_actionable_disclaimers_required",
        "future_dashboard_may_use_only_audited_goal07b_goal08b_goal09_diagnostics",
        "future_dashboard_top_n_candidate_display_blocked",
        "future_dashboard_actionable_language_blocked",
        "future_dashboard_forbidden_fields_blocked",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")
    if policy.get("warning_classification") != WARNING_CLASSIFICATION:
        failures.append("policy_warning_classification_invalid")
    if policy.get("future_dashboard_forbidden_fields") != sorted(DASHBOARD_FORBIDDEN_FIELD_NAMES):
        failures.append("policy_forbidden_fields_invalid")

    gate_row = workflow.get(WORKFLOW_ID, {})
    if gate_row.get("status") != "implemented_review_only":
        failures.append("goal091_workflow_not_implemented_review_only")
    if gate_row.get("implemented_in_repo") != "true":
        failures.append("goal091_workflow_not_marked_implemented")
    if gate_row.get("allowed_next_action") != DASHBOARD00_ALLOWED_NEXT:
        failures.append("goal091_allowed_next_invalid")
    dashboard = workflow.get(DASHBOARD_WORKFLOW_ID, {})
    if dashboard.get("status") != "locked_future":
        failures.append("dashboard_workflow_not_locked_future")
    if dashboard.get("implemented_in_repo") != "false":
        failures.append("dashboard_workflow_marked_implemented")
    for workflow_id in DOWNSTREAM_LOCKED_IDS:
        row = workflow.get(workflow_id, {})
        if row.get("status") != "locked_future":
            failures.append(f"{workflow_id}_not_locked_future")
        if row.get("implemented_in_repo") != "false":
            failures.append(f"{workflow_id}_marked_implemented")
    if workflow.get("dqn_rl_mainline", {}).get("status") != "deleted_from_active_mainline":
        failures.append("dqn_rl_not_deleted_from_active_mainline")
    if workflow.get("v2_factor_research_upgrade", {}).get("status") != "planned_locked":
        failures.append("v2_factor_not_planned_locked")

    failures.extend(f"forbidden_output_dir_present:{path}" for path in _forbidden_output_dirs_present(root))
    failures.extend(f"local_lake_path_present:{path}" for path in _local_lake_paths_present(root))
    failures.extend(f"forbidden_tracked_artifact:{path}" for path in _tracked_forbidden_files(root))

    status = PASS if not failures else BLOCKED
    write_text(
        root / AUDIT_PATH,
        "\n".join(
            [
                "# GOAL-09.1 Dashboard Readiness Audit",
                "",
                f"Status: `{status}`",
                "",
                f"GOAL-09.1 workflow status: `{gate_row.get('status', 'missing')}`",
                f"Dashboard workflow status: `{dashboard.get('status', 'missing')}`",
                "GOAL-DASHBOARD-00 may be explicitly requested next as a future design-only contract/layout gate: `true`",
                "Dashboard outputs generated: `false`",
                "New recommendation or position rows generated: `false`",
                "Actual position sizing, portfolio weights, target weights, order quantities, buy/sell/hold actions, target prices, trading, production, backtest, factor-mining, broker, local-lake, and DQN/RL outputs generated: `false`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == PASS


def load_goal091_dashboard_readiness_bundle(root: Path) -> dict[str, object]:
    return {
        "goal07b_report": _read(root / GOAL07B_REPORT_PATH),
        "goal07b_audit": _read(root / GOAL07B_AUDIT_PATH),
        "goal07b_manifest": _read_json(root / GOAL07B_MANIFEST_PATH),
        "goal07b_rows": _read_csv(root / GOAL07B_ROWS_PATH),
        "goal08a_report": _read(root / GOAL08A_REPORT_PATH),
        "goal08a_audit": _read(root / GOAL08A_AUDIT_PATH),
        "goal08a_manifest": _read_json(root / GOAL08A_MANIFEST_PATH),
        "storage01_report": _read(root / STORAGE01_REPORT_PATH),
        "storage01_audit": _read(root / STORAGE01_AUDIT_PATH),
        "storage01_manifest": _read_json(root / STORAGE01_MANIFEST_PATH),
        "goal08b0_report": _read(root / GOAL08B0_REPORT_PATH),
        "goal08b0_audit": _read(root / GOAL08B0_AUDIT_PATH),
        "goal08b0_manifest": _read_json(root / GOAL08B0_MANIFEST_PATH),
        "goal08b_report": _read(root / GOAL08B_REPORT_PATH),
        "goal08b_audit": _read(root / GOAL08B_AUDIT_PATH),
        "goal08b_manifest": _read_json(root / GOAL08B_MANIFEST_PATH),
        "goal08b_rows": _read_csv(root / GOAL08B_ROWS_PATH),
        "goal090_report": _read(root / GOAL090_REPORT_PATH),
        "goal090_audit": _read(root / GOAL090_AUDIT_PATH),
        "goal090_manifest": _read_json(root / GOAL090_MANIFEST_PATH),
        "goal09_report": _read(root / GOAL09_REPORT_PATH),
        "goal09_audit": _read(root / GOAL09_AUDIT_PATH),
        "goal09_manifest": _read_json(root / GOAL09_MANIFEST_PATH),
        "goal09_rows": _read_csv(root / GOAL09_DIAGNOSTIC_PATH),
        "goal09_valid_evidence": goal09_valid_position_band_diagnostics_evidence(root),
        "workflow_rows": _read_csv(root / "configs/project/workflow_status.csv"),
        "forbidden_output_dirs": _forbidden_output_dirs_present(root),
        "local_lake_paths": _local_lake_paths_present(root),
        "tracked_forbidden_files": _tracked_forbidden_files(root),
    }


def evaluate_goal091_dashboard_readiness(bundle: dict[str, object]) -> dict[str, object]:
    failures = _validate_input_bundle(bundle)
    goal09_rows = [dict(row) for row in bundle.get("goal09_rows", []) if isinstance(row, dict)]
    warning_codes = _goal09_warning_codes(goal09_rows, bundle.get("goal09_manifest", {}))
    unknown_warnings = sorted(set(warning_codes) - set(WARNING_CLASSIFICATION))
    if unknown_warnings:
        failures.extend(f"unclassified_goal09_warning:{code}" for code in unknown_warnings)
    classifications = _classification_rows(warning_codes)
    status = BLOCKED if failures else PASS_WITH_WARNINGS if warning_codes else PASS
    manifest = _manifest(status, goal09_rows, warning_codes, classifications, sorted(set(failures)))
    return {
        "status": status,
        "failures": sorted(set(failures)),
        "warnings": warning_codes,
        "classifications": classifications,
        "manifest": manifest,
    }


def goal091_valid_dashboard_readiness_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        _report_pass_or_warn(report, "GOAL-09.1 Position-Band Warning Review and Dashboard Readiness Gate:")
        and "Status: `PASS`" in audit
        and manifest.get("goal") == GOAL_NAME
        and manifest.get("mode") == MODE
        and manifest.get("future_dashboard_contract_design_gate_may_be_requested") is True
        and manifest.get("dashboard_daily_report_status_after_goal091") == "locked_future"
        and manifest.get("dashboard_implemented_by_this_goal") is False
        and manifest.get("dashboard_outputs_generated") is False
        and manifest.get("new_recommendation_rows_generated") is False
        and manifest.get("new_position_rows_generated") is False
        and manifest.get("future_dashboard_top_n_candidate_display_blocked") is True
        and manifest.get("warning_classification") == WARNING_CLASSIFICATION
    )


def goal091_implemented_workflow_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-09.1 Position-Band Warning Review and Dashboard Readiness Gate",
        "stage_or_goal": "GOAL-09.1",
        "status": "implemented_review_only",
        "current_repo_role": "review_only_dashboard_readiness_governance_gate",
        "implemented_in_repo": "true",
        "allowed_next_action": DASHBOARD00_ALLOWED_NEXT,
        "depends_on": GOAL09_WORKFLOW_ID,
        "produces_artifacts": WORKFLOW_PRODUCES_ARTIFACTS,
        "primary_docs": WORKFLOW_PRIMARY_DOCS,
        "primary_scripts": WORKFLOW_PRIMARY_SCRIPTS,
        "primary_outputs": WORKFLOW_PRIMARY_OUTPUTS,
        "promotion_rule": "implemented_review_only_after_goal091_dashboard_readiness_pass_with_warnings",
        "notes": WORKFLOW_NOTES,
    }


def _validate_input_bundle(bundle: dict[str, object]) -> list[str]:
    failures: list[str] = []
    workflow = {row.get("workflow_id", ""): row for row in bundle.get("workflow_rows", []) if isinstance(row, dict)}
    goal09_rows = [dict(row) for row in bundle.get("goal09_rows", []) if isinstance(row, dict)]
    goal09_manifest = bundle.get("goal09_manifest", {})

    if not _report_pass_or_warn(str(bundle.get("goal07b_report", "")), "GOAL-07B Risk Overlay Calculation Prototype:"):
        failures.append("goal07b_report_not_pass_or_warn")
    if "Status: `PASS`" not in str(bundle.get("goal07b_audit", "")):
        failures.append("goal07b_audit_not_pass")
    if bundle.get("goal07b_manifest", {}).get("mode") != "review_only":
        failures.append("goal07b_manifest_not_review_only")
    if bundle.get("goal07b_manifest", {}).get("output_grain") != "trade_date + symbol":
        failures.append("goal07b_manifest_grain_invalid")

    if not _report_pass_or_warn(str(bundle.get("goal08a_report", "")), "GOAL-08A Recommendation Contract Design Gate:"):
        failures.append("goal08a_report_not_pass_or_warn")
    if "Status: `PASS`" not in str(bundle.get("goal08a_audit", "")):
        failures.append("goal08a_audit_not_pass")
    if bundle.get("goal08a_manifest", {}).get("mode") != "design_only":
        failures.append("goal08a_manifest_not_design_only")

    if "GOAL-STORAGE-01 Local Research Lake Hardening Gate: PASS" not in str(bundle.get("storage01_report", "")):
        failures.append("storage01_report_not_pass")
    if "Status: `PASS`" not in str(bundle.get("storage01_audit", "")):
        failures.append("storage01_audit_not_pass")
    if bundle.get("storage01_manifest", {}).get("mode") != "infrastructure_only":
        failures.append("storage01_manifest_not_infrastructure_only")
    if bundle.get("storage01_manifest", {}).get("local_data_files_created") is not False:
        failures.append("storage01_local_data_files_created_not_false")

    if not _report_pass_or_warn(str(bundle.get("goal08b0_report", "")), "GOAL-08B.0 Recommendation Review-Only Unlock Gate:"):
        failures.append("goal08b0_report_not_pass_or_warn")
    if "Status: `PASS`" not in str(bundle.get("goal08b0_audit", "")):
        failures.append("goal08b0_audit_not_pass")
    if bundle.get("goal08b0_manifest", {}).get("mode") != "review_only_unlock_gate":
        failures.append("goal08b0_manifest_mode_invalid")

    if not _report_pass_or_warn(str(bundle.get("goal08b_report", "")), "GOAL-08B Recommendation Diagnostics Prototype:"):
        failures.append("goal08b_report_not_pass_or_warn")
    if "Status: `PASS`" not in str(bundle.get("goal08b_audit", "")):
        failures.append("goal08b_audit_not_pass")
    if bundle.get("goal08b_manifest", {}).get("mode") != "review_only":
        failures.append("goal08b_manifest_not_review_only")
    if bundle.get("goal08b_manifest", {}).get("actionability_status_values") != ["never_actionable"]:
        failures.append("goal08b_actionability_values_invalid")

    if not _report_pass_or_warn(str(bundle.get("goal090_report", "")), "GOAL-09.0 Position-Band Review-Only Unlock Gate:"):
        failures.append("goal090_report_not_pass_or_warn")
    if "Status: `PASS`" not in str(bundle.get("goal090_audit", "")):
        failures.append("goal090_audit_not_pass")
    if bundle.get("goal090_manifest", {}).get("mode") != "review_only_unlock_gate":
        failures.append("goal090_manifest_mode_invalid")

    if bundle.get("goal09_valid_evidence") is not True:
        failures.append("goal09_valid_evidence_missing")
    if not _report_pass_or_warn(str(bundle.get("goal09_report", "")), "GOAL-09 Position-Band Diagnostics Prototype:"):
        failures.append("goal09_report_not_pass_or_warn")
    if "Status: `PASS`" not in str(bundle.get("goal09_audit", "")):
        failures.append("goal09_audit_not_pass")
    if goal09_manifest.get("mode") != "review_only":
        failures.append("goal09_manifest_not_review_only")
    if goal09_manifest.get("output_grain") != "trade_date + symbol":
        failures.append("goal09_manifest_grain_invalid")
    if goal09_manifest.get("position_actionability_status_values") != ["never_actionable"]:
        failures.append("goal09_position_actionability_values_invalid")
    if goal09_manifest.get("position_band_diagnostic_row_count") != len(goal09_rows):
        failures.append("goal09_manifest_row_count_mismatch")
    for key in [
        "position_rows_generated",
        "actual_position_sizing_generated",
        "portfolio_weights_generated",
        "target_weights_generated",
        "order_quantities_generated",
        "buy_sell_hold_outputs_generated",
        "target_prices_generated",
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
        if goal09_manifest.get(key) is not False:
            failures.append(f"goal09_manifest_{key}_not_false")
    if not goal09_rows:
        failures.append("goal09_rows_missing")
    else:
        grain = [(row.get("trade_date", ""), row.get("symbol", "")) for row in goal09_rows]
        if len(grain) != len(set(grain)):
            failures.append("goal09_rows_not_unique_trade_date_symbol")
        fields = set(goal09_rows[0].keys())
        forbidden_fields = fields & DASHBOARD_FORBIDDEN_FIELD_NAMES
        if forbidden_fields:
            failures.append("goal09_rows_forbidden_action_fields:" + ";".join(sorted(forbidden_fields)))
        for index, row in enumerate(goal09_rows):
            if row.get("diagnostic_mode") != "review_only":
                failures.append(f"goal09_row_{index}_not_review_only")
            if row.get("position_actionability_status") != "never_actionable":
                failures.append(f"goal09_row_{index}_position_actionability_not_never_actionable")
            if row.get("position_actionability_blocked") != "true":
                failures.append(f"goal09_row_{index}_position_actionability_not_blocked")
            if not row.get("non_actionable_disclaimer"):
                failures.append(f"goal09_row_{index}_non_actionable_disclaimer_missing")

    goal09 = workflow.get(GOAL09_WORKFLOW_ID, {})
    if goal09.get("status") != "implemented_review_only" or goal09.get("implemented_in_repo") != "true":
        failures.append("goal09_workflow_not_implemented_review_only")
    dashboard = workflow.get(DASHBOARD_WORKFLOW_ID, {})
    if dashboard.get("status") != "locked_future":
        failures.append("dashboard_workflow_not_locked_future")
    if dashboard.get("implemented_in_repo") != "false":
        failures.append("dashboard_workflow_marked_implemented")
    for workflow_id in DOWNSTREAM_LOCKED_IDS:
        row = workflow.get(workflow_id, {})
        if row.get("status") != "locked_future":
            failures.append(f"{workflow_id}_not_locked_future")
        if row.get("implemented_in_repo") != "false":
            failures.append(f"{workflow_id}_marked_implemented")
    if workflow.get("dqn_rl_mainline", {}).get("status") != "deleted_from_active_mainline":
        failures.append("dqn_rl_not_deleted_from_active_mainline")
    if workflow.get("v2_factor_research_upgrade", {}).get("status") != "planned_locked":
        failures.append("v2_factor_not_planned_locked")

    if bundle.get("forbidden_output_dirs"):
        failures.append("forbidden_output_dirs_present:" + ";".join(str(path) for path in bundle["forbidden_output_dirs"]))
    if bundle.get("local_lake_paths"):
        failures.append("local_lake_paths_present:" + ";".join(str(path) for path in bundle["local_lake_paths"]))
    if bundle.get("tracked_forbidden_files"):
        failures.append("tracked_forbidden_artifacts_present:" + ";".join(str(path) for path in bundle["tracked_forbidden_files"]))
    return failures


def _goal09_warning_codes(rows: list[dict[str, str]], manifest: dict[str, object]) -> list[str]:
    codes = set()
    for value in manifest.get("remaining_warnings", []) or []:
        if isinstance(value, str) and value != "none":
            codes.add(value)
    for row in rows:
        codes.update(_split_codes(row.get("propagated_warning_codes", "")))
        codes.update(_split_codes(row.get("risk_warning_codes", "")))
    return sorted(code for code in codes if code and code != "none")


def _classification_rows(warning_codes: list[str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for code in sorted(warning_codes):
        group = WARNING_CLASSIFICATION.get(code, "unclassified")
        rows.append(
            {
                "warning_code": code,
                "dashboard_display_group": group,
                "global_banner_required": group in {"dashboard_blocking_banner", "provider_concentration_banner"},
                "row_level_display_required": True,
                "summary_display_required": True,
                "prevents_ranked_top_n_candidate_display": True,
                "prevents_buy_position_action_display": True,
                "required_dashboard_copy": _warning_copy(code, group),
            }
        )
    return rows


def _warning_copy(code: str, group: str) -> str:
    if group == "dashboard_blocking_banner":
        return f"{code}: show as a blocking review-only banner; do not show ranked candidates or action-oriented lists."
    if group == "provider_concentration_banner":
        return f"{code}: show provider concentration banner and row-level warning; do not show action-oriented lists."
    if group == "row_level_and_summary_warning":
        return f"{code}: show at row level and in summary warning inventory; keep all rows non-actionable."
    return f"{code}: unclassified warning; block future dashboard contract until classified."


def _manifest(
    status: str,
    goal09_rows: list[dict[str, str]],
    warning_codes: list[str],
    classifications: list[dict[str, object]],
    failures: list[str],
) -> dict[str, object]:
    actionability_values = sorted({row.get("position_actionability_status", "") for row in goal09_rows})
    banner_codes = [code for code in warning_codes if WARNING_CLASSIFICATION.get(code) == "dashboard_blocking_banner"]
    provider_codes = [code for code in warning_codes if WARNING_CLASSIFICATION.get(code) == "provider_concentration_banner"]
    row_summary_codes = [code for code in warning_codes if WARNING_CLASSIFICATION.get(code) == "row_level_and_summary_warning"]
    return {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "status": status,
        "mode": MODE,
        "source_goal09_required": True,
        "goal09_status_confirmed": bool(goal09_rows) and status != BLOCKED,
        "goal09_non_actionable_confirmed": bool(goal09_rows) and actionability_values == ["never_actionable"],
        "goal09_output_grain": "trade_date + symbol",
        "goal09_row_count": len(goal09_rows),
        "position_actionability_status_values": actionability_values,
        "warning_codes_reviewed": warning_codes,
        "warning_classification": WARNING_CLASSIFICATION,
        "warning_classification_rows": classifications,
        "dashboard_blocking_banner_warning_codes": banner_codes,
        "provider_concentration_banner_warning_codes": provider_codes,
        "row_level_and_summary_warning_codes": row_summary_codes,
        "row_level_warning_codes_required": warning_codes,
        "warning_codes_preventing_action_oriented_display": warning_codes,
        "future_dashboard_contract_design_gate_may_be_requested": status != BLOCKED,
        "goal_dashboard00_request_status": "eligible_for_explicit_design_only_contract_gate" if status != BLOCKED else "blocked",
        "dashboard_daily_report_status_after_goal091": "locked_future",
        "dashboard_design_only_eligibility_only": status != BLOCKED,
        "dashboard_implemented_by_this_goal": False,
        "future_dashboard_review_only_required": True,
        "future_dashboard_never_actionable_required": True,
        "future_dashboard_non_actionable_disclaimers_required": True,
        "future_dashboard_global_and_row_level_disclaimers_required": True,
        "future_dashboard_may_use_only_audited_goal07b_goal08b_goal09_diagnostics": True,
        "future_dashboard_top_n_candidate_display_blocked": True,
        "future_dashboard_buy_candidate_display_blocked": True,
        "future_dashboard_position_candidate_display_blocked": True,
        "future_dashboard_actionable_language_blocked": True,
        "future_dashboard_forbidden_fields_blocked": True,
        "future_dashboard_forbidden_fields": sorted(DASHBOARD_FORBIDDEN_FIELD_NAMES),
        "future_dashboard_required_input_contracts": _dashboard_input_contracts(),
        "input_artifacts": [
            GOAL07B_REPORT_PATH,
            GOAL07B_AUDIT_PATH,
            GOAL07B_MANIFEST_PATH,
            GOAL07B_ROWS_PATH,
            GOAL08A_REPORT_PATH,
            GOAL08A_AUDIT_PATH,
            GOAL08A_MANIFEST_PATH,
            STORAGE01_REPORT_PATH,
            STORAGE01_AUDIT_PATH,
            STORAGE01_MANIFEST_PATH,
            GOAL08B0_REPORT_PATH,
            GOAL08B0_AUDIT_PATH,
            GOAL08B0_MANIFEST_PATH,
            GOAL08B_REPORT_PATH,
            GOAL08B_AUDIT_PATH,
            GOAL08B_MANIFEST_PATH,
            GOAL08B_ROWS_PATH,
            GOAL090_REPORT_PATH,
            GOAL090_AUDIT_PATH,
            GOAL090_MANIFEST_PATH,
            GOAL09_REPORT_PATH,
            GOAL09_AUDIT_PATH,
            GOAL09_MANIFEST_PATH,
            GOAL09_DIAGNOSTIC_PATH,
        ],
        "failures": failures,
        "warnings": warning_codes,
        "allowed_next_action": DASHBOARD00_ALLOWED_NEXT if status != BLOCKED else "repair_goal091_dashboard_readiness_blockers",
        **{key: False for key in FALSE_BOUNDARY_KEYS},
    }


def _dashboard_input_contracts() -> dict[str, object]:
    return {
        "risk_overlay_diagnostics": {
            "source_goal": "GOAL-07B",
            "path": GOAL07B_ROWS_PATH,
            "grain": "trade_date + symbol",
            "required_fields": ["trade_date", "symbol", "mode", "risk_severity", "risk_state", "risk_tag", "warning_propagation", "non_actionable"],
        },
        "recommendation_diagnostics": {
            "source_goal": "GOAL-08B",
            "path": GOAL08B_ROWS_PATH,
            "grain": "trade_date + symbol",
            "required_fields": ["trade_date", "symbol", "recommendation_diagnostic_label", "actionability_status", "actionability_blocked", "warning_propagation_codes", "diagnostic_mode", "non_actionable_disclaimer"],
        },
        "position_band_diagnostics": {
            "source_goal": "GOAL-09",
            "path": GOAL09_DIAGNOSTIC_PATH,
            "grain": "trade_date + symbol",
            "required_fields": ["trade_date", "symbol", "position_band_diagnostic_label", "position_band_status", "position_actionability_status", "position_actionability_blocked", "propagated_warning_codes", "diagnostic_mode", "non_actionable_disclaimer"],
        },
        "warning_propagation": {
            "required_fields": ["risk_warning_codes", "propagated_warning_codes", "blocked_reason_codes"],
            "display_requirement": "show_all_propagated_warning_codes_at_summary_and_row_level",
        },
        "actionability_flags": {
            "required_values": {"diagnostic_mode": "review_only", "actionability_status": "never_actionable", "position_actionability_status": "never_actionable"},
            "display_requirement": "global_and_row_level_non_actionable_disclaimers_required",
        },
        "audit_metadata": {
            "required_sources": [GOAL07B_MANIFEST_PATH, GOAL08B_MANIFEST_PATH, GOAL09_MANIFEST_PATH, MANIFEST_PATH],
            "display_requirement": "show_source_goal_lineage_manifest_status_and_audit_timestamps_when_available",
        },
    }


def _write_policy(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    write_json(
        root / CONFIG_PATH,
        {
            "goal": GOAL_NAME,
            "mode": MODE,
            "status": result["status"],
            "warning_classification": WARNING_CLASSIFICATION,
            "warning_classification_rows": result["classifications"],
            "dashboard_readiness": {
                "future_dashboard_contract_design_gate_may_be_requested": manifest["future_dashboard_contract_design_gate_may_be_requested"],
                "dashboard_daily_report_status_after_goal091": "locked_future",
                "dashboard_design_only_eligibility_only": True,
                "dashboard_outputs_generated": False,
            },
            "future_dashboard_rules": {
                "review_only_required": True,
                "never_actionable_required": True,
                "non_actionable_disclaimers_required_at_global_and_row_level": True,
                "only_audited_goal07b_goal08b_goal09_diagnostics_allowed": True,
                "ranked_top_n_candidate_lists_forbidden": True,
                "buy_position_action_oriented_displays_forbidden": True,
                "all_propagated_warning_codes_must_display": True,
                "audit_metadata_and_source_goal_lineage_required": True,
            },
            "future_dashboard_forbidden_fields": sorted(DASHBOARD_FORBIDDEN_FIELD_NAMES),
            "future_dashboard_required_input_contracts": _dashboard_input_contracts(),
            "forbidden_execution_output_constraints": {key: "must_remain_false" for key in FALSE_BOUNDARY_KEYS},
        },
    )


def _write_outputs(root: Path, result: dict[str, object]) -> None:
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_report(root, result)
    _write_doc(root, result)


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    classification_lines = [
        f"- `{row['warning_code']}`: `{row['dashboard_display_group']}`"
        for row in result["classifications"]
    ] or ["- `none`"]
    write_text(
        root / REPORT_PATH,
        "\n".join(
            [
                "# GOAL-09.1 Position-Band Warning Review and Dashboard Readiness Gate",
                "",
                f"GOAL-09.1 Position-Band Warning Review and Dashboard Readiness Gate: {result['status']}",
                "Mode: `review_readiness_only`",
                f"GOAL-09 rows reviewed: `{manifest['goal09_row_count']}`",
                "GOAL-09 output grain: `trade_date + symbol`",
                "GOAL-09 position actionability status: `never_actionable`",
                "GOAL-DASHBOARD-00 may be explicitly requested next as a future design-only contract/layout gate.",
                "Dashboard / Daily Report UI remains `locked_future`; no dashboard implementation is created.",
                "No dashboard files, HTML, Streamlit, frontend code, visual reports, new recommendation rows, new position rows, actual position sizes, portfolio weights, target weights, order quantities, buy/sell/hold actions, target prices, trading, production, backtest, factor-mining, broker, local-lake, or DQN/RL outputs were created.",
                "",
                "## Warning Classification",
                *classification_lines,
                "",
                "## Future Dashboard Contract Blocks",
                "- Future dashboard must remain review-only and never-actionable.",
                "- Future dashboard must show all propagated warnings at row and summary level.",
                "- Blocking and provider banners are required for their classified warning codes.",
                "- Ranked Top-N, buy-candidate, position-candidate, and action-oriented displays are blocked.",
                "- Buy, sell, hold, target price, expected return for action, position size, portfolio weight, target weight, order quantity, and execution fields are forbidden.",
                "",
                "## Failures",
                *[f"- {failure}" for failure in result["failures"]],
                "",
            ]
        ),
    )


def _write_doc(root: Path, result: dict[str, object]) -> None:
    classification_lines = [
        f"- `{row['warning_code']}`: `{row['dashboard_display_group']}`"
        for row in result["classifications"]
    ] or ["- `none`"]
    write_text(
        root / DOC_PATH,
        "\n".join(
            [
                "# GOAL-09.1 Warning Review and Dashboard Readiness",
                "",
                f"Status: `{result['status']}`",
                "",
                "GOAL-09.1 is a review/readiness-only gate. It classifies GOAL-09 warning codes and defines the constraints any future GOAL-DASHBOARD-00 contract/layout design gate must honor.",
                "",
                "It does not implement a dashboard and does not generate dashboard outputs, HTML, Streamlit, frontend code, or visual reports.",
                "",
                "## Warning Classification",
                "",
                *classification_lines,
                "",
                "## Future Dashboard Contract Requirements",
                "",
                "- Future dashboard views must be `review_only` and `never_actionable`.",
                "- Future dashboard views may display only audited GOAL-07B risk diagnostics, GOAL-08B recommendation diagnostics, GOAL-09 position-band diagnostics, warning propagation, actionability flags, and audit metadata.",
                "- Future dashboard views must show non-actionable disclaimers globally and at row level.",
                "- Future dashboard views must show all propagated warning codes.",
                "- Future dashboard views must not display ranked Top-N, buy-candidate, position-candidate, or action-oriented lists.",
                "- Future dashboard views must not include buy/sell/hold, target price, expected return for action, position size, portfolio weight, target weight, order quantity, trade action, or execution fields.",
                "- Paper/live trading, broker integration, production, backtest, factor-mining, local-lake, and DQN/RL remain locked.",
                "",
            ]
        ),
    )


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys())
    by_id = {row["workflow_id"]: row for row in rows}
    patch = goal091_implemented_workflow_patch()
    if result["status"] == BLOCKED:
        patch.update(
            {
                "status": "locked_future",
                "current_repo_role": "review_readiness_blocked",
                "implemented_in_repo": "false",
                "allowed_next_action": "repair_goal091_dashboard_readiness_blockers",
                "produces_artifacts": "",
                "primary_scripts": "",
                "primary_outputs": "",
                "promotion_rule": "locked_until_goal091_dashboard_readiness_passes",
                "notes": "GOAL-09.1 dashboard readiness is blocked; no dashboard contract design gate may be requested.",
            }
        )
    if WORKFLOW_ID in by_id:
        by_id[WORKFLOW_ID].update(patch)
    else:
        insert_at = next((index + 1 for index, item in enumerate(rows) if item["workflow_id"] == GOAL09_WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": WORKFLOW_ID, **patch})
        by_id = {row["workflow_id"]: row for row in rows}
    if DASHBOARD_WORKFLOW_ID in by_id:
        by_id[DASHBOARD_WORKFLOW_ID].update(
            {
                "status": "locked_future",
                "current_repo_role": "locked_downstream_boundary",
                "implemented_in_repo": "false",
                "allowed_next_action": DASHBOARD_LOCKED_NEXT if result["status"] != BLOCKED else "remain_locked",
                "depends_on": WORKFLOW_ID,
                "promotion_rule": "locked_until_explicit_goal_dashboard00_contract_design_gate",
                "notes": "Locked dashboard workflow; GOAL-09.1 allows only a future explicit design-only contract/layout gate request and creates no dashboard outputs.",
            }
        )
    for workflow_id in DOWNSTREAM_LOCKED_IDS:
        if workflow_id in by_id and workflow_id != DASHBOARD_WORKFLOW_ID:
            by_id[workflow_id]["status"] = "locked_future"
            by_id[workflow_id]["implemented_in_repo"] = "false"
            by_id[workflow_id]["allowed_next_action"] = "remain_locked"
    if "dqn_rl_mainline" in by_id:
        by_id["dqn_rl_mainline"]["status"] = "deleted_from_active_mainline"
        by_id["dqn_rl_mainline"]["implemented_in_repo"] = "false"
    if "v2_factor_research_upgrade" in by_id:
        by_id["v2_factor_research_upgrade"]["status"] = "planned_locked"
        by_id["v2_factor_research_upgrade"]["implemented_in_repo"] = "false"
    write_csv(path, rows, fields)


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    if not path.exists():
        return
    payload = read_json(path)
    payload[WORKFLOW_ID] = "implemented_review_only" if result["status"] != BLOCKED else False
    for key in [
        "dashboard",
        "paper_trading",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
        "signal_backtest",
        "portfolio_backtest",
        "dqn_rl",
    ]:
        payload[key] = False
    write_json(path, payload)


def _split_codes(value: str) -> list[str]:
    if not value or value == "none":
        return []
    return [item for item in str(value).split(";") if item and item != "none"]


def _report_pass_or_warn(text: str, prefix: str) -> bool:
    return f"{prefix} {PASS}" in text or f"{prefix} {PASS_WITH_WARNINGS}" in text


def _forbidden_output_dirs_present(root: Path) -> list[str]:
    return [path for path in FORBIDDEN_OUTPUT_DIRS if (root / path).exists()]


def _local_lake_paths_present(root: Path) -> list[str]:
    return [path for path in LOCAL_LAKE_PATHS if (root / path).exists()]


def _tracked_forbidden_files(root: Path) -> list[str]:
    try:
        result = subprocess.run(["git", "ls-files"], cwd=root, text=True, capture_output=True, check=True)
        tracked = result.stdout.splitlines()
    except Exception:  # pragma: no cover - fallback for non-git contexts
        tracked = [path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()]
    allowed = {
        CONFIG_PATH,
        DOC_PATH,
        REPORT_PATH,
        MANIFEST_PATH,
        AUDIT_PATH,
        GOAL07B_ROWS_PATH,
        GOAL08B_ROWS_PATH,
        GOAL09_DIAGNOSTIC_PATH,
    }
    matches: list[str] = []
    for rel in tracked:
        if rel in allowed:
            continue
        lowered = rel.lower()
        suffix = Path(lowered).suffix
        if lowered.endswith(".csv.gz") or suffix in FORBIDDEN_TRACKED_SUFFIXES:
            matches.append(rel)
    return sorted(set(matches))


def _workflow_rows(root: Path) -> dict[str, dict[str, str]]:
    path = root / "configs/project/workflow_status.csv"
    return {row["workflow_id"]: row for row in read_csv(path)} if path.exists() else {}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_csv(path: Path) -> list[dict[str, str]]:
    return read_csv(path) if path.exists() else []


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return read_json(path)
    except Exception:
        return {}

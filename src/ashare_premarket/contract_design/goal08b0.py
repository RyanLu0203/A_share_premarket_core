from __future__ import annotations

import subprocess
from pathlib import Path

from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.review_diagnostics.goal08b import (
    DIAGNOSTIC_PATH as GOAL08B_DIAGNOSTIC_PATH,
    GOAL08B_ALLOWED_NEXT as GOAL08B_IMPLEMENTED_ALLOWED_NEXT,
    GOAL08B_IMPLEMENTED_STATUS,
    WORKFLOW_NOTES as GOAL08B_WORKFLOW_NOTES,
    WORKFLOW_PRIMARY_DOCS as GOAL08B_WORKFLOW_PRIMARY_DOCS,
    WORKFLOW_PRIMARY_OUTPUTS as GOAL08B_WORKFLOW_PRIMARY_OUTPUTS,
    WORKFLOW_PRIMARY_SCRIPTS as GOAL08B_WORKFLOW_PRIMARY_SCRIPTS,
    WORKFLOW_PRODUCES_ARTIFACTS as GOAL08B_WORKFLOW_PRODUCES_ARTIFACTS,
    goal08b_valid_diagnostics_evidence,
)
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-08B.0"
GOAL_NAME = "GOAL-08B.0-RECOMMENDATION-REVIEW-ONLY-UNLOCK-GATE"
MODE = "review_only_unlock_gate"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

CONFIG_DIR = "configs/recommendation"
DOC_DIR = "docs/recommendation"
AUDIT_DIR = "outputs/audits"

POLICY_PATH = f"{CONFIG_DIR}/goal08b0_review_only_unlock_policy.yaml"
DOC_PATH = f"{DOC_DIR}/GOAL08B0_RECOMMENDATION_REVIEW_ONLY_UNLOCK_GATE.md"
REPORT_PATH = f"{AUDIT_DIR}/goal08b0_recommendation_review_only_unlock_report.md"
MANIFEST_PATH = f"{AUDIT_DIR}/goal08b0_recommendation_review_only_unlock_manifest.json"
AUDIT_PATH = f"{AUDIT_DIR}/goal08b0_recommendation_review_only_unlock_audit.md"

GOAL07B_REPORT_PATH = "outputs/audits/goal07b_risk_overlay_calculation_report.md"
GOAL07B_AUDIT_PATH = "outputs/audits/goal07b_risk_overlay_calculation_audit.md"
GOAL07B_MANIFEST_PATH = "outputs/audits/goal07b_risk_overlay_calculation_manifest.json"
GOAL08A_REPORT_PATH = "outputs/audits/goal08a_recommendation_contract_design_report.md"
GOAL08A_AUDIT_PATH = "outputs/audits/goal08a_recommendation_contract_design_audit.md"
GOAL08A_MANIFEST_PATH = "outputs/audits/goal08a_recommendation_contract_design_manifest.json"
GOAL08A_INPUT_CONTRACT_PATH = "configs/recommendation/goal08a_future_recommendation_input_contract.yaml"
GOAL08A_SCHEMA_PATH = "configs/recommendation/goal08a_future_recommendation_schema.yaml"
GOAL08A_WARNING_POLICY_PATH = "configs/recommendation/goal08a_warning_propagation_policy.yaml"
GOAL08A_ACTIONABILITY_PATH = "configs/recommendation/goal08a_actionability_guardrails.yaml"
GOAL_STORAGE01_REPORT_PATH = "outputs/audits/goal_storage01_local_research_lake_hardening_report.md"
GOAL_STORAGE01_AUDIT_PATH = "outputs/audits/goal_storage01_local_research_lake_hardening_audit.md"
GOAL_STORAGE01_MANIFEST_PATH = "outputs/audits/goal_storage01_local_research_lake_hardening_manifest.json"

GOAL07B_WORKFLOW_ID = "goal07b_risk_overlay_calculation"
GOAL08A_WORKFLOW_ID = "goal08a_recommendation_contract_design_gate"
GOAL_STORAGE01_WORKFLOW_ID = "goal_storage01_local_research_lake_hardening_gate"
GOAL08B0_WORKFLOW_ID = "goal08b0_recommendation_review_only_unlock_gate"
GOAL08B_WORKFLOW_ID = "goal08b_recommendation_review_only_prototype"

GOAL08B_LOCKED_STATUS = "locked_future"
GOAL08B_ELIGIBLE_STATUS = "future_review_only"
GOAL08B0_READY = "eligible_for_future_review_only_prototype"
GOAL08B0_BLOCKED = "blocked_until_prior_review_evidence_passes"
GOAL08B0_ALLOWED_NEXT = "await_explicit_goal08b_review_only_recommendation_diagnostics_prototype"
GOAL08B0_BLOCKED_NEXT = "repair_goal08b0_unlock_blockers"

FORBIDDEN_OUTPUT_DIRS = [
    "outputs/recommendations",
    "outputs/positions",
    "outputs/dashboard",
    "outputs/paper_trading",
    "outputs/live_trading",
    "outputs/backtests",
    "outputs/factors",
]

LOCAL_LAKE_PATH_MARKERS = [
    "data/raw/",
    "data/bundles/",
    "data/lake/",
    "data/metadata/",
    "data/exports/",
    "local_data/",
    "local_data_lake",
    "raw_provider_payloads",
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

DOWNSTREAM_LOCKED_IDS = [
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
]

FALSE_BOUNDARY_KEYS = [
    "recommendation_diagnostics_rows_generated",
    "recommendation_rows_generated",
    "buy_sell_hold_outputs_generated",
    "target_prices_generated",
    "position_sizing_generated",
    "portfolio_construction_generated",
    "dashboard_generated",
    "paper_trading_enabled",
    "live_trading_enabled",
    "broker_integration_enabled",
    "production_model_behavior_created",
    "database_writes_created",
    "backtests_run",
    "factor_mining_outputs_created",
    "dqn_rl_outputs_created",
    "actionable_outputs_generated",
    "local_lake_files_created",
    "data_coverage_expanded",
    "live_calculation_outputs_used",
    "downstream_stages_unlocked_by_this_gate",
]


def run_goal08b0_recommendation_review_only_unlock_gate(root: Path) -> bool:
    bundle = load_goal08b0_unlock_bundle(root)
    review = evaluate_goal08b0_unlock_gate(bundle)
    _write_policy(root, review)
    _write_outputs(root, review)
    _update_workflow_status(root, review)
    _update_locked_capabilities(root, review)
    audit_ok = audit_goal08b0_recommendation_review_only_unlock_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return review["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal08b0_recommendation_review_only_unlock_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    workflow = _workflow_rows(root)
    goal08b_valid = goal08b_valid_diagnostics_evidence(root)
    failures: list[str] = []
    warnings: list[str] = []

    if not _report_pass_or_warn(report, "GOAL-08B.0 Recommendation Review-Only Unlock Gate:"):
        failures.append("unlock_report_not_pass_or_warn")
    if manifest.get("goal") != GOAL_NAME:
        failures.append("manifest_goal_invalid")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_not_review_only_unlock_gate")
    if manifest.get("goal08b0_unlock_status") != GOAL08B0_READY:
        failures.append("manifest_unlock_status_not_ready")
    if manifest.get("goal08b_target_status") not in {GOAL08B_ELIGIBLE_STATUS, GOAL08B_IMPLEMENTED_STATUS}:
        failures.append("manifest_goal08b_target_not_future_or_implemented_review_only")
    if manifest.get("goal08b_implemented_by_this_gate") is not False:
        failures.append("manifest_goal08b_implemented_by_gate_not_false")
    if goal08b_valid:
        if manifest.get("goal08b_implemented_in_repo") is not True:
            failures.append("manifest_goal08b_implemented_in_repo_not_true_after_valid_diagnostics")
    elif manifest.get("goal08b_implemented_in_repo") is not False:
        failures.append("manifest_goal08b_implemented_in_repo_not_false_without_valid_diagnostics")
    if manifest.get("evidence_basis") != "prior_pass_or_pass_with_warnings_review_only_and_design_evidence_only_no_live_outputs":
        failures.append("manifest_evidence_basis_invalid")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"manifest_{key}_not_false")
    for key in [
        "future_goal08b_input_contract_ready",
        "high_risk_actionability_block_preserved",
        "goal07b_warnings_propagate_to_future_diagnostics",
        "future_recommendation_diagnostics_non_actionable_required",
        "storage_prerequisite_ready",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")

    gate_row = workflow.get(GOAL08B0_WORKFLOW_ID, {})
    if gate_row.get("status") != "implemented_review_only":
        failures.append("goal08b0_workflow_not_implemented_review_only")
    if gate_row.get("implemented_in_repo") != "true":
        failures.append("goal08b0_workflow_not_marked_implemented")
    goal08b = workflow.get(GOAL08B_WORKFLOW_ID, {})
    if goal08b_valid:
        if goal08b.get("status") != GOAL08B_IMPLEMENTED_STATUS:
            failures.append("goal08b_valid_diagnostics_not_implemented_review_only")
        if goal08b.get("implemented_in_repo") != "true":
            failures.append("goal08b_valid_diagnostics_not_marked_implemented")
        if goal08b.get("allowed_next_action") != GOAL08B_IMPLEMENTED_ALLOWED_NEXT:
            failures.append("goal08b_valid_diagnostics_allowed_next_invalid")
    else:
        if goal08b.get("status") != GOAL08B_ELIGIBLE_STATUS:
            failures.append("goal08b_workflow_not_future_review_only")
        if goal08b.get("implemented_in_repo") != "false":
            failures.append("goal08b_workflow_marked_implemented_without_valid_diagnostics")
        if goal08b.get("allowed_next_action") != GOAL08B0_ALLOWED_NEXT:
            failures.append("goal08b_allowed_next_invalid")
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

    forbidden_dirs = _forbidden_output_dirs_present(root)
    failures.extend(f"forbidden_output_dir_present:{path}" for path in forbidden_dirs)
    forbidden_rows = _forbidden_recommendation_row_outputs(root)
    failures.extend(f"forbidden_recommendation_row_output_present:{path}" for path in forbidden_rows)
    tracked_heavy = _tracked_forbidden_files(root)
    failures.extend(f"forbidden_tracked_artifact:{path}" for path in tracked_heavy)
    local_lake = _local_lake_paths_present(root)
    failures.extend(f"local_lake_path_present:{path}" for path in local_lake)

    status = PASS if not failures else BLOCKED
    write_text(
        root / AUDIT_PATH,
        "\n".join(
            [
                "# GOAL-08B.0 Recommendation Review-Only Unlock Audit",
                "",
                f"Status: `{status}`",
                "",
                f"GOAL-08B.0 workflow status: `{gate_row.get('status', 'missing')}`",
                f"GOAL-08B workflow status: `{goal08b.get('status', 'missing')}`",
                "GOAL-08B implemented by this gate: `false`",
                f"GOAL-08B implemented in repo: `{str(goal08b_valid).lower()}`",
                "Future GOAL-08B eligibility: `future_review_only`",
                "Recommendation diagnostic rows generated by this gate: `false`",
                "Recommendation, position, dashboard, trading, production, backtest, factor-mining, broker, and DQN/RL outputs generated: `false`",
                "Evidence basis: prior GOAL-07B, GOAL-08A, and GOAL-STORAGE-01 PASS/PASS_WITH_WARNINGS reports and manifests only; no live outputs.",
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
    return status == PASS


def load_goal08b0_unlock_bundle(root: Path) -> dict[str, object]:
    return {
        "goal07b_report": _read(root / GOAL07B_REPORT_PATH),
        "goal07b_audit": _read(root / GOAL07B_AUDIT_PATH),
        "goal07b_manifest": _read_json(root / GOAL07B_MANIFEST_PATH),
        "goal08a_report": _read(root / GOAL08A_REPORT_PATH),
        "goal08a_audit": _read(root / GOAL08A_AUDIT_PATH),
        "goal08a_manifest": _read_json(root / GOAL08A_MANIFEST_PATH),
        "goal08a_input_contract": _read_json(root / GOAL08A_INPUT_CONTRACT_PATH),
        "goal08a_schema": _read_json(root / GOAL08A_SCHEMA_PATH),
        "goal08a_warning_policy": _read_json(root / GOAL08A_WARNING_POLICY_PATH),
        "goal08a_actionability": _read_json(root / GOAL08A_ACTIONABILITY_PATH),
        "storage01_report": _read(root / GOAL_STORAGE01_REPORT_PATH),
        "storage01_audit": _read(root / GOAL_STORAGE01_AUDIT_PATH),
        "storage01_manifest": _read_json(root / GOAL_STORAGE01_MANIFEST_PATH),
        "workflow_rows": _read_csv(root / "configs/project/workflow_status.csv"),
        "forbidden_output_dirs": _forbidden_output_dirs_present(root),
        "forbidden_row_outputs": _forbidden_recommendation_row_outputs(root),
        "tracked_forbidden_files": _tracked_forbidden_files(root),
        "local_lake_paths": _local_lake_paths_present(root),
        "goal08b_valid_diagnostics_evidence": goal08b_valid_diagnostics_evidence(root),
    }


def evaluate_goal08b0_unlock_gate(bundle: dict[str, object]) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    goal07b_manifest = bundle.get("goal07b_manifest", {})
    goal08a_manifest = bundle.get("goal08a_manifest", {})
    goal08a_input_contract = bundle.get("goal08a_input_contract", {})
    goal08a_schema = bundle.get("goal08a_schema", {})
    goal08a_warning_policy = bundle.get("goal08a_warning_policy", {})
    goal08a_actionability = bundle.get("goal08a_actionability", {})
    storage01_manifest = bundle.get("storage01_manifest", {})
    workflow = {row.get("workflow_id", ""): row for row in bundle.get("workflow_rows", []) if isinstance(row, dict)}
    goal08b_valid = bool(bundle.get("goal08b_valid_diagnostics_evidence"))

    if not _report_pass_or_warn(str(bundle.get("goal07b_report", "")), "GOAL-07B Risk Overlay Calculation Prototype:"):
        failures.append("goal07b_report_not_pass_or_warn")
    elif "PASS_WITH_WARNINGS" in str(bundle.get("goal07b_report", "")):
        warnings.append("goal07b_prior_pass_with_warnings")
    if "Status: `PASS`" not in str(bundle.get("goal07b_audit", "")):
        failures.append("goal07b_audit_not_pass")
    if not isinstance(goal07b_manifest, dict) or not goal07b_manifest:
        failures.append("goal07b_manifest_missing")
        goal07b_manifest = {}
    if goal07b_manifest.get("mode") != "review_only":
        failures.append("goal07b_manifest_not_review_only")
    if goal07b_manifest.get("output_grain") != "trade_date + symbol":
        failures.append("goal07b_manifest_grain_invalid")
    if goal07b_manifest.get("non_actionable") is not True:
        failures.append("goal07b_manifest_not_non_actionable")
    for key in [
        "recommendation_generated",
        "position_generated",
        "dashboard_generated",
        "paper_live_trading_generated",
        "trading_generated",
        "production_generated",
        "backtest_generated",
        "factor_mining_generated",
        "dqn_rl_generated",
    ]:
        if goal07b_manifest.get(key) is not False:
            failures.append(f"goal07b_manifest_{key}_not_false")

    if not _report_pass_or_warn(str(bundle.get("goal08a_report", "")), "GOAL-08A Recommendation Contract Design Gate:"):
        failures.append("goal08a_report_not_pass_or_warn")
    if "Status: `PASS`" not in str(bundle.get("goal08a_audit", "")):
        failures.append("goal08a_audit_not_pass")
    if not isinstance(goal08a_manifest, dict) or not goal08a_manifest:
        failures.append("goal08a_manifest_missing")
        goal08a_manifest = {}
    if goal08a_manifest.get("mode") != "design_only":
        failures.append("goal08a_manifest_not_design_only")
    if goal08a_manifest.get("future_schema_row_count") != 0:
        failures.append("goal08a_manifest_future_schema_row_count_not_zero")
    if goal08a_manifest.get("future_schema_names_only") is not True:
        failures.append("goal08a_manifest_schema_not_names_only")
    if goal08a_manifest.get("high_risk_severity_blocks_actionable_output") is not True:
        failures.append("goal08a_manifest_high_risk_block_missing")
    for key in _goal08a_false_boundary_keys():
        if goal08a_manifest.get(key) is not False:
            failures.append(f"goal08a_manifest_{key}_not_false")
    if goal08a_input_contract.get("required_input_grain") != "trade_date + symbol":
        failures.append("goal08a_input_contract_grain_invalid")
    if goal08a_input_contract.get("source_artifacts", {}).get("rows_are_actionable") is not False:
        failures.append("goal08a_input_contract_source_not_non_actionable")
    if goal08a_schema.get("future_schema_names_only") is not True:
        failures.append("goal08a_schema_not_names_only")
    if goal08a_schema.get("empty_schema_sample", {}).get("row_count") != 0:
        failures.append("goal08a_schema_row_count_not_zero")
    if goal08a_schema.get("empty_schema_sample", {}).get("rows") != []:
        failures.append("goal08a_schema_rows_not_empty")
    if goal08a_actionability.get("high_risk_severity_blocks_actionable_recommendation") is not True:
        failures.append("goal08a_actionability_high_risk_block_missing")
    if goal08a_actionability.get("recommendation_like_diagnostic_must_be_non_actionable") is not True:
        failures.append("goal08a_actionability_non_actionable_missing")
    if goal08a_actionability.get("goal08a_generates_actions") is not False:
        failures.append("goal08a_actionability_generates_actions_not_false")
    for item in goal08a_warning_policy.get("warning_propagation_rules", []):
        if item.get("propagate_to_future_contract") is not True:
            failures.append(f"goal08a_warning_policy_not_propagated:{item.get('warning_code', 'missing')}")

    if "GOAL-STORAGE-01 Local Research Lake Hardening Gate: PASS" not in str(bundle.get("storage01_report", "")):
        failures.append("storage01_report_not_pass")
    if "Status: `PASS`" not in str(bundle.get("storage01_audit", "")):
        failures.append("storage01_audit_not_pass")
    if not isinstance(storage01_manifest, dict) or not storage01_manifest:
        failures.append("storage01_manifest_missing")
        storage01_manifest = {}
    if storage01_manifest.get("mode") != "infrastructure_only":
        failures.append("storage01_manifest_not_infrastructure_only")
    if storage01_manifest.get("workflow_status_after_pass") != "implemented_infrastructure_only":
        failures.append("storage01_manifest_workflow_status_invalid")
    if storage01_manifest.get("goal08b_implemented_by_this_gate") is not False:
        failures.append("storage01_manifest_goal08b_implemented_not_false")
    if storage01_manifest.get("goal08b_unlocked_by_this_gate") is not False:
        failures.append("storage01_manifest_goal08b_unlocked_by_storage_not_false")
    if storage01_manifest.get("local_data_files_created") is not False:
        failures.append("storage01_manifest_local_files_created_not_false")
    if storage01_manifest.get("tracked_forbidden_artifact_count") != 0:
        failures.append("storage01_manifest_tracked_forbidden_artifacts_not_zero")
    for key in _storage_false_boundary_keys():
        if storage01_manifest.get(key) is not False:
            failures.append(f"storage01_manifest_{key}_not_false")

    goal07b = workflow.get(GOAL07B_WORKFLOW_ID, {})
    if goal07b.get("status") != "implemented_review_only" or goal07b.get("implemented_in_repo") != "true":
        failures.append("goal07b_workflow_not_implemented_review_only")
    goal08a = workflow.get(GOAL08A_WORKFLOW_ID, {})
    if goal08a.get("status") != "implemented_design_only" or goal08a.get("implemented_in_repo") != "true":
        failures.append("goal08a_workflow_not_implemented_design_only")
    storage01 = workflow.get(GOAL_STORAGE01_WORKFLOW_ID, {})
    if storage01.get("status") != "implemented_infrastructure_only" or storage01.get("implemented_in_repo") != "true":
        failures.append("storage01_workflow_not_implemented_infrastructure_only")
    goal08b = workflow.get(GOAL08B_WORKFLOW_ID, {})
    if goal08b_valid:
        if goal08b.get("status") != GOAL08B_IMPLEMENTED_STATUS or goal08b.get("implemented_in_repo") != "true":
            failures.append("goal08b_valid_diagnostics_not_preserved")
    else:
        if goal08b.get("status") not in {GOAL08B_LOCKED_STATUS, GOAL08B_ELIGIBLE_STATUS}:
            failures.append("goal08b_workflow_not_locked_or_future_review_only")
        if goal08b.get("implemented_in_repo") != "false":
            failures.append("goal08b_workflow_marked_implemented_before_unlock")
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
    if bundle.get("forbidden_row_outputs"):
        failures.append("forbidden_recommendation_row_outputs_present:" + ";".join(str(path) for path in bundle["forbidden_row_outputs"]))
    if bundle.get("tracked_forbidden_files"):
        failures.append("tracked_forbidden_artifacts_present:" + ";".join(str(path) for path in bundle["tracked_forbidden_files"]))
    if bundle.get("local_lake_paths"):
        failures.append("local_lake_paths_present:" + ";".join(str(path) for path in bundle["local_lake_paths"]))

    status = BLOCKED if failures else (PASS_WITH_WARNINGS if warnings else PASS)
    return {
        "status": status,
        "goal08b0_unlock_status": GOAL08B0_BLOCKED if failures else GOAL08B0_READY,
        "goal08b_prior_status": goal08b.get("status", "missing"),
        "goal08b_target_status": GOAL08B_LOCKED_STATUS if failures else (GOAL08B_IMPLEMENTED_STATUS if goal08b_valid else GOAL08B_ELIGIBLE_STATUS),
        "goal08b_transition_rule": "preserve_valid_implemented_review_only_or_locked_future_to_future_review_only_eligibility_only",
        "goal08b_implemented_in_repo": goal08b_valid,
        "allowed_next_action": GOAL08B0_BLOCKED_NEXT if failures else (GOAL08B_IMPLEMENTED_ALLOWED_NEXT if goal08b_valid else GOAL08B0_ALLOWED_NEXT),
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "goal07b_warnings": sorted(str(item) for item in goal07b_manifest.get("warnings_remaining", [])),
        "evidence_inputs": [
            GOAL07B_REPORT_PATH,
            GOAL07B_AUDIT_PATH,
            GOAL07B_MANIFEST_PATH,
            GOAL08A_REPORT_PATH,
            GOAL08A_AUDIT_PATH,
            GOAL08A_MANIFEST_PATH,
            GOAL08A_INPUT_CONTRACT_PATH,
            GOAL08A_SCHEMA_PATH,
            GOAL08A_WARNING_POLICY_PATH,
            GOAL08A_ACTIONABILITY_PATH,
            GOAL_STORAGE01_REPORT_PATH,
            GOAL_STORAGE01_AUDIT_PATH,
            GOAL_STORAGE01_MANIFEST_PATH,
            "configs/project/workflow_status.csv",
        ],
    }


def _write_policy(root: Path, review: dict[str, object]) -> None:
    write_json(
        root / POLICY_PATH,
        {
            "goal": GOAL_NAME,
            "mode": MODE,
            "unlocks": "GOAL-08B review-only eligibility only",
            "goal08b_status_after_pass": review["goal08b_target_status"],
            "goal08b_implemented_by_this_gate_after_pass": False,
            "goal08b_implemented_in_repo_after_pass": review["goal08b_implemented_in_repo"],
            "allowed_next_action_after_pass": review["allowed_next_action"],
            "required_prior_evidence": [
                "GOAL-07B implemented_review_only PASS/PASS_WITH_WARNINGS non-actionable diagnostics",
                "GOAL-08A implemented_design_only PASS names-only zero-row contract",
                "GOAL-STORAGE-01 implemented_infrastructure_only PASS storage hardening",
            ],
            "future_goal08b_requirements": {
                "diagnostics_must_be_non_actionable": True,
                "high_risk_severity_blocks_actionable_output": True,
                "goal07b_warnings_must_propagate": True,
                "requires_separate_explicit_prototype_request": True,
            },
            "forbidden_execution": {
                "recommendation_diagnostics_rows": True,
                "recommendation_rows": True,
                "buy_sell_hold_outputs": True,
                "target_prices": True,
                "position_sizing": True,
                "portfolio_construction": True,
                "dashboard_outputs": True,
                "paper_or_live_trading": True,
                "broker_integration": True,
                "production_db_writes": True,
                "production_model_behavior": True,
                "backtests": True,
                "factor_mining": True,
                "dqn_rl": True,
                "local_lake_materialization": True,
                "data_coverage_expansion": True,
            },
            "evidence_source_policy": "prior_audit_reports_and_manifests_only_no_live_calculation_outputs",
            "forbidden_output_dirs": FORBIDDEN_OUTPUT_DIRS,
            "status": review["status"],
        },
    )


def _write_outputs(root: Path, review: dict[str, object]) -> None:
    _write_report(root, review)
    _write_manifest(root, review)
    _write_doc(root, review)


def _write_report(root: Path, review: dict[str, object]) -> None:
    warning_lines = [f"- `{warning}`" for warning in review["warnings"]] or ["- `none`"]
    goal07b_warning_lines = [f"- `{warning}`" for warning in review["goal07b_warnings"]] or ["- `none`"]
    write_text(
        root / REPORT_PATH,
        "\n".join(
            [
                "# GOAL-08B.0 Recommendation Review-Only Unlock Gate Report",
                "",
                f"GOAL-08B.0 Recommendation Review-Only Unlock Gate: {review['status']}",
                f"GOAL-08B.0 unlock status: {review['goal08b0_unlock_status']}",
                f"GOAL-08B prior status: `{review['goal08b_prior_status']}`",
                f"GOAL-08B target status: `{review['goal08b_target_status']}`",
                f"GOAL-08B transition rule: `{review['goal08b_transition_rule']}`",
                f"Allowed next action: `{review['allowed_next_action']}`",
                "",
                "GOAL-08B.0 only grants eligibility for a future explicit non-actionable recommendation diagnostics prototype request or preserves an already valid GOAL-08B review-only diagnostic state.",
                "GOAL-08B is not implemented by this gate.",
                "No recommendation diagnostics rows, recommendation rows, buy/sell/hold decisions, target prices, position sizing, portfolio construction, dashboard outputs, paper/live trading paths, broker paths, production behavior, backtests, factor-mining outputs, local lake files, or DQN/RL outputs were created by this gate.",
                "Future GOAL-08B work, if separately requested later, must remain review-only, non-actionable, and must propagate GOAL-07B warnings. HIGH GOAL-07B risk severity must continue to block actionable output.",
                "Evidence basis: prior GOAL-07B PASS/PASS_WITH_WARNINGS review-only diagnostics, GOAL-08A PASS design-only zero-row contracts, and GOAL-STORAGE-01 PASS infrastructure evidence only; no live calculation outputs were used.",
                "",
                "## Evidence Inputs",
                *[f"- `{item}`" for item in review["evidence_inputs"]],
                "",
                "## GOAL-07B Warnings To Propagate",
                *goal07b_warning_lines,
                "",
                "## Failures",
                *[f"- {failure}" for failure in review["failures"]],
                "",
                "## Warnings",
                *warning_lines,
                "",
            ]
        ),
    )


def _write_manifest(root: Path, review: dict[str, object]) -> None:
    manifest = {
        "goal": GOAL_NAME,
        "status": review["status"],
        "mode": MODE,
        "goal08b0_unlock_status": review["goal08b0_unlock_status"],
        "goal08b_prior_status": review["goal08b_prior_status"],
        "goal08b_target_status": review["goal08b_target_status"],
        "goal08b_transition_rule": review["goal08b_transition_rule"],
        "goal08b_implemented_by_this_gate": False,
        "goal08b_implemented_in_repo": review["goal08b_implemented_in_repo"],
        "allowed_next_action": review["allowed_next_action"],
        "future_goal08b_input_contract_ready": review["status"] != BLOCKED,
        "high_risk_actionability_block_preserved": review["status"] != BLOCKED,
        "goal07b_warnings_propagate_to_future_diagnostics": review["status"] != BLOCKED,
        "future_recommendation_diagnostics_non_actionable_required": review["status"] != BLOCKED,
        "storage_prerequisite_ready": review["status"] != BLOCKED,
        "evidence_inputs": review["evidence_inputs"],
        "evidence_basis": "prior_pass_or_pass_with_warnings_review_only_and_design_evidence_only_no_live_outputs",
        "goal07b_warnings_to_propagate": review["goal07b_warnings"],
        "failures": review["failures"],
        "warnings": review["warnings"],
        **{key: False for key in FALSE_BOUNDARY_KEYS},
    }
    write_json(root / MANIFEST_PATH, manifest)


def _write_doc(root: Path, review: dict[str, object]) -> None:
    write_text(
        root / DOC_PATH,
        "\n".join(
            [
                "# GOAL-08B.0 Recommendation Review-Only Unlock Gate",
                "",
                f"Status: `{review['status']}`",
                "",
                "GOAL-08B.0 is an unlock-only governance gate. It may mark GOAL-08B `future_review_only` eligible for a later explicit non-actionable diagnostics prototype request, or preserve a valid later GOAL-08B `implemented_review_only` diagnostic state. It does not implement GOAL-08B by itself.",
                "",
                "## Evidence Basis",
                "",
                "- GOAL-07B is `implemented_review_only` and produces only non-actionable risk overlay diagnostics.",
                "- GOAL-08A is `implemented_design_only` and its future schema sample has row count `0`.",
                "- GOAL-STORAGE-01 is `implemented_infrastructure_only` and does not unlock GOAL-08B by itself.",
                "",
                "## Preserved Boundary",
                "",
                "This gate creates no recommendation diagnostics rows, recommendation rows, buy/sell/hold outputs, target prices, positions, portfolio weights, dashboards, paper/live trading paths, broker paths, production behavior, backtests, factor-mining artifacts, local lake files, or DQN/RL outputs.",
                "",
                "Any future GOAL-08B prototype must remain review-only and non-actionable, must propagate GOAL-07B warnings, and must keep HIGH risk severity as an actionability blocker.",
                "",
            ]
        ),
    )


def _update_workflow_status(root: Path, review: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys())
    by_id = {row["workflow_id"]: row for row in rows}
    gate_row = {
        "workflow_id": GOAL08B0_WORKFLOW_ID,
        "display_name": "GOAL-08B.0 Recommendation Review-Only Unlock Gate",
        "stage_or_goal": "GOAL-08B.0",
        "status": "implemented_review_only" if review["status"] != BLOCKED else "locked_future",
        "current_repo_role": "review_only_unlock_governance_gate",
        "implemented_in_repo": "true" if review["status"] != BLOCKED else "false",
        "allowed_next_action": str(review["allowed_next_action"]),
        "depends_on": GOAL_STORAGE01_WORKFLOW_ID,
        "produces_artifacts": ";".join([POLICY_PATH, DOC_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH]),
        "primary_docs": f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "scripts/run_goal08b0_recommendation_review_only_unlock_gate.py;scripts/audit_goal08b0_recommendation_review_only_unlock_gate.py",
        "primary_outputs": f"{REPORT_PATH};{MANIFEST_PATH};{AUDIT_PATH}",
        "promotion_rule": "implemented_review_only_after_goal08b0_unlock_gate_pass_with_warnings",
        "notes": "Review-only unlock gate; marks GOAL-08B eligible for a future non-actionable diagnostics prototype but does not implement recommendation diagnostics.",
    }
    if GOAL08B0_WORKFLOW_ID in by_id:
        by_id[GOAL08B0_WORKFLOW_ID].update(gate_row)
    else:
        insert_at = next((index for index, row in enumerate(rows) if row["workflow_id"] == GOAL08B_WORKFLOW_ID), len(rows))
        rows.insert(insert_at, gate_row)
    by_id = {row["workflow_id"]: row for row in rows}
    if GOAL08B_WORKFLOW_ID in by_id:
        if review["goal08b_target_status"] == GOAL08B_IMPLEMENTED_STATUS:
            by_id[GOAL08B_WORKFLOW_ID].update(
                {
                    "display_name": "GOAL-08B Recommendation Review-Only Prototype",
                    "stage_or_goal": "GOAL-08B",
                    "status": GOAL08B_IMPLEMENTED_STATUS,
                    "current_repo_role": "review_only_recommendation_diagnostic_prototype",
                    "implemented_in_repo": "true",
                    "allowed_next_action": GOAL08B_IMPLEMENTED_ALLOWED_NEXT,
                    "depends_on": GOAL08B0_WORKFLOW_ID,
                    "produces_artifacts": GOAL08B_WORKFLOW_PRODUCES_ARTIFACTS,
                    "primary_docs": GOAL08B_WORKFLOW_PRIMARY_DOCS,
                    "primary_scripts": GOAL08B_WORKFLOW_PRIMARY_SCRIPTS,
                    "primary_outputs": GOAL08B_WORKFLOW_PRIMARY_OUTPUTS,
                    "promotion_rule": "implemented_review_only_after_goal08b_diagnostics_pass_with_warnings",
                    "notes": GOAL08B_WORKFLOW_NOTES,
                }
            )
        else:
            by_id[GOAL08B_WORKFLOW_ID].update(
                {
                    "display_name": "GOAL-08B Recommendation Review-Only Prototype",
                    "stage_or_goal": "GOAL-08B",
                    "status": str(review["goal08b_target_status"]),
                    "current_repo_role": "review_only_eligible_not_implemented" if review["status"] != BLOCKED else "locked_downstream_recommendation_boundary",
                    "implemented_in_repo": "false",
                    "allowed_next_action": GOAL08B0_ALLOWED_NEXT if review["status"] != BLOCKED else "remain_locked_until_goal08b0_passes",
                    "depends_on": GOAL08B0_WORKFLOW_ID,
                    "produces_artifacts": "",
                    "primary_docs": f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
                    "primary_scripts": "",
                    "primary_outputs": "",
                    "promotion_rule": "eligible_for_future_review_only_prototype_after_goal08b0_unlock_gate",
                    "notes": "Eligibility only; GOAL-08B recommendation diagnostics are not implemented and no recommendation rows or downstream outputs exist.",
                }
            )
    for workflow_id in DOWNSTREAM_LOCKED_IDS:
        if workflow_id in by_id:
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


def _update_locked_capabilities(root: Path, review: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    if not path.exists():
        return
    payload = read_json(path)
    payload[GOAL08B0_WORKFLOW_ID] = "implemented_review_only" if review["status"] != BLOCKED else False
    payload[GOAL08B_WORKFLOW_ID] = review["goal08b_target_status"] if review["status"] != BLOCKED else False
    for key in [
        "position_band_recommendation",
        "signal_backtest",
        "portfolio_backtest",
        "dashboard",
        "paper_trading",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
        "dqn_rl",
    ]:
        payload[key] = False
    write_json(path, payload)


def goal08b0_valid_unlock_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        _report_pass_or_warn(report, "GOAL-08B.0 Recommendation Review-Only Unlock Gate:")
        and "Status: `PASS`" in audit
        and manifest.get("mode") == MODE
        and manifest.get("goal08b0_unlock_status") == GOAL08B0_READY
        and manifest.get("goal08b_target_status") in {GOAL08B_ELIGIBLE_STATUS, GOAL08B_IMPLEMENTED_STATUS}
        and manifest.get("goal08b_implemented_by_this_gate") is False
        and manifest.get("recommendation_diagnostics_rows_generated") is False
        and manifest.get("recommendation_rows_generated") is False
        and manifest.get("downstream_stages_unlocked_by_this_gate") is False
    )


def _goal08a_false_boundary_keys() -> list[str]:
    return [
        "recommendation_rows_generated",
        "buy_sell_hold_outputs_generated",
        "target_prices_generated",
        "position_sizing_generated",
        "portfolio_construction_generated",
        "dashboard_generated",
        "paper_trading_enabled",
        "live_trading_enabled",
        "broker_integration_enabled",
        "production_model_behavior_created",
        "database_writes_created",
        "backtests_run",
        "factor_mining_outputs_created",
        "dqn_rl_outputs_created",
        "actionable_outputs_generated",
    ]


def _storage_false_boundary_keys() -> list[str]:
    return [
        "source_coverage_expanded",
        "symbol_coverage_expanded",
        "full_market_fetch_performed",
        "live_data_fetch_performed",
        "raw_provider_payloads_committed",
        "duckdb_or_parquet_files_committed",
        "recommendation_rows_generated",
        "buy_sell_hold_outputs_generated",
        "position_sizing_generated",
        "portfolio_construction_generated",
        "dashboard_generated",
        "paper_trading_enabled",
        "live_trading_enabled",
        "broker_integration_enabled",
        "production_model_behavior_created",
        "database_writes_created",
        "backtests_run",
        "factor_mining_outputs_created",
        "dqn_rl_outputs_created",
        "workflow_downstream_unlocked",
    ]


def _report_pass_or_warn(text: str, prefix: str) -> bool:
    return f"{prefix} {PASS}" in text or f"{prefix} {PASS_WITH_WARNINGS}" in text


def _forbidden_output_dirs_present(root: Path) -> list[str]:
    return [path for path in FORBIDDEN_OUTPUT_DIRS if (root / path).exists()]


def _forbidden_recommendation_row_outputs(root: Path) -> list[str]:
    output_root = root / "outputs"
    if not output_root.exists():
        return []
    matches: list[str] = []
    for path in output_root.rglob("*.csv"):
        rel = path.relative_to(root).as_posix()
        lower = rel.lower()
        if lower.startswith("outputs/audits/"):
            continue
        if rel == GOAL08B_DIAGNOSTIC_PATH:
            continue
        if lower.startswith("outputs/diagnostics/") and not any(token in lower for token in ["goal08b", "recommendation"]):
            continue
        if any(
            token in lower
            for token in [
                "goal08b",
                "recommendation",
                "position_size",
                "portfolio_weight",
                "target_price",
                "buy_sell_hold",
            ]
        ):
            matches.append(rel)
    return sorted(set(matches))


def _tracked_forbidden_files(root: Path) -> list[str]:
    try:
        result = subprocess.run(["git", "ls-files"], cwd=root, text=True, capture_output=True, check=True)
        tracked = result.stdout.splitlines()
    except Exception:  # pragma: no cover - fallback for non-git contexts
        tracked = [path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()]
    matches: list[str] = []
    for rel in tracked:
        lowered = rel.lower()
        suffix = Path(lowered).suffix
        if lowered.endswith(".csv.gz") or suffix in FORBIDDEN_TRACKED_SUFFIXES:
            matches.append(rel)
            continue
        if any(marker in lowered for marker in LOCAL_LAKE_PATH_MARKERS):
            matches.append(rel)
    return sorted(set(matches))


def _local_lake_paths_present(root: Path) -> list[str]:
    present: list[str] = []
    for rel in ["data/raw", "data/bundles", "data/lake", "data/metadata", "data/exports", "local_data", "local_data_lake"]:
        if (root / rel).exists():
            present.append(rel)
    return present


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

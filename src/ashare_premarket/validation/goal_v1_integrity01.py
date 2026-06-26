from __future__ import annotations

import subprocess
from pathlib import Path

from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import preserve_later_review_only_capabilities, preserve_later_review_only_workflow_states
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-V1-INTEGRITY-01"
GOAL_NAME = "GOAL-V1-INTEGRITY-01-END-TO-END-ARTIFACT-LINEAGE-AND-STRUCTURE-GATE"
MODE = "infrastructure_integrity_only"
WORKFLOW_ID = "goal_v1_integrity01_artifact_lineage_structure_gate"
GOAL091_WORKFLOW_ID = "goal091_position_band_warning_dashboard_readiness_gate"
DASHBOARD_WORKFLOW_ID = "dashboard_daily_report"
ALLOWED_NEXT_ACTION = "request_explicit_goal_dashboard00_contract_design_gate"
DASHBOARD_LOCKED_NEXT = "remain_locked_until_explicit_goal_dashboard00_contract_design_gate"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

CONFIG_PATH = "configs/validation/goal_v1_integrity01_artifact_lineage_contract.yaml"
DOC_PATH = "docs/validation/GOAL_V1_INTEGRITY01_ARTIFACT_LINEAGE_STRUCTURE_GATE.md"
REPORT_PATH = "outputs/audits/goal_v1_integrity01_artifact_lineage_structure_report.md"
MANIFEST_PATH = "outputs/audits/goal_v1_integrity01_artifact_lineage_structure_manifest.json"
AUDIT_PATH = "outputs/audits/goal_v1_integrity01_artifact_lineage_structure_audit.md"

WORKFLOW_PRODUCES_ARTIFACTS = ";".join([CONFIG_PATH, DOC_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH])
WORKFLOW_PRIMARY_DOCS = f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md"
WORKFLOW_PRIMARY_SCRIPTS = "scripts/run_goal_v1_integrity01_artifact_lineage_structure_gate.py;scripts/audit_goal_v1_integrity01_artifact_lineage_structure_gate.py"
WORKFLOW_PRIMARY_OUTPUTS = f"{REPORT_PATH};{MANIFEST_PATH};{AUDIT_PATH}"
WORKFLOW_NOTES = "Infrastructure-only V1 artifact-lineage and structure integrity gate; no dashboard files, new diagnostic rows, trading, production, backtest, factor-mining, broker, local-lake, or DQN/RL output."

GOAL07B_ROWS_PATH = "outputs/risk_overlay/goal07b_review_only_risk_overlay.csv"
GOAL07B_REPORT_PATH = "outputs/audits/goal07b_risk_overlay_calculation_report.md"
GOAL07B_MANIFEST_PATH = "outputs/audits/goal07b_risk_overlay_calculation_manifest.json"
GOAL07B_AUDIT_PATH = "outputs/audits/goal07b_risk_overlay_calculation_audit.md"
GOAL08B_ROWS_PATH = "outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv"
GOAL08B_REPORT_PATH = "outputs/audits/goal08b_recommendation_diagnostics_report.md"
GOAL08B_MANIFEST_PATH = "outputs/audits/goal08b_recommendation_diagnostics_manifest.json"
GOAL08B_AUDIT_PATH = "outputs/audits/goal08b_recommendation_diagnostics_audit.md"
GOAL09_ROWS_PATH = "outputs/position/goal09_review_only_position_band_diagnostics.csv"
GOAL09_REPORT_PATH = "outputs/audits/goal09_position_band_diagnostics_report.md"
GOAL09_MANIFEST_PATH = "outputs/audits/goal09_position_band_diagnostics_manifest.json"
GOAL09_AUDIT_PATH = "outputs/audits/goal09_position_band_diagnostics_audit.md"
GOAL091_POLICY_PATH = "configs/dashboard/goal091_dashboard_readiness_warning_policy.yaml"
GOAL091_REPORT_PATH = "outputs/audits/goal091_dashboard_readiness_report.md"
GOAL091_MANIFEST_PATH = "outputs/audits/goal091_dashboard_readiness_manifest.json"
GOAL091_AUDIT_PATH = "outputs/audits/goal091_dashboard_readiness_audit.md"

CANONICAL_CHAIN = [
    {
        "goal_id": "GOAL-07B",
        "workflow_id": "goal07b_risk_overlay_calculation",
        "output_path": GOAL07B_ROWS_PATH,
        "report_path": GOAL07B_REPORT_PATH,
        "manifest_path": GOAL07B_MANIFEST_PATH,
        "audit_path": GOAL07B_AUDIT_PATH,
        "mode": "review_only",
        "row_count_manifest_key": "risk_overlay_row_count",
        "report_prefix": "GOAL-07B Risk Overlay Calculation Prototype:",
    },
    {
        "goal_id": "GOAL-08B",
        "workflow_id": "goal08b_recommendation_review_only_prototype",
        "output_path": GOAL08B_ROWS_PATH,
        "report_path": GOAL08B_REPORT_PATH,
        "manifest_path": GOAL08B_MANIFEST_PATH,
        "audit_path": GOAL08B_AUDIT_PATH,
        "mode": "review_only",
        "row_count_manifest_key": "diagnostic_row_count",
        "report_prefix": "GOAL-08B Recommendation Diagnostics Prototype:",
    },
    {
        "goal_id": "GOAL-09",
        "workflow_id": "position_band_recommendation",
        "output_path": GOAL09_ROWS_PATH,
        "report_path": GOAL09_REPORT_PATH,
        "manifest_path": GOAL09_MANIFEST_PATH,
        "audit_path": GOAL09_AUDIT_PATH,
        "mode": "review_only",
        "row_count_manifest_key": "position_band_diagnostic_row_count",
        "report_prefix": "GOAL-09 Position-Band Diagnostics Prototype:",
    },
    {
        "goal_id": "GOAL-09.1",
        "workflow_id": GOAL091_WORKFLOW_ID,
        "output_path": GOAL091_POLICY_PATH,
        "report_path": GOAL091_REPORT_PATH,
        "manifest_path": GOAL091_MANIFEST_PATH,
        "audit_path": GOAL091_AUDIT_PATH,
        "mode": "review_readiness_only",
        "row_count_manifest_key": "goal09_row_count",
        "report_prefix": "GOAL-09.1 Position-Band Warning Review and Dashboard Readiness Gate:",
    },
]

ALLOWED_STATUSES = {
    "implemented_active",
    "implemented_review_only",
    "implemented_design_only",
    "implemented_infrastructure_only",
    "locked_future",
    "deleted_from_active_mainline",
    "planned_locked",
}

EXPECTED_WARNING_CLASSIFICATION = {
    "calibration_not_reliable_for_thresholding": "dashboard_blocking_banner",
    "target_horizon_calibration_warning": "dashboard_blocking_banner",
    "weak_target_horizon_rank_signal": "dashboard_blocking_banner",
    "selected_score_variant_weak_rank_signal": "dashboard_blocking_banner",
    "single_provider_mode_akshare_direct": "provider_concentration_banner",
    "provider_source_concentration_disclosed": "provider_concentration_banner",
    "feature_sign_instability_bounded": "row_level_and_summary_warning",
}

FORBIDDEN_FIELD_NAMES = {
    "buy",
    "sell",
    "hold",
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
    "buy_sell_hold",
    "capital_allocation",
}

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

FORBIDDEN_DASHBOARD_INPUT_SOURCES = [
    "data/raw",
    "data/bundles",
    "data/lake",
    "data/metadata",
    "data/exports",
    "outputs/local",
    "notebooks",
    ".pytest_cache",
]

FILESYSTEM_FORBIDDEN_DASHBOARD_INPUT_SOURCES = [
    path for path in FORBIDDEN_DASHBOARD_INPUT_SOURCES if path not in {"outputs/local", ".pytest_cache"}
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
    "new_risk_rows_generated",
    "new_recommendation_rows_generated",
    "new_position_rows_generated",
    "diagnostic_output_schemas_changed",
    "actual_position_sizing_generated",
    "portfolio_construction_generated",
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
    "large_refactor_performed",
    "downstream_execution_unlocked_by_this_goal",
]

DOC_CONSISTENCY_PATHS = [
    "README.md",
    "PROJECT_STATE.md",
    "CODEX.md",
    "AGENTS.md",
    "ROADMAP.md",
    "docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
    "docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md",
    "docs/architecture/ACTIVE_WORKFLOW_THROUGH_GOAL06B.md",
    "docs/architecture/CANONICAL_WORKFLOW_STATUS.md",
]

DOC_STALE_MARKERS = [
    "GOAL-09 remains locked_future",
    "GOAL-09 remains `locked_future`",
    "GOAL-09 is locked_future",
    "GOAL-09 is `locked_future`",
    "GOAL-09 is not implemented",
    "Dashboard / Daily Report UI is implemented",
    "Dashboard / Daily Report UI implemented",
    "dashboard output is implemented",
    "dashboard outputs are implemented",
]


def run_goal_v1_integrity01_artifact_lineage_structure_gate(root: Path) -> bool:
    result = evaluate_goal_v1_integrity01_artifact_lineage_structure_gate(root)
    _write_config(root, result)
    _write_outputs(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal_v1_integrity01_artifact_lineage_structure_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal_v1_integrity01_artifact_lineage_structure_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    config = _read_json(root / CONFIG_PATH)
    workflow = _workflow_rows(root)
    recheck = evaluate_goal_v1_integrity01_artifact_lineage_structure_gate(root)
    failures: list[str] = []

    if not _report_pass_or_warn(report, "GOAL-V1-INTEGRITY-01 Artifact Lineage and Structure Gate:"):
        failures.append("goal_v1_integrity01_report_not_pass_or_warn")
    if recheck["status"] == BLOCKED:
        failures.extend(f"recheck:{failure}" for failure in recheck["failures"])
    if manifest.get("goal") != GOAL_NAME:
        failures.append("manifest_goal_invalid")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_invalid")
    for key in [
        "canonical_artifact_lineage_verified",
        "source_of_truth_docs_synchronized",
        "workflow_status_synchronized",
        "fresh_clone_validation_expectations_include_v1_chain",
        "future_dashboard_may_read_only_canonical_outputs_and_audit_metadata",
        "future_dashboard_forbidden_source_inputs_blocked",
        "forbidden_field_names_absent_from_diagnostic_outputs",
        "forbidden_field_names_absent_from_future_dashboard_required_fields",
        "goal08b_rows_never_actionable",
        "goal09_rows_never_actionable",
        "goal091_warning_classifications_available",
        "heavy_artifact_hygiene_enforced",
        "dashboard_daily_report_locked_future",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"manifest_{key}_not_false")
    if manifest.get("goal_dashboard00_request_status") != "eligible_for_explicit_design_only_contract_gate":
        failures.append("manifest_goal_dashboard00_request_status_invalid")
    if manifest.get("dashboard_daily_report_status_after_goal_v1_integrity01") != "locked_future":
        failures.append("manifest_dashboard_status_invalid")
    if manifest.get("warning_classification") != EXPECTED_WARNING_CLASSIFICATION:
        failures.append("manifest_warning_classification_invalid")
    if config.get("canonical_artifact_lineage") != _contract_canonical_artifact_lineage():
        failures.append("config_canonical_artifact_lineage_invalid")
    gate_row = workflow.get(WORKFLOW_ID, {})
    if gate_row.get("status") != "implemented_infrastructure_only":
        failures.append("goal_v1_integrity01_workflow_not_implemented_infrastructure_only")
    if gate_row.get("implemented_in_repo") != "true":
        failures.append("goal_v1_integrity01_workflow_not_marked_implemented")
    if gate_row.get("allowed_next_action") != ALLOWED_NEXT_ACTION:
        failures.append("goal_v1_integrity01_allowed_next_invalid")
    if gate_row.get("depends_on") != GOAL091_WORKFLOW_ID:
        failures.append("goal_v1_integrity01_depends_on_invalid")
    dashboard = workflow.get(DASHBOARD_WORKFLOW_ID, {})
    if dashboard.get("status") != "locked_future":
        failures.append("dashboard_workflow_not_locked_future")
    if dashboard.get("implemented_in_repo") != "false":
        failures.append("dashboard_workflow_marked_implemented")
    if dashboard.get("depends_on") != WORKFLOW_ID:
        failures.append("dashboard_workflow_does_not_depend_on_goal_v1_integrity01")

    status = PASS if not failures else BLOCKED
    write_text(
        root / AUDIT_PATH,
        "\n".join(
            [
                "# GOAL-V1-INTEGRITY-01 Artifact Lineage and Structure Audit",
                "",
                f"Status: `{status}`",
                "",
                f"Workflow status: `{gate_row.get('status', 'missing')}`",
                f"Dashboard workflow status: `{dashboard.get('status', 'missing')}`",
                "GOAL-DASHBOARD-00 may still be explicitly requested next as a future design-only contract/layout gate: `true`",
                "Dashboard outputs generated: `false`",
                "New risk/recommendation/position rows generated: `false`",
                "Actual position sizing, portfolio weights, target weights, order quantities, buy/sell/hold actions, target prices, trading, production, backtest, factor-mining, broker, local-lake, and DQN/RL outputs generated: `false`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == PASS


def evaluate_goal_v1_integrity01_artifact_lineage_structure_gate(root: Path) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    workflow_rows = _read_csv(root / "configs/project/workflow_status.csv")
    workflow = {row.get("workflow_id", ""): row for row in workflow_rows}
    risk_rows = _read_csv(root / GOAL07B_ROWS_PATH)
    recommendation_rows = _read_csv(root / GOAL08B_ROWS_PATH)
    position_rows = _read_csv(root / GOAL09_ROWS_PATH)
    goal091_manifest = _read_json(root / GOAL091_MANIFEST_PATH)
    goal091_policy = _read_json(root / GOAL091_POLICY_PATH)

    failures.extend(_validate_canonical_artifacts(root))
    failures.extend(_validate_workflow_status(workflow_rows, workflow))
    lineage_failures, lineage = _validate_row_lineage(risk_rows, recommendation_rows, position_rows)
    failures.extend(lineage_failures)
    failures.extend(_validate_goal07b_rows(risk_rows))
    failures.extend(_validate_goal08b_rows(recommendation_rows))
    failures.extend(_validate_goal09_rows(position_rows))
    failures.extend(_validate_goal091_readiness(goal091_manifest, goal091_policy))
    failures.extend(_validate_docs(root))
    failures.extend(_validate_heavy_artifact_hygiene(root))

    warning_codes = sorted(goal091_manifest.get("warning_classification", EXPECTED_WARNING_CLASSIFICATION))
    if warning_codes:
        warnings.extend(warning_codes)
    status = BLOCKED if failures else PASS_WITH_WARNINGS if warnings else PASS
    manifest = _manifest(status, failures, warnings, lineage, risk_rows, recommendation_rows, position_rows, goal091_manifest)
    return {
        "status": status,
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "lineage": lineage,
        "manifest": manifest,
    }


def goal_v1_integrity01_valid_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        _report_pass_or_warn(report, "GOAL-V1-INTEGRITY-01 Artifact Lineage and Structure Gate:")
        and "Status: `PASS`" in audit
        and manifest.get("goal") == GOAL_NAME
        and manifest.get("mode") == MODE
        and manifest.get("canonical_artifact_lineage_verified") is True
        and manifest.get("dashboard_daily_report_status_after_goal_v1_integrity01") == "locked_future"
        and manifest.get("dashboard_outputs_generated") is False
        and manifest.get("new_risk_rows_generated") is False
        and manifest.get("new_recommendation_rows_generated") is False
        and manifest.get("new_position_rows_generated") is False
        and manifest.get("goal_dashboard00_request_status") == "eligible_for_explicit_design_only_contract_gate"
    )


def goal_v1_integrity01_implemented_workflow_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-V1-INTEGRITY-01 Artifact Lineage and Structure Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_infrastructure_only",
        "current_repo_role": "infrastructure_only_artifact_lineage_integrity_gate",
        "implemented_in_repo": "true",
        "allowed_next_action": ALLOWED_NEXT_ACTION,
        "depends_on": GOAL091_WORKFLOW_ID,
        "produces_artifacts": WORKFLOW_PRODUCES_ARTIFACTS,
        "primary_docs": WORKFLOW_PRIMARY_DOCS,
        "primary_scripts": WORKFLOW_PRIMARY_SCRIPTS,
        "primary_outputs": WORKFLOW_PRIMARY_OUTPUTS,
        "promotion_rule": "implemented_infrastructure_only_after_goal_v1_integrity01_pass_with_warnings",
        "notes": WORKFLOW_NOTES,
    }


def _validate_canonical_artifacts(root: Path) -> list[str]:
    failures: list[str] = []
    for item in CANONICAL_CHAIN:
        output_path = str(item["output_path"])
        report_path = str(item["report_path"])
        manifest_path = str(item["manifest_path"])
        audit_path = str(item["audit_path"])
        for rel in [output_path, report_path, manifest_path, audit_path]:
            if not (root / rel).exists():
                failures.append(f"canonical_artifact_missing:{rel}")
        report = _read(root / report_path)
        manifest = _read_json(root / manifest_path)
        audit = _read(root / audit_path)
        if not _report_pass_or_warn(report, str(item["report_prefix"])):
            failures.append(f"{item['goal_id']}_report_not_pass_or_warn")
        if manifest.get("mode") != item["mode"]:
            failures.append(f"{item['goal_id']}_manifest_mode_invalid")
        if "Status: `PASS`" not in audit:
            failures.append(f"{item['goal_id']}_audit_not_pass")
    return failures


def _validate_workflow_status(rows: list[dict[str, str]], workflow: dict[str, dict[str, str]]) -> list[str]:
    failures: list[str] = []
    if not rows:
        return ["workflow_status_missing_or_empty"]
    for row in rows:
        if row.get("status") not in ALLOWED_STATUSES:
            failures.append(f"workflow_status_vocabulary_invalid:{row.get('workflow_id')}:{row.get('status')}")
    expected = {
        "goal07b_risk_overlay_calculation": "implemented_review_only",
        "goal08a_recommendation_contract_design_gate": "implemented_design_only",
        "goal_storage01_local_research_lake_hardening_gate": "implemented_infrastructure_only",
        "goal08b0_recommendation_review_only_unlock_gate": "implemented_review_only",
        "goal08b_recommendation_review_only_prototype": "implemented_review_only",
        "goal090_position_band_review_only_unlock_gate": "implemented_review_only",
        "position_band_recommendation": "implemented_review_only",
        GOAL091_WORKFLOW_ID: "implemented_review_only",
    }
    for workflow_id, expected_status in expected.items():
        row = workflow.get(workflow_id, {})
        if row.get("status") != expected_status:
            failures.append(f"workflow_status_mismatch:{workflow_id}:{row.get('status')}")
        if row.get("implemented_in_repo") != "true":
            failures.append(f"workflow_implemented_flag_invalid:{workflow_id}")
    dashboard = workflow.get(DASHBOARD_WORKFLOW_ID, {})
    if dashboard.get("status") != "locked_future":
        failures.append("dashboard_daily_report_not_locked_future")
    if dashboard.get("implemented_in_repo") != "false":
        failures.append("dashboard_daily_report_marked_implemented")
    if workflow.get("dqn_rl_mainline", {}).get("status") != "deleted_from_active_mainline":
        failures.append("dqn_rl_mainline_not_deleted_from_active_mainline")
    if workflow.get("v2_factor_research_upgrade", {}).get("status") != "planned_locked":
        failures.append("v2_factor_research_not_planned_locked")
    return failures


def _validate_row_lineage(
    risk_rows: list[dict[str, str]],
    recommendation_rows: list[dict[str, str]],
    position_rows: list[dict[str, str]],
) -> tuple[list[str], dict[str, object]]:
    failures: list[str] = []
    risk_keys = _key_set(risk_rows)
    recommendation_keys = _key_set(recommendation_rows)
    position_keys = _key_set(position_rows)
    if not risk_rows:
        failures.append("goal07b_rows_missing")
    if not recommendation_rows:
        failures.append("goal08b_rows_missing")
    if not position_rows:
        failures.append("goal09_rows_missing")
    if len(risk_rows) != len(risk_keys):
        failures.append("goal07b_rows_not_unique_trade_date_symbol")
    if len(recommendation_rows) != len(recommendation_keys):
        failures.append("goal08b_rows_not_unique_trade_date_symbol")
    if len(position_rows) != len(position_keys):
        failures.append("goal09_rows_not_unique_trade_date_symbol")
    if risk_keys != recommendation_keys:
        failures.append("goal07b_goal08b_trade_date_symbol_keys_mismatch")
    if recommendation_keys != position_keys:
        failures.append("goal08b_goal09_trade_date_symbol_keys_mismatch")
    return failures, {
        "risk_overlay_rows": len(risk_rows),
        "recommendation_diagnostics_rows": len(recommendation_rows),
        "position_band_diagnostics_rows": len(position_rows),
        "trade_date_symbol_keys_match": not failures and bool(risk_keys),
        "grain": "trade_date + symbol",
        "source_order": ["GOAL-07B", "GOAL-08B", "GOAL-09", "GOAL-09.1"],
    }


def _validate_goal07b_rows(rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    fields = set(rows[0].keys()) if rows else set()
    failures.extend(_forbidden_field_failures("goal07b", fields))
    for index, row in enumerate(rows):
        if row.get("mode") != "review_only":
            failures.append(f"goal07b_row_{index}_mode_not_review_only")
        if row.get("non_actionable") != "true":
            failures.append(f"goal07b_row_{index}_not_non_actionable")
        for flag in [
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
            if row.get(flag) != "false":
                failures.append(f"goal07b_row_{index}_{flag}_not_false")
    return failures


def _validate_goal08b_rows(rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    fields = set(rows[0].keys()) if rows else set()
    failures.extend(_forbidden_field_failures("goal08b", fields))
    for index, row in enumerate(rows):
        if row.get("source_goal") != "GOAL-07B":
            failures.append(f"goal08b_row_{index}_source_goal_invalid")
        if row.get("source_goal07b_mode") != "review_only":
            failures.append(f"goal08b_row_{index}_source_goal07b_mode_invalid")
        if row.get("diagnostic_mode") != "review_only":
            failures.append(f"goal08b_row_{index}_diagnostic_mode_invalid")
        if row.get("actionability_status") != "never_actionable":
            failures.append(f"goal08b_row_{index}_actionability_status_invalid")
        if row.get("actionability_blocked") != "true":
            failures.append(f"goal08b_row_{index}_actionability_blocked_invalid")
        if not row.get("non_actionable_disclaimer"):
            failures.append(f"goal08b_row_{index}_non_actionable_disclaimer_missing")
    return failures


def _validate_goal09_rows(rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    fields = set(rows[0].keys()) if rows else set()
    failures.extend(_forbidden_field_failures("goal09", fields))
    for index, row in enumerate(rows):
        if row.get("source_goal") != "GOAL-08B":
            failures.append(f"goal09_row_{index}_source_goal_invalid")
        if row.get("source_goal08b_mode") != "review_only":
            failures.append(f"goal09_row_{index}_source_goal08b_mode_invalid")
        if row.get("source_goal07b_mode") != "review_only":
            failures.append(f"goal09_row_{index}_source_goal07b_mode_invalid")
        if row.get("diagnostic_mode") != "review_only":
            failures.append(f"goal09_row_{index}_diagnostic_mode_invalid")
        if row.get("recommendation_actionability_status") != "never_actionable":
            failures.append(f"goal09_row_{index}_recommendation_actionability_invalid")
        if row.get("position_actionability_status") != "never_actionable":
            failures.append(f"goal09_row_{index}_position_actionability_invalid")
        if row.get("position_actionability_blocked") != "true":
            failures.append(f"goal09_row_{index}_position_actionability_blocked_invalid")
        if not row.get("non_actionable_disclaimer"):
            failures.append(f"goal09_row_{index}_non_actionable_disclaimer_missing")
    return failures


def _validate_goal091_readiness(manifest: dict[str, object], policy: dict[str, object]) -> list[str]:
    failures: list[str] = []
    if manifest.get("mode") != "review_readiness_only":
        failures.append("goal091_manifest_mode_invalid")
    if manifest.get("dashboard_daily_report_status_after_goal091") != "locked_future":
        failures.append("goal091_dashboard_not_locked_future")
    if manifest.get("future_dashboard_contract_design_gate_may_be_requested") is not True:
        failures.append("goal091_dashboard00_not_eligible")
    if manifest.get("warning_classification") != EXPECTED_WARNING_CLASSIFICATION:
        failures.append("goal091_warning_classification_invalid")
    if policy.get("warning_classification") != EXPECTED_WARNING_CLASSIFICATION:
        failures.append("goal091_policy_warning_classification_invalid")
    if set(manifest.get("row_level_warning_codes_required", [])) != set(EXPECTED_WARNING_CLASSIFICATION):
        failures.append("goal091_row_level_warning_codes_invalid")
    if set(manifest.get("warning_codes_preventing_action_oriented_display", [])) != set(EXPECTED_WARNING_CLASSIFICATION):
        failures.append("goal091_action_display_warning_codes_invalid")
    required_contracts = manifest.get("future_dashboard_required_input_contracts", {})
    if not isinstance(required_contracts, dict):
        failures.append("goal091_future_dashboard_required_input_contracts_missing")
    else:
        for contract_name, contract in required_contracts.items():
            if not isinstance(contract, dict):
                failures.append(f"goal091_contract_invalid:{contract_name}")
                continue
            required_fields = set(contract.get("required_fields", []))
            overlap = required_fields & FORBIDDEN_FIELD_NAMES
            if overlap:
                failures.append(f"goal091_future_contract_forbidden_required_fields:{contract_name}:{';'.join(sorted(overlap))}")
            path = contract.get("path")
            if isinstance(path, str) and path not in _allowed_future_dashboard_paths():
                failures.append(f"goal091_future_contract_unapproved_path:{path}")
    forbidden_fields = set(manifest.get("future_dashboard_forbidden_fields", []))
    if not FORBIDDEN_FIELD_NAMES.issubset(forbidden_fields):
        failures.append("goal091_future_dashboard_forbidden_field_inventory_incomplete")
    return failures


def _validate_docs(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in DOC_CONSISTENCY_PATHS:
        text = _read(root / rel)
        if not text:
            failures.append(f"source_of_truth_doc_missing:{rel}")
            continue
        for stale in DOC_STALE_MARKERS:
            if stale in text:
                failures.append(f"stale_doc_marker:{rel}:{stale}")

    required_top_level_markers = {
        "README.md": [
            "GOAL-V1-INTEGRITY-01",
            "GOAL-07B",
            "GOAL-08B",
            "GOAL-09",
            "GOAL-09.1",
            "Dashboard / Daily Report UI remains `locked_future`",
        ],
        "PROJECT_STATE.md": [
            "GOAL-V1-INTEGRITY-01",
            "GOAL-09.1",
            "Dashboard / Daily Report UI remains `locked_future`",
        ],
        "ROADMAP.md": [
            "GOAL-V1-INTEGRITY-01",
            "GOAL-DASHBOARD-00",
            "locked_future",
        ],
    }
    for rel, required_current_markers in required_top_level_markers.items():
        text = _read(root / rel)
        for marker in required_current_markers:
            if marker not in text:
                failures.append(f"source_of_truth_doc_missing_marker:{rel}:{marker}")
    return failures


def _validate_heavy_artifact_hygiene(root: Path) -> list[str]:
    failures: list[str] = []
    failures.extend(f"forbidden_output_dir_present:{path}" for path in _forbidden_output_dirs_present(root))
    failures.extend(f"forbidden_dashboard_input_source_present:{path}" for path in _forbidden_dashboard_input_sources_present(root))
    failures.extend(f"local_lake_path_present:{path}" for path in _local_lake_paths_present(root))
    failures.extend(f"forbidden_tracked_artifact:{path}" for path in _tracked_forbidden_files(root))
    return failures


def _manifest(
    status: str,
    failures: list[str],
    warnings: list[str],
    lineage: dict[str, object],
    risk_rows: list[dict[str, str]],
    recommendation_rows: list[dict[str, str]],
    position_rows: list[dict[str, str]],
    goal091_manifest: dict[str, object],
) -> dict[str, object]:
    warning_classification = goal091_manifest.get("warning_classification", EXPECTED_WARNING_CLASSIFICATION)
    canonical_outputs = _contract_canonical_artifact_lineage()
    return {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "status": status,
        "mode": MODE,
        "allowed_next_action": ALLOWED_NEXT_ACTION if status != BLOCKED else "repair_goal_v1_integrity01_blockers",
        "canonical_artifact_lineage": canonical_outputs,
        "canonical_artifact_lineage_verified": status != BLOCKED,
        "artifact_lineage_summary": lineage,
        "goal07b_row_count": len(risk_rows),
        "goal08b_row_count": len(recommendation_rows),
        "goal09_row_count": len(position_rows),
        "goal08b_actionability_status_values": sorted({row.get("actionability_status", "") for row in recommendation_rows}),
        "goal09_position_actionability_status_values": sorted({row.get("position_actionability_status", "") for row in position_rows}),
        "workflow_status_synchronized": status != BLOCKED,
        "source_of_truth_docs_synchronized": status != BLOCKED,
        "status_vocabulary_allowed": sorted(ALLOWED_STATUSES),
        "fresh_clone_validation_expectations_include_v1_chain": True,
        "future_dashboard_may_read_only_canonical_outputs_and_audit_metadata": True,
        "future_dashboard_allowed_inputs": _allowed_future_dashboard_paths(),
        "future_dashboard_forbidden_source_inputs_blocked": True,
        "future_dashboard_forbidden_source_inputs": FORBIDDEN_DASHBOARD_INPUT_SOURCES,
        "forbidden_field_names": sorted(FORBIDDEN_FIELD_NAMES),
        "forbidden_field_names_absent_from_diagnostic_outputs": True,
        "forbidden_field_names_absent_from_future_dashboard_required_fields": True,
        "goal08b_rows_never_actionable": sorted({row.get("actionability_status", "") for row in recommendation_rows}) == ["never_actionable"],
        "goal09_rows_never_actionable": sorted({row.get("position_actionability_status", "") for row in position_rows}) == ["never_actionable"],
        "goal091_warning_classifications_available": warning_classification == EXPECTED_WARNING_CLASSIFICATION,
        "warning_classification": warning_classification,
        "heavy_artifact_hygiene_enforced": status != BLOCKED,
        "dashboard_daily_report_locked_future": True,
        "dashboard_daily_report_status_after_goal_v1_integrity01": "locked_future",
        "goal_dashboard00_request_status": "eligible_for_explicit_design_only_contract_gate" if status != BLOCKED else "blocked",
        "input_artifacts": [
            GOAL07B_ROWS_PATH,
            GOAL07B_REPORT_PATH,
            GOAL07B_MANIFEST_PATH,
            GOAL07B_AUDIT_PATH,
            GOAL08B_ROWS_PATH,
            GOAL08B_REPORT_PATH,
            GOAL08B_MANIFEST_PATH,
            GOAL08B_AUDIT_PATH,
            GOAL09_ROWS_PATH,
            GOAL09_REPORT_PATH,
            GOAL09_MANIFEST_PATH,
            GOAL09_AUDIT_PATH,
            GOAL091_POLICY_PATH,
            GOAL091_REPORT_PATH,
            GOAL091_MANIFEST_PATH,
            GOAL091_AUDIT_PATH,
        ],
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        **{key: False for key in FALSE_BOUNDARY_KEYS},
    }


def _write_config(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    write_json(
        root / CONFIG_PATH,
        {
            "goal": GOAL_NAME,
            "mode": MODE,
            "status": result["status"],
            "canonical_artifact_lineage": _contract_canonical_artifact_lineage(),
            "status_vocabulary_allowed": sorted(ALLOWED_STATUSES),
            "future_dashboard_allowed_inputs": _allowed_future_dashboard_paths(),
            "future_dashboard_forbidden_source_inputs": FORBIDDEN_DASHBOARD_INPUT_SOURCES,
            "forbidden_field_names": sorted(FORBIDDEN_FIELD_NAMES),
            "warning_classification_required": EXPECTED_WARNING_CLASSIFICATION,
            "dashboard_daily_report_status_after_goal_v1_integrity01": manifest["dashboard_daily_report_status_after_goal_v1_integrity01"],
            "goal_dashboard00_request_status": manifest["goal_dashboard00_request_status"],
            "forbidden_execution_output_constraints": {key: "must_remain_false" for key in FALSE_BOUNDARY_KEYS},
        },
    )


def _write_outputs(root: Path, result: dict[str, object]) -> None:
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_report(root, result)
    _write_doc(root, result)


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    lineage = manifest["artifact_lineage_summary"]
    write_text(
        root / REPORT_PATH,
        "\n".join(
            [
                "# GOAL-V1-INTEGRITY-01 Artifact Lineage and Structure Gate",
                "",
                f"GOAL-V1-INTEGRITY-01 Artifact Lineage and Structure Gate: {result['status']}",
                f"Mode: `{MODE}`",
                "",
                "## Artifact Lineage",
                f"- GOAL-07B risk overlay diagnostics rows: `{lineage['risk_overlay_rows']}`",
                f"- GOAL-08B recommendation diagnostics rows: `{lineage['recommendation_diagnostics_rows']}`",
                f"- GOAL-09 position-band diagnostics rows: `{lineage['position_band_diagnostics_rows']}`",
                f"- Trade-date plus symbol keys match across canonical diagnostic outputs: `{str(lineage['trade_date_symbol_keys_match']).lower()}`",
                "- GOAL-09.1 dashboard-readiness warning policy and audit evidence are present.",
                "",
                "## Source Of Truth",
                "- `workflow_status.csv`, README, PROJECT_STATE, ROADMAP, CODEX, AGENTS, and architecture docs are checked for current-state consistency.",
                "- Dashboard / Daily Report UI remains `locked_future`.",
                "- GOAL-DASHBOARD-00 may still be explicitly requested next only as a future design/contract gate.",
                "",
                "## Safety",
                "- Future dashboard inputs are limited to canonical review-only diagnostics and audit metadata.",
                "- No dashboard output, HTML, Streamlit, frontend code, visual report, new risk row, new recommendation row, new position row, schema change, position sizing, portfolio weight, target weight, order quantity, buy/sell/hold action, target price, trading, production, backtest, factor-mining, broker, local-lake, or DQN/RL output was created.",
                "",
                "## Failures",
                *[f"- {failure}" for failure in result["failures"]],
                "",
                "## Warnings",
                *[f"- {warning}" for warning in result["warnings"]],
                "",
            ]
        ),
    )


def _write_doc(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    write_text(
        root / DOC_PATH,
        "\n".join(
            [
                "# GOAL-V1-INTEGRITY-01 Artifact Lineage and Structure Gate",
                "",
                f"Status: `{result['status']}`",
                "",
                "GOAL-V1-INTEGRITY-01 is an infrastructure-only integrity gate. It verifies that the V1 review-only chain from GOAL-07B risk diagnostics through GOAL-08B recommendation diagnostics, GOAL-09 position-band diagnostics, and GOAL-09.1 dashboard-readiness evidence is structurally complete and source-of-truth consistent.",
                "",
                "It does not implement a dashboard and does not generate dashboard output, HTML, Streamlit, frontend code, visual reports, new risk rows, new recommendation rows, new position rows, or execution artifacts.",
                "",
                "## Canonical Lineage",
                "",
                "- `outputs/risk_overlay/goal07b_review_only_risk_overlay.csv`",
                "- `outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv`",
                "- `outputs/position/goal09_review_only_position_band_diagnostics.csv`",
                "- `configs/dashboard/goal091_dashboard_readiness_warning_policy.yaml`",
                "",
                "Each canonical stage must have matching report, manifest, and audit evidence.",
                "",
                "## Dashboard Boundary",
                "",
                "- Dashboard / Daily Report UI remains `locked_future`.",
                "- GOAL-DASHBOARD-00 may be explicitly requested next only as a future design/contract gate.",
                "- Future dashboard inputs may read only canonical review-only diagnostics and audit metadata.",
                "- Future dashboard inputs must not read local lake files, raw provider payloads, cache files, notebooks, or uncommitted artifacts.",
                "- Future dashboard contracts must not require forbidden actionable field names.",
                "",
                f"GOAL-DASHBOARD-00 request status: `{manifest['goal_dashboard00_request_status']}`.",
                "",
            ]
        ),
    )


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys())
    by_id = {row["workflow_id"]: row for row in rows}
    patch = goal_v1_integrity01_implemented_workflow_patch()
    if result["status"] == BLOCKED:
        patch.update(
            {
                "status": "locked_future",
                "current_repo_role": "artifact_lineage_integrity_blocked",
                "implemented_in_repo": "false",
                "allowed_next_action": "repair_goal_v1_integrity01_blockers",
                "produces_artifacts": "",
                "primary_scripts": "",
                "primary_outputs": "",
                "promotion_rule": "locked_until_goal_v1_integrity01_passes",
                "notes": "GOAL-V1-INTEGRITY-01 is blocked; no dashboard contract design gate may be requested.",
            }
        )
    if WORKFLOW_ID in by_id:
        by_id[WORKFLOW_ID].update(patch)
    else:
        insert_at = next((index + 1 for index, item in enumerate(rows) if item["workflow_id"] == GOAL091_WORKFLOW_ID), len(rows))
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
                "notes": "Locked dashboard workflow; GOAL-V1-INTEGRITY-01 allows only a future explicit design-only contract/layout gate request and creates no dashboard outputs.",
            }
        )
    for workflow_id in [
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
    preserve_later_review_only_workflow_states(root, by_id)
    write_csv(path, rows, fields)


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    if not path.exists():
        return
    payload = read_json(path)
    payload[WORKFLOW_ID] = "implemented_infrastructure_only" if result["status"] != BLOCKED else False
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
    preserve_later_review_only_capabilities(root, payload)
    write_json(path, payload)


def _contract_canonical_artifact_lineage() -> list[dict[str, str]]:
    return [
        {
            "source_goal": str(item["goal_id"]),
            "workflow_id": str(item["workflow_id"]),
            "canonical_output": str(item["output_path"]),
            "report": str(item["report_path"]),
            "manifest": str(item["manifest_path"]),
            "audit": str(item["audit_path"]),
            "mode": str(item["mode"]),
        }
        for item in CANONICAL_CHAIN
    ]


def _allowed_future_dashboard_paths() -> list[str]:
    return [
        GOAL07B_ROWS_PATH,
        GOAL08B_ROWS_PATH,
        GOAL09_ROWS_PATH,
        GOAL091_POLICY_PATH,
        GOAL07B_REPORT_PATH,
        GOAL07B_MANIFEST_PATH,
        GOAL07B_AUDIT_PATH,
        GOAL08B_REPORT_PATH,
        GOAL08B_MANIFEST_PATH,
        GOAL08B_AUDIT_PATH,
        GOAL09_REPORT_PATH,
        GOAL09_MANIFEST_PATH,
        GOAL09_AUDIT_PATH,
        GOAL091_REPORT_PATH,
        GOAL091_MANIFEST_PATH,
        GOAL091_AUDIT_PATH,
        REPORT_PATH,
        MANIFEST_PATH,
        AUDIT_PATH,
    ]


def _forbidden_field_failures(label: str, fields: set[str]) -> list[str]:
    overlap = fields & FORBIDDEN_FIELD_NAMES
    return [f"{label}_forbidden_field_present:{field}" for field in sorted(overlap)]


def _key_set(rows: list[dict[str, str]]) -> set[tuple[str, str]]:
    return {(row.get("trade_date", ""), row.get("symbol", "")) for row in rows}


def _split_codes(value: str) -> list[str]:
    if not value or value == "none":
        return []
    return [item for item in str(value).split(";") if item and item != "none"]


def _report_pass_or_warn(text: str, prefix: str) -> bool:
    return f"{prefix} {PASS}" in text or f"{prefix} {PASS_WITH_WARNINGS}" in text


def _forbidden_output_dirs_present(root: Path) -> list[str]:
    return [path for path in FORBIDDEN_OUTPUT_DIRS if (root / path).exists()]


def _forbidden_dashboard_input_sources_present(root: Path) -> list[str]:
    return [path for path in FILESYSTEM_FORBIDDEN_DASHBOARD_INPUT_SOURCES if (root / path).exists()]


def _local_lake_paths_present(root: Path) -> list[str]:
    return [path for path in LOCAL_LAKE_PATHS if (root / path).exists()]


def _tracked_forbidden_files(root: Path) -> list[str]:
    try:
        result = subprocess.run(["git", "ls-files"], cwd=root, text=True, capture_output=True, check=True)
        tracked = result.stdout.splitlines()
    except Exception:  # pragma: no cover - fallback for non-git contexts
        tracked = [path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()]
    allowed = {
        GOAL07B_ROWS_PATH,
        GOAL08B_ROWS_PATH,
        GOAL09_ROWS_PATH,
        GOAL091_POLICY_PATH,
        CONFIG_PATH,
        DOC_PATH,
        REPORT_PATH,
        MANIFEST_PATH,
        AUDIT_PATH,
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

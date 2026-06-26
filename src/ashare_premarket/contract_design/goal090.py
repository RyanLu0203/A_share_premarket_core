from __future__ import annotations

import subprocess
from pathlib import Path

from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import preserve_later_review_only_capabilities, preserve_later_review_only_workflow_states
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-09.0"
GOAL_NAME = "GOAL-09.0-POSITION-BAND-REVIEW-ONLY-UNLOCK-GATE"
MODE = "review_only_unlock_gate"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

CONFIG_DIR = "configs/position"
DOC_DIR = "docs/position"
AUDIT_DIR = "outputs/audits"

POLICY_PATH = f"{CONFIG_DIR}/goal090_position_band_review_only_unlock_policy.yaml"
DOC_PATH = f"{DOC_DIR}/GOAL090_POSITION_BAND_REVIEW_ONLY_UNLOCK_GATE.md"
REPORT_PATH = f"{AUDIT_DIR}/goal090_position_band_review_only_unlock_report.md"
MANIFEST_PATH = f"{AUDIT_DIR}/goal090_position_band_review_only_unlock_manifest.json"
AUDIT_PATH = f"{AUDIT_DIR}/goal090_position_band_review_only_unlock_audit.md"

GOAL07B_REPORT_PATH = "outputs/audits/goal07b_risk_overlay_calculation_report.md"
GOAL07B_AUDIT_PATH = "outputs/audits/goal07b_risk_overlay_calculation_audit.md"
GOAL07B_MANIFEST_PATH = "outputs/audits/goal07b_risk_overlay_calculation_manifest.json"
GOAL08A_REPORT_PATH = "outputs/audits/goal08a_recommendation_contract_design_report.md"
GOAL08A_AUDIT_PATH = "outputs/audits/goal08a_recommendation_contract_design_audit.md"
GOAL08A_MANIFEST_PATH = "outputs/audits/goal08a_recommendation_contract_design_manifest.json"
GOAL_STORAGE01_REPORT_PATH = "outputs/audits/goal_storage01_local_research_lake_hardening_report.md"
GOAL_STORAGE01_AUDIT_PATH = "outputs/audits/goal_storage01_local_research_lake_hardening_audit.md"
GOAL_STORAGE01_MANIFEST_PATH = "outputs/audits/goal_storage01_local_research_lake_hardening_manifest.json"
GOAL08B0_REPORT_PATH = "outputs/audits/goal08b0_recommendation_review_only_unlock_report.md"
GOAL08B0_AUDIT_PATH = "outputs/audits/goal08b0_recommendation_review_only_unlock_audit.md"
GOAL08B0_MANIFEST_PATH = "outputs/audits/goal08b0_recommendation_review_only_unlock_manifest.json"
GOAL08B_DIAGNOSTIC_PATH = "outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv"
GOAL08B_REPORT_PATH = "outputs/audits/goal08b_recommendation_diagnostics_report.md"
GOAL08B_AUDIT_PATH = "outputs/audits/goal08b_recommendation_diagnostics_audit.md"
GOAL08B_MANIFEST_PATH = "outputs/audits/goal08b_recommendation_diagnostics_manifest.json"

GOAL08B_WORKFLOW_ID = "goal08b_recommendation_review_only_prototype"
GOAL090_WORKFLOW_ID = "goal090_position_band_review_only_unlock_gate"
GOAL09_WORKFLOW_ID = "position_band_recommendation"
GOAL09_ELIGIBLE_STATUS = "future_review_only"
GOAL09_IMPLEMENTED_STATUS = "implemented_review_only"
GOAL090_READY = "eligible_for_future_review_only_prototype"
GOAL090_BLOCKED = "blocked_until_goal08b_review_only_diagnostics_pass"
GOAL09_ALLOWED_NEXT = "await_explicit_goal09_position_band_diagnostics_prototype"
GOAL09_IMPLEMENTED_ALLOWED_NEXT = "fix_goal09_position_band_warnings_before_any_downstream_request"
GOAL090_BLOCKED_NEXT = "repair_goal090_unlock_blockers"

WORKFLOW_PRODUCES_ARTIFACTS = ";".join([POLICY_PATH, DOC_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH])
WORKFLOW_PRIMARY_DOCS = f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md"
WORKFLOW_PRIMARY_SCRIPTS = "scripts/run_goal090_position_band_review_only_unlock_gate.py;scripts/audit_goal090_position_band_review_only_unlock_gate.py"
WORKFLOW_PRIMARY_OUTPUTS = f"{REPORT_PATH};{MANIFEST_PATH};{AUDIT_PATH}"
WORKFLOW_NOTES = "Review-only unlock gate; GOAL-09 position-band diagnostics become eligible only for a future explicit non-actionable prototype and are not implemented here."

GOAL08B_REQUIRED_FIELDS = [
    "trade_date",
    "symbol",
    "source_goal",
    "source_goal07b_mode",
    "risk_severity",
    "risk_state",
    "source_risk_tag",
    "source_triggered_rule_ids",
    "risk_warning_codes",
    "recommendation_diagnostic_label",
    "actionability_status",
    "actionability_blocked",
    "blocked_reason_codes",
    "warning_propagation_codes",
    "provider_concentration_disclosure",
    "contract_version",
    "diagnostic_mode",
    "deterministic_rule_trace",
    "non_actionable_disclaimer",
]

FORBIDDEN_GOAL08B_FIELD_NAMES = {
    "buy",
    "sell",
    "hold",
    "target_price",
    "expected_return",
    "expected_return_action",
    "position_size",
    "position_band",
    "portfolio_weight",
    "weight",
    "order",
    "execution",
    "trade_signal",
}

FORBIDDEN_OUTPUT_DIRS = [
    "outputs/recommendations",
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
    "position_band_diagnostics_rows_generated",
    "position_rows_generated",
    "position_sizing_generated",
    "portfolio_construction_generated",
    "portfolio_weights_generated",
    "buy_sell_hold_outputs_generated",
    "target_prices_generated",
    "expected_returns_for_action_generated",
    "actionable_recommendation_rows_generated",
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
]


def run_goal090_position_band_review_only_unlock_gate(root: Path) -> bool:
    bundle = load_goal090_unlock_bundle(root)
    review = evaluate_goal090_unlock_gate(bundle)
    _write_policy(root, review)
    _write_outputs(root, review)
    _update_workflow_status(root, review)
    _update_locked_capabilities(root, review)
    audit_ok = audit_goal090_position_band_review_only_unlock_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return review["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal090_position_band_review_only_unlock_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    workflow = _workflow_rows(root)
    failures: list[str] = []
    warnings: list[str] = []

    if not _report_pass_or_warn(report, "GOAL-09.0 Position-Band Review-Only Unlock Gate:"):
        failures.append("unlock_report_not_pass_or_warn")
    if manifest.get("goal") != GOAL_NAME:
        failures.append("manifest_goal_invalid")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_not_review_only_unlock_gate")
    if manifest.get("goal090_unlock_status") != GOAL090_READY:
        failures.append("manifest_goal090_unlock_status_not_ready")
    goal09_valid = _goal09_valid_diagnostics_evidence(root)
    expected_goal09_status = GOAL09_IMPLEMENTED_STATUS if goal09_valid else GOAL09_ELIGIBLE_STATUS
    expected_goal09_implemented = True if goal09_valid else False
    if manifest.get("goal09_target_status") != expected_goal09_status:
        failures.append("manifest_goal09_target_not_preserved_status")
    if manifest.get("goal09_implemented_by_this_gate") is not False:
        failures.append("manifest_goal09_implemented_by_gate_not_false")
    if manifest.get("goal09_implemented_in_repo") is not expected_goal09_implemented:
        failures.append("manifest_goal09_implemented_in_repo_not_preserved")
    if manifest.get("future_position_band_diagnostics_non_actionable_required") is not True:
        failures.append("manifest_future_position_band_non_actionable_not_true")
    if manifest.get("evidence_basis") != "prior_pass_or_pass_with_warnings_review_only_design_infrastructure_evidence_only_no_position_outputs":
        failures.append("manifest_evidence_basis_invalid")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"manifest_{key}_not_false")
    for key in [
        "goal08b_diagnostics_valid",
        "goal08b_non_actionable_preserved",
        "goal08b_output_grain_trade_date_symbol",
        "goal08b_actionability_status_never_actionable",
        "high_risk_actionability_block_preserved",
        "goal08b_warnings_propagate_to_future_position_band_diagnostics",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")

    gate_row = workflow.get(GOAL090_WORKFLOW_ID, {})
    if gate_row.get("status") != "implemented_review_only":
        failures.append("goal090_workflow_not_implemented_review_only")
    if gate_row.get("implemented_in_repo") != "true":
        failures.append("goal090_workflow_not_marked_implemented")
    goal09 = workflow.get(GOAL09_WORKFLOW_ID, {})
    if goal09.get("status") != expected_goal09_status:
        failures.append("goal09_workflow_not_preserved_status")
    if goal09.get("implemented_in_repo") != ("true" if goal09_valid else "false"):
        failures.append("goal09_workflow_implemented_flag_not_preserved")
    if goal09.get("allowed_next_action") not in {GOAL09_ALLOWED_NEXT, GOAL09_IMPLEMENTED_ALLOWED_NEXT}:
        failures.append("goal09_allowed_next_invalid")
    if goal09.get("depends_on") != GOAL090_WORKFLOW_ID:
        failures.append("goal09_depends_on_not_goal090")
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
                "# GOAL-09.0 Position-Band Review-Only Unlock Audit",
                "",
                f"Status: `{status}`",
                "",
                f"GOAL-09.0 workflow status: `{gate_row.get('status', 'missing')}`",
                f"GOAL-09 target workflow status: `{goal09.get('status', 'missing')}`",
                "GOAL-09 implemented by this gate: `false`",
                f"GOAL-09 implemented in repo: `{str(expected_goal09_implemented).lower()}`",
                f"GOAL-09 target status after this gate: `{expected_goal09_status}`",
                "Position-band diagnostic rows generated by this gate: `false`",
                "Position rows, position sizing, portfolio weights, dashboards, trading, production, backtest, factor-mining, broker, local-lake, and DQN/RL outputs generated: `false`",
                "Evidence basis: prior GOAL-07B, GOAL-08A, GOAL-STORAGE-01, GOAL-08B.0, and GOAL-08B PASS/PASS_WITH_WARNINGS review-only evidence only; no position-band calculation outputs.",
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


def load_goal090_unlock_bundle(root: Path) -> dict[str, object]:
    return {
        "goal07b_report": _read(root / GOAL07B_REPORT_PATH),
        "goal07b_audit": _read(root / GOAL07B_AUDIT_PATH),
        "goal07b_manifest": _read_json(root / GOAL07B_MANIFEST_PATH),
        "goal08a_report": _read(root / GOAL08A_REPORT_PATH),
        "goal08a_audit": _read(root / GOAL08A_AUDIT_PATH),
        "goal08a_manifest": _read_json(root / GOAL08A_MANIFEST_PATH),
        "storage01_report": _read(root / GOAL_STORAGE01_REPORT_PATH),
        "storage01_audit": _read(root / GOAL_STORAGE01_AUDIT_PATH),
        "storage01_manifest": _read_json(root / GOAL_STORAGE01_MANIFEST_PATH),
        "goal08b0_report": _read(root / GOAL08B0_REPORT_PATH),
        "goal08b0_audit": _read(root / GOAL08B0_AUDIT_PATH),
        "goal08b0_manifest": _read_json(root / GOAL08B0_MANIFEST_PATH),
        "goal08b_rows": _read_csv(root / GOAL08B_DIAGNOSTIC_PATH),
        "goal08b_report": _read(root / GOAL08B_REPORT_PATH),
        "goal08b_audit": _read(root / GOAL08B_AUDIT_PATH),
        "goal08b_manifest": _read_json(root / GOAL08B_MANIFEST_PATH),
        "goal09_valid_evidence": _goal09_valid_diagnostics_evidence(root),
        "workflow_rows": _read_csv(root / "configs/project/workflow_status.csv"),
        "forbidden_output_dirs": _forbidden_output_dirs_present(root),
        "local_lake_paths": _local_lake_paths_present(root),
        "tracked_forbidden_files": _tracked_forbidden_files(root),
    }


def evaluate_goal090_unlock_gate(bundle: dict[str, object]) -> dict[str, object]:
    failures = _validate_input_bundle(bundle)
    goal08b_rows = [dict(row) for row in bundle.get("goal08b_rows", []) if isinstance(row, dict)]
    warning_codes = _goal08b_warning_codes(goal08b_rows, bundle.get("goal08b_manifest", {}))
    status = BLOCKED if failures else PASS_WITH_WARNINGS if warning_codes else PASS
    manifest = _manifest(status, goal08b_rows, warning_codes, sorted(set(failures)), bool(bundle.get("goal09_valid_evidence")))
    return {
        "status": status,
        "failures": sorted(set(failures)),
        "warnings": warning_codes if status != BLOCKED else [],
        "goal08b_rows": goal08b_rows,
        "manifest": manifest,
    }


def goal090_valid_unlock_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        _report_pass_or_warn(report, "GOAL-09.0 Position-Band Review-Only Unlock Gate:")
        and "Status: `PASS`" in audit
        and manifest.get("goal") == GOAL_NAME
        and manifest.get("mode") == MODE
        and manifest.get("goal090_unlock_status") == GOAL090_READY
        and manifest.get("goal09_target_status") in {GOAL09_ELIGIBLE_STATUS, GOAL09_IMPLEMENTED_STATUS}
        and manifest.get("goal09_implemented_by_this_gate") is False
        and isinstance(manifest.get("goal09_implemented_in_repo"), bool)
        and manifest.get("future_position_band_diagnostics_non_actionable_required") is True
        and manifest.get("goal08b_diagnostics_valid") is True
        and manifest.get("position_band_diagnostics_rows_generated") is False
        and manifest.get("position_rows_generated") is False
        and manifest.get("downstream_stages_unlocked_by_this_gate") is False
    )


def _validate_input_bundle(bundle: dict[str, object]) -> list[str]:
    failures: list[str] = []
    workflow = {row.get("workflow_id", ""): row for row in bundle.get("workflow_rows", []) if isinstance(row, dict)}
    goal08b_rows = [dict(row) for row in bundle.get("goal08b_rows", []) if isinstance(row, dict)]
    goal08b_manifest = bundle.get("goal08b_manifest", {})

    if not _report_pass_or_warn(str(bundle.get("goal07b_report", "")), "GOAL-07B Risk Overlay Calculation Prototype:"):
        failures.append("goal07b_report_not_pass_or_warn")
    if "Status: `PASS`" not in str(bundle.get("goal07b_audit", "")):
        failures.append("goal07b_audit_not_pass")
    if bundle.get("goal07b_manifest", {}).get("mode") != "review_only":
        failures.append("goal07b_manifest_not_review_only")

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

    if not _report_pass_or_warn(str(bundle.get("goal08b0_report", "")), "GOAL-08B.0 Recommendation Review-Only Unlock Gate:"):
        failures.append("goal08b0_report_not_pass_or_warn")
    if "Status: `PASS`" not in str(bundle.get("goal08b0_audit", "")):
        failures.append("goal08b0_audit_not_pass")
    if bundle.get("goal08b0_manifest", {}).get("goal08b0_unlock_status") != "eligible_for_future_review_only_prototype":
        failures.append("goal08b0_manifest_unlock_not_ready")

    if not _report_pass_or_warn(str(bundle.get("goal08b_report", "")), "GOAL-08B Recommendation Diagnostics Prototype:"):
        failures.append("goal08b_report_not_pass_or_warn")
    if "Status: `PASS`" not in str(bundle.get("goal08b_audit", "")):
        failures.append("goal08b_audit_not_pass")
    if goal08b_manifest.get("mode") != "review_only":
        failures.append("goal08b_manifest_not_review_only")
    if goal08b_manifest.get("output_grain") != "trade_date + symbol":
        failures.append("goal08b_manifest_grain_invalid")
    if goal08b_manifest.get("diagnostic_rows_generated") is not True:
        failures.append("goal08b_manifest_diagnostic_rows_not_true")
    if goal08b_manifest.get("recommendation_diagnostics_rows_generated") is not True:
        failures.append("goal08b_manifest_recommendation_diagnostics_not_true")
    if goal08b_manifest.get("non_actionable") is not True:
        failures.append("goal08b_manifest_not_non_actionable")
    if goal08b_manifest.get("actionability_status_values") != ["never_actionable"]:
        failures.append("goal08b_manifest_actionability_invalid")
    if goal08b_manifest.get("diagnostic_row_count") != len(goal08b_rows):
        failures.append("goal08b_manifest_row_count_mismatch")
    for key in [
        "actionable_recommendation_rows_generated",
        "position_sizing_generated",
        "portfolio_weights_generated",
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
        if goal08b_manifest.get(key) is not False:
            failures.append(f"goal08b_manifest_{key}_not_false")

    if not goal08b_rows:
        failures.append("goal08b_diagnostic_rows_missing")
    else:
        fields = list(goal08b_rows[0].keys())
        missing = sorted(set(GOAL08B_REQUIRED_FIELDS) - set(fields))
        failures.extend(f"goal08b_missing_field:{field}" for field in missing)
        failures.extend(f"goal08b_forbidden_field:{field}" for field in forbidden_goal090_source_fields(fields))
        grain = [(row.get("trade_date", ""), row.get("symbol", "")) for row in goal08b_rows]
        if len(grain) != len(set(grain)):
            failures.append("goal08b_rows_not_unique_trade_date_symbol")
        for index, row in enumerate(goal08b_rows):
            failures.extend(_goal08b_row_failures(row, index))

    goal08b = workflow.get(GOAL08B_WORKFLOW_ID, {})
    if goal08b.get("status") != "implemented_review_only" or goal08b.get("implemented_in_repo") != "true":
        failures.append("goal08b_workflow_not_implemented_review_only")
    goal09 = workflow.get(GOAL09_WORKFLOW_ID, {})
    goal09_valid = bool(bundle.get("goal09_valid_evidence"))
    if goal09 and goal09.get("status") not in {"locked_future", GOAL09_ELIGIBLE_STATUS, GOAL09_IMPLEMENTED_STATUS}:
        failures.append("goal09_workflow_not_locked_future_or_implemented_review_only")
    if goal09 and goal09.get("status") == GOAL09_IMPLEMENTED_STATUS:
        if not goal09_valid:
            failures.append("goal09_implemented_without_valid_diagnostics_evidence")
        if goal09.get("implemented_in_repo") != "true":
            failures.append("goal09_implemented_not_marked_implemented")
    elif goal09 and goal09.get("implemented_in_repo") != "false":
        failures.append("goal09_workflow_marked_implemented_before_goal09")
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


def forbidden_goal090_source_fields(fields: list[str]) -> list[str]:
    failures: list[str] = []
    for field in fields:
        lowered = field.lower()
        if lowered in FORBIDDEN_GOAL08B_FIELD_NAMES:
            failures.append(field)
            continue
        if lowered.startswith(("buy", "sell", "hold", "order", "execution")):
            failures.append(field)
            continue
        if any(token in lowered for token in ["target_price", "expected_return", "position_size", "position_band", "portfolio_weight"]):
            failures.append(field)
    return sorted(set(failures))


def _goal08b_row_failures(row: dict[str, str], index: int) -> list[str]:
    failures: list[str] = []
    if row.get("diagnostic_mode") != "review_only":
        failures.append(f"goal08b_row_{index}_not_review_only")
    if row.get("actionability_status") != "never_actionable":
        failures.append(f"goal08b_row_{index}_actionability_status_not_never_actionable")
    if row.get("actionability_blocked") != "true":
        failures.append(f"goal08b_row_{index}_actionability_not_blocked")
    if row.get("source_goal07b_mode") != "review_only":
        failures.append(f"goal08b_row_{index}_source_goal07b_not_review_only")
    if row.get("risk_severity") == "HIGH" and "high_risk_severity" not in _split_codes(row.get("blocked_reason_codes", "")):
        failures.append(f"goal08b_row_{index}_high_risk_not_blocked")
    if not row.get("non_actionable_disclaimer"):
        failures.append(f"goal08b_row_{index}_disclaimer_missing")
    return failures


def _goal08b_warning_codes(rows: list[dict[str, str]], manifest: object) -> list[str]:
    warnings = {code for row in rows for code in _split_codes(row.get("warning_propagation_codes", ""))}
    if isinstance(manifest, dict):
        for key in ["remaining_warnings", "warning_codes_propagated"]:
            value = manifest.get(key, [])
            if isinstance(value, list):
                warnings.update(str(item) for item in value if item and item != "none")
    return sorted(code for code in warnings if code and code != "none")


def _manifest(
    status: str,
    goal08b_rows: list[dict[str, str]],
    warning_codes: list[str],
    failures: list[str],
    goal09_valid: bool,
) -> dict[str, object]:
    goal09_target = GOAL09_IMPLEMENTED_STATUS if status != BLOCKED and goal09_valid else ("locked_future" if status == BLOCKED else GOAL09_ELIGIBLE_STATUS)
    goal09_allowed_next = GOAL09_IMPLEMENTED_ALLOWED_NEXT if status != BLOCKED and goal09_valid else (GOAL090_BLOCKED_NEXT if status == BLOCKED else GOAL09_ALLOWED_NEXT)
    return {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "status": status,
        "mode": MODE,
        "goal090_unlock_status": GOAL090_BLOCKED if status == BLOCKED else GOAL090_READY,
        "goal09_target_status": goal09_target,
        "goal09_implemented_by_this_gate": False,
        "goal09_implemented_in_repo": bool(status != BLOCKED and goal09_valid),
        "goal09_status_after_goal090": goal09_target,
        "allowed_next_action": goal09_allowed_next,
        "evidence_basis": "prior_pass_or_pass_with_warnings_review_only_design_infrastructure_evidence_only_no_position_outputs",
        "evidence_inputs": [
            GOAL07B_REPORT_PATH,
            GOAL07B_AUDIT_PATH,
            GOAL07B_MANIFEST_PATH,
            GOAL08A_REPORT_PATH,
            GOAL08A_AUDIT_PATH,
            GOAL08A_MANIFEST_PATH,
            GOAL_STORAGE01_REPORT_PATH,
            GOAL_STORAGE01_AUDIT_PATH,
            GOAL_STORAGE01_MANIFEST_PATH,
            GOAL08B0_REPORT_PATH,
            GOAL08B0_AUDIT_PATH,
            GOAL08B0_MANIFEST_PATH,
            GOAL08B_DIAGNOSTIC_PATH,
            GOAL08B_REPORT_PATH,
            GOAL08B_AUDIT_PATH,
            GOAL08B_MANIFEST_PATH,
        ],
        "goal08b_diagnostics_valid": status != BLOCKED,
        "goal08b_row_count": len(goal08b_rows),
        "goal08b_output_grain": "trade_date + symbol",
        "goal08b_output_grain_trade_date_symbol": True,
        "goal08b_actionability_status_values": sorted({row.get("actionability_status", "") for row in goal08b_rows}),
        "goal08b_actionability_status_never_actionable": bool(goal08b_rows) and {row.get("actionability_status") for row in goal08b_rows} == {"never_actionable"},
        "goal08b_non_actionable_preserved": bool(goal08b_rows) and {row.get("diagnostic_mode") for row in goal08b_rows} == {"review_only"},
        "high_risk_actionability_block_preserved": _high_risk_block_preserved(goal08b_rows),
        "goal08b_warnings_propagate_to_future_position_band_diagnostics": bool(warning_codes),
        "warning_codes_to_propagate": warning_codes,
        "future_position_band_diagnostics_non_actionable_required": True,
        "future_position_band_output_grain_required": "trade_date + symbol",
        "future_goal09_requires_separate_explicit_request": True,
        "failures": failures,
        "warnings": warning_codes if status != BLOCKED else [],
        **{key: False for key in FALSE_BOUNDARY_KEYS},
    }


def _write_policy(root: Path, review: dict[str, object]) -> None:
    write_json(
        root / POLICY_PATH,
        {
            "goal": GOAL_NAME,
            "mode": MODE,
            "target_workflow_id": GOAL09_WORKFLOW_ID,
            "target_status_after_pass": review["manifest"]["goal09_target_status"],
            "goal09_implemented_by_this_gate": False,
            "goal09_implemented_in_repo": review["manifest"]["goal09_implemented_in_repo"],
            "consumes_only": review["manifest"]["evidence_inputs"],
            "evidence_basis": review["manifest"]["evidence_basis"],
            "future_goal09_constraints": {
                "requires_separate_explicit_request": True,
                "diagnostics_only": True,
                "non_actionable_required": True,
                "output_grain_required": "trade_date + symbol",
                "position_rows_allowed_by_this_gate": False,
                "position_sizing_allowed_by_this_gate": False,
                "portfolio_weights_allowed_by_this_gate": False,
            },
            "forbidden_execution": {key: True for key in FALSE_BOUNDARY_KEYS},
            "status": review["status"],
        },
    )


def _write_outputs(root: Path, review: dict[str, object]) -> None:
    write_json(root / MANIFEST_PATH, review["manifest"])
    _write_report(root, review)
    _write_doc(root, review)


def _write_report(root: Path, review: dict[str, object]) -> None:
    warning_lines = [f"- `{warning}`" for warning in review["warnings"]] or ["- `none`"]
    write_text(
        root / REPORT_PATH,
        "\n".join(
            [
                "# GOAL-09.0 Position-Band Review-Only Unlock Gate",
                "",
                f"GOAL-09.0 Position-Band Review-Only Unlock Gate: {review['status']}",
                "GOAL-09.0 mode: `review_only_unlock_gate`",
                f"GOAL-09 target status after pass: `{review['manifest']['goal09_target_status']}`",
                "GOAL-09 implemented by this gate: `false`",
                f"GOAL-09 implemented in repo: `{str(review['manifest']['goal09_implemented_in_repo']).lower()}`",
                f"GOAL-08B diagnostic rows reviewed: `{review['manifest']['goal08b_row_count']}`",
                "Evidence basis: prior PASS/PASS_WITH_WARNINGS review-only, design-only, and infrastructure-only artifacts only.",
                "No position-band diagnostic rows, position rows, position sizing, portfolio weights, dashboards, paper/live trading paths, broker outputs, production behavior, backtests, factor-mining outputs, local lake files, or DQN/RL outputs were created.",
                f"Allowed next action: `{review['manifest']['allowed_next_action']}`",
                "",
                "## Evidence Inputs",
                *[f"- `{item}`" for item in review["manifest"].get("evidence_inputs", [])],
                "",
                "## Warning Codes To Propagate",
                *warning_lines,
                "",
                "## Failures",
                *[f"- {failure}" for failure in review["failures"]],
                "",
            ]
        ),
    )


def _write_doc(root: Path, review: dict[str, object]) -> None:
    if review["manifest"].get("goal09_implemented_in_repo") is True:
        goal09_boundary = "GOAL-09 is already preserved as `implemented_review_only` by separate GOAL-09 diagnostic evidence; GOAL-09.0 did not implement it."
    else:
        goal09_boundary = "GOAL-09 remains not implemented and is only `future_review_only` eligible."
    write_text(
        root / DOC_PATH,
        "\n".join(
            [
                "# GOAL-09.0 Position-Band Review-Only Unlock Gate",
                "",
                f"Status: `{review['status']}`",
                "",
                "GOAL-09.0 is an unlock-only governance gate. It may mark GOAL-09 position-band diagnostics as `future_review_only` eligible for a later explicit non-actionable prototype request or preserve a separately implemented GOAL-09 review-only diagnostics state. It does not implement GOAL-09.",
                "",
                "## Evidence Basis",
                "",
                "- Prior GOAL-07B risk overlay diagnostics are review-only and non-actionable.",
                "- GOAL-08A recommendation contracts are design-only and generated zero rows.",
                "- GOAL-STORAGE-01 is infrastructure-only and did not materialize a local lake.",
                "- GOAL-08B.0 is unlock-only evidence.",
                "- GOAL-08B recommendation diagnostics are review-only, non-actionable, and at `trade_date + symbol` grain.",
                "",
                "## Boundary",
                "",
                f"- {goal09_boundary}",
                "- Future position-band diagnostic changes or downstream unlocks require a separate explicit request.",
                "- Future GOAL-09 diagnostics must inherit `actionability_status=never_actionable` and warning propagation from GOAL-08B.",
                "- No position rows, position sizing, portfolio weights, buy/sell/hold outputs, target prices, expected returns for action, dashboards, trading, production, backtests, factor-mining, broker, local-lake, or DQN/RL outputs are created by this gate.",
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
        "workflow_id": GOAL090_WORKFLOW_ID,
        "display_name": "GOAL-09.0 Position-Band Review-Only Unlock Gate",
        "stage_or_goal": "GOAL-09.0",
        "status": "implemented_review_only" if review["status"] != BLOCKED else "locked_future",
        "current_repo_role": "review_only_unlock_governance_gate",
        "implemented_in_repo": "true" if review["status"] != BLOCKED else "false",
        "allowed_next_action": GOAL09_ALLOWED_NEXT if review["status"] != BLOCKED else GOAL090_BLOCKED_NEXT,
        "depends_on": GOAL08B_WORKFLOW_ID,
        "produces_artifacts": WORKFLOW_PRODUCES_ARTIFACTS,
        "primary_docs": WORKFLOW_PRIMARY_DOCS,
        "primary_scripts": WORKFLOW_PRIMARY_SCRIPTS,
        "primary_outputs": WORKFLOW_PRIMARY_OUTPUTS,
        "promotion_rule": "implemented_review_only_after_goal090_unlock_gate_pass_with_warnings",
        "notes": WORKFLOW_NOTES,
    }
    if GOAL090_WORKFLOW_ID in by_id:
        by_id[GOAL090_WORKFLOW_ID].update(gate_row)
    else:
        insert_at = next((index for index, item in enumerate(rows) if item["workflow_id"] == GOAL09_WORKFLOW_ID), len(rows))
        rows.insert(insert_at, gate_row)
        by_id = {row["workflow_id"]: row for row in rows}

    if GOAL09_WORKFLOW_ID in by_id:
        if review["status"] == BLOCKED:
            by_id[GOAL09_WORKFLOW_ID].update(goal09_locked_workflow_patch())
        else:
            by_id[GOAL09_WORKFLOW_ID].update(goal09_eligible_workflow_patch(root))
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
    preserve_later_review_only_workflow_states(root, by_id)
    write_csv(path, rows, fields)


def _update_locked_capabilities(root: Path, review: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    if not path.exists():
        return
    payload = read_json(path)
    payload[GOAL090_WORKFLOW_ID] = "implemented_review_only" if review["status"] != BLOCKED else False
    payload[GOAL09_WORKFLOW_ID] = _goal09_capability_status(root) if review["status"] != BLOCKED else False
    for key in [
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
    preserve_later_review_only_capabilities(root, payload)
    write_json(path, payload)


def goal09_eligible_workflow_patch(root: Path | None = None) -> dict[str, str]:
    if root is not None and _goal09_valid_diagnostics_evidence(root):
        try:
            from ashare_premarket.review_diagnostics.goal09 import goal09_implemented_workflow_patch

            return goal09_implemented_workflow_patch()
        except Exception:
            pass
    return {
        "display_name": "GOAL-09 Position-Band Diagnostics Prototype",
        "stage_or_goal": "GOAL-09",
        "status": GOAL09_ELIGIBLE_STATUS,
        "current_repo_role": "review_only_eligible_not_implemented",
        "implemented_in_repo": "false",
        "allowed_next_action": GOAL09_ALLOWED_NEXT,
        "depends_on": GOAL090_WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": WORKFLOW_PRIMARY_DOCS,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "eligible_for_future_review_only_prototype_after_goal090_unlock_gate",
        "notes": "Eligibility only; GOAL-09 position-band diagnostics are not implemented and no position rows or downstream outputs exist.",
    }


def goal09_locked_workflow_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-09 Position-Band Diagnostics Prototype",
        "stage_or_goal": "GOAL-09",
        "status": "locked_future",
        "current_repo_role": "locked_downstream_boundary",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal090_passes",
        "depends_on": GOAL090_WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": WORKFLOW_PRIMARY_DOCS,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_goal090_unlock_gate_passes",
        "notes": "Locked future position-band diagnostics; no position rows or downstream outputs exist.",
    }


def _goal09_capability_status(root: Path) -> str:
    return GOAL09_IMPLEMENTED_STATUS if _goal09_valid_diagnostics_evidence(root) else GOAL09_ELIGIBLE_STATUS


def _goal09_valid_diagnostics_evidence(root: Path) -> bool:
    try:
        from ashare_premarket.review_diagnostics.goal09 import goal09_valid_position_band_diagnostics_evidence

        return goal09_valid_position_band_diagnostics_evidence(root)
    except Exception:
        return False


def _high_risk_block_preserved(rows: list[dict[str, str]]) -> bool:
    high_risk_rows = [row for row in rows if row.get("risk_severity") == "HIGH"]
    return bool(high_risk_rows) and all("high_risk_severity" in _split_codes(row.get("blocked_reason_codes", "")) for row in high_risk_rows)


def _split_codes(value: str) -> list[str]:
    if not value or value == "none":
        return []
    return [item for item in str(value).split(";") if item and item != "none"]


def _report_pass_or_warn(text: str, prefix: str) -> bool:
    return f"{prefix} {PASS}" in text or f"{prefix} {PASS_WITH_WARNINGS}" in text


def _forbidden_output_dirs_present(root: Path) -> list[str]:
    allowed_when_goal09_valid = {"outputs/position"} if _goal09_valid_diagnostics_evidence(root) or _goal09_output_dir_contains_only_known_safe_artifacts(root) else set()
    return [path for path in FORBIDDEN_OUTPUT_DIRS if path not in allowed_when_goal09_valid and (root / path).exists()]


def _goal09_output_dir_contains_only_known_safe_artifacts(root: Path) -> bool:
    position_dir = root / "outputs/position"
    if not position_dir.exists():
        return False
    allowed = {"outputs/position/goal09_review_only_position_band_diagnostics.csv"}
    files = {path.relative_to(root).as_posix() for path in position_dir.rglob("*") if path.is_file()}
    return bool(files) and files <= allowed


def _local_lake_paths_present(root: Path) -> list[str]:
    return [path for path in LOCAL_LAKE_PATHS if (root / path).exists()]


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

from __future__ import annotations

import subprocess
from pathlib import Path

from ashare_premarket.contract_design.goal090 import (
    GOAL09_WORKFLOW_ID,
    GOAL090_WORKFLOW_ID,
    goal090_valid_unlock_evidence,
)
from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import preserve_later_review_only_capabilities, preserve_later_review_only_workflow_states
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-09"
GOAL_NAME = "GOAL-09-POSITION-BAND-DIAGNOSTICS-PROTOTYPE"
MODE = "review_only"
OUTPUT_TYPE = "position_band_diagnostic"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

CONFIG_DIR = "configs/position"
DOC_DIR = "docs/position"
OUTPUT_DIR = "outputs/position"
AUDIT_DIR = "outputs/audits"

POLICY_PATH = f"{CONFIG_DIR}/goal09_review_only_position_band_diagnostics_policy.yaml"
DIAGNOSTIC_PATH = f"{OUTPUT_DIR}/goal09_review_only_position_band_diagnostics.csv"
DOC_PATH = f"{DOC_DIR}/GOAL09_REVIEW_ONLY_POSITION_BAND_DIAGNOSTICS.md"
REPORT_PATH = f"{AUDIT_DIR}/goal09_position_band_diagnostics_report.md"
MANIFEST_PATH = f"{AUDIT_DIR}/goal09_position_band_diagnostics_manifest.json"
AUDIT_PATH = f"{AUDIT_DIR}/goal09_position_band_diagnostics_audit.md"

WORKFLOW_PRODUCES_ARTIFACTS = ";".join([POLICY_PATH, DIAGNOSTIC_PATH, DOC_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH])
WORKFLOW_PRIMARY_DOCS = f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md"
WORKFLOW_PRIMARY_SCRIPTS = "scripts/run_goal09_position_band_diagnostics_prototype.py;scripts/audit_goal09_position_band_diagnostics_prototype.py"
WORKFLOW_PRIMARY_OUTPUTS = f"{DIAGNOSTIC_PATH};{REPORT_PATH};{MANIFEST_PATH};{AUDIT_PATH}"
WORKFLOW_NOTES = "Review-only non-actionable position-band diagnostics; not position sizing, target weights, orders, buy/sell/hold, dashboard, trading, production, backtest, factor-mining, broker, local-lake, or DQN/RL output."

GOAL07B_OVERLAY_PATH = "outputs/risk_overlay/goal07b_review_only_risk_overlay.csv"
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
GOAL090_REPORT_PATH = "outputs/audits/goal090_position_band_review_only_unlock_report.md"
GOAL090_AUDIT_PATH = "outputs/audits/goal090_position_band_review_only_unlock_audit.md"
GOAL090_MANIFEST_PATH = "outputs/audits/goal090_position_band_review_only_unlock_manifest.json"

GOAL08B_WORKFLOW_ID = "goal08b_recommendation_review_only_prototype"
GOAL09_IMPLEMENTED_STATUS = "implemented_review_only"
GOAL09_ALLOWED_NEXT = "fix_goal09_position_band_warnings_before_any_downstream_request"
GOAL09_BLOCKED_NEXT = "repair_goal09_position_band_diagnostics_blockers"

CONTRACT_VERSION = "goal09_review_only_position_band_diagnostics_v1"

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

GOAL07B_REQUIRED_FIELDS = [
    "trade_date",
    "symbol",
    "mode",
    "risk_severity",
    "risk_state",
    "risk_tag",
    "triggered_rule_ids",
    "warning_propagation",
    "non_actionable",
    "recommendation_generated",
    "position_generated",
    "dashboard_generated",
    "paper_live_trading_generated",
    "trading_generated",
    "production_generated",
    "backtest_generated",
    "factor_mining_generated",
    "dqn_rl_generated",
]

OUTPUT_FIELDS = [
    "trade_date",
    "symbol",
    "source_goal",
    "source_goal08b_mode",
    "source_goal07b_mode",
    "recommendation_diagnostic_label",
    "recommendation_actionability_status",
    "recommendation_actionability_blocked",
    "risk_severity",
    "risk_state",
    "risk_warning_codes",
    "propagated_warning_codes",
    "position_band_diagnostic_label",
    "position_band_status",
    "position_actionability_status",
    "position_actionability_blocked",
    "blocked_reason_codes",
    "contract_version",
    "diagnostic_mode",
    "deterministic_rule_trace",
    "non_actionable_disclaimer",
]

ALLOWED_POSITION_BAND_LABELS = {
    "blocked_high_risk",
    "blocked_never_actionable_recommendation",
    "blocked_calibration_unreliable",
    "blocked_weak_rank_signal",
    "blocked_provider_concentration",
    "review_only_no_position_band",
    "review_only_monitor_only",
}

ALLOWED_POSITION_BAND_STATUSES = {
    "diagnostic_blocked_no_position_instruction",
    "review_only_no_position_band",
    "review_only_monitor_only",
}

CALIBRATION_WARNINGS = {
    "calibration_not_reliable_for_thresholding",
    "target_horizon_calibration_warning",
}

WEAK_RANK_WARNINGS = {
    "selected_score_variant_weak_rank_signal",
    "weak_target_horizon_rank_signal",
}

PROVIDER_WARNINGS = {
    "provider_source_concentration_disclosed",
    "single_provider_mode_akshare_direct",
}

FORBIDDEN_OUTPUT_FIELD_NAMES = {
    "position_size",
    "position_weight",
    "portfolio_weight",
    "target_weight",
    "max_weight",
    "buy_amount",
    "sell_amount",
    "order_quantity",
    "target_price",
    "expected_return_action",
    "trade_action",
    "execution_action",
    "capital_allocation",
}

FORBIDDEN_OUTPUT_DIRS = [
    "outputs/recommendations",
    "outputs/positions",
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
    "position_rows_generated",
    "actual_position_sizing_generated",
    "portfolio_construction_generated",
    "portfolio_weights_generated",
    "target_weights_generated",
    "order_quantities_generated",
    "capital_allocation_amounts_generated",
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
    "stochastic_ranking_used",
    "optimization_used",
    "learned_policy_used",
    "downstream_stages_unlocked_by_this_goal",
]


def run_goal09_position_band_diagnostics_prototype(root: Path) -> bool:
    bundle = load_goal09_position_band_diagnostics_bundle(root)
    result = evaluate_goal09_position_band_diagnostics(bundle)
    _write_policy(root, result)
    _write_outputs(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal09_position_band_diagnostics_prototype(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal09_position_band_diagnostics_prototype(root: Path) -> bool:
    rows = _read_csv(root / DIAGNOSTIC_PATH)
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    workflow = _workflow_rows(root)
    failures: list[str] = []
    warnings: list[str] = []

    if not _report_pass_or_warn(report, "GOAL-09 Position-Band Diagnostics Prototype:"):
        failures.append("goal09_report_not_pass_or_warn")
    if not rows:
        failures.append("position_band_diagnostic_rows_missing")
    if rows:
        fields = list(rows[0].keys())
        missing = [field for field in OUTPUT_FIELDS if field not in fields]
        failures.extend(f"missing_output_field:{field}" for field in missing)
        failures.extend(f"forbidden_output_field:{field}" for field in forbidden_goal09_output_fields(fields))
        grain = [(row.get("trade_date", ""), row.get("symbol", "")) for row in rows]
        if len(grain) != len(set(grain)):
            failures.append("output_grain_not_unique_trade_date_symbol")
        for index, row in enumerate(rows):
            failures.extend(_diagnostic_row_failures(row, index))

    if manifest.get("goal") != GOAL_NAME:
        failures.append("manifest_goal_invalid")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_not_review_only")
    if manifest.get("output_type") != OUTPUT_TYPE:
        failures.append("manifest_output_type_invalid")
    if manifest.get("output_grain") != "trade_date + symbol":
        failures.append("manifest_output_grain_invalid")
    if manifest.get("output_path") != DIAGNOSTIC_PATH:
        failures.append("manifest_output_path_invalid")
    if manifest.get("position_band_diagnostics_rows_generated") is not True:
        failures.append("manifest_position_band_rows_generated_not_true")
    if manifest.get("position_band_diagnostic_row_count") != len(rows):
        failures.append("manifest_row_count_mismatch")
    if manifest.get("non_actionable") is not True:
        failures.append("manifest_non_actionable_not_true")
    if manifest.get("deterministic_rules_only") is not True:
        failures.append("manifest_deterministic_rules_only_not_true")
    if manifest.get("position_actionability_status_values") != ["never_actionable"]:
        failures.append("manifest_position_actionability_values_invalid")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"manifest_{key}_not_false")
    for key in [
        "goal08b_actionability_status_never_actionable_enforced",
        "high_risk_blocking_enforced",
        "goal08b_warning_codes_propagated",
        "goal07b_risk_warning_codes_propagated",
        "future_position_band_diagnostics_non_actionable_required",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")

    goal09 = workflow.get(GOAL09_WORKFLOW_ID, {})
    if goal09.get("status") != GOAL09_IMPLEMENTED_STATUS:
        failures.append("goal09_workflow_not_implemented_review_only")
    if goal09.get("implemented_in_repo") != "true":
        failures.append("goal09_workflow_not_marked_implemented")
    if goal09.get("allowed_next_action") != GOAL09_ALLOWED_NEXT:
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
                "# GOAL-09 Position-Band Diagnostics Audit",
                "",
                f"Status: `{status}`",
                "",
                f"GOAL-09 workflow status: `{goal09.get('status', 'missing')}`",
                f"Position-band diagnostic rows: `{len(rows)}`",
                "Output grain: `trade_date + symbol`",
                "Diagnostic mode: `review_only`",
                "Position actionability status: `never_actionable`",
                "Position-band diagnostic rows are non-actionable and are not position recommendations.",
                "Actual position sizing, portfolio weights, target weights, order quantities, buy/sell/hold actions, target prices, dashboards, trading, production, backtest, factor-mining, broker, local-lake, and DQN/RL outputs generated: `false`",
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


def load_goal09_position_band_diagnostics_bundle(root: Path) -> dict[str, object]:
    return {
        "goal07b_rows": _read_csv(root / GOAL07B_OVERLAY_PATH),
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
        "goal090_report": _read(root / GOAL090_REPORT_PATH),
        "goal090_audit": _read(root / GOAL090_AUDIT_PATH),
        "goal090_manifest": _read_json(root / GOAL090_MANIFEST_PATH),
        "goal090_valid_evidence": goal090_valid_unlock_evidence(root),
        "workflow_rows": _read_csv(root / "configs/project/workflow_status.csv"),
        "forbidden_output_dirs": _forbidden_output_dirs_present(root),
        "local_lake_paths": _local_lake_paths_present(root),
        "tracked_forbidden_files": _tracked_forbidden_files(root),
    }


def evaluate_goal09_position_band_diagnostics(bundle: dict[str, object]) -> dict[str, object]:
    failures = _validate_input_bundle(bundle)
    if failures:
        return {
            "status": BLOCKED,
            "failures": sorted(set(failures)),
            "warnings": [],
            "diagnostic_rows": [],
            "manifest": _manifest(BLOCKED, [], [], sorted(set(failures)), []),
        }

    goal07b_by_key = {
        (row["trade_date"], row["symbol"]): row
        for row in bundle["goal07b_rows"]
        if isinstance(row, dict) and row.get("trade_date") and row.get("symbol")
    }
    goal08b_rows = sorted(
        [dict(row) for row in bundle["goal08b_rows"]],
        key=lambda row: (row["trade_date"], row["symbol"]),
    )
    diagnostic_rows = [_diagnostic_row(row, goal07b_by_key.get((row["trade_date"], row["symbol"]), {})) for row in goal08b_rows]
    warning_codes = sorted({code for row in diagnostic_rows for code in _split_codes(row["propagated_warning_codes"])})
    warning_codes = [code for code in warning_codes if code != "none"]
    warnings = sorted(set(warning_codes))
    labels = sorted({row["position_band_diagnostic_label"] for row in diagnostic_rows})
    status = PASS_WITH_WARNINGS if warnings else PASS
    manifest = _manifest(status, diagnostic_rows, warning_codes, [], warnings)
    manifest.update(
        {
            "input_artifacts": [
                GOAL07B_OVERLAY_PATH,
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
                GOAL090_REPORT_PATH,
                GOAL090_AUDIT_PATH,
                GOAL090_MANIFEST_PATH,
            ],
            "source_goal08b_row_count": len(goal08b_rows),
            "source_goal07b_row_count": len(goal07b_by_key),
            "position_band_diagnostic_labels_used": labels,
            "warning_codes_propagated": warning_codes,
            "remaining_warnings": warnings,
            "allowed_next_action": GOAL09_ALLOWED_NEXT,
        }
    )
    return {
        "status": status,
        "failures": [],
        "warnings": warnings,
        "diagnostic_rows": diagnostic_rows,
        "manifest": manifest,
    }


def forbidden_goal09_output_fields(fields: list[str]) -> list[str]:
    failures: list[str] = []
    for field in fields:
        lowered = field.lower()
        if lowered == "trade_date":
            continue
        if lowered in FORBIDDEN_OUTPUT_FIELD_NAMES:
            failures.append(field)
            continue
        if any(token in lowered for token in ["position_size", "position_weight", "portfolio_weight", "target_weight", "max_weight"]):
            failures.append(field)
            continue
        if any(token in lowered for token in ["buy_amount", "sell_amount", "order_quantity", "target_price", "expected_return_action", "capital_allocation"]):
            failures.append(field)
            continue
        if lowered in {"trade_action", "execution_action"}:
            failures.append(field)
    return sorted(set(failures))


def goal09_valid_position_band_diagnostics_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    rows = _read_csv(root / DIAGNOSTIC_PATH)
    return (
        _report_pass_or_warn(report, "GOAL-09 Position-Band Diagnostics Prototype:")
        and "Status: `PASS`" in audit
        and manifest.get("goal") == GOAL_NAME
        and manifest.get("mode") == MODE
        and manifest.get("output_grain") == "trade_date + symbol"
        and manifest.get("position_band_diagnostics_rows_generated") is True
        and manifest.get("non_actionable") is True
        and manifest.get("position_actionability_status_values") == ["never_actionable"]
        and manifest.get("position_rows_generated") is False
        and manifest.get("actual_position_sizing_generated") is False
        and manifest.get("portfolio_weights_generated") is False
        and manifest.get("buy_sell_hold_outputs_generated") is False
        and manifest.get("target_prices_generated") is False
        and manifest.get("downstream_stages_unlocked_by_this_goal") is False
        and bool(rows)
        and manifest.get("position_band_diagnostic_row_count") == len(rows)
    )


def goal09_implemented_workflow_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-09 Position-Band Diagnostics Prototype",
        "stage_or_goal": "GOAL-09",
        "status": GOAL09_IMPLEMENTED_STATUS,
        "current_repo_role": "review_only_position_band_diagnostic_prototype",
        "implemented_in_repo": "true",
        "allowed_next_action": GOAL09_ALLOWED_NEXT,
        "depends_on": GOAL090_WORKFLOW_ID,
        "produces_artifacts": WORKFLOW_PRODUCES_ARTIFACTS,
        "primary_docs": WORKFLOW_PRIMARY_DOCS,
        "primary_scripts": WORKFLOW_PRIMARY_SCRIPTS,
        "primary_outputs": WORKFLOW_PRIMARY_OUTPUTS,
        "promotion_rule": "implemented_review_only_after_goal09_position_band_diagnostics_pass_with_warnings",
        "notes": WORKFLOW_NOTES,
    }


def _validate_input_bundle(bundle: dict[str, object]) -> list[str]:
    failures: list[str] = []
    workflow = {row.get("workflow_id", ""): row for row in bundle.get("workflow_rows", []) if isinstance(row, dict)}
    goal07b_rows = [dict(row) for row in bundle.get("goal07b_rows", []) if isinstance(row, dict)]
    goal08b_rows = [dict(row) for row in bundle.get("goal08b_rows", []) if isinstance(row, dict)]
    goal07b_manifest = bundle.get("goal07b_manifest", {})
    goal08b_manifest = bundle.get("goal08b_manifest", {})
    goal090_manifest = bundle.get("goal090_manifest", {})

    if not _report_pass_or_warn(str(bundle.get("goal07b_report", "")), "GOAL-07B Risk Overlay Calculation Prototype:"):
        failures.append("goal07b_report_not_pass_or_warn")
    if "Status: `PASS`" not in str(bundle.get("goal07b_audit", "")):
        failures.append("goal07b_audit_not_pass")
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
    if not goal07b_rows:
        failures.append("goal07b_rows_missing")
    else:
        fields = set(goal07b_rows[0].keys())
        failures.extend(f"goal07b_missing_field:{field}" for field in sorted(set(GOAL07B_REQUIRED_FIELDS) - fields))
        grain = [(row.get("trade_date", ""), row.get("symbol", "")) for row in goal07b_rows]
        if len(grain) != len(set(grain)):
            failures.append("goal07b_rows_not_unique_trade_date_symbol")
        for index, row in enumerate(goal07b_rows):
            if row.get("mode") != "review_only":
                failures.append(f"goal07b_row_{index}_not_review_only")
            if row.get("non_actionable") != "true":
                failures.append(f"goal07b_row_{index}_not_non_actionable")
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
                if row.get(key) != "false":
                    failures.append(f"goal07b_row_{index}_{key}_not_false")

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
    if bundle.get("goal08b0_manifest", {}).get("goal08b0_unlock_status") != "eligible_for_future_review_only_prototype":
        failures.append("goal08b0_unlock_not_ready")

    if not _report_pass_or_warn(str(bundle.get("goal08b_report", "")), "GOAL-08B Recommendation Diagnostics Prototype:"):
        failures.append("goal08b_report_not_pass_or_warn")
    if "Status: `PASS`" not in str(bundle.get("goal08b_audit", "")):
        failures.append("goal08b_audit_not_pass")
    if goal08b_manifest.get("mode") != "review_only":
        failures.append("goal08b_manifest_not_review_only")
    if goal08b_manifest.get("output_grain") != "trade_date + symbol":
        failures.append("goal08b_manifest_grain_invalid")
    if goal08b_manifest.get("non_actionable") is not True:
        failures.append("goal08b_manifest_not_non_actionable")
    if goal08b_manifest.get("actionability_status_values") != ["never_actionable"]:
        failures.append("goal08b_actionability_values_invalid")
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
        failures.append("goal08b_rows_missing")
    else:
        fields = list(goal08b_rows[0].keys())
        failures.extend(f"goal08b_missing_field:{field}" for field in sorted(set(GOAL08B_REQUIRED_FIELDS) - set(fields)))
        grain = [(row.get("trade_date", ""), row.get("symbol", "")) for row in goal08b_rows]
        if len(grain) != len(set(grain)):
            failures.append("goal08b_rows_not_unique_trade_date_symbol")
        for index, row in enumerate(goal08b_rows):
            failures.extend(_goal08b_row_failures(row, index))

    if not _report_pass_or_warn(str(bundle.get("goal090_report", "")), "GOAL-09.0 Position-Band Review-Only Unlock Gate:"):
        failures.append("goal090_report_not_pass_or_warn")
    if "Status: `PASS`" not in str(bundle.get("goal090_audit", "")):
        failures.append("goal090_audit_not_pass")
    if goal090_manifest.get("mode") != "review_only_unlock_gate":
        failures.append("goal090_manifest_mode_invalid")
    if goal090_manifest.get("goal090_unlock_status") != "eligible_for_future_review_only_prototype":
        failures.append("goal090_unlock_not_ready")
    if goal090_manifest.get("future_position_band_diagnostics_non_actionable_required") is not True:
        failures.append("goal090_future_non_actionable_not_true")
    if bundle.get("goal090_valid_evidence") is not True:
        failures.append("goal090_valid_evidence_missing")

    goal09 = workflow.get(GOAL09_WORKFLOW_ID, {})
    if goal09.get("status") not in {"future_review_only", GOAL09_IMPLEMENTED_STATUS}:
        failures.append("goal09_workflow_not_future_or_implemented_review_only")
    if goal09.get("status") == "future_review_only" and goal09.get("implemented_in_repo") != "false":
        failures.append("goal09_future_review_only_marked_implemented")
    if goal09.get("status") == GOAL09_IMPLEMENTED_STATUS and goal09.get("implemented_in_repo") != "true":
        failures.append("goal09_implemented_review_only_not_marked_implemented")
    if goal09.get("depends_on") not in {GOAL090_WORKFLOW_ID, ""}:
        failures.append("goal09_depends_on_invalid")
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


def _diagnostic_row(source: dict[str, str], risk_row: dict[str, str]) -> dict[str, object]:
    warnings = sorted(set(_split_codes(source.get("warning_propagation_codes", "")) + _split_codes(source.get("risk_warning_codes", "")) + _split_codes(risk_row.get("warning_propagation", ""))))
    reasons = _blocked_reasons(source, warnings)
    label = _position_band_label(source, warnings)
    status = _position_band_status(label)
    return {
        "trade_date": source["trade_date"],
        "symbol": source["symbol"],
        "source_goal": "GOAL-08B",
        "source_goal08b_mode": source.get("diagnostic_mode", "review_only"),
        "source_goal07b_mode": source.get("source_goal07b_mode", risk_row.get("mode", "review_only")),
        "recommendation_diagnostic_label": source.get("recommendation_diagnostic_label", "unknown"),
        "recommendation_actionability_status": source.get("actionability_status", "unknown"),
        "recommendation_actionability_blocked": source.get("actionability_blocked", "true"),
        "risk_severity": source.get("risk_severity", risk_row.get("risk_severity", "UNKNOWN")),
        "risk_state": source.get("risk_state", risk_row.get("risk_state", "unknown")),
        "risk_warning_codes": source.get("risk_warning_codes", risk_row.get("warning_propagation", "none")),
        "propagated_warning_codes": ";".join(warnings) if warnings else "none",
        "position_band_diagnostic_label": label,
        "position_band_status": status,
        "position_actionability_status": "never_actionable",
        "position_actionability_blocked": True,
        "blocked_reason_codes": ";".join(reasons),
        "contract_version": CONTRACT_VERSION,
        "diagnostic_mode": MODE,
        "deterministic_rule_trace": _deterministic_trace(source, risk_row, reasons, label),
        "non_actionable_disclaimer": "diagnostic_only_not_investment_advice_not_position_instruction_not_trade_instruction",
    }


def _blocked_reasons(source: dict[str, str], warnings: list[str]) -> list[str]:
    reasons = [
        "future_position_diagnostics_non_actionable_policy",
        "review_only_non_actionable_policy",
    ]
    warning_set = set(warnings)
    if source.get("actionability_status") == "never_actionable":
        reasons.append("inherited_recommendation_never_actionable")
    if source.get("risk_severity") == "HIGH":
        reasons.append("high_risk_severity_blocks_position_band")
    if CALIBRATION_WARNINGS & warning_set:
        reasons.append("calibration_warning_blocks_position_band")
    if WEAK_RANK_WARNINGS & warning_set:
        reasons.append("weak_rank_signal_blocks_position_band")
    if PROVIDER_WARNINGS & warning_set:
        reasons.append("provider_concentration_warning_disclosed")
    return sorted(set(reasons))


def _position_band_label(source: dict[str, str], warnings: list[str]) -> str:
    warning_set = set(warnings)
    if source.get("risk_severity") == "HIGH":
        return "blocked_high_risk"
    if source.get("actionability_status") == "never_actionable":
        return "blocked_never_actionable_recommendation"
    if CALIBRATION_WARNINGS & warning_set:
        return "blocked_calibration_unreliable"
    if WEAK_RANK_WARNINGS & warning_set:
        return "blocked_weak_rank_signal"
    if PROVIDER_WARNINGS & warning_set:
        return "blocked_provider_concentration"
    if warning_set:
        return "review_only_no_position_band"
    return "review_only_monitor_only"


def _position_band_status(label: str) -> str:
    if label.startswith("blocked_"):
        return "diagnostic_blocked_no_position_instruction"
    if label == "review_only_monitor_only":
        return "review_only_monitor_only"
    return "review_only_no_position_band"


def _deterministic_trace(source: dict[str, str], risk_row: dict[str, str], reasons: list[str], label: str) -> str:
    return (
        "source_goal=GOAL-08B;"
        f"source_mode={source.get('diagnostic_mode', 'review_only')};"
        f"source_goal07b_mode={source.get('source_goal07b_mode', risk_row.get('mode', 'review_only'))};"
        f"risk_severity={source.get('risk_severity', risk_row.get('risk_severity', 'UNKNOWN'))};"
        f"recommendation_actionability_status={source.get('actionability_status', 'unknown')};"
        f"position_band_diagnostic_label={label};"
        f"blocked_reason_codes={';'.join(reasons)}"
    )


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


def _diagnostic_row_failures(row: dict[str, str], index: int) -> list[str]:
    failures: list[str] = []
    if row.get("diagnostic_mode") != MODE:
        failures.append(f"row_{index}_diagnostic_mode_not_review_only")
    if row.get("position_actionability_status") != "never_actionable":
        failures.append(f"row_{index}_position_actionability_not_never_actionable")
    if row.get("position_actionability_blocked") != "true":
        failures.append(f"row_{index}_position_actionability_not_blocked")
    if row.get("recommendation_actionability_status") != "never_actionable":
        failures.append(f"row_{index}_recommendation_actionability_not_preserved")
    if row.get("position_band_diagnostic_label") not in ALLOWED_POSITION_BAND_LABELS:
        failures.append(f"row_{index}_position_band_label_invalid:{row.get('position_band_diagnostic_label')}")
    if row.get("position_band_status") not in ALLOWED_POSITION_BAND_STATUSES:
        failures.append(f"row_{index}_position_band_status_invalid:{row.get('position_band_status')}")
    if not row.get("non_actionable_disclaimer"):
        failures.append(f"row_{index}_disclaimer_missing")
    if "position_instruction" not in row.get("non_actionable_disclaimer", ""):
        failures.append(f"row_{index}_disclaimer_does_not_block_position_instruction")
    reasons = set(_split_codes(row.get("blocked_reason_codes", "")))
    warnings = set(_split_codes(row.get("propagated_warning_codes", "")))
    if row.get("risk_severity") == "HIGH" and "high_risk_severity_blocks_position_band" not in reasons:
        failures.append(f"row_{index}_high_risk_not_blocked")
    if row.get("recommendation_actionability_status") == "never_actionable" and "inherited_recommendation_never_actionable" not in reasons:
        failures.append(f"row_{index}_never_actionable_recommendation_not_blocked")
    if CALIBRATION_WARNINGS & warnings and "calibration_warning_blocks_position_band" not in reasons:
        failures.append(f"row_{index}_calibration_warning_not_blocked")
    if WEAK_RANK_WARNINGS & warnings and "weak_rank_signal_blocks_position_band" not in reasons:
        failures.append(f"row_{index}_weak_rank_warning_not_blocked")
    if PROVIDER_WARNINGS & warnings and "provider_concentration_warning_disclosed" not in reasons:
        failures.append(f"row_{index}_provider_warning_not_disclosed")
    return failures


def _manifest(
    status: str,
    rows: list[dict[str, object]],
    warning_codes: list[str],
    failures: list[str],
    warnings: list[str],
) -> dict[str, object]:
    actionability_values = sorted({str(row.get("position_actionability_status")) for row in rows}) if rows else []
    labels = sorted({str(row.get("position_band_diagnostic_label")) for row in rows}) if rows else []
    return {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "status": status,
        "mode": MODE,
        "output_type": OUTPUT_TYPE,
        "output_path": DIAGNOSTIC_PATH,
        "output_grain": "trade_date + symbol",
        "position_band_diagnostic_row_count": len(rows),
        "position_band_diagnostics_rows_generated": bool(rows),
        "non_actionable": True,
        "position_actionability_status_values": actionability_values,
        "position_band_diagnostic_labels_used": labels,
        "contract_version": CONTRACT_VERSION,
        "deterministic_rules_only": True,
        "source_goal": "GOAL-08B",
        "source_goal08b_required": True,
        "source_goal07b_required": True,
        "goal09_status_after_pass": GOAL09_IMPLEMENTED_STATUS,
        "high_risk_blocking_enforced": any(row.get("risk_severity") == "HIGH" for row in rows)
        and all("high_risk_severity_blocks_position_band" in _split_codes(str(row.get("blocked_reason_codes", ""))) for row in rows if row.get("risk_severity") == "HIGH"),
        "goal08b_actionability_status_never_actionable_enforced": bool(rows) and {row.get("recommendation_actionability_status") for row in rows} == {"never_actionable"},
        "future_position_band_diagnostics_non_actionable_required": True,
        "goal08b_warning_codes_propagated": bool(warning_codes),
        "goal07b_risk_warning_codes_propagated": bool(warning_codes),
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        **{key: False for key in FALSE_BOUNDARY_KEYS},
    }


def _write_policy(root: Path, result: dict[str, object]) -> None:
    write_json(
        root / POLICY_PATH,
        {
            "goal": GOAL_NAME,
            "mode": MODE,
            "output_path": DIAGNOSTIC_PATH,
            "output_grain": "trade_date + symbol",
            "contract_version": CONTRACT_VERSION,
            "consumes_only": result["manifest"].get("input_artifacts", []),
            "deterministic_rules": {
                "high_risk_label": "blocked_high_risk",
                "never_actionable_recommendation_label": "blocked_never_actionable_recommendation",
                "calibration_warning_label": "blocked_calibration_unreliable",
                "weak_rank_warning_label": "blocked_weak_rank_signal",
                "provider_warning_label": "blocked_provider_concentration",
                "default_label": "review_only_no_position_band",
                "no_warning_label": "review_only_monitor_only",
            },
            "output_field_policy": {
                "diagnostic_mode": MODE,
                "position_actionability_status": "never_actionable",
                "position_actionability_blocked": True,
                "non_actionable_disclaimer_required": True,
                "forbidden_fields": sorted(FORBIDDEN_OUTPUT_FIELD_NAMES),
            },
            "forbidden_execution": {key: True for key in FALSE_BOUNDARY_KEYS},
            "status": result["status"],
        },
    )


def _write_outputs(root: Path, result: dict[str, object]) -> None:
    write_csv(root / DIAGNOSTIC_PATH, result["diagnostic_rows"], OUTPUT_FIELDS)
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_report(root, result)
    _write_doc(root, result)


def _write_report(root: Path, result: dict[str, object]) -> None:
    rows = result["diagnostic_rows"]
    manifest = result["manifest"]
    warning_lines = [f"- `{warning}`" for warning in result["warnings"]] or ["- `none`"]
    label_lines = [f"- `{label}`" for label in manifest.get("position_band_diagnostic_labels_used", [])] or ["- `none`"]
    write_text(
        root / REPORT_PATH,
        "\n".join(
            [
                "# GOAL-09 Position-Band Diagnostics Prototype",
                "",
                f"GOAL-09 Position-Band Diagnostics Prototype: {result['status']}",
                "GOAL-09 mode: `review_only`",
                f"Position-band diagnostic rows generated: `{len(rows)}`",
                "Output grain: `trade_date + symbol`",
                "Position actionability status: `never_actionable`",
                "Outputs are non-actionable diagnostics only and are not position recommendations.",
                "No actual position sizes, portfolio weights, target weights, order quantities, buy/sell/hold actions, target prices, expected returns for action, dashboards, paper/live trading paths, broker outputs, production behavior, backtests, factor-mining outputs, local lake files, or DQN/RL outputs were created.",
                f"Allowed next action: `{GOAL09_ALLOWED_NEXT}`",
                "",
                "## Evidence Inputs",
                *[f"- `{item}`" for item in manifest.get("input_artifacts", [])],
                "",
                "## Position-Band Diagnostic Labels Used",
                *label_lines,
                "",
                "## Remaining Warnings",
                *warning_lines,
                "",
                "## Failures",
                *[f"- {failure}" for failure in result["failures"]],
                "",
            ]
        ),
    )


def _write_doc(root: Path, result: dict[str, object]) -> None:
    write_text(
        root / DOC_PATH,
        "\n".join(
            [
                "# GOAL-09 Review-Only Position-Band Diagnostics",
                "",
                f"Status: `{result['status']}`",
                "",
                "GOAL-09 is implemented only as a review-only, non-actionable position-band diagnostics prototype.",
                "",
                "It consumes prior GOAL-08B recommendation diagnostics and GOAL-07B risk overlay diagnostics at `trade_date + symbol` grain. It writes a small diagnostic CSV under `outputs/position/` and does not create actual position recommendations.",
                "",
                "## Boundary",
                "",
                "- `diagnostic_mode` is always `review_only`.",
                "- `position_actionability_status` is always `never_actionable`.",
                "- `position_band_status` never contains an actual position instruction.",
                "- HIGH GOAL-07B risk severity remains blocked.",
                "- GOAL-08B warning codes and GOAL-07B risk warning codes propagate into the diagnostic output.",
                "- No position size, portfolio weight, target weight, order quantity, capital allocation amount, buy/sell/hold action, target price, expected return for action, dashboard, trading, production, backtest, factor-mining, broker, local-lake, or DQN/RL output is created.",
                "",
            ]
        ),
    )


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys())
    by_id = {row["workflow_id"]: row for row in rows}
    patch = goal09_implemented_workflow_patch()
    if result["status"] == BLOCKED:
        patch.update(
            {
                "status": "future_review_only",
                "current_repo_role": "review_only_eligible_not_implemented",
                "implemented_in_repo": "false",
                "allowed_next_action": GOAL09_BLOCKED_NEXT,
                "produces_artifacts": "",
                "primary_scripts": "",
                "primary_outputs": "",
                "promotion_rule": "eligible_for_future_review_only_prototype_after_goal090_unlock_gate",
                "notes": "GOAL-09 diagnostics remain eligible but not implemented until blockers are repaired.",
            }
        )
    if GOAL09_WORKFLOW_ID in by_id:
        by_id[GOAL09_WORKFLOW_ID].update(patch)
    else:
        insert_at = next((index + 1 for index, item in enumerate(rows) if item["workflow_id"] == GOAL090_WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": GOAL09_WORKFLOW_ID, **patch})
        by_id = {row["workflow_id"]: row for row in rows}
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


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    if not path.exists():
        return
    payload = read_json(path)
    payload[GOAL09_WORKFLOW_ID] = GOAL09_IMPLEMENTED_STATUS if result["status"] != BLOCKED else "future_review_only"
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
    matches: list[str] = []
    allowed = {DIAGNOSTIC_PATH, POLICY_PATH, DOC_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH}
    for rel in tracked:
        if rel in allowed:
            continue
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

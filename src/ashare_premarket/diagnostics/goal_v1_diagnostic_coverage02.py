from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.constants import APPROVED_SYMBOLS
from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import (
    preserve_later_review_only_capabilities,
    preserve_later_review_only_workflow_states,
)
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.labels.goal_data_label01 import goal_data_label01_valid_forward_return_label_coverage_evidence
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-V1-DIAGNOSTIC-COVERAGE-02"
GOAL_NAME = "GOAL-V1-DIAGNOSTIC-COVERAGE-02-MULTI-SYMBOL-DIAGNOSTICS-EXPANSION"
MODE = "review_only_multi_symbol_diagnostic_coverage_expansion"
WORKFLOW_ID = "goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"
GOAL_DATA_LABEL01_WORKFLOW_ID = "goal_data_label01_forward_return_label_coverage_expansion"
GOAL10B2_WORKFLOW_ID = "goal10b2_recommendation_backtest_revalidation"
GOAL10C_WORKFLOW_ID = "goal10c_backtest_cost_slippage_sensitivity_gate"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
ALLOWED_NEXT = "request_goal10b2_recommendation_backtest_revalidation_or_fix_diagnostic_coverage_warnings"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

SOURCE_STAGE6C_PATH = "outputs/stage6c/STAGE6C_engineering_expanded_validation_dataset_sample.csv"
GOAL_DATA_LABEL01_SAMPLE_PATH = "outputs/labels/goal_data_label01_forward_return_label_coverage_sample.csv"
GOAL08B_DIAGNOSTICS_PATH = "outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv"
GOAL09_DIAGNOSTICS_PATH = "outputs/position/goal09_review_only_position_band_diagnostics.csv"

DIAGNOSTICS_DIR = "outputs/diagnostics"
RISK_DIAGNOSTICS_PATH = f"{DIAGNOSTICS_DIR}/goal_v1_diagnostic_coverage02_risk_diagnostics.csv"
RECOMMENDATION_DIAGNOSTICS_PATH = f"{DIAGNOSTICS_DIR}/goal_v1_diagnostic_coverage02_recommendation_diagnostics.csv"
POSITION_DIAGNOSTICS_PATH = f"{DIAGNOSTICS_DIR}/goal_v1_diagnostic_coverage02_position_band_diagnostics.csv"
COVERAGE_SUMMARY_PATH = f"{DIAGNOSTICS_DIR}/goal_v1_diagnostic_coverage02_coverage_summary.csv"
REPORT_PATH = "outputs/audits/goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_report.md"
MANIFEST_PATH = "outputs/audits/goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_manifest.json"
AUDIT_PATH = "outputs/audits/goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_audit.md"
DOC_PATH = "docs/diagnostics/GOAL_V1_DIAGNOSTIC_COVERAGE02_MULTI_SYMBOL_DIAGNOSTICS_EXPANSION.md"

RISK_FIELDS = [
    "trade_date",
    "symbol",
    "as_of_date",
    "diagnostic_type",
    "risk_diagnostic_status",
    "risk_severity",
    "risk_blocker_code",
    "source_stage6c_path",
    "source_panel_tier",
    "source_bundle_id",
    "forward_return_1d",
    "benchmark_forward_return_1d",
    "excess_forward_return_1d",
    "forward_return_3d",
    "forward_return_5d",
    "forward_return_20d",
    "label_coverage_status",
    "approved_symbol_flag",
    "review_only",
    "actionability_block",
    "non_actionable_disclaimer",
    "warning_codes",
]

RECOMMENDATION_FIELDS = [
    "trade_date",
    "symbol",
    "as_of_date",
    "diagnostic_type",
    "recommendation_eligibility_status",
    "recommendation_eligibility_reason",
    "actionability_status",
    "source_risk_severity",
    "risk_blocker_code",
    "source_stage6c_path",
    "forward_return_1d",
    "excess_forward_return_1d",
    "label_coverage_status",
    "review_only",
    "non_actionable_disclaimer",
    "warning_codes",
]

POSITION_FIELDS = [
    "trade_date",
    "symbol",
    "as_of_date",
    "diagnostic_type",
    "position_band_status",
    "position_band_reason",
    "position_actionability_status",
    "source_risk_severity",
    "recommendation_eligibility_status",
    "source_stage6c_path",
    "forward_return_1d",
    "excess_forward_return_1d",
    "label_coverage_status",
    "review_only",
    "non_actionable_disclaimer",
    "warning_codes",
]

COVERAGE_SUMMARY_FIELDS = [
    "diagnostic_area",
    "row_count",
    "unique_symbols",
    "unique_trade_dates",
    "date_min",
    "date_max",
    "approved_symbol_rows",
    "never_actionable_rows",
    "warning_rows",
    "label_20d_ready_rows",
    "canonical_goal08b_overlap_rows",
    "canonical_goal09_overlap_rows",
    "goal_data_label01_overlap_rows",
    "coverage_status",
]

FALSE_BOUNDARY_KEYS = [
    "new_data_fetched",
    "network_ingestion_run",
    "provider_ingestion_modified",
    "data_panel_expanded",
    "local_bundle_files_committed",
    "local_lake_files_created",
    "raw_provider_payloads_committed",
    "canonical_goal07b_rows_created",
    "canonical_goal07b_rows_overwritten",
    "canonical_goal08b_rows_created",
    "canonical_goal08b_rows_overwritten",
    "canonical_goal09_rows_created",
    "canonical_goal09_rows_overwritten",
    "recommendation_rows_generated",
    "actionable_recommendation_rows_generated",
    "position_rows_generated",
    "buy_sell_hold_outputs_generated",
    "target_prices_generated",
    "expected_returns_for_action_generated",
    "position_sizing_generated",
    "actual_position_sizing_generated",
    "order_quantities_generated",
    "target_weights_generated",
    "portfolio_weights_generated",
    "portfolio_returns_generated",
    "equity_curves_generated",
    "portfolio_construction_generated",
    "dashboard_outputs_generated",
    "dashboard_files_generated",
    "html_generated",
    "streamlit_generated",
    "frontend_code_generated",
    "visual_reports_generated",
    "paper_trading_enabled",
    "live_trading_enabled",
    "broker_integration_enabled",
    "production_model_behavior_created",
    "database_writes_created",
    "backtests_run",
    "backtest_execution_run",
    "backtest_performance_rows_generated",
    "signal_backtests_run",
    "portfolio_backtests_run",
    "cost_slippage_outputs_created",
    "factor_mining_outputs_created",
    "dqn_rl_outputs_created",
    "downstream_execution_unlocked_by_this_goal",
]

FORBIDDEN_OUTPUT_DIRS = [
    "outputs/backtests",
    "outputs/equity_curves",
    "outputs/portfolio_returns",
    "outputs/dashboard",
    "outputs/dashboards",
    "outputs/frontend",
    "outputs/streamlit",
    "outputs/visual_reports",
    "outputs/recommendations",
    "outputs/positions",
    "outputs/position_sizing",
    "outputs/position_weights",
    "outputs/orders",
    "outputs/trading",
    "outputs/paper_trading",
    "outputs/live_trading",
    "outputs/broker",
    "outputs/production",
    "outputs/factors",
    "outputs/dqn",
    "outputs/rl",
    "data/raw",
    "data/bundles",
    "data/lake",
    "data/exports",
]

WORKFLOW_PRODUCES_ARTIFACTS = ";".join(
    [
        RISK_DIAGNOSTICS_PATH,
        RECOMMENDATION_DIAGNOSTICS_PATH,
        POSITION_DIAGNOSTICS_PATH,
        COVERAGE_SUMMARY_PATH,
        REPORT_PATH,
        MANIFEST_PATH,
        AUDIT_PATH,
        DOC_PATH,
    ]
)
WORKFLOW_PRIMARY_DOCS = f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md"
WORKFLOW_PRIMARY_SCRIPTS = "scripts/run_goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion.py;scripts/audit_goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion.py"
WORKFLOW_PRIMARY_OUTPUTS = ";".join(
    [
        RISK_DIAGNOSTICS_PATH,
        RECOMMENDATION_DIAGNOSTICS_PATH,
        POSITION_DIAGNOSTICS_PATH,
        COVERAGE_SUMMARY_PATH,
        REPORT_PATH,
        MANIFEST_PATH,
        AUDIT_PATH,
    ]
)
WORKFLOW_NOTES = "Review-only multi-symbol diagnostic coverage expansion from existing committed Stage 6C approved-symbol evidence. It creates separate non-actionable risk, recommendation, and position-band diagnostic coverage rows, does not overwrite canonical GOAL-07B/08B/09 artifacts, and creates no backtest, portfolio, dashboard, trading, production, broker, local-lake, factor-mining, or DQN/RL outputs."


def run_goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion(root: Path) -> bool:
    result = evaluate_goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    risk_rows = _read_csv(root / RISK_DIAGNOSTICS_PATH)
    recommendation_rows = _read_csv(root / RECOMMENDATION_DIAGNOSTICS_PATH)
    position_rows = _read_csv(root / POSITION_DIAGNOSTICS_PATH)
    coverage_rows = _read_csv(root / COVERAGE_SUMMARY_PATH)
    workflow = _workflow_rows(root)
    recheck = evaluate_goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion(root)
    failures: list[str] = []

    if not _report_pass_or_warn(report):
        failures.append("goal_v1_diagnostic_coverage02_report_not_pass_or_warn")
    if recheck["status"] == BLOCKED:
        failures.extend(f"recheck:{failure}" for failure in recheck["failures"])
    if manifest.get("goal") != GOAL_NAME:
        failures.append("manifest_goal_invalid")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_invalid")
    if manifest.get("status") not in {PASS, PASS_WITH_WARNINGS}:
        failures.append("manifest_status_invalid")
    for key in [
        "multi_symbol_diagnostics_generated",
        "risk_diagnostics_rows_generated",
        "recommendation_diagnostics_rows_generated",
        "position_band_diagnostics_rows_generated",
        "keys_match_across_risk_recommendation_position",
        "approved_symbols_only",
        "used_committed_stage6c_evidence_only",
        "canonical_goal07b_goal08b_goal09_preserved",
        "goal10b2_locked_future",
        "goal10c_locked_future",
        "goal10d_locked_future",
        "dashboard_daily_report_locked_future",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"manifest_{key}_not_false")
    if manifest.get("forward_return_20d_available") is not False:
        failures.append("manifest_forward_return_20d_available_not_false")
    if manifest.get("multi_horizon_backtest_ready") is not False:
        failures.append("manifest_multi_horizon_backtest_ready_not_false")
    if not risk_rows:
        failures.append("risk_diagnostics_missing")
    elif set(risk_rows[0]) != set(RISK_FIELDS):
        failures.append("risk_diagnostics_fields_invalid")
    if not recommendation_rows:
        failures.append("recommendation_diagnostics_missing")
    elif set(recommendation_rows[0]) != set(RECOMMENDATION_FIELDS):
        failures.append("recommendation_diagnostics_fields_invalid")
    elif {row.get("actionability_status", "") for row in recommendation_rows} != {"never_actionable"}:
        failures.append("recommendation_actionability_not_never_actionable")
    if not position_rows:
        failures.append("position_diagnostics_missing")
    elif set(position_rows[0]) != set(POSITION_FIELDS):
        failures.append("position_diagnostics_fields_invalid")
    elif {row.get("position_actionability_status", "") for row in position_rows} != {"never_actionable"}:
        failures.append("position_actionability_not_never_actionable")
    if not coverage_rows:
        failures.append("coverage_summary_missing")
    elif set(coverage_rows[0]) != set(COVERAGE_SUMMARY_FIELDS):
        failures.append("coverage_summary_fields_invalid")
    if _keys(risk_rows) != _keys(recommendation_rows) or _keys(risk_rows) != _keys(position_rows):
        failures.append("diagnostic_keys_do_not_match")

    row = workflow.get(WORKFLOW_ID, {})
    if row.get("status") != "implemented_review_only":
        failures.append("goal_v1_diagnostic_coverage02_workflow_not_implemented_review_only")
    if row.get("implemented_in_repo") != "true":
        failures.append("goal_v1_diagnostic_coverage02_workflow_not_marked_implemented")
    if row.get("depends_on") != GOAL_DATA_LABEL01_WORKFLOW_ID:
        failures.append("goal_v1_diagnostic_coverage02_depends_on_invalid")
    if row.get("allowed_next_action") != ALLOWED_NEXT:
        failures.append("goal_v1_diagnostic_coverage02_allowed_next_invalid")
    for workflow_id, dependency in [
        (GOAL10B2_WORKFLOW_ID, WORKFLOW_ID),
        (GOAL10C_WORKFLOW_ID, GOAL10B2_WORKFLOW_ID),
    ]:
        target = workflow.get(workflow_id, {})
        if target.get("status") not in {"locked_future", "implemented_review_only"}:
            failures.append(f"{workflow_id}_invalid_status")
        if target.get("status") == "implemented_review_only":
            if target.get("implemented_in_repo") != "true":
                failures.append(f"{workflow_id}_not_marked_implemented")
        elif target.get("implemented_in_repo") != "false":
            failures.append(f"{workflow_id}_marked_implemented")
        if target.get("depends_on") != dependency:
            failures.append(f"{workflow_id}_dependency_invalid")
    target = workflow.get(GOAL10D_WORKFLOW_ID, {})
    if target.get("status") != "locked_future":
        failures.append(f"{GOAL10D_WORKFLOW_ID}_not_locked_future")
    if target.get("implemented_in_repo") != "false":
        failures.append(f"{GOAL10D_WORKFLOW_ID}_marked_implemented")
    if target.get("depends_on") != GOAL10C_WORKFLOW_ID:
        failures.append(f"{GOAL10D_WORKFLOW_ID}_dependency_invalid")
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
        downstream = workflow.get(workflow_id, {})
        if downstream.get("status") != "locked_future":
            failures.append(f"{workflow_id}_not_locked_future")
        if downstream.get("implemented_in_repo") != "false":
            failures.append(f"{workflow_id}_marked_implemented")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))

    status = PASS if not failures else BLOCKED
    write_text(
        root / AUDIT_PATH,
        "\n".join(
            [
                "# GOAL-V1-DIAGNOSTIC-COVERAGE-02 Multi-Symbol Diagnostics Expansion Audit",
                "",
                f"Status: `{status}`",
                "",
                f"Risk rows: `{len(risk_rows)}`",
                f"Recommendation rows: `{len(recommendation_rows)}`",
                f"Position-band rows: `{len(position_rows)}`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == PASS


def evaluate_goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion(root: Path) -> dict[str, object]:
    source_rows = _read_csv(root / SOURCE_STAGE6C_PATH)
    label_rows = _read_csv(root / GOAL_DATA_LABEL01_SAMPLE_PATH)
    goal08b_rows = _read_csv(root / GOAL08B_DIAGNOSTICS_PATH)
    goal09_rows = _read_csv(root / GOAL09_DIAGNOSTICS_PATH)
    failures: list[str] = []
    warnings: list[str] = []

    if not goal_data_label01_valid_forward_return_label_coverage_evidence(root):
        failures.append("goal_data_label01_prerequisite_not_valid")
    if not source_rows:
        failures.append("stage6c_engineering_source_missing_or_empty")
    elif not _required_source_fields().issubset(source_rows[0]):
        missing = sorted(_required_source_fields() - set(source_rows[0]))
        failures.append(f"stage6c_engineering_source_missing_fields:{';'.join(missing)}")

    keys = [(row.get("trade_date", ""), row.get("symbol", "")) for row in source_rows]
    if len(keys) != len(set(keys)):
        failures.append("stage6c_engineering_source_duplicate_trade_date_symbol")
    symbols = sorted({symbol for _, symbol in keys if symbol})
    if len(symbols) < 2:
        failures.append("stage6c_engineering_source_not_multi_symbol")
    unexpected_symbols = sorted(set(symbols) - set(APPROVED_SYMBOLS))
    if unexpected_symbols:
        failures.append(f"stage6c_engineering_source_contains_unapproved_symbols:{';'.join(unexpected_symbols)}")
    if any(row.get("review_only", "").lower() != "true" for row in source_rows):
        failures.append("stage6c_engineering_source_not_review_only")

    if any(not row.get("fwd_20d_return", "") for row in source_rows):
        warnings.append("forward_return_20d_not_available_for_multi_symbol_diagnostics")
    if any(not row.get("fwd_3d_return", "") or not row.get("fwd_5d_return", "") for row in source_rows):
        warnings.append("forward_return_3d_5d_incomplete_in_multi_symbol_source")
    if any("CONTRACT_DEMO" in row.get("data_quality_flags", "") for row in source_rows):
        warnings.append("multi_symbol_source_uses_contract_demo_fixture")
    if _overlap(source_rows, label_rows) == 0:
        warnings.append("goal_data_label01_no_trade_date_symbol_overlap_with_multi_symbol_diagnostics")
    if _overlap(source_rows, goal08b_rows) == 0:
        warnings.append("canonical_goal08b_not_aligned_to_multi_symbol_diagnostics")
    if _overlap(source_rows, goal09_rows) == 0:
        warnings.append("canonical_goal09_not_aligned_to_multi_symbol_diagnostics")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))

    risk_rows = _risk_rows(source_rows) if not failures else []
    recommendation_rows = _recommendation_rows(risk_rows) if not failures else []
    position_rows = _position_rows(recommendation_rows) if not failures else []
    coverage_rows = _coverage_rows(risk_rows, recommendation_rows, position_rows, label_rows, goal08b_rows, goal09_rows)
    status = BLOCKED if failures else PASS_WITH_WARNINGS if warnings else PASS
    manifest = _manifest(status, failures, warnings, risk_rows, recommendation_rows, position_rows, coverage_rows, label_rows, goal08b_rows, goal09_rows)
    return {
        "status": status,
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "risk_rows": risk_rows,
        "recommendation_rows": recommendation_rows,
        "position_rows": position_rows,
        "coverage_rows": coverage_rows,
        "manifest": manifest,
    }


def goal_v1_diagnostic_coverage02_valid_multi_symbol_diagnostic_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        _report_pass_or_warn(report)
        and "Status: `PASS`" in audit
        and manifest.get("goal") == GOAL_NAME
        and manifest.get("mode") == MODE
        and manifest.get("multi_symbol_diagnostics_generated") is True
        and manifest.get("keys_match_across_risk_recommendation_position") is True
        and manifest.get("approved_symbols_only") is True
        and int(manifest.get("unique_symbols", 0) or 0) >= 2
        and int(manifest.get("risk_diagnostic_row_count", 0) or 0) > 0
        and manifest.get("forward_return_20d_available") is False
        and manifest.get("multi_horizon_backtest_ready") is False
        and manifest.get("goal10b2_locked_future") is True
        and manifest.get("backtests_run") is False
        and manifest.get("portfolio_returns_generated") is False
        and manifest.get("dashboard_outputs_generated") is False
    )


def goal_v1_diagnostic_coverage02_implemented_workflow_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-V1-DIAGNOSTIC-COVERAGE-02 Multi-Symbol Diagnostics Expansion",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_review_only",
        "current_repo_role": "review_only_multi_symbol_diagnostic_coverage_gate",
        "implemented_in_repo": "true",
        "allowed_next_action": ALLOWED_NEXT,
        "depends_on": GOAL_DATA_LABEL01_WORKFLOW_ID,
        "produces_artifacts": WORKFLOW_PRODUCES_ARTIFACTS,
        "primary_docs": WORKFLOW_PRIMARY_DOCS,
        "primary_scripts": WORKFLOW_PRIMARY_SCRIPTS,
        "primary_outputs": WORKFLOW_PRIMARY_OUTPUTS,
        "promotion_rule": "implemented_review_only_after_goal_v1_diagnostic_coverage02_pass_with_warnings",
        "notes": WORKFLOW_NOTES,
    }


def locked_goal10b2_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-10B.2 Recommendation Backtest Revalidation",
        "stage_or_goal": "GOAL-10B.2",
        "status": "locked_future",
        "current_repo_role": "locked_future_recommendation_backtest_revalidation",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10b2_request_after_diagnostic_coverage_warning_acceptance",
        "depends_on": WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal10b2_revalidation_gate",
        "notes": "Future recommendation backtest revalidation remains locked. GOAL-V1-DIAGNOSTIC-COVERAGE-02 creates non-actionable multi-symbol diagnostics but still warns that 20d multi-symbol label alignment is unavailable.",
    }


def locked_goal10c_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-10C Backtest Cost / Slippage Sensitivity",
        "stage_or_goal": "GOAL-10C",
        "status": "locked_future",
        "current_repo_role": "locked_future_backtest_sensitivity",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10c_request",
        "depends_on": GOAL10B2_WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_goal10b2_revalidation_passes",
        "notes": "Future GOAL-10C backtest work remains locked; this diagnostic coverage gate creates no backtest rows, portfolio returns, or cost/slippage outputs.",
    }


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / RISK_DIAGNOSTICS_PATH, result["risk_rows"], RISK_FIELDS)
    write_csv(root / RECOMMENDATION_DIAGNOSTICS_PATH, result["recommendation_rows"], RECOMMENDATION_FIELDS)
    write_csv(root / POSITION_DIAGNOSTICS_PATH, result["position_rows"], POSITION_FIELDS)
    write_csv(root / COVERAGE_SUMMARY_PATH, result["coverage_rows"], COVERAGE_SUMMARY_FIELDS)
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_report(root, result)
    _write_doc(root, result)


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    write_text(
        root / REPORT_PATH,
        "\n".join(
            [
                "# GOAL-V1-DIAGNOSTIC-COVERAGE-02 Multi-Symbol Diagnostics Expansion",
                "",
                f"GOAL-V1-DIAGNOSTIC-COVERAGE-02 Multi-Symbol Diagnostics Expansion: {result['status']}",
                f"Mode: `{MODE}`",
                "",
                "## Coverage",
                f"- Source Stage 6C sample: `{SOURCE_STAGE6C_PATH}`",
                f"- Risk diagnostic rows: `{manifest['risk_diagnostic_row_count']}`",
                f"- Recommendation diagnostic rows: `{manifest['recommendation_diagnostic_row_count']}`",
                f"- Position-band diagnostic rows: `{manifest['position_band_diagnostic_row_count']}`",
                f"- Unique symbols: `{manifest['unique_symbols']}`",
                f"- Unique trade dates: `{manifest['unique_trade_dates']}`",
                f"- Keys match across diagnostic families: `{str(manifest['keys_match_across_risk_recommendation_position']).lower()}`",
                "",
                "## Boundary",
                "- Diagnostics are derived only from existing committed Stage 6C approved-symbol evidence.",
                "- Canonical GOAL-07B, GOAL-08B, and GOAL-09 artifacts are preserved and not overwritten.",
                "- All recommendation and position-band outputs are `never_actionable` and are not buy/sell/hold actions, target prices, position sizes, weights, orders, or portfolio instructions.",
                "- GOAL-10B.2 and GOAL-10C may only exist as explicit review-only non-actionable diagnostic gates over this bounded coverage. GOAL-10D, Dashboard / Daily Report UI, signal and portfolio backtest promotion, trading, production, broker, local-lake, factor-mining, and DQN/RL remain locked.",
                "",
                "## Warnings",
                *[f"- {warning}" for warning in result["warnings"]],
                "",
                "## Failures",
                *[f"- {failure}" for failure in result["failures"]],
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
                "# GOAL-V1-DIAGNOSTIC-COVERAGE-02 Multi-Symbol Diagnostics Expansion",
                "",
                f"Status: `{result['status']}`",
                "",
                "GOAL-V1-DIAGNOSTIC-COVERAGE-02 creates a bounded review-only diagnostic coverage bridge for the next revalidation request. It uses the committed Stage 6C approved-symbol sample to generate separate non-actionable risk, recommendation, and position-band diagnostic coverage rows at `trade_date + symbol` grain.",
                "",
                "It does not overwrite the canonical GOAL-07B, GOAL-08B, or GOAL-09 artifacts and does not run any backtest.",
                "",
                "## Outputs",
                "",
                f"- `{RISK_DIAGNOSTICS_PATH}`",
                f"- `{RECOMMENDATION_DIAGNOSTICS_PATH}`",
                f"- `{POSITION_DIAGNOSTICS_PATH}`",
                f"- `{COVERAGE_SUMMARY_PATH}`",
                f"- `{REPORT_PATH}`",
                f"- `{MANIFEST_PATH}`",
                f"- `{AUDIT_PATH}`",
                "",
                "## Current Coverage",
                "",
                f"- Diagnostic rows per family: `{manifest['risk_diagnostic_row_count']}`",
                f"- Unique symbols: `{manifest['unique_symbols']}`",
                f"- Unique trade dates: `{manifest['unique_trade_dates']}`",
                f"- Forward-return 20d available: `{str(manifest['forward_return_20d_available']).lower()}`",
                f"- Multi-horizon backtest ready: `{str(manifest['multi_horizon_backtest_ready']).lower()}`",
                "",
                "## Locked Boundary",
                "",
                "GOAL-10B.2 and GOAL-10C may only exist as explicit review-only non-actionable diagnostic gates over this bounded coverage. GOAL-10D, Dashboard / Daily Report UI, signal and portfolio backtest promotion, trading, production, broker integration, local-lake writes, factor-mining, and DQN/RL remain locked.",
                "",
            ]
        ),
    )


def _manifest(
    status: str,
    failures: list[str],
    warnings: list[str],
    risk_rows: list[dict[str, object]],
    recommendation_rows: list[dict[str, object]],
    position_rows: list[dict[str, object]],
    coverage_rows: list[dict[str, object]],
    label_rows: list[dict[str, str]],
    goal08b_rows: list[dict[str, str]],
    goal09_rows: list[dict[str, str]],
) -> dict[str, object]:
    keys_match = _keys(risk_rows) == _keys(recommendation_rows) == _keys(position_rows)
    symbols = sorted({str(row.get("symbol", "")) for row in risk_rows if row.get("symbol", "")})
    dates = sorted({str(row.get("trade_date", "")) for row in risk_rows if row.get("trade_date", "")})
    label_20d_ready_rows = sum(1 for row in risk_rows if row.get("forward_return_20d", ""))
    return {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "status": status,
        "mode": MODE,
        "allowed_next_action": ALLOWED_NEXT if status != BLOCKED else "repair_goal_v1_diagnostic_coverage02_blockers",
        "recommended_next_goal": "GOAL-10B.2",
        "source_stage6c_path": SOURCE_STAGE6C_PATH,
        "risk_output_path": RISK_DIAGNOSTICS_PATH,
        "recommendation_output_path": RECOMMENDATION_DIAGNOSTICS_PATH,
        "position_output_path": POSITION_DIAGNOSTICS_PATH,
        "risk_diagnostic_row_count": len(risk_rows),
        "recommendation_diagnostic_row_count": len(recommendation_rows),
        "position_band_diagnostic_row_count": len(position_rows),
        "coverage_summary_rows": len(coverage_rows),
        "unique_symbols": len(symbols),
        "symbols": symbols,
        "unique_trade_dates": len(dates),
        "date_min": dates[0] if dates else "",
        "date_max": dates[-1] if dates else "",
        "multi_symbol_diagnostics_generated": status != BLOCKED,
        "risk_diagnostics_rows_generated": bool(risk_rows),
        "recommendation_diagnostics_rows_generated": bool(recommendation_rows),
        "position_band_diagnostics_rows_generated": bool(position_rows),
        "keys_match_across_risk_recommendation_position": keys_match,
        "approved_symbols_only": not (set(symbols) - set(APPROVED_SYMBOLS)),
        "used_committed_stage6c_evidence_only": True,
        "canonical_goal07b_goal08b_goal09_preserved": True,
        "actionability_status_values": sorted({str(row.get("actionability_status", "")) for row in recommendation_rows if row.get("actionability_status", "")}),
        "position_actionability_status_values": sorted({str(row.get("position_actionability_status", "")) for row in position_rows if row.get("position_actionability_status", "")}),
        "forward_return_20d_available": label_20d_ready_rows > 0,
        "multi_horizon_backtest_ready": False,
        "goal_data_label01_overlap_rows": _overlap(risk_rows, label_rows),
        "canonical_goal08b_overlap_rows": _overlap(risk_rows, goal08b_rows),
        "canonical_goal09_overlap_rows": _overlap(risk_rows, goal09_rows),
        "goal_v1_diagnostic_coverage02_status_after_gate": "implemented_review_only" if status != BLOCKED else "locked_future",
        "goal10b2_status_after_goal_v1_diagnostic_coverage02": "locked_future",
        "goal10c_status_after_goal_v1_diagnostic_coverage02": "locked_future",
        "goal10d_status_after_goal_v1_diagnostic_coverage02": "locked_future",
        "dashboard_daily_report_status_after_goal_v1_diagnostic_coverage02": "locked_future",
        "goal10b2_locked_future": True,
        "goal10c_locked_future": True,
        "goal10d_locked_future": True,
        "dashboard_daily_report_locked_future": True,
        "input_artifacts": [SOURCE_STAGE6C_PATH, GOAL_DATA_LABEL01_SAMPLE_PATH, GOAL08B_DIAGNOSTICS_PATH, GOAL09_DIAGNOSTICS_PATH],
        "output_artifacts": [RISK_DIAGNOSTICS_PATH, RECOMMENDATION_DIAGNOSTICS_PATH, POSITION_DIAGNOSTICS_PATH, COVERAGE_SUMMARY_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH],
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        **{key: False for key in FALSE_BOUNDARY_KEYS},
    }


def _risk_rows(source_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in sorted(source_rows, key=lambda item: (item.get("trade_date", ""), item.get("symbol", ""))):
        missing = []
        if not row.get("fwd_3d_return", ""):
            missing.append("MISSING_3D_FORWARD_RETURN")
        if not row.get("fwd_5d_return", ""):
            missing.append("MISSING_5D_FORWARD_RETURN")
        missing.append("MISSING_20D_FORWARD_RETURN")
        warning_codes = ";".join(sorted(set(missing + ["REVIEW_ONLY_DIAGNOSTIC_COVERAGE"])))
        rows.append(
            {
                "trade_date": row.get("trade_date", ""),
                "symbol": row.get("symbol", ""),
                "as_of_date": row.get("as_of_date", ""),
                "diagnostic_type": "risk_coverage_diagnostic",
                "risk_diagnostic_status": "blocked_review_only_multihorizon_incomplete",
                "risk_severity": "HIGH",
                "risk_blocker_code": "insufficient_multihorizon_forward_return_alignment",
                "source_stage6c_path": SOURCE_STAGE6C_PATH,
                "source_panel_tier": row.get("panel_tier", ""),
                "source_bundle_id": row.get("source_bundle_id", ""),
                "forward_return_1d": row.get("fwd_1d_return", ""),
                "benchmark_forward_return_1d": row.get("benchmark_fwd_1d_return", ""),
                "excess_forward_return_1d": row.get("excess_fwd_1d_return", ""),
                "forward_return_3d": row.get("fwd_3d_return", ""),
                "forward_return_5d": row.get("fwd_5d_return", ""),
                "forward_return_20d": "",
                "label_coverage_status": "1d_only_multi_symbol_20d_missing",
                "approved_symbol_flag": row.get("symbol", "") in APPROVED_SYMBOLS,
                "review_only": True,
                "actionability_block": True,
                "non_actionable_disclaimer": "diagnostic_only_not_investment_advice_not_trade_instruction",
                "warning_codes": warning_codes,
            }
        )
    return rows


def _recommendation_rows(risk_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in risk_rows:
        rows.append(
            {
                "trade_date": row.get("trade_date", ""),
                "symbol": row.get("symbol", ""),
                "as_of_date": row.get("as_of_date", ""),
                "diagnostic_type": "recommendation_coverage_diagnostic",
                "recommendation_eligibility_status": "blocked_review_only_multihorizon_incomplete",
                "recommendation_eligibility_reason": "multi_symbol_diagnostics_exist_but_20d_label_alignment_missing",
                "actionability_status": "never_actionable",
                "source_risk_severity": row.get("risk_severity", ""),
                "risk_blocker_code": row.get("risk_blocker_code", ""),
                "source_stage6c_path": SOURCE_STAGE6C_PATH,
                "forward_return_1d": row.get("forward_return_1d", ""),
                "excess_forward_return_1d": row.get("excess_forward_return_1d", ""),
                "label_coverage_status": row.get("label_coverage_status", ""),
                "review_only": True,
                "non_actionable_disclaimer": "diagnostic_only_not_investment_advice_not_trade_instruction",
                "warning_codes": row.get("warning_codes", ""),
            }
        )
    return rows


def _position_rows(recommendation_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in recommendation_rows:
        rows.append(
            {
                "trade_date": row.get("trade_date", ""),
                "symbol": row.get("symbol", ""),
                "as_of_date": row.get("as_of_date", ""),
                "diagnostic_type": "position_band_coverage_diagnostic",
                "position_band_status": "blocked_review_only_no_position_instruction",
                "position_band_reason": "recommendation_diagnostic_never_actionable_and_multihorizon_alignment_incomplete",
                "position_actionability_status": "never_actionable",
                "source_risk_severity": row.get("source_risk_severity", ""),
                "recommendation_eligibility_status": row.get("recommendation_eligibility_status", ""),
                "source_stage6c_path": SOURCE_STAGE6C_PATH,
                "forward_return_1d": row.get("forward_return_1d", ""),
                "excess_forward_return_1d": row.get("excess_forward_return_1d", ""),
                "label_coverage_status": row.get("label_coverage_status", ""),
                "review_only": True,
                "non_actionable_disclaimer": "diagnostic_only_not_investment_advice_not_trade_instruction",
                "warning_codes": row.get("warning_codes", ""),
            }
        )
    return rows


def _coverage_rows(
    risk_rows: list[dict[str, object]],
    recommendation_rows: list[dict[str, object]],
    position_rows: list[dict[str, object]],
    label_rows: list[dict[str, str]],
    goal08b_rows: list[dict[str, str]],
    goal09_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    rows_by_area = {
        "risk": risk_rows,
        "recommendation": recommendation_rows,
        "position_band": position_rows,
    }
    output: list[dict[str, object]] = []
    for area, rows in rows_by_area.items():
        dates = sorted({str(row.get("trade_date", "")) for row in rows if row.get("trade_date", "")})
        symbols = sorted({str(row.get("symbol", "")) for row in rows if row.get("symbol", "")})
        never_actionable = sum(
            1
            for row in rows
            if row.get("actionability_status") == "never_actionable" or row.get("position_actionability_status") == "never_actionable"
        )
        output.append(
            {
                "diagnostic_area": area,
                "row_count": len(rows),
                "unique_symbols": len(symbols),
                "unique_trade_dates": len(dates),
                "date_min": dates[0] if dates else "",
                "date_max": dates[-1] if dates else "",
                "approved_symbol_rows": sum(1 for row in rows if row.get("symbol", "") in APPROVED_SYMBOLS),
                "never_actionable_rows": never_actionable,
                "warning_rows": sum(1 for row in rows if row.get("warning_codes", "")),
                "label_20d_ready_rows": sum(1 for row in rows if row.get("forward_return_20d", "")),
                "canonical_goal08b_overlap_rows": _overlap(rows, goal08b_rows),
                "canonical_goal09_overlap_rows": _overlap(rows, goal09_rows),
                "goal_data_label01_overlap_rows": _overlap(rows, label_rows),
                "coverage_status": "review_only_multi_symbol_20d_incomplete",
            }
        )
    return output


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys())
    by_id = {row["workflow_id"]: row for row in rows}
    patch = goal_v1_diagnostic_coverage02_implemented_workflow_patch()
    if result["status"] == BLOCKED:
        patch.update(
            {
                "status": "locked_future",
                "current_repo_role": "review_only_multi_symbol_diagnostic_coverage_blocked",
                "implemented_in_repo": "false",
                "allowed_next_action": "repair_goal_v1_diagnostic_coverage02_blockers",
                "produces_artifacts": "",
                "primary_scripts": "",
                "primary_outputs": "",
                "promotion_rule": "locked_until_goal_v1_diagnostic_coverage02_passes",
                "notes": "GOAL-V1-DIAGNOSTIC-COVERAGE-02 is blocked; GOAL-10B.2 and downstream backtest goals remain locked.",
            }
        )
    _upsert_workflow_row(rows, by_id, WORKFLOW_ID, patch, after=GOAL_DATA_LABEL01_WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL10B2_WORKFLOW_ID, locked_goal10b2_patch(), after=WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL10C_WORKFLOW_ID, locked_goal10c_patch(), after=GOAL10B2_WORKFLOW_ID)
    for workflow_id in [
        GOAL10D_WORKFLOW_ID,
        "dashboard_daily_report",
        "signal_backtest",
        "portfolio_backtest",
        "cost_slippage_sensitivity",
        "paper_trading_journal",
        "failure_attribution",
        "production_hardening",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
    ]:
        if workflow_id in by_id:
            by_id[workflow_id]["status"] = "locked_future"
            by_id[workflow_id]["implemented_in_repo"] = "false"
    if GOAL10D_WORKFLOW_ID in by_id:
        by_id[GOAL10D_WORKFLOW_ID]["depends_on"] = GOAL10C_WORKFLOW_ID
    if "dashboard_daily_report" in by_id:
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_v1_diagnostic_coverage02"
    if "dqn_rl_mainline" in by_id:
        by_id["dqn_rl_mainline"]["status"] = "deleted_from_active_mainline"
        by_id["dqn_rl_mainline"]["implemented_in_repo"] = "false"
    if "v2_factor_research_upgrade" in by_id:
        by_id["v2_factor_research_upgrade"]["status"] = "planned_locked"
        by_id["v2_factor_research_upgrade"]["implemented_in_repo"] = "false"
    preserve_later_review_only_workflow_states(root, by_id)
    if result["status"] != BLOCKED and WORKFLOW_ID in by_id:
        by_id[WORKFLOW_ID].update(goal_v1_diagnostic_coverage02_implemented_workflow_patch())
    write_csv(path, rows, fields)


def _upsert_workflow_row(
    rows: list[dict[str, str]],
    by_id: dict[str, dict[str, str]],
    workflow_id: str,
    patch: dict[str, str],
    *,
    after: str,
) -> None:
    if workflow_id in by_id:
        by_id[workflow_id].update(patch)
        return
    insert_at = next((index + 1 for index, item in enumerate(rows) if item["workflow_id"] == after), len(rows))
    row = {"workflow_id": workflow_id, **patch}
    rows.insert(insert_at, row)
    by_id[workflow_id] = row


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    if not path.exists():
        return
    payload = read_json(path)
    payload[WORKFLOW_ID] = "implemented_review_only" if result["status"] != BLOCKED else False
    payload[GOAL10B2_WORKFLOW_ID] = False
    payload[GOAL10C_WORKFLOW_ID] = False
    payload[GOAL10D_WORKFLOW_ID] = False
    for key in [
        "signal_backtest",
        "portfolio_backtest",
        "dashboard",
        "paper_trading",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
        "dqn_rl",
        "factor_mining",
        "local_lake",
    ]:
        payload[key] = False
    preserve_later_review_only_capabilities(root, payload)
    if result["status"] != BLOCKED:
        payload[WORKFLOW_ID] = "implemented_review_only"
    write_json(path, payload)


def _required_source_fields() -> set[str]:
    return {
        "trade_date",
        "symbol",
        "as_of_date",
        "fwd_1d_return",
        "benchmark_fwd_1d_return",
        "excess_fwd_1d_return",
        "review_only",
        "panel_tier",
        "source_bundle_id",
        "data_quality_flags",
    }


def _overlap(left_rows: list[dict[str, object]], right_rows: list[dict[str, object]]) -> int:
    right_keys = {(str(row.get("trade_date", "")), str(row.get("symbol", ""))) for row in right_rows if row.get("trade_date") and row.get("symbol")}
    return sum(1 for row in left_rows if (str(row.get("trade_date", "")), str(row.get("symbol", ""))) in right_keys)


def _keys(rows: list[dict[str, object]]) -> set[tuple[str, str]]:
    return {(str(row.get("trade_date", "")), str(row.get("symbol", ""))) for row in rows if row.get("trade_date") and row.get("symbol")}


def _forbidden_outputs_present(root: Path) -> list[str]:
    return [path for path in FORBIDDEN_OUTPUT_DIRS if (root / path).exists()]


def _workflow_rows(root: Path) -> dict[str, dict[str, str]]:
    path = root / "configs/project/workflow_status.csv"
    if not path.exists():
        return {}
    return {row["workflow_id"]: row for row in read_csv(path)}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    return read_csv(path)


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return read_json(path)
    except Exception:
        return {}


def _report_pass_or_warn(text: str) -> bool:
    prefix = "GOAL-V1-DIAGNOSTIC-COVERAGE-02 Multi-Symbol Diagnostics Expansion:"
    return f"{prefix} {PASS}" in text or f"{prefix} {PASS_WITH_WARNINGS}" in text

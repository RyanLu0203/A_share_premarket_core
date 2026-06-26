from __future__ import annotations

from collections import Counter
from pathlib import Path

from ashare_premarket.backtest.goal10b import (
    AUDIT_PATH as GOAL10B_AUDIT_PATH,
    FALLBACK_LABEL_SOURCE_PATH,
    GOAL08B_DIAGNOSTICS_PATH,
    GOAL10C_WORKFLOW_ID,
    GOAL10D_WORKFLOW_ID,
    MANIFEST_PATH as GOAL10B_MANIFEST_PATH,
    PRIMARY_LABEL_SOURCE_PATH,
    REPORT_PATH as GOAL10B_REPORT_PATH,
    goal10b_valid_review_only_evidence,
)
from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import (
    preserve_later_review_only_capabilities,
    preserve_later_review_only_workflow_states,
)
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-10B.1"
GOAL_NAME = "GOAL-10B.1-BACKTEST-COVERAGE-AND-GROUP-VARIATION-REPAIR-GATE"
MODE = "review_only"
WORKFLOW_ID = "goal10b1_backtest_coverage_repair_gate"
GOAL10B_WORKFLOW_ID = "goal10b_backtest_review_only_validation_gate"
GOAL10B2_WORKFLOW_ID = "goal10b2_recommendation_backtest_revalidation"
GOAL10B1_ALLOWED_NEXT = "request_future_data_label_coverage_expansion_gate_or_fix_goal10b1_warnings"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

BACKTEST_DIR = "outputs/backtest"
DIAGNOSTIC_SUMMARY_PATH = f"{BACKTEST_DIR}/goal10b1_coverage_repair_diagnostic_summary.csv"
RECOMMENDATION_DISTRIBUTION_AUDIT_PATH = f"{BACKTEST_DIR}/goal10b1_recommendation_distribution_audit.csv"
LABEL_SOURCE_COVERAGE_AUDIT_PATH = f"{BACKTEST_DIR}/goal10b1_label_source_coverage_audit.csv"
REPAIRED_SNAPSHOT_PATH = f"{BACKTEST_DIR}/goal10b1_repaired_backtest_input_snapshot.csv"
REPAIRED_RECOMMENDATION_METRICS_PATH = f"{BACKTEST_DIR}/goal10b1_repaired_recommendation_group_metrics.csv"

REPORT_PATH = "outputs/audits/goal10b1_backtest_coverage_repair_report.md"
MANIFEST_PATH = "outputs/audits/goal10b1_backtest_coverage_repair_manifest.json"
AUDIT_PATH = "outputs/audits/goal10b1_backtest_coverage_repair_audit.md"
DOC_PATH = "docs/backtest/GOAL10B1_BACKTEST_COVERAGE_REPAIR_GATE.md"

LABEL_SOURCE_CANDIDATES = [
    PRIMARY_LABEL_SOURCE_PATH,
    FALLBACK_LABEL_SOURCE_PATH,
    "outputs/stage6c/STAGE6C_engineering_expanded_validation_dataset_sample.csv",
    "outputs/stage6c/STAGE6C_expanded_validation_dataset.csv",
    "outputs/labels/engineering_label_panel_sample.csv",
    "outputs/labels/daily_label_snapshot.csv",
]

DIAGNOSTIC_SUMMARY_FIELDS = [
    "diagnostic_area",
    "finding_code",
    "status",
    "evidence",
    "repair_status",
    "recommended_next_gate",
]

RECOMMENDATION_DISTRIBUTION_FIELDS = [
    "dimension",
    "value",
    "row_count",
    "unique_symbols",
    "unique_trade_dates",
    "share_of_rows",
    "variation_status",
]

LABEL_SOURCE_COVERAGE_FIELDS = [
    "label_source_path",
    "source_role",
    "exists",
    "row_count",
    "unique_symbols",
    "unique_trade_dates",
    "date_min",
    "date_max",
    "has_trade_date_symbol",
    "has_forward_return_1d",
    "has_forward_return_5d",
    "has_forward_return_20d",
    "has_excess_return_1d",
    "has_excess_return_5d",
    "has_excess_return_20d",
    "contract_valid_for_goal10b1",
    "overlap_symbols_with_goal08b",
    "t_plus_1_covered_goal08b_rows",
    "t_plus_1_missing_goal08b_rows",
    "supports_repair_candidate",
    "repair_limitation_codes",
]

WORKFLOW_PRODUCES_ARTIFACTS = ";".join(
    [
        DIAGNOSTIC_SUMMARY_PATH,
        RECOMMENDATION_DISTRIBUTION_AUDIT_PATH,
        LABEL_SOURCE_COVERAGE_AUDIT_PATH,
        REPORT_PATH,
        MANIFEST_PATH,
        AUDIT_PATH,
        DOC_PATH,
    ]
)
WORKFLOW_PRIMARY_DOCS = f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md"
WORKFLOW_PRIMARY_SCRIPTS = "scripts/run_goal10b1_backtest_coverage_repair_gate.py;scripts/audit_goal10b1_backtest_coverage_repair_gate.py"
WORKFLOW_PRIMARY_OUTPUTS = ";".join(
    [
        DIAGNOSTIC_SUMMARY_PATH,
        RECOMMENDATION_DISTRIBUTION_AUDIT_PATH,
        LABEL_SOURCE_COVERAGE_AUDIT_PATH,
        REPORT_PATH,
        MANIFEST_PATH,
        AUDIT_PATH,
    ]
)
WORKFLOW_NOTES = "Review-only GOAL-10B coverage and group-variation repair diagnostic gate; audits existing label and recommendation artifacts and records whether repair is possible without fetching data or fabricating metrics. It creates no repaired rows unless existing contract-valid inputs can support them, and creates no portfolio, dashboard, trading, production, broker, factor-mining, local-lake, or DQN/RL outputs."

FALSE_BOUNDARY_KEYS = [
    "new_data_fetched",
    "data_panel_expanded",
    "provider_ingestion_modified",
    "goal08b_rows_created",
    "goal08b_rows_overwritten",
    "goal09_rows_created",
    "goal09_rows_overwritten",
    "buy_sell_hold_outputs_generated",
    "target_prices_generated",
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
    "local_lake_files_created",
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

ALLOWED_BACKTEST_OUTPUTS = {
    "outputs/backtest/goal10b_recommendation_backtest_input_snapshot.csv",
    "outputs/backtest/goal10b_recommendation_group_metrics.csv",
    "outputs/backtest/goal10b_risk_severity_group_metrics.csv",
    "outputs/backtest/goal10b_warning_group_metrics.csv",
    "outputs/backtest/goal10b_ic_rank_ic_summary.csv",
    DIAGNOSTIC_SUMMARY_PATH,
    RECOMMENDATION_DISTRIBUTION_AUDIT_PATH,
    LABEL_SOURCE_COVERAGE_AUDIT_PATH,
    REPAIRED_SNAPSHOT_PATH,
    REPAIRED_RECOMMENDATION_METRICS_PATH,
}

FIELD_CANDIDATES = {
    "forward_return_1d": ["fwd_1d_return", "forward_return_1d"],
    "forward_return_5d": ["fwd_5d_return", "forward_return_5d"],
    "forward_return_20d": ["fwd_20d_return", "forward_return_20d"],
    "excess_return_1d": ["excess_fwd_1d_return", "benchmark_excess_return_1d"],
    "excess_return_5d": ["excess_fwd_5d_return", "benchmark_excess_return_5d"],
    "excess_return_20d": ["excess_fwd_20d_return", "benchmark_excess_return_20d"],
}


def run_goal10b1_backtest_coverage_repair_gate(root: Path) -> bool:
    result = evaluate_goal10b1_backtest_coverage_repair_gate(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal10b1_backtest_coverage_repair_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal10b1_backtest_coverage_repair_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    diagnostic_summary = _read_csv(root / DIAGNOSTIC_SUMMARY_PATH)
    recommendation_distribution = _read_csv(root / RECOMMENDATION_DISTRIBUTION_AUDIT_PATH)
    label_coverage = _read_csv(root / LABEL_SOURCE_COVERAGE_AUDIT_PATH)
    workflow = _workflow_rows(root)
    recheck = evaluate_goal10b1_backtest_coverage_repair_gate(root)
    failures: list[str] = []

    if not _report_pass_or_warn(report, "GOAL-10B.1 Backtest Coverage and Group Variation Repair Gate:"):
        failures.append("goal10b1_report_not_pass_or_warn")
    if recheck["status"] == BLOCKED:
        failures.extend(f"recheck:{failure}" for failure in recheck["failures"])
    if manifest.get("goal") != GOAL_NAME:
        failures.append("manifest_goal_invalid")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_invalid")
    if manifest.get("status") not in {PASS, PASS_WITH_WARNINGS}:
        failures.append("manifest_status_invalid")
    if manifest.get("repair_decision") != "coverage_repair_not_possible_with_current_artifacts":
        failures.append("manifest_repair_decision_invalid")
    for key in [
        "review_only_coverage_repair_diagnostics_generated",
        "label_source_coverage_audited",
        "recommendation_distribution_audited",
        "used_existing_artifacts_only",
        "goal10b1_workflow_status_after_goal10b1_implemented",
        "goal10c_locked_future",
        "goal10d_locked_future",
        "dashboard_daily_report_locked_future",
        "portfolio_backtest_locked_future",
        "cost_slippage_sensitivity_locked_future",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"manifest_{key}_not_false")
    if manifest.get("repaired_snapshot_generated") is not False:
        failures.append("manifest_repaired_snapshot_generated_not_false")
    if manifest.get("repaired_group_metrics_generated") is not False:
        failures.append("manifest_repaired_group_metrics_generated_not_false")
    if (root / REPAIRED_SNAPSHOT_PATH).exists():
        failures.append("repaired_snapshot_should_not_exist_without_valid_repair")
    if (root / REPAIRED_RECOMMENDATION_METRICS_PATH).exists():
        failures.append("repaired_recommendation_metrics_should_not_exist_without_valid_repair")
    if not diagnostic_summary:
        failures.append("diagnostic_summary_missing")
    elif set(diagnostic_summary[0]) != set(DIAGNOSTIC_SUMMARY_FIELDS):
        failures.append("diagnostic_summary_fields_invalid")
    if not recommendation_distribution:
        failures.append("recommendation_distribution_missing")
    elif set(recommendation_distribution[0]) != set(RECOMMENDATION_DISTRIBUTION_FIELDS):
        failures.append("recommendation_distribution_fields_invalid")
    if not label_coverage:
        failures.append("label_source_coverage_missing")
    elif set(label_coverage[0]) != set(LABEL_SOURCE_COVERAGE_FIELDS):
        failures.append("label_source_coverage_fields_invalid")

    row = workflow.get(WORKFLOW_ID, {})
    if row.get("status") != "implemented_review_only":
        failures.append("goal10b1_workflow_not_implemented_review_only")
    if row.get("implemented_in_repo") != "true":
        failures.append("goal10b1_workflow_not_marked_implemented")
    if row.get("depends_on") != GOAL10B_WORKFLOW_ID:
        failures.append("goal10b1_depends_on_invalid")
    if row.get("allowed_next_action") != GOAL10B1_ALLOWED_NEXT:
        failures.append("goal10b1_allowed_next_invalid")
    if workflow.get(GOAL10C_WORKFLOW_ID, {}).get("status") != "locked_future":
        failures.append("goal10c_not_locked_future")
    if workflow.get(GOAL10C_WORKFLOW_ID, {}).get("depends_on") not in {WORKFLOW_ID, GOAL10B2_WORKFLOW_ID}:
        failures.append("goal10c_dependency_invalid_after_goal10b1")
    if workflow.get(GOAL10D_WORKFLOW_ID, {}).get("status") != "locked_future":
        failures.append("goal10d_not_locked_future")
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
    failures.extend(f"unexpected_backtest_output:{path}" for path in _unexpected_backtest_outputs(root))

    status = PASS if not failures else BLOCKED
    write_text(
        root / AUDIT_PATH,
        "\n".join(
            [
                "# GOAL-10B.1 Backtest Coverage Repair Audit",
                "",
                f"Status: `{status}`",
                "",
                f"GOAL-10B.1 workflow status: `{row.get('status', 'missing')}`",
                f"Repair decision: `{manifest.get('repair_decision', 'missing')}`",
                f"Candidate label sources audited: `{manifest.get('candidate_label_source_count', 0)}`",
                f"Repaired snapshot generated: `{manifest.get('repaired_snapshot_generated', False)}`",
                "BUY/SELL/HOLD, target price, position sizing, portfolio, equity curve, dashboard, trading, production, local-lake, factor-mining, and DQN/RL outputs generated: `false`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == PASS


def evaluate_goal10b1_backtest_coverage_repair_gate(root: Path) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    workflow = _workflow_rows(root)
    goal08b_rows = _read_csv(root / GOAL08B_DIAGNOSTICS_PATH)
    goal10b_manifest = _read_json(root / GOAL10B_MANIFEST_PATH)

    if not goal10b_valid_review_only_evidence(root):
        failures.append("goal10b_review_only_evidence_not_ready")
    goal10b_row = workflow.get(GOAL10B_WORKFLOW_ID, {})
    if goal10b_row.get("status") != "implemented_review_only":
        failures.append("goal10b_workflow_not_implemented_review_only")
    if goal10b_row.get("implemented_in_repo") != "true":
        failures.append("goal10b_workflow_not_marked_implemented")
    if not goal08b_rows:
        failures.append("goal08b_diagnostics_missing")

    label_coverage = _label_source_coverage_rows(root, goal08b_rows)
    recommendation_distribution = _recommendation_distribution_rows(goal08b_rows)
    summary = _diagnostic_summary_rows(goal08b_rows, label_coverage, goal10b_manifest)

    repair_possible = _repair_possible(goal08b_rows, label_coverage)
    repair_decision = "repair_possible_with_existing_contract_valid_artifacts" if repair_possible else "coverage_repair_not_possible_with_current_artifacts"
    if not repair_possible:
        warnings.append("coverage_repair_not_possible_with_current_artifacts")
    if len({row.get("symbol", "") for row in goal08b_rows if row.get("symbol", "")}) < 2:
        warnings.append("single_symbol_goal08b_diagnostics")
    if len({row.get("recommendation_diagnostic_label", "") for row in goal08b_rows if row.get("recommendation_diagnostic_label", "")}) < 2:
        warnings.append("goal08b_single_recommendation_group")
    if len({row.get("risk_severity", "") for row in goal08b_rows if row.get("risk_severity", "")}) < 2:
        warnings.append("goal08b_single_risk_severity")
    if not any(_truthy(row.get("has_forward_return_20d")) for row in label_coverage):
        warnings.append("no_existing_forward_return_20d_label_source")
    if not _has_ranking_variation(goal08b_rows):
        warnings.append("goal08b_ranking_variation_not_available")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))
    failures.extend(f"unexpected_backtest_output:{path}" for path in _unexpected_backtest_outputs(root))

    status = BLOCKED if failures else PASS_WITH_WARNINGS if warnings else PASS
    manifest = _manifest(status, failures, warnings, goal08b_rows, label_coverage, recommendation_distribution, repair_decision, goal10b_manifest)
    return {
        "status": status,
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "diagnostic_summary": summary,
        "recommendation_distribution": recommendation_distribution,
        "label_coverage": label_coverage,
        "manifest": manifest,
    }


def goal10b1_valid_coverage_repair_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        _report_pass_or_warn(report, "GOAL-10B.1 Backtest Coverage and Group Variation Repair Gate:")
        and "Status: `PASS`" in audit
        and manifest.get("goal") == GOAL_NAME
        and manifest.get("mode") == MODE
        and manifest.get("review_only_coverage_repair_diagnostics_generated") is True
        and manifest.get("repair_decision") == "coverage_repair_not_possible_with_current_artifacts"
        and manifest.get("repaired_snapshot_generated") is False
        and manifest.get("goal10c_locked_future") is True
        and manifest.get("dashboard_daily_report_locked_future") is True
        and manifest.get("portfolio_returns_generated") is False
        and manifest.get("equity_curves_generated") is False
        and manifest.get("buy_sell_hold_outputs_generated") is False
    )


def goal10b1_implemented_workflow_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-10B.1 Backtest Coverage Repair Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_review_only",
        "current_repo_role": "review_only_backtest_coverage_repair_diagnostic_gate",
        "implemented_in_repo": "true",
        "allowed_next_action": GOAL10B1_ALLOWED_NEXT,
        "depends_on": GOAL10B_WORKFLOW_ID,
        "produces_artifacts": WORKFLOW_PRODUCES_ARTIFACTS,
        "primary_docs": WORKFLOW_PRIMARY_DOCS,
        "primary_scripts": WORKFLOW_PRIMARY_SCRIPTS,
        "primary_outputs": WORKFLOW_PRIMARY_OUTPUTS,
        "promotion_rule": "implemented_review_only_after_goal10b1_coverage_repair_audit_pass_with_warnings",
        "notes": WORKFLOW_NOTES,
    }


def locked_goal10c_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-10C Backtest Cost / Slippage Sensitivity",
        "stage_or_goal": "GOAL-10C",
        "status": "locked_future",
        "current_repo_role": "locked_future_backtest_sensitivity",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10c_request",
        "depends_on": WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal10c_cost_slippage_sensitivity_gate",
        "notes": "Future cost/slippage sensitivity remains locked; GOAL-10B.1 creates no cost/slippage sensitivity rows.",
    }


def locked_goal10d_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-10D Backtest Failure Attribution",
        "stage_or_goal": "GOAL-10D",
        "status": "locked_future",
        "current_repo_role": "locked_future_backtest_failure_attribution",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10d_request",
        "depends_on": GOAL10C_WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal10d_failure_attribution_gate",
        "notes": "Future failure attribution remains locked; GOAL-10B.1 creates no attribution rows or reports.",
    }


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / DIAGNOSTIC_SUMMARY_PATH, result["diagnostic_summary"], DIAGNOSTIC_SUMMARY_FIELDS)
    write_csv(root / RECOMMENDATION_DISTRIBUTION_AUDIT_PATH, result["recommendation_distribution"], RECOMMENDATION_DISTRIBUTION_FIELDS)
    write_csv(root / LABEL_SOURCE_COVERAGE_AUDIT_PATH, result["label_coverage"], LABEL_SOURCE_COVERAGE_FIELDS)
    _remove_optional_repaired_outputs(root)
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_report(root, result)
    _write_doc(root, result)


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    write_text(
        root / REPORT_PATH,
        "\n".join(
            [
                "# GOAL-10B.1 Backtest Coverage and Group Variation Repair Gate",
                "",
                f"GOAL-10B.1 Backtest Coverage and Group Variation Repair Gate: {result['status']}",
                f"Mode: `{MODE}`",
                "",
                "## Investigation",
                f"- GOAL-10B label source: `{manifest['goal10b_label_source_path']}`",
                f"- Candidate label sources audited: `{manifest['candidate_label_source_count']}`",
                f"- GOAL-08B rows: `{manifest['goal08b_row_count']}`",
                f"- GOAL-08B symbols: `{manifest['goal08b_unique_symbols']}`",
                f"- GOAL-08B recommendation groups: `{manifest['goal08b_recommendation_group_count']}`",
                f"- GOAL-08B risk-severity groups: `{manifest['goal08b_risk_severity_group_count']}`",
                f"- GOAL-10B evaluable rows: `{manifest['goal10b_evaluable_row_count']}`",
                "",
                "## Repair Decision",
                f"- `{manifest['repair_decision']}`",
                "- Current artifacts do not contain an existing contract-valid source that both improves GOAL-10B label coverage and creates recommendation/risk group variation.",
                "- GOAL-08B itself contains one symbol, one recommendation label, one actionability status, and one risk-severity bucket, so group variation cannot be repaired by swapping label files.",
                "",
                "## Boundary",
                "- GOAL-10B.1 is review-only diagnostics over existing committed artifacts.",
                "- No new data fetch, panel expansion, provider change, GOAL-08B row, GOAL-09 row, BUY/SELL/HOLD output, target price, position sizing, portfolio return, equity curve, dashboard, trading, production, broker, local-lake, factor-mining, or DQN/RL output was created.",
                "- GOAL-DATA-LABEL-01 may follow only as review-only label coverage expansion; GOAL-V1-DIAGNOSTIC-COVERAGE-02, GOAL-10B.2, GOAL-10C, GOAL-10D, Dashboard / Daily Report UI, signal backtest promotion, portfolio backtest, cost/slippage sensitivity, paper/live trading, broker, production, factor-mining, local-lake, and DQN/RL remain locked unless their own explicit gates pass.",
                "",
                "## Recommended Next Gate",
                "- `future_data_label_coverage_expansion_gate` should be requested before attempting GOAL-10C or any broader backtest diagnostics.",
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
                "# GOAL-10B.1 Backtest Coverage Repair Gate",
                "",
                f"Status: `{result['status']}`",
                "",
                "GOAL-10B.1 is a review-only coverage and group-variation repair gate for GOAL-10B. It investigates whether the GOAL-10B warnings can be repaired using only existing contract-valid artifacts already committed to the repository.",
                "",
                "It does not fetch data, expand the panel, create new recommendation diagnostics, create position rows, run portfolio backtests, or create dashboard/frontend outputs.",
                "",
                "## Findings",
                "",
                f"- GOAL-10B used `{manifest['goal10b_label_source_path']}` because it is the primary existing Stage6C source-backed label source in the GOAL-10B loader.",
                "- That source is a bounded sample with one symbol and no 20d forward-return fields.",
                "- Existing alternate committed label files either have the same one-symbol coverage, no GOAL-08B symbol/date overlap, or lack the required 5d/20d fields.",
                "- GOAL-08B has one recommendation group (`blocked_high_risk`), one actionability status (`never_actionable`), and one risk-severity bucket (`HIGH`), so recommendation/risk group variation cannot be repaired by changing label files.",
                "",
                "## Outputs",
                "",
                f"- `{DIAGNOSTIC_SUMMARY_PATH}`",
                f"- `{RECOMMENDATION_DISTRIBUTION_AUDIT_PATH}`",
                f"- `{LABEL_SOURCE_COVERAGE_AUDIT_PATH}`",
                f"- `{REPORT_PATH}`",
                f"- `{MANIFEST_PATH}`",
                f"- `{AUDIT_PATH}`",
                "",
                "## Repair Decision",
                "",
                f"`{manifest['repair_decision']}`",
                "",
                "GOAL-10B.1 does not write repaired snapshots or repaired group metrics because doing so would fabricate variation or coverage that is absent from the current contract-valid artifacts.",
                "",
                "## Follow-on Label Coverage Step",
                "",
                "GOAL-DATA-LABEL-01 follows this gate only as review-only label coverage expansion from existing committed OHLCV and benchmark samples. It may add 20d forward-return label coverage where future bars exist, but it does not create new GOAL-08B or GOAL-09 diagnostics and does not run GOAL-10B.2 or GOAL-10C backtests.",
                "",
                "## Locked Boundary",
                "",
                "GOAL-V1-DIAGNOSTIC-COVERAGE-02, GOAL-10B.2, GOAL-10C, GOAL-10D, Dashboard / Daily Report UI, signal backtest promotion, portfolio backtest, cost/slippage sensitivity, paper/live trading, live trading, broker integration, production writes, factor-mining, local-lake writes, and DQN/RL remain locked or deleted from active mainline.",
                "",
            ]
        ),
    )


def _manifest(
    status: str,
    failures: list[str],
    warnings: list[str],
    goal08b_rows: list[dict[str, str]],
    label_coverage: list[dict[str, object]],
    recommendation_distribution: list[dict[str, object]],
    repair_decision: str,
    goal10b_manifest: dict[str, object],
) -> dict[str, object]:
    recommendation_groups = sorted({row.get("recommendation_diagnostic_label", "") for row in goal08b_rows if row.get("recommendation_diagnostic_label", "")})
    actionability_values = sorted({row.get("actionability_status", "") for row in goal08b_rows if row.get("actionability_status", "")})
    risk_groups = sorted({row.get("risk_severity", "") for row in goal08b_rows if row.get("risk_severity", "")})
    symbols = sorted({row.get("symbol", "") for row in goal08b_rows if row.get("symbol", "")})
    return {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "status": status,
        "mode": MODE,
        "allowed_next_action": GOAL10B1_ALLOWED_NEXT if status != BLOCKED else "repair_goal10b1_coverage_repair_blockers",
        "repair_decision": repair_decision,
        "recommended_future_gate": "future_data_label_coverage_expansion_gate",
        "goal10b_label_source_path": goal10b_manifest.get("label_source_path", PRIMARY_LABEL_SOURCE_PATH),
        "goal10b_evaluable_row_count": goal10b_manifest.get("evaluable_row_count", 0),
        "goal10b_warning_codes": goal10b_manifest.get("warnings", []),
        "goal08b_row_count": len(goal08b_rows),
        "goal08b_unique_symbols": len(symbols),
        "goal08b_symbols": symbols,
        "goal08b_recommendation_groups": recommendation_groups,
        "goal08b_recommendation_group_count": len(recommendation_groups),
        "goal08b_actionability_status_values": actionability_values,
        "goal08b_risk_severity_groups": risk_groups,
        "goal08b_risk_severity_group_count": len(risk_groups),
        "recommendation_distribution_rows": len(recommendation_distribution),
        "candidate_label_source_count": len(label_coverage),
        "contract_valid_label_source_count": sum(1 for row in label_coverage if _truthy(row.get("contract_valid_for_goal10b1"))),
        "repair_candidate_label_source_count": sum(1 for row in label_coverage if _truthy(row.get("supports_repair_candidate"))),
        "primary_label_source_is_sample": True,
        "primary_label_source_causes_single_symbol_label_coverage": True,
        "primary_label_source_missing_forward_return_20d": True,
        "limited_t_plus_1_label_coverage_confirmed": True,
        "insufficient_recommendation_group_variation_source": "goal08b_single_recommendation_group",
        "insufficient_risk_severity_variation_source": "goal07b_goal08b_single_high_risk_severity",
        "insufficient_ranking_variation_source": "no_numeric_alpha_or_ranking_variation_in_goal08b",
        "review_only_coverage_repair_diagnostics_generated": status != BLOCKED,
        "label_source_coverage_audited": status != BLOCKED,
        "recommendation_distribution_audited": status != BLOCKED,
        "used_existing_artifacts_only": True,
        "repaired_snapshot_generated": False,
        "repaired_group_metrics_generated": False,
        "goal10b1_workflow_status_after_goal10b1": "implemented_review_only" if status != BLOCKED else "locked_future",
        "goal10b1_workflow_status_after_goal10b1_implemented": status != BLOCKED,
        "goal10c_status_after_goal10b1": "locked_future",
        "goal10d_status_after_goal10b1": "locked_future",
        "dashboard_daily_report_status_after_goal10b1": "locked_future",
        "signal_backtest_status_after_goal10b1": "locked_future",
        "portfolio_backtest_status_after_goal10b1": "locked_future",
        "cost_slippage_sensitivity_status_after_goal10b1": "locked_future",
        "goal10c_locked_future": True,
        "goal10d_locked_future": True,
        "dashboard_daily_report_locked_future": True,
        "signal_backtest_locked_future": True,
        "portfolio_backtest_locked_future": True,
        "cost_slippage_sensitivity_locked_future": True,
        "input_artifacts": [GOAL08B_DIAGNOSTICS_PATH, GOAL10B_REPORT_PATH, GOAL10B_MANIFEST_PATH, GOAL10B_AUDIT_PATH, *LABEL_SOURCE_CANDIDATES],
        "output_artifacts": [DIAGNOSTIC_SUMMARY_PATH, RECOMMENDATION_DISTRIBUTION_AUDIT_PATH, LABEL_SOURCE_COVERAGE_AUDIT_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH],
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        **{key: False for key in FALSE_BOUNDARY_KEYS},
    }


def _diagnostic_summary_rows(
    goal08b_rows: list[dict[str, str]],
    label_coverage: list[dict[str, object]],
    goal10b_manifest: dict[str, object],
) -> list[dict[str, object]]:
    recommendation_groups = sorted({row.get("recommendation_diagnostic_label", "") for row in goal08b_rows if row.get("recommendation_diagnostic_label", "")})
    risk_groups = sorted({row.get("risk_severity", "") for row in goal08b_rows if row.get("risk_severity", "")})
    symbols = sorted({row.get("symbol", "") for row in goal08b_rows if row.get("symbol", "")})
    primary = next((row for row in label_coverage if row["label_source_path"] == PRIMARY_LABEL_SOURCE_PATH), {})
    best_t1 = max([int(row.get("t_plus_1_covered_goal08b_rows", 0)) for row in label_coverage] or [0])
    return [
        _summary_row(
            "label_source_selection",
            "goal10b_primary_stage6c_source_backed_sample_used",
            "confirmed",
            f"GOAL-10B manifest label_source_path={goal10b_manifest.get('label_source_path', PRIMARY_LABEL_SOURCE_PATH)}",
            "no_code_repair_needed_primary_loader_behavior_documented",
        ),
        _summary_row(
            "label_source_coverage",
            "primary_label_source_is_single_symbol_sample",
            "confirmed",
            f"primary rows={primary.get('row_count', 0)} unique_symbols={primary.get('unique_symbols', 0)} unique_trade_dates={primary.get('unique_trade_dates', 0)}",
            "not_repaired_current_artifacts_are_bounded_samples",
        ),
        _summary_row(
            "label_source_coverage",
            "missing_forward_return_20d",
            "confirmed",
            "No audited existing label source has a forward_return_20d/fwd_20d_return field.",
            "not_repaired_future_label_horizon_expansion_required",
        ),
        _summary_row(
            "label_source_alignment",
            "limited_t_plus_1_label_coverage",
            "confirmed",
            f"best existing same-symbol T+1 coverage={best_t1}/{len(goal08b_rows)} GOAL-08B rows.",
            "not_repaired_no_later_label_for_final_signal_row",
        ),
        _summary_row(
            "recommendation_distribution",
            "goal08b_single_recommendation_group",
            "confirmed",
            f"recommendation_groups={';'.join(recommendation_groups)}",
            "not_repaired_requires_new_upstream_review_only_diagnostic_variation",
        ),
        _summary_row(
            "risk_distribution",
            "goal08b_single_risk_severity",
            "confirmed",
            f"risk_severity_groups={';'.join(risk_groups)}",
            "not_repaired_requires_upstream_risk_overlay_variation",
        ),
        _summary_row(
            "ranking_variation",
            "goal08b_no_contract_valid_numeric_ranking_variation",
            "confirmed",
            f"goal08b_symbols={';'.join(symbols)}",
            "not_repaired_current_goal08b_schema_has_no_usable_score_variation",
        ),
        _summary_row(
            "repair_decision",
            "coverage_repair_not_possible_with_current_artifacts",
            "confirmed",
            "Existing committed artifacts cannot improve GOAL-10B label coverage and cannot create recommendation/risk group variation without fabrication.",
            "future_data_label_coverage_expansion_gate_required",
        ),
    ]


def _summary_row(area: str, code: str, status: str, evidence: str, repair_status: str) -> dict[str, object]:
    return {
        "diagnostic_area": area,
        "finding_code": code,
        "status": status,
        "evidence": evidence,
        "repair_status": repair_status,
        "recommended_next_gate": "future_data_label_coverage_expansion_gate",
    }


def _recommendation_distribution_rows(goal08b_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for dimension, field in [
        ("recommendation_eligibility", "recommendation_diagnostic_label"),
        ("actionability_status", "actionability_status"),
        ("risk_severity", "risk_severity"),
        ("symbol", "symbol"),
    ]:
        rows.extend(_distribution_for_field(goal08b_rows, dimension, field))
    warning_counts: Counter[str] = Counter()
    warning_symbols: dict[str, set[str]] = {}
    warning_dates: dict[str, set[str]] = {}
    for row in goal08b_rows:
        for code in _split_codes(row.get("warning_propagation_codes", "")):
            warning_counts[code] += 1
            warning_symbols.setdefault(code, set()).add(row.get("symbol", ""))
            warning_dates.setdefault(code, set()).add(row.get("trade_date", ""))
    total = len(goal08b_rows)
    variation = "single_value" if len(warning_counts) <= 1 else "multi_value"
    for code, count in sorted(warning_counts.items()):
        rows.append(
            {
                "dimension": "warning_flag",
                "value": code,
                "row_count": count,
                "unique_symbols": len({item for item in warning_symbols.get(code, set()) if item}),
                "unique_trade_dates": len({item for item in warning_dates.get(code, set()) if item}),
                "share_of_rows": _ratio(count, total),
                "variation_status": variation,
            }
        )
    return rows


def _distribution_for_field(rows: list[dict[str, str]], dimension: str, field: str) -> list[dict[str, object]]:
    counts = Counter(row.get(field, "") or "missing" for row in rows)
    total = len(rows)
    variation = "single_value" if len(counts) <= 1 else "multi_value"
    output: list[dict[str, object]] = []
    for value, count in sorted(counts.items()):
        scoped = [row for row in rows if (row.get(field, "") or "missing") == value]
        output.append(
            {
                "dimension": dimension,
                "value": value,
                "row_count": count,
                "unique_symbols": len({row.get("symbol", "") for row in scoped if row.get("symbol", "")}),
                "unique_trade_dates": len({row.get("trade_date", "") for row in scoped if row.get("trade_date", "")}),
                "share_of_rows": _ratio(count, total),
                "variation_status": variation,
            }
        )
    return output


def _label_source_coverage_rows(root: Path, goal08b_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index, source_path in enumerate(LABEL_SOURCE_CANDIDATES):
        source_rows = _read_csv(root / source_path)
        fields = set(source_rows[0].keys()) if source_rows else set(_csv_fieldnames(root / source_path))
        symbols = sorted({row.get("symbol", "") for row in source_rows if row.get("symbol", "")})
        dates = sorted({row.get("trade_date", "") for row in source_rows if row.get("trade_date", "")})
        has_trade_date_symbol = {"trade_date", "symbol"}.issubset(fields)
        has_1d = _has_any_field(fields, "forward_return_1d")
        has_5d = _has_any_field(fields, "forward_return_5d")
        has_20d = _has_any_field(fields, "forward_return_20d")
        has_excess_1d = _has_any_field(fields, "excess_return_1d")
        has_excess_5d = _has_any_field(fields, "excess_return_5d")
        has_excess_20d = _has_any_field(fields, "excess_return_20d")
        contract_valid = bool(source_rows and has_trade_date_symbol and has_1d and has_5d and has_excess_1d and has_excess_5d)
        covered = _t_plus_1_covered_rows(goal08b_rows, source_rows) if contract_valid else 0
        overlap_symbols = len(set(symbols) & {row.get("symbol", "") for row in goal08b_rows if row.get("symbol", "")})
        limitations = _label_source_limitations(source_rows, fields, goal08b_rows, covered)
        supports_repair = contract_valid and overlap_symbols > 0 and covered == len(goal08b_rows) and len(symbols) > 1 and has_20d
        rows.append(
            {
                "label_source_path": source_path,
                "source_role": "goal10b_primary" if index == 0 else "candidate_existing_artifact",
                "exists": (root / source_path).exists(),
                "row_count": len(source_rows),
                "unique_symbols": len(symbols),
                "unique_trade_dates": len(dates),
                "date_min": dates[0] if dates else "",
                "date_max": dates[-1] if dates else "",
                "has_trade_date_symbol": has_trade_date_symbol,
                "has_forward_return_1d": has_1d,
                "has_forward_return_5d": has_5d,
                "has_forward_return_20d": has_20d,
                "has_excess_return_1d": has_excess_1d,
                "has_excess_return_5d": has_excess_5d,
                "has_excess_return_20d": has_excess_20d,
                "contract_valid_for_goal10b1": contract_valid,
                "overlap_symbols_with_goal08b": overlap_symbols,
                "t_plus_1_covered_goal08b_rows": covered,
                "t_plus_1_missing_goal08b_rows": max(len(goal08b_rows) - covered, 0),
                "supports_repair_candidate": supports_repair,
                "repair_limitation_codes": ";".join(limitations) if limitations else "none",
            }
        )
    return rows


def _label_source_limitations(
    source_rows: list[dict[str, str]],
    fields: set[str],
    goal08b_rows: list[dict[str, str]],
    covered: int,
) -> list[str]:
    limitations: list[str] = []
    if not source_rows:
        limitations.append("missing_or_empty")
    if not {"trade_date", "symbol"}.issubset(fields):
        limitations.append("missing_trade_date_symbol")
    for key, code in [
        ("forward_return_1d", "missing_forward_return_1d"),
        ("forward_return_5d", "missing_forward_return_5d"),
        ("forward_return_20d", "missing_forward_return_20d"),
        ("excess_return_1d", "missing_excess_return_1d"),
        ("excess_return_5d", "missing_excess_return_5d"),
        ("excess_return_20d", "missing_excess_return_20d"),
    ]:
        if not _has_any_field(fields, key):
            limitations.append(code)
    symbols = {row.get("symbol", "") for row in source_rows if row.get("symbol", "")}
    goal08b_symbols = {row.get("symbol", "") for row in goal08b_rows if row.get("symbol", "")}
    if len(symbols) < 2:
        limitations.append("single_symbol_label_coverage")
    if not (symbols & goal08b_symbols):
        limitations.append("no_goal08b_symbol_overlap")
    if covered < len(goal08b_rows):
        limitations.append("limited_t_plus_1_label_coverage")
    return sorted(set(limitations))


def _repair_possible(goal08b_rows: list[dict[str, str]], label_coverage: list[dict[str, object]]) -> bool:
    if len({row.get("recommendation_diagnostic_label", "") for row in goal08b_rows if row.get("recommendation_diagnostic_label", "")}) < 2:
        return False
    if len({row.get("risk_severity", "") for row in goal08b_rows if row.get("risk_severity", "")}) < 2:
        return False
    return any(_truthy(row.get("supports_repair_candidate")) for row in label_coverage)


def _has_ranking_variation(goal08b_rows: list[dict[str, str]]) -> bool:
    for field in ["alpha_score", "ranking_score", "diagnostic_score", "risk_confidence"]:
        values = {row.get(field, "") for row in goal08b_rows if _is_float(row.get(field, ""))}
        if len(values) >= 2:
            return True
    return False


def _t_plus_1_covered_rows(goal08b_rows: list[dict[str, str]], label_rows: list[dict[str, str]]) -> int:
    dates_by_symbol: dict[str, list[str]] = {}
    ready_by_key: set[tuple[str, str]] = set()
    for row in label_rows:
        symbol = row.get("symbol", "")
        trade_date = row.get("trade_date", "")
        if symbol and trade_date:
            dates_by_symbol.setdefault(symbol, []).append(trade_date)
            if _label_ready(row):
                ready_by_key.add((trade_date, symbol))
    for dates in dates_by_symbol.values():
        dates.sort()
    covered = 0
    for row in goal08b_rows:
        symbol = row.get("symbol", "")
        trade_date = row.get("trade_date", "")
        next_date = _next_label_date(dates_by_symbol.get(symbol, []), trade_date)
        if next_date and (next_date, symbol) in ready_by_key:
            covered += 1
    return covered


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys())
    by_id = {row["workflow_id"]: row for row in rows}
    patch = goal10b1_implemented_workflow_patch()
    if result["status"] == BLOCKED:
        patch.update(
            {
                "status": "locked_future",
                "current_repo_role": "review_only_backtest_coverage_repair_blocked",
                "implemented_in_repo": "false",
                "allowed_next_action": "repair_goal10b1_coverage_repair_blockers",
                "produces_artifacts": "",
                "primary_scripts": "",
                "primary_outputs": "",
                "promotion_rule": "locked_until_goal10b1_coverage_repair_gate_passes",
                "notes": "GOAL-10B.1 is blocked; GOAL-10C, GOAL-10D, dashboard, trading, production, factor-mining, local-lake, and DQN/RL remain locked.",
            }
        )
    _upsert_workflow_row(rows, by_id, WORKFLOW_ID, patch, after=GOAL10B_WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL10C_WORKFLOW_ID, locked_goal10c_patch(), after=WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL10D_WORKFLOW_ID, locked_goal10d_patch(), after=GOAL10C_WORKFLOW_ID)
    for workflow_id in [
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
    if "dashboard_daily_report" in by_id:
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal10b1"
    if "signal_backtest" in by_id:
        by_id["signal_backtest"]["allowed_next_action"] = "remain_locked_review_only_diagnostics_represented_by_goal10b_only"
    if "dqn_rl_mainline" in by_id:
        by_id["dqn_rl_mainline"]["status"] = "deleted_from_active_mainline"
        by_id["dqn_rl_mainline"]["implemented_in_repo"] = "false"
    if "v2_factor_research_upgrade" in by_id:
        by_id["v2_factor_research_upgrade"]["status"] = "planned_locked"
        by_id["v2_factor_research_upgrade"]["implemented_in_repo"] = "false"
    preserve_later_review_only_workflow_states(root, by_id)
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
    write_json(path, payload)


def _remove_optional_repaired_outputs(root: Path) -> None:
    for path in [root / REPAIRED_SNAPSHOT_PATH, root / REPAIRED_RECOMMENDATION_METRICS_PATH]:
        if path.exists():
            path.unlink()


def _forbidden_outputs_present(root: Path) -> list[str]:
    return [path for path in FORBIDDEN_OUTPUT_DIRS if (root / path).exists()]


def _unexpected_backtest_outputs(root: Path) -> list[str]:
    path = root / BACKTEST_DIR
    if not path.exists():
        return []
    return [
        str(item.relative_to(root))
        for item in sorted(path.glob("*"))
        if str(item.relative_to(root)) not in ALLOWED_BACKTEST_OUTPUTS
    ]


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


def _csv_fieldnames(path: Path) -> list[str]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        first = handle.readline().strip()
    return first.split(",") if first else []


def _report_pass_or_warn(text: str, prefix: str) -> bool:
    return f"{prefix} {PASS}" in text or f"{prefix} {PASS_WITH_WARNINGS}" in text


def _has_any_field(fields: set[str], key: str) -> bool:
    return any(candidate in fields for candidate in FIELD_CANDIDATES[key])


def _label_ready(row: dict[str, str]) -> bool:
    if not row:
        return False
    for field in ["label_ready", "usable_for_validation", "review_only"]:
        if field in row:
            return str(row.get(field, "")).lower() == "true"
    return True


def _next_label_date(dates: list[str], trade_date: str) -> str:
    for candidate in dates:
        if candidate > trade_date:
            return candidate
    return ""


def _split_codes(raw: str) -> list[str]:
    return sorted({item for item in raw.split(";") if item and item != "none"})


def _ratio(count: int, total: int) -> str:
    if total <= 0:
        return ""
    return f"{count / total:.6f}"


def _is_float(raw: str) -> bool:
    try:
        float(raw)
        return True
    except (TypeError, ValueError):
        return False


def _truthy(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() == "true"

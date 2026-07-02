from __future__ import annotations

from pathlib import Path
from statistics import median

from ashare_premarket.contract_design.goal10a import goal10a_valid_design_evidence
from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import (
    preserve_later_review_only_capabilities,
    preserve_later_review_only_workflow_states,
)
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-10B"
GOAL_NAME = "GOAL-10B-RECOMMENDATION-DIAGNOSTICS-BACKTEST-REVIEW-ONLY-PROTOTYPE"
MODE = "review_only"
WORKFLOW_ID = "goal10b_backtest_review_only_validation_gate"
GOAL10A_WORKFLOW_ID = "goal10a_backtest_contract_design_gate"
GOAL10C_WORKFLOW_ID = "goal10c_backtest_cost_slippage_sensitivity_gate"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
GOAL10B_ALLOWED_NEXT = "fix_goal10b_backtest_warnings_before_goal10c_request"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

GOAL08B_DIAGNOSTICS_PATH = "outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv"
GOAL10A_REPORT_PATH = "outputs/audits/goal10a_backtest_contract_design_report.md"
GOAL10A_MANIFEST_PATH = "outputs/audits/goal10a_backtest_contract_design_manifest.json"
GOAL10A_AUDIT_PATH = "outputs/audits/goal10a_backtest_contract_design_audit.md"

PRIMARY_LABEL_SOURCE_PATH = "outputs/samples/stage6c_source_backed_engineering_panel_sample.csv"
FALLBACK_LABEL_SOURCE_PATH = "outputs/samples/source_backed_label_panel_sample.csv"

BACKTEST_DIR = "outputs/backtest"
SNAPSHOT_PATH = f"{BACKTEST_DIR}/goal10b_recommendation_backtest_input_snapshot.csv"
RECOMMENDATION_GROUP_METRICS_PATH = f"{BACKTEST_DIR}/goal10b_recommendation_group_metrics.csv"
RISK_SEVERITY_GROUP_METRICS_PATH = f"{BACKTEST_DIR}/goal10b_risk_severity_group_metrics.csv"
WARNING_GROUP_METRICS_PATH = f"{BACKTEST_DIR}/goal10b_warning_group_metrics.csv"
IC_RANK_IC_SUMMARY_PATH = f"{BACKTEST_DIR}/goal10b_ic_rank_ic_summary.csv"

DOC_PATH = "docs/backtest/GOAL10B_RECOMMENDATION_BACKTEST_REVIEW_ONLY.md"
REPORT_PATH = "outputs/audits/goal10b_recommendation_backtest_report.md"
MANIFEST_PATH = "outputs/audits/goal10b_recommendation_backtest_manifest.json"
AUDIT_PATH = "outputs/audits/goal10b_recommendation_backtest_audit.md"

WORKFLOW_PRODUCES_ARTIFACTS = ";".join(
    [
        SNAPSHOT_PATH,
        RECOMMENDATION_GROUP_METRICS_PATH,
        RISK_SEVERITY_GROUP_METRICS_PATH,
        WARNING_GROUP_METRICS_PATH,
        IC_RANK_IC_SUMMARY_PATH,
        REPORT_PATH,
        MANIFEST_PATH,
        AUDIT_PATH,
        DOC_PATH,
    ]
)
WORKFLOW_PRIMARY_DOCS = f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md"
WORKFLOW_PRIMARY_SCRIPTS = "scripts/run_goal10b_recommendation_backtest_review_only.py;scripts/audit_goal10b_recommendation_backtest_review_only.py"
WORKFLOW_PRIMARY_OUTPUTS = ";".join(
    [
        SNAPSHOT_PATH,
        RECOMMENDATION_GROUP_METRICS_PATH,
        RISK_SEVERITY_GROUP_METRICS_PATH,
        WARNING_GROUP_METRICS_PATH,
        IC_RANK_IC_SUMMARY_PATH,
        REPORT_PATH,
        MANIFEST_PATH,
        AUDIT_PATH,
    ]
)
WORKFLOW_NOTES = "Review-only GOAL-08B recommendation diagnostic forward-return validation; computes non-actionable group metrics and IC/RankIC availability checks only. It creates no buy/sell/hold actions, target prices, position sizing, portfolio weights, portfolio returns, equity curves, dashboards, trading, production, broker, factor-mining, local-lake, or DQN/RL outputs."

TARGET_HORIZONS = ["1d", "5d", "20d"]
AVAILABLE_HORIZONS = ["1d", "5d"]

SNAPSHOT_FIELDS = [
    "trade_date",
    "symbol",
    "signal_date",
    "execution_date",
    "recommendation_eligibility",
    "actionability_status",
    "risk_severity",
    "warning_codes",
    "evaluation_status",
    "evaluation_reason",
    "forward_return_1d",
    "forward_return_5d",
    "forward_return_20d",
    "benchmark_excess_return_1d",
    "benchmark_excess_return_5d",
    "benchmark_excess_return_20d",
    "label_source_path",
    "label_source_trade_date",
    "label_ready",
    "diagnostic_mode",
    "non_actionable_disclaimer",
]

RECOMMENDATION_METRIC_FIELDS = [
    "recommendation_eligibility",
    "actionability_status",
    "row_count",
    "unique_symbols",
    "unique_trade_dates",
    "mean_forward_return_1d",
    "median_forward_return_1d",
    "mean_forward_return_5d",
    "median_forward_return_5d",
    "mean_forward_return_20d",
    "median_forward_return_20d",
    "hit_rate_1d",
    "hit_rate_5d",
    "hit_rate_20d",
    "benchmark_excess_return_1d",
    "benchmark_excess_return_5d",
    "benchmark_excess_return_20d",
]

RISK_METRIC_FIELDS = [
    "risk_severity",
    "row_count",
    "mean_forward_return_1d",
    "mean_forward_return_5d",
    "mean_forward_return_20d",
    "hit_rate",
    "excess_return",
]

WARNING_METRIC_FIELDS = [
    "warning_flag",
    "row_count",
    "mean_forward_return_1d",
    "mean_forward_return_5d",
    "mean_forward_return_20d",
    "hit_rate",
    "excess_return",
]

IC_FIELDS = [
    "diagnostic_score_field",
    "valid_row_count",
    "unique_score_count",
    "IC_1d",
    "IC_5d",
    "IC_20d",
    "Rank_IC_1d",
    "Rank_IC_5d",
    "Rank_IC_20d",
    "status",
    "warning_code",
]

REQUIRED_GOAL08B_FIELDS = [
    "trade_date",
    "symbol",
    "recommendation_diagnostic_label",
    "actionability_status",
    "risk_severity",
    "risk_warning_codes",
    "warning_propagation_codes",
    "diagnostic_mode",
    "non_actionable_disclaimer",
]

LABEL_FIELD_CANDIDATES = {
    "forward_return_1d": ["fwd_1d_return", "forward_return_1d"],
    "forward_return_5d": ["fwd_5d_return", "forward_return_5d"],
    "benchmark_excess_return_1d": ["excess_fwd_1d_return", "benchmark_excess_return_1d"],
    "benchmark_excess_return_5d": ["excess_fwd_5d_return", "benchmark_excess_return_5d"],
}

FALSE_BOUNDARY_KEYS = [
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
    "new_data_fetched",
    "data_panel_expanded",
    "provider_ingestion_modified",
    "local_lake_files_created",
    "factor_mining_outputs_created",
    "dqn_rl_outputs_created",
    "goal07b_rows_overwritten",
    "goal08b_rows_overwritten",
    "goal09_rows_overwritten",
    "goal08b_actionable_status_changed",
    "goal09_actionable_status_changed",
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
    SNAPSHOT_PATH,
    RECOMMENDATION_GROUP_METRICS_PATH,
    RISK_SEVERITY_GROUP_METRICS_PATH,
    WARNING_GROUP_METRICS_PATH,
    IC_RANK_IC_SUMMARY_PATH,
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


def run_goal10b_recommendation_backtest_review_only(root: Path) -> bool:
    result = evaluate_goal10b_recommendation_backtest_review_only(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal10b_recommendation_backtest_review_only(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal10b_recommendation_backtest_review_only(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    snapshot = _read_csv(root / SNAPSHOT_PATH)
    recommendation_metrics = _read_csv(root / RECOMMENDATION_GROUP_METRICS_PATH)
    risk_metrics = _read_csv(root / RISK_SEVERITY_GROUP_METRICS_PATH)
    warning_metrics = _read_csv(root / WARNING_GROUP_METRICS_PATH)
    ic_summary = _read_csv(root / IC_RANK_IC_SUMMARY_PATH)
    workflow = _workflow_rows(root)
    recheck = evaluate_goal10b_recommendation_backtest_review_only(root)
    failures: list[str] = []

    if not _report_pass_or_warn(report, "GOAL-10B Recommendation Diagnostics Backtest Review-Only:"):
        failures.append("goal10b_report_not_pass_or_warn")
    if recheck["status"] == BLOCKED:
        failures.extend(f"recheck:{failure}" for failure in recheck["failures"])
    if manifest.get("goal") != GOAL_NAME:
        failures.append("manifest_goal_invalid")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_invalid")
    if manifest.get("status") not in {PASS, PASS_WITH_WARNINGS}:
        failures.append("manifest_status_invalid")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"manifest_{key}_not_false")
    for key in [
        "review_only_backtest_diagnostics_generated",
        "forward_return_diagnostics_generated",
        "goal08b_inputs_never_actionable",
        "t_plus_1_alignment_applied",
        "no_lookahead_contract_followed",
        "goal10c_locked_future",
        "goal10d_locked_future",
        "dashboard_daily_report_locked_future",
        "portfolio_backtest_locked_future",
        "cost_slippage_sensitivity_locked_future",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")

    if len(snapshot) != manifest.get("input_snapshot_row_count"):
        failures.append("snapshot_row_count_mismatch")
    if len([row for row in snapshot if row.get("evaluation_status") == "evaluable"]) != manifest.get("evaluable_row_count"):
        failures.append("snapshot_evaluable_count_mismatch")
    if not snapshot:
        failures.append("snapshot_missing")
    elif set(snapshot[0]) != set(SNAPSHOT_FIELDS):
        failures.append("snapshot_fields_invalid")
    for field in RECOMMENDATION_METRIC_FIELDS:
        if recommendation_metrics and field not in recommendation_metrics[0]:
            failures.append(f"recommendation_metric_missing_field:{field}")
    for field in RISK_METRIC_FIELDS:
        if risk_metrics and field not in risk_metrics[0]:
            failures.append(f"risk_metric_missing_field:{field}")
    for field in WARNING_METRIC_FIELDS:
        if warning_metrics and field not in warning_metrics[0]:
            failures.append(f"warning_metric_missing_field:{field}")
    for field in IC_FIELDS:
        if ic_summary and field not in ic_summary[0]:
            failures.append(f"ic_summary_missing_field:{field}")
    if not recommendation_metrics:
        failures.append("recommendation_metrics_missing")
    if not risk_metrics:
        failures.append("risk_metrics_missing")
    if not warning_metrics:
        failures.append("warning_metrics_missing")
    if not ic_summary:
        failures.append("ic_rank_ic_summary_missing")
    if ic_summary and ic_summary[0].get("status") != "not_computed":
        failures.append("ic_summary_should_be_not_computed_for_single_bucket")

    gate_row = workflow.get(WORKFLOW_ID, {})
    if gate_row.get("status") != "implemented_review_only":
        failures.append("goal10b_workflow_not_implemented_review_only")
    if gate_row.get("implemented_in_repo") != "true":
        failures.append("goal10b_workflow_not_marked_implemented")
    if gate_row.get("depends_on") != GOAL10A_WORKFLOW_ID:
        failures.append("goal10b_depends_on_invalid")
    if gate_row.get("allowed_next_action") != GOAL10B_ALLOWED_NEXT:
        failures.append("goal10b_allowed_next_invalid")
    goal10c_row = workflow.get(GOAL10C_WORKFLOW_ID, {})
    if goal10c_row.get("status") not in {"locked_future", "implemented_review_only"}:
        failures.append(f"{GOAL10C_WORKFLOW_ID}_invalid_status")
    if goal10c_row.get("status") == "implemented_review_only":
        if goal10c_row.get("implemented_in_repo") != "true":
            failures.append(f"{GOAL10C_WORKFLOW_ID}_not_marked_implemented")
    elif goal10c_row.get("implemented_in_repo") != "false":
        failures.append(f"{GOAL10C_WORKFLOW_ID}_marked_implemented")
    goal10d_row = workflow.get(GOAL10D_WORKFLOW_ID, {})
    if goal10d_row.get("status") != "locked_future":
        failures.append(f"{GOAL10D_WORKFLOW_ID}_not_locked_future")
    if goal10d_row.get("implemented_in_repo") != "false":
        failures.append(f"{GOAL10D_WORKFLOW_ID}_marked_implemented")
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
        row = workflow.get(workflow_id, {})
        if row.get("status") != "locked_future":
            failures.append(f"{workflow_id}_not_locked_future")
        if row.get("implemented_in_repo") != "false":
            failures.append(f"{workflow_id}_marked_implemented")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))
    failures.extend(f"unexpected_backtest_output:{path}" for path in _unexpected_backtest_outputs(root))

    status = PASS if not failures else BLOCKED
    write_text(
        root / AUDIT_PATH,
        "\n".join(
            [
                "# GOAL-10B Recommendation Diagnostics Backtest Audit",
                "",
                f"Status: `{status}`",
                "",
                f"GOAL-10B workflow status: `{gate_row.get('status', 'missing')}`",
                "GOAL-10B mode: `review_only`",
                f"Input snapshot rows: `{len(snapshot)}`",
                f"Evaluable rows: `{manifest.get('evaluable_row_count', 0)}`",
                "BUY/SELL/HOLD, target price, position sizing, portfolio, equity curve, dashboard, trading, production, local-lake, factor-mining, and DQN/RL outputs generated: `false`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == PASS


def evaluate_goal10b_recommendation_backtest_review_only(root: Path) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    workflow = _workflow_rows(root)
    goal08b_rows = _read_csv(root / GOAL08B_DIAGNOSTICS_PATH)
    label_source_path, label_rows = _load_label_rows(root)

    if not goal10a_valid_design_evidence(root):
        failures.append("goal10a_design_evidence_not_ready")
    failures.extend(_validate_goal08b_inputs(goal08b_rows))
    failures.extend(_validate_label_rows(label_rows, label_source_path))
    goal10a_row = workflow.get(GOAL10A_WORKFLOW_ID, {})
    if goal10a_row.get("status") != "implemented_design_only":
        failures.append("goal10a_workflow_not_implemented_design_only")
    if goal10a_row.get("implemented_in_repo") != "true":
        failures.append("goal10a_workflow_not_marked_implemented")

    snapshot_rows = _build_snapshot(goal08b_rows, label_rows, label_source_path)
    evaluable_rows = [row for row in snapshot_rows if row["evaluation_status"] == "evaluable"]
    recommendation_metrics = _recommendation_group_metrics(evaluable_rows)
    risk_metrics = _risk_group_metrics(evaluable_rows)
    warning_metrics = _warning_group_metrics(evaluable_rows)
    ic_summary = _ic_rank_ic_summary(evaluable_rows)

    if not evaluable_rows:
        failures.append("no_evaluable_t_plus_1_rows")
    if len(evaluable_rows) != len(goal08b_rows):
        warnings.append("missing_t_plus_1_label_rows_excluded")
    if "20d" not in AVAILABLE_HORIZONS:
        warnings.append("missing_forward_return_20d")
    if len({row["recommendation_eligibility"] for row in evaluable_rows}) < 2:
        warnings.append("insufficient_recommendation_group_variation")
    if len({row["risk_severity"] for row in evaluable_rows}) < 2:
        warnings.append("insufficient_risk_severity_variation")
    if ic_summary[0]["status"] != "computed":
        warnings.append(ic_summary[0]["warning_code"])
    if len({row["symbol"] for row in evaluable_rows}) < 2:
        warnings.append("single_symbol_label_coverage")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))
    failures.extend(f"unexpected_backtest_output:{path}" for path in _unexpected_backtest_outputs(root))

    status = BLOCKED if failures else PASS_WITH_WARNINGS if warnings else PASS
    manifest = _manifest(
        status,
        failures,
        warnings,
        goal08b_rows,
        snapshot_rows,
        evaluable_rows,
        label_source_path,
        recommendation_metrics,
        risk_metrics,
        warning_metrics,
        ic_summary,
    )
    return {
        "status": status,
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "snapshot_rows": snapshot_rows,
        "recommendation_metrics": recommendation_metrics,
        "risk_metrics": risk_metrics,
        "warning_metrics": warning_metrics,
        "ic_summary": ic_summary,
        "manifest": manifest,
    }


def goal10b_valid_review_only_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        _report_pass_or_warn(report, "GOAL-10B Recommendation Diagnostics Backtest Review-Only:")
        and "Status: `PASS`" in audit
        and manifest.get("goal") == GOAL_NAME
        and manifest.get("mode") == MODE
        and manifest.get("review_only_backtest_diagnostics_generated") is True
        and manifest.get("goal08b_inputs_never_actionable") is True
        and manifest.get("goal10c_locked_future") is True
        and manifest.get("goal10d_locked_future") is True
        and manifest.get("dashboard_daily_report_locked_future") is True
        and manifest.get("portfolio_returns_generated") is False
        and manifest.get("equity_curves_generated") is False
        and manifest.get("buy_sell_hold_outputs_generated") is False
        and manifest.get("target_prices_generated") is False
    )


def goal10b_implemented_workflow_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-10B Recommendation Diagnostics Backtest Review-Only",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_review_only",
        "current_repo_role": "review_only_recommendation_backtest_diagnostics",
        "implemented_in_repo": "true",
        "allowed_next_action": GOAL10B_ALLOWED_NEXT,
        "depends_on": GOAL10A_WORKFLOW_ID,
        "produces_artifacts": WORKFLOW_PRODUCES_ARTIFACTS,
        "primary_docs": WORKFLOW_PRIMARY_DOCS,
        "primary_scripts": WORKFLOW_PRIMARY_SCRIPTS,
        "primary_outputs": WORKFLOW_PRIMARY_OUTPUTS,
        "promotion_rule": "implemented_review_only_after_goal10b_backtest_diagnostics_pass_with_warnings",
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
        "notes": "Future cost/slippage sensitivity remains locked; GOAL-10B creates no cost/slippage sensitivity rows.",
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
        "notes": "Future failure attribution remains locked; GOAL-10B creates no attribution rows or reports.",
    }


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / SNAPSHOT_PATH, result["snapshot_rows"], SNAPSHOT_FIELDS)
    write_csv(root / RECOMMENDATION_GROUP_METRICS_PATH, result["recommendation_metrics"], RECOMMENDATION_METRIC_FIELDS)
    write_csv(root / RISK_SEVERITY_GROUP_METRICS_PATH, result["risk_metrics"], RISK_METRIC_FIELDS)
    write_csv(root / WARNING_GROUP_METRICS_PATH, result["warning_metrics"], WARNING_METRIC_FIELDS)
    write_csv(root / IC_RANK_IC_SUMMARY_PATH, result["ic_summary"], IC_FIELDS)
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_report(root, result)
    _write_doc(root, result)


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    write_text(
        root / REPORT_PATH,
        "\n".join(
            [
                "# GOAL-10B Recommendation Diagnostics Backtest Review-Only",
                "",
                f"GOAL-10B Recommendation Diagnostics Backtest Review-Only: {result['status']}",
                f"Mode: `{MODE}`",
                "",
                "## Input Alignment",
                f"- GOAL-08B recommendation diagnostics rows: `{manifest['source_goal08b_rows']}`",
                f"- Input snapshot rows: `{manifest['input_snapshot_row_count']}`",
                f"- Evaluable T+1 rows: `{manifest['evaluable_row_count']}`",
                f"- Label source: `{manifest['label_source_path']}`",
                "- Signal date equals the upstream GOAL-08B `trade_date`; execution date is the next available label date for the same symbol.",
                "",
                "## Diagnostics",
                f"- Recommendation group metric rows: `{manifest['recommendation_group_metric_rows']}`",
                f"- Risk-severity group metric rows: `{manifest['risk_severity_group_metric_rows']}`",
                f"- Warning group metric rows: `{manifest['warning_group_metric_rows']}`",
                f"- IC/Rank IC status: `{manifest['ic_rank_ic_status']}`",
                "",
                "## Boundary",
                "- Outputs are non-actionable review-only diagnostics.",
                "- No BUY/SELL/HOLD, target prices, position sizing, order quantities, target weights, portfolio weights, portfolio returns, equity curves, portfolio construction, dashboards, HTML, Streamlit, frontend, trading, production, broker, factor-mining, local-lake, or DQN/RL outputs were generated.",
                "- GOAL-10C, GOAL-10D, Dashboard / Daily Report UI, paper/live trading, broker, production, factor-mining, local-lake, and DQN/RL remain locked.",
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
                "# GOAL-10B Recommendation Diagnostics Backtest Review-Only",
                "",
                f"Status: `{result['status']}`",
                "",
                "GOAL-10B is a review-only diagnostic gate that evaluates whether GOAL-08B non-actionable recommendation eligibility diagnostics have observable forward-return separation under the GOAL-10A input, metric, grouping, and T+1/no-lookahead contracts.",
                "",
                "It is not an actionable recommendation, signal backtest workflow promotion, portfolio backtest, trading system, dashboard, or production path.",
                "",
                "## Source Inputs",
                "",
                "- `outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv`",
                f"- `{manifest['label_source_path']}`",
                "- `configs/backtest/goal10a_backtest_input_contract.yaml`",
                "- `configs/backtest/goal10a_backtest_metric_contract.yaml`",
                "- `configs/backtest/goal10a_backtest_grouping_contract.yaml`",
                "- `configs/backtest/goal10a_execution_alignment_policy.yaml`",
                "",
                "GOAL-08B rows remain `never_actionable`. The GOAL-10B join preserves the `trade_date + symbol` signal grain and uses the next available same-symbol label date as the diagnostic execution date.",
                "",
                "## Outputs",
                "",
                f"- `{SNAPSHOT_PATH}`",
                f"- `{RECOMMENDATION_GROUP_METRICS_PATH}`",
                f"- `{RISK_SEVERITY_GROUP_METRICS_PATH}`",
                f"- `{WARNING_GROUP_METRICS_PATH}`",
                f"- `{IC_RANK_IC_SUMMARY_PATH}`",
                f"- `{REPORT_PATH}`",
                f"- `{MANIFEST_PATH}`",
                f"- `{AUDIT_PATH}`",
                "",
                "## Warnings",
                "",
                "The current committed label sample supports 1d and 5d forward-return diagnostics, but not 20d. The final signal row has no next available execution label in the bounded sample. GOAL-08B also has a single recommendation eligibility bucket and single risk-severity bucket, so IC/Rank IC is explicitly marked `not_computed` rather than fabricated.",
                "",
                "## Locked Boundary",
                "",
                "GOAL-10C, GOAL-10D, Dashboard / Daily Report UI, signal backtest promotion, portfolio backtest, cost/slippage sensitivity, paper trading, live trading, broker integration, production writes, factor-mining, local-lake writes, and DQN/RL remain locked or deleted from active mainline.",
                "",
            ]
        ),
    )


def _manifest(
    status: str,
    failures: list[str],
    warnings: list[str],
    goal08b_rows: list[dict[str, str]],
    snapshot_rows: list[dict[str, object]],
    evaluable_rows: list[dict[str, object]],
    label_source_path: str,
    recommendation_metrics: list[dict[str, object]],
    risk_metrics: list[dict[str, object]],
    warning_metrics: list[dict[str, object]],
    ic_summary: list[dict[str, object]],
) -> dict[str, object]:
    actionability_values = sorted({row.get("actionability_status", "") for row in goal08b_rows})
    return {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "status": status,
        "mode": MODE,
        "allowed_next_action": GOAL10B_ALLOWED_NEXT if status != BLOCKED else "repair_goal10b_backtest_diagnostic_blockers",
        "source_goal08b_rows": len(goal08b_rows),
        "input_snapshot_row_count": len(snapshot_rows),
        "evaluable_row_count": len(evaluable_rows),
        "excluded_row_count": len(snapshot_rows) - len(evaluable_rows),
        "label_source_path": label_source_path,
        "input_grain": "trade_date + symbol",
        "signal_date_field": "trade_date",
        "execution_date_alignment": "first_available_label_trade_date_strictly_after_signal_date_for_same_symbol",
        "target_horizons": TARGET_HORIZONS,
        "available_horizons": AVAILABLE_HORIZONS,
        "missing_horizons": [horizon for horizon in TARGET_HORIZONS if horizon not in AVAILABLE_HORIZONS],
        "goal08b_actionability_status_values": actionability_values,
        "goal08b_inputs_never_actionable": actionability_values == ["never_actionable"],
        "recommendation_group_metric_rows": len(recommendation_metrics),
        "risk_severity_group_metric_rows": len(risk_metrics),
        "warning_group_metric_rows": len(warning_metrics),
        "ic_rank_ic_status": ic_summary[0]["status"] if ic_summary else "missing",
        "ic_rank_ic_warning_code": ic_summary[0]["warning_code"] if ic_summary else "missing_ic_summary",
        "review_only_backtest_diagnostics_generated": status != BLOCKED,
        "forward_return_diagnostics_generated": status != BLOCKED,
        "diagnostic_rows_generated": status != BLOCKED,
        "t_plus_1_alignment_applied": True,
        "no_lookahead_contract_followed": True,
        "benchmark_alignment_followed": True,
        "non_actionable": True,
        "goal10b_workflow_status_after_goal10b": "implemented_review_only" if status != BLOCKED else "locked_future",
        "goal10c_status_after_goal10b": "locked_future",
        "goal10d_status_after_goal10b": "locked_future",
        "dashboard_daily_report_status_after_goal10b": "locked_future",
        "signal_backtest_status_after_goal10b": "locked_future",
        "portfolio_backtest_status_after_goal10b": "locked_future",
        "cost_slippage_sensitivity_status_after_goal10b": "locked_future",
        "goal10c_locked_future": True,
        "goal10d_locked_future": True,
        "dashboard_daily_report_locked_future": True,
        "signal_backtest_locked_future": True,
        "portfolio_backtest_locked_future": True,
        "cost_slippage_sensitivity_locked_future": True,
        "input_artifacts": [
            GOAL08B_DIAGNOSTICS_PATH,
            PRIMARY_LABEL_SOURCE_PATH,
            FALLBACK_LABEL_SOURCE_PATH,
            GOAL10A_REPORT_PATH,
            GOAL10A_MANIFEST_PATH,
            GOAL10A_AUDIT_PATH,
        ],
        "output_artifacts": sorted(ALLOWED_BACKTEST_OUTPUTS) + [REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH],
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        **{key: False for key in FALSE_BOUNDARY_KEYS},
    }


def _build_snapshot(
    goal08b_rows: list[dict[str, str]],
    label_rows: list[dict[str, str]],
    label_source_path: str,
) -> list[dict[str, object]]:
    labels_by_key = {(row.get("trade_date", ""), row.get("symbol", "")): row for row in label_rows}
    label_dates_by_symbol: dict[str, list[str]] = {}
    for row in label_rows:
        symbol = row.get("symbol", "")
        trade_date = row.get("trade_date", "")
        if symbol and trade_date:
            label_dates_by_symbol.setdefault(symbol, []).append(trade_date)
    for dates in label_dates_by_symbol.values():
        dates.sort()

    snapshot_rows: list[dict[str, object]] = []
    for source in sorted(goal08b_rows, key=lambda row: (row.get("symbol", ""), row.get("trade_date", ""))):
        trade_date = source.get("trade_date", "")
        symbol = source.get("symbol", "")
        execution_date = _next_label_date(label_dates_by_symbol.get(symbol, []), trade_date)
        label = labels_by_key.get((execution_date, symbol), {}) if execution_date else {}
        label_ready = _label_ready(label) if label else False
        evaluation_status = "evaluable" if execution_date and label_ready else "excluded_missing_t_plus_1_label"
        evaluation_reason = "t_plus_1_label_available" if evaluation_status == "evaluable" else "missing_next_available_execution_label"
        snapshot_rows.append(
            {
                "trade_date": trade_date,
                "symbol": symbol,
                "signal_date": trade_date,
                "execution_date": execution_date,
                "recommendation_eligibility": source.get("recommendation_diagnostic_label", ""),
                "actionability_status": source.get("actionability_status", ""),
                "risk_severity": source.get("risk_severity", ""),
                "warning_codes": _combined_warning_codes(source),
                "evaluation_status": evaluation_status,
                "evaluation_reason": evaluation_reason,
                "forward_return_1d": _label_value(label, "forward_return_1d") if label_ready else "",
                "forward_return_5d": _label_value(label, "forward_return_5d") if label_ready else "",
                "forward_return_20d": "",
                "benchmark_excess_return_1d": _label_value(label, "benchmark_excess_return_1d") if label_ready else "",
                "benchmark_excess_return_5d": _label_value(label, "benchmark_excess_return_5d") if label_ready else "",
                "benchmark_excess_return_20d": "",
                "label_source_path": label_source_path if label else "",
                "label_source_trade_date": label.get("trade_date", ""),
                "label_ready": label_ready,
                "diagnostic_mode": MODE,
                "non_actionable_disclaimer": "GOAL-10B review-only diagnostics; not investment advice or trading instruction.",
            }
        )
    return snapshot_rows


def _recommendation_group_metrics(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped = _group_by(rows, ["recommendation_eligibility", "actionability_status"])
    output = []
    for key in sorted(grouped):
        items = grouped[key]
        recommendation_eligibility, actionability_status = key
        metric = _base_horizon_metrics(items)
        output.append(
            {
                "recommendation_eligibility": recommendation_eligibility,
                "actionability_status": actionability_status,
                "row_count": len(items),
                "unique_symbols": len({row["symbol"] for row in items}),
                "unique_trade_dates": len({row["trade_date"] for row in items}),
                **metric,
            }
        )
    return output


def _risk_group_metrics(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped = _group_by(rows, ["risk_severity"])
    output = []
    for key in sorted(grouped):
        items = grouped[key]
        output.append(
            {
                "risk_severity": key[0],
                "row_count": len(items),
                "mean_forward_return_1d": _format_metric(_mean(_numbers(items, "forward_return_1d"))),
                "mean_forward_return_5d": _format_metric(_mean(_numbers(items, "forward_return_5d"))),
                "mean_forward_return_20d": "",
                "hit_rate": _format_metric(_hit_rate(_numbers(items, "forward_return_1d"))),
                "excess_return": _format_metric(_mean(_numbers(items, "benchmark_excess_return_1d"))),
            }
        )
    return output


def _warning_group_metrics(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    warning_map: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        for warning in _split_codes(str(row.get("warning_codes", ""))):
            warning_map.setdefault(warning, []).append(row)
    output = []
    for warning in sorted(warning_map):
        items = warning_map[warning]
        output.append(
            {
                "warning_flag": warning,
                "row_count": len(items),
                "mean_forward_return_1d": _format_metric(_mean(_numbers(items, "forward_return_1d"))),
                "mean_forward_return_5d": _format_metric(_mean(_numbers(items, "forward_return_5d"))),
                "mean_forward_return_20d": "",
                "hit_rate": _format_metric(_hit_rate(_numbers(items, "forward_return_1d"))),
                "excess_return": _format_metric(_mean(_numbers(items, "benchmark_excess_return_1d"))),
            }
        )
    return output


def _ic_rank_ic_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    scores = [_diagnostic_score(row) for row in rows]
    valid_rows = [row for row, score in zip(rows, scores) if score is not None]
    unique_score_count = len({score for score in scores if score is not None})
    if len(valid_rows) < 3:
        return [_empty_ic_summary(len(valid_rows), unique_score_count, "insufficient_rows_for_ic")]
    if unique_score_count < 2:
        return [_empty_ic_summary(len(valid_rows), unique_score_count, "insufficient_ranking_variation")]
    score_values = [score for score in scores if score is not None]
    return [
        {
            "diagnostic_score_field": "recommendation_eligibility_order",
            "valid_row_count": len(valid_rows),
            "unique_score_count": unique_score_count,
            "IC_1d": _format_metric(_correlation(score_values, _numbers(valid_rows, "forward_return_1d"))),
            "IC_5d": _format_metric(_correlation(score_values, _numbers(valid_rows, "forward_return_5d"))),
            "IC_20d": "",
            "Rank_IC_1d": _format_metric(_correlation(_ranks(score_values), _ranks(_numbers(valid_rows, "forward_return_1d")))),
            "Rank_IC_5d": _format_metric(_correlation(_ranks(score_values), _ranks(_numbers(valid_rows, "forward_return_5d")))),
            "Rank_IC_20d": "",
            "status": "computed",
            "warning_code": "",
        }
    ]


def _empty_ic_summary(valid_row_count: int, unique_score_count: int, warning_code: str) -> dict[str, object]:
    return {
        "diagnostic_score_field": "recommendation_eligibility_order",
        "valid_row_count": valid_row_count,
        "unique_score_count": unique_score_count,
        "IC_1d": "",
        "IC_5d": "",
        "IC_20d": "",
        "Rank_IC_1d": "",
        "Rank_IC_5d": "",
        "Rank_IC_20d": "",
        "status": "not_computed",
        "warning_code": warning_code,
    }


def _base_horizon_metrics(items: list[dict[str, object]]) -> dict[str, object]:
    metrics: dict[str, object] = {}
    for horizon in TARGET_HORIZONS:
        values = _numbers(items, f"forward_return_{horizon}")
        metrics[f"mean_forward_return_{horizon}"] = _format_metric(_mean(values))
        metrics[f"median_forward_return_{horizon}"] = _format_metric(_median(values))
    for horizon in TARGET_HORIZONS:
        metrics[f"hit_rate_{horizon}"] = _format_metric(_hit_rate(_numbers(items, f"forward_return_{horizon}")))
    for horizon in TARGET_HORIZONS:
        metrics[f"benchmark_excess_return_{horizon}"] = _format_metric(_mean(_numbers(items, f"benchmark_excess_return_{horizon}")))
    return metrics


def _group_by(rows: list[dict[str, object]], fields: list[str]) -> dict[tuple[str, ...], list[dict[str, object]]]:
    grouped: dict[tuple[str, ...], list[dict[str, object]]] = {}
    for row in rows:
        key = tuple(str(row.get(field, "")) for field in fields)
        grouped.setdefault(key, []).append(row)
    return grouped


def _numbers(rows: list[dict[str, object]], field: str) -> list[float]:
    values = []
    for row in rows:
        raw = row.get(field, "")
        if raw in {"", None}:
            continue
        try:
            values.append(float(raw))
        except ValueError:
            continue
    return values


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _median(values: list[float]) -> float | None:
    return float(median(values)) if values else None


def _hit_rate(values: list[float]) -> float | None:
    return sum(1 for value in values if value > 0) / len(values) if values else None


def _correlation(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 2 or len(set(xs)) < 2 or len(set(ys)) < 2:
        return None
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denom_x = sum((x - mean_x) ** 2 for x in xs) ** 0.5
    denom_y = sum((y - mean_y) ** 2 for y in ys) ** 0.5
    if denom_x == 0 or denom_y == 0:
        return None
    return numerator / (denom_x * denom_y)


def _ranks(values: list[float]) -> list[float]:
    order = sorted((value, index) for index, value in enumerate(values))
    ranks = [0.0] * len(values)
    cursor = 0
    while cursor < len(order):
        end = cursor
        while end + 1 < len(order) and order[end + 1][0] == order[cursor][0]:
            end += 1
        rank = (cursor + end + 2) / 2
        for _, index in order[cursor : end + 1]:
            ranks[index] = rank
        cursor = end + 1
    return ranks


def _format_metric(value: float | None) -> str:
    if value is None:
        return ""
    text = f"{value:.10f}".rstrip("0").rstrip(".")
    return text if text not in {"-0", ""} else "0"


def _diagnostic_score(row: dict[str, object]) -> float | None:
    value = str(row.get("recommendation_eligibility", ""))
    order = {
        "blocked_high_risk": 0.0,
        "eligible_review_only": 1.0,
    }
    return order.get(value)


def _load_label_rows(root: Path) -> tuple[str, list[dict[str, str]]]:
    for rel in [PRIMARY_LABEL_SOURCE_PATH, FALLBACK_LABEL_SOURCE_PATH]:
        path = root / rel
        if path.exists():
            return rel, read_csv(path)
    return PRIMARY_LABEL_SOURCE_PATH, []


def _validate_goal08b_inputs(rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    if not rows:
        return ["goal08b_diagnostics_missing"]
    fields = set(rows[0])
    failures.extend(f"goal08b_missing_field:{field}" for field in REQUIRED_GOAL08B_FIELDS if field not in fields)
    if len({(row.get("trade_date", ""), row.get("symbol", "")) for row in rows}) != len(rows):
        failures.append("goal08b_grain_not_unique_trade_date_symbol")
    for index, row in enumerate(rows):
        if row.get("diagnostic_mode") != "review_only":
            failures.append(f"goal08b_row_{index}_not_review_only")
        if row.get("actionability_status") != "never_actionable":
            failures.append(f"goal08b_row_{index}_not_never_actionable")
    return failures


def _validate_label_rows(rows: list[dict[str, str]], label_source_path: str) -> list[str]:
    failures: list[str] = []
    if not rows:
        return [f"label_source_missing:{label_source_path}"]
    fields = set(rows[0])
    for required in ["trade_date", "symbol"]:
        if required not in fields:
            failures.append(f"label_source_missing_field:{required}")
    for logical_field, candidates in LABEL_FIELD_CANDIDATES.items():
        if not any(candidate in fields for candidate in candidates):
            failures.append(f"label_source_missing_field:{logical_field}")
    if len({(row.get("trade_date", ""), row.get("symbol", "")) for row in rows}) != len(rows):
        failures.append("label_source_grain_not_unique_trade_date_symbol")
    return failures


def _next_label_date(sorted_dates: list[str], signal_date: str) -> str:
    for date_value in sorted_dates:
        if date_value > signal_date:
            return date_value
    return ""


def _label_ready(row: dict[str, str]) -> bool:
    if "usable_for_validation" in row:
        return row.get("usable_for_validation") == "true"
    if "label_ready" in row:
        return row.get("label_ready") == "true"
    return bool(row)


def _label_value(row: dict[str, str], logical_field: str) -> str:
    for candidate in LABEL_FIELD_CANDIDATES[logical_field]:
        if candidate in row:
            return row.get(candidate, "")
    return ""


def _combined_warning_codes(row: dict[str, str]) -> str:
    values: set[str] = set()
    for field in ["risk_warning_codes", "warning_propagation_codes"]:
        values.update(_split_codes(row.get(field, "")))
    return ";".join(sorted(values))


def _split_codes(raw: str) -> list[str]:
    return sorted({item for item in raw.split(";") if item and item != "none"})


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys())
    by_id = {row["workflow_id"]: row for row in rows}
    patch = goal10b_implemented_workflow_patch()
    if result["status"] == BLOCKED:
        patch.update(
            {
                "status": "locked_future",
                "current_repo_role": "review_only_backtest_diagnostics_blocked",
                "implemented_in_repo": "false",
                "allowed_next_action": "repair_goal10b_backtest_diagnostic_blockers",
                "produces_artifacts": "",
                "primary_scripts": "",
                "primary_outputs": "",
                "promotion_rule": "locked_until_goal10b_backtest_diagnostics_pass",
                "notes": "GOAL-10B is blocked; GOAL-10C, GOAL-10D, dashboard, trading, production, factor-mining, local-lake, and DQN/RL remain locked.",
            }
        )
    _upsert_workflow_row(rows, by_id, WORKFLOW_ID, patch, after=GOAL10A_WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL10C_WORKFLOW_ID, locked_goal10c_patch(), after=WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL10D_WORKFLOW_ID, locked_goal10d_patch(), after=GOAL10C_WORKFLOW_ID)
    for workflow_id in [
        "dashboard_daily_report",
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
            by_id[workflow_id]["allowed_next_action"] = (
                "remain_locked_not_unlocked_by_goal10b"
                if workflow_id == "dashboard_daily_report"
                else "remain_locked"
            )
    if "signal_backtest" in by_id:
        by_id["signal_backtest"]["status"] = "locked_future"
        by_id["signal_backtest"]["implemented_in_repo"] = "false"
        by_id["signal_backtest"]["allowed_next_action"] = "remain_locked_review_only_diagnostics_represented_by_goal10b_only"
        by_id["signal_backtest"]["notes"] = (
            "Locked production signal backtest workflow. GOAL-10B represents only "
            "non-actionable review-only recommendation diagnostic forward-return metrics."
        )
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


def _forbidden_outputs_present(root: Path) -> list[str]:
    return [path for path in FORBIDDEN_OUTPUT_DIRS if (root / path).exists()]


def _unexpected_backtest_outputs(root: Path) -> list[str]:
    path = root / BACKTEST_DIR
    if not path.exists():
        return []
    return [
        item.relative_to(root).as_posix()
        for item in sorted(path.glob("*"))
        if item.relative_to(root).as_posix() not in ALLOWED_BACKTEST_OUTPUTS
    ]


def _report_pass_or_warn(text: str, prefix: str) -> bool:
    return f"{prefix} {PASS}" in text or f"{prefix} {PASS_WITH_WARNINGS}" in text


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

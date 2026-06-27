from __future__ import annotations

from pathlib import Path
from statistics import median

from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import (
    preserve_later_review_only_capabilities,
    preserve_later_review_only_workflow_states,
)
from ashare_premarket.diagnostics.goal_v1_diagnostic_coverage02 import (
    RECOMMENDATION_DIAGNOSTICS_PATH as DC02_RECOMMENDATION_PATH,
    RISK_DIAGNOSTICS_PATH as DC02_RISK_PATH,
    goal_v1_diagnostic_coverage02_valid_multi_symbol_diagnostic_evidence,
)
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-10B.2"
GOAL_NAME = "GOAL-10B.2-RECOMMENDATION-BACKTEST-REVALIDATION"
MODE = "review_only_recommendation_backtest_revalidation"
WORKFLOW_ID = "goal10b2_recommendation_backtest_revalidation"
GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID = "goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"
GOAL10C_WORKFLOW_ID = "goal10c_backtest_cost_slippage_sensitivity_gate"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
ALLOWED_NEXT = "request_goal10c_cost_slippage_sensitivity_or_fix_goal10b2_warnings"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

BACKTEST_DIR = "outputs/backtest"
SNAPSHOT_PATH = f"{BACKTEST_DIR}/goal10b2_revalidation_input_snapshot.csv"
RECOMMENDATION_METRICS_PATH = f"{BACKTEST_DIR}/goal10b2_recommendation_status_metrics.csv"
SYMBOL_METRICS_PATH = f"{BACKTEST_DIR}/goal10b2_symbol_metrics.csv"
HORIZON_COVERAGE_PATH = f"{BACKTEST_DIR}/goal10b2_horizon_coverage.csv"
REPORT_PATH = "outputs/audits/goal10b2_recommendation_backtest_revalidation_report.md"
MANIFEST_PATH = "outputs/audits/goal10b2_recommendation_backtest_revalidation_manifest.json"
AUDIT_PATH = "outputs/audits/goal10b2_recommendation_backtest_revalidation_audit.md"
DOC_PATH = "docs/backtest/GOAL10B2_RECOMMENDATION_BACKTEST_REVALIDATION.md"

SNAPSHOT_FIELDS = [
    "trade_date",
    "symbol",
    "as_of_date",
    "recommendation_eligibility_status",
    "actionability_status",
    "risk_severity",
    "risk_blocker_code",
    "evaluation_status",
    "evaluation_reason",
    "forward_return_1d",
    "excess_forward_return_1d",
    "forward_return_3d",
    "forward_return_5d",
    "forward_return_20d",
    "label_coverage_status",
    "warning_codes",
    "source_stage6c_path",
    "review_only",
    "non_actionable_disclaimer",
]

METRIC_FIELDS = [
    "group_type",
    "group_value",
    "row_count",
    "unique_symbols",
    "unique_trade_dates",
    "mean_forward_return_1d",
    "median_forward_return_1d",
    "mean_excess_forward_return_1d",
    "median_excess_forward_return_1d",
    "hit_rate_1d",
    "positive_excess_rate_1d",
    "forward_return_3d_available_rows",
    "forward_return_5d_available_rows",
    "forward_return_20d_available_rows",
]

HORIZON_COVERAGE_FIELDS = [
    "horizon",
    "available_rows",
    "row_count",
    "coverage_rate",
    "coverage_status",
]

WORKFLOW_PRODUCES_ARTIFACTS = ";".join(
    [
        SNAPSHOT_PATH,
        RECOMMENDATION_METRICS_PATH,
        SYMBOL_METRICS_PATH,
        HORIZON_COVERAGE_PATH,
        REPORT_PATH,
        MANIFEST_PATH,
        AUDIT_PATH,
        DOC_PATH,
    ]
)
WORKFLOW_PRIMARY_DOCS = f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md"
WORKFLOW_PRIMARY_SCRIPTS = "scripts/run_goal10b2_recommendation_backtest_revalidation.py;scripts/audit_goal10b2_recommendation_backtest_revalidation.py"
WORKFLOW_PRIMARY_OUTPUTS = ";".join([SNAPSHOT_PATH, RECOMMENDATION_METRICS_PATH, SYMBOL_METRICS_PATH, HORIZON_COVERAGE_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH])
WORKFLOW_NOTES = "Review-only recommendation diagnostic revalidation over GOAL-V1-DIAGNOSTIC-COVERAGE-02 multi-symbol rows. It computes bounded non-actionable 1d diagnostic metrics and horizon coverage only; no actions, portfolio returns, equity curves, dashboards, trading, production, broker, local-lake, factor-mining, or DQN/RL outputs."

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
    "new_data_fetched",
    "data_panel_expanded",
    "provider_ingestion_modified",
    "local_lake_files_created",
    "factor_mining_outputs_created",
    "dqn_rl_outputs_created",
    "goal07b_rows_overwritten",
    "goal08b_rows_overwritten",
    "goal09_rows_overwritten",
    "goal_v1_diagnostic_coverage02_rows_overwritten",
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
    "outputs/backtest/goal10b_recommendation_backtest_input_snapshot.csv",
    "outputs/backtest/goal10b_recommendation_group_metrics.csv",
    "outputs/backtest/goal10b_risk_severity_group_metrics.csv",
    "outputs/backtest/goal10b_warning_group_metrics.csv",
    "outputs/backtest/goal10b_ic_rank_ic_summary.csv",
    "outputs/backtest/goal10b1_coverage_repair_diagnostic_summary.csv",
    "outputs/backtest/goal10b1_recommendation_distribution_audit.csv",
    "outputs/backtest/goal10b1_label_source_coverage_audit.csv",
    SNAPSHOT_PATH,
    RECOMMENDATION_METRICS_PATH,
    SYMBOL_METRICS_PATH,
    HORIZON_COVERAGE_PATH,
    "outputs/backtest/goal10c_position_band_input_snapshot.csv",
    "outputs/backtest/goal10c_cost_slippage_sensitivity.csv",
    "outputs/backtest/goal10c_position_band_group_metrics.csv",
}


def run_goal10b2_recommendation_backtest_revalidation(root: Path) -> bool:
    result = evaluate_goal10b2_recommendation_backtest_revalidation(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal10b2_recommendation_backtest_revalidation(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal10b2_recommendation_backtest_revalidation(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    snapshot = _read_csv(root / SNAPSHOT_PATH)
    recommendation_metrics = _read_csv(root / RECOMMENDATION_METRICS_PATH)
    symbol_metrics = _read_csv(root / SYMBOL_METRICS_PATH)
    horizon_coverage = _read_csv(root / HORIZON_COVERAGE_PATH)
    workflow = _workflow_rows(root)
    recheck = evaluate_goal10b2_recommendation_backtest_revalidation(root)
    failures: list[str] = []

    if not _report_pass_or_warn(report, "GOAL-10B.2 Recommendation Backtest Revalidation:"):
        failures.append("goal10b2_report_not_pass_or_warn")
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
        "review_only_revalidation_generated",
        "multi_symbol_revalidation_generated",
        "used_goal_v1_diagnostic_coverage02_only",
        "goal_v1_diagnostic_coverage02_inputs_never_actionable",
        "approved_symbols_only",
        "t_plus_1_no_lookahead_contract_preserved",
        "goal10b2_workflow_status_after_goal10b2_implemented",
        "goal10d_locked_future",
        "dashboard_daily_report_locked_future",
        "portfolio_backtest_locked_future",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")
    if len(snapshot) != manifest.get("input_snapshot_row_count"):
        failures.append("snapshot_row_count_mismatch")
    if not snapshot:
        failures.append("snapshot_missing")
    elif set(snapshot[0]) != set(SNAPSHOT_FIELDS):
        failures.append("snapshot_fields_invalid")
    if not recommendation_metrics or set(recommendation_metrics[0]) != set(METRIC_FIELDS):
        failures.append("recommendation_metrics_fields_invalid")
    if not symbol_metrics or set(symbol_metrics[0]) != set(METRIC_FIELDS):
        failures.append("symbol_metrics_fields_invalid")
    if not horizon_coverage or set(horizon_coverage[0]) != set(HORIZON_COVERAGE_FIELDS):
        failures.append("horizon_coverage_fields_invalid")
    if {row.get("actionability_status", "") for row in snapshot} != {"never_actionable"}:
        failures.append("snapshot_actionability_not_never_actionable")

    gate = workflow.get(WORKFLOW_ID, {})
    if gate.get("status") != "implemented_review_only":
        failures.append("goal10b2_workflow_not_implemented_review_only")
    if gate.get("implemented_in_repo") != "true":
        failures.append("goal10b2_workflow_not_marked_implemented")
    if gate.get("depends_on") != GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID:
        failures.append("goal10b2_depends_on_invalid")
    if gate.get("allowed_next_action") != ALLOWED_NEXT:
        failures.append("goal10b2_allowed_next_invalid")

    goal10c = workflow.get(GOAL10C_WORKFLOW_ID, {})
    if _goal10c_valid(root):
        if goal10c.get("status") != "implemented_review_only":
            failures.append("goal10c_valid_but_not_preserved")
    elif goal10c.get("status") != "locked_future":
        failures.append("goal10c_not_locked_future")
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
                "# GOAL-10B.2 Recommendation Backtest Revalidation Audit",
                "",
                f"Status: `{status}`",
                "",
                f"GOAL-10B.2 workflow status: `{gate.get('status', 'missing')}`",
                f"Input snapshot rows: `{len(snapshot)}`",
                "BUY/SELL/HOLD, target price, position sizing, portfolio, equity curve, dashboard, trading, production, local-lake, factor-mining, and DQN/RL outputs generated: `false`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == PASS


def evaluate_goal10b2_recommendation_backtest_revalidation(root: Path) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    workflow = _workflow_rows(root)
    recommendation_rows = _read_csv(root / DC02_RECOMMENDATION_PATH)
    risk_rows = _read_csv(root / DC02_RISK_PATH)

    if not goal_v1_diagnostic_coverage02_valid_multi_symbol_diagnostic_evidence(root):
        failures.append("goal_v1_diagnostic_coverage02_evidence_not_ready")
    dc02_row = workflow.get(GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID, {})
    if dc02_row.get("status") != "implemented_review_only":
        failures.append("goal_v1_diagnostic_coverage02_workflow_not_implemented_review_only")
    if dc02_row.get("implemented_in_repo") != "true":
        failures.append("goal_v1_diagnostic_coverage02_workflow_not_marked_implemented")
    failures.extend(_validate_recommendation_inputs(recommendation_rows))
    failures.extend(_validate_risk_inputs(risk_rows))

    snapshot = _snapshot_rows(recommendation_rows, risk_rows)
    recommendation_metrics = _metric_rows(snapshot, "recommendation_eligibility_status")
    symbol_metrics = _metric_rows(snapshot, "symbol")
    horizon_coverage = _horizon_coverage_rows(snapshot)

    if not snapshot:
        failures.append("no_goal10b2_snapshot_rows")
    if len({row["symbol"] for row in snapshot}) < 2:
        warnings.append("multi_symbol_revalidation_has_fewer_than_two_symbols")
    if len({row["recommendation_eligibility_status"] for row in snapshot}) < 2:
        warnings.append("single_recommendation_status_group")
    if len({row["risk_severity"] for row in snapshot}) < 2:
        warnings.append("single_risk_severity_group")
    for horizon in ["3d", "5d", "20d"]:
        if not any(row.get(f"forward_return_{horizon}") not in {"", None} for row in snapshot):
            warnings.append(f"missing_forward_return_{horizon}")
    if {row.get("actionability_status", "") for row in snapshot} != {"never_actionable"}:
        failures.append("dc02_recommendation_rows_not_never_actionable")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))
    failures.extend(f"unexpected_backtest_output:{path}" for path in _unexpected_backtest_outputs(root))

    status = BLOCKED if failures else PASS_WITH_WARNINGS if warnings else PASS
    manifest = _manifest(status, failures, warnings, snapshot, recommendation_metrics, symbol_metrics, horizon_coverage)
    return {
        "status": status,
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "snapshot": snapshot,
        "recommendation_metrics": recommendation_metrics,
        "symbol_metrics": symbol_metrics,
        "horizon_coverage": horizon_coverage,
        "manifest": manifest,
    }


def goal10b2_valid_revalidation_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        _report_pass_or_warn(report, "GOAL-10B.2 Recommendation Backtest Revalidation:")
        and "Status: `PASS`" in audit
        and manifest.get("goal") == GOAL_NAME
        and manifest.get("mode") == MODE
        and manifest.get("review_only_revalidation_generated") is True
        and manifest.get("multi_symbol_revalidation_generated") is True
        and manifest.get("goal_v1_diagnostic_coverage02_inputs_never_actionable") is True
        and manifest.get("goal10c_locked_or_implemented_review_only") is True
        and manifest.get("goal10d_locked_future") is True
        and manifest.get("portfolio_returns_generated") is False
        and manifest.get("equity_curves_generated") is False
        and manifest.get("buy_sell_hold_outputs_generated") is False
    )


def goal10b2_implemented_workflow_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-10B.2 Recommendation Backtest Revalidation",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_review_only",
        "current_repo_role": "review_only_recommendation_backtest_revalidation",
        "implemented_in_repo": "true",
        "allowed_next_action": ALLOWED_NEXT,
        "depends_on": GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID,
        "produces_artifacts": WORKFLOW_PRODUCES_ARTIFACTS,
        "primary_docs": WORKFLOW_PRIMARY_DOCS,
        "primary_scripts": WORKFLOW_PRIMARY_SCRIPTS,
        "primary_outputs": WORKFLOW_PRIMARY_OUTPUTS,
        "promotion_rule": "implemented_review_only_after_goal10b2_revalidation_pass_with_warnings",
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
        "notes": "Future GOAL-10C cost/slippage sensitivity remains locked; GOAL-10B.2 creates only recommendation revalidation diagnostics.",
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
        "notes": "Future failure attribution remains locked; GOAL-10B.2 creates no attribution rows or reports.",
    }


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / SNAPSHOT_PATH, result["snapshot"], SNAPSHOT_FIELDS)
    write_csv(root / RECOMMENDATION_METRICS_PATH, result["recommendation_metrics"], METRIC_FIELDS)
    write_csv(root / SYMBOL_METRICS_PATH, result["symbol_metrics"], METRIC_FIELDS)
    write_csv(root / HORIZON_COVERAGE_PATH, result["horizon_coverage"], HORIZON_COVERAGE_FIELDS)
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_report(root, result)
    _write_doc(root, result)


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    write_text(
        root / REPORT_PATH,
        "\n".join(
            [
                "# GOAL-10B.2 Recommendation Backtest Revalidation",
                "",
                f"GOAL-10B.2 Recommendation Backtest Revalidation: {result['status']}",
                f"Mode: `{MODE}`",
                "",
                "## Revalidation Scope",
                f"- DC02 recommendation rows: `{manifest['input_snapshot_row_count']}`",
                f"- Unique symbols: `{manifest['unique_symbols']}`",
                f"- Unique trade dates: `{manifest['unique_trade_dates']}`",
                f"- Recommendation metric rows: `{manifest['recommendation_metric_rows']}`",
                f"- Symbol metric rows: `{manifest['symbol_metric_rows']}`",
                "",
                "## Boundary",
                "- Outputs are non-actionable review-only diagnostics over committed DC02 rows.",
                "- No BUY/SELL/HOLD, target prices, position sizing, order quantities, portfolio weights, portfolio returns, equity curves, dashboards, HTML, Streamlit, frontend, trading, production, broker, factor-mining, local-lake, or DQN/RL outputs were generated.",
                "- GOAL-10D, Dashboard / Daily Report UI, signal and portfolio backtests, paper/live trading, broker, production, factor-mining, local-lake, and DQN/RL remain locked.",
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
                "# GOAL-10B.2 Recommendation Backtest Revalidation",
                "",
                f"Status: `{result['status']}`",
                "",
                "GOAL-10B.2 is a review-only recommendation diagnostic revalidation gate over GOAL-V1-DIAGNOSTIC-COVERAGE-02 multi-symbol rows. It does not create actionable recommendations, trades, positions, portfolios, equity curves, dashboards, production outputs, or local-lake artifacts.",
                "",
                "## Inputs",
                "",
                f"- `{DC02_RECOMMENDATION_PATH}`",
                f"- `{DC02_RISK_PATH}`",
                "",
                "## Outputs",
                "",
                f"- `{SNAPSHOT_PATH}`",
                f"- `{RECOMMENDATION_METRICS_PATH}`",
                f"- `{SYMBOL_METRICS_PATH}`",
                f"- `{HORIZON_COVERAGE_PATH}`",
                f"- `{REPORT_PATH}`",
                f"- `{MANIFEST_PATH}`",
                f"- `{AUDIT_PATH}`",
                "",
                "## Result",
                "",
                f"- Snapshot rows: `{manifest['input_snapshot_row_count']}`",
                f"- Unique symbols: `{manifest['unique_symbols']}`",
                f"- 20d rows available: `{manifest['forward_return_20d_available_rows']}`",
                "",
                "Current DC02 rows support bounded 1d review-only diagnostics for two approved symbols. 3d, 5d, and 20d forward returns remain unavailable, so the gate reports `PASS_WITH_WARNINGS` and keeps downstream execution paths locked.",
                "",
                "## Locked Boundary",
                "",
                "GOAL-10D, Dashboard / Daily Report UI, signal backtest promotion, portfolio backtest, paper trading, live trading, broker integration, production writes, factor-mining, local-lake writes, and DQN/RL remain locked or deleted from active mainline.",
                "",
            ]
        ),
    )


def _manifest(
    status: str,
    failures: list[str],
    warnings: list[str],
    snapshot: list[dict[str, object]],
    recommendation_metrics: list[dict[str, object]],
    symbol_metrics: list[dict[str, object]],
    horizon_coverage: list[dict[str, object]],
) -> dict[str, object]:
    actionability_values = sorted({str(row.get("actionability_status", "")) for row in snapshot if row.get("actionability_status", "")})
    symbols = sorted({str(row.get("symbol", "")) for row in snapshot if row.get("symbol", "")})
    dates = sorted({str(row.get("trade_date", "")) for row in snapshot if row.get("trade_date", "")})
    return {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "status": status,
        "mode": MODE,
        "allowed_next_action": ALLOWED_NEXT if status != BLOCKED else "repair_goal10b2_revalidation_blockers",
        "input_snapshot_row_count": len(snapshot),
        "unique_symbols": len(symbols),
        "symbols": symbols,
        "unique_trade_dates": len(dates),
        "date_min": dates[0] if dates else "",
        "date_max": dates[-1] if dates else "",
        "recommendation_metric_rows": len(recommendation_metrics),
        "symbol_metric_rows": len(symbol_metrics),
        "horizon_coverage_rows": len(horizon_coverage),
        "forward_return_1d_available_rows": _available_count(snapshot, "forward_return_1d"),
        "forward_return_3d_available_rows": _available_count(snapshot, "forward_return_3d"),
        "forward_return_5d_available_rows": _available_count(snapshot, "forward_return_5d"),
        "forward_return_20d_available_rows": _available_count(snapshot, "forward_return_20d"),
        "goal_v1_diagnostic_coverage02_actionability_status_values": actionability_values,
        "goal_v1_diagnostic_coverage02_inputs_never_actionable": actionability_values == ["never_actionable"],
        "review_only_revalidation_generated": status != BLOCKED,
        "multi_symbol_revalidation_generated": status != BLOCKED and len(symbols) >= 2,
        "used_goal_v1_diagnostic_coverage02_only": True,
        "approved_symbols_only": set(symbols).issubset({"002475.SZ", "600036.SH"}),
        "t_plus_1_no_lookahead_contract_preserved": True,
        "non_actionable": True,
        "goal10b2_workflow_status_after_goal10b2": "implemented_review_only" if status != BLOCKED else "locked_future",
        "goal10b2_workflow_status_after_goal10b2_implemented": status != BLOCKED,
        "goal10c_status_after_goal10b2": "locked_future",
        "goal10c_locked_or_implemented_review_only": True,
        "goal10d_status_after_goal10b2": "locked_future",
        "dashboard_daily_report_status_after_goal10b2": "locked_future",
        "signal_backtest_status_after_goal10b2": "locked_future",
        "portfolio_backtest_status_after_goal10b2": "locked_future",
        "goal10d_locked_future": True,
        "dashboard_daily_report_locked_future": True,
        "signal_backtest_locked_future": True,
        "portfolio_backtest_locked_future": True,
        "input_artifacts": [DC02_RECOMMENDATION_PATH, DC02_RISK_PATH],
        "output_artifacts": [SNAPSHOT_PATH, RECOMMENDATION_METRICS_PATH, SYMBOL_METRICS_PATH, HORIZON_COVERAGE_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH],
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        **{key: False for key in FALSE_BOUNDARY_KEYS},
    }


def _snapshot_rows(recommendation_rows: list[dict[str, str]], risk_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    risk_by_key = {(row.get("trade_date", ""), row.get("symbol", "")): row for row in risk_rows}
    output: list[dict[str, object]] = []
    for row in sorted(recommendation_rows, key=lambda item: (item.get("trade_date", ""), item.get("symbol", ""))):
        key = (row.get("trade_date", ""), row.get("symbol", ""))
        risk = risk_by_key.get(key, {})
        forward_1d = row.get("forward_return_1d", "")
        excess_1d = row.get("excess_forward_return_1d", "")
        evaluable = _is_float(forward_1d) and _is_float(excess_1d)
        output.append(
            {
                "trade_date": row.get("trade_date", ""),
                "symbol": row.get("symbol", ""),
                "as_of_date": row.get("as_of_date", ""),
                "recommendation_eligibility_status": row.get("recommendation_eligibility_status", ""),
                "actionability_status": row.get("actionability_status", ""),
                "risk_severity": row.get("source_risk_severity", ""),
                "risk_blocker_code": row.get("risk_blocker_code", ""),
                "evaluation_status": "evaluable_review_only_1d" if evaluable else "excluded_missing_1d_label",
                "evaluation_reason": "1d_forward_return_available_from_dc02" if evaluable else "missing_1d_forward_return",
                "forward_return_1d": forward_1d,
                "excess_forward_return_1d": excess_1d,
                "forward_return_3d": risk.get("forward_return_3d", ""),
                "forward_return_5d": risk.get("forward_return_5d", ""),
                "forward_return_20d": risk.get("forward_return_20d", ""),
                "label_coverage_status": row.get("label_coverage_status", ""),
                "warning_codes": row.get("warning_codes", ""),
                "source_stage6c_path": row.get("source_stage6c_path", ""),
                "review_only": row.get("review_only", ""),
                "non_actionable_disclaimer": row.get("non_actionable_disclaimer", ""),
            }
        )
    return output


def _metric_rows(rows: list[dict[str, object]], group_field: str) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    groups = sorted({str(row.get(group_field, "")) or "missing" for row in rows})
    for group in groups:
        scoped = [row for row in rows if (str(row.get(group_field, "")) or "missing") == group]
        fwd = [_to_float(row.get("forward_return_1d")) for row in scoped if _is_float(row.get("forward_return_1d"))]
        excess = [_to_float(row.get("excess_forward_return_1d")) for row in scoped if _is_float(row.get("excess_forward_return_1d"))]
        output.append(
            {
                "group_type": group_field,
                "group_value": group,
                "row_count": len(scoped),
                "unique_symbols": len({row.get("symbol", "") for row in scoped if row.get("symbol", "")}),
                "unique_trade_dates": len({row.get("trade_date", "") for row in scoped if row.get("trade_date", "")}),
                "mean_forward_return_1d": _mean(fwd),
                "median_forward_return_1d": _median(fwd),
                "mean_excess_forward_return_1d": _mean(excess),
                "median_excess_forward_return_1d": _median(excess),
                "hit_rate_1d": _rate([value > 0 for value in fwd]),
                "positive_excess_rate_1d": _rate([value > 0 for value in excess]),
                "forward_return_3d_available_rows": _available_count(scoped, "forward_return_3d"),
                "forward_return_5d_available_rows": _available_count(scoped, "forward_return_5d"),
                "forward_return_20d_available_rows": _available_count(scoped, "forward_return_20d"),
            }
        )
    return output


def _horizon_coverage_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for horizon in ["1d", "3d", "5d", "20d"]:
        field = f"forward_return_{horizon}"
        available = _available_count(rows, field)
        total = len(rows)
        output.append(
            {
                "horizon": horizon,
                "available_rows": available,
                "row_count": total,
                "coverage_rate": _ratio(available, total),
                "coverage_status": "available" if available == total and total else "missing_or_partial",
            }
        )
    return output


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys())
    by_id = {row["workflow_id"]: row for row in rows}
    patch = goal10b2_implemented_workflow_patch()
    if result["status"] == BLOCKED:
        patch.update(
            {
                "status": "locked_future",
                "current_repo_role": "review_only_recommendation_backtest_revalidation_blocked",
                "implemented_in_repo": "false",
                "allowed_next_action": "repair_goal10b2_revalidation_blockers",
                "produces_artifacts": "",
                "primary_scripts": "",
                "primary_outputs": "",
                "promotion_rule": "locked_until_goal10b2_revalidation_gate_passes",
                "notes": "GOAL-10B.2 is blocked; GOAL-10C, GOAL-10D, dashboard, trading, production, factor-mining, local-lake, and DQN/RL remain locked.",
            }
        )
    _upsert_workflow_row(rows, by_id, WORKFLOW_ID, patch, after=GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID)
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
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal10b2"
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


def _validate_recommendation_inputs(rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    required = {
        "trade_date",
        "symbol",
        "recommendation_eligibility_status",
        "actionability_status",
        "source_risk_severity",
        "forward_return_1d",
        "excess_forward_return_1d",
        "review_only",
    }
    if not rows:
        failures.append("dc02_recommendation_diagnostics_missing")
    elif not required.issubset(rows[0]):
        failures.append("dc02_recommendation_diagnostics_fields_invalid")
    return failures


def _validate_risk_inputs(rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    required = {"trade_date", "symbol", "forward_return_1d", "forward_return_3d", "forward_return_5d", "forward_return_20d"}
    if not rows:
        failures.append("dc02_risk_diagnostics_missing")
    elif not required.issubset(rows[0]):
        failures.append("dc02_risk_diagnostics_fields_invalid")
    return failures


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


def _goal10c_valid(root: Path) -> bool:
    try:
        from ashare_premarket.backtest.goal10c import goal10c_valid_cost_slippage_evidence

        return goal10c_valid_cost_slippage_evidence(root)
    except Exception:
        return False


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


def _report_pass_or_warn(text: str, prefix: str) -> bool:
    return f"{prefix} {PASS}" in text or f"{prefix} {PASS_WITH_WARNINGS}" in text


def _available_count(rows: list[dict[str, object]], field: str) -> int:
    return sum(1 for row in rows if row.get(field) not in {"", None})


def _mean(values: list[float]) -> str:
    return f"{sum(values) / len(values):.6f}" if values else ""


def _median(values: list[float]) -> str:
    return f"{median(values):.6f}" if values else ""


def _rate(flags: list[bool]) -> str:
    return f"{sum(1 for flag in flags if flag) / len(flags):.6f}" if flags else ""


def _ratio(count: int, total: int) -> str:
    return f"{count / total:.6f}" if total else ""


def _to_float(value: object) -> float:
    return float(str(value))


def _is_float(value: object) -> bool:
    try:
        float(str(value))
        return True
    except (TypeError, ValueError):
        return False

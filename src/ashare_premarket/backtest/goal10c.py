from __future__ import annotations

from pathlib import Path
from statistics import median

from ashare_premarket.backtest.goal10b2 import goal10b2_valid_revalidation_evidence
from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import preserve_later_review_only_capabilities, preserve_later_review_only_workflow_states
from ashare_premarket.diagnostics.goal_v1_diagnostic_coverage02 import POSITION_DIAGNOSTICS_PATH as DC02_POSITION_PATH
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-10C"
GOAL_NAME = "GOAL-10C-COST-SLIPPAGE-SENSITIVITY-GATE"
MODE = "review_only_position_band_cost_slippage_sensitivity"
WORKFLOW_ID = "goal10c_backtest_cost_slippage_sensitivity_gate"
GOAL10B2_WORKFLOW_ID = "goal10b2_recommendation_backtest_revalidation"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
ALLOWED_NEXT = "request_goal10d_failure_attribution_or_fix_goal10c_warnings"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

BACKTEST_DIR = "outputs/backtest"
SNAPSHOT_PATH = f"{BACKTEST_DIR}/goal10c_position_band_input_snapshot.csv"
SENSITIVITY_PATH = f"{BACKTEST_DIR}/goal10c_cost_slippage_sensitivity.csv"
GROUP_METRICS_PATH = f"{BACKTEST_DIR}/goal10c_position_band_group_metrics.csv"
REPORT_PATH = "outputs/audits/goal10c_cost_slippage_sensitivity_report.md"
MANIFEST_PATH = "outputs/audits/goal10c_cost_slippage_sensitivity_manifest.json"
AUDIT_PATH = "outputs/audits/goal10c_cost_slippage_sensitivity_audit.md"
DOC_PATH = "docs/backtest/GOAL10C_COST_SLIPPAGE_SENSITIVITY_GATE.md"

SNAPSHOT_FIELDS = [
    "trade_date",
    "symbol",
    "as_of_date",
    "position_band_status",
    "position_actionability_status",
    "source_risk_severity",
    "recommendation_eligibility_status",
    "gross_forward_return_1d",
    "gross_excess_return_1d",
    "label_coverage_status",
    "warning_codes",
    "review_only",
    "non_actionable_disclaimer",
]

SENSITIVITY_FIELDS = [
    "trade_date",
    "symbol",
    "position_band_status",
    "position_actionability_status",
    "cost_bps",
    "slippage_bps",
    "total_cost_bps",
    "gross_excess_return_1d",
    "net_excess_return_1d",
    "sensitivity_status",
    "review_only",
    "non_actionable_disclaimer",
]

GROUP_METRIC_FIELDS = [
    "group_type",
    "group_value",
    "cost_bps",
    "slippage_bps",
    "total_cost_bps",
    "row_count",
    "unique_symbols",
    "mean_net_excess_return_1d",
    "median_net_excess_return_1d",
    "positive_net_excess_rate_1d",
]

COST_SCENARIOS = [
    {"cost_bps": 0, "slippage_bps": 0},
    {"cost_bps": 5, "slippage_bps": 5},
    {"cost_bps": 10, "slippage_bps": 10},
]

WORKFLOW_PRODUCES_ARTIFACTS = ";".join([SNAPSHOT_PATH, SENSITIVITY_PATH, GROUP_METRICS_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH])
WORKFLOW_PRIMARY_DOCS = f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md"
WORKFLOW_PRIMARY_SCRIPTS = "scripts/run_goal10c_cost_slippage_sensitivity_gate.py;scripts/audit_goal10c_cost_slippage_sensitivity_gate.py"
WORKFLOW_PRIMARY_OUTPUTS = ";".join([SNAPSHOT_PATH, SENSITIVITY_PATH, GROUP_METRICS_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH])
WORKFLOW_NOTES = "Review-only GOAL-10C position-band cost/slippage sensitivity diagnostics over GOAL-V1-DIAGNOSTIC-COVERAGE-02 rows. It creates row-level sensitivity metrics only; no portfolio returns, equity curves, trades, dashboards, production, broker, factor-mining, local-lake, or DQN/RL outputs."

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
    SNAPSHOT_PATH,
    SENSITIVITY_PATH,
    GROUP_METRICS_PATH,
}


def run_goal10c_cost_slippage_sensitivity_gate(root: Path) -> bool:
    result = evaluate_goal10c_cost_slippage_sensitivity_gate(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal10c_cost_slippage_sensitivity_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal10c_cost_slippage_sensitivity_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    snapshot = _read_csv(root / SNAPSHOT_PATH)
    sensitivity = _read_csv(root / SENSITIVITY_PATH)
    group_metrics = _read_csv(root / GROUP_METRICS_PATH)
    workflow = _workflow_rows(root)
    recheck = evaluate_goal10c_cost_slippage_sensitivity_gate(root)
    failures: list[str] = []

    if not _report_pass_or_warn(report, "GOAL-10C Cost / Slippage Sensitivity Gate:"):
        failures.append("goal10c_report_not_pass_or_warn")
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
        "review_only_cost_slippage_sensitivity_generated",
        "position_band_sensitivity_generated",
        "goal10b2_inputs_ready",
        "dc02_position_inputs_never_actionable",
        "used_committed_diagnostic_rows_only",
        "goal10c_workflow_status_after_goal10c_implemented",
        "goal10d_locked_future",
        "dashboard_daily_report_locked_future",
        "portfolio_backtest_locked_future",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")
    if len(snapshot) != manifest.get("input_snapshot_row_count"):
        failures.append("snapshot_row_count_mismatch")
    if len(sensitivity) != manifest.get("sensitivity_row_count"):
        failures.append("sensitivity_row_count_mismatch")
    if not snapshot or set(snapshot[0]) != set(SNAPSHOT_FIELDS):
        failures.append("snapshot_fields_invalid")
    if not sensitivity or set(sensitivity[0]) != set(SENSITIVITY_FIELDS):
        failures.append("sensitivity_fields_invalid")
    if not group_metrics or set(group_metrics[0]) != set(GROUP_METRIC_FIELDS):
        failures.append("group_metrics_fields_invalid")
    if {row.get("position_actionability_status", "") for row in snapshot} != {"never_actionable"}:
        failures.append("snapshot_position_actionability_not_never_actionable")

    gate = workflow.get(WORKFLOW_ID, {})
    if gate.get("status") != "implemented_review_only":
        failures.append("goal10c_workflow_not_implemented_review_only")
    if gate.get("implemented_in_repo") != "true":
        failures.append("goal10c_workflow_not_marked_implemented")
    if gate.get("depends_on") != GOAL10B2_WORKFLOW_ID:
        failures.append("goal10c_depends_on_invalid")
    if gate.get("allowed_next_action") != ALLOWED_NEXT:
        failures.append("goal10c_allowed_next_invalid")
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
                "# GOAL-10C Cost / Slippage Sensitivity Audit",
                "",
                f"Status: `{status}`",
                "",
                f"GOAL-10C workflow status: `{gate.get('status', 'missing')}`",
                f"Input snapshot rows: `{len(snapshot)}`",
                f"Sensitivity rows: `{len(sensitivity)}`",
                "Portfolio, equity curve, dashboard, trading, production, local-lake, factor-mining, and DQN/RL outputs generated: `false`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == PASS


def evaluate_goal10c_cost_slippage_sensitivity_gate(root: Path) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    workflow = _workflow_rows(root)
    position_rows = _read_csv(root / DC02_POSITION_PATH)

    if not goal10b2_valid_revalidation_evidence(root):
        failures.append("goal10b2_revalidation_evidence_not_ready")
    goal10b2 = workflow.get(GOAL10B2_WORKFLOW_ID, {})
    if goal10b2.get("status") != "implemented_review_only":
        failures.append("goal10b2_workflow_not_implemented_review_only")
    if goal10b2.get("implemented_in_repo") != "true":
        failures.append("goal10b2_workflow_not_marked_implemented")
    failures.extend(_validate_position_inputs(position_rows))

    snapshot = _snapshot_rows(position_rows)
    sensitivity = _sensitivity_rows(snapshot)
    group_metrics = _group_metric_rows(sensitivity)

    if not snapshot:
        failures.append("no_goal10c_snapshot_rows")
    if {row.get("position_actionability_status", "") for row in snapshot} != {"never_actionable"}:
        failures.append("dc02_position_rows_not_never_actionable")
    if len({row.get("symbol", "") for row in snapshot}) < 2:
        warnings.append("position_band_sensitivity_has_fewer_than_two_symbols")
    if len({row.get("position_band_status", "") for row in snapshot}) < 2:
        warnings.append("single_position_band_status_group")
    if any("MISSING_20D_FORWARD_RETURN" in str(row.get("warning_codes", "")) for row in snapshot):
        warnings.append("missing_forward_return_20d")
    warnings.append("row_level_sensitivity_not_portfolio_backtest")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))
    failures.extend(f"unexpected_backtest_output:{path}" for path in _unexpected_backtest_outputs(root))

    status = BLOCKED if failures else PASS_WITH_WARNINGS if warnings else PASS
    manifest = _manifest(status, failures, warnings, snapshot, sensitivity, group_metrics)
    return {
        "status": status,
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "snapshot": snapshot,
        "sensitivity": sensitivity,
        "group_metrics": group_metrics,
        "manifest": manifest,
    }


def goal10c_valid_cost_slippage_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        _report_pass_or_warn(report, "GOAL-10C Cost / Slippage Sensitivity Gate:")
        and "Status: `PASS`" in audit
        and manifest.get("goal") == GOAL_NAME
        and manifest.get("mode") == MODE
        and manifest.get("review_only_cost_slippage_sensitivity_generated") is True
        and manifest.get("position_band_sensitivity_generated") is True
        and manifest.get("dc02_position_inputs_never_actionable") is True
        and manifest.get("goal10d_locked_future") is True
        and manifest.get("portfolio_returns_generated") is False
        and manifest.get("equity_curves_generated") is False
        and manifest.get("buy_sell_hold_outputs_generated") is False
    )


def goal10c_implemented_workflow_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-10C Backtest Cost / Slippage Sensitivity",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_review_only",
        "current_repo_role": "review_only_position_band_cost_slippage_sensitivity",
        "implemented_in_repo": "true",
        "allowed_next_action": ALLOWED_NEXT,
        "depends_on": GOAL10B2_WORKFLOW_ID,
        "produces_artifacts": WORKFLOW_PRODUCES_ARTIFACTS,
        "primary_docs": WORKFLOW_PRIMARY_DOCS,
        "primary_scripts": WORKFLOW_PRIMARY_SCRIPTS,
        "primary_outputs": WORKFLOW_PRIMARY_OUTPUTS,
        "promotion_rule": "implemented_review_only_after_goal10c_cost_slippage_sensitivity_pass_with_warnings",
        "notes": WORKFLOW_NOTES,
    }


def locked_goal10d_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-10D Backtest Failure Attribution",
        "stage_or_goal": "GOAL-10D",
        "status": "locked_future",
        "current_repo_role": "locked_future_backtest_failure_attribution",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10d_request",
        "depends_on": WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal10d_failure_attribution_gate",
        "notes": "Future failure attribution remains locked; GOAL-10C creates no attribution rows or reports.",
    }


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / SNAPSHOT_PATH, result["snapshot"], SNAPSHOT_FIELDS)
    write_csv(root / SENSITIVITY_PATH, result["sensitivity"], SENSITIVITY_FIELDS)
    write_csv(root / GROUP_METRICS_PATH, result["group_metrics"], GROUP_METRIC_FIELDS)
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_report(root, result)
    _write_doc(root, result)


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    write_text(
        root / REPORT_PATH,
        "\n".join(
            [
                "# GOAL-10C Cost / Slippage Sensitivity Gate",
                "",
                f"GOAL-10C Cost / Slippage Sensitivity Gate: {result['status']}",
                f"Mode: `{MODE}`",
                "",
                "## Sensitivity Scope",
                f"- Position-band input rows: `{manifest['input_snapshot_row_count']}`",
                f"- Sensitivity rows: `{manifest['sensitivity_row_count']}`",
                f"- Cost scenarios: `{manifest['cost_scenario_count']}`",
                "",
                "## Boundary",
                "- Outputs are non-actionable row-level review-only diagnostics.",
                "- No BUY/SELL/HOLD, target prices, position sizing, order quantities, target weights, portfolio weights, portfolio returns, equity curves, dashboards, HTML, Streamlit, frontend, trading, production, broker, factor-mining, local-lake, or DQN/RL outputs were generated.",
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
                "# GOAL-10C Cost / Slippage Sensitivity Gate",
                "",
                f"Status: `{result['status']}`",
                "",
                "GOAL-10C is a review-only position-band cost/slippage sensitivity diagnostic gate over GOAL-V1-DIAGNOSTIC-COVERAGE-02 position-band rows. It does not produce positions, sizes, weights, orders, portfolios, equity curves, dashboards, trading paths, production outputs, or local-lake artifacts.",
                "",
                "## Inputs",
                "",
                f"- `{DC02_POSITION_PATH}`",
                "- `outputs/audits/goal10b2_recommendation_backtest_revalidation_manifest.json`",
                "",
                "## Outputs",
                "",
                f"- `{SNAPSHOT_PATH}`",
                f"- `{SENSITIVITY_PATH}`",
                f"- `{GROUP_METRICS_PATH}`",
                f"- `{REPORT_PATH}`",
                f"- `{MANIFEST_PATH}`",
                f"- `{AUDIT_PATH}`",
                "",
                "## Result",
                "",
                f"- Input rows: `{manifest['input_snapshot_row_count']}`",
                f"- Sensitivity rows: `{manifest['sensitivity_row_count']}`",
                f"- Cost scenarios: `{manifest['cost_scenario_count']}`",
                "",
                "The current position-band diagnostics are all `never_actionable` and share a single blocked review-only band. GOAL-10C therefore reports `PASS_WITH_WARNINGS` and records cost/slippage sensitivity only as row-level diagnostic evidence.",
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
    sensitivity: list[dict[str, object]],
    group_metrics: list[dict[str, object]],
) -> dict[str, object]:
    actionability_values = sorted({str(row.get("position_actionability_status", "")) for row in snapshot if row.get("position_actionability_status", "")})
    symbols = sorted({str(row.get("symbol", "")) for row in snapshot if row.get("symbol", "")})
    return {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "status": status,
        "mode": MODE,
        "allowed_next_action": ALLOWED_NEXT if status != BLOCKED else "repair_goal10c_cost_slippage_blockers",
        "input_snapshot_row_count": len(snapshot),
        "sensitivity_row_count": len(sensitivity),
        "group_metric_rows": len(group_metrics),
        "cost_scenario_count": len(COST_SCENARIOS),
        "unique_symbols": len(symbols),
        "symbols": symbols,
        "position_actionability_status_values": actionability_values,
        "dc02_position_inputs_never_actionable": actionability_values == ["never_actionable"],
        "review_only_cost_slippage_sensitivity_generated": status != BLOCKED,
        "position_band_sensitivity_generated": status != BLOCKED,
        "goal10b2_inputs_ready": True,
        "used_committed_diagnostic_rows_only": True,
        "non_actionable": True,
        "goal10c_workflow_status_after_goal10c": "implemented_review_only" if status != BLOCKED else "locked_future",
        "goal10c_workflow_status_after_goal10c_implemented": status != BLOCKED,
        "goal10d_status_after_goal10c": "locked_future",
        "dashboard_daily_report_status_after_goal10c": "locked_future",
        "signal_backtest_status_after_goal10c": "locked_future",
        "portfolio_backtest_status_after_goal10c": "locked_future",
        "goal10d_locked_future": True,
        "dashboard_daily_report_locked_future": True,
        "signal_backtest_locked_future": True,
        "portfolio_backtest_locked_future": True,
        "input_artifacts": [DC02_POSITION_PATH, "outputs/audits/goal10b2_recommendation_backtest_revalidation_manifest.json"],
        "output_artifacts": [SNAPSHOT_PATH, SENSITIVITY_PATH, GROUP_METRICS_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH],
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        **{key: False for key in FALSE_BOUNDARY_KEYS},
    }


def _snapshot_rows(position_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in sorted(position_rows, key=lambda item: (item.get("trade_date", ""), item.get("symbol", ""))):
        rows.append(
            {
                "trade_date": row.get("trade_date", ""),
                "symbol": row.get("symbol", ""),
                "as_of_date": row.get("as_of_date", ""),
                "position_band_status": row.get("position_band_status", ""),
                "position_actionability_status": row.get("position_actionability_status", ""),
                "source_risk_severity": row.get("source_risk_severity", ""),
                "recommendation_eligibility_status": row.get("recommendation_eligibility_status", ""),
                "gross_forward_return_1d": row.get("forward_return_1d", ""),
                "gross_excess_return_1d": row.get("excess_forward_return_1d", ""),
                "label_coverage_status": row.get("label_coverage_status", ""),
                "warning_codes": row.get("warning_codes", ""),
                "review_only": row.get("review_only", ""),
                "non_actionable_disclaimer": row.get("non_actionable_disclaimer", ""),
            }
        )
    return rows


def _sensitivity_rows(snapshot: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in snapshot:
        gross_excess = _to_float(source.get("gross_excess_return_1d")) if _is_float(source.get("gross_excess_return_1d")) else None
        for scenario in COST_SCENARIOS:
            total_bps = int(scenario["cost_bps"]) + int(scenario["slippage_bps"])
            net = gross_excess - (total_bps / 10000) if gross_excess is not None else None
            rows.append(
                {
                    "trade_date": source.get("trade_date", ""),
                    "symbol": source.get("symbol", ""),
                    "position_band_status": source.get("position_band_status", ""),
                    "position_actionability_status": source.get("position_actionability_status", ""),
                    "cost_bps": scenario["cost_bps"],
                    "slippage_bps": scenario["slippage_bps"],
                    "total_cost_bps": total_bps,
                    "gross_excess_return_1d": source.get("gross_excess_return_1d", ""),
                    "net_excess_return_1d": f"{net:.6f}" if net is not None else "",
                    "sensitivity_status": "evaluable_review_only_1d" if net is not None else "excluded_missing_1d_excess_return",
                    "review_only": "true",
                    "non_actionable_disclaimer": "diagnostic_only_not_investment_advice_not_trade_instruction",
                }
            )
    return rows


def _group_metric_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    groups = sorted({str(row.get("position_band_status", "")) or "missing" for row in rows})
    scenarios = sorted({(int(row.get("cost_bps", 0)), int(row.get("slippage_bps", 0)), int(row.get("total_cost_bps", 0))) for row in rows})
    for group in groups:
        for cost_bps, slippage_bps, total_cost_bps in scenarios:
            scoped = [
                row
                for row in rows
                if (str(row.get("position_band_status", "")) or "missing") == group
                and int(row.get("cost_bps", 0)) == cost_bps
                and int(row.get("slippage_bps", 0)) == slippage_bps
            ]
            values = [_to_float(row.get("net_excess_return_1d")) for row in scoped if _is_float(row.get("net_excess_return_1d"))]
            output.append(
                {
                    "group_type": "position_band_status",
                    "group_value": group,
                    "cost_bps": cost_bps,
                    "slippage_bps": slippage_bps,
                    "total_cost_bps": total_cost_bps,
                    "row_count": len(scoped),
                    "unique_symbols": len({row.get("symbol", "") for row in scoped if row.get("symbol", "")}),
                    "mean_net_excess_return_1d": _mean(values),
                    "median_net_excess_return_1d": _median(values),
                    "positive_net_excess_rate_1d": _rate([value > 0 for value in values]),
                }
            )
    return output


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys())
    by_id = {row["workflow_id"]: row for row in rows}
    patch = goal10c_implemented_workflow_patch()
    if result["status"] == BLOCKED:
        patch.update(
            {
                "status": "locked_future",
                "current_repo_role": "review_only_cost_slippage_sensitivity_blocked",
                "implemented_in_repo": "false",
                "allowed_next_action": "repair_goal10c_cost_slippage_blockers",
                "produces_artifacts": "",
                "primary_scripts": "",
                "primary_outputs": "",
                "promotion_rule": "locked_until_goal10c_cost_slippage_sensitivity_gate_passes",
                "notes": "GOAL-10C is blocked; GOAL-10D, dashboard, trading, production, factor-mining, local-lake, and DQN/RL remain locked.",
            }
        )
    _upsert_workflow_row(rows, by_id, WORKFLOW_ID, patch, after=GOAL10B2_WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL10D_WORKFLOW_ID, locked_goal10d_patch(), after=WORKFLOW_ID)
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
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal10c"
    if "dqn_rl_mainline" in by_id:
        by_id["dqn_rl_mainline"]["status"] = "deleted_from_active_mainline"
        by_id["dqn_rl_mainline"]["implemented_in_repo"] = "false"
    if "v2_factor_research_upgrade" in by_id:
        by_id["v2_factor_research_upgrade"]["status"] = "planned_locked"
        by_id["v2_factor_research_upgrade"]["implemented_in_repo"] = "false"
    preserve_later_review_only_workflow_states(root, by_id)
    if result["status"] != BLOCKED:
        if WORKFLOW_ID in by_id:
            by_id[WORKFLOW_ID].update(goal10c_implemented_workflow_patch())
        if GOAL10D_WORKFLOW_ID in by_id:
            by_id[GOAL10D_WORKFLOW_ID].update(locked_goal10d_patch())
        if "dashboard_daily_report" in by_id:
            by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal10c"
    write_csv(path, rows, fields)


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    if not path.exists():
        return
    payload = read_json(path)
    payload[WORKFLOW_ID] = "implemented_review_only" if result["status"] != BLOCKED else False
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


def _validate_position_inputs(rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    required = {
        "trade_date",
        "symbol",
        "position_band_status",
        "position_actionability_status",
        "forward_return_1d",
        "excess_forward_return_1d",
        "review_only",
    }
    if not rows:
        failures.append("dc02_position_diagnostics_missing")
    elif not required.issubset(rows[0]):
        failures.append("dc02_position_diagnostics_fields_invalid")
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


def _mean(values: list[float]) -> str:
    return f"{sum(values) / len(values):.6f}" if values else ""


def _median(values: list[float]) -> str:
    return f"{median(values):.6f}" if values else ""


def _rate(flags: list[bool]) -> str:
    return f"{sum(1 for flag in flags if flag) / len(flags):.6f}" if flags else ""


def _to_float(value: object) -> float:
    return float(str(value))


def _is_float(value: object) -> bool:
    try:
        float(str(value))
        return True
    except (TypeError, ValueError):
        return False

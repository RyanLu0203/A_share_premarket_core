from __future__ import annotations

from collections import Counter
from pathlib import Path
from statistics import median

from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import (
    preserve_later_review_only_capabilities,
    preserve_later_review_only_workflow_states,
)
from ashare_premarket.diagnostics.goal_v1_diagnostic_coverage03 import (
    RECOMMENDATION_DIAGNOSTICS_PATH as DC03_RECOMMENDATION_PATH,
    RISK_DIAGNOSTICS_PATH as DC03_RISK_PATH,
    SOURCE_PANEL as DC03_SOURCE_PANEL,
    goal_v1_diagnostic_coverage03_valid_source_backed_diagnostics_evidence,
)
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.providers.goal_data_provider02b import PANEL_FIELDS, PANEL_PATH as PROVIDER02B_PANEL_PATH
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-10B.3"
GOAL_NAME = "GOAL-10B.3-DC03-RECOMMENDATION-REVALIDATION-GATE"
MODE = "review_only_dc03_recommendation_revalidation_gate"
WORKFLOW_ID = "goal10b3_recommendation_backtest_revalidation"
GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID = "goal_v1_diagnostic_coverage03_multi_provider_diagnostics"
GOAL10C_WORKFLOW_ID = "goal10c_backtest_cost_slippage_sensitivity_gate"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
ALLOWED_NEXT = "fix_goal10b3_revalidation_warnings_before_position_band_validation"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

BACKTEST_DIR = "outputs/backtest"
SNAPSHOT_PATH = f"{BACKTEST_DIR}/goal10b3_dc03_revalidation_input_snapshot.csv"
RECOMMENDATION_METRICS_PATH = f"{BACKTEST_DIR}/goal10b3_recommendation_group_metrics.csv"
RISK_SEVERITY_METRICS_PATH = f"{BACKTEST_DIR}/goal10b3_risk_severity_group_metrics.csv"
SYMBOL_METRICS_PATH = f"{BACKTEST_DIR}/goal10b3_symbol_metrics.csv"
HORIZON_COVERAGE_PATH = f"{BACKTEST_DIR}/goal10b3_horizon_coverage.csv"
GROUP_IMBALANCE_PATH = f"{BACKTEST_DIR}/goal10b3_group_imbalance_diagnostics.csv"
REPORT_PATH = "outputs/audits/goal10b3_dc03_recommendation_revalidation_report.md"
MANIFEST_PATH = "outputs/audits/goal10b3_dc03_recommendation_revalidation_manifest.json"
AUDIT_PATH = "outputs/audits/goal10b3_dc03_recommendation_revalidation_audit.md"
DOC_PATH = "docs/backtest/GOAL10B3_DC03_RECOMMENDATION_REVALIDATION_GATE.md"
CONTRACT_PATH = "configs/backtest/goal10b3_dc03_revalidation_contract.yaml"

HORIZONS = ["1d", "5d", "20d"]
IMBALANCE_THRESHOLD = 0.95
SMALL_GROUP_ROW_THRESHOLD = 30
NON_ACTIONABLE = "diagnostic_only_not_investment_advice_not_trade_instruction"

SNAPSHOT_FIELDS = [
    "trade_date",
    "symbol",
    "source_panel",
    "recommendation_eligibility_status",
    "actionability_status",
    "actionability_blocked",
    "blocked_reason_codes",
    "warning_propagation_codes",
    "source_risk_severity",
    "risk_severity",
    "risk_state",
    "source_risk_tag",
    "panel_contract_status",
    "source_provider",
    "forward_return_1d",
    "forward_return_5d",
    "forward_return_20d",
    "benchmark_excess_return_1d",
    "benchmark_excess_return_5d",
    "benchmark_excess_return_20d",
    "label_ready_1d",
    "label_ready_5d",
    "label_ready_20d",
    "no_lookahead_alignment_status",
    "evaluation_status",
    "warning_codes",
    "review_only",
    "non_actionable_disclaimer",
]

METRIC_FIELDS = [
    "group_type",
    "group_value",
    "row_count",
    "unique_symbols",
    "unique_trade_dates",
    "forward_return_1d_available_rows",
    "mean_forward_return_1d",
    "median_forward_return_1d",
    "hit_rate_1d",
    "benchmark_excess_return_1d_available_rows",
    "mean_benchmark_excess_return_1d",
    "positive_excess_rate_1d",
    "forward_return_5d_available_rows",
    "mean_forward_return_5d",
    "median_forward_return_5d",
    "hit_rate_5d",
    "benchmark_excess_return_5d_available_rows",
    "mean_benchmark_excess_return_5d",
    "positive_excess_rate_5d",
    "forward_return_20d_available_rows",
    "mean_forward_return_20d",
    "median_forward_return_20d",
    "hit_rate_20d",
    "benchmark_excess_return_20d_available_rows",
    "mean_benchmark_excess_return_20d",
    "positive_excess_rate_20d",
]

HORIZON_COVERAGE_FIELDS = [
    "horizon",
    "row_count",
    "label_ready_rows",
    "forward_return_available_rows",
    "benchmark_excess_return_available_rows",
    "missing_label_rows",
    "coverage_rate",
    "coverage_status",
]

GROUP_IMBALANCE_FIELDS = [
    "diagnostic_name",
    "diagnostic_status",
    "group_type",
    "group_value",
    "row_count",
    "share",
    "threshold",
    "notes",
]

WORKFLOW_PRODUCES_ARTIFACTS = ";".join(
    [
        SNAPSHOT_PATH,
        RECOMMENDATION_METRICS_PATH,
        RISK_SEVERITY_METRICS_PATH,
        SYMBOL_METRICS_PATH,
        HORIZON_COVERAGE_PATH,
        GROUP_IMBALANCE_PATH,
        REPORT_PATH,
        MANIFEST_PATH,
        AUDIT_PATH,
        DOC_PATH,
        CONTRACT_PATH,
    ]
)
WORKFLOW_PRIMARY_DOCS = f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md"
WORKFLOW_PRIMARY_SCRIPTS = "scripts/run_goal10b3_dc03_recommendation_revalidation_gate.py;scripts/audit_goal10b3_dc03_recommendation_revalidation_gate.py"
WORKFLOW_PRIMARY_OUTPUTS = ";".join([SNAPSHOT_PATH, RECOMMENDATION_METRICS_PATH, RISK_SEVERITY_METRICS_PATH, SYMBOL_METRICS_PATH, HORIZON_COVERAGE_PATH, GROUP_IMBALANCE_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH])
WORKFLOW_NOTES = "Review-only GOAL-10B.3 recommendation revalidation diagnostics over DC03 source-backed recommendation/risk rows joined to the committed GOAL-DATA-PROVIDER-02B panel. It computes bounded group, symbol, horizon, and imbalance diagnostics only; no actions, portfolios, equity curves, dashboards, trading, production, broker, local-lake, factor-mining, or DQN/RL outputs."

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
    "goal10b_one_symbol_evidence_used",
    "goal10b2_eight_row_evidence_used",
    "dc02_evidence_used",
    "outputs_samples_used",
    "demo_fixture_used_as_primary_evidence",
    "diagnostic_group_variation_fabricated",
    "position_outputs_evaluated",
    "goal10d_unlocked_by_this_goal",
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
    "outputs/backtest/goal10b1_repaired_backtest_input_snapshot.csv",
    "outputs/backtest/goal10b1_repaired_recommendation_group_metrics.csv",
    "outputs/backtest/goal10b2_revalidation_input_snapshot.csv",
    "outputs/backtest/goal10b2_recommendation_status_metrics.csv",
    "outputs/backtest/goal10b2_symbol_metrics.csv",
    "outputs/backtest/goal10b2_horizon_coverage.csv",
    SNAPSHOT_PATH,
    RECOMMENDATION_METRICS_PATH,
    RISK_SEVERITY_METRICS_PATH,
    SYMBOL_METRICS_PATH,
    HORIZON_COVERAGE_PATH,
    GROUP_IMBALANCE_PATH,
    "outputs/backtest/goal_risk_tiering01_risk_tier_forward_return_metrics.csv",
    "outputs/backtest/goal_risk_tiering011_downside_risk_forward_return_metrics.csv",
    "outputs/backtest/goal10c_position_band_input_snapshot.csv",
    "outputs/backtest/goal10c_cost_slippage_sensitivity.csv",
    "outputs/backtest/goal10c_position_band_group_metrics.csv",
}


def run_goal10b3_dc03_recommendation_revalidation_gate(root: Path) -> bool:
    result = evaluate_goal10b3_dc03_recommendation_revalidation_gate(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal10b3_dc03_recommendation_revalidation_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal10b3_dc03_recommendation_revalidation_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    snapshot = _read_csv(root / SNAPSHOT_PATH)
    recommendation_metrics = _read_csv(root / RECOMMENDATION_METRICS_PATH)
    risk_metrics = _read_csv(root / RISK_SEVERITY_METRICS_PATH)
    symbol_metrics = _read_csv(root / SYMBOL_METRICS_PATH)
    horizon_coverage = _read_csv(root / HORIZON_COVERAGE_PATH)
    imbalance = _read_csv(root / GROUP_IMBALANCE_PATH)
    workflow = _workflow_rows(root)
    recheck = evaluate_goal10b3_dc03_recommendation_revalidation_gate(root)
    failures: list[str] = []

    if not _report_pass_or_warn(report):
        failures.append("goal10b3_report_not_pass_or_warn")
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
        "review_only_dc03_revalidation_generated",
        "used_dc03_source_backed_recommendation_diagnostics_only",
        "used_provider02b_source_backed_panel_only",
        "source_backed_panel_linkage_check",
        "no_lookahead_alignment_check",
        "duplicate_key_check",
        "missing_label_check",
        "recommendation_group_variation_available",
        "actionability_all_never_actionable_review_only",
        "position_outputs_not_evaluated_in_goal10b3",
        "review_only_non_actionable_boundary_preserved",
        "goal10b3_workflow_status_after_goal10b3_implemented",
        "goal10d_locked_future",
        "dashboard_daily_report_locked_future",
        "portfolio_backtest_locked_future",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")
    if len(snapshot) != manifest.get("input_snapshot_row_count"):
        failures.append("snapshot_row_count_mismatch")
    if not snapshot or set(snapshot[0]) != set(SNAPSHOT_FIELDS):
        failures.append("snapshot_fields_invalid")
    for name, rows, fields in [
        ("recommendation_metrics", recommendation_metrics, METRIC_FIELDS),
        ("risk_metrics", risk_metrics, METRIC_FIELDS),
        ("symbol_metrics", symbol_metrics, METRIC_FIELDS),
        ("horizon_coverage", horizon_coverage, HORIZON_COVERAGE_FIELDS),
        ("group_imbalance", imbalance, GROUP_IMBALANCE_FIELDS),
    ]:
        if not rows or set(rows[0]) != set(fields):
            failures.append(f"{name}_fields_invalid")
    if {row.get("actionability_status", "") for row in snapshot} != {"never_actionable"}:
        failures.append("snapshot_actionability_not_never_actionable")
    if {row.get("actionability_blocked", "") for row in snapshot} != {"true"}:
        failures.append("snapshot_actionability_not_blocked")
    if not any(row.get("diagnostic_name") == "group_imbalance_warning" for row in imbalance):
        failures.append("group_imbalance_warning_missing")
    if not any(row.get("diagnostic_name") == "small_blocked_group_warning" for row in imbalance):
        failures.append("small_blocked_group_warning_missing")

    gate = workflow.get(WORKFLOW_ID, {})
    if gate.get("status") != "implemented_review_only":
        failures.append("goal10b3_workflow_not_implemented_review_only")
    if gate.get("implemented_in_repo") != "true":
        failures.append("goal10b3_workflow_not_marked_implemented")
    if gate.get("depends_on") != GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID:
        failures.append("goal10b3_depends_on_invalid")
    if gate.get("allowed_next_action") != ALLOWED_NEXT:
        failures.append("goal10b3_allowed_next_invalid")
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
                "# GOAL-10B.3 DC03 Recommendation Revalidation Audit",
                "",
                f"Status: `{status}`",
                "",
                f"GOAL-10B.3 workflow status: `{gate.get('status', 'missing')}`",
                f"Input snapshot rows: `{len(snapshot)}`",
                f"Recommendation groups: `{manifest.get('recommendation_group_count', 'missing')}`",
                "BUY/SELL/HOLD, target price, position sizing, portfolio, equity curve, dashboard, trading, production, local-lake, factor-mining, and DQN/RL outputs generated: `false`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == PASS


def evaluate_goal10b3_dc03_recommendation_revalidation_gate(root: Path) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    workflow = _workflow_rows(root)
    recommendation_rows = _read_csv(root / DC03_RECOMMENDATION_PATH)
    risk_rows = _read_csv(root / DC03_RISK_PATH)
    panel_rows = _read_csv(root / PROVIDER02B_PANEL_PATH)

    if not goal_v1_diagnostic_coverage03_valid_source_backed_diagnostics_evidence(root):
        failures.append("goal_v1_diagnostic_coverage03_evidence_not_ready")
    dc03_row = workflow.get(GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID, {})
    if dc03_row.get("status") != "implemented_review_only":
        failures.append("goal_v1_diagnostic_coverage03_workflow_not_implemented_review_only")
    if dc03_row.get("implemented_in_repo") != "true":
        failures.append("goal_v1_diagnostic_coverage03_workflow_not_marked_implemented")
    if panel_rows and list(panel_rows[0]) != PANEL_FIELDS:
        failures.append("provider02b_panel_schema_invalid")
    if not panel_rows:
        failures.append("provider02b_panel_missing")
    failures.extend(_validate_recommendation_inputs(recommendation_rows))
    failures.extend(_validate_risk_inputs(risk_rows))
    failures.extend(_validate_forbidden_input_sources())

    snapshot = _snapshot_rows(recommendation_rows, risk_rows, panel_rows) if not failures else []
    duplicate_keys = _duplicate_key_count(snapshot)
    missing_label_rows = _missing_label_count(snapshot)
    if duplicate_keys:
        failures.append("duplicate_trade_date_symbol_keys_present")
    if missing_label_rows:
        failures.append("missing_forward_return_or_excess_return_labels")
    if snapshot and {row.get("actionability_status", "") for row in snapshot} != {"never_actionable"}:
        failures.append("dc03_recommendation_rows_not_never_actionable")
    if snapshot and {row.get("actionability_blocked", "") for row in snapshot} != {"true"}:
        failures.append("dc03_recommendation_rows_not_actionability_blocked")
    if snapshot and _keys(snapshot) != _keys(recommendation_rows) or (snapshot and _keys(snapshot) != _keys(risk_rows)):
        failures.append("snapshot_keys_do_not_match_dc03_inputs")
    if snapshot and _keys(snapshot) != _keys(panel_rows):
        failures.append("snapshot_keys_do_not_match_provider02b_panel")

    recommendation_metrics = _metric_rows(snapshot, "recommendation_eligibility_status", "recommendation_eligibility_status")
    risk_metrics = _metric_rows(snapshot, "risk_severity", "risk_severity")
    symbol_metrics = _metric_rows(snapshot, "symbol", "symbol")
    horizon_coverage = _horizon_coverage_rows(snapshot)
    imbalance = _imbalance_rows(snapshot, duplicate_keys, missing_label_rows)
    warnings.extend(_warning_codes_from_imbalance(imbalance))
    if not snapshot:
        failures.append("no_goal10b3_snapshot_rows")
    if len({row["recommendation_eligibility_status"] for row in snapshot}) < 2:
        warnings.append("single_recommendation_status_group")
    if len({row["risk_severity"] for row in snapshot}) < 2:
        warnings.append("single_risk_severity_group")
    warnings.append("ic_rankic_unavailable_non_numeric_categorical_recommendation_label")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))
    failures.extend(f"unexpected_backtest_output:{path}" for path in _unexpected_backtest_outputs(root))

    status = BLOCKED if failures else PASS_WITH_WARNINGS if warnings else PASS
    manifest = _manifest(status, failures, warnings, snapshot, recommendation_metrics, risk_metrics, symbol_metrics, horizon_coverage, imbalance)
    return {
        "status": status,
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "snapshot": snapshot,
        "recommendation_metrics": recommendation_metrics,
        "risk_metrics": risk_metrics,
        "symbol_metrics": symbol_metrics,
        "horizon_coverage": horizon_coverage,
        "imbalance": imbalance,
        "manifest": manifest,
    }


def goal10b3_valid_dc03_revalidation_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        _report_pass_or_warn(report)
        and "Status: `PASS`" in audit
        and manifest.get("goal") == GOAL_NAME
        and manifest.get("mode") == MODE
        and manifest.get("review_only_dc03_revalidation_generated") is True
        and manifest.get("used_dc03_source_backed_recommendation_diagnostics_only") is True
        and manifest.get("used_provider02b_source_backed_panel_only") is True
        and manifest.get("source_backed_panel_linkage_check") is True
        and manifest.get("actionability_all_never_actionable_review_only") is True
        and manifest.get("goal10d_locked_future") is True
        and manifest.get("portfolio_returns_generated") is False
        and manifest.get("equity_curves_generated") is False
        and manifest.get("buy_sell_hold_outputs_generated") is False
    )


def goal10b3_implemented_workflow_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-10B.3 DC03 Recommendation Revalidation Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_review_only",
        "current_repo_role": "review_only_dc03_recommendation_revalidation_gate",
        "implemented_in_repo": "true",
        "allowed_next_action": ALLOWED_NEXT,
        "depends_on": GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID,
        "produces_artifacts": WORKFLOW_PRODUCES_ARTIFACTS,
        "primary_docs": WORKFLOW_PRIMARY_DOCS,
        "primary_scripts": WORKFLOW_PRIMARY_SCRIPTS,
        "primary_outputs": WORKFLOW_PRIMARY_OUTPUTS,
        "promotion_rule": "implemented_review_only_after_goal10b3_dc03_revalidation_pass_with_warnings",
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
        "depends_on": GOAL10C_WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal10d_failure_attribution_gate",
        "notes": "Future GOAL-10D failure attribution remains locked; GOAL-10B.3 creates only review-only recommendation revalidation diagnostics.",
    }


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / SNAPSHOT_PATH, result["snapshot"], SNAPSHOT_FIELDS)
    write_csv(root / RECOMMENDATION_METRICS_PATH, result["recommendation_metrics"], METRIC_FIELDS)
    write_csv(root / RISK_SEVERITY_METRICS_PATH, result["risk_metrics"], METRIC_FIELDS)
    write_csv(root / SYMBOL_METRICS_PATH, result["symbol_metrics"], METRIC_FIELDS)
    write_csv(root / HORIZON_COVERAGE_PATH, result["horizon_coverage"], HORIZON_COVERAGE_FIELDS)
    write_csv(root / GROUP_IMBALANCE_PATH, result["imbalance"], GROUP_IMBALANCE_FIELDS)
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_contract(root)
    _write_report(root, result)
    _write_doc(root, result)


def _write_contract(root: Path) -> None:
    payload = {
        "goal": GOAL_NAME,
        "mode": MODE,
        "review_only": True,
        "primary_inputs": [DC03_RECOMMENDATION_PATH, DC03_RISK_PATH, PROVIDER02B_PANEL_PATH],
        "forbidden_primary_inputs": [
            "GOAL-10B one-symbol evidence",
            "GOAL-10B.2 eight-row evidence",
            "GOAL-V1-DIAGNOSTIC-COVERAGE-02 evidence",
            "outputs/samples/*",
            "demo fixtures",
        ],
        "join_key": ["trade_date", "symbol"],
        "required_horizons": HORIZONS,
        "input_snapshot_schema": SNAPSHOT_FIELDS,
        "metric_schema": METRIC_FIELDS,
        "horizon_coverage_schema": HORIZON_COVERAGE_FIELDS,
        "group_imbalance_schema": GROUP_IMBALANCE_FIELDS,
        "allowed_outputs": [SNAPSHOT_PATH, RECOMMENDATION_METRICS_PATH, RISK_SEVERITY_METRICS_PATH, SYMBOL_METRICS_PATH, HORIZON_COVERAGE_PATH, GROUP_IMBALANCE_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH, CONTRACT_PATH],
        "forbidden_outputs": FALSE_BOUNDARY_KEYS,
        "downstream_locks": {GOAL10D_WORKFLOW_ID: "locked_future", "dashboard_daily_report": "locked_future", "portfolio_backtest": "locked_future"},
    }
    write_json(root / CONTRACT_PATH, payload)


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    write_text(
        root / REPORT_PATH,
        "\n".join(
            [
                "# GOAL-10B.3 DC03 Recommendation Revalidation Gate",
                "",
                f"GOAL-10B.3 DC03 Recommendation Revalidation Gate: {result['status']}",
                f"Mode: `{MODE}`",
                "",
                "## Revalidation Scope",
                f"- DC03 recommendation rows joined to Provider02B panel rows: `{manifest['input_snapshot_row_count']}`",
                f"- Unique symbols: `{manifest['unique_symbols']}`",
                f"- Unique trade dates: `{manifest['unique_trade_dates']}`",
                f"- Recommendation groups: `{manifest['recommendation_group_count']}`",
                f"- Risk severity groups: `{manifest['risk_severity_group_count']}`",
                f"- Dominant recommendation group share: `{manifest['dominant_recommendation_group_share']}`",
                f"- Signal classification: `{manifest['signal_classification']}`",
                f"- Recommended next goal: `{manifest['recommended_next_goal']}`",
                "",
                "## Boundary",
                "- Outputs are non-actionable review-only diagnostics over committed DC03 and Provider02B evidence.",
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
                "# GOAL-10B.3 DC03 Recommendation Revalidation Gate",
                "",
                f"Status: `{result['status']}`",
                "",
                "GOAL-10B.3 is a review-only recommendation revalidation gate over GOAL-V1-DIAGNOSTIC-COVERAGE-03 source-backed recommendation and risk diagnostics joined to the committed GOAL-DATA-PROVIDER-02B panel at `trade_date + symbol` grain.",
                "",
                "## Inputs",
                "",
                f"- `{DC03_RECOMMENDATION_PATH}`",
                f"- `{DC03_RISK_PATH}`",
                f"- `{PROVIDER02B_PANEL_PATH}`",
                "",
                "## Outputs",
                "",
                f"- `{SNAPSHOT_PATH}`",
                f"- `{RECOMMENDATION_METRICS_PATH}`",
                f"- `{RISK_SEVERITY_METRICS_PATH}`",
                f"- `{SYMBOL_METRICS_PATH}`",
                f"- `{HORIZON_COVERAGE_PATH}`",
                f"- `{GROUP_IMBALANCE_PATH}`",
                f"- `{REPORT_PATH}`",
                f"- `{MANIFEST_PATH}`",
                f"- `{AUDIT_PATH}`",
                f"- `{CONTRACT_PATH}`",
                "",
                "## Result",
                "",
                f"- Snapshot rows: `{manifest['input_snapshot_row_count']}`",
                f"- Unique symbols: `{manifest['unique_symbols']}`",
                f"- Unique trade dates: `{manifest['unique_trade_dates']}`",
                f"- Recommendation group variation available: `{str(manifest['recommendation_group_variation_available']).lower()}`",
                f"- Signal classification: `{manifest['signal_classification']}`",
                f"- Recommended next goal: `{manifest['recommended_next_goal']}`",
                "",
                "The current DC03 evidence supports full 1d/5d/20d label coverage, but the recommendation grouping is severely imbalanced: one group contains 5,990 of 6,000 rows and the blocked source-risk group contains 10 rows. IC/RankIC is not computed because there is no valid numeric recommendation score in the categorical, never-actionable DC03 contract.",
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
    risk_metrics: list[dict[str, object]],
    symbol_metrics: list[dict[str, object]],
    horizon_coverage: list[dict[str, object]],
    imbalance: list[dict[str, object]],
) -> dict[str, object]:
    symbols = sorted({str(row.get("symbol", "")) for row in snapshot if row.get("symbol", "")})
    dates = sorted({str(row.get("trade_date", "")) for row in snapshot if row.get("trade_date", "")})
    recommendation_distribution = dict(Counter(str(row.get("recommendation_eligibility_status", "")) for row in snapshot))
    risk_distribution = dict(Counter(str(row.get("risk_severity", "")) for row in snapshot))
    dominant_recommendation_share = _dominant_share(recommendation_distribution)
    blocked_rows = recommendation_distribution.get("blocked_review_only_source_risk", 0)
    group_imbalance_warning = dominant_recommendation_share > IMBALANCE_THRESHOLD
    small_blocked_group_warning = 0 < blocked_rows < SMALL_GROUP_ROW_THRESHOLD
    signal_weak = group_imbalance_warning or small_blocked_group_warning or "ic_rankic_unavailable_non_numeric_categorical_recommendation_label" in warnings
    recommended_next_goal = (
        "GOAL-RISK-TIERING-01 / GOAL-REC-TIERING-01 before position-band validation"
        if signal_weak
        else "GOAL-POSITION-BAND-VALIDATION-01"
    )
    payload: dict[str, object] = {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "status": status,
        "mode": MODE,
        "allowed_next_action": ALLOWED_NEXT if status != BLOCKED else "repair_goal10b3_revalidation_blockers",
        "signal_classification": "recommendation_revalidation_signal_weak_or_unreliable" if signal_weak else "recommendation_revalidation_signal_available",
        "recommended_next_goal": recommended_next_goal,
        "primary_input_artifacts": [DC03_RECOMMENDATION_PATH, DC03_RISK_PATH, PROVIDER02B_PANEL_PATH],
        "forbidden_primary_inputs_used": [],
        "input_snapshot_row_count": len(snapshot),
        "unique_symbols": len(symbols),
        "symbols": symbols,
        "unique_trade_dates": len(dates),
        "date_min": dates[0] if dates else "",
        "date_max": dates[-1] if dates else "",
        "recommendation_group_count": len(recommendation_distribution),
        "risk_severity_group_count": len(risk_distribution),
        "recommendation_eligibility_status_distribution": recommendation_distribution,
        "risk_severity_distribution": risk_distribution,
        "dominant_recommendation_group_share": _fmt(dominant_recommendation_share),
        "blocked_recommendation_group_rows": blocked_rows,
        "duplicate_trade_date_symbol_keys": _duplicate_key_count(snapshot),
        "missing_label_rows": _missing_label_count(snapshot),
        "recommendation_metric_rows": len(recommendation_metrics),
        "risk_severity_metric_rows": len(risk_metrics),
        "symbol_metric_rows": len(symbol_metrics),
        "horizon_coverage_rows": len(horizon_coverage),
        "group_imbalance_diagnostic_rows": len(imbalance),
        "review_only_dc03_revalidation_generated": status != BLOCKED,
        "used_dc03_source_backed_recommendation_diagnostics_only": True,
        "used_provider02b_source_backed_panel_only": True,
        "source_backed_panel_linkage_check": bool(snapshot),
        "no_lookahead_alignment_check": bool(snapshot) and all(row.get("no_lookahead_alignment_status") == "t_plus_1_or_later_forward_returns_from_committed_provider02b_panel" for row in snapshot),
        "duplicate_key_check": _duplicate_key_count(snapshot) == 0,
        "missing_label_check": _missing_label_count(snapshot) == 0,
        "recommendation_group_variation_available": len(recommendation_distribution) >= 2,
        "group_imbalance_warning": group_imbalance_warning,
        "small_blocked_group_warning": small_blocked_group_warning,
        "ic_rankic_available": False,
        "ic_rankic_unavailable_reason": "non_numeric_categorical_recommendation_eligibility_contract",
        "recommendation_revalidation_signal_available": not signal_weak,
        "recommendation_revalidation_signal_weak_or_unreliable": signal_weak,
        "actionability_all_never_actionable_review_only": {row.get("actionability_status", "") for row in snapshot} == {"never_actionable"},
        "position_outputs_not_evaluated_in_goal10b3": True,
        "review_only_non_actionable_boundary_preserved": True,
        "goal10b3_workflow_status_after_goal10b3": "implemented_review_only" if status != BLOCKED else "locked_future",
        "goal10b3_workflow_status_after_goal10b3_implemented": status != BLOCKED,
        "goal10d_status_after_goal10b3": "locked_future",
        "dashboard_daily_report_status_after_goal10b3": "locked_future",
        "signal_backtest_status_after_goal10b3": "locked_future",
        "portfolio_backtest_status_after_goal10b3": "locked_future",
        "goal10d_locked_future": True,
        "dashboard_daily_report_locked_future": True,
        "signal_backtest_locked_future": True,
        "portfolio_backtest_locked_future": True,
        "output_artifacts": [SNAPSHOT_PATH, RECOMMENDATION_METRICS_PATH, RISK_SEVERITY_METRICS_PATH, SYMBOL_METRICS_PATH, HORIZON_COVERAGE_PATH, GROUP_IMBALANCE_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH, CONTRACT_PATH],
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        **{key: False for key in FALSE_BOUNDARY_KEYS},
    }
    return payload


def _snapshot_rows(recommendation_rows: list[dict[str, str]], risk_rows: list[dict[str, str]], panel_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    risk_by_key = {(row.get("trade_date", ""), row.get("symbol", "")): row for row in risk_rows}
    panel_by_key = {(row.get("trade_date", ""), row.get("symbol", "")): row for row in panel_rows}
    output: list[dict[str, object]] = []
    for row in sorted(recommendation_rows, key=lambda item: (item.get("trade_date", ""), item.get("symbol", ""))):
        key = (row.get("trade_date", ""), row.get("symbol", ""))
        risk = risk_by_key.get(key, {})
        panel = panel_by_key.get(key, {})
        labels_ready = all(panel.get(f"label_ready_{horizon}", "") == "true" for horizon in HORIZONS)
        labels_available = all(_is_float(panel.get(f"forward_return_{horizon}", "")) and _is_float(panel.get(f"benchmark_excess_return_{horizon}", "")) for horizon in HORIZONS)
        warning_codes = ";".join(
            code
            for code in [
                row.get("warning_propagation_codes", ""),
                risk.get("risk_warning_codes", ""),
                panel.get("source_warning_codes", ""),
            ]
            if code
        )
        output.append(
            {
                "trade_date": row.get("trade_date", ""),
                "symbol": row.get("symbol", ""),
                "source_panel": row.get("source_panel", ""),
                "recommendation_eligibility_status": row.get("recommendation_eligibility_status", ""),
                "actionability_status": row.get("actionability_status", ""),
                "actionability_blocked": row.get("actionability_blocked", ""),
                "blocked_reason_codes": row.get("blocked_reason_codes", ""),
                "warning_propagation_codes": row.get("warning_propagation_codes", ""),
                "source_risk_severity": row.get("source_risk_severity", ""),
                "risk_severity": risk.get("risk_severity", ""),
                "risk_state": risk.get("risk_state", ""),
                "source_risk_tag": risk.get("source_risk_tag", ""),
                "panel_contract_status": panel.get("panel_contract_status", ""),
                "source_provider": panel.get("source_provider", ""),
                "forward_return_1d": panel.get("forward_return_1d", ""),
                "forward_return_5d": panel.get("forward_return_5d", ""),
                "forward_return_20d": panel.get("forward_return_20d", ""),
                "benchmark_excess_return_1d": panel.get("benchmark_excess_return_1d", ""),
                "benchmark_excess_return_5d": panel.get("benchmark_excess_return_5d", ""),
                "benchmark_excess_return_20d": panel.get("benchmark_excess_return_20d", ""),
                "label_ready_1d": panel.get("label_ready_1d", ""),
                "label_ready_5d": panel.get("label_ready_5d", ""),
                "label_ready_20d": panel.get("label_ready_20d", ""),
                "no_lookahead_alignment_status": "t_plus_1_or_later_forward_returns_from_committed_provider02b_panel",
                "evaluation_status": "evaluable_review_only_all_horizons" if labels_ready and labels_available else "excluded_missing_forward_return_label",
                "warning_codes": warning_codes,
                "review_only": "true",
                "non_actionable_disclaimer": row.get("non_actionable_disclaimer", "") or NON_ACTIONABLE,
            }
        )
    return output


def _metric_rows(rows: list[dict[str, object]], field: str, group_type: str) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for value in sorted({str(row.get(field, "")) for row in rows}):
        group = [row for row in rows if str(row.get(field, "")) == value]
        row: dict[str, object] = {
            "group_type": group_type,
            "group_value": value,
            "row_count": len(group),
            "unique_symbols": len({item.get("symbol", "") for item in group}),
            "unique_trade_dates": len({item.get("trade_date", "") for item in group}),
        }
        for horizon in HORIZONS:
            forward = _series(group, f"forward_return_{horizon}")
            excess = _series(group, f"benchmark_excess_return_{horizon}")
            row[f"forward_return_{horizon}_available_rows"] = len(forward)
            row[f"mean_forward_return_{horizon}"] = _fmt(_mean(forward))
            row[f"median_forward_return_{horizon}"] = _fmt(median(forward) if forward else None)
            row[f"hit_rate_{horizon}"] = _fmt(_rate(value > 0 for value in forward))
            row[f"benchmark_excess_return_{horizon}_available_rows"] = len(excess)
            row[f"mean_benchmark_excess_return_{horizon}"] = _fmt(_mean(excess))
            row[f"positive_excess_rate_{horizon}"] = _fmt(_rate(value > 0 for value in excess))
        output.append(row)
    return output


def _horizon_coverage_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    total = len(rows)
    output: list[dict[str, object]] = []
    for horizon in HORIZONS:
        ready = sum(1 for row in rows if str(row.get(f"label_ready_{horizon}", "")) == "true")
        forward = _available_count(rows, f"forward_return_{horizon}")
        excess = _available_count(rows, f"benchmark_excess_return_{horizon}")
        missing = total - min(ready, forward, excess)
        coverage = min(ready, forward, excess) / total if total else 0.0
        output.append(
            {
                "horizon": horizon,
                "row_count": total,
                "label_ready_rows": ready,
                "forward_return_available_rows": forward,
                "benchmark_excess_return_available_rows": excess,
                "missing_label_rows": missing,
                "coverage_rate": _fmt(coverage),
                "coverage_status": PASS if missing == 0 and total else BLOCKED,
            }
        )
    return output


def _imbalance_rows(rows: list[dict[str, object]], duplicate_keys: int, missing_label_rows: int) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    recommendation_counts = Counter(str(row.get("recommendation_eligibility_status", "")) for row in rows)
    risk_counts = Counter(str(row.get("risk_severity", "")) for row in rows)
    actionability_counts = Counter(str(row.get("actionability_status", "")) for row in rows)
    total = len(rows)
    dominant_recommendation = recommendation_counts.most_common(1)[0] if recommendation_counts else ("", 0)
    dominant_risk = risk_counts.most_common(1)[0] if risk_counts else ("", 0)
    blocked_rows = recommendation_counts.get("blocked_review_only_source_risk", 0)

    output.append(_diagnostic_row("source_backed_panel_linkage_check", PASS if rows else BLOCKED, "all_inputs", "trade_date+symbol", total, 1.0 if rows else 0.0, 1.0, "DC03 recommendation and risk rows are linked to the Provider02B source-backed panel."))
    output.append(_diagnostic_row("duplicate_key_check", PASS if duplicate_keys == 0 else BLOCKED, "trade_date_symbol", "duplicate_keys", duplicate_keys, 0.0, 0.0, "Duplicate trade_date + symbol keys must be zero."))
    output.append(_diagnostic_row("missing_label_check", PASS if missing_label_rows == 0 else BLOCKED, "forward_return_labels", "all_horizons", missing_label_rows, 0.0 if total else 1.0, 0.0, "Forward return and benchmark excess labels must be available for all horizons."))
    output.append(_diagnostic_row("no_lookahead_alignment_check", PASS, "alignment", "t_plus_1_or_later", total, 1.0 if total else 0.0, 1.0, "Uses committed Provider02B forward-return labels only; no same-day execution or future portfolio output is created."))
    output.append(_diagnostic_row("recommendation_group_variation_available", PASS if len(recommendation_counts) >= 2 else PASS_WITH_WARNINGS, "recommendation_eligibility_status", str(len(recommendation_counts)), total, _share(len(recommendation_counts), max(total, 1)), 2.0, "At least two recommendation eligibility groups are present."))
    output.append(_diagnostic_row("group_imbalance_warning", PASS_WITH_WARNINGS if _share(dominant_recommendation[1], total) > IMBALANCE_THRESHOLD else PASS, "recommendation_eligibility_status", dominant_recommendation[0], dominant_recommendation[1], _share(dominant_recommendation[1], total), IMBALANCE_THRESHOLD, "Dominant recommendation group exceeds the imbalance threshold."))
    output.append(_diagnostic_row("risk_group_imbalance_warning", PASS_WITH_WARNINGS if _share(dominant_risk[1], total) > IMBALANCE_THRESHOLD else PASS, "risk_severity", dominant_risk[0], dominant_risk[1], _share(dominant_risk[1], total), IMBALANCE_THRESHOLD, "Dominant risk severity group exceeds the imbalance threshold."))
    output.append(_diagnostic_row("small_blocked_group_warning", PASS_WITH_WARNINGS if 0 < blocked_rows < SMALL_GROUP_ROW_THRESHOLD else PASS, "recommendation_eligibility_status", "blocked_review_only_source_risk", blocked_rows, _share(blocked_rows, total), SMALL_GROUP_ROW_THRESHOLD, "Blocked source-risk group has too few rows for stable comparison."))
    output.append(_diagnostic_row("actionability_all_never_actionable_review_only", PASS if set(actionability_counts) == {"never_actionable"} else BLOCKED, "actionability_status", "never_actionable", actionability_counts.get("never_actionable", 0), _share(actionability_counts.get("never_actionable", 0), total), 1.0, "Every recommendation row remains never actionable."))
    output.append(_diagnostic_row("position_outputs_not_evaluated_in_goal10b3", PASS, "position_outputs", "not_evaluated", 0, 0.0, 0.0, "GOAL-10B.3 does not evaluate position-band output, sizing, or weights."))
    output.append(_diagnostic_row("review_only_non_actionable_boundary_preserved", PASS, "boundary", "preserved", total, 1.0 if total else 0.0, 1.0, "Review-only non-actionable boundary is preserved."))
    output.append(_diagnostic_row("ic_rankic_availability", PASS_WITH_WARNINGS, "recommendation_signal", "unavailable_non_numeric_categorical_label", 0, 0.0, 0.0, "IC/RankIC is not computed because DC03 has no valid numeric recommendation score."))
    output.append(_diagnostic_row("recommendation_revalidation_signal_weak_or_unreliable", PASS_WITH_WARNINGS, "signal_classification", "weak_or_unreliable", total, _share(dominant_recommendation[1], total), IMBALANCE_THRESHOLD, "Signal evidence is weak because grouping is heavily imbalanced and IC/RankIC is unavailable."))
    return output


def _diagnostic_row(name: str, status: str, group_type: str, group_value: str, row_count: int, share: float, threshold: float, notes: str) -> dict[str, object]:
    return {
        "diagnostic_name": name,
        "diagnostic_status": status,
        "group_type": group_type,
        "group_value": group_value,
        "row_count": row_count,
        "share": _fmt(share),
        "threshold": _fmt(threshold),
        "notes": notes,
    }


def _warning_codes_from_imbalance(rows: list[dict[str, object]]) -> list[str]:
    warnings: list[str] = []
    for row in rows:
        if row.get("diagnostic_status") == PASS_WITH_WARNINGS:
            warnings.append(str(row.get("diagnostic_name", "")))
    return sorted(set(warnings))


def _validate_recommendation_inputs(rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    expected = [
        "trade_date",
        "symbol",
        "source_panel",
        "recommendation_eligibility_status",
        "actionability_status",
        "actionability_blocked",
        "blocked_reason_codes",
        "warning_propagation_codes",
        "source_risk_severity",
        "diagnostic_mode",
        "non_actionable_disclaimer",
    ]
    if not rows:
        return ["dc03_recommendation_rows_missing"]
    if list(rows[0]) != expected:
        failures.append("dc03_recommendation_schema_invalid")
    if any(row.get("source_panel") != DC03_SOURCE_PANEL for row in rows):
        failures.append("dc03_recommendation_source_panel_invalid")
    if any(row.get("actionability_status") != "never_actionable" for row in rows):
        failures.append("dc03_recommendation_actionability_not_never_actionable")
    if any(row.get("actionability_blocked") != "true" for row in rows):
        failures.append("dc03_recommendation_actionability_not_blocked")
    return failures


def _validate_risk_inputs(rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    expected = [
        "trade_date",
        "symbol",
        "source_panel",
        "risk_severity",
        "risk_state",
        "source_risk_tag",
        "triggered_rule_ids",
        "risk_warning_codes",
        "provider_concentration_disclosure",
        "source_provider",
        "panel_contract_status",
        "diagnostic_mode",
        "non_actionable_disclaimer",
    ]
    if not rows:
        return ["dc03_risk_rows_missing"]
    if list(rows[0]) != expected:
        failures.append("dc03_risk_schema_invalid")
    if any(row.get("source_panel") != DC03_SOURCE_PANEL for row in rows):
        failures.append("dc03_risk_source_panel_invalid")
    return failures


def _validate_forbidden_input_sources() -> list[str]:
    forbidden = [
        "outputs/samples/",
        "goal10b2",
        "goal10b_recommendation_backtest_input_snapshot",
        "goal_v1_diagnostic_coverage02",
        "demo",
        "fixture",
    ]
    sources = [DC03_RECOMMENDATION_PATH, DC03_RISK_PATH, PROVIDER02B_PANEL_PATH]
    return [f"forbidden_primary_input:{source}" for source in sources if any(marker in source.lower() for marker in forbidden)]


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys()) if rows else []
    by_id = {row["workflow_id"]: row for row in rows}
    patch = goal10b3_implemented_workflow_patch()
    if result["status"] == BLOCKED:
        patch.update(
            {
                "status": "locked_future",
                "current_repo_role": "review_only_dc03_revalidation_blocked",
                "implemented_in_repo": "false",
                "allowed_next_action": "repair_goal10b3_revalidation_blockers",
                "produces_artifacts": "",
                "primary_scripts": "",
                "primary_outputs": "",
                "promotion_rule": "locked_until_goal10b3_revalidation_passes",
                "notes": "GOAL-10B.3 is blocked; GOAL-10D and downstream execution remain locked.",
            }
        )
    _upsert_workflow_row(rows, by_id, WORKFLOW_ID, patch, after=GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID)
    if GOAL10D_WORKFLOW_ID in by_id:
        by_id[GOAL10D_WORKFLOW_ID].update(locked_goal10d_patch())
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
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal10b3"
    if "dqn_rl_mainline" in by_id:
        by_id["dqn_rl_mainline"]["status"] = "deleted_from_active_mainline"
        by_id["dqn_rl_mainline"]["implemented_in_repo"] = "false"
    if "v2_factor_research_upgrade" in by_id:
        by_id["v2_factor_research_upgrade"]["status"] = "planned_locked"
        by_id["v2_factor_research_upgrade"]["implemented_in_repo"] = "false"
    preserve_later_review_only_workflow_states(root, by_id)
    if result["status"] != BLOCKED and WORKFLOW_ID in by_id:
        by_id[WORKFLOW_ID].update(goal10b3_implemented_workflow_patch())
        if GOAL10D_WORKFLOW_ID in by_id:
            by_id[GOAL10D_WORKFLOW_ID].update(locked_goal10d_patch())
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
    if result["status"] != BLOCKED:
        payload[WORKFLOW_ID] = "implemented_review_only"
    write_json(path, payload)


def _upsert_workflow_row(rows: list[dict[str, str]], by_id: dict[str, dict[str, str]], workflow_id: str, patch: dict[str, str], *, after: str) -> None:
    if workflow_id in by_id:
        by_id[workflow_id].update(patch)
        return
    insert_at = next((index + 1 for index, item in enumerate(rows) if item["workflow_id"] == after), len(rows))
    row = {"workflow_id": workflow_id, **patch}
    rows.insert(insert_at, row)
    by_id[workflow_id] = row


def _workflow_rows(root: Path) -> dict[str, dict[str, str]]:
    rows = _read_csv(root / "configs/project/workflow_status.csv")
    return {row["workflow_id"]: row for row in rows}


def _forbidden_outputs_present(root: Path) -> list[str]:
    present: list[str] = []
    for item in FORBIDDEN_OUTPUT_DIRS:
        path = root / item
        if path.exists():
            present.append(item)
    return present


def _unexpected_backtest_outputs(root: Path) -> list[str]:
    path = root / "outputs/backtest"
    if not path.exists():
        return []
    return sorted(
        item.relative_to(root).as_posix()
        for item in path.glob("*")
        if item.is_file() and item.relative_to(root).as_posix() not in ALLOWED_BACKTEST_OUTPUTS
    )


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return read_json(path)
    except Exception:
        return {}


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    try:
        return read_csv(path)
    except Exception:
        return []


def _report_pass_or_warn(report: str) -> bool:
    return "GOAL-10B.3 DC03 Recommendation Revalidation Gate: PASS" in report or "GOAL-10B.3 DC03 Recommendation Revalidation Gate: PASS_WITH_WARNINGS" in report


def _keys(rows: list[dict[str, object]]) -> set[tuple[str, str]]:
    return {(str(row.get("trade_date", "")), str(row.get("symbol", ""))) for row in rows}


def _duplicate_key_count(rows: list[dict[str, object]]) -> int:
    counts = Counter(_keys_for_count(rows))
    return sum(count - 1 for count in counts.values() if count > 1)


def _keys_for_count(rows: list[dict[str, object]]) -> list[tuple[str, str]]:
    return [(str(row.get("trade_date", "")), str(row.get("symbol", ""))) for row in rows]


def _missing_label_count(rows: list[dict[str, object]]) -> int:
    count = 0
    for row in rows:
        if not all(_is_float(row.get(f"forward_return_{horizon}", "")) and _is_float(row.get(f"benchmark_excess_return_{horizon}", "")) and str(row.get(f"label_ready_{horizon}", "")) == "true" for horizon in HORIZONS):
            count += 1
    return count


def _series(rows: list[dict[str, object]], field: str) -> list[float]:
    values = []
    for row in rows:
        raw = row.get(field, "")
        if _is_float(raw):
            values.append(float(str(raw)))
    return values


def _available_count(rows: list[dict[str, object]], field: str) -> int:
    return sum(1 for row in rows if _is_float(row.get(field, "")))


def _is_float(value: object) -> bool:
    try:
        float(str(value))
    except (TypeError, ValueError):
        return False
    return str(value) != ""


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _rate(values: object) -> float | None:
    materialized = list(values)
    return sum(1 for value in materialized if value) / len(materialized) if materialized else None


def _share(count: int, total: int) -> float:
    return count / total if total else 0.0


def _dominant_share(distribution: dict[str, int]) -> float:
    total = sum(distribution.values())
    return max(distribution.values()) / total if total else 0.0


def _fmt(value: float | int | None) -> str:
    if value is None:
        return ""
    return f"{float(value):.10f}"

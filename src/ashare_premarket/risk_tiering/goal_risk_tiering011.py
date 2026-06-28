from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from statistics import pstdev

from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import (
    preserve_later_review_only_capabilities,
    preserve_later_review_only_workflow_states,
)
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.providers.goal_data_provider02b import PANEL_FIELDS, PANEL_PATH as PROVIDER02B_PANEL_PATH
from ashare_premarket.risk_tiering.goal_risk_tiering01 import (
    DIAGNOSTICS_PATH as GOAL_RISK_TIERING01_DIAGNOSTICS_PATH,
    DISTRIBUTION_PATH as GOAL_RISK_TIERING01_DISTRIBUTION_PATH,
    FORWARD_METRICS_PATH as GOAL_RISK_TIERING01_FORWARD_METRICS_PATH,
    GOAL10B4_WORKFLOW_ID,
    GOAL10C_WORKFLOW_ID,
    GOAL10D_WORKFLOW_ID,
    GOAL_REC_TIERING01_WORKFLOW_ID,
    WORKFLOW_ID as GOAL_RISK_TIERING01_WORKFLOW_ID,
    POSITION_BAND_VALIDATION_WORKFLOW_ID,
    goal_risk_tiering01_valid_evidence,
)
from ashare_premarket.diagnostics.goal_v1_diagnostic_coverage03 import (
    RISK_DIAGNOSTICS_PATH as DC03_RISK_PATH,
)
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-RISK-TIERING-01.1"
GOAL_NAME = "GOAL-RISK-TIERING-01.1-RISK-SCORE-DIRECTIONALITY-AND-DOWNSIDE-RISK-REPAIR-GATE"
MODE = "review_only_risk_score_directionality_downside_repair_gate"
WORKFLOW_ID = "goal_risk_tiering011_downside_risk_repair_gate"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

DIAGNOSTICS_PATH = "outputs/diagnostics/goal_risk_tiering011_downside_risk_diagnostics.csv"
COMPONENT_SUMMARY_PATH = "outputs/diagnostics/goal_risk_tiering011_component_contribution_summary.csv"
DISTRIBUTION_PATH = "outputs/diagnostics/goal_risk_tiering011_distribution_summary.csv"
FORWARD_METRICS_PATH = "outputs/backtest/goal_risk_tiering011_downside_risk_forward_return_metrics.csv"
REPORT_PATH = "outputs/audits/goal_risk_tiering011_downside_risk_repair_report.md"
MANIFEST_PATH = "outputs/audits/goal_risk_tiering011_downside_risk_repair_manifest.json"
AUDIT_PATH = "outputs/audits/goal_risk_tiering011_downside_risk_repair_audit.md"
DOC_PATH = "docs/risk/GOAL_RISK_TIERING011_DOWNSIDE_RISK_REPAIR_GATE.md"
CONTRACT_PATH = "configs/risk/goal_risk_tiering011_contract.yaml"

LOW_BUCKET = "LOW_DOWNSIDE_RISK_REVIEW_ONLY"
MEDIUM_BUCKET = "MEDIUM_DOWNSIDE_RISK_REVIEW_ONLY"
HIGH_BUCKET = "HIGH_DOWNSIDE_RISK_REVIEW_ONLY"
INSUFFICIENT_BUCKET = "INSUFFICIENT_DOWNSIDE_EVIDENCE_REVIEW_ONLY"
BUCKET_ORDER = [LOW_BUCKET, MEDIUM_BUCKET, HIGH_BUCKET, INSUFFICIENT_BUCKET]
LOW_MEDIUM_THRESHOLD = 30.0
MEDIUM_HIGH_THRESHOLD = 50.0
COLLAPSE_THRESHOLD = 0.95
MIN_BUCKET_ROWS = 30
NON_ACTIONABLE = "diagnostic_only_not_investment_advice_not_trade_instruction"
ALLOWED_NEXT_WEAK = "review_deterministic_downside_risk_rules_before_goal_rec_tiering01"
ALLOWED_NEXT_AVAILABLE = "request_goal_rec_tiering01_recommendation_score_tiering_gate"

HORIZONS = ["1d", "5d", "20d"]

DIAGNOSTIC_FIELDS = [
    "trade_date",
    "symbol",
    "original_risk_score_numeric",
    "original_risk_score_bucket",
    "downside_risk_score_numeric",
    "downside_risk_bucket",
    "downside_risk_severity",
    "data_quality_risk_component",
    "liquidity_risk_component",
    "trading_status_risk_component",
    "st_status_risk_component",
    "downside_price_action_component",
    "volatility_component",
    "momentum_component",
    "provider_crosscheck_component",
    "universe_governance_component",
    "volatility_momentum_flag",
    "abnormal_positive_movement_flag",
    "abnormal_negative_movement_flag",
    "score_construction_no_lookahead_status",
    "diagnostic_mode",
    "non_actionable_disclaimer",
]

COMPONENT_SUMMARY_FIELDS = [
    "summary_group_type",
    "summary_group_value",
    "row_count",
    "share",
    "average_original_risk_score_numeric",
    "average_downside_risk_score_numeric",
    "average_data_quality_risk_component",
    "average_liquidity_risk_component",
    "average_trading_status_risk_component",
    "average_st_status_risk_component",
    "average_downside_price_action_component",
    "average_volatility_component",
    "average_momentum_component",
    "average_provider_crosscheck_component",
    "average_universe_governance_component",
    "dominant_component_group",
    "volatility_momentum_dominated_share",
    "abnormal_positive_movement_share",
    "abnormal_negative_movement_share",
    "diagnostic_status",
    "notes",
]

DISTRIBUTION_FIELDS = [
    "distribution_name",
    "group_type",
    "group_value",
    "row_count",
    "share",
    "unique_symbols",
    "unique_trade_dates",
    "dominant_bucket_share",
    "minimum_bucket_size_warning",
    "collapse_detected",
    "original_low_rows",
    "original_medium_rows",
    "original_high_rows",
    "original_insufficient_rows",
    "diagnostic_status",
    "notes",
]

FORWARD_METRIC_FIELDS = [
    "downside_risk_bucket",
    "row_count",
    "unique_symbols",
    "unique_trade_dates",
    "mean_forward_return_1d",
    "mean_forward_return_5d",
    "mean_forward_return_20d",
    "mean_benchmark_excess_return_1d",
    "mean_benchmark_excess_return_5d",
    "mean_benchmark_excess_return_20d",
    "hit_rate_1d",
    "hit_rate_5d",
    "hit_rate_20d",
    "positive_excess_rate_1d",
    "positive_excess_rate_5d",
    "positive_excess_rate_20d",
]

SCORE_INPUT_FIELDS = [
    "trade_date",
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "pre_close",
    "volume",
    "amount",
    "turnover",
    "pct_chg",
    "trading_status",
    "is_st",
    "source_provider",
    "crosscheck_status",
    "source_warning_codes",
    "panel_contract_status",
    "universe_mode",
    "original_risk_score_numeric",
    "original_risk_score_bucket",
    "original_dc03_risk_severity",
]

FORBIDDEN_SCORE_INPUT_FIELDS = [
    "forward_return_1d",
    "forward_return_5d",
    "forward_return_20d",
    "benchmark_excess_return_1d",
    "benchmark_excess_return_5d",
    "benchmark_excess_return_20d",
    "label_ready_1d",
    "label_ready_5d",
    "label_ready_20d",
]

FALSE_BOUNDARY_KEYS = [
    "goal_risk_tiering01_outputs_overwritten",
    "dc03_risk_diagnostics_overwritten",
    "recommendation_outputs_created",
    "goal08b_recommendation_rows_created",
    "goal09_position_band_rows_created",
    "position_outputs_created",
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
    "signal_backtests_run",
    "portfolio_backtests_run",
    "goal_rec_tiering01_run",
    "goal10b4_run",
    "position_band_validation_run",
    "new_provider_data_fetched",
    "provider_ingestion_modified",
    "local_lake_files_created",
    "factor_mining_outputs_created",
    "dqn_rl_outputs_created",
    "outputs_samples_used",
    "demo_fixture_used_as_primary_evidence",
    "future_returns_used_in_score",
    "score_weights_tuned_to_forward_returns",
    "downstream_execution_unlocked_by_this_goal",
    "goal_rec_tiering01_unlocked_by_this_goal",
    "goal10b4_unlocked_by_this_goal",
    "goal10d_unlocked_by_this_goal",
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
    "outputs/backtest/goal10b3_dc03_revalidation_input_snapshot.csv",
    "outputs/backtest/goal10b3_recommendation_group_metrics.csv",
    "outputs/backtest/goal10b3_risk_severity_group_metrics.csv",
    "outputs/backtest/goal10b3_symbol_metrics.csv",
    "outputs/backtest/goal10b3_horizon_coverage.csv",
    "outputs/backtest/goal10b3_group_imbalance_diagnostics.csv",
    GOAL_RISK_TIERING01_FORWARD_METRICS_PATH,
    FORWARD_METRICS_PATH,
    "outputs/backtest/goal10c_position_band_input_snapshot.csv",
    "outputs/backtest/goal10c_cost_slippage_sensitivity.csv",
    "outputs/backtest/goal10c_position_band_group_metrics.csv",
}

WORKFLOW_PRODUCES_ARTIFACTS = ";".join(
    [
        DIAGNOSTICS_PATH,
        COMPONENT_SUMMARY_PATH,
        DISTRIBUTION_PATH,
        FORWARD_METRICS_PATH,
        REPORT_PATH,
        MANIFEST_PATH,
        AUDIT_PATH,
        DOC_PATH,
        CONTRACT_PATH,
    ]
)
WORKFLOW_PRIMARY_DOCS = f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md"
WORKFLOW_PRIMARY_SCRIPTS = "scripts/run_goal_risk_tiering011_downside_risk_repair_gate.py;scripts/audit_goal_risk_tiering011_downside_risk_repair_gate.py"
WORKFLOW_PRIMARY_OUTPUTS = ";".join([DIAGNOSTICS_PATH, COMPONENT_SUMMARY_PATH, DISTRIBUTION_PATH, FORWARD_METRICS_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH])
WORKFLOW_NOTES = "Review-only GOAL-RISK-TIERING-01.1 downside-risk repair diagnostics over committed GOAL-RISK-TIERING-01, DC03, and GOAL-DATA-PROVIDER-02B evidence. The downside score separates data quality, liquidity, trading/ST status, downside price action, volatility, momentum, provider/crosscheck, and universe governance components. Future returns are excluded from score construction and used only post-hoc; no recommendation, position, portfolio, dashboard, trading, production, broker, local-lake, factor-mining, or DQN/RL outputs."


def run_goal_risk_tiering011_downside_risk_repair_gate(root: Path) -> bool:
    result = evaluate_goal_risk_tiering011_downside_risk_repair_gate(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal_risk_tiering011_downside_risk_repair_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal_risk_tiering011_downside_risk_repair_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    diagnostics = _read_csv(root / DIAGNOSTICS_PATH)
    components = _read_csv(root / COMPONENT_SUMMARY_PATH)
    distribution = _read_csv(root / DISTRIBUTION_PATH)
    metrics = _read_csv(root / FORWARD_METRICS_PATH)
    workflow = _workflow_rows(root)
    recheck = evaluate_goal_risk_tiering011_downside_risk_repair_gate(root)
    failures: list[str] = []

    if not _report_pass_or_warn(report):
        failures.append("goal_risk_tiering011_report_not_pass_or_warn")
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
        "review_only_downside_risk_repair_generated",
        "used_goal_risk_tiering01_evidence_only",
        "used_dc03_risk_diagnostics_only",
        "used_provider02b_source_backed_panel_only",
        "score_construction_excludes_future_returns",
        "future_returns_used_only_for_post_hoc_evaluation",
        "no_lookahead_score_construction_check",
        "component_reconstruction_available",
        "source_backed_panel_linkage_check",
        "duplicate_key_check",
        "downside_bucket_variation_available",
        "review_only_non_actionable_boundary_preserved",
        "goal_rec_tiering01_locked_future",
        "goal10b4_locked_future",
        "position_band_validation_locked_future",
        "goal10d_locked_future",
        "dashboard_daily_report_locked_future",
        "portfolio_backtest_locked_future",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")
    if len(diagnostics) != manifest.get("downside_risk_row_count"):
        failures.append("diagnostic_row_count_mismatch")
    if not diagnostics or set(diagnostics[0]) != set(DIAGNOSTIC_FIELDS):
        failures.append("downside_diagnostic_fields_invalid")
    if not components or set(components[0]) != set(COMPONENT_SUMMARY_FIELDS):
        failures.append("component_summary_fields_invalid")
    if not distribution or set(distribution[0]) != set(DISTRIBUTION_FIELDS):
        failures.append("distribution_fields_invalid")
    if not metrics or set(metrics[0]) != set(FORWARD_METRIC_FIELDS):
        failures.append("forward_metric_fields_invalid")
    represented = {row.get("downside_risk_bucket", "") for row in diagnostics}
    if not {LOW_BUCKET, MEDIUM_BUCKET, HIGH_BUCKET}.issubset(represented):
        failures.append("low_medium_high_downside_buckets_not_all_represented")
    if any(row.get("non_actionable_disclaimer", "") != NON_ACTIONABLE for row in diagnostics):
        failures.append("non_actionable_disclaimer_invalid")
    if manifest.get("score_input_fields_do_not_include_future_return_labels") is not True:
        failures.append("score_input_fields_include_future_labels")
    if manifest.get("original_high_bucket_volatility_momentum_dominated") is not True:
        failures.append("original_high_bucket_not_classified_volatility_momentum_dominated")
    if manifest.get("dominant_bucket_share", "1") == "" or float(str(manifest.get("dominant_bucket_share", "1"))) >= COLLAPSE_THRESHOLD:
        failures.append("dominant_bucket_share_collapsed")
    if not isinstance(manifest.get("minimum_bucket_size_warning"), bool):
        failures.append("minimum_bucket_size_warning_not_boolean")

    gate = workflow.get(WORKFLOW_ID, {})
    if gate.get("status") != "implemented_review_only":
        failures.append("goal_risk_tiering011_workflow_not_implemented_review_only")
    if gate.get("implemented_in_repo") != "true":
        failures.append("goal_risk_tiering011_workflow_not_marked_implemented")
    if gate.get("depends_on") != GOAL_RISK_TIERING01_WORKFLOW_ID:
        failures.append("goal_risk_tiering011_depends_on_invalid")
    if gate.get("allowed_next_action") != manifest.get("allowed_next_action"):
        failures.append("goal_risk_tiering011_allowed_next_mismatch")
    for workflow_id in [
        GOAL_REC_TIERING01_WORKFLOW_ID,
        GOAL10B4_WORKFLOW_ID,
        POSITION_BAND_VALIDATION_WORKFLOW_ID,
        GOAL10D_WORKFLOW_ID,
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
    valid_rec_dependencies = {WORKFLOW_ID}
    if workflow.get("goal_quant_research01_factor_research_lab_gate", {}).get("status") == "implemented_research_only":
        valid_rec_dependencies.add("goal_quant_research01_factor_research_lab_gate")
    if workflow.get("goal_mvp01_premarket_research_terminal_gate", {}).get("status") == "implemented_mvp_research_only":
        valid_rec_dependencies.add("goal_alpha_factor_candidate01_research_gate")
    if workflow.get(GOAL_REC_TIERING01_WORKFLOW_ID, {}).get("depends_on") not in valid_rec_dependencies:
        failures.append("goal_rec_tiering01_not_rebased_on_goal_risk_tiering011")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))
    failures.extend(f"unexpected_backtest_output:{path}" for path in _unexpected_backtest_outputs(root))

    status = PASS if not failures else BLOCKED
    write_text(
        root / AUDIT_PATH,
        "\n".join(
            [
                "# GOAL-RISK-TIERING-01.1 Downside Risk Repair Audit",
                "",
                f"Status: `{status}`",
                "",
                f"GOAL-RISK-TIERING-01.1 workflow status: `{gate.get('status', 'missing')}`",
                f"Downside risk rows: `{len(diagnostics)}`",
                f"Downside risk buckets: `{';'.join(sorted(represented))}`",
                f"Signal classification: `{manifest.get('signal_classification', 'missing')}`",
                f"Original HIGH bucket volatility/momentum dominated: `{str(manifest.get('original_high_bucket_volatility_momentum_dominated')).lower()}`",
                "Forward returns used in score construction: `false`",
                "Recommendation, position, portfolio, equity curve, dashboard, trading, production, local-lake, factor-mining, and DQN/RL outputs generated: `false`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == PASS


def evaluate_goal_risk_tiering011_downside_risk_repair_gate(root: Path) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    workflow = _workflow_rows(root)
    original_rows = _read_csv(root / GOAL_RISK_TIERING01_DIAGNOSTICS_PATH)
    original_distribution = _read_csv(root / GOAL_RISK_TIERING01_DISTRIBUTION_PATH)
    original_metrics = _read_csv(root / GOAL_RISK_TIERING01_FORWARD_METRICS_PATH)
    dc03_rows = _read_csv(root / DC03_RISK_PATH)
    panel_rows = _read_csv(root / PROVIDER02B_PANEL_PATH)

    if not goal_risk_tiering01_valid_evidence(root):
        failures.append("goal_risk_tiering01_evidence_not_ready")
    goal_risk_row = workflow.get(GOAL_RISK_TIERING01_WORKFLOW_ID, {})
    if goal_risk_row.get("status") != "implemented_review_only":
        failures.append("goal_risk_tiering01_workflow_not_implemented_review_only")
    if not original_rows:
        failures.append("goal_risk_tiering01_diagnostics_missing")
    elif list(original_rows[0]) != _original_risk_tiering_fields():
        failures.append("goal_risk_tiering01_schema_invalid")
    if not original_distribution:
        failures.append("goal_risk_tiering01_distribution_missing")
    if not original_metrics:
        failures.append("goal_risk_tiering01_forward_metrics_missing")
    if not dc03_rows:
        failures.append("dc03_risk_rows_missing")
    if not panel_rows:
        failures.append("provider02b_panel_missing")
    elif list(panel_rows[0]) != PANEL_FIELDS:
        failures.append("provider02b_panel_schema_invalid")
    failures.extend(_validate_forbidden_input_sources())
    failures.extend(_validate_score_input_contract())

    diagnostics = _downside_diagnostic_rows(original_rows, panel_rows) if not failures else []
    if diagnostics and _keys(diagnostics) != _keys(original_rows):
        failures.append("downside_keys_do_not_match_goal_risk_tiering01")
    if diagnostics and _keys(diagnostics) != _keys(panel_rows):
        failures.append("downside_keys_do_not_match_provider02b_panel")
    duplicate_keys = _duplicate_key_count(diagnostics)
    if duplicate_keys:
        failures.append("duplicate_trade_date_symbol_keys_present")
    if diagnostics and not {LOW_BUCKET, MEDIUM_BUCKET, HIGH_BUCKET}.issubset({row["downside_risk_bucket"] for row in diagnostics}):
        warnings.append("downside_bucket_variation_incomplete")

    component_summary = _component_summary_rows(diagnostics)
    distribution = _distribution_rows(diagnostics, original_rows)
    metrics = _forward_metric_rows(diagnostics, panel_rows)
    correlations = _rank_correlation_rows(diagnostics, panel_rows)
    warnings.extend(_warning_codes_from_distribution(distribution))
    original_high_dominated = _original_high_volatility_momentum_dominated(diagnostics)
    if original_high_dominated:
        warnings.append("original_high_bucket_volatility_momentum_dominated")
    signal_classification = _signal_classification(diagnostics, distribution, correlations, metrics)
    if signal_classification == "downside_risk_tiering_signal_weak_or_unreliable":
        warnings.append("downside_risk_tiering_signal_weak_or_unreliable")
    elif signal_classification == "downside_risk_tiering_not_evaluable":
        warnings.append("downside_risk_tiering_not_evaluable")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))
    failures.extend(f"unexpected_backtest_output:{path}" for path in _unexpected_backtest_outputs(root))

    status = BLOCKED if failures else PASS_WITH_WARNINGS if warnings else PASS
    manifest = _manifest(status, failures, warnings, diagnostics, component_summary, distribution, metrics, correlations, original_rows)
    return {
        "status": status,
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "diagnostics": diagnostics,
        "component_summary": component_summary,
        "distribution": distribution,
        "metrics": metrics,
        "correlations": correlations,
        "manifest": manifest,
    }


def goal_risk_tiering011_valid_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        _report_pass_or_warn(report)
        and "Status: `PASS`" in audit
        and manifest.get("goal") == GOAL_NAME
        and manifest.get("mode") == MODE
        and manifest.get("review_only_downside_risk_repair_generated") is True
        and manifest.get("downside_risk_row_count") == 6000
        and manifest.get("used_goal_risk_tiering01_evidence_only") is True
        and manifest.get("used_provider02b_source_backed_panel_only") is True
        and manifest.get("score_construction_excludes_future_returns") is True
        and manifest.get("future_returns_used_only_for_post_hoc_evaluation") is True
        and manifest.get("component_reconstruction_available") is True
        and manifest.get("original_high_bucket_volatility_momentum_dominated") is True
        and manifest.get("downside_bucket_variation_available") is True
        and manifest.get("goal_rec_tiering01_locked_future") is True
        and manifest.get("goal10b4_locked_future") is True
        and manifest.get("goal10d_locked_future") is True
        and manifest.get("dashboard_outputs_generated") is False
        and manifest.get("recommendation_outputs_created") is False
        and manifest.get("position_outputs_created") is False
        and manifest.get("portfolio_returns_generated") is False
        and manifest.get("future_returns_used_in_score") is False
    )


def _goal_quant_research01_valid(root: Path) -> bool:
    try:
        from ashare_premarket.research.goal_quant_research01 import goal_quant_research01_valid_evidence
    except Exception:
        return False
    return goal_quant_research01_valid_evidence(root)


def goal_risk_tiering011_implemented_workflow_patch(status: str = PASS_WITH_WARNINGS) -> dict[str, str]:
    allowed = ALLOWED_NEXT_AVAILABLE if status == PASS else ALLOWED_NEXT_WEAK
    return {
        "display_name": "GOAL-RISK-TIERING-01.1 Downside Risk Repair Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_review_only",
        "current_repo_role": MODE,
        "implemented_in_repo": "true",
        "allowed_next_action": allowed,
        "depends_on": GOAL_RISK_TIERING01_WORKFLOW_ID,
        "produces_artifacts": WORKFLOW_PRODUCES_ARTIFACTS,
        "primary_docs": WORKFLOW_PRIMARY_DOCS,
        "primary_scripts": WORKFLOW_PRIMARY_SCRIPTS,
        "primary_outputs": WORKFLOW_PRIMARY_OUTPUTS,
        "promotion_rule": "implemented_review_only_after_goal_risk_tiering011_pass_with_warnings",
        "notes": WORKFLOW_NOTES,
    }


def locked_goal_rec_tiering01_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-REC-TIERING-01 Recommendation Score Tiering Gate",
        "stage_or_goal": "GOAL-REC-TIERING-01",
        "status": "locked_future",
        "current_repo_role": "locked_future_recommendation_score_tiering_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal_risk_tiering011_signal_ready",
        "depends_on": WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal_rec_tiering01_gate",
        "notes": "Future recommendation score tiering remains locked; GOAL-RISK-TIERING-01.1 creates downside-risk diagnostics only and no recommendation rows.",
    }


def locked_goal10b4_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-10B.4 Recommendation Backtest Revalidation",
        "stage_or_goal": "GOAL-10B.4",
        "status": "locked_future",
        "current_repo_role": "locked_future_recommendation_revalidation_after_tiering",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal_rec_tiering01_passes",
        "depends_on": GOAL_REC_TIERING01_WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal10b4_revalidation_gate",
        "notes": "Future GOAL-10B.4 remains locked; GOAL-RISK-TIERING-01.1 creates no recommendation revalidation rows.",
    }


def locked_position_band_validation_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-POSITION-BAND-VALIDATION-01 Position-Band Validation",
        "stage_or_goal": "GOAL-POSITION-BAND-VALIDATION-01",
        "status": "locked_future",
        "current_repo_role": "locked_future_position_band_validation_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal10b4_and_explicit_position_validation_request",
        "depends_on": GOAL10B4_WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_position_band_validation_gate",
        "notes": "Future position-band validation remains locked; GOAL-RISK-TIERING-01.1 creates no position outputs.",
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
        "notes": "Future GOAL-10D failure attribution remains locked; GOAL-RISK-TIERING-01.1 creates only review-only downside-risk diagnostics.",
    }


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / DIAGNOSTICS_PATH, result["diagnostics"], DIAGNOSTIC_FIELDS)
    write_csv(root / COMPONENT_SUMMARY_PATH, result["component_summary"], COMPONENT_SUMMARY_FIELDS)
    write_csv(root / DISTRIBUTION_PATH, result["distribution"], DISTRIBUTION_FIELDS)
    write_csv(root / FORWARD_METRICS_PATH, result["metrics"], FORWARD_METRIC_FIELDS)
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_contract(root)
    _write_report(root, result)
    _write_doc(root, result)


def _write_contract(root: Path) -> None:
    payload = {
        "goal": GOAL_NAME,
        "mode": MODE,
        "review_only": True,
        "primary_inputs": [
            GOAL_RISK_TIERING01_DIAGNOSTICS_PATH,
            GOAL_RISK_TIERING01_DISTRIBUTION_PATH,
            GOAL_RISK_TIERING01_FORWARD_METRICS_PATH,
            DC03_RISK_PATH,
            PROVIDER02B_PANEL_PATH,
        ],
        "score_input_fields": SCORE_INPUT_FIELDS,
        "forbidden_score_input_fields": FORBIDDEN_SCORE_INPUT_FIELDS,
        "score_thresholds": {
            LOW_BUCKET: f"< {LOW_MEDIUM_THRESHOLD}",
            MEDIUM_BUCKET: f">= {LOW_MEDIUM_THRESHOLD} and < {MEDIUM_HIGH_THRESHOLD}",
            HIGH_BUCKET: f">= {MEDIUM_HIGH_THRESHOLD}",
            INSUFFICIENT_BUCKET: "critical source evidence missing or GOAL-RISK-TIERING-01 insufficient evidence",
        },
        "downside_score_policy": "governance_first_not_tuned_to_forward_returns",
        "volatility_and_momentum_policy": "tracked_as_separate_flags_and_components; momentum does not add to downside score",
        "diagnostic_schema": DIAGNOSTIC_FIELDS,
        "component_summary_schema": COMPONENT_SUMMARY_FIELDS,
        "distribution_schema": DISTRIBUTION_FIELDS,
        "post_hoc_forward_metric_schema": FORWARD_METRIC_FIELDS,
        "allowed_outputs": [DIAGNOSTICS_PATH, COMPONENT_SUMMARY_PATH, DISTRIBUTION_PATH, FORWARD_METRICS_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH, CONTRACT_PATH],
        "forbidden_outputs": FALSE_BOUNDARY_KEYS,
        "downstream_locks": {
            GOAL_REC_TIERING01_WORKFLOW_ID: "locked_future",
            GOAL10B4_WORKFLOW_ID: "locked_future",
            POSITION_BAND_VALIDATION_WORKFLOW_ID: "locked_future",
            GOAL10D_WORKFLOW_ID: "locked_future",
            "dashboard_daily_report": "locked_future",
            "portfolio_backtest": "locked_future",
        },
    }
    write_json(root / CONTRACT_PATH, payload)


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    write_text(
        root / REPORT_PATH,
        "\n".join(
            [
                "# GOAL-RISK-TIERING-01.1 Downside Risk Repair Gate",
                "",
                f"GOAL-RISK-TIERING-01.1 Downside Risk Repair Gate: {result['status']}",
                f"Mode: `{MODE}`",
                "",
                "## Repair Scope",
                f"- Downside-risk rows: `{manifest['downside_risk_row_count']}`",
                f"- Unique symbols: `{manifest['unique_symbols']}`",
                f"- Unique trade dates: `{manifest['unique_trade_dates']}`",
                f"- Downside bucket distribution: `{manifest['downside_risk_bucket_distribution']}`",
                f"- Dominant bucket share: `{manifest['dominant_bucket_share']}`",
                f"- Original HIGH bucket volatility/momentum dominated: `{str(manifest['original_high_bucket_volatility_momentum_dominated']).lower()}`",
                f"- Original HIGH volatility/momentum dominated share: `{manifest['original_high_bucket_volatility_momentum_dominated_share']}`",
                f"- Signal classification: `{manifest['signal_classification']}`",
                f"- Recommended next action: `{manifest['recommended_next_goal']}`",
                "",
                "## No-Lookahead Boundary",
                "- Downside score construction excludes all `forward_return_*`, `benchmark_excess_return_*`, and `label_ready_*` fields.",
                "- Forward returns are used only for post-hoc group evaluation metrics after deterministic downside buckets are assigned.",
                "- Score weights are deterministic governance rules and are not tuned to maximize forward returns.",
                "",
                "## Locked Boundary",
                "- GOAL-RISK-TIERING-01 and DC03 artifacts are not overwritten.",
                "- No recommendation rows, position rows, BUY/SELL/HOLD outputs, target prices, position sizing, order quantities, portfolio weights, portfolio returns, equity curves, dashboards, HTML, Streamlit, frontend, trading, production, broker, local-lake, factor-mining, or DQN/RL outputs were generated.",
                "- GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, signal and portfolio backtests, paper/live trading, broker, production, factor-mining, local-lake, and DQN/RL remain locked.",
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
                "# GOAL-RISK-TIERING-01.1 Downside Risk Repair Gate",
                "",
                f"Status: `{result['status']}`",
                "",
                "GOAL-RISK-TIERING-01.1 is a review-only directionality repair gate for the prior numeric risk score. It creates a separate downside-focused diagnostic artifact and does not overwrite GOAL-RISK-TIERING-01, DC03, GOAL-07B, recommendation, or position outputs.",
                "",
                "## Inputs",
                "",
                f"- `{GOAL_RISK_TIERING01_DIAGNOSTICS_PATH}`",
                f"- `{GOAL_RISK_TIERING01_DISTRIBUTION_PATH}`",
                f"- `{GOAL_RISK_TIERING01_FORWARD_METRICS_PATH}`",
                f"- `{DC03_RISK_PATH}`",
                f"- `{PROVIDER02B_PANEL_PATH}`",
                "",
                "## Outputs",
                "",
                f"- `{DIAGNOSTICS_PATH}`",
                f"- `{COMPONENT_SUMMARY_PATH}`",
                f"- `{DISTRIBUTION_PATH}`",
                f"- `{FORWARD_METRICS_PATH}`",
                f"- `{REPORT_PATH}`",
                f"- `{MANIFEST_PATH}`",
                f"- `{AUDIT_PATH}`",
                f"- `{CONTRACT_PATH}`",
                "",
                "## Repair Logic",
                "",
                "The repair reconstructs deterministic component contributions from the source-backed panel: data quality, liquidity, trading status, ST status, downside price action from current/trailing information available at `trade_date`, volatility, momentum, provider/crosscheck, and universe governance.",
                "",
                "Momentum and abnormal positive movement are tracked separately and do not add to the downside score. Volatility contributes only a small bounded amount so the repaired score is not merely a volatility/momentum score. Future-return and benchmark-excess fields are excluded from construction and used only for post-hoc evaluation.",
                "",
                "## Result",
                "",
                f"- Downside-risk rows: `{manifest['downside_risk_row_count']}`",
                f"- Bucket distribution: `{manifest['downside_risk_bucket_distribution']}`",
                f"- Dominant bucket share: `{manifest['dominant_bucket_share']}`",
                f"- Minimum bucket size warning: `{str(manifest['minimum_bucket_size_warning']).lower()}`",
                f"- Collapse detected: `{str(manifest['downside_bucket_collapse_detected']).lower()}`",
                f"- Original HIGH volatility/momentum dominated: `{str(manifest['original_high_bucket_volatility_momentum_dominated']).lower()}`",
                f"- Signal classification: `{manifest['signal_classification']}`",
                f"- Recommended next goal: `{manifest['recommended_next_goal']}`",
                "",
                "## Locked Boundary",
                "",
                "GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, signal backtest promotion, portfolio backtest, paper trading, live trading, broker integration, production writes, factor-mining, local-lake writes, and DQN/RL remain locked or deleted from active mainline.",
                "",
            ]
        ),
    )


def _manifest(
    status: str,
    failures: list[str],
    warnings: list[str],
    diagnostics: list[dict[str, object]],
    component_summary: list[dict[str, object]],
    distribution: list[dict[str, object]],
    metrics: list[dict[str, object]],
    correlations: list[dict[str, object]],
    original_rows: list[dict[str, str]],
) -> dict[str, object]:
    symbols = sorted({str(row.get("symbol", "")) for row in diagnostics if row.get("symbol", "")})
    dates = sorted({str(row.get("trade_date", "")) for row in diagnostics if row.get("trade_date", "")})
    bucket_distribution = dict(Counter(str(row.get("downside_risk_bucket", "")) for row in diagnostics))
    original_distribution = dict(Counter(str(row.get("risk_score_bucket", "")) for row in original_rows))
    dominant_bucket_share = _dominant_share(bucket_distribution)
    represented_counts = [count for count in bucket_distribution.values() if count > 0]
    minimum_bucket_size_warning = any(0 < count < MIN_BUCKET_ROWS for count in represented_counts)
    collapse = len(represented_counts) < 2 or dominant_bucket_share >= COLLAPSE_THRESHOLD
    original_high_share = _original_high_volatility_momentum_dominated_share(diagnostics)
    original_high_dominated = original_high_share >= 0.50
    signal_classification = _signal_classification(diagnostics, distribution, correlations, metrics)
    allowed_next = ALLOWED_NEXT_AVAILABLE if signal_classification == "downside_risk_tiering_signal_available" and not minimum_bucket_size_warning and not collapse else ALLOWED_NEXT_WEAK
    recommended_next = (
        "GOAL-REC-TIERING-01"
        if allowed_next == ALLOWED_NEXT_AVAILABLE
        else "another_deterministic_governance_risk_rule_review_before_goal_rec_tiering01"
    )
    return {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "status": status,
        "mode": MODE,
        "allowed_next_action": allowed_next if status != BLOCKED else "repair_goal_risk_tiering011_blockers",
        "signal_classification": signal_classification,
        "recommended_next_goal": recommended_next,
        "primary_input_artifacts": [GOAL_RISK_TIERING01_DIAGNOSTICS_PATH, GOAL_RISK_TIERING01_DISTRIBUTION_PATH, GOAL_RISK_TIERING01_FORWARD_METRICS_PATH, DC03_RISK_PATH, PROVIDER02B_PANEL_PATH],
        "forbidden_primary_inputs_used": [],
        "downside_risk_row_count": len(diagnostics),
        "component_summary_rows": len(component_summary),
        "distribution_summary_rows": len(distribution),
        "forward_metric_rows": len(metrics),
        "unique_symbols": len(symbols),
        "symbols": symbols,
        "unique_trade_dates": len(dates),
        "date_min": dates[0] if dates else "",
        "date_max": dates[-1] if dates else "",
        "downside_risk_bucket_distribution": bucket_distribution,
        "downside_bucket_count": len([count for count in bucket_distribution.values() if count > 0]),
        "dominant_bucket_share": _fmt(dominant_bucket_share),
        "minimum_bucket_size_warning": minimum_bucket_size_warning,
        "downside_bucket_collapse_detected": collapse,
        "original_goal_risk_tiering01_bucket_distribution": original_distribution,
        "original_low_rows": original_distribution.get("LOW_RISK_REVIEW_ONLY", 0),
        "original_medium_rows": original_distribution.get("MEDIUM_RISK_REVIEW_ONLY", 0),
        "original_high_rows": original_distribution.get("HIGH_RISK_REVIEW_ONLY", 0),
        "original_insufficient_rows": original_distribution.get("INSUFFICIENT_EVIDENCE_REVIEW_ONLY", 0),
        "original_high_bucket_volatility_momentum_dominated": original_high_dominated,
        "original_high_bucket_volatility_momentum_dominated_share": _fmt(original_high_share),
        "rank_correlation_rows": correlations,
        "rank_correlation_available": any(row.get("correlation_status") == "available" for row in correlations),
        "review_only_downside_risk_repair_generated": status != BLOCKED,
        "used_goal_risk_tiering01_evidence_only": True,
        "used_dc03_risk_diagnostics_only": True,
        "used_provider02b_source_backed_panel_only": True,
        "source_backed_panel_linkage_check": bool(diagnostics),
        "duplicate_trade_date_symbol_keys": _duplicate_key_count(diagnostics),
        "duplicate_key_check": _duplicate_key_count(diagnostics) == 0,
        "component_reconstruction_available": bool(component_summary),
        "downside_bucket_variation_available": len([count for count in bucket_distribution.values() if count > 0]) >= 3,
        "score_input_fields": SCORE_INPUT_FIELDS,
        "forbidden_score_input_fields": FORBIDDEN_SCORE_INPUT_FIELDS,
        "score_input_fields_do_not_include_future_return_labels": _score_fields_exclude_future_returns(),
        "score_construction_excludes_future_returns": True,
        "future_returns_used_only_for_post_hoc_evaluation": True,
        "no_lookahead_score_construction_check": True,
        "score_weights_tuning_policy": "deterministic_governance_rules_not_tuned_to_forward_returns",
        "volatility_momentum_separated_from_downside_score": True,
        "review_only_non_actionable_boundary_preserved": True,
        "goal_risk_tiering011_workflow_status_after_goal": "implemented_review_only" if status != BLOCKED else "locked_future",
        "goal_rec_tiering01_status_after_goal_risk_tiering011": "locked_future",
        "goal10b4_status_after_goal_risk_tiering011": "locked_future",
        "position_band_validation_status_after_goal_risk_tiering011": "locked_future",
        "goal10d_status_after_goal_risk_tiering011": "locked_future",
        "dashboard_daily_report_status_after_goal_risk_tiering011": "locked_future",
        "portfolio_backtest_status_after_goal_risk_tiering011": "locked_future",
        "goal_rec_tiering01_locked_future": True,
        "goal10b4_locked_future": True,
        "position_band_validation_locked_future": True,
        "goal10d_locked_future": True,
        "dashboard_daily_report_locked_future": True,
        "portfolio_backtest_locked_future": True,
        "output_artifacts": [DIAGNOSTICS_PATH, COMPONENT_SUMMARY_PATH, DISTRIBUTION_PATH, FORWARD_METRICS_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH, CONTRACT_PATH],
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        **{key: False for key in FALSE_BOUNDARY_KEYS},
    }


def _downside_diagnostic_rows(original_rows: list[dict[str, str]], panel_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    panel_by_key = {(row.get("trade_date", ""), row.get("symbol", "")): row for row in panel_rows}
    trailing_features = _trailing_feature_map(panel_rows)
    provider_counts = Counter(row.get("source_provider", "") for row in panel_rows)
    output: list[dict[str, object]] = []
    for original in sorted(original_rows, key=lambda item: (item.get("trade_date", ""), item.get("symbol", ""))):
        key = (original.get("trade_date", ""), original.get("symbol", ""))
        panel = panel_by_key.get(key, {})
        components, insufficient = _component_scores(original, panel, trailing_features.get(key, {}), provider_counts)
        score = _downside_score(components)
        bucket = INSUFFICIENT_BUCKET if insufficient else _bucket(score)
        output.append(
            {
                "trade_date": original.get("trade_date", ""),
                "symbol": original.get("symbol", ""),
                "original_risk_score_numeric": original.get("risk_score_numeric", ""),
                "original_risk_score_bucket": original.get("risk_score_bucket", ""),
                "downside_risk_score_numeric": _fmt(score),
                "downside_risk_bucket": bucket,
                "downside_risk_severity": bucket,
                "data_quality_risk_component": _fmt(components["data_quality"]),
                "liquidity_risk_component": _fmt(components["liquidity"]),
                "trading_status_risk_component": _fmt(components["trading_status"]),
                "st_status_risk_component": _fmt(components["st_status"]),
                "downside_price_action_component": _fmt(components["downside_price_action"]),
                "volatility_component": _fmt(components["volatility"]),
                "momentum_component": _fmt(components["momentum"]),
                "provider_crosscheck_component": _fmt(components["provider_crosscheck"]),
                "universe_governance_component": _fmt(components["universe_governance"]),
                "volatility_momentum_flag": components["volatility"] + components["momentum"] > components["downside_price_action"],
                "abnormal_positive_movement_flag": components["abnormal_positive_movement"] > 0,
                "abnormal_negative_movement_flag": components["abnormal_negative_movement"] > 0,
                "score_construction_no_lookahead_status": "passed_future_return_fields_excluded",
                "diagnostic_mode": MODE,
                "non_actionable_disclaimer": NON_ACTIONABLE,
            }
        )
    return output


def _component_scores(original: dict[str, str], panel: dict[str, str], features: dict[str, object], provider_counts: Counter[str]) -> tuple[dict[str, float], bool]:
    insufficient = original.get("risk_score_bucket") == "INSUFFICIENT_EVIDENCE_REVIEW_ONLY"
    data_quality = 0.0
    for field in ["open", "high", "low", "close", "pre_close"]:
        if not _is_float(panel.get(field, "")):
            data_quality += 8.0
            insufficient = True
    if not _is_float(panel.get("amount", "")) or float(str(panel.get("amount", "0") or "0")) <= 0:
        data_quality += 10.0
        insufficient = True
    if not _is_float(panel.get("turnover", "")):
        data_quality += 10.0
        insufficient = True
    if panel.get("panel_contract_status") != "source_backed_evaluation_panel_ready_for_dc03":
        data_quality += 5.0

    liquidity = 0.0
    amount = _float_or_none(panel.get("amount", ""))
    if amount is None:
        liquidity += 15.0
    elif amount < 50_000_000:
        liquidity += 18.0
    elif amount < 150_000_000:
        liquidity += 10.0
    elif amount < 300_000_000:
        liquidity += 5.0
    turnover = _float_or_none(panel.get("turnover", ""))
    if turnover is None:
        liquidity += 10.0
    elif turnover < 0.15:
        liquidity += 12.0
    elif turnover < 0.30:
        liquidity += 7.0
    elif turnover < 0.60:
        liquidity += 3.0
    liquidity = min(liquidity, 25.0)

    trading_status = 28.0 if panel.get("trading_status") and panel.get("trading_status") != "trading" else 0.0
    st_status = 24.0 if panel.get("is_st") == "true" else 0.0
    pct = _float_or_none(panel.get("pct_chg", "")) or 0.0
    downside = 0.0
    abnormal_negative = 0.0
    if pct <= -9.5:
        downside += 24.0
        abnormal_negative = 1.0
    elif pct <= -5.0:
        downside += 16.0
        abnormal_negative = 1.0
    elif pct <= -3.0:
        downside += 10.0
        abnormal_negative = 1.0
    elif pct <= -1.5:
        downside += 5.0

    trailing_5d = features.get("trailing_return_5d")
    if isinstance(trailing_5d, float):
        if trailing_5d <= -0.15:
            downside += 22.0
            abnormal_negative = 1.0
        elif trailing_5d <= -0.08:
            downside += 14.0
            abnormal_negative = 1.0
        elif trailing_5d <= -0.04:
            downside += 8.0
        elif trailing_5d <= -0.02:
            downside += 4.0
    else:
        downside += 2.0

    trailing_20d = features.get("trailing_return_20d")
    if isinstance(trailing_20d, float):
        if trailing_20d <= -0.30:
            downside += 20.0
            abnormal_negative = 1.0
        elif trailing_20d <= -0.18:
            downside += 14.0
            abnormal_negative = 1.0
        elif trailing_20d <= -0.10:
            downside += 8.0
        elif trailing_20d <= -0.05:
            downside += 4.0
    else:
        downside += 2.0

    drawdown_20d = features.get("drawdown_from_20d_high")
    if isinstance(drawdown_20d, float):
        if drawdown_20d <= -0.25:
            downside += 12.0
            abnormal_negative = 1.0
        elif drawdown_20d <= -0.15:
            downside += 8.0
        elif drawdown_20d <= -0.08:
            downside += 4.0
    downside = min(downside, 55.0)

    volatility = 0.0
    volatility_proxy = features.get("trailing_volatility_proxy")
    if isinstance(volatility_proxy, float):
        if volatility_proxy >= 5.0:
            volatility += 10.0
        elif volatility_proxy >= 3.5:
            volatility += 7.0
        elif volatility_proxy >= 2.5:
            volatility += 4.0
    else:
        volatility += 2.0

    momentum = 0.0
    abnormal_positive = 0.0
    if pct >= 9.5:
        momentum += 12.0
        abnormal_positive = 1.0
    elif pct >= 5.0:
        momentum += 8.0
        abnormal_positive = 1.0
    elif pct >= 3.0:
        momentum += 4.0
    if isinstance(trailing_5d, float):
        if trailing_5d >= 0.15:
            momentum += 8.0
            abnormal_positive = 1.0
        elif trailing_5d >= 0.08:
            momentum += 6.0
        elif trailing_5d >= 0.04:
            momentum += 3.0
    if isinstance(trailing_20d, float):
        if trailing_20d >= 0.30:
            momentum += 8.0
            abnormal_positive = 1.0
        elif trailing_20d >= 0.18:
            momentum += 6.0
        elif trailing_20d >= 0.10:
            momentum += 3.0

    provider_crosscheck = 0.0
    if panel.get("crosscheck_status") != "checked_close_diff_within_tolerance":
        provider_crosscheck += 8.0
    provider = panel.get("source_provider", "")
    if provider and provider_counts.get(provider, 0) == sum(provider_counts.values()):
        provider_crosscheck += 6.0

    universe_governance = 0.0
    if panel.get("universe_mode") == "provider_panel_candidate_universe_review_only":
        universe_governance += 4.0
    if "canonical_approved_universe_below_50" in panel.get("source_warning_codes", ""):
        universe_governance += 2.0

    return (
        {
            "data_quality": data_quality,
            "liquidity": liquidity,
            "trading_status": trading_status,
            "st_status": st_status,
            "downside_price_action": downside,
            "volatility": volatility,
            "momentum": momentum,
            "provider_crosscheck": provider_crosscheck,
            "universe_governance": universe_governance,
            "abnormal_positive_movement": abnormal_positive,
            "abnormal_negative_movement": abnormal_negative,
        },
        insufficient,
    )


def _downside_score(components: dict[str, float]) -> float:
    return min(
        100.0,
        components["data_quality"]
        + components["liquidity"]
        + components["trading_status"]
        + components["st_status"]
        + components["downside_price_action"]
        + min(components["volatility"], 5.0)
        + components["provider_crosscheck"]
        + components["universe_governance"],
    )


def _trailing_feature_map(panel_rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, object]]:
    by_symbol: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in panel_rows:
        by_symbol[row.get("symbol", "")].append(row)
    output: dict[tuple[str, str], dict[str, object]] = {}
    for symbol, rows in by_symbol.items():
        ordered = sorted(rows, key=lambda item: item.get("trade_date", ""))
        for index, row in enumerate(ordered):
            close = _float_or_none(row.get("close", ""))
            trailing_5d = None
            trailing_20d = None
            drawdown = None
            volatility = None
            if close is not None and index >= 5:
                previous = _float_or_none(ordered[index - 5].get("close", ""))
                if previous:
                    trailing_5d = close / previous - 1.0
            if close is not None and index >= 20:
                previous = _float_or_none(ordered[index - 20].get("close", ""))
                if previous:
                    trailing_20d = close / previous - 1.0
                highs = [_float_or_none(ordered[item].get("close", "")) for item in range(index - 20, index + 1)]
                materialized_highs = [value for value in highs if value is not None and value > 0]
                if materialized_highs:
                    drawdown = close / max(materialized_highs) - 1.0
            pct_values = [_float_or_none(ordered[item].get("pct_chg", "")) for item in range(max(0, index - 19), index + 1)]
            pct_materialized = [value for value in pct_values if value is not None]
            if len(pct_materialized) >= 5:
                volatility = pstdev(pct_materialized)
            output[(row.get("trade_date", ""), symbol)] = {
                "trailing_return_5d": trailing_5d,
                "trailing_return_20d": trailing_20d,
                "drawdown_from_20d_high": drawdown,
                "trailing_volatility_proxy": volatility,
            }
    return output


def _component_summary_rows(diagnostics: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    total = len(diagnostics)
    for group_type, field, values in [
        ("original_risk_score_bucket", "original_risk_score_bucket", sorted({str(row.get("original_risk_score_bucket", "")) for row in diagnostics})),
        ("downside_risk_bucket", "downside_risk_bucket", BUCKET_ORDER),
    ]:
        for value in values:
            group = [row for row in diagnostics if row.get(field) == value]
            if not group:
                continue
            rows.append(_component_summary_row(group_type, value, group, total))
    rows.append(_component_summary_row("diagnostic", "all_rows", diagnostics, total))
    return rows


def _component_summary_row(group_type: str, group_value: str, group: list[dict[str, object]], total: int) -> dict[str, object]:
    component_fields = {
        "data_quality": "data_quality_risk_component",
        "liquidity": "liquidity_risk_component",
        "trading_status": "trading_status_risk_component",
        "st_status": "st_status_risk_component",
        "downside_price_action": "downside_price_action_component",
        "volatility": "volatility_component",
        "momentum": "momentum_component",
        "provider_crosscheck": "provider_crosscheck_component",
        "universe_governance": "universe_governance_component",
    }
    averages = {name: _mean(_series(group, field)) or 0.0 for name, field in component_fields.items()}
    dominant = max(averages.items(), key=lambda item: item[1])[0] if averages else ""
    vol_mom_share = _rate(str(row.get("volatility_momentum_flag", "")).lower() == "true" for row in group) or 0.0
    positive_share = _rate(str(row.get("abnormal_positive_movement_flag", "")).lower() == "true" for row in group) or 0.0
    negative_share = _rate(str(row.get("abnormal_negative_movement_flag", "")).lower() == "true" for row in group) or 0.0
    status = PASS_WITH_WARNINGS if group_type == "original_risk_score_bucket" and group_value == "HIGH_RISK_REVIEW_ONLY" and vol_mom_share >= 0.50 else PASS
    return {
        "summary_group_type": group_type,
        "summary_group_value": group_value,
        "row_count": len(group),
        "share": _fmt(_share(len(group), total)),
        "average_original_risk_score_numeric": _fmt(_mean(_series(group, "original_risk_score_numeric"))),
        "average_downside_risk_score_numeric": _fmt(_mean(_series(group, "downside_risk_score_numeric"))),
        "average_data_quality_risk_component": _fmt(averages["data_quality"]),
        "average_liquidity_risk_component": _fmt(averages["liquidity"]),
        "average_trading_status_risk_component": _fmt(averages["trading_status"]),
        "average_st_status_risk_component": _fmt(averages["st_status"]),
        "average_downside_price_action_component": _fmt(averages["downside_price_action"]),
        "average_volatility_component": _fmt(averages["volatility"]),
        "average_momentum_component": _fmt(averages["momentum"]),
        "average_provider_crosscheck_component": _fmt(averages["provider_crosscheck"]),
        "average_universe_governance_component": _fmt(averages["universe_governance"]),
        "dominant_component_group": dominant,
        "volatility_momentum_dominated_share": _fmt(vol_mom_share),
        "abnormal_positive_movement_share": _fmt(positive_share),
        "abnormal_negative_movement_share": _fmt(negative_share),
        "diagnostic_status": status,
        "notes": "Component contribution summary reconstructed from source panel and prior risk-tier rows.",
    }


def _distribution_rows(diagnostics: list[dict[str, object]], original_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    total = len(diagnostics)
    bucket_counts = Counter(str(row.get("downside_risk_bucket", "")) for row in diagnostics)
    original_counts = Counter(str(row.get("risk_score_bucket", "")) for row in original_rows)
    dominant = _dominant_share(dict(bucket_counts))
    represented_counts = [count for count in bucket_counts.values() if count > 0]
    min_warning = any(0 < count < MIN_BUCKET_ROWS for count in represented_counts)
    collapse = len(represented_counts) < 2 or dominant >= COLLAPSE_THRESHOLD
    rows: list[dict[str, object]] = []
    for bucket in BUCKET_ORDER:
        group = [row for row in diagnostics if row.get("downside_risk_bucket") == bucket]
        count = len(group)
        rows.append(
            _distribution_row(
                "downside_risk_bucket_distribution",
                "downside_risk_bucket",
                bucket,
                count,
                _share(count, total),
                len({row.get("symbol", "") for row in group}),
                len({row.get("trade_date", "") for row in group}),
                dominant,
                0 < count < MIN_BUCKET_ROWS,
                collapse,
                original_counts,
                PASS_WITH_WARNINGS if (0 < count < MIN_BUCKET_ROWS or collapse) else PASS,
                "Downside risk bucket row count and share.",
            )
        )
    for bucket in ["LOW_RISK_REVIEW_ONLY", "MEDIUM_RISK_REVIEW_ONLY", "HIGH_RISK_REVIEW_ONLY", "INSUFFICIENT_EVIDENCE_REVIEW_ONLY"]:
        count = original_counts.get(bucket, 0)
        rows.append(
            _distribution_row(
                "goal_risk_tiering01_bucket_distribution",
                "original_risk_score_bucket",
                bucket,
                count,
                _share(count, len(original_rows)),
                len({row.get("symbol", "") for row in original_rows if row.get("risk_score_bucket") == bucket}),
                len({row.get("trade_date", "") for row in original_rows if row.get("risk_score_bucket") == bucket}),
                dominant,
                min_warning,
                collapse,
                original_counts,
                PASS,
                "GOAL-RISK-TIERING-01 bucket distribution for comparison.",
            )
        )
    rows.append(
        _distribution_row(
            "dominant_bucket_share",
            "diagnostic",
            "dominant_bucket_share",
            max(bucket_counts.values()) if bucket_counts else 0,
            dominant,
            len({row.get("symbol", "") for row in diagnostics}),
            len({row.get("trade_date", "") for row in diagnostics}),
            dominant,
            min_warning,
            collapse,
            original_counts,
            PASS_WITH_WARNINGS if collapse else PASS,
            "Dominant downside bucket share compared with collapse threshold.",
        )
    )
    rows.append(
        _distribution_row(
            "minimum_bucket_size_warning",
            "diagnostic",
            "represented_bucket_minimum",
            min(represented_counts) if represented_counts else 0,
            _share(min(represented_counts) if represented_counts else 0, total),
            len({row.get("symbol", "") for row in diagnostics}),
            len({row.get("trade_date", "") for row in diagnostics}),
            dominant,
            min_warning,
            collapse,
            original_counts,
            PASS_WITH_WARNINGS if min_warning else PASS,
            "Warns when any represented downside risk bucket has fewer than 30 rows.",
        )
    )
    return rows


def _distribution_row(
    name: str,
    group_type: str,
    group_value: str,
    row_count: int,
    share: float,
    unique_symbols: int,
    unique_dates: int,
    dominant: float,
    min_warning: bool,
    collapse: bool,
    original_counts: Counter[str],
    status: str,
    notes: str,
) -> dict[str, object]:
    return {
        "distribution_name": name,
        "group_type": group_type,
        "group_value": group_value,
        "row_count": row_count,
        "share": _fmt(share),
        "unique_symbols": unique_symbols,
        "unique_trade_dates": unique_dates,
        "dominant_bucket_share": _fmt(dominant),
        "minimum_bucket_size_warning": min_warning,
        "collapse_detected": collapse,
        "original_low_rows": original_counts.get("LOW_RISK_REVIEW_ONLY", 0),
        "original_medium_rows": original_counts.get("MEDIUM_RISK_REVIEW_ONLY", 0),
        "original_high_rows": original_counts.get("HIGH_RISK_REVIEW_ONLY", 0),
        "original_insufficient_rows": original_counts.get("INSUFFICIENT_EVIDENCE_REVIEW_ONLY", 0),
        "diagnostic_status": status,
        "notes": notes,
    }


def _forward_metric_rows(diagnostics: list[dict[str, object]], panel_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    panel_by_key = {(row.get("trade_date", ""), row.get("symbol", "")): row for row in panel_rows}
    joined = []
    for row in diagnostics:
        panel = panel_by_key.get((str(row.get("trade_date", "")), str(row.get("symbol", ""))), {})
        joined.append({**row, **{field: panel.get(field, "") for field in _post_hoc_label_fields()}})
    output: list[dict[str, object]] = []
    for bucket in BUCKET_ORDER:
        group = [row for row in joined if row.get("downside_risk_bucket") == bucket]
        if not group:
            continue
        metric: dict[str, object] = {
            "downside_risk_bucket": bucket,
            "row_count": len(group),
            "unique_symbols": len({row.get("symbol", "") for row in group}),
            "unique_trade_dates": len({row.get("trade_date", "") for row in group}),
        }
        for horizon in HORIZONS:
            forward = _series(group, f"forward_return_{horizon}")
            excess = _series(group, f"benchmark_excess_return_{horizon}")
            metric[f"mean_forward_return_{horizon}"] = _fmt(_mean(forward))
            metric[f"mean_benchmark_excess_return_{horizon}"] = _fmt(_mean(excess))
            metric[f"hit_rate_{horizon}"] = _fmt(_rate(value > 0 for value in forward))
            metric[f"positive_excess_rate_{horizon}"] = _fmt(_rate(value > 0 for value in excess))
        output.append(metric)
    return output


def _rank_correlation_rows(diagnostics: list[dict[str, object]], panel_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    panel_by_key = {(row.get("trade_date", ""), row.get("symbol", "")): row for row in panel_rows}
    scores_by_key = {
        (str(row.get("trade_date", "")), str(row.get("symbol", ""))): float(str(row.get("downside_risk_score_numeric", "0") or "0"))
        for row in diagnostics
        if _is_float(row.get("downside_risk_score_numeric", ""))
    }
    rows: list[dict[str, object]] = []
    for field in _post_hoc_label_fields():
        pairs: list[tuple[float, float]] = []
        for key, score in scores_by_key.items():
            panel = panel_by_key.get(key, {})
            if _is_float(panel.get(field, "")):
                pairs.append((score, float(str(panel.get(field)))))
        valid = len(pairs) >= MIN_BUCKET_ROWS and len({score for score, _ in pairs}) >= 3 and len({value for _, value in pairs}) >= 3
        corr = _spearman([score for score, _ in pairs], [value for _, value in pairs]) if valid else None
        rows.append(
            {
                "target_field": field,
                "available_rows": len(pairs),
                "rank_correlation": _fmt(corr),
                "absolute_rank_correlation": _fmt(abs(corr) if corr is not None else None),
                "correlation_status": "available" if valid else "not_evaluable",
            }
        )
    return rows


def _signal_classification(
    diagnostics: list[dict[str, object]],
    distribution: list[dict[str, object]],
    correlations: list[dict[str, object]],
    metrics: list[dict[str, object]],
) -> str:
    if not diagnostics or not correlations or not metrics:
        return "downside_risk_tiering_not_evaluable"
    collapse = any(str(row.get("collapse_detected", "")).lower() == "true" for row in distribution)
    min_warning = any(str(row.get("minimum_bucket_size_warning", "")).lower() == "true" for row in distribution)
    by_bucket = {row["downside_risk_bucket"]: row for row in metrics}
    low = by_bucket.get(LOW_BUCKET, {})
    high = by_bucket.get(HIGH_BUCKET, {})
    separation = False
    if _is_float(low.get("mean_benchmark_excess_return_20d", "")) and _is_float(high.get("mean_benchmark_excess_return_20d", "")):
        separation = float(str(high["mean_benchmark_excess_return_20d"])) < float(str(low["mean_benchmark_excess_return_20d"]))
    available = [row for row in correlations if row.get("correlation_status") == "available" and _is_float(row.get("absolute_rank_correlation", ""))]
    if not available:
        return "downside_risk_tiering_not_evaluable"
    max_abs = max(float(str(row.get("absolute_rank_correlation"))) for row in available)
    if not collapse and not min_warning and separation and max_abs >= 0.08:
        return "downside_risk_tiering_signal_available"
    return "downside_risk_tiering_signal_weak_or_unreliable"


def _warning_codes_from_distribution(rows: list[dict[str, object]]) -> list[str]:
    return sorted({str(row.get("distribution_name", "")) for row in rows if row.get("diagnostic_status") == PASS_WITH_WARNINGS})


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys()) if rows else []
    by_id = {row["workflow_id"]: row for row in rows}
    manifest = result["manifest"]
    patch = goal_risk_tiering011_implemented_workflow_patch(str(result["status"]))
    if result["status"] == BLOCKED:
        patch.update(
            {
                "status": "locked_future",
                "current_repo_role": "review_only_downside_risk_repair_blocked",
                "implemented_in_repo": "false",
                "allowed_next_action": "repair_goal_risk_tiering011_blockers",
                "produces_artifacts": "",
                "primary_scripts": "",
                "primary_outputs": "",
                "promotion_rule": "locked_until_goal_risk_tiering011_passes",
                "notes": "GOAL-RISK-TIERING-01.1 is blocked; GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, and downstream execution remain locked.",
            }
        )
    else:
        patch["allowed_next_action"] = str(manifest.get("allowed_next_action", ALLOWED_NEXT_WEAK))
    _upsert_workflow_row(rows, by_id, WORKFLOW_ID, patch, after=GOAL_RISK_TIERING01_WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL_REC_TIERING01_WORKFLOW_ID, locked_goal_rec_tiering01_patch(), after=WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL10B4_WORKFLOW_ID, locked_goal10b4_patch(), after=GOAL_REC_TIERING01_WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, POSITION_BAND_VALIDATION_WORKFLOW_ID, locked_position_band_validation_patch(), after=GOAL10B4_WORKFLOW_ID)
    if GOAL10D_WORKFLOW_ID in by_id:
        by_id[GOAL10D_WORKFLOW_ID].update(locked_goal10d_patch())
    for workflow_id in [
        GOAL_REC_TIERING01_WORKFLOW_ID,
        GOAL10B4_WORKFLOW_ID,
        POSITION_BAND_VALIDATION_WORKFLOW_ID,
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
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_risk_tiering011"
    if "dqn_rl_mainline" in by_id:
        by_id["dqn_rl_mainline"]["status"] = "deleted_from_active_mainline"
        by_id["dqn_rl_mainline"]["implemented_in_repo"] = "false"
    if "v2_factor_research_upgrade" in by_id:
        by_id["v2_factor_research_upgrade"]["status"] = "planned_locked"
        by_id["v2_factor_research_upgrade"]["implemented_in_repo"] = "false"
    preserve_later_review_only_workflow_states(root, by_id)
    if result["status"] != BLOCKED and WORKFLOW_ID in by_id:
        by_id[WORKFLOW_ID].update(goal_risk_tiering011_implemented_workflow_patch(str(result["status"])))
        by_id[WORKFLOW_ID]["allowed_next_action"] = str(manifest.get("allowed_next_action", ALLOWED_NEXT_WEAK))
    if GOAL_REC_TIERING01_WORKFLOW_ID in by_id and not _goal_quant_research01_valid(root):
        by_id[GOAL_REC_TIERING01_WORKFLOW_ID].update(locked_goal_rec_tiering01_patch())
    write_csv(path, rows, fields)


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    if not path.exists():
        return
    payload = read_json(path)
    payload[WORKFLOW_ID] = "implemented_review_only" if result["status"] != BLOCKED else False
    payload[GOAL_REC_TIERING01_WORKFLOW_ID] = False
    payload[GOAL10B4_WORKFLOW_ID] = False
    payload[POSITION_BAND_VALIDATION_WORKFLOW_ID] = False
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


def _original_risk_tiering_fields() -> list[str]:
    return [
        "trade_date",
        "symbol",
        "source_panel",
        "risk_score_numeric",
        "risk_score_bucket",
        "risk_severity_tiered",
        "original_dc03_risk_severity",
        "risk_tiering_rule_ids",
        "risk_tiering_warning_codes",
        "source_provider",
        "universe_mode",
        "diagnostic_mode",
        "non_actionable_disclaimer",
    ]


def _validate_forbidden_input_sources() -> list[str]:
    forbidden = ["outputs/samples/", "demo", "fixture", "goal_v1_diagnostic_coverage02"]
    sources = [GOAL_RISK_TIERING01_DIAGNOSTICS_PATH, GOAL_RISK_TIERING01_DISTRIBUTION_PATH, GOAL_RISK_TIERING01_FORWARD_METRICS_PATH, DC03_RISK_PATH, PROVIDER02B_PANEL_PATH]
    return [f"forbidden_primary_input:{source}" for source in sources if any(marker in source.lower() for marker in forbidden)]


def _validate_score_input_contract() -> list[str]:
    return [] if _score_fields_exclude_future_returns() else ["score_input_fields_include_future_returns"]


def _score_fields_exclude_future_returns() -> bool:
    lowered = {field.lower() for field in SCORE_INPUT_FIELDS}
    return not any(field.lower() in lowered for field in FORBIDDEN_SCORE_INPUT_FIELDS) and not any("forward_return" in field or "benchmark_excess_return" in field or "label_ready" in field for field in lowered)


def _post_hoc_label_fields() -> list[str]:
    return [
        "forward_return_1d",
        "forward_return_5d",
        "forward_return_20d",
        "benchmark_excess_return_1d",
        "benchmark_excess_return_5d",
        "benchmark_excess_return_20d",
    ]


def _bucket(score: float) -> str:
    if score >= MEDIUM_HIGH_THRESHOLD:
        return HIGH_BUCKET
    if score >= LOW_MEDIUM_THRESHOLD:
        return MEDIUM_BUCKET
    return LOW_BUCKET


def _original_high_volatility_momentum_dominated(diagnostics: list[dict[str, object]]) -> bool:
    return _original_high_volatility_momentum_dominated_share(diagnostics) >= 0.50


def _original_high_volatility_momentum_dominated_share(diagnostics: list[dict[str, object]]) -> float:
    high_rows = [row for row in diagnostics if row.get("original_risk_score_bucket") == "HIGH_RISK_REVIEW_ONLY"]
    if not high_rows:
        return 0.0
    return _rate(
        (_to_float(row.get("volatility_component")) + _to_float(row.get("momentum_component"))) > _to_float(row.get("downside_price_action_component"))
        for row in high_rows
    ) or 0.0


def _forbidden_outputs_present(root: Path) -> list[str]:
    return [item for item in FORBIDDEN_OUTPUT_DIRS if (root / item).exists()]


def _unexpected_backtest_outputs(root: Path) -> list[str]:
    path = root / "outputs/backtest"
    if not path.exists():
        return []
    return sorted(str(item.relative_to(root)) for item in path.glob("*") if item.is_file() and str(item.relative_to(root)) not in ALLOWED_BACKTEST_OUTPUTS)


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
    return "GOAL-RISK-TIERING-01.1 Downside Risk Repair Gate: PASS" in report or "GOAL-RISK-TIERING-01.1 Downside Risk Repair Gate: PASS_WITH_WARNINGS" in report


def _keys(rows: list[dict[str, object]]) -> set[tuple[str, str]]:
    return {(str(row.get("trade_date", "")), str(row.get("symbol", ""))) for row in rows}


def _duplicate_key_count(rows: list[dict[str, object]]) -> int:
    counts = Counter((str(row.get("trade_date", "")), str(row.get("symbol", ""))) for row in rows)
    return sum(count - 1 for count in counts.values() if count > 1)


def _series(rows: list[dict[str, object]], field: str) -> list[float]:
    values = []
    for row in rows:
        raw = row.get(field, "")
        if _is_float(raw):
            values.append(float(str(raw)))
    return values


def _is_float(value: object) -> bool:
    try:
        float(str(value))
    except (TypeError, ValueError):
        return False
    return str(value) != ""


def _float_or_none(value: object) -> float | None:
    if not _is_float(value):
        return None
    return float(str(value))


def _to_float(value: object) -> float:
    return float(str(value)) if _is_float(value) else 0.0


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


def _ranks(values: list[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    index = 0
    while index < len(ordered):
        end = index
        while end + 1 < len(ordered) and ordered[end + 1][1] == ordered[index][1]:
            end += 1
        average_rank = (index + end + 2) / 2.0
        for item in range(index, end + 1):
            ranks[ordered[item][0]] = average_rank
        index = end + 1
    return ranks


def _spearman(x_values: list[float], y_values: list[float]) -> float | None:
    if len(x_values) != len(y_values) or len(x_values) < 2:
        return None
    return _pearson(_ranks(x_values), _ranks(y_values))


def _pearson(x_values: list[float], y_values: list[float]) -> float | None:
    if len(x_values) != len(y_values) or not x_values:
        return None
    x_mean = sum(x_values) / len(x_values)
    y_mean = sum(y_values) / len(y_values)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    x_var = sum((x - x_mean) ** 2 for x in x_values)
    y_var = sum((y - y_mean) ** 2 for y in y_values)
    if not x_var or not y_var:
        return None
    return numerator / (x_var**0.5 * y_var**0.5)


def _fmt(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.10f}"
    return str(value)

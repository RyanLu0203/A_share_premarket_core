from __future__ import annotations

from collections import Counter, defaultdict
from math import sqrt
from pathlib import Path
from statistics import median, pstdev

from ashare_premarket.backtest.goal10b3 import (
    GROUP_IMBALANCE_PATH as GOAL10B3_GROUP_IMBALANCE_PATH,
    RECOMMENDATION_METRICS_PATH as GOAL10B3_RECOMMENDATION_METRICS_PATH,
    WORKFLOW_ID as GOAL10B3_WORKFLOW_ID,
    goal10b3_valid_dc03_revalidation_evidence,
)
from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import (
    preserve_later_review_only_capabilities,
    preserve_later_review_only_workflow_states,
)
from ashare_premarket.diagnostics.goal_v1_diagnostic_coverage03 import (
    RISK_DIAGNOSTICS_PATH as DC03_RISK_PATH,
    SOURCE_PANEL as DC03_SOURCE_PANEL,
    goal_v1_diagnostic_coverage03_valid_source_backed_diagnostics_evidence,
)
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.providers.goal_data_provider02b import PANEL_FIELDS, PANEL_PATH as PROVIDER02B_PANEL_PATH
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-RISK-TIERING-01"
GOAL_NAME = "GOAL-RISK-TIERING-01-RISK-SEVERITY-AND-NUMERIC-SCORE-TIERING-GATE"
MODE = "review_only_risk_severity_numeric_score_tiering_gate"
WORKFLOW_ID = "goal_risk_tiering01_risk_severity_numeric_score_gate"
GOAL_REC_TIERING01_WORKFLOW_ID = "goal_rec_tiering01_recommendation_score_tiering_gate"
GOAL10B4_WORKFLOW_ID = "goal10b4_recommendation_backtest_revalidation"
POSITION_BAND_VALIDATION_WORKFLOW_ID = "goal_position_band_validation01_position_band_validation_gate"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
GOAL10C_WORKFLOW_ID = "goal10c_backtest_cost_slippage_sensitivity_gate"
ALLOWED_NEXT_WEAK = "repair_goal_risk_tiering01_rules_before_goal_rec_tiering01"
ALLOWED_NEXT_AVAILABLE = "request_goal_rec_tiering01_recommendation_score_tiering_gate"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

DIAGNOSTICS_PATH = "outputs/diagnostics/goal_risk_tiering01_risk_tiered_diagnostics.csv"
DISTRIBUTION_PATH = "outputs/diagnostics/goal_risk_tiering01_distribution_summary.csv"
FORWARD_METRICS_PATH = "outputs/backtest/goal_risk_tiering01_risk_tier_forward_return_metrics.csv"
REPORT_PATH = "outputs/audits/goal_risk_tiering01_risk_tiering_report.md"
MANIFEST_PATH = "outputs/audits/goal_risk_tiering01_risk_tiering_manifest.json"
AUDIT_PATH = "outputs/audits/goal_risk_tiering01_risk_tiering_audit.md"
DOC_PATH = "docs/risk/GOAL_RISK_TIERING01_RISK_SEVERITY_AND_NUMERIC_SCORE_TIERING_GATE.md"
CONTRACT_PATH = "configs/risk/goal_risk_tiering01_contract.yaml"

HORIZONS = ["1d", "5d", "20d"]
LOW_BUCKET = "LOW_RISK_REVIEW_ONLY"
MEDIUM_BUCKET = "MEDIUM_RISK_REVIEW_ONLY"
HIGH_BUCKET = "HIGH_RISK_REVIEW_ONLY"
INSUFFICIENT_BUCKET = "INSUFFICIENT_EVIDENCE_REVIEW_ONLY"
BUCKET_ORDER = [LOW_BUCKET, MEDIUM_BUCKET, HIGH_BUCKET, INSUFFICIENT_BUCKET]
LOW_MEDIUM_THRESHOLD = 35.0
MEDIUM_HIGH_THRESHOLD = 55.0
COLLAPSE_THRESHOLD = 0.95
MIN_BUCKET_ROWS = 30
NON_ACTIONABLE = "diagnostic_only_not_investment_advice_not_trade_instruction"

RISK_TIERED_FIELDS = [
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
    "original_dc03_medium_rows",
    "original_dc03_high_rows",
    "diagnostic_status",
    "notes",
]

FORWARD_METRIC_FIELDS = [
    "group_type",
    "risk_score_bucket",
    "risk_severity_tiered",
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
    "original_dc03_risk_severity",
    "dc03_risk_warning_codes",
    "dc03_provider_concentration_disclosure",
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
    "goal07b_outputs_overwritten",
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
    FORWARD_METRICS_PATH,
    "outputs/backtest/goal10c_position_band_input_snapshot.csv",
    "outputs/backtest/goal10c_cost_slippage_sensitivity.csv",
    "outputs/backtest/goal10c_position_band_group_metrics.csv",
}

WORKFLOW_PRODUCES_ARTIFACTS = ";".join(
    [
        DIAGNOSTICS_PATH,
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
WORKFLOW_PRIMARY_SCRIPTS = "scripts/run_goal_risk_tiering01_risk_severity_numeric_score_gate.py;scripts/audit_goal_risk_tiering01_risk_severity_numeric_score_gate.py"
WORKFLOW_PRIMARY_OUTPUTS = ";".join([DIAGNOSTICS_PATH, DISTRIBUTION_PATH, FORWARD_METRICS_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH])
WORKFLOW_NOTES = "Review-only GOAL-RISK-TIERING-01 numeric risk score and tier diagnostics over committed DC03 risk rows and GOAL-DATA-PROVIDER-02B panel evidence. The score uses governance/source-quality and current-or-trailing OHLCV rules only; forward returns are excluded from construction and used only for post-hoc evaluation. No recommendation, position, portfolio, dashboard, trading, production, broker, local-lake, factor-mining, or DQN/RL outputs."


def run_goal_risk_tiering01_risk_severity_numeric_score_gate(root: Path) -> bool:
    result = evaluate_goal_risk_tiering01_risk_severity_numeric_score_gate(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal_risk_tiering01_risk_severity_numeric_score_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal_risk_tiering01_risk_severity_numeric_score_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    diagnostics = _read_csv(root / DIAGNOSTICS_PATH)
    distribution = _read_csv(root / DISTRIBUTION_PATH)
    metrics = _read_csv(root / FORWARD_METRICS_PATH)
    workflow = _workflow_rows(root)
    recheck = evaluate_goal_risk_tiering01_risk_severity_numeric_score_gate(root)
    failures: list[str] = []

    if not _report_pass_or_warn(report):
        failures.append("goal_risk_tiering01_report_not_pass_or_warn")
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
        "review_only_risk_tiering_generated",
        "used_dc03_risk_diagnostics_only",
        "used_provider02b_source_backed_panel_only",
        "used_goal10b3_imbalance_evidence_only",
        "score_construction_excludes_future_returns",
        "future_returns_used_only_for_post_hoc_evaluation",
        "no_lookahead_score_construction_check",
        "source_backed_panel_linkage_check",
        "duplicate_key_check",
        "risk_bucket_variation_available",
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
    if len(diagnostics) != manifest.get("risk_tiered_row_count"):
        failures.append("diagnostic_row_count_mismatch")
    if not diagnostics or set(diagnostics[0]) != set(RISK_TIERED_FIELDS):
        failures.append("risk_tiered_fields_invalid")
    if not distribution or set(distribution[0]) != set(DISTRIBUTION_FIELDS):
        failures.append("distribution_fields_invalid")
    if not metrics or set(metrics[0]) != set(FORWARD_METRIC_FIELDS):
        failures.append("forward_metric_fields_invalid")
    represented = {row.get("risk_score_bucket", "") for row in diagnostics}
    if not {LOW_BUCKET, MEDIUM_BUCKET, HIGH_BUCKET}.issubset(represented):
        failures.append("low_medium_high_buckets_not_all_represented")
    if any(row.get("non_actionable_disclaimer", "") != NON_ACTIONABLE for row in diagnostics):
        failures.append("non_actionable_disclaimer_invalid")
    if any(_contains_forbidden_score_input(row.get("risk_tiering_rule_ids", "")) for row in diagnostics):
        failures.append("forbidden_score_input_in_rule_ids")
    if manifest.get("score_input_fields_do_not_include_future_return_labels") is not True:
        failures.append("score_input_fields_include_future_labels")
    if manifest.get("dominant_bucket_share", "1") == "" or float(str(manifest.get("dominant_bucket_share", "1"))) >= COLLAPSE_THRESHOLD:
        failures.append("dominant_bucket_share_collapsed")
    if not isinstance(manifest.get("minimum_bucket_size_warning"), bool):
        failures.append("minimum_bucket_size_warning_not_boolean")
    if manifest.get("original_dc03_risk_severity_distribution", {}).get("MEDIUM") != 5990:
        failures.append("original_dc03_medium_count_unexpected")
    if manifest.get("original_dc03_risk_severity_distribution", {}).get("HIGH") != 10:
        failures.append("original_dc03_high_count_unexpected")

    gate = workflow.get(WORKFLOW_ID, {})
    if gate.get("status") != "implemented_review_only":
        failures.append("goal_risk_tiering01_workflow_not_implemented_review_only")
    if gate.get("implemented_in_repo") != "true":
        failures.append("goal_risk_tiering01_workflow_not_marked_implemented")
    if gate.get("depends_on") != GOAL10B3_WORKFLOW_ID:
        failures.append("goal_risk_tiering01_depends_on_invalid")
    if gate.get("allowed_next_action") != manifest.get("allowed_next_action"):
        failures.append("goal_risk_tiering01_allowed_next_mismatch")
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
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))
    failures.extend(f"unexpected_backtest_output:{path}" for path in _unexpected_backtest_outputs(root))

    status = PASS if not failures else BLOCKED
    write_text(
        root / AUDIT_PATH,
        "\n".join(
            [
                "# GOAL-RISK-TIERING-01 Risk Tiering Audit",
                "",
                f"Status: `{status}`",
                "",
                f"GOAL-RISK-TIERING-01 workflow status: `{gate.get('status', 'missing')}`",
                f"Risk-tiered rows: `{len(diagnostics)}`",
                f"Risk score buckets: `{';'.join(sorted(represented))}`",
                f"Signal classification: `{manifest.get('signal_classification', 'missing')}`",
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


def evaluate_goal_risk_tiering01_risk_severity_numeric_score_gate(root: Path) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    workflow = _workflow_rows(root)
    risk_rows = _read_csv(root / DC03_RISK_PATH)
    panel_rows = _read_csv(root / PROVIDER02B_PANEL_PATH)
    imbalance_rows = _read_csv(root / GOAL10B3_GROUP_IMBALANCE_PATH)
    recommendation_metric_rows = _read_csv(root / GOAL10B3_RECOMMENDATION_METRICS_PATH)

    if not goal_v1_diagnostic_coverage03_valid_source_backed_diagnostics_evidence(root):
        failures.append("goal_v1_diagnostic_coverage03_evidence_not_ready")
    if not goal10b3_valid_dc03_revalidation_evidence(root):
        failures.append("goal10b3_revalidation_evidence_not_ready")
    goal10b3_row = workflow.get(GOAL10B3_WORKFLOW_ID, {})
    if goal10b3_row.get("status") != "implemented_review_only":
        failures.append("goal10b3_workflow_not_implemented_review_only")
    if goal10b3_row.get("implemented_in_repo") != "true":
        failures.append("goal10b3_workflow_not_marked_implemented")
    if not risk_rows:
        failures.append("dc03_risk_rows_missing")
    elif list(risk_rows[0]) != _dc03_risk_fields():
        failures.append("dc03_risk_schema_invalid")
    if any(row.get("source_panel") != DC03_SOURCE_PANEL for row in risk_rows):
        failures.append("dc03_risk_source_panel_invalid")
    if not panel_rows:
        failures.append("provider02b_panel_missing")
    elif list(panel_rows[0]) != PANEL_FIELDS:
        failures.append("provider02b_panel_schema_invalid")
    if not imbalance_rows:
        failures.append("goal10b3_group_imbalance_diagnostics_missing")
    if not recommendation_metric_rows:
        failures.append("goal10b3_recommendation_group_metrics_missing")
    failures.extend(_validate_forbidden_input_sources())
    failures.extend(_validate_score_input_contract())

    diagnostics = _risk_tiered_rows(risk_rows, panel_rows) if not failures else []
    duplicate_keys = _duplicate_key_count(diagnostics)
    if duplicate_keys:
        failures.append("duplicate_trade_date_symbol_keys_present")
    if diagnostics and _keys(diagnostics) != _keys(risk_rows):
        failures.append("risk_tiered_keys_do_not_match_dc03_risk")
    if diagnostics and _keys(diagnostics) != _keys(panel_rows):
        failures.append("risk_tiered_keys_do_not_match_provider02b_panel")
    if diagnostics and not {LOW_BUCKET, MEDIUM_BUCKET, HIGH_BUCKET}.issubset({row["risk_score_bucket"] for row in diagnostics}):
        warnings.append("risk_score_bucket_variation_incomplete")

    distribution = _distribution_rows(diagnostics, risk_rows)
    metrics = _forward_metric_rows(diagnostics, panel_rows)
    correlation_rows = _rank_correlation_rows(diagnostics, panel_rows)
    warnings.extend(_warning_codes_from_distribution(distribution))
    signal_classification = _signal_classification(diagnostics, distribution, correlation_rows)
    if signal_classification == "risk_tiering_signal_weak_or_unreliable":
        warnings.append("risk_tiering_signal_weak_or_unreliable")
    elif signal_classification == "risk_tiering_not_evaluable":
        warnings.append("risk_tiering_not_evaluable")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))
    failures.extend(f"unexpected_backtest_output:{path}" for path in _unexpected_backtest_outputs(root))

    status = BLOCKED if failures else PASS_WITH_WARNINGS if warnings else PASS
    manifest = _manifest(status, failures, warnings, diagnostics, distribution, metrics, correlation_rows, risk_rows)
    return {
        "status": status,
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "diagnostics": diagnostics,
        "distribution": distribution,
        "metrics": metrics,
        "correlations": correlation_rows,
        "manifest": manifest,
    }


def goal_risk_tiering01_valid_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        _report_pass_or_warn(report)
        and "Status: `PASS`" in audit
        and manifest.get("goal") == GOAL_NAME
        and manifest.get("mode") == MODE
        and manifest.get("review_only_risk_tiering_generated") is True
        and manifest.get("risk_tiered_row_count") == 6000
        and manifest.get("used_dc03_risk_diagnostics_only") is True
        and manifest.get("used_provider02b_source_backed_panel_only") is True
        and manifest.get("score_construction_excludes_future_returns") is True
        and manifest.get("future_returns_used_only_for_post_hoc_evaluation") is True
        and manifest.get("risk_bucket_variation_available") is True
        and manifest.get("goal_rec_tiering01_locked_future") is True
        and manifest.get("goal10b4_locked_future") is True
        and manifest.get("goal10d_locked_future") is True
        and manifest.get("dashboard_outputs_generated") is False
        and manifest.get("recommendation_outputs_created") is False
        and manifest.get("position_outputs_created") is False
        and manifest.get("portfolio_returns_generated") is False
        and manifest.get("future_returns_used_in_score") is False
    )


def goal_risk_tiering01_implemented_workflow_patch(status: str = PASS_WITH_WARNINGS) -> dict[str, str]:
    allowed = ALLOWED_NEXT_AVAILABLE if status == PASS else ALLOWED_NEXT_WEAK
    return {
        "display_name": "GOAL-RISK-TIERING-01 Risk Severity Numeric Score Tiering Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_review_only",
        "current_repo_role": MODE,
        "implemented_in_repo": "true",
        "allowed_next_action": allowed,
        "depends_on": GOAL10B3_WORKFLOW_ID,
        "produces_artifacts": WORKFLOW_PRODUCES_ARTIFACTS,
        "primary_docs": WORKFLOW_PRIMARY_DOCS,
        "primary_scripts": WORKFLOW_PRIMARY_SCRIPTS,
        "primary_outputs": WORKFLOW_PRIMARY_OUTPUTS,
        "promotion_rule": "implemented_review_only_after_goal_risk_tiering01_pass_with_warnings",
        "notes": WORKFLOW_NOTES,
    }


def locked_goal_rec_tiering01_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-REC-TIERING-01 Recommendation Score Tiering Gate",
        "stage_or_goal": "GOAL-REC-TIERING-01",
        "status": "locked_future",
        "current_repo_role": "locked_future_recommendation_score_tiering_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal_risk_tiering01_signal_ready",
        "depends_on": WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal_rec_tiering01_gate",
        "notes": "Future recommendation score tiering remains locked; GOAL-RISK-TIERING-01 creates risk diagnostics only and no recommendation rows.",
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
        "notes": "Future GOAL-10B.4 remains locked; GOAL-RISK-TIERING-01 creates no recommendation revalidation rows.",
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
        "notes": "Future position-band validation remains locked; GOAL-RISK-TIERING-01 creates no position outputs.",
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
        "notes": "Future GOAL-10D failure attribution remains locked; GOAL-RISK-TIERING-01 creates only review-only risk tier diagnostics.",
    }


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / DIAGNOSTICS_PATH, result["diagnostics"], RISK_TIERED_FIELDS)
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
        "primary_inputs": [DC03_RISK_PATH, PROVIDER02B_PANEL_PATH, GOAL10B3_GROUP_IMBALANCE_PATH, GOAL10B3_RECOMMENDATION_METRICS_PATH],
        "forbidden_primary_inputs": [
            "outputs/samples/*",
            "demo fixtures",
            "GOAL-07B canonical risk overlay outputs as writable targets",
            "GOAL-08B recommendation rows",
            "GOAL-09 position-band rows",
            "future return labels for score construction",
        ],
        "score_input_fields": SCORE_INPUT_FIELDS,
        "forbidden_score_input_fields": FORBIDDEN_SCORE_INPUT_FIELDS,
        "score_thresholds": {
            LOW_BUCKET: f"< {LOW_MEDIUM_THRESHOLD}",
            MEDIUM_BUCKET: f">= {LOW_MEDIUM_THRESHOLD} and < {MEDIUM_HIGH_THRESHOLD}",
            HIGH_BUCKET: f">= {MEDIUM_HIGH_THRESHOLD}",
            INSUFFICIENT_BUCKET: "critical source evidence missing",
        },
        "risk_tiered_schema": RISK_TIERED_FIELDS,
        "distribution_schema": DISTRIBUTION_FIELDS,
        "post_hoc_forward_metric_schema": FORWARD_METRIC_FIELDS,
        "allowed_outputs": [DIAGNOSTICS_PATH, DISTRIBUTION_PATH, FORWARD_METRICS_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH, CONTRACT_PATH],
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
                "# GOAL-RISK-TIERING-01 Risk Severity Numeric Score Tiering Gate",
                "",
                f"GOAL-RISK-TIERING-01 Risk Severity Numeric Score Tiering Gate: {result['status']}",
                f"Mode: `{MODE}`",
                "",
                "## Tiering Scope",
                f"- Risk-tiered rows: `{manifest['risk_tiered_row_count']}`",
                f"- Unique symbols: `{manifest['unique_symbols']}`",
                f"- Unique trade dates: `{manifest['unique_trade_dates']}`",
                f"- Risk score bucket distribution: `{manifest['risk_score_bucket_distribution']}`",
                f"- Original DC03 risk severity distribution: `{manifest['original_dc03_risk_severity_distribution']}`",
                f"- Dominant bucket share: `{manifest['dominant_bucket_share']}`",
                f"- Signal classification: `{manifest['signal_classification']}`",
                f"- Recommended next action: `{manifest['recommended_next_goal']}`",
                "",
                "## No-Lookahead Boundary",
                "- Numeric risk score construction excludes all `forward_return_*`, `benchmark_excess_return_*`, and `label_ready_*` fields.",
                "- Forward returns are used only for post-hoc group evaluation metrics after the deterministic risk buckets are assigned.",
                "- Score weights are deterministic governance rules and are not tuned to maximize forward returns.",
                "",
                "## Locked Boundary",
                "- Canonical GOAL-07B and DC03 risk diagnostics are not overwritten.",
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
                "# GOAL-RISK-TIERING-01 Risk Severity And Numeric Score Tiering Gate",
                "",
                f"Status: `{result['status']}`",
                "",
                "GOAL-RISK-TIERING-01 is a review-only risk severity tiering gate over committed GOAL-V1-DIAGNOSTIC-COVERAGE-03 risk rows and the GOAL-DATA-PROVIDER-02B source-backed evaluation panel. It creates a separate non-actionable risk-tiering artifact and does not overwrite canonical GOAL-07B or DC03 risk diagnostics.",
                "",
                "## Inputs",
                "",
                f"- `{DC03_RISK_PATH}`",
                f"- `{PROVIDER02B_PANEL_PATH}`",
                f"- `{GOAL10B3_GROUP_IMBALANCE_PATH}`",
                f"- `{GOAL10B3_RECOMMENDATION_METRICS_PATH}`",
                "",
                "## Outputs",
                "",
                f"- `{DIAGNOSTICS_PATH}`",
                f"- `{DISTRIBUTION_PATH}`",
                f"- `{FORWARD_METRICS_PATH}`",
                f"- `{REPORT_PATH}`",
                f"- `{MANIFEST_PATH}`",
                f"- `{AUDIT_PATH}`",
                f"- `{CONTRACT_PATH}`",
                "",
                "## Score Construction",
                "",
                "The numeric risk score is deterministic and governance-first. It uses DC03 risk severity, source quality warnings, trading status, ST status, missing OHLCV/amount/turnover checks, liquidity proxies, crosscheck/provider concentration warnings, current 1d move magnitude, trailing 5d/20d return magnitude from prior/current panel closes, and a trailing volatility proxy from prior/current `pct_chg` values.",
                "",
                "The score does not use `forward_return_*`, `benchmark_excess_return_*`, or `label_ready_*` fields. Those fields are used only in the post-hoc forward-return metric output.",
                "",
                "## Result",
                "",
                f"- Risk-tiered rows: `{manifest['risk_tiered_row_count']}`",
                f"- Bucket distribution: `{manifest['risk_score_bucket_distribution']}`",
                f"- Dominant bucket share: `{manifest['dominant_bucket_share']}`",
                f"- Minimum bucket size warning: `{str(manifest['minimum_bucket_size_warning']).lower()}`",
                f"- Collapse detected: `{str(manifest['risk_bucket_collapse_detected']).lower()}`",
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
    distribution: list[dict[str, object]],
    metrics: list[dict[str, object]],
    correlations: list[dict[str, object]],
    risk_rows: list[dict[str, str]],
) -> dict[str, object]:
    symbols = sorted({str(row.get("symbol", "")) for row in diagnostics if row.get("symbol", "")})
    dates = sorted({str(row.get("trade_date", "")) for row in diagnostics if row.get("trade_date", "")})
    bucket_distribution = dict(Counter(str(row.get("risk_score_bucket", "")) for row in diagnostics))
    original_distribution = dict(Counter(str(row.get("risk_severity", "")) for row in risk_rows))
    dominant_bucket_share = _dominant_share(bucket_distribution)
    represented_bucket_counts = [count for bucket, count in bucket_distribution.items() if bucket != INSUFFICIENT_BUCKET or count > 0]
    minimum_bucket_size_warning = any(0 < count < MIN_BUCKET_ROWS for count in represented_bucket_counts)
    collapse = len([bucket for bucket, count in bucket_distribution.items() if count > 0]) < 2 or dominant_bucket_share >= COLLAPSE_THRESHOLD
    signal_classification = _signal_classification(diagnostics, distribution, correlations)
    allowed_next = ALLOWED_NEXT_AVAILABLE if signal_classification == "risk_tiering_signal_available" and not minimum_bucket_size_warning and not collapse else ALLOWED_NEXT_WEAK
    recommended_next = (
        "GOAL-REC-TIERING-01"
        if allowed_next == ALLOWED_NEXT_AVAILABLE
        else "adjust_deterministic_governance_risk_rules_before_goal_rec_tiering01"
    )
    payload: dict[str, object] = {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "status": status,
        "mode": MODE,
        "allowed_next_action": allowed_next if status != BLOCKED else "repair_goal_risk_tiering01_blockers",
        "signal_classification": signal_classification,
        "recommended_next_goal": recommended_next,
        "primary_input_artifacts": [DC03_RISK_PATH, PROVIDER02B_PANEL_PATH, GOAL10B3_GROUP_IMBALANCE_PATH, GOAL10B3_RECOMMENDATION_METRICS_PATH],
        "forbidden_primary_inputs_used": [],
        "risk_tiered_row_count": len(diagnostics),
        "distribution_summary_rows": len(distribution),
        "forward_metric_rows": len(metrics),
        "unique_symbols": len(symbols),
        "symbols": symbols,
        "unique_trade_dates": len(dates),
        "date_min": dates[0] if dates else "",
        "date_max": dates[-1] if dates else "",
        "risk_score_bucket_distribution": bucket_distribution,
        "risk_score_bucket_count": len([count for count in bucket_distribution.values() if count > 0]),
        "dominant_bucket_share": _fmt(dominant_bucket_share),
        "minimum_bucket_size_warning": minimum_bucket_size_warning,
        "risk_bucket_collapse_detected": collapse,
        "original_dc03_risk_severity_distribution": original_distribution,
        "original_dc03_medium_rows": original_distribution.get("MEDIUM", 0),
        "original_dc03_high_rows": original_distribution.get("HIGH", 0),
        "rank_correlation_rows": correlations,
        "rank_correlation_available": any(row.get("correlation_status") == "available" for row in correlations),
        "review_only_risk_tiering_generated": status != BLOCKED,
        "used_dc03_risk_diagnostics_only": True,
        "used_provider02b_source_backed_panel_only": True,
        "used_goal10b3_imbalance_evidence_only": True,
        "source_backed_panel_linkage_check": bool(diagnostics),
        "duplicate_trade_date_symbol_keys": _duplicate_key_count(diagnostics),
        "duplicate_key_check": _duplicate_key_count(diagnostics) == 0,
        "risk_bucket_variation_available": len([count for count in bucket_distribution.values() if count > 0]) >= 3,
        "score_input_fields": SCORE_INPUT_FIELDS,
        "forbidden_score_input_fields": FORBIDDEN_SCORE_INPUT_FIELDS,
        "score_input_fields_do_not_include_future_return_labels": _score_fields_exclude_future_returns(),
        "score_construction_excludes_future_returns": True,
        "future_returns_used_only_for_post_hoc_evaluation": True,
        "no_lookahead_score_construction_check": True,
        "score_weights_tuning_policy": "deterministic_governance_rules_not_tuned_to_forward_returns",
        "review_only_non_actionable_boundary_preserved": True,
        "goal_risk_tiering01_workflow_status_after_goal": "implemented_review_only" if status != BLOCKED else "locked_future",
        "goal_rec_tiering01_status_after_goal_risk_tiering01": "locked_future",
        "goal10b4_status_after_goal_risk_tiering01": "locked_future",
        "position_band_validation_status_after_goal_risk_tiering01": "locked_future",
        "goal10d_status_after_goal_risk_tiering01": "locked_future",
        "dashboard_daily_report_status_after_goal_risk_tiering01": "locked_future",
        "portfolio_backtest_status_after_goal_risk_tiering01": "locked_future",
        "goal_rec_tiering01_locked_future": True,
        "goal10b4_locked_future": True,
        "position_band_validation_locked_future": True,
        "goal10d_locked_future": True,
        "dashboard_daily_report_locked_future": True,
        "portfolio_backtest_locked_future": True,
        "output_artifacts": [DIAGNOSTICS_PATH, DISTRIBUTION_PATH, FORWARD_METRICS_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH, CONTRACT_PATH],
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        **{key: False for key in FALSE_BOUNDARY_KEYS},
    }
    return payload


def _risk_tiered_rows(risk_rows: list[dict[str, str]], panel_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    panel_by_key = {(row.get("trade_date", ""), row.get("symbol", "")): row for row in panel_rows}
    trailing_features = _trailing_feature_map(panel_rows)
    provider_counts = Counter(row.get("source_provider", "") for row in panel_rows)
    output: list[dict[str, object]] = []
    for risk in sorted(risk_rows, key=lambda item: (item.get("trade_date", ""), item.get("symbol", ""))):
        key = (risk.get("trade_date", ""), risk.get("symbol", ""))
        panel = panel_by_key.get(key, {})
        score, rules, warnings, insufficient = _risk_score(risk, panel, trailing_features.get(key, {}), provider_counts)
        bucket = INSUFFICIENT_BUCKET if insufficient else _bucket(score)
        output.append(
            {
                "trade_date": risk.get("trade_date", ""),
                "symbol": risk.get("symbol", ""),
                "source_panel": PROVIDER02B_PANEL_PATH,
                "risk_score_numeric": _fmt(score),
                "risk_score_bucket": bucket,
                "risk_severity_tiered": bucket,
                "original_dc03_risk_severity": risk.get("risk_severity", ""),
                "risk_tiering_rule_ids": ";".join(rules),
                "risk_tiering_warning_codes": ";".join(sorted(set(warnings))),
                "source_provider": panel.get("source_provider", ""),
                "universe_mode": panel.get("universe_mode", ""),
                "diagnostic_mode": MODE,
                "non_actionable_disclaimer": NON_ACTIONABLE,
            }
        )
    return output


def _risk_score(risk: dict[str, str], panel: dict[str, str], features: dict[str, object], provider_counts: Counter[str]) -> tuple[float, list[str], list[str], bool]:
    score = 0.0
    rules: list[str] = []
    warnings: list[str] = ["future_return_labels_excluded_from_score", "review_only_non_actionable_risk_tiering"]
    insufficient = False
    warning_text = ";".join(
        [
            risk.get("risk_warning_codes", ""),
            risk.get("provider_concentration_disclosure", ""),
            panel.get("source_warning_codes", ""),
            panel.get("crosscheck_status", ""),
        ]
    ).lower()

    if risk.get("risk_severity") == "HIGH":
        score += 40
        rules.append("DC03_HIGH_RISK_SEVERITY")
    elif risk.get("risk_severity") == "MEDIUM":
        score += 8
        rules.append("DC03_MEDIUM_RISK_SEVERITY")

    if panel.get("trading_status") and panel.get("trading_status") != "trading":
        score += 45
        rules.append("NON_TRADING_ROW")
        warnings.append("non_trading_row")
    if panel.get("is_st") == "true":
        score += 35
        rules.append("ST_STATUS")
        warnings.append("st_status")
    if any(not _is_float(panel.get(field, "")) for field in ["open", "high", "low", "close", "pre_close"]):
        score += 20
        rules.append("MISSING_OHLCV")
        warnings.append("missing_ohlcv")
        insufficient = True
    if not _is_float(panel.get("amount", "")) or float(str(panel.get("amount", "0") or "0")) <= 0:
        score += 18
        rules.append("MISSING_AMOUNT")
        warnings.append("missing_amount")
        insufficient = True
    elif float(str(panel.get("amount"))) < 150_000_000:
        score += 4
        rules.append("LOW_AMOUNT_LIQUIDITY_PROXY")
    if not _is_float(panel.get("turnover", "")):
        score += 18
        rules.append("MISSING_TURNOVER")
        warnings.append("missing_turnover")
        insufficient = True
    elif float(str(panel.get("turnover"))) < 0.25:
        score += 3
        rules.append("LOW_TURNOVER_LIQUIDITY_PROXY")

    if "canonical_approved_universe_below_50" in warning_text:
        score += 5
        rules.append("CANONICAL_APPROVED_UNIVERSE_WARNING")
        warnings.append("canonical_approved_universe_warning")
    if "crosscheck_sample_scope_limited" in warning_text or panel.get("crosscheck_status") != "checked_close_diff_within_tolerance":
        score += 8
        rules.append("CROSSCHECK_LIMITED_OR_UNAVAILABLE")
        warnings.append("crosscheck_limited_or_unavailable")
    if panel.get("source_provider") and provider_counts.get(panel.get("source_provider", ""), 0) == sum(provider_counts.values()):
        score += 6
        rules.append("SINGLE_PRIMARY_PROVIDER_CONCENTRATION")
        warnings.append("single_primary_provider_concentration")
    if panel.get("universe_mode") == "provider_panel_candidate_universe_review_only":
        score += 4
        rules.append("REVIEW_ONLY_SOURCE_PANEL_WARNING")
        warnings.append("review_only_source_panel_warning")

    if _is_float(panel.get("pct_chg", "")):
        abs_1d = abs(float(str(panel.get("pct_chg"))))
        if abs_1d >= 9.5:
            score += 18
            rules.append("ABNORMAL_1D_RETURN_MAGNITUDE_EXTREME")
        elif abs_1d >= 5.0:
            score += 10
            rules.append("ABNORMAL_1D_RETURN_MAGNITUDE_HIGH")
        elif abs_1d >= 3.0:
            score += 5
            rules.append("ABNORMAL_1D_RETURN_MAGNITUDE_MODERATE")
    else:
        warnings.append("missing_current_pct_chg")

    trailing_5d = features.get("trailing_return_5d")
    if isinstance(trailing_5d, float):
        abs_5d = abs(trailing_5d)
        if abs_5d >= 0.15:
            score += 14
            rules.append("ABNORMAL_TRAILING_5D_RETURN_MAGNITUDE_HIGH")
        elif abs_5d >= 0.08:
            score += 8
            rules.append("ABNORMAL_TRAILING_5D_RETURN_MAGNITUDE_MODERATE")
        elif abs_5d >= 0.04:
            score += 4
            rules.append("ABNORMAL_TRAILING_5D_RETURN_MAGNITUDE_LOW")
    else:
        score += 2
        rules.append("TRAILING_5D_HISTORY_LIMITED")
        warnings.append("trailing_5d_history_limited")

    trailing_20d = features.get("trailing_return_20d")
    if isinstance(trailing_20d, float):
        abs_20d = abs(trailing_20d)
        if abs_20d >= 0.30:
            score += 16
            rules.append("ABNORMAL_TRAILING_20D_RETURN_MAGNITUDE_HIGH")
        elif abs_20d >= 0.18:
            score += 10
            rules.append("ABNORMAL_TRAILING_20D_RETURN_MAGNITUDE_MODERATE")
        elif abs_20d >= 0.10:
            score += 5
            rules.append("ABNORMAL_TRAILING_20D_RETURN_MAGNITUDE_LOW")
    else:
        score += 2
        rules.append("TRAILING_20D_HISTORY_LIMITED")
        warnings.append("trailing_20d_history_limited")

    volatility = features.get("trailing_volatility_proxy")
    if isinstance(volatility, float):
        if volatility >= 4.0:
            score += 10
            rules.append("TRAILING_VOLATILITY_PROXY_HIGH")
        elif volatility >= 2.5:
            score += 5
            rules.append("TRAILING_VOLATILITY_PROXY_MODERATE")
    else:
        score += 2
        rules.append("VOLATILITY_HISTORY_LIMITED")
        warnings.append("volatility_history_limited")

    if not rules:
        rules.append("NO_RISK_RULE_TRIGGERED")
    return min(score, 100.0), rules, warnings, insufficient


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
            volatility = None
            if close is not None and index >= 5:
                previous = _float_or_none(ordered[index - 5].get("close", ""))
                if previous:
                    trailing_5d = close / previous - 1.0
            if close is not None and index >= 20:
                previous = _float_or_none(ordered[index - 20].get("close", ""))
                if previous:
                    trailing_20d = close / previous - 1.0
            pct_values = [
                _float_or_none(ordered[item].get("pct_chg", ""))
                for item in range(max(0, index - 19), index + 1)
            ]
            pct_materialized = [value for value in pct_values if value is not None]
            if len(pct_materialized) >= 5:
                volatility = pstdev(pct_materialized)
            output[(row.get("trade_date", ""), symbol)] = {
                "trailing_return_5d": trailing_5d,
                "trailing_return_20d": trailing_20d,
                "trailing_volatility_proxy": volatility,
            }
    return output


def _distribution_rows(diagnostics: list[dict[str, object]], risk_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    total = len(diagnostics)
    bucket_counts = Counter(str(row.get("risk_score_bucket", "")) for row in diagnostics)
    original_counts = Counter(str(row.get("risk_severity", "")) for row in risk_rows)
    dominant = _dominant_share(dict(bucket_counts))
    represented_counts = [count for bucket, count in bucket_counts.items() if bucket != INSUFFICIENT_BUCKET or count > 0]
    min_warning = any(0 < count < MIN_BUCKET_ROWS for count in represented_counts)
    collapse = len([count for count in bucket_counts.values() if count > 0]) < 2 or dominant >= COLLAPSE_THRESHOLD
    rows: list[dict[str, object]] = []
    for bucket in BUCKET_ORDER:
        group = [row for row in diagnostics if row.get("risk_score_bucket") == bucket]
        count = len(group)
        rows.append(
            _distribution_row(
                "risk_score_bucket_distribution",
                "risk_score_bucket",
                bucket,
                count,
                _share(count, total),
                len({row.get("symbol", "") for row in group}),
                len({row.get("trade_date", "") for row in group}),
                dominant,
                0 < count < MIN_BUCKET_ROWS,
                collapse,
                original_counts.get("MEDIUM", 0),
                original_counts.get("HIGH", 0),
                PASS_WITH_WARNINGS if (0 < count < MIN_BUCKET_ROWS or collapse) else PASS,
                "Risk score bucket row count and share.",
            )
        )
    for severity in sorted(original_counts):
        count = original_counts[severity]
        rows.append(
            _distribution_row(
                "original_dc03_risk_severity_distribution",
                "original_dc03_risk_severity",
                severity,
                count,
                _share(count, len(risk_rows)),
                len({row.get("symbol", "") for row in risk_rows if row.get("risk_severity") == severity}),
                len({row.get("trade_date", "") for row in risk_rows if row.get("risk_severity") == severity}),
                dominant,
                min_warning,
                collapse,
                original_counts.get("MEDIUM", 0),
                original_counts.get("HIGH", 0),
                PASS,
                "Original DC03 risk severity distribution for comparison.",
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
            original_counts.get("MEDIUM", 0),
            original_counts.get("HIGH", 0),
            PASS_WITH_WARNINGS if collapse else PASS,
            "Dominant risk score bucket share compared with collapse threshold.",
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
            original_counts.get("MEDIUM", 0),
            original_counts.get("HIGH", 0),
            PASS_WITH_WARNINGS if min_warning else PASS,
            "Warns when any represented risk score bucket has fewer than 30 rows.",
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
    original_medium: int,
    original_high: int,
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
        "original_dc03_medium_rows": original_medium,
        "original_dc03_high_rows": original_high,
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
        group = [row for row in joined if row.get("risk_score_bucket") == bucket]
        if not group:
            continue
        metric: dict[str, object] = {
            "group_type": "risk_score_bucket",
            "risk_score_bucket": bucket,
            "risk_severity_tiered": bucket,
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
        (str(row.get("trade_date", "")), str(row.get("symbol", ""))): float(str(row.get("risk_score_numeric", "0") or "0"))
        for row in diagnostics
        if _is_float(row.get("risk_score_numeric", ""))
    }
    rows: list[dict[str, object]] = []
    for field in [
        "forward_return_1d",
        "forward_return_5d",
        "forward_return_20d",
        "benchmark_excess_return_1d",
        "benchmark_excess_return_5d",
        "benchmark_excess_return_20d",
    ]:
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


def _signal_classification(diagnostics: list[dict[str, object]], distribution: list[dict[str, object]], correlations: list[dict[str, object]]) -> str:
    if not diagnostics or not correlations:
        return "risk_tiering_not_evaluable"
    collapse = any(str(row.get("collapse_detected", "")) == "true" for row in distribution)
    min_warning = any(str(row.get("minimum_bucket_size_warning", "")) == "true" for row in distribution)
    available = [row for row in correlations if row.get("correlation_status") == "available" and _is_float(row.get("absolute_rank_correlation", ""))]
    if not available:
        return "risk_tiering_not_evaluable"
    max_abs = max(float(str(row.get("absolute_rank_correlation"))) for row in available)
    if not collapse and not min_warning and max_abs >= 0.08:
        return "risk_tiering_signal_available"
    return "risk_tiering_signal_weak_or_unreliable"


def _warning_codes_from_distribution(rows: list[dict[str, object]]) -> list[str]:
    warnings: list[str] = []
    for row in rows:
        if row.get("diagnostic_status") == PASS_WITH_WARNINGS:
            warnings.append(str(row.get("distribution_name", "")))
    return sorted(set(warnings))


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys()) if rows else []
    by_id = {row["workflow_id"]: row for row in rows}
    manifest = result["manifest"]
    patch = goal_risk_tiering01_implemented_workflow_patch(str(result["status"]))
    if result["status"] == BLOCKED:
        patch.update(
            {
                "status": "locked_future",
                "current_repo_role": "review_only_risk_tiering_blocked",
                "implemented_in_repo": "false",
                "allowed_next_action": "repair_goal_risk_tiering01_blockers",
                "produces_artifacts": "",
                "primary_scripts": "",
                "primary_outputs": "",
                "promotion_rule": "locked_until_goal_risk_tiering01_passes",
                "notes": "GOAL-RISK-TIERING-01 is blocked; GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, and downstream execution remain locked.",
            }
        )
    else:
        patch["allowed_next_action"] = str(manifest.get("allowed_next_action", ALLOWED_NEXT_WEAK))
    _upsert_workflow_row(rows, by_id, WORKFLOW_ID, patch, after=GOAL10B3_WORKFLOW_ID)
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
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_risk_tiering01"
    if "dqn_rl_mainline" in by_id:
        by_id["dqn_rl_mainline"]["status"] = "deleted_from_active_mainline"
        by_id["dqn_rl_mainline"]["implemented_in_repo"] = "false"
    if "v2_factor_research_upgrade" in by_id:
        by_id["v2_factor_research_upgrade"]["status"] = "planned_locked"
        by_id["v2_factor_research_upgrade"]["implemented_in_repo"] = "false"
    preserve_later_review_only_workflow_states(root, by_id)
    if result["status"] != BLOCKED and WORKFLOW_ID in by_id:
        by_id[WORKFLOW_ID].update(goal_risk_tiering01_implemented_workflow_patch(str(result["status"])))
        by_id[WORKFLOW_ID]["allowed_next_action"] = str(manifest.get("allowed_next_action", ALLOWED_NEXT_WEAK))
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


def _dc03_risk_fields() -> list[str]:
    return [
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


def _validate_forbidden_input_sources() -> list[str]:
    forbidden = ["outputs/samples/", "demo", "fixture", "goal_v1_diagnostic_coverage02"]
    sources = [DC03_RISK_PATH, PROVIDER02B_PANEL_PATH, GOAL10B3_GROUP_IMBALANCE_PATH, GOAL10B3_RECOMMENDATION_METRICS_PATH]
    return [f"forbidden_primary_input:{source}" for source in sources if any(marker in source.lower() for marker in forbidden)]


def _validate_score_input_contract() -> list[str]:
    failures: list[str] = []
    if not _score_fields_exclude_future_returns():
        failures.append("score_input_fields_include_future_returns")
    return failures


def _score_fields_exclude_future_returns() -> bool:
    lowered = {field.lower() for field in SCORE_INPUT_FIELDS}
    return not any(field.lower() in lowered for field in FORBIDDEN_SCORE_INPUT_FIELDS) and not any("forward_return" in field or "benchmark_excess_return" in field or "label_ready" in field for field in lowered)


def _contains_forbidden_score_input(text: object) -> bool:
    lowered = str(text).lower()
    return any(field.lower() in lowered for field in FORBIDDEN_SCORE_INPUT_FIELDS)


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
        str(item.relative_to(root))
        for item in path.glob("*")
        if item.is_file() and str(item.relative_to(root)) not in ALLOWED_BACKTEST_OUTPUTS
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
    return "GOAL-RISK-TIERING-01 Risk Severity Numeric Score Tiering Gate: PASS" in report or "GOAL-RISK-TIERING-01 Risk Severity Numeric Score Tiering Gate: PASS_WITH_WARNINGS" in report


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
    return numerator / sqrt(x_var * y_var)


def _fmt(value: float | int | None) -> str:
    if value is None:
        return ""
    return f"{float(value):.10f}"

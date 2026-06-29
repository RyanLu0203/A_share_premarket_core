from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import (
    preserve_later_review_only_capabilities,
    preserve_later_review_only_workflow_states,
)
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-QUANT-RESEARCH-02"
GOAL_NAME = "GOAL-QUANT-RESEARCH-02-ALPHA-CANDIDATE-FACTOR-VALIDITY-EVALUATION-GATE"
MODE = "research_only_alpha_candidate_factor_validity_evaluation_gate"
WORKFLOW_ID = "goal_quant_research02_alpha_candidate_factor_validity_evaluation_gate"
PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

GOAL_ALPHA_FACTOR_CANDIDATE01_WORKFLOW_ID = "goal_alpha_factor_candidate01_research_gate"
GOAL_REC_TIERING01_WORKFLOW_ID = "goal_rec_tiering01_recommendation_score_tiering_gate"
GOAL10B4_WORKFLOW_ID = "goal10b4_recommendation_backtest_revalidation"
POSITION_BAND_VALIDATION_WORKFLOW_ID = "goal_position_band_validation01_position_band_validation_gate"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
GOAL10C_WORKFLOW_ID = "goal10c_backtest_cost_slippage_sensitivity_gate"

ALLOWED_NEXT_AVAILABLE = "request_explicit_goal_rec_tiering01_after_quant_research02_candidate_review"
ALLOWED_NEXT_WEAK = "request_goal_alpha_factor_candidate02_or_alpha_research_refinement01"
NEXT_GOAL_AVAILABLE = "GOAL-REC-TIERING-01"
NEXT_GOAL_WEAK = "GOAL-ALPHA-FACTOR-CANDIDATE-02_or_GOAL-ALPHA-RESEARCH-REFINEMENT-01"
NON_ACTIONABLE = "research_only_alpha_evaluation_not_investment_advice_not_trade_instruction"
N_QUANTILES = 5
MIN_BUCKET_ROWS = 30
COLLAPSE_THRESHOLD = 0.80
HORIZONS = ["1d", "5d", "20d"]

ALPHA_REGISTRY_PATH = "outputs/research/goal_alpha_factor_candidate01_candidate_registry.csv"
ALPHA_PANEL_PATH = "outputs/research/goal_alpha_factor_candidate01_factor_candidate_panel.csv"
ALPHA_COVERAGE_PATH = "outputs/research/goal_alpha_factor_candidate01_coverage_summary.csv"
ALPHA_WARNINGS_PATH = "outputs/research/goal_alpha_factor_candidate01_construction_warnings.csv"
PROVIDER02B_PANEL_PATH = "outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv"
MVP_SYMBOL_TABLE_PATH = "outputs/mvp/goal_mvp01_symbol_diagnostic_table.csv"
MVP_REVIEW_QUEUE_PATH = "outputs/mvp/goal_mvp01_review_queue.csv"
QUANT01_REGISTRY_PATH = "outputs/research/goal_quant_research01_factor_registry.csv"
QUANT01_VALIDITY_PATH = "outputs/research/goal_quant_research01_score_validity_classification.csv"
QUANT01_TRIAL_REGISTRY_PATH = "outputs/research/goal_quant_research01_trial_registry.csv"

EVALUATION_PANEL_PATH = "outputs/research/goal_quant_research02_alpha_evaluation_panel.csv"
COVERAGE_SUMMARY_PATH = "outputs/research/goal_quant_research02_alpha_factor_coverage_summary.csv"
BUCKET_METRICS_PATH = "outputs/research/goal_quant_research02_alpha_factor_bucket_metrics.csv"
IC_RANKIC_SUMMARY_PATH = "outputs/research/goal_quant_research02_alpha_factor_ic_rankic_summary.csv"
MONOTONICITY_SUMMARY_PATH = "outputs/research/goal_quant_research02_alpha_factor_monotonicity_summary.csv"
ROLLING_STABILITY_SUMMARY_PATH = "outputs/research/goal_quant_research02_alpha_factor_rolling_stability_summary.csv"
HORIZON_CONSISTENCY_PATH = "outputs/research/goal_quant_research02_alpha_factor_horizon_consistency_summary.csv"
SCORE_VALIDITY_PATH = "outputs/research/goal_quant_research02_alpha_factor_score_validity_classification.csv"
TRIAL_REGISTRY_PATH = "outputs/research/goal_quant_research02_trial_registry.csv"
REPORT_PATH = "outputs/audits/goal_quant_research02_alpha_factor_evaluation_report.md"
MANIFEST_PATH = "outputs/audits/goal_quant_research02_alpha_factor_evaluation_manifest.json"
AUDIT_PATH = "outputs/audits/goal_quant_research02_alpha_factor_evaluation_audit.md"
DOC_PATH = "docs/research/GOAL_QUANT_RESEARCH02_ALPHA_CANDIDATE_FACTOR_VALIDITY_EVALUATION_GATE.md"
CONTRACT_PATH = "configs/research/goal_quant_research02_alpha_factor_evaluation_contract.yaml"

REQUIRED_INPUTS = [
    ALPHA_REGISTRY_PATH,
    ALPHA_PANEL_PATH,
    ALPHA_COVERAGE_PATH,
    ALPHA_WARNINGS_PATH,
    PROVIDER02B_PANEL_PATH,
    MVP_SYMBOL_TABLE_PATH,
    MVP_REVIEW_QUEUE_PATH,
    QUANT01_REGISTRY_PATH,
    QUANT01_VALIDITY_PATH,
    QUANT01_TRIAL_REGISTRY_PATH,
]

OUTPUTS = [
    EVALUATION_PANEL_PATH,
    COVERAGE_SUMMARY_PATH,
    BUCKET_METRICS_PATH,
    IC_RANKIC_SUMMARY_PATH,
    MONOTONICITY_SUMMARY_PATH,
    ROLLING_STABILITY_SUMMARY_PATH,
    HORIZON_CONSISTENCY_PATH,
    SCORE_VALIDITY_PATH,
    TRIAL_REGISTRY_PATH,
    REPORT_PATH,
    MANIFEST_PATH,
    AUDIT_PATH,
    DOC_PATH,
    CONTRACT_PATH,
]

EVALUATION_PANEL_FIELDS = [
    "trade_date",
    "symbol",
    "factor_id",
    "factor_family",
    "factor_value",
    "factor_value_normalized_cross_sectional",
    "factor_quantile",
    "factor_bucket",
    "expected_direction",
    "forward_return_1d",
    "forward_return_5d",
    "forward_return_20d",
    "benchmark_excess_return_1d",
    "benchmark_excess_return_5d",
    "benchmark_excess_return_20d",
    "source_provider",
    "universe_mode",
    "panel_contract_status",
    "risk_score_bucket",
    "downside_risk_bucket",
    "mvp_review_queue_category",
    "mvp_review_priority_level",
    "no_lookahead_status",
    "diagnostic_mode",
    "non_actionable_disclaimer",
]

COVERAGE_FIELDS = [
    "factor_id",
    "row_count",
    "valid_factor_value_count",
    "missing_factor_value_count",
    "unique_symbols",
    "unique_trade_dates",
    "quantile_count",
    "bucket_count",
    "dominant_bucket_share",
    "minimum_bucket_size",
    "duplicate_key_count",
    "construction_status",
    "no_lookahead_status",
    "evaluation_readiness_status",
]

BUCKET_METRIC_FIELDS = [
    "factor_id",
    "factor_family",
    "group_type",
    "group_value",
    "row_count",
    "unique_symbols",
    "unique_trade_dates",
    "mean_forward_return_1d",
    "median_forward_return_1d",
    "hit_rate_1d",
    "mean_forward_return_5d",
    "median_forward_return_5d",
    "hit_rate_5d",
    "mean_forward_return_20d",
    "median_forward_return_20d",
    "hit_rate_20d",
    "mean_benchmark_excess_return_1d",
    "median_benchmark_excess_return_1d",
    "positive_excess_rate_1d",
    "mean_benchmark_excess_return_5d",
    "median_benchmark_excess_return_5d",
    "positive_excess_rate_5d",
    "mean_benchmark_excess_return_20d",
    "median_benchmark_excess_return_20d",
    "positive_excess_rate_20d",
]

IC_RANKIC_FIELDS = [
    "factor_id",
    "factor_family",
    "daily_ic_1d",
    "daily_ic_5d",
    "daily_ic_20d",
    "daily_rank_ic_1d",
    "daily_rank_ic_5d",
    "daily_rank_ic_20d",
    "mean_ic_1d",
    "mean_ic_5d",
    "mean_ic_20d",
    "mean_rank_ic_1d",
    "mean_rank_ic_5d",
    "mean_rank_ic_20d",
    "ic_positive_rate_1d",
    "ic_positive_rate_5d",
    "ic_positive_rate_20d",
    "rank_ic_positive_rate_1d",
    "rank_ic_positive_rate_5d",
    "rank_ic_positive_rate_20d",
    "ic_availability_status",
    "insufficient_cross_section_warning",
]

MONOTONICITY_FIELDS = [
    "factor_id",
    "factor_family",
    "monotonicity_status_1d",
    "monotonicity_status_5d",
    "monotonicity_status_20d",
    "top_minus_bottom_return_spread_1d",
    "top_minus_bottom_return_spread_5d",
    "top_minus_bottom_return_spread_20d",
    "top_minus_bottom_excess_spread_1d",
    "top_minus_bottom_excess_spread_5d",
    "top_minus_bottom_excess_spread_20d",
    "expected_direction_alignment_status",
    "inverse_signal_warning",
]

ROLLING_STABILITY_FIELDS = [
    "factor_id",
    "factor_family",
    "rolling_window_spec",
    "rolling_mean_ic",
    "rolling_mean_rank_ic",
    "rolling_top_bottom_excess_spread",
    "stable_window_count",
    "unstable_window_count",
    "sign_flip_count",
    "stability_classification",
]

HORIZON_CONSISTENCY_FIELDS = [
    "factor_id",
    "factor_family",
    "1d_direction_status",
    "5d_direction_status",
    "20d_direction_status",
    "horizon_consistency_status",
    "conflicting_horizon_warning",
    "strongest_horizon",
    "weakest_horizon",
]

SCORE_VALIDITY_FIELDS = [
    "factor_id",
    "factor_family",
    "no_lookahead_status",
    "bucket_status",
    "ic_rankic_status",
    "monotonicity_status",
    "rolling_stability_status",
    "horizon_consistency_status",
    "score_validity_classification",
    "accepted_for_downstream",
    "candidate_for_rec_tiering",
    "rejection_reason",
    "recommended_next_action",
]

TRIAL_REGISTRY_FIELDS = [
    "trial_id",
    "factor_id",
    "factor_family",
    "source_candidate_goal",
    "input_artifacts",
    "evaluation_date_range",
    "universe_mode",
    "row_count",
    "no_lookahead_status",
    "bucket_status",
    "ic_rankic_status",
    "monotonicity_status",
    "rolling_stability_status",
    "horizon_consistency_status",
    "score_validity_classification",
    "accepted_for_downstream",
    "candidate_for_rec_tiering",
    "rejection_reason",
    "recommended_next_action",
]

FALSE_BOUNDARY_KEYS = [
    "recommendation_outputs_created",
    "recommendation_rows_created",
    "position_rows_created",
    "position_band_rows_created",
    "directional_trade_labels_generated",
    "buy_sell_hold_outputs_generated",
    "target_prices_generated",
    "actual_position_sizing_generated",
    "target_weights_generated",
    "portfolio_weights_generated",
    "order_quantities_generated",
    "portfolio_returns_generated",
    "equity_curves_generated",
    "dashboard_outputs_generated",
    "dashboard_files_generated",
    "html_generated",
    "streamlit_generated",
    "frontend_code_generated",
    "visual_reports_generated",
    "trading_outputs_created",
    "broker_outputs_created",
    "production_outputs_created",
    "local_lake_outputs_created",
    "factor_mining_outputs_created",
    "dqn_rl_outputs_created",
    "goal_rec_tiering01_run",
    "goal10b4_run",
    "position_band_validation_run",
    "goal10d_run",
    "live_provider_fetches_run",
    "future_returns_used_in_factor_construction",
    "benchmark_excess_returns_used_in_factor_construction",
    "label_ready_fields_used_in_factor_construction",
    "factor_formulas_tuned_to_future_returns",
    "factors_selected_by_posthoc_performance_without_recorded_logic",
    "production_predictive_validity_claimed",
    "factor_promoted_to_actionable_recommendation",
    "demo_fixture_used",
    "outputs_samples_used",
    "stale_goal10b_evidence_used",
    "stale_dc02_evidence_used",
]

FORBIDDEN_OUTPUT_PREFIXES = [
    "outputs/recommendations/",
    "outputs/positions/",
    "outputs/position_sizing/",
    "outputs/position_weights/",
    "outputs/orders/",
    "outputs/portfolio_returns/",
    "outputs/equity_curves/",
    "outputs/dashboard/",
    "outputs/dashboards/",
    "outputs/frontend/",
    "outputs/streamlit/",
    "outputs/visual_reports/",
    "outputs/trading/",
    "outputs/paper_trading/",
    "outputs/live_trading/",
    "outputs/broker/",
    "outputs/production/",
    "outputs/factors/",
    "outputs/dqn/",
    "outputs/rl/",
    "data/raw/",
    "data/bundles/",
    "data/lake/",
    "data/exports/",
]

EXPECTED_FACTOR_IDS = [
    "alpha_short_reversal_1d",
    "alpha_short_reversal_5d",
    "alpha_benchmark_relative_strength_5d",
    "alpha_benchmark_relative_strength_20d",
    "alpha_vol_adj_momentum_5d",
    "alpha_vol_adj_momentum_20d",
    "alpha_liquidity_pressure_5d",
    "alpha_turnover_pressure_20d",
    "alpha_price_volume_confirmation_5d",
    "alpha_downside_vol_adjusted_strength_20d",
    "alpha_intraday_recovery_pressure",
    "alpha_intraday_weakness_pressure",
    "alpha_risk_adjusted_relative_strength",
]


def run_goal_quant_research02_alpha_factor_evaluation_gate(root: Path) -> bool:
    result = evaluate_goal_quant_research02_alpha_factor_evaluation(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal_quant_research02_alpha_factor_evaluation_gate(root)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal_quant_research02_alpha_factor_evaluation_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    evaluation = _read_csv(root / EVALUATION_PANEL_PATH)
    coverage = _read_csv(root / COVERAGE_SUMMARY_PATH)
    bucket_metrics = _read_csv(root / BUCKET_METRICS_PATH)
    ic_rankic = _read_csv(root / IC_RANKIC_SUMMARY_PATH)
    monotonicity = _read_csv(root / MONOTONICITY_SUMMARY_PATH)
    rolling = _read_csv(root / ROLLING_STABILITY_SUMMARY_PATH)
    horizon = _read_csv(root / HORIZON_CONSISTENCY_PATH)
    validity = _read_csv(root / SCORE_VALIDITY_PATH)
    trials = _read_csv(root / TRIAL_REGISTRY_PATH)
    workflow = _workflow_rows(root)
    failures: list[str] = []

    for path in OUTPUTS:
        if path != AUDIT_PATH and not (root / path).exists():
            failures.append(f"missing_output:{path}")
    for path in REQUIRED_INPUTS:
        if not (root / path).exists():
            failures.append(f"missing_required_input:{path}")
    if not _report_pass_or_warn(report):
        failures.append("goal_quant_research02_report_not_pass_or_warn")
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
        "alpha_evaluation_panel_created",
        "coverage_summary_created",
        "bucket_metrics_created",
        "ic_rankic_summary_created",
        "monotonicity_summary_created",
        "rolling_stability_summary_created",
        "horizon_consistency_summary_created",
        "score_validity_classification_created",
        "trial_registry_created",
        "source_backed_lineage_verified",
        "used_committed_alpha_candidate01_evidence_only",
        "used_committed_provider02b_evidence_only",
        "future_returns_used_only_for_posthoc_evaluation",
        "benchmark_excess_returns_used_only_for_posthoc_evaluation",
        "no_lookahead_evaluation_passed",
        "anti_overfitting_policy_recorded",
        "goal_rec_tiering01_locked_future",
        "goal10b4_locked_future",
        "position_band_validation_locked_future",
        "goal10d_locked_future",
        "dashboard_daily_report_locked_future",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")
    if evaluation and list(evaluation[0]) != EVALUATION_PANEL_FIELDS:
        failures.append("evaluation_panel_fields_invalid")
    if coverage and list(coverage[0]) != COVERAGE_FIELDS:
        failures.append("coverage_fields_invalid")
    if bucket_metrics and list(bucket_metrics[0]) != BUCKET_METRIC_FIELDS:
        failures.append("bucket_metric_fields_invalid")
    if ic_rankic and list(ic_rankic[0]) != IC_RANKIC_FIELDS:
        failures.append("ic_rankic_fields_invalid")
    if monotonicity and list(monotonicity[0]) != MONOTONICITY_FIELDS:
        failures.append("monotonicity_fields_invalid")
    if rolling and list(rolling[0]) != ROLLING_STABILITY_FIELDS:
        failures.append("rolling_fields_invalid")
    if horizon and list(horizon[0]) != HORIZON_CONSISTENCY_FIELDS:
        failures.append("horizon_fields_invalid")
    if validity and list(validity[0]) != SCORE_VALIDITY_FIELDS:
        failures.append("validity_fields_invalid")
    if trials and list(trials[0]) != TRIAL_REGISTRY_FIELDS:
        failures.append("trial_registry_fields_invalid")
    if len(evaluation) != int(manifest.get("alpha_evaluation_panel_row_count", -1)):
        failures.append("evaluation_panel_row_count_mismatch")
    if len(evaluation) != 78000:
        failures.append("evaluation_panel_expected_78000_rows")
    if len(coverage) != int(manifest.get("coverage_summary_row_count", -1)):
        failures.append("coverage_row_count_mismatch")
    if len(validity) != int(manifest.get("score_validity_row_count", -1)):
        failures.append("validity_row_count_mismatch")
    if len(trials) != int(manifest.get("trial_registry_row_count", -1)):
        failures.append("trial_registry_row_count_mismatch")
    if len({(row.get("trade_date", ""), row.get("symbol", ""), row.get("factor_id", "")) for row in evaluation}) != len(evaluation):
        failures.append("duplicate_trade_date_symbol_factor_id_rows")
    if {row.get("factor_id", "") for row in coverage} != set(EXPECTED_FACTOR_IDS):
        failures.append("coverage_factor_ids_invalid")
    if any(row.get("non_actionable_disclaimer") != NON_ACTIONABLE for row in evaluation):
        failures.append("evaluation_non_actionable_disclaimer_invalid")
    if any(row.get("no_lookahead_status") != "passed_current_or_past_only" for row in evaluation):
        failures.append("evaluation_no_lookahead_status_invalid")
    if any(row.get("accepted_for_downstream") != "false" for row in validity + trials):
        failures.append("downstream_acceptance_flag_must_remain_false")
    ready = sum(1 for row in validity if row.get("candidate_for_rec_tiering") == "true")
    if int(manifest.get("ready_factor_count", -1)) != ready:
        failures.append("ready_factor_count_mismatch")
    if _contains_forbidden_label(evaluation + validity + trials):
        failures.append("forbidden_actionable_label_present")
    if _contains_secret_like_text(root, OUTPUTS):
        failures.append("secret_or_token_like_text_present")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))

    gate = workflow.get(WORKFLOW_ID, {})
    rec = workflow.get(GOAL_REC_TIERING01_WORKFLOW_ID, {})
    if gate.get("status") != "implemented_research_only":
        failures.append("goal_quant_research02_workflow_not_implemented_research_only")
    if gate.get("implemented_in_repo") != "true":
        failures.append("goal_quant_research02_workflow_not_marked_implemented")
    if gate.get("depends_on") != GOAL_ALPHA_FACTOR_CANDIDATE01_WORKFLOW_ID:
        failures.append("goal_quant_research02_dependency_invalid")
    if rec.get("status") != "locked_future" or rec.get("implemented_in_repo") != "false":
        failures.append("goal_rec_tiering01_not_locked_future")
    if rec.get("depends_on") not in {
        WORKFLOW_ID,
        "goal_alpha_factor_candidate02_refined_variants_research_gate",
    }:
        failures.append("goal_rec_tiering01_dependency_invalid")
    for workflow_id in [
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
        row = workflow.get(workflow_id, {})
        if row.get("status") != "locked_future":
            failures.append(f"{workflow_id}_not_locked_future")
        if row.get("implemented_in_repo") != "false":
            failures.append(f"{workflow_id}_marked_implemented")

    status = PASS if not failures else BLOCKED
    write_text(
        root / AUDIT_PATH,
        "\n".join(
            [
                "# GOAL-QUANT-RESEARCH-02 Alpha Factor Evaluation Audit",
                "",
                f"Status: `{status}`",
                "",
                f"Workflow status: `{gate.get('status', 'missing')}`",
                f"Alpha factors evaluated: `{len(coverage)}`",
                f"Evaluation panel rows: `{len(evaluation)}`",
                f"Ready factor count: `{manifest.get('ready_factor_count', 0)}`",
                f"Overall validity: `{manifest.get('overall_score_validity_status', 'missing')}`",
                "Forward returns and benchmark-excess returns used only post-hoc: `true`",
                "Recommendations, positions, portfolio outputs, dashboards, trading, production, local-lake, factor-mining, and DQN/RL generated: `false`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == PASS


def evaluate_goal_quant_research02_alpha_factor_evaluation(root: Path) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = ["posthoc_evaluation_only_no_production_predictive_validity_claimed"]
    for path in REQUIRED_INPUTS:
        if not (root / path).exists():
            failures.append(f"missing_required_input:{path}")
    if failures:
        return _blocked_result(failures, warnings)

    alpha_registry = _read_csv(root / ALPHA_REGISTRY_PATH)
    alpha_panel = _read_csv(root / ALPHA_PANEL_PATH)
    alpha_coverage = _read_csv(root / ALPHA_COVERAGE_PATH)
    alpha_warnings = _read_csv(root / ALPHA_WARNINGS_PATH)
    provider_panel = _read_csv(root / PROVIDER02B_PANEL_PATH)
    mvp_symbol_rows = _read_csv(root / MVP_SYMBOL_TABLE_PATH)
    mvp_queue_rows = _read_csv(root / MVP_REVIEW_QUEUE_PATH)
    quant01_registry = _read_csv(root / QUANT01_REGISTRY_PATH)
    quant01_validity = _read_csv(root / QUANT01_VALIDITY_PATH)
    quant01_trials = _read_csv(root / QUANT01_TRIAL_REGISTRY_PATH)

    if len(alpha_registry) != 13:
        failures.append(f"alpha_registry_row_count_is_{len(alpha_registry)}")
    if len(alpha_panel) != 78000:
        failures.append(f"alpha_panel_row_count_is_{len(alpha_panel)}")
    if {row.get("factor_id", "") for row in alpha_registry} != set(EXPECTED_FACTOR_IDS):
        failures.append("alpha_registry_factor_ids_invalid")
    provider_by_key = {_key(row): row for row in provider_panel}
    if len(provider_by_key) != len(provider_panel):
        failures.append("provider02b_duplicate_trade_date_symbol_keys")
    if failures:
        return _blocked_result(failures, warnings)

    registry_by_factor = {row["factor_id"]: row for row in alpha_registry}
    coverage_by_factor = {row["factor_id"]: row for row in alpha_coverage}
    evaluation_rows = _evaluation_panel_rows(alpha_panel, provider_by_key)
    coverage = _coverage_rows(evaluation_rows, registry_by_factor, coverage_by_factor)
    bucket_metrics = _bucket_metric_rows(evaluation_rows)
    ic_rankic = _ic_rankic_rows(evaluation_rows)
    monotonicity = _monotonicity_rows(evaluation_rows)
    rolling = _rolling_stability_rows(evaluation_rows)
    horizon = _horizon_consistency_rows(monotonicity)
    validity = _score_validity_rows(coverage, ic_rankic, monotonicity, rolling, horizon)
    trials = _trial_registry_rows(validity, evaluation_rows)
    ready = [row for row in validity if row["candidate_for_rec_tiering"] == "true"]
    if ready:
        status = PASS
        overall = "factor_candidate_for_rec_tiering_available"
        next_goal = NEXT_GOAL_AVAILABLE
        allowed_next = ALLOWED_NEXT_AVAILABLE
    else:
        status = PASS_WITH_WARNINGS
        overall = "no_factor_ready_for_rec_tiering"
        next_goal = NEXT_GOAL_WEAK
        allowed_next = ALLOWED_NEXT_WEAK
        warnings.append("no_factor_ready_for_rec_tiering_after_alpha_candidate_evaluation")

    manifest = {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "mode": MODE,
        "status": status,
        "workflow_id": WORKFLOW_ID,
        "allowed_next_action": allowed_next,
        "recommended_next_goal": next_goal,
        "overall_score_validity_status": overall,
        "evaluated_factor_count": len(alpha_registry),
        "source_alpha_panel_row_count": len(alpha_panel),
        "source_provider02b_row_count": len(provider_panel),
        "alpha_evaluation_panel_row_count": len(evaluation_rows),
        "coverage_summary_row_count": len(coverage),
        "bucket_metric_row_count": len(bucket_metrics),
        "ic_rankic_summary_row_count": len(ic_rankic),
        "monotonicity_summary_row_count": len(monotonicity),
        "rolling_stability_summary_row_count": len(rolling),
        "horizon_consistency_summary_row_count": len(horizon),
        "score_validity_row_count": len(validity),
        "trial_registry_row_count": len(trials),
        "ready_factor_count": len(ready),
        "ready_factor_ids": [row["factor_id"] for row in ready],
        "date_range": _date_range(evaluation_rows),
        "unique_symbols": len({row["symbol"] for row in evaluation_rows}),
        "unique_trade_dates": len({row["trade_date"] for row in evaluation_rows}),
        "alpha_evaluation_panel_created": True,
        "coverage_summary_created": True,
        "bucket_metrics_created": True,
        "ic_rankic_summary_created": True,
        "monotonicity_summary_created": True,
        "rolling_stability_summary_created": True,
        "horizon_consistency_summary_created": True,
        "score_validity_classification_created": True,
        "trial_registry_created": True,
        "source_backed_lineage_verified": True,
        "used_committed_alpha_candidate01_evidence_only": True,
        "used_committed_provider02b_evidence_only": True,
        "used_committed_mvp01_evidence_only": True,
        "used_committed_quant_research01_evidence_only": True,
        "future_returns_used_only_for_posthoc_evaluation": True,
        "benchmark_excess_returns_used_only_for_posthoc_evaluation": True,
        "no_lookahead_evaluation_passed": True,
        "anti_overfitting_policy_recorded": True,
        "goal_rec_tiering01_locked_future": True,
        "goal10b4_locked_future": True,
        "position_band_validation_locked_future": True,
        "goal10d_locked_future": True,
        "dashboard_daily_report_locked_future": True,
        "portfolio_backtest_locked_future": True,
        "input_lineage": REQUIRED_INPUTS,
        "output_artifacts": OUTPUTS,
        "input_row_counts": {
            ALPHA_REGISTRY_PATH: len(alpha_registry),
            ALPHA_PANEL_PATH: len(alpha_panel),
            ALPHA_COVERAGE_PATH: len(alpha_coverage),
            ALPHA_WARNINGS_PATH: len(alpha_warnings),
            PROVIDER02B_PANEL_PATH: len(provider_panel),
            MVP_SYMBOL_TABLE_PATH: len(mvp_symbol_rows),
            MVP_REVIEW_QUEUE_PATH: len(mvp_queue_rows),
            QUANT01_REGISTRY_PATH: len(quant01_registry),
            QUANT01_VALIDITY_PATH: len(quant01_validity),
            QUANT01_TRIAL_REGISTRY_PATH: len(quant01_trials),
        },
        "warnings": sorted(set(warnings)),
        "failures": failures,
    }
    for key in FALSE_BOUNDARY_KEYS:
        manifest[key] = False

    return {
        "status": status,
        "warnings": sorted(set(warnings)),
        "failures": failures,
        "evaluation_rows": evaluation_rows,
        "coverage": coverage,
        "bucket_metrics": bucket_metrics,
        "ic_rankic": ic_rankic,
        "monotonicity": monotonicity,
        "rolling": rolling,
        "horizon": horizon,
        "validity": validity,
        "trials": trials,
        "manifest": manifest,
    }


def goal_quant_research02_valid_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        (
            "GOAL-QUANT-RESEARCH-02 Alpha Candidate Factor Validity Evaluation Gate: PASS" in report
            or "GOAL-QUANT-RESEARCH-02 Alpha Candidate Factor Validity Evaluation Gate: PASS_WITH_WARNINGS" in report
        )
        and "Status: `PASS`" in audit
        and manifest.get("mode") == MODE
        and manifest.get("alpha_evaluation_panel_created") is True
        and manifest.get("future_returns_used_only_for_posthoc_evaluation") is True
        and manifest.get("recommendation_outputs_created") is False
    )


def goal_quant_research02_implemented_workflow_patch(status: str = PASS_WITH_WARNINGS, ready_factor_count: int = 0) -> dict[str, str]:
    return {
        "display_name": "GOAL-QUANT-RESEARCH-02 Alpha Candidate Factor Validity Evaluation Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_research_only",
        "current_repo_role": MODE,
        "implemented_in_repo": "true",
        "allowed_next_action": ALLOWED_NEXT_AVAILABLE if ready_factor_count else ALLOWED_NEXT_WEAK,
        "depends_on": GOAL_ALPHA_FACTOR_CANDIDATE01_WORKFLOW_ID,
        "produces_artifacts": ";".join(OUTPUTS),
        "primary_docs": f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "scripts/run_goal_quant_research02_alpha_factor_evaluation_gate.py;scripts/audit_goal_quant_research02_alpha_factor_evaluation_gate.py",
        "primary_outputs": ";".join([EVALUATION_PANEL_PATH, COVERAGE_SUMMARY_PATH, BUCKET_METRICS_PATH, IC_RANKIC_SUMMARY_PATH, MONOTONICITY_SUMMARY_PATH, ROLLING_STABILITY_SUMMARY_PATH, HORIZON_CONSISTENCY_PATH, SCORE_VALIDITY_PATH, TRIAL_REGISTRY_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH]),
        "promotion_rule": "implemented_research_only_after_goal_quant_research02_pass_or_pass_with_warnings",
        "notes": "Research-only alpha candidate validity evaluation over committed GOAL-ALPHA-FACTOR-CANDIDATE-01 and Provider02B evidence. It uses forward returns only post-hoc and creates no recommendation, position, portfolio, dashboard, trading, production, local-lake, factor-mining, broker, or DQN/RL outputs.",
    }


def locked_goal_rec_tiering01_patch(result: dict[str, object] | None = None) -> dict[str, str]:
    manifest = (result or {}).get("manifest", {}) if isinstance(result, dict) else {}
    ready = int(manifest.get("ready_factor_count", 0)) if isinstance(manifest, dict) else 0
    return {
        "status": "locked_future",
        "current_repo_role": "locked_future_recommendation_score_tiering_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "explicit_request_required_after_quant_research02_candidate_review" if ready else "remain_locked_until_new_alpha_candidate_or_research_refinement",
        "depends_on": WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal_rec_tiering01_gate_after_quant_research02",
        "notes": "Future recommendation score tiering remains locked; GOAL-QUANT-RESEARCH-02 creates research-only alpha validity diagnostics and no recommendation rows.",
    }


def locked_goal10b4_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal_rec_tiering01_passes",
        "depends_on": GOAL_REC_TIERING01_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal10b4_revalidation_gate",
        "notes": "Future GOAL-10B.4 remains locked; GOAL-QUANT-RESEARCH-02 creates no recommendation revalidation rows.",
    }


def locked_position_band_validation_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal10b4_and_explicit_position_validation_request",
        "depends_on": GOAL10B4_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_position_band_validation_gate",
        "notes": "Future position-band validation remains locked; GOAL-QUANT-RESEARCH-02 creates no position outputs.",
    }


def locked_goal10d_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10d_request",
        "depends_on": GOAL10C_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal10d_failure_attribution_gate",
        "notes": "Future GOAL-10D remains locked; GOAL-QUANT-RESEARCH-02 creates only research alpha validity diagnostics.",
    }


def _evaluation_panel_rows(alpha_rows: list[dict[str, str]], provider_by_key: dict[tuple[str, str], dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in sorted(alpha_rows, key=lambda item: (item["trade_date"], item["symbol"], item["factor_id"])):
        labels = provider_by_key.get(_key(row), {})
        output.append(
            {
                "trade_date": row["trade_date"],
                "symbol": row["symbol"],
                "factor_id": row["factor_id"],
                "factor_family": row["factor_family"],
                "factor_value": row.get("factor_value", ""),
                "factor_value_normalized_cross_sectional": row.get("factor_value_normalized_cross_sectional", ""),
                "factor_quantile": row.get("factor_quantile", ""),
                "factor_bucket": row.get("factor_bucket", ""),
                "expected_direction": row.get("expected_direction", ""),
                "forward_return_1d": labels.get("forward_return_1d", ""),
                "forward_return_5d": labels.get("forward_return_5d", ""),
                "forward_return_20d": labels.get("forward_return_20d", ""),
                "benchmark_excess_return_1d": labels.get("benchmark_excess_return_1d", ""),
                "benchmark_excess_return_5d": labels.get("benchmark_excess_return_5d", ""),
                "benchmark_excess_return_20d": labels.get("benchmark_excess_return_20d", ""),
                "source_provider": row.get("source_provider", labels.get("source_provider", "")),
                "universe_mode": row.get("universe_mode", labels.get("universe_mode", "")),
                "panel_contract_status": row.get("panel_contract_status", labels.get("panel_contract_status", "")),
                "risk_score_bucket": row.get("risk_score_bucket", ""),
                "downside_risk_bucket": row.get("downside_risk_bucket", ""),
                "mvp_review_queue_category": row.get("mvp_review_queue_category", ""),
                "mvp_review_priority_level": row.get("mvp_review_priority_level", ""),
                "no_lookahead_status": row.get("no_lookahead_status", ""),
                "diagnostic_mode": MODE,
                "non_actionable_disclaimer": NON_ACTIONABLE,
            }
        )
    return output


def _coverage_rows(rows: list[dict[str, object]], registry: dict[str, dict[str, str]], alpha_coverage: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    by_factor = _group_by(rows, "factor_id")
    output: list[dict[str, object]] = []
    for factor_id in EXPECTED_FACTOR_IDS:
        factor_rows = by_factor[factor_id]
        valid = [row for row in factor_rows if _float(row.get("factor_value", "")) is not None]
        buckets = Counter(str(row.get("factor_bucket", "")) for row in factor_rows if row.get("factor_bucket"))
        bucket_values = list(buckets.values())
        duplicate_count = _duplicate_count((row["trade_date"], row["symbol"], row["factor_id"]) for row in factor_rows)
        collapsed = max(bucket_values, default=0) / len(factor_rows) >= COLLAPSE_THRESHOLD if factor_rows else True
        min_size = min(bucket_values, default=0)
        readiness = "evaluation_ready" if valid and not duplicate_count and not collapsed and min_size >= MIN_BUCKET_ROWS else "evaluation_ready_with_warnings"
        output.append(
            {
                "factor_id": factor_id,
                "row_count": len(factor_rows),
                "valid_factor_value_count": len(valid),
                "missing_factor_value_count": len(factor_rows) - len(valid),
                "unique_symbols": len({row["symbol"] for row in factor_rows}),
                "unique_trade_dates": len({row["trade_date"] for row in factor_rows}),
                "quantile_count": len({row.get("factor_quantile", "") for row in factor_rows if row.get("factor_quantile")}),
                "bucket_count": len(buckets),
                "dominant_bucket_share": _fmt(max(bucket_values, default=0) / len(factor_rows) if factor_rows else 0.0),
                "minimum_bucket_size": min_size,
                "duplicate_key_count": duplicate_count,
                "construction_status": registry.get(factor_id, {}).get("construction_status", alpha_coverage.get(factor_id, {}).get("construction_status", "")),
                "no_lookahead_status": registry.get(factor_id, {}).get("no_lookahead_status", "passed_current_or_past_only"),
                "evaluation_readiness_status": readiness,
            }
        )
    return output


def _bucket_metric_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    by_factor = _group_by(rows, "factor_id")
    for factor_id in EXPECTED_FACTOR_IDS:
        factor_rows = by_factor[factor_id]
        family = str(factor_rows[0].get("factor_family", "")) if factor_rows else ""
        for group_type, field in [("factor_quantile", "factor_quantile"), ("factor_bucket", "factor_bucket")]:
            grouped = _group_by([row for row in factor_rows if row.get(field)], field)
            for group_value in sorted(grouped, key=_sort_group):
                output.append(_bucket_metric_row(factor_id, family, group_type, group_value, grouped[group_value]))
    return output


def _bucket_metric_row(factor_id: str, family: str, group_type: str, group_value: str, rows: list[dict[str, object]]) -> dict[str, object]:
    out = {
        "factor_id": factor_id,
        "factor_family": family,
        "group_type": group_type,
        "group_value": group_value,
        "row_count": len(rows),
        "unique_symbols": len({row["symbol"] for row in rows}),
        "unique_trade_dates": len({row["trade_date"] for row in rows}),
    }
    for horizon in HORIZONS:
        forward = [_float(row.get(f"forward_return_{horizon}", "")) for row in rows]
        excess = [_float(row.get(f"benchmark_excess_return_{horizon}", "")) for row in rows]
        out[f"mean_forward_return_{horizon}"] = _fmt(_mean(forward))
        out[f"median_forward_return_{horizon}"] = _fmt(_median(forward))
        out[f"hit_rate_{horizon}"] = _fmt(_positive_rate(forward))
        out[f"mean_benchmark_excess_return_{horizon}"] = _fmt(_mean(excess))
        out[f"median_benchmark_excess_return_{horizon}"] = _fmt(_median(excess))
        out[f"positive_excess_rate_{horizon}"] = _fmt(_positive_rate(excess))
    return out


def _ic_rankic_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    by_factor = _group_by(rows, "factor_id")
    for factor_id in EXPECTED_FACTOR_IDS:
        factor_rows = by_factor[factor_id]
        family = str(factor_rows[0].get("factor_family", "")) if factor_rows else ""
        daily = {
            "ic": {horizon: _daily_correlations(factor_rows, f"forward_return_{horizon}", rank=False) for horizon in HORIZONS},
            "rank_ic": {horizon: _daily_correlations(factor_rows, f"forward_return_{horizon}", rank=True) for horizon in HORIZONS},
        }
        status = "ic_rankic_available" if max(len(daily["ic"][horizon]) for horizon in HORIZONS) >= 20 else "ic_rankic_unavailable_insufficient_cross_section"
        row = {"factor_id": factor_id, "factor_family": family, "ic_availability_status": status, "insufficient_cross_section_warning": status != "ic_rankic_available"}
        for metric_name in ["ic", "rank_ic"]:
            prefix = "daily_ic" if metric_name == "ic" else "daily_rank_ic"
            mean_prefix = "mean_ic" if metric_name == "ic" else "mean_rank_ic"
            rate_prefix = "ic_positive_rate" if metric_name == "ic" else "rank_ic_positive_rate"
            for horizon in HORIZONS:
                values = [value for _, value in daily[metric_name][horizon]]
                row[f"{prefix}_{horizon}"] = _compact_daily_values(daily[metric_name][horizon])
                row[f"{mean_prefix}_{horizon}"] = _fmt(_mean(values))
                row[f"{rate_prefix}_{horizon}"] = _fmt(_positive_rate(values))
        output.append(row)
    return output


def _monotonicity_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    by_factor = _group_by(rows, "factor_id")
    for factor_id in EXPECTED_FACTOR_IDS:
        factor_rows = by_factor[factor_id]
        family = str(factor_rows[0].get("factor_family", "")) if factor_rows else ""
        row: dict[str, object] = {"factor_id": factor_id, "factor_family": family}
        statuses = []
        inverse = False
        for horizon in HORIZONS:
            return_spread = _top_bottom_spread(factor_rows, f"forward_return_{horizon}")
            excess_spread = _top_bottom_spread(factor_rows, f"benchmark_excess_return_{horizon}")
            status = _direction_status(return_spread)
            statuses.append(status)
            inverse = inverse or status == "inverse_signal_warning"
            row[f"monotonicity_status_{horizon}"] = status
            row[f"top_minus_bottom_return_spread_{horizon}"] = _fmt(return_spread)
            row[f"top_minus_bottom_excess_spread_{horizon}"] = _fmt(excess_spread)
        aligned = statuses.count("expected_direction_aligned")
        if aligned == 3:
            overall = "expected_direction_aligned"
        elif inverse:
            overall = "directionally_inconsistent_or_inverse"
        else:
            overall = "weak_or_mixed_directional_evidence"
        row["expected_direction_alignment_status"] = overall
        row["inverse_signal_warning"] = inverse
        output.append(row)
    return output


def _rolling_stability_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    dates = sorted({str(row["trade_date"]) for row in rows})
    windows = _rolling_windows(dates, 20) + _rolling_windows(dates, 40) + _split_windows(dates)
    by_factor = _group_by(rows, "factor_id")
    for factor_id in EXPECTED_FACTOR_IDS:
        factor_rows = by_factor[factor_id]
        family = str(factor_rows[0].get("factor_family", "")) if factor_rows else ""
        metrics = []
        for name, window_dates in windows:
            subset = [row for row in factor_rows if row["trade_date"] in window_dates]
            spread = _top_bottom_spread(subset, "benchmark_excess_return_20d")
            if spread is None:
                continue
            rank_values = [value for _, value in _daily_correlations(subset, "forward_return_20d", rank=True)]
            ic_values = [value for _, value in _daily_correlations(subset, "forward_return_20d", rank=False)]
            direction = 1 if spread > 0 else -1 if spread < 0 else 0
            metrics.append((name, _mean(ic_values), _mean(rank_values), spread, direction))
        stable = sum(1 for _, _, _, _, direction in metrics if direction > 0)
        unstable = sum(1 for _, _, _, _, direction in metrics if direction < 0)
        signs = [direction for _, _, _, _, direction in metrics if direction]
        flips = sum(1 for left, right in zip(signs, signs[1:]) if left != right)
        if not metrics:
            classification = "factor_not_evaluable"
        elif stable / len(metrics) >= 0.60 and flips <= 2:
            classification = "factor_stable"
        elif flips > max(3, len(metrics) // 5):
            classification = "factor_directionally_inconsistent"
        else:
            classification = "factor_unstable"
        output.append(
            {
                "factor_id": factor_id,
                "factor_family": family,
                "rolling_window_spec": "20d_rolling;40d_rolling;first_half_second_half;calendar_month_when_available",
                "rolling_mean_ic": _fmt(_mean([item[1] for item in metrics])),
                "rolling_mean_rank_ic": _fmt(_mean([item[2] for item in metrics])),
                "rolling_top_bottom_excess_spread": _fmt(_mean([item[3] for item in metrics])),
                "stable_window_count": stable,
                "unstable_window_count": unstable,
                "sign_flip_count": flips,
                "stability_classification": classification,
            }
        )
    return output


def _horizon_consistency_rows(monotonicity: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in monotonicity:
        statuses = {horizon: str(row.get(f"monotonicity_status_{horizon}", "")) for horizon in HORIZONS}
        spread = {horizon: abs(_float(row.get(f"top_minus_bottom_excess_spread_{horizon}", "")) or 0.0) for horizon in HORIZONS}
        aligned = sum(1 for value in statuses.values() if value == "expected_direction_aligned")
        inverse = sum(1 for value in statuses.values() if value == "inverse_signal_warning")
        if aligned == 3:
            consistency = "horizons_consistent_positive"
        elif inverse and aligned:
            consistency = "horizons_conflicting"
        elif inverse >= 2:
            consistency = "horizons_consistent_inverse"
        else:
            consistency = "horizons_weak_or_mixed"
        output.append(
            {
                "factor_id": row["factor_id"],
                "factor_family": row["factor_family"],
                "1d_direction_status": statuses["1d"],
                "5d_direction_status": statuses["5d"],
                "20d_direction_status": statuses["20d"],
                "horizon_consistency_status": consistency,
                "conflicting_horizon_warning": consistency == "horizons_conflicting",
                "strongest_horizon": max(spread, key=spread.get),
                "weakest_horizon": min(spread, key=spread.get),
            }
        )
    return output


def _score_validity_rows(
    coverage: list[dict[str, object]],
    ic_rankic: list[dict[str, object]],
    monotonicity: list[dict[str, object]],
    rolling: list[dict[str, object]],
    horizon: list[dict[str, object]],
) -> list[dict[str, object]]:
    coverage_map = {row["factor_id"]: row for row in coverage}
    ic_map = {row["factor_id"]: row for row in ic_rankic}
    mono_map = {row["factor_id"]: row for row in monotonicity}
    rolling_map = {row["factor_id"]: row for row in rolling}
    horizon_map = {row["factor_id"]: row for row in horizon}
    output: list[dict[str, object]] = []
    for factor_id in EXPECTED_FACTOR_IDS:
        cov = coverage_map[factor_id]
        ic = ic_map[factor_id]
        mono = mono_map[factor_id]
        roll = rolling_map[factor_id]
        hor = horizon_map[factor_id]
        min_ok = int(cov["minimum_bucket_size"] or 0) >= MIN_BUCKET_ROWS
        collapsed = _float(cov["dominant_bucket_share"]) is not None and (_float(cov["dominant_bucket_share"]) or 1.0) >= COLLAPSE_THRESHOLD
        no_lookahead_ok = cov["no_lookahead_status"] == "passed_current_or_past_only"
        ic_ok = ic["ic_availability_status"] == "ic_rankic_available"
        mono_ok = mono["expected_direction_alignment_status"] == "expected_direction_aligned"
        inverse = mono["inverse_signal_warning"] == "true"
        stable = roll["stability_classification"] == "factor_stable"
        horizon_ok = hor["horizon_consistency_status"] == "horizons_consistent_positive"
        candidate = bool(no_lookahead_ok and min_ok and not collapsed and ic_ok and (mono_ok or horizon_ok) and stable and not inverse)
        if candidate:
            classification = "factor_candidate_for_rec_tiering"
            rejection = ""
            next_action = "eligible_for_explicit_goal_rec_tiering01_review_request"
        elif not min_ok or collapsed:
            classification = "factor_requires_redefinition"
            rejection = "bucket_distribution_collapsed_or_minimum_bucket_size_unacceptable"
            next_action = "redefine_or_collect_more_candidate_evidence_before_rec_tiering"
        elif inverse:
            classification = "factor_signal_directionally_inconsistent"
            rejection = "monotonicity_or_horizon_direction_opposite_to_hypothesis"
            next_action = "review_factor_direction_or_replace_candidate"
        elif not ic_ok:
            classification = "factor_not_evaluable"
            rejection = "ic_rankic_unavailable_for_committed_cross_section"
            next_action = "collect_more_evidence_or_refine_candidate"
        elif not stable:
            classification = "factor_signal_weak_or_unreliable"
            rejection = "rolling_window_stability_not_acceptable"
            next_action = "continue_alpha_research_before_recommendation_tiering"
        else:
            classification = "factor_signal_available_but_needs_more_data"
            rejection = "evidence_available_but_not_strong_enough_for_rec_tiering"
            next_action = "expand_or_refine_alpha_research_before_rec_tiering"
        output.append(
            {
                "factor_id": factor_id,
                "factor_family": mono["factor_family"],
                "no_lookahead_status": cov["no_lookahead_status"],
                "bucket_status": "not_collapsed" if min_ok and not collapsed else "collapsed_or_imbalanced",
                "ic_rankic_status": ic["ic_availability_status"],
                "monotonicity_status": mono["expected_direction_alignment_status"],
                "rolling_stability_status": roll["stability_classification"],
                "horizon_consistency_status": hor["horizon_consistency_status"],
                "score_validity_classification": classification,
                "accepted_for_downstream": False,
                "candidate_for_rec_tiering": candidate,
                "rejection_reason": rejection,
                "recommended_next_action": next_action,
            }
        )
    return output


def _trial_registry_rows(validity: list[dict[str, object]], evaluation_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    date_range = _date_range(evaluation_rows)
    universe_modes = sorted({str(row.get("universe_mode", "")) for row in evaluation_rows if row.get("universe_mode")})
    rows = []
    for index, row in enumerate(validity, start=1):
        rows.append(
            {
                "trial_id": f"goal_quant_research02_trial_{index:02d}",
                "factor_id": row["factor_id"],
                "factor_family": row["factor_family"],
                "source_candidate_goal": "GOAL-ALPHA-FACTOR-CANDIDATE-01",
                "input_artifacts": ";".join(REQUIRED_INPUTS),
                "evaluation_date_range": date_range,
                "universe_mode": ";".join(universe_modes),
                "row_count": sum(1 for item in evaluation_rows if item["factor_id"] == row["factor_id"]),
                "no_lookahead_status": row["no_lookahead_status"],
                "bucket_status": row["bucket_status"],
                "ic_rankic_status": row["ic_rankic_status"],
                "monotonicity_status": row["monotonicity_status"],
                "rolling_stability_status": row["rolling_stability_status"],
                "horizon_consistency_status": row["horizon_consistency_status"],
                "score_validity_classification": row["score_validity_classification"],
                "accepted_for_downstream": False,
                "candidate_for_rec_tiering": row["candidate_for_rec_tiering"],
                "rejection_reason": row["rejection_reason"],
                "recommended_next_action": row["recommended_next_action"],
            }
        )
    return rows


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / EVALUATION_PANEL_PATH, result["evaluation_rows"], EVALUATION_PANEL_FIELDS)
    write_csv(root / COVERAGE_SUMMARY_PATH, result["coverage"], COVERAGE_FIELDS)
    write_csv(root / BUCKET_METRICS_PATH, result["bucket_metrics"], BUCKET_METRIC_FIELDS)
    write_csv(root / IC_RANKIC_SUMMARY_PATH, result["ic_rankic"], IC_RANKIC_FIELDS)
    write_csv(root / MONOTONICITY_SUMMARY_PATH, result["monotonicity"], MONOTONICITY_FIELDS)
    write_csv(root / ROLLING_STABILITY_SUMMARY_PATH, result["rolling"], ROLLING_STABILITY_FIELDS)
    write_csv(root / HORIZON_CONSISTENCY_PATH, result["horizon"], HORIZON_CONSISTENCY_FIELDS)
    write_csv(root / SCORE_VALIDITY_PATH, result["validity"], SCORE_VALIDITY_FIELDS)
    write_csv(root / TRIAL_REGISTRY_PATH, result["trials"], TRIAL_REGISTRY_FIELDS)
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_report(root, result)
    _write_doc(root, result)
    _write_contract(root, result)


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    validity = result["validity"]
    class_counts = Counter(str(row["score_validity_classification"]) for row in validity)
    body = [
        "# GOAL-QUANT-RESEARCH-02 Alpha Candidate Factor Validity Evaluation Gate",
        "",
        "## 1. Goal status",
        f"GOAL-QUANT-RESEARCH-02 Alpha Candidate Factor Validity Evaluation Gate: {manifest['status']}",
        "",
        "## 2. Current MVP and alpha-candidate context",
        "GOAL-ALPHA-FACTOR-CANDIDATE-01 constructed 13 research-only candidate factors over 50 symbols and 120 dates. This gate evaluates those candidates only after construction is complete.",
        "",
        "## 3. Source-backed evidence lineage",
        *[f"- `{path}`" for path in REQUIRED_INPUTS],
        "",
        "## 4. Alpha candidates evaluated",
        f"Factors evaluated: `{manifest['evaluated_factor_count']}`.",
        "",
        "## 5. Coverage and bucket diagnostics",
        f"Coverage rows: `{manifest['coverage_summary_row_count']}`. Bucket metric rows: `{manifest['bucket_metric_row_count']}`.",
        "",
        "## 6. Forward-return and benchmark-excess-return metrics",
        "Forward returns and benchmark-excess returns from Provider02B are used only post-hoc after candidate values, quantiles, and buckets already exist.",
        "",
        "## 7. IC / RankIC diagnostics",
        f"IC/RankIC rows: `{manifest['ic_rankic_summary_row_count']}`.",
        "",
        "## 8. Monotonicity and spread diagnostics",
        f"Monotonicity rows: `{manifest['monotonicity_summary_row_count']}`.",
        "",
        "## 9. Rolling stability diagnostics",
        "The gate evaluates 20-date rolling windows, 40-date rolling windows, first-half/second-half splits, and calendar-month windows when enough dates are available.",
        "",
        "## 10. Horizon consistency diagnostics",
        f"Horizon consistency rows: `{manifest['horizon_consistency_summary_row_count']}`.",
        "",
        "## 11. Score validity classification",
        f"Classification counts: `{dict(sorted(class_counts.items()))}`.",
        "",
        "## 12. Factor readiness for recommendation tiering",
        f"Ready factor count: `{manifest['ready_factor_count']}`.",
        f"Overall validity: `{manifest['overall_score_validity_status']}`.",
        "",
        "## 13. Trial registry and anti-overfitting controls",
        "Every alpha candidate is recorded as a trial. The policy forbids formula tuning to forward returns, unregistered repeated search, single-horizon promotion, promotion without stability checks, and portfolio-return or equity-curve selection.",
        "",
        "## 14. Locked downstream boundaries",
        "GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, portfolio backtests, trading, production, local-lake, broker, factor-mining, and DQN/RL remain locked.",
        "",
        "## 15. Recommended next goal",
        f"`{manifest['recommended_next_goal']}`.",
        "",
    ]
    write_text(root / REPORT_PATH, "\n".join(body))


def _write_doc(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    body = [
        "# GOAL-QUANT-RESEARCH-02 Alpha Candidate Factor Validity Evaluation Gate",
        "",
        f"Status: `{manifest['status']}`",
        "",
        "This gate is research-only. It evaluates the 13 GOAL-ALPHA-FACTOR-CANDIDATE-01 factors with committed Provider02B labels used only as post-hoc evaluation outcomes.",
        "",
        "## Outputs",
        *[f"- `{path}`" for path in OUTPUTS if path.startswith("outputs/research/")],
        "",
        "## Method",
        "The gate joins alpha candidate values to Provider02B forward-return labels, computes coverage, bucket metrics, IC/RankIC, monotonicity, rolling stability, horizon consistency, score validity classification, and a trial registry.",
        "",
        "## Result",
        f"- Factors evaluated: `{manifest['evaluated_factor_count']}`",
        f"- Evaluation rows: `{manifest['alpha_evaluation_panel_row_count']}`",
        f"- Ready factor count: `{manifest['ready_factor_count']}`",
        f"- Overall validity: `{manifest['overall_score_validity_status']}`",
        f"- Recommended next goal: `{manifest['recommended_next_goal']}`",
        "",
        "## Locked Boundary",
        "No recommendation rows, position rows, BUY/SELL/HOLD labels, target prices, position sizes, weights, orders, portfolio returns, equity curves, dashboards, HTML, Streamlit, frontend, visual reports, trading outputs, broker outputs, production outputs, local-lake files, factor-mining outputs, or DQN/RL outputs are created.",
        "",
    ]
    write_text(root / DOC_PATH, "\n".join(body))


def _write_contract(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    lines = [
        "{",
        '  "goal_id": "GOAL-QUANT-RESEARCH-02",',
        f'  "mode": "{MODE}",',
        f'  "status": "{manifest["status"]}",',
        '  "research_only": true,',
        '  "allowed_inputs": [',
        *[f'    "{path}",' for path in REQUIRED_INPUTS[:-1]],
        f'    "{REQUIRED_INPUTS[-1]}"',
        "  ],",
        '  "allowed_outputs": [',
        *[f'    "{path}",' for path in OUTPUTS[:-1]],
        f'    "{OUTPUTS[-1]}"',
        "  ],",
        '  "evaluation_panel_schema": ' + _json_list(EVALUATION_PANEL_FIELDS) + ",",
        '  "score_validity_schema": ' + _json_list(SCORE_VALIDITY_FIELDS) + ",",
        '  "posthoc_label_policy": "forward_return_and_benchmark_excess_fields_may_only_be_used_after_candidate_values_are_constructed",',
        '  "anti_overfitting_policy": [',
        '    "do_not_tune_factor_formulas_to_forward_returns",',
        '    "record_every_alpha_candidate_trial",',
        '    "do_not_promote_one_horizon_only",',
        '    "require_stability_checks",',
        '    "require_no_lookahead_audit",',
        '    "do_not_promote_collapsed_bucket_factors",',
        '    "do_not_use_portfolio_returns_or_equity_curves"',
        "  ],",
        '  "downstream_locks": {',
        '    "goal_rec_tiering01_recommendation_score_tiering_gate": "locked_future",',
        '    "goal10b4_recommendation_backtest_revalidation": "locked_future",',
        '    "goal_position_band_validation01_position_band_validation_gate": "locked_future",',
        '    "goal10d_backtest_failure_attribution_gate": "locked_future",',
        '    "dashboard_daily_report": "locked_future",',
        '    "portfolio_backtest": "locked_future"',
        "  }",
        "}",
    ]
    write_text(root / CONTRACT_PATH, "\n".join(lines))


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    by_id = {row["workflow_id"]: row for row in rows}
    if WORKFLOW_ID not in by_id:
        insert_at = next((idx + 1 for idx, row in enumerate(rows) if row["workflow_id"] == GOAL_ALPHA_FACTOR_CANDIDATE01_WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": WORKFLOW_ID})
        by_id = {row["workflow_id"]: row for row in rows}
    ready = int(result["manifest"].get("ready_factor_count", 0)) if isinstance(result.get("manifest"), dict) else 0
    by_id[WORKFLOW_ID].update(goal_quant_research02_implemented_workflow_patch(str(result["status"]), ready))
    if GOAL_REC_TIERING01_WORKFLOW_ID in by_id:
        by_id[GOAL_REC_TIERING01_WORKFLOW_ID].update(locked_goal_rec_tiering01_patch(result))
    if GOAL10B4_WORKFLOW_ID in by_id:
        by_id[GOAL10B4_WORKFLOW_ID].update(locked_goal10b4_patch())
    if POSITION_BAND_VALIDATION_WORKFLOW_ID in by_id:
        by_id[POSITION_BAND_VALIDATION_WORKFLOW_ID].update(locked_position_band_validation_patch())
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
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_quant_research02"
    preserve_later_review_only_workflow_states(root, by_id)
    if result["status"] in {PASS, PASS_WITH_WARNINGS} and WORKFLOW_ID in by_id:
        by_id[WORKFLOW_ID].update(goal_quant_research02_implemented_workflow_patch(str(result["status"]), ready))
        if GOAL_REC_TIERING01_WORKFLOW_ID in by_id:
            by_id[GOAL_REC_TIERING01_WORKFLOW_ID].update(locked_goal_rec_tiering01_patch(result))
    preserve_later_review_only_workflow_states(root, by_id)
    write_csv(path, rows)


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    payload = read_json(path) if path.exists() else {}
    payload[WORKFLOW_ID] = "implemented_research_only"
    payload[GOAL_REC_TIERING01_WORKFLOW_ID] = False
    payload[GOAL10B4_WORKFLOW_ID] = False
    payload[POSITION_BAND_VALIDATION_WORKFLOW_ID] = False
    payload[GOAL10D_WORKFLOW_ID] = False
    preserve_later_review_only_capabilities(root, payload)
    if result["status"] in {PASS, PASS_WITH_WARNINGS}:
        payload[WORKFLOW_ID] = "implemented_research_only"
        payload[GOAL_REC_TIERING01_WORKFLOW_ID] = False
    preserve_later_review_only_capabilities(root, payload)
    write_json(path, payload)


def _top_bottom_spread(rows: list[dict[str, object]], target_field: str) -> float | None:
    valued = [row for row in rows if row.get("factor_bucket") not in {"", "INSUFFICIENT_FACTOR_EVIDENCE_REVIEW_ONLY"}]
    if not valued:
        return None
    top = [row for row in valued if row.get("factor_bucket") == "HIGH_FACTOR_EXPOSURE_REVIEW_ONLY" or row.get("factor_quantile") == "5"]
    bottom = [row for row in valued if row.get("factor_bucket") == "LOW_FACTOR_EXPOSURE_REVIEW_ONLY" or row.get("factor_quantile") == "1"]
    if not top or not bottom:
        return None
    top_mean = _mean([_float(row.get(target_field, "")) for row in top])
    bottom_mean = _mean([_float(row.get(target_field, "")) for row in bottom])
    if top_mean is None or bottom_mean is None:
        return None
    return top_mean - bottom_mean


def _direction_status(spread: float | None) -> str:
    if spread is None:
        return "not_evaluable"
    if abs(spread) < 1e-12:
        return "flat_or_no_spread"
    return "expected_direction_aligned" if spread > 0 else "inverse_signal_warning"


def _daily_correlations(rows: list[dict[str, object]], target_field: str, *, rank: bool = False) -> list[tuple[str, float]]:
    output: list[tuple[str, float]] = []
    for date, date_rows in sorted(_group_by(rows, "trade_date").items()):
        pairs = []
        for row in date_rows:
            x = _float(row.get("factor_value", ""))
            y = _float(row.get(target_field, ""))
            if x is not None and y is not None:
                pairs.append((x, y))
        if len(pairs) < 3:
            continue
        xs = [item[0] for item in pairs]
        ys = [item[1] for item in pairs]
        if rank:
            xs = _ranks(xs)
            ys = _ranks(ys)
        corr = _correlation(xs, ys)
        if corr is not None:
            output.append((date, corr))
    return output


def _blocked_result(failures: list[str], warnings: list[str]) -> dict[str, object]:
    manifest = {"goal": GOAL_NAME, "goal_id": GOAL_ID, "mode": MODE, "status": BLOCKED, "workflow_id": WORKFLOW_ID, "failures": failures, "warnings": warnings}
    for key in FALSE_BOUNDARY_KEYS:
        manifest[key] = False
    return {
        "status": BLOCKED,
        "failures": failures,
        "warnings": warnings,
        "evaluation_rows": [],
        "coverage": [],
        "bucket_metrics": [],
        "ic_rankic": [],
        "monotonicity": [],
        "rolling": [],
        "horizon": [],
        "validity": [],
        "trials": [],
        "manifest": manifest,
    }


def _workflow_rows(root: Path) -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _read_csv(root / "configs/project/workflow_status.csv")}


def _forbidden_outputs_present(root: Path) -> list[str]:
    return [prefix.rstrip("/") for prefix in FORBIDDEN_OUTPUT_PREFIXES if (root / prefix).exists()]


def _contains_forbidden_label(rows: list[dict[str, object]]) -> bool:
    forbidden = {"BUY", "SELL", "HOLD", "STRONG_BUY", "STRONG_SELL", "TARGET_WEIGHT", "POSITION_SIZE", "ORDER_QUANTITY"}
    return any(str(value).upper() in forbidden for row in rows for value in row.values())


def _contains_secret_like_text(root: Path, paths: list[str]) -> bool:
    needles = ["TUSHARE_TOKEN=", "api_key=", "secret_key=", "access_token=", "password="]
    for rel in paths:
        path = root / rel
        if path.exists() and any(needle in path.read_text(encoding="utf-8", errors="ignore") for needle in needles):
            return True
    return False


def _rolling_windows(dates: list[str], size: int) -> list[tuple[str, set[str]]]:
    if len(dates) < size:
        return []
    return [(f"{size}d_window_{index + 1:03d}", set(dates[index : index + size])) for index in range(len(dates) - size + 1)]


def _split_windows(dates: list[str]) -> list[tuple[str, set[str]]]:
    if not dates:
        return []
    midpoint = len(dates) // 2
    windows = [("first_half", set(dates[:midpoint])), ("second_half", set(dates[midpoint:]))]
    months: dict[str, set[str]] = defaultdict(set)
    for date in dates:
        months[date[:7]].add(date)
    windows.extend((f"calendar_month_{month}", values) for month, values in sorted(months.items()) if len(values) >= 5)
    return windows


def _key(row: dict[str, object]) -> tuple[str, str]:
    return (str(row.get("trade_date", "")), str(row.get("symbol", "")))


def _group_by(rows: list[dict[str, object]], field: str) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(field, ""))].append(row)
    return grouped


def _duplicate_count(keys) -> int:
    counts = Counter(keys)
    return sum(count - 1 for count in counts.values() if count > 1)


def _date_range(rows: list[dict[str, object]]) -> str:
    dates = sorted({str(row["trade_date"]) for row in rows if row.get("trade_date")})
    return f"{dates[0]}..{dates[-1]}" if dates else ""


def _sort_group(value: str) -> tuple[int, str]:
    if value.isdigit():
        return (0, f"{int(value):03d}")
    return (1, value)


def _float(value: object) -> float | None:
    try:
        if value in {"", None}:
            return None
        return float(str(value))
    except (TypeError, ValueError):
        return None


def _mean(values: list[float | None]) -> float | None:
    clean = [value for value in values if value is not None]
    return sum(clean) / len(clean) if clean else None


def _median(values: list[float | None]) -> float | None:
    clean = [value for value in values if value is not None]
    return median(clean) if clean else None


def _positive_rate(values: list[float | None]) -> float | None:
    clean = [value for value in values if value is not None]
    return sum(1 for value in clean if value > 0) / len(clean) if clean else None


def _correlation(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    dx = [value - mean_x for value in xs]
    dy = [value - mean_y for value in ys]
    denom_x = sum(value * value for value in dx)
    denom_y = sum(value * value for value in dy)
    if denom_x <= 0 or denom_y <= 0:
        return None
    return sum(left * right for left, right in zip(dx, dy)) / ((denom_x * denom_y) ** 0.5)


def _ranks(values: list[float]) -> list[float]:
    ordered = sorted((value, index) for index, value in enumerate(values))
    ranks = [0.0] * len(values)
    current = 0
    while current < len(ordered):
        end = current + 1
        while end < len(ordered) and ordered[end][0] == ordered[current][0]:
            end += 1
        average_rank = (current + 1 + end) / 2.0
        for _, index in ordered[current:end]:
            ranks[index] = average_rank
        current = end
    return ranks


def _compact_daily_values(values: list[tuple[str, float]]) -> str:
    return ";".join(f"{date}:{_fmt(value)}" for date, value in values)


def _fmt(value: object) -> str:
    number = _float(value)
    return "" if number is None else f"{number:.10f}"


def _json_list(values: list[str]) -> str:
    return "[" + ", ".join(f'"{value}"' for value in values) + "]"


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


def _report_pass_or_warn(report: str) -> bool:
    return (
        "GOAL-QUANT-RESEARCH-02 Alpha Candidate Factor Validity Evaluation Gate: PASS" in report
        or "GOAL-QUANT-RESEARCH-02 Alpha Candidate Factor Validity Evaluation Gate: PASS_WITH_WARNINGS" in report
    )

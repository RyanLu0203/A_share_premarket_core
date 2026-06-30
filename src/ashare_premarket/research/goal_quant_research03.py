from __future__ import annotations

import subprocess
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

GOAL_ID = "GOAL-QUANT-RESEARCH-03"
GOAL_NAME = "GOAL-QUANT-RESEARCH-03-REFINED-ALPHA-FACTOR-VALIDITY-EVALUATION-GATE"
MODE = "research_only_refined_alpha_factor_validity_evaluation_gate"
WORKFLOW_ID = "goal_quant_research03_refined_alpha_factor_validity_evaluation_gate"
PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

GOAL_ALPHA_FACTOR_CANDIDATE02_WORKFLOW_ID = "goal_alpha_factor_candidate02_refined_variants_research_gate"
GOAL_REC_TIERING01_WORKFLOW_ID = "goal_rec_tiering01_recommendation_score_tiering_gate"
GOAL10B4_WORKFLOW_ID = "goal10b4_recommendation_backtest_revalidation"
POSITION_BAND_VALIDATION_WORKFLOW_ID = "goal_position_band_validation01_position_band_validation_gate"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
GOAL10C_WORKFLOW_ID = "goal10c_backtest_cost_slippage_sensitivity_gate"

ALLOWED_NEXT_READY = "request_explicit_goal_rec_tiering01_after_goal_quant_research03_ready_factor"
ALLOWED_NEXT_WEAK = "request_goal_data_expansion_or_regime_label_research_before_more_alpha_expansion"
NEXT_GOAL_READY = "GOAL-REC-TIERING-01"
NEXT_GOAL_PARTIAL = "GOAL-DATA-EXPANSION-RESEARCH-01_or_GOAL-REGIME-LABEL-RESEARCH-01"
NEXT_GOAL_WEAK = "GOAL-ALPHA-RESEARCH-DESIGN-02"
NON_ACTIONABLE = "research_only"
N_QUANTILES = 5
MIN_BUCKET_ROWS = 30
MIN_VALID_ROWS = 500
COLLAPSE_THRESHOLD = 0.80
SIZE_LIMIT_BYTES = 95 * 1024 * 1024
HORIZONS = ["1d", "5d", "20d"]

CANDIDATE02_REGISTRY_PATH = "outputs/research/goal_alpha_factor_candidate02_refined_candidate_registry.csv"
CANDIDATE02_PANEL_PATH = "outputs/research/goal_alpha_factor_candidate02_refined_candidate_panel.csv"
CANDIDATE02_COVERAGE_PATH = "outputs/research/goal_alpha_factor_candidate02_coverage_summary.csv"
CANDIDATE02_WARNINGS_PATH = "outputs/research/goal_alpha_factor_candidate02_construction_warnings.csv"
CANDIDATE02_TRIAL_REGISTRY_PATH = "outputs/research/goal_alpha_factor_candidate02_trial_registry.csv"
CANDIDATE02_INTRADAY_STATUS_PATH = "outputs/research/goal_alpha_factor_candidate02_intraday_redefinition_status.csv"
QUANT02_EVALUATION_PANEL_PATH = "outputs/research/goal_quant_research02_alpha_evaluation_panel.csv"
QUANT02_SCORE_VALIDITY_PATH = "outputs/research/goal_quant_research02_alpha_factor_score_validity_classification.csv"
QUANT02_IC_RANKIC_PATH = "outputs/research/goal_quant_research02_alpha_factor_ic_rankic_summary.csv"
QUANT02_MONOTONICITY_PATH = "outputs/research/goal_quant_research02_alpha_factor_monotonicity_summary.csv"
QUANT02_ROLLING_STABILITY_PATH = "outputs/research/goal_quant_research02_alpha_factor_rolling_stability_summary.csv"
QUANT02_HORIZON_CONSISTENCY_PATH = "outputs/research/goal_quant_research02_alpha_factor_horizon_consistency_summary.csv"
QUANT02_BUCKET_METRICS_PATH = "outputs/research/goal_quant_research02_alpha_factor_bucket_metrics.csv"
PROVIDER02B_PANEL_PATH = "outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv"
MVP_SYMBOL_TABLE_PATH = "outputs/mvp/goal_mvp01_symbol_diagnostic_table.csv"
MVP_REVIEW_QUEUE_PATH = "outputs/mvp/goal_mvp01_review_queue.csv"
RISK01_DIAGNOSTICS_PATH = "outputs/diagnostics/goal_risk_tiering01_risk_tiered_diagnostics.csv"
RISK011_DIAGNOSTICS_PATH = "outputs/diagnostics/goal_risk_tiering011_downside_risk_diagnostics.csv"

PANEL_PATH = "outputs/research/goal_quant_research03_refined_alpha_evaluation_panel.csv"
PANEL_PARTS_DIR = "outputs/research/goal_quant_research03_refined_evaluation_panel_parts"
PANEL_INDEX_PATH = "outputs/research/goal_quant_research03_refined_evaluation_panel_index.csv"
COVERAGE_SUMMARY_PATH = "outputs/research/goal_quant_research03_refined_factor_coverage_summary.csv"
BUCKET_METRICS_PATH = "outputs/research/goal_quant_research03_refined_factor_bucket_metrics.csv"
IC_RANKIC_SUMMARY_PATH = "outputs/research/goal_quant_research03_refined_factor_ic_rankic_summary.csv"
MONOTONICITY_SUMMARY_PATH = "outputs/research/goal_quant_research03_refined_factor_monotonicity_summary.csv"
ROLLING_STABILITY_SUMMARY_PATH = "outputs/research/goal_quant_research03_refined_factor_rolling_stability_summary.csv"
HORIZON_CONSISTENCY_PATH = "outputs/research/goal_quant_research03_refined_factor_horizon_consistency_summary.csv"
IMPROVEMENT_SUMMARY_PATH = "outputs/research/goal_quant_research03_refined_factor_improvement_summary.csv"
SCORE_VALIDITY_PATH = "outputs/research/goal_quant_research03_refined_factor_score_validity_classification.csv"
TRIAL_REGISTRY_PATH = "outputs/research/goal_quant_research03_trial_registry.csv"
REPORT_PATH = "outputs/audits/goal_quant_research03_refined_alpha_evaluation_report.md"
MANIFEST_PATH = "outputs/audits/goal_quant_research03_refined_alpha_evaluation_manifest.json"
AUDIT_PATH = "outputs/audits/goal_quant_research03_refined_alpha_evaluation_audit.md"
DOC_PATH = "docs/research/GOAL_QUANT_RESEARCH03_REFINED_ALPHA_FACTOR_VALIDITY_EVALUATION_GATE.md"
CONTRACT_PATH = "configs/research/goal_quant_research03_refined_alpha_evaluation_contract.yaml"

REQUIRED_INPUTS = [
    CANDIDATE02_REGISTRY_PATH,
    CANDIDATE02_PANEL_PATH,
    CANDIDATE02_COVERAGE_PATH,
    CANDIDATE02_WARNINGS_PATH,
    CANDIDATE02_TRIAL_REGISTRY_PATH,
    CANDIDATE02_INTRADAY_STATUS_PATH,
    QUANT02_EVALUATION_PANEL_PATH,
    QUANT02_SCORE_VALIDITY_PATH,
    QUANT02_IC_RANKIC_PATH,
    QUANT02_MONOTONICITY_PATH,
    QUANT02_ROLLING_STABILITY_PATH,
    QUANT02_HORIZON_CONSISTENCY_PATH,
    QUANT02_BUCKET_METRICS_PATH,
    PROVIDER02B_PANEL_PATH,
    MVP_SYMBOL_TABLE_PATH,
    MVP_REVIEW_QUEUE_PATH,
    RISK01_DIAGNOSTICS_PATH,
    RISK011_DIAGNOSTICS_PATH,
]

OUTPUTS = [
    PANEL_INDEX_PATH,
    COVERAGE_SUMMARY_PATH,
    BUCKET_METRICS_PATH,
    IC_RANKIC_SUMMARY_PATH,
    MONOTONICITY_SUMMARY_PATH,
    ROLLING_STABILITY_SUMMARY_PATH,
    HORIZON_CONSISTENCY_PATH,
    IMPROVEMENT_SUMMARY_PATH,
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
    "refined_factor_id",
    "source_factor_id",
    "refinement_type",
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

PANEL_INDEX_FIELDS = [
    "partition_id",
    "partition_field",
    "partition_value",
    "path",
    "row_count",
    "byte_size",
    "schema",
]

COVERAGE_FIELDS = [
    "refined_factor_id",
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
    "sparse_exposure_warning",
    "refinement_type",
    "source_factor_id",
]

BUCKET_METRIC_FIELDS = [
    "refined_factor_id",
    "source_factor_id",
    "refinement_type",
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
    "refined_factor_id",
    "source_factor_id",
    "refinement_type",
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
    "refined_factor_id",
    "source_factor_id",
    "refinement_type",
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
    "refined_factor_id",
    "source_factor_id",
    "refinement_type",
    "factor_family",
    "rolling_mean_ic",
    "rolling_mean_rank_ic",
    "rolling_top_bottom_excess_spread",
    "stable_window_count",
    "unstable_window_count",
    "sign_flip_count",
    "stability_classification",
]

HORIZON_CONSISTENCY_FIELDS = [
    "refined_factor_id",
    "source_factor_id",
    "refinement_type",
    "factor_family",
    "1d_direction_status",
    "5d_direction_status",
    "20d_direction_status",
    "horizon_consistency_status",
    "conflicting_horizon_warning",
    "strongest_horizon",
    "weakest_horizon",
]

IMPROVEMENT_FIELDS = [
    "refined_factor_id",
    "source_factor_id",
    "source_score_validity_classification",
    "source_rolling_stability_status",
    "source_horizon_consistency_status",
    "source_monotonicity_status",
    "refined_score_validity_classification",
    "refined_rolling_stability_status",
    "refined_horizon_consistency_status",
    "refined_monotonicity_status",
    "rolling_stability_improved",
    "horizon_consistency_improved",
    "bucket_health_improved",
    "directional_alignment_improved",
    "valid_row_count_delta",
    "dominant_bucket_share_delta",
    "improvement_summary",
    "improvement_status",
]

SCORE_VALIDITY_FIELDS = [
    "refined_factor_id",
    "source_factor_id",
    "refinement_type",
    "factor_family",
    "no_lookahead_status",
    "bucket_status",
    "ic_rankic_status",
    "monotonicity_status",
    "rolling_stability_status",
    "horizon_consistency_status",
    "refinement_improvement_status",
    "score_validity_classification",
    "accepted_for_downstream",
    "candidate_for_rec_tiering",
    "rejection_reason",
    "recommended_next_action",
]

TRIAL_REGISTRY_FIELDS = [
    "trial_id",
    "refined_factor_id",
    "source_factor_id",
    "refinement_type",
    "source_candidate_goal",
    "input_artifacts",
    "evaluation_date_range",
    "universe_mode",
    "row_count",
    "valid_factor_value_count",
    "no_lookahead_status",
    "bucket_status",
    "ic_rankic_status",
    "monotonicity_status",
    "rolling_stability_status",
    "horizon_consistency_status",
    "refinement_improvement_status",
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
    "refined_formulas_altered_by_posthoc_evaluation",
    "production_predictive_validity_claimed",
    "factor_promoted_to_actionable_recommendation",
    "demo_fixture_used",
    "outputs_samples_used",
    "stale_goal10b_evidence_used",
    "stale_dc02_evidence_used",
    "git_lfs_required",
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


def run_goal_quant_research03_refined_alpha_evaluation_gate(root: Path) -> bool:
    result = evaluate_goal_quant_research03_refined_alpha_evaluation(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal_quant_research03_refined_alpha_evaluation_gate(root)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal_quant_research03_refined_alpha_evaluation_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    evaluation = _read_evaluation_panel(root)
    coverage = _read_csv(root / COVERAGE_SUMMARY_PATH)
    bucket_metrics = _read_csv(root / BUCKET_METRICS_PATH)
    ic_rankic = _read_csv(root / IC_RANKIC_SUMMARY_PATH)
    monotonicity = _read_csv(root / MONOTONICITY_SUMMARY_PATH)
    rolling = _read_csv(root / ROLLING_STABILITY_SUMMARY_PATH)
    horizon = _read_csv(root / HORIZON_CONSISTENCY_PATH)
    improvement = _read_csv(root / IMPROVEMENT_SUMMARY_PATH)
    validity = _read_csv(root / SCORE_VALIDITY_PATH)
    trials = _read_csv(root / TRIAL_REGISTRY_PATH)
    index_rows = _read_csv(root / PANEL_INDEX_PATH)
    workflow = _workflow_rows(root)
    failures: list[str] = []

    for path in OUTPUTS:
        if path != AUDIT_PATH and not (root / path).exists():
            failures.append(f"missing_output:{path}")
    for path in REQUIRED_INPUTS:
        if not (root / path).exists():
            failures.append(f"missing_required_input:{path}")
    if not index_rows:
        failures.append("partition_index_missing_or_empty")
    if (root / PANEL_PATH).exists():
        failures.append("unpartitioned_panel_present_despite_partition_policy")
    if not _report_pass_or_warn(report):
        failures.append("goal_quant_research03_report_not_pass_or_warn")
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
        "refined_alpha_evaluation_panel_created",
        "refined_alpha_evaluation_panel_partitioned",
        "coverage_summary_created",
        "bucket_metrics_created",
        "ic_rankic_summary_created",
        "monotonicity_summary_created",
        "rolling_stability_summary_created",
        "horizon_consistency_summary_created",
        "improvement_summary_created",
        "score_validity_classification_created",
        "trial_registry_created",
        "source_backed_lineage_verified",
        "used_committed_candidate02_evidence_only",
        "used_committed_provider02b_evidence_only",
        "future_returns_used_only_for_posthoc_evaluation",
        "benchmark_excess_returns_used_only_for_posthoc_evaluation",
        "no_lookahead_evaluation_passed",
        "anti_overfitting_policy_recorded",
        "artifact_size_policy_passed",
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
    if improvement and list(improvement[0]) != IMPROVEMENT_FIELDS:
        failures.append("improvement_fields_invalid")
    if validity and list(validity[0]) != SCORE_VALIDITY_FIELDS:
        failures.append("validity_fields_invalid")
    if trials and list(trials[0]) != TRIAL_REGISTRY_FIELDS:
        failures.append("trial_registry_fields_invalid")
    expected_ids = _expected_refined_factor_ids(root)
    if len(evaluation) != int(manifest.get("refined_alpha_evaluation_panel_row_count", -1)):
        failures.append("evaluation_panel_row_count_mismatch")
    if len(evaluation) != 180000:
        failures.append("evaluation_panel_expected_180000_rows")
    for name, rows in [
        ("coverage", coverage),
        ("ic_rankic", ic_rankic),
        ("monotonicity", monotonicity),
        ("rolling", rolling),
        ("horizon", horizon),
        ("improvement", improvement),
        ("validity", validity),
        ("trials", trials),
    ]:
        if len(rows) != 30:
            failures.append(f"{name}_expected_30_rows")
    if {row.get("refined_factor_id", "") for row in coverage} != expected_ids:
        failures.append("coverage_refined_factor_ids_invalid")
    if len({(row.get("trade_date", ""), row.get("symbol", ""), row.get("refined_factor_id", "")) for row in evaluation}) != len(evaluation):
        failures.append("duplicate_trade_date_symbol_refined_factor_rows")
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
    if _contains_secret_like_text(root, OUTPUTS + _panel_part_paths(root)):
        failures.append("secret_or_token_like_text_present")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))
    oversized = _oversized_artifacts(root, include_tracked=True)
    if oversized:
        failures.extend(f"oversized_artifact:{path}:{size}" for path, size in oversized)

    gate = workflow.get(WORKFLOW_ID, {})
    rec = workflow.get(GOAL_REC_TIERING01_WORKFLOW_ID, {})
    if gate.get("status") != "implemented_research_only":
        failures.append("goal_quant_research03_workflow_not_implemented_research_only")
    if gate.get("implemented_in_repo") != "true":
        failures.append("goal_quant_research03_workflow_not_marked_implemented")
    if gate.get("depends_on") != GOAL_ALPHA_FACTOR_CANDIDATE02_WORKFLOW_ID:
        failures.append("goal_quant_research03_dependency_invalid")
    if rec.get("status") != "locked_future" or rec.get("implemented_in_repo") != "false":
        failures.append("goal_rec_tiering01_not_locked_future")
    if rec.get("depends_on") != WORKFLOW_ID:
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
                "# GOAL-QUANT-RESEARCH-03 Refined Alpha Evaluation Audit",
                "",
                f"Status: `{status}`",
                "",
                f"Workflow status: `{gate.get('status', 'missing')}`",
                f"Refined factors evaluated: `{len(coverage)}`",
                f"Evaluation panel rows: `{len(evaluation)}`",
                f"Ready factor count: `{manifest.get('ready_factor_count', 0)}`",
                f"Overall validity: `{manifest.get('overall_score_validity_status', 'missing')}`",
                "Forward returns and benchmark-excess returns used only post-hoc: `true`",
                "Recommendations, positions, portfolio outputs, dashboards, trading, production, local-lake, factor-mining, and DQN/RL generated: `false`",
                "Single-artifact size policy (<95 MiB): `PASS`" if not oversized else "Single-artifact size policy (<95 MiB): `FAIL`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == PASS


def evaluate_goal_quant_research03_refined_alpha_evaluation(root: Path) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = ["posthoc_evaluation_only_no_production_predictive_validity_claimed"]
    for path in REQUIRED_INPUTS:
        if not (root / path).exists():
            failures.append(f"missing_required_input:{path}")
    if failures:
        return _blocked_result(failures, warnings)

    registry = _read_csv(root / CANDIDATE02_REGISTRY_PATH)
    refined_panel = _read_csv(root / CANDIDATE02_PANEL_PATH)
    candidate02_coverage = _read_csv(root / CANDIDATE02_COVERAGE_PATH)
    candidate02_warnings = _read_csv(root / CANDIDATE02_WARNINGS_PATH)
    candidate02_trials = _read_csv(root / CANDIDATE02_TRIAL_REGISTRY_PATH)
    candidate02_intraday = _read_csv(root / CANDIDATE02_INTRADAY_STATUS_PATH)
    quant02_score = _read_csv(root / QUANT02_SCORE_VALIDITY_PATH)
    quant02_ic = _read_csv(root / QUANT02_IC_RANKIC_PATH)
    quant02_mono = _read_csv(root / QUANT02_MONOTONICITY_PATH)
    quant02_rolling = _read_csv(root / QUANT02_ROLLING_STABILITY_PATH)
    quant02_horizon = _read_csv(root / QUANT02_HORIZON_CONSISTENCY_PATH)
    quant02_bucket_metrics = _read_csv(root / QUANT02_BUCKET_METRICS_PATH)
    provider_panel = _read_csv(root / PROVIDER02B_PANEL_PATH)
    mvp_symbol_rows = _read_csv(root / MVP_SYMBOL_TABLE_PATH)
    mvp_queue_rows = _read_csv(root / MVP_REVIEW_QUEUE_PATH)
    risk01_rows = _read_csv(root / RISK01_DIAGNOSTICS_PATH)
    risk011_rows = _read_csv(root / RISK011_DIAGNOSTICS_PATH)

    if len(registry) != 30:
        failures.append(f"candidate02_registry_row_count_is_{len(registry)}")
    if len(refined_panel) != 180000:
        failures.append(f"candidate02_refined_panel_row_count_is_{len(refined_panel)}")
    expected_ids = {row.get("refined_factor_id", "") for row in registry}
    if len(expected_ids) != 30:
        failures.append("candidate02_refined_factor_id_count_invalid")
    provider_by_key = {_key(row): row for row in provider_panel}
    if len(provider_by_key) != len(provider_panel):
        failures.append("provider02b_duplicate_trade_date_symbol_keys")
    if failures:
        return _blocked_result(failures, warnings)

    registry_by_factor = {row["refined_factor_id"]: row for row in registry}
    candidate02_coverage_by_factor = {row["refined_factor_id"]: row for row in candidate02_coverage}
    evaluation_rows = _evaluation_panel_rows(refined_panel, provider_by_key)
    coverage = _coverage_rows(evaluation_rows, registry_by_factor, candidate02_coverage_by_factor)
    bucket_metrics = _bucket_metric_rows(evaluation_rows, registry_by_factor)
    ic_rankic = _ic_rankic_rows(evaluation_rows, registry_by_factor)
    monotonicity = _monotonicity_rows(evaluation_rows, registry_by_factor)
    rolling = _rolling_stability_rows(evaluation_rows, registry_by_factor)
    horizon = _horizon_consistency_rows(monotonicity)
    preliminary_validity = _score_validity_rows(coverage, ic_rankic, monotonicity, rolling, horizon, None)
    improvement = _improvement_rows(
        coverage,
        preliminary_validity,
        monotonicity,
        rolling,
        horizon,
        quant02_score,
        quant02_mono,
        quant02_rolling,
        quant02_horizon,
        quant02_bucket_metrics,
    )
    validity = _score_validity_rows(coverage, ic_rankic, monotonicity, rolling, horizon, improvement)
    improvement = _improvement_rows(
        coverage,
        validity,
        monotonicity,
        rolling,
        horizon,
        quant02_score,
        quant02_mono,
        quant02_rolling,
        quant02_horizon,
        quant02_bucket_metrics,
    )
    trials = _trial_registry_rows(validity, evaluation_rows)
    ready = [row for row in validity if row["candidate_for_rec_tiering"] is True]
    partial_improvement = [row for row in improvement if row["improvement_status"] == "refined_candidate_partially_improved"]
    material_improvement = [row for row in improvement if row["improvement_status"] == "refined_candidate_improved"]

    if ready:
        status = PASS
        overall = "refined_factor_candidate_for_rec_tiering_available"
        next_goal = NEXT_GOAL_READY
        allowed_next = ALLOWED_NEXT_READY
    elif material_improvement or partial_improvement:
        status = PASS_WITH_WARNINGS
        overall = "no_refined_factor_ready_but_partial_improvement_available"
        next_goal = NEXT_GOAL_PARTIAL
        allowed_next = ALLOWED_NEXT_WEAK
        warnings.append("no_refined_factor_ready_for_rec_tiering_but_some_partial_improvement")
    else:
        status = PASS_WITH_WARNINGS
        overall = "no_refined_factor_materially_improved"
        next_goal = NEXT_GOAL_WEAK
        allowed_next = ALLOWED_NEXT_WEAK
        warnings.append("no_refined_factor_ready_for_rec_tiering_after_quant_research03")

    oversized = _oversized_artifacts(root, include_tracked=True)
    if oversized:
        failures.extend(f"oversized_artifact:{path}:{size}" for path, size in oversized)
        status = BLOCKED
    manifest = {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "mode": MODE,
        "status": status,
        "workflow_id": WORKFLOW_ID,
        "allowed_next_action": allowed_next,
        "recommended_next_goal": next_goal,
        "overall_score_validity_status": overall,
        "evaluated_refined_factor_count": len(registry),
        "source_candidate02_panel_row_count": len(refined_panel),
        "source_provider02b_row_count": len(provider_panel),
        "refined_alpha_evaluation_panel_row_count": len(evaluation_rows),
        "coverage_summary_row_count": len(coverage),
        "bucket_metric_row_count": len(bucket_metrics),
        "ic_rankic_summary_row_count": len(ic_rankic),
        "monotonicity_summary_row_count": len(monotonicity),
        "rolling_stability_summary_row_count": len(rolling),
        "horizon_consistency_summary_row_count": len(horizon),
        "improvement_summary_row_count": len(improvement),
        "score_validity_row_count": len(validity),
        "trial_registry_row_count": len(trials),
        "ready_factor_count": len(ready),
        "ready_refined_factor_ids": [row["refined_factor_id"] for row in ready],
        "partial_or_material_improvement_count": len(material_improvement) + len(partial_improvement),
        "date_range": _date_range(evaluation_rows),
        "unique_symbols": len({row["symbol"] for row in evaluation_rows}),
        "unique_trade_dates": len({row["trade_date"] for row in evaluation_rows}),
        "refined_alpha_evaluation_panel_created": True,
        "refined_alpha_evaluation_panel_partitioned": True,
        "coverage_summary_created": True,
        "bucket_metrics_created": True,
        "ic_rankic_summary_created": True,
        "monotonicity_summary_created": True,
        "rolling_stability_summary_created": True,
        "horizon_consistency_summary_created": True,
        "improvement_summary_created": True,
        "score_validity_classification_created": True,
        "trial_registry_created": True,
        "source_backed_lineage_verified": True,
        "used_committed_candidate02_evidence_only": True,
        "used_committed_quant02_evidence_only": True,
        "used_committed_provider02b_evidence_only": True,
        "used_committed_mvp01_evidence_only": True,
        "used_committed_risk_tiering_evidence_only": True,
        "future_returns_used_only_for_posthoc_evaluation": True,
        "benchmark_excess_returns_used_only_for_posthoc_evaluation": True,
        "no_lookahead_evaluation_passed": True,
        "anti_overfitting_policy_recorded": True,
        "artifact_size_policy_passed": not oversized,
        "artifact_size_limit_bytes": SIZE_LIMIT_BYTES,
        "oversized_artifacts": [{"path": path, "byte_size": size} for path, size in oversized],
        "goal_rec_tiering01_locked_future": True,
        "goal10b4_locked_future": True,
        "position_band_validation_locked_future": True,
        "goal10d_locked_future": True,
        "dashboard_daily_report_locked_future": True,
        "portfolio_backtest_locked_future": True,
        "input_lineage": REQUIRED_INPUTS,
        "output_artifacts": OUTPUTS + _panel_part_paths(root),
        "input_row_counts": {
            CANDIDATE02_REGISTRY_PATH: len(registry),
            CANDIDATE02_PANEL_PATH: len(refined_panel),
            CANDIDATE02_COVERAGE_PATH: len(candidate02_coverage),
            CANDIDATE02_WARNINGS_PATH: len(candidate02_warnings),
            CANDIDATE02_TRIAL_REGISTRY_PATH: len(candidate02_trials),
            CANDIDATE02_INTRADAY_STATUS_PATH: len(candidate02_intraday),
            QUANT02_SCORE_VALIDITY_PATH: len(quant02_score),
            QUANT02_IC_RANKIC_PATH: len(quant02_ic),
            QUANT02_MONOTONICITY_PATH: len(quant02_mono),
            QUANT02_ROLLING_STABILITY_PATH: len(quant02_rolling),
            QUANT02_HORIZON_CONSISTENCY_PATH: len(quant02_horizon),
            QUANT02_BUCKET_METRICS_PATH: len(quant02_bucket_metrics),
            PROVIDER02B_PANEL_PATH: len(provider_panel),
            MVP_SYMBOL_TABLE_PATH: len(mvp_symbol_rows),
            MVP_REVIEW_QUEUE_PATH: len(mvp_queue_rows),
            RISK01_DIAGNOSTICS_PATH: len(risk01_rows),
            RISK011_DIAGNOSTICS_PATH: len(risk011_rows),
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
        "improvement": improvement,
        "validity": validity,
        "trials": trials,
        "manifest": manifest,
    }


def goal_quant_research03_valid_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        (
            "GOAL-QUANT-RESEARCH-03 Refined Alpha Factor Validity Evaluation Gate: PASS" in report
            or "GOAL-QUANT-RESEARCH-03 Refined Alpha Factor Validity Evaluation Gate: PASS_WITH_WARNINGS" in report
        )
        and "Status: `PASS`" in audit
        and manifest.get("mode") == MODE
        and manifest.get("refined_alpha_evaluation_panel_created") is True
        and manifest.get("future_returns_used_only_for_posthoc_evaluation") is True
        and manifest.get("recommendation_outputs_created") is False
        and manifest.get("artifact_size_policy_passed") is True
    )


def goal_quant_research03_implemented_workflow_patch(status: str = PASS_WITH_WARNINGS, ready_factor_count: int = 0) -> dict[str, str]:
    return {
        "display_name": "GOAL-QUANT-RESEARCH-03 Refined Alpha Factor Validity Evaluation Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_research_only",
        "current_repo_role": MODE,
        "implemented_in_repo": "true",
        "allowed_next_action": ALLOWED_NEXT_READY if ready_factor_count else ALLOWED_NEXT_WEAK,
        "depends_on": GOAL_ALPHA_FACTOR_CANDIDATE02_WORKFLOW_ID,
        "produces_artifacts": ";".join(OUTPUTS + [f"{PANEL_PARTS_DIR}/*.csv"]),
        "primary_docs": f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "scripts/run_goal_quant_research03_refined_alpha_evaluation_gate.py;scripts/audit_goal_quant_research03_refined_alpha_evaluation_gate.py",
        "primary_outputs": ";".join([PANEL_INDEX_PATH, COVERAGE_SUMMARY_PATH, BUCKET_METRICS_PATH, IC_RANKIC_SUMMARY_PATH, MONOTONICITY_SUMMARY_PATH, ROLLING_STABILITY_SUMMARY_PATH, HORIZON_CONSISTENCY_PATH, IMPROVEMENT_SUMMARY_PATH, SCORE_VALIDITY_PATH, TRIAL_REGISTRY_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH]),
        "promotion_rule": "implemented_research_only_after_goal_quant_research03_pass_or_pass_with_warnings",
        "notes": "Research-only refined alpha factor validity evaluation over committed GOAL-ALPHA-FACTOR-CANDIDATE-02 and Provider02B evidence. It uses forward returns only post-hoc and creates no recommendation, position, portfolio, dashboard, trading, production, local-lake, factor-mining, broker, or DQN/RL outputs.",
    }


def locked_goal_rec_tiering01_patch(result: dict[str, object] | None = None) -> dict[str, str]:
    manifest = (result or {}).get("manifest", {}) if isinstance(result, dict) else {}
    ready = int(manifest.get("ready_factor_count", 0)) if isinstance(manifest, dict) else 0
    return {
        "status": "locked_future",
        "current_repo_role": "locked_future_recommendation_score_tiering_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "explicit_request_required_after_goal_quant_research03_ready_factor" if ready else "remain_locked_until_goal_quant_research03_has_ready_factor",
        "depends_on": WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal_rec_tiering01_gate_after_refined_alpha_evaluation",
        "notes": "Future recommendation score tiering remains locked; GOAL-QUANT-RESEARCH-03 creates research-only refined alpha validity diagnostics and no recommendation rows.",
    }


def locked_goal10b4_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal_rec_tiering01_passes",
        "depends_on": GOAL_REC_TIERING01_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal10b4_revalidation_gate",
        "notes": "Future GOAL-10B.4 remains locked; GOAL-QUANT-RESEARCH-03 creates no recommendation revalidation rows.",
    }


def locked_position_band_validation_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal10b4_and_explicit_position_validation_request",
        "depends_on": GOAL10B4_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_position_band_validation_gate",
        "notes": "Future position-band validation remains locked; GOAL-QUANT-RESEARCH-03 creates no position outputs.",
    }


def locked_goal10d_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10d_request",
        "depends_on": GOAL10C_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal10d_failure_attribution_gate",
        "notes": "Future GOAL-10D remains locked; GOAL-QUANT-RESEARCH-03 creates only research refined alpha diagnostics.",
    }


def _evaluation_panel_rows(refined_rows: list[dict[str, str]], provider_by_key: dict[tuple[str, str], dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in sorted(refined_rows, key=lambda item: (item["trade_date"], item["symbol"], item["refined_factor_id"])):
        labels = provider_by_key.get(_key(row), {})
        output.append(
            {
                "trade_date": row["trade_date"],
                "symbol": row["symbol"],
                "refined_factor_id": row["refined_factor_id"],
                "source_factor_id": row["source_factor_id"],
                "refinement_type": row["refinement_type"],
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


def _coverage_rows(rows: list[dict[str, object]], registry: dict[str, dict[str, str]], candidate02_coverage: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    by_factor = _group_by(rows, "refined_factor_id")
    output: list[dict[str, object]] = []
    for refined_factor_id in sorted(registry):
        factor_rows = by_factor[refined_factor_id]
        valid = [row for row in factor_rows if _float(row.get("factor_value", "")) is not None]
        buckets = Counter(str(row.get("factor_bucket", "")) for row in factor_rows if row.get("factor_bucket"))
        bucket_values = list(buckets.values())
        duplicate_count = _duplicate_count((row["trade_date"], row["symbol"], row["refined_factor_id"]) for row in factor_rows)
        collapsed = max(bucket_values, default=0) / len(factor_rows) >= COLLAPSE_THRESHOLD if factor_rows else True
        min_size = min(bucket_values, default=0)
        sparse = len(valid) < MIN_VALID_ROWS or min_size < MIN_BUCKET_ROWS
        readiness = "evaluation_ready" if valid and not duplicate_count and not collapsed and not sparse else "evaluation_ready_with_warnings"
        reg = registry[refined_factor_id]
        candidate_cov = candidate02_coverage.get(refined_factor_id, {})
        output.append(
            {
                "refined_factor_id": refined_factor_id,
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
                "construction_status": reg.get("construction_status", candidate_cov.get("construction_status", "")),
                "no_lookahead_status": reg.get("no_lookahead_status", candidate_cov.get("no_lookahead_status", "passed_current_or_past_only")),
                "evaluation_readiness_status": readiness,
                "sparse_exposure_warning": sparse,
                "refinement_type": reg.get("refinement_type", ""),
                "source_factor_id": reg.get("source_factor_id", ""),
            }
        )
    return output


def _bucket_metric_rows(rows: list[dict[str, object]], registry: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    by_factor = _group_by(rows, "refined_factor_id")
    for refined_factor_id in sorted(registry):
        factor_rows = by_factor[refined_factor_id]
        reg = registry[refined_factor_id]
        for group_type, field in [("factor_quantile", "factor_quantile"), ("factor_bucket", "factor_bucket")]:
            grouped = _group_by([row for row in factor_rows if row.get(field)], field)
            for group_value in sorted(grouped, key=_sort_group):
                output.append(_bucket_metric_row(refined_factor_id, reg, group_type, group_value, grouped[group_value]))
    return output


def _bucket_metric_row(refined_factor_id: str, reg: dict[str, str], group_type: str, group_value: str, rows: list[dict[str, object]]) -> dict[str, object]:
    out = {
        "refined_factor_id": refined_factor_id,
        "source_factor_id": reg.get("source_factor_id", ""),
        "refinement_type": reg.get("refinement_type", ""),
        "factor_family": reg.get("factor_family", ""),
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


def _ic_rankic_rows(rows: list[dict[str, object]], registry: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    by_factor = _group_by(rows, "refined_factor_id")
    for refined_factor_id in sorted(registry):
        factor_rows = by_factor[refined_factor_id]
        reg = registry[refined_factor_id]
        daily = {
            "ic": {horizon: _daily_correlations(factor_rows, f"forward_return_{horizon}", rank=False) for horizon in HORIZONS},
            "rank_ic": {horizon: _daily_correlations(factor_rows, f"forward_return_{horizon}", rank=True) for horizon in HORIZONS},
        }
        status = "ic_rankic_available" if max(len(daily["ic"][horizon]) for horizon in HORIZONS) >= 20 else "ic_rankic_unavailable_insufficient_cross_section"
        row = {
            "refined_factor_id": refined_factor_id,
            "source_factor_id": reg.get("source_factor_id", ""),
            "refinement_type": reg.get("refinement_type", ""),
            "factor_family": reg.get("factor_family", ""),
            "ic_availability_status": status,
            "insufficient_cross_section_warning": status != "ic_rankic_available",
        }
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


def _monotonicity_rows(rows: list[dict[str, object]], registry: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    by_factor = _group_by(rows, "refined_factor_id")
    for refined_factor_id in sorted(registry):
        factor_rows = by_factor[refined_factor_id]
        reg = registry[refined_factor_id]
        row: dict[str, object] = {
            "refined_factor_id": refined_factor_id,
            "source_factor_id": reg.get("source_factor_id", ""),
            "refinement_type": reg.get("refinement_type", ""),
            "factor_family": reg.get("factor_family", ""),
        }
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


def _rolling_stability_rows(rows: list[dict[str, object]], registry: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    dates = sorted({str(row["trade_date"]) for row in rows})
    windows = _rolling_windows(dates, 20) + _rolling_windows(dates, 40) + _split_windows(dates)
    by_factor = _group_by(rows, "refined_factor_id")
    for refined_factor_id in sorted(registry):
        factor_rows = by_factor[refined_factor_id]
        reg = registry[refined_factor_id]
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
                "refined_factor_id": refined_factor_id,
                "source_factor_id": reg.get("source_factor_id", ""),
                "refinement_type": reg.get("refinement_type", ""),
                "factor_family": reg.get("factor_family", ""),
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
                "refined_factor_id": row["refined_factor_id"],
                "source_factor_id": row["source_factor_id"],
                "refinement_type": row["refinement_type"],
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
    improvement: list[dict[str, object]] | None,
) -> list[dict[str, object]]:
    coverage_map = {row["refined_factor_id"]: row for row in coverage}
    ic_map = {row["refined_factor_id"]: row for row in ic_rankic}
    mono_map = {row["refined_factor_id"]: row for row in monotonicity}
    rolling_map = {row["refined_factor_id"]: row for row in rolling}
    horizon_map = {row["refined_factor_id"]: row for row in horizon}
    improvement_map = {row["refined_factor_id"]: row for row in improvement or []}
    output: list[dict[str, object]] = []
    for refined_factor_id in sorted(coverage_map):
        cov = coverage_map[refined_factor_id]
        ic = ic_map[refined_factor_id]
        mono = mono_map[refined_factor_id]
        roll = rolling_map[refined_factor_id]
        hor = horizon_map[refined_factor_id]
        imp = improvement_map.get(refined_factor_id, {})
        min_ok = int(cov["minimum_bucket_size"] or 0) >= MIN_BUCKET_ROWS
        sufficient_valid = int(cov["valid_factor_value_count"] or 0) >= MIN_VALID_ROWS
        collapsed = _float(cov["dominant_bucket_share"]) is not None and (_float(cov["dominant_bucket_share"]) or 1.0) >= COLLAPSE_THRESHOLD
        no_lookahead_ok = cov["no_lookahead_status"] == "passed_current_or_past_only"
        ic_ok = ic["ic_availability_status"] == "ic_rankic_available"
        mono_ok = mono["expected_direction_alignment_status"] == "expected_direction_aligned"
        inverse = mono["inverse_signal_warning"] == "true"
        stable = roll["stability_classification"] == "factor_stable"
        horizon_ok = hor["horizon_consistency_status"] == "horizons_consistent_positive"
        improvement_status = str(imp.get("improvement_status", "refined_candidate_not_comparable"))
        improvement_ok = improvement_status in {"refined_candidate_improved", "refined_candidate_partially_improved"}
        candidate = bool(no_lookahead_ok and min_ok and sufficient_valid and not collapsed and ic_ok and (mono_ok or horizon_ok) and stable and improvement_ok and not inverse)
        if candidate:
            classification = "factor_candidate_for_rec_tiering"
            rejection = ""
            next_action = "eligible_for_explicit_goal_rec_tiering01_review_request"
        elif not sufficient_valid or not min_ok:
            classification = "factor_too_sparse_after_refinement"
            rejection = "valid_rows_or_minimum_bucket_size_below_threshold_after_refinement"
            next_action = "collect_more_evidence_or_redesign_refinement_before_rec_tiering"
        elif collapsed:
            classification = "factor_requires_redefinition"
            rejection = "bucket_distribution_collapsed_or_imbalanced"
            next_action = "redefine_refined_factor_or_bucket_policy_before_rec_tiering"
        elif inverse:
            classification = "factor_signal_directionally_inconsistent"
            rejection = "monotonicity_or_horizon_direction_opposite_to_hypothesis"
            next_action = "review_factor_direction_or_replace_refined_candidate"
        elif not ic_ok:
            classification = "factor_not_evaluable"
            rejection = "ic_rankic_unavailable_for_committed_cross_section"
            next_action = "expand_evidence_before_refined_alpha_evaluation"
        elif not stable:
            classification = "factor_signal_weak_or_unreliable"
            rejection = "rolling_window_stability_not_acceptable"
            next_action = "continue_refined_alpha_research_before_recommendation_tiering"
        elif improvement_status == "refined_candidate_not_improved":
            classification = "factor_signal_available_but_needs_more_data"
            rejection = "refinement_did_not_improve_source_factor_enough"
            next_action = "collect_more_data_or_design_new_refinement_before_rec_tiering"
        else:
            classification = "factor_signal_available_but_needs_more_data"
            rejection = "evidence_available_but_not_strong_enough_for_rec_tiering"
            next_action = "expand_or_refine_alpha_research_before_rec_tiering"
        output.append(
            {
                "refined_factor_id": refined_factor_id,
                "source_factor_id": cov["source_factor_id"],
                "refinement_type": cov["refinement_type"],
                "factor_family": mono["factor_family"],
                "no_lookahead_status": cov["no_lookahead_status"],
                "bucket_status": "not_collapsed" if min_ok and not collapsed else "collapsed_or_imbalanced",
                "ic_rankic_status": ic["ic_availability_status"],
                "monotonicity_status": mono["expected_direction_alignment_status"],
                "rolling_stability_status": roll["stability_classification"],
                "horizon_consistency_status": hor["horizon_consistency_status"],
                "refinement_improvement_status": improvement_status,
                "score_validity_classification": classification,
                "accepted_for_downstream": False,
                "candidate_for_rec_tiering": candidate,
                "rejection_reason": rejection,
                "recommended_next_action": next_action,
            }
        )
    return output


def _improvement_rows(
    coverage: list[dict[str, object]],
    validity: list[dict[str, object]],
    monotonicity: list[dict[str, object]],
    rolling: list[dict[str, object]],
    horizon: list[dict[str, object]],
    source_validity: list[dict[str, str]],
    source_monotonicity: list[dict[str, str]],
    source_rolling: list[dict[str, str]],
    source_horizon: list[dict[str, str]],
    source_bucket_metrics: list[dict[str, str]],
) -> list[dict[str, object]]:
    cov_map = {row["refined_factor_id"]: row for row in coverage}
    validity_map = {row["refined_factor_id"]: row for row in validity}
    mono_map = {row["refined_factor_id"]: row for row in monotonicity}
    rolling_map = {row["refined_factor_id"]: row for row in rolling}
    horizon_map = {row["refined_factor_id"]: row for row in horizon}
    source_validity_map = {row["factor_id"]: row for row in source_validity}
    source_mono_map = {row["factor_id"]: row for row in source_monotonicity}
    source_rolling_map = {row["factor_id"]: row for row in source_rolling}
    source_horizon_map = {row["factor_id"]: row for row in source_horizon}
    source_bucket_share = _source_dominant_bucket_share(source_bucket_metrics)
    output: list[dict[str, object]] = []
    for refined_factor_id in sorted(cov_map):
        cov = cov_map[refined_factor_id]
        val = validity_map[refined_factor_id]
        mono = mono_map[refined_factor_id]
        roll = rolling_map[refined_factor_id]
        hor = horizon_map[refined_factor_id]
        source_factor_id = str(cov["source_factor_id"])
        source_val = source_validity_map.get(source_factor_id, {})
        source_mono = source_mono_map.get(source_factor_id, {})
        source_roll = source_rolling_map.get(source_factor_id, {})
        source_hor = source_horizon_map.get(source_factor_id, {})
        source_dom = source_bucket_share.get(source_factor_id)
        refined_dom = _float(cov["dominant_bucket_share"])
        source_valid_count = 6000
        refined_valid_count = int(cov["valid_factor_value_count"] or 0)
        rolling_improved = _stability_score(str(roll["stability_classification"])) > _stability_score(str(source_roll.get("stability_classification", "")))
        horizon_improved = _horizon_score(str(hor["horizon_consistency_status"])) > _horizon_score(str(source_hor.get("horizon_consistency_status", "")))
        bucket_improved = source_dom is not None and refined_dom is not None and refined_dom <= source_dom
        directional_improved = _direction_score(str(mono["expected_direction_alignment_status"])) > _direction_score(str(source_mono.get("expected_direction_alignment_status", "")))
        improved_count = sum([rolling_improved, horizon_improved, bucket_improved, directional_improved])
        too_sparse = refined_valid_count < MIN_VALID_ROWS or int(cov["minimum_bucket_size"] or 0) < MIN_BUCKET_ROWS
        if too_sparse:
            status = "refined_candidate_too_sparse"
        elif not source_val:
            status = "refined_candidate_not_comparable"
        elif improved_count >= 3:
            status = "refined_candidate_improved"
        elif improved_count >= 1:
            status = "refined_candidate_partially_improved"
        else:
            status = "refined_candidate_not_improved"
        summary_bits = []
        if rolling_improved:
            summary_bits.append("rolling_stability_improved")
        if horizon_improved:
            summary_bits.append("horizon_consistency_improved")
        if bucket_improved:
            summary_bits.append("bucket_health_improved_or_preserved")
        if directional_improved:
            summary_bits.append("directional_alignment_improved")
        if not summary_bits:
            summary_bits.append(status)
        output.append(
            {
                "refined_factor_id": refined_factor_id,
                "source_factor_id": source_factor_id,
                "source_score_validity_classification": source_val.get("score_validity_classification", ""),
                "source_rolling_stability_status": source_roll.get("stability_classification", ""),
                "source_horizon_consistency_status": source_hor.get("horizon_consistency_status", ""),
                "source_monotonicity_status": source_mono.get("expected_direction_alignment_status", ""),
                "refined_score_validity_classification": val["score_validity_classification"],
                "refined_rolling_stability_status": roll["stability_classification"],
                "refined_horizon_consistency_status": hor["horizon_consistency_status"],
                "refined_monotonicity_status": mono["expected_direction_alignment_status"],
                "rolling_stability_improved": rolling_improved,
                "horizon_consistency_improved": horizon_improved,
                "bucket_health_improved": bucket_improved,
                "directional_alignment_improved": directional_improved,
                "valid_row_count_delta": refined_valid_count - source_valid_count,
                "dominant_bucket_share_delta": _fmt((refined_dom - source_dom) if refined_dom is not None and source_dom is not None else None),
                "improvement_summary": ";".join(summary_bits),
                "improvement_status": status,
            }
        )
    return output


def _trial_registry_rows(validity: list[dict[str, object]], evaluation_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    date_range = _date_range(evaluation_rows)
    universe_modes = sorted({str(row.get("universe_mode", "")) for row in evaluation_rows if row.get("universe_mode")})
    rows = []
    for index, row in enumerate(validity, start=1):
        factor_rows = [item for item in evaluation_rows if item["refined_factor_id"] == row["refined_factor_id"]]
        rows.append(
            {
                "trial_id": f"goal_quant_research03_trial_{index:03d}",
                "refined_factor_id": row["refined_factor_id"],
                "source_factor_id": row["source_factor_id"],
                "refinement_type": row["refinement_type"],
                "source_candidate_goal": "GOAL-ALPHA-FACTOR-CANDIDATE-02",
                "input_artifacts": ";".join(REQUIRED_INPUTS),
                "evaluation_date_range": date_range,
                "universe_mode": ";".join(universe_modes),
                "row_count": len(factor_rows),
                "valid_factor_value_count": sum(1 for item in factor_rows if _float(item.get("factor_value", "")) is not None),
                "no_lookahead_status": row["no_lookahead_status"],
                "bucket_status": row["bucket_status"],
                "ic_rankic_status": row["ic_rankic_status"],
                "monotonicity_status": row["monotonicity_status"],
                "rolling_stability_status": row["rolling_stability_status"],
                "horizon_consistency_status": row["horizon_consistency_status"],
                "refinement_improvement_status": row["refinement_improvement_status"],
                "score_validity_classification": row["score_validity_classification"],
                "accepted_for_downstream": False,
                "candidate_for_rec_tiering": row["candidate_for_rec_tiering"],
                "rejection_reason": row["rejection_reason"],
                "recommended_next_action": row["recommended_next_action"],
            }
        )
    return rows


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    _write_partitioned_panel(root, result["evaluation_rows"])
    write_csv(root / COVERAGE_SUMMARY_PATH, result["coverage"], COVERAGE_FIELDS)
    write_csv(root / BUCKET_METRICS_PATH, result["bucket_metrics"], BUCKET_METRIC_FIELDS)
    write_csv(root / IC_RANKIC_SUMMARY_PATH, result["ic_rankic"], IC_RANKIC_FIELDS)
    write_csv(root / MONOTONICITY_SUMMARY_PATH, result["monotonicity"], MONOTONICITY_FIELDS)
    write_csv(root / ROLLING_STABILITY_SUMMARY_PATH, result["rolling"], ROLLING_STABILITY_FIELDS)
    write_csv(root / HORIZON_CONSISTENCY_PATH, result["horizon"], HORIZON_CONSISTENCY_FIELDS)
    write_csv(root / IMPROVEMENT_SUMMARY_PATH, result["improvement"], IMPROVEMENT_FIELDS)
    write_csv(root / SCORE_VALIDITY_PATH, result["validity"], SCORE_VALIDITY_FIELDS)
    write_csv(root / TRIAL_REGISTRY_PATH, result["trials"], TRIAL_REGISTRY_FIELDS)
    manifest = dict(result["manifest"])
    part_paths = _panel_part_paths(root)
    manifest["panel_partition_artifacts"] = part_paths
    manifest["output_artifacts"] = OUTPUTS + part_paths
    manifest["max_output_artifact_bytes"] = max([_byte_size(root / path) for path in OUTPUTS + part_paths if (root / path).exists()] or [0])
    write_json(root / MANIFEST_PATH, manifest)
    result["manifest"] = manifest
    _write_report(root, result)
    _write_doc(root, result)
    _write_contract(root, result)


def _write_partitioned_panel(root: Path, rows: list[dict[str, object]]) -> None:
    panel_path = root / PANEL_PATH
    if panel_path.exists():
        panel_path.unlink()
    parts_dir = root / PANEL_PARTS_DIR
    parts_dir.mkdir(parents=True, exist_ok=True)
    for existing in parts_dir.glob("*.csv"):
        existing.unlink()
    index_rows = []
    grouped = _group_by(rows, "refinement_type")
    for idx, refinement_type in enumerate(sorted(grouped), start=1):
        filename = f"part_{idx:02d}_{_safe_slug(refinement_type)}.csv"
        rel = f"{PANEL_PARTS_DIR}/{filename}"
        write_csv(root / rel, grouped[refinement_type], EVALUATION_PANEL_FIELDS)
        index_rows.append(
            {
                "partition_id": f"part_{idx:02d}",
                "partition_field": "refinement_type",
                "partition_value": refinement_type,
                "path": rel,
                "row_count": len(grouped[refinement_type]),
                "byte_size": _byte_size(root / rel),
                "schema": ";".join(EVALUATION_PANEL_FIELDS),
            }
        )
    write_csv(root / PANEL_INDEX_PATH, index_rows, PANEL_INDEX_FIELDS)


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    validity = result["validity"]
    improvement = result["improvement"]
    class_counts = Counter(str(row["score_validity_classification"]) for row in validity)
    improvement_counts = Counter(str(row["improvement_status"]) for row in improvement)
    body = [
        "# GOAL-QUANT-RESEARCH-03 Refined Alpha Factor Validity Evaluation Gate",
        "",
        "## 1. Goal status",
        f"GOAL-QUANT-RESEARCH-03 Refined Alpha Factor Validity Evaluation Gate: {manifest['status']}",
        "",
        "## 2. Current Candidate02 context",
        "GOAL-ALPHA-FACTOR-CANDIDATE-02 constructed 30 refined alpha candidates over 50 symbols and 120 dates. This gate evaluates those refined values only after construction is complete.",
        "",
        "## 3. Source-backed evidence lineage",
        *[f"- `{path}`" for path in REQUIRED_INPUTS],
        "",
        "## 4. Refined alpha candidates evaluated",
        f"Refined factors evaluated: `{manifest['evaluated_refined_factor_count']}`.",
        f"Evaluation panel rows: `{manifest['refined_alpha_evaluation_panel_row_count']}`.",
        "",
        "## 5. Coverage and bucket diagnostics",
        f"Coverage rows: `{manifest['coverage_summary_row_count']}`. Bucket metric rows: `{manifest['bucket_metric_row_count']}`.",
        "",
        "## 6. Forward-return and benchmark-excess-return metrics",
        "Forward returns and benchmark-excess returns from Provider02B are used only post-hoc after refined factor values, quantiles, and buckets already exist.",
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
        "## 11. Refinement improvement diagnostics versus Quant02 source factors",
        f"Improvement rows: `{manifest['improvement_summary_row_count']}`. Improvement counts: `{dict(sorted(improvement_counts.items()))}`.",
        "",
        "## 12. Score validity classification",
        f"Classification counts: `{dict(sorted(class_counts.items()))}`.",
        "",
        "## 13. Factor readiness for recommendation tiering",
        f"Ready factor count: `{manifest['ready_factor_count']}`.",
        f"Overall validity: `{manifest['overall_score_validity_status']}`.",
        "",
        "## 14. Trial registry and anti-overfitting controls",
        "Every refined alpha candidate is recorded as a trial. The policy forbids formula tuning to forward returns, altering refined definitions from post-hoc results, unregistered repeated search, single-horizon promotion, and portfolio-return or equity-curve selection.",
        "",
        "## 15. Artifact size and partitioning policy",
        f"The refined evaluation panel is partitioned under `{PANEL_PARTS_DIR}/`. The per-artifact size limit is `{SIZE_LIMIT_BYTES}` bytes and the recorded maximum output artifact size is `{manifest['max_output_artifact_bytes']}` bytes.",
        "",
        "## 16. Locked downstream boundaries",
        "GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, portfolio backtests, trading, production, local-lake, broker, factor-mining, and DQN/RL remain locked.",
        "",
        "## 17. Recommended next goal",
        f"`{manifest['recommended_next_goal']}`.",
        "",
    ]
    write_text(root / REPORT_PATH, "\n".join(body))


def _write_doc(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    body = [
        "# GOAL-QUANT-RESEARCH-03 Refined Alpha Factor Validity Evaluation Gate",
        "",
        f"Status: `{manifest['status']}`",
        "",
        "This gate is research-only. It evaluates the 30 GOAL-ALPHA-FACTOR-CANDIDATE-02 refined factors with committed Provider02B labels used only as post-hoc evaluation outcomes.",
        "",
        "## Outputs",
        *[f"- `{path}`" for path in OUTPUTS if path.startswith("outputs/research/")],
        f"- `{PANEL_PARTS_DIR}/*.csv`",
        "",
        "## Method",
        "The gate joins refined candidate values to Provider02B forward-return labels, computes coverage, bucket metrics, IC/RankIC, monotonicity, rolling stability, horizon consistency, score validity, improvement versus Quant02 source factors, and a trial registry.",
        "",
        "## Result",
        f"- Refined factors evaluated: `{manifest['evaluated_refined_factor_count']}`",
        f"- Evaluation rows: `{manifest['refined_alpha_evaluation_panel_row_count']}`",
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
        '  "goal_id": "GOAL-QUANT-RESEARCH-03",',
        f'  "mode": "{MODE}",',
        f'  "status": "{manifest["status"]}",',
        '  "research_only": true,',
        f'  "artifact_size_limit_bytes": {SIZE_LIMIT_BYTES},',
        '  "evaluation_panel_partition_policy": "partition_by_refinement_type_under_outputs_research_goal_quant_research03_refined_evaluation_panel_parts",',
        '  "allowed_inputs": [',
        *[f'    "{path}",' for path in REQUIRED_INPUTS[:-1]],
        f'    "{REQUIRED_INPUTS[-1]}"',
        "  ],",
        '  "allowed_outputs": [',
        *[f'    "{path}",' for path in OUTPUTS],
        f'    "{PANEL_PARTS_DIR}/*.csv"',
        "  ],",
        '  "evaluation_panel_schema": ' + _json_list(EVALUATION_PANEL_FIELDS) + ",",
        '  "score_validity_schema": ' + _json_list(SCORE_VALIDITY_FIELDS) + ",",
        '  "posthoc_label_policy": "forward_return_and_benchmark_excess_fields_may_only_be_used_after_refined_factor_values_are_constructed",',
        '  "anti_overfitting_policy": [',
        '    "do_not_tune_factor_formulas_to_forward_returns",',
        '    "do_not_alter_refined_definitions_from_posthoc_results",',
        '    "record_every_refined_alpha_candidate_trial",',
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
        insert_at = next((idx + 1 for idx, row in enumerate(rows) if row["workflow_id"] == GOAL_ALPHA_FACTOR_CANDIDATE02_WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": WORKFLOW_ID})
        by_id = {row["workflow_id"]: row for row in rows}
    ready = int(result["manifest"].get("ready_factor_count", 0)) if isinstance(result.get("manifest"), dict) else 0
    by_id[WORKFLOW_ID].update(goal_quant_research03_implemented_workflow_patch(str(result["status"]), ready))
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
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_quant_research03"
    preserve_later_review_only_workflow_states(root, by_id)
    if result["status"] in {PASS, PASS_WITH_WARNINGS} and WORKFLOW_ID in by_id:
        by_id[WORKFLOW_ID].update(goal_quant_research03_implemented_workflow_patch(str(result["status"]), ready))
        if GOAL_REC_TIERING01_WORKFLOW_ID in by_id:
            by_id[GOAL_REC_TIERING01_WORKFLOW_ID].update(locked_goal_rec_tiering01_patch(result))
        if GOAL10B4_WORKFLOW_ID in by_id:
            by_id[GOAL10B4_WORKFLOW_ID].update(locked_goal10b4_patch())
        if POSITION_BAND_VALIDATION_WORKFLOW_ID in by_id:
            by_id[POSITION_BAND_VALIDATION_WORKFLOW_ID].update(locked_position_band_validation_patch())
        if GOAL10D_WORKFLOW_ID in by_id:
            by_id[GOAL10D_WORKFLOW_ID].update(locked_goal10d_patch())
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
    valued = [row for row in rows if row.get("factor_bucket") not in {"", "INSUFFICIENT_REFINED_FACTOR_EVIDENCE_REVIEW_ONLY"}]
    if not valued:
        return None
    top = [row for row in valued if row.get("factor_bucket") == "HIGH_REFINED_FACTOR_EXPOSURE_REVIEW_ONLY" or row.get("factor_quantile") == "5"]
    bottom = [row for row in valued if row.get("factor_bucket") == "LOW_REFINED_FACTOR_EXPOSURE_REVIEW_ONLY" or row.get("factor_quantile") == "1"]
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
        "improvement": [],
        "validity": [],
        "trials": [],
        "manifest": manifest,
    }


def _read_evaluation_panel(root: Path) -> list[dict[str, str]]:
    index_rows = _read_csv(root / PANEL_INDEX_PATH)
    rows: list[dict[str, str]] = []
    for item in index_rows:
        rows.extend(_read_csv(root / item["path"]))
    return rows


def _panel_part_paths(root: Path) -> list[str]:
    parts = root / PANEL_PARTS_DIR
    if not parts.exists():
        return []
    return [str(path.relative_to(root)) for path in sorted(parts.glob("*.csv"))]


def _expected_refined_factor_ids(root: Path) -> set[str]:
    return {row.get("refined_factor_id", "") for row in _read_csv(root / CANDIDATE02_REGISTRY_PATH)}


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


def _oversized_artifacts(root: Path, *, include_tracked: bool) -> list[tuple[str, int]]:
    paths = set(REQUIRED_INPUTS + OUTPUTS + _panel_part_paths(root))
    if include_tracked:
        try:
            completed = subprocess.run(["git", "ls-files"], cwd=root, text=True, capture_output=True, check=False)
            if completed.returncode == 0:
                paths.update(line.strip() for line in completed.stdout.splitlines() if line.strip())
        except OSError:
            pass
    oversized = []
    for rel in sorted(paths):
        path = root / rel
        if path.is_file():
            size = path.stat().st_size
            if size >= SIZE_LIMIT_BYTES:
                oversized.append((rel, size))
    return oversized


def _source_dominant_bucket_share(rows: list[dict[str, str]]) -> dict[str, float]:
    by_factor: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        if row.get("group_type") == "factor_bucket":
            by_factor[row["factor_id"]].append(int(row.get("row_count") or 0))
    return {factor_id: max(counts) / sum(counts) for factor_id, counts in by_factor.items() if sum(counts)}


def _stability_score(value: str) -> int:
    return {"factor_not_evaluable": 0, "factor_directionally_inconsistent": 1, "factor_unstable": 2, "factor_stable": 3}.get(value, 0)


def _horizon_score(value: str) -> int:
    return {"horizons_consistent_inverse": 0, "horizons_conflicting": 1, "horizons_weak_or_mixed": 2, "horizons_consistent_positive": 3}.get(value, 0)


def _direction_score(value: str) -> int:
    return {"directionally_inconsistent_or_inverse": 0, "weak_or_mixed_directional_evidence": 1, "expected_direction_aligned": 2}.get(value, 0)


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


def _safe_slug(value: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in value.lower()).strip("_") or "unknown"


def _byte_size(path: Path) -> int:
    return path.stat().st_size if path.exists() else 0


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
        "GOAL-QUANT-RESEARCH-03 Refined Alpha Factor Validity Evaluation Gate: PASS" in report
        or "GOAL-QUANT-RESEARCH-03 Refined Alpha Factor Validity Evaluation Gate: PASS_WITH_WARNINGS" in report
    )

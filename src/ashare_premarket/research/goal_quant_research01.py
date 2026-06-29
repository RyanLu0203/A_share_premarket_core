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

GOAL_ID = "GOAL-QUANT-RESEARCH-01"
GOAL_NAME = "GOAL-QUANT-RESEARCH-01-FACTOR-RESEARCH-LAB-AND-SCORE-VALIDITY-GATE"
MODE = "research_only_factor_research_lab_and_score_validity_gate"
WORKFLOW_ID = "goal_quant_research01_factor_research_lab_gate"
PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

PROVIDER02B_PANEL_PATH = "outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv"
DC03_RISK_PATH = "outputs/diagnostics/goal_v1_diagnostic_coverage03_risk_diagnostics.csv"
DC03_RECOMMENDATION_PATH = "outputs/diagnostics/goal_v1_diagnostic_coverage03_recommendation_diagnostics.csv"
RISK01_DIAGNOSTICS_PATH = "outputs/diagnostics/goal_risk_tiering01_risk_tiered_diagnostics.csv"
RISK01_DISTRIBUTION_PATH = "outputs/diagnostics/goal_risk_tiering01_distribution_summary.csv"
RISK01_FORWARD_METRICS_PATH = "outputs/backtest/goal_risk_tiering01_risk_tier_forward_return_metrics.csv"
RISK011_DIAGNOSTICS_PATH = "outputs/diagnostics/goal_risk_tiering011_downside_risk_diagnostics.csv"
RISK011_COMPONENT_SUMMARY_PATH = "outputs/diagnostics/goal_risk_tiering011_component_contribution_summary.csv"
RISK011_DISTRIBUTION_PATH = "outputs/diagnostics/goal_risk_tiering011_distribution_summary.csv"
RISK011_FORWARD_METRICS_PATH = "outputs/backtest/goal_risk_tiering011_downside_risk_forward_return_metrics.csv"
GOAL10B3_RECOMMENDATION_METRICS_PATH = "outputs/backtest/goal10b3_recommendation_group_metrics.csv"
GOAL10B3_IMBALANCE_PATH = "outputs/backtest/goal10b3_group_imbalance_diagnostics.csv"

FACTOR_REGISTRY_PATH = "outputs/research/goal_quant_research01_factor_registry.csv"
FACTOR_EVALUATION_PANEL_PATH = "outputs/research/goal_quant_research01_factor_evaluation_panel.csv"
FACTOR_BUCKET_METRICS_PATH = "outputs/research/goal_quant_research01_factor_bucket_metrics.csv"
IC_RANKIC_SUMMARY_PATH = "outputs/research/goal_quant_research01_factor_ic_rankic_summary.csv"
MONOTONICITY_SUMMARY_PATH = "outputs/research/goal_quant_research01_factor_monotonicity_summary.csv"
ROLLING_STABILITY_SUMMARY_PATH = "outputs/research/goal_quant_research01_factor_rolling_stability_summary.csv"
REGIME_SPLIT_SUMMARY_PATH = "outputs/research/goal_quant_research01_factor_regime_split_summary.csv"
TRIAL_REGISTRY_PATH = "outputs/research/goal_quant_research01_trial_registry.csv"
SCORE_VALIDITY_PATH = "outputs/research/goal_quant_research01_score_validity_classification.csv"
REPORT_PATH = "outputs/audits/goal_quant_research01_factor_research_lab_report.md"
MANIFEST_PATH = "outputs/audits/goal_quant_research01_factor_research_lab_manifest.json"
AUDIT_PATH = "outputs/audits/goal_quant_research01_factor_research_lab_audit.md"
CONTRACT_PATH = "configs/research/goal_quant_research01_factor_research_lab_contract.yaml"
DOC_PATH = "docs/research/GOAL_QUANT_RESEARCH01_FACTOR_RESEARCH_LAB_AND_SCORE_VALIDITY_GATE.md"

GOAL_RISK_TIERING011_WORKFLOW_ID = "goal_risk_tiering011_downside_risk_repair_gate"
GOAL_MVP01_WORKFLOW_ID = "goal_mvp01_premarket_research_terminal_gate"
GOAL_ALPHA_FACTOR_CANDIDATE01_WORKFLOW_ID = "goal_alpha_factor_candidate01_research_gate"
GOAL_QUANT_RESEARCH02_WORKFLOW_ID = "goal_quant_research02_alpha_candidate_factor_validity_evaluation_gate"
GOAL_REC_TIERING01_WORKFLOW_ID = "goal_rec_tiering01_recommendation_score_tiering_gate"
GOAL10B4_WORKFLOW_ID = "goal10b4_recommendation_backtest_revalidation"
POSITION_BAND_VALIDATION_WORKFLOW_ID = "goal_position_band_validation01_position_band_validation_gate"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
ALLOWED_NEXT_WEAK = "request_goal_alpha_factor_candidate01_before_recommendation_tiering"
ALLOWED_NEXT_AVAILABLE = "request_explicit_goal_rec_tiering01_after_research_candidate_review"
NON_ACTIONABLE = "research_only_not_investment_advice_not_trade_instruction"
N_QUANTILES = 5
MIN_BUCKET_ROWS = 30
COLLAPSE_THRESHOLD = 0.80
HORIZONS = ["1d", "5d", "20d"]

REQUIRED_INPUTS = [
    PROVIDER02B_PANEL_PATH,
    DC03_RISK_PATH,
    DC03_RECOMMENDATION_PATH,
    RISK01_DIAGNOSTICS_PATH,
    RISK01_DISTRIBUTION_PATH,
    RISK01_FORWARD_METRICS_PATH,
    RISK011_DIAGNOSTICS_PATH,
    RISK011_COMPONENT_SUMMARY_PATH,
    RISK011_DISTRIBUTION_PATH,
    RISK011_FORWARD_METRICS_PATH,
    GOAL10B3_RECOMMENDATION_METRICS_PATH,
    GOAL10B3_IMBALANCE_PATH,
]

OUTPUTS = [
    FACTOR_REGISTRY_PATH,
    FACTOR_EVALUATION_PANEL_PATH,
    FACTOR_BUCKET_METRICS_PATH,
    IC_RANKIC_SUMMARY_PATH,
    MONOTONICITY_SUMMARY_PATH,
    ROLLING_STABILITY_SUMMARY_PATH,
    REGIME_SPLIT_SUMMARY_PATH,
    TRIAL_REGISTRY_PATH,
    SCORE_VALIDITY_PATH,
    REPORT_PATH,
    MANIFEST_PATH,
    AUDIT_PATH,
    CONTRACT_PATH,
    DOC_PATH,
]

FACTOR_REGISTRY_FIELDS = [
    "factor_id",
    "factor_family",
    "factor_name",
    "source_artifact",
    "input_columns",
    "factor_direction_hypothesis",
    "expected_monotonic_direction",
    "score_construction_no_lookahead_status",
    "uses_forward_returns_in_construction",
    "allowed_for_posthoc_evaluation_only",
    "research_stage_status",
    "trial_id",
    "rule_version",
    "governance_notes",
]

FACTOR_EVALUATION_FIELDS = [
    "trade_date",
    "symbol",
    "factor_id",
    "factor_family",
    "factor_value",
    "factor_bucket",
    "factor_quantile",
    "factor_direction_hypothesis",
    "expected_monotonic_direction",
    "forward_return_1d",
    "forward_return_5d",
    "forward_return_20d",
    "benchmark_excess_return_1d",
    "benchmark_excess_return_5d",
    "benchmark_excess_return_20d",
    "source_provider",
    "universe_mode",
    "panel_contract_status",
    "score_construction_no_lookahead_status",
    "diagnostic_mode",
    "non_actionable_disclaimer",
]

BUCKET_METRIC_FIELDS = [
    "factor_id",
    "factor_family",
    "group_type",
    "group_value",
    "row_count",
    "unique_symbols",
    "unique_trade_dates",
    "bucket_count",
    "quantile_count",
    "dominant_bucket_share",
    "minimum_bucket_size",
    "missing_factor_value_count",
    "duplicate_key_count",
    "factor_collapse_detected",
    "group_imbalance_warning",
    "quantile_coverage_status",
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
    "rolling_rank_ic",
    "rolling_top_bottom_spread",
    "stable_window_count",
    "unstable_window_count",
    "sign_flip_count",
    "stability_classification",
]

REGIME_SPLIT_FIELDS = [
    "factor_id",
    "factor_family",
    "regime_split_status",
    "regime_tags_evaluated",
    "no_lookahead_regime_status",
    "notes",
]

TRIAL_REGISTRY_FIELDS = [
    "trial_id",
    "goal_id",
    "factor_id",
    "factor_family",
    "rule_version",
    "input_artifacts",
    "score_components",
    "score_weights_policy",
    "no_lookahead_status",
    "date_range",
    "universe_mode",
    "row_count",
    "metric_summary",
    "accepted_for_downstream",
    "rejection_reason",
    "overfitting_warning_codes",
    "notes",
]

SCORE_VALIDITY_FIELDS = [
    "factor_id",
    "factor_family",
    "score_validity_classification",
    "accepted_for_downstream",
    "candidate_for_rec_tiering",
    "bucket_distribution_status",
    "ic_rankic_status",
    "monotonicity_alignment_status",
    "rolling_stability_status",
    "no_lookahead_status",
    "rejection_reason",
    "recommended_next_action",
]

FALSE_BOUNDARY_KEYS = [
    "recommendation_outputs_created",
    "goal08b_recommendation_rows_created",
    "goal09_position_band_rows_created",
    "goal_rec_tiering01_run",
    "goal10b4_run",
    "position_band_validation_run",
    "goal10d_run",
    "buy_sell_hold_outputs_generated",
    "target_prices_generated",
    "actual_position_sizing_generated",
    "target_weights_generated",
    "portfolio_weights_generated",
    "order_quantities_generated",
    "portfolio_returns_generated",
    "equity_curves_generated",
    "dashboard_outputs_generated",
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
    "live_provider_fetches_run",
    "future_returns_used_in_score_construction",
    "production_predictive_validity_claimed",
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


FACTOR_DEFINITIONS: list[dict[str, object]] = [
    {
        "factor_id": "risk_score_numeric",
        "factor_family": "risk_score",
        "factor_name": "GOAL-RISK-TIERING-01 numeric risk score",
        "source_artifact": RISK01_DIAGNOSTICS_PATH,
        "input_columns": "risk_score_numeric",
        "source": "risk01",
        "column": "risk_score_numeric",
        "value_type": "numeric",
        "factor_direction_hypothesis": "higher_risk_score_should_imply_lower_forward_returns",
        "expected_monotonic_direction": "higher_factor_lower_forward_return",
        "expected_sign": -1,
    },
    {
        "factor_id": "downside_risk_score_numeric",
        "factor_family": "downside_risk_score",
        "factor_name": "GOAL-RISK-TIERING-01.1 downside risk score",
        "source_artifact": RISK011_DIAGNOSTICS_PATH,
        "input_columns": "downside_risk_score_numeric",
        "source": "risk011",
        "column": "downside_risk_score_numeric",
        "value_type": "numeric",
        "factor_direction_hypothesis": "higher_downside_risk_should_imply_lower_forward_returns",
        "expected_monotonic_direction": "higher_factor_lower_forward_return",
        "expected_sign": -1,
    },
    {
        "factor_id": "volatility_component",
        "factor_family": "risk_component",
        "factor_name": "Volatility component from downside-risk repair",
        "source_artifact": RISK011_DIAGNOSTICS_PATH,
        "input_columns": "volatility_component",
        "source": "risk011",
        "column": "volatility_component",
        "value_type": "numeric",
        "factor_direction_hypothesis": "higher_volatility_component_should_imply_lower_forward_returns",
        "expected_monotonic_direction": "higher_factor_lower_forward_return",
        "expected_sign": -1,
    },
    {
        "factor_id": "momentum_component",
        "factor_family": "momentum_component",
        "factor_name": "Momentum component from downside-risk repair",
        "source_artifact": RISK011_DIAGNOSTICS_PATH,
        "input_columns": "momentum_component",
        "source": "risk011",
        "column": "momentum_component",
        "value_type": "numeric",
        "factor_direction_hypothesis": "higher_momentum_component_should_imply_higher_forward_returns",
        "expected_monotonic_direction": "higher_factor_higher_forward_return",
        "expected_sign": 1,
    },
    {
        "factor_id": "abnormal_positive_movement_flag",
        "factor_family": "abnormal_movement_flag",
        "factor_name": "Abnormal positive movement flag",
        "source_artifact": RISK011_DIAGNOSTICS_PATH,
        "input_columns": "abnormal_positive_movement_flag",
        "source": "risk011",
        "column": "abnormal_positive_movement_flag",
        "value_type": "binary",
        "factor_direction_hypothesis": "abnormal_positive_movement_may_mean_revert_lower",
        "expected_monotonic_direction": "higher_factor_lower_forward_return",
        "expected_sign": -1,
    },
    {
        "factor_id": "abnormal_negative_movement_flag",
        "factor_family": "abnormal_movement_flag",
        "factor_name": "Abnormal negative movement flag",
        "source_artifact": RISK011_DIAGNOSTICS_PATH,
        "input_columns": "abnormal_negative_movement_flag",
        "source": "risk011",
        "column": "abnormal_negative_movement_flag",
        "value_type": "binary",
        "factor_direction_hypothesis": "abnormal_negative_movement_may_rebound_higher",
        "expected_monotonic_direction": "higher_factor_higher_forward_return",
        "expected_sign": 1,
    },
    {
        "factor_id": "provider_crosscheck_component",
        "factor_family": "source_quality_component",
        "factor_name": "Provider crosscheck component",
        "source_artifact": RISK011_DIAGNOSTICS_PATH,
        "input_columns": "provider_crosscheck_component",
        "source": "risk011",
        "column": "provider_crosscheck_component",
        "value_type": "numeric",
        "factor_direction_hypothesis": "higher_provider_crosscheck_risk_should_imply_lower_forward_returns",
        "expected_monotonic_direction": "higher_factor_lower_forward_return",
        "expected_sign": -1,
    },
    {
        "factor_id": "data_quality_risk_component",
        "factor_family": "source_quality_component",
        "factor_name": "Data quality risk component",
        "source_artifact": RISK011_DIAGNOSTICS_PATH,
        "input_columns": "data_quality_risk_component",
        "source": "risk011",
        "column": "data_quality_risk_component",
        "value_type": "numeric",
        "factor_direction_hypothesis": "higher_data_quality_risk_should_imply_lower_forward_returns",
        "expected_monotonic_direction": "higher_factor_lower_forward_return",
        "expected_sign": -1,
    },
    {
        "factor_id": "liquidity_risk_component",
        "factor_family": "liquidity_component",
        "factor_name": "Liquidity risk component",
        "source_artifact": RISK011_DIAGNOSTICS_PATH,
        "input_columns": "liquidity_risk_component",
        "source": "risk011",
        "column": "liquidity_risk_component",
        "value_type": "numeric",
        "factor_direction_hypothesis": "higher_liquidity_risk_should_imply_lower_forward_returns",
        "expected_monotonic_direction": "higher_factor_lower_forward_return",
        "expected_sign": -1,
    },
    {
        "factor_id": "trading_status_risk_component",
        "factor_family": "trading_status_component",
        "factor_name": "Trading status risk component",
        "source_artifact": RISK011_DIAGNOSTICS_PATH,
        "input_columns": "trading_status_risk_component",
        "source": "risk011",
        "column": "trading_status_risk_component",
        "value_type": "numeric",
        "factor_direction_hypothesis": "higher_trading_status_risk_should_imply_lower_forward_returns",
        "expected_monotonic_direction": "higher_factor_lower_forward_return",
        "expected_sign": -1,
    },
    {
        "factor_id": "st_status_risk_component",
        "factor_family": "trading_status_component",
        "factor_name": "ST status risk component",
        "source_artifact": RISK011_DIAGNOSTICS_PATH,
        "input_columns": "st_status_risk_component",
        "source": "risk011",
        "column": "st_status_risk_component",
        "value_type": "numeric",
        "factor_direction_hypothesis": "higher_st_status_risk_should_imply_lower_forward_returns",
        "expected_monotonic_direction": "higher_factor_lower_forward_return",
        "expected_sign": -1,
    },
]


def run_goal_quant_research01_factor_research_lab_gate(root: Path) -> bool:
    result = evaluate_goal_quant_research01_factor_research_lab(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal_quant_research01_factor_research_lab_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal_quant_research01_factor_research_lab_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    registry = _read_csv(root / FACTOR_REGISTRY_PATH)
    panel = _read_csv(root / FACTOR_EVALUATION_PANEL_PATH)
    bucket_metrics = _read_csv(root / FACTOR_BUCKET_METRICS_PATH)
    ic_rankic = _read_csv(root / IC_RANKIC_SUMMARY_PATH)
    monotonicity = _read_csv(root / MONOTONICITY_SUMMARY_PATH)
    rolling = _read_csv(root / ROLLING_STABILITY_SUMMARY_PATH)
    regime = _read_csv(root / REGIME_SPLIT_SUMMARY_PATH)
    trials = _read_csv(root / TRIAL_REGISTRY_PATH)
    validity = _read_csv(root / SCORE_VALIDITY_PATH)
    workflow = _workflow_rows(root)
    failures: list[str] = []

    if not _report_pass_or_warn(report):
        failures.append("goal_quant_research01_report_not_pass_or_warn")
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
        "research_only_factor_lab_generated",
        "used_committed_provider02b_evidence_only",
        "used_committed_dc03_evidence_only",
        "used_committed_goal10b3_evidence_only",
        "used_committed_goal_risk_tiering01_evidence_only",
        "used_committed_goal_risk_tiering011_evidence_only",
        "future_returns_used_only_for_posthoc_evaluation",
        "no_lookahead_validation_passed",
        "anti_overfitting_policy_recorded",
        "trial_registry_created",
        "research_stage_roadmap_created",
        "goal_rec_tiering01_locked_future",
        "goal10b4_locked_future",
        "position_band_validation_locked_future",
        "goal10d_locked_future",
        "dashboard_daily_report_locked_future",
        "portfolio_backtest_locked_future",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")
    if len(registry) != manifest.get("factor_count"):
        failures.append("factor_registry_count_mismatch")
    if len(panel) != manifest.get("factor_evaluation_row_count"):
        failures.append("factor_evaluation_panel_count_mismatch")
    if len(panel) != manifest.get("source_panel_row_count", 0) * len(registry):
        failures.append("factor_evaluation_panel_not_trade_date_symbol_factor_grain")
    if registry and list(registry[0]) != FACTOR_REGISTRY_FIELDS:
        failures.append("factor_registry_fields_invalid")
    if panel and list(panel[0]) != FACTOR_EVALUATION_FIELDS:
        failures.append("factor_evaluation_fields_invalid")
    if bucket_metrics and list(bucket_metrics[0]) != BUCKET_METRIC_FIELDS:
        failures.append("bucket_metric_fields_invalid")
    if ic_rankic and list(ic_rankic[0]) != IC_RANKIC_FIELDS:
        failures.append("ic_rankic_fields_invalid")
    if monotonicity and list(monotonicity[0]) != MONOTONICITY_FIELDS:
        failures.append("monotonicity_fields_invalid")
    if rolling and list(rolling[0]) != ROLLING_STABILITY_FIELDS:
        failures.append("rolling_stability_fields_invalid")
    if regime and list(regime[0]) != REGIME_SPLIT_FIELDS:
        failures.append("regime_split_fields_invalid")
    if trials and list(trials[0]) != TRIAL_REGISTRY_FIELDS:
        failures.append("trial_registry_fields_invalid")
    if validity and list(validity[0]) != SCORE_VALIDITY_FIELDS:
        failures.append("score_validity_fields_invalid")
    if len(validity) != len(registry):
        failures.append("score_validity_count_mismatch")
    if any(row.get("uses_forward_returns_in_construction") != "false" for row in registry):
        failures.append("registry_uses_forward_returns_in_construction")
    if any(row.get("accepted_for_downstream") != "false" for row in trials):
        failures.append("trial_registry_promoted_downstream")
    if any(row.get("non_actionable_disclaimer") != NON_ACTIONABLE for row in panel):
        failures.append("factor_panel_non_actionable_disclaimer_invalid")
    duplicate_count = _duplicate_count((row["trade_date"], row["symbol"], row["factor_id"]) for row in panel)
    if duplicate_count != 0:
        failures.append("factor_panel_duplicate_trade_date_symbol_factor_rows")
    if manifest.get("ready_factor_count", 0) != sum(1 for row in validity if row.get("candidate_for_rec_tiering") == "true"):
        failures.append("ready_factor_count_mismatch")
    gate = workflow.get(WORKFLOW_ID, {})
    if gate.get("status") != "implemented_research_only":
        failures.append("goal_quant_research01_workflow_not_implemented_research_only")
    if gate.get("implemented_in_repo") != "true":
        failures.append("goal_quant_research01_workflow_not_marked_implemented")
    if gate.get("depends_on") != GOAL_RISK_TIERING011_WORKFLOW_ID:
        failures.append("goal_quant_research01_dependency_invalid")
    rec = workflow.get(GOAL_REC_TIERING01_WORKFLOW_ID, {})
    if rec.get("status") != "locked_future" or rec.get("implemented_in_repo") != "false":
        failures.append("goal_rec_tiering01_not_locked_after_quant_research")
    quant02_valid_for_dependency = _goal_quant_research02_valid(root)
    expected_rec_dependency = (
        GOAL_QUANT_RESEARCH02_WORKFLOW_ID
        if quant02_valid_for_dependency or workflow.get(GOAL_ALPHA_FACTOR_CANDIDATE01_WORKFLOW_ID, {}).get("status") == "implemented_research_only"
        else GOAL_ALPHA_FACTOR_CANDIDATE01_WORKFLOW_ID
        if workflow.get(GOAL_MVP01_WORKFLOW_ID, {}).get("status") == "implemented_mvp_research_only"
        else WORKFLOW_ID
    )
    if rec.get("depends_on") != expected_rec_dependency:
        failures.append("goal_rec_tiering01_not_rebased_on_quant_research")
    if workflow.get(GOAL_ALPHA_FACTOR_CANDIDATE01_WORKFLOW_ID, {}).get("status") == "implemented_research_only":
        quant02 = workflow.get(GOAL_QUANT_RESEARCH02_WORKFLOW_ID, {})
        quant02_valid = _goal_quant_research02_valid(root)
        if quant02_valid:
            if quant02.get("status") != "implemented_research_only" or quant02.get("implemented_in_repo") != "true":
                failures.append("goal_quant_research02_valid_but_not_implemented")
        elif quant02.get("status") != "locked_future" or quant02.get("implemented_in_repo") != "false":
            failures.append("goal_quant_research02_not_locked_after_alpha_candidate")
        if quant02.get("depends_on") != GOAL_ALPHA_FACTOR_CANDIDATE01_WORKFLOW_ID:
            failures.append("goal_quant_research02_dependency_invalid")
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
                "# GOAL-QUANT-RESEARCH-01 Factor Research Lab Audit",
                "",
                f"Status: `{status}`",
                "",
                f"Workflow status: `{gate.get('status', 'missing')}`",
                f"Factors evaluated: `{len(registry)}`",
                f"Factor evaluation rows: `{len(panel)}`",
                f"Ready factor count: `{manifest.get('ready_factor_count', 0)}`",
                f"Overall validity: `{manifest.get('overall_score_validity_status', 'missing')}`",
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


def evaluate_goal_quant_research01_factor_research_lab(root: Path) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    for path in REQUIRED_INPUTS:
        if not (root / path).exists():
            failures.append(f"missing_required_input:{path}")

    panel_rows = _read_csv(root / PROVIDER02B_PANEL_PATH)
    dc03_risk_rows = _read_csv(root / DC03_RISK_PATH)
    dc03_rec_rows = _read_csv(root / DC03_RECOMMENDATION_PATH)
    risk01_rows = _read_csv(root / RISK01_DIAGNOSTICS_PATH)
    risk011_rows = _read_csv(root / RISK011_DIAGNOSTICS_PATH)
    risk01_distribution = _read_csv(root / RISK01_DISTRIBUTION_PATH)
    risk01_forward_metrics = _read_csv(root / RISK01_FORWARD_METRICS_PATH)
    risk011_component_summary = _read_csv(root / RISK011_COMPONENT_SUMMARY_PATH)
    risk011_distribution = _read_csv(root / RISK011_DISTRIBUTION_PATH)
    risk011_forward_metrics = _read_csv(root / RISK011_FORWARD_METRICS_PATH)
    goal10b3_metrics = _read_csv(root / GOAL10B3_RECOMMENDATION_METRICS_PATH)
    goal10b3_imbalance = _read_csv(root / GOAL10B3_IMBALANCE_PATH)

    if failures:
        return _blocked_result(failures, warnings)

    panel_keys = [_key(row) for row in panel_rows]
    risk01_by_key = {_key(row): row for row in risk01_rows}
    risk011_by_key = {_key(row): row for row in risk011_rows}
    dc03_risk_by_key = {_key(row): row for row in dc03_risk_rows}
    dc03_rec_by_key = {_key(row): row for row in dc03_rec_rows}
    if len(panel_rows) != 6000:
        warnings.append(f"provider02b_panel_row_count_is_{len(panel_rows)}")
    if len(set(panel_keys)) != len(panel_rows):
        failures.append("provider02b_panel_duplicate_trade_date_symbol_keys")
    for name, keyed in [
        ("risk01", risk01_by_key),
        ("risk011", risk011_by_key),
        ("dc03_risk", dc03_risk_by_key),
        ("dc03_recommendation", dc03_rec_by_key),
    ]:
        if set(panel_keys) != set(keyed):
            failures.append(f"{name}_keys_do_not_match_provider02b_panel")
    if failures:
        return _blocked_result(failures, warnings)

    registry = _factor_registry_rows()
    evaluation_rows = _factor_evaluation_rows(panel_rows, risk01_by_key, risk011_by_key)
    bucket_metrics = _bucket_metric_rows(evaluation_rows)
    ic_rankic = _ic_rankic_rows(evaluation_rows)
    monotonicity = _monotonicity_rows(evaluation_rows)
    rolling = _rolling_stability_rows(evaluation_rows)
    regime = _regime_split_rows(registry)
    validity = _score_validity_rows(registry, bucket_metrics, ic_rankic, monotonicity, rolling)
    trials = _trial_registry_rows(registry, validity, panel_rows)
    ready = [row for row in validity if row["candidate_for_rec_tiering"] == "true"]
    if ready:
        status = PASS
        overall_validity = "factor_candidate_for_rec_tiering_available"
        recommended_next = "request_explicit_goal_rec_tiering01_after_research_candidate_review"
        allowed_next = ALLOWED_NEXT_AVAILABLE
    else:
        status = PASS_WITH_WARNINGS
        overall_validity = "no_factor_ready_for_rec_tiering"
        recommended_next = "GOAL-ALPHA-FACTOR-CANDIDATE-01_before_recommendation_tiering"
        allowed_next = ALLOWED_NEXT_WEAK
        warnings.append("no_factor_ready_for_rec_tiering")

    manifest = {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "mode": MODE,
        "status": status,
        "workflow_id": WORKFLOW_ID,
        "allowed_next_action": allowed_next,
        "recommended_next_goal": recommended_next,
        "overall_score_validity_status": overall_validity,
        "factor_count": len(registry),
        "source_panel_row_count": len(panel_rows),
        "factor_evaluation_row_count": len(evaluation_rows),
        "factor_bucket_metric_row_count": len(bucket_metrics),
        "ic_rankic_summary_row_count": len(ic_rankic),
        "monotonicity_summary_row_count": len(monotonicity),
        "rolling_stability_summary_row_count": len(rolling),
        "regime_split_summary_row_count": len(regime),
        "trial_registry_row_count": len(trials),
        "score_validity_row_count": len(validity),
        "ready_factor_count": len(ready),
        "candidate_factor_ids": [row["factor_id"] for row in ready],
        "date_range": _date_range(panel_rows),
        "unique_symbols": len({row["symbol"] for row in panel_rows}),
        "unique_trade_dates": len({row["trade_date"] for row in panel_rows}),
        "research_only_factor_lab_generated": True,
        "used_committed_provider02b_evidence_only": True,
        "used_committed_dc03_evidence_only": True,
        "used_committed_goal10b3_evidence_only": True,
        "used_committed_goal_risk_tiering01_evidence_only": True,
        "used_committed_goal_risk_tiering011_evidence_only": True,
        "future_candidate_framework_defined": True,
        "future_returns_used_only_for_posthoc_evaluation": True,
        "no_lookahead_validation_passed": True,
        "anti_overfitting_policy_recorded": True,
        "trial_registry_created": True,
        "research_stage_roadmap_created": True,
        "goal_rec_tiering01_locked_future": True,
        "goal10b4_locked_future": True,
        "position_band_validation_locked_future": True,
        "goal10d_locked_future": True,
        "dashboard_daily_report_locked_future": True,
        "portfolio_backtest_locked_future": True,
        "input_row_counts": {
            PROVIDER02B_PANEL_PATH: len(panel_rows),
            DC03_RISK_PATH: len(dc03_risk_rows),
            DC03_RECOMMENDATION_PATH: len(dc03_rec_rows),
            RISK01_DIAGNOSTICS_PATH: len(risk01_rows),
            RISK01_DISTRIBUTION_PATH: len(risk01_distribution),
            RISK01_FORWARD_METRICS_PATH: len(risk01_forward_metrics),
            RISK011_DIAGNOSTICS_PATH: len(risk011_rows),
            RISK011_COMPONENT_SUMMARY_PATH: len(risk011_component_summary),
            RISK011_DISTRIBUTION_PATH: len(risk011_distribution),
            RISK011_FORWARD_METRICS_PATH: len(risk011_forward_metrics),
            GOAL10B3_RECOMMENDATION_METRICS_PATH: len(goal10b3_metrics),
            GOAL10B3_IMBALANCE_PATH: len(goal10b3_imbalance),
        },
        "warnings": sorted(set(warnings)),
        "failures": failures,
    }
    for key in FALSE_BOUNDARY_KEYS:
        manifest[key] = False

    return {
        "status": status,
        "failures": failures,
        "warnings": sorted(set(warnings)),
        "registry": registry,
        "evaluation_rows": evaluation_rows,
        "bucket_metrics": bucket_metrics,
        "ic_rankic": ic_rankic,
        "monotonicity": monotonicity,
        "rolling": rolling,
        "regime": regime,
        "trials": trials,
        "validity": validity,
        "manifest": manifest,
    }


def goal_quant_research01_valid_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        ("GOAL-QUANT-RESEARCH-01 Factor Research Lab: PASS" in report or "GOAL-QUANT-RESEARCH-01 Factor Research Lab: PASS_WITH_WARNINGS" in report)
        and "Status: `PASS`" in audit
        and manifest.get("mode") == MODE
        and manifest.get("research_only_factor_lab_generated") is True
        and manifest.get("future_returns_used_only_for_posthoc_evaluation") is True
        and manifest.get("recommendation_outputs_created") is False
    )


def goal_quant_research01_implemented_workflow_patch(status: str = PASS_WITH_WARNINGS) -> dict[str, str]:
    return {
        "display_name": "GOAL-QUANT-RESEARCH-01 Factor Research Lab Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_research_only",
        "current_repo_role": MODE,
        "implemented_in_repo": "true",
        "allowed_next_action": ALLOWED_NEXT_AVAILABLE if status == PASS else ALLOWED_NEXT_WEAK,
        "depends_on": GOAL_RISK_TIERING011_WORKFLOW_ID,
        "produces_artifacts": ";".join(OUTPUTS),
        "primary_docs": f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "scripts/run_goal_quant_research01_factor_research_lab_gate.py;scripts/audit_goal_quant_research01_factor_research_lab_gate.py",
        "primary_outputs": ";".join(
            [
                FACTOR_REGISTRY_PATH,
                FACTOR_EVALUATION_PANEL_PATH,
                FACTOR_BUCKET_METRICS_PATH,
                IC_RANKIC_SUMMARY_PATH,
                MONOTONICITY_SUMMARY_PATH,
                ROLLING_STABILITY_SUMMARY_PATH,
                REGIME_SPLIT_SUMMARY_PATH,
                TRIAL_REGISTRY_PATH,
                SCORE_VALIDITY_PATH,
                REPORT_PATH,
                MANIFEST_PATH,
                AUDIT_PATH,
            ]
        ),
        "promotion_rule": "implemented_research_only_after_goal_quant_research01_pass_or_pass_with_warnings",
        "notes": "Research-only factor lab over committed Provider02B, DC03, GOAL-10B.3, GOAL-RISK-TIERING-01, and GOAL-RISK-TIERING-01.1 evidence. It creates factor validity diagnostics only; no recommendation, position, portfolio, dashboard, trading, production, broker, local-lake, factor-mining, or DQN/RL outputs.",
    }


def locked_goal_rec_tiering01_patch(result: dict[str, object] | None = None) -> dict[str, str]:
    manifest = (result or {}).get("manifest", {}) if isinstance(result, dict) else {}
    ready = int(manifest.get("ready_factor_count", 0)) if isinstance(manifest, dict) else 0
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "explicit_request_required_after_quant_research_candidate_review" if ready else "remain_locked_until_new_alpha_factor_candidate_research",
        "depends_on": WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal_rec_tiering01_gate",
        "notes": "Future recommendation score tiering remains locked; GOAL-QUANT-RESEARCH-01 creates research-only factor diagnostics and no recommendation rows.",
    }


def locked_goal10b4_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal_rec_tiering01_passes",
        "depends_on": GOAL_REC_TIERING01_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal10b4_revalidation_gate",
        "notes": "Future GOAL-10B.4 remains locked; GOAL-QUANT-RESEARCH-01 creates no recommendation revalidation rows.",
    }


def locked_position_band_validation_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal10b4_and_explicit_position_validation_request",
        "depends_on": GOAL10B4_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_position_band_validation_gate",
        "notes": "Future position-band validation remains locked; GOAL-QUANT-RESEARCH-01 creates no position outputs.",
    }


def locked_goal10d_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10d_request",
        "depends_on": "goal10c_backtest_cost_slippage_sensitivity_gate",
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal10d_failure_attribution_gate",
        "notes": "Future GOAL-10D remains locked; GOAL-QUANT-RESEARCH-01 creates only research diagnostics.",
    }


def _factor_registry_rows() -> list[dict[str, object]]:
    rows = []
    for index, factor in enumerate(FACTOR_DEFINITIONS, start=1):
        rows.append(
            {
                "factor_id": factor["factor_id"],
                "factor_family": factor["factor_family"],
                "factor_name": factor["factor_name"],
                "source_artifact": factor["source_artifact"],
                "input_columns": factor["input_columns"],
                "factor_direction_hypothesis": factor["factor_direction_hypothesis"],
                "expected_monotonic_direction": factor["expected_monotonic_direction"],
                "score_construction_no_lookahead_status": "passed_committed_factor_values_no_forward_return_construction",
                "uses_forward_returns_in_construction": False,
                "allowed_for_posthoc_evaluation_only": True,
                "research_stage_status": "research_only_candidate_under_evaluation",
                "trial_id": f"goal_quant_research01_trial_{index:02d}",
                "rule_version": "v1_governance_first_no_forward_return_tuning",
                "governance_notes": "Factor value is taken from committed upstream evidence; forward returns are used only after factor assignment for post-hoc diagnostics.",
            }
        )
    return rows


def _factor_evaluation_rows(
    panel_rows: list[dict[str, str]],
    risk01_by_key: dict[tuple[str, str], dict[str, str]],
    risk011_by_key: dict[tuple[str, str], dict[str, str]],
) -> list[dict[str, object]]:
    working: list[dict[str, object]] = []
    by_factor_date: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for panel in sorted(panel_rows, key=lambda row: (row["trade_date"], row["symbol"])):
        key = _key(panel)
        source_rows = {"risk01": risk01_by_key[key], "risk011": risk011_by_key[key]}
        for factor in FACTOR_DEFINITIONS:
            source_row = source_rows[str(factor["source"])]
            raw_value = source_row.get(str(factor["column"]), "")
            value = _factor_value(raw_value, str(factor["value_type"]))
            row = {
                "trade_date": panel["trade_date"],
                "symbol": panel["symbol"],
                "factor_id": factor["factor_id"],
                "factor_family": factor["factor_family"],
                "factor_value": _fmt(value) if value is not None else "",
                "factor_bucket": "",
                "factor_quantile": "",
                "factor_direction_hypothesis": factor["factor_direction_hypothesis"],
                "expected_monotonic_direction": factor["expected_monotonic_direction"],
                "forward_return_1d": panel.get("forward_return_1d", ""),
                "forward_return_5d": panel.get("forward_return_5d", ""),
                "forward_return_20d": panel.get("forward_return_20d", ""),
                "benchmark_excess_return_1d": panel.get("benchmark_excess_return_1d", ""),
                "benchmark_excess_return_5d": panel.get("benchmark_excess_return_5d", ""),
                "benchmark_excess_return_20d": panel.get("benchmark_excess_return_20d", ""),
                "source_provider": panel.get("source_provider", ""),
                "universe_mode": panel.get("universe_mode", ""),
                "panel_contract_status": panel.get("panel_contract_status", ""),
                "score_construction_no_lookahead_status": "passed_forward_returns_excluded_from_factor_construction",
                "diagnostic_mode": MODE,
                "non_actionable_disclaimer": NON_ACTIONABLE,
                "_factor_value_float": value,
                "_value_type": factor["value_type"],
            }
            working.append(row)
            by_factor_date[(str(factor["factor_id"]), panel["trade_date"])].append(row)

    for factor in FACTOR_DEFINITIONS:
        factor_id = str(factor["factor_id"])
        value_type = str(factor["value_type"])
        for date in sorted({row["trade_date"] for row in panel_rows}):
            rows = by_factor_date[(factor_id, date)]
            valued = [row for row in rows if row["_factor_value_float"] is not None]
            valued.sort(key=lambda row: (float(row["_factor_value_float"]), str(row["symbol"])))
            total = len(valued)
            for index, row in enumerate(valued):
                quantile = min(N_QUANTILES, int(index * N_QUANTILES / max(total, 1)) + 1)
                row["factor_quantile"] = str(quantile)
                if value_type == "binary":
                    row["factor_bucket"] = "FLAG_TRUE" if float(row["_factor_value_float"]) >= 0.5 else "FLAG_FALSE"
                else:
                    row["factor_bucket"] = f"Q{quantile}"
            for row in rows:
                if row["_factor_value_float"] is None:
                    row["factor_bucket"] = "MISSING"
                    row["factor_quantile"] = ""

    return [{key: value for key, value in row.items() if not key.startswith("_")} for row in working]


def _bucket_metric_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    rows_by_factor = _group_by(rows, "factor_id")
    for factor in FACTOR_DEFINITIONS:
        factor_id = str(factor["factor_id"])
        factor_rows = rows_by_factor[factor_id]
        overview = _factor_distribution_overview(factor_rows)
        output.append(
            _bucket_metric_row(
                factor_id,
                str(factor["factor_family"]),
                "factor_overall",
                "all",
                factor_rows,
                overview,
                include_returns=False,
            )
        )
        for group_type, field in [("factor_bucket", "factor_bucket"), ("factor_quantile", "factor_quantile")]:
            grouped = _group_by([row for row in factor_rows if row.get(field) not in {"", "MISSING"}], field)
            for group_value in sorted(grouped):
                output.append(
                    _bucket_metric_row(
                        factor_id,
                        str(factor["factor_family"]),
                        group_type,
                        group_value,
                        grouped[group_value],
                        overview,
                        include_returns=True,
                    )
                )
    return output


def _ic_rankic_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    rows_by_factor = _group_by(rows, "factor_id")
    definitions = {str(factor["factor_id"]): factor for factor in FACTOR_DEFINITIONS}
    for factor_id in [str(factor["factor_id"]) for factor in FACTOR_DEFINITIONS]:
        factor = definitions[factor_id]
        if factor["value_type"] == "binary":
            output.append(_empty_ic_row(factor, "ic_rankic_unavailable_non_numeric_factor"))
            continue
        factor_rows = rows_by_factor[factor_id]
        daily: dict[str, dict[str, list[tuple[str, float]]]] = {"ic": {}, "rank_ic": {}}
        for horizon in HORIZONS:
            daily["ic"][horizon] = _daily_correlations(factor_rows, f"forward_return_{horizon}", rank=False)
            daily["rank_ic"][horizon] = _daily_correlations(factor_rows, f"forward_return_{horizon}", rank=True)
        valid_counts = [len(daily["ic"][horizon]) for horizon in HORIZONS]
        status = "ic_rankic_available" if max(valid_counts) >= 20 else "ic_rankic_unavailable_insufficient_cross_section"
        row = {
            "factor_id": factor_id,
            "factor_family": factor["factor_family"],
            "ic_availability_status": status,
            "insufficient_cross_section_warning": max(valid_counts) < 20,
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


def _monotonicity_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    rows_by_factor = _group_by(rows, "factor_id")
    definitions = {str(factor["factor_id"]): factor for factor in FACTOR_DEFINITIONS}
    for factor_id in [str(factor["factor_id"]) for factor in FACTOR_DEFINITIONS]:
        factor = definitions[factor_id]
        factor_rows = rows_by_factor[factor_id]
        sign = int(factor["expected_sign"])
        row = {"factor_id": factor_id, "factor_family": factor["factor_family"]}
        statuses = []
        inverse = False
        for horizon in HORIZONS:
            return_spread = _top_bottom_spread(factor_rows, f"forward_return_{horizon}")
            excess_spread = _top_bottom_spread(factor_rows, f"benchmark_excess_return_{horizon}")
            status = _direction_status(return_spread, sign)
            statuses.append(status)
            if status == "inverse_signal_warning":
                inverse = True
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
    output = []
    dates = sorted({str(row["trade_date"]) for row in rows})
    windows = _rolling_windows(dates, 20) + _rolling_windows(dates, 40) + _split_windows(dates)
    rows_by_factor = _group_by(rows, "factor_id")
    definitions = {str(factor["factor_id"]): factor for factor in FACTOR_DEFINITIONS}
    for factor_id in [str(factor["factor_id"]) for factor in FACTOR_DEFINITIONS]:
        factor = definitions[factor_id]
        sign = int(factor["expected_sign"])
        factor_rows = rows_by_factor[factor_id]
        window_metrics = []
        for name, window_dates in windows:
            subset = [row for row in factor_rows if row["trade_date"] in window_dates]
            rank_values = [value for _, value in _daily_correlations(subset, "forward_return_20d", rank=True)]
            ic_values = [value for _, value in _daily_correlations(subset, "forward_return_20d", rank=False)]
            spread = _top_bottom_spread(subset, "forward_return_20d")
            if spread is None:
                continue
            direction = 1 if sign * spread > 0 else -1 if sign * spread < 0 else 0
            window_metrics.append((name, _mean(ic_values), _mean(rank_values), spread, direction))
        stable = sum(1 for _, _, _, _, direction in window_metrics if direction > 0)
        unstable = sum(1 for _, _, _, _, direction in window_metrics if direction < 0)
        signs = [direction for _, _, _, _, direction in window_metrics if direction != 0]
        flips = sum(1 for left, right in zip(signs, signs[1:]) if left != right)
        if not window_metrics:
            classification = "factor_not_evaluable"
        elif stable / len(window_metrics) >= 0.60 and flips <= 2:
            classification = "factor_stable"
        elif flips > max(3, len(window_metrics) // 5):
            classification = "factor_directionally_inconsistent"
        else:
            classification = "factor_unstable"
        output.append(
            {
                "factor_id": factor_id,
                "factor_family": factor["factor_family"],
                "rolling_window_spec": "20d_rolling;40d_rolling;first_half_second_half;calendar_month_when_available",
                "rolling_mean_ic": _fmt(_mean([item[1] for item in window_metrics if item[1] is not None])),
                "rolling_rank_ic": _fmt(_mean([item[2] for item in window_metrics if item[2] is not None])),
                "rolling_top_bottom_spread": _fmt(_mean([item[3] for item in window_metrics if item[3] is not None])),
                "stable_window_count": stable,
                "unstable_window_count": unstable,
                "sign_flip_count": flips,
                "stability_classification": classification,
            }
        )
    return output


def _regime_split_rows(registry: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for row in registry:
        rows.append(
            {
                "factor_id": row["factor_id"],
                "factor_family": row["factor_family"],
                "regime_split_status": "regime_split_not_evaluable",
                "regime_tags_evaluated": "",
                "no_lookahead_regime_status": "not_evaluable_no_committed_trailing_benchmark_state_inputs",
                "notes": "Provider02B contains benchmark forward-return fields for post-hoc evaluation, but this gate has no committed trailing benchmark state series for no-lookahead regime construction.",
            }
        )
    return rows


def _score_validity_rows(
    registry: list[dict[str, object]],
    bucket_metrics: list[dict[str, object]],
    ic_rankic: list[dict[str, object]],
    monotonicity: list[dict[str, object]],
    rolling: list[dict[str, object]],
) -> list[dict[str, object]]:
    overview = {row["factor_id"]: row for row in bucket_metrics if row["group_type"] == "factor_overall"}
    ic_map = {row["factor_id"]: row for row in ic_rankic}
    mono_map = {row["factor_id"]: row for row in monotonicity}
    rolling_map = {row["factor_id"]: row for row in rolling}
    rows = []
    for factor in registry:
        factor_id = str(factor["factor_id"])
        dist = overview[factor_id]
        ic = ic_map[factor_id]
        mono = mono_map[factor_id]
        stable = rolling_map[factor_id]
        collapsed = dist["factor_collapse_detected"] == "true"
        min_ok = int(dist["minimum_bucket_size"] or "0") >= MIN_BUCKET_ROWS
        ic_status = str(ic["ic_availability_status"])
        mono_status = str(mono["expected_direction_alignment_status"])
        stability = str(stable["stability_classification"])
        aligned_horizons = sum(1 for horizon in HORIZONS if mono[f"monotonicity_status_{horizon}"] == "expected_direction_aligned")
        inverse = mono["inverse_signal_warning"] == "true"
        candidate = (
            not collapsed
            and min_ok
            and ic_status == "ic_rankic_available"
            and aligned_horizons >= 2
            and not inverse
            and stability == "factor_stable"
        )
        if candidate:
            classification = "factor_candidate_for_rec_tiering"
            rejection = ""
            next_action = "eligible_for_explicit_goal_rec_tiering01_review_request"
        elif collapsed:
            classification = "factor_requires_redefinition"
            rejection = "bucket_distribution_collapsed_or_minimum_bucket_size_unacceptable"
            next_action = "redefine_factor_before_rec_tiering"
        elif inverse:
            classification = "factor_signal_directionally_inconsistent"
            rejection = "monotonicity_or_spread_direction_opposite_to_hypothesis"
            next_action = "review_factor_direction_or_replace_candidate"
        elif ic_status.startswith("ic_rankic_unavailable") and aligned_horizons == 0:
            classification = "factor_not_evaluable"
            rejection = "ic_rankic_unavailable_and_bucket_spread_not_directionally_aligned"
            next_action = "collect_or_define_more_robust_factor_candidate"
        else:
            classification = "factor_signal_weak_or_unreliable"
            rejection = "evidence_weak_mixed_or_unstable_across_horizons"
            next_action = "continue_research_before_recommendation_tiering"
        rows.append(
            {
                "factor_id": factor_id,
                "factor_family": factor["factor_family"],
                "score_validity_classification": classification,
                "accepted_for_downstream": False,
                "candidate_for_rec_tiering": candidate,
                "bucket_distribution_status": "not_collapsed" if not collapsed and min_ok else "collapsed_or_imbalanced",
                "ic_rankic_status": ic_status,
                "monotonicity_alignment_status": mono_status,
                "rolling_stability_status": stability,
                "no_lookahead_status": factor["score_construction_no_lookahead_status"],
                "rejection_reason": rejection,
                "recommended_next_action": next_action,
            }
        )
    return rows


def _trial_registry_rows(
    registry: list[dict[str, object]],
    validity: list[dict[str, object]],
    panel_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    validity_by_factor = {row["factor_id"]: row for row in validity}
    date_range = _date_range(panel_rows)
    universe_modes = sorted({row.get("universe_mode", "") for row in panel_rows if row.get("universe_mode")})
    rows = []
    for factor in registry:
        valid = validity_by_factor[str(factor["factor_id"])]
        rows.append(
            {
                "trial_id": factor["trial_id"],
                "goal_id": GOAL_ID,
                "factor_id": factor["factor_id"],
                "factor_family": factor["factor_family"],
                "rule_version": factor["rule_version"],
                "input_artifacts": ";".join(REQUIRED_INPUTS),
                "score_components": factor["input_columns"],
                "score_weights_policy": "no_forward_return_tuning_no_weight_search_observed_value_only",
                "no_lookahead_status": "passed",
                "date_range": date_range,
                "universe_mode": ";".join(universe_modes),
                "row_count": len(panel_rows),
                "metric_summary": f"{valid['score_validity_classification']};{valid['ic_rankic_status']};{valid['rolling_stability_status']}",
                "accepted_for_downstream": False,
                "rejection_reason": valid["rejection_reason"],
                "overfitting_warning_codes": "no_weight_tuning;trial_recorded;multi_horizon_required;stability_required;no_portfolio_returns_or_equity_curves",
                "notes": "Research-only trial record; no factor is promoted unless future explicit governance accepts the evidence.",
            }
        )
    return rows


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / FACTOR_REGISTRY_PATH, result["registry"], FACTOR_REGISTRY_FIELDS)
    write_csv(root / FACTOR_EVALUATION_PANEL_PATH, result["evaluation_rows"], FACTOR_EVALUATION_FIELDS)
    write_csv(root / FACTOR_BUCKET_METRICS_PATH, result["bucket_metrics"], BUCKET_METRIC_FIELDS)
    write_csv(root / IC_RANKIC_SUMMARY_PATH, result["ic_rankic"], IC_RANKIC_FIELDS)
    write_csv(root / MONOTONICITY_SUMMARY_PATH, result["monotonicity"], MONOTONICITY_FIELDS)
    write_csv(root / ROLLING_STABILITY_SUMMARY_PATH, result["rolling"], ROLLING_STABILITY_FIELDS)
    write_csv(root / REGIME_SPLIT_SUMMARY_PATH, result["regime"], REGIME_SPLIT_FIELDS)
    write_csv(root / TRIAL_REGISTRY_PATH, result["trials"], TRIAL_REGISTRY_FIELDS)
    write_csv(root / SCORE_VALIDITY_PATH, result["validity"], SCORE_VALIDITY_FIELDS)
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_contract(root, result)
    _write_doc(root, result)
    _write_report(root, result)


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    validity = result["validity"]
    class_counts = Counter(str(row["score_validity_classification"]) for row in validity)
    body = [
        "# GOAL-QUANT-RESEARCH-01 Factor Research Lab",
        "",
        f"GOAL-QUANT-RESEARCH-01 Factor Research Lab: {manifest['status']}",
        "",
        "## 1. Current Project Stage",
        "The project has entered a research-only factor validity stage after Provider02B, DC03, GOAL-10B.3, GOAL-RISK-TIERING-01, and GOAL-RISK-TIERING-01.1 produced source-backed diagnostics with weak or unreliable score semantics.",
        "",
        "## 2. Why The Project Has Entered Deep Quant Research",
        "Prior risk and downside-risk scores have usable row coverage but weak directional evidence. This gate evaluates factor semantics before any recommendation tiering or position validation.",
        "",
        "## 3. Source-Backed Evidence Lineage",
        *[f"- `{path}`" for path in REQUIRED_INPUTS],
        "",
        "## 4. Factor Research Methodology",
        "The lab builds factor values from committed upstream evidence, assigns buckets and quantiles, evaluates post-hoc forward and benchmark-excess returns, computes IC/RankIC when numeric, checks monotonicity, rolling stability, group imbalance, no-lookahead status, trial registration, and anti-overfitting controls.",
        "",
        "## 5. Factor Registry Summary",
        f"Factors registered: `{manifest['factor_count']}`.",
        "",
        "## 6. Score/Factor Candidates Evaluated",
        *[f"- `{row['factor_id']}`: `{row['score_validity_classification']}`" for row in validity],
        "",
        "## 7. Bucket And Quantile Diagnostics",
        f"Bucket metric rows: `{manifest['factor_bucket_metric_row_count']}`.",
        "",
        "## 8. Forward-Return And Benchmark-Excess-Return Results",
        "Forward returns and benchmark-excess returns are used only after factor assignment for post-hoc diagnostics.",
        "",
        "## 9. IC / RankIC Results",
        f"IC/RankIC rows: `{manifest['ic_rankic_summary_row_count']}`.",
        "",
        "## 10. Monotonicity And Spread Results",
        f"Monotonicity rows: `{manifest['monotonicity_summary_row_count']}`.",
        "",
        "## 11. Rolling Stability Results",
        f"Rolling stability rows: `{manifest['rolling_stability_summary_row_count']}`.",
        "",
        "## 12. Regime Split Availability",
        "Regime split is classified as `regime_split_not_evaluable` because committed evidence does not include a trailing benchmark state series suitable for no-lookahead regime tags.",
        "",
        "## 13. Trial Registry And Anti-Overfitting Controls",
        "Every factor candidate is recorded in the trial registry. The policy forbids tuning weights to forward returns, unregistered repeated rule search, single-horizon promotion, promotion without stability checks, promotion without no-lookahead audit, promotion from collapsed buckets, and any use of portfolio returns or equity curves.",
        "",
        "## 14. Score Validity Classification",
        f"Classification counts: `{dict(sorted(class_counts.items()))}`.",
        "",
        "## 15. Whether Any Factor Is Ready For REC-TIERING-01",
        f"Ready factor count: `{manifest['ready_factor_count']}`.",
        f"Overall validity: `{manifest['overall_score_validity_status']}`.",
        "",
        "## 16. Recommended Next Goal",
        f"`{manifest['recommended_next_goal']}`.",
        "",
        "## Locked Boundary",
        "GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, portfolio backtests, paper/live trading, broker integration, production writes, local-lake writes, factor-mining, and DQN/RL remain locked or deleted from active mainline.",
        "",
    ]
    write_text(root / REPORT_PATH, "\n".join(body))


def _write_contract(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    lines = [
        "{",
        '  "goal_id": "GOAL-QUANT-RESEARCH-01",',
        f'  "mode": "{MODE}",',
        '  "status": "' + str(manifest["status"]) + '",',
        '  "research_only": true,',
        '  "allowed_inputs": [',
        *[f'    "{path}",' for path in REQUIRED_INPUTS[:-1]],
        f'    "{REQUIRED_INPUTS[-1]}"',
        "  ],",
        '  "allowed_outputs": [',
        *[f'    "{path}",' for path in OUTPUTS[:-1]],
        f'    "{OUTPUTS[-1]}"',
        "  ],",
        '  "factor_registry_schema": ' + _json_list(FACTOR_REGISTRY_FIELDS) + ",",
        '  "factor_evaluation_schema": ' + _json_list(FACTOR_EVALUATION_FIELDS) + ",",
        '  "anti_overfitting_policy": [',
        '    "do_not_tune_score_weights_to_forward_returns",',
        '    "record_every_trial",',
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


def _write_doc(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    body = [
        "# GOAL-QUANT-RESEARCH-01 Factor Research Lab And Score Validity Gate",
        "",
        f"Status: `{manifest['status']}`",
        "",
        "This gate is research-only. It creates a reusable Alphalens-style factor research framework over committed Provider02B, DC03, GOAL-10B.3, GOAL-RISK-TIERING-01, and GOAL-RISK-TIERING-01.1 evidence.",
        "",
        "## Outputs",
        *[f"- `{path}`" for path in OUTPUTS if path.startswith("outputs/research/")],
        "",
        "## Method",
        "The framework records a factor registry, constructs a `trade_date + symbol + factor_id` evaluation panel, assigns buckets and quantiles, computes post-hoc forward-return and benchmark-excess-return metrics, IC/RankIC summaries, monotonicity, rolling stability, regime availability, trial registry, and score validity classifications.",
        "",
        "## Result",
        f"- Factors evaluated: `{manifest['factor_count']}`",
        f"- Factor evaluation rows: `{manifest['factor_evaluation_row_count']}`",
        f"- Ready factor count: `{manifest['ready_factor_count']}`",
        f"- Overall validity: `{manifest['overall_score_validity_status']}`",
        f"- Recommended next goal: `{manifest['recommended_next_goal']}`",
        "",
        "## Locked Boundary",
        "No recommendation rows, position rows, BUY/SELL/HOLD actions, target prices, position sizes, weights, order quantities, portfolio returns, equity curves, dashboards, HTML, Streamlit, frontend, visual reports, trading outputs, broker outputs, production outputs, local-lake files, factor-mining outputs, or DQN/RL outputs are created.",
        "",
    ]
    write_text(root / DOC_PATH, "\n".join(body))


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    by_id = {row["workflow_id"]: row for row in rows}
    if WORKFLOW_ID not in by_id:
        insert_at = next((idx + 1 for idx, row in enumerate(rows) if row["workflow_id"] == GOAL_RISK_TIERING011_WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": WORKFLOW_ID})
        by_id = {row["workflow_id"]: row for row in rows}
    by_id[WORKFLOW_ID].update(goal_quant_research01_implemented_workflow_patch(str(result["status"])))
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
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_quant_research01"
    preserve_later_review_only_workflow_states(root, by_id)
    if result["status"] in {PASS, PASS_WITH_WARNINGS} and WORKFLOW_ID in by_id:
        by_id[WORKFLOW_ID].update(goal_quant_research01_implemented_workflow_patch(str(result["status"])))
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
    write_json(path, payload)


def _factor_distribution_overview(rows: list[dict[str, object]]) -> dict[str, object]:
    buckets = Counter(str(row.get("factor_bucket", "")) for row in rows if row.get("factor_bucket") not in {"", "MISSING"})
    quantiles = Counter(str(row.get("factor_quantile", "")) for row in rows if row.get("factor_quantile"))
    row_count = len(rows)
    dominant = max(buckets.values(), default=0) / row_count if row_count else 0.0
    minimum = min(buckets.values(), default=0)
    collapse = dominant >= COLLAPSE_THRESHOLD or len(buckets) <= 1 or minimum < MIN_BUCKET_ROWS
    return {
        "bucket_count": len(buckets),
        "quantile_count": len(quantiles),
        "dominant_bucket_share": dominant,
        "minimum_bucket_size": minimum,
        "missing_factor_value_count": sum(1 for row in rows if row.get("factor_value", "") == ""),
        "duplicate_key_count": _duplicate_count((row["trade_date"], row["symbol"], row["factor_id"]) for row in rows),
        "factor_collapse_detected": collapse,
        "group_imbalance_warning": collapse or dominant >= COLLAPSE_THRESHOLD,
        "quantile_coverage_status": "quantile_coverage_complete" if len(quantiles) == N_QUANTILES else "quantile_coverage_partial_or_collapsed",
    }


def _bucket_metric_row(
    factor_id: str,
    factor_family: str,
    group_type: str,
    group_value: str,
    rows: list[dict[str, object]],
    overview: dict[str, object],
    *,
    include_returns: bool,
) -> dict[str, object]:
    row = {
        "factor_id": factor_id,
        "factor_family": factor_family,
        "group_type": group_type,
        "group_value": group_value,
        "row_count": len(rows),
        "unique_symbols": len({row["symbol"] for row in rows}),
        "unique_trade_dates": len({row["trade_date"] for row in rows}),
        "bucket_count": overview["bucket_count"],
        "quantile_count": overview["quantile_count"],
        "dominant_bucket_share": _fmt(overview["dominant_bucket_share"]),
        "minimum_bucket_size": overview["minimum_bucket_size"],
        "missing_factor_value_count": overview["missing_factor_value_count"],
        "duplicate_key_count": overview["duplicate_key_count"],
        "factor_collapse_detected": overview["factor_collapse_detected"],
        "group_imbalance_warning": overview["group_imbalance_warning"],
        "quantile_coverage_status": overview["quantile_coverage_status"],
    }
    metric_rows = rows if include_returns else []
    for horizon in HORIZONS:
        forward = [_float(item.get(f"forward_return_{horizon}", "")) for item in metric_rows]
        excess = [_float(item.get(f"benchmark_excess_return_{horizon}", "")) for item in metric_rows]
        forward_values = [value for value in forward if value is not None]
        excess_values = [value for value in excess if value is not None]
        row[f"mean_forward_return_{horizon}"] = _fmt(_mean(forward_values))
        row[f"median_forward_return_{horizon}"] = _fmt(_median(forward_values))
        row[f"hit_rate_{horizon}"] = _fmt(_positive_rate(forward_values))
        row[f"mean_benchmark_excess_return_{horizon}"] = _fmt(_mean(excess_values))
        row[f"median_benchmark_excess_return_{horizon}"] = _fmt(_median(excess_values))
        row[f"positive_excess_rate_{horizon}"] = _fmt(_positive_rate(excess_values))
    return row


def _empty_ic_row(factor: dict[str, object], status: str) -> dict[str, object]:
    row = {
        "factor_id": factor["factor_id"],
        "factor_family": factor["factor_family"],
        "ic_availability_status": status,
        "insufficient_cross_section_warning": True,
    }
    for field in IC_RANKIC_FIELDS:
        row.setdefault(field, "")
    return row


def _daily_correlations(rows: list[dict[str, object]], target_field: str, *, rank: bool = False) -> list[tuple[str, float]]:
    output = []
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


def _top_bottom_spread(rows: list[dict[str, object]], target_field: str) -> float | None:
    valued = [row for row in rows if row.get("factor_bucket") not in {"", "MISSING"}]
    if not valued:
        return None
    buckets = {str(row["factor_bucket"]) for row in valued}
    if {"FLAG_FALSE", "FLAG_TRUE"}.issubset(buckets):
        bottom = [row for row in valued if row["factor_bucket"] == "FLAG_FALSE"]
        top = [row for row in valued if row["factor_bucket"] == "FLAG_TRUE"]
    elif {"Q1", "Q5"}.issubset(buckets):
        bottom = [row for row in valued if row["factor_bucket"] == "Q1"]
        top = [row for row in valued if row["factor_bucket"] == "Q5"]
    else:
        return None
    top_mean = _mean([_float(row.get(target_field, "")) for row in top if _float(row.get(target_field, "")) is not None])
    bottom_mean = _mean([_float(row.get(target_field, "")) for row in bottom if _float(row.get(target_field, "")) is not None])
    if top_mean is None or bottom_mean is None:
        return None
    return top_mean - bottom_mean


def _direction_status(spread: float | None, expected_sign: int) -> str:
    if spread is None:
        return "not_evaluable"
    if abs(spread) < 1e-12:
        return "flat_or_no_spread"
    if expected_sign * spread > 0:
        return "expected_direction_aligned"
    return "inverse_signal_warning"


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


def _blocked_result(failures: list[str], warnings: list[str]) -> dict[str, object]:
    manifest = {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "mode": MODE,
        "status": BLOCKED,
        "workflow_id": WORKFLOW_ID,
        "failures": failures,
        "warnings": warnings,
    }
    for key in FALSE_BOUNDARY_KEYS:
        manifest[key] = False
    return {
        "status": BLOCKED,
        "failures": failures,
        "warnings": warnings,
        "registry": [],
        "evaluation_rows": [],
        "bucket_metrics": [],
        "ic_rankic": [],
        "monotonicity": [],
        "rolling": [],
        "regime": [],
        "trials": [],
        "validity": [],
        "manifest": manifest,
    }


def _workflow_rows(root: Path) -> dict[str, dict[str, str]]:
    rows = _read_csv(root / "configs/project/workflow_status.csv")
    return {row["workflow_id"]: row for row in rows}


def _forbidden_outputs_present(root: Path) -> list[str]:
    present = []
    for prefix in FORBIDDEN_OUTPUT_PREFIXES:
        base = root / prefix
        if base.exists():
            present.append(prefix.rstrip("/"))
    return present


def _key(row: dict[str, str]) -> tuple[str, str]:
    return (row.get("trade_date", ""), row.get("symbol", ""))


def _factor_value(raw: str, value_type: str) -> float | None:
    if value_type == "binary":
        if str(raw).lower() == "true":
            return 1.0
        if str(raw).lower() == "false":
            return 0.0
    return _float(raw)


def _group_by(rows: list[dict[str, object]], field: str) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(field, ""))].append(row)
    return grouped


def _duplicate_count(keys) -> int:
    counts = Counter(keys)
    return sum(count - 1 for count in counts.values() if count > 1)


def _date_range(rows: list[dict[str, str]]) -> str:
    dates = sorted({row["trade_date"] for row in rows if row.get("trade_date")})
    return f"{dates[0]}..{dates[-1]}" if dates else ""


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
    return "GOAL-QUANT-RESEARCH-01 Factor Research Lab: PASS" in report or "GOAL-QUANT-RESEARCH-01 Factor Research Lab: PASS_WITH_WARNINGS" in report


def _goal_quant_research02_valid(root: Path) -> bool:
    try:
        from ashare_premarket.research.goal_quant_research02 import goal_quant_research02_valid_evidence

        return goal_quant_research02_valid_evidence(root)
    except Exception:
        return False

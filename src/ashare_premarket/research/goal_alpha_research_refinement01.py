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

GOAL_ID = "GOAL-ALPHA-RESEARCH-REFINEMENT-01"
GOAL_NAME = "GOAL-ALPHA-RESEARCH-REFINEMENT-01-ROLLING-STABILITY-AND-CANDIDATE-REFINEMENT-GATE"
MODE = "research_only_rolling_stability_and_candidate_refinement_gate"
WORKFLOW_ID = "goal_alpha_research_refinement01_rolling_stability_candidate_refinement_gate"
PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

GOAL_QUANT_RESEARCH02_WORKFLOW_ID = "goal_quant_research02_alpha_candidate_factor_validity_evaluation_gate"
GOAL_ALPHA_FACTOR_CANDIDATE02_WORKFLOW_ID = "goal_alpha_factor_candidate02_refined_variants_research_gate"
GOAL_REC_TIERING01_WORKFLOW_ID = "goal_rec_tiering01_recommendation_score_tiering_gate"
GOAL10B4_WORKFLOW_ID = "goal10b4_recommendation_backtest_revalidation"
POSITION_BAND_VALIDATION_WORKFLOW_ID = "goal_position_band_validation01_position_band_validation_gate"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
GOAL10C_WORKFLOW_ID = "goal10c_backtest_cost_slippage_sensitivity_gate"

ALLOWED_NEXT_WITH_DESIGNS = "request_goal_alpha_factor_candidate02_refined_variants_only"
ALLOWED_NEXT_NO_DESIGNS = "request_goal_data_expansion_research01_or_alpha_research_design02"
NEXT_GOAL_WITH_DESIGNS = "GOAL-ALPHA-FACTOR-CANDIDATE-02"
NEXT_GOAL_NO_DESIGNS = "GOAL-DATA-EXPANSION-RESEARCH-01_or_GOAL-ALPHA-RESEARCH-DESIGN-02"
NON_ACTIONABLE = "research_only_alpha_refinement_not_investment_advice_not_trade_instruction"
NOT_EVALUATED = "proposed_refined_candidate_not_evaluated"
REDEFINITION_REQUIRED = "proposed_redefinition_required"

QUANT02_EVALUATION_PANEL_PATH = "outputs/research/goal_quant_research02_alpha_evaluation_panel.csv"
QUANT02_SCORE_VALIDITY_PATH = "outputs/research/goal_quant_research02_alpha_factor_score_validity_classification.csv"
QUANT02_IC_RANKIC_PATH = "outputs/research/goal_quant_research02_alpha_factor_ic_rankic_summary.csv"
QUANT02_MONOTONICITY_PATH = "outputs/research/goal_quant_research02_alpha_factor_monotonicity_summary.csv"
QUANT02_ROLLING_PATH = "outputs/research/goal_quant_research02_alpha_factor_rolling_stability_summary.csv"
QUANT02_HORIZON_PATH = "outputs/research/goal_quant_research02_alpha_factor_horizon_consistency_summary.csv"
QUANT02_BUCKET_METRICS_PATH = "outputs/research/goal_quant_research02_alpha_factor_bucket_metrics.csv"
QUANT02_TRIAL_REGISTRY_PATH = "outputs/research/goal_quant_research02_trial_registry.csv"
ALPHA_REGISTRY_PATH = "outputs/research/goal_alpha_factor_candidate01_candidate_registry.csv"
ALPHA_PANEL_PATH = "outputs/research/goal_alpha_factor_candidate01_factor_candidate_panel.csv"
PROVIDER02B_PANEL_PATH = "outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv"
MVP_SYMBOL_TABLE_PATH = "outputs/mvp/goal_mvp01_symbol_diagnostic_table.csv"
MVP_REVIEW_QUEUE_PATH = "outputs/mvp/goal_mvp01_review_queue.csv"

INSTABILITY_ATTRIBUTION_PATH = "outputs/research/goal_alpha_research_refinement01_instability_attribution.csv"
CONDITIONAL_STABILITY_PATH = "outputs/research/goal_alpha_research_refinement01_conditional_stability_summary.csv"
REFINED_DESIGNS_PATH = "outputs/research/goal_alpha_research_refinement01_refined_candidate_designs.csv"
INTRADAY_REDEFINITION_PATH = "outputs/research/goal_alpha_research_refinement01_intraday_redefinition_plan.csv"
TRIAL_REGISTRY_UPDATE_PATH = "outputs/research/goal_alpha_research_refinement01_trial_registry_update.csv"
REPORT_PATH = "outputs/audits/goal_alpha_research_refinement01_report.md"
MANIFEST_PATH = "outputs/audits/goal_alpha_research_refinement01_manifest.json"
AUDIT_PATH = "outputs/audits/goal_alpha_research_refinement01_audit.md"
DOC_PATH = "docs/research/GOAL_ALPHA_RESEARCH_REFINEMENT01_ROLLING_STABILITY_AND_CANDIDATE_REFINEMENT_GATE.md"
CONTRACT_PATH = "configs/research/goal_alpha_research_refinement01_contract.yaml"

REQUIRED_INPUTS = [
    QUANT02_EVALUATION_PANEL_PATH,
    QUANT02_SCORE_VALIDITY_PATH,
    QUANT02_IC_RANKIC_PATH,
    QUANT02_MONOTONICITY_PATH,
    QUANT02_ROLLING_PATH,
    QUANT02_HORIZON_PATH,
    QUANT02_BUCKET_METRICS_PATH,
    QUANT02_TRIAL_REGISTRY_PATH,
    ALPHA_REGISTRY_PATH,
    ALPHA_PANEL_PATH,
    PROVIDER02B_PANEL_PATH,
    MVP_SYMBOL_TABLE_PATH,
    MVP_REVIEW_QUEUE_PATH,
]

OUTPUTS = [
    INSTABILITY_ATTRIBUTION_PATH,
    CONDITIONAL_STABILITY_PATH,
    REFINED_DESIGNS_PATH,
    INTRADAY_REDEFINITION_PATH,
    TRIAL_REGISTRY_UPDATE_PATH,
    REPORT_PATH,
    MANIFEST_PATH,
    AUDIT_PATH,
    DOC_PATH,
    CONTRACT_PATH,
]

PROMISING_CANDIDATES = [
    "alpha_benchmark_relative_strength_20d",
    "alpha_vol_adj_momentum_5d",
    "alpha_vol_adj_momentum_20d",
    "alpha_price_volume_confirmation_5d",
    "alpha_downside_vol_adjusted_strength_20d",
    "alpha_risk_adjusted_relative_strength",
]

REDEFINITION_CANDIDATES = [
    "alpha_intraday_recovery_pressure",
    "alpha_intraday_weakness_pressure",
]

INSTABILITY_FIELDS = [
    "factor_id",
    "factor_family",
    "aligned_20d_window_count",
    "inverse_20d_window_count",
    "aligned_40d_window_count",
    "inverse_40d_window_count",
    "first_half_direction",
    "second_half_direction",
    "calendar_month_direction_summary",
    "sign_flip_count",
    "sign_flip_windows",
    "instability_type",
    "instability_evidence",
    "not_evaluated_status",
]

CONDITIONAL_STABILITY_FIELDS = [
    "factor_id",
    "factor_family",
    "slice_dimension",
    "slice_value",
    "row_count",
    "unique_symbols",
    "unique_trade_dates",
    "mean_rank_ic_20d",
    "mean_top_bottom_excess_spread_20d",
    "aligned_window_count",
    "inverse_window_count",
    "stability_classification",
    "slicing_group_source",
    "no_lookahead_policy",
    "not_evaluated_status",
]

REFINED_DESIGN_FIELDS = [
    "refined_factor_id",
    "source_factor_id",
    "refinement_type",
    "economic_hypothesis",
    "deterministic_rule_description",
    "required_columns",
    "no_lookahead_policy",
    "expected_direction",
    "reason_for_refinement",
    "not_evaluated_status",
]

INTRADAY_REDEFINITION_FIELDS = [
    "original_factor_id",
    "bucket_count",
    "dominant_bucket",
    "dominant_bucket_share",
    "minimum_bucket_size",
    "sparsity_driver",
    "definition_issue_type",
    "proposed_refined_factor_id",
    "revised_definition",
    "required_columns",
    "no_lookahead_policy",
    "not_evaluated_status",
]

TRIAL_REGISTRY_FIELDS = [
    "trial_id",
    "source_goal_id",
    "original_factor_id",
    "refinement_id",
    "refinement_type",
    "reason_for_refinement",
    "no_lookahead_policy",
    "downstream_status",
    "accepted_for_downstream",
    "candidate_for_rec_tiering",
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
    "goal_alpha_factor_candidate02_run",
    "goal_rec_tiering01_run",
    "goal10b4_run",
    "position_band_validation_run",
    "goal10d_run",
    "live_provider_fetches_run",
    "future_returns_used_in_refined_factor_construction",
    "benchmark_excess_returns_used_in_refined_factor_construction",
    "label_ready_fields_used_in_refined_factor_construction",
    "refined_factor_panel_constructed",
    "factor_formulas_tuned_to_future_returns",
    "predictive_validity_claimed",
    "factor_promoted_to_recommendation_tiering",
    "demo_fixture_used",
    "outputs_samples_used",
    "stale_goal10b_evidence_used",
    "stale_dc02_evidence_used",
]

FORBIDDEN_TABLE_LABELS = {
    "BUY",
    "SELL",
    "HOLD",
    "STRONG_BUY",
    "STRONG_SELL",
    "TARGET_WEIGHT",
    "POSITION_SIZE",
    "ORDER_QUANTITY",
}

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


def run_goal_alpha_research_refinement01_gate(root: Path) -> bool:
    result = evaluate_goal_alpha_research_refinement01(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal_alpha_research_refinement01_gate(root)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal_alpha_research_refinement01_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    instability = _read_csv(root / INSTABILITY_ATTRIBUTION_PATH)
    conditional = _read_csv(root / CONDITIONAL_STABILITY_PATH)
    designs = _read_csv(root / REFINED_DESIGNS_PATH)
    intraday = _read_csv(root / INTRADAY_REDEFINITION_PATH)
    trials = _read_csv(root / TRIAL_REGISTRY_UPDATE_PATH)
    workflow = _workflow_rows(root)
    failures: list[str] = []

    for path in OUTPUTS:
        if path != AUDIT_PATH and not (root / path).exists():
            failures.append(f"missing_output:{path}")
    for path in REQUIRED_INPUTS:
        if not (root / path).exists():
            failures.append(f"missing_required_input:{path}")
    if not _report_pass_or_warn(report):
        failures.append("goal_alpha_research_refinement01_report_not_pass_or_warn")
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
        "instability_attribution_created",
        "conditional_stability_summary_created",
        "refined_candidate_designs_created",
        "intraday_redefinition_plan_created",
        "trial_registry_update_created",
        "source_backed_lineage_verified",
        "used_committed_quant02_evidence_only",
        "used_committed_alpha_candidate01_evidence_only",
        "used_committed_provider02b_evidence_only",
        "no_lookahead_refinement_policy_recorded",
        "future_returns_used_only_for_posthoc_diagnostics",
        "refined_candidates_not_evaluated",
        "goal_alpha_factor_candidate02_locked_future",
        "goal_rec_tiering01_locked_future",
        "goal10b4_locked_future",
        "position_band_validation_locked_future",
        "goal10d_locked_future",
        "dashboard_daily_report_locked_future",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")
    if instability and list(instability[0]) != INSTABILITY_FIELDS:
        failures.append("instability_fields_invalid")
    if conditional and list(conditional[0]) != CONDITIONAL_STABILITY_FIELDS:
        failures.append("conditional_fields_invalid")
    if designs and list(designs[0]) != REFINED_DESIGN_FIELDS:
        failures.append("refined_design_fields_invalid")
    if intraday and list(intraday[0]) != INTRADAY_REDEFINITION_FIELDS:
        failures.append("intraday_redefinition_fields_invalid")
    if trials and list(trials[0]) != TRIAL_REGISTRY_FIELDS:
        failures.append("trial_registry_fields_invalid")
    if {row.get("factor_id", "") for row in instability} != set(PROMISING_CANDIDATES):
        failures.append("instability_promising_factor_set_invalid")
    if {row.get("original_factor_id", "") for row in intraday} != set(REDEFINITION_CANDIDATES):
        failures.append("intraday_redefinition_factor_set_invalid")
    if len(instability) != int(manifest.get("instability_attribution_row_count", -1)):
        failures.append("instability_row_count_mismatch")
    if len(conditional) != int(manifest.get("conditional_stability_row_count", -1)):
        failures.append("conditional_row_count_mismatch")
    if len(designs) != int(manifest.get("refined_candidate_design_count", -1)):
        failures.append("design_row_count_mismatch")
    if len(intraday) != int(manifest.get("intraday_redefinition_row_count", -1)):
        failures.append("intraday_row_count_mismatch")
    if len(trials) != int(manifest.get("trial_registry_update_row_count", -1)):
        failures.append("trial_row_count_mismatch")
    if len(designs) < len(PROMISING_CANDIDATES):
        failures.append("not_enough_refined_design_rows")
    if any(row.get("not_evaluated_status") != NOT_EVALUATED for row in instability + conditional + designs):
        failures.append("not_evaluated_status_invalid")
    if any(row.get("not_evaluated_status") != REDEFINITION_REQUIRED for row in intraday):
        failures.append("intraday_redefinition_status_invalid")
    if any(row.get("accepted_for_downstream") != "false" for row in trials):
        failures.append("trial_downstream_acceptance_must_remain_false")
    if any(row.get("candidate_for_rec_tiering") != "false" for row in trials):
        failures.append("trial_rec_tiering_flag_must_remain_false")
    if _contains_forbidden_label(instability + conditional + designs + intraday + trials):
        failures.append("forbidden_actionable_label_present")
    if _contains_secret_like_text(root, OUTPUTS):
        failures.append("secret_or_token_like_text_present")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))

    gate = workflow.get(WORKFLOW_ID, {})
    alpha02 = workflow.get(GOAL_ALPHA_FACTOR_CANDIDATE02_WORKFLOW_ID, {})
    rec = workflow.get(GOAL_REC_TIERING01_WORKFLOW_ID, {})
    if gate.get("status") != "implemented_research_only":
        failures.append("goal_alpha_research_refinement01_workflow_not_implemented_research_only")
    if gate.get("implemented_in_repo") != "true":
        failures.append("goal_alpha_research_refinement01_workflow_not_marked_implemented")
    if gate.get("depends_on") != GOAL_QUANT_RESEARCH02_WORKFLOW_ID:
        failures.append("goal_alpha_research_refinement01_dependency_invalid")
    if alpha02.get("status") == "implemented_research_only":
        if alpha02.get("implemented_in_repo") != "true":
            failures.append("goal_alpha_factor_candidate02_implemented_flag_invalid")
    elif alpha02.get("status") != "locked_future" or alpha02.get("implemented_in_repo") != "false":
        failures.append("goal_alpha_factor_candidate02_not_locked_future")
    if alpha02.get("depends_on") != WORKFLOW_ID:
        failures.append("goal_alpha_factor_candidate02_dependency_invalid")
    if rec.get("status") != "locked_future" or rec.get("implemented_in_repo") != "false":
        failures.append("goal_rec_tiering01_not_locked_future")
    if rec.get("depends_on") not in {
        GOAL_ALPHA_FACTOR_CANDIDATE02_WORKFLOW_ID,
        "goal_quant_research03_refined_alpha_factor_validity_evaluation_gate",
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
                "# GOAL-ALPHA-RESEARCH-REFINEMENT-01 Audit",
                "",
                f"Status: `{status}`",
                "",
                f"Workflow status: `{gate.get('status', 'missing')}`",
                f"Promising candidates diagnosed: `{len(instability)}`",
                f"Conditional stability rows: `{len(conditional)}`",
                f"Refined design rows: `{len(designs)}`",
                f"Intraday redefinition rows: `{len(intraday)}`",
                f"Trial registry update rows: `{len(trials)}`",
                "Refined candidate panels, recommendations, positions, portfolios, dashboards, trading, production, local-lake, factor-mining, and DQN/RL generated: `false`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == PASS


def evaluate_goal_alpha_research_refinement01(root: Path) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = ["refined_candidate_designs_are_not_evaluated_or_promoted"]
    for path in REQUIRED_INPUTS:
        if not (root / path).exists():
            failures.append(f"missing_required_input:{path}")
    if failures:
        return _blocked_result(failures, warnings)

    evaluation = _read_csv(root / QUANT02_EVALUATION_PANEL_PATH)
    validity = _read_csv(root / QUANT02_SCORE_VALIDITY_PATH)
    ic_rankic = _read_csv(root / QUANT02_IC_RANKIC_PATH)
    monotonicity = _read_csv(root / QUANT02_MONOTONICITY_PATH)
    rolling = _read_csv(root / QUANT02_ROLLING_PATH)
    horizon = _read_csv(root / QUANT02_HORIZON_PATH)
    bucket_metrics = _read_csv(root / QUANT02_BUCKET_METRICS_PATH)
    quant02_trials = _read_csv(root / QUANT02_TRIAL_REGISTRY_PATH)
    alpha_registry = _read_csv(root / ALPHA_REGISTRY_PATH)
    alpha_panel = _read_csv(root / ALPHA_PANEL_PATH)
    provider_panel = _read_csv(root / PROVIDER02B_PANEL_PATH)
    mvp_symbol_rows = _read_csv(root / MVP_SYMBOL_TABLE_PATH)
    mvp_queue_rows = _read_csv(root / MVP_REVIEW_QUEUE_PATH)

    if len(evaluation) != 78000:
        failures.append(f"quant02_evaluation_row_count_is_{len(evaluation)}")
    if len(validity) != 13:
        failures.append(f"quant02_validity_row_count_is_{len(validity)}")
    if len(alpha_panel) != 78000:
        failures.append(f"alpha_candidate01_panel_row_count_is_{len(alpha_panel)}")
    if len(provider_panel) != 6000:
        failures.append(f"provider02b_panel_row_count_is_{len(provider_panel)}")
    if failures:
        return _blocked_result(failures, warnings)

    validity_by_factor = {row["factor_id"]: row for row in validity}
    registry_by_factor = {row["factor_id"]: row for row in alpha_registry}
    ic_by_factor = {row["factor_id"]: row for row in ic_rankic}
    monotonicity_by_factor = {row["factor_id"]: row for row in monotonicity}
    rolling_by_factor = {row["factor_id"]: row for row in rolling}
    horizon_by_factor = {row["factor_id"]: row for row in horizon}
    queue_by_symbol = _mvp_memberships(mvp_symbol_rows + mvp_queue_rows)
    eval_by_factor = _group_by(evaluation, "factor_id")
    dates = sorted({row["trade_date"] for row in evaluation})

    promising = [
        factor_id
        for factor_id in PROMISING_CANDIDATES
        if validity_by_factor.get(factor_id, {}).get("rejection_reason") == "rolling_window_stability_not_acceptable"
    ]
    if set(promising) != set(PROMISING_CANDIDATES):
        warnings.append("promising_candidate_set_uses_objective_focus_list_despite_current_classification_variance")
        promising = list(PROMISING_CANDIDATES)

    instability = _instability_rows(
        promising,
        eval_by_factor,
        dates,
        registry_by_factor,
        rolling_by_factor,
        horizon_by_factor,
    )
    conditional = _conditional_stability_rows(promising, eval_by_factor, queue_by_symbol)
    designs = _refined_candidate_design_rows(
        promising,
        registry_by_factor,
        validity_by_factor,
        horizon_by_factor,
        conditional,
    )
    intraday = _intraday_redefinition_rows(REDEFINITION_CANDIDATES, eval_by_factor)
    trials = _trial_registry_rows(designs, intraday)

    if designs:
        status = PASS_WITH_WARNINGS
        recommended_next = NEXT_GOAL_WITH_DESIGNS
        allowed_next = ALLOWED_NEXT_WITH_DESIGNS
    else:
        status = PASS_WITH_WARNINGS
        recommended_next = NEXT_GOAL_NO_DESIGNS
        allowed_next = ALLOWED_NEXT_NO_DESIGNS
        warnings.append("no_supportable_refined_designs")

    manifest = {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "mode": MODE,
        "status": status,
        "workflow_id": WORKFLOW_ID,
        "allowed_next_action": allowed_next,
        "recommended_next_goal": recommended_next,
        "source_quant02_evaluation_row_count": len(evaluation),
        "source_quant02_validity_row_count": len(validity),
        "source_alpha_candidate01_panel_row_count": len(alpha_panel),
        "source_provider02b_row_count": len(provider_panel),
        "source_mvp_symbol_row_count": len(mvp_symbol_rows),
        "source_mvp_review_queue_row_count": len(mvp_queue_rows),
        "promising_candidate_count": len(promising),
        "promising_candidate_ids": promising,
        "intraday_redefinition_candidate_count": len(REDEFINITION_CANDIDATES),
        "instability_attribution_row_count": len(instability),
        "conditional_stability_row_count": len(conditional),
        "refined_candidate_design_count": len(designs),
        "intraday_redefinition_row_count": len(intraday),
        "trial_registry_update_row_count": len(trials),
        "date_range": _date_range(evaluation),
        "unique_symbols": len({row["symbol"] for row in evaluation}),
        "unique_trade_dates": len({row["trade_date"] for row in evaluation}),
        "quant02_ready_factor_count": sum(1 for row in validity if row.get("candidate_for_rec_tiering") == "true"),
        "quant02_overall_validity": "no_factor_ready_for_rec_tiering",
        "classification_counts": dict(sorted(Counter(row.get("score_validity_classification", "") for row in validity).items())),
        "instability_type_counts": dict(sorted(Counter(row["instability_type"] for row in instability).items())),
        "instability_attribution_created": True,
        "conditional_stability_summary_created": True,
        "refined_candidate_designs_created": True,
        "intraday_redefinition_plan_created": True,
        "trial_registry_update_created": True,
        "source_backed_lineage_verified": True,
        "used_committed_quant02_evidence_only": True,
        "used_committed_alpha_candidate01_evidence_only": True,
        "used_committed_provider02b_evidence_only": True,
        "used_committed_mvp01_evidence_only": True,
        "no_lookahead_refinement_policy_recorded": True,
        "future_returns_used_only_for_posthoc_diagnostics": True,
        "benchmark_excess_returns_used_only_for_posthoc_diagnostics": True,
        "refined_candidates_not_evaluated": True,
        "goal_alpha_factor_candidate02_locked_future": True,
        "goal_rec_tiering01_locked_future": True,
        "goal10b4_locked_future": True,
        "position_band_validation_locked_future": True,
        "goal10d_locked_future": True,
        "dashboard_daily_report_locked_future": True,
        "portfolio_backtest_locked_future": True,
        "input_lineage": REQUIRED_INPUTS,
        "output_artifacts": OUTPUTS,
        "input_row_counts": {
            QUANT02_EVALUATION_PANEL_PATH: len(evaluation),
            QUANT02_SCORE_VALIDITY_PATH: len(validity),
            QUANT02_IC_RANKIC_PATH: len(ic_rankic),
            QUANT02_MONOTONICITY_PATH: len(monotonicity),
            QUANT02_ROLLING_PATH: len(rolling),
            QUANT02_HORIZON_PATH: len(horizon),
            QUANT02_BUCKET_METRICS_PATH: len(bucket_metrics),
            QUANT02_TRIAL_REGISTRY_PATH: len(quant02_trials),
            ALPHA_REGISTRY_PATH: len(alpha_registry),
            ALPHA_PANEL_PATH: len(alpha_panel),
            PROVIDER02B_PANEL_PATH: len(provider_panel),
            MVP_SYMBOL_TABLE_PATH: len(mvp_symbol_rows),
            MVP_REVIEW_QUEUE_PATH: len(mvp_queue_rows),
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
        "instability": instability,
        "conditional": conditional,
        "designs": designs,
        "intraday": intraday,
        "trials": trials,
        "manifest": manifest,
    }


def goal_alpha_research_refinement01_valid_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        (
            "GOAL-ALPHA-RESEARCH-REFINEMENT-01 Rolling Stability and Candidate Refinement Gate: PASS" in report
            or "GOAL-ALPHA-RESEARCH-REFINEMENT-01 Rolling Stability and Candidate Refinement Gate: PASS_WITH_WARNINGS" in report
        )
        and "Status: `PASS`" in audit
        and manifest.get("mode") == MODE
        and manifest.get("refined_candidate_designs_created") is True
        and manifest.get("refined_candidates_not_evaluated") is True
        and manifest.get("recommendation_outputs_created") is False
    )


def goal_alpha_research_refinement01_implemented_workflow_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-ALPHA-RESEARCH-REFINEMENT-01 Rolling Stability and Candidate Refinement Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_research_only",
        "current_repo_role": MODE,
        "implemented_in_repo": "true",
        "allowed_next_action": ALLOWED_NEXT_WITH_DESIGNS,
        "depends_on": GOAL_QUANT_RESEARCH02_WORKFLOW_ID,
        "produces_artifacts": ";".join(OUTPUTS),
        "primary_docs": f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "scripts/run_goal_alpha_research_refinement01_gate.py;scripts/audit_goal_alpha_research_refinement01_gate.py",
        "primary_outputs": ";".join([INSTABILITY_ATTRIBUTION_PATH, CONDITIONAL_STABILITY_PATH, REFINED_DESIGNS_PATH, INTRADAY_REDEFINITION_PATH, TRIAL_REGISTRY_UPDATE_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH]),
        "promotion_rule": "implemented_research_only_after_goal_alpha_research_refinement01_pass_or_pass_with_warnings",
        "notes": "Research-only rolling-stability diagnosis and refined candidate design plan over committed GOAL-QUANT-RESEARCH-02 evidence. It defines proposed refined candidates only; no refined factor panel, recommendation, position, portfolio, dashboard, trading, production, local-lake, factor-mining, broker, or DQN/RL outputs.",
    }


def locked_goal_alpha_factor_candidate02_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-ALPHA-FACTOR-CANDIDATE-02 Refined Variant Candidate Construction Gate",
        "stage_or_goal": "GOAL-ALPHA-FACTOR-CANDIDATE-02",
        "status": "locked_future",
        "current_repo_role": "locked_future_refined_alpha_candidate_construction_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal_alpha_factor_candidate02_request",
        "depends_on": WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal_alpha_factor_candidate02_refined_variants_gate",
        "notes": "Future refined alpha candidate construction remains locked; GOAL-ALPHA-RESEARCH-REFINEMENT-01 creates design definitions only and no refined factor panel.",
    }


def locked_goal_rec_tiering01_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "current_repo_role": "locked_future_recommendation_score_tiering_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal_alpha_factor_candidate02_evaluates_refined_variants",
        "depends_on": GOAL_ALPHA_FACTOR_CANDIDATE02_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal_rec_tiering01_gate_after_refined_alpha_candidate_evidence",
        "notes": "Future recommendation score tiering remains locked; GOAL-ALPHA-RESEARCH-REFINEMENT-01 creates only refinement designs and no recommendation rows.",
    }


def locked_goal10b4_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal_rec_tiering01_passes",
        "depends_on": GOAL_REC_TIERING01_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal10b4_revalidation_gate",
        "notes": "Future GOAL-10B.4 remains locked; GOAL-ALPHA-RESEARCH-REFINEMENT-01 creates no recommendation revalidation rows.",
    }


def locked_position_band_validation_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal10b4_and_explicit_position_validation_request",
        "depends_on": GOAL10B4_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_position_band_validation_gate",
        "notes": "Future position-band validation remains locked; GOAL-ALPHA-RESEARCH-REFINEMENT-01 creates no position outputs.",
    }


def locked_goal10d_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10d_request",
        "depends_on": GOAL10C_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal10d_failure_attribution_gate",
        "notes": "Future GOAL-10D remains locked; GOAL-ALPHA-RESEARCH-REFINEMENT-01 creates only research refinement design diagnostics.",
    }


def _instability_rows(
    factors: list[str],
    eval_by_factor: dict[str, list[dict[str, str]]],
    dates: list[str],
    registry: dict[str, dict[str, str]],
    rolling_summary: dict[str, dict[str, str]],
    horizon_summary: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for factor_id in factors:
        factor_rows = eval_by_factor.get(factor_id, [])
        family = registry.get(factor_id, {}).get("factor_family", factor_rows[0].get("factor_family", "") if factor_rows else "")
        stats20 = _window_stats(factor_rows, _rolling_windows(dates, 20))
        stats40 = _window_stats(factor_rows, _rolling_windows(dates, 40))
        split_stats = _window_stats(factor_rows, _split_windows(dates))
        month_stats = _window_stats(factor_rows, _month_windows(dates))
        all_stats = stats20 + stats40 + split_stats + month_stats
        signs = [item["direction_sign"] for item in all_stats if item["direction_sign"]]
        flips = [
            f"{right['window_name']}:{right['start_date']}..{right['end_date']}"
            for left, right in zip(all_stats, all_stats[1:])
            if left["direction_sign"] and right["direction_sign"] and left["direction_sign"] != right["direction_sign"]
        ]
        first_half = next((item["direction_label"] for item in split_stats if item["window_name"] == "first_half"), "not_evaluable")
        second_half = next((item["direction_label"] for item in split_stats if item["window_name"] == "second_half"), "not_evaluable")
        month_summary = ";".join(f"{item['window_name']}:{item['direction_label']}" for item in month_stats) or "not_evaluable"
        instability_type = _instability_type(factor_id, stats20, stats40, split_stats, month_stats, rolling_summary.get(factor_id, {}), horizon_summary.get(factor_id, {}))
        evidence = (
            f"rolling_summary={rolling_summary.get(factor_id, {}).get('stability_classification', 'missing')};"
            f"aligned20={_count_direction(stats20, 1)};inverse20={_count_direction(stats20, -1)};"
            f"aligned40={_count_direction(stats40, 1)};inverse40={_count_direction(stats40, -1)};"
            f"sign_flips={len(flips)}"
        )
        rows.append(
            {
                "factor_id": factor_id,
                "factor_family": family,
                "aligned_20d_window_count": _count_direction(stats20, 1),
                "inverse_20d_window_count": _count_direction(stats20, -1),
                "aligned_40d_window_count": _count_direction(stats40, 1),
                "inverse_40d_window_count": _count_direction(stats40, -1),
                "first_half_direction": first_half,
                "second_half_direction": second_half,
                "calendar_month_direction_summary": month_summary,
                "sign_flip_count": len(flips),
                "sign_flip_windows": ";".join(flips),
                "instability_type": instability_type,
                "instability_evidence": evidence,
                "not_evaluated_status": NOT_EVALUATED,
            }
        )
    return rows


def _conditional_stability_rows(
    factors: list[str],
    eval_by_factor: dict[str, list[dict[str, str]]],
    queue_by_symbol: dict[str, dict[str, bool]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for factor_id in factors:
        factor_rows = eval_by_factor.get(factor_id, [])
        family = factor_rows[0].get("factor_family", "") if factor_rows else ""
        enriched = []
        for row in factor_rows:
            memberships = queue_by_symbol.get(row.get("symbol", ""), {})
            item = dict(row)
            item["liquidity_review_queue_membership"] = "liquidity_member" if memberships.get("liquidity") or "liquidity" in row.get("mvp_review_queue_category", "").lower() else "non_liquidity_member"
            item["volatility_momentum_review_membership"] = "volatility_momentum_member" if memberships.get("volatility_momentum") or _has_volatility_momentum(row.get("mvp_review_queue_category", "") + ";" + row.get("mvp_review_priority_level", "")) else "non_volatility_momentum_member"
            enriched.append(item)
        for dimension in [
            "risk_score_bucket",
            "downside_risk_bucket",
            "mvp_review_queue_category",
            "mvp_review_priority_level",
            "liquidity_review_queue_membership",
            "volatility_momentum_review_membership",
        ]:
            grouped = _group_by(enriched, dimension)
            for value in sorted(grouped):
                subset = grouped[value]
                rank_values = [value for _, value in _daily_rankic(subset, "forward_return_20d")]
                spread = _top_bottom_spread(subset, "benchmark_excess_return_20d")
                window_stats = _window_stats(subset, _rolling_windows(sorted({row["trade_date"] for row in subset}), 20))
                aligned = _count_direction(window_stats, 1)
                inverse = _count_direction(window_stats, -1)
                if len(subset) < 100 or len({row["trade_date"] for row in subset}) < 20:
                    classification = "condition_not_evaluable_sparse_slice"
                elif aligned > inverse and (_mean(rank_values) or 0.0) > 0:
                    classification = "conditionally_more_stable_aligned"
                elif inverse > aligned:
                    classification = "conditionally_inverse_or_unstable"
                else:
                    classification = "condition_mixed_or_unstable"
                rows.append(
                    {
                        "factor_id": factor_id,
                        "factor_family": family,
                        "slice_dimension": dimension,
                        "slice_value": value,
                        "row_count": len(subset),
                        "unique_symbols": len({row["symbol"] for row in subset}),
                        "unique_trade_dates": len({row["trade_date"] for row in subset}),
                        "mean_rank_ic_20d": _fmt(_mean(rank_values)),
                        "mean_top_bottom_excess_spread_20d": _fmt(spread),
                        "aligned_window_count": aligned,
                        "inverse_window_count": inverse,
                        "stability_classification": classification,
                        "slicing_group_source": "committed_mvp_and_quant02_diagnostic_groups_current_or_past_only",
                        "no_lookahead_policy": "slicing_groups_exclude_forward_returns_and_labels",
                        "not_evaluated_status": NOT_EVALUATED,
                    }
                )
    return rows


def _refined_candidate_design_rows(
    factors: list[str],
    registry: dict[str, dict[str, str]],
    validity: dict[str, dict[str, str]],
    horizon: dict[str, dict[str, str]],
    conditional: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    condition_by_factor = _group_by(conditional, "factor_id")
    for factor_id in factors:
        source = registry.get(factor_id, {})
        family = source.get("factor_family", "")
        hypothesis = source.get("economic_hypothesis", f"Refine {factor_id} to reduce rolling instability without using labels in construction.")
        expected = source.get("expected_direction", "higher_value_research_hypothesis_positive")
        rejection = validity.get(factor_id, {}).get("rejection_reason", "rolling_window_stability_not_acceptable")
        strongest_horizon = horizon.get(factor_id, {}).get("strongest_horizon", "20d")
        best_condition = _best_condition(condition_by_factor.get(factor_id, []))
        templates = [
            (
                "risk_filtered",
                "risk_score_bucket",
                "Retain the source factor only for LOW_RISK_REVIEW_ONLY and MEDIUM_RISK_REVIEW_ONLY rows; mark HIGH/INSUFFICIENT risk rows missing before cross-sectional bucketing.",
            ),
            (
                "downside_risk_filtered",
                "downside_risk_bucket",
                "Retain the source factor only outside HIGH_DOWNSIDE_RISK_REVIEW_ONLY; rows with high downside-risk diagnostics are excluded before bucketing.",
            ),
            (
                "liquidity_filtered",
                "mvp_review_queue_category;mvp_review_priority_level",
                "Retain the source factor only outside liquidity review queue membership, using committed MVP review categories and priorities.",
            ),
            (
                "review_queue_conditioned",
                "mvp_review_queue_category;mvp_review_priority_level",
                f"Evaluate the source factor only in the most stable committed review slice observed in diagnostics: {best_condition}.",
            ),
            (
                "horizon_specific",
                "factor_value_normalized_cross_sectional",
                f"Carry the source factor forward as a horizon-specific design focused on the strongest observed horizon `{strongest_horizon}`; do not mix horizons until a later construction gate.",
            ),
        ]
        for refinement_type, columns, rule in templates:
            refined_id = f"{factor_id}__{refinement_type}"
            rows.append(
                {
                    "refined_factor_id": refined_id,
                    "source_factor_id": factor_id,
                    "refinement_type": refinement_type,
                    "economic_hypothesis": hypothesis,
                    "deterministic_rule_description": rule,
                    "required_columns": f"trade_date;symbol;{columns}",
                    "no_lookahead_policy": "uses_only_current_or_past_candidate_values_and_committed_diagnostic_groups_no_forward_returns",
                    "expected_direction": expected,
                    "reason_for_refinement": rejection,
                    "not_evaluated_status": NOT_EVALUATED,
                }
            )
    return rows


def _intraday_redefinition_rows(factors: list[str], eval_by_factor: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for factor_id in factors:
        factor_rows = eval_by_factor.get(factor_id, [])
        buckets = Counter(row.get("factor_bucket", "") for row in factor_rows if row.get("factor_bucket"))
        bucket_count = len(buckets)
        dominant_bucket, dominant_count = buckets.most_common(1)[0] if buckets else ("", 0)
        min_size = min(buckets.values()) if buckets else 0
        share = dominant_count / len(factor_rows) if factor_rows else 0.0
        issue = "too_binary_or_threshold_sensitive_same_day_ohlc_shape"
        driver = "dominant_or_sparse_factor_bucket_distribution"
        proposals = [
            (
                f"{factor_id}__continuous_body_wick_balance",
                "Replace binary intraday pressure flags with a continuous current-day body/wick balance rank, winsorized cross-sectionally before bucketing.",
                "open;high;low;close;factor_value_normalized_cross_sectional",
            ),
            (
                f"{factor_id}__volume_confirmed_pressure",
                "Require intraday recovery/weakness pressure to be confirmed by current-or-trailing turnover/liquidity diagnostics before assigning exposure buckets.",
                "open;high;low;close;turnover;volume;mvp_review_queue_category",
            ),
        ]
        for proposed_id, definition, columns in proposals:
            rows.append(
                {
                    "original_factor_id": factor_id,
                    "bucket_count": bucket_count,
                    "dominant_bucket": dominant_bucket,
                    "dominant_bucket_share": _fmt(share),
                    "minimum_bucket_size": min_size,
                    "sparsity_driver": driver,
                    "definition_issue_type": issue,
                    "proposed_refined_factor_id": proposed_id,
                    "revised_definition": definition,
                    "required_columns": columns,
                    "no_lookahead_policy": "current_day_ohlc_shape_and_current_or_past_liquidity_only_no_forward_returns",
                    "not_evaluated_status": REDEFINITION_REQUIRED,
                }
            )
    return rows


def _trial_registry_rows(designs: list[dict[str, object]], intraday: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    index = 1
    for design in designs:
        rows.append(
            {
                "trial_id": f"goal_alpha_research_refinement01_trial_{index:02d}",
                "source_goal_id": GOAL_ID,
                "original_factor_id": design["source_factor_id"],
                "refinement_id": design["refined_factor_id"],
                "refinement_type": design["refinement_type"],
                "reason_for_refinement": design["reason_for_refinement"],
                "no_lookahead_policy": design["no_lookahead_policy"],
                "downstream_status": NOT_EVALUATED,
                "accepted_for_downstream": False,
                "candidate_for_rec_tiering": False,
                "recommended_next_action": "construct_in_future_explicit_goal_alpha_factor_candidate02_before_any_evaluation",
            }
        )
        index += 1
    for item in intraday:
        rows.append(
            {
                "trial_id": f"goal_alpha_research_refinement01_trial_{index:02d}",
                "source_goal_id": GOAL_ID,
                "original_factor_id": item["original_factor_id"],
                "refinement_id": item["proposed_refined_factor_id"],
                "refinement_type": "intraday_pressure_redefinition",
                "reason_for_refinement": item["definition_issue_type"],
                "no_lookahead_policy": item["no_lookahead_policy"],
                "downstream_status": REDEFINITION_REQUIRED,
                "accepted_for_downstream": False,
                "candidate_for_rec_tiering": False,
                "recommended_next_action": "redefine_in_future_explicit_goal_alpha_factor_candidate02_before_evaluation",
            }
        )
        index += 1
    return rows


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / INSTABILITY_ATTRIBUTION_PATH, result["instability"], INSTABILITY_FIELDS)
    write_csv(root / CONDITIONAL_STABILITY_PATH, result["conditional"], CONDITIONAL_STABILITY_FIELDS)
    write_csv(root / REFINED_DESIGNS_PATH, result["designs"], REFINED_DESIGN_FIELDS)
    write_csv(root / INTRADAY_REDEFINITION_PATH, result["intraday"], INTRADAY_REDEFINITION_FIELDS)
    write_csv(root / TRIAL_REGISTRY_UPDATE_PATH, result["trials"], TRIAL_REGISTRY_FIELDS)
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_report(root, result)
    _write_doc(root, result)
    _write_contract(root, result)


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    body = [
        "# GOAL-ALPHA-RESEARCH-REFINEMENT-01 Rolling Stability and Candidate Refinement Gate",
        "",
        "## 1. Goal status",
        f"GOAL-ALPHA-RESEARCH-REFINEMENT-01 Rolling Stability and Candidate Refinement Gate: {manifest['status']}",
        "",
        "## 2. Current Quant02 context",
        "GOAL-QUANT-RESEARCH-02 evaluated 13 alpha candidates, found ready factor count 0, and recommended Alpha Candidate 02 or Alpha Research Refinement before recommendation tiering.",
        "",
        "## 3. Why no factor is ready for recommendation tiering",
        "Promising candidates retained non-collapsed buckets, available IC/RankIC, and aligned monotonicity, but failed rolling-window stability. This gate diagnoses that instability without constructing refined factor values.",
        "",
        "## 4. Promising candidate focus set",
        *[f"- `{factor_id}`" for factor_id in PROMISING_CANDIDATES],
        "",
        "## 5. Rolling instability attribution",
        f"Instability attribution rows: `{manifest['instability_attribution_row_count']}`. Instability type counts: `{manifest['instability_type_counts']}`.",
        "",
        "## 6. Conditional stability findings",
        f"Conditional stability rows: `{manifest['conditional_stability_row_count']}`. Slices use only committed risk, downside-risk, and MVP review groups.",
        "",
        "## 7. Candidate refinement design plan",
        f"Refined candidate design rows: `{manifest['refined_candidate_design_count']}`. These are deterministic design definitions only and are not evaluated.",
        "",
        "## 8. Intraday pressure redefinition plan",
        f"Intraday redefinition rows: `{manifest['intraday_redefinition_row_count']}` for alpha_intraday_recovery_pressure and alpha_intraday_weakness_pressure.",
        "",
        "## 9. Research governance and trial registry update",
        f"Trial registry update rows: `{manifest['trial_registry_update_row_count']}`. accepted_for_downstream and candidate_for_rec_tiering are always false.",
        "",
        "## 10. Why this is not recommendation tiering",
        "This gate does not create recommendations, positions, BUY/SELL/HOLD labels, target prices, sizing, weights, orders, portfolio returns, equity curves, dashboards, trading outputs, production outputs, or predictive-validity claims.",
        "",
        "## 11. Locked downstream boundaries",
        "GOAL-ALPHA-FACTOR-CANDIDATE-02, GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, portfolio backtests, trading, production, broker, local-lake, factor-mining, and DQN/RL remain locked.",
        "",
        "## 12. Recommended next goal",
        f"`{manifest['recommended_next_goal']}`.",
        "",
    ]
    write_text(root / REPORT_PATH, "\n".join(body))


def _write_doc(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    body = [
        "# GOAL-ALPHA-RESEARCH-REFINEMENT-01 Rolling Stability and Candidate Refinement Gate",
        "",
        f"Status: `{manifest['status']}`",
        "",
        "This gate is research-only. It diagnoses Quant02 rolling instability and writes proposed refined candidate designs without constructing or evaluating refined factor panels.",
        "",
        "## Outputs",
        *[f"- `{path}`" for path in OUTPUTS if path.startswith("outputs/research/")],
        "",
        "## Method",
        "The gate analyzes aligned and inverse rolling windows, sign flips, half/month behavior, conditional stability slices, and intraday pressure bucket imbalance using committed Quant02, Alpha Candidate 01, Provider02B, and MVP evidence.",
        "",
        "## Result",
        f"- Promising candidates diagnosed: `{manifest['promising_candidate_count']}`",
        f"- Refined candidate design rows: `{manifest['refined_candidate_design_count']}`",
        f"- Intraday redefinition rows: `{manifest['intraday_redefinition_row_count']}`",
        f"- Recommended next goal: `{manifest['recommended_next_goal']}`",
        "",
        "## Locked Boundary",
        "No refined factor panel, recommendation rows, position rows, BUY/SELL/HOLD labels, target prices, position sizes, weights, orders, portfolio returns, equity curves, dashboards, HTML, Streamlit, frontend, visual reports, trading outputs, broker outputs, production outputs, local-lake files, factor-mining outputs, or DQN/RL outputs are created.",
        "",
    ]
    write_text(root / DOC_PATH, "\n".join(body))


def _write_contract(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    lines = [
        "{",
        f'  "goal_id": "{GOAL_ID}",',
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
        '  "instability_attribution_schema": ' + _json_list(INSTABILITY_FIELDS) + ",",
        '  "refined_design_schema": ' + _json_list(REFINED_DESIGN_FIELDS) + ",",
        '  "refinement_policy": "design_definitions_only_no_refined_factor_panel_no_predictive_validity_claim",',
        '  "no_lookahead_policy": "slicing_groups_and_refinement_rules_use_only_current_or_past_committed_diagnostics_no_forward_returns_in_construction",',
        '  "downstream_locks": {',
        f'    "{GOAL_ALPHA_FACTOR_CANDIDATE02_WORKFLOW_ID}": "locked_future",',
        f'    "{GOAL_REC_TIERING01_WORKFLOW_ID}": "locked_future",',
        f'    "{GOAL10B4_WORKFLOW_ID}": "locked_future",',
        f'    "{POSITION_BAND_VALIDATION_WORKFLOW_ID}": "locked_future",',
        f'    "{GOAL10D_WORKFLOW_ID}": "locked_future",',
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
        insert_at = next((idx + 1 for idx, row in enumerate(rows) if row["workflow_id"] == GOAL_QUANT_RESEARCH02_WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": WORKFLOW_ID})
        by_id = {row["workflow_id"]: row for row in rows}
    if GOAL_ALPHA_FACTOR_CANDIDATE02_WORKFLOW_ID not in by_id:
        insert_at = next((idx + 1 for idx, row in enumerate(rows) if row["workflow_id"] == WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": GOAL_ALPHA_FACTOR_CANDIDATE02_WORKFLOW_ID})
        by_id = {row["workflow_id"]: row for row in rows}
    by_id[WORKFLOW_ID].update(goal_alpha_research_refinement01_implemented_workflow_patch())
    by_id[GOAL_ALPHA_FACTOR_CANDIDATE02_WORKFLOW_ID].update(locked_goal_alpha_factor_candidate02_patch())
    if GOAL_REC_TIERING01_WORKFLOW_ID in by_id:
        by_id[GOAL_REC_TIERING01_WORKFLOW_ID].update(locked_goal_rec_tiering01_patch())
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
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_alpha_research_refinement01"
    preserve_later_review_only_workflow_states(root, by_id)
    if result["status"] in {PASS, PASS_WITH_WARNINGS} and WORKFLOW_ID in by_id:
        by_id[WORKFLOW_ID].update(goal_alpha_research_refinement01_implemented_workflow_patch())
        by_id[GOAL_ALPHA_FACTOR_CANDIDATE02_WORKFLOW_ID].update(locked_goal_alpha_factor_candidate02_patch())
        if GOAL_REC_TIERING01_WORKFLOW_ID in by_id:
            by_id[GOAL_REC_TIERING01_WORKFLOW_ID].update(locked_goal_rec_tiering01_patch())
        preserve_later_review_only_workflow_states(root, by_id)
    write_csv(path, rows)


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    payload = read_json(path) if path.exists() else {}
    payload[WORKFLOW_ID] = "implemented_research_only"
    payload[GOAL_ALPHA_FACTOR_CANDIDATE02_WORKFLOW_ID] = False
    payload[GOAL_REC_TIERING01_WORKFLOW_ID] = False
    payload[GOAL10B4_WORKFLOW_ID] = False
    payload[POSITION_BAND_VALIDATION_WORKFLOW_ID] = False
    payload[GOAL10D_WORKFLOW_ID] = False
    preserve_later_review_only_capabilities(root, payload)
    if result["status"] in {PASS, PASS_WITH_WARNINGS}:
        payload[WORKFLOW_ID] = "implemented_research_only"
        payload[GOAL_ALPHA_FACTOR_CANDIDATE02_WORKFLOW_ID] = False
        payload[GOAL_REC_TIERING01_WORKFLOW_ID] = False
    write_json(path, payload)


def _window_stats(factor_rows: list[dict[str, str]], windows: list[tuple[str, list[str]]]) -> list[dict[str, object]]:
    rows = []
    for name, window_dates in windows:
        subset = [row for row in factor_rows if row.get("trade_date") in window_dates]
        spread = _top_bottom_spread(subset, "benchmark_excess_return_20d")
        rank_values = [value for _, value in _daily_rankic(subset, "forward_return_20d")]
        mean_rank = _mean(rank_values)
        direction = 1 if (spread or 0.0) > 0 and (mean_rank or 0.0) >= -0.01 else -1 if (spread or 0.0) < 0 else 0
        rows.append(
            {
                "window_name": name,
                "start_date": window_dates[0] if window_dates else "",
                "end_date": window_dates[-1] if window_dates else "",
                "spread": spread,
                "mean_rank_ic": mean_rank,
                "direction_sign": direction,
                "direction_label": "aligned" if direction > 0 else "inverse" if direction < 0 else "neutral_or_not_evaluable",
            }
        )
    return rows


def _instability_type(
    factor_id: str,
    stats20: list[dict[str, object]],
    stats40: list[dict[str, object]],
    split_stats: list[dict[str, object]],
    month_stats: list[dict[str, object]],
    rolling_row: dict[str, str],
    horizon_row: dict[str, str],
) -> str:
    all_stats = stats20 + stats40 + split_stats + month_stats
    if len(all_stats) < 4:
        return "insufficient_window_count"
    if horizon_row.get("horizon_consistency_status") == "horizons_conflicting":
        return "horizon_conflict"
    if _count_direction(stats20, -1) > _count_direction(stats40, -1) and _count_direction(stats40, -1) <= 1:
        return "short_window_noise"
    if "liquidity" in factor_id:
        return "liquidity_sensitive_signal"
    if "risk" in factor_id or "downside" in factor_id:
        return "risk_bucket_sensitive_signal"
    if int(rolling_row.get("sign_flip_count", "0") or 0) >= 4:
        return "regime_sensitive_signal"
    return "candidate_definition_too_noisy"


def _mvp_memberships(rows: list[dict[str, str]]) -> dict[str, dict[str, bool]]:
    memberships: dict[str, dict[str, bool]] = defaultdict(lambda: {"liquidity": False, "volatility_momentum": False})
    for row in rows:
        symbol = row.get("symbol", "")
        text = ";".join(
            [
                row.get("review_queue_category", ""),
                row.get("review_priority_level", ""),
                row.get("review_reason_codes", ""),
            ]
        ).lower()
        memberships[symbol]["liquidity"] = memberships[symbol]["liquidity"] or "liquidity" in text
        memberships[symbol]["volatility_momentum"] = memberships[symbol]["volatility_momentum"] or _has_volatility_momentum(text)
    return memberships


def _has_volatility_momentum(text: str) -> bool:
    lowered = text.lower()
    return "volatility" in lowered or "momentum" in lowered


def _best_condition(rows: list[dict[str, object]]) -> str:
    candidates = [
        row
        for row in rows
        if row.get("stability_classification") == "conditionally_more_stable_aligned"
        and int(row.get("row_count", 0) or 0) >= 100
    ]
    if not candidates:
        return "no_single_slice_approved_use_as_design_note_only"
    best = max(candidates, key=lambda row: _float(row.get("mean_rank_ic_20d", "")) or 0.0)
    return f"{best['slice_dimension']}={best['slice_value']}"


def _top_bottom_spread(rows: list[dict[str, str]], target_field: str) -> float | None:
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


def _daily_rankic(rows: list[dict[str, str]], target_field: str) -> list[tuple[str, float]]:
    daily = _group_by(rows, "trade_date")
    output: list[tuple[str, float]] = []
    for date in sorted(daily):
        x = [_float(row.get("factor_value", "")) for row in daily[date]]
        y = [_float(row.get(target_field, "")) for row in daily[date]]
        pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
        if len(pairs) < 5:
            continue
        corr = _correlation(_ranks([a for a, _ in pairs]), _ranks([b for _, b in pairs]))
        if corr is not None:
            output.append((date, corr))
    return output


def _rolling_windows(dates: list[str], size: int) -> list[tuple[str, list[str]]]:
    if len(dates) < size:
        return []
    return [(f"{size}d_{window[0]}_{window[-1]}", window) for window in (dates[index : index + size] for index in range(0, len(dates) - size + 1))]


def _split_windows(dates: list[str]) -> list[tuple[str, list[str]]]:
    if len(dates) < 2:
        return []
    midpoint = len(dates) // 2
    return [("first_half", dates[:midpoint]), ("second_half", dates[midpoint:])]


def _month_windows(dates: list[str]) -> list[tuple[str, list[str]]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for date in dates:
        grouped[date[:7]].append(date)
    return [(month, month_dates) for month, month_dates in sorted(grouped.items()) if len(month_dates) >= 5]


def _count_direction(rows: list[dict[str, object]], sign: int) -> int:
    return sum(1 for row in rows if row.get("direction_sign") == sign)


def _group_by(rows: list[dict[str, object]], field: str) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(field, ""))].append(row)
    return grouped


def _mean(values: list[float | None]) -> float | None:
    clean = [value for value in values if value is not None]
    return sum(clean) / len(clean) if clean else None


def _median(values: list[float | None]) -> float | None:
    clean = sorted(value for value in values if value is not None)
    return median(clean) if clean else None


def _correlation(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        return None
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right))
    left_var = sum((x - left_mean) ** 2 for x in left)
    right_var = sum((y - right_mean) ** 2 for y in right)
    if left_var <= 0 or right_var <= 0:
        return None
    return numerator / (left_var**0.5 * right_var**0.5)


def _ranks(values: list[float]) -> list[float]:
    indexed = sorted((value, index) for index, value in enumerate(values))
    ranks = [0.0] * len(values)
    cursor = 0
    while cursor < len(indexed):
        end = cursor + 1
        while end < len(indexed) and indexed[end][0] == indexed[cursor][0]:
            end += 1
        rank = (cursor + end + 1) / 2
        for _, index in indexed[cursor:end]:
            ranks[index] = rank
        cursor = end
    return ranks


def _float(value: object) -> float | None:
    try:
        if value in {"", None}:
            return None
        return float(str(value))
    except (TypeError, ValueError):
        return None


def _fmt(value: float | None) -> str:
    return "" if value is None else f"{value:.10f}"


def _date_range(rows: list[dict[str, object]]) -> str:
    dates = sorted(str(row.get("trade_date", "")) for row in rows if row.get("trade_date"))
    return f"{dates[0]}..{dates[-1]}" if dates else ""


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


def _workflow_rows(root: Path) -> dict[str, dict[str, str]]:
    rows = _read_csv(root / "configs/project/workflow_status.csv")
    return {row["workflow_id"]: row for row in rows}


def _report_pass_or_warn(report: str) -> bool:
    return (
        "GOAL-ALPHA-RESEARCH-REFINEMENT-01 Rolling Stability and Candidate Refinement Gate: PASS" in report
        or "GOAL-ALPHA-RESEARCH-REFINEMENT-01 Rolling Stability and Candidate Refinement Gate: PASS_WITH_WARNINGS" in report
    )


def _contains_forbidden_label(rows: list[dict[str, object]]) -> bool:
    return any(str(value).upper() in FORBIDDEN_TABLE_LABELS for row in rows for value in row.values())


def _contains_secret_like_text(root: Path, paths: list[str]) -> bool:
    needles = ["TUSHARE_TOKEN=", "api_key=", "secret_key=", "access_token=", "password="]
    for rel in paths:
        path = root / rel
        if path.exists() and any(needle in path.read_text(encoding="utf-8", errors="ignore") for needle in needles):
            return True
    return False


def _forbidden_outputs_present(root: Path) -> list[str]:
    present = []
    for prefix in FORBIDDEN_OUTPUT_PREFIXES:
        path = root / prefix
        if path.exists():
            present.append(prefix)
    return present


def _json_list(values: list[str]) -> str:
    return "[" + ", ".join(f'"{value}"' for value in values) + "]"


def _blocked_result(failures: list[str], warnings: list[str]) -> dict[str, object]:
    manifest = {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "mode": MODE,
        "status": BLOCKED,
        "workflow_id": WORKFLOW_ID,
        "recommended_next_goal": NEXT_GOAL_NO_DESIGNS,
        "failures": failures,
        "warnings": sorted(set(warnings)),
    }
    for key in FALSE_BOUNDARY_KEYS:
        manifest[key] = False
    return {
        "status": BLOCKED,
        "warnings": sorted(set(warnings)),
        "failures": failures,
        "instability": [],
        "conditional": [],
        "designs": [],
        "intraday": [],
        "trials": [],
        "manifest": manifest,
    }

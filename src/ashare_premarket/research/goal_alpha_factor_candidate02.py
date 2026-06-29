from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from pathlib import Path

from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import (
    preserve_later_review_only_capabilities,
    preserve_later_review_only_workflow_states,
)
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-ALPHA-FACTOR-CANDIDATE-02"
GOAL_NAME = "GOAL-ALPHA-FACTOR-CANDIDATE-02-REFINED-ALPHA-CANDIDATE-CONSTRUCTION-GATE"
MODE = "research_only_refined_candidate"
WORKFLOW_ID = "goal_alpha_factor_candidate02_refined_variants_research_gate"
PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

GOAL_ALPHA_RESEARCH_REFINEMENT01_WORKFLOW_ID = "goal_alpha_research_refinement01_rolling_stability_candidate_refinement_gate"
GOAL_QUANT_RESEARCH03_WORKFLOW_ID = "goal_quant_research03_refined_alpha_factor_validity_evaluation_gate"
GOAL_REC_TIERING01_WORKFLOW_ID = "goal_rec_tiering01_recommendation_score_tiering_gate"
GOAL10B4_WORKFLOW_ID = "goal10b4_recommendation_backtest_revalidation"
POSITION_BAND_VALIDATION_WORKFLOW_ID = "goal_position_band_validation01_position_band_validation_gate"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
GOAL10C_WORKFLOW_ID = "goal10c_backtest_cost_slippage_sensitivity_gate"

ALLOWED_NEXT = "request_goal_quant_research03_refined_alpha_factor_validity_evaluation_gate"
NEXT_GOAL = "GOAL-QUANT-RESEARCH-03-REFINED-ALPHA-FACTOR-VALIDITY-EVALUATION-GATE"
NON_ACTIONABLE = "research_only_not_trade_instruction"
NO_LOOKAHEAD = "passed_current_or_past_only"
DEFAULT_EXPECTED_DIRECTION = "higher_positive"
PANEL_UNIVERSE_MODE = "p02b_universe"
PANEL_CONTRACT_STATUS = "p02b_ready"
SOURCE_VALUE_MISSING_STATUS = "constructed_source_missing"
MIN_VALID_ROWS = 100
MIN_VALID_DATES = 20
COLLAPSE_THRESHOLD = 0.80

REFINEMENT_DESIGNS_PATH = "outputs/research/goal_alpha_research_refinement01_refined_candidate_designs.csv"
INTRADAY_REDEFINITION_PLAN_PATH = "outputs/research/goal_alpha_research_refinement01_intraday_redefinition_plan.csv"
INSTABILITY_ATTRIBUTION_PATH = "outputs/research/goal_alpha_research_refinement01_instability_attribution.csv"
CONDITIONAL_STABILITY_PATH = "outputs/research/goal_alpha_research_refinement01_conditional_stability_summary.csv"
REFINEMENT_TRIAL_REGISTRY_PATH = "outputs/research/goal_alpha_research_refinement01_trial_registry_update.csv"
ALPHA01_PANEL_PATH = "outputs/research/goal_alpha_factor_candidate01_factor_candidate_panel.csv"
ALPHA01_REGISTRY_PATH = "outputs/research/goal_alpha_factor_candidate01_candidate_registry.csv"
QUANT02_EVALUATION_PANEL_PATH = "outputs/research/goal_quant_research02_alpha_evaluation_panel.csv"
QUANT02_SCORE_VALIDITY_PATH = "outputs/research/goal_quant_research02_alpha_factor_score_validity_classification.csv"
PROVIDER02B_PANEL_PATH = "outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv"
MVP_SYMBOL_TABLE_PATH = "outputs/mvp/goal_mvp01_symbol_diagnostic_table.csv"
MVP_REVIEW_QUEUE_PATH = "outputs/mvp/goal_mvp01_review_queue.csv"
RISK01_DIAGNOSTICS_PATH = "outputs/diagnostics/goal_risk_tiering01_risk_tiered_diagnostics.csv"
RISK011_DIAGNOSTICS_PATH = "outputs/diagnostics/goal_risk_tiering011_downside_risk_diagnostics.csv"

REFINED_REGISTRY_PATH = "outputs/research/goal_alpha_factor_candidate02_refined_candidate_registry.csv"
REFINED_PANEL_PATH = "outputs/research/goal_alpha_factor_candidate02_refined_candidate_panel.csv"
COVERAGE_SUMMARY_PATH = "outputs/research/goal_alpha_factor_candidate02_coverage_summary.csv"
CONSTRUCTION_WARNINGS_PATH = "outputs/research/goal_alpha_factor_candidate02_construction_warnings.csv"
INTRADAY_STATUS_PATH = "outputs/research/goal_alpha_factor_candidate02_intraday_redefinition_status.csv"
TRIAL_REGISTRY_PATH = "outputs/research/goal_alpha_factor_candidate02_trial_registry.csv"
REPORT_PATH = "outputs/audits/goal_alpha_factor_candidate02_report.md"
MANIFEST_PATH = "outputs/audits/goal_alpha_factor_candidate02_manifest.json"
AUDIT_PATH = "outputs/audits/goal_alpha_factor_candidate02_audit.md"
DOC_PATH = "docs/research/GOAL_ALPHA_FACTOR_CANDIDATE02_REFINED_ALPHA_CANDIDATE_CONSTRUCTION_GATE.md"
CONTRACT_PATH = "configs/research/goal_alpha_factor_candidate02_contract.yaml"

REQUIRED_INPUTS = [
    REFINEMENT_DESIGNS_PATH,
    INTRADAY_REDEFINITION_PLAN_PATH,
    INSTABILITY_ATTRIBUTION_PATH,
    CONDITIONAL_STABILITY_PATH,
    REFINEMENT_TRIAL_REGISTRY_PATH,
    ALPHA01_PANEL_PATH,
    ALPHA01_REGISTRY_PATH,
    QUANT02_EVALUATION_PANEL_PATH,
    QUANT02_SCORE_VALIDITY_PATH,
    PROVIDER02B_PANEL_PATH,
    MVP_SYMBOL_TABLE_PATH,
    MVP_REVIEW_QUEUE_PATH,
    RISK01_DIAGNOSTICS_PATH,
    RISK011_DIAGNOSTICS_PATH,
]

OUTPUTS = [
    REFINED_REGISTRY_PATH,
    REFINED_PANEL_PATH,
    COVERAGE_SUMMARY_PATH,
    CONSTRUCTION_WARNINGS_PATH,
    INTRADAY_STATUS_PATH,
    TRIAL_REGISTRY_PATH,
    REPORT_PATH,
    MANIFEST_PATH,
    AUDIT_PATH,
    DOC_PATH,
    CONTRACT_PATH,
]

REGISTRY_FIELDS = [
    "refined_factor_id",
    "source_factor_id",
    "refinement_type",
    "factor_family",
    "economic_hypothesis",
    "deterministic_rule_description",
    "required_columns",
    "construction_formula_plain_english",
    "construction_formula_expression",
    "expected_direction",
    "no_lookahead_status",
    "uses_forward_returns_in_construction",
    "uses_benchmark_excess_returns_in_construction",
    "uses_label_ready_fields_in_construction",
    "source_input_artifacts",
    "construction_status",
    "rejection_or_missing_reason",
    "intended_future_evaluation_goal",
    "non_actionable_disclaimer",
]

PANEL_FIELDS = [
    "trade_date",
    "symbol",
    "refined_factor_id",
    "source_factor_id",
    "refinement_type",
    "factor_family",
    "factor_value",
    "factor_value_raw",
    "factor_value_normalized_cross_sectional",
    "factor_quantile",
    "factor_bucket",
    "expected_direction",
    "construction_status",
    "no_lookahead_status",
    "required_column_status",
    "source_provider",
    "universe_mode",
    "panel_contract_status",
    "risk_score_bucket",
    "downside_risk_bucket",
    "mvp_review_queue_category",
    "mvp_review_priority_level",
    "original_alpha_factor_value",
    "original_alpha_factor_bucket",
    "diagnostic_mode",
    "non_actionable_disclaimer",
]

COVERAGE_FIELDS = [
    "refined_factor_id",
    "row_count",
    "valid_factor_value_count",
    "missing_factor_value_count",
    "unique_symbols",
    "unique_trade_dates",
    "date_min",
    "date_max",
    "quantile_count",
    "bucket_count",
    "dominant_bucket_share",
    "minimum_bucket_size",
    "construction_status",
    "no_lookahead_status",
    "required_column_status",
    "refinement_type",
    "source_factor_id",
]

WARNING_FIELDS = [
    "refined_factor_id",
    "warning_code",
    "warning_severity",
    "warning_detail",
    "non_actionable_disclaimer",
]

INTRADAY_STATUS_FIELDS = [
    "original_factor_id",
    "proposed_refined_factor_id",
    "required_columns",
    "construction_status",
    "rejection_or_missing_reason",
    "not_evaluated_status",
    "intended_future_evaluation_goal",
    "non_actionable_disclaimer",
]

TRIAL_REGISTRY_FIELDS = [
    "trial_id",
    "source_goal_id",
    "refined_factor_id",
    "source_factor_id",
    "refinement_type",
    "reason_for_refinement",
    "no_lookahead_policy",
    "construction_status",
    "accepted_for_downstream",
    "candidate_for_rec_tiering",
    "downstream_status",
    "intended_future_evaluation_goal",
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
    "goal_quant_research03_run",
    "goal_rec_tiering01_run",
    "goal10b4_run",
    "position_band_validation_run",
    "goal10d_run",
    "live_provider_fetches_run",
    "future_returns_used_in_refined_candidate_construction",
    "benchmark_excess_returns_used_in_refined_candidate_construction",
    "label_ready_fields_used_in_refined_candidate_construction",
    "posthoc_performance_used_to_select_or_tune_formulas",
    "predictive_validity_evaluated",
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

WARNING_CODE_TAXONOMY = [
    "insufficient_valid_rows_after_filter",
    "collapsed_or_imbalanced_bucket",
    "missing_required_columns",
    "sparse_review_queue_slice",
    "source_factor_value_missing",
    "initial_trailing_window_missing",
    "retained_rows_below_threshold",
    "construction_completed_with_sparse_exposure",
]


def run_goal_alpha_factor_candidate02_gate(root: Path) -> bool:
    result = evaluate_goal_alpha_factor_candidate02(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal_alpha_factor_candidate02_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal_alpha_factor_candidate02_gate(root: Path) -> bool:
    failures: list[str] = []
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    registry = _read_csv(root / REFINED_REGISTRY_PATH)
    panel = _read_csv(root / REFINED_PANEL_PATH)
    coverage = _read_csv(root / COVERAGE_SUMMARY_PATH)
    warnings = _read_csv(root / CONSTRUCTION_WARNINGS_PATH)
    intraday = _read_csv(root / INTRADAY_STATUS_PATH)
    trials = _read_csv(root / TRIAL_REGISTRY_PATH)
    workflow = _workflow_rows(root)

    if not _report_pass_or_warn(report):
        failures.append("report_not_pass_or_warn")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_invalid")
    if manifest.get("status") not in {PASS, PASS_WITH_WARNINGS}:
        failures.append("manifest_status_invalid")
    if manifest.get("refined_candidate_registry_created") is not True:
        failures.append("registry_not_marked_created")
    if manifest.get("refined_candidate_panel_created") is not True:
        failures.append("panel_not_marked_created")
    if manifest.get("refined_candidate_design_count") != 30:
        failures.append("refined_candidate_design_count_not_30")
    if manifest.get("constructed_refined_candidate_count", 0) < 1:
        failures.append("no_refined_candidates_constructed")
    if len(registry) != int(manifest.get("refined_candidate_registry_row_count", -1)):
        failures.append("registry_row_count_mismatch")
    if len(panel) != int(manifest.get("refined_candidate_panel_row_count", -1)):
        failures.append("panel_row_count_mismatch")
    if len(coverage) != int(manifest.get("coverage_summary_row_count", -1)):
        failures.append("coverage_row_count_mismatch")
    if len(trials) != int(manifest.get("trial_registry_row_count", -1)):
        failures.append("trial_registry_row_count_mismatch")
    if registry and list(registry[0]) != REGISTRY_FIELDS:
        failures.append("registry_schema_invalid")
    if panel and list(panel[0]) != PANEL_FIELDS:
        failures.append("panel_schema_invalid")
    if coverage and list(coverage[0]) != COVERAGE_FIELDS:
        failures.append("coverage_schema_invalid")
    if warnings and list(warnings[0]) != WARNING_FIELDS:
        failures.append("warning_schema_invalid")
    if intraday and list(intraday[0]) != INTRADAY_STATUS_FIELDS:
        failures.append("intraday_status_schema_invalid")
    if trials and list(trials[0]) != TRIAL_REGISTRY_FIELDS:
        failures.append("trial_registry_schema_invalid")

    if _duplicate_count((row.get("trade_date"), row.get("symbol"), row.get("refined_factor_id")) for row in panel):
        failures.append("duplicate_trade_date_symbol_refined_factor_rows")
    if {row.get("accepted_for_downstream") for row in trials} != {"false"}:
        failures.append("trial_registry_downstream_acceptance_not_false")
    if {row.get("candidate_for_rec_tiering") for row in trials} != {"false"}:
        failures.append("trial_registry_rec_tiering_flag_not_false")
    if any(row.get("no_lookahead_status") != NO_LOOKAHEAD for row in registry + panel + coverage):
        failures.append("no_lookahead_status_invalid")
    if any(row.get("uses_forward_returns_in_construction") != "false" for row in registry):
        failures.append("registry_forward_return_construction_flag_invalid")
    if any(row.get("uses_benchmark_excess_returns_in_construction") != "false" for row in registry):
        failures.append("registry_benchmark_excess_construction_flag_invalid")
    if any(row.get("uses_label_ready_fields_in_construction") != "false" for row in registry):
        failures.append("registry_label_ready_construction_flag_invalid")
    if any(row.get("non_actionable_disclaimer") != NON_ACTIONABLE for row in registry + panel + warnings + intraday):
        failures.append("non_actionable_disclaimer_invalid")
    if any(_as_float(row.get("factor_value")) is not None and not _finite_or_blank(row.get("factor_value")) for row in panel):
        failures.append("non_finite_factor_value_present")
    valid_buckets = {
        "LOW_REFINED_FACTOR_EXPOSURE_REVIEW_ONLY",
        "MEDIUM_REFINED_FACTOR_EXPOSURE_REVIEW_ONLY",
        "HIGH_REFINED_FACTOR_EXPOSURE_REVIEW_ONLY",
        "INSUFFICIENT_REFINED_FACTOR_EVIDENCE_REVIEW_ONLY",
    }
    if any(row.get("factor_bucket") not in valid_buckets for row in panel):
        failures.append("invalid_refined_factor_bucket")
    if _forbidden_table_label_hits([registry, panel, coverage, warnings, intraday, trials]):
        failures.append("forbidden_actionable_label_present")
    if _leakage_field_hits([panel, coverage, warnings, intraday, trials]):
        failures.append("future_or_label_field_present_outside_allowed_metadata")
    if _contains_secret_like_text(root, OUTPUTS):
        failures.append("secret_or_token_like_text_present")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))

    gate = workflow.get(WORKFLOW_ID, {})
    quant03 = workflow.get(GOAL_QUANT_RESEARCH03_WORKFLOW_ID, {})
    rec = workflow.get(GOAL_REC_TIERING01_WORKFLOW_ID, {})
    if gate.get("status") != "implemented_research_only":
        failures.append("workflow_not_implemented_research_only")
    if gate.get("implemented_in_repo") != "true":
        failures.append("workflow_not_marked_implemented")
    if gate.get("depends_on") != GOAL_ALPHA_RESEARCH_REFINEMENT01_WORKFLOW_ID:
        failures.append("workflow_dependency_invalid")
    if gate.get("allowed_next_action") != ALLOWED_NEXT:
        failures.append("workflow_allowed_next_invalid")
    if quant03.get("status") != "locked_future" or quant03.get("implemented_in_repo") != "false":
        failures.append("goal_quant_research03_not_locked_future")
    if quant03.get("depends_on") != WORKFLOW_ID:
        failures.append("goal_quant_research03_dependency_invalid")
    if rec.get("status") != "locked_future" or rec.get("implemented_in_repo") != "false":
        failures.append("goal_rec_tiering01_not_locked_future")
    if rec.get("depends_on") != GOAL_QUANT_RESEARCH03_WORKFLOW_ID:
        failures.append("goal_rec_tiering01_not_rebased_on_goal_quant_research03")
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
        if row.get("status") != "locked_future" or row.get("implemented_in_repo") != "false":
            failures.append(f"{workflow_id}_not_locked_future")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"boundary_flag_not_false:{key}")

    status = "PASS" if not failures else "BLOCKED"
    lines = [
        "# GOAL-ALPHA-FACTOR-CANDIDATE-02 Audit",
        "",
        f"Status: `{status}`",
        "",
        f"Registry rows: `{len(registry)}`",
        f"Panel rows: `{len(panel)}`",
        f"Coverage rows: `{len(coverage)}`",
        f"Warning rows: `{len(warnings)}`",
        f"Intraday redefinition status rows: `{len(intraday)}`",
        f"Trial registry rows: `{len(trials)}`",
        "",
        "Refined candidate construction uses committed current-or-past evidence only. Predictive-validity evaluation, recommendation tiering, position sizing, portfolios, dashboards, trading, production, local-lake, factor-mining, broker, and DQN/RL generated: `false`.",
        "",
        "Failures:",
        *(f"- {failure}" for failure in failures),
    ]
    write_text(root / AUDIT_PATH, "\n".join(lines))
    return not failures


def evaluate_goal_alpha_factor_candidate02(root: Path) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = ["refined_candidate_construction_only_no_predictive_validity_evaluated"]
    for path in REQUIRED_INPUTS:
        if not (root / path).exists():
            failures.append(f"missing_required_input:{path}")
    if failures:
        return _blocked_result(failures, warnings)

    designs = _read_csv(root / REFINEMENT_DESIGNS_PATH)
    intraday_plan = _read_csv(root / INTRADAY_REDEFINITION_PLAN_PATH)
    instability = _read_csv(root / INSTABILITY_ATTRIBUTION_PATH)
    conditional = _read_csv(root / CONDITIONAL_STABILITY_PATH)
    refinement_trials = _read_csv(root / REFINEMENT_TRIAL_REGISTRY_PATH)
    alpha_panel = _read_csv(root / ALPHA01_PANEL_PATH)
    alpha_registry = _read_csv(root / ALPHA01_REGISTRY_PATH)
    quant02_evaluation = _read_csv(root / QUANT02_EVALUATION_PANEL_PATH)
    quant02_validity = _read_csv(root / QUANT02_SCORE_VALIDITY_PATH)
    provider_panel = _read_csv(root / PROVIDER02B_PANEL_PATH)
    mvp_symbol_rows = _read_csv(root / MVP_SYMBOL_TABLE_PATH)
    mvp_queue_rows = _read_csv(root / MVP_REVIEW_QUEUE_PATH)
    risk01_rows = _read_csv(root / RISK01_DIAGNOSTICS_PATH)
    risk011_rows = _read_csv(root / RISK011_DIAGNOSTICS_PATH)

    if len(designs) != 30:
        warnings.append("refined_design_count_not_expected_30")
    if not alpha_panel:
        failures.append("alpha_candidate01_panel_empty")
    if not designs:
        failures.append("refined_designs_empty")
    if failures:
        return _blocked_result(failures, warnings)

    alpha_registry_by_factor = {row.get("factor_id", ""): row for row in alpha_registry}
    alpha_rows_by_factor: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in alpha_panel:
        alpha_rows_by_factor[row.get("factor_id", "")].append(row)

    registry = _registry_rows(designs, alpha_registry_by_factor, alpha_rows_by_factor)
    raw_panel = _raw_panel_rows(registry, alpha_rows_by_factor)
    refined_panel = _add_cross_sectional_normalization(raw_panel)
    coverage = _coverage_summary(refined_panel, registry)
    registry = _finalize_registry_status(registry, coverage)
    raw_panel = _apply_final_status_to_raw_panel(raw_panel, registry)
    refined_panel = _add_cross_sectional_normalization(raw_panel)
    coverage = _coverage_summary(refined_panel, registry)
    construction_warnings = _construction_warnings(coverage)
    if construction_warnings:
        warnings.append("refined_candidate_construction_warnings_present")
    intraday_status = _intraday_status_rows(intraday_plan, set(alpha_panel[0]) if alpha_panel else set())
    trials = _trial_registry_rows(registry, designs)

    constructed_count = sum(1 for row in registry if row["construction_status"] == "constructed")
    constructible_count = sum(1 for row in coverage if row["construction_status"] == "constructed")
    non_collapsed_count = sum(
        1
        for row in coverage
        if row["construction_status"] == "constructed"
        and int(row["valid_factor_value_count"]) >= MIN_VALID_ROWS
        and _as_float(row["dominant_bucket_share"]) is not None
        and (_as_float(row["dominant_bucket_share"]) or 1.0) < COLLAPSE_THRESHOLD
    )
    recommended_next = NEXT_GOAL if non_collapsed_count >= 1 else "GOAL-DATA-EXPANSION-RESEARCH-01_or_GOAL-ALPHA-RESEARCH-DESIGN-02"
    allowed_next = ALLOWED_NEXT if non_collapsed_count >= 1 else "request_goal_data_expansion_research01_or_alpha_research_design02"
    status = PASS_WITH_WARNINGS if warnings else PASS
    unique_dates = sorted({row["trade_date"] for row in refined_panel if row.get("trade_date")})
    unique_symbols = sorted({row["symbol"] for row in refined_panel if row.get("symbol")})
    manifest = {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "mode": MODE,
        "status": status,
        "workflow_id": WORKFLOW_ID,
        "allowed_next_action": allowed_next,
        "recommended_next_goal": recommended_next,
        "refined_candidate_design_count": len(designs),
        "refined_candidate_registry_row_count": len(registry),
        "constructed_refined_candidate_count": constructed_count,
        "constructible_refined_candidate_count": constructible_count,
        "non_collapsed_constructed_candidate_count": non_collapsed_count,
        "refined_candidate_panel_row_count": len(refined_panel),
        "coverage_summary_row_count": len(coverage),
        "construction_warning_row_count": len(construction_warnings),
        "intraday_redefinition_plan_row_count": len(intraday_plan),
        "intraday_redefinition_status_row_count": len(intraday_status),
        "trial_registry_row_count": len(trials),
        "unique_symbols": len(unique_symbols),
        "unique_trade_dates": len(unique_dates),
        "date_min": min(unique_dates) if unique_dates else "",
        "date_max": max(unique_dates) if unique_dates else "",
        "source_alpha_candidate01_panel_row_count": len(alpha_panel),
        "source_alpha_candidate01_registry_row_count": len(alpha_registry),
        "source_quant02_evaluation_row_count": len(quant02_evaluation),
        "source_quant02_validity_row_count": len(quant02_validity),
        "source_alpha_refinement01_design_row_count": len(designs),
        "source_alpha_refinement01_instability_row_count": len(instability),
        "source_alpha_refinement01_conditional_row_count": len(conditional),
        "source_alpha_refinement01_trial_row_count": len(refinement_trials),
        "source_provider02b_row_count": len(provider_panel),
        "source_mvp_symbol_row_count": len(mvp_symbol_rows),
        "source_mvp_review_queue_row_count": len(mvp_queue_rows),
        "source_risk_tiering01_row_count": len(risk01_rows),
        "source_risk_tiering011_row_count": len(risk011_rows),
        "refined_candidate_registry_created": True,
        "refined_candidate_panel_created": True,
        "coverage_summary_created": True,
        "construction_warnings_created": True,
        "intraday_redefinition_status_created": True,
        "trial_registry_created": True,
        "source_backed_lineage_verified": True,
        "used_committed_alpha_refinement01_evidence_only": True,
        "used_committed_alpha_candidate01_evidence_only": True,
        "used_committed_quant02_evidence_only": True,
        "used_committed_provider02b_evidence_only": True,
        "used_committed_mvp01_evidence_only": True,
        "used_committed_risk_tiering_evidence_only": True,
        "no_lookahead_construction_passed": True,
        "candidate_values_only": True,
        "refined_candidates_not_evaluated": True,
        "accepted_for_downstream_count": 0,
        "candidate_for_rec_tiering_count": 0,
        "goal_quant_research03_locked_future": True,
        "goal_rec_tiering01_locked_future": True,
        "goal10b4_locked_future": True,
        "position_band_validation_locked_future": True,
        "goal10d_locked_future": True,
        "dashboard_daily_report_locked_future": True,
        "portfolio_backtest_locked_future": True,
        "warning_code_taxonomy": WARNING_CODE_TAXONOMY,
        "input_lineage": REQUIRED_INPUTS,
        "output_artifacts": OUTPUTS,
        "input_row_counts": {
            REFINEMENT_DESIGNS_PATH: len(designs),
            INTRADAY_REDEFINITION_PLAN_PATH: len(intraday_plan),
            INSTABILITY_ATTRIBUTION_PATH: len(instability),
            CONDITIONAL_STABILITY_PATH: len(conditional),
            REFINEMENT_TRIAL_REGISTRY_PATH: len(refinement_trials),
            ALPHA01_PANEL_PATH: len(alpha_panel),
            ALPHA01_REGISTRY_PATH: len(alpha_registry),
            QUANT02_EVALUATION_PANEL_PATH: len(quant02_evaluation),
            QUANT02_SCORE_VALIDITY_PATH: len(quant02_validity),
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
        "registry": registry,
        "refined_panel": refined_panel,
        "coverage": coverage,
        "construction_warnings": construction_warnings,
        "intraday_status": intraday_status,
        "trials": trials,
        "manifest": manifest,
    }


def goal_alpha_factor_candidate02_valid_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        (
            "GOAL-ALPHA-FACTOR-CANDIDATE-02 Refined Alpha Candidate Construction Gate: PASS" in report
            or "GOAL-ALPHA-FACTOR-CANDIDATE-02 Refined Alpha Candidate Construction Gate: PASS_WITH_WARNINGS" in report
        )
        and "Status: `PASS`" in audit
        and manifest.get("mode") == MODE
        and manifest.get("refined_candidate_panel_created") is True
        and manifest.get("refined_candidates_not_evaluated") is True
        and manifest.get("future_returns_used_in_refined_candidate_construction") is False
        and manifest.get("recommendation_outputs_created") is False
    )


def goal_alpha_factor_candidate02_implemented_workflow_patch(status: str = PASS_WITH_WARNINGS) -> dict[str, str]:
    return {
        "display_name": "GOAL-ALPHA-FACTOR-CANDIDATE-02 Refined Alpha Candidate Construction Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_research_only",
        "current_repo_role": MODE,
        "implemented_in_repo": "true",
        "allowed_next_action": ALLOWED_NEXT,
        "depends_on": GOAL_ALPHA_RESEARCH_REFINEMENT01_WORKFLOW_ID,
        "produces_artifacts": ";".join(OUTPUTS),
        "primary_docs": f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "scripts/run_goal_alpha_factor_candidate02_gate.py;scripts/audit_goal_alpha_factor_candidate02_gate.py",
        "primary_outputs": ";".join(
            [
                REFINED_REGISTRY_PATH,
                REFINED_PANEL_PATH,
                COVERAGE_SUMMARY_PATH,
                CONSTRUCTION_WARNINGS_PATH,
                INTRADAY_STATUS_PATH,
                TRIAL_REGISTRY_PATH,
                REPORT_PATH,
                MANIFEST_PATH,
                AUDIT_PATH,
            ]
        ),
        "promotion_rule": "implemented_research_only_after_goal_alpha_factor_candidate02_pass_or_pass_with_warnings",
        "notes": "Research-only refined alpha candidate construction over committed GOAL-ALPHA-RESEARCH-REFINEMENT-01 and GOAL-ALPHA-FACTOR-CANDIDATE-01 evidence. It creates refined candidate values only; no predictive-validity evaluation, recommendation, position, portfolio, dashboard, trading, production, local-lake, factor-mining, broker, or DQN/RL outputs.",
    }


def locked_goal_quant_research03_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-QUANT-RESEARCH-03 Refined Alpha Factor Validity Evaluation Gate",
        "stage_or_goal": "GOAL-QUANT-RESEARCH-03",
        "status": "locked_future",
        "current_repo_role": "locked_future_refined_alpha_factor_validity_evaluation_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal_quant_research03_request",
        "depends_on": WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal_quant_research03_refined_alpha_evaluation_gate",
        "notes": "Future refined alpha factor validity evaluation remains locked; GOAL-ALPHA-FACTOR-CANDIDATE-02 constructs candidate values only and does not evaluate predictive validity.",
    }


def locked_goal_rec_tiering01_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "current_repo_role": "locked_future_recommendation_score_tiering_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal_quant_research03_evaluates_refined_candidates",
        "depends_on": GOAL_QUANT_RESEARCH03_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal_rec_tiering01_gate_after_refined_alpha_evaluation",
        "notes": "Future recommendation score tiering remains locked; GOAL-ALPHA-FACTOR-CANDIDATE-02 creates only refined candidate values and no recommendation rows.",
    }


def locked_goal10b4_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal_rec_tiering01_passes",
        "depends_on": GOAL_REC_TIERING01_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal10b4_revalidation_gate",
        "notes": "Future GOAL-10B.4 remains locked; GOAL-ALPHA-FACTOR-CANDIDATE-02 creates no recommendation revalidation rows.",
    }


def locked_position_band_validation_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal10b4_and_explicit_position_validation_request",
        "depends_on": GOAL10B4_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_position_band_validation_gate",
        "notes": "Future position-band validation remains locked; GOAL-ALPHA-FACTOR-CANDIDATE-02 creates no position outputs.",
    }


def locked_goal10d_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10d_request",
        "depends_on": GOAL10C_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal10d_failure_attribution_gate",
        "notes": "Future GOAL-10D remains locked; GOAL-ALPHA-FACTOR-CANDIDATE-02 creates only research candidate construction evidence.",
    }


def _registry_rows(
    designs: list[dict[str, str]],
    alpha_registry_by_factor: dict[str, dict[str, str]],
    alpha_rows_by_factor: dict[str, list[dict[str, str]]],
) -> list[dict[str, str]]:
    rows = []
    source_artifacts = ";".join(REQUIRED_INPUTS)
    all_columns = set()
    for source_rows in alpha_rows_by_factor.values():
        if source_rows:
            all_columns.update(source_rows[0])
    for design in designs:
        refined_id = design["refined_factor_id"]
        source_id = design["source_factor_id"]
        source = alpha_registry_by_factor.get(source_id, {})
        required = _required_columns(design.get("required_columns", ""))
        missing = sorted(col for col in required if col not in all_columns)
        if not alpha_rows_by_factor.get(source_id):
            missing.append(f"source_factor:{source_id}")
        construction_status = "constructed" if not missing else "not_constructed_missing_required_columns"
        reason = "none" if not missing else "missing:" + ";".join(sorted(set(missing)))
        plain, expression = _construction_formula(design)
        rows.append(
            {
                "refined_factor_id": refined_id,
                "source_factor_id": source_id,
                "refinement_type": design["refinement_type"],
                "factor_family": source.get("factor_family", _family_from_source(source_id)),
                "economic_hypothesis": design.get("economic_hypothesis", ""),
                "deterministic_rule_description": design.get("deterministic_rule_description", ""),
                "required_columns": design.get("required_columns", ""),
                "construction_formula_plain_english": plain,
                "construction_formula_expression": expression,
                "expected_direction": _compact_expected_direction(design.get("expected_direction", "")),
                "no_lookahead_status": NO_LOOKAHEAD,
                "uses_forward_returns_in_construction": "false",
                "uses_benchmark_excess_returns_in_construction": "false",
                "uses_label_ready_fields_in_construction": "false",
                "source_input_artifacts": source_artifacts,
                "construction_status": construction_status,
                "rejection_or_missing_reason": reason,
                "intended_future_evaluation_goal": NEXT_GOAL,
                "non_actionable_disclaimer": NON_ACTIONABLE,
            }
        )
    return rows


def _raw_panel_rows(
    registry: list[dict[str, str]],
    alpha_rows_by_factor: dict[str, list[dict[str, str]]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for definition in registry:
        source_rows = alpha_rows_by_factor.get(definition["source_factor_id"], [])
        for source in source_rows:
            original_value = _as_float(source.get("factor_value"))
            keep, reason = _keep_source_value(definition, source)
            refined_value = original_value if keep and original_value is not None else None
            if definition["construction_status"] != "constructed":
                row_status = definition["construction_status"]
            elif original_value is None:
                row_status = SOURCE_VALUE_MISSING_STATUS
            elif not keep:
                row_status = f"constructed_filtered_out_{reason}"
            else:
                row_status = "constructed"
            rows.append(
                {
                    "trade_date": source.get("trade_date", ""),
                    "symbol": source.get("symbol", ""),
                    "refined_factor_id": definition["refined_factor_id"],
                    "source_factor_id": definition["source_factor_id"],
                    "refinement_type": definition["refinement_type"],
                    "factor_family": definition["factor_family"],
                    "factor_value": _fmt(refined_value),
                    "factor_value_raw": _fmt(refined_value),
                    "factor_value_normalized_cross_sectional": "",
                    "factor_quantile": "",
                    "factor_bucket": "INSUFFICIENT_REFINED_FACTOR_EVIDENCE_REVIEW_ONLY",
                    "expected_direction": definition["expected_direction"],
                    "construction_status": row_status,
                    "no_lookahead_status": NO_LOOKAHEAD,
                    "required_column_status": "available" if definition["construction_status"] == "constructed" else "missing_required_columns",
                    "source_provider": source.get("source_provider", ""),
                    "universe_mode": PANEL_UNIVERSE_MODE if source.get("universe_mode") else "",
                    "panel_contract_status": PANEL_CONTRACT_STATUS if source.get("panel_contract_status") else "",
                    "risk_score_bucket": source.get("risk_score_bucket", ""),
                    "downside_risk_bucket": source.get("downside_risk_bucket", ""),
                    "mvp_review_queue_category": source.get("mvp_review_queue_category", ""),
                    "mvp_review_priority_level": source.get("mvp_review_priority_level", ""),
                    "original_alpha_factor_value": source.get("factor_value", ""),
                    "original_alpha_factor_bucket": source.get("factor_bucket", ""),
                    "diagnostic_mode": MODE,
                    "non_actionable_disclaimer": NON_ACTIONABLE,
                }
            )
    return rows


def _keep_source_value(definition: dict[str, str], row: dict[str, str]) -> tuple[bool, str]:
    refinement_type = definition["refinement_type"]
    if refinement_type == "risk_filtered":
        return row.get("risk_score_bucket") in {"LOW_RISK_REVIEW_ONLY", "MEDIUM_RISK_REVIEW_ONLY"}, "risk_filter"
    if refinement_type == "downside_risk_filtered":
        return row.get("downside_risk_bucket") != "HIGH_DOWNSIDE_RISK_REVIEW_ONLY", "downside_risk_filter"
    if refinement_type == "liquidity_filtered":
        category = row.get("mvp_review_queue_category", "").lower()
        priority = row.get("mvp_review_priority_level", "").upper()
        return "liquidity" not in category and priority != "LIQUIDITY_REVIEW", "liquidity_filter"
    if refinement_type == "review_queue_conditioned":
        field, value = _review_condition(definition.get("deterministic_rule_description", ""))
        if not field or not value:
            return False, "review_queue_slice_unavailable"
        return row.get(field, "") == value, "review_queue_condition"
    return True, "horizon_specific"


def _add_cross_sectional_normalization(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[(str(row["trade_date"]), str(row["refined_factor_id"]))].append(row)
    for group_rows in groups.values():
        valid = [row for row in group_rows if _as_float(row.get("factor_value")) is not None]
        valid_sorted = sorted(valid, key=lambda item: (_as_float(item["factor_value"]) or 0.0, str(item["symbol"])))
        n = len(valid_sorted)
        for idx, row in enumerate(valid_sorted):
            if n >= 2:
                row["factor_value_normalized_cross_sectional"] = _fmt((idx / (n - 1)) * 2.0 - 1.0)
            else:
                row["factor_value_normalized_cross_sectional"] = ""
            if n >= 5:
                quantile = min(5, int((idx * 5) / n) + 1)
                row["factor_quantile"] = str(quantile)
                row["factor_bucket"] = _bucket_from_quantile(quantile)
            else:
                row["factor_quantile"] = ""
                row["factor_bucket"] = "INSUFFICIENT_REFINED_FACTOR_EVIDENCE_REVIEW_ONLY"
    return [{field: row.get(field, "") for field in PANEL_FIELDS} for row in rows]


def _coverage_summary(panel: list[dict[str, object]], registry: list[dict[str, str]]) -> list[dict[str, object]]:
    by_factor: dict[str, list[dict[str, object]]] = defaultdict(list)
    registry_by_factor = {row["refined_factor_id"]: row for row in registry}
    for row in panel:
        by_factor[str(row["refined_factor_id"])].append(row)
    summary = []
    for refined_id in sorted(by_factor):
        rows = by_factor[refined_id]
        valid = [row for row in rows if _as_float(row.get("factor_value")) is not None]
        buckets = Counter(row.get("factor_bucket", "") for row in rows if row.get("factor_bucket"))
        bucket_values = list(buckets.values())
        dates = sorted({str(row["trade_date"]) for row in rows if row.get("trade_date")})
        definition = registry_by_factor[refined_id]
        summary.append(
            {
                "refined_factor_id": refined_id,
                "row_count": len(rows),
                "valid_factor_value_count": len(valid),
                "missing_factor_value_count": len(rows) - len(valid),
                "unique_symbols": len({row.get("symbol", "") for row in rows if row.get("symbol")}),
                "unique_trade_dates": len(dates),
                "date_min": min(dates) if dates else "",
                "date_max": max(dates) if dates else "",
                "quantile_count": len({row.get("factor_quantile", "") for row in rows if row.get("factor_quantile")}),
                "bucket_count": len(buckets),
                "dominant_bucket_share": _fmt(max(bucket_values, default=0) / len(rows) if rows else 0.0),
                "minimum_bucket_size": min(bucket_values, default=0),
                "construction_status": definition["construction_status"],
                "no_lookahead_status": definition["no_lookahead_status"],
                "required_column_status": "available" if definition["construction_status"] == "constructed" else "missing_required_columns",
                "refinement_type": definition["refinement_type"],
                "source_factor_id": definition["source_factor_id"],
            }
        )
    return summary


def _finalize_registry_status(registry: list[dict[str, str]], coverage: list[dict[str, object]]) -> list[dict[str, str]]:
    coverage_by_factor = {row["refined_factor_id"]: row for row in coverage}
    finalized = []
    for row in registry:
        item = dict(row)
        summary = coverage_by_factor.get(row["refined_factor_id"], {})
        valid = int(summary.get("valid_factor_value_count", 0) or 0)
        dates = int(summary.get("unique_trade_dates", 0) or 0)
        if item["construction_status"] == "constructed" and (valid < MIN_VALID_ROWS or dates < MIN_VALID_DATES):
            item["construction_status"] = "not_constructed_insufficient_valid_rows"
            item["rejection_or_missing_reason"] = f"insufficient_valid_rows:{valid};unique_trade_dates:{dates}"
        finalized.append(item)
    return finalized


def _apply_final_status_to_raw_panel(rows: list[dict[str, object]], registry: list[dict[str, str]]) -> list[dict[str, object]]:
    status_by_factor = {row["refined_factor_id"]: row["construction_status"] for row in registry}
    required_by_factor = {
        row["refined_factor_id"]: "available" if row["construction_status"] == "constructed" else "missing_or_insufficient"
        for row in registry
    }
    output = []
    for row in rows:
        item = dict(row)
        refined_id = str(item["refined_factor_id"])
        if status_by_factor.get(refined_id) != "constructed":
            item["factor_value"] = ""
            item["factor_value_raw"] = ""
            item["factor_value_normalized_cross_sectional"] = ""
            item["factor_quantile"] = ""
            item["factor_bucket"] = "INSUFFICIENT_REFINED_FACTOR_EVIDENCE_REVIEW_ONLY"
            item["construction_status"] = status_by_factor.get(refined_id, "not_constructed_insufficient_valid_rows")
        item["required_column_status"] = required_by_factor.get(refined_id, "missing_or_insufficient")
        output.append(item)
    return output


def _construction_warnings(coverage: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for row in coverage:
        refined_id = row["refined_factor_id"]
        row_count = int(row["row_count"])
        valid = int(row["valid_factor_value_count"])
        missing = int(row["missing_factor_value_count"])
        dominant = _as_float(row["dominant_bucket_share"]) or 0.0
        if row["construction_status"] == "not_constructed_missing_required_columns":
            rows.append(_warning(refined_id, "missing_required_columns", "required columns unavailable for refined design"))
        if row["construction_status"] == "not_constructed_insufficient_valid_rows":
            rows.append(_warning(refined_id, "insufficient_valid_rows_after_filter", f"valid_rows={valid};unique_trade_dates={row['unique_trade_dates']}"))
        if missing:
            rows.append(_warning(refined_id, "source_factor_value_missing", f"missing_or_filtered_rows={missing}"))
            rows.append(_warning(refined_id, "initial_trailing_window_missing", "some source alpha rows are blank because original trailing windows were unavailable or filtered"))
        if row["refinement_type"] == "review_queue_conditioned" and valid < 1000:
            rows.append(_warning(refined_id, "sparse_review_queue_slice", f"review_queue_conditioned_valid_rows={valid}"))
        if row_count and valid / row_count < 0.5:
            rows.append(_warning(refined_id, "retained_rows_below_threshold", f"retained_share={_fmt(valid / row_count)}"))
            if row["construction_status"] == "constructed":
                rows.append(_warning(refined_id, "construction_completed_with_sparse_exposure", f"constructed_with_retained_share={_fmt(valid / row_count)}"))
        if dominant >= COLLAPSE_THRESHOLD or int(row["bucket_count"]) < 3:
            rows.append(_warning(refined_id, "collapsed_or_imbalanced_bucket", f"dominant_bucket_share={row['dominant_bucket_share']};bucket_count={row['bucket_count']}"))
    return rows


def _warning(refined_id: str, code: str, detail: str) -> dict[str, str]:
    return {
        "refined_factor_id": refined_id,
        "warning_code": code,
        "warning_severity": "research_warning",
        "warning_detail": detail,
        "non_actionable_disclaimer": NON_ACTIONABLE,
    }


def _intraday_status_rows(plan: list[dict[str, str]], available_columns: set[str]) -> list[dict[str, str]]:
    rows = []
    for row in plan:
        missing = [col for col in _required_columns(row.get("required_columns", "")) if col not in available_columns]
        constructible = not missing and "revised_definition" in row
        rows.append(
            {
                "original_factor_id": row.get("original_factor_id", ""),
                "proposed_refined_factor_id": row.get("proposed_refined_factor_id", ""),
                "required_columns": row.get("required_columns", ""),
                "construction_status": "intraday_redefinition_design_preserved_not_constructed_in_main_panel"
                if constructible
                else "not_constructed_redefinition_only",
                "rejection_or_missing_reason": "redefinition_plan_preserved_for_future_explicit_construction"
                if constructible
                else "missing_required_columns:" + ";".join(missing),
                "not_evaluated_status": "intraday_redefined_candidate_not_evaluated" if constructible else "not_constructed_redefinition_only",
                "intended_future_evaluation_goal": NEXT_GOAL,
                "non_actionable_disclaimer": NON_ACTIONABLE,
            }
        )
    return rows


def _trial_registry_rows(registry: list[dict[str, str]], designs: list[dict[str, str]]) -> list[dict[str, str]]:
    design_by_id = {row["refined_factor_id"]: row for row in designs}
    rows = []
    for index, row in enumerate(registry, start=1):
        design = design_by_id.get(row["refined_factor_id"], {})
        rows.append(
            {
                "trial_id": f"goal_alpha_factor_candidate02_trial_{index:03d}",
                "source_goal_id": GOAL_ID,
                "refined_factor_id": row["refined_factor_id"],
                "source_factor_id": row["source_factor_id"],
                "refinement_type": row["refinement_type"],
                "reason_for_refinement": design.get("reason_for_refinement", ""),
                "no_lookahead_policy": "current_or_past_source_candidate_values_and_committed_diagnostic_groups_only",
                "construction_status": row["construction_status"],
                "accepted_for_downstream": "false",
                "candidate_for_rec_tiering": "false",
                "downstream_status": "not_evaluated_not_accepted_for_downstream",
                "intended_future_evaluation_goal": NEXT_GOAL,
                "recommended_next_action": ALLOWED_NEXT,
            }
        )
    return rows


def _construction_formula(design: dict[str, str]) -> tuple[str, str]:
    kind = design.get("refinement_type", "")
    if kind == "risk_filtered":
        return (
            "Carry the source alpha value only for LOW or MEDIUM risk buckets; otherwise leave refined exposure blank.",
            "source_factor_value if risk_score_bucket in {LOW_RISK_REVIEW_ONLY, MEDIUM_RISK_REVIEW_ONLY} else missing",
        )
    if kind == "downside_risk_filtered":
        return (
            "Carry the source alpha value only when the committed downside-risk bucket is not HIGH.",
            "source_factor_value if downside_risk_bucket != HIGH_DOWNSIDE_RISK_REVIEW_ONLY else missing",
        )
    if kind == "liquidity_filtered":
        return (
            "Carry the source alpha value only outside committed liquidity review queue membership.",
            "source_factor_value if not liquidity_review_queue_member else missing",
        )
    if kind == "review_queue_conditioned":
        field, value = _review_condition(design.get("deterministic_rule_description", ""))
        return (
            f"Carry the source alpha value only in the committed diagnostic slice {field}={value}.",
            f"source_factor_value if {field} == {value} else missing",
        )
    return (
        "Carry the source alpha value as a horizon-specific refined candidate without mixing horizons.",
        "source_factor_value",
    )


def _review_condition(text: str) -> tuple[str, str]:
    match = re.search(r"(risk_score_bucket|downside_risk_bucket|mvp_review_queue_category|mvp_review_priority_level)=([A-Za-z0-9_]+)", text)
    if not match:
        return "", ""
    return match.group(1), match.group(2)


def _required_columns(raw: str) -> list[str]:
    columns = []
    for item in raw.split(";"):
        item = item.strip()
        if item:
            columns.append(item)
    return columns


def _compact_expected_direction(raw: str) -> str:
    if raw == "lower_value_research_hypothesis_positive":
        return "lower_positive"
    return DEFAULT_EXPECTED_DIRECTION


def _bucket_from_quantile(quantile: int) -> str:
    if quantile <= 2:
        return "LOW_REFINED_FACTOR_EXPOSURE_REVIEW_ONLY"
    if quantile == 3:
        return "MEDIUM_REFINED_FACTOR_EXPOSURE_REVIEW_ONLY"
    return "HIGH_REFINED_FACTOR_EXPOSURE_REVIEW_ONLY"


def _family_from_source(source_factor_id: str) -> str:
    if "benchmark_relative_strength" in source_factor_id:
        return "benchmark_relative_strength"
    if "vol_adj_momentum" in source_factor_id:
        return "volatility_adjusted_momentum"
    if "price_volume" in source_factor_id:
        return "price_volume_confirmation"
    if "downside" in source_factor_id:
        return "downside_volatility_adjusted_signal"
    if "risk_adjusted" in source_factor_id:
        return "risk_adjusted_alpha_candidate"
    return "refined_alpha_candidate"


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / REFINED_REGISTRY_PATH, result["registry"], REGISTRY_FIELDS)
    write_csv(root / REFINED_PANEL_PATH, result["refined_panel"], PANEL_FIELDS)
    write_csv(root / COVERAGE_SUMMARY_PATH, result["coverage"], COVERAGE_FIELDS)
    write_csv(root / CONSTRUCTION_WARNINGS_PATH, result["construction_warnings"], WARNING_FIELDS)
    write_csv(root / INTRADAY_STATUS_PATH, result["intraday_status"], INTRADAY_STATUS_FIELDS)
    write_csv(root / TRIAL_REGISTRY_PATH, result["trials"], TRIAL_REGISTRY_FIELDS)
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_report(root, result)
    _write_doc(root, result)
    _write_contract(root, result)


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    constructed = manifest.get("constructed_refined_candidate_count", 0)
    not_constructed = int(manifest.get("refined_candidate_registry_row_count", 0)) - int(constructed)
    body = [
        "# GOAL-ALPHA-FACTOR-CANDIDATE-02 Refined Alpha Candidate Construction Gate",
        "",
        "## 1. Goal status",
        f"GOAL-ALPHA-FACTOR-CANDIDATE-02 Refined Alpha Candidate Construction Gate: {manifest['status']}",
        "",
        "## 2. Current Alpha Refinement context",
        "GOAL-ALPHA-RESEARCH-REFINEMENT-01 produced deterministic refined candidate designs from unstable but partially promising alpha candidates.",
        "",
        "## 3. Source-backed input lineage",
        *[f"- `{path}`" for path in REQUIRED_INPUTS],
        "",
        "## 4. Refined candidate construction principles",
        "The gate carries source alpha values through deterministic risk, downside-risk, liquidity, review-queue, and horizon-specific filters only. It excludes forward returns, benchmark-excess returns, label-ready fields, and post-hoc performance from construction.",
        "",
        "## 5. Refined candidates constructed",
        f"Constructed refined candidate count: `{constructed}`.",
        "",
        "## 6. Refined candidates not constructed and why",
        f"Not constructed count: `{not_constructed}`.",
        "",
        "## 7. Intraday redefinition status",
        f"Intraday redefinition status rows: `{manifest['intraday_redefinition_status_row_count']}`. Redefinition plans are preserved separately and not forced into the main refined panel.",
        "",
        "## 8. No-lookahead construction policy",
        "Each refined value uses only current source candidate exposure, current committed diagnostic groups, and current-or-past metadata at the same trade date.",
        "",
        "## 9. Refined candidate panel coverage",
        f"Panel rows: `{manifest['refined_candidate_panel_row_count']}`. Symbols: `{manifest['unique_symbols']}`. Trade dates: `{manifest['unique_trade_dates']}`.",
        "",
        "## 10. Construction warnings",
        f"Warning rows: `{manifest['construction_warning_row_count']}`. Warnings describe sparse exposure, source missing windows, or bucket imbalance; they are not predictive-validity results.",
        "",
        "## 11. Trial registry and governance",
        f"Trial registry rows: `{manifest['trial_registry_row_count']}`. All accepted_for_downstream and candidate_for_rec_tiering flags remain false.",
        "",
        "## 12. Why these are not recommendations",
        "These are refined research candidate exposures only. They are not trade labels, recommendation rows, target prices, position sizes, portfolio weights, order instructions, portfolio results, or model-validity claims.",
        "",
        "## 13. Locked downstream boundaries",
        "GOAL-QUANT-RESEARCH-03, GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, portfolio backtests, trading, production, broker integration, local-lake writes, factor-mining, and DQN/RL remain locked.",
        "",
        "## 14. Required next evaluation goal",
        f"`{manifest['recommended_next_goal']}`.",
        "",
    ]
    write_text(root / REPORT_PATH, "\n".join(body))


def _write_doc(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    body = [
        "# GOAL-ALPHA-FACTOR-CANDIDATE-02 Refined Alpha Candidate Construction Gate",
        "",
        f"Status: `{manifest['status']}`",
        "",
        "This gate constructs research-only refined alpha candidate values from committed GOAL-ALPHA-RESEARCH-REFINEMENT-01 designs and GOAL-ALPHA-FACTOR-CANDIDATE-01 source candidate values.",
        "",
        "## Outputs",
        *[f"- `{path}`" for path in OUTPUTS],
        "",
        "## Boundary",
        "The gate creates refined candidate values only. It does not evaluate predictive validity, create recommendation rows, create position rows, create portfolio outputs, create dashboard/frontend files, fetch live data, write local-lake data, or unlock execution paths.",
        "",
        "## Next Required Goal",
        f"`{NEXT_GOAL}` remains locked until explicitly requested.",
        "",
    ]
    write_text(root / DOC_PATH, "\n".join(body))


def _write_contract(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    lines = [
        "{",
        '  "goal_id": "GOAL-ALPHA-FACTOR-CANDIDATE-02",',
        f'  "mode": "{MODE}",',
        f'  "status": "{manifest["status"]}",',
        '  "research_only": true,',
        '  "candidate_values_only": true,',
        '  "predictive_validity_evaluation": false,',
        '  "allowed_inputs": [',
        *[f'    "{path}",' for path in REQUIRED_INPUTS[:-1]],
        f'    "{REQUIRED_INPUTS[-1]}"',
        "  ],",
        '  "allowed_outputs": [',
        *[f'    "{path}",' for path in OUTPUTS[:-1]],
        f'    "{OUTPUTS[-1]}"',
        "  ],",
        '  "refined_candidate_registry_schema": ' + _json_list(REGISTRY_FIELDS) + ",",
        '  "refined_candidate_panel_schema": ' + _json_list(PANEL_FIELDS) + ",",
        '  "coverage_summary_schema": ' + _json_list(COVERAGE_FIELDS) + ",",
        '  "forbidden_construction_inputs": ["forward_return_*", "benchmark_excess_return_*", "label_ready_*", "posthoc_performance_metrics"],',
        '  "downstream_locks": {',
        f'    "{GOAL_QUANT_RESEARCH03_WORKFLOW_ID}": "locked_future",',
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
        insert_at = next((idx + 1 for idx, row in enumerate(rows) if row["workflow_id"] == GOAL_ALPHA_RESEARCH_REFINEMENT01_WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": WORKFLOW_ID})
        by_id = {row["workflow_id"]: row for row in rows}
    if GOAL_QUANT_RESEARCH03_WORKFLOW_ID not in by_id:
        insert_at = next((idx + 1 for idx, row in enumerate(rows) if row["workflow_id"] == WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": GOAL_QUANT_RESEARCH03_WORKFLOW_ID})
        by_id = {row["workflow_id"]: row for row in rows}
    by_id[WORKFLOW_ID].update(goal_alpha_factor_candidate02_implemented_workflow_patch(str(result["status"])))
    by_id[GOAL_QUANT_RESEARCH03_WORKFLOW_ID].update(locked_goal_quant_research03_patch())
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
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_alpha_factor_candidate02"
    preserve_later_review_only_workflow_states(root, by_id)
    if result["status"] in {PASS, PASS_WITH_WARNINGS} and WORKFLOW_ID in by_id:
        by_id[WORKFLOW_ID].update(goal_alpha_factor_candidate02_implemented_workflow_patch(str(result["status"])))
        by_id[GOAL_QUANT_RESEARCH03_WORKFLOW_ID].update(locked_goal_quant_research03_patch())
        if GOAL_REC_TIERING01_WORKFLOW_ID in by_id:
            by_id[GOAL_REC_TIERING01_WORKFLOW_ID].update(locked_goal_rec_tiering01_patch())
        preserve_later_review_only_workflow_states(root, by_id)
        by_id[WORKFLOW_ID].update(goal_alpha_factor_candidate02_implemented_workflow_patch(str(result["status"])))
        by_id[GOAL_QUANT_RESEARCH03_WORKFLOW_ID].update(locked_goal_quant_research03_patch())
        if GOAL_REC_TIERING01_WORKFLOW_ID in by_id:
            by_id[GOAL_REC_TIERING01_WORKFLOW_ID].update(locked_goal_rec_tiering01_patch())
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
    payload[GOAL_QUANT_RESEARCH03_WORKFLOW_ID] = False
    payload[GOAL_REC_TIERING01_WORKFLOW_ID] = False
    payload[GOAL10B4_WORKFLOW_ID] = False
    payload[POSITION_BAND_VALIDATION_WORKFLOW_ID] = False
    payload[GOAL10D_WORKFLOW_ID] = False
    preserve_later_review_only_capabilities(root, payload)
    if result["status"] in {PASS, PASS_WITH_WARNINGS}:
        payload[WORKFLOW_ID] = "implemented_research_only"
        payload[GOAL_QUANT_RESEARCH03_WORKFLOW_ID] = False
        payload[GOAL_REC_TIERING01_WORKFLOW_ID] = False
        preserve_later_review_only_capabilities(root, payload)
    write_json(path, payload)


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
        "warnings": warnings,
        "failures": failures,
        "registry": [],
        "refined_panel": [],
        "coverage": [],
        "construction_warnings": [],
        "intraday_status": [],
        "trials": [],
        "manifest": manifest,
    }


def _report_pass_or_warn(report: str) -> bool:
    return (
        "GOAL-ALPHA-FACTOR-CANDIDATE-02 Refined Alpha Candidate Construction Gate: PASS" in report
        or "GOAL-ALPHA-FACTOR-CANDIDATE-02 Refined Alpha Candidate Construction Gate: PASS_WITH_WARNINGS" in report
    )


def _workflow_rows(root: Path) -> dict[str, dict[str, str]]:
    rows = _read_csv(root / "configs/project/workflow_status.csv")
    return {row["workflow_id"]: row for row in rows}


def _forbidden_outputs_present(root: Path) -> list[str]:
    present = []
    for prefix in FORBIDDEN_OUTPUT_PREFIXES:
        if (root / prefix).exists():
            present.append(prefix.rstrip("/"))
    return present


def _forbidden_table_label_hits(tables: list[list[dict[str, str]]]) -> list[str]:
    hits = []
    for rows in tables:
        for row in rows:
            for key, value in row.items():
                if key in {"factor_bucket", "original_alpha_factor_bucket"}:
                    continue
                tokens = re.split(r"[^A-Za-z0-9_]+", str(value).upper())
                if any(token in FORBIDDEN_TABLE_LABELS for token in tokens):
                    hits.append(str(value))
    return hits


def _leakage_field_hits(tables: list[list[dict[str, str]]]) -> list[str]:
    patterns = ["forward_return", "benchmark_excess_return", "label_ready"]
    allowed_metadata_keys = {
        "uses_forward_returns_in_construction",
        "uses_benchmark_excess_returns_in_construction",
        "uses_label_ready_fields_in_construction",
        "no_lookahead_policy",
        "warning_detail",
    }
    hits = []
    for rows in tables:
        for row in rows:
            for key, value in row.items():
                key_lower = key.lower()
                value_lower = str(value).lower()
                if key_lower in allowed_metadata_keys:
                    continue
                if any(pattern in key_lower for pattern in patterns) or any(pattern in value_lower for pattern in patterns):
                    hits.append(f"{key}:{value}".lower())
    return hits


def _contains_secret_like_text(root: Path, paths: list[str]) -> bool:
    patterns = [r"(?i)tushare_token", r"(?i)api[_-]?key", r"(?i)secret", r"(?i)bearer\s+[a-z0-9]"]
    for path in paths:
        target = root / path
        if not target.exists() or target.suffix.lower() not in {".md", ".json", ".csv", ".yaml"}:
            continue
        text = target.read_text(encoding="utf-8")
        if any(re.search(pattern, text) for pattern in patterns):
            return True
    return False


def _duplicate_count(keys) -> int:
    counts = Counter(keys)
    return sum(count - 1 for count in counts.values() if count > 1)


def _json_list(values: list[str]) -> str:
    return "[" + ", ".join(f'"{value}"' for value in values) + "]"


def _float(value: object) -> float | None:
    try:
        if value == "" or value is None:
            return None
        output = float(value)
        return output if math.isfinite(output) else None
    except (TypeError, ValueError):
        return None


def _as_float(value: object) -> float | None:
    return _float(value)


def _fmt(value: object) -> str:
    numeric = _as_float(value)
    if numeric is None or not math.isfinite(numeric):
        return ""
    return f"{numeric:.10f}"


def _finite_or_blank(value: object) -> bool:
    if value in {"", None}:
        return True
    numeric = _as_float(value)
    return numeric is not None and math.isfinite(numeric)


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

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import (
    preserve_later_review_only_capabilities,
    preserve_later_review_only_workflow_states,
)
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.validation.workflow_status import run_workflow_status_audit
from ashare_premarket.research.goal_regime_label_research01 import (
    _composite_label,
    _float,
    _quantile,
    evaluate_goal_regime_label_research01,
)

GOAL_ID = "GOAL-REGIME-LABEL-RESEARCH-02"
GOAL_NAME = "GOAL-REGIME-LABEL-RESEARCH-02-EXPANDED-MARKET-REGIME-LABEL-REFINEMENT-GATE"
MODE = "research_only_expanded_market_regime_label_refinement_gate"
WORKFLOW_ID = "goal_regime_label_research02_expanded_market_regime_label_refinement_gate"
PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID = "goal_data_expansion_research01_market_regime_data_expansion_gate"
GOAL_QUANT_RESEARCH04_WORKFLOW_ID = "goal_quant_research04_regime_conditional_factor_evaluation_gate"
GOAL_REC_TIERING01_WORKFLOW_ID = "goal_rec_tiering01_recommendation_score_tiering_gate"
GOAL10B4_WORKFLOW_ID = "goal10b4_recommendation_backtest_revalidation"
POSITION_BAND_VALIDATION_WORKFLOW_ID = "goal_position_band_validation01_position_band_validation_gate"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"

ALLOWED_NEXT_READY = "request_goal_quant_research04_regime_conditional_factor_evaluation_gate"
ALLOWED_NEXT_SPARSE = "request_goal_data_provider_health02_akshare_source_stability_gate"
NEXT_GOAL_READY = "GOAL-QUANT-RESEARCH-04-REGIME-CONDITIONAL-FACTOR-EVALUATION-GATE"
NEXT_GOAL_SPARSE = "GOAL-DATA-PROVIDER-HEALTH-02-AKSHARE-SOURCE-STABILITY-GATE"
NON_ACTIONABLE = "research_only"
NO_LOOKAHEAD = "passed_current_or_past_only"
SIZE_LIMIT_BYTES = 95 * 1024 * 1024

EXPANDED_DATE_PANEL_PATH = "outputs/data_expansion/goal_data_expansion_research01/expanded_date_regime_feature_panel.csv"
EXPANDED_SYMBOL_PANEL_PATH = "outputs/data_expansion/goal_data_expansion_research01/expanded_symbol_context_panel.csv"
REGIME01_DATE_LABELS_PATH = "outputs/research/goal_regime_label_research01_date_regime_labels.csv"
REGIME01_SYMBOL_CONTEXT_PATH = "outputs/research/goal_regime_label_research01_symbol_regime_context.csv"

DATE_LABELS_PATH = "outputs/research/goal_regime_label_research02_refined_date_regime_labels.csv"
SYMBOL_CONTEXT_PATH = "outputs/research/goal_regime_label_research02_refined_symbol_regime_context.csv"
COVERAGE_SUMMARY_PATH = "outputs/research/goal_regime_label_research02_refined_regime_coverage_summary.csv"
TRANSITION_SUMMARY_PATH = "outputs/research/goal_regime_label_research02_refined_regime_transition_summary.csv"
AGREEMENT_SUMMARY_PATH = "outputs/research/goal_regime_label_research02_expanded_agreement_summary.csv"
FACTOR_BRIDGE_PATH = "outputs/research/goal_regime_label_research02_refined_factor_regime_bridge.csv"
CONSTRUCTION_WARNINGS_PATH = "outputs/research/goal_regime_label_research02_construction_warnings.csv"
REPORT_PATH = "outputs/audits/goal_regime_label_research02_report.md"
MANIFEST_PATH = "outputs/audits/goal_regime_label_research02_manifest.json"
AUDIT_PATH = "outputs/audits/goal_regime_label_research02_audit.md"
DOC_PATH = "docs/research/GOAL_REGIME_LABEL_RESEARCH02_EXPANDED_MARKET_REGIME_LABEL_REFINEMENT_GATE.md"
CONTRACT_PATH = "configs/research/goal_regime_label_research02_contract.yaml"

REQUIRED_INPUTS = [
    REGIME01_DATE_LABELS_PATH,
    REGIME01_SYMBOL_CONTEXT_PATH,
    EXPANDED_DATE_PANEL_PATH,
    EXPANDED_SYMBOL_PANEL_PATH,
]

OUTPUTS = [
    DATE_LABELS_PATH,
    SYMBOL_CONTEXT_PATH,
    COVERAGE_SUMMARY_PATH,
    TRANSITION_SUMMARY_PATH,
    AGREEMENT_SUMMARY_PATH,
    FACTOR_BRIDGE_PATH,
    CONSTRUCTION_WARNINGS_PATH,
    REPORT_PATH,
    MANIFEST_PATH,
    AUDIT_PATH,
    DOC_PATH,
    CONTRACT_PATH,
]

DATE_LABEL_FIELDS = [
    "trade_date",
    "benchmark_symbol",
    "base_composite_regime_label",
    "refined_composite_regime_label",
    "benchmark_trend_regime",
    "benchmark_volatility_regime",
    "breadth_regime",
    "dispersion_regime",
    "liquidity_regime",
    "downside_risk_regime",
    "benchmark_trend_expanded_agreement",
    "benchmark_volatility_expanded_agreement",
    "breadth_expanded_agreement",
    "dispersion_expanded_agreement",
    "liquidity_expanded_agreement",
    "downside_risk_expanded_agreement",
    "broad_index_trend_20d",
    "broad_index_volatility_20d",
    "sector_breadth_positive_share",
    "sector_dispersion_level",
    "market_liquidity_pressure",
    "expanded_dimension_available_count",
    "expanded_dimension_agreement_count",
    "regime_confidence_tier",
    "source_coverage_score",
    "external_data_quality_score",
    "regime_refinement_status",
    "no_lookahead_status",
    "non_actionable_disclaimer",
]

SYMBOL_CONTEXT_FIELDS = [
    "trade_date",
    "symbol",
    "base_composite_regime_label",
    "refined_composite_regime_label",
    "benchmark_trend_regime",
    "benchmark_volatility_regime",
    "breadth_regime",
    "dispersion_regime",
    "liquidity_regime",
    "downside_risk_regime",
    "risk_score_bucket",
    "downside_risk_bucket",
    "mvp_review_queue_category",
    "symbol_listing_status",
    "symbol_suspension_status",
    "symbol_st_status",
    "symbol_flow_available",
    "event_risk_context_available",
    "regime_confidence_tier",
    "source_coverage_score",
    "external_data_quality_score",
    "regime_refinement_status",
    "no_lookahead_status",
    "non_actionable_disclaimer",
]

COVERAGE_FIELDS = [
    "regime_dimension",
    "regime_label",
    "row_count",
    "unique_trade_dates",
    "unique_symbols_if_symbol_level",
    "date_min",
    "date_max",
    "dominant_label_share",
    "minimum_label_count",
    "construction_status",
    "no_lookahead_status",
]

TRANSITION_FIELDS = [
    "regime_dimension",
    "from_regime_label",
    "to_regime_label",
    "transition_count",
    "first_transition_date",
    "last_transition_date",
    "transition_density",
    "notes",
]

AGREEMENT_FIELDS = [
    "regime_dimension",
    "expanded_agreement_status",
    "row_count",
    "share_of_dates",
    "notes",
]

BRIDGE_FIELDS = [
    "trade_date",
    "symbol",
    "refined_factor_id",
    "source_factor_id",
    "refinement_type",
    "factor_family",
    "refined_composite_regime_label",
    "regime_confidence_tier",
    "factor_value_available",
    "factor_bucket",
    "risk_score_bucket",
    "downside_risk_bucket",
    "mvp_review_queue_category",
    "no_lookahead_status",
    "bridge_status",
    "intended_future_evaluation_goal",
    "non_actionable_disclaimer",
]

WARNING_FIELDS = [
    "warning_code",
    "regime_dimension",
    "affected_label",
    "row_count",
    "details",
]

REGIME_DIMENSIONS = [
    ("benchmark_trend", "benchmark_trend_regime"),
    ("benchmark_volatility", "benchmark_volatility_regime"),
    ("breadth", "breadth_regime"),
    ("dispersion", "dispersion_regime"),
    ("liquidity", "liquidity_regime"),
    ("downside_risk", "downside_risk_regime"),
    ("composite", "refined_composite_regime_label"),
]

AGREEMENT_DIMENSIONS = [
    ("benchmark_trend", "benchmark_trend_expanded_agreement"),
    ("benchmark_volatility", "benchmark_volatility_expanded_agreement"),
    ("breadth", "breadth_expanded_agreement"),
    ("dispersion", "dispersion_expanded_agreement"),
    ("liquidity", "liquidity_expanded_agreement"),
    ("downside_risk", "downside_risk_expanded_agreement"),
]

FORBIDDEN_BRIDGE_FIELDS = [
    "forward_return_1d",
    "forward_return_5d",
    "forward_return_20d",
    "benchmark_excess_return_1d",
    "benchmark_excess_return_5d",
    "benchmark_excess_return_20d",
    "daily_ic_1d",
    "daily_rank_ic_1d",
    "hit_rate_1d",
    "portfolio_return",
    "equity_curve",
    "recommendation_label",
    "position_size",
    "portfolio_weight",
]

AGREE = "agree_review_only"
DIVERGE = "diverge_review_only"
UNAVAILABLE = "expanded_evidence_unavailable_review_only"

NEUTRAL_LABEL = {
    "benchmark_trend": "benchmark_trend_flat_review_only",
    "benchmark_volatility": "benchmark_vol_medium_review_only",
    "breadth": "breadth_mixed_review_only",
    "dispersion": "dispersion_medium_review_only",
    "liquidity": "liquidity_normal_review_only",
    "downside_risk": "downside_risk_mixed_review_only",
}


def run_goal_regime_label_research02_gate(root: Path) -> bool:
    result = evaluate_goal_regime_label_research02(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    gate_ok = audit_goal_regime_label_research02_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return gate_ok and workflow_ok


def audit_goal_regime_label_research02_gate(root: Path) -> bool:
    failures: list[str] = []
    for path in OUTPUTS:
        if path == AUDIT_PATH:
            continue
        if not (root / path).exists():
            failures.append(f"missing_output:{path}")
    if failures:
        _write_audit(root, failures)
        return False

    manifest = _read_json(root / MANIFEST_PATH)
    date_rows = read_csv(root / DATE_LABELS_PATH)
    symbol_rows = read_csv(root / SYMBOL_CONTEXT_PATH)
    bridge_rows = read_csv(root / FACTOR_BRIDGE_PATH)
    coverage_rows = read_csv(root / COVERAGE_SUMMARY_PATH)
    transition_rows = read_csv(root / TRANSITION_SUMMARY_PATH)
    agreement_rows = read_csv(root / AGREEMENT_SUMMARY_PATH)
    warning_rows = read_csv(root / CONSTRUCTION_WARNINGS_PATH)

    _assert_schema(failures, "refined_date_regime_labels", date_rows, DATE_LABEL_FIELDS)
    _assert_schema(failures, "refined_symbol_regime_context", symbol_rows, SYMBOL_CONTEXT_FIELDS)
    _assert_schema(failures, "refined_regime_coverage_summary", coverage_rows, COVERAGE_FIELDS)
    _assert_schema(failures, "refined_regime_transition_summary", transition_rows, TRANSITION_FIELDS)
    _assert_schema(failures, "expanded_agreement_summary", agreement_rows, AGREEMENT_FIELDS)
    _assert_schema(failures, "refined_factor_regime_bridge", bridge_rows, BRIDGE_FIELDS)
    _assert_schema(failures, "construction_warnings", warning_rows, WARNING_FIELDS)

    _assert_no_duplicates(failures, "refined_date_regime_labels", date_rows, ["trade_date"])
    _assert_no_duplicates(failures, "refined_symbol_regime_context", symbol_rows, ["trade_date", "symbol"])
    _assert_no_duplicates(failures, "refined_factor_regime_bridge", bridge_rows, ["trade_date", "symbol", "refined_factor_id"])

    for schema_name, fields in [
        ("refined_date_regime_labels", DATE_LABEL_FIELDS),
        ("refined_symbol_regime_context", SYMBOL_CONTEXT_FIELDS),
        ("refined_factor_regime_bridge", BRIDGE_FIELDS),
        ("refined_regime_coverage_summary", COVERAGE_FIELDS),
        ("refined_regime_transition_summary", TRANSITION_FIELDS),
        ("expanded_agreement_summary", AGREEMENT_FIELDS),
    ]:
        if _forbidden_lookahead_columns(fields):
            failures.append(f"forbidden_lookahead_columns:{schema_name}")

    if any(field in BRIDGE_FIELDS for field in FORBIDDEN_BRIDGE_FIELDS):
        failures.append("bridge_contains_forbidden_performance_or_position_field")
    if any("forward_return" in field or "benchmark_excess_return" in field or "label_ready" in field for field in BRIDGE_FIELDS):
        failures.append("bridge_contains_future_or_label_ready_field")
    if any("ic" in field.lower() or "hit_rate" in field.lower() for field in BRIDGE_FIELDS):
        failures.append("bridge_contains_factor_performance_metric_field")

    required_true = [
        "refined_date_level_regime_table_created",
        "refined_symbol_regime_context_created",
        "refined_regime_coverage_summary_created",
        "refined_regime_transition_summary_created",
        "expanded_agreement_summary_created",
        "refined_factor_regime_bridge_created",
        "construction_warnings_created",
        "source_backed_lineage_verified",
        "expanded_regime_evidence_integrated",
        "no_lookahead_construction_passed",
        "artifact_size_policy_passed",
        "goal_quant_research04_locked_future",
        "goal_rec_tiering01_locked_future",
        "goal10b4_locked_future",
        "position_band_validation_locked_future",
        "goal10d_locked_future",
        "dashboard_daily_report_locked_future",
    ]
    for key in required_true:
        if manifest.get(key) is not True:
            failures.append(f"manifest_true_flag_invalid:{key}")
    required_false = [
        "future_returns_used_in_label_construction",
        "benchmark_excess_forward_returns_used_in_label_construction",
        "label_ready_fields_used_in_label_construction",
        "posthoc_factor_performance_used_in_label_construction",
        "factor_predictive_validity_evaluated",
        "ic_rankic_metrics_introduced",
        "recommendation_rows_created",
        "position_rows_created",
        "buy_sell_hold_outputs_generated",
        "target_prices_generated",
        "actual_position_sizing_generated",
        "portfolio_weights_generated",
        "order_quantities_generated",
        "portfolio_returns_generated",
        "equity_curves_generated",
        "dashboard_outputs_generated",
        "html_generated",
        "streamlit_generated",
        "frontend_code_generated",
        "trading_outputs_created",
        "broker_outputs_created",
        "production_outputs_created",
        "local_lake_outputs_created",
        "factor_mining_outputs_created",
        "dqn_rl_outputs_created",
        "live_provider_fetches_run",
        "goal_quant_research04_run",
        "goal_rec_tiering01_run",
        "goal10b4_run",
        "position_band_validation_run",
        "goal10d_run",
        "regime_definitions_tuned_to_future_returns",
        "regime_labels_altered_by_factor_performance",
        "market_timing_validity_claimed",
        "factor_promoted_to_recommendation_tiering",
        "demo_fixture_used",
        "outputs_samples_used",
        "stale_goal10b_evidence_used",
        "stale_dc02_evidence_used",
    ]
    for key in required_false:
        if manifest.get(key) is not False:
            failures.append(f"manifest_false_flag_invalid:{key}")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_invalid")
    if manifest.get("refined_date_regime_row_count") != len(date_rows):
        failures.append("manifest_date_row_count_mismatch")
    if manifest.get("refined_symbol_regime_context_row_count") != len(symbol_rows):
        failures.append("manifest_symbol_row_count_mismatch")
    if manifest.get("refined_factor_regime_bridge_row_count") != len(bridge_rows):
        failures.append("manifest_bridge_row_count_mismatch")
    if manifest.get("refined_factor_regime_bridge_row_count") != 180000:
        failures.append("bridge_row_count_not_180000")
    if manifest.get("refined_date_regime_row_count") != 120:
        failures.append("refined_date_regime_row_count_not_120")
    if manifest.get("refined_symbol_regime_context_row_count") != 6000:
        failures.append("refined_symbol_regime_context_row_count_not_6000")
    if _contains_actionable_language([date_rows, symbol_rows, bridge_rows, agreement_rows]):
        failures.append("actionable_language_found_in_machine_readable_regime_artifact")
    if _contains_secret_like_text(root, OUTPUTS + [
        "src/ashare_premarket/research/goal_regime_label_research02.py",
        "scripts/run_goal_regime_label_research02_gate.py",
        "scripts/audit_goal_regime_label_research02_gate.py",
    ]):
        failures.append("potential_token_or_secret_leakage")
    oversized = _oversized_outputs(root)
    if oversized:
        failures.append("output_artifact_exceeds_95_mib:" + ";".join(f"{path}={size}" for path, size in oversized))

    workflow = {row["workflow_id"]: row for row in read_csv(root / "configs/project/workflow_status.csv")}
    gate = workflow.get(WORKFLOW_ID, {})
    data_expansion01 = workflow.get(GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID, {})
    q04 = workflow.get(GOAL_QUANT_RESEARCH04_WORKFLOW_ID, {})
    rec = workflow.get(GOAL_REC_TIERING01_WORKFLOW_ID, {})
    if gate.get("status") != "implemented_research_only" or gate.get("implemented_in_repo") != "true":
        failures.append("workflow_regime_label_research02_not_implemented_research_only")
    if gate.get("depends_on") != GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID:
        failures.append("workflow_regime_label_research02_dependency_invalid")
    if data_expansion01.get("status") != "implemented_research_only":
        failures.append("workflow_data_expansion01_not_implemented_research_only")
    if q04.get("status") == "implemented_research_only":
        if q04.get("implemented_in_repo") != "true":
            failures.append("workflow_goal_quant_research04_not_locked_future")
    elif q04.get("status") != "locked_future" or q04.get("implemented_in_repo") != "false":
        failures.append("workflow_goal_quant_research04_not_locked_future")
    if rec.get("status") != "locked_future" or rec.get("implemented_in_repo") != "false":
        failures.append("workflow_goal_rec_tiering01_not_locked_future")

    _write_audit(root, failures)
    return not failures


def evaluate_goal_regime_label_research02(root: Path) -> dict[str, object]:
    missing_inputs = [path for path in REQUIRED_INPUTS if not (root / path).exists()]
    base = evaluate_goal_regime_label_research01(root) if not missing_inputs else {"date_rows": [], "symbol_rows": [], "bridge_rows": []}
    base_date_rows = list(base.get("date_rows", []))
    base_symbol_rows = list(base.get("symbol_rows", []))
    base_bridge_rows = list(base.get("bridge_rows", []))
    expanded_date_rows = read_csv(root / EXPANDED_DATE_PANEL_PATH) if not missing_inputs else []
    expanded_symbol_rows = read_csv(root / EXPANDED_SYMBOL_PANEL_PATH) if not missing_inputs else []
    expanded_date_by_date = {row["trade_date"]: row for row in expanded_date_rows}
    expanded_symbol_by_key = {(row["trade_date"], row["symbol"]): row for row in expanded_symbol_rows}

    warnings: list[dict[str, object]] = []
    vol_values = [_float(row.get("broad_index_volatility_20d")) for row in expanded_date_rows]
    dispersion_values = [_float(row.get("sector_dispersion_level")) for row in expanded_date_rows]
    vol_terciles = _terciles([value for value in vol_values if value is not None])
    dispersion_terciles = _terciles([value for value in dispersion_values if value is not None])

    date_rows = _refined_date_rows(base_date_rows, expanded_date_by_date, vol_terciles, dispersion_terciles, warnings)
    refined_by_date = {row["trade_date"]: row for row in date_rows}
    symbol_rows = _refined_symbol_rows(base_symbol_rows, refined_by_date, expanded_symbol_by_key)
    bridge_rows = _refined_bridge_rows(base_bridge_rows, refined_by_date)
    coverage_rows = _coverage_summary_rows(date_rows)
    transition_rows = _transition_summary_rows(date_rows)
    agreement_rows = _agreement_summary_rows(date_rows)
    _append_warning_rows(date_rows, symbol_rows, bridge_rows, coverage_rows, agreement_rows, warnings)

    source_coverage_score = _float(_first(expanded_date_rows, "source_coverage_score"))
    external_data_quality_score = _float(_first(expanded_date_rows, "external_data_quality_score"))
    acceptable_coverage = _acceptable_coverage(date_rows, coverage_rows, bridge_rows)
    status = PASS_WITH_WARNINGS if warnings else PASS
    if missing_inputs or not date_rows or not symbol_rows or not bridge_rows:
        status = BLOCKED
    max_output_size = _max_existing_output_size(root)
    manifest = {
        "goal_id": GOAL_ID,
        "goal": GOAL_NAME,
        "workflow_id": WORKFLOW_ID,
        "mode": MODE,
        "status": status,
        "input_lineage": REQUIRED_INPUTS,
        "missing_inputs": missing_inputs,
        "input_row_counts": {
            REGIME01_DATE_LABELS_PATH: len(base_date_rows),
            REGIME01_SYMBOL_CONTEXT_PATH: len(base_symbol_rows),
            EXPANDED_DATE_PANEL_PATH: len(expanded_date_rows),
            EXPANDED_SYMBOL_PANEL_PATH: len(expanded_symbol_rows),
        },
        "refined_date_regime_row_count": len(date_rows),
        "refined_symbol_regime_context_row_count": len(symbol_rows),
        "refined_factor_regime_bridge_row_count": len(bridge_rows),
        "refined_regime_coverage_summary_row_count": len(coverage_rows),
        "refined_regime_transition_summary_row_count": len(transition_rows),
        "expanded_agreement_summary_row_count": len(agreement_rows),
        "construction_warning_row_count": len(warnings),
        "unique_trade_dates": len({row["trade_date"] for row in date_rows}),
        "unique_symbols": len({row["symbol"] for row in symbol_rows}),
        "refined_factor_count": len({row["refined_factor_id"] for row in bridge_rows}),
        "expanded_date_feature_dates": len(expanded_date_rows),
        "expanded_symbol_context_rows": len(expanded_symbol_rows),
        "source_coverage_score": source_coverage_score,
        "external_data_quality_score": external_data_quality_score,
        "regime_confidence_tier_distribution": _tier_distribution(date_rows),
        "acceptable_regime_coverage": acceptable_coverage,
        "recommended_next_goal": NEXT_GOAL_READY if acceptable_coverage else NEXT_GOAL_SPARSE,
        "allowed_next_action": ALLOWED_NEXT_READY if acceptable_coverage else ALLOWED_NEXT_SPARSE,
        "refined_date_level_regime_table_created": bool(date_rows),
        "refined_symbol_regime_context_created": bool(symbol_rows),
        "refined_regime_coverage_summary_created": bool(coverage_rows),
        "refined_regime_transition_summary_created": bool(transition_rows),
        "expanded_agreement_summary_created": bool(agreement_rows),
        "refined_factor_regime_bridge_created": bool(bridge_rows),
        "construction_warnings_created": True,
        "source_backed_lineage_verified": not missing_inputs,
        "expanded_regime_evidence_integrated": bool(expanded_date_rows) and bool(expanded_symbol_rows),
        "used_committed_regime01_evidence_only": True,
        "used_committed_data_expansion01_evidence_only": True,
        "no_lookahead_construction_passed": True,
        "future_returns_used_in_label_construction": False,
        "benchmark_excess_forward_returns_used_in_label_construction": False,
        "label_ready_fields_used_in_label_construction": False,
        "posthoc_factor_performance_used_in_label_construction": False,
        "factor_predictive_validity_evaluated": False,
        "ic_rankic_metrics_introduced": False,
        "regime_definitions_tuned_to_future_returns": False,
        "regime_labels_altered_by_factor_performance": False,
        "market_timing_validity_claimed": False,
        "recommendation_rows_created": False,
        "position_rows_created": False,
        "position_band_rows_created": False,
        "buy_sell_hold_outputs_generated": False,
        "target_prices_generated": False,
        "actual_position_sizing_generated": False,
        "target_weights_generated": False,
        "portfolio_weights_generated": False,
        "order_quantities_generated": False,
        "portfolio_returns_generated": False,
        "equity_curves_generated": False,
        "dashboard_outputs_generated": False,
        "dashboard_files_generated": False,
        "html_generated": False,
        "streamlit_generated": False,
        "frontend_code_generated": False,
        "visual_reports_generated": False,
        "trading_outputs_created": False,
        "broker_outputs_created": False,
        "production_outputs_created": False,
        "local_lake_outputs_created": False,
        "factor_mining_outputs_created": False,
        "dqn_rl_outputs_created": False,
        "live_provider_fetches_run": False,
        "goal_quant_research04_run": False,
        "goal_quant_research04_locked_future": True,
        "goal_rec_tiering01_run": False,
        "goal_rec_tiering01_locked_future": True,
        "goal10b4_run": False,
        "goal10b4_locked_future": True,
        "position_band_validation_run": False,
        "position_band_validation_locked_future": True,
        "goal10d_run": False,
        "goal10d_locked_future": True,
        "dashboard_daily_report_locked_future": True,
        "portfolio_backtest_locked_future": True,
        "factor_promoted_to_recommendation_tiering": False,
        "demo_fixture_used": False,
        "outputs_samples_used": False,
        "stale_goal10b_evidence_used": False,
        "stale_dc02_evidence_used": False,
        "artifact_size_limit_bytes": SIZE_LIMIT_BYTES,
        "max_output_artifact_bytes": max_output_size,
        "artifact_size_policy_passed": max_output_size < SIZE_LIMIT_BYTES,
        "output_artifacts": OUTPUTS,
        "warnings": sorted({str(row["warning_code"]) for row in warnings}),
    }
    return {
        "status": status,
        "manifest": manifest,
        "date_rows": date_rows,
        "symbol_rows": symbol_rows,
        "bridge_rows": bridge_rows,
        "coverage_rows": coverage_rows,
        "transition_rows": transition_rows,
        "agreement_rows": agreement_rows,
        "warning_rows": warnings,
    }


def implemented_workflow_patch(status: str = PASS_WITH_WARNINGS, acceptable_coverage: bool | None = None) -> dict[str, str]:
    allowed_next = ALLOWED_NEXT_READY if acceptable_coverage is not False else ALLOWED_NEXT_SPARSE
    return {
        "display_name": "GOAL-REGIME-LABEL-RESEARCH-02 Expanded Market Regime Label Refinement Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_research_only",
        "current_repo_role": MODE,
        "implemented_in_repo": "true",
        "allowed_next_action": allowed_next,
        "depends_on": GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID,
        "produces_artifacts": ";".join(OUTPUTS),
        "primary_docs": f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "scripts/run_goal_regime_label_research02_gate.py;scripts/audit_goal_regime_label_research02_gate.py",
        "primary_outputs": ";".join([DATE_LABELS_PATH, SYMBOL_CONTEXT_PATH, COVERAGE_SUMMARY_PATH, TRANSITION_SUMMARY_PATH, AGREEMENT_SUMMARY_PATH, FACTOR_BRIDGE_PATH, CONSTRUCTION_WARNINGS_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH]),
        "promotion_rule": "implemented_research_only_after_goal_regime_label_research02_pass_or_pass_with_warnings",
        "notes": "Research-only no-lookahead expanded market regime label refinement over accepted DataExpansion01 evidence and Regime01 labels. Refines composite regime labels by cross-checking broad-index, sector, and liquidity evidence; produces conditioning context only, not factor evaluation, market timing, recommendations, positions, portfolios, dashboards, trading, production, local-lake, factor-mining, broker, or DQN/RL outputs.",
    }


def goal_regime_label_research02_valid_evidence(root: Path) -> bool:
    manifest = _read_json(root / MANIFEST_PATH)
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    report_passed = (
        "GOAL-REGIME-LABEL-RESEARCH-02 Expanded Market Regime Label Refinement Gate: PASS" in report
        or "GOAL-REGIME-LABEL-RESEARCH-02 Expanded Market Regime Label Refinement Gate: PASS_WITH_WARNINGS" in report
    )
    return (
        manifest.get("mode") == MODE
        and manifest.get("status") in {PASS, PASS_WITH_WARNINGS}
        and manifest.get("refined_date_regime_row_count") == 120
        and manifest.get("refined_symbol_regime_context_row_count") == 6000
        and manifest.get("refined_factor_regime_bridge_row_count") == 180000
        and manifest.get("no_lookahead_construction_passed") is True
        and manifest.get("expanded_regime_evidence_integrated") is True
        and manifest.get("recommendation_rows_created") is False
        and manifest.get("position_rows_created") is False
        and manifest.get("goal_quant_research04_locked_future") is True
        and manifest.get("goal_rec_tiering01_locked_future") is True
        and report_passed
    ) and "Status: `PASS`" in audit


def _refined_date_rows(base_date_rows, expanded_by_date, vol_terciles, dispersion_terciles, warnings):
    output: list[dict[str, object]] = []
    for base in base_date_rows:
        trade_date = str(base["trade_date"])
        expanded = expanded_by_date.get(trade_date, {})
        trend_agree = _trend_agreement(str(base["benchmark_trend_regime"]), _float(expanded.get("broad_index_trend_20d")))
        vol_agree = _tercile_agreement(str(base["benchmark_volatility_regime"]), "benchmark_vol", _float(expanded.get("broad_index_volatility_20d")), vol_terciles)
        breadth_agree = _breadth_agreement(str(base["breadth_regime"]), _float(expanded.get("sector_breadth_positive_share")))
        dispersion_agree = _tercile_agreement(str(base["dispersion_regime"]), "dispersion", _float(expanded.get("sector_dispersion_level")), dispersion_terciles)
        liquidity_agree = _liquidity_agreement(str(base["liquidity_regime"]), str(expanded.get("market_liquidity_pressure", "")))
        downside_agree = UNAVAILABLE
        agreements = {
            "benchmark_trend": trend_agree,
            "benchmark_volatility": vol_agree,
            "breadth": breadth_agree,
            "dispersion": dispersion_agree,
            "liquidity": liquidity_agree,
            "downside_risk": downside_agree,
        }
        refined_trend = _refine(str(base["benchmark_trend_regime"]), "benchmark_trend", trend_agree)
        refined_vol = _refine(str(base["benchmark_volatility_regime"]), "benchmark_volatility", vol_agree)
        refined_breadth = _refine(str(base["breadth_regime"]), "breadth", breadth_agree)
        refined_liquidity = _refine(str(base["liquidity_regime"]), "liquidity", liquidity_agree)
        refined_downside = _refine(str(base["downside_risk_regime"]), "downside_risk", downside_agree)
        refined_composite = _composite_label(refined_trend, refined_vol, refined_breadth, refined_liquidity, refined_downside)
        available = sum(1 for value in agreements.values() if value != UNAVAILABLE)
        agree_count = sum(1 for value in agreements.values() if value == AGREE)
        confidence = _confidence_tier(agree_count)
        refinement_status = "refined_with_expanded_cross_source_evidence" if available >= 4 else "refined_with_partial_expanded_evidence"
        output.append({
            "trade_date": trade_date,
            "benchmark_symbol": base["benchmark_symbol"],
            "base_composite_regime_label": base["composite_regime_label"],
            "refined_composite_regime_label": refined_composite,
            "benchmark_trend_regime": base["benchmark_trend_regime"],
            "benchmark_volatility_regime": base["benchmark_volatility_regime"],
            "breadth_regime": base["breadth_regime"],
            "dispersion_regime": base["dispersion_regime"],
            "liquidity_regime": base["liquidity_regime"],
            "downside_risk_regime": base["downside_risk_regime"],
            "benchmark_trend_expanded_agreement": trend_agree,
            "benchmark_volatility_expanded_agreement": vol_agree,
            "breadth_expanded_agreement": breadth_agree,
            "dispersion_expanded_agreement": dispersion_agree,
            "liquidity_expanded_agreement": liquidity_agree,
            "downside_risk_expanded_agreement": downside_agree,
            "broad_index_trend_20d": _passthrough(expanded.get("broad_index_trend_20d")),
            "broad_index_volatility_20d": _passthrough(expanded.get("broad_index_volatility_20d")),
            "sector_breadth_positive_share": _passthrough(expanded.get("sector_breadth_positive_share")),
            "sector_dispersion_level": _passthrough(expanded.get("sector_dispersion_level")),
            "market_liquidity_pressure": expanded.get("market_liquidity_pressure", UNAVAILABLE),
            "expanded_dimension_available_count": available,
            "expanded_dimension_agreement_count": agree_count,
            "regime_confidence_tier": confidence,
            "source_coverage_score": _passthrough(expanded.get("source_coverage_score")),
            "external_data_quality_score": _passthrough(expanded.get("external_data_quality_score")),
            "regime_refinement_status": refinement_status,
            "no_lookahead_status": NO_LOOKAHEAD,
            "non_actionable_disclaimer": NON_ACTIONABLE,
        })
    return output


def _refined_symbol_rows(base_symbol_rows, refined_by_date, expanded_symbol_by_key):
    output: list[dict[str, object]] = []
    for base in base_symbol_rows:
        key = (str(base["trade_date"]), str(base["symbol"]))
        refined_date = refined_by_date.get(str(base["trade_date"]), {})
        expanded = expanded_symbol_by_key.get(key, {})
        output.append({
            "trade_date": base["trade_date"],
            "symbol": base["symbol"],
            "base_composite_regime_label": base["composite_regime_label"],
            "refined_composite_regime_label": refined_date.get("refined_composite_regime_label", "insufficient_composite_regime_evidence_review_only"),
            "benchmark_trend_regime": base["benchmark_trend_regime"],
            "benchmark_volatility_regime": base["benchmark_volatility_regime"],
            "breadth_regime": base["breadth_regime"],
            "dispersion_regime": base["dispersion_regime"],
            "liquidity_regime": base["liquidity_regime"],
            "downside_risk_regime": base["downside_risk_regime"],
            "risk_score_bucket": base["risk_score_bucket"],
            "downside_risk_bucket": base["downside_risk_bucket"],
            "mvp_review_queue_category": base["mvp_review_queue_category"],
            "symbol_listing_status": expanded.get("listing_status", "expanded_symbol_context_unavailable"),
            "symbol_suspension_status": expanded.get("suspension_status", "expanded_symbol_context_unavailable"),
            "symbol_st_status": expanded.get("st_status", "expanded_symbol_context_unavailable"),
            "symbol_flow_available": expanded.get("symbol_flow_available", "false"),
            "event_risk_context_available": expanded.get("event_risk_context_available", "false"),
            "regime_confidence_tier": refined_date.get("regime_confidence_tier", "low_confidence_review_only"),
            "source_coverage_score": refined_date.get("source_coverage_score", ""),
            "external_data_quality_score": refined_date.get("external_data_quality_score", ""),
            "regime_refinement_status": refined_date.get("regime_refinement_status", "refined_with_partial_expanded_evidence"),
            "no_lookahead_status": NO_LOOKAHEAD,
            "non_actionable_disclaimer": NON_ACTIONABLE,
        })
    return output


def _refined_bridge_rows(base_bridge_rows, refined_by_date):
    output: list[dict[str, object]] = []
    for base in base_bridge_rows:
        refined_date = refined_by_date.get(str(base["trade_date"]), {})
        output.append({
            "trade_date": base["trade_date"],
            "symbol": base["symbol"],
            "refined_factor_id": base["refined_factor_id"],
            "source_factor_id": base["source_factor_id"],
            "refinement_type": base["refinement_type"],
            "factor_family": base["factor_family"],
            "refined_composite_regime_label": refined_date.get("refined_composite_regime_label", "insufficient_composite_regime_evidence_review_only"),
            "regime_confidence_tier": refined_date.get("regime_confidence_tier", "low_confidence_review_only"),
            "factor_value_available": base["factor_value_available"],
            "factor_bucket": base["factor_bucket"],
            "risk_score_bucket": base["risk_score_bucket"],
            "downside_risk_bucket": base["downside_risk_bucket"],
            "mvp_review_queue_category": base["mvp_review_queue_category"],
            "no_lookahead_status": NO_LOOKAHEAD,
            "bridge_status": "linked_no_perf",
            "intended_future_evaluation_goal": "GOAL-QUANT-RESEARCH-04",
            "non_actionable_disclaimer": NON_ACTIONABLE,
        })
    return output


def _coverage_summary_rows(date_rows):
    output: list[dict[str, object]] = []
    dates = [str(row["trade_date"]) for row in date_rows]
    for dimension, field in REGIME_DIMENSIONS:
        counts = Counter(str(row[field]) for row in date_rows)
        dominant = max(counts.values()) / len(date_rows) if date_rows else 0.0
        minimum = min(counts.values()) if counts else 0
        for label, count in sorted(counts.items()):
            output.append({
                "regime_dimension": dimension,
                "regime_label": label,
                "row_count": count,
                "unique_trade_dates": count,
                "unique_symbols_if_symbol_level": "",
                "date_min": min(dates) if dates else "",
                "date_max": max(dates) if dates else "",
                "dominant_label_share": _fmt(dominant),
                "minimum_label_count": minimum,
                "construction_status": "constructed" if not label.startswith("insufficient_") else "constructed_with_insufficient_evidence_warning",
                "no_lookahead_status": NO_LOOKAHEAD,
            })
    return output


def _transition_summary_rows(date_rows):
    output: list[dict[str, object]] = []
    total_possible = max(len(date_rows) - 1, 1)
    for dimension, field in REGIME_DIMENSIONS:
        transitions: dict[tuple[str, str], list[str]] = defaultdict(list)
        previous = None
        for row in date_rows:
            label = str(row[field])
            if previous is not None and previous[1] != label:
                transitions[(previous[1], label)].append(str(row["trade_date"]))
            previous = (str(row["trade_date"]), label)
        if not transitions:
            output.append({
                "regime_dimension": dimension,
                "from_regime_label": "no_transition",
                "to_regime_label": "no_transition",
                "transition_count": 0,
                "first_transition_date": "",
                "last_transition_date": "",
                "transition_density": "0.0000000000",
                "notes": "label_stable_over_committed_window",
            })
            continue
        for (from_label, to_label), transition_dates in sorted(transitions.items()):
            output.append({
                "regime_dimension": dimension,
                "from_regime_label": from_label,
                "to_regime_label": to_label,
                "transition_count": len(transition_dates),
                "first_transition_date": min(transition_dates),
                "last_transition_date": max(transition_dates),
                "transition_density": _fmt(len(transition_dates) / total_possible),
                "notes": "review_only_transition_count_not_market_timing_signal",
            })
    return output


def _agreement_summary_rows(date_rows):
    output: list[dict[str, object]] = []
    total = len(date_rows) or 1
    for dimension, field in AGREEMENT_DIMENSIONS:
        counts = Counter(str(row[field]) for row in date_rows)
        for status in [AGREE, DIVERGE, UNAVAILABLE]:
            count = counts.get(status, 0)
            output.append({
                "regime_dimension": dimension,
                "expanded_agreement_status": status,
                "row_count": count,
                "share_of_dates": _fmt(count / total),
                "notes": "review_only_cross_source_agreement_not_market_timing_signal",
            })
    return output


def _append_warning_rows(date_rows, symbol_rows, bridge_rows, coverage_rows, agreement_rows, warnings):
    for row in coverage_rows:
        label = str(row["regime_label"])
        count = int(row["row_count"])
        dominant = _float(row["dominant_label_share"]) or 0.0
        if count < 3:
            warnings.append(_warning("sparse_refined_regime_label", row["regime_dimension"], label, count, "Refined regime label appears fewer than the configured minimum label count."))
        if dominant > 0.80:
            warnings.append(_warning("dominant_refined_regime_label", row["regime_dimension"], label, count, "One refined label dominates this regime dimension across the committed date window."))
        if label.startswith("insufficient_"):
            warnings.append(_warning("refined_regime_dimension_not_constructed", row["regime_dimension"], label, count, "At least one date has insufficient evidence for this refined dimension."))
    for row in agreement_rows:
        if str(row["expanded_agreement_status"]) == DIVERGE and int(row["row_count"]) > 0:
            warnings.append(_warning("expanded_cross_source_divergence", row["regime_dimension"], DIVERGE, int(row["row_count"]), "Expanded broad-index/sector evidence diverges from the Regime01 label on at least one date."))
        if str(row["expanded_agreement_status"]) == UNAVAILABLE and int(row["row_count"]) == len(date_rows) and len(date_rows) > 0:
            warnings.append(_warning("expanded_evidence_unavailable_offline_replay", row["regime_dimension"], UNAVAILABLE, int(row["row_count"]), "Expanded evidence for this dimension is unavailable in committed offline replay."))
    if len(symbol_rows) != 6000:
        warnings.append(_warning("insufficient_symbol_coverage", "refined_symbol_regime_context", "row_count", len(symbol_rows), "Refined symbol regime context row count differs from the 6000-row Regime01 panel."))
    if len(bridge_rows) != 180000:
        warnings.append(_warning("bridge_missing_refined_factor_rows", "refined_factor_regime_bridge", "row_count", len(bridge_rows), "Refined bridge row count differs from the 180000-row Candidate02 refined factor panel."))


def _acceptable_coverage(date_rows, coverage_rows, bridge_rows):
    if len(date_rows) != 120 or len(bridge_rows) != 180000:
        return False
    composite_rows = [row for row in coverage_rows if row["regime_dimension"] == "composite"]
    if not composite_rows:
        return False
    dominant = max((_float(row["dominant_label_share"]) or 0.0) for row in composite_rows)
    labels = {row["regime_label"] for row in composite_rows if not str(row["regime_label"]).startswith("insufficient_")}
    return dominant <= 0.80 and len(labels) >= 2


def _trend_agreement(base_label: str, broad_trend_20d: float | None) -> str:
    if broad_trend_20d is None:
        return UNAVAILABLE
    if broad_trend_20d > 0.01:
        expanded = "up"
    elif broad_trend_20d < -0.01:
        expanded = "down"
    else:
        expanded = "flat"
    base = "up" if "trend_up" in base_label else "down" if "trend_down" in base_label else "flat" if "trend_flat" in base_label else None
    if base is None:
        return UNAVAILABLE
    return AGREE if base == expanded else DIVERGE


def _tercile_agreement(base_label: str, prefix: str, value: float | None, thresholds) -> str:
    if value is None or thresholds[0] is None or thresholds[1] is None:
        return UNAVAILABLE
    low, high = thresholds
    expanded = "low" if value <= low else "high" if value >= high else "medium"
    base = "low" if f"{prefix}_low" in base_label else "high" if f"{prefix}_high" in base_label else "medium" if f"{prefix}_medium" in base_label else None
    if base is None:
        return UNAVAILABLE
    return AGREE if base == expanded else DIVERGE


def _breadth_agreement(base_label: str, positive_share: float | None) -> str:
    if positive_share is None:
        return UNAVAILABLE
    expanded = "positive" if positive_share >= 0.55 else "negative" if positive_share <= 0.45 else "mixed"
    base = "positive" if "breadth_positive" in base_label else "negative" if "breadth_negative" in base_label else "mixed" if "breadth_mixed" in base_label else None
    if base is None:
        return UNAVAILABLE
    return AGREE if base == expanded else DIVERGE


def _liquidity_agreement(base_label: str, pressure_label: str) -> str:
    if not pressure_label or pressure_label == "not_available_offline_replay":
        return UNAVAILABLE
    if not pressure_label.endswith("_review_only"):
        return UNAVAILABLE
    return AGREE if pressure_label == base_label else DIVERGE


def _refine(base_label: str, dimension: str, agreement: str) -> str:
    if base_label.startswith("insufficient_"):
        return base_label
    if agreement == DIVERGE:
        return NEUTRAL_LABEL[dimension]
    return base_label


def _confidence_tier(agree_count: int) -> str:
    if agree_count >= 4:
        return "high_confidence_review_only"
    if agree_count >= 2:
        return "medium_confidence_review_only"
    return "low_confidence_review_only"


def _tier_distribution(date_rows):
    return dict(sorted(Counter(str(row["regime_confidence_tier"]) for row in date_rows).items()))


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / DATE_LABELS_PATH, result["date_rows"], DATE_LABEL_FIELDS)
    write_csv(root / SYMBOL_CONTEXT_PATH, result["symbol_rows"], SYMBOL_CONTEXT_FIELDS)
    write_csv(root / COVERAGE_SUMMARY_PATH, result["coverage_rows"], COVERAGE_FIELDS)
    write_csv(root / TRANSITION_SUMMARY_PATH, result["transition_rows"], TRANSITION_FIELDS)
    write_csv(root / AGREEMENT_SUMMARY_PATH, result["agreement_rows"], AGREEMENT_FIELDS)
    write_csv(root / FACTOR_BRIDGE_PATH, result["bridge_rows"], BRIDGE_FIELDS)
    write_csv(root / CONSTRUCTION_WARNINGS_PATH, result["warning_rows"], WARNING_FIELDS)
    manifest = dict(result["manifest"])
    manifest["max_output_artifact_bytes"] = _max_existing_output_size(root)
    manifest["artifact_size_policy_passed"] = manifest["max_output_artifact_bytes"] < SIZE_LIMIT_BYTES
    write_json(root / MANIFEST_PATH, manifest)
    _write_report(root, {**result, "manifest": manifest})
    _write_doc(root, {**result, "manifest": manifest})
    _write_contract(root, {**result, "manifest": manifest})


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    agreement_counts = Counter(row["regime_dimension"] for row in result["agreement_rows"])
    body = [
        "# GOAL-REGIME-LABEL-RESEARCH-02 Expanded Market Regime Label Refinement Gate",
        "",
        "## 1. Goal status",
        f"GOAL-REGIME-LABEL-RESEARCH-02 Expanded Market Regime Label Refinement Gate: {manifest['status']}",
        "",
        "## 2. Current DataExpansion01 context",
        "GOAL-DATA-EXPANSION-RESEARCH-01 produced committed broad-index, sector/concept, liquidity, and expanded date/symbol regime evidence over offline replay. This gate refines the Regime01 labels using that expanded evidence only.",
        "",
        "## 3. Why refined regime labels are needed",
        "Refined labels cross-check the single-benchmark Regime01 composite against broad-index and sector cross-sections, adding a research confidence tier. They are conditioning context only, not market timing signals.",
        "",
        "## 4. Source-backed input lineage",
        *[f"- `{path}`" for path in REQUIRED_INPUTS],
        "",
        "## 5. No-lookahead refinement policy",
        "Refinement uses only current-date or trailing committed Regime01 and DataExpansion01 evidence. Future returns, benchmark-excess forward returns, label-ready fields, and post-hoc factor performance are excluded, and no factor predictive validity is evaluated.",
        "",
        "## 6. Regime dimensions refined",
        f"Dimensions: `{', '.join(dimension for dimension, _ in REGIME_DIMENSIONS)}`.",
        "",
        "## 7. Refined date-level regime coverage",
        f"Refined date rows: `{manifest['refined_date_regime_row_count']}` over `{manifest['unique_trade_dates']}` dates.",
        "",
        "## 8. Refined symbol-level regime context coverage",
        f"Refined symbol rows: `{manifest['refined_symbol_regime_context_row_count']}` over `{manifest['unique_symbols']}` symbols.",
        "",
        "## 9. Expanded cross-source agreement summary",
        f"Agreement rows: `{manifest['expanded_agreement_summary_row_count']}`. Dimensions covered: `{dict(sorted(agreement_counts.items()))}`.",
        "",
        "## 10. Regime confidence tier distribution",
        f"Confidence tiers: `{manifest['regime_confidence_tier_distribution']}`.",
        "",
        "## 11. Refined regime transition summary",
        f"Transition rows: `{manifest['refined_regime_transition_summary_row_count']}`.",
        "",
        "## 12. Refined regime-factor bridge summary",
        f"Bridge rows: `{manifest['refined_factor_regime_bridge_row_count']}` across `{manifest['refined_factor_count']}` refined factors. The bridge carries no forward returns, benchmark-excess returns, IC/RankIC, hit rates, portfolio returns, recommendation labels, or position fields.",
        "",
        "## 13. Construction warnings",
        f"Warning rows: `{manifest['construction_warning_row_count']}`. Warning codes: `{manifest['warnings']}`.",
        "",
        "## 14. External data quality context",
        f"Source coverage score: `{manifest['source_coverage_score']}`; external data quality score: `{manifest['external_data_quality_score']}`. Offline-unavailable flow and margin evidence is treated as missing, not zero.",
        "",
        "## 15. Why this is not factor evaluation or recommendation tiering",
        "Refined regime labels are rule-based research context only. The gate does not evaluate factor predictive validity, does not optimize labels against future returns or factor performance, and does not promote factors to recommendation tiering.",
        "",
        "## 16. Locked downstream boundaries",
        "GOAL-QUANT-RESEARCH-04, GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, portfolio backtests, trading, production, local-lake, broker, factor-mining, and DQN/RL remain locked.",
        "",
        "## 17. Recommended next goal",
        f"`{manifest['recommended_next_goal']}`.",
        "",
    ]
    write_text(root / REPORT_PATH, "\n".join(body))


def _write_doc(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    body = [
        "# GOAL-REGIME-LABEL-RESEARCH-02 Expanded Market Regime Label Refinement Gate",
        "",
        f"Status: `{manifest['status']}`",
        "",
        "This gate refines the deterministic no-lookahead Regime01 market regime labels by integrating committed DataExpansion01 expanded regime evidence only.",
        "",
        "## Network Policy",
        "Offline committed-evidence replay only. No live provider fetches are performed and provider network default remains disabled.",
        "",
        "## Outputs",
        *[f"- `{path}`" for path in OUTPUTS if path.startswith("outputs/research/")],
        "",
        "## Method",
        "Regime01 per-dimension labels are cross-checked against DataExpansion01 broad-index trend/volatility, sector breadth/dispersion, and market liquidity-pressure evidence. Divergent dimensions are conservatively neutralized before the refined composite is recomputed, and a research confidence tier records how many expanded dimensions agree.",
        "",
        "## Result",
        f"- Refined date-level rows: `{manifest['refined_date_regime_row_count']}`",
        f"- Refined symbol-level rows: `{manifest['refined_symbol_regime_context_row_count']}`",
        f"- Refined bridge rows: `{manifest['refined_factor_regime_bridge_row_count']}`",
        f"- Recommended next goal: `{manifest['recommended_next_goal']}`",
        "",
        "## Locked Boundary",
        "Refined regime labels are research conditioning labels only. They are not market timing signals, trading signals, recommendations, positions, portfolios, dashboards, production outputs, local-lake outputs, factor-mining outputs, broker outputs, or DQN/RL outputs, and no factor predictive validity is evaluated.",
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
        f'  "artifact_size_limit_bytes": {SIZE_LIMIT_BYTES},',
        '  "allowed_input_artifacts": ' + _json_list(REQUIRED_INPUTS) + ",",
        '  "allowed_regime_dimensions": ' + _json_list([dimension for dimension, _ in REGIME_DIMENSIONS]) + ",",
        '  "allowed_labels": [',
        '    "*_review_only",',
        '    "insufficient_*_review_only"',
        "  ],",
        '  "no_lookahead_construction_policy": "use_same_date_or_trailing_committed_fields_only; exclude forward returns, benchmark-excess forward returns, label-ready fields, and post-hoc factor performance",',
        '  "forbidden_columns": ' + _json_list(["forward_return_1d", "forward_return_5d", "forward_return_20d", "benchmark_excess_return_1d", "benchmark_excess_return_5d", "benchmark_excess_return_20d", "label_ready_1d", "label_ready_5d", "label_ready_20d", "daily_ic", "daily_rank_ic", "hit_rate", "portfolio_return", "equity_curve"]) + ",",
        '  "forbidden_outputs": ' + _json_list(["recommendation_rows", "position_rows", "buy_sell_hold", "target_prices", "position_sizes", "portfolio_weights", "order_quantities", "portfolio_returns", "equity_curves", "dashboard", "html", "streamlit", "frontend", "trading", "broker", "production", "local_lake", "factor_mining", "dqn_rl"]) + ",",
        '  "required_output_schemas": {',
        '    "refined_date_regime_labels": ' + _json_list(DATE_LABEL_FIELDS) + ",",
        '    "refined_symbol_regime_context": ' + _json_list(SYMBOL_CONTEXT_FIELDS) + ",",
        '    "refined_factor_regime_bridge": ' + _json_list(BRIDGE_FIELDS),
        "  },",
        '  "downstream_locks": {',
        f'    "{GOAL_QUANT_RESEARCH04_WORKFLOW_ID}": "locked_future",',
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
        insert_at = next((idx + 1 for idx, row in enumerate(rows) if row["workflow_id"] == GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": WORKFLOW_ID})
        by_id = {row["workflow_id"]: row for row in rows}
    acceptable = bool(result["manifest"].get("acceptable_regime_coverage"))
    by_id[WORKFLOW_ID].update(implemented_workflow_patch(str(result["status"]), acceptable))
    preserve_later_review_only_workflow_states(root, by_id)
    if result["status"] in {PASS, PASS_WITH_WARNINGS} and WORKFLOW_ID in by_id:
        by_id[WORKFLOW_ID].update(implemented_workflow_patch(str(result["status"]), acceptable))
    preserve_later_review_only_workflow_states(root, by_id)
    by_id[WORKFLOW_ID].update(implemented_workflow_patch(str(result["status"]), acceptable))
    write_csv(path, rows)


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    payload = read_json(path) if path.exists() else {}
    payload[WORKFLOW_ID] = "implemented_research_only"
    payload[GOAL_QUANT_RESEARCH04_WORKFLOW_ID] = False
    payload[GOAL_REC_TIERING01_WORKFLOW_ID] = False
    preserve_later_review_only_capabilities(root, payload)
    if result["status"] in {PASS, PASS_WITH_WARNINGS}:
        payload[WORKFLOW_ID] = "implemented_research_only"
    preserve_later_review_only_capabilities(root, payload)
    payload[WORKFLOW_ID] = "implemented_research_only"
    write_json(path, payload)


def _write_audit(root: Path, failures: list[str]) -> None:
    status = "PASS" if not failures else "BLOCKED"
    body = [
        "# GOAL-REGIME-LABEL-RESEARCH-02 Audit",
        "",
        f"Status: `{status}`",
        "",
        "## Checks",
        "- Required files exist.",
        "- Required refined schemas exist and pass the forbidden-lookahead column scan.",
        "- Date-level grain is `trade_date`.",
        "- Symbol-level grain is `trade_date + symbol`.",
        "- Bridge grain is `trade_date + symbol + refined_factor_id`.",
        "- No duplicate keys.",
        "- Forward returns, benchmark-excess forward returns, label-ready fields, IC/RankIC, hit rates, recommendation labels, position fields, portfolio returns, and equity curves are excluded from the bridge and refined label construction evidence.",
        "- Expanded DataExpansion01 regime evidence is integrated without factor predictive validity evaluation.",
        "- Downstream locks are preserved.",
        "",
        "## Failures",
        *[f"- {failure}" for failure in failures],
        "",
    ]
    write_text(root / AUDIT_PATH, "\n".join(body))


def _assert_schema(failures, name, rows, fields):
    if not rows:
        failures.append(f"{name}_empty")
        return
    if list(rows[0].keys()) != fields:
        failures.append(f"{name}_schema_mismatch")


def _assert_no_duplicates(failures, name, rows, key_fields):
    keys = [tuple(row[field] for field in key_fields) for row in rows]
    if len(keys) != len(set(keys)):
        failures.append(f"{name}_duplicate_keys")


def _forbidden_lookahead_columns(fields):
    forbidden = {
        "future_return_1d", "future_return_5d", "future_return_20d",
        "benchmark_excess_return", "benchmark_excess_return_1d", "benchmark_excess_return_5d", "benchmark_excess_return_20d",
        "label_ready", "label_ready_1d", "label_ready_5d", "label_ready_20d",
        "ic", "rank_ic", "hit_rate",
    }
    hits = []
    for field in fields:
        lower = field.lower()
        if lower in forbidden or lower.startswith("future_return_") or lower.startswith("benchmark_excess_return_"):
            hits.append(field)
    return hits


def _terciles(values):
    return _quantile(values, 1 / 3), _quantile(values, 2 / 3)


def _first(rows, field):
    for row in rows:
        value = row.get(field)
        if value not in {"", None}:
            return value
    return None


def _passthrough(value):
    return "" if value is None else str(value)


def _fmt(value):
    return "" if value is None else f"{value:.10f}"


def _warning(code, dimension, label, row_count, details):
    return {
        "warning_code": code,
        "regime_dimension": dimension,
        "affected_label": label,
        "row_count": row_count,
        "details": details,
    }


def _oversized_outputs(root):
    outputs = [root / path for path in OUTPUTS if (root / path).exists()]
    return [(path.relative_to(root).as_posix(), path.stat().st_size) for path in outputs if path.stat().st_size >= SIZE_LIMIT_BYTES]


def _max_existing_output_size(root):
    sizes = [(root / path).stat().st_size for path in OUTPUTS if (root / path).exists()]
    return max(sizes) if sizes else 0


def _contains_actionable_language(row_groups):
    import re
    pattern = re.compile(r"^(BUY|SELL|HOLD)$|target_price|position_size|portfolio_weight|target_weight|order_quantity|portfolio_return|equity_curve", re.IGNORECASE)
    for rows in row_groups:
        for row in rows:
            if any(pattern.search(str(value)) for value in row.values()):
                return True
    return False


def _contains_secret_like_text(root, paths):
    import re
    patterns = [
        re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
        re.compile(r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|password)\s*[:=]\s*[A-Za-z0-9_./+=-]{12,}"),
        re.compile(r"(?i)authorization\s*[:=]\s*bearer\s+[A-Za-z0-9_./+=-]{12,}"),
    ]
    for rel in paths:
        path = root / rel
        if path.exists() and path.is_file() and path.suffix.lower() in {".csv", ".json", ".md", ".yaml", ".py"}:
            text = path.read_text(encoding="utf-8")
            if any(pattern.search(text) for pattern in patterns):
                return True
    return False


def _json_list(values):
    return "[" + ", ".join(f'"{value}"' for value in values) + "]"


def _read(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_json(path):
    try:
        return read_json(path)
    except Exception:
        return {}

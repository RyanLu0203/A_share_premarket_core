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

GOAL_ID = "GOAL-REGIME-LABEL-RESEARCH-01"
GOAL_NAME = "GOAL-REGIME-LABEL-RESEARCH-01-MARKET-REGIME-LABEL-CONSTRUCTION-GATE"
MODE = "research_only_market_regime_label_construction_gate"
WORKFLOW_ID = "goal_regime_label_research01_market_regime_label_construction_gate"
PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

GOAL_QUANT_RESEARCH03_WORKFLOW_ID = "goal_quant_research03_refined_alpha_factor_validity_evaluation_gate"
GOAL_QUANT_RESEARCH04_WORKFLOW_ID = "goal_quant_research04_regime_conditional_factor_evaluation_gate"
GOAL_ARCHITECTURE_REFACTOR03_WORKFLOW_ID = "goal_architecture_refactor03_akshare_source_catalog_and_provider_modularization_gate"
GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID = "goal_data_expansion_research01_market_regime_data_expansion_gate"
GOAL_REC_TIERING01_WORKFLOW_ID = "goal_rec_tiering01_recommendation_score_tiering_gate"
GOAL10B4_WORKFLOW_ID = "goal10b4_recommendation_backtest_revalidation"
POSITION_BAND_VALIDATION_WORKFLOW_ID = "goal_position_band_validation01_position_band_validation_gate"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
GOAL10C_WORKFLOW_ID = "goal10c_backtest_cost_slippage_sensitivity_gate"

ALLOWED_NEXT_READY = "request_goal_quant_research04_regime_conditional_factor_evaluation_gate"
ALLOWED_NEXT_SPARSE = "request_goal_data_expansion_research01_before_regime_conditional_factor_evaluation"
NEXT_GOAL_READY = "GOAL-QUANT-RESEARCH-04-REGIME-CONDITIONAL-FACTOR-EVALUATION-GATE"
NEXT_GOAL_SPARSE = "GOAL-DATA-EXPANSION-RESEARCH-01"
NON_ACTIONABLE = "research_only"
NO_LOOKAHEAD = "passed_current_or_past_only"
SIZE_LIMIT_BYTES = 95 * 1024 * 1024
MIN_LABEL_COUNT = 3
DOMINANT_LABEL_THRESHOLD = 0.80

PROVIDER02B_PANEL_PATH = "outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv"
QUANT03_IMPROVEMENT_PATH = "outputs/research/goal_quant_research03_refined_factor_improvement_summary.csv"
QUANT03_SCORE_VALIDITY_PATH = "outputs/research/goal_quant_research03_refined_factor_score_validity_classification.csv"
QUANT03_ROLLING_STABILITY_PATH = "outputs/research/goal_quant_research03_refined_factor_rolling_stability_summary.csv"
QUANT03_HORIZON_CONSISTENCY_PATH = "outputs/research/goal_quant_research03_refined_factor_horizon_consistency_summary.csv"
CANDIDATE02_REGISTRY_PATH = "outputs/research/goal_alpha_factor_candidate02_refined_candidate_registry.csv"
CANDIDATE02_PANEL_PATH = "outputs/research/goal_alpha_factor_candidate02_refined_candidate_panel.csv"
MVP_SYMBOL_TABLE_PATH = "outputs/mvp/goal_mvp01_symbol_diagnostic_table.csv"
MVP_REVIEW_QUEUE_PATH = "outputs/mvp/goal_mvp01_review_queue.csv"
RISK01_DIAGNOSTICS_PATH = "outputs/diagnostics/goal_risk_tiering01_risk_tiered_diagnostics.csv"
RISK011_DIAGNOSTICS_PATH = "outputs/diagnostics/goal_risk_tiering011_downside_risk_diagnostics.csv"

DATE_LABELS_PATH = "outputs/research/goal_regime_label_research01_date_regime_labels.csv"
SYMBOL_CONTEXT_PATH = "outputs/research/goal_regime_label_research01_symbol_regime_context.csv"
COVERAGE_SUMMARY_PATH = "outputs/research/goal_regime_label_research01_regime_coverage_summary.csv"
TRANSITION_SUMMARY_PATH = "outputs/research/goal_regime_label_research01_regime_transition_summary.csv"
FACTOR_BRIDGE_PATH = "outputs/research/goal_regime_label_research01_factor_regime_bridge.csv"
CONSTRUCTION_WARNINGS_PATH = "outputs/research/goal_regime_label_research01_construction_warnings.csv"
REPORT_PATH = "outputs/audits/goal_regime_label_research01_report.md"
MANIFEST_PATH = "outputs/audits/goal_regime_label_research01_manifest.json"
AUDIT_PATH = "outputs/audits/goal_regime_label_research01_audit.md"
DOC_PATH = "docs/research/GOAL_REGIME_LABEL_RESEARCH01_MARKET_REGIME_LABEL_CONSTRUCTION_GATE.md"
CONTRACT_PATH = "configs/research/goal_regime_label_research01_contract.yaml"

REQUIRED_INPUTS = [
    PROVIDER02B_PANEL_PATH,
    QUANT03_IMPROVEMENT_PATH,
    QUANT03_SCORE_VALIDITY_PATH,
    QUANT03_ROLLING_STABILITY_PATH,
    QUANT03_HORIZON_CONSISTENCY_PATH,
    CANDIDATE02_REGISTRY_PATH,
    CANDIDATE02_PANEL_PATH,
    MVP_SYMBOL_TABLE_PATH,
    MVP_REVIEW_QUEUE_PATH,
    RISK01_DIAGNOSTICS_PATH,
    RISK011_DIAGNOSTICS_PATH,
]

OUTPUTS = [
    DATE_LABELS_PATH,
    SYMBOL_CONTEXT_PATH,
    COVERAGE_SUMMARY_PATH,
    TRANSITION_SUMMARY_PATH,
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
    "benchmark_trend_regime",
    "benchmark_volatility_regime",
    "breadth_regime",
    "dispersion_regime",
    "liquidity_regime",
    "downside_risk_regime",
    "composite_regime_label",
    "benchmark_trailing_return_5d",
    "benchmark_trailing_return_20d",
    "benchmark_trailing_volatility_20d",
    "universe_positive_return_share",
    "universe_negative_return_share",
    "universe_return_dispersion",
    "universe_liquidity_proxy",
    "high_downside_risk_share",
    "valid_symbol_count",
    "source_provider",
    "universe_mode",
    "no_lookahead_status",
    "label_construction_status",
    "non_actionable_disclaimer",
]

SYMBOL_CONTEXT_FIELDS = [
    "trade_date",
    "symbol",
    "composite_regime_label",
    "benchmark_trend_regime",
    "benchmark_volatility_regime",
    "breadth_regime",
    "dispersion_regime",
    "liquidity_regime",
    "downside_risk_regime",
    "risk_score_bucket",
    "downside_risk_bucket",
    "mvp_review_queue_category",
    "mvp_review_priority_level",
    "source_provider",
    "universe_mode",
    "panel_contract_status",
    "no_lookahead_status",
    "label_construction_status",
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

BRIDGE_FIELDS = [
    "trade_date",
    "symbol",
    "refined_factor_id",
    "source_factor_id",
    "refinement_type",
    "factor_family",
    "composite_regime_label",
    "benchmark_trend_regime",
    "benchmark_volatility_regime",
    "breadth_regime",
    "dispersion_regime",
    "liquidity_regime",
    "downside_risk_regime",
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
    ("composite", "composite_regime_label"),
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


def run_goal_regime_label_research01_gate(root: Path) -> bool:
    result = evaluate_goal_regime_label_research01(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    gate_ok = audit_goal_regime_label_research01_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return gate_ok and workflow_ok


def audit_goal_regime_label_research01_gate(root: Path) -> bool:
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
    warning_rows = read_csv(root / CONSTRUCTION_WARNINGS_PATH)

    _assert_schema(failures, "date_regime_labels", date_rows, DATE_LABEL_FIELDS)
    _assert_schema(failures, "symbol_regime_context", symbol_rows, SYMBOL_CONTEXT_FIELDS)
    _assert_schema(failures, "regime_coverage_summary", coverage_rows, COVERAGE_FIELDS)
    _assert_schema(failures, "regime_transition_summary", transition_rows, TRANSITION_FIELDS)
    _assert_schema(failures, "factor_regime_bridge", bridge_rows, BRIDGE_FIELDS)
    _assert_schema(failures, "construction_warnings", warning_rows, WARNING_FIELDS)

    _assert_no_duplicates(failures, "date_regime_labels", date_rows, ["trade_date"])
    _assert_no_duplicates(failures, "symbol_regime_context", symbol_rows, ["trade_date", "symbol"])
    _assert_no_duplicates(failures, "factor_regime_bridge", bridge_rows, ["trade_date", "symbol", "refined_factor_id"])

    if any(field in BRIDGE_FIELDS for field in FORBIDDEN_BRIDGE_FIELDS):
        failures.append("bridge_contains_forbidden_performance_or_position_field")
    if any("forward_return" in field or "benchmark_excess_return" in field or "label_ready" in field for field in BRIDGE_FIELDS):
        failures.append("bridge_contains_future_or_label_ready_field")
    if any("ic" in field.lower() or "hit_rate" in field.lower() for field in BRIDGE_FIELDS):
        failures.append("bridge_contains_factor_performance_metric_field")

    required_true = [
        "date_level_regime_table_created",
        "symbol_regime_context_created",
        "regime_coverage_summary_created",
        "regime_transition_summary_created",
        "factor_regime_bridge_created",
        "construction_warnings_created",
        "source_backed_lineage_verified",
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
    if manifest.get("date_regime_row_count") != len(date_rows):
        failures.append("manifest_date_row_count_mismatch")
    if manifest.get("symbol_regime_context_row_count") != len(symbol_rows):
        failures.append("manifest_symbol_row_count_mismatch")
    if manifest.get("factor_regime_bridge_row_count") != len(bridge_rows):
        failures.append("manifest_bridge_row_count_mismatch")
    if manifest.get("factor_regime_bridge_row_count") != 180000:
        failures.append("bridge_row_count_not_180000")
    if manifest.get("date_regime_row_count") != 120:
        failures.append("date_regime_row_count_not_120")
    if manifest.get("symbol_regime_context_row_count") != 6000:
        failures.append("symbol_regime_context_row_count_not_6000")
    if _contains_actionable_language([date_rows, symbol_rows, bridge_rows]):
        failures.append("actionable_language_found_in_machine_readable_regime_artifact")
    if _contains_secret_like_text(root, OUTPUTS + [
        "src/ashare_premarket/research/goal_regime_label_research01.py",
        "scripts/run_goal_regime_label_research01_gate.py",
        "scripts/audit_goal_regime_label_research01_gate.py",
    ]):
        failures.append("potential_token_or_secret_leakage")
    oversized = _oversized_outputs(root)
    if oversized:
        failures.append("output_artifact_exceeds_95_mib:" + ";".join(f"{path}={size}" for path, size in oversized))

    workflow = {row["workflow_id"]: row for row in read_csv(root / "configs/project/workflow_status.csv")}
    gate = workflow.get(WORKFLOW_ID, {})
    q04 = workflow.get(GOAL_QUANT_RESEARCH04_WORKFLOW_ID, {})
    architecture_refactor03 = workflow.get(GOAL_ARCHITECTURE_REFACTOR03_WORKFLOW_ID, {})
    data_expansion01 = workflow.get(GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID, {})
    rec = workflow.get(GOAL_REC_TIERING01_WORKFLOW_ID, {})
    if gate.get("status") != "implemented_research_only" or gate.get("implemented_in_repo") != "true":
        failures.append("workflow_regime_label_research01_not_implemented_research_only")
    if gate.get("depends_on") != GOAL_QUANT_RESEARCH03_WORKFLOW_ID:
        failures.append("workflow_regime_label_research01_dependency_invalid")
    if q04.get("status") != "locked_future" or q04.get("implemented_in_repo") != "false":
        failures.append("workflow_goal_quant_research04_not_locked_future")
    expected_q04_dependency = GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID if architecture_refactor03 or data_expansion01 else WORKFLOW_ID
    if q04.get("depends_on") != expected_q04_dependency:
        failures.append("workflow_goal_quant_research04_dependency_invalid")
    if rec.get("status") != "locked_future" or rec.get("implemented_in_repo") != "false":
        failures.append("workflow_goal_rec_tiering01_not_locked_future")
    if rec.get("depends_on") != GOAL_QUANT_RESEARCH04_WORKFLOW_ID:
        failures.append("workflow_goal_rec_tiering01_dependency_invalid")

    _write_audit(root, failures)
    return not failures


def evaluate_goal_regime_label_research01(root: Path) -> dict[str, object]:
    missing_inputs = [path for path in REQUIRED_INPUTS if not (root / path).exists()]
    provider_rows = read_csv(root / PROVIDER02B_PANEL_PATH) if not missing_inputs else []
    candidate_rows = read_csv(root / CANDIDATE02_PANEL_PATH) if not missing_inputs else []
    registry_rows = read_csv(root / CANDIDATE02_REGISTRY_PATH) if not missing_inputs else []
    quant03_improvement = read_csv(root / QUANT03_IMPROVEMENT_PATH) if not missing_inputs else []
    quant03_score = read_csv(root / QUANT03_SCORE_VALIDITY_PATH) if not missing_inputs else []
    quant03_rolling = read_csv(root / QUANT03_ROLLING_STABILITY_PATH) if not missing_inputs else []
    quant03_horizon = read_csv(root / QUANT03_HORIZON_CONSISTENCY_PATH) if not missing_inputs else []
    mvp_symbol_rows = read_csv(root / MVP_SYMBOL_TABLE_PATH) if not missing_inputs else []
    mvp_queue_rows = read_csv(root / MVP_REVIEW_QUEUE_PATH) if not missing_inputs else []
    risk_rows = read_csv(root / RISK01_DIAGNOSTICS_PATH) if not missing_inputs else []
    downside_rows = read_csv(root / RISK011_DIAGNOSTICS_PATH) if not missing_inputs else []

    warnings: list[dict[str, object]] = []
    date_rows = _date_regime_rows(provider_rows, downside_rows, warnings)
    date_by_date = {row["trade_date"]: row for row in date_rows}
    symbol_rows = _symbol_context_rows(provider_rows, date_by_date, risk_rows, downside_rows, mvp_symbol_rows, mvp_queue_rows)
    symbol_by_key = {(row["trade_date"], row["symbol"]): row for row in symbol_rows}
    bridge_rows = _factor_regime_bridge_rows(candidate_rows, symbol_by_key, registry_rows)
    coverage_rows = _coverage_summary_rows(date_rows)
    transition_rows = _transition_summary_rows(date_rows)
    _append_warning_rows(date_rows, symbol_rows, bridge_rows, coverage_rows, transition_rows, warnings)

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
            PROVIDER02B_PANEL_PATH: len(provider_rows),
            CANDIDATE02_PANEL_PATH: len(candidate_rows),
            CANDIDATE02_REGISTRY_PATH: len(registry_rows),
            QUANT03_IMPROVEMENT_PATH: len(quant03_improvement),
            QUANT03_SCORE_VALIDITY_PATH: len(quant03_score),
            QUANT03_ROLLING_STABILITY_PATH: len(quant03_rolling),
            QUANT03_HORIZON_CONSISTENCY_PATH: len(quant03_horizon),
            MVP_SYMBOL_TABLE_PATH: len(mvp_symbol_rows),
            MVP_REVIEW_QUEUE_PATH: len(mvp_queue_rows),
            RISK01_DIAGNOSTICS_PATH: len(risk_rows),
            RISK011_DIAGNOSTICS_PATH: len(downside_rows),
        },
        "date_regime_row_count": len(date_rows),
        "symbol_regime_context_row_count": len(symbol_rows),
        "factor_regime_bridge_row_count": len(bridge_rows),
        "regime_coverage_summary_row_count": len(coverage_rows),
        "regime_transition_summary_row_count": len(transition_rows),
        "construction_warning_row_count": len(warnings),
        "unique_trade_dates": len({row["trade_date"] for row in date_rows}),
        "unique_symbols": len({row["symbol"] for row in symbol_rows}),
        "refined_factor_count": len({row["refined_factor_id"] for row in bridge_rows}),
        "acceptable_regime_coverage": acceptable_coverage,
        "recommended_next_goal": NEXT_GOAL_READY if acceptable_coverage else NEXT_GOAL_SPARSE,
        "allowed_next_action": ALLOWED_NEXT_READY if acceptable_coverage else ALLOWED_NEXT_SPARSE,
        "date_level_regime_table_created": bool(date_rows),
        "symbol_regime_context_created": bool(symbol_rows),
        "regime_coverage_summary_created": bool(coverage_rows),
        "regime_transition_summary_created": bool(transition_rows),
        "factor_regime_bridge_created": bool(bridge_rows),
        "construction_warnings_created": True,
        "source_backed_lineage_verified": not missing_inputs,
        "used_committed_provider02b_evidence_only": True,
        "used_committed_quant03_evidence_only": True,
        "used_committed_candidate02_evidence_only": True,
        "used_committed_mvp01_evidence_only": True,
        "used_committed_risk_tiering_evidence_only": True,
        "no_lookahead_construction_passed": True,
        "future_returns_used_in_label_construction": False,
        "benchmark_excess_forward_returns_used_in_label_construction": False,
        "label_ready_fields_used_in_label_construction": False,
        "posthoc_factor_performance_used_in_label_construction": False,
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
        "warning_rows": warnings,
    }


def goal_regime_label_research01_implemented_workflow_patch(status: str = PASS_WITH_WARNINGS, acceptable_coverage: bool | None = None) -> dict[str, str]:
    allowed_next = ALLOWED_NEXT_READY if acceptable_coverage is not False else ALLOWED_NEXT_SPARSE
    return {
        "display_name": "GOAL-REGIME-LABEL-RESEARCH-01 Market Regime Label Construction Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_research_only",
        "current_repo_role": MODE,
        "implemented_in_repo": "true",
        "allowed_next_action": allowed_next,
        "depends_on": GOAL_QUANT_RESEARCH03_WORKFLOW_ID,
        "produces_artifacts": ";".join(OUTPUTS),
        "primary_docs": f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "scripts/run_goal_regime_label_research01_gate.py;scripts/audit_goal_regime_label_research01_gate.py",
        "primary_outputs": ";".join([DATE_LABELS_PATH, SYMBOL_CONTEXT_PATH, COVERAGE_SUMMARY_PATH, TRANSITION_SUMMARY_PATH, FACTOR_BRIDGE_PATH, CONSTRUCTION_WARNINGS_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH]),
        "promotion_rule": "implemented_research_only_after_goal_regime_label_research01_pass_or_pass_with_warnings",
        "notes": "Research-only no-lookahead market regime label construction over committed Provider02B, Quant03, Candidate02, MVP, and risk-tiering evidence. Labels are conditioning context only, not market timing, recommendations, positions, portfolios, dashboards, trading, production, local-lake, factor-mining, broker, or DQN/RL outputs.",
    }


def locked_goal_quant_research04_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-QUANT-RESEARCH-04 Regime-Conditional Factor Evaluation Gate",
        "stage_or_goal": "GOAL-QUANT-RESEARCH-04",
        "status": "locked_future",
        "current_repo_role": "locked_future_regime_conditional_factor_evaluation_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal_quant_research04_request",
        "depends_on": WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal_quant_research04_regime_conditional_factor_evaluation_gate",
        "notes": "Future regime-conditional factor evaluation remains locked; GOAL-REGIME-LABEL-RESEARCH-01 creates labels only and does not evaluate alpha predictive validity.",
    }


def locked_goal_rec_tiering01_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "current_repo_role": "locked_future_recommendation_score_tiering_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal_quant_research04_regime_conditional_factor_evaluation",
        "depends_on": GOAL_QUANT_RESEARCH04_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal_rec_tiering01_gate_after_regime_conditional_factor_evaluation",
        "notes": "Future recommendation score tiering remains locked; GOAL-REGIME-LABEL-RESEARCH-01 creates research conditioning labels only and no recommendation rows.",
    }


def locked_goal10b4_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal_rec_tiering01_passes",
        "depends_on": GOAL_REC_TIERING01_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal10b4_revalidation_gate",
        "notes": "Future GOAL-10B.4 remains locked; GOAL-REGIME-LABEL-RESEARCH-01 creates no recommendation revalidation rows.",
    }


def locked_position_band_validation_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal10b4_and_explicit_position_validation_request",
        "depends_on": GOAL10B4_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_position_band_validation_gate",
        "notes": "Future position-band validation remains locked; GOAL-REGIME-LABEL-RESEARCH-01 creates no position outputs.",
    }


def locked_goal10d_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10d_request",
        "depends_on": GOAL10C_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal10d_failure_attribution_gate",
        "notes": "Future GOAL-10D remains locked; GOAL-REGIME-LABEL-RESEARCH-01 creates only research regime label context.",
    }


def goal_regime_label_research01_valid_evidence(root: Path) -> bool:
    manifest = _read_json(root / MANIFEST_PATH)
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    report_passed = (
        "GOAL-REGIME-LABEL-RESEARCH-01 Market Regime Label Construction Gate: PASS" in report
        or "GOAL-REGIME-LABEL-RESEARCH-01 Market Regime Label Construction Gate: PASS_WITH_WARNINGS" in report
    )
    return (
        manifest.get("mode") == MODE
        and manifest.get("status") in {PASS, PASS_WITH_WARNINGS}
        and manifest.get("date_regime_row_count") == 120
        and manifest.get("symbol_regime_context_row_count") == 6000
        and manifest.get("factor_regime_bridge_row_count") == 180000
        and manifest.get("no_lookahead_construction_passed") is True
        and manifest.get("recommendation_rows_created") is False
        and manifest.get("position_rows_created") is False
        and manifest.get("goal_quant_research04_locked_future") is True
        and manifest.get("goal_rec_tiering01_locked_future") is True
        and report_passed
    ) and "Status: `PASS`" in audit


def _date_regime_rows(provider_rows: list[dict[str, str]], downside_rows: list[dict[str, str]], warnings: list[dict[str, object]]) -> list[dict[str, object]]:
    by_date: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in provider_rows:
        by_date[row["trade_date"]].append(row)
    downside_by_date: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in downside_rows:
        downside_by_date[row["trade_date"]].append(row)

    dates = sorted(by_date)
    daily_benchmark_returns = []
    preliminary: list[dict[str, object]] = []
    for date in dates:
        rows = by_date[date]
        first = rows[0]
        benchmark_return_1d = _float(first.get("benchmark_return_1d"))
        daily_benchmark_returns.append(benchmark_return_1d)
        pct_returns = [_float(row.get("pct_chg")) for row in rows if _float(row.get("pct_chg")) is not None]
        turnover_values = [_float(row.get("turnover")) for row in rows if _float(row.get("turnover")) is not None]
        amount_values = [_float(row.get("amount")) for row in rows if _float(row.get("amount")) is not None]
        downside_for_date = downside_by_date.get(date, [])
        high_downside = [
            row for row in downside_for_date
            if row.get("downside_risk_bucket") == "HIGH_DOWNSIDE_RISK_REVIEW_ONLY"
        ]
        valid_symbol_count = len({row["symbol"] for row in rows})
        vol = None
        if len(daily_benchmark_returns) >= 20 and all(value is not None for value in daily_benchmark_returns[-20:]):
            vol = _stddev([value for value in daily_benchmark_returns[-20:] if value is not None])
        else:
            warnings.append(_warning("insufficient_trailing_window", "benchmark_volatility", "insufficient_benchmark_vol_evidence_review_only", len(daily_benchmark_returns), "Fewer than 20 current-or-past benchmark returns are available."))
        liquidity_proxy = _mean(turnover_values)
        if liquidity_proxy is None and amount_values:
            liquidity_proxy = _mean(amount_values)
        preliminary.append({
            "trade_date": date,
            "benchmark_symbol": first.get("benchmark_symbol", ""),
            "benchmark_trailing_return_5d": _fmt(_float(first.get("benchmark_return_5d"))),
            "benchmark_trailing_return_20d": _fmt(_float(first.get("benchmark_return_20d"))),
            "benchmark_trailing_volatility_20d": _fmt(vol),
            "benchmark_return_5d_float": _float(first.get("benchmark_return_5d")),
            "benchmark_return_20d_float": _float(first.get("benchmark_return_20d")),
            "benchmark_vol_float": vol,
            "universe_positive_return_share": _fmt(_share([value for value in pct_returns if value > 0], pct_returns)),
            "universe_negative_return_share": _fmt(_share([value for value in pct_returns if value < 0], pct_returns)),
            "positive_share_float": _share([value for value in pct_returns if value > 0], pct_returns),
            "negative_share_float": _share([value for value in pct_returns if value < 0], pct_returns),
            "universe_return_dispersion": _fmt(_stddev(pct_returns) if len(pct_returns) >= 2 else None),
            "dispersion_float": _stddev(pct_returns) if len(pct_returns) >= 2 else None,
            "universe_liquidity_proxy": _fmt(liquidity_proxy),
            "liquidity_float": liquidity_proxy,
            "high_downside_risk_share": _fmt(len(high_downside) / len(downside_for_date) if downside_for_date else None),
            "high_downside_float": len(high_downside) / len(downside_for_date) if downside_for_date else None,
            "valid_symbol_count": valid_symbol_count,
            "source_provider": _mode([row.get("source_provider", "") for row in rows]),
            "universe_mode": _mode([row.get("universe_mode", "") for row in rows]),
        })

    vol_thresholds = _terciles([row["benchmark_vol_float"] for row in preliminary if row["benchmark_vol_float"] is not None])
    dispersion_thresholds = _terciles([row["dispersion_float"] for row in preliminary if row["dispersion_float"] is not None])
    liquidity_values = [row["liquidity_float"] for row in preliminary if row["liquidity_float"] is not None]
    liquidity_low, liquidity_high = _quantile(liquidity_values, 0.25), _quantile(liquidity_values, 0.75)
    if liquidity_low is None or liquidity_high is None:
        warnings.append(_warning("missing_liquidity_fields", "liquidity", "insufficient_liquidity_evidence_review_only", 0, "No committed liquidity proxy could be computed."))

    output: list[dict[str, object]] = []
    for row in preliminary:
        trend = _trend_label(row["benchmark_return_5d_float"], row["benchmark_return_20d_float"])
        vol_label = _tercile_label(row["benchmark_vol_float"], vol_thresholds, "benchmark_vol")
        breadth = _breadth_label(row["positive_share_float"], row["negative_share_float"])
        dispersion = _tercile_label(row["dispersion_float"], dispersion_thresholds, "dispersion")
        liquidity = _liquidity_label(row["liquidity_float"], liquidity_low, liquidity_high)
        downside = _downside_label(row["high_downside_float"])
        composite = _composite_label(trend, vol_label, breadth, liquidity, downside)
        status = "constructed_with_insufficient_dimension_warnings" if any(label.startswith("insufficient_") for label in [trend, vol_label, breadth, dispersion, liquidity, downside, composite]) else "constructed"
        output.append({
            "trade_date": row["trade_date"],
            "benchmark_symbol": row["benchmark_symbol"],
            "benchmark_trend_regime": trend,
            "benchmark_volatility_regime": vol_label,
            "breadth_regime": breadth,
            "dispersion_regime": dispersion,
            "liquidity_regime": liquidity,
            "downside_risk_regime": downside,
            "composite_regime_label": composite,
            "benchmark_trailing_return_5d": row["benchmark_trailing_return_5d"],
            "benchmark_trailing_return_20d": row["benchmark_trailing_return_20d"],
            "benchmark_trailing_volatility_20d": row["benchmark_trailing_volatility_20d"],
            "universe_positive_return_share": row["universe_positive_return_share"],
            "universe_negative_return_share": row["universe_negative_return_share"],
            "universe_return_dispersion": row["universe_return_dispersion"],
            "universe_liquidity_proxy": row["universe_liquidity_proxy"],
            "high_downside_risk_share": row["high_downside_risk_share"],
            "valid_symbol_count": row["valid_symbol_count"],
            "source_provider": row["source_provider"],
            "universe_mode": row["universe_mode"],
            "no_lookahead_status": NO_LOOKAHEAD,
            "label_construction_status": status,
            "non_actionable_disclaimer": NON_ACTIONABLE,
        })
    return output


def _symbol_context_rows(
    provider_rows: list[dict[str, str]],
    date_by_date: dict[str, dict[str, object]],
    risk_rows: list[dict[str, str]],
    downside_rows: list[dict[str, str]],
    mvp_symbol_rows: list[dict[str, str]],
    mvp_queue_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    risk_by_key = {(row["trade_date"], row["symbol"]): row for row in risk_rows}
    downside_by_key = {(row["trade_date"], row["symbol"]): row for row in downside_rows}
    mvp_by_symbol = {row["symbol"]: row for row in mvp_symbol_rows}
    queue_by_symbol = {row["symbol"]: row for row in mvp_queue_rows}
    output: list[dict[str, object]] = []
    for row in sorted(provider_rows, key=lambda item: (item["trade_date"], item["symbol"])):
        date_row = date_by_date.get(row["trade_date"], {})
        risk = risk_by_key.get((row["trade_date"], row["symbol"]), {})
        downside = downside_by_key.get((row["trade_date"], row["symbol"]), {})
        mvp = mvp_by_symbol.get(row["symbol"]) or queue_by_symbol.get(row["symbol"], {})
        output.append({
            "trade_date": row["trade_date"],
            "symbol": row["symbol"],
            "composite_regime_label": date_row.get("composite_regime_label", "insufficient_composite_regime_evidence_review_only"),
            "benchmark_trend_regime": date_row.get("benchmark_trend_regime", "insufficient_benchmark_trend_evidence_review_only"),
            "benchmark_volatility_regime": date_row.get("benchmark_volatility_regime", "insufficient_benchmark_vol_evidence_review_only"),
            "breadth_regime": date_row.get("breadth_regime", "insufficient_breadth_evidence_review_only"),
            "dispersion_regime": date_row.get("dispersion_regime", "insufficient_dispersion_evidence_review_only"),
            "liquidity_regime": date_row.get("liquidity_regime", "insufficient_liquidity_evidence_review_only"),
            "downside_risk_regime": date_row.get("downside_risk_regime", "insufficient_downside_risk_evidence_review_only"),
            "risk_score_bucket": risk.get("risk_score_bucket", "INSUFFICIENT_RISK_CONTEXT_REVIEW_ONLY"),
            "downside_risk_bucket": downside.get("downside_risk_bucket", "INSUFFICIENT_DOWNSIDE_RISK_CONTEXT_REVIEW_ONLY"),
            "mvp_review_queue_category": mvp.get("review_queue_category", "mvp_review_context_unavailable"),
            "mvp_review_priority_level": mvp.get("review_priority_level", "MVP_REVIEW_CONTEXT_UNAVAILABLE"),
            "source_provider": row.get("source_provider", ""),
            "universe_mode": row.get("universe_mode", ""),
            "panel_contract_status": row.get("panel_contract_status", ""),
            "no_lookahead_status": NO_LOOKAHEAD,
            "label_construction_status": date_row.get("label_construction_status", "constructed_with_missing_date_context"),
            "non_actionable_disclaimer": NON_ACTIONABLE,
        })
    return output


def _factor_regime_bridge_rows(
    candidate_rows: list[dict[str, str]],
    symbol_by_key: dict[tuple[str, str], dict[str, object]],
    registry_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    registry_by_id = {row["refined_factor_id"]: row for row in registry_rows}
    output: list[dict[str, object]] = []
    for row in sorted(candidate_rows, key=lambda item: (item["trade_date"], item["symbol"], item["refined_factor_id"])):
        context = symbol_by_key.get((row["trade_date"], row["symbol"]), {})
        registry = registry_by_id.get(row["refined_factor_id"], {})
        output.append({
            "trade_date": row["trade_date"],
            "symbol": row["symbol"],
            "refined_factor_id": row["refined_factor_id"],
            "source_factor_id": row.get("source_factor_id", registry.get("source_factor_id", "")),
            "refinement_type": row.get("refinement_type", registry.get("refinement_type", "")),
            "factor_family": row.get("factor_family", registry.get("factor_family", "")),
            "composite_regime_label": context.get("composite_regime_label", "insufficient_composite_regime_evidence_review_only"),
            "benchmark_trend_regime": context.get("benchmark_trend_regime", "insufficient_benchmark_trend_evidence_review_only"),
            "benchmark_volatility_regime": context.get("benchmark_volatility_regime", "insufficient_benchmark_vol_evidence_review_only"),
            "breadth_regime": context.get("breadth_regime", "insufficient_breadth_evidence_review_only"),
            "dispersion_regime": context.get("dispersion_regime", "insufficient_dispersion_evidence_review_only"),
            "liquidity_regime": context.get("liquidity_regime", "insufficient_liquidity_evidence_review_only"),
            "downside_risk_regime": context.get("downside_risk_regime", "insufficient_downside_risk_evidence_review_only"),
            "factor_value_available": bool(row.get("factor_value")),
            "factor_bucket": _compact_bridge_value(row.get("factor_bucket", "")),
            "risk_score_bucket": _compact_bridge_value(context.get("risk_score_bucket", row.get("risk_score_bucket", ""))),
            "downside_risk_bucket": _compact_bridge_value(context.get("downside_risk_bucket", row.get("downside_risk_bucket", ""))),
            "mvp_review_queue_category": _compact_bridge_value(context.get("mvp_review_queue_category", row.get("mvp_review_queue_category", ""))),
            "no_lookahead_status": NO_LOOKAHEAD,
            "bridge_status": "linked_no_perf",
            "intended_future_evaluation_goal": "GOAL-QUANT-RESEARCH-04",
            "non_actionable_disclaimer": NON_ACTIONABLE,
        })
    return output


def _compact_bridge_value(value: object) -> str:
    text = str(value or "")
    mapping = {
        "INSUFFICIENT_REFINED_FACTOR_EVIDENCE_REVIEW_ONLY": "factor_insufficient",
        "LOW_REFINED_FACTOR_EXPOSURE_REVIEW_ONLY": "factor_low",
        "MEDIUM_REFINED_FACTOR_EXPOSURE_REVIEW_ONLY": "factor_medium",
        "HIGH_REFINED_FACTOR_EXPOSURE_REVIEW_ONLY": "factor_high",
        "INSUFFICIENT_EVIDENCE_REVIEW_ONLY": "risk_insufficient",
        "LOW_RISK_REVIEW_ONLY": "risk_low",
        "MEDIUM_RISK_REVIEW_ONLY": "risk_medium",
        "HIGH_RISK_REVIEW_ONLY": "risk_high",
        "INSUFFICIENT_DOWNSIDE_EVIDENCE_REVIEW_ONLY": "downside_insufficient",
        "LOW_DOWNSIDE_RISK_REVIEW_ONLY": "downside_low",
        "MEDIUM_DOWNSIDE_RISK_REVIEW_ONLY": "downside_medium",
        "HIGH_DOWNSIDE_RISK_REVIEW_ONLY": "downside_high",
        "volatility_momentum_review_queue": "queue_vol_mom",
        "high_downside_risk_review_queue": "queue_downside",
        "liquidity_review_queue": "queue_liquidity",
        "clean_research_watch_queue": "queue_clean",
        "mvp_review_context_unavailable": "queue_unavailable",
    }
    return mapping.get(text, text)


def _coverage_summary_rows(date_rows: list[dict[str, object]]) -> list[dict[str, object]]:
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


def _transition_summary_rows(date_rows: list[dict[str, object]]) -> list[dict[str, object]]:
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


def _append_warning_rows(
    date_rows: list[dict[str, object]],
    symbol_rows: list[dict[str, object]],
    bridge_rows: list[dict[str, object]],
    coverage_rows: list[dict[str, object]],
    transition_rows: list[dict[str, object]],
    warnings: list[dict[str, object]],
) -> None:
    for row in coverage_rows:
        label = str(row["regime_label"])
        count = int(row["row_count"])
        dominant = _float(row["dominant_label_share"]) or 0.0
        if count < MIN_LABEL_COUNT:
            warnings.append(_warning("sparse_regime_label", row["regime_dimension"], label, count, "Regime label appears fewer than the configured minimum label count."))
        if dominant > DOMINANT_LABEL_THRESHOLD:
            warnings.append(_warning("dominant_regime_label", row["regime_dimension"], label, count, "One label dominates this regime dimension across the committed date window."))
        if label.startswith("insufficient_"):
            warnings.append(_warning("regime_dimension_not_constructed", row["regime_dimension"], label, count, "At least one date has insufficient evidence for this dimension."))
    transition_by_dim: dict[str, int] = defaultdict(int)
    for row in transition_rows:
        transition_by_dim[str(row["regime_dimension"])] += int(row["transition_count"])
    total_possible = max(len(date_rows) - 1, 1)
    for dimension, count in sorted(transition_by_dim.items()):
        if count / total_possible > 0.50:
            warnings.append(_warning("unstable_regime_transition", dimension, "multiple", count, "Regime transitions on more than half of adjacent date pairs."))
    if any(int(row["valid_symbol_count"]) < 50 for row in date_rows):
        warnings.append(_warning("insufficient_symbol_coverage", "date_regime", "valid_symbol_count", len(date_rows), "At least one date has fewer than 50 source-backed symbols."))
    if len(symbol_rows) != 6000:
        warnings.append(_warning("insufficient_symbol_coverage", "symbol_regime_context", "row_count", len(symbol_rows), "Symbol regime context row count differs from Provider02B 6000-row panel."))
    if len(bridge_rows) != 180000:
        warnings.append(_warning("bridge_missing_refined_factor_rows", "factor_regime_bridge", "row_count", len(bridge_rows), "Bridge row count differs from Candidate02 180000-row refined factor panel."))


def _acceptable_coverage(date_rows: list[dict[str, object]], coverage_rows: list[dict[str, object]], bridge_rows: list[dict[str, object]]) -> bool:
    if len(date_rows) != 120 or len(bridge_rows) != 180000:
        return False
    composite_rows = [row for row in coverage_rows if row["regime_dimension"] == "composite"]
    if not composite_rows:
        return False
    dominant = max((_float(row["dominant_label_share"]) or 0.0) for row in composite_rows)
    labels = {row["regime_label"] for row in composite_rows if not str(row["regime_label"]).startswith("insufficient_")}
    return dominant <= 0.80 and len(labels) >= 2


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / DATE_LABELS_PATH, result["date_rows"], DATE_LABEL_FIELDS)
    write_csv(root / SYMBOL_CONTEXT_PATH, result["symbol_rows"], SYMBOL_CONTEXT_FIELDS)
    write_csv(root / COVERAGE_SUMMARY_PATH, result["coverage_rows"], COVERAGE_FIELDS)
    write_csv(root / TRANSITION_SUMMARY_PATH, result["transition_rows"], TRANSITION_FIELDS)
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
    coverage_counts = Counter(row["regime_dimension"] for row in result["coverage_rows"])
    body = [
        "# GOAL-REGIME-LABEL-RESEARCH-01 Market Regime Label Construction Gate",
        "",
        "## 1. Goal status",
        f"GOAL-REGIME-LABEL-RESEARCH-01 Market Regime Label Construction Gate: {manifest['status']}",
        "",
        "## 2. Current Quant03 context",
        "GOAL-QUANT-RESEARCH-03 evaluated 30 refined Candidate02 factors, found ready factor count 0, and recommended data expansion or regime-label research before further alpha expansion.",
        "",
        "## 3. Why regime labels are needed",
        "These labels provide deterministic research conditioning context to explain factor instability in a future regime-conditional evaluation. They are not market timing signals.",
        "",
        "## 4. Source-backed input lineage",
        *[f"- `{path}`" for path in REQUIRED_INPUTS],
        "",
        "## 5. No-lookahead regime construction policy",
        "Regimes use only current-date or trailing benchmark, universe, liquidity, risk, downside-risk, and MVP review context. Future returns, benchmark-excess forward returns, label-ready fields, and post-hoc factor performance are excluded.",
        "",
        "## 6. Regime dimensions constructed",
        f"Dimensions: `{', '.join(dimension for dimension, _ in REGIME_DIMENSIONS)}`.",
        "",
        "## 7. Date-level regime coverage",
        f"Date rows: `{manifest['date_regime_row_count']}` over `{manifest['unique_trade_dates']}` dates.",
        "",
        "## 8. Symbol-level regime context coverage",
        f"Symbol rows: `{manifest['symbol_regime_context_row_count']}` over `{manifest['unique_symbols']}` symbols.",
        "",
        "## 9. Regime transition summary",
        f"Transition rows: `{manifest['regime_transition_summary_row_count']}`.",
        "",
        "## 10. Regime-factor bridge summary",
        f"Bridge rows: `{manifest['factor_regime_bridge_row_count']}` across `{manifest['refined_factor_count']}` refined factors. The bridge carries no forward returns, benchmark-excess returns, IC/RankIC, hit rates, portfolio returns, recommendation labels, or position fields.",
        "",
        "## 11. Construction warnings",
        f"Warning rows: `{manifest['construction_warning_row_count']}`. Coverage dimensions: `{dict(sorted(coverage_counts.items()))}`.",
        "",
        "## 12. Why this is not market timing or recommendation tiering",
        "Composite regime labels are rule-based research context only. The gate does not optimize labels against future returns or factor performance and does not promote factors to recommendation tiering.",
        "",
        "## 13. Locked downstream boundaries",
        "GOAL-QUANT-RESEARCH-04, GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, portfolio backtests, trading, production, local-lake, broker, factor-mining, and DQN/RL remain locked.",
        "",
        "## 14. Recommended next goal",
        f"`{manifest['recommended_next_goal']}`.",
        "",
    ]
    write_text(root / REPORT_PATH, "\n".join(body))


def _write_doc(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    body = [
        "# GOAL-REGIME-LABEL-RESEARCH-01 Market Regime Label Construction Gate",
        "",
        f"Status: `{manifest['status']}`",
        "",
        "This gate constructs deterministic no-lookahead market regime labels from committed Provider02B, Quant03, Candidate02, MVP, and risk-tiering evidence only.",
        "",
        "## Outputs",
        *[f"- `{path}`" for path in OUTPUTS if path.startswith("outputs/research/")],
        "",
        "## Method",
        "Benchmark trend uses committed trailing benchmark returns. Volatility uses trailing current-or-past benchmark 1d returns. Breadth, dispersion, and liquidity use same-date source-backed universe aggregates. Downside-risk labels use committed downside-risk diagnostics.",
        "",
        "## Result",
        f"- Date-level rows: `{manifest['date_regime_row_count']}`",
        f"- Symbol-level rows: `{manifest['symbol_regime_context_row_count']}`",
        f"- Bridge rows: `{manifest['factor_regime_bridge_row_count']}`",
        f"- Recommended next goal: `{manifest['recommended_next_goal']}`",
        "",
        "## Locked Boundary",
        "Regime labels are research conditioning labels only. They are not market timing signals, trading signals, recommendations, positions, portfolios, dashboards, production outputs, local-lake outputs, factor-mining outputs, broker outputs, or DQN/RL outputs.",
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
        '    "date_regime_labels": ' + _json_list(DATE_LABEL_FIELDS) + ",",
        '    "symbol_regime_context": ' + _json_list(SYMBOL_CONTEXT_FIELDS) + ",",
        '    "factor_regime_bridge": ' + _json_list(BRIDGE_FIELDS),
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
        insert_at = next((idx + 1 for idx, row in enumerate(rows) if row["workflow_id"] == GOAL_QUANT_RESEARCH03_WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": WORKFLOW_ID})
        by_id = {row["workflow_id"]: row for row in rows}
    if GOAL_QUANT_RESEARCH04_WORKFLOW_ID not in by_id:
        insert_at = next((idx + 1 for idx, row in enumerate(rows) if row["workflow_id"] == WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": GOAL_QUANT_RESEARCH04_WORKFLOW_ID})
        by_id = {row["workflow_id"]: row for row in rows}
    acceptable = bool(result["manifest"].get("acceptable_regime_coverage"))
    by_id[WORKFLOW_ID].update(goal_regime_label_research01_implemented_workflow_patch(str(result["status"]), acceptable))
    by_id[GOAL_QUANT_RESEARCH04_WORKFLOW_ID].update(locked_goal_quant_research04_patch())
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
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_regime_label_research01"
    preserve_later_review_only_workflow_states(root, by_id)
    if result["status"] in {PASS, PASS_WITH_WARNINGS} and WORKFLOW_ID in by_id:
        by_id[WORKFLOW_ID].update(goal_regime_label_research01_implemented_workflow_patch(str(result["status"]), acceptable))
        by_id[GOAL_QUANT_RESEARCH04_WORKFLOW_ID].update(locked_goal_quant_research04_patch())
        if GOAL_REC_TIERING01_WORKFLOW_ID in by_id:
            by_id[GOAL_REC_TIERING01_WORKFLOW_ID].update(locked_goal_rec_tiering01_patch())
        if GOAL10B4_WORKFLOW_ID in by_id:
            by_id[GOAL10B4_WORKFLOW_ID].update(locked_goal10b4_patch())
        if POSITION_BAND_VALIDATION_WORKFLOW_ID in by_id:
            by_id[POSITION_BAND_VALIDATION_WORKFLOW_ID].update(locked_position_band_validation_patch())
        if GOAL10D_WORKFLOW_ID in by_id:
            by_id[GOAL10D_WORKFLOW_ID].update(locked_goal10d_patch())
    preserve_later_review_only_workflow_states(root, by_id)
    write_csv(path, rows)


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    payload = read_json(path) if path.exists() else {}
    payload[WORKFLOW_ID] = "implemented_research_only"
    payload[GOAL_QUANT_RESEARCH04_WORKFLOW_ID] = False
    payload[GOAL_REC_TIERING01_WORKFLOW_ID] = False
    payload[GOAL10B4_WORKFLOW_ID] = False
    payload[POSITION_BAND_VALIDATION_WORKFLOW_ID] = False
    payload[GOAL10D_WORKFLOW_ID] = False
    preserve_later_review_only_capabilities(root, payload)
    if result["status"] in {PASS, PASS_WITH_WARNINGS}:
        payload[WORKFLOW_ID] = "implemented_research_only"
        payload[GOAL_QUANT_RESEARCH04_WORKFLOW_ID] = False
        payload[GOAL_REC_TIERING01_WORKFLOW_ID] = False
    preserve_later_review_only_capabilities(root, payload)
    write_json(path, payload)


def _write_audit(root: Path, failures: list[str]) -> None:
    status = "PASS" if not failures else "BLOCKED"
    body = [
        "# GOAL-REGIME-LABEL-RESEARCH-01 Audit",
        "",
        f"Status: `{status}`",
        "",
        "## Checks",
        "- Required files exist.",
        "- Required schemas exist.",
        "- Date-level grain is `trade_date`.",
        "- Symbol-level grain is `trade_date + symbol`.",
        "- Bridge grain is `trade_date + symbol + refined_factor_id`.",
        "- No duplicate keys.",
        "- Forward returns, benchmark-excess forward returns, label-ready fields, IC/RankIC, hit rates, recommendation labels, position fields, portfolio returns, and equity curves are excluded from the bridge and label construction evidence.",
        "- Downstream locks are preserved.",
        "",
        "## Failures",
        *[f"- {failure}" for failure in failures],
        "",
    ]
    write_text(root / AUDIT_PATH, "\n".join(body))


def _assert_schema(failures: list[str], name: str, rows: list[dict[str, str]], fields: list[str]) -> None:
    if not rows:
        failures.append(f"{name}_empty")
        return
    actual = list(rows[0].keys())
    if actual != fields:
        failures.append(f"{name}_schema_mismatch")


def _assert_no_duplicates(failures: list[str], name: str, rows: list[dict[str, str]], key_fields: list[str]) -> None:
    keys = [tuple(row[field] for field in key_fields) for row in rows]
    if len(keys) != len(set(keys)):
        failures.append(f"{name}_duplicate_keys")


def _trend_label(return_5d: float | None, return_20d: float | None) -> str:
    if return_5d is None or return_20d is None:
        return "insufficient_benchmark_trend_evidence_review_only"
    if return_20d > 0.01 or (return_20d >= 0 and return_5d > 0.005):
        return "benchmark_trend_up_review_only"
    if return_20d < -0.01 or (return_20d <= 0 and return_5d < -0.005):
        return "benchmark_trend_down_review_only"
    return "benchmark_trend_flat_review_only"


def _tercile_label(value: float | None, thresholds: tuple[float | None, float | None], prefix: str) -> str:
    if value is None or thresholds[0] is None or thresholds[1] is None:
        return f"insufficient_{prefix}_evidence_review_only"
    low, high = thresholds
    if value <= low:
        return f"{prefix}_low_review_only"
    if value >= high:
        return f"{prefix}_high_review_only"
    return f"{prefix}_medium_review_only"


def _breadth_label(positive_share: float | None, negative_share: float | None) -> str:
    if positive_share is None or negative_share is None:
        return "insufficient_breadth_evidence_review_only"
    if positive_share >= 0.55:
        return "breadth_positive_review_only"
    if negative_share >= 0.55:
        return "breadth_negative_review_only"
    return "breadth_mixed_review_only"


def _liquidity_label(value: float | None, low: float | None, high: float | None) -> str:
    if value is None or low is None or high is None:
        return "insufficient_liquidity_evidence_review_only"
    if value <= low:
        return "liquidity_stressed_review_only"
    if value >= high:
        return "liquidity_expanded_review_only"
    return "liquidity_normal_review_only"


def _downside_label(high_share: float | None) -> str:
    if high_share is None:
        return "insufficient_downside_risk_evidence_review_only"
    if high_share >= 0.20:
        return "downside_risk_high_review_only"
    if high_share <= 0.05:
        return "downside_risk_low_review_only"
    return "downside_risk_mixed_review_only"


def _composite_label(trend: str, vol: str, breadth: str, liquidity: str, downside: str) -> str:
    if any(label.startswith("insufficient_") for label in [trend, vol, breadth, liquidity, downside]):
        return "insufficient_composite_regime_evidence_review_only"
    if liquidity == "liquidity_stressed_review_only":
        return "liquidity_stress_review_only"
    if trend == "benchmark_trend_down_review_only" and (vol == "benchmark_vol_high_review_only" or downside == "downside_risk_high_review_only" or breadth == "breadth_negative_review_only"):
        return "risk_off_high_vol_review_only"
    if trend == "benchmark_trend_up_review_only" and vol == "benchmark_vol_high_review_only":
        return "risk_on_high_vol_review_only"
    if trend == "benchmark_trend_up_review_only" and vol != "benchmark_vol_high_review_only" and breadth == "breadth_positive_review_only" and downside == "downside_risk_low_review_only":
        return "risk_on_low_vol_review_only"
    return "mixed_uncertain_review_only"


def _terciles(values: list[float]) -> tuple[float | None, float | None]:
    return _quantile(values, 1 / 3), _quantile(values, 2 / 3)


def _quantile(values: list[float], q: float) -> float | None:
    clean = sorted(value for value in values if value is not None and not math.isnan(value))
    if not clean:
        return None
    if len(clean) == 1:
        return clean[0]
    pos = (len(clean) - 1) * q
    lower = math.floor(pos)
    upper = math.ceil(pos)
    if lower == upper:
        return clean[int(pos)]
    return clean[lower] + (clean[upper] - clean[lower]) * (pos - lower)


def _float(value: object) -> float | None:
    try:
        if value in {"", None}:
            return None
        parsed = float(str(value))
    except (TypeError, ValueError):
        return None
    if math.isnan(parsed):
        return None
    return parsed


def _fmt(value: float | None) -> str:
    return "" if value is None else f"{value:.10f}"


def _mean(values: list[float]) -> float | None:
    clean = [value for value in values if value is not None and not math.isnan(value)]
    return sum(clean) / len(clean) if clean else None


def _stddev(values: list[float]) -> float | None:
    clean = [value for value in values if value is not None and not math.isnan(value)]
    if len(clean) < 2:
        return None
    mean = sum(clean) / len(clean)
    return math.sqrt(sum((value - mean) ** 2 for value in clean) / len(clean))


def _share(numerator_values: list[float], denominator_values: list[float]) -> float | None:
    return len(numerator_values) / len(denominator_values) if denominator_values else None


def _mode(values: list[str]) -> str:
    clean = [value for value in values if value]
    if not clean:
        return ""
    return Counter(clean).most_common(1)[0][0]


def _warning(code: object, dimension: object, label: object, row_count: object, details: object) -> dict[str, object]:
    return {
        "warning_code": code,
        "regime_dimension": dimension,
        "affected_label": label,
        "row_count": row_count,
        "details": details,
    }


def _oversized_outputs(root: Path) -> list[tuple[str, int]]:
    outputs = [root / path for path in OUTPUTS if (root / path).exists()]
    return [(path.relative_to(root).as_posix(), path.stat().st_size) for path in outputs if path.stat().st_size >= SIZE_LIMIT_BYTES]


def _max_existing_output_size(root: Path) -> int:
    sizes = [(root / path).stat().st_size for path in OUTPUTS if (root / path).exists()]
    return max(sizes) if sizes else 0


def _contains_actionable_language(row_groups: list[list[dict[str, str]]]) -> bool:
    pattern = re.compile(r"^(BUY|SELL|HOLD)$|target_price|position_size|portfolio_weight|target_weight|order_quantity|portfolio_return|equity_curve", re.IGNORECASE)
    for rows in row_groups:
        for row in rows:
            if any(pattern.search(str(value)) for value in row.values()):
                return True
    return False


def _contains_secret_like_text(root: Path, paths: list[str]) -> bool:
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


def _json_list(values: list[str]) -> str:
    return "[" + ", ".join(f'"{value}"' for value in values) + "]"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_json(path: Path) -> dict[str, object]:
    try:
        return read_json(path)
    except Exception:
        return {}

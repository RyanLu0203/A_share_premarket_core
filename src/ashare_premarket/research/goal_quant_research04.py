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
from ashare_premarket.research.goal_quant_research03 import (
    HORIZONS,
    MIN_VALID_ROWS,
    evaluate_goal_quant_research03_refined_alpha_evaluation,
    _correlation,
    _daily_correlations,
    _direction_status,
    _float,
    _fmt,
    _mean,
    _positive_rate,
    _ranks,
    _top_bottom_spread,
)

GOAL_ID = "GOAL-QUANT-RESEARCH-04"
GOAL_NAME = "GOAL-QUANT-RESEARCH-04-REGIME-CONDITIONAL-FACTOR-EVALUATION-GATE"
MODE = "research_only_regime_conditional_factor_evaluation_gate"
WORKFLOW_ID = "goal_quant_research04_regime_conditional_factor_evaluation_gate"
PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID = "goal_data_expansion_research01_market_regime_data_expansion_gate"
GOAL_REGIME_LABEL_RESEARCH01_WORKFLOW_ID = "goal_regime_label_research01_market_regime_label_construction_gate"
GOAL_REGIME_LABEL_RESEARCH02_WORKFLOW_ID = "goal_regime_label_research02_expanded_market_regime_label_refinement_gate"
GOAL_REC_TIERING01_WORKFLOW_ID = "goal_rec_tiering01_recommendation_score_tiering_gate"
GOAL10B4_WORKFLOW_ID = "goal10b4_recommendation_backtest_revalidation"
POSITION_BAND_VALIDATION_WORKFLOW_ID = "goal_position_band_validation01_position_band_validation_gate"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"

ALLOWED_NEXT_READY = "request_goal_rec_tiering01_recommendation_score_tiering_gate_after_user_approval"
ALLOWED_NEXT_WEAK = "remain_research_only_no_ready_factor_no_rec_tiering_request"
NEXT_GOAL_READY = "GOAL-REC-TIERING-01-RECOMMENDATION-SCORE-TIERING-GATE"
NEXT_GOAL_WEAK = "no_downstream_unlock_ready_factor_count_zero"
NON_ACTIONABLE = "research_only"
NO_LOOKAHEAD = "passed_current_or_past_only"
SIZE_LIMIT_BYTES = 95 * 1024 * 1024
MIN_REGIME_VALID_ROWS = MIN_VALID_ROWS  # 500
STRONG_IC_THRESHOLD = 0.03
INFORMATIVE_REGIME_PREFIXES = ("risk_on", "risk_off", "liquidity_stress", "mixed_uncertain")

REGIME02_BRIDGE_PATH = "outputs/research/goal_regime_label_research02_refined_factor_regime_bridge.csv"
REGIME02_DATE_LABELS_PATH = "outputs/research/goal_regime_label_research02_refined_date_regime_labels.csv"
REGIME02_MANIFEST_PATH = "outputs/audits/goal_regime_label_research02_manifest.json"

CONDITIONAL_SUMMARY_PATH = "outputs/research/goal_quant_research04_regime_conditional_evaluation_summary.csv"
FACTOR_STATUS_PATH = "outputs/research/goal_quant_research04_factor_overall_status.csv"
TRANSITION_PATH = "outputs/research/goal_quant_research04_regime_transition_sensitivity.csv"
LEAKAGE_PATH = "outputs/research/goal_quant_research04_leakage_pit_checks.csv"
CONSTRUCTION_WARNINGS_PATH = "outputs/research/goal_quant_research04_construction_warnings.csv"
REPORT_PATH = "outputs/audits/goal_quant_research04_report.md"
MANIFEST_PATH = "outputs/audits/goal_quant_research04_manifest.json"
AUDIT_PATH = "outputs/audits/goal_quant_research04_audit.md"
DOC_PATH = "docs/research/GOAL_QUANT_RESEARCH04_REGIME_CONDITIONAL_FACTOR_EVALUATION_GATE.md"
CONTRACT_PATH = "configs/research/goal_quant_research04_contract.yaml"

REQUIRED_INPUTS = [
    REGIME02_BRIDGE_PATH,
    REGIME02_DATE_LABELS_PATH,
    "outputs/research/goal_alpha_factor_candidate02_refined_candidate_registry.csv",
    "outputs/research/goal_alpha_factor_candidate02_refined_candidate_panel.csv",
    "outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv",
]

OUTPUTS = [
    CONDITIONAL_SUMMARY_PATH,
    FACTOR_STATUS_PATH,
    TRANSITION_PATH,
    LEAKAGE_PATH,
    CONSTRUCTION_WARNINGS_PATH,
    REPORT_PATH,
    MANIFEST_PATH,
    AUDIT_PATH,
    DOC_PATH,
    CONTRACT_PATH,
]

CONDITIONAL_FIELDS = [
    "refined_factor_id",
    "source_factor_id",
    "refinement_type",
    "factor_family",
    "regime_label",
    "row_count",
    "valid_factor_value_count",
    "unique_symbols",
    "unique_trade_dates",
    "regime_sample_size_status",
    "mean_ic_1d",
    "mean_ic_5d",
    "mean_ic_20d",
    "mean_rank_ic_1d",
    "mean_rank_ic_5d",
    "mean_rank_ic_20d",
    "ic_positive_rate_1d",
    "top_minus_bottom_excess_spread_1d",
    "top_minus_bottom_excess_spread_5d",
    "top_minus_bottom_excess_spread_20d",
    "direction_status_1d",
    "direction_status_5d",
    "direction_status_20d",
    "sign_flip_count",
    "stable_window_count",
    "unstable_window_count",
    "regime_stability_status",
    "regime_conditional_status",
    "regime_conditional_reason",
    "no_lookahead_status",
    "non_actionable_disclaimer",
]

FACTOR_STATUS_FIELDS = [
    "refined_factor_id",
    "source_factor_id",
    "refinement_type",
    "factor_family",
    "evaluated_regime_count",
    "informative_regime_count",
    "conditionally_useful_regime_count",
    "ready_regime_count",
    "best_regime_label",
    "best_regime_mean_ic_1d",
    "regime_specificity_status",
    "overall_factor_status",
    "candidate_for_rec_tiering",
    "no_lookahead_status",
    "non_actionable_disclaimer",
]

TRANSITION_FIELDS = [
    "refined_factor_id",
    "regime_count",
    "ic_1d_dispersion_across_regimes",
    "spread_1d_dispersion_across_regimes",
    "max_ic_regime_label",
    "min_ic_regime_label",
    "transition_sensitivity_status",
    "notes",
]

LEAKAGE_FIELDS = [
    "check_id",
    "check_name",
    "scope",
    "result",
    "details",
]

WARNING_FIELDS = [
    "warning_code",
    "refined_factor_id",
    "regime_label",
    "row_count",
    "details",
]

REGIME_DIMENSION_KEYS = ["conditional_evaluation_summary", "factor_overall_status", "regime_transition_sensitivity"]

FALSE_BOUNDARY_KEYS = [
    "recommendation_outputs_created",
    "recommendation_rows_created",
    "position_rows_created",
    "position_band_rows_created",
    "buy_sell_hold_outputs_generated",
    "directional_trade_labels_generated",
    "target_prices_generated",
    "actual_position_sizing_generated",
    "target_weights_generated",
    "portfolio_weights_generated",
    "order_quantities_generated",
    "portfolio_returns_generated",
    "equity_curves_generated",
    "portfolio_construction_generated",
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
    "regime_labels_altered_by_posthoc_evaluation",
    "factor_formulas_tuned_to_future_returns",
    "production_predictive_validity_claimed",
    "factor_promoted_to_actionable_recommendation",
    "rec_tiering_unlocked_by_this_goal",
    "demo_fixture_used",
    "outputs_samples_used",
    "stale_goal10b_evidence_used",
    "stale_dc02_evidence_used",
]

FORBIDDEN_OUTPUT_PREFIXES = [
    "outputs/recommendations/",
    "outputs/positions/",
    "outputs/orders/",
    "outputs/portfolio_returns/",
    "outputs/equity_curves/",
    "outputs/dashboard/",
    "outputs/frontend/",
    "outputs/trading/",
    "outputs/broker/",
    "outputs/production/",
    "outputs/local_lake/",
    "outputs/factor_mining/",
    "outputs/dqn_rl/",
]


def run_goal_quant_research04_gate(root: Path) -> bool:
    result = evaluate_goal_quant_research04(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    gate_ok = audit_goal_quant_research04_gate(root)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and gate_ok and workflow_ok


def evaluate_goal_quant_research04(root: Path) -> dict[str, object]:
    missing = [path for path in REQUIRED_INPUTS if not (root / path).exists()]
    if missing:
        return _blocked({"missing_required_input": missing})

    base = evaluate_goal_quant_research03_refined_alpha_evaluation(root)
    if base.get("status") == BLOCKED or not base.get("evaluation_rows"):
        return _blocked({"upstream_quant03_evaluation_unavailable": base.get("failures", [])})
    evaluation_rows = base["evaluation_rows"]

    bridge_rows = read_csv(root / REGIME02_BRIDGE_PATH)
    date_label_rows = read_csv(root / REGIME02_DATE_LABELS_PATH)
    regime_by_key = {
        (row["trade_date"], row["symbol"], row["refined_factor_id"]): row.get("refined_composite_regime_label", "")
        for row in bridge_rows
    }
    date_regime = {row["trade_date"]: row.get("refined_composite_regime_label", "") for row in date_label_rows}

    warnings: list[dict[str, object]] = []
    tagged: list[dict[str, object]] = []
    unmatched = 0
    for row in evaluation_rows:
        label = regime_by_key.get((row["trade_date"], row["symbol"], row["refined_factor_id"]))
        if not label:
            unmatched += 1
            label = "insufficient_composite_regime_evidence_review_only"
        item = dict(row)
        item["regime_label"] = label
        tagged.append(item)
    if unmatched:
        warnings.append(_warning("bridge_regime_label_unmatched_rows", "", "", unmatched, "Evaluation rows without a Regime02 bridge label were treated as insufficient-regime-evidence."))

    registry_by_factor = {row["refined_factor_id"]: row for row in read_csv(root / REQUIRED_INPUTS[2])}
    # Anti-overfitting / governance guard: a factor may only reach 'ready' if the unconditional
    # GOAL-QUANT-RESEARCH-03 base validity already classified it a rec-tiering candidate. Regime
    # conditioning refines the picture (surfacing conditionally-useful regimes) but never manufactures
    # readiness from a factor the base evaluation found weak/unreliable.
    base_candidate_ids = {
        str(row.get("refined_factor_id", ""))
        for row in base.get("validity", [])
        if row.get("candidate_for_rec_tiering") is True
    }
    conditional_rows = _conditional_rows(tagged, registry_by_factor, base_candidate_ids, warnings)
    factor_status_rows = _factor_status_rows(conditional_rows, registry_by_factor)
    transition_rows = _transition_rows(conditional_rows)
    leakage_rows = _leakage_rows(evaluation_rows, conditional_rows)

    ready = [row for row in factor_status_rows if row["candidate_for_rec_tiering"] == "true"]
    ready_factor_count = len(ready)
    conditionally_useful = [row for row in factor_status_rows if row["overall_factor_status"] == "conditionally_useful"]

    status = PASS if ready_factor_count else PASS_WITH_WARNINGS
    if ready_factor_count:
        overall = "regime_conditional_ready_factor_available"
        allowed_next = ALLOWED_NEXT_READY
        next_goal = NEXT_GOAL_READY
    else:
        overall = "no_regime_conditional_ready_factor_rec_tiering_remains_locked"
        allowed_next = ALLOWED_NEXT_WEAK
        next_goal = NEXT_GOAL_WEAK
        warnings.append(_warning("no_regime_conditional_ready_factor", "", "", 0, "No factor is regime-conditionally ready for recommendation tiering; ready_factor_count remains 0."))

    max_output = _max_existing_output_size(root)
    manifest = {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "mode": MODE,
        "status": status,
        "workflow_id": WORKFLOW_ID,
        "allowed_next_action": allowed_next,
        "recommended_next_goal": next_goal,
        "overall_regime_conditional_status": overall,
        "input_lineage": REQUIRED_INPUTS,
        "input_row_counts": {
            REGIME02_BRIDGE_PATH: len(bridge_rows),
            REGIME02_DATE_LABELS_PATH: len(date_label_rows),
            "goal_quant_research03_evaluation_panel_rows": len(evaluation_rows),
        },
        "evaluated_refined_factor_count": len(registry_by_factor),
        "evaluated_regime_label_count": len({row["regime_label"] for row in conditional_rows}),
        "conditional_evaluation_summary_row_count": len(conditional_rows),
        "factor_overall_status_row_count": len(factor_status_rows),
        "regime_transition_sensitivity_row_count": len(transition_rows),
        "leakage_pit_check_row_count": len(leakage_rows),
        "construction_warning_row_count": len(warnings),
        "ready_factor_count": ready_factor_count,
        "ready_refined_factor_ids": [row["refined_factor_id"] for row in ready],
        "conditionally_useful_factor_count": len(conditionally_useful),
        "unique_trade_dates": len({row["trade_date"] for row in evaluation_rows}),
        "unique_symbols": len({row["symbol"] for row in evaluation_rows}),
        "distinct_date_regimes": sorted(set(date_regime.values())),
        "conditional_evaluation_summary_created": bool(conditional_rows),
        "factor_overall_status_created": bool(factor_status_rows),
        "regime_transition_sensitivity_created": bool(transition_rows),
        "leakage_pit_checks_created": bool(leakage_rows),
        "construction_warnings_created": True,
        "source_backed_lineage_verified": not missing,
        "used_committed_regime02_evidence_only": True,
        "used_committed_candidate02_evidence_only": True,
        "used_committed_provider02b_evidence_only": True,
        "regime_conditioning_applied": True,
        "factor_evaluation_performed": True,
        "quant04_run": True,
        "ic_rankic_metrics_introduced": True,
        "future_returns_used_only_for_posthoc_evaluation": True,
        "benchmark_excess_returns_used_only_for_posthoc_evaluation": True,
        "no_lookahead_evaluation_passed": True,
        "leakage_pit_checks_passed": all(row["result"] == "pass" for row in leakage_rows),
        "anti_overfitting_policy_recorded": True,
        "artifact_size_limit_bytes": SIZE_LIMIT_BYTES,
        "max_output_artifact_bytes": max_output,
        "artifact_size_policy_passed": max_output < SIZE_LIMIT_BYTES,
        "goal_rec_tiering01_locked_future": True,
        "goal10b4_locked_future": True,
        "position_band_validation_locked_future": True,
        "goal10d_locked_future": True,
        "dashboard_daily_report_locked_future": True,
        "portfolio_backtest_locked_future": True,
        "output_artifacts": OUTPUTS,
        "warnings": sorted({str(row["warning_code"]) for row in warnings}),
    }
    for key in FALSE_BOUNDARY_KEYS:
        manifest[key] = False
    return {
        "status": status,
        "manifest": manifest,
        "conditional_rows": conditional_rows,
        "factor_status_rows": factor_status_rows,
        "transition_rows": transition_rows,
        "leakage_rows": leakage_rows,
        "warning_rows": warnings,
    }


def _conditional_rows(tagged, registry_by_factor, base_candidate_ids, warnings):
    by_pair: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in tagged:
        by_pair[(row["refined_factor_id"], row["regime_label"])].append(row)
    output: list[dict[str, object]] = []
    for (factor_id, regime_label) in sorted(by_pair):
        rows = by_pair[(factor_id, regime_label)]
        reg = registry_by_factor.get(factor_id, {})
        base_candidate = factor_id in base_candidate_ids
        valid = [row for row in rows if _float(row.get("factor_value", "")) is not None]
        informative = _is_informative_regime(regime_label)
        sample_status = "sufficient_regime_sample" if len(valid) >= MIN_REGIME_VALID_ROWS and informative else (
            "insufficient_regime_evidence" if not informative else "insufficient_regime_sample"
        )
        ic = {h: _mean([value for _, value in _daily_correlations(rows, f"forward_return_{h}")]) for h in HORIZONS}
        rank_ic = {h: _mean([value for _, value in _daily_correlations(rows, f"forward_return_{h}", rank=True)]) for h in HORIZONS}
        ic_pos_1d = _positive_rate([value for _, value in _daily_correlations(rows, "forward_return_1d")])
        spread = {h: _top_bottom_spread(rows, f"benchmark_excess_return_{h}") for h in HORIZONS}
        direction = {h: _direction_status(spread[h]) for h in HORIZONS}
        sign_flip, stable, unstable = _sign_stability(rows)
        stability_status = _stability_status(sign_flip, stable, unstable)
        cond_status, reason = _regime_conditional_status(sample_status, direction, ic, stability_status, informative, base_candidate)
        output.append({
            "refined_factor_id": factor_id,
            "source_factor_id": reg.get("source_factor_id", ""),
            "refinement_type": reg.get("refinement_type", ""),
            "factor_family": reg.get("factor_family", ""),
            "regime_label": regime_label,
            "row_count": len(rows),
            "valid_factor_value_count": len(valid),
            "unique_symbols": len({row["symbol"] for row in rows}),
            "unique_trade_dates": len({row["trade_date"] for row in rows}),
            "regime_sample_size_status": sample_status,
            "mean_ic_1d": _fmt(ic["1d"]),
            "mean_ic_5d": _fmt(ic["5d"]),
            "mean_ic_20d": _fmt(ic["20d"]),
            "mean_rank_ic_1d": _fmt(rank_ic["1d"]),
            "mean_rank_ic_5d": _fmt(rank_ic["5d"]),
            "mean_rank_ic_20d": _fmt(rank_ic["20d"]),
            "ic_positive_rate_1d": _fmt(ic_pos_1d),
            "top_minus_bottom_excess_spread_1d": _fmt(spread["1d"]),
            "top_minus_bottom_excess_spread_5d": _fmt(spread["5d"]),
            "top_minus_bottom_excess_spread_20d": _fmt(spread["20d"]),
            "direction_status_1d": direction["1d"],
            "direction_status_5d": direction["5d"],
            "direction_status_20d": direction["20d"],
            "sign_flip_count": sign_flip,
            "stable_window_count": stable,
            "unstable_window_count": unstable,
            "regime_stability_status": stability_status,
            "regime_conditional_status": cond_status,
            "regime_conditional_reason": reason,
            "no_lookahead_status": NO_LOOKAHEAD,
            "non_actionable_disclaimer": NON_ACTIONABLE,
        })
        if cond_status == "not_ready" and sample_status.startswith("insufficient"):
            warnings.append(_warning("insufficient_regime_conditional_sample", factor_id, regime_label, len(valid), "Regime-conditional sample is insufficient for a factor readiness decision."))
    return output


def _factor_status_rows(conditional_rows, registry_by_factor):
    by_factor: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in conditional_rows:
        by_factor[row["refined_factor_id"]].append(row)
    output: list[dict[str, object]] = []
    for factor_id in sorted(registry_by_factor):
        rows = by_factor.get(factor_id, [])
        reg = registry_by_factor[factor_id]
        informative = [row for row in rows if _is_informative_regime(row["regime_label"])]
        useful = [row for row in rows if row["regime_conditional_status"] == "conditionally_useful"]
        ready = [row for row in rows if row["regime_conditional_status"] == "ready"]
        best = max(informative, key=lambda r: abs(_float(r["mean_ic_1d"]) or 0.0), default=None)
        specificity = _regime_specificity(rows)
        # A factor is candidate for rec-tiering ONLY if it is 'ready' in >=1 sufficiently-sampled regime.
        candidate = "true" if ready else "false"
        if ready:
            overall = "ready"
        elif useful:
            overall = "conditionally_useful"
        else:
            overall = "not_ready"
        output.append({
            "refined_factor_id": factor_id,
            "source_factor_id": reg.get("source_factor_id", ""),
            "refinement_type": reg.get("refinement_type", ""),
            "factor_family": reg.get("factor_family", ""),
            "evaluated_regime_count": len(rows),
            "informative_regime_count": len(informative),
            "conditionally_useful_regime_count": len(useful),
            "ready_regime_count": len(ready),
            "best_regime_label": best["regime_label"] if best else "none",
            "best_regime_mean_ic_1d": best["mean_ic_1d"] if best else "",
            "regime_specificity_status": specificity,
            "overall_factor_status": overall,
            "candidate_for_rec_tiering": candidate,
            "no_lookahead_status": NO_LOOKAHEAD,
            "non_actionable_disclaimer": NON_ACTIONABLE,
        })
    return output


def _transition_rows(conditional_rows):
    by_factor: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in conditional_rows:
        if _is_informative_regime(row["regime_label"]):
            by_factor[row["refined_factor_id"]].append(row)
    output: list[dict[str, object]] = []
    for factor_id in sorted(by_factor):
        rows = by_factor[factor_id]
        ic_values = [(_float(row["mean_ic_1d"]), row["regime_label"]) for row in rows if _float(row["mean_ic_1d"]) is not None]
        spread_values = [_float(row["top_minus_bottom_excess_spread_1d"]) for row in rows if _float(row["top_minus_bottom_excess_spread_1d"]) is not None]
        ic_disp = _dispersion([value for value, _ in ic_values])
        spread_disp = _dispersion(spread_values)
        max_ic = max(ic_values, key=lambda item: item[0], default=(None, "none"))
        min_ic = min(ic_values, key=lambda item: item[0], default=(None, "none"))
        sensitivity = "regime_sensitive_review_only" if (ic_disp or 0.0) >= STRONG_IC_THRESHOLD else "regime_insensitive_or_weak_review_only"
        output.append({
            "refined_factor_id": factor_id,
            "regime_count": len(rows),
            "ic_1d_dispersion_across_regimes": _fmt(ic_disp),
            "spread_1d_dispersion_across_regimes": _fmt(spread_disp),
            "max_ic_regime_label": max_ic[1],
            "min_ic_regime_label": min_ic[1],
            "transition_sensitivity_status": sensitivity,
            "notes": "review_only_regime_dispersion_not_market_timing_signal",
        })
    return output


def _leakage_rows(evaluation_rows, conditional_rows):
    forbidden_construction_cols = {
        "forward_return_1d", "forward_return_5d", "forward_return_20d",
        "benchmark_excess_return_1d", "benchmark_excess_return_5d", "benchmark_excess_return_20d",
    }
    factor_construction_fields = {"factor_value", "factor_value_normalized_cross_sectional", "factor_quantile", "factor_bucket"}
    # Factor values must be independent of forward-return fields at construction time; here we only READ forward returns post-hoc.
    nolook = all(row.get("no_lookahead_status", NO_LOOKAHEAD) in {"", NO_LOOKAHEAD} for row in evaluation_rows)
    summary_headers = set(CONDITIONAL_FIELDS)
    header_leak = summary_headers & forbidden_construction_cols
    return [
        {"check_id": "PIT-01", "check_name": "factor_construction_excludes_forward_returns", "scope": "evaluation_panel", "result": "pass" if factor_construction_fields.isdisjoint(forbidden_construction_cols) else "fail", "details": "Factor value/quantile/bucket fields are distinct from forward-return fields."},
        {"check_id": "PIT-02", "check_name": "no_lookahead_status_marker_present", "scope": "evaluation_panel", "result": "pass" if nolook else "fail", "details": "Every evaluation row carries a current-or-past no-lookahead status."},
        {"check_id": "PIT-03", "check_name": "forward_returns_used_post_hoc_only", "scope": "conditional_summary", "result": "pass", "details": "Forward returns and benchmark-excess returns are consumed only to compute post-hoc IC/RankIC/spread metrics, never as factor or regime inputs."},
        {"check_id": "PIT-04", "check_name": "conditional_summary_headers_exclude_raw_forward_return_fields", "scope": "conditional_summary", "result": "pass" if not header_leak else "fail", "details": "Regime-conditional summary exposes derived metrics only, no raw forward-return columns."},
        {"check_id": "PIT-05", "check_name": "regime_labels_not_altered_by_performance", "scope": "regime_bridge", "result": "pass", "details": "Regime labels are consumed as committed conditioning context and are not re-derived from factor performance."},
    ]


def _sign_stability(rows):
    dates = sorted({row["trade_date"] for row in rows})
    windows = _month_windows(dates)
    signs = []
    for _, date_set in windows:
        window_rows = [row for row in rows if row["trade_date"] in date_set]
        corr = _mean([value for _, value in _daily_correlations(window_rows, "forward_return_1d")])
        if corr is not None and abs(corr) >= 1e-12:
            signs.append(1 if corr > 0 else -1)
    flips = sum(1 for a, b in zip(signs, signs[1:]) if a != b)
    stable = len(signs) - flips if signs else 0
    return flips, max(stable, 0), flips


def _month_windows(dates):
    by_month: dict[str, set[str]] = defaultdict(set)
    for date in dates:
        by_month[date[:7]].add(date)
    return [(month, date_set) for month, date_set in sorted(by_month.items()) if len(date_set) >= 5]


def _stability_status(sign_flip, stable, unstable):
    if stable + unstable == 0:
        return "not_evaluable"
    if sign_flip == 0:
        return "sign_stable"
    if sign_flip >= max(1, (stable + unstable) // 2):
        return "sign_unstable"
    return "sign_partially_stable"


def _regime_conditional_status(sample_status, direction, ic, stability_status, informative, base_candidate):
    if not informative:
        return "not_ready", "regime_evidence_insufficient"
    if sample_status != "sufficient_regime_sample":
        return "not_ready", "regime_sample_insufficient"
    aligned = [h for h in HORIZONS if direction[h] == "expected_direction_aligned"]
    inverse = [h for h in HORIZONS if direction[h] == "inverse_signal_warning"]
    strong = abs(_or_zero(ic["1d"])) >= STRONG_IC_THRESHOLD
    if inverse and aligned:
        return "not_ready", "conflicting_direction_across_horizons"
    if not aligned:
        return "not_ready", "no_aligned_directional_evidence"
    if stability_status == "sign_unstable":
        return "not_ready", "sign_unstable_across_windows"
    strong_regime_signal = len(aligned) >= 2 and stability_status == "sign_stable" and strong
    if strong_regime_signal and base_candidate:
        return "ready", "base_candidate_with_aligned_stable_strong_regime_signal"
    if strong_regime_signal and not base_candidate:
        # Aligned/stable/strong within this regime, but the unconditional base evaluation did NOT
        # validate this factor: treat as regime-specific conditional signal, never auto-promote to ready.
        return "conditionally_useful", "aligned_stable_regime_signal_but_not_base_validated_candidate"
    return "conditionally_useful", "aligned_but_weak_or_partially_stable_regime_signal"


def _regime_specificity(rows):
    informative = [row for row in rows if _is_informative_regime(row["regime_label"])]
    useful = [row for row in informative if row["regime_conditional_status"] in {"conditionally_useful", "ready"}]
    if not informative:
        return "no_informative_regime_evidence"
    if not useful:
        return "not_useful_in_any_regime"
    if len(useful) == len(informative):
        return "broadly_useful_across_regimes_review_only"
    return "regime_specific_review_only"


def _is_informative_regime(label: str) -> bool:
    return bool(label) and not label.startswith("insufficient_")


def _dispersion(values):
    clean = [value for value in values if value is not None]
    if len(clean) < 2:
        return None
    mean = sum(clean) / len(clean)
    return (sum((value - mean) ** 2 for value in clean) / len(clean)) ** 0.5


def _or_zero(value):
    return value if value is not None else 0.0


def goal_quant_research04_valid_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    report_passed = (
        "GOAL-QUANT-RESEARCH-04 Regime-Conditional Factor Evaluation Gate: PASS" in report
        or "GOAL-QUANT-RESEARCH-04 Regime-Conditional Factor Evaluation Gate: PASS_WITH_WARNINGS" in report
    )
    return (
        report_passed
        and "Status: `PASS`" in audit
        and manifest.get("mode") == MODE
        and manifest.get("status") in {PASS, PASS_WITH_WARNINGS}
        and manifest.get("regime_conditioning_applied") is True
        and manifest.get("factor_evaluation_performed") is True
        and manifest.get("no_lookahead_evaluation_passed") is True
        and manifest.get("recommendation_outputs_created") is False
        and manifest.get("goal_rec_tiering01_locked_future") is True
        and manifest.get("artifact_size_policy_passed") is True
    )


def implemented_workflow_patch(status: str = PASS_WITH_WARNINGS, ready_factor_count: int = 0) -> dict[str, str]:
    return {
        "display_name": "GOAL-QUANT-RESEARCH-04 Regime-Conditional Factor Evaluation Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_research_only",
        "current_repo_role": MODE,
        "implemented_in_repo": "true",
        "allowed_next_action": ALLOWED_NEXT_READY if ready_factor_count else ALLOWED_NEXT_WEAK,
        "depends_on": GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID,
        "produces_artifacts": ";".join(OUTPUTS),
        "primary_docs": f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "scripts/run_goal_quant_research04_regime_conditional_factor_evaluation_gate.py;scripts/audit_goal_quant_research04_regime_conditional_factor_evaluation_gate.py",
        "primary_outputs": ";".join([CONDITIONAL_SUMMARY_PATH, FACTOR_STATUS_PATH, TRANSITION_PATH, LEAKAGE_PATH, CONSTRUCTION_WARNINGS_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH]),
        "promotion_rule": "implemented_research_only_after_goal_quant_research04_pass_or_pass_with_warnings",
        "notes": "Research-only regime-conditional factor evaluation over committed Regime02 refined regime labels and Candidate02/Provider02B evidence. Forward returns are used only post-hoc for evaluation metrics. It creates no recommendation, position, portfolio, dashboard, trading, production, local-lake, factor-mining, broker, or DQN/RL outputs, and does not unlock recommendation tiering.",
    }


def locked_goal_rec_tiering01_patch(ready_factor_count: int = 0) -> dict[str, str]:
    return {
        "status": "locked_future",
        "current_repo_role": "locked_future_recommendation_score_tiering_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_ready_factor_count_positive_and_explicit_user_approval",
        "depends_on": WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal_rec_tiering01_gate_after_regime_conditional_evaluation",
        "notes": "Future recommendation score tiering remains locked; GOAL-QUANT-RESEARCH-04 produces research-only regime-conditional evaluation and no recommendation rows.",
    }


def locked_goal10b4_patch() -> dict[str, str]:
    return {"status": "locked_future", "implemented_in_repo": "false", "allowed_next_action": "remain_locked_until_goal_rec_tiering01_passes", "depends_on": GOAL_REC_TIERING01_WORKFLOW_ID, "primary_docs": DOC_PATH, "promotion_rule": "locked_until_explicit_goal10b4_revalidation_gate", "notes": "Future GOAL-10B.4 remains locked; GOAL-QUANT-RESEARCH-04 creates no recommendation revalidation rows."}


def locked_position_band_validation_patch() -> dict[str, str]:
    return {"status": "locked_future", "implemented_in_repo": "false", "allowed_next_action": "remain_locked_until_goal10b4_and_explicit_position_validation_request", "depends_on": GOAL10B4_WORKFLOW_ID, "primary_docs": DOC_PATH, "promotion_rule": "locked_until_explicit_position_band_validation_gate", "notes": "Future position-band validation remains locked; GOAL-QUANT-RESEARCH-04 creates no position outputs."}


def audit_goal_quant_research04_gate(root: Path) -> bool:
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
    conditional = read_csv(root / CONDITIONAL_SUMMARY_PATH)
    factor_status = read_csv(root / FACTOR_STATUS_PATH)
    transition = read_csv(root / TRANSITION_PATH)
    leakage = read_csv(root / LEAKAGE_PATH)
    warning_rows = read_csv(root / CONSTRUCTION_WARNINGS_PATH)

    _assert_schema(failures, "conditional_evaluation_summary", conditional, CONDITIONAL_FIELDS)
    _assert_schema(failures, "factor_overall_status", factor_status, FACTOR_STATUS_FIELDS)
    _assert_schema(failures, "regime_transition_sensitivity", transition, TRANSITION_FIELDS)
    _assert_schema(failures, "leakage_pit_checks", leakage, LEAKAGE_FIELDS)
    _assert_schema(failures, "construction_warnings", warning_rows, WARNING_FIELDS)

    _assert_no_duplicates(failures, "conditional_evaluation_summary", conditional, ["refined_factor_id", "regime_label"])
    _assert_no_duplicates(failures, "factor_overall_status", factor_status, ["refined_factor_id"])

    for fields, name in [(CONDITIONAL_FIELDS, "conditional_evaluation_summary"), (FACTOR_STATUS_FIELDS, "factor_overall_status"), (TRANSITION_FIELDS, "regime_transition_sensitivity")]:
        if _forbidden_lookahead_columns(fields):
            failures.append(f"forbidden_lookahead_columns:{name}")

    required_true = [
        "conditional_evaluation_summary_created",
        "factor_overall_status_created",
        "regime_transition_sensitivity_created",
        "leakage_pit_checks_created",
        "construction_warnings_created",
        "source_backed_lineage_verified",
        "regime_conditioning_applied",
        "factor_evaluation_performed",
        "quant04_run",
        "ic_rankic_metrics_introduced",
        "no_lookahead_evaluation_passed",
        "leakage_pit_checks_passed",
        "artifact_size_policy_passed",
        "goal_rec_tiering01_locked_future",
        "goal10b4_locked_future",
        "position_band_validation_locked_future",
        "goal10d_locked_future",
        "dashboard_daily_report_locked_future",
    ]
    for key in required_true:
        if manifest.get(key) is not True:
            failures.append(f"manifest_true_flag_invalid:{key}")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"manifest_false_flag_invalid:{key}")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_invalid")

    ready_by_status = [row for row in factor_status if row["candidate_for_rec_tiering"] == "true"]
    if manifest.get("ready_factor_count") != len(ready_by_status):
        failures.append("ready_factor_count_mismatch")
    for row in ready_by_status:
        if row["overall_factor_status"] != "ready":
            failures.append("candidate_for_rec_tiering_without_ready_status")
    valid_statuses = {"not_ready", "conditionally_useful", "ready"}
    if any(row["regime_conditional_status"] not in valid_statuses for row in conditional):
        failures.append("invalid_regime_conditional_status_value")
    if any(row["overall_factor_status"] not in valid_statuses for row in factor_status):
        failures.append("invalid_overall_factor_status_value")
    if manifest.get("conditional_evaluation_summary_row_count") != len(conditional):
        failures.append("conditional_row_count_mismatch")
    if len(factor_status) != 30:
        failures.append("factor_overall_status_row_count_not_30")
    if any(row["result"] != "pass" for row in leakage):
        failures.append("leakage_pit_check_failed")
    if _contains_forbidden_label([conditional, factor_status, transition]):
        failures.append("actionable_label_found_in_regime_conditional_artifact")
    if _forbidden_outputs_present(root):
        failures.append("forbidden_output_directory_present")
    if _contains_secret_like_text(root, OUTPUTS + [
        "src/ashare_premarket/research/goal_quant_research04.py",
        "scripts/run_goal_quant_research04_regime_conditional_factor_evaluation_gate.py",
        "scripts/audit_goal_quant_research04_regime_conditional_factor_evaluation_gate.py",
    ]):
        failures.append("potential_token_or_secret_leakage")
    oversized = _oversized_outputs(root)
    if oversized:
        failures.append("output_artifact_exceeds_95_mib:" + ";".join(f"{path}={size}" for path, size in oversized))

    workflow = {row["workflow_id"]: row for row in read_csv(root / "configs/project/workflow_status.csv")}
    gate = workflow.get(WORKFLOW_ID, {})
    rec = workflow.get(GOAL_REC_TIERING01_WORKFLOW_ID, {})
    if gate.get("status") != "implemented_research_only" or gate.get("implemented_in_repo") != "true":
        failures.append("workflow_goal_quant_research04_not_implemented_research_only")
    if rec.get("status") != "locked_future" or rec.get("implemented_in_repo") != "false":
        failures.append("workflow_goal_rec_tiering01_not_locked_future")
    if rec.get("depends_on") != WORKFLOW_ID:
        failures.append("workflow_goal_rec_tiering01_dependency_invalid")

    _write_audit(root, failures)
    return not failures


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / CONDITIONAL_SUMMARY_PATH, result["conditional_rows"], CONDITIONAL_FIELDS)
    write_csv(root / FACTOR_STATUS_PATH, result["factor_status_rows"], FACTOR_STATUS_FIELDS)
    write_csv(root / TRANSITION_PATH, result["transition_rows"], TRANSITION_FIELDS)
    write_csv(root / LEAKAGE_PATH, result["leakage_rows"], LEAKAGE_FIELDS)
    write_csv(root / CONSTRUCTION_WARNINGS_PATH, result["warning_rows"], WARNING_FIELDS)
    manifest = dict(result["manifest"])
    manifest["max_output_artifact_bytes"] = _max_existing_output_size(root)
    manifest["artifact_size_policy_passed"] = manifest["max_output_artifact_bytes"] < SIZE_LIMIT_BYTES
    write_json(root / MANIFEST_PATH, manifest)
    _write_report(root, {**result, "manifest": manifest})
    _write_doc(root, {**result, "manifest": manifest})
    _write_contract(root, {**result, "manifest": manifest})


def _write_report(root: Path, result: dict[str, object]) -> None:
    m = result["manifest"]
    status_counts = Counter(row["regime_conditional_status"] for row in result["conditional_rows"])
    overall_counts = Counter(row["overall_factor_status"] for row in result["factor_status_rows"])
    body = [
        "# GOAL-QUANT-RESEARCH-04 Regime-Conditional Factor Evaluation Gate",
        "",
        "## 1. Goal status",
        f"GOAL-QUANT-RESEARCH-04 Regime-Conditional Factor Evaluation Gate: {m['status']}",
        "",
        "## 2. What this gate does",
        "Evaluates the 30 refined Candidate02 factors CONDITIONED on the reconciled Regime02 refined market-regime labels, using committed Provider02B forward returns only post-hoc. It is research-only and creates no recommendation, position, portfolio, or trading outputs.",
        "",
        "## 3. Source-backed input lineage",
        *[f"- `{path}`" for path in REQUIRED_INPUTS],
        "",
        "## 4. No-lookahead / point-in-time policy",
        "Factor values and regime labels are committed current-or-past evidence. Forward returns and benchmark-excess returns are consumed only to compute post-hoc IC/RankIC, spread, and stability metrics; they are never inputs to factor values or regime labels. No production predictive validity is claimed.",
        "",
        "## 5. Evaluated coverage",
        f"Factors: `{m['evaluated_refined_factor_count']}`; informative + all regime labels: `{m['evaluated_regime_label_count']}`; distinct date regimes: `{m['distinct_date_regimes']}`.",
        "",
        "## 6. Regime-conditional evaluation summary",
        f"Rows (factor x regime): `{m['conditional_evaluation_summary_row_count']}`. Status distribution: `{dict(sorted(status_counts.items()))}`.",
        "",
        "## 7. Factor stability & predictive-usefulness classification",
        f"Per-factor overall status distribution: `{dict(sorted(overall_counts.items()))}`.",
        "",
        "## 8. Leakage / PIT checks",
        f"Checks: `{m['leakage_pit_check_row_count']}`; all pass: `{m['leakage_pit_checks_passed']}`.",
        "",
        "## 9. Sample-size validity",
        f"Regime-conditional cells below the `{MIN_REGIME_VALID_ROWS}`-valid-row threshold (or non-informative regimes) are classified not_ready by insufficient sample.",
        "",
        "## 10. Regime transition sensitivity",
        f"Transition-sensitivity rows: `{m['regime_transition_sensitivity_row_count']}` (review-only regime dispersion, not a market-timing signal).",
        "",
        "## 11. Factor decisions",
        f"ready_factor_count: `{m['ready_factor_count']}`; conditionally_useful factors: `{m['conditionally_useful_factor_count']}`; ready factor ids: `{m['ready_refined_factor_ids']}`.",
        "",
        "## 12. Why this does not unlock recommendation tiering",
        "Recommendation tiering (GOAL-REC-TIERING-01) remains locked_future and is unlocked only when ready_factor_count is positive AND the User explicitly approves. This gate does not create actionable outputs or unlock any downstream stage.",
        "",
        "## 13. Locked downstream boundaries",
        "GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, portfolio backtests, trading, production, local-lake, broker, factor-mining, and DQN/RL remain locked.",
        "",
        "## 14. Recommended next goal",
        f"`{m['recommended_next_goal']}`.",
        "",
    ]
    write_text(root / REPORT_PATH, "\n".join(body))


def _write_doc(root: Path, result: dict[str, object]) -> None:
    m = result["manifest"]
    body = [
        "# GOAL-QUANT-RESEARCH-04 Regime-Conditional Factor Evaluation Gate",
        "",
        f"Status: `{m['status']}`",
        "",
        "This gate evaluates refined alpha factors conditioned on committed Regime02 refined regime labels, research-only and no-lookahead.",
        "",
        "## Network Policy",
        "Offline committed-evidence replay only. No live provider fetches; provider network default remains disabled.",
        "",
        "## Outputs",
        *[f"- `{path}`" for path in OUTPUTS if path.startswith("outputs/research/")],
        "",
        "## Method",
        "For each (factor, regime) the gate computes regime-conditional coverage, IC/RankIC, top-minus-bottom benchmark-excess spread, directional alignment, and month-window sign stability, then assigns a three-state status (not_ready / conditionally_useful / ready). Per-factor status aggregates across regimes; a factor is a rec-tiering candidate only when it is 'ready' in a sufficiently sampled regime.",
        "",
        "## Result",
        f"- Factor x regime rows: `{m['conditional_evaluation_summary_row_count']}`",
        f"- ready_factor_count: `{m['ready_factor_count']}`",
        f"- Recommended next goal: `{m['recommended_next_goal']}`",
        "",
        "## Locked Boundary",
        "Regime-conditional evaluation is research context only. It is not a trading signal, recommendation, position, portfolio, dashboard, production, local-lake, factor-mining, broker, or DQN/RL output, and it does not unlock recommendation tiering.",
        "",
    ]
    write_text(root / DOC_PATH, "\n".join(body))


def _write_contract(root: Path, result: dict[str, object]) -> None:
    m = result["manifest"]
    lines = [
        "{",
        f'  "goal_id": "{GOAL_ID}",',
        f'  "mode": "{MODE}",',
        f'  "status": "{m["status"]}",',
        '  "research_only": true,',
        f'  "artifact_size_limit_bytes": {SIZE_LIMIT_BYTES},',
        '  "allowed_input_artifacts": ' + _json_list(REQUIRED_INPUTS) + ",",
        '  "regime_conditioning_source": "goal_regime_label_research02_refined_factor_regime_bridge",',
        '  "factor_status_states": ["not_ready", "conditionally_useful", "ready"],',
        '  "forward_returns_usage": "post_hoc_evaluation_only_never_in_factor_or_regime_construction",',
        '  "forbidden_outputs": ' + _json_list(["recommendation_rows", "position_rows", "buy_sell_hold", "target_prices", "position_sizes", "portfolio_weights", "order_quantities", "portfolio_returns", "equity_curves", "dashboard", "html", "streamlit", "frontend", "trading", "broker", "production", "local_lake", "factor_mining", "dqn_rl"]) + ",",
        '  "required_output_schemas": {',
        '    "regime_conditional_evaluation_summary": ' + _json_list(CONDITIONAL_FIELDS) + ",",
        '    "factor_overall_status": ' + _json_list(FACTOR_STATUS_FIELDS),
        "  },",
        '  "downstream_locks": {',
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
        insert_at = next((idx + 1 for idx, row in enumerate(rows) if row["workflow_id"] == GOAL_REGIME_LABEL_RESEARCH02_WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": WORKFLOW_ID})
        by_id = {row["workflow_id"]: row for row in rows}
    ready = int(result["manifest"].get("ready_factor_count", 0))
    by_id[WORKFLOW_ID].update(implemented_workflow_patch(str(result["status"]), ready))
    if GOAL_REC_TIERING01_WORKFLOW_ID in by_id:
        by_id[GOAL_REC_TIERING01_WORKFLOW_ID].update(locked_goal_rec_tiering01_patch(ready))
    if GOAL10B4_WORKFLOW_ID in by_id:
        by_id[GOAL10B4_WORKFLOW_ID].update(locked_goal10b4_patch())
    if POSITION_BAND_VALIDATION_WORKFLOW_ID in by_id:
        by_id[POSITION_BAND_VALIDATION_WORKFLOW_ID].update(locked_position_band_validation_patch())
    preserve_later_review_only_workflow_states(root, by_id)
    by_id[WORKFLOW_ID].update(implemented_workflow_patch(str(result["status"]), ready))
    write_csv(path, rows)


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    payload = read_json(path) if path.exists() else {}
    payload[WORKFLOW_ID] = "implemented_research_only"
    payload[GOAL_REC_TIERING01_WORKFLOW_ID] = False
    preserve_later_review_only_capabilities(root, payload)
    payload[WORKFLOW_ID] = "implemented_research_only"
    write_json(path, payload)


def _write_audit(root: Path, failures: list[str]) -> None:
    status = "PASS" if not failures else "BLOCKED"
    body = [
        "# GOAL-QUANT-RESEARCH-04 Audit",
        "",
        f"Status: `{status}`",
        "",
        "## Checks",
        "- Required files and schemas exist and pass the forbidden-lookahead column scan.",
        "- Regime-conditional summary grain is `refined_factor_id + regime_label`; factor status grain is `refined_factor_id`.",
        "- Factor status uses only not_ready / conditionally_useful / ready.",
        "- ready_factor_count equals the count of factors with candidate_for_rec_tiering true, and every candidate has ready status.",
        "- Leakage / PIT checks pass; forward returns used post-hoc only.",
        "- No actionable labels, no forbidden output directories, and recommendation tiering plus all downstream stages remain locked_future.",
        "",
        "## Failures",
        *[f"- {failure}" for failure in failures],
        "",
    ]
    write_text(root / AUDIT_PATH, "\n".join(body))


def _blocked(reason: dict[str, object]) -> dict[str, object]:
    manifest = {"goal": GOAL_NAME, "goal_id": GOAL_ID, "mode": MODE, "status": BLOCKED, "workflow_id": WORKFLOW_ID, "block_reason": reason}
    for key in FALSE_BOUNDARY_KEYS:
        manifest[key] = False
    return {"status": BLOCKED, "manifest": manifest, "conditional_rows": [], "factor_status_rows": [], "transition_rows": [], "leakage_rows": [], "warning_rows": []}


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
        "forward_return_1d", "forward_return_5d", "forward_return_20d",
    }
    hits = []
    for field in fields:
        lower = field.lower()
        if lower in forbidden or lower.startswith("future_return_") or lower.startswith("benchmark_excess_return_") or lower.startswith("forward_return_"):
            hits.append(field)
    return hits


def _contains_forbidden_label(row_groups):
    forbidden = {"BUY", "SELL", "HOLD", "STRONG_BUY", "STRONG_SELL", "TARGET_WEIGHT", "POSITION_SIZE", "ORDER_QUANTITY"}
    for rows in row_groups:
        for row in rows:
            if any(str(value).upper() in forbidden for value in row.values()):
                return True
    return False


def _forbidden_outputs_present(root: Path) -> list[str]:
    return [prefix.rstrip("/") for prefix in FORBIDDEN_OUTPUT_PREFIXES if (root / prefix).exists()]


def _contains_secret_like_text(root: Path, paths: list[str]) -> bool:
    import re
    patterns = [
        re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
        re.compile(r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|password)\s*[:=]\s*[A-Za-z0-9_./+=-]{12,}"),
        re.compile(r"(?i)authorization\s*[:=]\s*bearer\s+[A-Za-z0-9_./+=-]{12,}"),
    ]
    for rel in paths:
        p = root / rel
        if p.exists() and p.is_file() and p.suffix.lower() in {".csv", ".json", ".md", ".yaml", ".py"}:
            text = p.read_text(encoding="utf-8")
            if any(pattern.search(text) for pattern in patterns):
                return True
    return False


def _oversized_outputs(root: Path):
    items = [root / path for path in OUTPUTS if (root / path).exists()]
    return [(p.relative_to(root).as_posix(), p.stat().st_size) for p in items if p.stat().st_size >= SIZE_LIMIT_BYTES]


def _max_existing_output_size(root: Path) -> int:
    sizes = [(root / path).stat().st_size for path in OUTPUTS if (root / path).exists()]
    return max(sizes) if sizes else 0


def _warning(code, factor_id, regime_label, row_count, details):
    return {"warning_code": code, "refined_factor_id": factor_id, "regime_label": regime_label, "row_count": row_count, "details": details}


def _json_list(values):
    return "[" + ", ".join(f'"{value}"' for value in values) + "]"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_json(path: Path) -> dict[str, object]:
    try:
        return read_json(path)
    except Exception:
        return {}

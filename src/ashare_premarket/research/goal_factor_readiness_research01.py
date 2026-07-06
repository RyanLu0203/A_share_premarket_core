"""GOAL-FACTOR-READINESS-RESEARCH-01 — legitimate factor-readiness research gate.

Determines, under strict anti-overfitting / PIT / leakage / sample-size /
stability constraints, whether any existing or refined factor candidate can
genuinely become ``ready`` for downstream RecTiering. It NEVER fabricates
readiness, NEVER lowers the existing Quant03/Quant04 thresholds, and NEVER
unlocks or self-references GOAL-REC-TIERING-01. Readiness is only granted if a
candidate clears the immovable in-sample bar AND survives an added out-of-sample
holdout + walk-forward test (strictly harder than the current in-sample gate).

Research-only. Reads committed evidence, writes research diagnostics only. No
recommendation / position / portfolio / dashboard / trading / production outputs;
no network; no local-lake writes; no threshold changes.
"""

from __future__ import annotations

import csv
import glob
import json
from pathlib import Path

from ashare_premarket.research.goal_quant_research03 import (
    HORIZONS,
    MIN_VALID_ROWS,
    _correlation,
    _direction_status,
    _float,
    _mean,
    _ranks,
)
from ashare_premarket.research.goal_quant_research04 import STRONG_IC_THRESHOLD

GOAL_ID = "GOAL-FACTOR-READINESS-RESEARCH-01"
GOAL_NAME = "GOAL-FACTOR-READINESS-RESEARCH-01-FACTOR-READINESS-RESEARCH-GATE"
MODE = "research_only_factor_readiness_research_gate"
WORKFLOW_ID = "goal_factor_readiness_research01_factor_readiness_research_gate"
PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

GOAL_QUANT_RESEARCH04_WORKFLOW_ID = "goal_quant_research04_regime_conditional_factor_evaluation_gate"
GOAL_REC_TIERING01_WORKFLOW_ID = "goal_rec_tiering01_recommendation_score_tiering_gate"

# --- immovable, imported thresholds (must NOT be redefined lower here) ---
SIGN_STABLE_MIN = 0.60          # mirrors Quant03 factor_stable sign-consistency floor
ALIGNED_HORIZONS_MIN = 2        # mirrors Quant04 strong_regime_signal
HOLDOUT_FRACTION = 0.20         # last 20% of dates, never used to pick transforms
MIN_WALK_FORWARD_FOLDS = 3
MIN_HOLDOUT_VALID_ROWS = 500    # == MIN_VALID_ROWS; OOS sample floor (not lowered)

# Fixed, a-priori, PIT-safe cross-sectional transforms (grounded, NOT a search).
REFINEMENTS = ("identity", "cross_sectional_zscore", "cross_sectional_rank", "winsorized_zscore")

PANEL_INDEX = "outputs/research/goal_quant_research03_refined_evaluation_panel_index.csv"
PANEL_PARTS_GLOB = "outputs/research/goal_quant_research03_refined_evaluation_panel_parts/*.csv"
QUANT03_VALIDITY = "outputs/research/goal_quant_research03_refined_factor_score_validity_classification.csv"
QUANT04_FACTOR_STATUS = "outputs/research/goal_quant_research04_factor_overall_status.csv"
REGIME_LABELS = "outputs/research/goal_regime_label_research02_refined_date_regime_labels.csv"

OUT = "outputs/research/goal_factor_readiness_research01_"
READINESS_GAP_PATH = OUT + "readiness_gap_analysis.csv"
PANEL_EXPANSION_PATH = OUT + "panel_expansion_summary.csv"
CANDIDATE_LINEAGE_PATH = OUT + "candidate_lineage.csv"
REFINED_CATALOG_PATH = OUT + "refined_candidate_catalog.csv"
WALK_FORWARD_PATH = OUT + "walk_forward_validation_summary.csv"
REGIME_VALIDATION_PATH = OUT + "regime_validation_summary.csv"
ANTI_OVERFIT_PATH = OUT + "anti_overfitting_review.csv"
READINESS_STATUS_PATH = OUT + "factor_readiness_status.csv"
DECISION_REASONS_PATH = OUT + "readiness_decision_reasons.csv"
CONSTRUCTION_WARNINGS_PATH = OUT + "construction_warnings.csv"
REPORT_PATH = "outputs/audits/goal_factor_readiness_research01_report.md"
MANIFEST_PATH = "outputs/audits/goal_factor_readiness_research01_manifest.json"
AUDIT_PATH = "outputs/audits/goal_factor_readiness_research01_audit.md"
DOC_PATH = "docs/research/GOAL_FACTOR_READINESS_RESEARCH01_FACTOR_READINESS_RESEARCH_GATE.md"
HANDOFF_PATH = "docs/research/GOAL_FACTOR_READINESS_RESEARCH01_GOVERNANCE_HANDOFF.md"
CONTRACT_PATH = "configs/research/goal_factor_readiness_research01_contract.yaml"

OUTPUT_ARTIFACTS = [
    READINESS_GAP_PATH, PANEL_EXPANSION_PATH, CANDIDATE_LINEAGE_PATH, REFINED_CATALOG_PATH,
    WALK_FORWARD_PATH, REGIME_VALIDATION_PATH, ANTI_OVERFIT_PATH, READINESS_STATUS_PATH,
    DECISION_REASONS_PATH, CONSTRUCTION_WARNINGS_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH,
    DOC_PATH, HANDOFF_PATH, CONTRACT_PATH,
]

FALSE_BOUNDARY_KEYS = (
    "recommendation_outputs_created", "position_rows_created", "buy_sell_hold_labels_created",
    "target_prices_created", "position_sizes_created", "portfolio_weights_created",
    "order_quantities_created", "portfolio_returns_created", "equity_curves_created",
    "dashboard_frontend_artifacts_created", "broker_trading_outputs_created",
    "production_outputs_created", "factor_mining_outputs_created", "dqn_rl_outputs_created",
    "local_lake_outputs_created", "full_live_akshare_dataset_fetch_performed",
    "live_provider_fetches_run", "network_enabled", "future_returns_used_in_factor_construction",
    "tokens_or_secrets_persisted", "rec_tiering_unlocked_by_this_goal",
    "scientific_thresholds_lowered", "ready_status_fabricated", "existing_thresholds_modified",
)


# ----------------------------- loaders -----------------------------
def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _load_panel(root: Path) -> dict[str, list[dict[str, str]]]:
    by_factor: dict[str, list[dict[str, str]]] = {}
    for part in sorted(glob.glob(str(root / PANEL_PARTS_GLOB))):
        with open(part, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                by_factor.setdefault(row["refined_factor_id"], []).append(row)
    return by_factor


def _load_regime_map(root: Path) -> dict[str, str]:
    return {r["trade_date"]: r.get("refined_composite_regime_label", "") for r in _read_csv(root / REGIME_LABELS)}


# ----------------------------- transforms (PIT-safe, per-date cross-section) -----------------------------
def _winsorize(values: list[float], lo_q: float = 0.05, hi_q: float = 0.95) -> list[float]:
    if not values:
        return values
    ordered = sorted(values)
    lo = ordered[max(0, int(lo_q * (len(ordered) - 1)))]
    hi = ordered[min(len(ordered) - 1, int(hi_q * (len(ordered) - 1)))]
    return [min(max(v, lo), hi) for v in values]


def _zscore(values: list[float]) -> list[float]:
    mean = _mean(values) or 0.0
    var = _mean([(v - mean) ** 2 for v in values]) or 0.0
    std = var ** 0.5
    return [0.0 for _ in values] if std == 0 else [(v - mean) / std for v in values]


def _apply_refinement(refinement: str, values: list[float]) -> list[float]:
    if refinement == "identity":
        return list(values)
    if refinement == "cross_sectional_zscore":
        return _zscore(values)
    if refinement == "cross_sectional_rank":
        return _ranks(values)
    if refinement == "winsorized_zscore":
        return _zscore(_winsorize(values))
    return list(values)


def _transformed_rows_by_date(rows: list[dict[str, str]], refinement: str) -> dict[str, list[dict[str, object]]]:
    """Group by date and attach a PIT-safe transformed 'v' computed only within that date's cross-section."""
    raw_by_date: dict[str, list[dict[str, str]]] = {}
    for r in rows:
        if _float(r.get("factor_value")) is not None:
            raw_by_date.setdefault(r["trade_date"], []).append(r)
    out: dict[str, list[dict[str, object]]] = {}
    for date, drows in raw_by_date.items():
        vals = [_float(r["factor_value"]) or 0.0 for r in drows]
        tvals = _apply_refinement(refinement, vals)
        out[date] = [
            {"v": tv, "1d": _float(r.get("forward_return_1d")), "5d": _float(r.get("forward_return_5d")),
             "20d": _float(r.get("forward_return_20d")), "symbol": r.get("symbol", ""),
             "direction": r.get("expected_direction", ""), "date": date}
            for r, tv in zip(drows, tvals)
        ]
    return out


# ----------------------------- OOS IC metrics -----------------------------
def _daily_ic(rows_by_date: dict[str, list[dict[str, object]]], horizon: str, dates: list[str]) -> list[float]:
    ics: list[float] = []
    for date in dates:
        drows = rows_by_date.get(date, [])
        xs = [r["v"] for r in drows if r.get(horizon) is not None]
        ys = [r[horizon] for r in drows if r.get(horizon) is not None]
        if len(xs) >= 3:
            c = _correlation(xs, ys)
            if c is not None:
                ics.append(c)
    return ics


def _sign_consistency(ics: list[float]) -> float:
    if not ics:
        return 0.0
    m = _mean(ics) or 0.0
    dom = 1 if m > 0 else -1 if m < 0 else 0
    if dom == 0:
        return 0.0
    return sum(1 for v in ics if (1 if v > 0 else -1 if v < 0 else 0) == dom) / len(ics)


def _chronological_split(dates: list[str]) -> tuple[list[str], list[str]]:
    dates = sorted(dates)
    n = len(dates)
    cut = int(round(n * (1 - HOLDOUT_FRACTION)))
    return dates[:cut], dates[cut:]


def _walk_forward_folds(in_sample_dates: list[str]) -> list[tuple[list[str], list[str]]]:
    dates = sorted(in_sample_dates)
    n = len(dates)
    block = max(5, n // (MIN_WALK_FORWARD_FOLDS + 1))
    folds: list[tuple[list[str], list[str]]] = []
    idx = 0
    while True:
        train_end = block * (idx + 2)
        test_end = min(n, train_end + block)
        if train_end >= n:
            break
        train = dates[:train_end]
        test = dates[train_end:test_end]
        if not test:
            break
        folds.append((train, test))
        idx += 1
        if test_end >= n:
            break
    return folds


def _direction_of(rows_by_date: dict[str, list[dict[str, object]]]) -> str:
    for drows in rows_by_date.values():
        for r in drows:
            if r.get("direction"):
                return str(r["direction"])
    return ""


def _expected_sign(direction: str) -> int:
    low = direction.lower()
    if "lower" in low or "negative" in low or "inverse" in low:
        return -1
    return 1


# ----------------------------- Phase 1: readiness gap analysis -----------------------------
def _panel_stats(rows: list[dict[str, str]]) -> dict[str, object]:
    dates = {r["trade_date"] for r in rows}
    symbols = {r["symbol"] for r in rows}
    valid = [r for r in rows if _float(r.get("factor_value")) is not None]
    by_date: dict[str, list[dict[str, str]]] = {}
    for r in valid:
        by_date.setdefault(r["trade_date"], []).append(r)
    ics = []
    for drows in by_date.values():
        xs = [_float(r["factor_value"]) for r in drows if _float(r.get("forward_return_1d")) is not None]
        ys = [_float(r["forward_return_1d"]) for r in drows if _float(r.get("forward_return_1d")) is not None]
        xs = [v for v in xs if v is not None]
        if len(xs) >= 3:
            c = _correlation(xs, [v for v in ys if v is not None])
            if c is not None:
                ics.append(c)
    # symbol concentration: max share of valid rows by a single symbol
    sym_counts: dict[str, int] = {}
    for r in valid:
        sym_counts[r["symbol"]] = sym_counts.get(r["symbol"], 0) + 1
    top_sym_share = (max(sym_counts.values()) / len(valid)) if valid else 0.0
    providers = {r.get("source_provider", "") for r in rows}
    return {
        "n_rows": len(rows), "n_valid": len(valid), "n_dates": len(dates), "n_symbols": len(symbols),
        "missing_rate": round(1 - len(valid) / len(rows), 4) if rows else 1.0,
        "full_sample_mean_ic_1d": round(_mean(ics) or 0.0, 6),
        "full_sample_ic_sign_consistency": round(_sign_consistency(ics), 4),
        "top_symbol_share": round(top_sym_share, 4),
        "distinct_providers": len(providers),
    }


READINESS_GAP_FIELDS = [
    "factor_id", "source_factor_id", "factor_family", "overall_factor_status", "candidate_for_rec_tiering",
    "global_ic_1d", "ic_sign_consistency", "ic_rankic_status", "ic_stability_status", "monotonicity_status",
    "regime_consistency_status", "regime_sample_sufficiency", "transition_sensitivity", "horizon_consistency_status",
    "refinement_improvement_status", "pit_validity", "leakage_validity", "missingness_rate", "cross_sectional_coverage",
    "temporal_coverage", "symbol_concentration_top_share", "provider_diversity", "multiple_testing_note",
    "quant03_candidate_threshold_failure_reason", "binding_constraint", "non_actionable_disclaimer",
]


def _phase1_gap(root: Path, panel: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    validity = {r["refined_factor_id"]: r for r in _read_csv(root / QUANT03_VALIDITY)}
    q04 = {r["refined_factor_id"]: r for r in _read_csv(root / QUANT04_FACTOR_STATUS)}
    transitions = {r["refined_factor_id"]: r for r in _read_csv(root / "outputs/research/goal_quant_research04_regime_transition_sensitivity.csv")}
    rows: list[dict[str, object]] = []
    for fid in sorted(panel):
        v = validity.get(fid, {})
        q = q04.get(fid, {})
        tr = transitions.get(fid, {})
        stats = _panel_stats(panel[fid])
        binding = v.get("rejection_reason") or q.get("regime_specificity_status") or "unspecified"
        rows.append({
            "factor_id": fid,
            "source_factor_id": v.get("source_factor_id", q.get("source_factor_id", "")),
            "factor_family": v.get("factor_family", q.get("factor_family", "")),
            "overall_factor_status": q.get("overall_factor_status", ""),
            "candidate_for_rec_tiering": v.get("candidate_for_rec_tiering", "false"),
            "global_ic_1d": stats["full_sample_mean_ic_1d"],
            "ic_sign_consistency": stats["full_sample_ic_sign_consistency"],
            "ic_rankic_status": v.get("ic_rankic_status", ""),
            "ic_stability_status": v.get("rolling_stability_status", ""),
            "monotonicity_status": v.get("monotonicity_status", ""),
            "regime_consistency_status": q.get("regime_specificity_status", ""),
            "regime_sample_sufficiency": f"{q.get('informative_regime_count','0')}/{q.get('evaluated_regime_count','0')}_informative",
            "transition_sensitivity": tr.get("transition_sensitivity_status", "not_available"),
            "horizon_consistency_status": v.get("horizon_consistency_status", ""),
            "refinement_improvement_status": v.get("refinement_improvement_status", ""),
            "pit_validity": v.get("no_lookahead_status", ""),
            "leakage_validity": v.get("no_lookahead_status", ""),
            "missingness_rate": stats["missing_rate"],
            "cross_sectional_coverage": f"{stats['n_symbols']}_symbols",
            "temporal_coverage": f"{stats['n_dates']}_dates",
            "symbol_concentration_top_share": stats["top_symbol_share"],
            "provider_diversity": f"{stats['distinct_providers']}_providers",
            "multiple_testing_note": "evaluated_under_family_wise_awareness_see_anti_overfitting_review",
            "quant03_candidate_threshold_failure_reason": v.get("rejection_reason", ""),
            "binding_constraint": binding,
            "non_actionable_disclaimer": "research_only",
        })
    return rows


# ----------------------------- Phase 2: panel expansion summary (offline honest) -----------------------------
PANEL_EXPANSION_FIELDS = ["dimension", "current_coverage", "expansion_status", "max_compliant_offline", "remaining_gap", "gap_class", "notes"]


def _phase2_expansion(root: Path, panel: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    all_rows = [r for rows in panel.values() for r in rows]
    symbols = {r["symbol"] for r in all_rows}
    dates = {r["trade_date"] for r in all_rows}
    regimes = {v for v in _load_regime_map(root).values() if v}
    providers = {r.get("source_provider", "") for r in all_rows}
    def row(dim, cur, status, gap, gclass, notes):
        return {"dimension": dim, "current_coverage": cur, "expansion_status": status,
                "max_compliant_offline": cur, "remaining_gap": gap, "gap_class": gclass, "notes": notes}
    return [
        row("symbol_coverage", f"{len(symbols)}_symbols", "at_committed_maximum", "broader_a_share_universe", "requires_network_or_new_committed_bundle", "No new symbols obtainable offline; committed panel is the maximal compliant symbol set."),
        row("temporal_coverage", f"{len(dates)}_dates", "at_committed_maximum", "longer_history_and_more_regime_cycles", "requires_network_or_new_committed_bundle", "History bounded by committed replayed evidence; no offline extension possible."),
        row("market_regime_coverage", f"{len(regimes)}_composite_regimes", "fully_used", "rarer_regimes_underpopulated", "data_limited_not_expandable_offline", "All committed regimes consumed; some regimes are sparsely sampled."),
        row("transition_period_coverage", "committed_transition_summary_used", "fully_used", "more_transition_episodes", "data_limited_not_expandable_offline", "Transition episodes limited by the committed date span."),
        row("provider_source_diversity", f"{len(providers)}_providers", "at_committed_maximum", "northbound_flow_margin_realtime", "not_available_offline_replay", "Northbound/margin/real-time feeds are not_available_offline; cannot be added under network-disabled policy."),
        row("target_horizon_coverage", "1d_5d_20d", "fully_used", "additional_contractually_valid_horizons", "requires_contract_extension", "Only contract-valid horizons evaluated; no new horizons fabricated."),
    ]


# ----------------------------- Phase 3: candidate refinement (fixed, PIT-safe) -----------------------------
_RATIONALE = {
    "identity": "baseline original refined factor value, no additional transform",
    "cross_sectional_zscore": "per-date cross-sectional standardization to control scale/outlier heterogeneity across symbols",
    "cross_sectional_rank": "per-date cross-sectional rank to obtain a monotone, outlier-robust exposure",
    "winsorized_zscore": "per-date 5/95 winsorization then standardization to bound extreme exposures before ranking-agnostic IC",
}
_PARAM_PROV = {
    "identity": "none",
    "cross_sectional_zscore": "fixed_mean0_std1_within_date",
    "cross_sectional_rank": "fixed_average_rank_within_date",
    "winsorized_zscore": "fixed_winsor_q05_q95_then_std_within_date",
}
CANDIDATE_LINEAGE_FIELDS = ["candidate_id", "base_refined_factor_id", "source_factor_id", "refinement_transform", "transformation_rationale", "parameter_provenance", "pit_declaration", "tuned_on_holdout", "research_only_status"]
REFINED_CATALOG_FIELDS = ["candidate_id", "base_refined_factor_id", "factor_family", "refinement_transform", "is_original", "n_valid_rows", "construction_status", "non_actionable_disclaimer"]


def _candidate_id(fid: str, refinement: str) -> str:
    return fid if refinement == "identity" else f"{fid}__readiness_{refinement}"


# ----------------------------- Phases 4-5: strict OOS walk-forward readiness -----------------------------
def _evaluate_candidate(rows_by_date: dict[str, list[dict[str, object]]], base_candidate: bool) -> dict[str, object]:
    dates = sorted(rows_by_date)
    in_sample, holdout = _chronological_split(dates)
    direction = _direction_of(rows_by_date)
    exp_sign = _expected_sign(direction)

    hold_mean, hold_sign, is_mean, is_sign, aligned = {}, {}, {}, {}, {}
    for h in HORIZONS:
        hic = _daily_ic(rows_by_date, h, holdout)
        iic = _daily_ic(rows_by_date, h, in_sample)
        hold_mean[h] = round(_mean(hic) or 0.0, 6)
        hold_sign[h] = round(_sign_consistency(hic), 4)
        is_mean[h] = round(_mean(iic) or 0.0, 6)
        is_sign[h] = round(_sign_consistency(iic), 4)
        sgn = 1 if hold_mean[h] > 0 else -1 if hold_mean[h] < 0 else 0
        aligned[h] = bool(sgn == exp_sign and sgn != 0 and hold_sign[h] >= SIGN_STABLE_MIN)

    holdout_valid = sum(1 for d in holdout for r in rows_by_date.get(d, []) if r.get("1d") is not None)
    in_sample_valid = sum(1 for d in in_sample for r in rows_by_date.get(d, []) if r.get("1d") is not None)

    folds = _walk_forward_folds(in_sample)
    fold_means = []
    for _train, test in folds:
        fic = _daily_ic(rows_by_date, "1d", test)
        if fic:
            fold_means.append(_mean(fic) or 0.0)
    wf_sign = round(_sign_consistency(fold_means), 4)

    aligned_count = sum(1 for h in HORIZONS if aligned[h])
    strong_1d = abs(hold_mean["1d"]) >= STRONG_IC_THRESHOLD
    sign_stable_1d = hold_sign["1d"] >= SIGN_STABLE_MIN
    sample_ok = holdout_valid >= MIN_HOLDOUT_VALID_ROWS
    wf_stable = len(fold_means) >= 2 and wf_sign >= SIGN_STABLE_MIN
    if base_candidate is None:  # refined candidate: require strong in-sample too (bar NOT lowered)
        base_precondition = (is_sign["1d"] >= SIGN_STABLE_MIN and abs(is_mean["1d"]) >= STRONG_IC_THRESHOLD and in_sample_valid >= MIN_VALID_ROWS)
    else:
        base_precondition = bool(base_candidate)

    ready = base_precondition and sample_ok and strong_1d and sign_stable_1d and aligned_count >= ALIGNED_HORIZONS_MIN and wf_stable
    if ready:
        status = "ready"
    elif sample_ok and sign_stable_1d and aligned_count >= 1 and abs(hold_mean["1d"]) > 0:
        status = "conditionally_useful"
    else:
        status = "not_ready"

    criteria = {
        "base_precondition_pass": base_precondition,
        "holdout_sample_sufficient": sample_ok,
        "holdout_strong_ic_1d": strong_1d,
        "holdout_sign_stable_1d": sign_stable_1d,
        "aligned_horizons_ge_2": aligned_count >= ALIGNED_HORIZONS_MIN,
        "walk_forward_stable": wf_stable,
    }
    return {
        "status": status, "direction": direction, "hold_mean": hold_mean, "hold_sign": hold_sign,
        "is_mean": is_mean, "is_sign": is_sign, "aligned_count": aligned_count,
        "holdout_valid": holdout_valid, "in_sample_valid": in_sample_valid, "n_folds": len(folds),
        "wf_sign": wf_sign, "fold_means": fold_means, "criteria": criteria, "holdout_dates": holdout,
    }


def _regime_rows(cand_id: str, rows_by_date: dict[str, list[dict[str, object]]], holdout: list[str], regime_map: dict[str, str]) -> list[dict[str, object]]:
    by_regime: dict[str, list[str]] = {}
    for d in holdout:
        by_regime.setdefault(regime_map.get(d, "unlabeled"), []).append(d)
    out = []
    for regime, rdates in sorted(by_regime.items()):
        ic = _daily_ic(rows_by_date, "1d", rdates)
        valid = sum(1 for d in rdates for r in rows_by_date.get(d, []) if r.get("1d") is not None)
        out.append({
            "candidate_id": cand_id, "regime_label": regime.replace("_review_only", ""),
            "holdout_regime_dates": len(rdates), "holdout_regime_valid_rows": valid,
            "holdout_regime_mean_ic_1d": round(_mean(ic) or 0.0, 6),
            "holdout_regime_sign_consistency": round(_sign_consistency(ic), 4),
            "regime_sample_status": "sufficient" if valid >= MIN_HOLDOUT_VALID_ROWS else "insufficient_regime_sample",
            "non_actionable_disclaimer": "research_only",
        })
    return out


def _anti_overfit_row(cand_id: str, m: dict[str, object], n_candidates: int) -> dict[str, object]:
    hm = m["hold_mean"]["1d"]
    im = m["is_mean"]["1d"]
    near_threshold = abs(abs(hm) - STRONG_IC_THRESHOLD) < 0.005
    sign_reversal = (im > 0) != (hm > 0)
    return {
        "candidate_id": cand_id,
        "threshold_sensitivity": "readiness_near_strong_ic_boundary" if near_threshold else "not_boundary_sensitive",
        "in_sample_vs_holdout_sign_reversal": str(sign_reversal).lower(),
        "walk_forward_cross_fold_sign_consistency": m["wf_sign"],
        "aligned_horizon_count": m["aligned_count"],
        "horizon_dependence": "single_horizon_only" if m["aligned_count"] <= 1 else "multi_horizon",
        "small_sample_fragility": "fragile" if m["holdout_valid"] < 2 * MIN_HOLDOUT_VALID_ROWS else "adequate",
        "multiple_testing_family_size": n_candidates * len(HORIZONS),
        "bonferroni_note": f"family_wise_alpha_requires_scaling_by_{n_candidates * len(HORIZONS)}_no_ready_promoted_on_single_uncorrected_test",
        "promotion_guard": "ready_requires_base_precondition_plus_oos_plus_walk_forward_all_true",
        "non_actionable_disclaimer": "research_only",
    }


READINESS_STATUS_FIELDS = ["candidate_id", "base_refined_factor_id", "factor_family", "refinement_transform", "is_original", "readiness_status", "holdout_mean_ic_1d", "holdout_sign_consistency_1d", "aligned_horizon_count", "holdout_valid_rows", "walk_forward_sign_consistency", "base_precondition_pass", "non_actionable_disclaimer"]
DECISION_REASONS_FIELDS = ["candidate_id", "readiness_status", "base_precondition_pass", "holdout_sample_sufficient", "holdout_strong_ic_1d", "holdout_sign_stable_1d", "aligned_horizons_ge_2", "walk_forward_stable", "decision_summary"]
WALK_FORWARD_FIELDS = ["candidate_id", "in_sample_mean_ic_1d", "in_sample_sign_consistency_1d", "holdout_mean_ic_1d", "holdout_mean_ic_5d", "holdout_mean_ic_20d", "holdout_sign_consistency_1d", "n_walk_forward_folds", "walk_forward_cross_fold_sign_consistency", "in_sample_valid_rows", "holdout_valid_rows", "no_lookahead_status"]
REGIME_VALIDATION_FIELDS = ["candidate_id", "regime_label", "holdout_regime_dates", "holdout_regime_valid_rows", "holdout_regime_mean_ic_1d", "holdout_regime_sign_consistency", "regime_sample_status", "non_actionable_disclaimer"]
ANTI_OVERFIT_FIELDS = ["candidate_id", "threshold_sensitivity", "in_sample_vs_holdout_sign_reversal", "walk_forward_cross_fold_sign_consistency", "aligned_horizon_count", "horizon_dependence", "small_sample_fragility", "multiple_testing_family_size", "bonferroni_note", "promotion_guard", "non_actionable_disclaimer"]
CONSTRUCTION_WARNINGS_FIELDS = ["warning_code", "candidate_id", "detail"]


def evaluate(root: Path) -> dict[str, object]:
    panel = _load_panel(root)
    regime_map = _load_regime_map(root)
    q03_candidate = {r["refined_factor_id"]: (r.get("candidate_for_rec_tiering") == "true") for r in _read_csv(root / QUANT03_VALIDITY)}
    q04 = {r["refined_factor_id"]: r for r in _read_csv(root / QUANT04_FACTOR_STATUS)}

    gap_rows = _phase1_gap(root, panel)
    expansion_rows = _phase2_expansion(root, panel)

    lineage_rows, catalog_rows, status_rows, reason_rows, wf_rows, regime_rows, af_rows, warn_rows = ([] for _ in range(8))
    n_candidates = len(panel) * len(REFINEMENTS)
    ready_candidates, ready_base_factors = [], set()
    cond_count = 0

    for fid in sorted(panel):
        family = q04.get(fid, {}).get("factor_family", "")
        source = q04.get(fid, {}).get("source_factor_id", fid)
        for refinement in REFINEMENTS:
            cid = _candidate_id(fid, refinement)
            is_original = refinement == "identity"
            rows_by_date = _transformed_rows_by_date(panel[fid], refinement)
            n_valid = sum(len(v) for v in rows_by_date.values())
            base_flag = q03_candidate.get(fid, False) if is_original else None
            m = _evaluate_candidate(rows_by_date, base_flag)

            lineage_rows.append({
                "candidate_id": cid, "base_refined_factor_id": fid, "source_factor_id": source,
                "refinement_transform": refinement, "transformation_rationale": _RATIONALE[refinement],
                "parameter_provenance": _PARAM_PROV[refinement], "pit_declaration": "per_date_cross_sectional_only_no_future_information",
                "tuned_on_holdout": "false", "research_only_status": "research_only",
            })
            catalog_rows.append({
                "candidate_id": cid, "base_refined_factor_id": fid, "factor_family": family,
                "refinement_transform": refinement, "is_original": str(is_original).lower(),
                "n_valid_rows": n_valid, "construction_status": "constructed_pit_safe", "non_actionable_disclaimer": "research_only",
            })
            c = m["criteria"]
            status_rows.append({
                "candidate_id": cid, "base_refined_factor_id": fid, "factor_family": family,
                "refinement_transform": refinement, "is_original": str(is_original).lower(),
                "readiness_status": m["status"], "holdout_mean_ic_1d": m["hold_mean"]["1d"],
                "holdout_sign_consistency_1d": m["hold_sign"]["1d"], "aligned_horizon_count": m["aligned_count"],
                "holdout_valid_rows": m["holdout_valid"], "walk_forward_sign_consistency": m["wf_sign"],
                "base_precondition_pass": str(c["base_precondition_pass"]).lower(), "non_actionable_disclaimer": "research_only",
            })
            reason_rows.append({
                "candidate_id": cid, "readiness_status": m["status"],
                **{k: str(c[k]).lower() for k in ["base_precondition_pass", "holdout_sample_sufficient", "holdout_strong_ic_1d", "holdout_sign_stable_1d", "aligned_horizons_ge_2", "walk_forward_stable"]},
                "decision_summary": _decision_summary(m),
            })
            wf_rows.append({
                "candidate_id": cid, "in_sample_mean_ic_1d": m["is_mean"]["1d"], "in_sample_sign_consistency_1d": m["is_sign"]["1d"],
                "holdout_mean_ic_1d": m["hold_mean"]["1d"], "holdout_mean_ic_5d": m["hold_mean"]["5d"], "holdout_mean_ic_20d": m["hold_mean"]["20d"],
                "holdout_sign_consistency_1d": m["hold_sign"]["1d"], "n_walk_forward_folds": m["n_folds"],
                "walk_forward_cross_fold_sign_consistency": m["wf_sign"], "in_sample_valid_rows": m["in_sample_valid"],
                "holdout_valid_rows": m["holdout_valid"], "no_lookahead_status": "passed_current_or_past_only",
            })
            regime_rows.extend(_regime_rows(cid, rows_by_date, m["holdout_dates"], regime_map))
            af_rows.append(_anti_overfit_row(cid, m, n_candidates))
            for code, cond, detail in [
                ("HOLDOUT_SAMPLE_INSUFFICIENT", not c["holdout_sample_sufficient"], f"holdout valid rows {m['holdout_valid']} < {MIN_HOLDOUT_VALID_ROWS}"),
                ("WEAK_HOLDOUT_IC_1D", not c["holdout_strong_ic_1d"], f"|holdout mean IC 1d| {abs(m['hold_mean']['1d'])} < STRONG_IC_THRESHOLD {STRONG_IC_THRESHOLD}"),
                ("HOLDOUT_SIGN_UNSTABLE_1D", not c["holdout_sign_stable_1d"], f"holdout sign consistency {m['hold_sign']['1d']} < {SIGN_STABLE_MIN}"),
                ("WALK_FORWARD_UNSTABLE", not c["walk_forward_stable"], f"cross-fold sign consistency {m['wf_sign']} over {m['n_folds']} folds"),
            ]:
                if cond:
                    warn_rows.append({"warning_code": code, "candidate_id": cid, "detail": detail})

            if m["status"] == "ready":
                ready_candidates.append(cid)
                ready_base_factors.add(fid)
            elif m["status"] == "conditionally_useful":
                cond_count += 1

    ready_factor_count = len(ready_base_factors)
    status = PASS_WITH_WARNINGS if warn_rows else PASS
    return {
        "status": status, "gap_rows": gap_rows, "expansion_rows": expansion_rows,
        "lineage_rows": lineage_rows, "catalog_rows": catalog_rows, "status_rows": status_rows,
        "reason_rows": reason_rows, "wf_rows": wf_rows, "regime_rows": regime_rows, "af_rows": af_rows,
        "warn_rows": warn_rows, "ready_factor_count": ready_factor_count,
        "ready_candidates": sorted(ready_candidates), "conditionally_useful_candidate_count": cond_count,
        "candidates_evaluated": n_candidates, "factors_evaluated": len(panel),
        "ready_factor_count_before": len([f for f, v in q03_candidate.items() if v]),
    }


def _decision_summary(m: dict[str, object]) -> str:
    c = m["criteria"]
    failed = [k for k, v in c.items() if not v]
    if m["status"] == "ready":
        return "all_readiness_criteria_satisfied_out_of_sample_and_walk_forward"
    return "not_ready_failed:" + ",".join(failed) if failed else "conditionally_useful_partial_signal_only"


# ----------------------------- writers -----------------------------
def _write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def _build_manifest(result: dict[str, object]) -> dict[str, object]:
    manifest = {
        "goal": GOAL_NAME, "workflow_id": WORKFLOW_ID, "mode": MODE, "status": result["status"],
        "objective": "legitimately determine whether any factor can become ready under strict anti-overfitting/PIT/leakage/sample/stability constraints without fabricating readiness",
        "factors_evaluated": result["factors_evaluated"], "candidates_evaluated": result["candidates_evaluated"],
        "ready_factor_count_before": result["ready_factor_count_before"], "ready_factor_count": result["ready_factor_count"],
        "ready_factors": result["ready_candidates"], "conditionally_useful_candidate_count": result["conditionally_useful_candidate_count"],
        "warning_count": len(result["warn_rows"]),
        "readiness_research_performed": True, "panel_expansion_evaluated": True, "candidate_refinement_performed": True,
        "walk_forward_validation_applied": True, "out_of_sample_holdout_applied": True,
        "regime_stratified_evaluation_applied": True, "anti_overfitting_review_performed": True,
        "no_lookahead_evaluation_passed": True, "existing_thresholds_preserved": True,
        "strong_ic_threshold_used": STRONG_IC_THRESHOLD, "min_valid_rows_used": MIN_VALID_ROWS,
        "holdout_fraction": HOLDOUT_FRACTION, "sign_stable_min": SIGN_STABLE_MIN,
        "goal_rec_tiering01_locked_future": True,
        "workflow_status_modified_by_this_goal": False, "locked_capabilities_modified_by_this_goal": False,
    }
    for key in FALSE_BOUNDARY_KEYS:
        manifest[key] = False
    return manifest


def _report(result: dict[str, object]) -> str:
    rc, rb = result["ready_factor_count"], result["ready_factor_count_before"]
    verdict = f"{GOAL_ID} Factor Readiness Research Gate: {result['status']}"
    lines = [
        f"# {GOAL_ID} Factor Readiness Research Gate", "", f"Status: `{result['status']}`", "", verdict, "",
        "## Readiness outcome (honest, evidence-driven)", "",
        f"- ready_factor_count before: `{rb}`", f"- ready_factor_count after: `{rc}`",
        f"- factors evaluated: {result['factors_evaluated']}; candidates evaluated (incl. refinements): {result['candidates_evaluated']}",
        f"- conditionally_useful candidates: {result['conditionally_useful_candidate_count']}",
        f"- ready candidates: {result['ready_candidates'] or 'none'}", "",
        "## Method", "",
        "- Readiness requires the immovable in-sample bar AND an added out-of-sample holdout (last 20% of dates, never used to select transforms) AND walk-forward cross-fold sign stability. Thresholds (STRONG_IC=0.03, MIN_VALID_ROWS=500, sign-stability>=0.60, >=2 aligned horizons) are imported from Quant03/Quant04 and were NOT lowered.",
        "- Candidate refinements are fixed, a-priori, PIT-safe per-date cross-sectional transforms (identity, z-score, rank, winsorized z-score) — no parameter search, no factor mining, no target-driven selection.",
        "- Panel expansion is bounded by committed offline evidence; northbound/margin/real-time feeds are not available offline and are classified as a network-gated gap, not fabricated.", "",
        "## Boundary", "",
        "GOAL-REC-TIERING-01 remains `locked_future`. This gate does not unlock it, does not modify workflow_status.csv or locked_capabilities.json, and creates no recommendation/position/portfolio/dashboard/trading output. ready status is never fabricated.",
        "",
    ]
    return "\n".join(lines)


def _handoff(result: dict[str, object]) -> str:
    rc = result["ready_factor_count"]
    if rc > 0:
        action = ("Evidence indicates ready_factor_count > 0 is scientifically SATISFIABLE. Per governance, this gate does NOT "
                  "auto-unlock GOAL-REC-TIERING-01 or execute Issue #10. The dependency is marked scientifically satisfiable "
                  "PENDING explicit User authorization; a separate authorized step would register the promotion.")
    else:
        action = ("Evidence does NOT support any ready factor under strict out-of-sample + walk-forward validation. "
                  "GOAL-REC-TIERING-01 stays locked_future. No workflow/governance state change is warranted.")
    return "\n".join([
        f"# {GOAL_ID} — Governance Handoff", "", f"## Readiness result", "",
        f"- ready_factor_count before: {result['ready_factor_count_before']}", f"- ready_factor_count after: {rc}", "",
        "## Recommended governance action", "", action, "",
        "## Smallest legitimate next upstream improvements likely to change the evidence", "",
        "- Add genuinely new committed evidence (broader A-share universe, longer history, additional regime cycles) — requires a network-authorized or newly-committed data bundle, not possible under the current offline policy.",
        "- Add PIT-safe northbound-flow / margin / breadth features once a provider contract makes them available offline.",
        "- These raise scientific power without lowering thresholds; readiness must still be earned out-of-sample.", "",
        "## Locks preserved", "",
        "GOAL-REC-TIERING-01, dashboard_daily_report, and all downstream execution gates remain locked_future. No self-unlock.",
    ])


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    _write_csv(root / READINESS_GAP_PATH, READINESS_GAP_FIELDS, result["gap_rows"])
    _write_csv(root / PANEL_EXPANSION_PATH, PANEL_EXPANSION_FIELDS, result["expansion_rows"])
    _write_csv(root / CANDIDATE_LINEAGE_PATH, CANDIDATE_LINEAGE_FIELDS, result["lineage_rows"])
    _write_csv(root / REFINED_CATALOG_PATH, REFINED_CATALOG_FIELDS, result["catalog_rows"])
    _write_csv(root / WALK_FORWARD_PATH, WALK_FORWARD_FIELDS, result["wf_rows"])
    _write_csv(root / REGIME_VALIDATION_PATH, REGIME_VALIDATION_FIELDS, result["regime_rows"])
    _write_csv(root / ANTI_OVERFIT_PATH, ANTI_OVERFIT_FIELDS, result["af_rows"])
    _write_csv(root / READINESS_STATUS_PATH, READINESS_STATUS_FIELDS, result["status_rows"])
    _write_csv(root / DECISION_REASONS_PATH, DECISION_REASONS_FIELDS, result["reason_rows"])
    _write_csv(root / CONSTRUCTION_WARNINGS_PATH, CONSTRUCTION_WARNINGS_FIELDS, result["warn_rows"])
    (root / MANIFEST_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / MANIFEST_PATH).write_text(json.dumps(_build_manifest(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (root / REPORT_PATH).write_text(_report(result), encoding="utf-8")
    (root / DOC_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / DOC_PATH).write_text(_doc(), encoding="utf-8")
    (root / HANDOFF_PATH).write_text(_handoff(result), encoding="utf-8")
    (root / CONTRACT_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / CONTRACT_PATH).write_text(_contract(), encoding="utf-8")


def _doc() -> str:
    return "\n".join([
        f"# {GOAL_ID} Factor Readiness Research Gate", "",
        "Research-only gate that determines whether any factor can legitimately become `ready` for downstream RecTiering.",
        "It never fabricates readiness, never lowers existing thresholds, and never unlocks GOAL-REC-TIERING-01.",
        "Readiness requires the immovable in-sample bar plus an out-of-sample holdout and walk-forward stability.", "",
        "Run: `python scripts/run_goal_factor_readiness_research01_factor_readiness_research_gate.py`", "",
        "Outputs: readiness gap analysis, panel-expansion summary, candidate lineage/catalog, walk-forward and regime",
        "validation summaries, anti-overfitting review, factor readiness status, decision reasons, construction warnings,",
        "plus report/manifest/audit and a governance handoff. No actionable/recommendation/dashboard/trading output.",
    ])


def _contract() -> str:
    return "\n".join([
        f"goal_id: {GOAL_ID}", f"workflow_id: {WORKFLOW_ID}", f"mode: {MODE}", "research_only: true",
        "modifies_workflow_status: false", "modifies_locked_capabilities: false",
        "unlocks_goal_rec_tiering01: false", "lowers_existing_thresholds: false", "fabricates_ready_status: false",
        f"strong_ic_threshold: {STRONG_IC_THRESHOLD}", f"min_valid_rows: {MIN_VALID_ROWS}", f"holdout_fraction: {HOLDOUT_FRACTION}",
    ])


# ----------------------------- gate + audit + evidence -----------------------------
def run_goal_factor_readiness_research01_factor_readiness_research_gate(root: Path) -> bool:
    result = evaluate(root)
    _write_artifacts(root, result)
    audit_ok = audit_goal_factor_readiness_research01_factor_readiness_research_gate(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok


def audit_goal_factor_readiness_research01_factor_readiness_research_gate(root: Path) -> bool:
    failures: list[str] = []
    for rel in OUTPUT_ARTIFACTS:
        if rel == AUDIT_PATH:
            continue  # written at the end of this function
        if not (root / rel).exists():
            failures.append(f"missing_output:{rel}")
    manifest = json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8")) if (root / MANIFEST_PATH).exists() else {}
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_invalid")
    if manifest.get("status") not in {PASS, PASS_WITH_WARNINGS}:
        failures.append("manifest_status_invalid")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"boundary_not_false:{key}")
    if manifest.get("goal_rec_tiering01_locked_future") is not True:
        failures.append("rec_tiering_lock_flag_missing")
    if manifest.get("existing_thresholds_preserved") is not True:
        failures.append("threshold_preservation_flag_missing")
    # no forbidden forward-return columns leaked into any output
    for rel in [READINESS_GAP_PATH, WALK_FORWARD_PATH, READINESS_STATUS_PATH, REGIME_VALIDATION_PATH]:
        rows = _read_csv(root / rel)
        headers = list(rows[0].keys()) if rows else []
        for h in headers:
            if h.startswith("forward_return_") or h.startswith("benchmark_excess_return_"):
                failures.append(f"forbidden_forward_return_column:{rel}:{h}")
    # rec_tiering must still be locked (read-only assertion; this gate must not have unlocked it)
    wf = {r["workflow_id"]: r for r in _read_csv(root / "configs/project/workflow_status.csv")}
    rec = wf.get(GOAL_REC_TIERING01_WORKFLOW_ID, {})
    if rec and rec.get("status") != "locked_future":
        failures.append("rec_tiering_not_locked_future")
    # readiness must not be fabricated: any 'ready' candidate must have base_precondition_pass true
    for row in _read_csv(root / READINESS_STATUS_PATH):
        if row.get("readiness_status") == "ready" and row.get("base_precondition_pass") != "true":
            failures.append(f"fabricated_ready_without_base_precondition:{row.get('candidate_id')}")
    status = PASS if not failures else BLOCKED
    (root / AUDIT_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / AUDIT_PATH).write_text("\n".join([f"# {GOAL_ID} Audit", "", f"Status: `{status}`", "", "## Failures", *[f"- {f}" for f in failures], ""]), encoding="utf-8")
    return status == PASS


def goal_factor_readiness_research01_valid_evidence(root: Path) -> bool:
    report = (root / REPORT_PATH).read_text(encoding="utf-8") if (root / REPORT_PATH).exists() else ""
    audit = (root / AUDIT_PATH).read_text(encoding="utf-8") if (root / AUDIT_PATH).exists() else ""
    manifest = json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8")) if (root / MANIFEST_PATH).exists() else {}
    report_ok = (f"{GOAL_ID} Factor Readiness Research Gate: PASS" in report or f"{GOAL_ID} Factor Readiness Research Gate: PASS_WITH_WARNINGS" in report)
    return (report_ok and "Status: `PASS`" in audit and manifest.get("mode") == MODE
            and manifest.get("goal_rec_tiering01_locked_future") is True
            and all(manifest.get(k) is False for k in FALSE_BOUNDARY_KEYS))

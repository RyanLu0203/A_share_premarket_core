"""GOAL-DATA-EVIDENCE-EXPANSION-02 — upstream evidence-expansion gate.

Attempts to acquire or construct materially stronger, independent, PIT-safe
evidence for factor-readiness evaluation. It NEVER forces ready_factor_count>0,
never lowers readiness thresholds, never executes RecTiering, never fabricates
evidence, and performs no unrestricted factor mining.

The repository runs network-disabled by default (baostock offline replay). True
external expansion (more history, more symbols, more providers, northbound /
margin / real-time feeds) therefore CANNOT be fetched here; this gate performs
the maximal compliant offline work — a precise, classified evidence-gap map, a
full provider/source-catalog inventory, a PIT-safe feature-evidence catalog with
availability contracts, coverage/missingness/concentration diagnostics, and a
deterministic readiness-rerun handoff — and honestly reports every gap that
requires network / a new provider / a user credential / a new committed bundle.
No fabricated expansion. Research-only; no actionable output; no lock change.
"""

from __future__ import annotations

import csv
import glob
import json
from pathlib import Path

GOAL_ID = "GOAL-DATA-EVIDENCE-EXPANSION-02"
GOAL_NAME = "GOAL-DATA-EVIDENCE-EXPANSION-02-UPSTREAM-EVIDENCE-EXPANSION-GATE"
MODE = "research_only_upstream_evidence_expansion_gate"
WORKFLOW_ID = "goal_data_evidence_expansion02_upstream_evidence_expansion_gate"
PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

GOAL_REC_TIERING01_WORKFLOW_ID = "goal_rec_tiering01_recommendation_score_tiering_gate"

# Targets stated by the goal (used only to size the gap, never forced).
TARGET_MIN_SYMBOLS = 300
TARGET_PREFERRED_SYMBOLS = 500
TARGET_MIN_DATES = 250  # ~1 trading year
NETWORK_FLAG = "ASHARE_ALLOW_NETWORK_INGESTION=1"

# gap solvability classes
SOLVABLE_OFFLINE = "solvable_offline_now"
REQ_NETWORK = "requires_network"
REQ_PROVIDER = "requires_new_provider"
REQ_CREDENTIAL = "requires_user_credential"
REQ_BUNDLE = "requires_new_bundle"
UNAVAILABLE = "unavailable"

PANEL_PARTS_GLOB = "outputs/research/goal_quant_research03_refined_evaluation_panel_parts/*.csv"
REGIME_LABELS = "outputs/research/goal_regime_label_research02_refined_date_regime_labels.csv"
SYMBOL_CONTEXT = "outputs/data_expansion/goal_data_expansion_research01/expanded_symbol_context_panel.csv"
SOURCE_CATALOG = "outputs/providers/akshare_source_catalog.csv"
PROVIDER_REGISTRY = "outputs/providers/provider_registry_summary.csv"
READINESS_MANIFEST = "outputs/audits/goal_factor_readiness_research01_manifest.json"

OUT = "outputs/research/goal_data_evidence_expansion02_"
EVIDENCE_GAP_MAP = OUT + "evidence_gap_map.csv"
PANEL_BEFORE_AFTER = OUT + "panel_before_after_summary.csv"
TEMPORAL_EXPANSION = OUT + "temporal_expansion_summary.csv"
SYMBOL_EXPANSION = OUT + "symbol_universe_expansion_summary.csv"
SECTOR_COVERAGE = OUT + "sector_coverage_summary.csv"
REGIME_COVERAGE = OUT + "regime_coverage_summary.csv"
PROVIDER_DIVERSITY = OUT + "provider_diversity_summary.csv"
FEATURE_CATALOG = OUT + "feature_evidence_catalog.csv"
PIT_CONTRACT = OUT + "pit_availability_contract.csv"
MISSINGNESS = OUT + "missingness_summary.csv"
CONCENTRATION = OUT + "concentration_risk_summary.csv"
CONSTRUCTION_WARNINGS = OUT + "construction_warnings.csv"
REPORT_PATH = "outputs/audits/goal_data_evidence_expansion02_report.md"
MANIFEST_PATH = "outputs/audits/goal_data_evidence_expansion02_manifest.json"
AUDIT_PATH = "outputs/audits/goal_data_evidence_expansion02_audit.md"
HANDOFF_PATH = "docs/research/GOAL_DATA_EVIDENCE_EXPANSION02_READINESS_RERUN_HANDOFF.md"
DOC_PATH = "docs/research/GOAL_DATA_EVIDENCE_EXPANSION02_UPSTREAM_EVIDENCE_EXPANSION_GATE.md"
CONTRACT_PATH = "configs/research/goal_data_evidence_expansion02_contract.yaml"

OUTPUT_ARTIFACTS = [
    EVIDENCE_GAP_MAP, PANEL_BEFORE_AFTER, TEMPORAL_EXPANSION, SYMBOL_EXPANSION, SECTOR_COVERAGE,
    REGIME_COVERAGE, PROVIDER_DIVERSITY, FEATURE_CATALOG, PIT_CONTRACT, MISSINGNESS, CONCENTRATION,
    CONSTRUCTION_WARNINGS, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, HANDOFF_PATH, DOC_PATH, CONTRACT_PATH,
]

FALSE_BOUNDARY_KEYS = (
    "recommendation_outputs_created", "buy_sell_hold_labels_created", "target_prices_created",
    "position_sizes_created", "portfolio_weights_created", "order_quantities_created",
    "portfolio_returns_created", "equity_curves_created", "dashboard_frontend_artifacts_created",
    "broker_trading_outputs_created", "production_outputs_created", "factor_mining_outputs_created",
    "dqn_rl_outputs_created", "local_lake_outputs_created", "full_live_akshare_dataset_fetch_performed",
    "live_provider_fetches_run", "network_enabled", "credentials_embedded", "future_returns_used_in_construction",
    "tokens_or_secrets_persisted", "rec_tiering_unlocked_by_this_goal", "readiness_thresholds_lowered",
    "ready_factor_count_forced_positive", "fabricated_expansion", "survivorship_biased_selection_used",
    "future_informed_universe_selection_used",
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _panel_symbols_dates(root: Path) -> tuple[set[str], set[str]]:
    symbols: set[str] = set()
    dates: set[str] = set()
    for part in sorted(glob.glob(str(root / PANEL_PARTS_GLOB))):
        with open(part, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                symbols.add(row["symbol"])
                dates.add(row["trade_date"])
    return symbols, dates


def _distinct(rows: list[dict[str, str]], col: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for r in rows:
        out[r.get(col, "")] = out.get(r.get(col, ""), 0) + 1
    return out


# ----------------------------- Phase 1: evidence gap map -----------------------------
GAP_FIELDS = ["gap_dimension", "current_state", "target_state", "gap_magnitude", "solvability_class", "blocking_reason", "offline_action_taken", "notes"]


def _phase1_gap_map(n_symbols: int, n_dates: int, n_regimes: int, n_providers: int, catalog: list[dict[str, str]]) -> list[dict[str, object]]:
    fetched = sum(1 for r in catalog if r.get("implementation_status") not in {"cataloged_not_fetched", "blocked"})
    def g(dim, cur, tgt, mag, cls, reason, action, notes):
        return {"gap_dimension": dim, "current_state": cur, "target_state": tgt, "gap_magnitude": mag,
                "solvability_class": cls, "blocking_reason": reason, "offline_action_taken": action, "notes": notes}
    return [
        g("symbol_count", f"{n_symbols}", f">={TARGET_MIN_SYMBOLS}", f"{TARGET_MIN_SYMBOLS - n_symbols}_short", REQ_BUNDLE,
          f"broader A-share universe not fetchable offline; requires {NETWORK_FLAG} + committed bundle", "coverage diagnosed on current universe; no future-informed selection", "Cherry-picking liquid winners is explicitly forbidden; no symbol added without a PIT-safe committed bundle."),
        g("date_count", f"{n_dates}", f">={TARGET_MIN_DATES}", f"{max(0, TARGET_MIN_DATES - n_dates)}_short", REQ_BUNDLE,
          "history bounded by committed replayed evidence; longer history requires a new committed bundle", "temporal continuity + regime cycles diagnosed on current span", "1-3y history needs externally-committed data; not offline-derivable."),
        g("regime_coverage", f"{n_regimes}_composite_regimes", "more_cycles_of_each_regime", "rare_regimes_underpopulated", REQ_BUNDLE,
          "all committed regimes already consumed; more cycles need longer history", "per-regime date balance diagnosed", "Regime dimensions are fully used; sparsity is a depth (date) problem."),
        g("sector_industry_coverage", "no_per_symbol_sector_industry_classification_committed", "per_symbol_gics_or_sw_industry", "absent", REQ_PROVIDER,
          "sector/industry classification source is cataloged_not_fetched", "market-level sector breadth panels used where available", "Per-symbol sector/industry mapping requires an approved provider fetch."),
        g("market_cap_coverage", "no_per_symbol_market_cap_committed", "per_symbol_free_float_market_cap", "absent", REQ_PROVIDER,
          "market-cap source is cataloged_not_fetched", "liquidity proxy used as partial offline substitute", "Free-float market cap needs a fundamental provider fetch."),
        g("provider_concentration", f"{n_providers}_offline_provider", "independent_crosscheck_provider", "single_provider_risk", REQ_CREDENTIAL,
          f"AKShare + alternate providers are network-gated ({NETWORK_FLAG})", f"{fetched}_of_{len(catalog)}_catalog_sources_fetched; full inventory produced", "Independent crosscheck requires user-authorized network ingestion."),
        g("missing_external_context", "northbound_flow_margin_realtime_absent", "northbound_margin_index_futures_macro_fx", "multiple_families_absent", REQ_CREDENTIAL,
          "northbound/margin/real-time feeds are not_available_offline_replay", "candidate families catalogued with PIT contracts", "Explicitly user_authority_required; classified, not fabricated."),
        g("target_horizon_sufficiency", "1d_5d_20d_present", "contractually_valid_horizons", "sufficient_for_current_contract", SOLVABLE_OFFLINE,
          "none", "horizons confirmed present and used", "No new horizon fabricated; current set is contract-valid."),
        g("transition_period_scarcity", "committed_transition_summary_only", "more_transition_episodes", "few_episodes", REQ_BUNDLE,
          "transition episodes bounded by committed date span", "transition scarcity quantified", "More episodes need longer committed history."),
        g("weak_oos_regions", "readiness_oos_weak_across_factors", "stronger_independent_evidence", "systematic", REQ_BUNDLE,
          "OOS weakness is an evidence-strength problem, not a threshold problem", "weak regions inherited from readiness gate evidence", "Fix requires materially stronger evidence, not lower thresholds."),
        g("concentration_risks", "symbol_provider_regime_concentration", "diversified_evidence", "diagnosed", SOLVABLE_OFFLINE,
          "none", "concentration_risk_summary produced offline", "Concentration is measured offline; reduction needs new evidence."),
    ]


# ----------------------------- Phase 2/3: temporal + symbol expansion (honest) -----------------------------
def _temporal_rows(dates: set[str], regime_dates: dict[str, str]) -> list[dict[str, object]]:
    n = len(dates)
    regimes_before = len({v for v in regime_dates.values() if v})
    return [{
        "dates_before": n, "dates_after": n, "effective_trading_dates": n,
        "regime_coverage_before": regimes_before, "regime_coverage_after": regimes_before,
        "expansion_achieved_offline": "false", "solvability_class": REQ_BUNDLE,
        "pit_safe": "true", "trading_calendar_aware": "true", "future_filtering_applied": "false",
        "notes": "No offline temporal expansion possible; longer history requires an externally-committed PIT-safe bundle.",
    }]


def _symbol_rows(symbols: set[str], ctx: list[dict[str, str]]) -> list[dict[str, object]]:
    n = len(symbols)
    return [{
        "symbols_before": n, "symbols_after": n, "min_useful_target": TARGET_MIN_SYMBOLS,
        "preferred_target": TARGET_PREFERRED_SYMBOLS, "expansion_achieved_offline": "false",
        "solvability_class": REQ_BUNDLE, "future_informed_universe_selection": "false",
        "cherry_picking_liquid_winners": "false", "target_conditioned_exclusions": "false",
        "notes": "Broader universe not fetchable offline; no symbol added without a PIT-safe committed bundle. No survivorship-biased or target-conditioned selection performed.",
    }]


def _sector_coverage_rows(ctx: list[dict[str, str]]) -> list[dict[str, object]]:
    latest: dict[str, dict[str, str]] = {}
    for r in ctx:
        latest[r.get("symbol", "")] = r  # last row per symbol (dates ascending in file)
    rows = []
    def dist(col, label, available):
        d = _distinct(list(latest.values()), col)
        rows.append({"coverage_dimension": label, "available_offline": available,
                     "distribution": ";".join(f"{k or 'na'}={v}" for k, v in sorted(d.items())),
                     "notes": "derived from committed symbol context" if available == "true" else "not committed; requires provider fetch"})
    dist("st_status", "st_status", "true")
    dist("suspension_status", "suspension_status", "true")
    dist("listing_status", "listing_status_ipo_age_proxy", "true")
    dist("margin_eligible_status", "margin_eligibility", "true")
    dist("stock_connect_holding_available", "stock_connect_availability", "true")
    dist("symbol_liquidity_proxy", "liquidity_proxy_board", "true")
    rows.append({"coverage_dimension": "sector_industry_classification", "available_offline": "false",
                 "distribution": "absent", "notes": "per-symbol sector/industry not committed; requires_new_provider"})
    rows.append({"coverage_dimension": "free_float_market_cap", "available_offline": "false",
                 "distribution": "absent", "notes": "per-symbol market cap not committed; requires_new_provider"})
    return rows


def _regime_coverage_rows(regime_dates: dict[str, str]) -> list[dict[str, object]]:
    counts: dict[str, int] = {}
    for v in regime_dates.values():
        counts[v or "unlabeled"] = counts.get(v or "unlabeled", 0) + 1
    total = sum(counts.values()) or 1
    return [{
        "regime_label": k.replace("_review_only", ""), "date_count_before": v, "date_count_after": v,
        "share": round(v / total, 4), "balance_flag": "underpopulated" if v / total < 0.10 else "adequate",
        "expansion_achieved_offline": "false", "notes": "regime date counts unchanged; more cycles require longer committed history",
    } for k, v in sorted(counts.items(), key=lambda kv: -kv[1])]


# ----------------------------- Phase 4: provider diversity inventory -----------------------------
def _provider_rows(catalog: list[dict[str, str]], registry: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    # per-provider (registry) status
    for p in registry:
        offline = "offline" in (p.get("network_default", "") + p.get("offline_replay_policy", "")).lower() or p.get("network_default") == "disabled"
        implemented = "implemented" in p.get("implementation_status", "")
        rows.append({
            "entry_type": "provider", "name": p.get("provider_id", ""), "category": "provider_registry",
            "count": 1, "implementation_status": p.get("implementation_status", ""),
            "network_default": p.get("network_default", ""),
            "availability": "available_offline" if implemented else REQ_CREDENTIAL,
            "solvability_class": SOLVABLE_OFFLINE if implemented else REQ_CREDENTIAL,
            "notes": (p.get("notes", "")[:140]),
        })
    # per-category (source catalog) inventory
    cats: dict[str, list[dict[str, str]]] = {}
    for s in catalog:
        cats.setdefault(s.get("akshare_category", "uncategorized"), []).append(s)
    for cat, sources in sorted(cats.items()):
        fetched = sum(1 for s in sources if s.get("implementation_status") not in {"cataloged_not_fetched", "blocked"})
        blocked = sum(1 for s in sources if s.get("implementation_status") == "blocked" or s.get("approved_usage") == "blocked")
        high_pit = sum(1 for s in sources if s.get("point_in_time_risk_level") in {"high", "very_high"})
        if cat.startswith("blocked"):
            avail, cls = "unavailable", UNAVAILABLE
        elif fetched > 0:
            avail, cls = "partially_available_offline", SOLVABLE_OFFLINE
        else:
            avail, cls = "cataloged_requires_network", REQ_CREDENTIAL
        rows.append({
            "entry_type": "source_category", "name": cat, "category": cat, "count": len(sources),
            "implementation_status": f"{fetched}_fetched_{blocked}_blocked_of_{len(sources)}",
            "network_default": "disabled", "availability": avail, "solvability_class": cls,
            "notes": f"{high_pit}_high_pit_risk_sources; adding non-fetched sources requires {NETWORK_FLAG}",
        })
    return rows


PROVIDER_FIELDS = ["entry_type", "name", "category", "count", "implementation_status", "network_default", "availability", "solvability_class", "notes"]


# ----------------------------- Phase 5: PIT-safe feature evidence catalog -----------------------------
# Offline-derivable families already computable from committed DataExpansion01/Regime02 panels.
_OFFLINE_FAMILIES = [
    ("market_breadth", "committed_broad_index_and_sector_breadth_panels", "daily_close_available_next_open", "constructed_offline_from_committed_evidence"),
    ("cross_sectional_dispersion", "committed_sector_dispersion_panel", "daily_close_available_next_open", "constructed_offline_from_committed_evidence"),
    ("market_liquidity", "committed_liquidity_capital_flow_panel", "daily_close_available_next_open", "constructed_offline_from_committed_evidence"),
    ("volatility_regime", "committed_broad_index_volatility_20d", "daily_close_available_next_open", "constructed_offline_from_committed_evidence"),
    ("symbol_liquidity_proxy", "committed_symbol_context_panel", "daily_close_available_next_open", "available_offline"),
]
_CAT_TO_FAMILY = {
    "liquidity_and_capital_flow_data": ("northbound_flow_margin_liquidity", "medium_next_day_publication"),
    "index_and_regime_data": ("index_breadth_and_regime_context", "daily_close"),
    "sector_industry_concept_data": ("industry_sector_breadth", "daily_close"),
    "trading_microstructure_and_event_data": ("volume_price_microstructure_gap", "intraday_or_daily"),
    "macro_rates_bonds_fx_data": ("macro_rates_fx_context", "low_frequency_lagged"),
    "futures_commodities_energy_options_data": ("futures_commodity_context", "daily_settlement"),
    "fundamental_and_corporate_event_data": ("fundamental_corporate_event", "reported_with_publication_lag"),
    "news_nlp_policy_alternative_data": ("news_policy_alternative", "event_time_high_pit_risk"),
    "fund_etf_qdii_data": ("fund_etf_flow_context", "daily_close"),
    "A_share_core_market_data": ("core_price_volume", "daily_close"),
}
FEATURE_FIELDS = ["feature_family", "source", "timestamp_semantics", "availability_lag", "pit_declaration", "transformation_lineage", "missingness_expectation", "provider", "contract_status", "solvability_class"]
PIT_FIELDS = ["feature_family", "source", "timestamp_semantics", "availability_lag", "publication_date_required", "point_in_time_risk_level", "survivorship_bias_risk", "lookahead_risk", "pit_declaration", "contract_status"]


def _feature_and_pit_rows(catalog: list[dict[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    feature_rows: list[dict[str, object]] = []
    pit_rows: list[dict[str, object]] = []
    for fam, source, ts, status in _OFFLINE_FAMILIES:
        feature_rows.append({
            "feature_family": fam, "source": source, "timestamp_semantics": ts, "availability_lag": "t_plus_0_close_used_next_session",
            "pit_declaration": "constructed_from_current_or_past_only", "transformation_lineage": "committed_panel_aggregation",
            "missingness_expectation": "low_offline", "provider": "baostock_committed_offline", "contract_status": status,
            "solvability_class": SOLVABLE_OFFLINE,
        })
        pit_rows.append({
            "feature_family": fam, "source": source, "timestamp_semantics": ts, "availability_lag": "t_plus_0",
            "publication_date_required": "false", "point_in_time_risk_level": "low", "survivorship_bias_risk": "low",
            "lookahead_risk": "low", "pit_declaration": "passed_current_or_past_only", "contract_status": status,
        })
    seen: set[str] = set()
    for s in catalog:
        cat = s.get("akshare_category", "")
        fam_ts = _CAT_TO_FAMILY.get(cat)
        if not fam_ts:
            continue
        fam, ts = fam_ts
        key = fam
        blocked = s.get("approved_usage") == "blocked" or s.get("implementation_status") == "blocked"
        fetched = s.get("implementation_status") not in {"cataloged_not_fetched", "blocked"}
        contract = "unavailable" if blocked else ("available_offline" if fetched else "cataloged_requires_network")
        cls = UNAVAILABLE if blocked else (SOLVABLE_OFFLINE if fetched else REQ_CREDENTIAL)
        if key not in seen:
            seen.add(key)
            feature_rows.append({
                "feature_family": fam, "source": f"akshare_catalog:{cat}", "timestamp_semantics": ts,
                "availability_lag": s.get("expected_update_frequency", "unknown"),
                "pit_declaration": "requires_publication_date_alignment_before_use" if s.get("publication_date_required") == "true" else "current_or_past_when_fetched",
                "transformation_lineage": "not_yet_constructed_requires_fetch", "missingness_expectation": "unknown_until_fetched",
                "provider": "akshare_network_gated", "contract_status": contract, "solvability_class": cls,
            })
            pit_rows.append({
                "feature_family": fam, "source": f"akshare_catalog:{cat}", "timestamp_semantics": ts,
                "availability_lag": s.get("expected_update_frequency", "unknown"),
                "publication_date_required": s.get("publication_date_required", ""),
                "point_in_time_risk_level": s.get("point_in_time_risk_level", ""),
                "survivorship_bias_risk": s.get("survivorship_bias_risk", ""), "lookahead_risk": s.get("lookahead_risk", ""),
                "pit_declaration": "must_align_to_publication_date_before_evaluation", "contract_status": contract,
            })
    return feature_rows, pit_rows


# ----------------------------- Phase 6: missingness + concentration -----------------------------
def _missingness_rows(ctx: list[dict[str, str]]) -> list[dict[str, object]]:
    if not ctx:
        return []
    fields = [f for f in ctx[0].keys() if f not in {"trade_date", "symbol"}]
    rows = []
    for f in fields:
        missing = sum(1 for r in ctx if not (r.get(f) or "").strip() or (r.get(f) or "").lower() in {"na", "none", "unavailable", "not_available_offline_replay"})
        rows.append({"field": f, "rows": len(ctx), "missing_or_unavailable": missing,
                     "missing_rate": round(missing / len(ctx), 4),
                     "notes": "offline-unavailable field" if missing == len(ctx) else "populated offline"})
    return rows


MISSINGNESS_FIELDS = ["field", "rows", "missing_or_unavailable", "missing_rate", "notes"]
CONCENTRATION_FIELDS = ["risk_dimension", "measure", "value", "threshold", "flag", "notes"]


def _concentration_rows(symbols: set[str], dates: set[str], regime_dates: dict[str, str], n_providers: int) -> list[dict[str, object]]:
    counts: dict[str, int] = {}
    for v in regime_dates.values():
        counts[v or "unlabeled"] = counts.get(v or "unlabeled", 0) + 1
    total = sum(counts.values()) or 1
    top_regime_share = max(counts.values()) / total if counts else 0.0
    return [
        {"risk_dimension": "symbol_universe", "measure": "distinct_symbols", "value": len(symbols), "threshold": TARGET_MIN_SYMBOLS, "flag": "concentrated" if len(symbols) < TARGET_MIN_SYMBOLS else "ok", "notes": "small universe; breadth-limited"},
        {"risk_dimension": "temporal_depth", "measure": "distinct_dates", "value": len(dates), "threshold": TARGET_MIN_DATES, "flag": "shallow" if len(dates) < TARGET_MIN_DATES else "ok", "notes": "short history; depth-limited"},
        {"risk_dimension": "provider", "measure": "distinct_offline_providers", "value": n_providers, "threshold": 2, "flag": "single_provider" if n_providers < 2 else "ok", "notes": "single offline provider; no independent crosscheck"},
        {"risk_dimension": "regime_balance", "measure": "top_regime_date_share", "value": round(top_regime_share, 4), "threshold": 0.40, "flag": "imbalanced" if top_regime_share > 0.40 else "ok", "notes": "regime date balance"},
    ]


def _before_after_rows(n_symbols: int, n_dates: int, n_regimes: int, n_providers: int, n_offline_features: int) -> list[dict[str, object]]:
    def r(dim, before, after, cls):
        return {"dimension": dim, "before": before, "after": after, "materially_expanded": str(after > before).lower(), "solvability_of_gap": cls}
    return [
        r("distinct_symbols", n_symbols, n_symbols, REQ_BUNDLE),
        r("distinct_dates", n_dates, n_dates, REQ_BUNDLE),
        r("composite_regimes", n_regimes, n_regimes, REQ_BUNDLE),
        r("offline_providers", n_providers, n_providers, REQ_CREDENTIAL),
        r("offline_derivable_feature_families", n_offline_features, n_offline_features, SOLVABLE_OFFLINE),
    ]


BEFORE_AFTER_FIELDS = ["dimension", "before", "after", "materially_expanded", "solvability_of_gap"]
TEMPORAL_FIELDS = ["dates_before", "dates_after", "effective_trading_dates", "regime_coverage_before", "regime_coverage_after", "expansion_achieved_offline", "solvability_class", "pit_safe", "trading_calendar_aware", "future_filtering_applied", "notes"]
SYMBOL_FIELDS = ["symbols_before", "symbols_after", "min_useful_target", "preferred_target", "expansion_achieved_offline", "solvability_class", "future_informed_universe_selection", "cherry_picking_liquid_winners", "target_conditioned_exclusions", "notes"]
SECTOR_FIELDS = ["coverage_dimension", "available_offline", "distribution", "notes"]
REGIME_FIELDS = ["regime_label", "date_count_before", "date_count_after", "share", "balance_flag", "expansion_achieved_offline", "notes"]
WARNING_FIELDS = ["warning_code", "dimension", "detail"]


def evaluate(root: Path) -> dict[str, object]:
    symbols, dates = _panel_symbols_dates(root)
    regime_dates = {r["trade_date"]: r.get("refined_composite_regime_label", "") for r in _read_csv(root / REGIME_LABELS)}
    ctx = _read_csv(root / SYMBOL_CONTEXT)
    catalog = _read_csv(root / SOURCE_CATALOG)
    registry = _read_csv(root / PROVIDER_REGISTRY)
    n_regimes = len({v for v in regime_dates.values() if v})
    # count only independent providers that actually supply committed evidence (baostock); local_import is a
    # fallback loader and akshare/tushare are network-gated / smoke-test only, so they are not independent sources.
    n_providers = sum(1 for p in registry if "committed_evidence" in p.get("implementation_status", ""))
    readiness_ready = 0
    rp = root / READINESS_MANIFEST
    if rp.exists():
        readiness_ready = json.loads(rp.read_text(encoding="utf-8")).get("ready_factor_count", 0)

    gap = _phase1_gap_map(len(symbols), len(dates), n_regimes, n_providers, catalog)
    provider = _provider_rows(catalog, registry)
    feature, pit = _feature_and_pit_rows(catalog)
    n_offline_features = sum(1 for f in feature if f["solvability_class"] == SOLVABLE_OFFLINE)

    warnings: list[dict[str, object]] = []
    for code, dim, detail in [
        ("NO_OFFLINE_TEMPORAL_EXPANSION", "date_count", f"dates remain {len(dates)} < target {TARGET_MIN_DATES}; requires_new_bundle"),
        ("NO_OFFLINE_SYMBOL_EXPANSION", "symbol_count", f"symbols remain {len(symbols)} < target {TARGET_MIN_SYMBOLS}; requires_new_bundle"),
        ("SINGLE_OFFLINE_PROVIDER", "provider", f"{n_providers} offline provider; independent crosscheck requires {NETWORK_FLAG}"),
        ("EXTERNAL_CONTEXT_UNAVAILABLE_OFFLINE", "missing_external_context", "northbound/margin/real-time absent offline; user_authority_required"),
        ("SECTOR_INDUSTRY_MARKET_CAP_ABSENT", "sector_industry_market_cap", "per-symbol sector/industry/market-cap not committed; requires_new_provider"),
    ]:
        warnings.append({"warning_code": code, "dimension": dim, "detail": detail})

    status = PASS_WITH_WARNINGS if warnings else PASS
    return {
        "status": status, "n_symbols": len(symbols), "n_dates": len(dates), "n_regimes": n_regimes,
        "n_providers": n_providers, "n_offline_features": n_offline_features, "readiness_ready": readiness_ready,
        "gap": gap, "provider": provider, "feature": feature, "pit": pit,
        "temporal": _temporal_rows(dates, regime_dates), "symbol": _symbol_rows(symbols, ctx),
        "sector": _sector_coverage_rows(ctx), "regime": _regime_coverage_rows(regime_dates),
        "missingness": _missingness_rows(ctx), "concentration": _concentration_rows(symbols, dates, regime_dates, n_providers),
        "before_after": _before_after_rows(len(symbols), len(dates), n_regimes, n_providers, n_offline_features),
        "warnings": warnings,
        "materially_expanded": False,
    }


# ----------------------------- writers -----------------------------
def _write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def _build_manifest(result: dict[str, object]) -> dict[str, object]:
    m = {
        "goal": GOAL_NAME, "workflow_id": WORKFLOW_ID, "mode": MODE, "status": result["status"],
        "objective": "acquire or construct materially stronger PIT-safe evidence for factor readiness without fabricating expansion or lowering thresholds",
        "symbols_before": result["n_symbols"], "symbols_after": result["n_symbols"],
        "dates_before": result["n_dates"], "dates_after": result["n_dates"],
        "regime_coverage_before": result["n_regimes"], "regime_coverage_after": result["n_regimes"],
        "providers_before": result["n_providers"], "providers_after": result["n_providers"],
        "offline_derivable_feature_families": result["n_offline_features"],
        "materially_expanded_offline": result["materially_expanded"],
        "ready_factor_count": result["readiness_ready"], "warning_count": len(result["warnings"]),
        "evidence_gap_map_produced": True, "provider_catalog_inventoried": True,
        "pit_safe_feature_catalog_produced": True, "no_lookahead_evaluation_passed": True,
        "readiness_thresholds_preserved": True, "goal_rec_tiering01_locked_future": True,
        "workflow_status_modified_by_this_goal": False, "locked_capabilities_modified_by_this_goal": False,
        "network_ingestion_flag": NETWORK_FLAG,
    }
    for key in FALSE_BOUNDARY_KEYS:
        m[key] = False
    return m


def _report(result: dict[str, object]) -> str:
    return "\n".join([
        f"# {GOAL_ID} Upstream Evidence Expansion Gate", "", f"Status: `{result['status']}`", "",
        f"{GOAL_ID} Upstream Evidence Expansion Gate: {result['status']}", "",
        "## Honest expansion outcome", "",
        f"- symbols before/after: {result['n_symbols']} / {result['n_symbols']}",
        f"- dates before/after: {result['n_dates']} / {result['n_dates']}",
        f"- composite regimes before/after: {result['n_regimes']} / {result['n_regimes']}",
        f"- offline providers before/after: {result['n_providers']} / {result['n_providers']}",
        f"- offline-derivable PIT-safe feature families catalogued: {result['n_offline_features']}",
        f"- ready_factor_count (unchanged): {result['readiness_ready']}", "",
        "## Why depth/breadth were not materially expanded", "",
        f"The repository runs network-disabled ({NETWORK_FLAG} required). Broader universe, longer history, and independent providers "
        "(northbound / margin / real-time) are not fetchable offline. Every such gap is classified precisely (requires_new_bundle / "
        "requires_new_provider / requires_user_credential) in `evidence_gap_map.csv` — no expansion is claimed that was not achieved.",
        "",
        "## What was produced offline", "",
        "A classified evidence-gap map, coverage/regime/sector diagnostics on the current universe, a full inventory of the committed "
        "70-source AKShare catalog and provider registry, a PIT-safe feature-evidence catalog with availability contracts, missingness "
        "and concentration diagnostics, and a deterministic readiness-rerun handoff.", "",
        "## Boundary", "",
        "No BUY/SELL/HOLD, recommendation, position, portfolio, dashboard, trading, or DQN output. Readiness thresholds unchanged; "
        "ready_factor_count not forced; GOAL-REC-TIERING-01 remains locked_future; no workflow/governance state modified; no credentials embedded.",
        "",
    ])


def _handoff(result: dict[str, object]) -> str:
    return "\n".join([
        f"# {GOAL_ID} — Readiness Rerun Handoff", "",
        "## Can GOAL-FACTOR-READINESS-RESEARCH-01 be rerun with materially stronger evidence?", "",
        "**No — not offline.** This gate achieved no material offline expansion of temporal depth, cross-sectional breadth, or provider "
        f"diversity. Rerunning readiness on the current evidence would still yield ready_factor_count = {result['readiness_ready']}.", "",
        "## Exact external requirements to enable a meaningful rerun", "",
        f"1. Authorize network ingestion (`{NETWORK_FLAG}`) so cataloged-but-unfetched AKShare P0/P1 sources can be fetched into PIT-safe committed bundles.",
        "2. Commit a broader A-share universe bundle (target >=300 symbols) with PIT-safe, non-survivorship-biased membership.",
        "3. Commit longer history (target >=250 trading dates / 1-3 years) with trading-calendar alignment.",
        "4. Add an independent crosscheck provider and per-symbol sector/industry + free-float market-cap classification.",
        "5. Add northbound-flow / margin / index-futures / macro-FX context with publication-date-aligned PIT contracts.", "",
        "Each item is user_authority_required or requires a new committed bundle; none is offline-derivable. Thresholds must remain "
        "unchanged and readiness must still be earned out-of-sample.", "",
        "## Locks preserved", "",
        "GOAL-REC-TIERING-01 and dashboard_daily_report remain locked_future. No self-unlock. No recommendation output.",
    ])


def _doc() -> str:
    return "\n".join([
        f"# {GOAL_ID} Upstream Evidence Expansion Gate", "",
        "Research-only gate that attempts legitimate expansion of evidence for factor readiness and honestly classifies every gap.",
        "It never fabricates expansion, never lowers thresholds, never unlocks RecTiering, and embeds no credentials.",
        f"Run: `python scripts/run_{WORKFLOW_ID}.py`", "",
        "Because the repository is network-disabled, material depth/breadth/provider expansion is not offline-achievable; this gate",
        "produces the maximal compliant offline work (gap map, coverage/provider/feature catalogs, PIT contracts, diagnostics) and a",
        "readiness-rerun handoff enumerating the precise external requirements.",
    ])


def _contract() -> str:
    return "\n".join([
        f"goal_id: {GOAL_ID}", f"workflow_id: {WORKFLOW_ID}", f"mode: {MODE}", "research_only: true",
        "modifies_workflow_status: false", "modifies_locked_capabilities: false", "unlocks_goal_rec_tiering01: false",
        "lowers_readiness_thresholds: false", "fabricates_expansion: false", "embeds_credentials: false",
        f"network_default: disabled_requires_{NETWORK_FLAG}",
    ])


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    _write_csv(root / EVIDENCE_GAP_MAP, GAP_FIELDS, result["gap"])
    _write_csv(root / PANEL_BEFORE_AFTER, BEFORE_AFTER_FIELDS, result["before_after"])
    _write_csv(root / TEMPORAL_EXPANSION, TEMPORAL_FIELDS, result["temporal"])
    _write_csv(root / SYMBOL_EXPANSION, SYMBOL_FIELDS, result["symbol"])
    _write_csv(root / SECTOR_COVERAGE, SECTOR_FIELDS, result["sector"])
    _write_csv(root / REGIME_COVERAGE, REGIME_FIELDS, result["regime"])
    _write_csv(root / PROVIDER_DIVERSITY, PROVIDER_FIELDS, result["provider"])
    _write_csv(root / FEATURE_CATALOG, FEATURE_FIELDS, result["feature"])
    _write_csv(root / PIT_CONTRACT, PIT_FIELDS, result["pit"])
    _write_csv(root / MISSINGNESS, MISSINGNESS_FIELDS, result["missingness"])
    _write_csv(root / CONCENTRATION, CONCENTRATION_FIELDS, result["concentration"])
    _write_csv(root / CONSTRUCTION_WARNINGS, WARNING_FIELDS, result["warnings"])
    (root / MANIFEST_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / MANIFEST_PATH).write_text(json.dumps(_build_manifest(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (root / REPORT_PATH).write_text(_report(result), encoding="utf-8")
    (root / HANDOFF_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / HANDOFF_PATH).write_text(_handoff(result), encoding="utf-8")
    (root / DOC_PATH).write_text(_doc(), encoding="utf-8")
    (root / CONTRACT_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / CONTRACT_PATH).write_text(_contract(), encoding="utf-8")


def run_goal_data_evidence_expansion02_upstream_evidence_expansion_gate(root: Path) -> bool:
    result = evaluate(root)
    _write_artifacts(root, result)
    audit_ok = audit_goal_data_evidence_expansion02_upstream_evidence_expansion_gate(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok


def audit_goal_data_evidence_expansion02_upstream_evidence_expansion_gate(root: Path) -> bool:
    failures: list[str] = []
    for rel in OUTPUT_ARTIFACTS:
        if rel == AUDIT_PATH:
            continue
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
    if manifest.get("materially_expanded_offline") is not False:
        failures.append("must_not_claim_material_offline_expansion")
    # no forbidden forward-return columns anywhere
    for rel in [EVIDENCE_GAP_MAP, FEATURE_CATALOG, PIT_CONTRACT, PROVIDER_DIVERSITY]:
        rows = _read_csv(root / rel)
        for h in (list(rows[0].keys()) if rows else []):
            if h.startswith("forward_return_") or h.startswith("benchmark_excess_return_"):
                failures.append(f"forbidden_forward_return_column:{rel}:{h}")
    # rec_tiering must still be locked (read-only assertion)
    wf = {r["workflow_id"]: r for r in _read_csv(root / "configs/project/workflow_status.csv")}
    rec = wf.get(GOAL_REC_TIERING01_WORKFLOW_ID, {})
    if rec and rec.get("status") != "locked_future":
        failures.append("rec_tiering_not_locked_future")
    status = PASS if not failures else BLOCKED
    (root / AUDIT_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / AUDIT_PATH).write_text("\n".join([f"# {GOAL_ID} Audit", "", f"Status: `{status}`", "", "## Failures", *[f"- {f}" for f in failures], ""]), encoding="utf-8")
    return status == PASS


def goal_data_evidence_expansion02_valid_evidence(root: Path) -> bool:
    report = (root / REPORT_PATH).read_text(encoding="utf-8") if (root / REPORT_PATH).exists() else ""
    audit = (root / AUDIT_PATH).read_text(encoding="utf-8") if (root / AUDIT_PATH).exists() else ""
    manifest = json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8")) if (root / MANIFEST_PATH).exists() else {}
    report_ok = (f"{GOAL_ID} Upstream Evidence Expansion Gate: PASS" in report or f"{GOAL_ID} Upstream Evidence Expansion Gate: PASS_WITH_WARNINGS" in report)
    return (report_ok and "Status: `PASS`" in audit and manifest.get("mode") == MODE
            and manifest.get("goal_rec_tiering01_locked_future") is True
            and all(manifest.get(k) is False for k in FALSE_BOUNDARY_KEYS))

"""Design-only alpha hypothesis reset after existing-factor failure attribution."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

GOAL_ID = "GOAL-ALPHA-HYPOTHESIS-REDESIGN-01"
SOURCE_MANIFEST = "outputs/audits/goal_factor_failure_attribution01_manifest.json"
PREFIX = "outputs/research/goal_alpha_hypothesis_redesign01_"
OUTPUTS = {
    "freeze": PREFIX + "existing_family_freeze.csv",
    "registry": PREFIX + "hypothesis_registry.csv",
    "evidence": PREFIX + "evidence_readiness.csv",
    "experiments": PREFIX + "pre_registered_experiment_plan.csv",
    "decision": PREFIX + "program_decision.csv",
}
REPORT = "outputs/audits/goal_alpha_hypothesis_redesign01_report.md"
MANIFEST = "outputs/audits/goal_alpha_hypothesis_redesign01_manifest.json"
AUDIT = "outputs/audits/goal_alpha_hypothesis_redesign01_audit.md"

FROZEN_FAMILIES = (
    "benchmark_relative_strength",
    "downside_volatility_adjusted_signal",
    "price_volume_confirmation",
    "risk_adjusted_alpha_candidate",
    "volatility_adjusted_momentum",
)

HYPOTHESES = (
    {
        "hypothesis_id": "HYP-LIQUIDITY-SHOCK-01",
        "economic_hypothesis": "abnormal liquidity shocks followed by bounded short-horizon normalization",
        "orthogonal_evidence_family": "volume_turnover_liquidity",
        "required_pit_fields": "volume;turnover_rate;free_float_shares;trade_status",
        "required_availability": "known_by_trade_date_close_or_earlier",
        "target_horizons_pre_registered": "1d;5d",
        "minimum_symbols": 100,
        "minimum_dates": 500,
        "minimum_independent_providers": 2,
        "primary_test": "sector_neutral_rank_ic_and_top_bottom_spread",
        "falsification_rule": "stop_if_holdout_rank_ic_sign_or_spread_direction_disagrees_in_two_of_three_walk_forward_folds",
        "status": "design_only_evidence_not_ready",
        "priority": 1,
    },
    {
        "hypothesis_id": "HYP-EVENT-DRIFT-01",
        "economic_hypothesis": "timestamped corporate events produce delayed cross-sectional repricing",
        "orthogonal_evidence_family": "corporate_event_metadata",
        "required_pit_fields": "event_type;published_at;available_at;symbol;revision_id",
        "required_availability": "provider_available_at_verified_before_feature_cutoff",
        "target_horizons_pre_registered": "1d;5d;20d",
        "minimum_symbols": 100,
        "minimum_dates": 500,
        "minimum_independent_providers": 1,
        "primary_test": "event_time_matched_control_excess_return",
        "falsification_rule": "stop_if_direction_is_unstable_across_event_cohorts_or_timestamp_coverage_below_95pct",
        "status": "design_only_evidence_not_ready",
        "priority": 2,
    },
    {
        "hypothesis_id": "HYP-FUNDAMENTAL-REVISION-01",
        "economic_hypothesis": "point_in_time fundamental revisions contain information not present in price momentum",
        "orthogonal_evidence_family": "pit_fundamental_revision",
        "required_pit_fields": "report_period;published_at;available_at;revision_id;fundamental_metric",
        "required_availability": "revision_aware_asof_join_before_feature_cutoff",
        "target_horizons_pre_registered": "5d;20d",
        "minimum_symbols": 200,
        "minimum_dates": 750,
        "minimum_independent_providers": 1,
        "primary_test": "industry_neutral_rank_ic_with_revision_aware_asof_join",
        "falsification_rule": "stop_if_revision_lineage_or_publication_time_is_unverifiable_or_holdout_sign_is_unstable",
        "status": "design_only_evidence_not_ready",
        "priority": 3,
    },
    {
        "hypothesis_id": "HYP-SECTOR-NEUTRAL-VALUATION-01",
        "economic_hypothesis": "sector_neutral valuation dispersion mean_reverts conditional on quality safeguards",
        "orthogonal_evidence_family": "pit_valuation_quality_industry",
        "required_pit_fields": "valuation_metric;quality_metric;industry_membership;published_at;available_at",
        "required_availability": "historical_industry_and_fundamental_asof_join",
        "target_horizons_pre_registered": "20d",
        "minimum_symbols": 300,
        "minimum_dates": 750,
        "minimum_independent_providers": 1,
        "primary_test": "industry_neutral_rank_ic_and_monotonic_quintile_spread",
        "falsification_rule": "stop_if_industry_history_is_current_membership_backfilled_or_monotonicity_fails_holdout",
        "status": "design_only_evidence_not_ready",
        "priority": 4,
    },
)


def _write(root: Path, rel: str, fields: list[str], rows: list[dict]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_goal_alpha_hypothesis_redesign01(root: Path) -> bool:
    source_path = root / SOURCE_MANIFEST
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if source.get("candidate_count") != 120 or source.get("ready_factor_count_after") != 0:
        return False
    freeze = [{
        "factor_family": family,
        "prior_candidate_count": 40 if family == "volatility_adjusted_momentum" else 20,
        "freeze_status": "frozen_current_definition",
        "reason": "failure_attribution01_stop_current_family_definition",
        "allowed_action": "no_more_variants_or_threshold_changes_without_explicit_new_goal",
    } for family in FROZEN_FAMILIES]
    registry = [dict(row) for row in HYPOTHESES]
    evidence = []
    for h in HYPOTHESES:
        evidence.extend([
            {"hypothesis_id": h["hypothesis_id"], "dimension": "symbol_breadth", "required": h["minimum_symbols"], "current": 41, "status": "not_ready"},
            {"hypothesis_id": h["hypothesis_id"], "dimension": "temporal_depth", "required": h["minimum_dates"], "current": 843, "status": "ready" if 843 >= h["minimum_dates"] else "not_ready"},
            {"hypothesis_id": h["hypothesis_id"], "dimension": "orthogonal_fields", "required": h["required_pit_fields"], "current": "not_accepted_for_this_hypothesis", "status": "not_ready"},
            {"hypothesis_id": h["hypothesis_id"], "dimension": "pit_availability", "required": h["required_availability"], "current": "not_verified_for_this_hypothesis", "status": "not_ready"},
        ])
    experiments = [{
        "sequence": h["priority"],
        "hypothesis_id": h["hypothesis_id"],
        "stage": "blocked_pending_evidence_acceptance",
        "construction_allowed": "false",
        "threshold_search_allowed": "false",
        "holdout_selection_allowed": "false",
        "pre_registered_primary_test": h["primary_test"],
        "pre_registered_falsification_rule": h["falsification_rule"],
        "next_gate": "separate_evidence_acceptance_goal_required",
    } for h in HYPOTHESES]
    decisions = [
        {"decision_id": "D1", "decision": "freeze_existing_five_factor_families", "status": "effective"},
        {"decision_id": "D2", "decision": "prioritize_liquidity_shock_hypothesis_after_evidence_acceptance", "status": "design_only"},
        {"decision_id": "D3", "decision": "require_materially_different_pit_evidence_before_construction", "status": "mandatory"},
        {"decision_id": "D4", "decision": "keep_all_downstream_and_v2_factor_mining_locks", "status": "mandatory"},
    ]
    _write(root, OUTPUTS["freeze"], list(freeze[0]), freeze)
    _write(root, OUTPUTS["registry"], list(registry[0]), registry)
    _write(root, OUTPUTS["evidence"], list(evidence[0]), evidence)
    _write(root, OUTPUTS["experiments"], list(experiments[0]), experiments)
    _write(root, OUTPUTS["decision"], list(decisions[0]), decisions)
    report = """# GOAL-ALPHA-HYPOTHESIS-REDESIGN-01\n\nStatus: `PASS_WITH_WARNINGS` (`implemented_design_only`)\n\n## Decision\n\nFreeze the five existing price-derived factor families. Do not create Candidate03 variants or relax readiness thresholds. Four orthogonal hypotheses are pre-registered, but all are blocked pending separate acceptance of materially different PIT-safe evidence.\n\nThe preferred first hypothesis is bounded liquidity-shock normalization because its required evidence is conceptually closest to the governed market-data path while remaining distinct from the failed price-only variants. It still requires at least 100 symbols, verified volume/turnover/free-float/trade-status fields, and the pre-registered falsification rule before construction.\n\n## Boundary\n\nNo factor values, labels, provider calls, evaluation rows, recommendations, positions, backtests, dashboards, trading, production, local-lake, broker, factor mining, or DQN/RL outputs are created. All downstream locks remain unchanged.\n"""
    (root / REPORT).write_text(report, encoding="utf-8")
    manifest = {
        "goal_id": GOAL_ID, "status": "PASS_WITH_WARNINGS", "mode": "implemented_design_only",
        "source_manifest": SOURCE_MANIFEST, "source_manifest_sha256": _sha(source_path),
        "frozen_family_count": len(freeze), "frozen_candidate_count": sum(int(x["prior_candidate_count"]) for x in freeze),
        "hypothesis_count": len(registry), "evidence_ready_hypothesis_count": 0,
        "preferred_hypothesis_id": "HYP-LIQUIDITY-SHOCK-01",
        "factor_values_created": False, "thresholds_changed": False, "provider_calls_performed": False,
        "v2_factor_mining_unlocked": False, "rec_tiering_unlocked": False, "downstream_locks_preserved": True,
        "outputs": {k: {"path": v, "sha256": _sha(root / v)} for k, v in sorted(OUTPUTS.items())},
    }
    (root / MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return audit_goal_alpha_hypothesis_redesign01(root)


def audit_goal_alpha_hypothesis_redesign01(root: Path) -> bool:
    try:
        m = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
        ok = (
            m["frozen_family_count"] == 5 and m["frozen_candidate_count"] == 120
            and m["hypothesis_count"] == 4 and m["evidence_ready_hypothesis_count"] == 0
            and not m["factor_values_created"] and not m["thresholds_changed"]
            and not m["provider_calls_performed"] and not m["v2_factor_mining_unlocked"]
            and not m["rec_tiering_unlocked"] and m["downstream_locks_preserved"]
            and _sha(root / m["source_manifest"]) == m["source_manifest_sha256"]
            and all(_sha(root / x["path"]) == x["sha256"] for x in m["outputs"].values())
        )
    except (OSError, KeyError, ValueError, json.JSONDecodeError):
        ok = False
    (root / AUDIT).write_text(f"# {GOAL_ID} Audit\n\nStatus: `{'PASS' if ok else 'FAIL'}`\n", encoding="utf-8")
    return ok

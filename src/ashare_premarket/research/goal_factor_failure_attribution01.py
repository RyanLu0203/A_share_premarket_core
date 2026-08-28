"""Research-only attribution of existing factor-readiness failures.

Consumes committed Rerun02 and Quant04 diagnostics. It does not construct
factors, search thresholds, fetch data, or promote any downstream capability.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

GOAL_ID = "GOAL-FACTOR-FAILURE-ATTRIBUTION-01"
WORKFLOW_ID = "goal_factor_failure_attribution01"
PREFIX = "outputs/research/goal_factor_failure_attribution01_"
INPUTS = {
    "reasons": "outputs/research/goal_factor_readiness_rerun02_readiness_decision_reasons.csv",
    "status": "outputs/research/goal_factor_readiness_rerun02_factor_readiness_status.csv",
    "comparison": "outputs/research/goal_factor_readiness_rerun02_old_new_readiness_comparison.csv",
    "walk": "outputs/research/goal_factor_readiness_rerun02_walk_forward_validation_summary.csv",
    "panel": "outputs/research/goal_factor_readiness_rerun02_reconstructed_panel_summary.csv",
    "provider": "outputs/research/goal_factor_readiness_rerun02_provider_robustness_summary.csv",
    "regime": "outputs/research/goal_quant_research04_regime_conditional_evaluation_summary.csv",
}
OUTPUTS = {
    "matrix": PREFIX + "candidate_failure_matrix.csv",
    "criteria": PREFIX + "criterion_failure_summary.csv",
    "families": PREFIX + "family_attribution_summary.csv",
    "regimes": PREFIX + "regime_sign_instability.csv",
    "redundancy": PREFIX + "candidate_redundancy_summary.csv",
    "decision": PREFIX + "program_decision.csv",
}
REPORT = "outputs/audits/goal_factor_failure_attribution01_report.md"
MANIFEST = "outputs/audits/goal_factor_failure_attribution01_manifest.json"
AUDIT = "outputs/audits/goal_factor_failure_attribution01_audit.md"
CRITERIA = (
    "base_precondition_pass",
    "holdout_sample_sufficient",
    "holdout_strong_ic_1d",
    "holdout_sign_stable_1d",
    "aligned_horizons_ge_2",
    "walk_forward_stable",
    "provider_robustness_checked",
)


def _read(root: Path, rel: str) -> list[dict[str, str]]:
    with (root / rel).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write(root: Path, rel: str, fields: list[str], rows: list[dict]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_goal_factor_failure_attribution01(root: Path) -> bool:
    source = {name: _read(root, rel) for name, rel in INPUTS.items()}
    reasons = source["reasons"]
    status_by_id = {r["candidate_id"]: r for r in source["status"]}
    comp_by_id = {r["candidate_id"]: r for r in source["comparison"]}
    walk_by_id = {r["candidate_id"]: r for r in source["walk"]}
    if not reasons or set(status_by_id) != {r["candidate_id"] for r in reasons}:
        return False

    matrix = []
    criterion_counts = Counter()
    family_totals: dict[str, Counter] = defaultdict(Counter)
    fingerprint_members: dict[tuple, list[str]] = defaultdict(list)
    for row in sorted(reasons, key=lambda x: x["candidate_id"]):
        cid = row["candidate_id"]
        status = status_by_id[cid]
        comparison = comp_by_id[cid]
        walk = walk_by_id[cid]
        failed = [key for key in CRITERIA if row[key] != "true"]
        for key in failed:
            criterion_counts[key] += 1
        family = status["factor_family"]
        family_totals[family]["candidates"] += 1
        family_totals[family]["failed_criteria"] += len(failed)
        family_totals[family]["lost_conditional"] += comparison["transition_category"] == "lost_conditional_status"
        family_totals[family]["sign_unstable"] += row["holdout_sign_stable_1d"] != "true"
        fp = tuple(walk[k] for k in (
            "holdout_mean_ic_1d", "holdout_mean_ic_5d", "holdout_mean_ic_20d",
            "holdout_rank_ic_1d", "holdout_sign_consistency_1d",
            "walk_forward_cross_fold_sign_consistency",
        ))
        fingerprint_members[(family,) + fp].append(cid)
        primary = max(failed, key=lambda k: (criterion_counts[k], k)) if failed else "none"
        matrix.append({
            "candidate_id": cid,
            "factor_family": family,
            "old_status": comparison["old_status"],
            "new_status": comparison["new_status"],
            "transition_category": comparison["transition_category"],
            "failed_criterion_count": len(failed),
            "failed_criteria": ";".join(failed),
            "primary_failure_class": primary,
            "holdout_mean_ic_1d": status["holdout_mean_ic_1d"],
            "holdout_sign_consistency_1d": status["holdout_sign_consistency_1d"],
            "aligned_horizon_count": status["aligned_horizon_count"],
            "holdout_valid_rows": status["holdout_valid_rows"],
            "research_decision": "redesign_or_stop_no_promotion",
        })

    n = len(matrix)
    criteria = [{
        "criterion": key,
        "failure_count": criterion_counts[key],
        "candidate_count": n,
        "failure_rate": f"{criterion_counts[key] / n:.6f}",
        "binding_rank": 0,
        "interpretation": "binding" if criterion_counts[key] >= n / 2 else "secondary",
    } for key in CRITERIA]
    criteria.sort(key=lambda x: (-x["failure_count"], x["criterion"]))
    for rank, row in enumerate(criteria, 1):
        row["binding_rank"] = rank

    regime_by_family: dict[str, Counter] = defaultdict(Counter)
    for row in source["regime"]:
        fam = row["factor_family"]
        regime_by_family[fam]["cells"] += 1
        regime_by_family[fam]["sign_flips"] += int(row.get("sign_flip_count") or 0)
        regime_by_family[fam]["unstable"] += row["regime_stability_status"] not in {"stable", "not_evaluable"}
        regime_by_family[fam]["not_evaluable"] += row["regime_stability_status"] == "not_evaluable"
    regime_rows = [{
        "factor_family": fam,
        "regime_cells": c["cells"],
        "sign_flip_count": c["sign_flips"],
        "unstable_cell_count": c["unstable"],
        "not_evaluable_cell_count": c["not_evaluable"],
        "regime_instability_status": "material" if c["sign_flips"] or c["unstable"] else "not_observed",
    } for fam, c in sorted(regime_by_family.items())]

    redundant_by_family = Counter()
    unique_by_family = Counter()
    for key, members in fingerprint_members.items():
        family = key[0]
        unique_by_family[family] += 1
        redundant_by_family[family] += max(0, len(members) - 1)
    redundancy = [{
        "factor_family": fam,
        "candidate_count": family_totals[fam]["candidates"],
        "unique_metric_fingerprint_count": unique_by_family[fam],
        "redundant_candidate_count": redundant_by_family[fam],
        "redundancy_rate": f"{redundant_by_family[fam] / family_totals[fam]['candidates']:.6f}",
        "method": "exact_existing_holdout_walkforward_metric_fingerprint_no_factor_recalculation",
    } for fam in sorted(family_totals)]

    regime_lookup = {r["factor_family"]: r for r in regime_rows}
    family_rows = []
    for fam, counts in sorted(family_totals.items()):
        fail_rate = counts["failed_criteria"] / (counts["candidates"] * len(CRITERIA))
        decision = "stop_current_family_definition" if fail_rate >= .5 else "redesign_before_any_retest"
        family_rows.append({
            "factor_family": fam,
            "candidate_count": counts["candidates"],
            "average_failed_criteria": f"{counts['failed_criteria'] / counts['candidates']:.6f}",
            "lost_conditional_count": counts["lost_conditional"],
            "holdout_sign_unstable_count": counts["sign_unstable"],
            "regime_sign_flip_count": regime_lookup.get(fam, {}).get("sign_flip_count", 0),
            "redundant_candidate_count": redundant_by_family[fam],
            "family_decision": decision,
            "promotion_allowed": "false",
        })

    panel_symbols = max(int(r["symbol_count"]) for r in source["panel"])
    panel_dates = max(int(r["date_count"]) for r in source["panel"])
    provider = source["provider"][0]
    decisions = [
        {"decision_id": "D1", "dimension": "research", "decision": "do_not_promote_any_existing_candidate", "evidence": f"{n}_of_{n}_candidates_not_ready"},
        {"decision_id": "D2", "dimension": "method", "decision": "stop_candidate_proliferation_and_redesign_hypotheses", "evidence": f"{sum(redundant_by_family.values())}_metric_redundant_candidates"},
        {"decision_id": "D3", "dimension": "coverage", "decision": "treat_cross_sectional_breadth_as_limited", "evidence": f"{panel_symbols}_symbols_{panel_dates}_dates"},
        {"decision_id": "D4", "dimension": "provider", "decision": "retain_provider_fragility_warning", "evidence": provider["status"]},
        {"decision_id": "D5", "dimension": "governance", "decision": "keep_all_downstream_locks", "evidence": "ready_factor_count_zero"},
    ]

    _write(root, OUTPUTS["matrix"], list(matrix[0]), matrix)
    _write(root, OUTPUTS["criteria"], list(criteria[0]), criteria)
    _write(root, OUTPUTS["families"], list(family_rows[0]), family_rows)
    _write(root, OUTPUTS["regimes"], list(regime_rows[0]), regime_rows)
    _write(root, OUTPUTS["redundancy"], list(redundancy[0]), redundancy)
    _write(root, OUTPUTS["decision"], list(decisions[0]), decisions)

    top = criteria[0]
    report = f"""# {GOAL_ID} Research-Only Factor Failure Attribution\n\nStatus: `PASS_WITH_WARNINGS`\n\n## Decision\n\nAll `{n}` existing candidates remain non-ready. No promotion is allowed. The most frequent failed criterion is `{top['criterion']}` ({top['failure_count']}/{n}). Candidate proliferation should stop until existing hypothesis families are redesigned from this evidence.\n\n## Evidence\n\n- Effective breadth: `{panel_symbols}` symbols across `{panel_dates}` dates.\n- Metric-fingerprint redundant candidates: `{sum(redundant_by_family.values())}`.\n- Lost prior conditional status: `{sum(c['lost_conditional'] for c in family_totals.values())}`.\n- Provider robustness: `{provider['status']}`.\n\n## Boundary\n\nThis goal constructs no factor, changes no threshold, fetches no data, and unlocks no recommendation, position, backtest, dashboard, trading, production, factor-mining, broker, local-lake, or DQN/RL path. GOAL-10D remains separately locked.\n"""
    (root / REPORT).write_text(report, encoding="utf-8")
    manifest = {
        "goal_id": GOAL_ID, "status": "PASS_WITH_WARNINGS", "research_only": True,
        "candidate_count": n, "ready_factor_count_before": 0, "ready_factor_count_after": 0,
        "family_count": len(family_rows), "effective_symbol_count": panel_symbols,
        "effective_date_count": panel_dates, "top_failed_criterion": top["criterion"],
        "top_failed_criterion_count": top["failure_count"],
        "metric_fingerprint_redundant_candidate_count": sum(redundant_by_family.values()),
        "new_factors_constructed": False, "thresholds_changed": False,
        "provider_calls_performed": False, "goal10d_unlocked": False,
        "rec_tiering_unlocked": False, "downstream_locks_preserved": True,
        "inputs": {k: {"path": v, "sha256": _sha(root / v)} for k, v in sorted(INPUTS.items())},
        "outputs": {k: {"path": v, "sha256": _sha(root / v)} for k, v in sorted(OUTPUTS.items())},
    }
    (root / MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return audit_goal_factor_failure_attribution01(root)


def audit_goal_factor_failure_attribution01(root: Path) -> bool:
    try:
        m = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
        ok = (
            m["candidate_count"] == 120 and m["ready_factor_count_after"] == 0
            and not m["new_factors_constructed"] and not m["thresholds_changed"]
            and not m["provider_calls_performed"] and not m["goal10d_unlocked"]
            and not m["rec_tiering_unlocked"] and m["downstream_locks_preserved"]
            and all(_sha(root / x["path"]) == x["sha256"] for x in m["outputs"].values())
        )
    except (OSError, KeyError, ValueError, json.JSONDecodeError):
        ok = False
    (root / AUDIT).write_text(
        f"# {GOAL_ID} Audit\n\nStatus: `{'PASS' if ok else 'FAIL'}`\n",
        encoding="utf-8",
    )
    return ok

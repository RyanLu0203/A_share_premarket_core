from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.research.goal_factor_readiness_research01 import (
    FALSE_BOUNDARY_KEYS,
    HOLDOUT_FRACTION,
    MANIFEST_PATH,
    READINESS_STATUS_PATH,
    CANDIDATE_LINEAGE_PATH,
    WALK_FORWARD_PATH,
    _chronological_split,
    _walk_forward_folds,
    audit_goal_factor_readiness_research01_factor_readiness_research_gate as audit_gate,
    goal_factor_readiness_research01_valid_evidence,
    run_goal_factor_readiness_research01_factor_readiness_research_gate as run_gate,
)
from ashare_premarket.research.goal_quant_research04 import STRONG_IC_THRESHOLD

ROOT = Path(__file__).resolve().parents[1]


def _rows(rel: str) -> list[dict[str, str]]:
    with (ROOT / rel).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _manifest() -> dict:
    return json.loads((ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))


def test_gate_and_audit_pass_and_evidence_valid() -> None:
    assert run_gate(ROOT)
    assert audit_gate(ROOT)
    assert goal_factor_readiness_research01_valid_evidence(ROOT)
    assert _manifest()["status"] in {"PASS", "PASS_WITH_WARNINGS"}


def test_thresholds_preserved_and_boundaries_false() -> None:
    run_gate(ROOT)
    m = _manifest()
    assert m["existing_thresholds_preserved"] is True
    assert m["scientific_thresholds_lowered"] is False
    assert m["existing_thresholds_modified"] is False
    assert m["strong_ic_threshold_used"] == STRONG_IC_THRESHOLD == 0.03
    for key in FALSE_BOUNDARY_KEYS:
        assert m[key] is False, key
    assert m["goal_rec_tiering01_locked_future"] is True


def test_ready_count_honest_and_not_fabricated() -> None:
    run_gate(ROOT)
    rows = _rows(READINESS_STATUS_PATH)
    assert rows
    assert all(r["readiness_status"] in {"ready", "conditionally_useful", "not_ready"} for r in rows)
    ready = [r for r in rows if r["readiness_status"] == "ready"]
    # No ready factor may be fabricated: every ready row must satisfy the base precondition.
    for r in ready:
        assert r["base_precondition_pass"] == "true", r["candidate_id"]
    m = _manifest()
    distinct_ready_base = {r["base_refined_factor_id"] for r in ready}
    assert m["ready_factor_count"] == len(distinct_ready_base)
    assert isinstance(m["ready_factor_count"], int) and m["ready_factor_count"] >= 0


def test_no_auto_unlock_and_no_governance_mutation() -> None:
    run_gate(ROOT)
    m = _manifest()
    assert m["workflow_status_modified_by_this_goal"] is False
    assert m["locked_capabilities_modified_by_this_goal"] is False
    assert m["rec_tiering_unlocked_by_this_goal"] is False
    workflow = {r["workflow_id"]: r for r in _rows("configs/project/workflow_status.csv")}
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["status"] == "locked_future"
    assert workflow["dashboard_daily_report"]["status"] == "locked_future"


def test_no_forward_return_or_actionable_columns() -> None:
    run_gate(ROOT)
    for rel in [READINESS_STATUS_PATH, WALK_FORWARD_PATH, CANDIDATE_LINEAGE_PATH]:
        headers = list(_rows(rel)[0].keys())
        for h in headers:
            assert not h.startswith("forward_return_")
            assert not h.startswith("benchmark_excess_return_")
        import re
        joined = " ".join(headers).lower()
        # word-boundary match so out-of-sample "holdout" columns are not mistaken for a HOLD action
        for bad in ("buy", "sell", "hold", "target_price", "order_quantity", "position_size", "portfolio_weight"):
            assert not re.search(r"(?<![a-z])" + re.escape(bad) + r"(?![a-z])", joined), (bad, headers)


def test_candidate_lineage_complete() -> None:
    run_gate(ROOT)
    lineage = {r["candidate_id"]: r for r in _rows(CANDIDATE_LINEAGE_PATH)}
    for status in _rows(READINESS_STATUS_PATH):
        lin = lineage[status["candidate_id"]]
        assert lin["base_refined_factor_id"]
        assert lin["refinement_transform"]
        assert lin["tuned_on_holdout"] == "false"
        assert lin["pit_declaration"] == "per_date_cross_sectional_only_no_future_information"


def test_holdout_isolated_and_chronological() -> None:
    dates = [f"2025-{m:02d}-{d:02d}" for m in (1, 2, 3) for d in range(1, 21)]
    in_sample, holdout = _chronological_split(dates)
    assert holdout, "expected a non-empty holdout"
    assert set(in_sample).isdisjoint(set(holdout))
    assert max(in_sample) < min(holdout)  # strict chronological separation
    assert abs(len(holdout) / len(dates) - HOLDOUT_FRACTION) < 0.05
    for train, test in _walk_forward_folds(in_sample):
        assert max(train) < min(test)  # no lookahead within folds


def test_deterministic_reconstruction() -> None:
    run_gate(ROOT)
    first = (ROOT / READINESS_STATUS_PATH).read_text(encoding="utf-8")
    run_gate(ROOT)
    second = (ROOT / READINESS_STATUS_PATH).read_text(encoding="utf-8")
    assert first == second

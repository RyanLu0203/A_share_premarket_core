from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.research.goal_alpha_research_refinement01 import (
    AUDIT_PATH,
    CONDITIONAL_STABILITY_FIELDS,
    CONDITIONAL_STABILITY_PATH,
    FALSE_BOUNDARY_KEYS,
    INSTABILITY_ATTRIBUTION_PATH,
    INSTABILITY_FIELDS,
    MANIFEST_PATH,
    PROMISING_CANDIDATES,
    REFINED_DESIGNS_PATH,
    TRIAL_REGISTRY_UPDATE_PATH,
    audit_goal_alpha_research_refinement01_gate,
    evaluate_goal_alpha_research_refinement01,
    run_goal_alpha_research_refinement01_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal_alpha_research_refinement01_schema_and_counts() -> None:
    result = evaluate_goal_alpha_research_refinement01(ROOT)
    manifest = result["manifest"]

    assert manifest["status"] in {"PASS", "PASS_WITH_WARNINGS"}
    assert manifest["source_quant02_evaluation_row_count"] == 78000
    assert manifest["promising_candidate_count"] == 6
    assert set(manifest["promising_candidate_ids"]) == set(PROMISING_CANDIDATES)
    assert manifest["refined_candidate_design_count"] >= 6
    assert manifest["intraday_redefinition_row_count"] >= 2
    assert len(result["instability"]) == 6
    assert list(result["instability"][0]) == INSTABILITY_FIELDS
    assert list(result["conditional"][0]) == CONDITIONAL_STABILITY_FIELDS


def test_goal_alpha_research_refinement01_runner_preserves_boundaries() -> None:
    assert run_goal_alpha_research_refinement01_gate(ROOT)
    assert audit_goal_alpha_research_refinement01_gate(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")

    manifest = _json(MANIFEST_PATH)
    instability = _rows(INSTABILITY_ATTRIBUTION_PATH)
    conditional = _rows(CONDITIONAL_STABILITY_PATH)
    designs = _rows(REFINED_DESIGNS_PATH)
    trials = _rows(TRIAL_REGISTRY_UPDATE_PATH)

    assert len(instability) == 6
    assert len(conditional) > len(instability)
    assert len(designs) == manifest["refined_candidate_design_count"]
    assert len(trials) == manifest["trial_registry_update_row_count"]
    assert {row["not_evaluated_status"] for row in designs} == {"proposed_refined_candidate_not_evaluated"}
    assert {row["accepted_for_downstream"] for row in trials} == {"false"}
    assert {row["candidate_for_rec_tiering"] for row in trials} == {"false"}
    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert manifest["refined_candidates_not_evaluated"] is True
    assert manifest["goal_alpha_factor_candidate02_locked_future"] is True
    assert manifest["goal_rec_tiering01_locked_future"] is True

    workflow = _workflow()
    assert workflow["goal_alpha_research_refinement01_rolling_stability_candidate_refinement_gate"]["status"] == "implemented_research_only"
    assert workflow["goal_alpha_research_refinement01_rolling_stability_candidate_refinement_gate"]["depends_on"] == "goal_quant_research02_alpha_candidate_factor_validity_evaluation_gate"
    assert workflow["goal_alpha_factor_candidate02_refined_variants_research_gate"]["status"] in {
        "locked_future",
        "implemented_research_only",
    }
    assert workflow["goal_alpha_factor_candidate02_refined_variants_research_gate"]["depends_on"] == "goal_alpha_research_refinement01_rolling_stability_candidate_refinement_gate"
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["status"] == "locked_future"
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["depends_on"] in {
        "goal_alpha_factor_candidate02_refined_variants_research_gate",
        "goal_quant_research03_refined_alpha_factor_validity_evaluation_gate",
        "goal_quant_research04_regime_conditional_factor_evaluation_gate",
    }
    if workflow["goal_alpha_factor_candidate02_refined_variants_research_gate"]["status"] == "implemented_research_only":
        assert workflow["goal_quant_research03_refined_alpha_factor_validity_evaluation_gate"]["status"] in {
            "locked_future",
            "implemented_research_only",
        }
        assert workflow["goal_quant_research03_refined_alpha_factor_validity_evaluation_gate"]["depends_on"] == "goal_alpha_factor_candidate02_refined_variants_research_gate"

from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.research.goal_alpha_factor_candidate02 import (
    AUDIT_PATH,
    COVERAGE_SUMMARY_PATH,
    FALSE_BOUNDARY_KEYS,
    MANIFEST_PATH,
    PANEL_FIELDS,
    REFINED_PANEL_PATH,
    REFINED_REGISTRY_PATH,
    REGISTRY_FIELDS,
    TRIAL_REGISTRY_PATH,
    audit_goal_alpha_factor_candidate02_gate,
    evaluate_goal_alpha_factor_candidate02,
    run_goal_alpha_factor_candidate02_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal_alpha_factor_candidate02_evaluation_schema_and_counts() -> None:
    result = evaluate_goal_alpha_factor_candidate02(ROOT)
    manifest = result["manifest"]

    assert manifest["status"] in {"PASS", "PASS_WITH_WARNINGS"}
    assert manifest["refined_candidate_design_count"] == 30
    assert manifest["refined_candidate_registry_row_count"] == 30
    assert manifest["constructed_refined_candidate_count"] == 30
    assert manifest["refined_candidate_panel_row_count"] == 180000
    assert manifest["unique_symbols"] == 50
    assert manifest["unique_trade_dates"] == 120
    assert list(result["registry"][0]) == REGISTRY_FIELDS
    assert list(result["refined_panel"][0]) == PANEL_FIELDS


def test_goal_alpha_factor_candidate02_runner_preserves_research_boundaries() -> None:
    assert run_goal_alpha_factor_candidate02_gate(ROOT)
    assert audit_goal_alpha_factor_candidate02_gate(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")

    manifest = _json(MANIFEST_PATH)
    registry = _rows(REFINED_REGISTRY_PATH)
    panel = _rows(REFINED_PANEL_PATH)
    coverage = _rows(COVERAGE_SUMMARY_PATH)
    trials = _rows(TRIAL_REGISTRY_PATH)

    assert len(registry) == 30
    assert len(panel) == 180000
    assert len(coverage) == 30
    assert len(trials) == 30
    assert len({(row["trade_date"], row["symbol"], row["refined_factor_id"]) for row in panel}) == len(panel)
    assert {row["uses_forward_returns_in_construction"] for row in registry} == {"false"}
    assert {row["uses_benchmark_excess_returns_in_construction"] for row in registry} == {"false"}
    assert {row["uses_label_ready_fields_in_construction"] for row in registry} == {"false"}
    assert {row["no_lookahead_status"] for row in panel} == {"passed_current_or_past_only"}
    assert {row["accepted_for_downstream"] for row in trials} == {"false"}
    assert {row["candidate_for_rec_tiering"] for row in trials} == {"false"}

    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert manifest["refined_candidates_not_evaluated"] is True
    assert manifest["goal_quant_research03_locked_future"] is True
    assert manifest["goal_rec_tiering01_locked_future"] is True

    workflow = _workflow()
    assert workflow["goal_alpha_factor_candidate02_refined_variants_research_gate"]["status"] == "implemented_research_only"
    assert workflow["goal_alpha_factor_candidate02_refined_variants_research_gate"]["depends_on"] == "goal_alpha_research_refinement01_rolling_stability_candidate_refinement_gate"
    assert workflow["goal_quant_research03_refined_alpha_factor_validity_evaluation_gate"]["status"] in {
        "locked_future",
        "implemented_research_only",
    }
    assert workflow["goal_quant_research03_refined_alpha_factor_validity_evaluation_gate"]["depends_on"] == "goal_alpha_factor_candidate02_refined_variants_research_gate"
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["status"] == "locked_future"
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["depends_on"] == "goal_quant_research03_refined_alpha_factor_validity_evaluation_gate"

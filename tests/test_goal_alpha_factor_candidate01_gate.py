from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.research.goal_alpha_factor_candidate01 import (
    AUDIT_PATH,
    CANDIDATE_PANEL_PATH,
    CANDIDATE_REGISTRY_PATH,
    COVERAGE_SUMMARY_PATH,
    FALSE_BOUNDARY_KEYS,
    MANIFEST_PATH,
    PANEL_FIELDS,
    REGISTRY_FIELDS,
    audit_goal_alpha_factor_candidate01_gate,
    evaluate_goal_alpha_factor_candidate01,
    run_goal_alpha_factor_candidate01_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal_alpha_factor_candidate01_evaluation_schema_and_counts() -> None:
    result = evaluate_goal_alpha_factor_candidate01(ROOT)
    manifest = result["manifest"]

    assert manifest["status"] == "PASS_WITH_WARNINGS"
    assert manifest["constructed_candidate_count"] == 13
    assert manifest["candidate_registry_row_count"] == 13
    assert manifest["candidate_panel_row_count"] == 78000
    assert manifest["unique_symbols"] == 50
    assert manifest["unique_trade_dates"] == 120
    assert result["registry"]
    assert result["candidate_panel"]
    assert list(result["registry"][0]) == REGISTRY_FIELDS
    assert list(result["candidate_panel"][0]) == PANEL_FIELDS


def test_goal_alpha_factor_candidate01_runner_preserves_research_only_boundaries() -> None:
    assert run_goal_alpha_factor_candidate01_gate(ROOT)
    assert audit_goal_alpha_factor_candidate01_gate(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")

    manifest = _json(MANIFEST_PATH)
    registry = _rows(CANDIDATE_REGISTRY_PATH)
    panel = _rows(CANDIDATE_PANEL_PATH)
    coverage = _rows(COVERAGE_SUMMARY_PATH)

    assert len(registry) == 13
    assert len(panel) == 78000
    assert len(coverage) == 13
    assert len({(row["trade_date"], row["symbol"], row["factor_id"]) for row in panel}) == len(panel)
    assert {row["uses_forward_returns_in_construction"] for row in registry} == {"false"}
    assert {row["uses_benchmark_excess_returns_in_construction"] for row in registry} == {"false"}
    assert {row["uses_label_ready_fields_in_construction"] for row in registry} == {"false"}
    assert {row["no_lookahead_status"] for row in panel} == {"passed_current_or_past_only"}

    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert manifest["alpha_candidate_panel_created"] is True
    assert manifest["goal_quant_research02_locked_future"] is True
    assert manifest["goal_rec_tiering01_locked_future"] is True

    workflow = _workflow()
    assert workflow["goal_alpha_factor_candidate01_research_gate"]["status"] == "implemented_research_only"
    assert workflow["goal_alpha_factor_candidate01_research_gate"]["implemented_in_repo"] == "true"
    assert workflow["goal_quant_research02_alpha_candidate_factor_validity_evaluation_gate"]["status"] in {
        "locked_future",
        "implemented_research_only",
    }
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["depends_on"] in {
        "goal_quant_research02_alpha_candidate_factor_validity_evaluation_gate",
        "goal_alpha_factor_candidate02_refined_variants_research_gate",
        "goal_quant_research03_refined_alpha_factor_validity_evaluation_gate",
        "goal_quant_research04_regime_conditional_factor_evaluation_gate",
    }

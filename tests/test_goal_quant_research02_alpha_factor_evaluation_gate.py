from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.research.goal_quant_research02 import (
    AUDIT_PATH,
    EVALUATION_PANEL_FIELDS,
    EVALUATION_PANEL_PATH,
    FALSE_BOUNDARY_KEYS,
    MANIFEST_PATH,
    SCORE_VALIDITY_PATH,
    audit_goal_quant_research02_alpha_factor_evaluation_gate,
    evaluate_goal_quant_research02_alpha_factor_evaluation,
    run_goal_quant_research02_alpha_factor_evaluation_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal_quant_research02_evaluation_schema_and_counts() -> None:
    result = evaluate_goal_quant_research02_alpha_factor_evaluation(ROOT)
    manifest = result["manifest"]

    assert manifest["status"] in {"PASS", "PASS_WITH_WARNINGS"}
    assert manifest["evaluated_factor_count"] == 13
    assert manifest["source_alpha_panel_row_count"] == 78000
    assert manifest["alpha_evaluation_panel_row_count"] == 78000
    assert manifest["unique_symbols"] == 50
    assert manifest["unique_trade_dates"] == 120
    assert len(result["coverage"]) == 13
    assert len(result["validity"]) == 13
    assert len(result["trials"]) == 13
    assert list(result["evaluation_rows"][0]) == EVALUATION_PANEL_FIELDS


def test_goal_quant_research02_runner_preserves_research_only_boundaries() -> None:
    assert run_goal_quant_research02_alpha_factor_evaluation_gate(ROOT)
    assert audit_goal_quant_research02_alpha_factor_evaluation_gate(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")

    manifest = _json(MANIFEST_PATH)
    panel = _rows(EVALUATION_PANEL_PATH)
    validity = _rows(SCORE_VALIDITY_PATH)

    assert len(panel) == 78000
    assert len(validity) == 13
    assert len({(row["trade_date"], row["symbol"], row["factor_id"]) for row in panel}) == len(panel)
    assert {row["non_actionable_disclaimer"] for row in panel} == {
        "research_only_alpha_evaluation_not_investment_advice_not_trade_instruction"
    }
    assert {row["accepted_for_downstream"] for row in validity} == {"false"}
    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert manifest["future_returns_used_only_for_posthoc_evaluation"] is True
    assert manifest["benchmark_excess_returns_used_only_for_posthoc_evaluation"] is True
    assert manifest["goal_rec_tiering01_locked_future"] is True

    workflow = _workflow()
    assert workflow["goal_quant_research02_alpha_candidate_factor_validity_evaluation_gate"]["status"] == "implemented_research_only"
    assert workflow["goal_quant_research02_alpha_candidate_factor_validity_evaluation_gate"]["implemented_in_repo"] == "true"
    assert workflow["goal_quant_research02_alpha_candidate_factor_validity_evaluation_gate"]["depends_on"] == "goal_alpha_factor_candidate01_research_gate"
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["status"] == "locked_future"
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["depends_on"] in {
        "goal_quant_research02_alpha_candidate_factor_validity_evaluation_gate",
        "goal_alpha_factor_candidate02_refined_variants_research_gate",
        "goal_quant_research03_refined_alpha_factor_validity_evaluation_gate",
    }

from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.research.goal_quant_research03 import (
    AUDIT_PATH,
    COVERAGE_SUMMARY_PATH,
    EVALUATION_PANEL_FIELDS,
    FALSE_BOUNDARY_KEYS,
    MANIFEST_PATH,
    PANEL_INDEX_PATH,
    SCORE_VALIDITY_PATH,
    SIZE_LIMIT_BYTES,
    TRIAL_REGISTRY_PATH,
    audit_goal_quant_research03_refined_alpha_evaluation_gate,
    evaluate_goal_quant_research03_refined_alpha_evaluation,
    run_goal_quant_research03_refined_alpha_evaluation_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _panel_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in _rows(PANEL_INDEX_PATH):
        rows.extend(_rows(item["path"]))
    return rows


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal_quant_research03_evaluation_schema_and_counts() -> None:
    result = evaluate_goal_quant_research03_refined_alpha_evaluation(ROOT)
    manifest = result["manifest"]

    assert manifest["status"] in {"PASS", "PASS_WITH_WARNINGS"}
    assert manifest["evaluated_refined_factor_count"] == 30
    assert manifest["source_candidate02_panel_row_count"] == 180000
    assert manifest["refined_alpha_evaluation_panel_row_count"] == 180000
    assert manifest["unique_symbols"] == 50
    assert manifest["unique_trade_dates"] == 120
    assert len(result["coverage"]) == 30
    assert len(result["validity"]) == 30
    assert len(result["trials"]) == 30
    assert list(result["evaluation_rows"][0]) == EVALUATION_PANEL_FIELDS
    assert manifest["artifact_size_policy_passed"] is True


def test_goal_quant_research03_runner_preserves_research_only_boundaries() -> None:
    assert run_goal_quant_research03_refined_alpha_evaluation_gate(ROOT)
    assert audit_goal_quant_research03_refined_alpha_evaluation_gate(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")

    manifest = _json(MANIFEST_PATH)
    panel = _panel_rows()
    coverage = _rows(COVERAGE_SUMMARY_PATH)
    validity = _rows(SCORE_VALIDITY_PATH)
    trials = _rows(TRIAL_REGISTRY_PATH)
    index_rows = _rows(PANEL_INDEX_PATH)

    assert len(panel) == 180000
    assert len(coverage) == 30
    assert len(validity) == 30
    assert len(trials) == 30
    assert len(index_rows) == 5
    assert all(int(row["byte_size"]) < SIZE_LIMIT_BYTES for row in index_rows)
    assert len({(row["trade_date"], row["symbol"], row["refined_factor_id"]) for row in panel}) == len(panel)
    assert {row["non_actionable_disclaimer"] for row in panel} == {"research_only"}
    assert {row["accepted_for_downstream"] for row in validity} == {"false"}
    assert {row["accepted_for_downstream"] for row in trials} == {"false"}
    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert manifest["future_returns_used_only_for_posthoc_evaluation"] is True
    assert manifest["benchmark_excess_returns_used_only_for_posthoc_evaluation"] is True
    assert manifest["goal_rec_tiering01_locked_future"] is True
    assert manifest["artifact_size_policy_passed"] is True

    workflow = _workflow()
    assert workflow["goal_quant_research03_refined_alpha_factor_validity_evaluation_gate"]["status"] == "implemented_research_only"
    assert workflow["goal_quant_research03_refined_alpha_factor_validity_evaluation_gate"]["implemented_in_repo"] == "true"
    assert workflow["goal_quant_research03_refined_alpha_factor_validity_evaluation_gate"]["depends_on"] == "goal_alpha_factor_candidate02_refined_variants_research_gate"
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["status"] == "locked_future"
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["depends_on"] == "goal_quant_research03_refined_alpha_factor_validity_evaluation_gate"

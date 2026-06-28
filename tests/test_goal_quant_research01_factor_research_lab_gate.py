from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.research.goal_quant_research01 import (
    AUDIT_PATH,
    FACTOR_EVALUATION_PANEL_PATH,
    FACTOR_REGISTRY_PATH,
    FALSE_BOUNDARY_KEYS,
    MANIFEST_PATH,
    SCORE_VALIDITY_PATH,
    TRIAL_REGISTRY_PATH,
    audit_goal_quant_research01_factor_research_lab_gate,
    run_goal_quant_research01_factor_research_lab_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal_quant_research01_runner_is_research_only_and_deterministic() -> None:
    assert run_goal_quant_research01_factor_research_lab_gate(ROOT)
    first = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert run_goal_quant_research01_factor_research_lab_gate(ROOT)
    second = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert first == second
    assert audit_goal_quant_research01_factor_research_lab_gate(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")


def test_goal_quant_research01_creates_factor_lab_artifacts_without_forward_return_construction() -> None:
    assert run_goal_quant_research01_factor_research_lab_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    registry = _rows(FACTOR_REGISTRY_PATH)
    panel = _rows(FACTOR_EVALUATION_PANEL_PATH)
    trials = _rows(TRIAL_REGISTRY_PATH)
    validity = _rows(SCORE_VALIDITY_PATH)

    assert manifest["status"] == "PASS_WITH_WARNINGS"
    assert manifest["factor_count"] == 11
    assert manifest["source_panel_row_count"] == 6000
    assert manifest["factor_evaluation_row_count"] == 66000
    assert manifest["ready_factor_count"] == 0
    assert manifest["overall_score_validity_status"] == "no_factor_ready_for_rec_tiering"
    assert manifest["recommended_next_goal"] == "GOAL-ALPHA-FACTOR-CANDIDATE-01_before_recommendation_tiering"
    assert len(registry) == 11
    assert len(panel) == 66000
    assert len(validity) == 11
    assert {row["uses_forward_returns_in_construction"] for row in registry} == {"false"}
    assert {row["allowed_for_posthoc_evaluation_only"] for row in registry} == {"true"}
    assert {row["accepted_for_downstream"] for row in trials} == {"false"}
    assert {row["candidate_for_rec_tiering"] for row in validity} == {"false"}
    assert {row["non_actionable_disclaimer"] for row in panel} == {
        "research_only_not_investment_advice_not_trade_instruction"
    }
    assert len({(row["trade_date"], row["symbol"], row["factor_id"]) for row in panel}) == len(panel)


def test_goal_quant_research01_preserves_boundaries_and_workflow_locks() -> None:
    assert run_goal_quant_research01_factor_research_lab_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    workflow = _workflow()

    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert manifest["research_only_factor_lab_generated"] is True
    assert manifest["future_returns_used_only_for_posthoc_evaluation"] is True
    assert manifest["no_lookahead_validation_passed"] is True
    assert manifest["anti_overfitting_policy_recorded"] is True
    assert manifest["trial_registry_created"] is True
    assert workflow["goal_quant_research01_factor_research_lab_gate"]["status"] == "implemented_research_only"
    assert workflow["goal_quant_research01_factor_research_lab_gate"]["implemented_in_repo"] == "true"
    assert workflow["goal_quant_research01_factor_research_lab_gate"]["depends_on"] == "goal_risk_tiering011_downside_risk_repair_gate"
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["status"] == "locked_future"
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["implemented_in_repo"] == "false"
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["depends_on"] in {
        "goal_quant_research01_factor_research_lab_gate",
        "goal_alpha_factor_candidate01_research_gate",
        "goal_quant_research02_alpha_candidate_factor_validity_evaluation_gate",
    }
    for workflow_id in [
        "goal10b4_recommendation_backtest_revalidation",
        "goal_position_band_validation01_position_band_validation_gate",
        "goal10d_backtest_failure_attribution_gate",
        "dashboard_daily_report",
        "portfolio_backtest",
        "signal_backtest",
    ]:
        assert workflow[workflow_id]["status"] == "locked_future"
        assert workflow[workflow_id]["implemented_in_repo"] == "false"

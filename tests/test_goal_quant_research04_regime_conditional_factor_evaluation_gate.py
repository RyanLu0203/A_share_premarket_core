from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.research.goal_quant_research04 import (
    AUDIT_PATH,
    CONDITIONAL_FIELDS,
    FACTOR_STATUS_FIELDS,
    FALSE_BOUNDARY_KEYS,
    MANIFEST_PATH,
    SIZE_LIMIT_BYTES,
    TRANSITION_FIELDS,
    audit_goal_quant_research04_gate,
    evaluate_goal_quant_research04,
    run_goal_quant_research04_gate,
)

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_HEADER_TOKENS = {"forward_return_1d", "forward_return_5d", "forward_return_20d", "benchmark_excess_return_1d", "benchmark_excess_return_5d", "benchmark_excess_return_20d"}


def _workflow() -> dict[str, dict[str, str]]:
    with (ROOT / "configs/project/workflow_status.csv").open(newline="", encoding="utf-8") as handle:
        return {row["workflow_id"]: row for row in csv.DictReader(handle)}


def test_quant04_summary_headers_exclude_raw_forward_return_fields() -> None:
    for fields in (CONDITIONAL_FIELDS, FACTOR_STATUS_FIELDS, TRANSITION_FIELDS):
        assert not (set(fields) & FORBIDDEN_HEADER_TOKENS)
        for field in fields:
            assert not field.startswith("forward_return_")
            assert not field.startswith("benchmark_excess_return_")


def test_quant04_evaluate_regime_conditional_and_preserves_ready_factor_count() -> None:
    result = evaluate_goal_quant_research04(ROOT)
    manifest = result["manifest"]
    assert manifest["status"] in {"PASS", "PASS_WITH_WARNINGS"}
    assert manifest["regime_conditioning_applied"] is True
    assert manifest["factor_evaluation_performed"] is True
    assert manifest["no_lookahead_evaluation_passed"] is True
    assert manifest["leakage_pit_checks_passed"] is True
    # Anti-overfitting / governance: regime slicing must not manufacture readiness.
    assert manifest["ready_factor_count"] == 0
    assert manifest["factor_overall_status_row_count"] == 30
    assert manifest["goal_rec_tiering01_locked_future"] is True
    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    valid_states = {"not_ready", "conditionally_useful", "ready"}
    assert all(row["regime_conditional_status"] in valid_states for row in result["conditional_rows"])
    assert all(row["overall_factor_status"] in valid_states for row in result["factor_status_rows"])
    assert all(row["candidate_for_rec_tiering"] == "false" for row in result["factor_status_rows"])
    assert {row["no_lookahead_status"] for row in result["conditional_rows"]} == {"passed_current_or_past_only"}


def test_quant04_gate_runs_and_audit_passes() -> None:
    assert run_goal_quant_research04_gate(ROOT)
    assert audit_goal_quant_research04_gate(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")
    manifest = json.loads((ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))
    assert manifest["mode"] == "research_only_regime_conditional_factor_evaluation_gate"
    for path in manifest["output_artifacts"]:
        assert (ROOT / path).stat().st_size < SIZE_LIMIT_BYTES


def test_quant04_workflow_implemented_and_rec_tiering_stays_locked() -> None:
    run_goal_quant_research04_gate(ROOT)
    workflow = _workflow()
    q04 = workflow["goal_quant_research04_regime_conditional_factor_evaluation_gate"]
    assert q04["status"] == "implemented_research_only"
    assert q04["implemented_in_repo"] == "true"
    rec = workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]
    assert rec["status"] == "locked_future"
    assert rec["implemented_in_repo"] == "false"
    assert rec["depends_on"] == "goal_quant_research04_regime_conditional_factor_evaluation_gate"
    assert workflow["goal10b4_recommendation_backtest_revalidation"]["status"] == "locked_future"
    assert workflow["dashboard_daily_report"]["status"] == "locked_future"

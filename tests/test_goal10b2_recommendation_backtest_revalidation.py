from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.backtest.goal10b2 import (
    AUDIT_PATH,
    FALSE_BOUNDARY_KEYS,
    HORIZON_COVERAGE_PATH,
    MANIFEST_PATH,
    RECOMMENDATION_METRICS_PATH,
    SNAPSHOT_PATH,
    SYMBOL_METRICS_PATH,
    audit_goal10b2_recommendation_backtest_revalidation,
    run_goal10b2_recommendation_backtest_revalidation,
)

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal10b2_runner_is_review_only_and_deterministic() -> None:
    assert run_goal10b2_recommendation_backtest_revalidation(ROOT)
    first = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert run_goal10b2_recommendation_backtest_revalidation(ROOT)
    second = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert first == second
    assert audit_goal10b2_recommendation_backtest_revalidation(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")


def test_goal10b2_revalidates_dc02_multi_symbol_rows() -> None:
    assert run_goal10b2_recommendation_backtest_revalidation(ROOT)
    manifest = _json(MANIFEST_PATH)
    snapshot = _rows(SNAPSHOT_PATH)
    recommendation_metrics = _rows(RECOMMENDATION_METRICS_PATH)
    symbol_metrics = _rows(SYMBOL_METRICS_PATH)
    horizon = _rows(HORIZON_COVERAGE_PATH)

    assert manifest["status"] == "PASS_WITH_WARNINGS"
    assert manifest["input_snapshot_row_count"] == 8
    assert manifest["unique_symbols"] == 2
    assert len(snapshot) == 8
    assert {row["actionability_status"] for row in snapshot} == {"never_actionable"}
    assert len(recommendation_metrics) == 1
    assert len(symbol_metrics) == 2
    assert {row["horizon"]: row["available_rows"] for row in horizon} == {"1d": "8", "3d": "0", "5d": "0", "20d": "0"}


def test_goal10b2_preserves_boundaries_and_workflow() -> None:
    assert run_goal10b2_recommendation_backtest_revalidation(ROOT)
    manifest = _json(MANIFEST_PATH)
    workflow = _workflow()

    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert manifest["review_only_revalidation_generated"] is True
    assert manifest["goal_v1_diagnostic_coverage02_inputs_never_actionable"] is True
    assert workflow["goal10b2_recommendation_backtest_revalidation"]["status"] == "implemented_review_only"
    assert workflow["goal10b2_recommendation_backtest_revalidation"]["implemented_in_repo"] == "true"
    assert workflow["goal10b2_recommendation_backtest_revalidation"]["depends_on"] == "goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"
    assert workflow["goal10c_backtest_cost_slippage_sensitivity_gate"]["depends_on"] == "goal10b2_recommendation_backtest_revalidation"
    assert workflow["goal10d_backtest_failure_attribution_gate"]["status"] == "locked_future"
    assert workflow["dashboard_daily_report"]["status"] == "locked_future"

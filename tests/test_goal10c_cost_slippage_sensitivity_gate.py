from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.backtest.goal10c import (
    AUDIT_PATH,
    FALSE_BOUNDARY_KEYS,
    GROUP_METRICS_PATH,
    MANIFEST_PATH,
    SENSITIVITY_PATH,
    SNAPSHOT_PATH,
    audit_goal10c_cost_slippage_sensitivity_gate,
    run_goal10c_cost_slippage_sensitivity_gate,
)
from ashare_premarket.backtest.goal10b2 import run_goal10b2_recommendation_backtest_revalidation

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal10c_runner_is_review_only_and_deterministic() -> None:
    assert run_goal10b2_recommendation_backtest_revalidation(ROOT)
    assert run_goal10c_cost_slippage_sensitivity_gate(ROOT)
    first = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert run_goal10c_cost_slippage_sensitivity_gate(ROOT)
    second = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert first == second
    assert audit_goal10c_cost_slippage_sensitivity_gate(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")


def test_goal10c_generates_position_band_sensitivity_rows() -> None:
    assert run_goal10b2_recommendation_backtest_revalidation(ROOT)
    assert run_goal10c_cost_slippage_sensitivity_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    snapshot = _rows(SNAPSHOT_PATH)
    sensitivity = _rows(SENSITIVITY_PATH)
    group_metrics = _rows(GROUP_METRICS_PATH)

    assert manifest["status"] == "PASS_WITH_WARNINGS"
    assert manifest["input_snapshot_row_count"] == 8
    assert manifest["sensitivity_row_count"] == 24
    assert len(snapshot) == 8
    assert len(sensitivity) == 24
    assert len(group_metrics) == 3
    assert {row["position_actionability_status"] for row in snapshot} == {"never_actionable"}
    assert {row["total_cost_bps"] for row in sensitivity} == {"0", "10", "20"}


def test_goal10c_preserves_locked_execution_boundaries() -> None:
    assert run_goal10b2_recommendation_backtest_revalidation(ROOT)
    assert run_goal10c_cost_slippage_sensitivity_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    workflow = _workflow()

    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert manifest["review_only_cost_slippage_sensitivity_generated"] is True
    assert manifest["dc02_position_inputs_never_actionable"] is True
    assert workflow["goal10c_backtest_cost_slippage_sensitivity_gate"]["status"] == "implemented_review_only"
    assert workflow["goal10c_backtest_cost_slippage_sensitivity_gate"]["implemented_in_repo"] == "true"
    assert workflow["goal10c_backtest_cost_slippage_sensitivity_gate"]["depends_on"] == "goal10b2_recommendation_backtest_revalidation"
    assert workflow["goal10d_backtest_failure_attribution_gate"]["status"] == "locked_future"
    assert workflow["dashboard_daily_report"]["status"] == "locked_future"
    assert workflow["portfolio_backtest"]["status"] == "locked_future"

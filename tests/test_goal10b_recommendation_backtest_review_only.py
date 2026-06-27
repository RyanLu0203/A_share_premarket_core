from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.backtest.goal10b import (
    AUDIT_PATH,
    FALSE_BOUNDARY_KEYS,
    IC_RANK_IC_SUMMARY_PATH,
    MANIFEST_PATH,
    RECOMMENDATION_GROUP_METRICS_PATH,
    RISK_SEVERITY_GROUP_METRICS_PATH,
    SNAPSHOT_PATH,
    WARNING_GROUP_METRICS_PATH,
    audit_goal10b_recommendation_backtest_review_only,
    run_goal10b_recommendation_backtest_review_only,
)

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal10b_runner_is_review_only_and_deterministic() -> None:
    assert run_goal10b_recommendation_backtest_review_only(ROOT)
    first = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert run_goal10b_recommendation_backtest_review_only(ROOT)
    second = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert first == second
    assert audit_goal10b_recommendation_backtest_review_only(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")


def test_goal10b_snapshot_applies_t_plus_1_alignment_and_keeps_non_actionable_status() -> None:
    assert run_goal10b_recommendation_backtest_review_only(ROOT)
    snapshot = _rows(SNAPSHOT_PATH)
    manifest = _json(MANIFEST_PATH)
    assert len(snapshot) == 100
    assert manifest["input_snapshot_row_count"] == 100
    assert manifest["evaluable_row_count"] == 99
    assert {row["actionability_status"] for row in snapshot} == {"never_actionable"}
    assert {row["diagnostic_mode"] for row in snapshot} == {"review_only"}
    evaluable = [row for row in snapshot if row["evaluation_status"] == "evaluable"]
    assert all(row["execution_date"] > row["signal_date"] for row in evaluable)
    assert all(row["forward_return_1d"] for row in evaluable)
    assert all(row["forward_return_5d"] for row in evaluable)
    assert all(row["forward_return_20d"] == "" for row in snapshot)
    assert "missing_forward_return_20d" in manifest["warnings"]


def test_goal10b_group_metrics_and_ic_warning_are_contract_complete() -> None:
    assert run_goal10b_recommendation_backtest_review_only(ROOT)
    recommendation_metrics = _rows(RECOMMENDATION_GROUP_METRICS_PATH)
    risk_metrics = _rows(RISK_SEVERITY_GROUP_METRICS_PATH)
    warning_metrics = _rows(WARNING_GROUP_METRICS_PATH)
    ic_summary = _rows(IC_RANK_IC_SUMMARY_PATH)

    assert recommendation_metrics
    assert recommendation_metrics[0]["recommendation_eligibility"] == "blocked_high_risk"
    assert recommendation_metrics[0]["actionability_status"] == "never_actionable"
    for field in [
        "mean_forward_return_1d",
        "median_forward_return_1d",
        "mean_forward_return_5d",
        "median_forward_return_5d",
        "hit_rate_1d",
        "hit_rate_5d",
        "benchmark_excess_return_1d",
        "benchmark_excess_return_5d",
    ]:
        assert recommendation_metrics[0][field] != ""
    assert recommendation_metrics[0]["mean_forward_return_20d"] == ""
    assert risk_metrics[0]["risk_severity"] == "HIGH"
    assert risk_metrics[0]["row_count"] == "99"
    assert len(warning_metrics) >= 7
    assert ic_summary[0]["status"] == "not_computed"
    assert ic_summary[0]["warning_code"] == "insufficient_ranking_variation"


def test_goal10b_preserves_locked_boundaries_and_workflow_status() -> None:
    assert run_goal10b_recommendation_backtest_review_only(ROOT)
    manifest = _json(MANIFEST_PATH)
    workflow = _workflow()
    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert manifest["review_only_backtest_diagnostics_generated"] is True
    assert manifest["goal10c_locked_future"] is True
    assert manifest["goal10d_locked_future"] is True
    assert manifest["dashboard_daily_report_locked_future"] is True
    assert workflow["goal10b_backtest_review_only_validation_gate"]["status"] == "implemented_review_only"
    assert workflow["goal10b_backtest_review_only_validation_gate"]["implemented_in_repo"] == "true"
    assert workflow["goal10c_backtest_cost_slippage_sensitivity_gate"]["status"] in {"locked_future", "implemented_review_only"}
    assert workflow["goal10d_backtest_failure_attribution_gate"]["status"] == "locked_future"
    assert workflow["dashboard_daily_report"]["status"] == "locked_future"
    assert workflow["signal_backtest"]["status"] == "locked_future"
    assert workflow["portfolio_backtest"]["status"] == "locked_future"

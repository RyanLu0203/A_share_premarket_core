from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.backtest.goal10b3 import (
    AUDIT_PATH,
    FALSE_BOUNDARY_KEYS,
    GROUP_IMBALANCE_PATH,
    HORIZON_COVERAGE_PATH,
    MANIFEST_PATH,
    RECOMMENDATION_METRICS_PATH,
    RISK_SEVERITY_METRICS_PATH,
    SNAPSHOT_PATH,
    SYMBOL_METRICS_PATH,
    audit_goal10b3_dc03_recommendation_revalidation_gate,
    run_goal10b3_dc03_recommendation_revalidation_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal10b3_runner_is_review_only_and_deterministic() -> None:
    assert run_goal10b3_dc03_recommendation_revalidation_gate(ROOT)
    first = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert run_goal10b3_dc03_recommendation_revalidation_gate(ROOT)
    second = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert first == second
    assert audit_goal10b3_dc03_recommendation_revalidation_gate(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")


def test_goal10b3_revalidates_dc03_source_backed_rows() -> None:
    assert run_goal10b3_dc03_recommendation_revalidation_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    snapshot = _rows(SNAPSHOT_PATH)
    recommendation_metrics = _rows(RECOMMENDATION_METRICS_PATH)
    risk_metrics = _rows(RISK_SEVERITY_METRICS_PATH)
    symbol_metrics = _rows(SYMBOL_METRICS_PATH)
    horizon = _rows(HORIZON_COVERAGE_PATH)
    imbalance = _rows(GROUP_IMBALANCE_PATH)

    assert manifest["status"] == "PASS_WITH_WARNINGS"
    assert manifest["input_snapshot_row_count"] == 6000
    assert manifest["unique_symbols"] == 50
    assert manifest["unique_trade_dates"] == 120
    assert len(snapshot) == 6000
    assert {row["actionability_status"] for row in snapshot} == {"never_actionable"}
    assert {row["recommendation_eligibility_status"] for row in snapshot} == {
        "eligible_for_review_only_revalidation_never_actionable",
        "blocked_review_only_source_risk",
    }
    assert len(recommendation_metrics) == 2
    assert len(risk_metrics) == 2
    assert len(symbol_metrics) == 50
    assert {row["horizon"]: row["forward_return_available_rows"] for row in horizon} == {"1d": "6000", "5d": "6000", "20d": "6000"}
    assert {row["horizon"]: row["missing_label_rows"] for row in horizon} == {"1d": "0", "5d": "0", "20d": "0"}
    assert any(row["diagnostic_name"] == "group_imbalance_warning" and row["diagnostic_status"] == "PASS_WITH_WARNINGS" for row in imbalance)
    assert any(row["diagnostic_name"] == "small_blocked_group_warning" and row["diagnostic_status"] == "PASS_WITH_WARNINGS" for row in imbalance)


def test_goal10b3_preserves_boundaries_and_workflow() -> None:
    assert run_goal10b3_dc03_recommendation_revalidation_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    workflow = _workflow()

    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert manifest["review_only_dc03_revalidation_generated"] is True
    assert manifest["used_dc03_source_backed_recommendation_diagnostics_only"] is True
    assert manifest["used_provider02b_source_backed_panel_only"] is True
    assert manifest["recommendation_group_variation_available"] is True
    assert manifest["group_imbalance_warning"] is True
    assert manifest["small_blocked_group_warning"] is True
    assert manifest["recommendation_revalidation_signal_weak_or_unreliable"] is True
    assert manifest["recommendation_revalidation_signal_available"] is False
    assert manifest["position_outputs_not_evaluated_in_goal10b3"] is True
    assert workflow["goal10b3_recommendation_backtest_revalidation"]["status"] == "implemented_review_only"
    assert workflow["goal10b3_recommendation_backtest_revalidation"]["implemented_in_repo"] == "true"
    assert workflow["goal10b3_recommendation_backtest_revalidation"]["depends_on"] == "goal_v1_diagnostic_coverage03_multi_provider_diagnostics"
    assert workflow["goal10d_backtest_failure_attribution_gate"]["status"] == "locked_future"
    assert workflow["dashboard_daily_report"]["status"] == "locked_future"
    assert workflow["portfolio_backtest"]["status"] == "locked_future"

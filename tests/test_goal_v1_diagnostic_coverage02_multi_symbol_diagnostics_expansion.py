from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.diagnostics.goal_v1_diagnostic_coverage02 import (
    AUDIT_PATH,
    FALSE_BOUNDARY_KEYS,
    MANIFEST_PATH,
    POSITION_DIAGNOSTICS_PATH,
    RECOMMENDATION_DIAGNOSTICS_PATH,
    RISK_DIAGNOSTICS_PATH,
    audit_goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion,
    run_goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal_v1_diagnostic_coverage02_runner_is_deterministic_and_auditable() -> None:
    assert run_goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion(ROOT)
    first = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert run_goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion(ROOT)
    second = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert first == second
    assert audit_goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")


def test_goal_v1_diagnostic_coverage02_generates_non_actionable_multi_symbol_diagnostics() -> None:
    assert run_goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion(ROOT)
    manifest = _json(MANIFEST_PATH)
    risk_rows = _rows(RISK_DIAGNOSTICS_PATH)
    recommendation_rows = _rows(RECOMMENDATION_DIAGNOSTICS_PATH)
    position_rows = _rows(POSITION_DIAGNOSTICS_PATH)

    assert manifest["status"] == "PASS_WITH_WARNINGS"
    assert manifest["multi_symbol_diagnostics_generated"] is True
    assert manifest["risk_diagnostic_row_count"] == 8
    assert manifest["recommendation_diagnostic_row_count"] == 8
    assert manifest["position_band_diagnostic_row_count"] == 8
    assert manifest["unique_symbols"] == 2
    assert manifest["symbols"] == ["002475.SZ", "600036.SH"]
    assert manifest["keys_match_across_risk_recommendation_position"] is True
    assert manifest["forward_return_20d_available"] is False
    assert manifest["multi_horizon_backtest_ready"] is False
    assert all(row["risk_severity"] == "HIGH" for row in risk_rows)
    assert {row["actionability_status"] for row in recommendation_rows} == {"never_actionable"}
    assert {row["position_actionability_status"] for row in position_rows} == {"never_actionable"}
    assert "forward_return_20d_not_available_for_multi_symbol_diagnostics" in manifest["warnings"]


def test_goal_v1_diagnostic_coverage02_preserves_downstream_locks() -> None:
    assert run_goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion(ROOT)
    manifest = _json(MANIFEST_PATH)
    workflow = _workflow()

    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert workflow["goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"]["status"] == "implemented_review_only"
    assert workflow["goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"]["depends_on"] == "goal_data_label01_forward_return_label_coverage_expansion"
    assert workflow["goal10b2_recommendation_backtest_revalidation"]["status"] in {"locked_future", "implemented_review_only"}
    assert workflow["goal10b2_recommendation_backtest_revalidation"]["depends_on"] == "goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"
    assert workflow["goal10c_backtest_cost_slippage_sensitivity_gate"]["status"] in {"locked_future", "implemented_review_only"}
    assert workflow["goal10c_backtest_cost_slippage_sensitivity_gate"]["depends_on"] == "goal10b2_recommendation_backtest_revalidation"
    assert workflow["goal10d_backtest_failure_attribution_gate"]["status"] == "locked_future"
    assert workflow["dashboard_daily_report"]["status"] == "locked_future"

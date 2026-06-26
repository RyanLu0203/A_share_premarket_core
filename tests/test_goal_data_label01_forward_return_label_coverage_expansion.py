from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.labels.goal_data_label01 import (
    AUDIT_PATH,
    FALSE_BOUNDARY_KEYS,
    LABEL_COVERAGE_SUMMARY_PATH,
    LABEL_SAMPLE_PATH,
    MANIFEST_PATH,
    audit_goal_data_label01_forward_return_label_coverage_expansion,
    run_goal_data_label01_forward_return_label_coverage_expansion,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal_data_label01_runner_is_deterministic_and_auditable() -> None:
    assert run_goal_data_label01_forward_return_label_coverage_expansion(ROOT)
    first = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert run_goal_data_label01_forward_return_label_coverage_expansion(ROOT)
    second = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert first == second
    assert audit_goal_data_label01_forward_return_label_coverage_expansion(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")


def test_goal_data_label01_expands_forward_return_horizon_coverage_without_backtests() -> None:
    assert run_goal_data_label01_forward_return_label_coverage_expansion(ROOT)
    manifest = _json(MANIFEST_PATH)
    rows = _rows(LABEL_SAMPLE_PATH)
    summary = {row["horizon"]: row for row in _rows(LABEL_COVERAGE_SUMMARY_PATH)}

    assert manifest["status"] == "PASS_WITH_WARNINGS"
    assert manifest["forward_return_label_coverage_expanded"] is True
    assert manifest["forward_return_20d_labels_generated"] is True
    assert manifest["label_row_count"] == 100
    assert manifest["label_unique_symbols"] == 1
    assert manifest["label_ready_20d_rows"] == 80
    assert summary["20d"]["label_ready_rows"] == "80"
    assert any(row["fwd_20d_return"] and row["excess_fwd_20d_return"] for row in rows)
    assert all(row["diagnostic_join_ready"] == "false" for row in rows)
    assert manifest["diagnostic_join_ready"] is False
    assert "goal08b_diagnostics_not_aligned_to_expanded_label_dates" in manifest["warnings"]


def test_goal_data_label01_preserves_locked_boundaries() -> None:
    assert run_goal_data_label01_forward_return_label_coverage_expansion(ROOT)
    manifest = _json(MANIFEST_PATH)
    workflow = _workflow()
    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert workflow["goal_data_label01_forward_return_label_coverage_expansion"]["status"] == "implemented_review_only"
    assert workflow["goal_data_label01_forward_return_label_coverage_expansion"]["depends_on"] == "goal10b1_backtest_coverage_repair_gate"
    assert workflow["goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"]["status"] == "locked_future"
    assert workflow["goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"]["depends_on"] == "goal_data_label01_forward_return_label_coverage_expansion"
    assert workflow["goal10b2_recommendation_backtest_revalidation"]["status"] == "locked_future"
    assert workflow["goal10b2_recommendation_backtest_revalidation"]["depends_on"] == "goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"
    assert workflow["goal10c_backtest_cost_slippage_sensitivity_gate"]["status"] == "locked_future"
    assert workflow["goal10c_backtest_cost_slippage_sensitivity_gate"]["depends_on"] == "goal10b2_recommendation_backtest_revalidation"
    assert workflow["dashboard_daily_report"]["status"] == "locked_future"

from __future__ import annotations

import csv
from pathlib import Path

from ashare_premarket.validation.stage6c import audit_stage6c_leakage_and_boundary, run_stage6c_walk_forward_validation


ROOT = Path(__file__).resolve().parents[1]


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_goal06c_walk_forward_preserves_chronological_order() -> None:
    run_stage6c_walk_forward_validation(ROOT)
    rows = _rows("outputs/stage6c/STAGE6C_walk_forward_diagnostics.csv")
    assert rows
    for row in rows:
        assert row["train_start_date"] <= row["train_end_date"]
        assert row["train_end_date"] < row["validation_start_date"]
        assert row["validation_start_date"] <= row["validation_end_date"]


def test_goal06c_boundary_locks_and_workflow_status() -> None:
    assert audit_stage6c_leakage_and_boundary(ROOT)
    workflow = {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}
    assert workflow["goal06c_expanded_validation_ranking"]["status"] == "implemented_review_only"
    assert workflow["goal06d_model_comparison_calibration"]["status"] == "implemented_review_only"
    assert workflow["goal06d_model_comparison_calibration"]["allowed_next_action"] == "fix_goal06d_model_stability_or_calibration_warnings"
    assert workflow["goal07a_risk_overlay_design"]["status"] == "implemented_design_only"
    goal07b = workflow["goal07b_risk_overlay_calculation"]
    assert goal07b["status"] in {"locked_future", "future_review_only", "implemented_review_only"}
    assert goal07b["implemented_in_repo"] == ("true" if goal07b["status"] == "implemented_review_only" else "false")
    assert workflow["position_band_recommendation"]["status"] == "locked_future"
    assert workflow["dashboard_daily_report"]["status"] == "locked_future"
    assert workflow["paper_trading_journal"]["status"] == "locked_future"
    assert workflow["broker_live_trading"]["status"] == "locked_future"
    assert workflow["production_db_writes"]["status"] == "locked_future"
    assert workflow["production_model_promotion"]["status"] == "locked_future"
    assert workflow["dqn_rl_mainline"]["status"] == "deleted_from_active_mainline"

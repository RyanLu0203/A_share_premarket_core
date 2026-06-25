from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


LOCKED_ROWS = {
    "dashboard_daily_report",
    "paper_trading_journal",
    "broker_live_trading",
    "production_db_writes",
    "production_model_promotion",
}


def test_goal06d1_keeps_goal07a_design_only_and_downstream_locked() -> None:
    with (ROOT / "configs/project/workflow_status.csv").open(newline="", encoding="utf-8") as handle:
        workflow = {row["workflow_id"]: row for row in csv.DictReader(handle)}
    assert workflow["goal06d1_calibration_stability_warning_repair"]["status"] == "implemented_review_only"
    assert workflow["goal06d1_calibration_stability_warning_repair"]["allowed_next_action"] in {
        "prepare_goal07a_risk_overlay_design_only",
        "proceed_to_goal07a_design_only_with_warnings",
        "continue_goal06d_warning_repair",
    }
    assert workflow["goal07a_risk_overlay_design"]["status"] == "implemented_design_only"
    goal07b = workflow["goal07b_risk_overlay_calculation"]
    assert goal07b["status"] in {"locked_future", "future_review_only", "implemented_review_only"}
    assert goal07b["implemented_in_repo"] == ("true" if goal07b["status"] == "implemented_review_only" else "false")
    assert workflow["position_band_recommendation"]["status"] in {"locked_future", "future_review_only"}
    assert workflow["position_band_recommendation"]["implemented_in_repo"] == "false"
    for workflow_id in LOCKED_ROWS:
        assert workflow[workflow_id]["status"] == "locked_future"
    assert workflow["dqn_rl_mainline"]["status"] == "deleted_from_active_mainline"
    assert workflow["v2_factor_research_upgrade"]["status"] == "planned_locked"


def test_goal06d1_boundary_audit_locks_v2_and_downstream() -> None:
    text = (ROOT / "outputs/audits/goal06d1_boundary_lock_audit.md").read_text(encoding="utf-8")
    assert "Status: `PASS`" in text
    assert "GOAL-07A remains design-only" in text
    assert "V2 factor research remains planned_locked" in text

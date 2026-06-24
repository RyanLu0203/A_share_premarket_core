from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _workflow() -> dict[str, dict[str, str]]:
    with (ROOT / "configs/project/workflow_status.csv").open(newline="", encoding="utf-8") as handle:
        return {row["workflow_id"]: row for row in csv.DictReader(handle)}


def test_goal07a_is_design_only_and_goal07b_remains_locked() -> None:
    workflow = _workflow()
    assert workflow["goal07a_risk_overlay_design"]["status"] == "implemented_design_only"
    assert workflow["goal07a_risk_overlay_design"]["allowed_next_action"] == "prepare_goal07b_design_review_or_fix_goal07a_warnings"
    assert workflow["goal07b_risk_overlay_calculation"]["status"] in {"locked_future", "future_review_only"}
    assert workflow["goal07b_risk_overlay_calculation"]["implemented_in_repo"] == "false"
    assert workflow["position_band_recommendation"]["status"] == "locked_future"
    assert workflow["dashboard_daily_report"]["status"] == "locked_future"
    assert workflow["paper_trading_journal"]["status"] == "locked_future"
    assert workflow["broker_live_trading"]["status"] == "locked_future"
    assert workflow["production_db_writes"]["status"] == "locked_future"
    assert workflow["production_model_promotion"]["status"] == "locked_future"
    assert workflow["dqn_rl_mainline"]["status"] == "deleted_from_active_mainline"


def test_goal07a_boundary_audit_passes() -> None:
    text = (ROOT / "outputs/audits/goal07a_boundary_lock_audit.md").read_text(encoding="utf-8")
    assert "Status: `PASS`" in text
    assert "GOAL-07B remains not implemented" in text

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_goal06d_and_downstream_remain_locked() -> None:
    status = (ROOT / "configs/project/workflow_status.csv").read_text(encoding="utf-8")
    assert "goal06c5_engineering_data_coverage_storage_panel_expansion" in status
    assert "goal06c6_source_backed_engineering_pilot_bundle" in status
    assert "goal06d_model_comparison_calibration,GOAL-06D Model Comparison and Calibration,GOAL-06D,future_review_only" in status
    assert "review_only_entry_allowed_after_goal06c7_engineering_pilot" in status
    for workflow_id in [
        "goal07b_risk_overlay_calculation",
        "position_band_recommendation",
        "dashboard_daily_report",
        "paper_trading_journal",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
    ]:
        assert f"{workflow_id}," in status and ",locked_future," in status


def test_active_source_has_no_downstream_imports() -> None:
    locked_terms = ["dashboard", "dqn", "paper_trading", "broker", "live_trading"]
    for path in (ROOT / "src").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name.lower() for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [(node.module or "").lower()]
            assert not any(term in name for name in names for term in locked_terms)

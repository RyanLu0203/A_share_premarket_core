from __future__ import annotations

import ast
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_goal06d_and_downstream_remain_locked() -> None:
    with (ROOT / "configs/project/workflow_status.csv").open(newline="", encoding="utf-8") as handle:
        rows = {row["workflow_id"]: row for row in csv.DictReader(handle)}
    assert rows["goal06c5_engineering_data_coverage_storage_panel_expansion"]["status"] == "implemented_review_only"
    assert rows["goal06c6_source_backed_engineering_pilot_bundle"]["status"] == "implemented_review_only"
    assert rows["goal06d_model_comparison_calibration"]["status"] == "implemented_review_only"
    assert rows["goal06d_model_comparison_calibration"]["allowed_next_action"] == "fix_goal06d_model_stability_or_calibration_warnings"
    assert rows["goal07a_risk_overlay_design"]["status"] == "implemented_design_only"
    assert rows["goal07b_risk_overlay_calculation"]["status"] in {"locked_future", "future_review_only"}
    assert rows["goal07b_risk_overlay_calculation"]["implemented_in_repo"] == "false"
    for workflow_id in [
        "position_band_recommendation",
        "dashboard_daily_report",
        "paper_trading_journal",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
    ]:
        assert rows[workflow_id]["status"] == "locked_future"


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

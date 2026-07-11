from __future__ import annotations

import ast
import csv
import json
from pathlib import Path

from ashare_premarket.core.boundary import forbidden_locked_import_terms

ROOT = Path(__file__).resolve().parents[1]


def test_goal06d_and_downstream_remain_locked() -> None:
    with (ROOT / "configs/project/workflow_status.csv").open(newline="", encoding="utf-8") as handle:
        rows = {row["workflow_id"]: row for row in csv.DictReader(handle)}
    assert rows["goal06c5_engineering_data_coverage_storage_panel_expansion"]["status"] == "implemented_review_only"
    assert rows["goal06c6_source_backed_engineering_pilot_bundle"]["status"] == "implemented_review_only"
    assert rows["goal06d_model_comparison_calibration"]["status"] == "implemented_review_only"
    assert rows["goal06d_model_comparison_calibration"]["allowed_next_action"] == "fix_goal06d_model_stability_or_calibration_warnings"
    assert rows["goal07a_risk_overlay_design"]["status"] == "implemented_design_only"
    goal07b = rows["goal07b_risk_overlay_calculation"]
    assert goal07b["status"] in {"locked_future", "future_review_only", "implemented_review_only"}
    assert goal07b["implemented_in_repo"] == ("true" if goal07b["status"] == "implemented_review_only" else "false")
    goal09 = rows["position_band_recommendation"]
    assert goal09["status"] in {"locked_future", "future_review_only", "implemented_review_only"}
    assert goal09["implemented_in_repo"] == ("true" if goal09["status"] == "implemented_review_only" else "false")
    for workflow_id in [
        "dashboard_daily_report",
        "paper_trading_journal",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
    ]:
        assert rows[workflow_id]["status"] == "locked_future"
    assert rows["goal_premarket_research_position_workspace_dashboard01"]["status"] == "implemented_research_only"


def test_active_source_has_no_downstream_imports() -> None:
    locked_terms = ["dashboard", "dqn", "paper_trading", "broker", "live_trading"]
    capabilities = json.loads((ROOT / "configs/project/locked_capabilities.json").read_text(encoding="utf-8"))
    assert capabilities["dashboard"] is False
    assert capabilities["goal_premarket_research_position_workspace_dashboard01_gate"] == "implemented_research_only"
    for path in (ROOT / "src").rglob("*.py"):
        relative = path.relative_to(ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name.lower() for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [(node.module or "").lower()]
            for name in names:
                assert not forbidden_locked_import_terms(ROOT, name, relative, locked_terms)

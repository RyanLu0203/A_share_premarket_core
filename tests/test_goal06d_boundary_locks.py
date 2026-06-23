from __future__ import annotations

import ast
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCKED_IDS = {
    "goal07b_risk_overlay_calculation",
    "position_band_recommendation",
    "dashboard_daily_report",
    "paper_trading_journal",
    "broker_live_trading",
    "production_db_writes",
    "production_model_promotion",
}


def _workflow() -> dict[str, dict[str, str]]:
    with (ROOT / "configs/project/workflow_status.csv").open(newline="", encoding="utf-8") as handle:
        return {row["workflow_id"]: row for row in csv.DictReader(handle)}


def test_goal06d_keeps_goal07a_design_only_and_downstream_locked() -> None:
    workflow = _workflow()

    assert workflow["goal06d_model_comparison_calibration"]["status"] == "implemented_review_only"
    assert workflow["goal06d_model_comparison_calibration"]["allowed_next_action"] == "fix_goal06d_model_stability_or_calibration_warnings"
    assert workflow["goal07a_risk_overlay_design"]["status"] == "future_design_only"
    assert workflow["goal07a_risk_overlay_design"]["allowed_next_action"] == "locked_until_goal06d_pass"
    assert {workflow[workflow_id]["status"] for workflow_id in LOCKED_IDS} == {"locked_future"}


def test_goal06d_scripts_do_not_import_locked_downstream_modules() -> None:
    locked_fragments = {
        "risk_overlay",
        "position_band",
        "recommendation",
        "dashboard",
        "paper_trading",
        "broker",
        "live_trading",
        "production_model",
        "dqn",
        "reinforcement_learning",
    }
    paths = [ROOT / "src/ashare_premarket/models/goal06d.py", *sorted((ROOT / "scripts").glob("*goal06d*.py"))]
    failures: list[str] = []
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name.lower() for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [(node.module or "").lower()]
            for name in names:
                if any(fragment in name for fragment in locked_fragments):
                    failures.append(f"{path.name} imports {name}")

    assert failures == []

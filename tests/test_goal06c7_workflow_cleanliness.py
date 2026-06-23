from __future__ import annotations

import csv
from pathlib import Path

from ashare_premarket.validation.workflow_cleanliness import audit_workflow_cleanliness

ROOT = Path(__file__).resolve().parents[1]


def test_goal06c7_workflow_row_allows_only_goal06d_review_only_and_design_only_goal07a() -> None:
    with (ROOT / "configs/project/workflow_status.csv").open(newline="", encoding="utf-8") as handle:
        rows = {row["workflow_id"]: row for row in csv.DictReader(handle)}
    assert rows["goal06c7_provider_ladder_browser_assisted_engineering_data_base_expansion"]["status"] == "implemented_review_only"
    assert rows["goal06c7_provider_ladder_browser_assisted_engineering_data_base_expansion"]["allowed_next_action"] == "allow_goal06d_review_only_after_engineering_pilot"
    assert rows["goal06d_model_comparison_calibration"]["status"] == "implemented_review_only"
    assert rows["goal06d_model_comparison_calibration"]["allowed_next_action"] == "fix_goal06d_model_stability_or_calibration_warnings"
    assert rows["goal07a_risk_overlay_design"]["status"] == "implemented_design_only"
    assert rows["goal07a_risk_overlay_design"]["allowed_next_action"] == "prepare_goal07b_design_review_or_fix_goal07a_warnings"


def test_workflow_cleanliness_audit_passes_or_warns_without_blocking() -> None:
    assert audit_workflow_cleanliness(ROOT)

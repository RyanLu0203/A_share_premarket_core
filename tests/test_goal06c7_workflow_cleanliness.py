from __future__ import annotations

import csv
from pathlib import Path

from ashare_premarket.validation.workflow_cleanliness import audit_workflow_cleanliness

ROOT = Path(__file__).resolve().parents[1]


def test_goal06c7_workflow_row_blocks_goal06d_until_engineering_pilot() -> None:
    with (ROOT / "configs/project/workflow_status.csv").open(newline="", encoding="utf-8") as handle:
        rows = {row["workflow_id"]: row for row in csv.DictReader(handle)}
    assert rows["goal06c7_provider_ladder_browser_assisted_engineering_data_base_expansion"]["status"] == "implemented_review_only"
    assert rows["goal06c7_provider_ladder_browser_assisted_engineering_data_base_expansion"]["allowed_next_action"] == "block_goal06d_until_engineering_pilot"
    assert rows["goal06d_model_comparison_calibration"]["status"] == "future_review_only"
    assert "goal06c7" in rows["goal06d_model_comparison_calibration"]["allowed_next_action"]


def test_workflow_cleanliness_audit_passes_or_warns_without_blocking() -> None:
    assert audit_workflow_cleanliness(ROOT)

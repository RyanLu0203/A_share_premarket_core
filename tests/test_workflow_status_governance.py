from __future__ import annotations

import csv
from pathlib import Path

from ashare_premarket.validation.workflow_status import run_workflow_status_audit


ROOT = Path(__file__).resolve().parents[1]


def _workflow_rows() -> list[dict[str, str]]:
    with (ROOT / "configs/project/workflow_status.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_workflow_status_contract_exists_and_has_required_statuses() -> None:
    rows = _workflow_rows()
    statuses = {row["status"] for row in rows}
    assert "implemented_active" in statuses
    assert "implemented_review_only" in statuses
    assert "implemented_design_only" in statuses
    assert "locked_future" in statuses
    assert "deleted_from_active_mainline" in statuses


def test_goal06c_is_review_only_and_downstream_are_not_implemented_active() -> None:
    rows = {row["workflow_id"]: row for row in _workflow_rows()}
    assert rows["goal06c_expanded_validation_ranking"]["status"] == "implemented_review_only"
    assert rows["goal06d_model_comparison_calibration"]["status"] == "implemented_review_only"
    assert rows["goal06d_model_comparison_calibration"]["allowed_next_action"] == "fix_goal06d_model_stability_or_calibration_warnings"
    assert rows["goal07a_risk_overlay_design"]["status"] == "implemented_design_only"
    assert rows["goal07b0_risk_overlay_review_only_unlock_gate"]["status"] == "implemented_review_only"
    assert rows["goal07b_risk_overlay_calculation"]["status"] == "future_review_only"
    assert rows["goal07b_risk_overlay_calculation"]["implemented_in_repo"] == "false"
    assert rows["position_band_recommendation"]["status"] == "locked_future"
    assert rows["dqn_rl_mainline"]["status"] == "deleted_from_active_mainline"


def test_workflow_status_audit_passes() -> None:
    assert run_workflow_status_audit(ROOT)

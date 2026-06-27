from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.contract_design.goal08b0 import (
    GOAL08B0_ALLOWED_NEXT,
    _forbidden_recommendation_row_outputs,
    audit_goal08b0_recommendation_review_only_unlock_gate,
    run_goal08b0_recommendation_review_only_unlock_gate,
)
from ashare_premarket.review_diagnostics.goal08b import GOAL08B_ALLOWED_NEXT, goal08b_valid_diagnostics_evidence

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _workflow() -> dict[str, dict[str, str]]:
    with (ROOT / "configs/project/workflow_status.csv").open(newline="", encoding="utf-8") as handle:
        return {row["workflow_id"]: row for row in csv.DictReader(handle)}


def test_goal08b0_runner_is_unlock_only_and_deterministic() -> None:
    assert run_goal08b0_recommendation_review_only_unlock_gate(ROOT)
    first = (ROOT / "outputs/audits/goal08b0_recommendation_review_only_unlock_manifest.json").read_text(encoding="utf-8")
    assert run_goal08b0_recommendation_review_only_unlock_gate(ROOT)
    second = (ROOT / "outputs/audits/goal08b0_recommendation_review_only_unlock_manifest.json").read_text(encoding="utf-8")
    assert first == second
    assert audit_goal08b0_recommendation_review_only_unlock_gate(ROOT)


def test_goal08b0_preserves_goal08b_diagnostics_when_valid() -> None:
    assert run_goal08b0_recommendation_review_only_unlock_gate(ROOT)
    workflow = _workflow()
    manifest = _json("outputs/audits/goal08b0_recommendation_review_only_unlock_manifest.json")
    assert workflow["goal08b0_recommendation_review_only_unlock_gate"]["status"] == "implemented_review_only"
    assert workflow["goal08b0_recommendation_review_only_unlock_gate"]["implemented_in_repo"] == "true"
    goal08b = workflow["goal08b_recommendation_review_only_prototype"]
    if goal08b_valid_diagnostics_evidence(ROOT):
        assert goal08b["status"] == "implemented_review_only"
        assert goal08b["implemented_in_repo"] == "true"
        assert goal08b["allowed_next_action"] == GOAL08B_ALLOWED_NEXT
    else:
        assert goal08b["status"] == "future_review_only"
        assert goal08b["implemented_in_repo"] == "false"
        assert goal08b["allowed_next_action"] == GOAL08B0_ALLOWED_NEXT
    assert manifest["mode"] == "review_only_unlock_gate"
    assert manifest["goal08b0_unlock_status"] == "eligible_for_future_review_only_prototype"
    assert manifest["goal08b_target_status"] == goal08b["status"]
    assert manifest["goal08b_implemented_by_this_gate"] is False
    assert manifest["goal08b_implemented_in_repo"] is goal08b_valid_diagnostics_evidence(ROOT)


def test_goal08b0_uses_prior_evidence_and_preserves_non_actionability() -> None:
    assert run_goal08b0_recommendation_review_only_unlock_gate(ROOT)
    manifest = _json("outputs/audits/goal08b0_recommendation_review_only_unlock_manifest.json")
    assert manifest["future_goal08b_input_contract_ready"] is True
    assert manifest["high_risk_actionability_block_preserved"] is True
    assert manifest["goal07b_warnings_propagate_to_future_diagnostics"] is True
    assert manifest["future_recommendation_diagnostics_non_actionable_required"] is True
    assert manifest["storage_prerequisite_ready"] is True
    assert manifest["evidence_basis"] == "prior_pass_or_pass_with_warnings_review_only_and_design_evidence_only_no_live_outputs"
    assert "outputs/audits/goal07b_risk_overlay_calculation_manifest.json" in manifest["evidence_inputs"]
    assert "outputs/audits/goal08a_recommendation_contract_design_manifest.json" in manifest["evidence_inputs"]
    assert "outputs/audits/goal_storage01_local_research_lake_hardening_manifest.json" in manifest["evidence_inputs"]


def test_goal08b0_generates_no_forbidden_outputs() -> None:
    assert run_goal08b0_recommendation_review_only_unlock_gate(ROOT)
    manifest = _json("outputs/audits/goal08b0_recommendation_review_only_unlock_manifest.json")
    forbidden_rows = _forbidden_recommendation_row_outputs(ROOT)
    assert "outputs/diagnostics/goal_v1_diagnostic_coverage02_recommendation_diagnostics.csv" not in forbidden_rows
    for key in [
        "recommendation_diagnostics_rows_generated",
        "recommendation_rows_generated",
        "buy_sell_hold_outputs_generated",
        "target_prices_generated",
        "position_sizing_generated",
        "portfolio_construction_generated",
        "dashboard_generated",
        "paper_trading_enabled",
        "live_trading_enabled",
        "broker_integration_enabled",
        "production_model_behavior_created",
        "database_writes_created",
        "backtests_run",
        "factor_mining_outputs_created",
        "dqn_rl_outputs_created",
        "actionable_outputs_generated",
        "local_lake_files_created",
        "data_coverage_expanded",
        "live_calculation_outputs_used",
        "downstream_stages_unlocked_by_this_gate",
    ]:
        assert manifest[key] is False
    for rel in [
        "outputs/recommendations",
        "outputs/positions",
        "outputs/dashboard",
        "outputs/paper_trading",
        "outputs/live_trading",
        "outputs/backtests",
        "outputs/factors",
        "data/lake",
        "local_data",
    ]:
        assert not (ROOT / rel).exists()

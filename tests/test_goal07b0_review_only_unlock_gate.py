from __future__ import annotations

import copy
import csv
import json
from pathlib import Path

from ashare_premarket.risk_design.goal07b0 import (
    audit_goal07b0_risk_overlay_review_only_unlock_gate,
    evaluate_goal07b0_unlock_gate,
    load_goal07b0_unlock_bundle,
    run_goal07b0_risk_overlay_review_only_unlock_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _workflow() -> dict[str, dict[str, str]]:
    with (ROOT / "configs/project/workflow_status.csv").open(newline="", encoding="utf-8") as handle:
        return {row["workflow_id"]: row for row in csv.DictReader(handle)}


def test_goal07b0_runner_unlocks_only_future_review_eligibility() -> None:
    assert run_goal07b0_risk_overlay_review_only_unlock_gate(ROOT)
    report = (ROOT / "outputs/audits/goal07b0_unlock_gate_report.md").read_text(encoding="utf-8")
    assert "GOAL-07B.0 Risk Overlay Review-Only Unlock Gate: PASS_WITH_WARNINGS" in report
    assert "GOAL-07B target status: `future_review_only`" in report or "GOAL-07B target status: `implemented_review_only`" in report
    assert "GOAL-07B is not implemented by this gate." in report
    assert "No risk calculation was performed by this gate." in report
    assert "Evidence basis: prior PASS/PASS_WITH_WARNINGS design-review reports and manifests only" in report

    manifest = json.loads((ROOT / "outputs/audits/goal07b0_unlock_gate_manifest.json").read_text(encoding="utf-8"))
    assert manifest["goal07b0_unlock_status"] == "eligible_for_future_review_only_prototype"
    assert manifest["goal07b_target_status"] in {"future_review_only", "implemented_review_only"}
    assert manifest["goal07b_implemented_by_this_gate"] is False
    assert manifest["risk_calculation_performed"] is False
    assert manifest["symbol_level_risk_rows_created"] is False
    assert manifest["live_calculation_outputs_used"] is False


def test_goal07b0_audit_wrapper_passes_and_downstream_stays_locked() -> None:
    assert run_goal07b0_risk_overlay_review_only_unlock_gate(ROOT)
    assert audit_goal07b0_risk_overlay_review_only_unlock_gate(ROOT)
    workflow = _workflow()
    assert workflow["goal07b0_risk_overlay_review_only_unlock_gate"]["status"] == "implemented_review_only"
    goal07b = workflow["goal07b_risk_overlay_calculation"]
    assert goal07b["status"] in {"future_review_only", "implemented_review_only"}
    assert goal07b["implemented_in_repo"] == ("true" if goal07b["status"] == "implemented_review_only" else "false")
    for workflow_id in [
        "position_band_recommendation",
        "dashboard_daily_report",
        "paper_trading_journal",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
        "signal_backtest",
        "portfolio_backtest",
        "cost_slippage_sensitivity",
        "failure_attribution",
        "production_hardening",
    ]:
        assert workflow[workflow_id]["status"] == "locked_future"


def test_goal07b0_blocks_without_prior_unlock_readiness() -> None:
    bundle = load_goal07b0_unlock_bundle(ROOT)
    modified = copy.deepcopy(bundle)
    modified["goal07a1_manifest"]["goal07b_unlock_readiness"] = "not_ready_fix_goal07a_warnings"
    review = evaluate_goal07b0_unlock_gate(modified)
    assert review["status"] == "BLOCKED"
    assert "goal07a1_manifest_not_ready_for_unlock" in review["failures"]


def test_goal07b0_detects_forbidden_calculation_outputs() -> None:
    bundle = load_goal07b0_unlock_bundle(ROOT)
    modified = copy.deepcopy(bundle)
    modified["risk_calculation_csv_outputs"] = ["outputs/risk_overlay/example.csv"]
    review = evaluate_goal07b0_unlock_gate(modified)
    assert review["status"] == "BLOCKED"
    assert any("risk_calculation_csv_outputs_present" in failure for failure in review["failures"])


def test_goal07b0_creates_no_forbidden_output_directories_or_rows() -> None:
    existing_risk_outputs = set((ROOT / "outputs").glob("**/*risk_overlay*.csv"))
    assert run_goal07b0_risk_overlay_review_only_unlock_gate(ROOT)
    for rel in [
        "outputs/recommendations",
        "outputs/positions",
        "outputs/dashboard",
        "outputs/paper_trading",
        "outputs/live_trading",
        "outputs/backtests",
        "outputs/factors",
    ]:
        assert not (ROOT / rel).exists()
    assert set((ROOT / "outputs").glob("**/*risk_overlay*.csv")) == existing_risk_outputs

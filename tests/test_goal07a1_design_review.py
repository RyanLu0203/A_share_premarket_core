
from __future__ import annotations

import copy
import csv
import json
from pathlib import Path

from ashare_premarket.risk_design.goal07a1 import (
    classify_goal07a1_upstream_warnings,
    evaluate_goal07a1_design_review,
    load_goal07a1_design_bundle,
    review_goal07a1_input_contract,
    review_goal07a1_output_schema,
    review_goal07a1_rule_catalog,
    review_goal07a1_state_machine,
    run_goal07a1_risk_overlay_design_review_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def test_goal07a1_runner_is_deterministic_and_review_only() -> None:
    assert run_goal07a1_risk_overlay_design_review_gate(ROOT)
    report = (ROOT / "outputs/audits/goal07a1_design_review_report.md").read_text(encoding="utf-8")
    assert "GOAL-07A.1 Risk Overlay Design Review: PASS_WITH_WARNINGS" in report
    assert "GOAL-07B unlock readiness: ready_for_explicit_review_only_unlock" in report
    assert "No risk calculation was performed" in report
    assert "No recommendation/position/dashboard/paper/live/production/backtest/factor-mining/DQN/RL output was created" in report
    manifest = json.loads((ROOT / "outputs/audits/goal07a1_unlock_readiness_manifest.json").read_text(encoding="utf-8"))
    assert manifest["risk_calculation_performed"] is False
    assert manifest["symbol_level_risk_rows_created"] is False


def test_missing_required_goal07a_contract_fields_fail() -> None:
    bundle = load_goal07a1_design_bundle(ROOT)
    contract = copy.deepcopy(bundle["input_contract"])
    contract["required_upstream_datasets"] = []
    review = review_goal07a1_input_contract(contract, bundle["warning_mapping"])
    assert review["status"] == "FAIL"
    assert "required_upstream_datasets_not_explicit" in review["failures"]


def test_forbidden_future_output_schema_terms_are_detected() -> None:
    bundle = load_goal07a1_design_bundle(ROOT)
    schema = copy.deepcopy(bundle["output_schema"])
    schema["allowed_future_schema_fields"].append("recommended_position")
    review = review_goal07a1_output_schema(schema)
    assert review["status"] == "FAIL"
    assert any("forbidden_schema" in failure for failure in review["failures"])


def test_recommendation_and_position_like_fields_are_rejected() -> None:
    bundle = load_goal07a1_design_bundle(ROOT)
    for field in ["buy", "sell", "hold", "portfolio_weight", "broker_action", "production_signal"]:
        schema = copy.deepcopy(bundle["output_schema"])
        schema["allowed_future_schema_fields"].append(field)
        assert review_goal07a1_output_schema(schema)["status"] == "FAIL"


def test_rule_catalog_ambiguity_is_detected() -> None:
    bundle = load_goal07a1_design_bundle(ROOT)
    catalog = copy.deepcopy(bundle["rule_catalog"])
    catalog["rules"][0].pop("risk_domain_id")
    review = review_goal07a1_rule_catalog(catalog)
    assert review["status"] == "FAIL"
    assert any("domain_mapping_ambiguous" in failure for failure in review["failures"])


def test_state_machine_ambiguity_is_detected() -> None:
    bundle = load_goal07a1_design_bundle(ROOT)
    machine = copy.deepcopy(bundle["state_machine"])
    machine["blocked_transitions"] = []
    review = review_goal07a1_state_machine(machine)
    assert review["status"] == "FAIL"
    assert "blocked_transitions_not_explicit" in review["failures"]


def test_upstream_warnings_are_classified() -> None:
    rows = classify_goal07a1_upstream_warnings("", "", ";".join([
        "calibration_not_reliable_for_thresholding",
        "feature_sign_instability_bounded",
        "provider_source_concentration_disclosed",
        "selected_score_variant_weak_rank_signal",
        "single_provider_mode_akshare_direct",
        "weak_target_horizon_rank_signal",
        "target_horizon_calibration_warning",
    ]))
    mapping = {row["warning_code"]: row["classification"] for row in rows}
    assert mapping["missing_required_input_contract_fields"] == "BLOCKER_FOR_07B"
    assert mapping["calibration_not_reliable_for_thresholding"] == "PASS_THROUGH_WARNING"
    assert mapping["single_provider_mode_akshare_direct"] == "DESIGN_REVIEW_WARNING"


def test_goal07a1_does_not_implement_goal07b_itself() -> None:
    assert run_goal07a1_risk_overlay_design_review_gate(ROOT)
    with (ROOT / "configs/project/workflow_status.csv").open(newline="", encoding="utf-8") as handle:
        workflow = {row["workflow_id"]: row for row in csv.DictReader(handle)}
    assert workflow["goal07a1_risk_overlay_design_review_unlock_readiness"]["status"] == "implemented_review_only"
    goal07b = workflow["goal07b_risk_overlay_calculation"]
    assert goal07b["status"] in {"locked_future", "future_review_only", "implemented_review_only"}
    assert goal07b["implemented_in_repo"] == ("true" if goal07b["status"] == "implemented_review_only" else "false")


def test_goal07a1_does_not_create_new_risk_calculation_output_files() -> None:
    existing_risk_outputs = set((ROOT / "outputs").glob("**/*risk_overlay*.csv"))
    assert run_goal07a1_risk_overlay_design_review_gate(ROOT)
    for rel in [
        "outputs/recommendations",
        "outputs/positions",
        "outputs/dashboard",
        "outputs/paper_trading",
        "outputs/live_trading",
        "outputs/factors",
    ]:
        assert not (ROOT / rel).exists()
    assert set((ROOT / "outputs").glob("**/*risk_overlay*.csv")) == existing_risk_outputs


def test_goal07a1_current_bundle_is_ready_with_warnings() -> None:
    bundle = load_goal07a1_design_bundle(ROOT)
    review = evaluate_goal07a1_design_review(bundle)
    assert review["status"] == "PASS_WITH_WARNINGS"
    assert review["goal07b_unlock_readiness"] == "ready_for_explicit_review_only_unlock"
    assert review["goal07b_remains"] in {"locked_future", "future_review_only", "implemented_review_only"}

from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.contract_design.goal08a import (
    GOAL07B_WARNING_CODES,
    audit_goal08a_recommendation_contract_design_gate,
    run_goal08a_recommendation_contract_design_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _workflow() -> dict[str, dict[str, str]]:
    with (ROOT / "configs/project/workflow_status.csv").open(newline="", encoding="utf-8") as handle:
        return {row["workflow_id"]: row for row in csv.DictReader(handle)}


def test_goal08a_runner_is_design_only_and_deterministic() -> None:
    assert run_goal08a_recommendation_contract_design_gate(ROOT)
    first = (ROOT / "outputs/audits/goal08a_recommendation_contract_design_manifest.json").read_text(encoding="utf-8")
    assert run_goal08a_recommendation_contract_design_gate(ROOT)
    second = (ROOT / "outputs/audits/goal08a_recommendation_contract_design_manifest.json").read_text(encoding="utf-8")
    assert first == second
    assert audit_goal08a_recommendation_contract_design_gate(ROOT)


def test_goal08a_contract_requires_goal07b_trade_date_symbol_grain() -> None:
    assert run_goal08a_recommendation_contract_design_gate(ROOT)
    contract = _json("configs/recommendation/goal08a_future_recommendation_input_contract.yaml")
    assert contract["mode"] == "design_only"
    assert contract["source_goal"] == "GOAL-07B"
    assert contract["required_input_grain"] == "trade_date + symbol"
    for field in [
        "trade_date",
        "symbol",
        "risk_severity",
        "risk_state",
        "warning_propagation",
        "upstream_warning_mapping",
        "non_actionable",
        "recommendation_generated",
    ]:
        assert field in contract["required_goal07b_fields"]
    assert contract["source_artifacts"]["rows_are_actionable"] is False


def test_goal08a_schema_is_names_only_with_zero_rows() -> None:
    assert run_goal08a_recommendation_contract_design_gate(ROOT)
    schema = _json("configs/recommendation/goal08a_future_recommendation_schema.yaml")
    assert schema["future_schema_names_only"] is True
    assert schema["empty_schema_sample"]["row_count"] == 0
    assert schema["empty_schema_sample"]["rows"] == []
    forbidden = set(schema["future_schema_fields"]) & set(schema["forbidden_future_schema_fields"])
    assert forbidden == set()


def test_goal08a_propagates_goal07b_warnings_and_blocks_high_risk_actionability() -> None:
    assert run_goal08a_recommendation_contract_design_gate(ROOT)
    policy = _json("configs/recommendation/goal08a_warning_propagation_policy.yaml")
    actionability = _json("configs/recommendation/goal08a_actionability_guardrails.yaml")
    propagated = {row["warning_code"]: row for row in policy["warning_propagation_rules"]}
    assert set(GOAL07B_WARNING_CODES) <= set(propagated)
    assert all(row["propagate_to_future_contract"] is True for row in propagated.values())
    assert actionability["high_risk_severity_blocks_actionable_recommendation"] is True
    assert actionability["high_risk_rule"]["condition"] == "source_goal07b_risk_severity == HIGH"
    assert actionability["high_risk_rule"]["actionable_recommendation_allowed"] is False
    assert actionability["recommendation_like_diagnostic_must_be_non_actionable"] is True


def test_goal08a_workflow_and_manifest_keep_goal08b_and_downstream_locked() -> None:
    assert run_goal08a_recommendation_contract_design_gate(ROOT)
    workflow = _workflow()
    manifest = _json("outputs/audits/goal08a_recommendation_contract_design_manifest.json")
    assert workflow["goal08a_recommendation_contract_design_gate"]["status"] == "implemented_design_only"
    assert workflow["goal08a_recommendation_contract_design_gate"]["implemented_in_repo"] == "true"
    assert workflow["goal08b_recommendation_review_only_prototype"]["status"] in {"locked_future", "future_review_only"}
    assert workflow["goal08b_recommendation_review_only_prototype"]["implemented_in_repo"] == "false"
    assert manifest["mode"] == "design_only"
    assert manifest["future_schema_row_count"] == 0
    assert manifest["high_risk_severity_blocks_actionable_output"] is True
    for key in [
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
    ]:
        assert not (ROOT / rel).exists()

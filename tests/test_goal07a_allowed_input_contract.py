from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _contract() -> dict[str, object]:
    return json.loads((ROOT / "configs/risk/goal07a_allowed_input_contract.yaml").read_text(encoding="utf-8"))


def test_goal07a_allowed_input_contract_contains_all_risk_domains() -> None:
    contract = _contract()
    domains = {row["risk_domain_id"]: row for row in contract["risk_domains"]}
    assert set(domains) == {
        "data_quality_risk",
        "provider_concentration_risk",
        "model_confidence_risk",
        "calibration_risk",
        "feature_stability_risk",
        "target_horizon_risk",
        "market_regime_risk",
        "liquidity_proxy_risk",
        "volatility_risk",
        "gap_risk",
        "source_health_risk",
        "governance_boundary_risk",
    }
    required = {
        "risk_domain_id",
        "description",
        "upstream_evidence_source",
        "allowed_input_fields",
        "future_allowed_output_fields",
        "design_only_rule",
        "blocking_condition_design",
        "downgrade_condition_design",
        "warning_condition_design",
        "forbidden_use_in_goal07a",
    }
    assert all(required <= set(row) for row in domains.values())


def test_goal07a_contract_forbids_live_or_forward_inputs() -> None:
    contract = _contract()
    assert contract["mode"] == "design_only"
    assert contract["goal07a_execution_policy"]["calculate_risk_values"] is False
    assert contract["goal07a_execution_policy"]["write_symbol_level_outputs"] is False
    assert "future_returns_as_risk_features" in contract["forbidden_inputs"]
    assert "anything_not_pit_safe" in contract["forbidden_inputs"]

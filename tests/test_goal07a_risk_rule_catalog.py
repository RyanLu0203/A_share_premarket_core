from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_goal07a_rule_catalog_is_design_only_and_complete() -> None:
    catalog = json.loads((ROOT / "configs/risk/goal07a_risk_rule_catalog.yaml").read_text(encoding="utf-8"))
    assert set(catalog["allowed_future_risk_states"]) == {"PASS", "WARNING", "DEGRADED", "BLOCKED", "NOT_EVALUATED"}
    rules = catalog["rules"]
    assert len(rules) >= 6
    assert all(rule["execution_in_goal07a"] is False for rule in rules)
    assert all(rule["real_symbol_assignment_in_goal07a"] is False for rule in rules)
    assert any(rule["trigger_design"] == "leakage_flags not PASS" and rule["future_effect_design"] == "BLOCKED" for rule in rules)

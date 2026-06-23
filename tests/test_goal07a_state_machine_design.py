from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_goal07a_state_machine_has_required_states_and_transitions() -> None:
    machine = json.loads((ROOT / "configs/risk/goal07a_risk_state_machine.yaml").read_text(encoding="utf-8"))
    assert set(machine["states"]) == {
        "not_evaluated",
        "input_invalid",
        "data_blocked",
        "model_warning",
        "source_warning",
        "market_warning",
        "eligible_for_review_only_snapshot",
        "blocked_from_recommendation",
    }
    triggers = {item["trigger_design"] for item in machine["transitions"]}
    assert "input contract failure" in triggers
    assert "leakage flag failure" in triggers
    assert "any hard boundary violation" in triggers
    assert all(item["execution_in_goal07a"] is False for item in machine["transitions"])

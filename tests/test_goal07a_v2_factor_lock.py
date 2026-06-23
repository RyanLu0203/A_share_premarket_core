from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_goal07a_v2_factor_lock_audit_passes() -> None:
    text = (ROOT / "outputs/audits/goal07a_v2_factor_lock_audit.md").read_text(encoding="utf-8")
    assert "Status: `PASS`" in text
    assert "V2 factor research remains planned_locked." in text
    assert "No factor mining script exists." in text


def test_v2_factor_placeholder_remains_locked_and_inactive() -> None:
    contract = (ROOT / "configs/factors/v2_factor_research_contract.yaml").read_text(encoding="utf-8")
    assert "status: planned_locked" in contract
    assert "enabled: false" in contract
    assert "active_in_v1: false" in contract
    assert not (ROOT / "outputs/factors").exists()

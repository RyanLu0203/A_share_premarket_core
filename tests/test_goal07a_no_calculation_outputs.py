from __future__ import annotations

from pathlib import Path

from ashare_premarket.risk_design.goal07a import run_goal07a_risk_overlay_design_gate

ROOT = Path(__file__).resolve().parents[1]


def test_goal07a_runner_does_not_create_forbidden_output_directories() -> None:
    assert run_goal07a_risk_overlay_design_gate(ROOT)
    for rel in [
        "outputs/risk_overlay",
        "outputs/recommendations",
        "outputs/positions",
        "outputs/dashboard",
        "outputs/paper_trading",
        "outputs/live_trading",
        "outputs/factors",
    ]:
        assert not (ROOT / rel).exists()


def test_goal07a_does_not_create_symbol_level_risk_rows() -> None:
    generated = list((ROOT / "outputs").glob("**/*risk_overlay*.csv"))
    assert generated == []

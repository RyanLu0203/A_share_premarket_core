from __future__ import annotations

from pathlib import Path

from ashare_premarket.risk_design.goal07a import run_goal07a_risk_overlay_design_gate

ROOT = Path(__file__).resolve().parents[1]


def test_goal07a_runner_does_not_create_forbidden_output_directories() -> None:
    existing_risk_outputs = set((ROOT / "outputs").glob("**/*risk_overlay*.csv"))
    assert run_goal07a_risk_overlay_design_gate(ROOT)
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


def test_goal07a_does_not_create_symbol_level_risk_rows() -> None:
    generated = {path.relative_to(ROOT).as_posix() for path in (ROOT / "outputs").glob("**/*risk_overlay*.csv")}
    assert generated <= {
        "outputs/risk_overlay/goal07b_review_only_risk_overlay.csv",
        "outputs/diagnostics/goal07b_risk_overlay_diagnostics.csv",
    }

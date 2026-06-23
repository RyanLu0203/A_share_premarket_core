from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_goal06d1_governance_confirms_review_only_boundaries() -> None:
    text = (ROOT / "outputs/audits/goal06d1_governance_audit.md").read_text(encoding="utf-8")
    assert "Status: `PASS`" in text
    assert "GOAL-06D.1 is review-only: `true`" in text
    assert "GOAL-07A implemented: `false`" in text
    assert "Risk overlay calculation exists: `false`" in text
    assert "Recommendation outputs exist: `false`" in text
    assert "Position outputs exist: `false`" in text
    assert "Factor mining outputs exist: `false`" in text


def test_goal06d1_readiness_is_pass_or_pass_with_warnings() -> None:
    text = (ROOT / "outputs/audits/goal06d1_readiness_report.md").read_text(encoding="utf-8")
    assert (
        "GOAL-06D.1 Calibration Stability Warning Repair Readiness: PASS" in text
        or "GOAL-06D.1 Calibration Stability Warning Repair Readiness: PASS_WITH_WARNINGS" in text
    )
    assert "No recommendation, position, risk overlay, dashboard, trading, production, factor-mining, or DQN/RL output was created." in text

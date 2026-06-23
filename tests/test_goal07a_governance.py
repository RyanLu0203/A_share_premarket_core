from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_goal07a_governance_boundary_confirms_design_only() -> None:
    text = (ROOT / "outputs/audits/goal07a_governance_boundary_audit.md").read_text(encoding="utf-8")
    assert "Status: `PASS`" in text
    assert "GOAL-07A is design-only: `true`" in text
    assert "GOAL-07B implemented: `false`" in text
    assert "Risk overlay calculation exists: `false`" in text
    assert "Recommendation output exists: `false`" in text
    assert "Position output exists: `false`" in text


def test_goal07a_readiness_carries_upstream_warnings() -> None:
    text = (ROOT / "outputs/audits/goal07a_readiness_report.md").read_text(encoding="utf-8")
    assert "GOAL-07A Risk Overlay Design Readiness: PASS_WITH_WARNINGS" in text
    for warning in [
        "calibration_not_reliable_for_thresholding",
        "feature_sign_instability_bounded",
        "provider_source_concentration_disclosed",
        "selected_score_variant_weak_rank_signal",
        "single_provider_mode_akshare_direct",
        "weak_target_horizon_rank_signal",
        "target_horizon_calibration_warning",
    ]:
        assert warning in text

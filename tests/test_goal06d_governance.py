from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_goal06d_governance_audit_confirms_review_only_boundaries() -> None:
    text = (ROOT / "outputs/audits/goal06d_governance_audit.md").read_text(encoding="utf-8")

    assert "Status: `PASS`" in text
    assert "GOAL-06D is review-only: `true`" in text
    assert "Recommendation outputs exist: `false`" in text
    assert "Position outputs exist: `false`" in text
    assert "Risk overlay calculation exists: `false`" in text
    assert "Dashboard exists: `false`" in text
    assert "Paper/live trading exists: `false`" in text
    assert "Production DB writes exist: `false`" in text
    assert "Production model promotion exists: `false`" in text
    assert "DQN/RL added: `false`" in text


def test_goal06d_does_not_commit_model_binaries_or_heavy_artifacts() -> None:
    forbidden_suffixes = {".pkl", ".joblib", ".onnx", ".db", ".sqlite", ".sqlite3", ".parquet", ".zip", ".html", ".log"}
    artifacts = [path for path in (ROOT / "outputs/models/goal06d").rglob("*") if path.is_file()]

    assert artifacts
    assert all(path.suffix.lower() not in forbidden_suffixes for path in artifacts)
    assert {path.suffix.lower() for path in artifacts} <= {".csv", ".md"}


def test_goal06d_readiness_warns_instead_of_unlocking_goal07a() -> None:
    text = (ROOT / "outputs/audits/goal06d_readiness_report.md").read_text(encoding="utf-8")

    assert "GOAL-06D Model Comparison Calibration Readiness: PASS_WITH_WARNINGS" in text
    assert "Allowed next action: `fix_goal06d_model_stability_or_calibration_warnings`" in text
    assert "GOAL-07A mode if allowed: `design_only`" in text
    assert "No recommendation, position, risk overlay, dashboard, trading, production, or DQN/RL output was created." in text

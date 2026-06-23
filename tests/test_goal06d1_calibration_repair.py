from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_goal06d1_calibration_repair_never_allows_thresholding() -> None:
    with (ROOT / "outputs/models/goal06d1/calibration_repair_summary.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert all(row["thresholding_allowed"] == "false" for row in rows)
    assert all("threshold" not in row["calibration_method_selected"].lower() for row in rows)
    audit = (ROOT / "outputs/audits/goal06d1_calibration_repair_audit.md").read_text(encoding="utf-8")
    assert "Trading thresholds generated: `false`" in audit
    assert "Position bands generated: `false`" in audit
    assert "Risk overlay cutoffs generated: `false`" in audit
    assert "Recommendation thresholds generated: `false`" in audit


def test_goal06d1_decile_diagnostics_are_review_only() -> None:
    with (ROOT / "outputs/models/goal06d1/decile_calibration_diagnostics.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert all(row["review_only"] == "true" for row in rows)

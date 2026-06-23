from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_goal06d_calibration_summary_is_review_only_and_complete() -> None:
    with (ROOT / "outputs/models/goal06d/calibration_summary.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert {row["calibration_method"] for row in rows} == {"quantile_bin_calibration"}
    assert {row["target"] for row in rows} == {"excess_fwd_3d_return"}
    assert all(int(row["sample_count"]) > 0 for row in rows)
    assert all(int(row["bin_count"]) >= 1 for row in rows)
    assert all(row["monotonicity_check"] in {"PASS", "PASS_WITH_WARNINGS"} for row in rows)


def test_goal06d_calibration_audit_does_not_create_thresholds_or_position_bands() -> None:
    text = (ROOT / "outputs/audits/goal06d_calibration_audit.md").read_text(encoding="utf-8")

    assert "Trading thresholds generated: `false`" in text
    assert "Position bands generated: `false`" in text

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_goal06d1_target_horizon_comparison_is_review_only_and_complete() -> None:
    rows = _rows("outputs/models/goal06d1/target_horizon_comparison.csv")
    assert {row["target"] for row in rows} == {"excess_fwd_1d_return", "excess_fwd_3d_return", "excess_fwd_5d_return"}
    assert all(row["top_bottom_spread_offline_diagnostic_only"] for row in rows)
    audit = (ROOT / "outputs/audits/goal06d1_target_horizon_audit.md").read_text(encoding="utf-8")
    assert "offline diagnostic only" in audit
    assert "not a portfolio backtest" in audit
    assert "not a recommendation" in audit

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_goal06d1_provider_concentration_is_disclosed_not_faked() -> None:
    with (ROOT / "outputs/models/goal06d1/provider_source_concentration_summary.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert {row["provider_mode"] for row in rows} == {"akshare_direct"}
    assert all(row["production_diversification_sufficient"] == "false" for row in rows)
    disclosure = (ROOT / "outputs/audits/goal06d1_provider_concentration_disclosure.md").read_text(encoding="utf-8")
    assert "source-backed but concentrated in akshare_direct" in disclosure
    assert "Fake diversification implemented: `false`" in disclosure

from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.io import read_csv
from ashare_premarket.providers.akshare.market_regime_sources import (
    ALLOWED_APPROVED_USAGE,
    ALLOWED_PRIORITY_BANDS,
    BLOCKED_APPROVED_USAGE,
    select_market_regime_sources,
)

ROOT = Path(__file__).resolve().parents[1]


def test_market_regime_source_selection_uses_only_approved_p0_p1_sources() -> None:
    catalog_rows = read_csv(ROOT / "outputs/providers/akshare_source_catalog.csv")
    selected_rows = select_market_regime_sources(catalog_rows)
    active_rows = [row for row in selected_rows if row["selected_for_goal"] == "true"]
    inactive_rows = [row for row in selected_rows if row["selected_for_goal"] == "false"]

    assert len(active_rows) == 29
    assert active_rows
    assert all(row["priority_band"] in ALLOWED_PRIORITY_BANDS for row in active_rows)
    assert all(row["approved_usage"] in ALLOWED_APPROVED_USAGE for row in active_rows)
    assert not any(row["approved_usage"] in BLOCKED_APPROVED_USAGE for row in active_rows)
    assert all(row["fetch_mode"] == "committed_evidence_replay" for row in active_rows)
    assert all("raw" not in row["commit_policy"].lower() or "raw_payload_forbidden" in row["commit_policy"] for row in active_rows)
    assert any(row["approved_usage"] in BLOCKED_APPROVED_USAGE or row["priority_band"].startswith("P3") for row in inactive_rows)


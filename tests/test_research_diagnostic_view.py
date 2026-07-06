from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

from ashare_premarket.research.research_diagnostic_view import (
    DISCLAIMER,
    INPUTS,
    MANIFEST_PATH,
    build_view_manifest,
    load_table,
    render_html,
    sort_filter_topn,
)

ROOT = Path(__file__).resolve().parents[1]
MODULE_HEADERS = [
    "1. Market / Regime Context",
    "2. Factor Diagnostic Overview",
    "3. Warnings / Integrity",
    "4. Evidence / Provenance",
]


def _factor_rows() -> list[dict[str, str]]:
    _, rows = load_table(ROOT, "factor_diagnostic_overview")
    return rows


def test_loaders_handle_missing_files(tmp_path: Path) -> None:
    headers, rows = load_table(tmp_path, "factor_diagnostic_overview")
    assert headers == [] and rows == []
    assert sort_filter_topn([], sort_by="x", top_n=3) == []


def test_render_has_four_modules_and_disclaimer() -> None:
    page = render_html(ROOT)
    assert page.startswith("<!doctype html>")
    for header in MODULE_HEADERS:
        assert header in page
    assert DISCLAIMER in page


def test_view_fabricates_no_ready_or_actionable_semantics() -> None:
    rows = _factor_rows()
    assert rows, "expected committed factor diagnostics"
    # The view never promotes a factor: no ``ready`` status, no rec-tiering candidacy.
    for row in rows:
        assert row["overall_factor_status"] != "ready"
        assert row["candidate_for_rec_tiering"] == "false"
    # The factor table adds no new columns/semantics beyond the committed source schema.
    src_headers, _ = load_table(ROOT, "factor_diagnostic_overview")
    for actionable in ("buy", "sell", "hold", "target_price", "order_quantity", "position_size", "portfolio_weight", "recommendation_tag"):
        assert not any(actionable in h.lower() for h in src_headers)


def test_sort_filter_topn_is_presentation_only() -> None:
    rows = _factor_rows()
    top = sort_filter_topn(rows, sort_by="diagnostic_composite_score", top_n=10)
    assert len(top) == min(10, len(rows))
    # scores are non-increasing
    scores = [float(r["diagnostic_composite_score"]) for r in top]
    assert scores == sorted(scores, reverse=True)
    # filtering does not change any row's status
    filtered = sort_filter_topn(rows, status_filter="conditionally_useful")
    assert all(r["overall_factor_status"] == "conditionally_useful" for r in filtered)
    assert len(filtered) <= len(rows)


def test_manifest_reproducible_and_boundaries_safe() -> None:
    manifest = build_view_manifest(ROOT)
    committed = json.loads((ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))
    assert committed == manifest
    for flag in (
        "creates_new_signal_semantics",
        "creates_readiness_semantics",
        "creates_recommendation_semantics",
        "creates_position_semantics",
        "writes_actionable_output",
        "commits_frontend_artifact",
        "modifies_workflow_or_governance_state",
        "unlocks_goal_rec_tiering01",
        "unlocks_dashboard_daily_report",
    ):
        assert manifest[flag] is False
    assert manifest["ready_factor_count_expected"] == 0
    assert set(manifest["inputs_consumed"]) == set(INPUTS)


def test_view_creates_no_forbidden_artifact_and_no_gate_change() -> None:
    render_html(ROOT)  # rendering must not write any file
    assert not (ROOT / "outputs/premarket_signal_v0_5.csv").exists()
    for forbidden_dir in ("outputs/dashboard", "outputs/dashboards"):
        assert not (ROOT / forbidden_dir).exists()
    with (ROOT / "configs/project/workflow_status.csv").open(newline="", encoding="utf-8") as handle:
        workflow = {r["workflow_id"]: r for r in csv.DictReader(handle)}
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["status"] == "locked_future"
    assert workflow["dashboard_daily_report"]["status"] == "locked_future"


def test_app_startup_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "apps/research_diagnostic_dashboard_v0.py"), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "startup smoke ok" in result.stdout

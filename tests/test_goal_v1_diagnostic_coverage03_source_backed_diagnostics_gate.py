from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.diagnostics.goal_v1_diagnostic_coverage03 import (
    AUDIT_PATH,
    DISTRIBUTION_SUMMARY_PATH,
    FALSE_BOUNDARY_KEYS,
    MANIFEST_PATH,
    POSITION_DIAGNOSTICS_PATH,
    RECOMMENDATION_DIAGNOSTICS_PATH,
    RISK_DIAGNOSTICS_PATH,
    SOURCE_PANEL,
    TARGET_ROWS,
    TARGET_SYMBOLS,
    TARGET_TRADE_DATES,
    audit_goal_v1_diagnostic_coverage03_source_backed_diagnostics_gate,
    run_goal_v1_diagnostic_coverage03_source_backed_diagnostics_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def _keys(rows: list[dict[str, str]]) -> set[tuple[str, str]]:
    return {(row["trade_date"], row["symbol"]) for row in rows}


def test_goal_v1_diagnostic_coverage03_runner_is_deterministic_and_auditable() -> None:
    assert run_goal_v1_diagnostic_coverage03_source_backed_diagnostics_gate(ROOT)
    first = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert run_goal_v1_diagnostic_coverage03_source_backed_diagnostics_gate(ROOT)
    second = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert first == second
    assert audit_goal_v1_diagnostic_coverage03_source_backed_diagnostics_gate(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")


def test_goal_v1_diagnostic_coverage03_generates_source_backed_diagnostic_families() -> None:
    assert run_goal_v1_diagnostic_coverage03_source_backed_diagnostics_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    risk_rows = _rows(RISK_DIAGNOSTICS_PATH)
    recommendation_rows = _rows(RECOMMENDATION_DIAGNOSTICS_PATH)
    position_rows = _rows(POSITION_DIAGNOSTICS_PATH)
    distribution_rows = _rows(DISTRIBUTION_SUMMARY_PATH)

    assert manifest["status"] in {"PASS", "PASS_WITH_WARNINGS"}
    assert manifest["primary_input_artifact"] == SOURCE_PANEL
    assert manifest["input_artifacts"] == [SOURCE_PANEL]
    assert len(risk_rows) >= TARGET_ROWS
    assert len(recommendation_rows) >= TARGET_ROWS
    assert len(position_rows) >= TARGET_ROWS
    assert int(manifest["unique_symbols"]) >= TARGET_SYMBOLS
    assert int(manifest["unique_trade_dates"]) >= TARGET_TRADE_DATES
    assert manifest["duplicate_trade_date_symbol_keys"] == 0
    assert _keys(risk_rows) == _keys(recommendation_rows) == _keys(position_rows)
    assert manifest["keys_match_across_diagnostic_families"] is True
    assert distribution_rows


def test_goal_v1_diagnostic_coverage03_remains_non_actionable_and_preserves_locks() -> None:
    assert run_goal_v1_diagnostic_coverage03_source_backed_diagnostics_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    recommendation_rows = _rows(RECOMMENDATION_DIAGNOSTICS_PATH)
    position_rows = _rows(POSITION_DIAGNOSTICS_PATH)
    workflow = _workflow()

    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert {row["actionability_status"] for row in recommendation_rows} == {"never_actionable"}
    assert {row["actionability_blocked"] for row in recommendation_rows} == {"true"}
    assert {row["position_band_blocked"] for row in position_rows} == {"true"}
    assert manifest["canonical_goal07b_goal08b_goal09_preserved"] is True
    assert workflow["goal_v1_diagnostic_coverage03_multi_provider_diagnostics"]["status"] == "implemented_review_only"
    assert workflow["goal_v1_diagnostic_coverage03_multi_provider_diagnostics"]["depends_on"] == "goal_data_provider02b_provider_selection_gate"
    assert workflow["goal_data_panel02_evaluation_panel_gate"]["status"] == "locked_future"
    assert workflow["goal10b3_recommendation_backtest_revalidation"]["status"] == "locked_future"
    assert workflow["goal10b3_recommendation_backtest_revalidation"]["depends_on"] == "goal_v1_diagnostic_coverage03_multi_provider_diagnostics"
    assert workflow["goal10d_backtest_failure_attribution_gate"]["status"] == "locked_future"
    assert workflow["dashboard_daily_report"]["status"] == "locked_future"

from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.providers.goal_data_provider02b import (
    AUDIT_PATH,
    COVERAGE_SUMMARY_PATH,
    MANIFEST_PATH,
    PANEL_FIELDS,
    PANEL_PATH,
    TARGET_ROWS,
    TARGET_SYMBOLS,
    TARGET_TRADE_DATES,
    audit_goal_data_provider02b_source_backed_panel_build_gate,
    goal_data_provider02b_valid_source_backed_panel_evidence,
)

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal_data_provider02b_committed_panel_schema_and_thresholds(monkeypatch) -> None:
    monkeypatch.delenv("ASHARE_ALLOW_NETWORK_INGESTION", raising=False)
    assert audit_goal_data_provider02b_source_backed_panel_build_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    rows = _rows(PANEL_PATH)
    coverage = {row["metric"]: row for row in _rows(COVERAGE_SUMMARY_PATH)}

    assert manifest["status"] in {"PASS", "PASS_WITH_WARNINGS"}
    assert manifest["mode"] == "review_only_source_backed_evaluation_panel_build_gate"
    assert manifest["panel_schema"] == PANEL_FIELDS
    assert len(rows) >= TARGET_ROWS
    assert list(rows[0]) == PANEL_FIELDS
    assert int(manifest["unique_symbols"]) >= TARGET_SYMBOLS
    assert int(manifest["unique_trade_dates"]) >= TARGET_TRADE_DATES
    assert manifest["panel_contract_status"] == "source_backed_evaluation_panel_ready_for_dc03"
    assert coverage["threshold_classification"]["observed_value"] == "source_backed_evaluation_panel_ready_for_dc03"
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")


def test_goal_data_provider02b_is_review_only_and_preserves_locks() -> None:
    assert goal_data_provider02b_valid_source_backed_panel_evidence(ROOT)
    manifest = _json(MANIFEST_PATH)
    workflow = _workflow()

    assert manifest["source_backed_evaluation_panel_created"] is True
    assert manifest["approved_universe_expanded"] is False
    assert manifest["recommendation_diagnostics_run"] is False
    assert manifest["position_band_diagnostics_run"] is False
    assert manifest["backtests_run"] is False
    assert manifest["portfolio_returns_generated"] is False
    assert manifest["equity_curves_generated"] is False
    assert manifest["dashboard_outputs_generated"] is False
    assert manifest["local_lake_files_created"] is False
    assert manifest["raw_payloads_never_persisted"] is True
    assert manifest["provider_tokens_never_persisted"] is True
    assert workflow["goal_data_provider02b_provider_selection_gate"]["status"] == "implemented_review_only"
    assert workflow["goal_data_provider02b_provider_selection_gate"]["implemented_in_repo"] == "true"
    assert workflow["goal_data_provider02b_provider_selection_gate"]["depends_on"] == "goal_data_provider02a1_network_opt_in_provider_smoke_test"
    assert workflow["goal_v1_diagnostic_coverage03_multi_provider_diagnostics"]["status"] == "implemented_review_only"
    assert workflow["goal_v1_diagnostic_coverage03_multi_provider_diagnostics"]["implemented_in_repo"] == "true"
    for workflow_id in [
        "goal_data_panel02_evaluation_panel_gate",
        "goal10b3_recommendation_backtest_revalidation",
        "goal10d_backtest_failure_attribution_gate",
        "dashboard_daily_report",
        "portfolio_backtest",
    ]:
        assert workflow[workflow_id]["status"] == "locked_future"
        assert workflow[workflow_id]["implemented_in_repo"] == "false"

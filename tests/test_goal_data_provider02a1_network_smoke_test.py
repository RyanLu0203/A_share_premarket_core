from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.providers.goal_data_provider02a1 import (
    AUDIT_PATH,
    FALSE_BOUNDARY_KEYS,
    MANIFEST_PATH,
    RESULT_FIELDS,
    RESULT_PATH,
    PROVIDERS,
    audit_goal_data_provider02a1_network_smoke_test,
    run_goal_data_provider02a1_network_smoke_test,
)

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal_data_provider02a1_runner_is_review_only_and_deterministic_without_opt_in(monkeypatch) -> None:
    monkeypatch.delenv("ASHARE_ALLOW_NETWORK_INGESTION", raising=False)
    monkeypatch.delenv("ASHARE_ALLOW_TUSHARE", raising=False)
    assert run_goal_data_provider02a1_network_smoke_test(ROOT)
    first = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert run_goal_data_provider02a1_network_smoke_test(ROOT)
    second = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert first == second
    assert audit_goal_data_provider02a1_network_smoke_test(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")


def test_goal_data_provider02a1_default_run_does_not_attempt_live_access(monkeypatch) -> None:
    monkeypatch.delenv("ASHARE_ALLOW_NETWORK_INGESTION", raising=False)
    assert run_goal_data_provider02a1_network_smoke_test(ROOT)
    manifest = _json(MANIFEST_PATH)
    rows = _rows(RESULT_PATH)

    assert manifest["status"] in {"PASS", "PASS_WITH_WARNINGS"}
    assert manifest["provider_count"] == 7
    assert manifest["providers_smoke_tested"] == PROVIDERS
    assert manifest["result_schema"] == RESULT_FIELDS
    assert manifest["network_opt_in_present"] is False
    assert manifest["live_provider_access_attempted_count"] == 0
    assert manifest["provider_tokens_never_persisted"] is True
    assert manifest["raw_payloads_never_persisted"] is True
    assert [row["provider_name"] for row in rows] == PROVIDERS
    assert list(rows[0]) == RESULT_FIELDS
    assert all(row["live_access_attempted"] == "false" for row in rows)
    assert all(row["raw_payload_persisted"] == "false" for row in rows)
    assert all(row["provider_token_persisted"] == "false" for row in rows)
    assert {row["provider_name"]: row["provider_role"] for row in rows}["yfinance"] == "auxiliary_only"
    assert {row["provider_name"]: row["provider_role"] for row in rows}["local_import"] == "fallback"


def test_goal_data_provider02a1_preserves_downstream_locks(monkeypatch) -> None:
    monkeypatch.delenv("ASHARE_ALLOW_NETWORK_INGESTION", raising=False)
    assert run_goal_data_provider02a1_network_smoke_test(ROOT)
    manifest = _json(MANIFEST_PATH)
    workflow = _workflow()

    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert manifest["review_only_network_smoke_test_generated"] is True
    assert manifest["all_required_providers_represented"] is True
    assert manifest["qstock_backtest_strategy_modules_not_used"] is True
    assert manifest["yfinance_auxiliary_not_primary"] is True
    assert workflow["goal_data_provider02a1_network_opt_in_provider_smoke_test"]["status"] == "implemented_review_only"
    assert workflow["goal_data_provider02a1_network_opt_in_provider_smoke_test"]["implemented_in_repo"] == "true"
    assert workflow["goal_data_provider02a1_network_opt_in_provider_smoke_test"]["depends_on"] == "goal_data_provider02a_multi_provider_capability_probe"
    assert workflow["goal_data_provider02b_provider_selection_gate"]["depends_on"] == "goal_data_provider02a1_network_opt_in_provider_smoke_test"
    assert workflow["goal_data_provider02b_provider_selection_gate"]["status"] == "implemented_review_only"
    assert workflow["goal_data_provider02b_provider_selection_gate"]["implemented_in_repo"] == "true"
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

from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.providers.goal_data_provider02a import (
    AUDIT_PATH,
    FALSE_BOUNDARY_KEYS,
    FAILURE_TAXONOMY_PATH,
    MANIFEST_PATH,
    PROBE_FIELDS,
    PROBE_PATH,
    PROVIDERS,
    SCHEMA_MAPPING_PATH,
    audit_goal_data_provider02a_multi_provider_capability_probe_gate,
    run_goal_data_provider02a_multi_provider_capability_probe_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal_data_provider02a_runner_is_review_only_and_deterministic() -> None:
    assert run_goal_data_provider02a_multi_provider_capability_probe_gate(ROOT)
    first = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert run_goal_data_provider02a_multi_provider_capability_probe_gate(ROOT)
    second = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert first == second
    assert audit_goal_data_provider02a_multi_provider_capability_probe_gate(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")


def test_goal_data_provider02a_provider_probe_schema_and_roles() -> None:
    assert run_goal_data_provider02a_multi_provider_capability_probe_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    rows = _rows(PROBE_PATH)
    mapping_rows = _rows(SCHEMA_MAPPING_PATH)
    taxonomy_rows = _rows(FAILURE_TAXONOMY_PATH)

    assert manifest["status"] in {"PASS", "PASS_WITH_WARNINGS"}
    assert manifest["provider_count"] == 7
    assert manifest["providers_probed"] == PROVIDERS
    assert manifest["probe_schema"] == PROBE_FIELDS
    assert [row["provider_name"] for row in rows] == PROVIDERS
    assert list(rows[0]) == PROBE_FIELDS
    assert rows[0]["provider_name"] == "tushare_pro"
    if rows[0]["token_available"] == "false":
        assert rows[0]["failure_code"] == "tushare_unavailable_missing_token"
    assert {row["provider_name"] for row in mapping_rows} == set(PROVIDERS)
    assert {row["provider_name"] for row in taxonomy_rows} == set(PROVIDERS)
    assert {row["provider_name"]: row["provider_role"] for row in rows}["yfinance"] == "auxiliary_only"
    assert {row["provider_name"]: row["source_priority_recommendation"] for row in rows}["yfinance"] == "auxiliary_not_primary"
    assert {row["provider_name"]: row["provider_role"] for row in rows}["local_import"] == "fallback"


def test_goal_data_provider02a_preserves_downstream_locks() -> None:
    assert run_goal_data_provider02a_multi_provider_capability_probe_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    workflow = _workflow()

    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert manifest["review_only_capability_probe_generated"] is True
    assert manifest["all_required_providers_represented"] is True
    assert manifest["qstock_backtest_strategy_modules_not_used"] is True
    assert manifest["yfinance_auxiliary_not_primary"] is True
    assert workflow["goal_data_provider02a_multi_provider_capability_probe"]["status"] == "implemented_review_only"
    assert workflow["goal_data_provider02a_multi_provider_capability_probe"]["implemented_in_repo"] == "true"
    assert workflow["goal_data_provider02a_multi_provider_capability_probe"]["depends_on"] == "goal10c_backtest_cost_slippage_sensitivity_gate"
    assert workflow["goal_data_provider02b_provider_selection_gate"]["status"] == "implemented_review_only"
    assert workflow["goal_data_provider02b_provider_selection_gate"]["implemented_in_repo"] == "true"
    for workflow_id in [
        "goal_data_panel02_evaluation_panel_gate",
        "goal_v1_diagnostic_coverage03_multi_provider_diagnostics",
        "goal10b3_recommendation_backtest_revalidation",
        "goal10d_backtest_failure_attribution_gate",
        "dashboard_daily_report",
        "portfolio_backtest",
    ]:
        assert workflow[workflow_id]["status"] == "locked_future"
        assert workflow[workflow_id]["implemented_in_repo"] == "false"

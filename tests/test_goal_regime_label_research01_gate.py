from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.research.goal_regime_label_research01 import (
    AUDIT_PATH,
    BRIDGE_FIELDS,
    COVERAGE_FIELDS,
    DATE_LABEL_FIELDS,
    DATE_LABELS_PATH,
    FACTOR_BRIDGE_PATH,
    MANIFEST_PATH,
    SIZE_LIMIT_BYTES,
    SYMBOL_CONTEXT_FIELDS,
    SYMBOL_CONTEXT_PATH,
    TRANSITION_FIELDS,
    WARNING_FIELDS,
    audit_goal_regime_label_research01_gate,
    evaluate_goal_regime_label_research01,
    run_goal_regime_label_research01_gate,
)

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_FIELDS = {
    "forward_return_1d",
    "forward_return_5d",
    "forward_return_20d",
    "benchmark_excess_return_1d",
    "benchmark_excess_return_5d",
    "benchmark_excess_return_20d",
    "label_ready_1d",
    "label_ready_5d",
    "label_ready_20d",
    "daily_ic_1d",
    "daily_rank_ic_1d",
    "hit_rate_1d",
    "recommendation_label",
    "position_size",
    "portfolio_weight",
    "portfolio_return",
    "equity_curve",
}

FALSE_BOUNDARY_KEYS = [
    "future_returns_used_in_label_construction",
    "benchmark_excess_forward_returns_used_in_label_construction",
    "label_ready_fields_used_in_label_construction",
    "posthoc_factor_performance_used_in_label_construction",
    "recommendation_rows_created",
    "position_rows_created",
    "buy_sell_hold_outputs_generated",
    "target_prices_generated",
    "actual_position_sizing_generated",
    "portfolio_weights_generated",
    "order_quantities_generated",
    "portfolio_returns_generated",
    "equity_curves_generated",
    "dashboard_outputs_generated",
    "html_generated",
    "streamlit_generated",
    "frontend_code_generated",
    "trading_outputs_created",
    "broker_outputs_created",
    "production_outputs_created",
    "local_lake_outputs_created",
    "factor_mining_outputs_created",
    "dqn_rl_outputs_created",
    "live_provider_fetches_run",
    "goal_quant_research04_run",
    "goal_rec_tiering01_run",
    "goal10b4_run",
    "position_band_validation_run",
    "goal10d_run",
    "regime_definitions_tuned_to_future_returns",
    "regime_labels_altered_by_factor_performance",
    "market_timing_validity_claimed",
    "factor_promoted_to_recommendation_tiering",
    "demo_fixture_used",
    "outputs_samples_used",
    "stale_goal10b_evidence_used",
    "stale_dc02_evidence_used",
]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal_regime_label_research01_evaluation_schema_counts_and_no_forbidden_fields() -> None:
    result = evaluate_goal_regime_label_research01(ROOT)
    manifest = result["manifest"]

    assert manifest["status"] in {"PASS", "PASS_WITH_WARNINGS"}
    assert manifest["date_regime_row_count"] == 120
    assert manifest["symbol_regime_context_row_count"] == 6000
    assert manifest["factor_regime_bridge_row_count"] == 180000
    assert manifest["unique_symbols"] == 50
    assert manifest["unique_trade_dates"] == 120
    assert list(result["date_rows"][0]) == DATE_LABEL_FIELDS
    assert list(result["symbol_rows"][0]) == SYMBOL_CONTEXT_FIELDS
    assert list(result["coverage_rows"][0]) == COVERAGE_FIELDS
    assert list(result["transition_rows"][0]) == TRANSITION_FIELDS
    assert list(result["bridge_rows"][0]) == BRIDGE_FIELDS
    assert list(result["warning_rows"][0]) == WARNING_FIELDS
    assert not (set(BRIDGE_FIELDS) & FORBIDDEN_FIELDS)
    assert manifest["no_lookahead_construction_passed"] is True
    assert manifest["source_backed_lineage_verified"] is True
    assert manifest["artifact_size_policy_passed"] is True


def test_goal_regime_label_research01_runner_preserves_research_only_boundaries() -> None:
    assert run_goal_regime_label_research01_gate(ROOT)
    assert audit_goal_regime_label_research01_gate(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")

    manifest = _json(MANIFEST_PATH)
    date_rows = _rows(DATE_LABELS_PATH)
    symbol_rows = _rows(SYMBOL_CONTEXT_PATH)
    bridge_rows = _rows(FACTOR_BRIDGE_PATH)

    assert len(date_rows) == 120
    assert len(symbol_rows) == 6000
    assert len(bridge_rows) == 180000
    assert len({row["trade_date"] for row in date_rows}) == 120
    assert len({(row["trade_date"], row["symbol"]) for row in symbol_rows}) == len(symbol_rows)
    assert len({(row["trade_date"], row["symbol"], row["refined_factor_id"]) for row in bridge_rows}) == len(bridge_rows)
    assert {row["no_lookahead_status"] for row in date_rows} == {"passed_current_or_past_only"}
    assert {row["no_lookahead_status"] for row in symbol_rows} == {"passed_current_or_past_only"}
    assert {row["no_lookahead_status"] for row in bridge_rows} == {"passed_current_or_past_only"}
    assert all((ROOT / path).stat().st_size < SIZE_LIMIT_BYTES for path in manifest["output_artifacts"])
    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert manifest["goal_quant_research04_locked_future"] is True
    assert manifest["goal_rec_tiering01_locked_future"] is True
    assert manifest["goal10b4_locked_future"] is True
    assert manifest["position_band_validation_locked_future"] is True
    assert manifest["goal10d_locked_future"] is True

    workflow = _workflow()
    assert workflow["goal_regime_label_research01_market_regime_label_construction_gate"]["status"] == "implemented_research_only"
    assert workflow["goal_regime_label_research01_market_regime_label_construction_gate"]["depends_on"] == "goal_quant_research03_refined_alpha_factor_validity_evaluation_gate"
    assert workflow["goal_architecture_refactor03_akshare_source_catalog_and_provider_modularization_gate"]["status"] == "implemented_engineering_research_support"
    assert workflow["goal_architecture_refactor03_akshare_source_catalog_and_provider_modularization_gate"]["depends_on"] == "goal_regime_label_research01_market_regime_label_construction_gate"
    assert workflow["goal_data_expansion_research01_market_regime_data_expansion_gate"]["status"] in {"locked_future", "implemented_research_only"}
    assert workflow["goal_data_expansion_research01_market_regime_data_expansion_gate"]["depends_on"] == "goal_architecture_refactor03_akshare_source_catalog_and_provider_modularization_gate"
    assert workflow["goal_quant_research04_regime_conditional_factor_evaluation_gate"]["status"] in {"locked_future", "implemented_research_only"}
    assert workflow["goal_quant_research04_regime_conditional_factor_evaluation_gate"]["depends_on"] == "goal_data_expansion_research01_market_regime_data_expansion_gate"
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["status"] == "locked_future"
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["depends_on"] == "goal_quant_research04_regime_conditional_factor_evaluation_gate"

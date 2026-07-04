from __future__ import annotations

import json
from pathlib import Path

from ashare_premarket.research.goal_regime_label_research02 import (
    AGREEMENT_FIELDS,
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
    audit_goal_regime_label_research02_gate,
    evaluate_goal_regime_label_research02,
    run_goal_regime_label_research02_gate,
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
    "factor_predictive_validity_evaluated",
    "ic_rankic_metrics_introduced",
    "recommendation_rows_created",
    "position_rows_created",
    "buy_sell_hold_outputs_generated",
    "regime_definitions_tuned_to_future_returns",
    "regime_labels_altered_by_factor_performance",
    "market_timing_validity_claimed",
    "factor_promoted_to_recommendation_tiering",
    "live_provider_fetches_run",
    "goal_quant_research04_run",
    "demo_fixture_used",
    "stale_goal10b_evidence_used",
    "stale_dc02_evidence_used",
]


def test_regime02_bridge_schema_excludes_lookahead_and_factor_performance_fields() -> None:
    assert not (set(BRIDGE_FIELDS) & FORBIDDEN_FIELDS)
    for field in BRIDGE_FIELDS:
        assert "forward_return" not in field
        assert "benchmark_excess_return" not in field
        assert "label_ready" not in field
        assert "ic" not in field.lower()
        assert "hit_rate" not in field.lower()


def test_regime02_evaluate_row_counts_and_no_lookahead() -> None:
    result = evaluate_goal_regime_label_research02(ROOT)
    manifest = result["manifest"]
    assert manifest["status"] in {"PASS", "PASS_WITH_WARNINGS"}
    assert manifest["refined_date_regime_row_count"] == 120
    assert manifest["refined_symbol_regime_context_row_count"] == 6000
    assert manifest["refined_factor_regime_bridge_row_count"] == 180000
    assert manifest["unique_symbols"] == 50
    assert manifest["unique_trade_dates"] == 120
    assert manifest["no_lookahead_construction_passed"] is True
    assert manifest["expanded_regime_evidence_integrated"] is True
    assert manifest["source_backed_lineage_verified"] is True
    assert manifest["artifact_size_policy_passed"] is True
    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    for key in [
        "goal_quant_research04_locked_future",
        "goal_rec_tiering01_locked_future",
        "goal10b4_locked_future",
        "position_band_validation_locked_future",
        "goal10d_locked_future",
    ]:
        assert manifest[key] is True
    assert list(result["date_rows"][0]) == DATE_LABEL_FIELDS
    assert list(result["symbol_rows"][0]) == SYMBOL_CONTEXT_FIELDS
    assert list(result["coverage_rows"][0]) == COVERAGE_FIELDS
    assert list(result["transition_rows"][0]) == TRANSITION_FIELDS
    assert list(result["agreement_rows"][0]) == AGREEMENT_FIELDS
    assert list(result["bridge_rows"][0]) == BRIDGE_FIELDS
    assert list(result["warning_rows"][0]) == WARNING_FIELDS
    assert {row["no_lookahead_status"] for row in result["date_rows"]} == {"passed_current_or_past_only"}
    assert {row["no_lookahead_status"] for row in result["symbol_rows"]} == {"passed_current_or_past_only"}
    assert {row["no_lookahead_status"] for row in result["bridge_rows"]} == {"passed_current_or_past_only"}


def test_regime02_gate_runs_and_audit_passes() -> None:
    assert run_goal_regime_label_research02_gate(ROOT)
    assert audit_goal_regime_label_research02_gate(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")
    manifest = json.loads((ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))
    assert manifest["mode"] == "research_only_expanded_market_regime_label_refinement_gate"
    for path in manifest["output_artifacts"]:
        assert (ROOT / path).stat().st_size < SIZE_LIMIT_BYTES


def test_regime02_workflow_row_implemented_and_downstream_locked() -> None:
    run_goal_regime_label_research02_gate(ROOT)
    import csv

    workflow = {row["workflow_id"]: row for row in csv.DictReader((ROOT / "configs/project/workflow_status.csv").open(encoding="utf-8"))}
    regime02 = workflow["goal_regime_label_research02_expanded_market_regime_label_refinement_gate"]
    assert regime02["status"] == "implemented_research_only"
    assert regime02["implemented_in_repo"] == "true"
    assert regime02["depends_on"] == "goal_data_expansion_research01_market_regime_data_expansion_gate"
    assert workflow["goal_quant_research04_regime_conditional_factor_evaluation_gate"]["status"] == "locked_future"
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["status"] == "locked_future"
    assert workflow["dashboard_daily_report"]["status"] == "locked_future"


def test_regime02_refined_labels_are_review_only_and_non_actionable() -> None:
    result = evaluate_goal_regime_label_research02(ROOT)
    for row in result["date_rows"]:
        assert row["refined_composite_regime_label"].endswith("_review_only")
        assert row["regime_confidence_tier"].endswith("_review_only")
        assert row["non_actionable_disclaimer"] == "research_only"

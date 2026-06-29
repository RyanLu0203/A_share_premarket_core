from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.risk_tiering.goal_risk_tiering011 import (
    AUDIT_PATH,
    COMPONENT_SUMMARY_PATH,
    DIAGNOSTICS_PATH,
    DISTRIBUTION_PATH,
    FALSE_BOUNDARY_KEYS,
    FORWARD_METRICS_PATH,
    HIGH_BUCKET,
    LOW_BUCKET,
    MANIFEST_PATH,
    MEDIUM_BUCKET,
    audit_goal_risk_tiering011_downside_risk_repair_gate,
    run_goal_risk_tiering011_downside_risk_repair_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal_risk_tiering011_runner_is_review_only_and_deterministic() -> None:
    assert run_goal_risk_tiering011_downside_risk_repair_gate(ROOT)
    first = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert run_goal_risk_tiering011_downside_risk_repair_gate(ROOT)
    second = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert first == second
    assert audit_goal_risk_tiering011_downside_risk_repair_gate(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")


def test_goal_risk_tiering011_creates_downside_score_components_without_overwriting_risk01() -> None:
    assert run_goal_risk_tiering011_downside_risk_repair_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    diagnostics = _rows(DIAGNOSTICS_PATH)
    components = _rows(COMPONENT_SUMMARY_PATH)
    distribution = _rows(DISTRIBUTION_PATH)
    metrics = _rows(FORWARD_METRICS_PATH)

    assert manifest["status"] == "PASS_WITH_WARNINGS"
    assert manifest["downside_risk_row_count"] == 6000
    assert manifest["unique_symbols"] == 50
    assert manifest["unique_trade_dates"] == 120
    assert len(diagnostics) == 6000
    assert {LOW_BUCKET, MEDIUM_BUCKET, HIGH_BUCKET}.issubset({row["downside_risk_bucket"] for row in diagnostics})
    assert all(float(row["downside_risk_score_numeric"]) >= 0 for row in diagnostics)
    assert any(row["summary_group_value"] == "HIGH_RISK_REVIEW_ONLY" for row in components)
    assert any(row["distribution_name"] == "downside_risk_bucket_distribution" for row in distribution)
    assert {LOW_BUCKET, MEDIUM_BUCKET, HIGH_BUCKET}.issubset({row["downside_risk_bucket"] for row in metrics})
    assert manifest["original_high_bucket_volatility_momentum_dominated"] is True
    assert manifest["downside_bucket_collapse_detected"] is False


def test_goal_risk_tiering011_preserves_no_lookahead_and_downstream_locks() -> None:
    assert run_goal_risk_tiering011_downside_risk_repair_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    diagnostics = _rows(DIAGNOSTICS_PATH)
    workflow = _workflow()

    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert manifest["score_construction_excludes_future_returns"] is True
    assert manifest["future_returns_used_only_for_post_hoc_evaluation"] is True
    assert manifest["no_lookahead_score_construction_check"] is True
    assert manifest["score_input_fields_do_not_include_future_return_labels"] is True
    assert manifest["signal_classification"] == "downside_risk_tiering_signal_weak_or_unreliable"
    assert "governance_risk_rule_review" in manifest["recommended_next_goal"]
    assert all(row["score_construction_no_lookahead_status"] == "passed_future_return_fields_excluded" for row in diagnostics)

    assert workflow["goal_risk_tiering011_downside_risk_repair_gate"]["status"] == "implemented_review_only"
    assert workflow["goal_risk_tiering011_downside_risk_repair_gate"]["implemented_in_repo"] == "true"
    assert workflow["goal_risk_tiering011_downside_risk_repair_gate"]["depends_on"] == "goal_risk_tiering01_risk_severity_numeric_score_gate"
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["depends_on"] in {
        "goal_risk_tiering011_downside_risk_repair_gate",
        "goal_quant_research01_factor_research_lab_gate",
        "goal_alpha_factor_candidate01_research_gate",
        "goal_quant_research02_alpha_candidate_factor_validity_evaluation_gate",
        "goal_alpha_factor_candidate02_refined_variants_research_gate",
    }
    for workflow_id in [
        "goal_rec_tiering01_recommendation_score_tiering_gate",
        "goal10b4_recommendation_backtest_revalidation",
        "goal_position_band_validation01_position_band_validation_gate",
        "goal10d_backtest_failure_attribution_gate",
        "dashboard_daily_report",
        "portfolio_backtest",
        "signal_backtest",
    ]:
        assert workflow[workflow_id]["status"] == "locked_future"
        assert workflow[workflow_id]["implemented_in_repo"] == "false"

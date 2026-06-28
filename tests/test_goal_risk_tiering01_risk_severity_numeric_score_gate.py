from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.risk_tiering.goal_risk_tiering01 import (
    AUDIT_PATH,
    DIAGNOSTICS_PATH,
    DISTRIBUTION_PATH,
    FALSE_BOUNDARY_KEYS,
    FORWARD_METRICS_PATH,
    HIGH_BUCKET,
    LOW_BUCKET,
    MANIFEST_PATH,
    MEDIUM_BUCKET,
    audit_goal_risk_tiering01_risk_severity_numeric_score_gate,
    run_goal_risk_tiering01_risk_severity_numeric_score_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal_risk_tiering01_runner_is_review_only_and_deterministic() -> None:
    assert run_goal_risk_tiering01_risk_severity_numeric_score_gate(ROOT)
    first = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert run_goal_risk_tiering01_risk_severity_numeric_score_gate(ROOT)
    second = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert first == second
    assert audit_goal_risk_tiering01_risk_severity_numeric_score_gate(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")


def test_goal_risk_tiering01_creates_numeric_score_buckets_without_overwriting_dc03() -> None:
    assert run_goal_risk_tiering01_risk_severity_numeric_score_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    diagnostics = _rows(DIAGNOSTICS_PATH)
    distribution = _rows(DISTRIBUTION_PATH)
    metrics = _rows(FORWARD_METRICS_PATH)

    assert manifest["status"] == "PASS_WITH_WARNINGS"
    assert manifest["risk_tiered_row_count"] == 6000
    assert manifest["unique_symbols"] == 50
    assert manifest["unique_trade_dates"] == 120
    assert manifest["original_dc03_risk_severity_distribution"] == {"HIGH": 10, "MEDIUM": 5990}
    assert len(diagnostics) == 6000
    assert {LOW_BUCKET, MEDIUM_BUCKET, HIGH_BUCKET}.issubset({row["risk_score_bucket"] for row in diagnostics})
    assert {LOW_BUCKET, MEDIUM_BUCKET, HIGH_BUCKET}.issubset({row["risk_severity_tiered"] for row in diagnostics})
    assert all(float(row["risk_score_numeric"]) >= 0 for row in diagnostics)
    assert any(row["distribution_name"] == "risk_score_bucket_distribution" for row in distribution)
    assert {LOW_BUCKET, MEDIUM_BUCKET, HIGH_BUCKET}.issubset({row["risk_score_bucket"] for row in metrics})
    assert manifest["minimum_bucket_size_warning"] is True
    assert manifest["risk_bucket_collapse_detected"] is False


def test_goal_risk_tiering01_preserves_no_lookahead_and_downstream_locks() -> None:
    assert run_goal_risk_tiering01_risk_severity_numeric_score_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    diagnostics = _rows(DIAGNOSTICS_PATH)
    workflow = _workflow()

    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert manifest["score_construction_excludes_future_returns"] is True
    assert manifest["future_returns_used_only_for_post_hoc_evaluation"] is True
    assert manifest["no_lookahead_score_construction_check"] is True
    assert manifest["score_input_fields_do_not_include_future_return_labels"] is True
    assert manifest["signal_classification"] == "risk_tiering_signal_weak_or_unreliable"
    assert "adjust_deterministic_governance_risk_rules" in manifest["recommended_next_goal"]
    assert all("forward_return" not in row["risk_tiering_rule_ids"] for row in diagnostics)
    assert all("benchmark_excess_return" not in row["risk_tiering_rule_ids"] for row in diagnostics)

    assert workflow["goal_risk_tiering01_risk_severity_numeric_score_gate"]["status"] == "implemented_review_only"
    assert workflow["goal_risk_tiering01_risk_severity_numeric_score_gate"]["implemented_in_repo"] == "true"
    assert workflow["goal_risk_tiering01_risk_severity_numeric_score_gate"]["depends_on"] == "goal10b3_recommendation_backtest_revalidation"
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

from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.backtest.goal10b1 import (
    AUDIT_PATH,
    DIAGNOSTIC_SUMMARY_PATH,
    FALSE_BOUNDARY_KEYS,
    LABEL_SOURCE_COVERAGE_AUDIT_PATH,
    MANIFEST_PATH,
    RECOMMENDATION_DISTRIBUTION_AUDIT_PATH,
    REPAIRED_RECOMMENDATION_METRICS_PATH,
    REPAIRED_SNAPSHOT_PATH,
    audit_goal10b1_backtest_coverage_repair_gate,
    run_goal10b1_backtest_coverage_repair_gate,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal10b1_runner_is_review_only_and_deterministic() -> None:
    assert run_goal10b1_backtest_coverage_repair_gate(ROOT)
    first = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert run_goal10b1_backtest_coverage_repair_gate(ROOT)
    second = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert first == second
    assert audit_goal10b1_backtest_coverage_repair_gate(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")


def test_goal10b1_classifies_repair_not_possible_without_fabricating_outputs() -> None:
    assert run_goal10b1_backtest_coverage_repair_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    summary = _rows(DIAGNOSTIC_SUMMARY_PATH)

    assert manifest["status"] == "PASS_WITH_WARNINGS"
    assert manifest["repair_decision"] == "coverage_repair_not_possible_with_current_artifacts"
    assert manifest["goal08b_unique_symbols"] == 1
    assert manifest["goal08b_recommendation_group_count"] == 1
    assert manifest["goal08b_risk_severity_group_count"] == 1
    assert manifest["repaired_snapshot_generated"] is False
    assert manifest["repaired_group_metrics_generated"] is False
    assert not (ROOT / REPAIRED_SNAPSHOT_PATH).exists()
    assert not (ROOT / REPAIRED_RECOMMENDATION_METRICS_PATH).exists()
    assert any(row["finding_code"] == "coverage_repair_not_possible_with_current_artifacts" for row in summary)


def test_goal10b1_audits_recommendation_and_label_coverage_sources() -> None:
    assert run_goal10b1_backtest_coverage_repair_gate(ROOT)
    distribution = _rows(RECOMMENDATION_DISTRIBUTION_AUDIT_PATH)
    coverage = _rows(LABEL_SOURCE_COVERAGE_AUDIT_PATH)

    recommendation = [row for row in distribution if row["dimension"] == "recommendation_eligibility"]
    risk = [row for row in distribution if row["dimension"] == "risk_severity"]
    assert recommendation == [
        {
            "dimension": "recommendation_eligibility",
            "value": "blocked_high_risk",
            "row_count": "100",
            "unique_symbols": "1",
            "unique_trade_dates": "100",
            "share_of_rows": "1.000000",
            "variation_status": "single_value",
        }
    ]
    assert risk[0]["value"] == "HIGH"
    assert risk[0]["variation_status"] == "single_value"

    primary = next(row for row in coverage if row["source_role"] == "goal10b_primary")
    assert primary["label_source_path"] == "outputs/samples/stage6c_source_backed_engineering_panel_sample.csv"
    assert primary["unique_symbols"] == "1"
    assert primary["t_plus_1_covered_goal08b_rows"] == "99"
    assert primary["has_forward_return_20d"] == "false"
    assert "single_symbol_label_coverage" in primary["repair_limitation_codes"]
    assert all(row["supports_repair_candidate"] == "false" for row in coverage)


def test_goal10b1_preserves_locked_boundaries_and_workflow_status() -> None:
    assert run_goal10b1_backtest_coverage_repair_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    workflow = _workflow()
    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert manifest["review_only_coverage_repair_diagnostics_generated"] is True
    assert workflow["goal10b1_backtest_coverage_repair_gate"]["status"] == "implemented_review_only"
    assert workflow["goal10b1_backtest_coverage_repair_gate"]["implemented_in_repo"] == "true"
    assert workflow["goal10b1_backtest_coverage_repair_gate"]["depends_on"] == "goal10b_backtest_review_only_validation_gate"
    assert workflow["goal10c_backtest_cost_slippage_sensitivity_gate"]["status"] == "locked_future"
    assert workflow["goal10c_backtest_cost_slippage_sensitivity_gate"]["depends_on"] in {
        "goal10b1_backtest_coverage_repair_gate",
        "goal10b2_recommendation_backtest_revalidation",
    }
    assert workflow["goal10d_backtest_failure_attribution_gate"]["status"] == "locked_future"
    assert workflow["dashboard_daily_report"]["status"] == "locked_future"
    assert workflow["signal_backtest"]["status"] == "locked_future"
    assert workflow["portfolio_backtest"]["status"] == "locked_future"

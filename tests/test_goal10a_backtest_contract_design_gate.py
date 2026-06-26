from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.contract_design.goal10a import (
    AUDIT_PATH,
    FALSE_BOUNDARY_KEYS,
    FORBIDDEN_OUTPUT_DIRS,
    GOAL10B_WORKFLOW_ID,
    GOAL10C_WORKFLOW_ID,
    GOAL10D_WORKFLOW_ID,
    MANIFEST_PATH,
    WORKFLOW_ID,
    audit_goal10a_backtest_contract_design_gate,
    run_goal10a_backtest_contract_design_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal10a_runner_is_design_only_and_deterministic() -> None:
    assert run_goal10a_backtest_contract_design_gate(ROOT)
    first = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert run_goal10a_backtest_contract_design_gate(ROOT)
    second = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert first == second
    assert audit_goal10a_backtest_contract_design_gate(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")


def test_goal10a_input_contract_uses_goal08b_and_goal09_never_actionable_diagnostics() -> None:
    assert run_goal10a_backtest_contract_design_gate(ROOT)
    contract = _json("configs/backtest/goal10a_backtest_input_contract.yaml")
    manifest = _json(MANIFEST_PATH)
    assert contract["mode"] == "design_only"
    assert contract["required_input_grain"] == "trade_date + symbol"
    assert contract["source_artifacts"]["goal08b_rows_are_actionable"] is False
    assert contract["source_artifacts"]["goal09_rows_are_actionable"] is False
    assert "recommendation_diagnostic_label" in contract["required_goal08b_fields"]
    assert "position_band_status" in contract["required_goal09_fields"]
    assert manifest["source_goal08b_rows"] == 100
    assert manifest["source_goal09_rows"] == 100
    assert manifest["source_trade_date_symbol_keys_match"] is True
    assert manifest["goal08b_actionability_status_values"] == ["never_actionable"]
    assert manifest["goal09_position_actionability_status_values"] == ["never_actionable"]


def test_goal10a_metric_contract_defines_future_metrics_without_running_them() -> None:
    assert run_goal10a_backtest_contract_design_gate(ROOT)
    contract = _json("configs/backtest/goal10a_backtest_metric_contract.yaml")
    metric_names = [row["metric_name"] for row in contract["future_metric_definitions"]]
    for expected in [
        "forward_return_1d",
        "forward_return_5d",
        "forward_return_20d",
        "benchmark_excess_return",
        "hit_rate",
        "mean_return",
        "median_return",
        "volatility",
        "max_drawdown",
        "IC",
        "Rank IC",
    ]:
        assert expected in metric_names
    assert contract["goal10a_runs_metrics"] is False
    assert contract["metric_output_row_count"] == 0


def test_goal10a_execution_policy_enforces_t_plus_1_no_lookahead_and_tradability_rules() -> None:
    assert run_goal10a_backtest_contract_design_gate(ROOT)
    policy = _json("configs/backtest/goal10a_execution_alignment_policy.yaml")
    assert policy["t_plus_1_execution_required"] is True
    assert policy["same_day_execution_allowed"] is False
    assert policy["date_alignment"]["signal_date"].startswith("The PIT-safe date")
    assert policy["date_alignment"]["execution_date"].startswith("The first eligible")
    assert policy["no_lookahead_constraints"]["future_returns_may_not_select_or_filter_inputs"] is True
    assert policy["benchmark_contract"]["benchmark_return_window_matches_row_window"] is True
    assert policy["cost_slippage_sensitivity"]["defined_for_future_use"] is True
    assert policy["cost_slippage_sensitivity"]["goal10a_runs_sensitivity"] is False
    assert policy["tradability_policy"]["suspended_at_execution"].startswith("mark_unevaluable")
    assert policy["tradability_policy"]["missing_price"].startswith("mark_missing_price")


def test_goal10a_grouping_contract_and_workflow_keep_future_backtest_gates_locked() -> None:
    assert run_goal10a_backtest_contract_design_gate(ROOT)
    grouping = _json("configs/backtest/goal10a_backtest_grouping_contract.yaml")
    groups = {row["group_name"]: row for row in grouping["future_grouping_rules"]}
    for expected in [
        "recommendation_eligibility_status",
        "actionability_status",
        "risk_severity",
        "position_band_status",
        "warning_category",
    ]:
        assert expected in groups
    assert grouping["goal10a_runs_group_evaluation"] is False

    workflow = _workflow()
    assert workflow[WORKFLOW_ID]["status"] == "implemented_design_only"
    assert workflow[WORKFLOW_ID]["implemented_in_repo"] == "true"
    assert workflow[GOAL10B_WORKFLOW_ID]["status"] == "implemented_review_only"
    assert workflow[GOAL10B_WORKFLOW_ID]["implemented_in_repo"] == "true"
    for workflow_id in [GOAL10C_WORKFLOW_ID, GOAL10D_WORKFLOW_ID]:
        assert workflow[workflow_id]["status"] == "locked_future"
        assert workflow[workflow_id]["implemented_in_repo"] == "false"
    assert workflow["dashboard_daily_report"]["status"] == "locked_future"


def test_goal10a_generates_no_backtest_or_downstream_outputs() -> None:
    assert run_goal10a_backtest_contract_design_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    for rel in FORBIDDEN_OUTPUT_DIRS:
        assert not (ROOT / rel).exists()

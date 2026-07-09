from __future__ import annotations

import csv
import importlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PREFIX = "outputs/research/goal_premarket_portfolio_risk_management01_"
MANIFEST_PATH = "outputs/audits/goal_premarket_portfolio_risk_management01_manifest.json"
AUDIT_PATH = "outputs/audits/goal_premarket_portfolio_risk_management01_audit.md"
REPORT_PATH = "outputs/audits/goal_premarket_portfolio_risk_management01_report.md"
HANDOFF_PATH = "docs/research/GOAL_PREMARKET_PORTFOLIO_RISK_MANAGEMENT01_GOVERNANCE_HANDOFF.md"
ALPHA_HANDOFF_PATH = "docs/research/GOAL_PREMARKET_PORTFOLIO_RISK_MANAGEMENT01_FUTURE_ALPHA_TILT_HANDOFF.md"

REQUIRED_OUTPUTS = [
    PREFIX + "provider_comparison.csv",
    PREFIX + "provider_discrepancy_quarantine.csv",
    PREFIX + "canonical_market_data_contract.csv",
    PREFIX + "canonical_market_data.csv",
    PREFIX + "canonical_risk_dataset_summary.csv",
    PREFIX + "current_holdings_input_contract.csv",
    PREFIX + "research_reference_portfolio.csv",
    PREFIX + "risk_estimator_comparison.csv",
    PREFIX + "covariance_quality_summary.csv",
    PREFIX + "portfolio_risk_state.csv",
    PREFIX + "risk_contribution_summary.csv",
    PREFIX + "concentration_summary.csv",
    PREFIX + "correlation_cluster_summary.csv",
    PREFIX + "drawdown_tail_risk_summary.csv",
    PREFIX + "position_constraint_catalog.csv",
    PREFIX + "position_constraint_evaluation.csv",
    PREFIX + "constraint_breach_summary.csv",
    PREFIX + "policy_catalog.csv",
    PREFIX + "policy_walk_forward_summary.csv",
    PREFIX + "policy_holdout_summary.csv",
    PREFIX + "policy_risk_comparison.csv",
    PREFIX + "policy_turnover_summary.csv",
    PREFIX + "policy_cost_sensitivity.csv",
    PREFIX + "policy_regime_stability.csv",
    PREFIX + "preferred_research_policy_decision.csv",
    PREFIX + "position_band_summary.csv",
    PREFIX + "position_band_stability.csv",
    PREFIX + "position_band_abstentions.csv",
    PREFIX + "construction_warnings.csv",
    REPORT_PATH,
    MANIFEST_PATH,
    AUDIT_PATH,
    HANDOFF_PATH,
    ALPHA_HANDOFF_PATH,
]


def _module():
    try:
        return importlib.import_module("ashare_premarket.portfolio_risk.goal_premarket_portfolio_risk_management01")
    except ModuleNotFoundError as exc:
        assert False, f"missing portfolio risk module: {exc}"


def _run_gate() -> dict[str, object]:
    module = _module()
    assert module.run_goal_premarket_portfolio_risk_management01(ROOT)
    assert module.audit_goal_premarket_portfolio_risk_management01(ROOT)
    return json.loads((ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))


def _rows(rel: str) -> list[dict[str, str]]:
    with (ROOT / rel).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


_MANIFEST: dict[str, object] | None = None


def _manifest_once() -> dict[str, object]:
    global _MANIFEST
    if _MANIFEST is None:
        _MANIFEST = _run_gate()
    return _MANIFEST


def test_required_outputs_and_research_only_boundary() -> None:
    manifest = _manifest_once()
    for rel in REQUIRED_OUTPUTS:
        assert (ROOT / rel).exists(), rel

    assert manifest["status"] in {"PASS", "PASS_WITH_WARNINGS"}
    assert manifest["goal"] == "GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01"
    assert manifest["research_only"] is True
    assert manifest["not_trading_advice"] is True
    assert manifest["not_for_execution"] is True
    assert manifest["recommendation_outputs_created"] is False
    assert manifest["buy_sell_hold_outputs_created"] is False
    assert manifest["orders_created"] is False
    assert manifest["broker_trading_outputs_created"] is False
    assert manifest["production_outputs_created"] is False
    assert manifest["dashboard_frontend_artifacts_created"] is False
    assert manifest["local_lake_outputs_created"] is False
    assert manifest["dqn_rl_outputs_created"] is False


def test_phase1_provider_reconciliation_canonical_data_and_quarantine() -> None:
    manifest = _manifest_once()
    assert manifest["phase1_provider_overlap_rows"] > 0
    assert manifest["phase1_quarantined_rows"] >= 0
    assert manifest["canonical_rows"] == 34543
    assert manifest["canonical_symbols"] == 41
    assert manifest["canonical_dates"] == 843
    assert manifest["provider_reconciliation_status"] in {
        "pass",
        "pass_with_material_discrepancy_quarantine",
    }

    comparison = {row["comparison_id"]: row for row in _rows(PREFIX + "provider_comparison.csv")}
    row = comparison["baostock_vs_akshare_sina_forward_return_1d"]
    assert int(row["overlap_rows"]) == manifest["phase1_provider_overlap_rows"]
    assert row["canonical_decision"] == "akshare_sina_primary_with_baostock_overlap_diagnostics"
    assert row["material_discrepancy_policy"] == "quarantine_from_risk_model_fitting"

    contract_rows = _rows(PREFIX + "canonical_market_data_contract.csv")
    assert {row["field_name"] for row in contract_rows} >= {
        "canonical_close",
        "canonical_return_1d",
        "canonical_price_status",
        "canonical_return_status",
        "risk_model_eligible",
    }

    canonical_sample = _rows(PREFIX + "canonical_market_data.csv")[:20]
    assert canonical_sample
    assert all(row["not_for_execution"] == "true" for row in canonical_sample)
    assert all(row["research_only"] == "true" for row in canonical_sample)


def test_phase2_risk_state_uses_reference_mode_without_fabricated_holdings() -> None:
    manifest = _manifest_once()
    assert manifest["current_holdings_mode"] == "research_reference_portfolio_mode"
    assert manifest["current_holdings_fabricated"] is False
    assert manifest["risk_estimators_compared"] >= 3
    assert manifest["covariance_estimators_compared"] >= 3

    state_rows = _rows(PREFIX + "portfolio_risk_state.csv")
    assert len(state_rows) == 1
    state = state_rows[0]
    assert state["portfolio_id"] == "research_reference_portfolio"
    assert state["risk_state"] in {
        "normal_risk_review_only",
        "elevated_volatility_review_only",
        "stressed_risk_review_only",
        "abstain_insufficient_confidence",
    }
    assert state["decision_rule_trace"]
    assert state["buy_sell_hold_generated"] == "false"

    contributions = _rows(PREFIX + "risk_contribution_summary.csv")
    assert contributions
    assert abs(sum(float(row["risk_contribution_share"]) for row in contributions) - 1.0) < 0.02


def test_phase3_constraint_engine_is_non_actionable_and_fail_closed() -> None:
    manifest = _manifest_once()
    assert manifest["constraints_implemented"] >= 6
    assert manifest["constraint_engine_non_actionable"] is True
    assert manifest["fail_closed_cases"] >= 1

    catalog = _rows(PREFIX + "position_constraint_catalog.csv")
    assert {row["constraint_id"] for row in catalog} >= {
        "max_symbol_weight",
        "max_symbol_risk_contribution",
        "min_history_observations",
        "quarantined_rows_excluded",
    }

    evaluations = _rows(PREFIX + "position_constraint_evaluation.csv")
    assert evaluations
    assert all(row["action_instruction"] == "none" for row in evaluations)
    assert any(row["fail_closed"] == "true" for row in evaluations)


def test_phase4_policy_comparison_has_fixed_policies_chronological_splits_and_costs() -> None:
    manifest = _manifest_once()
    assert set(manifest["policies_evaluated"]) >= {
        "equal_weight",
        "inverse_volatility",
        "minimum_variance_diagonal",
        "equal_risk_contribution_diagonal",
    }
    assert manifest["policy_selection_basis"] == "risk_first_not_return_optimized"
    assert manifest["historical_portfolio_returns_research_only"] is True

    catalog = _rows(PREFIX + "policy_catalog.csv")
    assert all(row["pre_specified"] == "true" for row in catalog)
    assert all(row["final_holdout_tuned"] == "false" for row in catalog)

    walk = _rows(PREFIX + "policy_walk_forward_summary.csv")
    holdout = _rows(PREFIX + "policy_holdout_summary.csv")
    costs = _rows(PREFIX + "policy_cost_sensitivity.csv")
    assert walk and holdout and costs
    assert all(row["chronological_split"] == "true" for row in walk)
    assert all(row["research_only"] == "true" and row["not_for_execution"] == "true" for row in holdout)
    assert {row["cost_bps"] for row in costs} >= {"0", "10", "30"}


def test_phase5_position_bands_are_bounded_not_target_weight_recommendations() -> None:
    manifest = _manifest_once()
    assert manifest["symbols_with_bands"] + manifest["symbols_abstained"] == manifest["canonical_symbols"]
    assert manifest["position_bands_are_target_weights"] is False
    assert manifest["position_bands_generate_orders"] is False

    bands = _rows(PREFIX + "position_band_summary.csv")
    assert bands
    assert all(row["target_weight"] == "" for row in bands)
    assert all(row["order_instruction"] == "none" for row in bands)
    assert all(row["alpha_required"] == "false" for row in bands)
    assert {row["constraint_integration_status"] for row in bands} <= {
        "constraints_applied",
        "abstain_due_to_data_or_constraint_uncertainty",
    }


def test_governance_locks_ready_factor_and_deterministic_replay() -> None:
    first = _run_gate()
    first_state = (ROOT / (PREFIX + "portfolio_risk_state.csv")).read_text(encoding="utf-8")
    first_bands = (ROOT / (PREFIX + "position_band_summary.csv")).read_text(encoding="utf-8")
    second = _run_gate()
    second_state = (ROOT / (PREFIX + "portfolio_risk_state.csv")).read_text(encoding="utf-8")
    second_bands = (ROOT / (PREFIX + "position_band_summary.csv")).read_text(encoding="utf-8")
    assert first == second
    assert first_state == second_state
    assert first_bands == second_bands

    workflow = {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}
    assert workflow["goal_premarket_portfolio_risk_management01"]["status"] == "implemented_research_only"
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["status"] == "locked_future"
    assert workflow["goal10b4_recommendation_backtest_revalidation"]["status"] == "locked_future"
    assert workflow["goal_position_band_validation01_position_band_validation_gate"]["status"] == "locked_future"

    manifest = _manifest_once()
    assert manifest["ready_factor_count"] == 0
    assert manifest["rec_tiering_state"] == "locked_future"
    assert manifest["recommendation_state"] == "locked_future"
    assert manifest["trading_state"] == "locked_future"
    assert manifest["credential_dependency_required"] is False
    assert manifest["tokens_or_secrets_persisted"] is False

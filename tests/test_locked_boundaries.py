from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_locked_capabilities_remain_false() -> None:
    locked = json.loads((ROOT / "configs/project/locked_capabilities.json").read_text(encoding="utf-8"))
    assert locked["position_band_recommendation"] in {False, "future_review_only", "implemented_review_only"}
    assert locked["goal091_position_band_warning_dashboard_readiness_gate"] == "implemented_review_only"
    assert locked["goal_v1_integrity01_artifact_lineage_structure_gate"] == "implemented_infrastructure_only"
    assert locked["goal10a_backtest_contract_design_gate"] == "implemented_design_only"
    assert locked["goal10b_backtest_review_only_validation_gate"] == "implemented_review_only"
    assert locked["goal10b1_backtest_coverage_repair_gate"] == "implemented_review_only"
    assert locked["goal_data_label01_forward_return_label_coverage_expansion"] == "implemented_review_only"
    assert locked["goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"] == "implemented_review_only"
    assert locked["goal10b2_recommendation_backtest_revalidation"] == "implemented_review_only"
    assert locked["goal10c_backtest_cost_slippage_sensitivity_gate"] == "implemented_review_only"
    assert locked["goal_data_provider02a_multi_provider_capability_probe"] == "implemented_review_only"
    assert locked["goal_data_provider02a1_network_opt_in_provider_smoke_test"] == "implemented_review_only"
    assert locked["goal_data_provider02b_provider_selection_gate"] == "implemented_review_only"
    assert locked["goal_data_panel02_evaluation_panel_gate"] is False
    assert locked["goal_v1_diagnostic_coverage03_multi_provider_diagnostics"] is False
    assert locked["goal10b3_recommendation_backtest_revalidation"] is False
    assert locked["goal10d_backtest_failure_attribution_gate"] is False
    for key in [
        "signal_backtest",
        "portfolio_backtest",
        "dashboard",
        "paper_trading",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
        "dqn_rl",
    ]:
        assert locked[key] is False


def test_active_source_has_no_locked_imports() -> None:
    import ast

    for path in (ROOT / "src").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name.lower() for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [(node.module or "").lower()]
            assert not any(token in name for name in names for token in ["dashboard", "dqn", "paper_trading"])

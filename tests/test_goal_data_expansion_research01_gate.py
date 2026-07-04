from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.data_expansion.goal_data_expansion_research01 import (
    AUDIT_PATH,
    MANIFEST_PATH,
    OUTPUTS,
    WORKFLOW_ID,
    audit_goal_data_expansion_research01_gate,
    run_goal_data_expansion_research01_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _workflow() -> dict[str, dict[str, str]]:
    with (ROOT / "configs/project/workflow_status.csv").open(newline="", encoding="utf-8") as handle:
        return {row["workflow_id"]: row for row in csv.DictReader(handle)}


def test_goal_data_expansion_research01_runner_writes_bounded_research_only_outputs() -> None:
    assert run_goal_data_expansion_research01_gate(ROOT)
    assert audit_goal_data_expansion_research01_gate(ROOT)

    manifest = json.loads((ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))
    workflow = _workflow()
    assert manifest["status"] == "PASS_WITH_WARNINGS"
    assert manifest["run_mode"] == "offline_dry_run"
    assert manifest["selected_source_count"] == 29
    assert manifest["expanded_date_regime_feature_panel_row_count"] == 120
    assert manifest["expanded_symbol_context_panel_row_count"] == 6000
    assert manifest["factor_evaluation_performed"] is False
    assert manifest["recommendation_outputs_created"] is False
    assert manifest["portfolio_returns_created"] is False
    assert manifest["equity_curves_created"] is False
    assert manifest["dashboard_frontend_artifacts_created"] is False
    assert workflow[WORKFLOW_ID]["status"] == "implemented_research_only"
    assert workflow["goal_regime_label_research02_expanded_market_regime_label_refinement_gate"]["status"] in {"locked_future", "implemented_research_only"}
    assert workflow["goal_quant_research04_regime_conditional_factor_evaluation_gate"]["status"] == "locked_future"
    assert workflow["dashboard_daily_report"]["status"] == "locked_future"
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")
    for path in OUTPUTS:
        assert (ROOT / path).exists()

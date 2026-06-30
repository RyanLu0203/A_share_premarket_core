from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.architecture.goal_architecture_refactor03 import (
    AKSHARE_CATALOG_CSV_PATH,
    GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID,
    GOAL_QUANT_RESEARCH04_WORKFLOW_ID,
    MANIFEST_PATH,
    WORKFLOW_ID,
    audit_goal_architecture_refactor03_gate,
    evaluate_goal_architecture_refactor03,
    run_goal_architecture_refactor03_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal_architecture_refactor03_evaluation_is_metadata_only() -> None:
    result = evaluate_goal_architecture_refactor03(ROOT)
    manifest = result["manifest"]
    assert manifest["status"] in {"PASS", "PASS_WITH_WARNINGS"}
    assert manifest["catalog_source_count"] >= 50
    assert manifest["provider_registry_count"] >= 3
    assert manifest["full_live_akshare_dataset_fetch_performed"] is False
    assert manifest["scientific_outputs_changed"] is False
    assert manifest["recommended_next_goal"] == "GOAL-DATA-EXPANSION-RESEARCH-01-MARKET-REGIME-DATA-EXPANSION-GATE"


def test_goal_architecture_refactor03_runner_preserves_locks() -> None:
    assert run_goal_architecture_refactor03_gate(ROOT)
    assert audit_goal_architecture_refactor03_gate(ROOT)
    manifest = json.loads((ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))
    catalog_rows = _rows(AKSHARE_CATALOG_CSV_PATH)
    workflow = _workflow()
    assert manifest["status"] in {"PASS", "PASS_WITH_WARNINGS"}
    assert len(catalog_rows) == manifest["catalog_source_count"]
    assert workflow[WORKFLOW_ID]["status"] == "implemented_engineering_research_support"
    assert workflow[GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID]["status"] == "locked_future"
    assert workflow[GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID]["depends_on"] == WORKFLOW_ID
    assert workflow[GOAL_QUANT_RESEARCH04_WORKFLOW_ID]["status"] == "locked_future"
    assert workflow[GOAL_QUANT_RESEARCH04_WORKFLOW_ID]["depends_on"] == GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID
    assert manifest["recommendation_outputs_created"] is False
    assert manifest["dashboard_frontend_artifacts_created"] is False

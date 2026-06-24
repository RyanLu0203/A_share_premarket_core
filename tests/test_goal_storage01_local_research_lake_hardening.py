from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.storage.lake_hardening import (
    REQUIRED_DIRECTORY_KEYS,
    REQUIRED_PLACEMENT_RULES,
    audit_goal_storage01_local_research_lake_hardening_gate,
    run_goal_storage01_local_research_lake_hardening_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _workflow() -> dict[str, dict[str, str]]:
    with (ROOT / "configs/project/workflow_status.csv").open(newline="", encoding="utf-8") as handle:
        return {row["workflow_id"]: row for row in csv.DictReader(handle)}


def test_goal_storage01_runner_is_infrastructure_only_and_deterministic() -> None:
    assert run_goal_storage01_local_research_lake_hardening_gate(ROOT)
    first = (ROOT / "outputs/audits/goal_storage01_local_research_lake_hardening_manifest.json").read_text(encoding="utf-8")
    assert run_goal_storage01_local_research_lake_hardening_gate(ROOT)
    second = (ROOT / "outputs/audits/goal_storage01_local_research_lake_hardening_manifest.json").read_text(encoding="utf-8")
    assert first == second
    assert audit_goal_storage01_local_research_lake_hardening_gate(ROOT)


def test_goal_storage01_contract_defines_root_boundaries_and_future_placement() -> None:
    assert run_goal_storage01_local_research_lake_hardening_gate(ROOT)
    contract = _json("configs/storage/goal_storage01_local_research_lake_contract.yaml")
    root_contract = contract["data_root_resolution"]
    assert root_contract["required_env_var"] == "ASHARE_PREMARKET_DATA_ROOT"
    assert root_contract["fallback_default_documentation_only"] is True
    assert root_contract["production_deployment_assumed"] is False
    assert root_contract["runner_creates_data_root"] is False
    assert set(REQUIRED_DIRECTORY_KEYS) <= set(contract["directory_boundaries"])
    assert set(REQUIRED_PLACEMENT_RULES) <= set(contract["future_placement_rules"])
    assert contract["bundle_versioning_rules"]["immutable_bundle_ids"] is True
    assert contract["checksum_requirements"]["algorithm"] == "sha256"
    assert contract["schema_registry_rules"]["committed_registry"] == "configs/storage/table_schema_registry.yaml"


def test_goal_storage01_manifest_and_workflow_keep_goal08b_locked() -> None:
    assert run_goal_storage01_local_research_lake_hardening_gate(ROOT)
    manifest = _json("outputs/audits/goal_storage01_local_research_lake_hardening_manifest.json")
    workflow = _workflow()
    assert workflow["goal_storage01_local_research_lake_hardening_gate"]["status"] == "implemented_infrastructure_only"
    assert workflow["goal_storage01_local_research_lake_hardening_gate"]["implemented_in_repo"] == "true"
    assert workflow["goal08a_recommendation_contract_design_gate"]["status"] == "implemented_design_only"
    assert workflow["goal08b_recommendation_review_only_prototype"]["status"] == "locked_future"
    assert workflow["goal08b_recommendation_review_only_prototype"]["implemented_in_repo"] == "false"
    assert manifest["mode"] == "infrastructure_only"
    assert manifest["goal08b_status_after_goal_storage01"] == "locked_future"
    assert manifest["goal08b_implemented_by_this_gate"] is False
    assert manifest["goal08b_unlocked_by_this_gate"] is False
    assert manifest["local_data_root_materialized_by_this_gate"] is False
    assert manifest["local_data_files_created"] is False


def test_goal_storage01_has_no_heavy_or_downstream_outputs() -> None:
    assert run_goal_storage01_local_research_lake_hardening_gate(ROOT)
    manifest = _json("outputs/audits/goal_storage01_local_research_lake_hardening_manifest.json")
    assert manifest["tracked_forbidden_artifact_count"] == 0
    for key in [
        "source_coverage_expanded",
        "symbol_coverage_expanded",
        "full_market_fetch_performed",
        "recommendation_rows_generated",
        "buy_sell_hold_outputs_generated",
        "position_sizing_generated",
        "portfolio_construction_generated",
        "dashboard_generated",
        "paper_trading_enabled",
        "live_trading_enabled",
        "broker_integration_enabled",
        "production_model_behavior_created",
        "database_writes_created",
        "backtests_run",
        "factor_mining_outputs_created",
        "dqn_rl_outputs_created",
        "workflow_downstream_unlocked",
    ]:
        assert manifest[key] is False
    for rel in [
        "outputs/recommendations",
        "outputs/positions",
        "outputs/dashboard",
        "outputs/paper_trading",
        "outputs/live_trading",
        "outputs/backtests",
        "outputs/factors",
    ]:
        assert not (ROOT / rel).exists()

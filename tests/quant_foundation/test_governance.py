from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.core.workflow import CLASS_A_CAPABILITIES
from ashare_premarket.core.constants import PUBLIC_COMMANDS
from ashare_premarket.quant_foundation.audit import audit_goal11_foundation
from ashare_premarket.quant_foundation.features import load_feature_config

ROOT = Path(__file__).resolve().parents[2]


def test_goal11_is_one_registered_research_only_goal() -> None:
    locked = json.loads(
        (ROOT / "configs/project/locked_capabilities.json").read_text(encoding="utf-8")
    )
    with (ROOT / "configs/project/workflow_status.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        workflow = {row["workflow_id"]: row for row in csv.DictReader(handle)}
    capabilities = {cap.capability_id: cap for cap in CLASS_A_CAPABILITIES}

    assert locked["goal11_quant_intelligence_foundation"] == "implemented_research_only"
    assert workflow["goal11_quant_intelligence_foundation"]["status"] == "implemented_research_only"
    assert workflow["goal11_quant_intelligence_foundation"]["implemented_in_repo"] == "true"
    assert "goal11_quant_intelligence_foundation" in capabilities
    assert capabilities["goal11_quant_intelligence_foundation"].owner_module == (
        "ashare_premarket.quant_foundation"
    )


def test_goal11_preserves_interfaces_production_locks_and_dashboard_deferral() -> None:
    registry = json.loads(
        (ROOT / "configs/project/canonical_interfaces.json").read_text(encoding="utf-8")
    )
    locked = json.loads(
        (ROOT / "configs/project/locked_capabilities.json").read_text(encoding="utf-8")
    )
    config = load_feature_config(ROOT)

    assert len(registry["interfaces"]) == 14
    assert len(registry["api_routes"]) == 22
    assert {method for route in registry["api_routes"] for method in route["methods"]} == {"GET"}
    assert config["governance"]["dashboard_integration"] == "DEFERRED_LOCK_PRESERVED"
    assert config["governance"]["ready_factor_count"] == 0
    for key in (
        "broker_live_trading",
        "dashboard",
        "dqn_rl",
        "factor_mining",
        "paper_trading",
        "production_db_writes",
        "production_model_promotion",
    ):
        assert locked[key] is False


def test_goal11_audit_passes_without_committed_runtime_artifacts() -> None:
    result = audit_goal11_foundation(ROOT)

    assert result["status"] == "PASS"
    assert result["ready_factor_count"] == 0
    assert result["api_route_count"] == 22
    assert result["generated_datasets_required"] is False
    assert result["production_locks_preserved"] is True
    assert "outputs/local/" in (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert (ROOT / "docs/quant/GOAL11_QUANT_INTELLIGENCE_RESEARCH_GUIDE.md").exists()


def test_goal11_audit_has_a_fresh_clone_safe_public_wrapper() -> None:
    command = "scripts/audit_goal11_quant_intelligence_foundation.py"
    assert command in PUBLIC_COMMANDS
    assert (ROOT / command).is_file()

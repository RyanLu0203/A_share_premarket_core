from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.alpha_validation.audit import audit_goal12_framework
from ashare_premarket.alpha_validation.config import load_goal12_config
from ashare_premarket.core.constants import PUBLIC_COMMANDS
from ashare_premarket.core.workflow import CLASS_A_CAPABILITIES

ROOT = Path(__file__).resolve().parents[2]


def test_goal12_is_one_registered_research_only_capability() -> None:
    locked = json.loads(
        (ROOT / "configs/project/locked_capabilities.json").read_text(encoding="utf-8")
    )
    with (ROOT / "configs/project/workflow_status.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        workflow = {row["workflow_id"]: row for row in csv.DictReader(handle)}
    capabilities = {row.capability_id: row for row in CLASS_A_CAPABILITIES}

    assert locked["goal12_alpha_validation_robustness"] == "implemented_research_only"
    assert workflow["goal12_alpha_validation_robustness"]["status"] == "implemented_research_only"
    assert workflow["goal12_alpha_validation_robustness"]["implemented_in_repo"] == "true"
    assert capabilities["goal12_alpha_validation_robustness"].owner_module == (
        "ashare_premarket.alpha_validation"
    )


def test_goal12_preserves_topology_locks_and_local_artifact_policy() -> None:
    registry = json.loads(
        (ROOT / "configs/project/canonical_interfaces.json").read_text(encoding="utf-8")
    )
    locked = json.loads(
        (ROOT / "configs/project/locked_capabilities.json").read_text(encoding="utf-8")
    )
    config = load_goal12_config(ROOT)

    assert len(registry["interfaces"]) == 14
    assert len(registry["api_routes"]) == 22
    assert {method for route in registry["api_routes"] for method in route["methods"]} == {"GET"}
    assert config["governance"]["production_ready"] is False
    assert config["governance"]["ready_factor_count"] == 0
    assert "outputs/local/" in (ROOT / ".gitignore").read_text(encoding="utf-8")
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


def test_goal12_audit_and_public_wrappers_are_fresh_clone_safe() -> None:
    result = audit_goal12_framework(ROOT)

    assert result["status"] == "PASS"
    assert result["interface_count"] == 14
    assert result["api_route_count"] == 22
    assert result["write_route_count"] == 0
    assert result["production_ready"] is False
    assert result["ready_factor_count"] == 0
    for command in (
        "scripts/run_goal12_alpha_validation.py",
        "scripts/audit_goal12_alpha_validation.py",
    ):
        assert command in PUBLIC_COMMANDS
        assert (ROOT / command).is_file()

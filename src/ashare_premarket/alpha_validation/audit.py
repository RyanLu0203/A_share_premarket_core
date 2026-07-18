from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

from ashare_premarket.alpha_validation.config import load_goal12_config
from ashare_premarket.core.constants import PUBLIC_COMMANDS

_PRODUCTION_LOCKS = (
    "broker_live_trading",
    "dashboard",
    "dqn_rl",
    "factor_mining",
    "paper_trading",
    "production_db_writes",
    "production_model_promotion",
)
_REQUIRED_FILES = (
    "configs/quant/goal12_alpha_validation_v1.json",
    "docs/quant/GOAL12_ALPHA_VALIDATION_ARCHITECTURE.md",
    "docs/quant/GOAL12_LABEL_AND_SPLIT_CONTRACT.md",
    "docs/quant/GOAL12_RESEARCH_DECISION_POLICY.md",
    "docs/quant/GOAL12_STATISTICAL_VALIDATION_METHOD.md",
    "scripts/run_goal12_alpha_validation.py",
    "scripts/audit_goal12_alpha_validation.py",
    "src/ashare_premarket/alpha_validation/config.py",
    "src/ashare_premarket/alpha_validation/data.py",
    "src/ashare_premarket/alpha_validation/decisions.py",
    "src/ashare_premarket/alpha_validation/folds.py",
    "src/ashare_premarket/alpha_validation/labels.py",
    "src/ashare_premarket/alpha_validation/models.py",
    "src/ashare_premarket/alpha_validation/nulls.py",
    "src/ashare_premarket/alpha_validation/pipeline.py",
    "src/ashare_premarket/alpha_validation/preprocessing.py",
    "src/ashare_premarket/alpha_validation/research.py",
    "src/ashare_premarket/alpha_validation/robustness.py",
    "src/ashare_premarket/alpha_validation/statistics.py",
    "src/ashare_premarket/alpha_validation/store.py",
)


def audit_goal12_framework(root: Path) -> dict[str, object]:
    repository = root.resolve()
    config = load_goal12_config(repository)
    locked = json.loads(
        (repository / "configs/project/locked_capabilities.json").read_text(
            encoding="utf-8"
        )
    )
    registry = json.loads(
        (repository / "configs/project/canonical_interfaces.json").read_text(
            encoding="utf-8"
        )
    )
    with (repository / "configs/project/workflow_status.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        workflow = {row["workflow_id"]: row for row in csv.DictReader(handle)}
    tracked = _tracked_files(repository)
    attributes = (repository / ".gitattributes").read_text(encoding="utf-8")
    checks = {
        "required_files_present": all((repository / path).is_file() for path in _REQUIRED_FILES),
        "goal_capability_research_only": locked.get("goal12_alpha_validation_robustness")
        == "implemented_research_only",
        "workflow_research_only": workflow.get("goal12_alpha_validation_robustness", {}).get(
            "status"
        )
        == "implemented_research_only",
        "production_locks_preserved": all(locked.get(key) is False for key in _PRODUCTION_LOCKS),
        "production_ready_false": dict(config["governance"])["production_ready"] is False,
        "ready_factor_count_zero": dict(config["governance"])["ready_factor_count"] == 0,
        "api_routes_get_only": len(registry["api_routes"]) == 22
        and all(route["methods"] == ["GET"] for route in registry["api_routes"]),
        "canonical_interfaces_unchanged": len(registry["interfaces"]) == 14,
        "public_wrappers_registered": all(
            command in PUBLIC_COMMANDS
            for command in (
                "scripts/run_goal12_alpha_validation.py",
                "scripts/audit_goal12_alpha_validation.py",
            )
        ),
        "local_output_ignored": "outputs/local/"
        in (repository / ".gitignore").read_text(encoding="utf-8"),
        "no_goal12_runtime_outputs_tracked": not any(
            path.startswith("outputs/local/")
            or (path.startswith("outputs/") and "goal12" in path.lower())
            for path in tracked
        ),
        "goal11_byte_protections_preserved": all(
            line in attributes
            for line in (
                "outputs/research/network_ingestion/daily_panel.csv -text",
                "outputs/research/network_ingestion/index_panel.csv -text",
                "outputs/research/network_ingestion/symbol_coverage.csv -text",
            )
        ),
    }
    return {
        "goal_id": "GOAL-12",
        "status": "PASS" if all(checks.values()) else "BLOCKED",
        "checks": checks,
        "production_ready": False,
        "ready_factor_count": 0,
        "interface_count": len(registry["interfaces"]),
        "api_route_count": len(registry["api_routes"]),
        "write_route_count": sum(
            method != "GET"
            for route in registry["api_routes"]
            for method in route["methods"]
        ),
        "generated_artifact_policy": "LOCAL_IGNORED_RESEARCH_ONLY",
        "research_only": True,
    }


def _tracked_files(root: Path) -> tuple[str, ...]:
    completed = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return tuple(line.replace("\\", "/") for line in completed.stdout.splitlines())

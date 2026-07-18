from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

from ashare_premarket.quant_foundation.features import load_feature_config

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
    "configs/quant/goal11_quant_intelligence_v1.json",
    "docs/quant/GOAL11_QUANT_INTELLIGENCE_ARCHITECTURE.md",
    "docs/quant/GOAL11_QUANT_INTELLIGENCE_RESEARCH_GUIDE.md",
    "src/ashare_premarket/quant_foundation/alpha.py",
    "src/ashare_premarket/quant_foundation/contracts.py",
    "src/ashare_premarket/quant_foundation/evaluation.py",
    "src/ashare_premarket/quant_foundation/features.py",
    "src/ashare_premarket/quant_foundation/linear_ranker.py",
    "src/ashare_premarket/quant_foundation/pipeline.py",
    "src/ashare_premarket/quant_foundation/snapshot_loader.py",
    "src/ashare_premarket/quant_foundation/store.py",
)


def audit_goal11_foundation(root: Path) -> dict[str, object]:
    repository = root.resolve()
    config = load_feature_config(repository)
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
    checks = {
        "required_files_present": all((repository / path).is_file() for path in _REQUIRED_FILES),
        "goal_capability_research_only": locked.get("goal11_quant_intelligence_foundation")
        == "implemented_research_only",
        "workflow_research_only": workflow.get("goal11_quant_intelligence_foundation", {}).get(
            "status"
        )
        == "implemented_research_only",
        "production_locks_preserved": all(locked.get(key) is False for key in _PRODUCTION_LOCKS),
        "ready_factor_count_zero": dict(config["governance"])["ready_factor_count"] == 0,
        "dashboard_deferred": dict(config["governance"])["dashboard_integration"]
        == "DEFERRED_LOCK_PRESERVED",
        "api_routes_get_only": len(registry["api_routes"]) == 22
        and all(route["methods"] == ["GET"] for route in registry["api_routes"]),
        "canonical_interfaces_unchanged": len(registry["interfaces"]) == 14,
        "local_output_ignored": "outputs/local/"
        in (repository / ".gitignore").read_text(encoding="utf-8"),
        "no_goal11_runtime_outputs_tracked": not any(
            path.startswith("outputs/local/")
            or (path.startswith("outputs/") and "goal11" in path.lower())
            for path in tracked
        ),
    }
    return {
        "goal_id": "GOAL-11",
        "status": "PASS" if all(checks.values()) else "BLOCKED",
        "checks": checks,
        "ready_factor_count": 0,
        "interface_count": len(registry["interfaces"]),
        "api_route_count": len(registry["api_routes"]),
        "generated_datasets_required": False,
        "production_locks_preserved": checks["production_locks_preserved"],
        "dashboard_integration": "DEFERRED_LOCK_PRESERVED",
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


def main() -> int:
    root = Path(__file__).resolve().parents[3]
    result = audit_goal11_foundation(root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

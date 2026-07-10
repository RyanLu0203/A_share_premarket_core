from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Iterable


ISSUE24_CAPABILITY_KEY = "goal_premarket_research_position_workspace_dashboard01_gate"
ISSUE24_DASHBOARD_MODULE = "ashare_premarket.dashboard"
ISSUE24_GOAL_ID = "GOAL-PREMARKET-RESEARCH-AND-POSITION-WORKSPACE-DASHBOARD-01"
ISSUE24_WORKFLOW_ID = "goal_premarket_research_position_workspace_dashboard01"
ISSUE24_AUTHORIZED_IMPORTERS = {
    "scripts/audit_goal_premarket_research_position_workspace_dashboard01.py",
    "scripts/run_goal_premarket_research_position_workspace_dashboard01.py",
    "scripts/run_premarket_workspace.py",
    "scripts/run_premarket_workspace_api.py",
    "src/ashare_premarket/dashboard/api.py",
    "src/ashare_premarket/dashboard/goal_premarket_research_position_workspace_dashboard01.py",
    "src/ashare_premarket/dashboard/repository.py",
}


def implementation_file_sha256(path: Path) -> str:
    """Hash implementation text without platform checkout line-ending drift."""

    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def forbidden_locked_import_terms(
    root: Path,
    module_name: str,
    relative_path: str,
    locked_terms: Iterable[str],
) -> list[str]:
    lowered = module_name.lower()
    allowed_dashboard = _issue24_dashboard_import_allowed(root, lowered, relative_path)
    return [
        term
        for term in locked_terms
        if term in lowered and not (term == "dashboard" and allowed_dashboard)
    ]


def _issue24_dashboard_import_allowed(root: Path, module_name: str, relative_path: str) -> bool:
    capabilities_path = root / "configs/project/locked_capabilities.json"
    try:
        capabilities = json.loads(capabilities_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        capabilities.get(ISSUE24_CAPABILITY_KEY) == "implemented_research_only"
        and (
            module_name == ISSUE24_DASHBOARD_MODULE
            or module_name.startswith(f"{ISSUE24_DASHBOARD_MODULE}.")
        )
        and relative_path in ISSUE24_AUTHORIZED_IMPORTERS
    )


def issue24_workspace_evidence_valid(root: Path) -> bool:
    root = root.resolve()
    manifest_path = root / "outputs/audits/goal_premarket_research_position_workspace_dashboard01_manifest.json"
    audit_path = root / "outputs/audits/goal_premarket_research_position_workspace_dashboard01_audit.md"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        audit = audit_path.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError):
        return False
    checksums = manifest.get("implementation_checksums")
    return (
        manifest.get("goal") == ISSUE24_GOAL_ID
        and manifest.get("status") == "PASS"
        and manifest.get("page_count") == 23
        and manifest.get("write_api_route_count") == 0
        and manifest.get("ready_factor_count") == 0
        and "Status: `PASS`" in audit
        and (root / "apps/premarket-workspace/package.json").exists()
        and isinstance(checksums, dict)
        and bool(checksums)
        and _implementation_checksums_valid(root, checksums)
    )


def _implementation_checksums_valid(root: Path, checksums: dict[object, object]) -> bool:
    signature: list[tuple[str, str, int, int]] = []
    for relative, expected in sorted(checksums.items(), key=lambda item: str(item[0])):
        path = (root / str(relative)).resolve()
        if root not in path.parents or not path.is_file():
            return False
        stat = path.stat()
        signature.append((str(relative), str(expected), stat.st_mtime_ns, stat.st_size))
    return _implementation_checksums_valid_cached(str(root), tuple(signature))


@lru_cache(maxsize=16)
def _implementation_checksums_valid_cached(
    root: str,
    signature: tuple[tuple[str, str, int, int], ...],
) -> bool:
    base = Path(root)
    for relative, expected, _mtime_ns, _size in signature:
        if implementation_file_sha256(base / relative) != expected:
            return False
    return True


def issue24_workspace_workflow_patch() -> dict[str, str]:
    return {
        "workflow_id": ISSUE24_WORKFLOW_ID,
        "display_name": "GOAL-PREMARKET-RESEARCH-AND-POSITION-WORKSPACE-DASHBOARD-01 Local Research Workspace",
        "stage_or_goal": ISSUE24_GOAL_ID,
        "status": "implemented_research_only",
        "current_repo_role": "local_research_only_read_only_workspace",
        "implemented_in_repo": "true",
        "allowed_next_action": "review_workspace_no_downstream_unlock",
        "depends_on": "goal_premarket_position_management_operational01",
        "produces_artifacts": "apps/premarket-workspace;src/ashare_premarket/dashboard;outputs/audits/goal_premarket_research_position_workspace_dashboard01_report.md;outputs/audits/goal_premarket_research_position_workspace_dashboard01_manifest.json;outputs/audits/goal_premarket_research_position_workspace_dashboard01_audit.md;docs/research/GOAL_PREMARKET_RESEARCH_POSITION_WORKSPACE_DASHBOARD01_LOCAL_WORKSPACE.md;configs/dashboard/goal_premarket_research_position_workspace_dashboard01_contract.yaml",
        "primary_docs": "docs/research/GOAL_PREMARKET_RESEARCH_POSITION_WORKSPACE_DASHBOARD01_LOCAL_WORKSPACE.md",
        "primary_scripts": "scripts/run_premarket_workspace.py;scripts/run_premarket_workspace_api.py;scripts/run_goal_premarket_research_position_workspace_dashboard01.py;scripts/audit_goal_premarket_research_position_workspace_dashboard01.py",
        "primary_outputs": "outputs/audits/goal_premarket_research_position_workspace_dashboard01_report.md;outputs/audits/goal_premarket_research_position_workspace_dashboard01_manifest.json;outputs/audits/goal_premarket_research_position_workspace_dashboard01_audit.md",
        "promotion_rule": "implemented_research_only_after_issue24_audit_pass_no_generic_dashboard_unlock",
        "notes": "Issue #24 goal-specific local read-only research workspace. Generic dashboard workflow, Recommendation Tiering, Issue #10, broker, orders, paper trading, production writes, production promotion, and DQN/RL remain locked.",
    }

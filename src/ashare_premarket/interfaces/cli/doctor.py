from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from ashare_premarket.interfaces.registry import load_interface_registry, repository_root


SNAPSHOT_POINTER = "outputs/research/premarket_position_management/latest_manifest.json"
REFRESH_POINTER = "outputs/research/daily_incremental_evidence_refresh/latest_refresh.json"
WORKSPACE_MANIFEST = "outputs/audits/goal_premarket_research_position_workspace_dashboard01_manifest.json"


def collect_doctor_report(root: Path | None = None) -> dict[str, Any]:
    base = (root or repository_root()).resolve()
    registry = load_interface_registry(base)
    capabilities = _read_json(base / registry["capability_state_source"])
    snapshot = _read_json(base / SNAPSHOT_POINTER)
    refresh = _read_json(base / REFRESH_POINTER)
    workspace = _read_json(base / WORKSPACE_MANIFEST)
    keys = [str(key) for key in registry["doctor_capabilities"]]
    canonical_commands: list[dict[str, Any]] = []
    for row in registry["interfaces"]:
        if row["visibility"] != "public":
            continue
        command = {"name": row["name"], "command": row["command"], "purpose": row["purpose"]}
        if "platform_commands" in row:
            command["platform_commands"] = dict(row["platform_commands"])
        canonical_commands.append(command)
    return {
        "authoritative_branch": registry["authoritative_branch"],
        "current_branch": _git(base, "branch", "--show-current"),
        "current_commit": _git(base, "rev-parse", "HEAD"),
        "canonical_commands": canonical_commands,
        "api_routes": registry["api_routes"],
        "frontend_url": registry["frontend_url"],
        "latest_snapshot": snapshot.get("snapshot_date", "UNAVAILABLE"),
        "latest_refresh_status": refresh.get("refresh_status", "UNAVAILABLE"),
        "ready_factor_count": workspace.get("ready_factor_count", 0),
        "locked_capabilities": {key: capabilities.get(key) for key in keys},
    }


def print_doctor_report(root: Path | None = None, *, as_json: bool = False) -> None:
    report = collect_doctor_report(root)
    if as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return
    print(f"Authoritative branch: {report['authoritative_branch']}")
    print(f"Current git state: {report['current_branch']} @ {report['current_commit']}")
    print(f"Frontend: {report['frontend_url']}")
    print(f"Latest snapshot: {report['latest_snapshot']}")
    print(f"Latest refresh: {report['latest_refresh_status']}")
    print(f"Ready factors: {report['ready_factor_count']}")
    print("Canonical commands:")
    for row in report["canonical_commands"]:
        print(f"  {row['name']}: {row['command']}")
        for platform, command in row.get("platform_commands", {}).items():
            print(f"    {platform}: {command}")
    print("API routes:")
    for row in report["api_routes"]:
        print(f"  {','.join(row['methods'])} {row['path']}")
    print("Locked capabilities:")
    for name, state in report["locked_capabilities"].items():
        print(f"  {name}: {state}")


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "UNAVAILABLE"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}

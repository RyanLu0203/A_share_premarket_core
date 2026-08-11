from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import plistlib
import subprocess
from typing import Any

from ashare_premarket.data.runtime_calendar import runtime_calendar_environment


WORKSPACE_LABEL = "com.ashare.premarket.workspace"
REFRESH_LABEL = "com.ashare.premarket.daily-refresh"
LATEST_REFRESH = "outputs/research/daily_incremental_evidence_refresh/latest_refresh.json"


def already_refreshed(root: Path, context: dict[str, str]) -> bool:
    target = context["target_trading_date"]
    candidates = [
        root / LATEST_REFRESH,
        root / f"outputs/research/daily_incremental_evidence_refresh/{target}/refresh_manifest.json",
    ]
    for path in candidates:
        payload = _read_json(path)
        if (
            payload.get("refresh_status") != "SUCCEEDED"
            or payload.get("target_trading_date") != target
            or payload.get("expected_previous_trading_date") != context["expected_previous_trading_date"]
        ):
            continue
        snapshot_path = _confined(root, str(payload.get("snapshot_manifest_path", "")))
        expected_version = str(payload.get("snapshot_version", "")).removeprefix("sha256:")
        if snapshot_path is None or not snapshot_path.is_file() or len(expected_version) != 16:
            continue
        if hashlib.sha256(snapshot_path.read_bytes()).hexdigest()[:16] != expected_version:
            continue
        manifest = _read_json(snapshot_path)
        if _snapshot_files_verified(snapshot_path.parent, manifest):
            return True
    return False


def workspace_plist(root: Path) -> dict[str, object]:
    root = root.resolve()
    log_root = root / "outputs/local/runtime/launchd"
    return {
        "Label": WORKSPACE_LABEL,
        "ProgramArguments": [str(root / ".venv/bin/python"), str(root / "scripts/run_premarket_workspace.py")],
        "WorkingDirectory": str(root),
        "RunAtLoad": True,
        "KeepAlive": True,
        "ThrottleInterval": 10,
        "EnvironmentVariables": _environment(root, allow_network=False),
        "StandardOutPath": str(log_root / "workspace.stdout.log"),
        "StandardErrorPath": str(log_root / "workspace.stderr.log"),
    }


def refresh_plist(root: Path, hour: int = 8, minute: int = 0) -> dict[str, object]:
    root = root.resolve()
    log_root = root / "outputs/local/runtime/launchd"
    return {
        "Label": REFRESH_LABEL,
        "ProgramArguments": [
            str(root / ".venv/bin/python"),
            str(root / "scripts/run_macos_daily_refresh.py"),
            "--allow-network",
        ],
        "WorkingDirectory": str(root),
        "StartCalendarInterval": {"Hour": hour, "Minute": minute},
        "ProcessType": "Background",
        "EnvironmentVariables": _environment(root, allow_network=True),
        "StandardOutPath": str(log_root / "daily-refresh.stdout.log"),
        "StandardErrorPath": str(log_root / "daily-refresh.stderr.log"),
    }


def check_installation(root: Path, launch_agents: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    target = (launch_agents or Path.home() / "Library/LaunchAgents").expanduser()
    checks = {
        "platform_is_macos": platform.system() == "Darwin",
        "launchd_root_outside_tcc_protected_folders": launchd_root_is_tcc_safe(root),
        "project_venv_python": (root / ".venv/bin/python").is_file(),
        "launchd_python_runtime_is_stable": launchd_python_runtime_is_stable(root),
        "frontend_dependencies": (root / "apps/premarket-workspace/node_modules").is_dir(),
        "workspace_runner": (root / "scripts/run_premarket_workspace.py").is_file(),
        "daily_refresh_runner": (root / "scripts/run_macos_daily_refresh.py").is_file(),
        "akshare_dependency": importlib.util.find_spec("akshare") is not None,
        "workspace_plist_installed": (target / f"{WORKSPACE_LABEL}.plist").is_file(),
        "daily_refresh_plist_installed": (target / f"{REFRESH_LABEL}.plist").is_file(),
    }
    required = [
        "platform_is_macos",
        "launchd_root_outside_tcc_protected_folders",
        "project_venv_python",
        "launchd_python_runtime_is_stable",
        "frontend_dependencies",
        "workspace_runner",
        "daily_refresh_runner",
        "akshare_dependency",
    ]
    return {"status": "PASS" if all(checks[key] for key in required) else "BLOCKED", "checks": checks}


def launchd_root_is_tcc_safe(root: Path, home: Path | None = None) -> bool:
    """Reject launchd roots protected through per-application macOS TCC grants."""

    resolved = root.expanduser().resolve()
    resolved_home = (home or Path.home()).expanduser().resolve()
    protected = tuple(resolved_home / name for name in ("Desktop", "Documents", "Downloads"))
    return not any(resolved == directory or directory in resolved.parents for directory in protected)


def launchd_python_runtime_is_stable(root: Path) -> bool:
    """Reject virtual environments backed by an ephemeral Codex runtime cache."""

    python = root.expanduser().resolve() / ".venv/bin/python"
    if not python.is_file():
        return False
    resolved = python.resolve()
    return not (".cache" in resolved.parts and "codex-runtimes" in resolved.parts)


def install(root: Path, launch_agents: Path | None = None, kickstart_refresh: bool = False) -> list[Path]:
    check = check_installation(root, launch_agents)
    if check["status"] != "PASS":
        failed = [key for key, passed in check["checks"].items() if not passed and not key.endswith("_installed")]
        raise RuntimeError(f"macOS launchd prerequisites failed: {','.join(failed)}")
    root = root.resolve()
    (root / "outputs/local/runtime/launchd").mkdir(parents=True, exist_ok=True)
    target = (launch_agents or Path.home() / "Library/LaunchAgents").expanduser()
    target.mkdir(parents=True, exist_ok=True)
    domain = f"gui/{os.getuid()}"
    paths = []
    for label, payload in {
        WORKSPACE_LABEL: workspace_plist(root),
        REFRESH_LABEL: refresh_plist(root),
    }.items():
        path = target / f"{label}.plist"
        path.write_bytes(plistlib.dumps(payload, fmt=plistlib.FMT_XML, sort_keys=True))
        subprocess.run(["launchctl", "bootout", domain, str(path)], check=False, capture_output=True)
        subprocess.run(["launchctl", "bootstrap", domain, str(path)], check=True)
        subprocess.run(["launchctl", "enable", f"{domain}/{label}"], check=True)
        paths.append(path)
    subprocess.run(["launchctl", "kickstart", "-k", f"{domain}/{WORKSPACE_LABEL}"], check=True)
    if kickstart_refresh:
        subprocess.run(["launchctl", "kickstart", "-k", f"{domain}/{REFRESH_LABEL}"], check=True)
    return paths


def uninstall(launch_agents: Path | None = None) -> None:
    target = (launch_agents or Path.home() / "Library/LaunchAgents").expanduser()
    domain = f"gui/{os.getuid()}"
    for label in (WORKSPACE_LABEL, REFRESH_LABEL):
        path = target / f"{label}.plist"
        subprocess.run(["launchctl", "bootout", domain, str(path)], check=False, capture_output=True)
        path.unlink(missing_ok=True)


def status() -> dict[str, bool]:
    domain = f"gui/{os.getuid()}"
    return {
        label: subprocess.run(
            ["launchctl", "print", f"{domain}/{label}"], check=False, capture_output=True
        ).returncode
        == 0
        for label in (WORKSPACE_LABEL, REFRESH_LABEL)
    }


def _environment(root: Path, allow_network: bool) -> dict[str, str]:
    values = {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
        "PYTHONUNBUFFERED": "1",
        **runtime_calendar_environment(root),
    }
    if allow_network:
        values["ASHARE_ALLOW_NETWORK_INGESTION"] = "1"
    return values


def _confined(root: Path, relative: str) -> Path | None:
    if not relative:
        return None
    resolved_root = root.resolve()
    candidate = (resolved_root / relative).resolve()
    return candidate if candidate != resolved_root and resolved_root in candidate.parents else None


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _snapshot_files_verified(directory: Path, manifest: dict[str, Any]) -> bool:
    checksums = dict(manifest.get("checksums", {}))
    if not checksums:
        return False
    return all(
        Path(name).name == name
        and isinstance(expected, str)
        and (directory / name).is_file()
        and hashlib.sha256((directory / name).read_bytes()).hexdigest() == expected
        for name, expected in checksums.items()
    )

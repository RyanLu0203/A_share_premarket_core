from __future__ import annotations

import json
import os
from pathlib import Path
import plistlib
import subprocess

from ashare_premarket.data.runtime_calendar import RUNTIME_CALENDAR


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
        if not path.exists():
            continue
        latest = json.loads(path.read_text(encoding="utf-8"))
        snapshot = root / str(latest.get("snapshot_manifest_path", ""))
        if (
            latest.get("refresh_status") == "SUCCEEDED"
            and latest.get("target_trading_date") == target
            and latest.get("expected_previous_trading_date") == context["expected_previous_trading_date"]
            and bool(latest.get("snapshot_version"))
            and snapshot.is_file()
        ):
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


def refresh_plist(root: Path, hour: int = 7, minute: int = 45) -> dict[str, object]:
    root = root.resolve()
    log_root = root / "outputs/local/runtime/launchd"
    intervals = [{"Weekday": weekday, "Hour": hour, "Minute": minute} for weekday in range(2, 7)]
    return {
        "Label": REFRESH_LABEL,
        "ProgramArguments": [
            str(root / ".venv/bin/python"),
            str(root / "scripts/run_macos_daily_refresh.py"),
            "--allow-network",
        ],
        "WorkingDirectory": str(root),
        "StartCalendarInterval": intervals,
        "ProcessType": "Background",
        "EnvironmentVariables": _environment(root, allow_network=True),
        "StandardOutPath": str(log_root / "daily-refresh.stdout.log"),
        "StandardErrorPath": str(log_root / "daily-refresh.stderr.log"),
    }


def install(root: Path, launch_agents: Path | None = None, kickstart_refresh: bool = False) -> list[Path]:
    root = root.resolve()
    if not (root / ".venv/bin/python").exists():
        raise RuntimeError("project .venv is missing")
    if not (root / "apps/premarket-workspace/node_modules").exists():
        raise RuntimeError("frontend node_modules is missing")
    (root / "outputs/local/runtime/launchd").mkdir(parents=True, exist_ok=True)
    target = (launch_agents or Path.home() / "Library/LaunchAgents").expanduser()
    target.mkdir(parents=True, exist_ok=True)
    payloads = {
        WORKSPACE_LABEL: workspace_plist(root),
        REFRESH_LABEL: refresh_plist(root),
    }
    domain = f"gui/{os.getuid()}"
    paths: list[Path] = []
    for label, payload in payloads.items():
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
        if path.exists():
            path.unlink()


def status() -> dict[str, bool]:
    domain = f"gui/{os.getuid()}"
    return {
        label: subprocess.run(["launchctl", "print", f"{domain}/{label}"], check=False, capture_output=True).returncode == 0
        for label in (WORKSPACE_LABEL, REFRESH_LABEL)
    }


def _environment(root: Path, allow_network: bool) -> dict[str, str]:
    values = {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
        "PYTHONUNBUFFERED": "1",
        "ASHARE_TRADING_CALENDAR_PATH": str(root / RUNTIME_CALENDAR),
    }
    if allow_network:
        values["ASHARE_ALLOW_NETWORK_INGESTION"] = "1"
    return values

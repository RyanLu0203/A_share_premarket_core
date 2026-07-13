from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from ashare_premarket.core.constants import PUBLIC_COMMANDS
from ashare_premarket.interfaces.cli.doctor import collect_doctor_report
from ashare_premarket.interfaces.registry import load_interface_registry


ROOT = Path(__file__).resolve().parents[1]
BASELINE_API_PATHS = {
    "/api/command-center",
    "/api/data-quality",
    "/api/experiment",
    "/api/health",
    "/api/market/context",
    "/api/portfolio/abstentions",
    "/api/portfolio/bands",
    "/api/portfolio/constraints",
    "/api/portfolio/overview",
    "/api/portfolio/risk",
    "/api/provenance",
    "/api/provider-health",
    "/api/quant/capabilities",
    "/api/snapshots",
    "/api/status",
    "/api/stocks",
    "/api/stocks/{symbol}",
    "/api/stocks/{symbol}/fundamentals",
    "/api/stocks/{symbol}/market",
    "/api/stocks/{symbol}/position",
    "/api/stocks/{symbol}/risk",
    "/api/watchlists",
}


def test_canonical_interface_registry_is_unique_and_complete() -> None:
    registry = load_interface_registry(ROOT)
    interfaces = registry["interfaces"]
    routes = registry["api_routes"]

    assert registry["authoritative_branch"] == "project-current"
    assert len({row["name"] for row in interfaces}) == len(interfaces)
    assert len({row["command"] for row in interfaces}) == len(interfaces)
    assert {row["path"] for row in routes} == BASELINE_API_PATHS
    assert all(row["methods"] == ["GET"] for row in routes)
    assert len({row["name"] for row in routes}) == 22
    assert len({row["path"] for row in routes}) == 22

    for row in interfaces:
        assert row["purpose"]
        assert row["module"]
        assert row["input_contract"]
        assert row["output_contract"]
        assert row["network_behavior"]
        assert row["mode_behavior"]
        assert row["expected_failure"]
        assert row["visibility"] in {"public", "internal", "compatibility_only"}


def test_registry_resolves_real_locked_capability_source() -> None:
    registry = load_interface_registry(ROOT)
    source = ROOT / registry["capability_state_source"]
    capabilities = json.loads(source.read_text(encoding="utf-8"))

    assert capabilities["dashboard"] is False
    assert capabilities["goal_rec_tiering01_recommendation_score_tiering_gate"] is False
    assert capabilities["broker_live_trading"] is False
    assert capabilities["paper_trading"] is False
    assert capabilities["production_db_writes"] is False
    assert capabilities["production_model_promotion"] is False
    assert capabilities["dqn_rl"] is False


def test_program_doctor_reports_repository_interfaces_and_locks() -> None:
    report = collect_doctor_report(ROOT)

    assert report["authoritative_branch"] == "project-current"
    assert report["current_branch"] == "codex-max/global-codebase-consolidation-stock-chart01"
    assert len(report["api_routes"]) == 22
    assert report["frontend_url"] == "http://127.0.0.1:3000"
    assert report["latest_snapshot"] == "2026-07-01"
    assert report["latest_refresh_status"] == "SUCCEEDED"
    assert report["ready_factor_count"] == 0
    assert report["locked_capabilities"]["dashboard"] is False
    assert report["locked_capabilities"]["broker_live_trading"] is False
    assert report["canonical_commands"]


def test_module_doctor_json_command_is_machine_readable() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ashare_premarket", "doctor", "--json", "--root", str(ROOT)],
        cwd=ROOT,
        env={**__import__("os").environ, "PYTHONPATH": str(ROOT / "src")},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["current_commit"]
    assert len(payload["api_routes"]) == 22
    assert payload["ready_factor_count"] == 0


def test_public_command_inventory_covers_every_python_script() -> None:
    scripts = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "scripts").glob("*.py")
        if path.name != "_bootstrap.py"
    }

    assert set(PUBLIC_COMMANDS) == scripts
    assert len(PUBLIC_COMMANDS) == len(set(PUBLIC_COMMANDS))


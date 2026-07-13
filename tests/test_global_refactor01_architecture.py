from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import re

from fastapi.testclient import TestClient

from ashare_premarket.application.workspace.repository import (
    PremarketWorkspaceRepository as CanonicalWorkspaceRepository,
)
from ashare_premarket.core.constants import PUBLIC_COMMANDS
from ashare_premarket.dashboard.repository import PremarketWorkspaceRepository
from ashare_premarket.dashboard.store import CommittedEvidenceStore
from ashare_premarket.domain.quant_contracts.factor_evidence import LockedFactorEvidenceProvider
from ashare_premarket.interfaces.api.app import create_app as canonical_create_app
from ashare_premarket.interfaces.cli.doctor import collect_doctor_report
from ashare_premarket.interfaces.registry import api_paths, load_interface_registry


ROOT = Path(__file__).resolve().parents[1]
POSIX_FRONTEND_COMMAND = "npm run dev --prefix apps/premarket-workspace"
WINDOWS_FRONTEND_COMMAND = "npm.cmd run dev --prefix apps/premarket-workspace"
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
API_CASES = [
    ("/api/health", {}),
    ("/api/status", {"mode": "replay", "snapshot_date": "2026-07-01"}),
    ("/api/command-center", {"mode": "replay", "snapshot_date": "2026-07-01"}),
    ("/api/watchlists", {}),
    ("/api/stocks", {"snapshot_date": "2026-07-01"}),
    ("/api/stocks/000333.SZ", {"snapshot_date": "2026-07-01"}),
    ("/api/stocks/000333.SZ/market", {"snapshot_date": "2026-07-01"}),
    ("/api/stocks/000333.SZ/fundamentals", {}),
    ("/api/stocks/000333.SZ/risk", {"snapshot_date": "2026-07-01"}),
    ("/api/stocks/000333.SZ/position", {"snapshot_date": "2026-07-01"}),
    ("/api/portfolio/overview", {"snapshot_date": "2026-07-01"}),
    ("/api/portfolio/bands", {"snapshot_date": "2026-07-01"}),
    ("/api/portfolio/risk", {"snapshot_date": "2026-07-01"}),
    ("/api/portfolio/constraints", {"snapshot_date": "2026-07-01"}),
    ("/api/portfolio/abstentions", {"snapshot_date": "2026-07-01"}),
    ("/api/market/context", {"snapshot_date": "2026-07-01"}),
    ("/api/quant/capabilities", {}),
    ("/api/experiment", {}),
    ("/api/data-quality", {"snapshot_date": "2026-07-01"}),
    ("/api/provider-health", {"snapshot_date": "2026-07-01"}),
    ("/api/snapshots", {}),
    ("/api/provenance", {"snapshot_date": "2026-07-01"}),
]


def test_canonical_interface_registry_is_unique_and_complete() -> None:
    registry = load_interface_registry(ROOT)
    interfaces = registry["interfaces"]
    routes = registry["api_routes"]
    frontend = next(row for row in interfaces if row["name"] == "workspace_frontend")

    assert registry["schema_version"] == "1.1"
    assert registry["authoritative_branch"] == "project-current"
    assert len(interfaces) == 14
    assert len({row["name"] for row in interfaces}) == len(interfaces)
    assert len({row["command"] for row in interfaces}) == len(interfaces)
    assert frontend["command"] == POSIX_FRONTEND_COMMAND
    assert frontend["platform_commands"] == {
        "posix": POSIX_FRONTEND_COMMAND,
        "windows": WINDOWS_FRONTEND_COMMAND,
    }
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
    frontend = next(
        row for row in report["canonical_commands"] if row["name"] == "workspace_frontend"
    )

    assert report["authoritative_branch"] == "project-current"
    assert report["current_branch"] == "codex-max/global-codebase-consolidation-stock-chart01"
    assert len(report["api_routes"]) == 22
    assert report["frontend_url"] == "http://127.0.0.1:3000"
    assert report["latest_snapshot"] == "2026-07-01"
    assert report["latest_refresh_status"] == "SUCCEEDED"
    assert report["ready_factor_count"] == 0
    assert report["locked_capabilities"]["dashboard"] is False
    assert report["locked_capabilities"]["broker_live_trading"] is False
    assert len(report["canonical_commands"]) == 14
    assert frontend["command"] == POSIX_FRONTEND_COMMAND
    assert frontend["platform_commands"] == {
        "posix": POSIX_FRONTEND_COMMAND,
        "windows": WINDOWS_FRONTEND_COMMAND,
    }


def test_module_doctor_text_uses_posix_canonical_command_and_labels_windows_alternative() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ashare_premarket", "doctor", "--root", str(ROOT)],
        cwd=ROOT,
        env={**__import__("os").environ, "PYTHONPATH": str(ROOT / "src")},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert f"workspace_frontend: {POSIX_FRONTEND_COMMAND}" in result.stdout
    assert f"workspace_frontend: {WINDOWS_FRONTEND_COMMAND}" not in result.stdout
    assert f"posix: {POSIX_FRONTEND_COMMAND}" in result.stdout
    assert f"windows: {WINDOWS_FRONTEND_COMMAND}" in result.stdout


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
    frontend = next(
        row for row in payload["canonical_commands"] if row["name"] == "workspace_frontend"
    )
    assert payload["current_commit"]
    assert len(payload["api_routes"]) == 22
    assert payload["ready_factor_count"] == 0
    assert frontend["command"] == POSIX_FRONTEND_COMMAND
    assert frontend["platform_commands"] == {
        "posix": POSIX_FRONTEND_COMMAND,
        "windows": WINDOWS_FRONTEND_COMMAND,
    }


def test_public_command_inventory_covers_every_python_script() -> None:
    scripts = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "scripts").glob("*.py")
        if path.name != "_bootstrap.py"
    }

    assert set(PUBLIC_COMMANDS) == scripts
    assert len(PUBLIC_COMMANDS) == len(set(PUBLIC_COMMANDS))


def test_compatibility_imports_forward_to_canonical_implementations() -> None:
    from ashare_premarket.dashboard.api import create_app
    from ashare_premarket.dashboard.repositories.snapshot_repository import (
        CommittedEvidenceStore as CanonicalEvidenceStore,
    )

    assert PremarketWorkspaceRepository is CanonicalWorkspaceRepository
    assert CommittedEvidenceStore is CanonicalEvidenceStore
    assert create_app is canonical_create_app
    assert len((ROOT / "src/ashare_premarket/dashboard/api.py").read_text(encoding="utf-8").splitlines()) <= 8
    assert len((ROOT / "src/ashare_premarket/dashboard/repository.py").read_text(encoding="utf-8").splitlines()) <= 8
    assert len((ROOT / "src/ashare_premarket/dashboard/store.py").read_text(encoding="utf-8").splitlines()) <= 8


def test_backend_refactor_preserves_openapi_and_all_public_responses() -> None:
    baseline = json.loads(
        (ROOT / "docs/architecture/refactor01/baseline_metrics.json").read_text(encoding="utf-8")
    )
    app = canonical_create_app(ROOT)
    client = TestClient(app)
    schema = app.openapi()
    canonical_openapi = json.dumps(schema, sort_keys=True, separators=(",", ":")).encode()

    assert set(schema["paths"]) >= BASELINE_API_PATHS
    assert {path for path in schema["paths"] if path.startswith("/api/")} == BASELINE_API_PATHS
    assert hashlib.sha256(canonical_openapi).hexdigest() == baseline["openapi_canonical_sha256"]
    assert set(api_paths(ROOT).values()) == BASELINE_API_PATHS

    for path, params in API_CASES:
        response = client.get(path, params=params)
        canonical = json.dumps(
            response.json(), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
        assert response.status_code == 200, path
        assert hashlib.sha256(canonical).hexdigest() == baseline["api_response_sha256"][path], path


def test_frontend_route_templates_match_registry_without_duplicate_literals() -> None:
    routes_path = ROOT / "apps/premarket-workspace/src/lib/api/routes.ts"
    source = routes_path.read_text(encoding="utf-8")
    block = source.split("export const API_ROUTE_TEMPLATES = {", 1)[1].split("} as const;", 1)[0]
    frontend_routes = set(re.findall(r'^\s+\w+: "(/api/[^"]+)",$', block, re.MULTILINE))

    assert frontend_routes == BASELINE_API_PATHS
    for path in (ROOT / "apps/premarket-workspace/src").rglob("*"):
        if path == routes_path or path.suffix not in {".ts", ".tsx"} or ".test." in path.name:
            continue
        assert not re.findall(r'["\'](/api/[^"\']+)["\']', path.read_text(encoding="utf-8")), path


def test_new_architecture_has_explicit_acyclic_dependency_directions() -> None:
    expected = [
        ROOT / "src/ashare_premarket/domain/quant_contracts/factor_evidence.py",
        ROOT / "src/ashare_premarket/application/workspace/repository.py",
        ROOT / "src/ashare_premarket/interfaces/api/app.py",
        ROOT / "src/ashare_premarket/dashboard/repositories/stock_repository.py",
        ROOT / "src/ashare_premarket/dashboard/repositories/portfolio_repository.py",
        ROOT / "src/ashare_premarket/dashboard/repositories/system_evidence_repository.py",
        ROOT / "src/ashare_premarket/dashboard/services/status_service.py",
        ROOT / "src/ashare_premarket/dashboard/services/capability_service.py",
    ]
    assert all(path.is_file() for path in expected)

    forbidden = {
        "domain": ("ashare_premarket.application", "ashare_premarket.dashboard", "ashare_premarket.interfaces"),
        "application": ("ashare_premarket.interfaces",),
        "dashboard": ("ashare_premarket.interfaces",),
    }
    for layer, terms in forbidden.items():
        base = ROOT / "src/ashare_premarket" / layer
        for path in base.rglob("*.py"):
            if path == ROOT / "src/ashare_premarket/dashboard/api.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module or "")
            assert not [name for name in imports if name.startswith(terms)], (path, imports)


def test_factor_evidence_extension_remains_locked_and_empty() -> None:
    snapshot = LockedFactorEvidenceProvider().snapshot()

    assert snapshot.ready_factor_count == 0
    assert snapshot.readiness_status == "LOCKED_NO_READY_FACTORS"
    assert snapshot.factor_rows == ()

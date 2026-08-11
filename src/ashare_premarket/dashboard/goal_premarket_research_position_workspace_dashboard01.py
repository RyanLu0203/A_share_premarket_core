from __future__ import annotations

import csv
import json
from pathlib import Path
import re
from typing import Any

from ashare_premarket.core.boundary import (
    ISSUE24_CAPABILITY_KEY,
    ISSUE24_WORKFLOW_ID,
    implementation_file_sha256,
    issue24_workspace_workflow_patch,
)
from ashare_premarket.dashboard.api import create_app
from ashare_premarket.dashboard.repository import PremarketWorkspaceRepository


GOAL_ID = "GOAL-PREMARKET-RESEARCH-AND-POSITION-WORKSPACE-DASHBOARD-01"
WORKFLOW_ID = "goal_premarket_research_position_workspace_dashboard01"
PREDECESSOR_GOAL_ID = "GOAL-PREMARKET-POSITION-MANAGEMENT-OPERATIONAL-01"
MANIFEST = "outputs/audits/goal_premarket_research_position_workspace_dashboard01_manifest.json"
REPORT = (
    "outputs/audits/goal_premarket_research_position_workspace_dashboard01_report.md"
)
AUDIT = "outputs/audits/goal_premarket_research_position_workspace_dashboard01_audit.md"
CAPABILITY_KEY = ISSUE24_CAPABILITY_KEY

REQUIRED_FILES = (
    "apps/premarket-workspace/package.json",
    "apps/premarket-workspace/package-lock.json",
    "apps/premarket-workspace/src/app/[[...segments]]/page.tsx",
    "apps/premarket-workspace/src/app/globals.css",
    "apps/premarket-workspace/src/components/DenseTable.tsx",
    "apps/premarket-workspace/src/components/BlockedCurrentStateNotice.tsx",
    "apps/premarket-workspace/src/components/WorkspaceApp.tsx",
    "apps/premarket-workspace/src/components/EvidenceCharts.tsx",
    "apps/premarket-workspace/src/components/FreshnessBanner.tsx",
    "apps/premarket-workspace/src/components/PriceVolumeChart.tsx",
    "apps/premarket-workspace/src/components/PriceVolumeChart.test.tsx",
    "apps/premarket-workspace/src/components/Sidebar.tsx",
    "apps/premarket-workspace/src/components/StockSymbolSearch.tsx",
    "apps/premarket-workspace/src/components/StockSymbolSearch.test.tsx",
    "apps/premarket-workspace/src/components/TopBar.tsx",
    "apps/premarket-workspace/src/components/workspace-shell.test.tsx",
    "apps/premarket-workspace/src/hooks/usePageEvidence.ts",
    "apps/premarket-workspace/src/hooks/useSelectedSymbol.ts",
    "apps/premarket-workspace/src/hooks/useSelectedSymbol.test.tsx",
    "apps/premarket-workspace/src/hooks/useWatchlist.ts",
    "apps/premarket-workspace/src/hooks/useWorkspaceRequest.ts",
    "apps/premarket-workspace/src/lib/api/client.ts",
    "apps/premarket-workspace/src/lib/api/contracts.ts",
    "apps/premarket-workspace/src/lib/api/page-plan.ts",
    "apps/premarket-workspace/src/lib/api/page-plan.test.ts",
    "apps/premarket-workspace/src/lib/api/routes.ts",
    "apps/premarket-workspace/src/lib/api/routes.test.ts",
    "apps/premarket-workspace/src/lib/navigation.ts",
    "apps/premarket-workspace/src/views/AbstentionCenterPage.tsx",
    "apps/premarket-workspace/src/views/CommandCenterPage.tsx",
    "apps/premarket-workspace/src/views/ConstraintMonitorPage.tsx",
    "apps/premarket-workspace/src/views/ExperimentPage.tsx",
    "apps/premarket-workspace/src/views/MarketContextPage.tsx",
    "apps/premarket-workspace/src/views/PortfolioOverviewPage.tsx",
    "apps/premarket-workspace/src/views/PositionBandsPage.tsx",
    "apps/premarket-workspace/src/views/QuantWorkspacePage.tsx",
    "apps/premarket-workspace/src/views/RiskMonitorPage.tsx",
    "apps/premarket-workspace/src/views/SnapshotHistoryPage.tsx",
    "apps/premarket-workspace/src/views/StockDetailPage.tsx",
    "apps/premarket-workspace/src/views/StockExplorerPage.tsx",
    "apps/premarket-workspace/src/views/SystemEvidencePage.tsx",
    "apps/premarket-workspace/src/views/WatchlistPage.tsx",
    "apps/premarket-workspace/src/views/resolveWorkspacePage.ts",
    "apps/premarket-workspace/src/views/pages.test.tsx",
    "apps/premarket-workspace/src/components/DenseTable.test.tsx",
    "apps/premarket-workspace/src/components/EvidenceCharts.test.tsx",
    "apps/premarket-workspace/scripts/visual-qa.mjs",
    "configs/dashboard/goal_premarket_research_position_workspace_dashboard01_contract.yaml",
    "docs/research/GOAL_PREMARKET_RESEARCH_POSITION_WORKSPACE_DASHBOARD01_LOCAL_WORKSPACE.md",
    "scripts/audit_goal_premarket_research_position_workspace_dashboard01.py",
    "scripts/run_goal_premarket_research_position_workspace_dashboard01.py",
    "scripts/run_premarket_workspace.py",
    "scripts/run_premarket_workspace_api.py",
    "src/ashare_premarket/core/boundary.py",
    "src/ashare_premarket/core/workflow_preservation.py",
    "src/ashare_premarket/application/workspace/repository.py",
    "src/ashare_premarket/domain/quant_contracts/factor_evidence.py",
    "src/ashare_premarket/dashboard/analytics.py",
    "src/ashare_premarket/dashboard/api.py",
    "src/ashare_premarket/dashboard/goal_premarket_research_position_workspace_dashboard01.py",
    "src/ashare_premarket/dashboard/repositories/base.py",
    "src/ashare_premarket/dashboard/repositories/portfolio_repository.py",
    "src/ashare_premarket/dashboard/repositories/snapshot_repository.py",
    "src/ashare_premarket/dashboard/repositories/stock_repository.py",
    "src/ashare_premarket/dashboard/repositories/system_evidence_repository.py",
    "src/ashare_premarket/dashboard/repository.py",
    "src/ashare_premarket/dashboard/services/capability_service.py",
    "src/ashare_premarket/dashboard/services/status_service.py",
    "src/ashare_premarket/dashboard/store.py",
    "src/ashare_premarket/interfaces/api/app.py",
    "src/ashare_premarket/interfaces/api/errors.py",
    "src/ashare_premarket/interfaces/api/routers/portfolio.py",
    "src/ashare_premarket/interfaces/api/routers/quant.py",
    "src/ashare_premarket/interfaces/api/routers/status.py",
    "src/ashare_premarket/interfaces/api/routers/stocks.py",
    "src/ashare_premarket/interfaces/api/routers/system.py",
    "src/ashare_premarket/ops/safety.py",
)


def run_goal_premarket_research_position_workspace_dashboard01(root: Path) -> bool:
    _write_goal_governance(root)
    facts, failures = _collect_facts(root)
    status = "PASS" if not failures else "BLOCKED"
    manifest = {
        "goal": GOAL_ID,
        "workflow_id": WORKFLOW_ID,
        "depends_on_goal": PREDECESSOR_GOAL_ID,
        "status": status,
        "mode": "local_research_only_read_only_workspace",
        "generated_at": facts.get("source_snapshot_execution_time"),
        **facts,
        "failures": failures,
        "research_only": True,
        "not_trading_advice": True,
        "not_for_execution": True,
        "broker_connection": False,
        "orders_created": False,
        "paper_trading": False,
        "production_db_writes": False,
        "production_model_promotion": False,
        "recommendation_outputs_created": False,
        "alpha_outputs_created": False,
        "factor_outputs_created": False,
        "ic_rankic_outputs_created": False,
    }
    _write_json(root / MANIFEST, manifest)
    _write_text(root / REPORT, _report(manifest))
    return status == "PASS"


def audit_goal_premarket_research_position_workspace_dashboard01(root: Path) -> bool:
    manifest = _read_json(root / MANIFEST)
    facts, current_failures = _collect_facts(root)
    failures = list(current_failures)
    for key in (
        "page_count",
        "read_only_api_route_count",
        "write_api_route_count",
        "source_snapshot_integrity",
        "ready_factor_count",
        "generic_dashboard_capability",
        "recommendation_tiering_state",
        "workspace_goal_capability",
    ):
        if manifest.get(key) != facts.get(key):
            failures.append(f"manifest_fact_mismatch:{key}")
    if manifest.get("goal") != GOAL_ID:
        failures.append("manifest_goal_mismatch")
    if manifest.get("status") != "PASS":
        failures.append("manifest_status_not_pass")
    for relative, expected in dict(
        manifest.get("implementation_checksums", {})
    ).items():
        path = root / relative
        actual = _sha256(path) if path.exists() else "missing"
        if actual != expected:
            failures.append(f"implementation_checksum_mismatch:{relative}")
    for key in (
        "broker_connection",
        "orders_created",
        "paper_trading",
        "production_db_writes",
        "production_model_promotion",
        "recommendation_outputs_created",
        "alpha_outputs_created",
        "factor_outputs_created",
        "ic_rankic_outputs_created",
    ):
        if manifest.get(key) is not False:
            failures.append(f"forbidden_capability_not_false:{key}")
    passed = not failures
    _write_text(root / AUDIT, _audit_report(passed, failures, facts))
    return passed


def _collect_facts(root: Path) -> tuple[dict[str, Any], list[str]]:
    root = root.resolve()
    failures: list[str] = []
    missing = [
        relative for relative in REQUIRED_FILES if not (root / relative).exists()
    ]
    failures.extend(f"missing_required_file:{relative}" for relative in missing)

    app = create_app(root)
    schema = app.openapi()
    api_paths = {
        path: methods
        for path, methods in schema["paths"].items()
        if path.startswith("/api/")
    }
    write_methods = sorted(
        f"{method.upper()} {path}"
        for path, methods in api_paths.items()
        for method in methods
        if method.lower() != "get"
    )
    if write_methods:
        failures.extend(f"write_api_route:{item}" for item in write_methods)

    repo = PremarketWorkspaceRepository(root)
    snapshot_date = repo.store.latest_snapshot_date()
    snapshot = repo.store.snapshot_manifest(snapshot_date)
    snapshot_verified, snapshot_failures = repo.store.verify_snapshot(snapshot_date)
    failures.extend(
        f"source_snapshot_checksum_failure:{name}" for name in snapshot_failures
    )
    quant = repo.quant_capabilities()
    provider = repo.provider_health(snapshot_date)
    constraints = repo.portfolio_constraints(snapshot_date)
    bands = repo.portfolio_bands(snapshot_date)
    abstentions = repo.portfolio_abstentions(snapshot_date)
    portfolio = repo.portfolio_overview(snapshot_date)

    navigation = (
        (root / "apps/premarket-workspace/src/lib/navigation.ts").read_text(
            encoding="utf-8"
        )
        if not missing
        else ""
    )
    page_ids = sorted(
        {int(value) for value in re.findall(r"\{id:\s*(\d+)", navigation)}
    )
    if page_ids != list(range(1, 24)):
        failures.append("page_registry_not_exactly_1_through_23")

    capabilities = _read_json(root / "configs/project/locked_capabilities.json")
    workflow = {
        row.get("workflow_id", ""): row
        for row in _read_csv(root / "configs/project/workflow_status.csv")
    }
    workspace_row = workflow.get(WORKFLOW_ID, {})
    if capabilities.get("dashboard") is not False:
        failures.append("generic_dashboard_capability_unlocked")
    if capabilities.get(CAPABILITY_KEY) != "implemented_research_only":
        failures.append("workspace_goal_capability_not_implemented_research_only")
    if (
        workspace_row.get("status") != "implemented_research_only"
        or workspace_row.get("implemented_in_repo") != "true"
    ):
        failures.append("workspace_workflow_row_invalid")
    if workflow.get("dashboard_daily_report", {}).get("status") != "locked_future":
        failures.append("generic_dashboard_workflow_not_locked")
    if quant.get("ready_factor_count") != 0:
        failures.append("ready_factor_count_not_zero")
    if quant.get("recommendation_tiering_state") != "locked_future":
        failures.append("recommendation_tiering_not_locked")
    if provider.get("adjustment_convention_status") != "UNRESOLVED":
        failures.append("provider_adjustment_status_not_unresolved")
    if provider.get("no_silent_averaging") is not True:
        failures.append("provider_silent_averaging_not_disabled")
    if portfolio.get("correlation_matrix", {}).get("decision_input") is not False:
        failures.append("display_correlation_marked_as_decision_input")

    checksum_files = [
        relative for relative in REQUIRED_FILES if (root / relative).exists()
    ]
    facts = {
        "page_count": len(page_ids),
        "page_ids": page_ids,
        "page_state_counts": {"AVAILABLE": 16, "HYBRID": 1, "LOCKED": 6},
        "read_only_api_route_count": len(api_paths)
        - len({item.split(" ", 1)[1] for item in write_methods}),
        "write_api_route_count": len(write_methods),
        "write_api_routes": write_methods,
        "source_snapshot_date": snapshot_date,
        "source_snapshot_execution_time": snapshot.get("execution_time"),
        "source_snapshot_integrity": "VERIFIED" if snapshot_verified else "FAILED",
        "source_snapshot_readiness": snapshot.get("readiness_state"),
        "source_snapshot_freshness": snapshot.get("freshness_code"),
        "stock_count": len(repo.stocks(snapshot_date)),
        "position_band_count": len(bands.get("rows", [])),
        "position_abstention_count": len(abstentions.get("rows", [])),
        "constraint_count": constraints.get("constraint_count"),
        "substantive_constraint_count": constraints.get("substantive_constraint_count"),
        "ready_factor_count": quant.get("ready_factor_count"),
        "recommendation_tiering_state": quant.get("recommendation_tiering_state"),
        "issue_10_state": quant.get("issue_10_state"),
        "provider_adjustment_convention_status": provider.get(
            "adjustment_convention_status"
        ),
        "provider_no_silent_averaging": provider.get("no_silent_averaging"),
        "correlation_matrix_derivation": portfolio.get("correlation_matrix", {}).get(
            "derivation"
        ),
        "correlation_matrix_decision_input": portfolio.get(
            "correlation_matrix", {}
        ).get("decision_input"),
        "generic_dashboard_capability": capabilities.get("dashboard"),
        "generic_dashboard_workflow_state": workflow.get(
            "dashboard_daily_report", {}
        ).get("status"),
        "workspace_goal_capability": capabilities.get(CAPABILITY_KEY),
        "workspace_workflow_state": workspace_row.get("status"),
        "implementation_checksums": {
            relative: _sha256(root / relative) for relative in sorted(checksum_files)
        },
    }
    return facts, sorted(set(failures))


def _report(manifest: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# {GOAL_ID}",
            "",
            f"Status: `{manifest['status']}`",
            "",
            "## Material implementation",
            "",
            f"- Pages registered: `{manifest['page_count']}`.",
            f"- Read-only API routes: `{manifest['read_only_api_route_count']}`.",
            f"- Source snapshot: `{manifest['source_snapshot_date']}` with `{manifest['source_snapshot_integrity']}` checksums.",
            f"- Browseable securities / reference-portfolio bands / abstentions: `{manifest['stock_count']}` / `{manifest['position_band_count']}` / `{manifest['position_abstention_count']}`.",
            f"- Constraints / substantive constraints: `{manifest['constraint_count']}` / `{manifest['substantive_constraint_count']}`.",
            "- Local watchlists persist only in browser local storage; the server exposes no write route.",
            "- ECharts and Lightweight Charts render evidence returned by the read-only API.",
            "",
            "## Governance",
            "",
            f"- Generic dashboard capability: `{str(manifest['generic_dashboard_capability']).lower()}`.",
            f"- Goal-specific workspace capability: `{manifest['workspace_goal_capability']}`.",
            f"- Recommendation Tiering / Issue #10: `{manifest['recommendation_tiering_state']}` / `{manifest['issue_10_state']}`.",
            "- Alpha, factor, IC/RankIC, recommendation, broker, order, paper-trading, and production outputs are not created.",
            "- The workspace is local, research-only, not trading advice, and not for execution.",
            "",
        ]
    )


def _audit_report(passed: bool, failures: list[str], facts: dict[str, Any]) -> str:
    lines = [
        f"# {GOAL_ID} Audit",
        "",
        f"Status: `{'PASS' if passed else 'FAIL'}`",
        "",
        "## Checks",
        "",
    ]
    lines.extend(
        [
            f"- Page registry: `{facts.get('page_count')}` pages.",
            f"- API surface: `{facts.get('read_only_api_route_count')}` GET-only routes and `{facts.get('write_api_route_count')}` write routes.",
            f"- Snapshot integrity: `{facts.get('source_snapshot_integrity')}`.",
            f"- Ready factors: `{facts.get('ready_factor_count')}`.",
            f"- Generic dashboard capability: `{str(facts.get('generic_dashboard_capability')).lower()}`.",
            f"- Goal-specific capability: `{facts.get('workspace_goal_capability')}`.",
        ]
    )
    if failures:
        lines.extend(
            ["", "## Failures", "", *[f"- `{failure}`" for failure in failures]]
        )
    return "\n".join(lines) + "\n"


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _write_goal_governance(root: Path) -> None:
    capabilities_path = root / "configs/project/locked_capabilities.json"
    capabilities = _read_json(capabilities_path)
    capabilities[CAPABILITY_KEY] = "implemented_research_only"
    capabilities["dashboard"] = False
    _write_json(capabilities_path, capabilities)

    workflow_path = root / "configs/project/workflow_status.csv"
    rows = _read_csv(workflow_path)
    if not rows:
        raise RuntimeError("workflow status table is unavailable")
    fieldnames = list(rows[0])
    patch = issue24_workspace_workflow_patch()
    by_id = {row["workflow_id"]: row for row in rows}
    if ISSUE24_WORKFLOW_ID in by_id:
        by_id[ISSUE24_WORKFLOW_ID].update(patch)
    else:
        rows.append(patch)
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    with workflow_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _sha256(path: Path) -> str:
    return implementation_file_sha256(path)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(payload)

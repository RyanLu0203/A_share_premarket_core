from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from ashare_premarket.core.boundary import forbidden_locked_import_terms, issue24_workspace_evidence_valid
from ashare_premarket.dashboard.api import create_app
from ashare_premarket.dashboard.goal_premarket_research_position_workspace_dashboard01 import (
    audit_goal_premarket_research_position_workspace_dashboard01,
    run_goal_premarket_research_position_workspace_dashboard01,
)
from ashare_premarket.dashboard.repository import PremarketWorkspaceRepository
from ashare_premarket.dashboard.store import CommittedEvidenceStore
from ashare_premarket.core.workflow_preservation import (
    preserve_later_review_only_capabilities,
    preserve_later_review_only_workflow_states,
)
from ashare_premarket.ops import safety as safety_module
from ashare_premarket.ops.safety import run_safety_gate


ROOT = Path(__file__).resolve().parents[1]


def _repo() -> PremarketWorkspaceRepository:
    return PremarketWorkspaceRepository(ROOT)


def test_replay_status_uses_immutable_snapshot_clock_and_checksums() -> None:
    status = _repo().status(mode="replay", snapshot_date="2026-07-01")

    assert status["execution_mode"] == "deterministic_replay"
    assert status["readiness_state"] == "READY_WITH_WARNINGS"
    assert status["freshness_code"] == "FRESH_T_MINUS_ONE_DATA"
    assert status["target_trading_date"] == "2026-07-01"
    assert status["expected_previous_trading_date"] == "2026-06-30"
    assert status["latest_available_data_date"] == "2026-06-30"
    assert status["holdings_mode"] == "RESEARCH REFERENCE PORTFOLIO"
    assert status["snapshot_integrity"] == "VERIFIED"
    assert status["research_only"] is True
    assert status["latest_refresh_status"] == "SUCCEEDED"
    assert status["last_successful_refresh_time"] == "2026-07-01T08:30:00+08:00"
    assert status["data_freshness_badge"] == "FRESH_T_MINUS_ONE_DATA"
    assert status["refresh_validation_status"] == "PASS"
    assert status["refresh_manifest_integrity"] == "VERIFIED"
    assert status["refresh_blocked_reasons"] == []
    assert status["snapshot_version"]


def test_dashboard_store_observes_refresh_and_snapshot_pointer_updates_without_restart(tmp_path: Path) -> None:
    store = CommittedEvidenceStore(tmp_path)
    refresh_root = tmp_path / "outputs/research/daily_incremental_evidence_refresh"
    refresh_root.mkdir(parents=True)

    def write_refresh(state: str) -> None:
        manifest = refresh_root / f"{state.lower()}.json"
        manifest.write_bytes((json.dumps({"refresh_status": state}, sort_keys=True) + "\n").encode("utf-8"))
        latest = {
            "refresh_status": state,
            "refresh_manifest_path": manifest.relative_to(tmp_path).as_posix(),
            "refresh_manifest_checksum": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        }
        (refresh_root / "latest_refresh.json").write_bytes((json.dumps(latest, sort_keys=True) + "\n").encode("utf-8"))

    write_refresh("BLOCKED")
    assert store.refresh_status()["refresh_status"] == "BLOCKED"
    write_refresh("SUCCEEDED")
    assert store.refresh_status()["refresh_status"] == "SUCCEEDED"

    snapshot_root = tmp_path / "outputs/research/premarket_position_management"
    for date in ("2026-07-01", "2026-07-02"):
        path = snapshot_root / date / "manifest.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"snapshot_date": date}), encoding="utf-8")
        (snapshot_root / "latest_manifest.json").write_text(json.dumps({"snapshot_date": date}), encoding="utf-8")
        assert store.latest_snapshot_date() == date


def test_live_status_blocks_stale_t_minus_one_without_self_reference() -> None:
    status = _repo().status(
        mode="live",
        execution_time=datetime(2026, 7, 9, 7, 45, tzinfo=ZoneInfo("Asia/Shanghai")),
    )

    assert status["execution_mode"] == "daily_operational"
    assert status["readiness_state"] == "BLOCKED"
    assert status["freshness_code"] == "STALE_SOURCE_DATA"
    assert status["target_trading_date"] == "2026-07-09"
    assert status["expected_previous_trading_date"] == "2026-07-08"
    assert status["latest_available_data_date"] == "2026-06-30"
    assert status["data_cutoff"] == "2026-07-08"
    assert status["current_panels_enabled"] is False


def test_live_status_fails_closed_when_calendar_coverage_is_exhausted() -> None:
    status = _repo().status(
        mode="live",
        execution_time=datetime(2026, 7, 11, 8, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
    )

    assert status["readiness_state"] == "BLOCKED"
    assert status["freshness_code"] == "TRADING_CALENDAR_COVERAGE_MISSING"
    assert status["target_trading_date"] == "UNRESOLVED"
    assert status["current_panels_enabled"] is False
    assert "TRADING_CALENDAR_COVERAGE_MISSING" in status["refresh_blocked_reasons"]


def test_stock_contract_uses_real_evidence_and_explicit_unavailable_values() -> None:
    repo = _repo()
    stocks = repo.stocks(snapshot_date="2026-07-01")

    assert len(stocks) == 41
    midea = next(row for row in stocks if row["symbol"] == "000333.SZ")
    assert midea["company_name"]["value"] == "Midea Group"
    assert midea["company_name"]["availability"] == "AVAILABLE"
    assert midea["company_name"]["asof_date"] is None
    assert midea["industry"]["value"] == "Home Appliances"
    assert midea["latest_price"]["asof_date"] == "2026-06-30"
    assert midea["latest_price"]["source"] == "akshare_sina"
    assert midea["market_cap"]["value"] is None
    assert midea["market_cap"]["availability"] == "UNAVAILABLE"
    assert "committed evidence" in midea["market_cap"]["reason"]


def test_stock_market_and_fundamentals_keep_different_evidence_dates_visible() -> None:
    repo = _repo()
    market = repo.stock_market("000333.SZ", snapshot_date="2026-07-01")
    fundamentals = repo.stock_fundamentals("000333.SZ")

    assert market["latest_close"]["asof_date"] == "2026-06-30"
    assert market["candles"]
    assert market["candles"][-1]["trade_date"] == "2026-05-21"
    assert market["candles"][-1]["source"] == "baostock"
    assert market["candlestick_latest_date"] == "2026-05-21"
    assert market["quality_markers"]
    assert market["regime_strip"]
    assert "provider_discrepancy_markers" in market
    assert fundamentals["pe_ttm"]["availability"] == "AVAILABLE"
    assert fundamentals["pe_ttm"]["asof_date"] == "2026-05-21"
    assert fundamentals["pb"]["availability"] == "AVAILABLE"
    assert fundamentals["revenue"]["availability"] == "UNAVAILABLE"
    assert fundamentals["roe"]["value"] is None


def test_portfolio_views_preserve_constraint_and_abstention_evidence() -> None:
    repo = _repo()
    overview = repo.portfolio_overview(snapshot_date="2026-07-01")
    constraints = repo.portfolio_constraints(snapshot_date="2026-07-01")
    abstentions = repo.portfolio_abstentions(snapshot_date="2026-07-01")
    bands = repo.portfolio_bands(snapshot_date="2026-07-01")

    assert overview["portfolio_mode"] == "RESEARCH REFERENCE PORTFOLIO"
    assert len(overview["positions"]) == 41
    assert overview["correlation_matrix"]["derivation"] == (
        "display_only_server_derived_from_validated_canonical_returns"
    )
    assert len(constraints["summary"]) == 13
    assert {row["constraint_id"] for row in constraints["summary"]} >= {
        "gross_exposure_max",
        "cash_buffer_band",
        "turnover_limit",
        "volatility_budget",
        "cluster_concentration_cap",
        "beta_budget",
        "liquidity_limit",
    }
    assert sum(1 for row in constraints["summary"] if row["state"] == "FAIL_CLOSED") == 3
    assert len(abstentions["rows"]) == 12
    assert all(row["abstain"] is True for row in abstentions["rows"])
    assert all(row["display_name"] for row in bands["rows"])
    assert all(row["risk_contribution"] is not None for row in bands["rows"])
    assert {
        "provider_discrepancy",
        "regime_instability",
        "covariance_sensitivity",
        "band_sensitivity",
        "history_sufficiency",
        "data_availability",
    } <= abstentions["rows"][0].keys()


def test_quant_capabilities_and_experiment_remain_locked_or_not_started() -> None:
    repo = _repo()
    quant = repo.quant_capabilities()
    experiment = repo.experiment()

    assert quant["ready_factor_count"] == 0
    assert quant["factor_monitor_state"] == "LOCKED_NO_READY_FACTORS"
    assert quant["ic_rankic_lab_state"] == "BLOCKED_PENDING_READY_FACTOR"
    assert quant["recommendation_tiering_state"] == "locked_future"
    assert quant["issue_10_state"] == "locked"
    assert quant["candidate_readiness"]["evaluated"] == 120
    assert quant["candidate_readiness"]["ready"] == 0
    assert quant["candidate_rows"][0]["decision_summary"].startswith("not_ready_failed:")
    assert experiment["status"] == "PREPARED_NOT_STARTED"
    assert experiment["observations"] == []


def test_system_views_expose_required_freshness_and_lineage_fields() -> None:
    repo = _repo()
    quality = repo.data_quality("2026-07-01")
    provider = repo.provider_health("2026-07-01")
    provenance = repo.provenance("2026-07-01")

    assert quality["status"]["target_trading_date"] == "2026-07-01"
    assert quality["status"]["expected_previous_trading_date"] == "2026-06-30"
    assert provider["provider_lineage"] == ["baostock", "akshare_sina"]
    assert provenance["source_lineage"]
    assert provenance["config_hash"]
    assert provenance["audit_status"] == "PASS"


def test_fastapi_surface_is_read_only_and_exposes_required_views() -> None:
    client = TestClient(create_app(ROOT))

    status = client.get("/api/status", params={"mode": "replay", "snapshot_date": "2026-07-01"})
    assert status.status_code == 200
    assert status.json()["execution_mode"] == "deterministic_replay"
    assert client.get("/api/command-center", params={"mode": "replay"}).status_code == 200
    assert client.get("/api/stocks").status_code == 200
    assert client.get("/api/stocks/000333.SZ").status_code == 200
    assert client.get("/api/stocks/000333.SZ/market").status_code == 200
    assert client.get("/api/stocks/000333.SZ/fundamentals").status_code == 200
    assert client.get("/api/stocks/000333.SZ/risk").status_code == 200
    assert client.get("/api/stocks/000333.SZ/position").status_code == 200
    assert client.get("/api/portfolio/overview").status_code == 200
    assert client.get("/api/portfolio/bands").status_code == 200
    assert client.get("/api/portfolio/risk").status_code == 200
    assert client.get("/api/portfolio/constraints").status_code == 200
    assert client.get("/api/portfolio/abstentions").status_code == 200
    assert client.get("/api/market/context").status_code == 200
    assert client.get("/api/quant/capabilities").status_code == 200
    assert client.get("/api/experiment").status_code == 200
    assert client.get("/api/snapshots").status_code == 200
    assert client.get("/api/provenance").status_code == 200
    assert client.post("/api/watchlists", json={"symbol": "000333.SZ"}).status_code == 405
    assert client.post("/api/orders", json={}).status_code in {404, 405}

    schema = client.get("/openapi.json").json()
    for path, methods in schema["paths"].items():
        if path.startswith("/api/"):
            assert set(methods).issubset({"get"}), (path, methods)


def test_local_cors_supports_a_non_default_frontend_port() -> None:
    client = TestClient(create_app(ROOT))
    response = client.options(
        "/api/status",
        headers={
            "Origin": "http://127.0.0.1:3010",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3010"


def test_api_launcher_check_loads_the_read_only_application() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/run_premarket_workspace_api.py"), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "read-only API check: PASS" in result.stdout


def test_workspace_launcher_check_validates_both_local_services() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/run_premarket_workspace.py"), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "workspace launcher check: PASS" in result.stdout
    assert "api=http://127.0.0.1:8000" in result.stdout
    assert "frontend=http://127.0.0.1:3000" in result.stdout


def test_goal_runner_and_audit_record_the_narrow_workspace_authorization() -> None:
    assert run_goal_premarket_research_position_workspace_dashboard01(ROOT) is True
    assert audit_goal_premarket_research_position_workspace_dashboard01(ROOT) is True

    manifest = __import__("json").loads(
        (ROOT / "outputs/audits/goal_premarket_research_position_workspace_dashboard01_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["status"] == "PASS"
    assert manifest["page_count"] == 23
    assert manifest["read_only_api_route_count"] == 22
    assert manifest["write_api_route_count"] == 0
    assert manifest["source_snapshot_integrity"] == "VERIFIED"
    assert manifest["ready_factor_count"] == 0
    assert manifest["generic_dashboard_capability"] is False
    assert manifest["recommendation_tiering_state"] == "locked_future"
    assert manifest["broker_connection"] is False
    assert manifest["orders_created"] is False


def test_safety_gate_accepts_only_the_named_issue24_workspace_surface() -> None:
    assert run_safety_gate(ROOT) is True


def test_safety_file_walk_prunes_generated_directories(tmp_path: Path) -> None:
    included = [tmp_path / "src/example.py", tmp_path / "outputs/audits/report.md"]
    ignored = [
        tmp_path / "apps/workspace/node_modules/package/dangerous.zip",
        tmp_path / "apps/workspace/.next/cache/chunk.py",
        tmp_path / ".venv/lib/python/site-packages/editable-install.pth",
        tmp_path / "venv/lib/python/site-packages/editable-install.pth",
        tmp_path / "outputs/local/raw_payload.csv",
    ]
    for path in [*included, *ignored]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture\n", encoding="utf-8")

    scanner = getattr(safety_module, "_iter_scannable_files", None)
    assert scanner is not None
    assert sorted(path.relative_to(tmp_path).as_posix() for path in scanner(tmp_path)) == [
        "outputs/audits/report.md",
        "src/example.py",
    ]


def test_dashboard_import_authorization_is_exact_not_prefix_based() -> None:
    authorized = "src/ashare_premarket/dashboard/api.py"

    assert forbidden_locked_import_terms(
        ROOT,
        "ashare_premarket.dashboard.repository",
        authorized,
        ["dashboard"],
    ) == []
    assert forbidden_locked_import_terms(
        ROOT,
        "ashare_premarket.dashboard_evil",
        authorized,
        ["dashboard"],
    ) == ["dashboard"]
    assert forbidden_locked_import_terms(
        ROOT,
        "ashare_premarket.dashboard.repository",
        "src/ashare_premarket/unrelated.py",
        ["dashboard"],
    ) == ["dashboard"]


def test_issue24_preservation_rejects_stale_implementation_checksums(tmp_path: Path) -> None:
    implementation = tmp_path / "src/example.py"
    implementation.parent.mkdir(parents=True)
    implementation.write_bytes(b"evidence = True\r\n")
    package = tmp_path / "apps/premarket-workspace/package.json"
    package.parent.mkdir(parents=True)
    package.write_text("{}\n", encoding="utf-8")
    audit = tmp_path / "outputs/audits/goal_premarket_research_position_workspace_dashboard01_audit.md"
    audit.parent.mkdir(parents=True)
    audit.write_text("Status: `PASS`\n", encoding="utf-8")
    manifest_path = tmp_path / "outputs/audits/goal_premarket_research_position_workspace_dashboard01_manifest.json"
    manifest = {
        "goal": "GOAL-PREMARKET-RESEARCH-AND-POSITION-WORKSPACE-DASHBOARD-01",
        "status": "PASS",
        "page_count": 23,
        "write_api_route_count": 0,
        "ready_factor_count": 0,
        "implementation_checksums": {"src/example.py": "stale"},
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    assert issue24_workspace_evidence_valid(tmp_path) is False
    manifest["implementation_checksums"]["src/example.py"] = hashlib.sha256(b"evidence = True\n").hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    assert issue24_workspace_evidence_valid(tmp_path) is True
    implementation.write_bytes(b"evidence = False\r\n")
    assert issue24_workspace_evidence_valid(tmp_path) is False


def test_earlier_goal_reruns_preserve_the_narrow_issue24_authorization() -> None:
    assert run_goal_premarket_research_position_workspace_dashboard01(ROOT) is True
    workflows: dict[str, dict[str, str]] = {}
    capabilities: dict[str, object] = {"dashboard": True}

    preserve_later_review_only_workflow_states(ROOT, workflows)
    preserve_later_review_only_capabilities(ROOT, capabilities)

    assert workflows["goal_premarket_research_position_workspace_dashboard01"]["status"] == "implemented_research_only"
    assert capabilities["goal_premarket_research_position_workspace_dashboard01_gate"] == "implemented_research_only"
    assert capabilities["dashboard"] is False

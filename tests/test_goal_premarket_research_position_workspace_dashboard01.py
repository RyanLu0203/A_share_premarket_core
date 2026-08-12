from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from ashare_premarket.core.boundary import (
    forbidden_locked_import_terms,
    issue24_workspace_evidence_valid,
)
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


def test_dashboard_store_observes_refresh_and_snapshot_pointer_updates_without_restart(
    tmp_path: Path,
) -> None:
    store = CommittedEvidenceStore(tmp_path)
    refresh_root = tmp_path / "outputs/research/daily_incremental_evidence_refresh"
    refresh_root.mkdir(parents=True)

    def write_refresh(state: str) -> None:
        manifest = refresh_root / f"{state.lower()}.json"
        manifest.write_bytes(
            (json.dumps({"refresh_status": state}, sort_keys=True) + "\n").encode(
                "utf-8"
            )
        )
        latest = {
            "refresh_status": state,
            "refresh_manifest_path": manifest.relative_to(tmp_path).as_posix(),
            "refresh_manifest_checksum": hashlib.sha256(
                manifest.read_bytes()
            ).hexdigest(),
        }
        (refresh_root / "latest_refresh.json").write_bytes(
            (json.dumps(latest, sort_keys=True) + "\n").encode("utf-8")
        )

    write_refresh("BLOCKED")
    assert store.refresh_status()["refresh_status"] == "BLOCKED"
    write_refresh("SUCCEEDED")
    assert store.refresh_status()["refresh_status"] == "SUCCEEDED"

    snapshot_root = tmp_path / "outputs/research/premarket_position_management"
    for date in ("2026-07-01", "2026-07-02"):
        data = snapshot_root / date / "data.csv"
        data.parent.mkdir(parents=True)
        data.write_text("value\nverified\n", encoding="utf-8")
        path = snapshot_root / date / "manifest.json"
        path.write_text(
            json.dumps(
                {
                    "snapshot_date": date,
                    "checksums": {
                        "data.csv": hashlib.sha256(data.read_bytes()).hexdigest()
                    },
                }
            ),
            encoding="utf-8",
        )
        (snapshot_root / "latest_manifest.json").write_text(
            json.dumps(
                {
                    "snapshot_date": date,
                    "snapshot_manifest_path": path.relative_to(tmp_path).as_posix(),
                    "snapshot_manifest_checksum": hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest(),
                }
            ),
            encoding="utf-8",
        )
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

    assert len(stocks) == 43
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

    luxshare = next(row for row in stocks if row["symbol"] == "002475.SZ")
    hengtong = next(row for row in stocks if row["symbol"] == "600487.SH")
    assert luxshare["display_name"] == "立讯精密"
    assert luxshare["latest_price"]["availability"] == "AVAILABLE"
    assert luxshare["latest_price"]["asof_date"] == "2026-05-21"
    assert hengtong["display_name"] == "亨通光电"
    assert hengtong["latest_price"]["availability"] == "UNAVAILABLE"
    assert all(
        row["portfolio_membership_state"] == "NOT_IN_REFERENCE_PORTFOLIO"
        for row in (luxshare, hengtong)
    )
    assert all(row["abstain"] is None for row in (luxshare, hengtong))


def test_ifind_pilot_symbols_are_browseable_without_fabricating_portfolio_evidence() -> (
    None
):
    repo = _repo()

    luxshare_market = repo.stock_market("002475.SZ", snapshot_date="2026-07-01")
    hengtong_market = repo.stock_market("600487.SH", snapshot_date="2026-07-01")
    for symbol in ("002475.SZ", "600487.SH"):
        detail = repo.stock(symbol, snapshot_date="2026-07-01")
        fundamentals = repo.stock_fundamentals(symbol)
        risk = repo.stock_risk(symbol, snapshot_date="2026-07-01")
        position = repo.stock_position(symbol, snapshot_date="2026-07-01")
        assert detail["portfolio_membership_state"] == "NOT_IN_REFERENCE_PORTFOLIO"
        assert fundamentals["research_only"] is True
        assert risk["risk_research_state"] == "RESEARCH_NOT_RUN_FOR_SECURITY_FOUNDATION"
        assert position["position_research_state"] == "POSITION_RESEARCH_NOT_RUN"
        assert position["actionable_use_allowed"] is False
        assert position["current_weight"] is None

    assert len(luxshare_market["candles"]) == 120
    assert hengtong_market["candles"] == []
    stocks = repo.stocks()
    watchlist_seed = repo.watchlist_seed()["symbols"]
    assert len(watchlist_seed) == 8
    assert all(
        next(row for row in stocks if row["symbol"] == symbol)[
            "portfolio_membership_state"
        ]
        == "REFERENCE_PORTFOLIO_MEMBER"
        for symbol in watchlist_seed
    )


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
    assert (
        sum(1 for row in constraints["summary"] if row["state"] == "FAIL_CLOSED") == 3
    )
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
    assert quant["candidate_rows"][0]["decision_summary"].startswith(
        "not_ready_failed:"
    )
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


def test_system_views_expose_only_credential_safe_ifind_readiness(
    monkeypatch,
) -> None:
    secret = "fixture-ifind-secret-never-render"
    monkeypatch.setenv("IFIND_MCP_API_KEY", secret)
    monkeypatch.delenv("ASHARE_ALLOW_NETWORK_INGESTION", raising=False)
    monkeypatch.delenv("ASHARE_ALLOW_IFIND", raising=False)
    monkeypatch.delenv("ASHARE_ALLOW_IFIND_MCP", raising=False)

    quality = _repo().data_quality("2026-07-01")
    provider = _repo().provider_health("2026-07-01")
    expected_readiness_fields = {
        "provider_id",
        "provider_name",
        "product_name",
        "channel_id",
        "interface_mode",
        "base_url",
        "protocol_version",
        "readiness_state",
        "network_opt_in",
        "provider_opt_in",
        "mcp_opt_in",
        "data_call_opt_in",
        "live_access_allowed",
        "credential_delivery_policy",
        "credential_verified",
        "keychain_lookup_available",
        "raw_payload_commit_allowed",
        "local_token_persistence_allowed",
        "supported_service_count",
        "entitlement_profile",
        "reviewed_tool_count",
        "expected_tool_count",
        "unavailable_by_plan_count",
        "unavailable_by_plan",
        "data_module_count",
        "last_probe_status",
        "last_probe_mode",
        "last_probe_server",
        "last_probe_failure_code",
        "last_probe_http_status",
        "last_probe_observed_at",
        "last_handshake_verified",
        "last_input_schemas_verified",
        "last_data_tool_called",
        "last_data_call_count",
        "last_failed_symbol",
        "s1_acceptance_state",
        "s1_temporal_class",
        "s1_provider_available_at_status",
        "s1_provider_available_at_verified",
        "s1_identity_observed_at",
        "s1_staged_symbol_count",
        "s1_identity_acceptance_verified",
        "s2_requires_separate_authorization",
        "ifind_canonical_accepted",
    }

    for payload in (quality, provider):
        readiness = payload["ifind_readiness"]
        assert set(readiness) == expected_readiness_fields
        assert readiness["readiness_state"] == "OFFLINE_READY_NETWORK_DISABLED"
        assert readiness["credential_delivery_policy"] == (
            "macos_keychain_preferred_environment_fallback"
        )
        assert readiness["credential_verified"] is False
        assert readiness["live_access_allowed"] is False
        assert readiness["raw_payload_commit_allowed"] is False
        assert readiness["local_token_persistence_allowed"] is False
        assert readiness["supported_service_count"] == 7
        assert readiness["entitlement_profile"] == "personal_trial_non_enterprise"
        assert readiness["reviewed_tool_count"] == 36
        assert readiness["expected_tool_count"] == 35
        assert readiness["unavailable_by_plan_count"] == 1
        assert readiness["unavailable_by_plan"] == ["edb:search_edb"]
        assert readiness["data_module_count"] == 7
        assert isinstance(readiness["last_data_tool_called"], bool)
        assert readiness["s1_provider_available_at_verified"] is False
        assert readiness["ifind_canonical_accepted"] is False
        if readiness["last_data_tool_called"]:
            assert readiness["last_data_call_count"] in {1, 2}
            if readiness["last_data_call_count"] == 1:
                assert readiness["last_failed_symbol"] == "002475.SZ"
            else:
                assert readiness["last_failed_symbol"] is None
        else:
            assert readiness["last_data_call_count"] is None
            assert readiness["last_failed_symbol"] is None
        assert len(payload["ifind_mcp_services"]) == 7
        assert len(payload["ifind_data_modules"]) == 7
        pilot = payload["ifind_pilot_acceptance"]
        assert pilot["canonical_approved_symbols_unchanged"] is True
        assert [row["symbol"] for row in pilot["symbols"]] == [
            "002475.SZ",
            "600487.SH",
        ]
        assert all(row["actionable_use_allowed"] is False for row in pilot["symbols"])
        assert {row["module_id"] for row in payload["ifind_data_modules"]} == {
            "security_master",
            "daily_market_and_calendar",
            "pit_fundamentals_and_valuation",
            "industry_and_constituents",
            "corporate_events_and_announcements",
            "macro_and_edb",
            "market_structure_crosscheck",
        }

    rendered = json.dumps(
        {"quality": quality, "provider": provider}, ensure_ascii=False
    )
    assert secret not in rendered
    assert "api_key_present" not in rendered
    assert "credential_source" not in rendered
    assert "600487.SH" in rendered


def test_live_system_views_separate_operational_tencent_from_historical_research_lineage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ASHARE_RUNTIME_CODE_COMMIT", "0" * 40)
    repo = _repo()
    provider = repo.provider_health()
    provenance = repo.provenance()
    quality = repo.data_quality()

    assert (
        provider["canonical_decision"]
        == "tencent_operational_primary_via_akshare_stock_zh_a_hist_tx"
    )
    assert provider["operational_provider"] == "Tencent"
    assert provider["operational_function"] == "stock_zh_a_hist_tx"
    assert provider["east_money_canonical_request_count"] == 0
    assert provider["adjustment_convention_status"] == "QFQ_ONLY"
    assert provider["amount_availability"] == "UNAVAILABLE_NULL_NOT_ZERO"
    assert provider["historical_research_provider_lineage"] == [
        "baostock",
        "akshare_sina",
    ]
    assert provenance["operational_source_lineage"][0] == "AKShare::stock_zh_a_hist_tx"
    assert provenance["code_commit"] == "0" * 40
    assert quality["status"]["execution_mode"] == "daily_operational"
    assert quality["status"]["operational_provider"] == "Tencent"


def test_fastapi_surface_is_read_only_and_exposes_required_views() -> None:
    client = TestClient(create_app(ROOT))

    status = client.get(
        "/api/status", params={"mode": "replay", "snapshot_date": "2026-07-01"}
    )
    assert status.status_code == 200
    assert status.json()["execution_mode"] == "deterministic_replay"
    assert (
        client.get("/api/command-center", params={"mode": "replay"}).status_code == 200
    )
    assert client.get("/api/stocks").status_code == 200
    assert client.get("/api/stocks/000333.SZ").status_code == 200
    assert client.get("/api/stocks/000333.SZ/market").status_code == 200
    assert client.get("/api/stocks/000333.SZ/fundamentals").status_code == 200
    assert client.get("/api/stocks/000333.SZ/risk").status_code == 200
    assert client.get("/api/stocks/000333.SZ/position").status_code == 200
    for symbol in ("002475.SZ", "600487.SH"):
        assert client.get(f"/api/stocks/{symbol}").status_code == 200
        assert client.get(f"/api/stocks/{symbol}/market").status_code == 200
        assert client.get(f"/api/stocks/{symbol}/fundamentals").status_code == 200
        assert client.get(f"/api/stocks/{symbol}/risk").status_code == 200
        assert client.get(f"/api/stocks/{symbol}/position").status_code == 200
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
    assert (
        client.post("/api/watchlists", json={"symbol": "000333.SZ"}).status_code == 405
    )
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
        [
            sys.executable,
            str(ROOT / "scripts/run_premarket_workspace_api.py"),
            "--check",
        ],
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
    assert "default_frontend_mode=production" in result.stdout


def test_workspace_launcher_prepares_complete_standalone_build(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    from scripts.run_premarket_workspace import _prepare_standalone

    frontend = tmp_path / "frontend"
    server = frontend / ".next/standalone/server.js"
    static = frontend / ".next/static/chunks/app.js"
    public = frontend / "public/health.txt"
    for path, content in ((server, "server"), (static, "chunk"), (public, "ok")):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    assert _prepare_standalone(frontend) == server
    assert (
        frontend / ".next/standalone/.next/static/chunks/app.js"
    ).read_text() == "chunk"
    assert (frontend / ".next/standalone/public/health.txt").read_text() == "ok"


def test_goal_runner_and_audit_record_the_narrow_workspace_authorization() -> None:
    assert run_goal_premarket_research_position_workspace_dashboard01(ROOT) is True
    assert audit_goal_premarket_research_position_workspace_dashboard01(ROOT) is True

    manifest = __import__("json").loads(
        (
            ROOT
            / "outputs/audits/goal_premarket_research_position_workspace_dashboard01_manifest.json"
        ).read_text(encoding="utf-8")
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
        tmp_path / ".venv/Lib/site-packages/dangerous.zip",
        tmp_path / "venv/Lib/site-packages/dangerous.zip",
        tmp_path / "outputs/local/raw_payload.csv",
    ]
    for path in [*included, *ignored]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture\n", encoding="utf-8")

    scanner = getattr(safety_module, "_iter_scannable_files", None)
    assert scanner is not None
    assert sorted(
        path.relative_to(tmp_path).as_posix() for path in scanner(tmp_path)
    ) == [
        "outputs/audits/report.md",
        "src/example.py",
    ]


def test_dashboard_import_authorization_is_exact_not_prefix_based() -> None:
    authorized = "src/ashare_premarket/dashboard/api.py"

    assert (
        forbidden_locked_import_terms(
            ROOT,
            "ashare_premarket.dashboard.repository",
            authorized,
            ["dashboard"],
        )
        == []
    )
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


def test_issue24_preservation_rejects_stale_implementation_checksums(
    tmp_path: Path,
) -> None:
    implementation = tmp_path / "src/example.py"
    implementation.parent.mkdir(parents=True)
    implementation.write_bytes(b"evidence = True\r\n")
    package = tmp_path / "apps/premarket-workspace/package.json"
    package.parent.mkdir(parents=True)
    package.write_text("{}\n", encoding="utf-8")
    audit = (
        tmp_path
        / "outputs/audits/goal_premarket_research_position_workspace_dashboard01_audit.md"
    )
    audit.parent.mkdir(parents=True)
    audit.write_text("Status: `PASS`\n", encoding="utf-8")
    manifest_path = (
        tmp_path
        / "outputs/audits/goal_premarket_research_position_workspace_dashboard01_manifest.json"
    )
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
    manifest["implementation_checksums"]["src/example.py"] = hashlib.sha256(
        b"evidence = True\n"
    ).hexdigest()
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

    assert (
        workflows["goal_premarket_research_position_workspace_dashboard01"]["status"]
        == "implemented_research_only"
    )
    assert (
        capabilities["goal_premarket_research_position_workspace_dashboard01_gate"]
        == "implemented_research_only"
    )
    assert capabilities["dashboard"] is False

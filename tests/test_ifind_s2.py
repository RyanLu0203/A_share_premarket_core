from __future__ import annotations

from datetime import date, timedelta
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

import pytest

from ashare_premarket.providers.ifind_http import IfindProviderError
from ashare_premarket.providers.ifind_s2 import (
    IFIND_S2_ACCEPTANCE_STATE,
    IFIND_S2_ADJUSTMENT_MODE,
    IFIND_S2_DATA_CALL_BUDGET,
    IFIND_S2_DAILY_SESSION_COUNT,
    IFIND_S2_FIXED_TOOLS,
    IFIND_S2_PREFLIGHT_STATE,
    IfindS2LiveResult,
    build_ifind_s2_offline_plan,
    normalize_ifind_s2_daily_market,
    normalize_ifind_s2_security_master,
    read_ifind_s2_status,
    run_ifind_s2_live_acceptance,
    s2_bundle_id,
    s2_manifest_sha256,
    write_ifind_s2_acceptance_bundle,
    write_ifind_s2_status,
)
from ashare_premarket.providers.ifind_mcp import (
    IFIND_MCP_ENTITLED_TOOL_CATALOG,
    IFIND_MCP_PROTOCOL_VERSION,
)


ROOT = Path(__file__).resolve().parents[1]


def _accepted_s1_status() -> dict[str, Any]:
    return {
        "status": "PASS",
        "mode": "live_stage_s1",
        "acceptance_state": "S1_IDENTITY_ACCEPTANCE_METADATA_VERIFIED",
        "data_call_count": 2,
        "staged_symbol_count": 2,
        "live_handshake_verified": True,
        "input_schemas_verified": True,
        "data_tool_called": True,
        "s1_identity_acceptance_verified": True,
        "s2_requires_separate_authorization": True,
        "canonical_accepted": False,
    }


def _staged(rows: list[Mapping[str, Any]]) -> Mapping[str, Any]:
    return {
        "staging_format": "provider_markdown_tables_v1",
        "provider_success": True,
        "canonical_accepted": False,
        "tables": [
            {
                "title": "fixture",
                "columns": list(rows[0]),
                "rows": [dict(row) for row in rows],
            }
        ],
    }


def _security_row(
    symbol: str = "002475.SZ", company_name: str = "立讯精密"
) -> dict[str, Any]:
    return {
        "证券代码": symbol,
        "证券简称": company_name,
        "数据日期": "2026-08-12",
        "数据可用时间": "2026-08-12T15:00:00+08:00",
        "上市日期": "2010-09-15",
        "交易状态": "正常交易",
        "总股本": "7737819806",
        "总股本单位": "股",
        "流通股本": "7600000000",
        "流通股本单位": "股",
        "所属行业": "电子",
    }


def _market_fixture(
    symbol: str = "002475.SZ", company_name: str = "立讯精密"
) -> tuple[list[dict[str, Any]], list[str]]:
    dates = [
        (date(2026, 4, 15) + timedelta(days=index)).isoformat()
        for index in range(IFIND_S2_DAILY_SESSION_COUNT)
    ]
    rows = [
        {
            "证券代码": symbol,
            "证券简称": company_name,
            "交易日期": trade_date,
            "开盘": "10.0",
            "最高": "11.0",
            "最低": "9.0",
            "收盘": "10.5",
            "成交量": "1000",
            "成交量单位": "股",
            "成交额": "10500",
            "成交额单位": "元",
            "换手率": "1.2",
            "换手率口径": "百分比",
            "复权方式": "前复权",
            "数据可用时间": "2026-08-12T15:00:00+08:00",
        }
        for trade_date in dates
    ]
    return rows, dates


class _FakeS2Client:
    def __init__(self, fail_first: bool = False) -> None:
        self.fail_first = fail_first
        self.calls: list[tuple[str, str, str]] = []

    def initialize(self, _server_type: str) -> Mapping[str, Any]:
        return {"protocolVersion": IFIND_MCP_PROTOCOL_VERSION}

    def list_tools(self, server_type: str) -> tuple[str, ...]:
        return tuple(sorted(IFIND_MCP_ENTITLED_TOOL_CATALOG[server_type]))

    def list_tool_contracts(self, server_type: str) -> tuple[Mapping[str, Any], ...]:
        return tuple(
            {
                "tool_name": tool_name,
                "schema_sha256": hashlib.sha256(
                    f"{server_type}:{tool_name}".encode("utf-8")
                ).hexdigest(),
                "supplier_contract_match": True,
            }
            for tool_name in sorted(IFIND_MCP_ENTITLED_TOOL_CATALOG[server_type])
        )

    def call_s2_stock_tool(
        self, symbol: str, tool_name: str, cutoff_date: str
    ) -> Mapping[str, Any]:
        self.calls.append((symbol, tool_name, cutoff_date))
        if self.fail_first:
            return {"staging_format": "invalid", "canonical_accepted": False}
        company = "立讯精密" if symbol == "002475.SZ" else "亨通光电"
        if tool_name == "get_stock_info":
            return _staged([_security_row(symbol, company)])
        rows, _dates = _market_fixture(symbol, company)
        return _staged(rows)


def test_s2_offline_plan_is_exact_bounded_and_never_authorizes_calls() -> None:
    plan = build_ifind_s2_offline_plan(
        ROOT,
        cutoff_date="2026-08-12",
        s1_status=_accepted_s1_status(),
    )
    summary = plan.safe_summary()

    assert summary["preflight_state"] == IFIND_S2_PREFLIGHT_STATE
    assert summary["fixed_tools"] == list(IFIND_S2_FIXED_TOOLS)
    assert summary["data_call_budget"] == IFIND_S2_DATA_CALL_BUDGET
    assert len(summary["calls"]) == IFIND_S2_DATA_CALL_BUDGET
    assert summary["separate_authorization_required"] is True
    assert summary["data_calls_authorized"] is False
    assert summary["network_accessed"] is False
    assert summary["keychain_accessed"] is False
    assert summary["data_tool_called"] is False
    assert summary["canonical_accepted"] is False
    assert plan.scope.allowed_symbols == ("002475.SZ", "600487.SH")
    assert plan.scope.allowed_tools == IFIND_S2_FIXED_TOOLS
    assert {(call.symbol, call.tool_name) for call in plan.calls} == {
        ("002475.SZ", "get_stock_info"),
        ("002475.SZ", "get_stock_performance"),
        ("600487.SH", "get_stock_info"),
        ("600487.SH", "get_stock_performance"),
    }
    assert {call.expected_row_count for call in plan.calls} == {1, 120}
    assert all(
        set(row) == {"symbol", "tool_name", "query_sha256", "expected_row_count"}
        for row in summary["calls"]
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("status", "BLOCKED"),
        ("data_call_count", 1),
        ("staged_symbol_count", 1),
        ("canonical_accepted", True),
        ("s2_requires_separate_authorization", False),
    ],
)
def test_s2_preflight_rejects_any_incomplete_or_promoted_s1_status(
    field: str, value: Any
) -> None:
    status = _accepted_s1_status()
    status[field] = value

    with pytest.raises(IfindProviderError) as exc:
        build_ifind_s2_offline_plan(ROOT, cutoff_date="2026-08-12", s1_status=status)

    assert exc.value.failure_code == "IFIND_MCP_S2_PREREQUISITE_UNVERIFIED"


def test_s2_security_master_normalizes_only_typed_identity_and_provider_time() -> None:
    batch = normalize_ifind_s2_security_master(
        staged=_staged([_security_row()]),
        symbol="002475.SZ",
        company_name="立讯精密",
        decision_cutoff="2026-08-12T16:00:00+08:00",
    )

    assert batch.module_id == "security_master"
    assert batch.source_function == "get_stock_info"
    assert len(batch.rows) == 1
    row = batch.rows[0]
    assert row["symbol"] == "002475.SZ"
    assert row["entity_name"] == "立讯精密"
    assert row["listing_date"] == "2010-09-15"
    assert row["available_at"] == "2026-08-12T07:00:00Z"
    assert row["total_shares"] == 7737819806.0


def test_s2_security_master_rejects_missing_provider_availability() -> None:
    row = _security_row()
    row["数据可用时间"] = ""

    with pytest.raises(IfindProviderError) as exc:
        normalize_ifind_s2_security_master(
            staged=_staged([row]),
            symbol="002475.SZ",
            company_name="立讯精密",
            decision_cutoff="2026-08-12T16:00:00+08:00",
        )

    assert exc.value.failure_code == "IFIND_MCP_S2_AVAILABILITY_AMBIGUOUS"
    assert exc.value.safe_metadata["failure_reason"] == (
        "provider_availability_missing"
    )


def test_s2_security_master_accepts_reviewed_listing_alias_and_exact_six_digit_code() -> (
    None
):
    row = _security_row()
    row["证券代码"] = "002475"
    row["首发上市日期"] = "20100915"
    del row["上市日期"]

    batch = normalize_ifind_s2_security_master(
        staged=_staged([row]),
        symbol="002475.SZ",
        company_name="立讯精密",
        decision_cutoff="2026-08-12T16:00:00+08:00",
    )

    assert batch.rows[0]["symbol"] == "002475.SZ"
    assert batch.rows[0]["listing_date"] == "2010-09-15"


def test_s2_daily_market_normalizes_exact_qfq_governed_calendar() -> None:
    rows, dates = _market_fixture()

    batch = normalize_ifind_s2_daily_market(
        staged=_staged(rows),
        symbol="002475.SZ",
        company_name="立讯精密",
        decision_cutoff="2026-08-12T16:00:00+08:00",
        expected_trade_dates=dates,
    )

    assert batch.module_id == "daily_market_and_calendar"
    assert batch.source_function == "get_stock_performance"
    assert len(batch.rows) == IFIND_S2_DAILY_SESSION_COUNT
    assert {row["adjustment_mode"] for row in batch.rows} == {IFIND_S2_ADJUSTMENT_MODE}
    assert batch.rows[-1]["trade_date"] == "2026-08-12"
    assert all(row["available_at"] == "2026-08-12T07:00:00Z" for row in batch.rows)


def test_s2_daily_market_rejects_non_qfq_and_calendar_drift() -> None:
    rows, dates = _market_fixture()
    rows[0]["复权方式"] = "不复权"

    with pytest.raises(IfindProviderError) as exc:
        normalize_ifind_s2_daily_market(
            staged=_staged(rows),
            symbol="002475.SZ",
            company_name="立讯精密",
            decision_cutoff="2026-08-12T16:00:00+08:00",
            expected_trade_dates=dates,
        )
    assert exc.value.failure_code == "IFIND_MCP_S2_ADJUSTMENT_MISMATCH"

    rows, dates = _market_fixture()
    dates[-1] = "2026-08-13"
    with pytest.raises(IfindProviderError) as exc:
        normalize_ifind_s2_daily_market(
            staged=_staged(rows),
            symbol="002475.SZ",
            company_name="立讯精密",
            decision_cutoff="2026-08-12T16:00:00+08:00",
            expected_trade_dates=dates,
        )
    assert exc.value.failure_code == "IFIND_MCP_S2_CALENDAR_MISMATCH"


@pytest.mark.parametrize(
    ("field", "value"),
    (("成交量单位", "手"), ("成交额单位", "万元"), ("换手率口径", "ratio")),
)
def test_s2_daily_market_rejects_unreviewed_units(field: str, value: str) -> None:
    rows, dates = _market_fixture()
    rows[0][field] = value

    with pytest.raises(IfindProviderError) as exc:
        normalize_ifind_s2_daily_market(
            staged=_staged(rows),
            symbol="002475.SZ",
            company_name="立讯精密",
            decision_cutoff="2026-08-12T16:00:00+08:00",
            expected_trade_dates=dates,
        )

    assert exc.value.failure_code == "IFIND_MCP_S2_UNIT_MISMATCH"


@pytest.mark.parametrize(
    ("field", "value"), (("总股本单位", "万股"), ("流通股本单位", "手"))
)
def test_s2_security_master_rejects_unreviewed_share_units(
    field: str, value: str
) -> None:
    row = _security_row()
    row[field] = value

    with pytest.raises(IfindProviderError) as exc:
        normalize_ifind_s2_security_master(
            staged=_staged([row]),
            symbol="002475.SZ",
            company_name="立讯精密",
            decision_cutoff="2026-08-12T16:00:00+08:00",
        )

    assert exc.value.failure_code == "IFIND_MCP_S2_UNIT_MISMATCH"


def test_s2_daily_market_rejects_cross_symbol_response() -> None:
    rows, dates = _market_fixture()
    rows[-1]["证券代码"] = "600487.SH"
    rows[-1]["证券简称"] = "亨通光电"

    with pytest.raises(IfindProviderError) as exc:
        normalize_ifind_s2_daily_market(
            staged=_staged(rows),
            symbol="002475.SZ",
            company_name="立讯精密",
            decision_cutoff="2026-08-12T16:00:00+08:00",
            expected_trade_dates=dates,
        )

    assert exc.value.failure_code == "IFIND_MCP_S2_IDENTITY_MISMATCH"


def test_s2_live_acceptance_runs_same_client_s0_and_exactly_four_fixed_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _FakeS2Client()
    _rows, dates = _market_fixture()
    monkeypatch.setattr(
        "ashare_premarket.providers.ifind_s2.expected_ifind_s2_trade_dates",
        lambda _root, _cutoff: tuple(dates),
    )

    result = run_ifind_s2_live_acceptance(
        ROOT,
        decision_timestamp="2026-08-12T16:00:00+08:00",
        cutoff_date="2026-08-12",
        s1_status=_accepted_s1_status(),
        environ={
            "ASHARE_ALLOW_NETWORK_INGESTION": "1",
            "ASHARE_ALLOW_IFIND": "1",
            "ASHARE_ALLOW_IFIND_MCP": "1",
            "ASHARE_ALLOW_IFIND_MCP_DATA_CALLS": "1",
        },
        client_factory=lambda _policy, _scope: fake,  # type: ignore[arg-type]
    )

    assert result.safe_result["status"] == "PASS"
    assert result.safe_result["acceptance_state"] == IFIND_S2_ACCEPTANCE_STATE
    assert result.safe_result["data_call_count"] == 4
    assert result.safe_result["normalized_row_count"] == 242
    assert result.safe_result["provider_schema_accepted"] is True
    assert result.safe_result["canonical_accepted"] is False
    assert len(result.batches) == 4
    assert fake.calls == [
        ("002475.SZ", "get_stock_info", "2026-08-12"),
        ("002475.SZ", "get_stock_performance", "2026-08-12"),
        ("600487.SH", "get_stock_info", "2026-08-12"),
        ("600487.SH", "get_stock_performance", "2026-08-12"),
    ]
    rendered = json.dumps(result.safe_result, ensure_ascii=False)
    assert "provider-secret" not in rendered
    assert "tables" not in rendered


def test_s2_live_acceptance_stops_after_first_schema_failure_without_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _FakeS2Client(fail_first=True)
    _rows, dates = _market_fixture()
    monkeypatch.setattr(
        "ashare_premarket.providers.ifind_s2.expected_ifind_s2_trade_dates",
        lambda _root, _cutoff: tuple(dates),
    )

    result = run_ifind_s2_live_acceptance(
        ROOT,
        decision_timestamp="2026-08-12T16:00:00+08:00",
        cutoff_date="2026-08-12",
        s1_status=_accepted_s1_status(),
        environ={
            "ASHARE_ALLOW_NETWORK_INGESTION": "1",
            "ASHARE_ALLOW_IFIND": "1",
            "ASHARE_ALLOW_IFIND_MCP": "1",
            "ASHARE_ALLOW_IFIND_MCP_DATA_CALLS": "1",
        },
        client_factory=lambda _policy, _scope: fake,  # type: ignore[arg-type]
    )

    assert result.safe_result["status"] == "BLOCKED"
    assert result.safe_result["data_call_count"] == 1
    assert result.safe_result["retries_per_request"] == 0
    assert result.safe_result["canonical_accepted"] is False
    assert result.batches == ()
    assert fake.calls == [("002475.SZ", "get_stock_info", "2026-08-12")]


def test_s2_live_failure_retains_only_metadata_shape_and_fixed_missing_columns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class PortalShapeClient(_FakeS2Client):
        def call_s2_stock_tool(
            self, symbol: str, tool_name: str, cutoff_date: str
        ) -> Mapping[str, Any]:
            self.calls.append((symbol, tool_name, cutoff_date))
            return _staged(
                [
                    {
                        "证券代码": "002475.SZ",
                        "证券简称": "立讯精密",
                        "首发上市日期": "20100915",
                        "公司中文名称": "fixture-secret-company",
                        "注册地址": "fixture-secret-address",
                    }
                ]
            )

    fake = PortalShapeClient()
    _rows, dates = _market_fixture()
    monkeypatch.setattr(
        "ashare_premarket.providers.ifind_s2.expected_ifind_s2_trade_dates",
        lambda _root, _cutoff: tuple(dates),
    )

    result = run_ifind_s2_live_acceptance(
        ROOT,
        decision_timestamp="2026-08-12T16:00:00+08:00",
        cutoff_date="2026-08-12",
        s1_status=_accepted_s1_status(),
        environ={
            "ASHARE_ALLOW_NETWORK_INGESTION": "1",
            "ASHARE_ALLOW_IFIND": "1",
            "ASHARE_ALLOW_IFIND_MCP": "1",
            "ASHARE_ALLOW_IFIND_MCP_DATA_CALLS": "1",
        },
        client_factory=lambda _policy, _scope: fake,  # type: ignore[arg-type]
    )

    assert result.safe_result["failure_code"] == (
        "IFIND_MCP_S2_REQUIRED_COLUMNS_MISSING"
    )
    diagnostic = result.safe_result["response_diagnostic"]
    assert diagnostic["failure_stage"] == "s2_table_selection"
    assert diagnostic["failure_reason"] == "required_columns_missing"
    assert diagnostic["missing_required_columns"] == [
        "数据日期",
        "数据可用时间",
        "交易状态",
        "总股本",
        "总股本单位",
        "流通股本",
        "流通股本单位",
    ]
    assert diagnostic["raw_payload_persisted"] is False
    rendered = json.dumps(result.safe_result, ensure_ascii=False)
    assert "fixture-secret-company" not in rendered
    assert "fixture-secret-address" not in rendered


def test_s2_local_status_preserves_only_allowlisted_shape_metadata(
    tmp_path: Path,
) -> None:
    write_ifind_s2_status(
        tmp_path,
        {
            "status": "BLOCKED",
            "failure_code": "IFIND_MCP_S2_REQUIRED_COLUMNS_MISSING",
            "failed_symbol": "002475.SZ",
            "failed_tool": "get_stock_info",
            "data_call_count": 1,
            "response_diagnostic": {
                "failure_stage": "s2_table_selection",
                "failure_reason": "required_columns_missing",
                "missing_required_columns": [
                    "数据可用时间",
                    "fixture-secret-column",
                ],
                "supplier_body": "fixture-secret-body",
                "raw_payload_persisted": True,
            },
        },
    )

    status = read_ifind_s2_status(tmp_path)
    diagnostic = status["response_diagnostic"]
    assert diagnostic["missing_required_columns"] == ["数据可用时间"]
    assert diagnostic["raw_payload_persisted"] is False
    rendered = json.dumps(status, ensure_ascii=False)
    assert "fixture-secret" not in rendered


@pytest.mark.parametrize(
    ("unsafe_override", "value"),
    [
        ("live_handshake_verified", False),
        ("input_schemas_verified", False),
        ("provider_schema_accepted", False),
        ("canonical_accepted", False),
        ("raw_payload_persisted", True),
        ("credential_exposed", True),
        ("bundle_id", "../untrusted"),
    ],
)
def test_s2_status_cannot_self_report_acceptance_without_every_gate(
    tmp_path: Path, unsafe_override: str, value: object
) -> None:
    payload = {
        "status": "PASS",
        "acceptance_state": IFIND_S2_ACCEPTANCE_STATE,
        "data_call_count": 4,
        "normalized_row_count": 242,
        "bundle_id": "ifind-s2-valid-anchor",
        "bundle_manifest_sha256": "0" * 64,
        "bundle_persisted": True,
        "live_handshake_verified": True,
        "input_schemas_verified": True,
        "provider_schema_accepted": True,
        "canonical_accepted": True,
        "raw_payload_persisted": False,
        "credential_exposed": False,
        unsafe_override: value,
    }

    write_ifind_s2_status(tmp_path, payload)
    status = read_ifind_s2_status(tmp_path)

    assert status["status"] == "INVALID_LOCAL_STATUS"
    assert status["acceptance_state"] == "NOT_ACCEPTED"
    assert status["bundle_id"] is None
    assert status["bundle_persisted"] is False
    assert status["provider_schema_accepted"] is False
    assert status["canonical_accepted"] is False
    assert status["failure_code"] == "IFIND_MCP_S2_STATUS_CONTRACT_INVALID"


def test_s2_bundle_is_external_atomic_normalized_only_and_status_is_sanitized(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = _FakeS2Client()
    _rows, dates = _market_fixture()
    monkeypatch.setattr(
        "ashare_premarket.providers.ifind_s2.expected_ifind_s2_trade_dates",
        lambda _root, _cutoff: tuple(dates),
    )
    result = run_ifind_s2_live_acceptance(
        ROOT,
        decision_timestamp="2026-08-12T16:00:00+08:00",
        cutoff_date="2026-08-12",
        s1_status=_accepted_s1_status(),
        environ={
            "ASHARE_ALLOW_NETWORK_INGESTION": "1",
            "ASHARE_ALLOW_IFIND": "1",
            "ASHARE_ALLOW_IFIND_MCP": "1",
            "ASHARE_ALLOW_IFIND_MCP_DATA_CALLS": "1",
        },
        client_factory=lambda _policy, _scope: fake,  # type: ignore[arg-type]
    )
    external = tmp_path / "paid-data"
    monkeypatch.setenv("ASHARE_PREMARKET_DATA_ROOT", str(external))
    bundle = s2_bundle_id(result)
    manifest_path = write_ifind_s2_acceptance_bundle(ROOT, result, bundle_id=bundle)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["bundle_id"] == bundle
    assert len(manifest["artifacts"]) == 4
    assert sum(row["row_count"] for row in manifest["artifacts"]) == 242
    assert all(row["file"].endswith(".jsonl") for row in manifest["artifacts"])
    assert all(
        row["schema_version"] == "ifind-normalized-v1" for row in manifest["artifacts"]
    )
    assert all(row["request_digest"] for row in manifest["artifacts"])
    assert all(row["source_function"] for row in manifest["artifacts"])
    assert not list(external.rglob("*raw*"))
    assert os.stat(manifest_path).st_mode & 0o777 == 0o600

    local_root = tmp_path / "local-status-root"
    payload = dict(result.safe_result)
    payload.update(
        {
            "bundle_id": bundle,
            "bundle_persisted": True,
            "bundle_manifest_sha256": s2_manifest_sha256(manifest_path),
            "canonical_accepted": True,
            "api_key": "must-never-persist",
        }
    )
    write_ifind_s2_status(local_root, payload)
    status = read_ifind_s2_status(local_root)
    assert status["provider_schema_accepted"] is True
    assert status["canonical_accepted"] is True
    assert status["bundle_manifest_sha256"] == s2_manifest_sha256(manifest_path)
    rendered = (local_root / "outputs/local/ifind/mcp_s2_status.json").read_text(
        encoding="utf-8"
    )
    assert "must-never-persist" not in rendered
    assert "api_key" not in rendered


def test_s2_bundle_writer_rejects_duplicate_module_symbol_batch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = _FakeS2Client()
    _rows, dates = _market_fixture()
    monkeypatch.setattr(
        "ashare_premarket.providers.ifind_s2.expected_ifind_s2_trade_dates",
        lambda _root, _cutoff: tuple(dates),
    )
    result = run_ifind_s2_live_acceptance(
        ROOT,
        decision_timestamp="2026-08-12T16:00:00+08:00",
        cutoff_date="2026-08-12",
        s1_status=_accepted_s1_status(),
        environ={
            "ASHARE_ALLOW_NETWORK_INGESTION": "1",
            "ASHARE_ALLOW_IFIND": "1",
            "ASHARE_ALLOW_IFIND_MCP": "1",
            "ASHARE_ALLOW_IFIND_MCP_DATA_CALLS": "1",
        },
        client_factory=lambda _policy, _scope: fake,  # type: ignore[arg-type]
    )
    duplicate = IfindS2LiveResult(
        safe_result=result.safe_result,
        batches=(result.batches[0], result.batches[0], *result.batches[2:]),
    )
    monkeypatch.setenv("ASHARE_PREMARKET_DATA_ROOT", str(tmp_path / "paid-data"))

    with pytest.raises(IfindProviderError) as exc:
        write_ifind_s2_acceptance_bundle(
            ROOT, duplicate, bundle_id=s2_bundle_id(result)
        )

    assert exc.value.failure_code == "IFIND_MCP_S2_BUNDLE_INVALID"
    assert not (tmp_path / "paid-data").exists()

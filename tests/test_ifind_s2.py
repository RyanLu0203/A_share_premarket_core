from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any, Mapping

import pytest

from ashare_premarket.providers.ifind_http import IfindProviderError
from ashare_premarket.providers.ifind_s2 import (
    IFIND_S2_ADJUSTMENT_MODE,
    IFIND_S2_DATA_CALL_BUDGET,
    IFIND_S2_DAILY_SESSION_COUNT,
    IFIND_S2_FIXED_TOOLS,
    IFIND_S2_PREFLIGHT_STATE,
    build_ifind_s2_offline_plan,
    normalize_ifind_s2_daily_market,
    normalize_ifind_s2_security_master,
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


def _security_row() -> dict[str, Any]:
    return {
        "证券代码": "002475.SZ",
        "证券简称": "立讯精密",
        "数据日期": "2026-08-12",
        "数据可用时间": "2026-08-12T15:00:00+08:00",
        "上市日期": "2010-09-15",
        "交易状态": "正常交易",
        "总股本": "7737819806",
        "流通股本": "7600000000",
        "所属行业": "电子",
    }


def _market_fixture() -> tuple[list[dict[str, Any]], list[str]]:
    dates = [
        (date(2026, 4, 15) + timedelta(days=index)).isoformat()
        for index in range(IFIND_S2_DAILY_SESSION_COUNT)
    ]
    rows = [
        {
            "证券代码": "002475.SZ",
            "证券简称": "立讯精密",
            "交易日期": trade_date,
            "开盘": "10.0",
            "最高": "11.0",
            "最低": "9.0",
            "收盘": "10.5",
            "成交量": "1000",
            "成交额": "10500",
            "换手率": "1.2",
            "复权方式": "前复权",
            "数据可用时间": "2026-08-12T15:00:00+08:00",
        }
        for trade_date in dates
    ]
    return rows, dates


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

    assert exc.value.failure_code == "IFIND_MCP_S2_RESPONSE_SCHEMA_MISMATCH"


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

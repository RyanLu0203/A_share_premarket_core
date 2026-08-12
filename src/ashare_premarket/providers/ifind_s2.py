from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence, Tuple

from ashare_premarket.providers.ifind_acceptance import (
    IFIND_DUAL_STOCK_IDENTITIES,
    IFIND_DUAL_STOCK_SYMBOLS,
    load_ifind_dual_stock_acceptance_config,
)
from ashare_premarket.providers.ifind_http import IfindProviderError
from ashare_premarket.providers.ifind_mcp import IfindMcpCallScope
from ashare_premarket.providers.ifind_normalization import (
    IfindNormalizedBatch,
    normalize_ifind_payload,
)


IFIND_S2_STAGE_ID = "S2_SECURITY_MASTER_AND_DAILY_MARKET"
IFIND_S2_FIXED_TOOLS = ("get_stock_info", "get_stock_performance")
IFIND_S2_DATA_CALL_BUDGET = 4
IFIND_S2_DAILY_SESSION_COUNT = 120
IFIND_S2_ADJUSTMENT_MODE = "qfq"
IFIND_S2_PREFLIGHT_STATE = "S2_OFFLINE_FOUNDATION_READY_AUTHORIZATION_REQUIRED"

_S2_QUERY_TEMPLATES = {
    "get_stock_info": (
        "返回{company_name}（{symbol}）的证券代码、证券简称、交易所、上市日期、"
        "交易状态、ST状态、总股本、流通股本、所属行业、数据日期和数据可用时间；"
        "数据可用时间必须包含时区；仅返回结构化字段。"
    ),
    "get_stock_performance": (
        "返回{company_name}（{symbol}）截至{cutoff_date}最近120个已完成交易日的"
        "前复权日线行情，包含证券代码、证券简称、交易日期、开盘、最高、最低、"
        "收盘、成交量、成交额、换手率、复权方式和数据可用时间；数据可用时间必须"
        "包含时区；不得返回未来日期；仅返回结构化字段。"
    ),
}

_SECURITY_REQUIRED_COLUMNS = (
    "证券代码",
    "证券简称",
    "数据日期",
    "数据可用时间",
    "上市日期",
    "交易状态",
    "总股本",
    "流通股本",
)
_MARKET_REQUIRED_COLUMNS = (
    "证券代码",
    "证券简称",
    "交易日期",
    "开盘",
    "最高",
    "最低",
    "收盘",
    "成交量",
    "成交额",
    "换手率",
    "复权方式",
    "数据可用时间",
)


@dataclass(frozen=True)
class IfindS2Call:
    symbol: str
    company_name: str
    tool_name: str
    query: str
    expected_row_count: int

    def safe_summary(self) -> Mapping[str, Any]:
        return {
            "symbol": self.symbol,
            "tool_name": self.tool_name,
            "query_sha256": hashlib.sha256(self.query.encode("utf-8")).hexdigest(),
            "expected_row_count": self.expected_row_count,
        }


@dataclass(frozen=True)
class IfindS2Plan:
    calls: Tuple[IfindS2Call, ...]
    scope: IfindMcpCallScope
    cutoff_date: str

    def safe_summary(self) -> Mapping[str, Any]:
        return {
            "status": "PASS",
            "mode": "offline_stage_s2_preflight",
            "stage_id": IFIND_S2_STAGE_ID,
            "preflight_state": IFIND_S2_PREFLIGHT_STATE,
            "symbols": list(IFIND_DUAL_STOCK_SYMBOLS),
            "fixed_tools": list(IFIND_S2_FIXED_TOOLS),
            "data_call_budget": IFIND_S2_DATA_CALL_BUDGET,
            "retries_per_request": 0,
            "daily_session_count": IFIND_S2_DAILY_SESSION_COUNT,
            "adjustment_mode": IFIND_S2_ADJUSTMENT_MODE,
            "calls": [call.safe_summary() for call in self.calls],
            "separate_authorization_required": True,
            "data_calls_authorized": False,
            "network_accessed": False,
            "keychain_accessed": False,
            "data_tool_called": False,
            "raw_payload_persisted": False,
            "canonical_accepted": False,
        }


def build_ifind_s2_offline_plan(
    repository_root: Path,
    *,
    cutoff_date: str,
    s1_status: Mapping[str, Any],
) -> IfindS2Plan:
    """Build the exact four-call S2 plan without creating a provider client."""

    config = load_ifind_dual_stock_acceptance_config(repository_root)
    _validate_s1_status(s1_status)
    stage = next(
        row
        for row in config.call_plan["stages"]
        if row["stage_id"] == IFIND_S2_STAGE_ID
    )
    if (
        tuple(stage.get("fixed_tools", ())) != IFIND_S2_FIXED_TOOLS
        or tuple(stage.get("fixed_symbols", ())) != IFIND_DUAL_STOCK_SYMBOLS
        or stage.get("data_call_budget") != IFIND_S2_DATA_CALL_BUDGET
        or stage.get("calls_per_tool_per_symbol") != 1
    ):
        raise _s2_contract_error()
    normalized_cutoff = _validate_cutoff_date(cutoff_date)
    names = {
        symbol: company for symbol, company, _exchange in IFIND_DUAL_STOCK_IDENTITIES
    }
    calls = tuple(
        IfindS2Call(
            symbol=symbol,
            company_name=names[symbol],
            tool_name=tool_name,
            query=_S2_QUERY_TEMPLATES[tool_name].format(
                symbol=symbol,
                company_name=names[symbol],
                cutoff_date=normalized_cutoff,
            ),
            expected_row_count=(
                1 if tool_name == "get_stock_info" else IFIND_S2_DAILY_SESSION_COUNT
            ),
        )
        for symbol in IFIND_DUAL_STOCK_SYMBOLS
        for tool_name in IFIND_S2_FIXED_TOOLS
    )
    if (
        len(calls) != IFIND_S2_DATA_CALL_BUDGET
        or len({(call.symbol, call.tool_name) for call in calls})
        != IFIND_S2_DATA_CALL_BUDGET
    ):
        raise _s2_contract_error()
    scope = IfindMcpCallScope(
        cohort_id=str(config.pilot["cohort_id"]),
        allowed_symbols=IFIND_DUAL_STOCK_SYMBOLS,
        company_names=tuple(
            (symbol, names[symbol]) for symbol in IFIND_DUAL_STOCK_SYMBOLS
        ),
        allowed_services=("stock",),
        allowed_tools=IFIND_S2_FIXED_TOOLS,
    )
    return IfindS2Plan(calls=calls, scope=scope, cutoff_date=normalized_cutoff)


def normalize_ifind_s2_security_master(
    *,
    staged: Mapping[str, Any],
    symbol: str,
    company_name: str,
    decision_cutoff: str,
) -> IfindNormalizedBatch:
    rows = _require_markdown_rows(staged, _SECURITY_REQUIRED_COLUMNS, exact_rows=1)
    row = rows[0]
    _validate_identity(row, symbol, company_name)
    provider_available_at = _required_text(row, "数据可用时间")
    table = _columnar_table(rows)
    mapping = {
        "证券代码": "symbol",
        "数据日期": "as_of_date",
        "上市日期": "listing_date",
        "证券简称": "entity_name",
        "交易状态": "trading_status",
        "总股本": "total_shares",
        "流通股本": "float_shares",
    }
    if "所属行业" in row:
        mapping["所属行业"] = "industry_name"
    return normalize_ifind_payload(
        module_id="security_master",
        payload={"tables": [table]},
        field_mapping=mapping,
        source_function="get_stock_info",
        available_at=provider_available_at,
        decision_cutoff=decision_cutoff,
        request_descriptor={
            "stage_id": IFIND_S2_STAGE_ID,
            "tool_name": "get_stock_info",
            "symbol": symbol,
        },
        quality_flags=("S2_TYPED_PROVIDER_SCHEMA",),
    )


def normalize_ifind_s2_daily_market(
    *,
    staged: Mapping[str, Any],
    symbol: str,
    company_name: str,
    decision_cutoff: str,
    expected_trade_dates: Sequence[str],
) -> IfindNormalizedBatch:
    expected_dates = tuple(str(value) for value in expected_trade_dates)
    if len(expected_dates) != IFIND_S2_DAILY_SESSION_COUNT or len(
        set(expected_dates)
    ) != len(expected_dates):
        raise IfindProviderError(
            "IFIND_MCP_S2_CALENDAR_INVALID",
            "S2 requires exactly 120 unique governed trading dates",
        )
    rows = _require_markdown_rows(
        staged, _MARKET_REQUIRED_COLUMNS, exact_rows=IFIND_S2_DAILY_SESSION_COUNT
    )
    for row in rows:
        _validate_identity(row, symbol, company_name)
        if _required_text(row, "复权方式").lower() not in {"前复权", "qfq"}:
            raise IfindProviderError(
                "IFIND_MCP_S2_ADJUSTMENT_MISMATCH",
                "S2 market rows must explicitly report qfq adjustment",
            )
        row["复权方式"] = IFIND_S2_ADJUSTMENT_MODE
    actual_dates = tuple(sorted(_required_text(row, "交易日期") for row in rows))
    if actual_dates != tuple(sorted(expected_dates)):
        raise IfindProviderError(
            "IFIND_MCP_S2_CALENDAR_MISMATCH",
            "S2 market rows do not exactly match the governed 120-session calendar",
        )
    available_values = {_required_text(row, "数据可用时间") for row in rows}
    if len(available_values) != 1:
        raise IfindProviderError(
            "IFIND_MCP_S2_AVAILABILITY_AMBIGUOUS",
            "S2 market batch requires one explicit provider availability timestamp",
        )
    return normalize_ifind_payload(
        module_id="daily_market_and_calendar",
        payload={"tables": [_columnar_table(rows)]},
        field_mapping={
            "证券代码": "symbol",
            "交易日期": "trade_date",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
            "成交额": "amount",
            "换手率": "turnover",
            "复权方式": "adjustment_mode",
        },
        source_function="get_stock_performance",
        available_at=next(iter(available_values)),
        decision_cutoff=decision_cutoff,
        request_descriptor={
            "stage_id": IFIND_S2_STAGE_ID,
            "tool_name": "get_stock_performance",
            "symbol": symbol,
            "session_count": IFIND_S2_DAILY_SESSION_COUNT,
            "adjustment_mode": IFIND_S2_ADJUSTMENT_MODE,
        },
        quality_flags=("S2_TYPED_PROVIDER_SCHEMA", "GOVERNED_CALENDAR_ALIGNED"),
    )


def _validate_s1_status(status: Mapping[str, Any]) -> None:
    required = {
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
    if any(status.get(key) != value for key, value in required.items()):
        raise IfindProviderError(
            "IFIND_MCP_S2_PREREQUISITE_UNVERIFIED",
            "S2 requires the exact accepted non-canonical S1 status",
        )


def _require_markdown_rows(
    staged: Mapping[str, Any],
    required_columns: Sequence[str],
    *,
    exact_rows: int,
) -> list[dict[str, Any]]:
    if (
        staged.get("canonical_accepted") is not False
        or staged.get("staging_format") != "provider_markdown_tables_v1"
    ):
        raise IfindProviderError(
            "IFIND_MCP_S2_RESPONSE_SCHEMA_MISMATCH",
            "S2 accepts only bounded non-canonical provider Markdown staging",
        )
    tables = staged.get("tables")
    if not isinstance(tables, list):
        raise IfindProviderError(
            "IFIND_MCP_S2_RESPONSE_SCHEMA_MISMATCH", "S2 tables are missing"
        )
    matches = []
    required = set(required_columns)
    for table in tables:
        if not isinstance(table, Mapping) or not isinstance(table.get("columns"), list):
            continue
        columns = tuple(str(value) for value in table["columns"])
        if required.issubset(columns):
            matches.append(table)
    if len(matches) != 1 or not isinstance(matches[0].get("rows"), list):
        raise IfindProviderError(
            "IFIND_MCP_S2_RESPONSE_SCHEMA_MISMATCH",
            "S2 response must contain exactly one reviewed table",
        )
    rows = matches[0]["rows"]
    if len(rows) != exact_rows or any(not isinstance(row, Mapping) for row in rows):
        raise IfindProviderError(
            "IFIND_MCP_S2_ROW_COUNT_MISMATCH",
            "S2 response row count does not match the fixed request contract",
        )
    return [dict(row) for row in rows]


def _validate_identity(row: Mapping[str, Any], symbol: str, company_name: str) -> None:
    if symbol not in IFIND_DUAL_STOCK_SYMBOLS:
        raise IfindProviderError(
            "IFIND_MCP_DATA_SCOPE_VIOLATION", "S2 symbol is outside the fixed cohort"
        )
    if (
        _required_text(row, "证券代码").upper() != symbol
        or _required_text(row, "证券简称") != company_name
    ):
        raise IfindProviderError(
            "IFIND_MCP_S2_IDENTITY_MISMATCH",
            "S2 provider identity does not match the fixed symbol and company",
        )


def _required_text(row: Mapping[str, Any], field: str) -> str:
    value = row.get(field)
    if not isinstance(value, (str, int, float)) or isinstance(value, bool):
        raise IfindProviderError(
            "IFIND_MCP_S2_RESPONSE_SCHEMA_MISMATCH",
            f"S2 field {field} must be a scalar value",
        )
    text = str(value).strip()
    if not text:
        raise IfindProviderError(
            "IFIND_MCP_S2_RESPONSE_SCHEMA_MISMATCH",
            f"S2 field {field} must not be empty",
        )
    return text


def _columnar_table(rows: Sequence[Mapping[str, Any]]) -> Mapping[str, list[Any]]:
    columns = tuple(str(key) for key in rows[0])
    if any(tuple(str(key) for key in row) != columns for row in rows):
        raise IfindProviderError(
            "IFIND_MCP_S2_RESPONSE_SCHEMA_MISMATCH",
            "S2 rows must expose one stable column order and schema",
        )
    return {column: [row.get(column) for row in rows] for column in columns}


def _validate_cutoff_date(value: str) -> str:
    text = str(value).strip()
    parts = text.split("-")
    if len(parts) != 3 or tuple(len(part) for part in parts) != (4, 2, 2):
        raise IfindProviderError(
            "IFIND_MCP_S2_CUTOFF_INVALID", "S2 cutoff must use YYYY-MM-DD"
        )
    try:
        year, month, day = (int(part) for part in parts)
        from datetime import date

        return date(year, month, day).isoformat()
    except ValueError as exc:
        raise IfindProviderError(
            "IFIND_MCP_S2_CUTOFF_INVALID", "S2 cutoff is not a calendar date"
        ) from exc


def _s2_contract_error() -> IfindProviderError:
    return IfindProviderError(
        "IFIND_MCP_S2_CONTRACT_INVALID",
        "committed S2 call-plan fields are inconsistent",
    )

from __future__ import annotations

import json
import hashlib
import math
import os
import re
import shutil
import socket
import ssl
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPSHandler, ProxyHandler, Request, build_opener

from ashare_premarket.providers.ifind_http import (
    IFIND_DATA_MODULES,
    IFIND_NETWORK_ENV,
    IFIND_PROVIDER_ENV,
    IfindNoRedirectHandler,
    IfindProviderError,
)


IFIND_MCP_BASE_URL = "https://api-mcp.51ifind.com:8643/ds-mcp-servers"
IFIND_MCP_HOST = "api-mcp.51ifind.com"
IFIND_MCP_PORT = 8643
IFIND_MCP_PROTOCOL_VERSION = "2025-03-26"
IFIND_MCP_PROVIDER_ENV = "ASHARE_ALLOW_IFIND_MCP"
IFIND_MCP_DATA_CALL_ENV = "ASHARE_ALLOW_IFIND_MCP_DATA_CALLS"
IFIND_MCP_API_KEY_ENV = "IFIND_MCP_API_KEY"
IFIND_MCP_KEYCHAIN_ACCOUNT = "ifind"
IFIND_MCP_KEYCHAIN_SERVER = "mcp.51ifind.com"
IFIND_MCP_KEYCHAIN_SERVICE = "AsharePremarket-iFinD-API-Key"
IFIND_MCP_LOCAL_PROBE_STATUS = "outputs/local/ifind/mcp_probe_status.json"

IFIND_MCP_SERVERS = {
    "stock": "hexin-ifind-ds-stock-mcp",
    "fund": "hexin-ifind-ds-fund-mcp",
    "edb": "hexin-ifind-ds-edb-mcp",
    "news": "hexin-ifind-ds-news-mcp",
    "bond": "hexin-ifind-ds-bond-mcp",
    "global_stock": "hexin-ifind-ds-global-stock-mcp",
    "index": "hexin-ifind-ds-index-mcp",
}

IFIND_MCP_TOOL_CATALOG = {
    "stock": (
        "search_stocks",
        "get_stock_summary",
        "get_stock_info",
        "get_stock_performance",
        "get_stock_shareholders",
        "get_stock_financials",
        "get_risk_indicators",
        "get_stock_events",
        "get_esg_data",
        "stock_highfreq_quotes",
    ),
    "fund": (
        "search_funds",
        "get_fund_profile",
        "get_fund_market_performance",
        "get_fund_ownership",
        "get_fund_portfolio",
        "get_fund_financials",
        "get_fund_company_info",
        "fund_highfreq_quotes",
    ),
    "edb": ("search_edb", "get_edb_data"),
    "news": ("search_news", "search_notice", "search_trending_news"),
    "bond": (
        "bond_basic_info",
        "bond_market_data",
        "bond_financial_data",
        "bond_special_data",
        "bond_highfreq_quotes",
    ),
    "global_stock": (
        "search_global_stocks",
        "global_stock_profile",
        "global_stock_quotes",
        "global_stock_financial",
        "global_stock_events",
    ),
    "index": ("index_data", "sector_data", "index_highfreq_quotes"),
}

# The supplier's reviewed full catalog includes enterprise-only capabilities.
# The purchased personal/trial channel is intentionally represented as a
# separate active entitlement profile so a documented plan limitation is not
# confused with schema drift or a provider outage.
IFIND_MCP_ENTITLEMENT_PROFILE = "personal_trial_non_enterprise"
IFIND_MCP_PLAN_UNAVAILABLE_TOOLS = {"edb": ("search_edb",)}
IFIND_MCP_ENTITLED_TOOL_CATALOG = {
    server_type: tuple(
        tool_name
        for tool_name in tool_names
        if tool_name not in IFIND_MCP_PLAN_UNAVAILABLE_TOOLS.get(server_type, ())
    )
    for server_type, tool_names in IFIND_MCP_TOOL_CATALOG.items()
}

IFIND_MCP_EXPECTED_INPUT_FIELDS = {
    tool_name: (
        ("symbols", "indicators", "data_mode")
        if tool_name
        in {
            "stock_highfreq_quotes",
            "fund_highfreq_quotes",
            "bond_highfreq_quotes",
            "index_highfreq_quotes",
        }
        else (
            ("query", "market")
            if tool_name == "search_global_stocks"
            else ("size",) if tool_name == "search_trending_news" else ("query",)
        )
    )
    for tools in IFIND_MCP_TOOL_CATALOG.values()
    for tool_name in tools
}

IFIND_MCP_SERVICE_CATALOG = tuple(
    {
        "server_type": server_type,
        "server_id": server_id,
        "endpoint_path": f"/ds-mcp-servers/{server_id}",
        "reviewed_tool_count": len(IFIND_MCP_TOOL_CATALOG[server_type]),
        "expected_tool_count": len(IFIND_MCP_ENTITLED_TOOL_CATALOG[server_type]),
        "unavailable_by_plan": ";".join(
            IFIND_MCP_PLAN_UNAVAILABLE_TOOLS.get(server_type, ())
        ),
        "implementation_state": "contract_ready_live_handshake_pending",
    }
    for server_type, server_id in IFIND_MCP_SERVERS.items()
)

_MCP_MODULE_BINDINGS = {
    "security_master": {
        "mcp_services": "stock",
        "mcp_tools": "get_stock_info;get_stock_shareholders;get_stock_events",
        "known_gap": "live_field_schema_and_effective_date_validation_pending",
    },
    "daily_market_and_calendar": {
        "mcp_services": "stock;index",
        "mcp_tools": "get_stock_performance;stock_highfreq_quotes;index_data",
        "known_gap": "trade_calendar_remains_existing_governed_calendar_or_optional_quantapi",
    },
    "pit_fundamentals_and_valuation": {
        "mcp_services": "stock",
        "mcp_tools": "get_stock_financials;get_stock_summary",
        "known_gap": "announcement_revision_and_available_at_mapping_pending",
    },
    "industry_and_constituents": {
        "mcp_services": "stock;index",
        "mcp_tools": "search_stocks;sector_data",
        "known_gap": "historical_membership_effective_period_mapping_pending",
    },
    "corporate_events_and_announcements": {
        "mcp_services": "stock;news",
        "mcp_tools": "get_stock_events;search_notice",
        "known_gap": "publication_timestamp_and_metadata_schema_validation_pending",
    },
    "macro_and_edb": {
        "mcp_services": "edb",
        "mcp_tools": "search_edb;get_edb_data",
        "known_gap": "release_and_revision_timestamps_mapping_pending",
    },
    "market_structure_crosscheck": {
        "mcp_services": "stock;index",
        "mcp_tools": "get_risk_indicators;get_stock_performance;index_data;sector_data",
        "known_gap": "vendor_definition_and_cross_provider_reconciliation_pending",
    },
}

IFIND_MCP_DATA_MODULES = tuple(
    {
        **module,
        **_MCP_MODULE_BINDINGS[module["module_id"]],
        "interface_channel": "ifind_mcp_api_key",
        "implementation_state": "mcp_contract_ready_live_schema_validation_pending",
    }
    for module in IFIND_DATA_MODULES
)

_HIGH_FREQUENCY_TOOLS = {
    "stock_highfreq_quotes",
    "fund_highfreq_quotes",
    "bond_highfreq_quotes",
    "index_highfreq_quotes",
}
_NEWS_SEARCH_TOOLS = {"search_news", "search_notice"}
_MAX_API_KEY_BYTES = 8 * 1024
_MAX_REQUEST_BYTES = 64 * 1024
_MAX_RESPONSE_BYTES = 8 * 1024 * 1024
_MAX_QUERY_CHARACTERS = 1_000
_MAX_TOOL_COUNT = 128
_MAX_TOOL_SCHEMA_BYTES = 512 * 1024
_MAX_PROVIDER_MARKDOWN_BYTES = 512 * 1024
_MAX_PROVIDER_MARKDOWN_LINES = 2_048
_MAX_PROVIDER_TABLES = 32
_MAX_PROVIDER_TABLE_COLUMNS = 64
_MAX_PROVIDER_TABLE_ROWS = 1_000
_MAX_JSON_DEPTH = 12
_MAX_JSON_ITEMS = 4_096
_MAX_NEWS_RESULTS = 20
_MAX_DATE_SPAN_DAYS = 3_660
_ALLOWED_INTERVALS = {1, 3, 5, 10, 15, 30, 60}
_PILOT_HIGHFREQ_INDICATORS = {"最新价"}
_BLOCKED_KEYS = {"__proto__", "prototype", "constructor"}
_API_KEY_RE = re.compile(r"^[A-Za-z0-9._~+/=-]+$")
_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9._~+:/=-]{1,1024}$")
_TOOL_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,127}$")
_COHORT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,127}$")
_CANONICAL_SYMBOL_RE = re.compile(r"^[0-9]{6}\.(?:SH|SZ)$")
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")
_COMPANY_NAME_RE = re.compile(r"^[A-Za-z0-9\u3400-\u9fff（）()· -]{1,64}$")
_RESPONSE_SYMBOL_KEYS = {
    "symbol",
    "symbols",
    "thscode",
    "ths_code",
    "stock_code",
    "security_code",
    "证券代码",
    "股票代码",
}

IFIND_MCP_RESPONSE_DIAGNOSTIC_VERSION = "ifind_response_shape_v1"
_RESPONSE_FAILURE_STAGES = {
    "jsonrpc_contract",
    "mcp_result_extraction",
    "provider_envelope",
    "provider_markdown",
    "s2_table_selection",
    "s2_semantic_validation",
    "normalization",
}
_RESPONSE_FAILURE_REASONS = {
    "jsonrpc_response_not_unique",
    "jsonrpc_result_not_object",
    "json_shape_invalid",
    "content_item_count_invalid",
    "content_item_type_invalid",
    "content_text_not_json_object",
    "structured_content_conflict",
    "provider_unsuccessful",
    "provider_data_not_string",
    "markdown_control_characters",
    "markdown_invalid_header",
    "markdown_row_width_mismatch",
    "markdown_empty_table",
    "markdown_unsafe_cell",
    "markdown_no_table",
    "staging_format_mismatch",
    "required_columns_missing",
    "matching_table_ambiguous",
    "row_count_mismatch",
    "identity_mismatch",
    "provider_availability_missing",
    "qfq_mismatch",
    "calendar_mismatch",
    "unit_mismatch",
    "pit_violation",
}
_RESULT_VARIANTS = {
    "structured_content",
    "single_json_text",
    "invalid",
    "unknown",
}
_PROVIDER_ENVELOPE_VARIANTS = {
    "code_data_markdown",
    "structured_json",
    "invalid",
    "unknown",
}
_PAYLOAD_SIZE_BUCKETS = {
    "0",
    "1_4k",
    "4_64k",
    "64_512k",
    "over_limit",
    "unknown",
}

_PILOT_STOCK_QUERY_TEMPLATES = {
    # The supplier's documented/portal-verified summary behavior is keyed by
    # the company name alone. S1 is an identity gate, not a valuation/PIT data
    # request; adding those concepts caused a different unreviewed response
    # shape. The returned symbol and company name remain independently checked.
    "get_stock_summary": "{company_name}",
    "get_stock_info": (
        "返回{company_name}（{symbol}）的证券代码、证券简称、交易所、上市日期、"
        "交易状态、ST状态、总股本、流通股本和行业；仅返回结构化字段。"
    ),
    "get_stock_performance": (
        "返回{company_name}（{symbol}）最近120个交易日的前复权日线行情，包含日期、"
        "前收盘、开盘、最高、最低、收盘、成交量、成交额和换手率；仅返回结构化字段。"
    ),
    "get_stock_shareholders": (
        "返回{company_name}（{symbol}）最新可得的股东与股本结构、报告期和披露时间；"
        "仅返回结构化字段。"
    ),
    "get_stock_financials": (
        "返回{company_name}（{symbol}）最近五个已披露报告期的主要财务、估值、报告期、"
        "公告日和修订时间；仅返回结构化字段。"
    ),
    "get_risk_indicators": (
        "返回{company_name}（{symbol}）最新可得的风险与市场结构指标、指标口径和数据时点；"
        "仅返回结构化字段。"
    ),
    "get_stock_events": (
        "返回{company_name}（{symbol}）最近一年的公司事件和公告元数据，包含事件类型、"
        "标题、发布时间和报告期；不返回公告全文，仅返回结构化字段。"
    ),
    "get_esg_data": (
        "返回{company_name}（{symbol}）最新可得的ESG结构化指标、口径和披露时间；"
        "仅返回结构化字段。"
    ),
}

IFIND_MCP_S2_QUERY_TEMPLATES = {
    "get_stock_info": (
        "返回{company_name}（{symbol}）的证券代码、证券简称、交易所、上市日期、"
        "交易状态、ST状态、总股本、总股本单位、流通股本、流通股本单位、所属行业、"
        "数据日期和数据可用时间；"
        "数据可用时间必须包含时区；仅返回结构化字段。"
    ),
    "get_stock_performance": (
        "返回{company_name}（{symbol}）截至{cutoff_date}最近120个已完成交易日的"
        "前复权日线行情，包含证券代码、证券简称、交易日期、开盘、最高、最低、"
        "收盘、成交量、成交量单位、成交额、成交额单位、换手率、换手率口径、"
        "复权方式和数据可用时间；数据可用时间必须"
        "包含时区；不得返回未来日期；仅返回结构化字段。"
    ),
}


@dataclass(frozen=True, repr=False)
class IfindMcpApiKey:
    value: str
    source: str = "in_memory"

    def __post_init__(self) -> None:
        _validate_api_key(self.value)

    def __repr__(self) -> str:
        return f"IfindMcpApiKey(configured={bool(self.value)}, source={self.source!r}, value_exposed=False)"

    @classmethod
    def from_environment(
        cls, environ: Optional[Mapping[str, str]] = None
    ) -> "IfindMcpApiKey":
        source = environ if environ is not None else os.environ
        value = str(source.get(IFIND_MCP_API_KEY_ENV, ""))
        if not value:
            raise IfindProviderError(
                "IFIND_MCP_CREDENTIAL_MISSING",
                f"environment credential {IFIND_MCP_API_KEY_ENV} is not configured",
            )
        return cls(value=value, source="environment")


class IfindMcpKeychainLoader:
    """Load a dedicated Keychain item into memory without rendering its value."""

    def __init__(
        self,
        account: str = IFIND_MCP_KEYCHAIN_ACCOUNT,
        server: str = IFIND_MCP_KEYCHAIN_SERVER,
        service: str = IFIND_MCP_KEYCHAIN_SERVICE,
        runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    ) -> None:
        self.account = account
        self.server = server
        self.service = service
        self._runner = runner

    def __repr__(self) -> str:
        return (
            "IfindMcpKeychainLoader("
            f"account={self.account!r}, service={self.service!r}, "
            f"server={self.server!r}, credential_exposed=False)"
        )

    def load(self) -> IfindMcpApiKey:
        security_command = _trusted_security_command()
        if security_command is None:
            raise IfindProviderError(
                "IFIND_MCP_KEYCHAIN_UNAVAILABLE",
                "macOS Keychain command is unavailable on this runtime",
            )
        commands = (
            (
                "macos_keychain_generic_password",
                [
                    security_command,
                    "find-generic-password",
                    "-a",
                    self.account,
                    "-s",
                    self.service,
                    "-w",
                ],
            ),
            (
                "macos_keychain_internet_password",
                [
                    security_command,
                    "find-internet-password",
                    "-a",
                    self.account,
                    "-s",
                    self.server,
                    "-w",
                ],
            ),
        )
        for credential_source, command in commands:
            try:
                result = self._runner(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                    timeout=45,
                )
            except subprocess.TimeoutExpired as exc:
                raise IfindProviderError(
                    "IFIND_MCP_KEYCHAIN_TIMEOUT",
                    "Keychain authorization did not complete within the approved timeout",
                ) from exc
            except OSError as exc:
                raise IfindProviderError(
                    "IFIND_MCP_KEYCHAIN_UNAVAILABLE",
                    "Keychain credential lookup could not be started",
                ) from exc
            if int(result.returncode) == 0:
                return self._credential_from_stdout(result.stdout, credential_source)
        raise IfindProviderError(
            "IFIND_MCP_KEYCHAIN_LOOKUP_FAILED",
            "Keychain did not return the dedicated iFinD credential",
        )

    @staticmethod
    def _credential_from_stdout(
        raw_stdout: object, credential_source: str
    ) -> IfindMcpApiKey:
        raw = bytes(raw_stdout or b"")
        if len(raw) > _MAX_API_KEY_BYTES + 2:
            raise IfindProviderError(
                "IFIND_MCP_CREDENTIAL_FORMAT_INVALID",
                "Keychain credential exceeds the approved size bound",
            )
        try:
            value = raw.decode("ascii").rstrip("\r\n")
        except UnicodeDecodeError as exc:
            raise IfindProviderError(
                "IFIND_MCP_CREDENTIAL_FORMAT_INVALID",
                "Keychain credential is not valid header-safe ASCII",
            ) from exc
        return IfindMcpApiKey(value=value, source=credential_source)


@dataclass(frozen=True)
class IfindMcpNetworkPolicy:
    network_opt_in: bool
    provider_opt_in: bool
    mcp_opt_in: bool
    data_call_opt_in: bool = False

    @classmethod
    def from_environment(
        cls, environ: Optional[Mapping[str, str]] = None
    ) -> "IfindMcpNetworkPolicy":
        source = environ if environ is not None else os.environ
        return cls(
            network_opt_in=_env_enabled(source.get(IFIND_NETWORK_ENV)),
            provider_opt_in=_env_enabled(source.get(IFIND_PROVIDER_ENV)),
            mcp_opt_in=_env_enabled(source.get(IFIND_MCP_PROVIDER_ENV)),
            data_call_opt_in=_env_enabled(source.get(IFIND_MCP_DATA_CALL_ENV)),
        )

    @property
    def live_access_allowed(self) -> bool:
        return self.network_opt_in and self.provider_opt_in and self.mcp_opt_in

    def require_live_access(self) -> None:
        if not self.network_opt_in:
            raise IfindProviderError(
                "IFIND_NETWORK_DISABLED_BY_POLICY",
                f"live access requires {IFIND_NETWORK_ENV}=1",
            )
        if not self.provider_opt_in:
            raise IfindProviderError(
                "IFIND_PROVIDER_DISABLED_BY_POLICY",
                f"live access requires {IFIND_PROVIDER_ENV}=1",
            )
        if not self.mcp_opt_in:
            raise IfindProviderError(
                "IFIND_MCP_DISABLED_BY_POLICY",
                f"live MCP access requires {IFIND_MCP_PROVIDER_ENV}=1",
            )

    def require_data_call_access(self) -> None:
        self.require_live_access()
        if not self.data_call_opt_in:
            raise IfindProviderError(
                "IFIND_MCP_DATA_CALLS_DISABLED_BY_POLICY",
                f"MCP financial-data calls require {IFIND_MCP_DATA_CALL_ENV}=1",
            )


@dataclass(frozen=True)
class IfindMcpCallScope:
    """Explicit cohort boundary required before any supplier financial-data call."""

    cohort_id: str
    allowed_symbols: Tuple[str, ...]
    company_names: Tuple[Tuple[str, str], ...]
    allowed_services: Tuple[str, ...]
    allowed_tools: Tuple[str, ...]

    def __post_init__(self) -> None:
        if not _COHORT_ID_RE.fullmatch(self.cohort_id):
            raise ValueError("cohort_id is outside the approved syntax")
        if not self.allowed_symbols or len(self.allowed_symbols) > 10:
            raise ValueError("allowed_symbols must contain between 1 and 10 symbols")
        if len(set(self.allowed_symbols)) != len(self.allowed_symbols):
            raise ValueError("allowed_symbols contains duplicates")
        if any(
            not _CANONICAL_SYMBOL_RE.fullmatch(value) for value in self.allowed_symbols
        ):
            raise ValueError(
                "allowed_symbols must use canonical exchange-suffixed symbols"
            )
        names = dict(self.company_names)
        if len(names) != len(self.company_names) or set(names) != set(
            self.allowed_symbols
        ):
            raise ValueError("company_names must map every allowed symbol exactly once")
        if any(not _COMPANY_NAME_RE.fullmatch(value) for value in names.values()):
            raise ValueError("company_names contains an unsafe company name")
        if not self.allowed_services or any(
            value not in IFIND_MCP_SERVERS for value in self.allowed_services
        ):
            raise ValueError("allowed_services contains an unapproved MCP service")
        approved_tools = {
            tool
            for service in self.allowed_services
            for tool in IFIND_MCP_TOOL_CATALOG[service]
        }
        if not self.allowed_tools or any(
            value not in approved_tools for value in self.allowed_tools
        ):
            raise ValueError("allowed_tools contains an unapproved MCP tool")

    def require(
        self, server_type: str, tool_name: str, scope_symbols: Sequence[str]
    ) -> None:
        if (
            server_type not in self.allowed_services
            or tool_name not in self.allowed_tools
        ):
            raise IfindProviderError(
                "IFIND_MCP_DATA_SCOPE_VIOLATION",
                "MCP data call is outside the accepted service and tool scope",
            )
        requested = tuple(scope_symbols)
        if not requested or len(requested) > len(self.allowed_symbols):
            raise IfindProviderError(
                "IFIND_MCP_DATA_SCOPE_VIOLATION",
                "MCP data call requires a bounded non-empty cohort symbol scope",
            )
        if len(set(requested)) != len(requested) or any(
            value not in self.allowed_symbols for value in requested
        ):
            raise IfindProviderError(
                "IFIND_MCP_DATA_SCOPE_VIOLATION",
                "MCP data call requested a symbol outside the accepted cohort",
            )

    def company_name(self, symbol: str) -> str:
        if symbol not in self.allowed_symbols:
            raise IfindProviderError(
                "IFIND_MCP_DATA_SCOPE_VIOLATION",
                "MCP data call requested a symbol outside the accepted cohort",
            )
        return dict(self.company_names)[symbol]


@dataclass(frozen=True, repr=False)
class IfindMcpHttpResponse:
    status: int
    headers: Mapping[str, str]
    body: bytes
    body_truncated: bool = False

    def __repr__(self) -> str:
        return (
            "IfindMcpHttpResponse("
            f"status={self.status}, body_truncated={self.body_truncated}, "
            "headers_exposed=False, body_exposed=False)"
        )


class IfindMcpUrllibTransport:
    """Verified HTTPS transport with no proxy inheritance or redirects."""

    def __init__(self) -> None:
        self._proxy_handler = ProxyHandler({})
        self._opener = build_opener(
            self._proxy_handler,
            HTTPSHandler(context=ssl.create_default_context()),
            IfindNoRedirectHandler(),
        )

    def post_json(
        self,
        url: str,
        headers: Mapping[str, str],
        payload: Mapping[str, Any],
        timeout_seconds: float,
    ) -> IfindMcpHttpResponse:
        _validate_mcp_url(url)
        try:
            raw_request = json.dumps(
                payload,
                ensure_ascii=False,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise IfindProviderError(
                "IFIND_MCP_REQUEST_INVALID",
                "MCP request is not valid bounded JSON",
            ) from exc
        if len(raw_request) > _MAX_REQUEST_BYTES:
            raise IfindProviderError(
                "IFIND_MCP_REQUEST_TOO_LARGE",
                "MCP request exceeds the approved payload bound",
            )
        try:
            request = Request(
                url, data=raw_request, headers=dict(headers), method="POST"
            )
            with self._opener.open(request, timeout=timeout_seconds) as response:
                body, truncated = _read_bounded(response, truncate=False)
                return IfindMcpHttpResponse(
                    status=int(getattr(response, "status", 200)),
                    headers=_response_headers(getattr(response, "headers", {})),
                    body=body,
                    body_truncated=truncated,
                )
        except HTTPError as exc:
            body, truncated = _read_bounded(exc, truncate=True)
            return IfindMcpHttpResponse(
                status=int(exc.code),
                headers=_response_headers(getattr(exc, "headers", {})),
                body=body,
                body_truncated=truncated,
            )
        except socket.timeout as exc:
            raise IfindProviderError(
                "IFIND_MCP_NETWORK_TIMEOUT", "MCP request timed out"
            ) from exc
        except ssl.SSLError as exc:
            raise IfindProviderError(
                "IFIND_MCP_TLS_FAILURE", "MCP TLS validation failed"
            ) from exc
        except URLError as exc:
            raise IfindProviderError(
                "IFIND_MCP_NETWORK_FAILURE", "MCP network request failed"
            ) from exc
        except (ValueError, UnicodeEncodeError):
            raise IfindProviderError(
                "IFIND_MCP_CREDENTIAL_FORMAT_INVALID",
                "MCP credential or session value is not safe for an HTTP header",
            ) from None


McpTransport = Callable[
    [str, Mapping[str, str], Mapping[str, Any], float],
    IfindMcpHttpResponse,
]


class IfindMcpRateLimiter:
    def __init__(
        self,
        minimum_interval_seconds: float = 0.5,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        if minimum_interval_seconds < 0 or minimum_interval_seconds > 10:
            raise ValueError("minimum interval is outside the approved bound")
        self.minimum_interval_seconds = minimum_interval_seconds
        self._clock = clock
        self._sleeper = sleeper
        self._last_request_at: Optional[float] = None

    def wait(self) -> None:
        now = self._clock()
        if self._last_request_at is not None:
            remaining = self.minimum_interval_seconds - (now - self._last_request_at)
            if remaining > 0:
                self._sleeper(remaining)
                now = self._clock()
        self._last_request_at = now


class IfindMcpClient:
    def __init__(
        self,
        api_key: IfindMcpApiKey,
        policy: Optional[IfindMcpNetworkPolicy] = None,
        transport: Optional[McpTransport] = None,
        rate_limiter: Optional[IfindMcpRateLimiter] = None,
        call_scope: Optional[IfindMcpCallScope] = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        if timeout_seconds <= 0 or timeout_seconds > 60:
            raise ValueError("timeout_seconds must be within (0, 60]")
        self.api_key = api_key
        self.policy = policy or IfindMcpNetworkPolicy.from_environment()
        self.transport = transport or IfindMcpUrllibTransport().post_json
        self.rate_limiter = rate_limiter or IfindMcpRateLimiter()
        self.call_scope = call_scope
        self.timeout_seconds = timeout_seconds
        self._request_ids: dict[str, int] = {}
        self._sessions: dict[str, str] = {}
        self._tool_names: dict[str, Tuple[str, ...]] = {}
        self._tool_contracts: dict[str, Tuple[Mapping[str, Any], ...]] = {}

    def __repr__(self) -> str:
        return (
            "IfindMcpClient("
            f"api_key_configured={bool(self.api_key.value)}, "
            f"live_access_allowed={self.policy.live_access_allowed}, "
            f"data_call_scope_configured={self.call_scope is not None}, "
            f"timeout_seconds={self.timeout_seconds}, credential_exposed=False)"
        )

    @classmethod
    def from_keychain(
        cls,
        policy: Optional[IfindMcpNetworkPolicy] = None,
        loader: Optional[IfindMcpKeychainLoader] = None,
        **kwargs: Any,
    ) -> "IfindMcpClient":
        credential = (loader or IfindMcpKeychainLoader()).load()
        return cls(api_key=credential, policy=policy, **kwargs)

    def initialize(self, server_type: str) -> Mapping[str, Any]:
        self._require_server(server_type)
        if server_type in self._sessions:
            return {
                "protocolVersion": IFIND_MCP_PROTOCOL_VERSION,
                "session_reused": True,
            }
        request_id = self._next_id(server_type)
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": IFIND_MCP_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "http-client", "version": "1.0.0"},
            },
        }
        message, response = self._rpc(
            server_type,
            payload,
            request_id=request_id,
            include_session=False,
        )
        result = _require_rpc_result(message, "initialize")
        protocol = result.get("protocolVersion")
        if protocol != IFIND_MCP_PROTOCOL_VERSION:
            raise IfindProviderError(
                "IFIND_MCP_PROTOCOL_MISMATCH",
                "MCP server did not negotiate the approved protocol version",
            )
        session_id = response.headers.get("mcp-session-id", "")
        _validate_session_id(session_id)
        self._sessions[server_type] = session_id
        notification = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        self._rpc(
            server_type,
            notification,
            request_id=None,
            include_session=True,
            allow_empty=True,
        )
        return dict(result)

    def list_tools(self, server_type: str) -> Tuple[str, ...]:
        self._require_server(server_type)
        if server_type in self._tool_names:
            return self._tool_names[server_type]
        self.initialize(server_type)
        request_id = self._next_id(server_type)
        message, _response = self._rpc(
            server_type,
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "tools/list",
                "params": {},
            },
            request_id=request_id,
            include_session=True,
        )
        result = _require_rpc_result(message, "tools/list")
        tools = result.get("tools")
        if not isinstance(tools, list) or len(tools) > _MAX_TOOL_COUNT:
            raise IfindProviderError(
                "IFIND_MCP_TOOL_CATALOG_INVALID",
                "MCP tools/list returned an invalid or unbounded tool catalog",
            )
        names = []
        contracts = []
        schema_bytes = 0
        for tool in tools:
            if not isinstance(tool, Mapping):
                raise IfindProviderError(
                    "IFIND_MCP_TOOL_CATALOG_INVALID",
                    "MCP tool metadata must be JSON objects",
                )
            name = tool.get("name")
            if not isinstance(name, str) or not _TOOL_NAME_RE.fullmatch(name):
                raise IfindProviderError(
                    "IFIND_MCP_TOOL_CATALOG_INVALID",
                    "MCP tool name is outside the approved syntax",
                )
            schema = tool.get("inputSchema", {})
            _validate_json_shape(schema)
            schema_bytes += len(
                json.dumps(schema, ensure_ascii=False, sort_keys=True).encode("utf-8")
            )
            contracts.append(_tool_schema_contract(name, schema))
            names.append(name)
        if schema_bytes > _MAX_TOOL_SCHEMA_BYTES or len(names) != len(set(names)):
            raise IfindProviderError(
                "IFIND_MCP_TOOL_CATALOG_INVALID",
                "MCP tool catalog is duplicated or exceeds the approved schema bound",
            )
        resolved = tuple(sorted(names))
        self._tool_names[server_type] = resolved
        self._tool_contracts[server_type] = tuple(
            sorted(contracts, key=lambda item: str(item["tool_name"]))
        )
        return resolved

    def list_tool_contracts(self, server_type: str) -> Tuple[Mapping[str, Any], ...]:
        self.list_tools(server_type)
        return self._tool_contracts[server_type]

    def call_pilot_stock_tool(
        self,
        symbol: str,
        tool_name: str,
    ) -> Mapping[str, Any]:
        self.policy.require_data_call_access()
        if tool_name not in _PILOT_STOCK_QUERY_TEMPLATES:
            raise IfindProviderError(
                "IFIND_MCP_TOOL_NOT_ALLOWED",
                "requested stock tool has no approved fixed pilot query template",
            )
        scope = self._require_call_scope()
        company_name = scope.company_name(symbol)
        query = _PILOT_STOCK_QUERY_TEMPLATES[tool_name].format(
            company_name=company_name,
            symbol=symbol,
        )
        result = self._call_tool(
            "stock",
            tool_name,
            {"query": query},
            scope_symbols=(symbol,),
        )
        return stage_ifind_mcp_pilot_stock_result(
            result,
            (symbol,),
            expected_company_names=(
                {symbol: company_name} if tool_name == "get_stock_info" else None
            ),
        )

    def call_pilot_stock_highfreq(
        self,
        symbols: Sequence[str],
        indicators: Sequence[str],
        data_mode: str,
        interval: Optional[int] = None,
    ) -> Mapping[str, Any]:
        self.policy.require_data_call_access()
        scope_symbols = tuple(symbols)
        selected_indicators = tuple(indicators)
        if not selected_indicators or any(
            value not in _PILOT_HIGHFREQ_INDICATORS for value in selected_indicators
        ):
            raise IfindProviderError(
                "IFIND_MCP_ARGUMENTS_INVALID",
                "pilot high-frequency indicators are outside the reviewed allowlist",
            )
        arguments: dict[str, Any] = {
            "symbols": ",".join(scope_symbols),
            "indicators": ",".join(selected_indicators),
            "data_mode": data_mode,
        }
        if interval is not None:
            arguments["interval"] = interval
        result = self._call_tool(
            "stock",
            "stock_highfreq_quotes",
            arguments,
            scope_symbols=scope_symbols,
        )
        return stage_ifind_mcp_pilot_stock_result(result, scope_symbols)

    def call_s2_stock_tool(
        self,
        symbol: str,
        tool_name: str,
        cutoff_date: str,
    ) -> Mapping[str, Any]:
        """Call one exact S2 tool without accepting caller-provided query text."""

        self.policy.require_data_call_access()
        if tool_name not in IFIND_MCP_S2_QUERY_TEMPLATES:
            raise IfindProviderError(
                "IFIND_MCP_TOOL_NOT_ALLOWED",
                "requested stock tool is outside the fixed S2 contract",
            )
        try:
            normalized_cutoff = date.fromisoformat(cutoff_date).isoformat()
        except ValueError as exc:
            raise IfindProviderError(
                "IFIND_MCP_ARGUMENTS_INVALID",
                "S2 cutoff must be a valid ISO calendar date",
            ) from exc
        scope = self._require_call_scope()
        company_name = scope.company_name(symbol)
        query = IFIND_MCP_S2_QUERY_TEMPLATES[tool_name].format(
            company_name=company_name,
            symbol=symbol,
            cutoff_date=normalized_cutoff,
        )
        result = self._call_tool(
            "stock",
            tool_name,
            {"query": query},
            scope_symbols=(symbol,),
        )
        return stage_ifind_mcp_pilot_stock_result(
            result,
            (symbol,),
            expected_company_names=(
                {symbol: company_name} if tool_name == "get_stock_info" else None
            ),
        )

    def _call_tool(
        self,
        server_type: str,
        tool_name: str,
        arguments: Mapping[str, Any],
        *,
        scope_symbols: Sequence[str],
    ) -> Mapping[str, Any]:
        self.policy.require_data_call_access()
        self._require_call_scope().require(server_type, tool_name, scope_symbols)
        self._require_server(server_type)
        _validate_tool_arguments(server_type, tool_name, arguments)
        available = self.list_tools(server_type)
        if tool_name not in available:
            raise IfindProviderError(
                "IFIND_MCP_TOOL_NOT_ENTITLED",
                "requested MCP tool is not present in the live entitlement catalog",
            )
        request_id = self._next_id(server_type)
        message, _response = self._rpc(
            server_type,
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": dict(arguments)},
            },
            request_id=request_id,
            include_session=True,
        )
        result = _require_rpc_result(message, "tools/call")
        if result.get("isError") is True:
            raise IfindProviderError(
                "IFIND_MCP_TOOL_CALL_FAILED",
                "MCP tool returned an application-level error",
            )
        _validate_json_shape(result)
        return dict(result)

    def _require_call_scope(self) -> IfindMcpCallScope:
        if self.call_scope is None:
            raise IfindProviderError(
                "IFIND_MCP_DATA_SCOPE_REQUIRED",
                "MCP financial-data calls require an accepted cohort scope",
            )
        return self.call_scope

    def _rpc(
        self,
        server_type: str,
        payload: Mapping[str, Any],
        request_id: Optional[int],
        include_session: bool,
        allow_empty: bool = False,
    ) -> Tuple[Optional[Mapping[str, Any]], IfindMcpHttpResponse]:
        self.policy.require_live_access()
        _validate_api_key(self.api_key.value)
        url = _server_url(server_type)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": self.api_key.value,
        }
        if include_session:
            session_id = self._sessions.get(server_type, "")
            _validate_session_id(session_id)
            headers["Mcp-Session-Id"] = session_id
        self.rate_limiter.wait()
        response = self.transport(url, headers, payload, self.timeout_seconds)
        if response.status in {401, 403}:
            raise IfindProviderError(
                "IFIND_MCP_AUTH_OR_PERMISSION_DENIED",
                "MCP credential or service entitlement was rejected",
                response.status,
            )
        if response.status == 429:
            raise IfindProviderError(
                "IFIND_MCP_RATE_LIMITED",
                "MCP request was rate limited",
                response.status,
            )
        if response.status >= 500:
            raise IfindProviderError(
                "IFIND_MCP_PROVIDER_SERVER_ERROR",
                "MCP provider returned a server error",
                response.status,
            )
        if response.status < 200 or response.status >= 300:
            raise IfindProviderError(
                "IFIND_MCP_HTTP_ERROR",
                "MCP provider returned a non-success HTTP status",
                response.status,
            )
        if response.body_truncated:
            raise IfindProviderError(
                "IFIND_MCP_RESPONSE_TOO_LARGE",
                "MCP response exceeds the approved payload bound",
            )
        message = _parse_mcp_response(response, request_id, allow_empty=allow_empty)
        if message is not None and "error" in message:
            raise IfindProviderError(
                "IFIND_MCP_JSONRPC_ERROR",
                "MCP provider returned a JSON-RPC error",
                response.status,
            )
        return message, response

    def _next_id(self, server_type: str) -> int:
        next_value = self._request_ids.get(server_type, 0) + 1
        self._request_ids[server_type] = next_value
        return next_value

    @staticmethod
    def _require_server(server_type: str) -> None:
        if server_type not in IFIND_MCP_SERVERS:
            raise IfindProviderError(
                "IFIND_MCP_SERVER_NOT_ALLOWED",
                "MCP server type is outside the approved seven-service catalog",
            )


def sanitize_ifind_mcp_response_diagnostic(value: Any) -> Mapping[str, Any]:
    """Return a bounded metadata-only response diagnostic.

    Arbitrary provider values, messages, titles, column names, paths, and
    payload digests are intentionally not part of this contract.
    """

    source = value if isinstance(value, Mapping) else {}

    def enum(field: str, allowed: set[str], fallback: str) -> str:
        candidate = source.get(field)
        return (
            candidate
            if isinstance(candidate, str) and candidate in allowed
            else fallback
        )

    def count(field: str, maximum: int) -> int:
        candidate = source.get(field)
        if isinstance(candidate, bool) or not isinstance(candidate, int):
            return 0
        return min(max(candidate, 0), maximum)

    def digest(field: str) -> Optional[str]:
        candidate = source.get(field)
        if isinstance(candidate, str) and re.fullmatch(r"[0-9a-f]{64}", candidate):
            return candidate
        return None

    missing = source.get("missing_required_columns")
    fixed_missing = []
    if isinstance(missing, (list, tuple)):
        for field in missing:
            if (
                field
                in {
                    "证券代码",
                    "证券简称",
                    "数据日期",
                    "数据可用时间",
                    "上市日期",
                    "交易状态",
                    "总股本",
                    "总股本单位",
                    "流通股本",
                    "流通股本单位",
                    "交易日期",
                    "开盘",
                    "最高",
                    "最低",
                    "收盘",
                    "成交量",
                    "成交量单位",
                    "成交额",
                    "成交额单位",
                    "换手率",
                    "换手率口径",
                    "复权方式",
                }
                and field not in fixed_missing
            ):
                fixed_missing.append(field)
    mask = source.get("required_column_presence_mask")
    if not isinstance(mask, str) or not re.fullmatch(r"[01]{0,24}", mask):
        mask = ""
    diagnostic = {
        "diagnostic_version": IFIND_MCP_RESPONSE_DIAGNOSTIC_VERSION,
        "failure_stage": enum(
            "failure_stage", _RESPONSE_FAILURE_STAGES, "mcp_result_extraction"
        ),
        "failure_reason": enum(
            "failure_reason", _RESPONSE_FAILURE_REASONS, "json_shape_invalid"
        ),
        "mcp_result_variant": enum("mcp_result_variant", _RESULT_VARIANTS, "unknown"),
        "provider_envelope_variant": enum(
            "provider_envelope_variant", _PROVIDER_ENVELOPE_VARIANTS, "unknown"
        ),
        "payload_size_bucket": enum(
            "payload_size_bucket", _PAYLOAD_SIZE_BUCKETS, "unknown"
        ),
        "line_count": count("line_count", _MAX_PROVIDER_MARKDOWN_LINES + 1),
        "table_candidate_count": count(
            "table_candidate_count", _MAX_PROVIDER_TABLES + 1
        ),
        "parsed_table_count": count("parsed_table_count", _MAX_PROVIDER_TABLES),
        "selected_table_column_count": count(
            "selected_table_column_count", _MAX_PROVIDER_TABLE_COLUMNS
        ),
        "selected_table_row_count": count(
            "selected_table_row_count", _MAX_PROVIDER_TABLE_ROWS
        ),
        "required_column_presence_mask": mask,
        "missing_required_columns": fixed_missing,
        "ordered_column_shape_sha256": digest("ordered_column_shape_sha256"),
        "response_shape_sha256": digest("response_shape_sha256"),
        "quarantine_class": "METADATA_ONLY",
        "raw_payload_persisted": False,
    }
    fingerprint_input = {
        key: diagnostic[key]
        for key in (
            "diagnostic_version",
            "failure_stage",
            "failure_reason",
            "mcp_result_variant",
            "provider_envelope_variant",
            "payload_size_bucket",
            "line_count",
            "table_candidate_count",
            "parsed_table_count",
            "selected_table_column_count",
            "selected_table_row_count",
            "required_column_presence_mask",
            "ordered_column_shape_sha256",
        )
    }
    diagnostic["response_shape_sha256"] = hashlib.sha256(
        json.dumps(
            fingerprint_input,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return diagnostic


def _with_response_diagnostic(
    error: IfindProviderError,
    metadata: Mapping[str, Any],
) -> IfindProviderError:
    combined = {**getattr(error, "safe_metadata", {}), **metadata}
    return IfindProviderError(
        error.failure_code,
        error.safe_message,
        error.http_status,
        safe_metadata=sanitize_ifind_mcp_response_diagnostic(combined),
    )


def _response_contract_error(
    failure_code: str,
    safe_message: str,
    *,
    failure_stage: str,
    failure_reason: str,
    metadata: Optional[Mapping[str, Any]] = None,
) -> IfindProviderError:
    return IfindProviderError(
        failure_code,
        safe_message,
        safe_metadata=sanitize_ifind_mcp_response_diagnostic(
            {
                **(metadata or {}),
                "failure_stage": failure_stage,
                "failure_reason": failure_reason,
            }
        ),
    )


def _payload_size_bucket(size: int) -> str:
    if size <= 0:
        return "0"
    if size <= 4 * 1024:
        return "1_4k"
    if size <= 64 * 1024:
        return "4_64k"
    if size <= 512 * 1024:
        return "64_512k"
    return "over_limit"


def _result_shape_metadata(result: Mapping[str, Any]) -> dict[str, Any]:
    structured = result.get("structuredContent")
    content = result.get("content")
    if isinstance(structured, Mapping):
        variant = "structured_content"
    elif (
        isinstance(content, list)
        and len(content) == 1
        and isinstance(content[0], Mapping)
        and content[0].get("type") == "text"
        and isinstance(content[0].get("text"), str)
    ):
        variant = "single_json_text"
    else:
        variant = "invalid"
    return {
        "mcp_result_variant": variant,
        "provider_envelope_variant": "unknown",
        "payload_size_bucket": "unknown",
    }


def _markdown_shape_metadata(markdown: str) -> dict[str, Any]:
    encoded_size = len(markdown.encode("utf-8"))
    lines = markdown.splitlines()
    candidates = 0
    for index in range(max(len(lines) - 1, 0)):
        if _looks_like_markdown_table_row(lines[index]) and _is_markdown_separator_row(
            lines[index + 1]
        ):
            candidates += 1
    return {
        "provider_envelope_variant": "code_data_markdown",
        "payload_size_bucket": _payload_size_bucket(encoded_size),
        "line_count": min(len(lines), _MAX_PROVIDER_MARKDOWN_LINES + 1),
        "table_candidate_count": min(candidates, _MAX_PROVIDER_TABLES + 1),
    }


def _successful_markdown_shape(
    tables: Sequence[Mapping[str, Any]], metadata: Mapping[str, Any]
) -> Mapping[str, Any]:
    column_shapes = [
        tuple(str(column) for column in table.get("columns", []))
        for table in tables
        if isinstance(table, Mapping) and isinstance(table.get("columns"), list)
    ]
    row_counts = [
        len(table.get("rows", []))
        for table in tables
        if isinstance(table, Mapping) and isinstance(table.get("rows"), list)
    ]
    column_digest = hashlib.sha256(
        json.dumps(
            column_shapes,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    shape = {
        "diagnostic_version": IFIND_MCP_RESPONSE_DIAGNOSTIC_VERSION,
        "mcp_result_variant": metadata.get("mcp_result_variant", "unknown"),
        "provider_envelope_variant": "code_data_markdown",
        "payload_size_bucket": metadata.get("payload_size_bucket", "unknown"),
        "line_count": metadata.get("line_count", 0),
        "table_candidate_count": metadata.get("table_candidate_count", 0),
        "parsed_table_count": len(column_shapes),
        "selected_table_column_count": max(
            (len(columns) for columns in column_shapes), default=0
        ),
        "selected_table_row_count": max(row_counts, default=0),
        "ordered_column_shape_sha256": column_digest,
        "raw_payload_persisted": False,
    }
    shape["response_shape_sha256"] = hashlib.sha256(
        json.dumps(
            shape, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()
    return shape


def extract_ifind_mcp_structured_payload(
    result: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Accept only structured JSON data; free-form MCP text stays non-canonical."""

    metadata = _result_shape_metadata(result)
    if result.get("isError") is True:
        raise IfindProviderError(
            "IFIND_MCP_TOOL_CALL_FAILED", "MCP tool result is marked as an error"
        )
    structured = result.get("structuredContent")
    content = result.get("content")
    if isinstance(structured, Mapping) and content is not None and content != []:
        raise _response_contract_error(
            "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
            "MCP result ambiguously contains both structured and text content",
            failure_stage="mcp_result_extraction",
            failure_reason="structured_content_conflict",
            metadata=metadata,
        )
    if isinstance(structured, Mapping):
        try:
            _validate_json_shape(structured)
        except IfindProviderError as exc:
            raise _with_response_diagnostic(exc, metadata) from exc
        return dict(structured)
    if not isinstance(content, list) or len(content) != 1:
        raise _response_contract_error(
            "IFIND_MCP_UNSTRUCTURED_RESULT",
            "MCP result is not a single structured JSON payload",
            failure_stage="mcp_result_extraction",
            failure_reason="content_item_count_invalid",
            metadata=metadata,
        )
    item = content[0]
    if (
        not isinstance(item, Mapping)
        or item.get("type") != "text"
        or not isinstance(item.get("text"), str)
    ):
        raise _response_contract_error(
            "IFIND_MCP_UNSTRUCTURED_RESULT",
            "MCP content type is not approved for canonical data",
            failure_stage="mcp_result_extraction",
            failure_reason="content_item_type_invalid",
            metadata=metadata,
        )
    text = item["text"]
    if len(text.encode("utf-8")) > _MAX_RESPONSE_BYTES:
        raise _response_contract_error(
            "IFIND_MCP_RESPONSE_TOO_LARGE",
            "MCP structured text exceeds the approved bound",
            failure_stage="mcp_result_extraction",
            failure_reason="json_shape_invalid",
            metadata={**metadata, "payload_size_bucket": "over_limit"},
        )
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise _response_contract_error(
            "IFIND_MCP_UNSTRUCTURED_RESULT",
            "free-form MCP text is not accepted as canonical provider data",
            failure_stage="mcp_result_extraction",
            failure_reason="content_text_not_json_object",
            metadata={
                **metadata,
                "payload_size_bucket": _payload_size_bucket(len(text.encode("utf-8"))),
            },
        ) from exc
    if not isinstance(parsed, Mapping):
        raise _response_contract_error(
            "IFIND_MCP_UNSTRUCTURED_RESULT",
            "MCP JSON result must be an object",
            failure_stage="mcp_result_extraction",
            failure_reason="content_text_not_json_object",
            metadata=metadata,
        )
    try:
        _validate_json_shape(parsed)
    except IfindProviderError as exc:
        raise _with_response_diagnostic(exc, metadata) from exc
    return dict(parsed)


def stage_ifind_mcp_pilot_stock_result(
    result: Mapping[str, Any],
    expected_symbols: Sequence[str],
    *,
    expected_company_names: Optional[Mapping[str, str]] = None,
) -> Mapping[str, Any]:
    """Convert one untrusted MCP stock result into bounded, non-canonical staging rows."""

    result_metadata = _result_shape_metadata(result)
    try:
        payload = extract_ifind_mcp_structured_payload(result)
    except IfindProviderError as exc:
        raise _with_response_diagnostic(exc, result_metadata) from exc
    if "code" in payload or "data" in payload:
        if payload.get("code") not in {1, "1"}:
            raise _response_contract_error(
                "IFIND_MCP_PROVIDER_RESPONSE_ERROR",
                "MCP stock provider envelope did not report success",
                failure_stage="provider_envelope",
                failure_reason="provider_unsuccessful",
                metadata={
                    **result_metadata,
                    "provider_envelope_variant": "invalid",
                },
            )
        if not isinstance(payload.get("data"), str):
            raise _response_contract_error(
                "IFIND_MCP_PROVIDER_RESPONSE_ERROR",
                "MCP stock provider data is not a bounded text payload",
                failure_stage="provider_envelope",
                failure_reason="provider_data_not_string",
                metadata={
                    **result_metadata,
                    "provider_envelope_variant": "invalid",
                },
            )
        markdown = str(payload["data"])
        markdown_metadata = {
            **result_metadata,
            **_markdown_shape_metadata(markdown),
        }
        try:
            tables = parse_ifind_mcp_provider_markdown_tables(markdown)
        except IfindProviderError as exc:
            raise _with_response_diagnostic(exc, markdown_metadata) from exc
        corrections: list[str] = []
        if expected_company_names is not None:
            tables, corrections = _normalize_ifind_mcp_summary_identity_tables(
                tables,
                expected_symbols,
                expected_company_names,
            )
        staged: dict[str, Any] = {
            "staging_format": "provider_markdown_tables_v1",
            "provider_success": True,
            "canonical_accepted": False,
            "tables": tables,
            "semantic_corrections": corrections,
            "response_shape": _successful_markdown_shape(tables, markdown_metadata),
        }
    else:
        staged = {
            "staging_format": "structured_json_v1",
            "provider_success": True,
            "canonical_accepted": False,
            "payload": dict(payload),
        }
    validate_ifind_mcp_pilot_response_scope(staged, expected_symbols)
    return staged


def _normalize_ifind_mcp_summary_identity_tables(
    tables: Sequence[Mapping[str, Any]],
    expected_symbols: Sequence[str],
    expected_company_names: Mapping[str, str],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Correct only the verified iFinD one-row code/name column inversion."""

    expected = tuple(expected_symbols)
    if (
        len(expected) != 1
        or set(expected_company_names) != set(expected)
        or not isinstance(expected_company_names.get(expected[0]), str)
    ):
        raise IfindProviderError(
            "IFIND_MCP_RESPONSE_IDENTITY_CONTRACT_INVALID",
            "MCP summary identity validation requires one exact symbol/name pair",
        )
    expected_symbol = expected[0]
    expected_name = str(expected_company_names[expected_symbol])
    normalized_tables: list[dict[str, Any]] = []
    corrections: list[str] = []
    identity_table_seen = False
    for table in tables:
        copied = dict(table)
        columns = table.get("columns")
        rows = table.get("rows")
        if (
            isinstance(columns, list)
            and "证券代码" in columns
            and "证券简称" in columns
        ):
            if identity_table_seen or not isinstance(rows, list) or len(rows) != 1:
                raise IfindProviderError(
                    "IFIND_MCP_RESPONSE_IDENTITY_AMBIGUOUS",
                    "MCP summary response must contain one bounded identity row",
                )
            identity_table_seen = True
            row = rows[0]
            if not isinstance(row, Mapping):
                raise IfindProviderError(
                    "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
                    "MCP summary identity row is malformed",
                )
            code_value = row.get("证券代码")
            name_value = row.get("证券简称")
            normal = (
                _matches_expected_provider_symbol(code_value, expected_symbol)
                and name_value == expected_name
            )
            inverted = (
                _matches_expected_provider_symbol(name_value, expected_symbol)
                and code_value == expected_name
            )
            if normal:
                copied["rows"] = [dict(row)]
            elif inverted:
                corrected = dict(row)
                corrected["证券代码"] = str(name_value)
                corrected["证券简称"] = str(code_value)
                copied["rows"] = [corrected]
                corrections.append("supplier_summary_security_code_name_inversion")
            else:
                raise IfindProviderError(
                    "IFIND_MCP_RESPONSE_IDENTITY_MISMATCH",
                    "MCP summary identity fields do not match the accepted symbol and company",
                )
        normalized_tables.append(copied)
    if not identity_table_seen:
        raise IfindProviderError(
            "IFIND_MCP_RESPONSE_IDENTITY_TABLE_MISSING",
            "MCP summary response does not contain the required identity table",
        )
    return normalized_tables, corrections


def _matches_expected_provider_symbol(value: Any, expected_symbol: str) -> bool:
    return isinstance(value, str) and value in {
        expected_symbol,
        expected_symbol[:6],
    }


def parse_ifind_mcp_provider_markdown_tables(markdown: str) -> list[dict[str, Any]]:
    """Parse the supplier's documented Markdown table envelope without rendering prose."""

    encoded = markdown.encode("utf-8")
    metadata = _markdown_shape_metadata(markdown)
    if not encoded or len(encoded) > _MAX_PROVIDER_MARKDOWN_BYTES:
        raise _response_contract_error(
            "IFIND_MCP_RESPONSE_TOO_LARGE",
            "MCP provider Markdown is empty or exceeds the staging bound",
            failure_stage="provider_markdown",
            failure_reason="json_shape_invalid",
            metadata=metadata,
        )
    if _CONTROL_RE.search(
        markdown.replace("\n", "").replace("\r", "").replace("\t", "")
    ):
        raise _response_contract_error(
            "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
            "MCP provider Markdown contains blocked control characters",
            failure_stage="provider_markdown",
            failure_reason="markdown_control_characters",
            metadata=metadata,
        )
    lines = markdown.splitlines()
    if len(lines) > _MAX_PROVIDER_MARKDOWN_LINES:
        raise _response_contract_error(
            "IFIND_MCP_RESPONSE_TOO_LARGE",
            "MCP provider Markdown contains too many lines",
            failure_stage="provider_markdown",
            failure_reason="json_shape_invalid",
            metadata=metadata,
        )
    tables: list[dict[str, Any]] = []
    current_title = ""
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("#"):
            current_title = stripped.lstrip("#").strip()[:256]
        if (
            _looks_like_markdown_table_row(stripped)
            and index + 1 < len(lines)
            and _is_markdown_separator_row(lines[index + 1])
        ):
            columns = _markdown_cells(stripped)
            if (
                not columns
                or len(columns) > _MAX_PROVIDER_TABLE_COLUMNS
                or any(not column or len(column) > 128 for column in columns)
                or len(columns) != len(set(columns))
            ):
                raise _response_contract_error(
                    "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
                    "MCP provider Markdown table has invalid columns",
                    failure_stage="provider_markdown",
                    failure_reason="markdown_invalid_header",
                    metadata=metadata,
                )
            index += 2
            rows: list[dict[str, str]] = []
            while index < len(lines) and _looks_like_markdown_table_row(lines[index]):
                values = _markdown_cells(lines[index])
                if len(values) != len(columns):
                    raise _response_contract_error(
                        "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
                        "MCP provider Markdown row width does not match its header",
                        failure_stage="provider_markdown",
                        failure_reason="markdown_row_width_mismatch",
                        metadata=metadata,
                    )
                rows.append(dict(zip(columns, values)))
                if len(rows) > _MAX_PROVIDER_TABLE_ROWS:
                    raise _response_contract_error(
                        "IFIND_MCP_RESPONSE_TOO_LARGE",
                        "MCP provider Markdown table exceeds the row bound",
                        failure_stage="provider_markdown",
                        failure_reason="json_shape_invalid",
                        metadata=metadata,
                    )
                index += 1
            if not rows:
                raise _response_contract_error(
                    "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
                    "MCP provider Markdown table has no data rows",
                    failure_stage="provider_markdown",
                    failure_reason="markdown_empty_table",
                    metadata=metadata,
                )
            tables.append({"title": current_title, "columns": columns, "rows": rows})
            if len(tables) > _MAX_PROVIDER_TABLES:
                raise _response_contract_error(
                    "IFIND_MCP_RESPONSE_TOO_LARGE",
                    "MCP provider Markdown contains too many tables",
                    failure_stage="provider_markdown",
                    failure_reason="json_shape_invalid",
                    metadata=metadata,
                )
            continue
        index += 1
    if not tables:
        raise _response_contract_error(
            "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
            "MCP provider response contains no parseable Markdown table",
            failure_stage="provider_markdown",
            failure_reason="markdown_no_table",
            metadata=metadata,
        )
    return tables


def _markdown_cells(line: str) -> list[str]:
    content = line.strip()
    if not _looks_like_markdown_table_row(content):
        raise IfindProviderError(
            "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
            "MCP provider Markdown table row is not pipe-delimited",
        )
    if content.startswith("|"):
        content = content[1:]
    if content.endswith("|") and not content.endswith("\\|"):
        content = content[:-1]
    cells = [
        cell.replace("\\|", "|").strip() for cell in re.split(r"(?<!\\)\|", content)
    ]
    is_separator = bool(cells) and all(
        re.fullmatch(r":?-{3,}:?", cell) for cell in cells
    )
    if not is_separator and any(_spreadsheet_formula_risk(cell) for cell in cells):
        raise _response_contract_error(
            "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
            "MCP provider Markdown contains a spreadsheet-formula-risk cell",
            failure_stage="provider_markdown",
            failure_reason="markdown_unsafe_cell",
        )
    return cells


def _looks_like_markdown_table_row(line: str) -> bool:
    content = line.strip()
    if not content or "|" not in content:
        return False
    if content.startswith("|"):
        content = content[1:]
    if content.endswith("|") and not content.endswith("\\|"):
        content = content[:-1]
    return bool(content and re.search(r"(?<!\\)\|", content))


def _spreadsheet_formula_risk(value: str) -> bool:
    """Reject provider cells that could execute if a staged table is later exported."""

    if not value:
        return False
    if value[0] in {"=", "+", "@"}:
        return True
    if value[0] != "-" or value in {"-", "--"}:
        return False
    return re.fullmatch(r"-[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?%?", value) is None


def _is_markdown_separator_row(line: str) -> bool:
    try:
        cells = _markdown_cells(line)
    except IfindProviderError:
        return False
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def validate_ifind_mcp_pilot_response_scope(
    payload: Mapping[str, Any],
    expected_symbols: Sequence[str],
) -> None:
    """Reject a stock result unless its explicit canonical symbols equal the pilot scope."""

    expected = tuple(expected_symbols)
    if not expected or len(set(expected)) != len(expected):
        raise IfindProviderError(
            "IFIND_MCP_RESPONSE_SCOPE_INVALID",
            "expected pilot response scope is empty or duplicated",
        )
    discovered: list[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, Mapping):
            for key, nested in value.items():
                if str(key).lower() in _RESPONSE_SYMBOL_KEYS:
                    if isinstance(nested, str):
                        raw_symbols = (nested,)
                    elif isinstance(nested, (list, tuple)) and all(
                        isinstance(item, str) for item in nested
                    ):
                        raw_symbols = tuple(nested)
                    else:
                        raise IfindProviderError(
                            "IFIND_MCP_RESPONSE_SCOPE_UNVERIFIED",
                            "MCP stock response symbol field is not a bounded string sequence",
                        )
                    parts = tuple(
                        item.strip()
                        for raw_symbol in raw_symbols
                        for item in raw_symbol.split(",")
                        if item.strip()
                    )
                    if not parts:
                        raise IfindProviderError(
                            "IFIND_MCP_RESPONSE_SCOPE_UNVERIFIED",
                            "MCP stock response contains an empty symbol field",
                        )
                    discovered.extend(parts)
                visit(nested)
        elif isinstance(value, list):
            for nested in value:
                visit(nested)

    visit(payload)
    if not discovered:
        raise IfindProviderError(
            "IFIND_MCP_RESPONSE_SCOPE_UNVERIFIED",
            "MCP stock response does not expose a canonical symbol field",
        )
    expected_by_code = {value[:6]: value for value in expected}
    if len(expected_by_code) != len(expected):
        raise IfindProviderError(
            "IFIND_MCP_RESPONSE_SCOPE_INVALID",
            "expected pilot response scope cannot resolve provider-native codes uniquely",
        )
    normalized = []
    for value in discovered:
        if _CANONICAL_SYMBOL_RE.fullmatch(value):
            normalized.append(value)
        elif re.fullmatch(r"[0-9]{6}", value) and value in expected_by_code:
            # iFinD summary tables use a six-digit 证券代码. It is accepted only
            # when it maps uniquely to the exact one-call allowlisted scope;
            # arbitrary aliases and codes outside that scope remain blocked.
            normalized.append(expected_by_code[value])
        else:
            raise IfindProviderError(
                "IFIND_MCP_RESPONSE_SCOPE_UNVERIFIED",
                "MCP stock response contains an unresolvable symbol alias",
            )
    if set(normalized) != set(expected):
        raise IfindProviderError(
            "IFIND_MCP_RESPONSE_SCOPE_VIOLATION",
            "MCP stock response contains a symbol outside the accepted pilot scope",
        )


def ifind_mcp_readiness(environ: Optional[Mapping[str, str]] = None) -> dict[str, Any]:
    source = environ if environ is not None else os.environ
    policy = IfindMcpNetworkPolicy.from_environment(source)
    keychain_lookup_available = _trusted_security_command() is not None
    if not policy.live_access_allowed:
        readiness_state = "OFFLINE_READY_NETWORK_DISABLED"
    else:
        readiness_state = "LIVE_HANDSHAKE_REQUIRED"
    return {
        "provider_id": "ifind",
        "provider_name": "同花顺 iFinD",
        "product_name": "AI 金融数据服务",
        "channel_id": "ifind_mcp_api_key",
        "interface_mode": "streamablehttp_mcp_api_key",
        "base_url": IFIND_MCP_BASE_URL,
        "protocol_version": IFIND_MCP_PROTOCOL_VERSION,
        "readiness_state": readiness_state,
        "network_opt_in": policy.network_opt_in,
        "provider_opt_in": policy.provider_opt_in,
        "mcp_opt_in": policy.mcp_opt_in,
        "data_call_opt_in": policy.data_call_opt_in,
        "live_access_allowed": policy.live_access_allowed,
        "credential_delivery_policy": "macos_keychain_preferred_environment_fallback",
        "credential_verified": False,
        "keychain_lookup_available": keychain_lookup_available,
        "raw_payload_commit_allowed": False,
        "local_token_persistence_allowed": False,
        "supported_service_count": len(IFIND_MCP_SERVERS),
        "entitlement_profile": IFIND_MCP_ENTITLEMENT_PROFILE,
        "reviewed_tool_count": sum(
            len(names) for names in IFIND_MCP_TOOL_CATALOG.values()
        ),
        "expected_tool_count": sum(
            len(names) for names in IFIND_MCP_ENTITLED_TOOL_CATALOG.values()
        ),
        "unavailable_by_plan_count": sum(
            len(names) for names in IFIND_MCP_PLAN_UNAVAILABLE_TOOLS.values()
        ),
        "unavailable_by_plan": [
            f"{server_type}:{tool_name}"
            for server_type, tool_names in IFIND_MCP_PLAN_UNAVAILABLE_TOOLS.items()
            for tool_name in tool_names
        ],
    }


def write_ifind_mcp_probe_status(
    root: Path,
    result: Mapping[str, Any],
) -> Path:
    """Persist only allowlisted, credential-free local probe metadata."""

    target = root / IFIND_MCP_LOCAL_PROBE_STATUS
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(target.parent, 0o700)
    payload = _sanitize_ifind_mcp_probe_status(
        {
            **result,
            "observed_at": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }
    )
    temporary = target.with_suffix(".json.tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(temporary, flags, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
    except Exception:
        try:
            temporary.unlink()
        except OSError:
            pass
        raise
    os.replace(temporary, target)
    os.chmod(target, 0o600)
    return target


def read_ifind_mcp_probe_status(root: Path) -> Mapping[str, Any]:
    """Read the sanitized local probe status without touching credentials."""

    target = root / IFIND_MCP_LOCAL_PROBE_STATUS
    try:
        raw = target.read_bytes()
    except OSError:
        return {
            "status": "NOT_RUN",
            "mode": "none",
            "live_handshake_verified": False,
            "input_schemas_verified": False,
            "data_tool_called": False,
        }
    if len(raw) > 64 * 1024:
        return {
            "status": "INVALID_LOCAL_STATUS",
            "mode": "none",
            "live_handshake_verified": False,
            "input_schemas_verified": False,
            "data_tool_called": False,
        }
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {
            "status": "INVALID_LOCAL_STATUS",
            "mode": "none",
            "live_handshake_verified": False,
            "input_schemas_verified": False,
            "data_tool_called": False,
        }
    if not isinstance(parsed, Mapping):
        return {
            "status": "INVALID_LOCAL_STATUS",
            "mode": "none",
            "live_handshake_verified": False,
            "input_schemas_verified": False,
            "data_tool_called": False,
        }
    return _sanitize_ifind_mcp_probe_status(parsed)


def reclassify_ifind_mcp_s1_probe_status(root: Path) -> Path:
    """Migrate the exact pre-contract S1 PIT block without a provider call.

    The old runner emitted this state only after both fixed symbol summaries
    passed identity, scope and schema staging. Reclassification preserves the
    original local observation time, keeps provider availability unknown, and
    never promotes a canonical row.
    """

    current = read_ifind_mcp_probe_status(root)
    if not (
        current.get("status") == "BLOCKED"
        and current.get("mode") == "live_stage_s1"
        and current.get("failure_code") == "IFIND_MCP_PIT_TIMESTAMP_UNPROVEN"
        and current.get("data_call_count") == 2
        and current.get("failed_symbol") is None
        and current.get("live_handshake_verified") is True
        and current.get("input_schemas_verified") is True
        and current.get("data_tool_called") is True
        and isinstance(current.get("observed_at"), str)
    ):
        raise IfindProviderError(
            "IFIND_MCP_S1_STATUS_RECLASSIFICATION_REJECTED",
            "local S1 status does not prove the exact dual-identity staging state",
        )
    return write_ifind_mcp_probe_status(
        root,
        {
            "status": "PASS",
            "mode": "live_stage_s1",
            "acceptance_state": "S1_IDENTITY_ACCEPTANCE_METADATA_VERIFIED",
            "temporal_class": "acceptance_metadata_only",
            "provider_available_at_status": (
                "UNKNOWN_NOT_REQUIRED_FOR_IDENTITY_METADATA"
            ),
            "identity_observed_at": current["observed_at"],
            "actual_tool_count": current.get("actual_tool_count"),
            "expected_tool_count": current.get("expected_tool_count"),
            "data_call_count": 2,
            "staged_symbol_count": 2,
            "live_handshake_verified": True,
            "input_schemas_verified": True,
            "data_tool_called": True,
            "s1_identity_acceptance_verified": True,
            "s2_requires_separate_authorization": True,
            "canonical_accepted": False,
        },
    )


def _sanitize_ifind_mcp_probe_status(value: Mapping[str, Any]) -> Mapping[str, Any]:
    status = str(value.get("status", "INVALID_LOCAL_STATUS"))
    if status not in {"PASS", "BLOCKED", "NOT_RUN", "INVALID_LOCAL_STATUS"}:
        status = "INVALID_LOCAL_STATUS"
    mode = str(value.get("mode", "none"))
    if mode not in {"none", "offline_contract", "live_handshake", "live_stage_s1"}:
        mode = "none"
    server = value.get("server")
    if server not in IFIND_MCP_SERVERS:
        server = None
    failure_code = value.get("failure_code")
    if not isinstance(failure_code, str) or not re.fullmatch(
        r"[A-Z0-9_]{1,96}", failure_code
    ):
        failure_code = None
    http_status = value.get("http_status")
    if (
        isinstance(http_status, bool)
        or not isinstance(http_status, int)
        or not 100 <= http_status <= 599
    ):
        http_status = None
    observed_at = value.get("observed_at")
    if not _is_safe_utc_timestamp(observed_at):
        observed_at = None
    actual_tool_count = value.get("actual_tool_count")
    if isinstance(actual_tool_count, bool) or not isinstance(actual_tool_count, int):
        actual_tool_count = None
    expected_tool_count = value.get("expected_tool_count")
    if isinstance(expected_tool_count, bool) or not isinstance(
        expected_tool_count, int
    ):
        expected_tool_count = None
    data_call_count = value.get("data_call_count")
    if isinstance(data_call_count, bool) or not isinstance(data_call_count, int):
        data_call_count = None
    elif not 0 <= data_call_count <= 16:
        data_call_count = None
    failed_symbol = value.get("failed_symbol")
    if not isinstance(failed_symbol, str) or not _CANONICAL_SYMBOL_RE.fullmatch(
        failed_symbol
    ):
        failed_symbol = None
    acceptance_state = value.get("acceptance_state")
    if acceptance_state != "S1_IDENTITY_ACCEPTANCE_METADATA_VERIFIED":
        acceptance_state = None
    temporal_class = value.get("temporal_class")
    if temporal_class != "acceptance_metadata_only":
        temporal_class = None
    provider_available_at_status = value.get("provider_available_at_status")
    if provider_available_at_status != ("UNKNOWN_NOT_REQUIRED_FOR_IDENTITY_METADATA"):
        provider_available_at_status = None
    identity_observed_at = value.get("identity_observed_at")
    if not _is_safe_utc_timestamp(identity_observed_at):
        identity_observed_at = None
    staged_symbol_count = value.get("staged_symbol_count")
    if (
        isinstance(staged_symbol_count, bool)
        or not isinstance(staged_symbol_count, int)
        or not 0 <= staged_symbol_count <= 2
    ):
        staged_symbol_count = None
    s1_identity_acceptance_verified = (
        status == "PASS"
        and mode == "live_stage_s1"
        and acceptance_state == "S1_IDENTITY_ACCEPTANCE_METADATA_VERIFIED"
        and temporal_class == "acceptance_metadata_only"
        and provider_available_at_status == "UNKNOWN_NOT_REQUIRED_FOR_IDENTITY_METADATA"
        and data_call_count == 2
        and staged_symbol_count == 2
        and failed_symbol is None
        and value.get("s1_identity_acceptance_verified") is True
    )
    if status == "PASS":
        failure_code = None
        http_status = None
        failed_symbol = None
    return {
        "status": status,
        "mode": mode,
        "server": server,
        "failure_code": failure_code,
        "http_status": http_status,
        "observed_at": observed_at,
        "actual_tool_count": actual_tool_count,
        "expected_tool_count": expected_tool_count,
        "data_call_count": data_call_count,
        "failed_symbol": failed_symbol,
        "acceptance_state": acceptance_state,
        "temporal_class": temporal_class,
        "provider_available_at_status": provider_available_at_status,
        "provider_available_at_verified": False,
        "identity_observed_at": identity_observed_at,
        "staged_symbol_count": staged_symbol_count,
        "s1_identity_acceptance_verified": s1_identity_acceptance_verified,
        "s2_requires_separate_authorization": (
            s1_identity_acceptance_verified
            and value.get("s2_requires_separate_authorization") is True
        ),
        "canonical_accepted": False,
        "live_handshake_verified": value.get("live_handshake_verified") is True,
        "input_schemas_verified": value.get("input_schemas_verified") is True,
        "data_tool_called": value.get("data_tool_called") is True,
        "credential_exposed": False,
    }


def _is_safe_utc_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or len(value) > 64 or not value.endswith("Z"):
        return False
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() == timezone.utc.utcoffset(
        None
    )


def _trusted_security_command() -> Optional[str]:
    if sys.platform != "darwin":
        return None
    resolved = shutil.which("security")
    if not resolved or os.path.realpath(resolved) != "/usr/bin/security":
        return None
    return "/usr/bin/security"


def _tool_schema_contract(tool_name: str, schema: Any) -> Mapping[str, Any]:
    if not isinstance(schema, Mapping) or schema.get("type") != "object":
        raise IfindProviderError(
            "IFIND_MCP_TOOL_SCHEMA_MISMATCH",
            "MCP tool inputSchema must be a JSON object schema",
        )
    properties = schema.get("properties")
    required = schema.get("required")
    if not isinstance(properties, Mapping) or not isinstance(required, list):
        raise IfindProviderError(
            "IFIND_MCP_TOOL_SCHEMA_MISMATCH",
            "MCP tool inputSchema must declare bounded properties and required fields",
        )
    if any(not isinstance(value, str) for value in required):
        raise IfindProviderError(
            "IFIND_MCP_TOOL_SCHEMA_MISMATCH",
            "MCP tool inputSchema required fields must be strings",
        )
    expected = IFIND_MCP_EXPECTED_INPUT_FIELDS.get(tool_name)
    supplier_contract_match = expected is not None and all(
        field in properties and field in required for field in expected
    )
    if expected is not None and not supplier_contract_match:
        raise IfindProviderError(
            "IFIND_MCP_TOOL_SCHEMA_MISMATCH",
            "MCP tool inputSchema does not contain the supplier-documented required fields",
        )
    canonical = json.dumps(
        schema,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return {
        "tool_name": tool_name,
        "schema_sha256": hashlib.sha256(canonical).hexdigest(),
        "required_fields": tuple(sorted(required)),
        "property_fields": tuple(sorted(str(value) for value in properties)),
        "supplier_contract_match": supplier_contract_match,
    }


def validate_ifind_mcp_contract_document(contract: Mapping[str, Any]) -> None:
    """Validate the committed MCP contract without credentials or network access."""

    expected_services = [
        {
            "server_type": server_type,
            "server_id": server_id,
            "expected_tools": list(IFIND_MCP_TOOL_CATALOG[server_type]),
        }
        for server_type, server_id in IFIND_MCP_SERVERS.items()
    ]
    channel = contract.get("purchased_mcp_channel")
    network = contract.get("network_policy")
    entitlement_profiles = (
        channel.get("entitlement_profiles") if isinstance(channel, Mapping) else None
    )
    active_entitlement = (
        entitlement_profiles.get(IFIND_MCP_ENTITLEMENT_PROFILE)
        if isinstance(entitlement_profiles, Mapping)
        else None
    )
    if (
        contract.get("contract_id") != "ifind_ai_financial_data_service_v1"
        or contract.get("provider_id") != "ifind"
        or not isinstance(channel, Mapping)
        or channel.get("base_url") != IFIND_MCP_BASE_URL
        or channel.get("protocol_version") != IFIND_MCP_PROTOCOL_VERSION
        or channel.get("services") != expected_services
        or not isinstance(entitlement_profiles, Mapping)
        or entitlement_profiles.get("active") != IFIND_MCP_ENTITLEMENT_PROFILE
        or not isinstance(active_entitlement, Mapping)
        or active_entitlement.get("reviewed_tool_count") != 36
        or active_entitlement.get("entitled_expected_tool_count") != 35
        or active_entitlement.get("unavailable_by_plan") != ["edb:search_edb"]
        or not isinstance(network, Mapping)
        or network.get("default") != "disabled"
        or network.get("required_opt_ins")
        != [
            f"{IFIND_NETWORK_ENV}=1",
            f"{IFIND_PROVIDER_ENV}=1",
            f"{IFIND_MCP_PROVIDER_ENV}=1",
        ]
    ):
        raise IfindProviderError(
            "IFIND_MCP_CONTRACT_INVALID",
            "committed iFinD MCP contract does not match the reviewed runtime boundary",
        )


def _server_url(server_type: str) -> str:
    server_id = IFIND_MCP_SERVERS.get(server_type)
    if not server_id:
        raise IfindProviderError(
            "IFIND_MCP_SERVER_NOT_ALLOWED", "MCP server type is not approved"
        )
    url = f"{IFIND_MCP_BASE_URL}/{server_id}"
    _validate_mcp_url(url)
    return url


def _validate_mcp_url(url: str) -> None:
    parsed = urlsplit(url)
    allowed_paths = {
        f"/ds-mcp-servers/{server_id}" for server_id in IFIND_MCP_SERVERS.values()
    }
    if (
        parsed.scheme != "https"
        or parsed.hostname != IFIND_MCP_HOST
        or parsed.port != IFIND_MCP_PORT
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in allowed_paths
    ):
        raise IfindProviderError(
            "IFIND_MCP_DOMAIN_BLOCKED",
            "MCP request target is outside the exact approved host, port, and path catalog",
        )


def _validate_api_key(value: str) -> None:
    try:
        encoded = value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise IfindProviderError(
            "IFIND_MCP_CREDENTIAL_FORMAT_INVALID",
            "MCP API key is not header-safe ASCII",
        ) from exc
    if not encoded:
        raise IfindProviderError(
            "IFIND_MCP_CREDENTIAL_MISSING", "MCP API key is missing"
        )
    if len(encoded) > _MAX_API_KEY_BYTES or not _API_KEY_RE.fullmatch(value):
        raise IfindProviderError(
            "IFIND_MCP_CREDENTIAL_FORMAT_INVALID",
            "MCP API key is outside the approved header-safe format",
        )


def _validate_session_id(value: str) -> None:
    if not value or not _SESSION_ID_RE.fullmatch(value):
        raise IfindProviderError(
            "IFIND_MCP_SESSION_INVALID",
            "MCP server did not provide a valid bounded session identifier",
        )


def _validate_tool_arguments(
    server_type: str,
    tool_name: str,
    arguments: Mapping[str, Any],
) -> None:
    if tool_name not in IFIND_MCP_TOOL_CATALOG.get(server_type, ()):
        raise IfindProviderError(
            "IFIND_MCP_TOOL_NOT_ALLOWED",
            "requested MCP tool is outside the reviewed supplier catalog",
        )
    if not isinstance(arguments, Mapping):
        raise IfindProviderError(
            "IFIND_MCP_ARGUMENTS_INVALID", "MCP tool arguments must be an object"
        )
    if any(key in _BLOCKED_KEYS for key in arguments):
        raise IfindProviderError(
            "IFIND_MCP_ARGUMENTS_INVALID", "MCP arguments contain a blocked field"
        )
    if tool_name in _HIGH_FREQUENCY_TOOLS:
        _validate_high_frequency_arguments(arguments)
    elif tool_name in _NEWS_SEARCH_TOOLS:
        _validate_news_arguments(arguments)
    elif tool_name == "search_trending_news":
        _validate_trending_arguments(arguments)
    elif tool_name == "search_global_stocks":
        _require_exact_keys(arguments, {"query", "market"}, {"query", "market"})
        _validate_text(arguments["query"], "query", _MAX_QUERY_CHARACTERS)
        if arguments["market"] not in {"港股", "美股"}:
            raise IfindProviderError(
                "IFIND_MCP_ARGUMENTS_INVALID",
                "global-stock market must be 港股 or 美股",
            )
    else:
        _require_exact_keys(arguments, {"query"}, {"query"})
        _validate_text(arguments["query"], "query", _MAX_QUERY_CHARACTERS)
    try:
        request_size = len(
            json.dumps(arguments, ensure_ascii=False, allow_nan=False).encode("utf-8")
        )
    except (TypeError, ValueError) as exc:
        raise IfindProviderError(
            "IFIND_MCP_ARGUMENTS_INVALID", "MCP arguments are not finite JSON"
        ) from exc
    if request_size > 16 * 1024:
        raise IfindProviderError(
            "IFIND_MCP_ARGUMENTS_INVALID",
            "MCP tool arguments exceed the approved bound",
        )


def _validate_high_frequency_arguments(arguments: Mapping[str, Any]) -> None:
    _require_exact_keys(
        arguments,
        {"symbols", "indicators", "data_mode", "interval"},
        {"symbols", "indicators", "data_mode"},
    )
    _split_bounded_csv(arguments["symbols"], "symbols", 10)
    _split_bounded_csv(arguments["indicators"], "indicators", 10)
    mode = arguments["data_mode"]
    if mode not in {"real_time", "highfreq"}:
        raise IfindProviderError(
            "IFIND_MCP_ARGUMENTS_INVALID",
            "data_mode must be real_time or highfreq",
        )
    interval = arguments.get("interval")
    if mode == "highfreq":
        if (
            isinstance(interval, bool)
            or not isinstance(interval, int)
            or interval not in _ALLOWED_INTERVALS
        ):
            raise IfindProviderError(
                "IFIND_MCP_ARGUMENTS_INVALID",
                "highfreq interval is missing or outside the approved minute set",
            )
    elif interval is not None:
        raise IfindProviderError(
            "IFIND_MCP_ARGUMENTS_INVALID",
            "real_time requests must not include a high-frequency interval",
        )


def _validate_news_arguments(arguments: Mapping[str, Any]) -> None:
    _require_exact_keys(
        arguments,
        {"query", "time_start", "time_end", "size"},
        {"query", "time_start", "time_end", "size"},
    )
    _validate_text(arguments["query"], "query", _MAX_QUERY_CHARACTERS)
    start = _parse_date(arguments["time_start"], "time_start")
    end = _parse_date(arguments["time_end"], "time_end")
    if start > end or (end - start).days > _MAX_DATE_SPAN_DAYS:
        raise IfindProviderError(
            "IFIND_MCP_ARGUMENTS_INVALID",
            "news date range is reversed or exceeds the approved bound",
        )
    _validate_size(arguments["size"])


def _validate_trending_arguments(arguments: Mapping[str, Any]) -> None:
    _require_exact_keys(
        arguments,
        {"keyword", "industry_name", "time_scope", "size"},
        {"keyword", "industry_name", "time_scope", "size"},
    )
    _validate_text(arguments["keyword"], "keyword", 128)
    _validate_text(arguments["industry_name"], "industry_name", 128)
    _validate_text(arguments["time_scope"], "time_scope", 64)
    _validate_size(arguments["size"])


def _validate_size(value: Any) -> None:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
        or value > _MAX_NEWS_RESULTS
    ):
        raise IfindProviderError(
            "IFIND_MCP_ARGUMENTS_INVALID",
            f"result size must be an integer from 1 to {_MAX_NEWS_RESULTS}",
        )


def _parse_date(value: Any, field: str) -> date:
    if not isinstance(value, str):
        raise IfindProviderError(
            "IFIND_MCP_ARGUMENTS_INVALID", f"{field} must use YYYY-MM-DD"
        )
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise IfindProviderError(
            "IFIND_MCP_ARGUMENTS_INVALID", f"{field} must use YYYY-MM-DD"
        ) from exc


def _require_exact_keys(
    arguments: Mapping[str, Any],
    allowed: set[str],
    required: set[str],
) -> None:
    keys = set(arguments)
    if not required.issubset(keys) or not keys.issubset(allowed):
        raise IfindProviderError(
            "IFIND_MCP_ARGUMENTS_INVALID",
            "MCP tool arguments are missing required keys or contain unapproved keys",
        )


def _validate_text(value: Any, field: str, maximum: int) -> None:
    if (
        not isinstance(value, str)
        or not value.strip()
        or len(value) > maximum
        or _CONTROL_RE.search(value)
    ):
        raise IfindProviderError(
            "IFIND_MCP_ARGUMENTS_INVALID",
            f"{field} is empty, contains control characters, or exceeds the approved bound",
        )


def _split_bounded_csv(value: Any, field: str, maximum: int) -> Tuple[str, ...]:
    if not isinstance(value, str):
        raise IfindProviderError(
            "IFIND_MCP_ARGUMENTS_INVALID", f"{field} must be a comma-separated string"
        )
    items = tuple(item.strip() for item in value.split(","))
    if (
        not items
        or len(items) > maximum
        or len(set(items)) != len(items)
        or any(not item or len(item) > 64 or _CONTROL_RE.search(item) for item in items)
    ):
        raise IfindProviderError(
            "IFIND_MCP_ARGUMENTS_INVALID",
            f"{field} is empty, duplicated, or above the approved count/length bound",
        )
    return items


def _parse_mcp_response(
    response: IfindMcpHttpResponse,
    request_id: Optional[int],
    allow_empty: bool,
) -> Optional[Mapping[str, Any]]:
    if not response.body:
        if allow_empty:
            return None
        raise IfindProviderError(
            "IFIND_MCP_RESPONSE_EMPTY", "MCP response body is empty"
        )
    content_type = response.headers.get("content-type", "").lower()
    if "text/event-stream" in content_type:
        messages = _parse_sse_json_messages(response.body)
        if request_id is not None:
            matching = [item for item in messages if item.get("id") == request_id]
            if len(matching) == 1:
                return matching[0]
        if len(messages) == 1:
            return messages[0]
        raise _response_contract_error(
            "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
            "MCP event stream did not contain one matching JSON-RPC response",
            failure_stage="jsonrpc_contract",
            failure_reason="jsonrpc_response_not_unique",
        )
    if content_type and "json" not in content_type:
        raise IfindProviderError(
            "IFIND_MCP_CONTENT_TYPE_INVALID",
            "MCP response content type is not JSON or event-stream",
        )
    try:
        parsed = json.loads(response.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IfindProviderError(
            "IFIND_MCP_RESPONSE_INVALID_JSON", "MCP response is not valid JSON"
        ) from exc
    if not isinstance(parsed, Mapping):
        raise _response_contract_error(
            "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
            "MCP JSON-RPC response must be an object",
            failure_stage="jsonrpc_contract",
            failure_reason="jsonrpc_result_not_object",
        )
    _validate_json_shape(parsed)
    if request_id is not None and parsed.get("id") != request_id:
        raise IfindProviderError(
            "IFIND_MCP_RESPONSE_ID_MISMATCH",
            "MCP response id does not match the request",
        )
    return dict(parsed)


def _parse_sse_json_messages(body: bytes) -> Tuple[Mapping[str, Any], ...]:
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise IfindProviderError(
            "IFIND_MCP_RESPONSE_INVALID_JSON", "MCP event stream is not UTF-8"
        ) from exc
    messages = []
    data_lines = []
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n") + [""]:
        if line == "":
            if data_lines:
                data = "\n".join(data_lines)
                data_lines = []
                if data == "[DONE]":
                    continue
                try:
                    parsed = json.loads(data)
                except json.JSONDecodeError as exc:
                    raise IfindProviderError(
                        "IFIND_MCP_RESPONSE_INVALID_JSON",
                        "MCP event data is not valid JSON",
                    ) from exc
                if not isinstance(parsed, Mapping):
                    raise _response_contract_error(
                        "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
                        "MCP event data must be a JSON object",
                        failure_stage="jsonrpc_contract",
                        failure_reason="jsonrpc_result_not_object",
                    )
                _validate_json_shape(parsed)
                messages.append(dict(parsed))
            continue
        if line.startswith(":"):
            continue
        if line.startswith("data:"):
            data_lines.append(line[5:].lstrip(" "))
    if not messages:
        raise IfindProviderError(
            "IFIND_MCP_RESPONSE_EMPTY", "MCP event stream contained no JSON data"
        )
    return tuple(messages)


def _require_rpc_result(
    message: Optional[Mapping[str, Any]],
    method: str,
) -> Mapping[str, Any]:
    if not isinstance(message, Mapping) or message.get("jsonrpc") != "2.0":
        raise _response_contract_error(
            "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
            f"{method} did not return a JSON-RPC 2.0 object",
            failure_stage="jsonrpc_contract",
            failure_reason="jsonrpc_result_not_object",
        )
    result = message.get("result")
    if not isinstance(result, Mapping):
        raise _response_contract_error(
            "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
            f"{method} did not return an object result",
            failure_stage="jsonrpc_contract",
            failure_reason="jsonrpc_result_not_object",
        )
    return result


def _validate_json_shape(value: Any) -> None:
    item_count = 0

    def walk(item: Any, depth: int) -> None:
        nonlocal item_count
        item_count += 1
        if item_count > _MAX_JSON_ITEMS or depth > _MAX_JSON_DEPTH:
            raise _response_contract_error(
                "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
                "MCP JSON structure exceeds the approved depth or item bound",
                failure_stage="mcp_result_extraction",
                failure_reason="json_shape_invalid",
            )
        if item is None or isinstance(item, (str, int, bool)):
            return
        if isinstance(item, float):
            if not math.isfinite(item):
                raise _response_contract_error(
                    "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
                    "MCP JSON contains a non-finite number",
                    failure_stage="mcp_result_extraction",
                    failure_reason="json_shape_invalid",
                )
            return
        if isinstance(item, list):
            for child in item:
                walk(child, depth + 1)
            return
        if isinstance(item, Mapping):
            for key, child in item.items():
                if not isinstance(key, str) or key in _BLOCKED_KEYS:
                    raise _response_contract_error(
                        "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
                        "MCP JSON contains an invalid or blocked object key",
                        failure_stage="mcp_result_extraction",
                        failure_reason="json_shape_invalid",
                    )
                walk(child, depth + 1)
            return
        raise _response_contract_error(
            "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
            "MCP JSON contains an unsupported value type",
            failure_stage="mcp_result_extraction",
            failure_reason="json_shape_invalid",
        )

    walk(value, 0)


def _read_bounded(handle: Any, truncate: bool) -> Tuple[bytes, bool]:
    raw = handle.read(_MAX_RESPONSE_BYTES + 1)
    if len(raw) > _MAX_RESPONSE_BYTES:
        if truncate:
            return raw[:_MAX_RESPONSE_BYTES], True
        raise IfindProviderError(
            "IFIND_MCP_RESPONSE_TOO_LARGE",
            "MCP response exceeds the approved payload bound",
        )
    return raw, False


def _response_headers(headers: Any) -> dict[str, str]:
    try:
        items = headers.items()
    except AttributeError:
        return {}
    return {str(key).lower(): str(value) for key, value in items}


def _env_enabled(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}

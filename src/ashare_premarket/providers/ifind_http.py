from __future__ import annotations

import json
import os
import re
import socket
import ssl
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Mapping, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import (
    HTTPRedirectHandler,
    HTTPSHandler,
    ProxyHandler,
    Request,
    build_opener,
)


IFIND_BASE_URL = "https://quantapi.51ifind.com"
IFIND_NETWORK_ENV = "ASHARE_ALLOW_NETWORK_INGESTION"
IFIND_PROVIDER_ENV = "ASHARE_ALLOW_IFIND"
IFIND_ACCESS_TOKEN_ENV = "IFIND_ACCESS_TOKEN"
IFIND_REFRESH_TOKEN_ENV = "IFIND_REFRESH_TOKEN"

IFIND_ENDPOINTS = {
    "access_token": "/api/v1/get_access_token",
    "history_quotation": "/api/v1/cmd_history_quotation",
    "basic_data": "/api/v1/basic_data_service",
    "date_sequence": "/api/v1/date_sequence",
    "data_pool": "/api/v1/data_pool",
    "edb": "/api/v1/edb_service",
    "report_query": "/api/v1/report_query",
    "trade_dates": "/api/v1/get_trade_dates",
}

IFIND_DATA_MODULES = (
    {
        "module_id": "security_master",
        "display_name": "证券主数据与资本结构",
        "priority": "P0",
        "endpoint": "basic_data",
        "intended_fields": "上市日期;交易状态;总股本;流通股本;自由流通股本;行业分类",
        "pit_requirement": "as_of_date_and_classification_version_required",
        "dashboard_surface": "stock_identity_and_capital_structure",
        "implementation_state": "adapter_ready_live_validation_pending",
    },
    {
        "module_id": "daily_market_and_calendar",
        "display_name": "日线行情与交易日历",
        "priority": "P0",
        "endpoint": "history_quotation;trade_dates",
        "intended_fields": "open;high;low;close;volume;amount;turnover;trade_date",
        "pit_requirement": "history_quotation_uses_trade_date_symbol;trade_dates_uses_trade_date_market_code;both_not_after_data_cutoff",
        "dashboard_surface": "stock_market_and_provider_health",
        "implementation_state": "adapter_ready_live_validation_pending",
    },
    {
        "module_id": "pit_fundamentals_and_valuation",
        "display_name": "PIT 财务与估值",
        "priority": "P0",
        "endpoint": "basic_data;date_sequence",
        "intended_fields": "PE;PB;PS;ROE;营收;净利润;利润率;负债率;现金流",
        "pit_requirement": "report_period_announcement_date_and_available_at_required",
        "dashboard_surface": "stock_fundamentals",
        "implementation_state": "adapter_ready_indicator_mapping_pending",
    },
    {
        "module_id": "industry_and_constituents",
        "display_name": "行业分类与历史成分",
        "priority": "P1",
        "endpoint": "data_pool;basic_data",
        "intended_fields": "行业代码;行业名称;成分股;生效日期;失效日期",
        "pit_requirement": "historical_membership_required_no_current_membership_backfill",
        "dashboard_surface": "market_context_and_stock_identity",
        "implementation_state": "adapter_ready_report_mapping_pending",
    },
    {
        "module_id": "corporate_events_and_announcements",
        "display_name": "公司事件与公告元数据",
        "priority": "P1",
        "endpoint": "report_query",
        "intended_fields": "公告时间;公告类型;标题;证券代码;报告期",
        "pit_requirement": "publication_timestamp_required_full_text_not_committed",
        "dashboard_surface": "stock_event_context",
        "implementation_state": "adapter_ready_live_validation_pending",
    },
    {
        "module_id": "macro_and_edb",
        "display_name": "宏观与经济数据库",
        "priority": "P1",
        "endpoint": "edb",
        "intended_fields": "指标代码;观测期;发布日期;修订标识;数值",
        "pit_requirement": "release_date_and_revision_policy_required",
        "dashboard_surface": "market_context",
        "implementation_state": "adapter_ready_series_mapping_pending",
    },
    {
        "module_id": "market_structure_crosscheck",
        "display_name": "两融、北向、宽度与资金流交叉验证",
        "priority": "P1",
        "endpoint": "basic_data;date_sequence;data_pool",
        "intended_fields": "融资融券;北向持股;市场宽度;资金流;自由流通市值",
        "pit_requirement": "source_timestamp_vendor_definition_and_revision_audit_required",
        "dashboard_surface": "provider_health_and_research_readiness",
        "implementation_state": "adapter_ready_entitlement_validation_pending",
    },
)

_SYMBOL_RE = re.compile(r"^[0-9]{6}\.(?:SH|SZ|BJ)$")
_INDICATOR_RE = re.compile(r"^[A-Za-z0-9_]+$")
_MAX_CODES = 50
_MAX_INDICATORS = 64
_MAX_REQUEST_BYTES = 128 * 1024
_MAX_RESPONSE_BYTES = 16 * 1024 * 1024
_MAX_DATE_SPAN_DAYS = 3660
_MAX_FUNCTION_PARAMS = 32
_MAX_OUTPUT_FIELDS = 64
_MAX_PARAM_TEXT = 512
_MAX_TOKEN_BYTES = 8 * 1024
_REPORT_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
_OUTPUT_FIELD_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(?::[YN])?$")
_FUNCTION_KEY_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
_TOKEN_RE = re.compile(r"^[A-Za-z0-9._~+/=-]+$")


class IfindProviderError(RuntimeError):
    """A credential-safe iFinD failure with a stable classification code."""

    def __init__(
        self,
        failure_code: str,
        safe_message: str,
        http_status: Optional[int] = None,
        *,
        safe_metadata: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(f"{failure_code}: {safe_message}")
        self.failure_code = failure_code
        self.safe_message = safe_message
        self.http_status = http_status
        # Metadata is never rendered or persisted directly. Consumers must
        # project it through their own fixed allowlist before it can leave the
        # process. This lets a live paid-data call retain structural failure
        # evidence without retaining provider values, response text, or keys.
        self.safe_metadata = dict(safe_metadata or {})


@dataclass(frozen=True, repr=False)
class IfindCredentials:
    access_token: str = ""
    refresh_token: str = ""

    def __repr__(self) -> str:
        return (
            "IfindCredentials("
            f"access_token_present={bool(self.access_token)}, "
            f"refresh_token_present={bool(self.refresh_token)})"
        )

    @classmethod
    def from_environment(
        cls, environ: Optional[Mapping[str, str]] = None
    ) -> "IfindCredentials":
        source = environ if environ is not None else os.environ
        return cls(
            access_token=str(source.get(IFIND_ACCESS_TOKEN_ENV, "")).strip(),
            refresh_token=str(source.get(IFIND_REFRESH_TOKEN_ENV, "")).strip(),
        )

    def safe_status(self) -> dict[str, Any]:
        return {
            "access_token_present": bool(self.access_token),
            "refresh_token_present": bool(self.refresh_token),
            "credential_source": (
                "access_token_environment"
                if self.access_token
                else "refresh_token_environment" if self.refresh_token else "missing"
            ),
            "token_value_exposed": False,
            "token_persisted": False,
        }


@dataclass(frozen=True)
class IfindNetworkPolicy:
    network_opt_in: bool
    provider_opt_in: bool

    @classmethod
    def from_environment(
        cls, environ: Optional[Mapping[str, str]] = None
    ) -> "IfindNetworkPolicy":
        source = environ if environ is not None else os.environ
        return cls(
            network_opt_in=_env_enabled(source.get(IFIND_NETWORK_ENV)),
            provider_opt_in=_env_enabled(source.get(IFIND_PROVIDER_ENV)),
        )

    @property
    def live_access_allowed(self) -> bool:
        return self.network_opt_in and self.provider_opt_in

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


class IfindUrllibTransport:
    """HTTPS-only transport that does not inherit system proxy settings."""

    def __init__(self) -> None:
        self._opener = build_opener(
            ProxyHandler({}),
            HTTPSHandler(context=ssl.create_default_context()),
            IfindNoRedirectHandler(),
        )

    def post_json(
        self,
        url: str,
        headers: Mapping[str, str],
        payload: Optional[Mapping[str, Any]],
        timeout_seconds: float,
    ) -> Tuple[int, Mapping[str, Any]]:
        try:
            body = (
                json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
                    "utf-8"
                )
                if payload is not None
                else b""
            )
            request = Request(url, data=body, headers=dict(headers), method="POST")
            with self._opener.open(request, timeout=timeout_seconds) as response:
                status = int(getattr(response, "status", 200))
                raw = _read_bounded(response)
        except HTTPError as exc:
            raw = _read_bounded(exc)
            return int(exc.code), _best_effort_json_object(raw)
        except socket.timeout as exc:
            raise IfindProviderError(
                "IFIND_NETWORK_TIMEOUT", "provider request timed out"
            ) from exc
        except ssl.SSLError as exc:
            raise IfindProviderError(
                "IFIND_TLS_FAILURE", "provider TLS validation failed"
            ) from exc
        except URLError as exc:
            raise IfindProviderError(
                "IFIND_NETWORK_FAILURE", "provider network request failed"
            ) from exc
        except (ValueError, UnicodeEncodeError):
            raise IfindProviderError(
                "IFIND_CREDENTIAL_FORMAT_INVALID",
                "provider credential is not safe for an HTTP header",
            ) from None
        return status, _safe_json_object(raw)


Transport = Callable[
    [str, Mapping[str, str], Optional[Mapping[str, Any]], float],
    Tuple[int, Mapping[str, Any]],
]


class IfindNoRedirectHandler(HTTPRedirectHandler):
    """Never forward provider credentials to a redirect target."""

    def redirect_request(
        self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> None:
        return None


class IfindHttpClient:
    """Bounded iFinD HTTP adapter; tokens remain in memory and are never logged."""

    def __init__(
        self,
        credentials: Optional[IfindCredentials] = None,
        policy: Optional[IfindNetworkPolicy] = None,
        transport: Optional[Transport] = None,
        timeout_seconds: float = 20.0,
    ) -> None:
        try:
            normalized_timeout = float(timeout_seconds)
        except (TypeError, ValueError) as exc:
            raise IfindProviderError(
                "IFIND_TIMEOUT_INVALID", "provider timeout must be numeric"
            ) from exc
        if isinstance(timeout_seconds, bool) or not 0 < normalized_timeout <= 60:
            raise IfindProviderError(
                "IFIND_TIMEOUT_INVALID",
                "provider timeout must be within 0 to 60 seconds",
            )
        self._credentials = credentials or IfindCredentials.from_environment()
        self.policy = policy or IfindNetworkPolicy.from_environment()
        self._transport = transport or IfindUrllibTransport().post_json
        self.timeout_seconds = normalized_timeout
        self._access_token = self._credentials.access_token

    def __repr__(self) -> str:
        return (
            "IfindHttpClient("
            f"credential_configured={bool(self._credentials.access_token or self._credentials.refresh_token)}, "
            f"live_access_allowed={self.policy.live_access_allowed})"
        )

    def credential_status(self) -> dict[str, Any]:
        return self._credentials.safe_status()

    def get_access_token(self) -> str:
        self.policy.require_live_access()
        if self._access_token:
            self._access_token = _validate_token(self._access_token)
            return self._access_token
        if not self._credentials.refresh_token:
            raise IfindProviderError(
                "IFIND_CREDENTIAL_MISSING",
                f"set {IFIND_ACCESS_TOKEN_ENV} or {IFIND_REFRESH_TOKEN_ENV} in the local environment",
            )
        status, payload = self._post(
            "access_token",
            headers={
                "Content-Type": "application/json",
                "refresh_token": self._credentials.refresh_token,
            },
            payload=None,
            authenticated=False,
        )
        self._raise_for_http_status(status)
        token_value = _nested(payload, "data", "access_token")
        if token_value is None or token_value == "":
            raise IfindProviderError(
                "IFIND_AUTH_RESPONSE_INVALID",
                "access-token response did not contain the required token field",
                http_status=status,
            )
        token = _validate_token(token_value)
        self._access_token = token
        return token

    def _query(self, endpoint: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        if endpoint == "access_token" or endpoint not in IFIND_ENDPOINTS:
            raise IfindProviderError(
                "IFIND_ENDPOINT_NOT_ALLOWED",
                "endpoint is outside the approved iFinD contract",
            )
        self.policy.require_live_access()
        self._validate_request_payload(payload)
        access_token = self.get_access_token()
        status, result = self._post(
            endpoint,
            headers={"Content-Type": "application/json", "access_token": access_token},
            payload=payload,
            authenticated=True,
        )
        self._raise_for_http_status(status)
        self._raise_for_provider_error(result, status)
        return result

    def history_quotation(
        self,
        codes: Sequence[str],
        indicators: Sequence[str],
        start_date: str,
        end_date: str,
        function_params: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        validated_codes = _validate_codes(codes)
        validated_indicators = _validate_indicators(indicators)
        start = _validate_date(start_date)
        end = _validate_date(end_date)
        _validate_date_span(start, end)
        return self._query(
            "history_quotation",
            {
                "codes": ",".join(validated_codes),
                "indicators": ",".join(validated_indicators),
                "startdate": start,
                "enddate": end,
                "functionpara": _validate_function_params(
                    function_params or {"Fill": "Blank"}
                ),
            },
        )

    def basic_data(
        self,
        codes: Sequence[str],
        indicator_params: Sequence[Mapping[str, Any]],
    ) -> Mapping[str, Any]:
        validated_codes = _validate_codes(codes)
        normalized = _validate_indicator_params(indicator_params)
        return self._query(
            "basic_data", {"codes": ",".join(validated_codes), "indipara": normalized}
        )

    def date_sequence(
        self,
        codes: Sequence[str],
        indicator_params: Sequence[Mapping[str, Any]],
        start_date: str,
        end_date: str,
        function_params: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        start = _validate_date(start_date)
        end = _validate_date(end_date)
        _validate_date_span(start, end)
        return self._query(
            "date_sequence",
            {
                "codes": ",".join(_validate_codes(codes)),
                "startdate": start,
                "enddate": end,
                "functionpara": _validate_function_params(
                    function_params or {"Fill": "Blank"}
                ),
                "indipara": _validate_indicator_params(indicator_params),
            },
        )

    def data_pool(
        self,
        report_name: str,
        function_params: Mapping[str, Any],
        output_fields: Sequence[str],
    ) -> Mapping[str, Any]:
        report = str(report_name).strip()
        if not _REPORT_NAME_RE.fullmatch(report):
            raise IfindProviderError(
                "IFIND_REQUEST_INVALID", "report name is outside the approved syntax"
            )
        return self._query(
            "data_pool",
            {
                "reportname": report,
                "functionpara": _validate_function_params(function_params),
                "outputpara": ",".join(_validate_output_fields(output_fields)),
            },
        )

    def edb(
        self, indicators: Sequence[str], start_date: str, end_date: str
    ) -> Mapping[str, Any]:
        start = _validate_date(start_date)
        end = _validate_date(end_date)
        _validate_date_span(start, end)
        return self._query(
            "edb",
            {
                "indicators": ",".join(_validate_indicators(indicators)),
                "startdate": start,
                "enddate": end,
            },
        )

    def report_query(
        self,
        codes: Sequence[str],
        report_types: Sequence[str],
        start_date: str,
        end_date: str,
        output_fields: Sequence[str],
    ) -> Mapping[str, Any]:
        start = _validate_date(start_date)
        end = _validate_date(end_date)
        _validate_date_span(start, end)
        normalized_types = [str(value).strip() for value in report_types]
        if (
            not normalized_types
            or len(normalized_types) > 16
            or len(set(normalized_types)) != len(normalized_types)
            or any(not value.isdigit() or len(value) > 12 for value in normalized_types)
        ):
            raise IfindProviderError(
                "IFIND_REQUEST_INVALID", "report types are outside the approved bound"
            )
        return self._query(
            "report_query",
            {
                "codes": ",".join(_validate_codes(codes)),
                "functionpara": {"reportType": ",".join(normalized_types)},
                "beginrDate": start,
                "endrDate": end,
                "outputpara": ",".join(_validate_output_fields(output_fields)),
            },
        )

    def trade_dates(
        self,
        market_code: str,
        start_date: str,
        *,
        offset: int,
        date_type: str = "0",
        period: str = "D",
        date_format: str = "0",
        output: str = "sequencedate",
    ) -> Mapping[str, Any]:
        market = str(market_code).strip()
        if not market.isdigit() or len(market) > 12:
            raise IfindProviderError(
                "IFIND_REQUEST_INVALID", "market code is outside the approved syntax"
            )
        if (
            isinstance(offset, bool)
            or not isinstance(offset, int)
            or abs(offset) > _MAX_DATE_SPAN_DAYS
        ):
            raise IfindProviderError(
                "IFIND_REQUEST_INVALID",
                "trading-date offset is outside the approved bound",
            )
        if str(date_type) not in {"0", "1"} or period not in {"D", "W", "M"}:
            raise IfindProviderError(
                "IFIND_REQUEST_INVALID",
                "trading-date frequency parameters are unsupported",
            )
        if str(date_format) not in {"0", "1", "2"} or output not in {
            "sequencedate",
            "singledate",
        }:
            raise IfindProviderError(
                "IFIND_REQUEST_INVALID",
                "trading-date output parameters are unsupported",
            )
        return self._query(
            "trade_dates",
            {
                "marketcode": market,
                "functionpara": {
                    "dateType": str(date_type),
                    "period": period,
                    "offset": str(offset),
                    "dateFormat": str(date_format),
                    "output": output,
                },
                "startdate": _validate_date(start_date),
            },
        )

    def _post(
        self,
        endpoint: str,
        headers: Mapping[str, str],
        payload: Optional[Mapping[str, Any]],
        authenticated: bool,
    ) -> Tuple[int, Mapping[str, Any]]:
        self.policy.require_live_access()
        path = IFIND_ENDPOINTS[endpoint]
        url = f"{IFIND_BASE_URL}{path}"
        _validate_provider_url(url, path)
        if authenticated and "access_token" not in headers:
            raise IfindProviderError(
                "IFIND_AUTH_HEADER_MISSING",
                "authenticated request is missing its token header",
            )
        safe_headers = dict(headers)
        for header_name in ("access_token", "refresh_token"):
            if header_name in safe_headers:
                safe_headers[header_name] = _validate_token(safe_headers[header_name])
        return self._transport(url, safe_headers, payload, self.timeout_seconds)

    @staticmethod
    def _validate_request_payload(payload: Mapping[str, Any]) -> None:
        if not isinstance(payload, Mapping):
            raise IfindProviderError(
                "IFIND_REQUEST_INVALID", "request payload must be an object"
            )
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
        if len(encoded) > _MAX_REQUEST_BYTES:
            raise IfindProviderError(
                "IFIND_REQUEST_TOO_LARGE", "request exceeds the approved payload bound"
            )

    @staticmethod
    def _raise_for_http_status(status: int) -> None:
        if 200 <= status < 300:
            return
        if status in {401, 403}:
            code = "IFIND_AUTH_OR_PERMISSION_DENIED"
        elif status == 429:
            code = "IFIND_RATE_LIMITED"
        elif status >= 500:
            code = "IFIND_PROVIDER_SERVER_ERROR"
        else:
            code = "IFIND_HTTP_ERROR"
        raise IfindProviderError(
            code, "provider returned a non-success HTTP status", http_status=status
        )

    @staticmethod
    def _raise_for_provider_error(payload: Mapping[str, Any], status: int) -> None:
        error_code = payload.get("errorcode")
        if error_code in {None, "", 0, "0"}:
            return
        raise IfindProviderError(
            "IFIND_PROVIDER_RESPONSE_ERROR",
            "provider returned a non-success application status",
            http_status=status,
        )


def ifind_readiness(environ: Optional[Mapping[str, str]] = None) -> dict[str, Any]:
    credentials = IfindCredentials.from_environment(environ)
    policy = IfindNetworkPolicy.from_environment(environ)
    credential_status = credentials.safe_status()
    live_ready = policy.live_access_allowed and (
        credential_status["access_token_present"]
        or credential_status["refresh_token_present"]
    )
    if live_ready:
        state = "LIVE_OPT_IN_READY_NOT_PROBED"
    elif not policy.live_access_allowed:
        state = "OFFLINE_READY_NETWORK_DISABLED"
    else:
        state = "BLOCKED_MISSING_CREDENTIAL"
    return {
        "provider_id": "ifind",
        "provider_name": "同花顺 iFinD",
        "product_name": "AI 金融数据服务",
        "interface_mode": "official_https_api",
        "base_url": IFIND_BASE_URL,
        "readiness_state": state,
        "network_opt_in": policy.network_opt_in,
        "provider_opt_in": policy.provider_opt_in,
        "live_access_allowed": policy.live_access_allowed,
        **credential_status,
        "raw_payload_commit_allowed": False,
        "local_token_persistence_allowed": False,
        "supported_endpoint_count": len(IFIND_ENDPOINTS) - 1,
        "data_module_count": len(IFIND_DATA_MODULES),
    }


def _env_enabled(value: Optional[str]) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _validate_token(value: Any) -> str:
    if not isinstance(value, str):
        raise IfindProviderError(
            "IFIND_CREDENTIAL_FORMAT_INVALID",
            "provider credential must be a bounded ASCII token",
        )
    try:
        encoded = value.encode("ascii")
    except UnicodeEncodeError:
        raise IfindProviderError(
            "IFIND_CREDENTIAL_FORMAT_INVALID",
            "provider credential must be a bounded ASCII token",
        ) from None
    if not encoded or len(encoded) > _MAX_TOKEN_BYTES or not _TOKEN_RE.fullmatch(value):
        raise IfindProviderError(
            "IFIND_CREDENTIAL_FORMAT_INVALID",
            "provider credential must be a bounded ASCII token",
        )
    return value


def _validate_codes(codes: Sequence[str]) -> list[str]:
    values = [str(code).strip().upper() for code in codes]
    if not values or len(values) > _MAX_CODES or len(set(values)) != len(values):
        raise IfindProviderError(
            "IFIND_REQUEST_INVALID",
            "symbol count is empty, duplicated, or above the approved bound",
        )
    if any(not _SYMBOL_RE.fullmatch(code) for code in values):
        raise IfindProviderError(
            "IFIND_REQUEST_INVALID",
            "symbol does not match the canonical exchange-suffixed format",
        )
    return values


def _validate_indicators(indicators: Sequence[str]) -> list[str]:
    values = [str(indicator).strip() for indicator in indicators]
    if not values or len(values) > _MAX_INDICATORS or len(set(values)) != len(values):
        raise IfindProviderError(
            "IFIND_REQUEST_INVALID",
            "indicator count is empty, duplicated, or above the approved bound",
        )
    if any(not _INDICATOR_RE.fullmatch(indicator) for indicator in values):
        raise IfindProviderError(
            "IFIND_REQUEST_INVALID", "indicator name contains unsupported characters"
        )
    return values


def _validate_indicator_params(
    indicator_params: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    if not indicator_params or len(indicator_params) > _MAX_INDICATORS:
        raise IfindProviderError(
            "IFIND_REQUEST_INVALID", "indicator count is outside the approved bound"
        )
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in indicator_params:
        if not isinstance(item, Mapping):
            raise IfindProviderError(
                "IFIND_REQUEST_INVALID", "indicator configuration must be an object"
            )
        indicator = _validate_indicators([str(item.get("indicator", ""))])[0]
        if indicator in seen:
            raise IfindProviderError(
                "IFIND_REQUEST_INVALID", "indicator configuration contains duplicates"
            )
        seen.add(indicator)
        params = item.get("indiparams", [])
        if not isinstance(params, list) or len(params) > 32:
            raise IfindProviderError(
                "IFIND_REQUEST_INVALID", "indicator parameters must be a bounded list"
            )
        normalized_params: list[str] = []
        for value in params:
            if isinstance(value, (Mapping, list, tuple, set)):
                raise IfindProviderError(
                    "IFIND_REQUEST_INVALID",
                    "nested indicator parameters are not allowed",
                )
            text = str(value)
            if len(text.encode("utf-8")) > _MAX_PARAM_TEXT:
                raise IfindProviderError(
                    "IFIND_REQUEST_INVALID",
                    "indicator parameter exceeds the approved bound",
                )
            normalized_params.append(text)
        normalized.append({"indicator": indicator, "indiparams": normalized_params})
    return normalized


def _validate_function_params(params: Mapping[str, Any]) -> dict[str, Any]:
    if (
        not isinstance(params, Mapping)
        or not params
        or len(params) > _MAX_FUNCTION_PARAMS
    ):
        raise IfindProviderError(
            "IFIND_REQUEST_INVALID",
            "function parameters are outside the approved bound",
        )
    normalized: dict[str, Any] = {}
    for raw_key, value in params.items():
        key = str(raw_key).strip()
        if not _FUNCTION_KEY_RE.fullmatch(key):
            raise IfindProviderError(
                "IFIND_REQUEST_INVALID",
                "function parameter key is outside the approved syntax",
            )
        if isinstance(value, (Mapping, list, tuple, set)) or value is None:
            raise IfindProviderError(
                "IFIND_REQUEST_INVALID",
                "nested or null function parameters are not allowed",
            )
        if len(str(value).encode("utf-8")) > _MAX_PARAM_TEXT:
            raise IfindProviderError(
                "IFIND_REQUEST_INVALID", "function parameter exceeds the approved bound"
            )
        normalized[key] = value
    return normalized


def _validate_output_fields(output_fields: Sequence[str]) -> list[str]:
    values = [str(value).strip() for value in output_fields]
    if (
        not values
        or len(values) > _MAX_OUTPUT_FIELDS
        or len(set(values)) != len(values)
        or any(not _OUTPUT_FIELD_RE.fullmatch(value) for value in values)
    ):
        raise IfindProviderError(
            "IFIND_REQUEST_INVALID", "output fields are outside the approved bound"
        )
    return values


def _validate_date(value: str) -> str:
    text = str(value).strip()
    for pattern in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(text, pattern).date().isoformat()
        except ValueError:
            continue
    raise IfindProviderError(
        "IFIND_REQUEST_INVALID", "date must use YYYY-MM-DD or YYYYMMDD"
    )


def _validate_date_span(start: str, end: str) -> None:
    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.strptime(end, "%Y-%m-%d").date()
    if start_date > end_date:
        raise IfindProviderError(
            "IFIND_REQUEST_INVALID", "start date must not be after end date"
        )
    if (end_date - start_date).days > _MAX_DATE_SPAN_DAYS:
        raise IfindProviderError(
            "IFIND_REQUEST_INVALID", "date span exceeds the approved request bound"
        )


def _nested(payload: Mapping[str, Any], *keys: str) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def _safe_json_object(raw: bytes) -> Mapping[str, Any]:
    if not raw:
        return {}
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IfindProviderError(
            "IFIND_RESPONSE_INVALID_JSON", "provider response was not valid JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise IfindProviderError(
            "IFIND_RESPONSE_SCHEMA_MISMATCH", "provider response must be a JSON object"
        )
    return payload


def _best_effort_json_object(raw: bytes) -> Mapping[str, Any]:
    """Preserve HTTP failure classification when a gateway returns text/HTML."""

    if not raw:
        return {}
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _validate_provider_url(url: str, expected_path: str) -> None:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "quantapi.51ifind.com"
        or parsed.port not in {None, 443}
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path != expected_path
        or parsed.query
        or parsed.fragment
    ):
        raise IfindProviderError(
            "IFIND_DOMAIN_BLOCKED",
            "provider URL is outside the exact approved HTTPS endpoint contract",
        )


def _read_bounded(response: Any) -> bytes:
    raw = response.read(_MAX_RESPONSE_BYTES + 1)
    if len(raw) > _MAX_RESPONSE_BYTES:
        raise IfindProviderError(
            "IFIND_RESPONSE_TOO_LARGE",
            "provider response exceeded the approved byte bound",
        )
    return raw

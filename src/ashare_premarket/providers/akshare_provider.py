from __future__ import annotations

import importlib
import importlib.util
import inspect
import time
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Any

from ashare_premarket.providers.failure_classification import classify_provider_failure, classify_provider_success
from ashare_premarket.providers.network_isolation import scoped_finance_network_env
from ashare_premarket.providers.provider_attempt_log import make_attempt
from ashare_premarket.providers.schema_normalization import (
    normalize_benchmark_schema,
    normalize_code_name_schema,
    normalize_spot_schema,
    normalize_stock_ohlcv_schema,
    normalize_tencent_stock_ohlcv_schema,
    symbol_to_provider_code,
)

PROVIDER_ID = "akshare"
DEFAULT_PROVIDER_TIMEOUT_SECONDS = 30


@dataclass
class ProviderResult:
    rows: list[dict[str, object]]
    attempt: dict[str, object]
    raw: Any = None


def akshare_available() -> bool:
    return importlib.util.find_spec("akshare") is not None


def akshare_function_signatures() -> dict[str, str]:
    if not akshare_available():
        return {}
    ak = importlib.import_module("akshare")
    signatures = {}
    for name in ["stock_info_a_code_name", "stock_zh_a_spot_em", "stock_zh_a_hist", "stock_zh_a_hist_tx", "index_zh_a_hist"]:
        fn = getattr(ak, name, None)
        signatures[name] = str(inspect.signature(fn)) if fn else "missing"
    return signatures


def load_a_share_code_name_list(network_enabled: bool) -> ProviderResult:
    return _call(
        "stock_info_a_code_name",
        {},
        network_enabled,
        lambda raw: normalize_code_name_schema(raw),
    )


def load_a_share_spot_snapshot(network_enabled: bool) -> tuple[dict[str, dict[str, object]], dict[str, object]]:
    result = _call(
        "stock_zh_a_spot_em",
        {},
        network_enabled,
        lambda raw: _normalize_spot_for_result(raw),
    )
    return {str(row["symbol"]): row for row in result.rows}, result.attempt


def load_stock_ohlcv_daily(symbol: str, start_date: str, end_date: str, adjust_policy: str, network_enabled: bool) -> ProviderResult:
    kwargs = {
        "symbol": symbol_to_provider_code(symbol),
        "period": "daily",
        "start_date": start_date.replace("-", ""),
        "end_date": end_date.replace("-", ""),
        "adjust": adjust_policy,
    }
    return _call(
        "stock_zh_a_hist",
        kwargs,
        network_enabled,
        lambda raw: normalize_stock_ohlcv_schema(raw, symbol),
        symbol=symbol,
        date_start=start_date,
        date_end=end_date,
    )


def tencent_symbol(symbol: str) -> str:
    code, separator, exchange = symbol.strip().upper().partition(".")
    if not separator or len(code) != 6 or not code.isdigit() or exchange not in {"SH", "SZ", "BJ"}:
        raise ValueError(f"unsupported_canonical_symbol:{symbol}")
    valid_market = (
        (exchange == "SH" and code.startswith(("5", "6", "9")))
        or (exchange == "SZ" and code.startswith(("0", "2", "3")))
        or (exchange == "BJ" and code.startswith(("4", "8", "92")))
    )
    if not valid_market:
        raise ValueError(f"canonical_symbol_exchange_mismatch:{symbol}")
    return f"{exchange.lower()}{code}"


def load_stock_ohlcv_daily_tencent(
    symbol: str,
    start_date: str,
    end_date: str,
    adjust_policy: str,
    network_enabled: bool,
) -> ProviderResult:
    kwargs = {
        "symbol": tencent_symbol(symbol),
        "start_date": start_date.replace("-", ""),
        "end_date": end_date.replace("-", ""),
        "adjust": adjust_policy,
    }
    result = _call(
        "stock_zh_a_hist_tx",
        kwargs,
        network_enabled,
        lambda raw: normalize_tencent_stock_ohlcv_schema(raw, symbol),
        symbol=symbol,
        date_start=start_date,
        date_end=end_date,
    )
    result.attempt["endpoint_family"] = "web.ifzq.gtimg.cn;proxy.finance.qq.com"
    if symbol.upper().endswith(".BJ") and result.attempt.get("status") != "PASS":
        result.attempt["failure_class"] = "TENCENT_BJ_UPSTREAM_UNSUPPORTED"
        result.attempt["rejection_reason"] = "TENCENT_BJ_UPSTREAM_UNSUPPORTED"
        result.attempt["retry_allowed"] = False
        result.attempt["notes"] = "governed BJ mapping is valid; Tencent history returned no supported day series"
    return result


def load_benchmark_ohlcv_daily(benchmark_symbol: str, start_date: str, end_date: str, network_enabled: bool) -> ProviderResult:
    kwargs = {
        "symbol": benchmark_symbol,
        "period": "daily",
        "start_date": start_date.replace("-", ""),
        "end_date": end_date.replace("-", ""),
    }
    return _call(
        "index_zh_a_hist",
        kwargs,
        network_enabled,
        lambda raw: normalize_benchmark_schema(raw, benchmark_symbol),
        symbol=benchmark_symbol,
        date_start=start_date,
        date_end=end_date,
    )


def _call(
    function_name: str,
    kwargs: dict[str, object],
    network_enabled: bool,
    normalizer,
    symbol: str = "",
    date_start: str = "",
    date_end: str = "",
) -> ProviderResult:
    start_monotonic = time.monotonic()
    started_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    if not network_enabled:
        return _empty_result(function_name, symbol, date_start, date_end, "NETWORK_DISABLED_BY_POLICY", "network disabled by policy")
    if not akshare_available():
        return _empty_result(function_name, symbol, date_start, date_end, "AKSHARE_IMPORT_FAILED", "optional dependency akshare is not installed", network_enabled=True)
    network_context: dict[str, object] = {}
    try:
        ak = importlib.import_module("akshare")
        fn = getattr(ak, function_name)
        call_kwargs = _filter_kwargs(fn, {**kwargs, "timeout": DEFAULT_PROVIDER_TIMEOUT_SECONDS})
        with scoped_finance_network_env(function_name, network_enabled=True) as scoped_context:
            network_context = scoped_context
            raw = fn(**call_kwargs)
        rows, schema_valid, notes = normalizer(raw)
        classification = classify_provider_success(len(rows), schema_valid)
        attempt = make_attempt(
            PROVIDER_ID,
            function_name,
            symbol=symbol,
            date_start=date_start,
            date_end=date_end,
            network_enabled=True,
            status="PASS" if classification.failure_class == "PROVIDER_OK" else "FAIL",
            failure_class=classification.failure_class,
            rows_returned=len(rows),
            schema_valid=schema_valid,
            retry_allowed=classification.retry_allowed,
            response_type=type(raw).__name__,
            notes=notes,
            attempt_ts=started_at,
            elapsed_seconds=round(time.monotonic() - start_monotonic, 6),
            request_parameters=call_kwargs,
            endpoint_family=network_context.get("target_domain", ""),
            akshare_version=str(getattr(ak, "__version__", "unknown")),
            exception_type="",
            terminal_exception_message="",
            network_context=network_context,
        )
        return ProviderResult(rows=rows, attempt=attempt, raw=raw)
    except Exception as exc:  # provider/runtime failure path
        classification = classify_provider_failure(exc=exc, context=network_context)
        status_code = getattr(getattr(exc, "response", None), "status_code", "")
        return ProviderResult(
            rows=[],
            attempt=make_attempt(
                PROVIDER_ID,
                function_name,
                symbol=symbol,
                date_start=date_start,
                date_end=date_end,
                network_enabled=True,
                status="FAIL",
                failure_class=classification.failure_class,
                rows_returned=0,
                schema_valid=False,
                retry_allowed=classification.retry_allowed,
                notes=classification.notes,
                attempt_ts=started_at,
                elapsed_seconds=round(time.monotonic() - start_monotonic, 6),
                request_parameters=kwargs,
                endpoint_family=network_context.get("target_domain", ""),
                akshare_version=_akshare_version(),
                exception_type=type(exc).__name__,
                terminal_exception_message=str(exc),
                http_status=str(status_code),
                network_context=network_context,
            ),
        )


def _normalize_spot_for_result(raw: Any) -> tuple[list[dict[str, object]], bool, str]:
    lookup, ok, notes = normalize_spot_schema(raw)
    return list(lookup.values()), ok, notes


def _filter_kwargs(fn: Any, kwargs: dict[str, object]) -> dict[str, object]:
    signature = inspect.signature(fn)
    if any(param.kind == inspect.Parameter.VAR_KEYWORD for param in signature.parameters.values()):
        return kwargs
    return {key: value for key, value in kwargs.items() if key in signature.parameters}


def _empty_result(
    function_name: str,
    symbol: str,
    date_start: str,
    date_end: str,
    failure_class: str,
    notes: str,
    network_enabled: bool = False,
) -> ProviderResult:
    classification = classify_provider_failure(exc=ModuleNotFoundError(notes)) if failure_class in {"DEPENDENCY_MISSING", "AKSHARE_IMPORT_FAILED"} else None
    return ProviderResult(
        rows=[],
        attempt=make_attempt(
            PROVIDER_ID,
            function_name,
            symbol=symbol,
            date_start=date_start,
            date_end=date_end,
            network_enabled=network_enabled,
            status="FAIL",
            failure_class=failure_class,
            rows_returned=0,
            schema_valid=False,
            retry_allowed=classification.retry_allowed if classification else False,
            notes=notes,
        ),
    )


def _akshare_version() -> str:
    try:
        return str(getattr(importlib.import_module("akshare"), "__version__", "unknown"))
    except Exception:
        return "unavailable"

from __future__ import annotations

import importlib
import importlib.util
import inspect
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
    symbol_to_provider_code,
)

PROVIDER_ID = "akshare"


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
    for name in ["stock_info_a_code_name", "stock_zh_a_spot_em", "stock_zh_a_hist", "index_zh_a_hist"]:
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


def load_stock_ohlcv_daily_sina(symbol: str, start_date: str, end_date: str, adjust_policy: str, network_enabled: bool) -> ProviderResult:
    """Load the bounded Sina daily series exposed through AKShare.

    This is an explicit fallback for ``stock_zh_a_hist`` provider failures. It
    remains date-bounded, normalized through the same OHLCV contract, and is
    identified separately in provider provenance.
    """
    market = symbol.rsplit(".", 1)[-1].lower() if "." in symbol else ""
    prefix = {"sh": "sh", "sz": "sz", "bj": "bj"}.get(market, "")
    kwargs = {
        "symbol": f"{prefix}{symbol_to_provider_code(symbol)}",
        "start_date": start_date.replace("-", ""),
        "end_date": end_date.replace("-", ""),
        "adjust": adjust_policy,
    }
    return _call(
        "stock_zh_a_daily",
        kwargs,
        network_enabled,
        lambda raw: normalize_stock_ohlcv_schema(raw, symbol, source_id="akshare_stock_zh_a_daily_sina"),
        symbol=symbol,
        date_start=start_date,
        date_end=end_date,
        provider_id="akshare_sina",
    )


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
    provider_id: str = PROVIDER_ID,
) -> ProviderResult:
    if not network_enabled:
        return _empty_result(function_name, symbol, date_start, date_end, "NETWORK_DISABLED_BY_POLICY", "network disabled by policy", provider_id=provider_id)
    if not akshare_available():
        return _empty_result(function_name, symbol, date_start, date_end, "AKSHARE_IMPORT_FAILED", "optional dependency akshare is not installed", network_enabled=True, provider_id=provider_id)
    network_context: dict[str, object] = {}
    try:
        ak = importlib.import_module("akshare")
        fn = getattr(ak, function_name)
        call_kwargs = _filter_kwargs(fn, kwargs)
        with scoped_finance_network_env(function_name, network_enabled=True) as scoped_context:
            network_context = scoped_context
            raw = fn(**call_kwargs)
        rows, schema_valid, notes = normalizer(raw)
        classification = classify_provider_success(len(rows), schema_valid)
        attempt = make_attempt(
            provider_id,
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
        )
        return ProviderResult(rows=rows, attempt=attempt, raw=raw)
    except Exception as exc:  # provider/runtime failure path
        classification = classify_provider_failure(exc=exc, context=network_context)
        return ProviderResult(
            rows=[],
            attempt=make_attempt(
                provider_id,
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
    provider_id: str = PROVIDER_ID,
) -> ProviderResult:
    classification = classify_provider_failure(exc=ModuleNotFoundError(notes)) if failure_class in {"DEPENDENCY_MISSING", "AKSHARE_IMPORT_FAILED"} else None
    return ProviderResult(
        rows=[],
        attempt=make_attempt(
            provider_id,
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

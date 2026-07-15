from __future__ import annotations

import importlib
from types import SimpleNamespace

import ashare_premarket.providers.akshare_provider as akshare_provider
from ashare_premarket.providers.akshare_provider import (
    DEFAULT_PROVIDER_TIMEOUT_SECONDS,
    akshare_function_signatures,
    load_a_share_code_name_list,
    load_benchmark_ohlcv_daily,
    load_stock_ohlcv_daily,
)
from ashare_premarket.providers.schema_normalization import code_to_symbol, normalize_stock_ohlcv_schema, symbol_to_provider_code


def test_core_package_imports_without_forcing_akshare() -> None:
    module = importlib.import_module("ashare_premarket")
    assert module is not None


def test_provider_wrappers_do_not_call_network_when_disabled() -> None:
    code_names = load_a_share_code_name_list(network_enabled=False)
    stock = load_stock_ohlcv_daily("600036.SH", "2024-01-01", "2024-01-31", "qfq", network_enabled=False)
    benchmark = load_benchmark_ohlcv_daily("000300", "2024-01-01", "2024-01-31", network_enabled=False)
    assert code_names.attempt["failure_class"] == "NETWORK_DISABLED_BY_POLICY"
    assert stock.attempt["failure_class"] == "NETWORK_DISABLED_BY_POLICY"
    assert benchmark.attempt["failure_class"] == "NETWORK_DISABLED_BY_POLICY"


def test_akshare_signatures_are_runtime_introspected_when_available() -> None:
    signatures = akshare_function_signatures()
    assert isinstance(signatures, dict)


def test_schema_normalization_uses_canonical_english_fields() -> None:
    rows, schema_valid, _ = normalize_stock_ohlcv_schema(
        [{"日期": "2024-01-02", "开盘": 10, "最高": 11, "最低": 9, "收盘": 10.5, "成交量": 100, "成交额": 1000, "换手率": 1.2}],
        "600036.SH",
    )
    assert schema_valid
    assert rows[0]["trade_date"] == "2024-01-02"
    assert rows[0]["symbol"] == "600036.SH"
    assert code_to_symbol("600036") == "600036.SH"
    assert symbol_to_provider_code("600036.SH") == "600036"


def test_provider_call_passes_bounded_timeout(monkeypatch) -> None:
    received: dict[str, object] = {}

    def stock_zh_a_hist(symbol: str, timeout: int | None = None) -> list[dict[str, object]]:
        received.update(symbol=symbol, timeout=timeout)
        return [{"ok": True}]

    provider = SimpleNamespace(stock_zh_a_hist=stock_zh_a_hist)
    real_import = akshare_provider.importlib.import_module
    monkeypatch.setattr(akshare_provider, "akshare_available", lambda: True)
    monkeypatch.setattr(
        akshare_provider.importlib,
        "import_module",
        lambda name: provider if name == "akshare" else real_import(name),
    )

    result = akshare_provider._call(
        "stock_zh_a_hist",
        {"symbol": "600036"},
        True,
        lambda raw: (raw, True, "normalized"),
    )

    assert result.attempt["status"] == "PASS"
    assert received == {"symbol": "600036", "timeout": DEFAULT_PROVIDER_TIMEOUT_SECONDS}


def test_provider_failure_remains_failed_without_silent_fallback(monkeypatch) -> None:
    def stock_zh_a_hist(symbol: str, timeout: int | None = None) -> list[dict[str, object]]:
        raise RuntimeError("ProxyError: Cannot connect to proxy")

    provider = SimpleNamespace(stock_zh_a_hist=stock_zh_a_hist)
    real_import = akshare_provider.importlib.import_module
    monkeypatch.setattr(akshare_provider, "akshare_available", lambda: True)
    monkeypatch.setattr(
        akshare_provider.importlib,
        "import_module",
        lambda name: provider if name == "akshare" else real_import(name),
    )

    result = akshare_provider._call(
        "stock_zh_a_hist",
        {"symbol": "600036"},
        True,
        lambda raw: (raw, True, "normalized"),
    )

    assert result.rows == []
    assert result.raw is None
    assert result.attempt["status"] == "FAIL"
    assert result.attempt["failure_class"] == "FINANCE_DIRECT_CHILD_ENV_CLEANED_BUT_PROVIDER_STILL_PROXY_FAILED"

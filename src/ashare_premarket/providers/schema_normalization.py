from __future__ import annotations

from typing import Any

STOCK_COLUMNS = ["trade_date", "symbol", "open", "high", "low", "close", "volume", "amount", "turnover_rate", "source_id", "quality_flags"]
BENCHMARK_COLUMNS = ["trade_date", "benchmark_symbol", "open", "high", "low", "close", "volume", "amount", "source_id", "quality_flags"]


def normalize_stock_ohlcv_schema(data: Any, symbol: str, source_id: str = "akshare_stock_zh_a_hist") -> tuple[list[dict[str, object]], bool, str]:
    rows = _records(data)
    normalized = []
    for row in rows:
        trade_date = _value(row, ["日期", "date", "trade_date"])
        open_value = _value(row, ["开盘", "open"])
        close_value = _value(row, ["收盘", "close"])
        high_value = _value(row, ["最高", "high"])
        low_value = _value(row, ["最低", "low"])
        if trade_date in {"", None} or close_value in {"", None}:
            continue
        normalized.append(
            {
                "trade_date": str(trade_date)[:10],
                "symbol": symbol,
                "open": _float(open_value),
                "high": _float(high_value),
                "low": _float(low_value),
                "close": _float(close_value),
                "volume": _float(_value(row, ["成交量", "volume"], 0)),
                "amount": _float(_value(row, ["成交额", "amount"], 0)),
                "turnover_rate": _float(_value(row, ["换手率", "turnover_rate"], 0)),
                "source_id": source_id,
                "quality_flags": "SOURCE_BACKED",
            }
        )
    return normalized, bool(normalized), "normalized_stock_ohlcv" if normalized else "missing required stock OHLCV columns"


def normalize_benchmark_schema(data: Any, benchmark_symbol: str, source_id: str = "akshare_index_zh_a_hist") -> tuple[list[dict[str, object]], bool, str]:
    rows = _records(data)
    normalized = []
    for row in rows:
        trade_date = _value(row, ["日期", "date", "trade_date"])
        close_value = _value(row, ["收盘", "close"])
        if trade_date in {"", None} or close_value in {"", None}:
            continue
        normalized.append(
            {
                "trade_date": str(trade_date)[:10],
                "benchmark_symbol": benchmark_symbol,
                "open": _float(_value(row, ["开盘", "open"])),
                "high": _float(_value(row, ["最高", "high"])),
                "low": _float(_value(row, ["最低", "low"])),
                "close": _float(close_value),
                "volume": _float(_value(row, ["成交量", "volume"], 0)),
                "amount": _float(_value(row, ["成交额", "amount"], 0)),
                "source_id": source_id,
                "quality_flags": "SOURCE_BACKED",
            }
        )
    return normalized, bool(normalized), "normalized_benchmark_ohlcv" if normalized else "missing required benchmark OHLCV columns"


def normalize_code_name_schema(data: Any) -> tuple[list[dict[str, object]], bool, str]:
    rows = _records(data)
    normalized = []
    for row in rows:
        code = str(_value(row, ["code", "代码", "证券代码"], "")).zfill(6)
        name = str(_value(row, ["name", "名称", "证券简称"], ""))
        symbol = code_to_symbol(code)
        if symbol:
            normalized.append({"symbol": symbol, "code": code, "name": name, "source_id": "akshare_stock_info_a_code_name"})
    return normalized, bool(normalized), "normalized_code_name" if normalized else "missing code/name rows"


def normalize_spot_schema(data: Any) -> tuple[dict[str, dict[str, object]], bool, str]:
    rows = _records(data)
    lookup: dict[str, dict[str, object]] = {}
    for row in rows:
        code = str(_value(row, ["代码", "code", "证券代码"], "")).zfill(6)
        symbol = code_to_symbol(code)
        if not symbol:
            continue
        lookup[symbol] = {
            "symbol": symbol,
            "amount": _float(_value(row, ["成交额", "amount"], 0)),
            "volume": _float(_value(row, ["成交量", "volume"], 0)),
            "name": str(_value(row, ["名称", "name"], "")),
        }
    return lookup, bool(lookup), "normalized_spot" if lookup else "spot snapshot unavailable"


def code_to_symbol(code: str) -> str:
    if len(code) != 6 or not code.isdigit():
        return ""
    if code.startswith(("5", "6", "9")):
        return f"{code}.SH"
    if code.startswith(("0", "2", "3")):
        return f"{code}.SZ"
    if code.startswith(("4", "8")):
        return f"{code}.BJ"
    return ""


def symbol_to_provider_code(symbol: str) -> str:
    return symbol.split(".")[0]


def _records(data: Any) -> list[dict[str, Any]]:
    if data is None:
        return []
    if hasattr(data, "to_dict"):
        return list(data.to_dict("records"))
    if isinstance(data, list):
        return [dict(row) for row in data]
    return []


def _value(row: dict[str, Any], names: list[str], default: Any = "") -> Any:
    for name in names:
        if name in row:
            return row[name]
    return default


def _float(value: Any) -> float:
    try:
        if value in {"", None, "-"}:
            return 0.0
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return 0.0

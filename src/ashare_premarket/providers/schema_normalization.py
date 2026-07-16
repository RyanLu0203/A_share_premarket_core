from __future__ import annotations

from typing import Any

STOCK_COLUMNS = ["trade_date", "symbol", "open", "high", "low", "close", "volume", "amount", "turnover_rate", "source_id", "quality_flags"]
BENCHMARK_COLUMNS = ["trade_date", "benchmark_symbol", "open", "high", "low", "close", "volume", "amount", "source_id", "quality_flags"]


def normalize_stock_ohlcv_schema(data: Any, symbol: str, source_id: str = "akshare_stock_zh_a_hist") -> tuple[list[dict[str, object]], bool, str]:
    rows = _records(data)
    normalized = []
    for row in rows:
        trade_date = _value(row, ["日期", "date", "trade_date"])
        values = {
            "open": _strict_float(_value(row, ["开盘", "open"], None)),
            "high": _strict_float(_value(row, ["最高", "high"], None)),
            "low": _strict_float(_value(row, ["最低", "low"], None)),
            "close": _strict_float(_value(row, ["收盘", "close"], None)),
            "volume": _strict_float(_value(row, ["成交量", "volume"], None)),
        }
        if trade_date in {"", None} or any(value is None for value in values.values()):
            return [], False, "missing required East Money date/OHLCV fields"
        amount = _strict_float(_value(row, ["成交额", "amount"], None))
        turnover = _strict_float(_value(row, ["换手率", "turnover_rate"], None))
        quality_flags = ["SOURCE_BACKED"]
        if amount is None:
            quality_flags.append("AMOUNT_UNAVAILABLE")
        if turnover is None:
            quality_flags.append("TURNOVER_RATE_UNAVAILABLE")
        normalized.append(
            {
                "trade_date": str(trade_date)[:10],
                "symbol": symbol,
                **values,
                "amount": amount,
                "turnover_rate": turnover,
                "source_id": source_id,
                "quality_flags": ";".join(quality_flags),
            }
        )
    return normalized, bool(normalized), "normalized_stock_ohlcv" if normalized else "missing required stock OHLCV columns"


def normalize_tencent_stock_ohlcv_schema(
    data: Any,
    symbol: str,
    source_id: str = "akshare_stock_zh_a_hist_tx",
) -> tuple[list[dict[str, object]], bool, str]:
    """Normalize AKShare's Tencent history without misrepresenting field semantics.

    ``stock_zh_a_hist_tx`` exposes six columns and names the sixth ``amount``.
    AKShare documents that field in ``手`` and cross-source fixtures prove a
    scale-1 match to East Money's ``成交量``.  The official AKShare function
    discards Tencent's separate monetary-amount field, so canonical ``amount``
    is deliberately unavailable rather than guessed or zero-filled.
    """

    rows = _records(data)
    normalized: list[dict[str, object]] = []
    seen_dates: set[str] = set()
    for row in rows:
        trade_date = str(_value(row, ["date", "日期", "trade_date"], ""))[:10]
        values = {
            "open": _strict_float(_value(row, ["open", "开盘"], None)),
            "high": _strict_float(_value(row, ["high", "最高"], None)),
            "low": _strict_float(_value(row, ["low", "最低"], None)),
            "close": _strict_float(_value(row, ["close", "收盘"], None)),
            # AKShare's Tencent adapter mislabels this source volume column.
            "volume": _strict_float(_value(row, ["amount"], None)),
        }
        if not trade_date or any(value is None for value in values.values()):
            return [], False, "tencent_missing_required_date_ohlcv_or_source_volume"
        if trade_date in seen_dates:
            return [], False, f"tencent_duplicate_trade_date:{trade_date}"
        if values["close"] <= 0 or values["volume"] < 0:
            return [], False, f"tencent_invalid_price_or_volume:{trade_date}"
        seen_dates.add(trade_date)
        normalized.append(
            {
                "trade_date": trade_date,
                "symbol": symbol,
                **values,
                "amount": None,
                "turnover_rate": None,
                "source_id": source_id,
                "quality_flags": "SOURCE_BACKED;TENCENT_AMOUNT_UNAVAILABLE",
                "source_volume_field": "akshare_amount_mislabeled_as_amount",
                "volume_semantics": "tencent_volume_unit_hand_scale_1_to_eastmoney_volume",
                "amount_semantics": "unavailable_from_stock_zh_a_hist_tx",
            }
        )
    normalized.sort(key=lambda row: str(row["trade_date"]))
    return (
        normalized,
        bool(normalized),
        "normalized_tencent_stock_ohlcv;amount_unavailable_from_official_akshare_function"
        if normalized
        else "missing required Tencent stock OHLCV rows",
    )


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


def _strict_float(value: Any) -> float | None:
    try:
        if value in {"", None, "-"}:
            return None
        parsed = float(str(value).replace(",", ""))
        return parsed if parsed == parsed and parsed not in {float("inf"), float("-inf")} else None
    except (TypeError, ValueError):
        return None

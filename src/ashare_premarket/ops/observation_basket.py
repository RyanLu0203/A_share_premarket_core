from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from ashare_premarket.core.io import write_json
from ashare_premarket.providers.akshare_provider import load_stock_ohlcv_daily, load_stock_ohlcv_daily_sina
from ashare_premarket.providers.provider_registry import network_enabled


OBSERVATION_EVIDENCE = "outputs/local/runtime/observation_basket.json"


def refresh_observation_basket(
    root: Path,
    symbols: list[str],
    fetch_start: str,
    expected_date: str,
    allow_network: bool = False,
) -> dict[str, object]:
    if not network_enabled(allow_network):
        raise RuntimeError("network authorization is required for observation refresh")
    rows: list[dict[str, object]] = []
    for symbol in sorted({value.strip().upper() for value in symbols if value.strip()}):
        primary = load_stock_ohlcv_daily(symbol, fetch_start, expected_date, "qfq", True)
        selected = primary
        provider = "akshare"
        if not _has_date(selected.rows, expected_date):
            selected = load_stock_ohlcv_daily_sina(symbol, fetch_start, expected_date, "qfq", True)
            provider = "akshare_sina"
        ordered = sorted(selected.rows, key=lambda row: str(row.get("trade_date", "")))
        target = next((row for row in ordered if str(row.get("trade_date")) == expected_date), None)
        prior = [row for row in ordered if str(row.get("trade_date", "")) < expected_date]
        close = _number(target.get("close")) if target else None
        previous_close = _number(prior[-1].get("close")) if prior else None
        daily_return = close / previous_close - 1.0 if close is not None and previous_close else None
        rows.append(
            {
                "symbol": symbol,
                "trade_date": expected_date if target else "",
                "close": close,
                "return_1d": daily_return,
                "selected_provider": provider,
                "selected_status": selected.attempt.get("status"),
                "primary_status": primary.attempt.get("status"),
                "primary_failure_class": primary.attempt.get("failure_class"),
                "observation_status": "AVAILABLE" if target and close is not None else "UNAVAILABLE",
                "research_only": True,
                "not_for_execution": True,
            }
        )
    payload: dict[str, object] = {
        "generated_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds"),
        "expected_date": expected_date,
        "source_scope": "bounded_daily_observation_only",
        "rows": rows,
        "research_only": True,
        "not_for_execution": True,
        "positions_created": False,
        "recommendations_created": False,
    }
    write_json(root / OBSERVATION_EVIDENCE, payload)
    return payload


def _has_date(rows: list[dict[str, object]], value: str) -> bool:
    return any(str(row.get("trade_date")) == value for row in rows)


def _number(value: object) -> float | None:
    try:
        result = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return result

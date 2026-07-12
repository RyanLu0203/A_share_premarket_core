from __future__ import annotations

from datetime import date, datetime, timedelta
import importlib
from pathlib import Path
from zoneinfo import ZoneInfo

from ashare_premarket.core.io import read_csv, write_csv, write_json
from ashare_premarket.providers.provider_registry import network_enabled


RUNTIME_CALENDAR = "outputs/local/runtime/trading_calendar.csv"
RUNTIME_CALENDAR_METADATA = "outputs/local/runtime/trading_calendar_metadata.json"
CALENDAR_FIELDS = ["date", "is_trading_day", "session_note"]


def sync_runtime_trading_calendar(root: Path, allow_network: bool = False) -> Path:
    """Build a source-backed local calendar without mutating committed config."""
    root = root.resolve()
    if not network_enabled(allow_network):
        raise RuntimeError("network authorization is required to sync the runtime trading calendar")
    akshare = importlib.import_module("akshare")
    raw = akshare.tool_trade_date_hist_sina()
    records = raw.to_dict("records") if hasattr(raw, "to_dict") else []
    trading_dates = sorted({str(row.get("trade_date", ""))[:10] for row in records if row.get("trade_date")})
    if not trading_dates:
        raise RuntimeError("AKShare/Sina returned no trading-calendar dates")

    committed_path = root / "configs/project/trading_calendar.csv"
    committed = read_csv(committed_path)
    start = date.fromisoformat(committed[0]["date"])
    source_end = date.fromisoformat(trading_dates[-1])
    trading_set = set(trading_dates)
    rows: list[dict[str, object]] = []
    current = start
    while current <= source_end:
        value = current.isoformat()
        if value in trading_set:
            rows.append({"date": value, "is_trading_day": True, "session_note": "regular_source_akshare_sina"})
        elif current.weekday() >= 5:
            rows.append({"date": value, "is_trading_day": False, "session_note": "weekend"})
        else:
            rows.append({"date": value, "is_trading_day": False, "session_note": "exchange_closed_source_calendar"})
        current += timedelta(days=1)

    output = root / RUNTIME_CALENDAR
    write_csv(output, rows, CALENDAR_FIELDS)
    generated_at = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")
    write_json(
        root / RUNTIME_CALENDAR_METADATA,
        {
            "generated_at": generated_at,
            "provider": "akshare_sina",
            "function": "tool_trade_date_hist_sina",
            "first_date": rows[0]["date"],
            "last_date": rows[-1]["date"],
            "row_count": len(rows),
            "research_only": True,
        },
    )
    return output

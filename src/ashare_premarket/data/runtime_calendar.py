from __future__ import annotations

import csv
from datetime import date, datetime
import hashlib
import importlib
import json
import os
from pathlib import Path
import tempfile
from zoneinfo import ZoneInfo

from ashare_premarket.providers.network_isolation import scoped_finance_network_env
from ashare_premarket.providers.provider_registry import network_enabled


RUNTIME_CALENDAR = "outputs/local/runtime/trading_calendar.csv"
RUNTIME_CALENDAR_METADATA = "outputs/local/runtime/trading_calendar_metadata.json"
CALENDAR_FIELDS = ["date", "is_trading_day", "session_note"]
APPROVED_PROVIDER = "akshare_sina"
APPROVED_FUNCTION = "tool_trade_date_hist_sina"


def sync_runtime_trading_calendar(root: Path, allow_network: bool = False) -> Path:
    """Atomically persist an approved-source calendar without changing committed evidence."""

    root = root.resolve()
    if not network_enabled(allow_network):
        raise RuntimeError("network authorization is required to sync the runtime trading calendar")
    try:
        akshare = importlib.import_module("akshare")
        with scoped_finance_network_env(APPROVED_FUNCTION, network_enabled=True):
            raw = getattr(akshare, APPROVED_FUNCTION)()
    except Exception as exc:
        raise RuntimeError(f"approved trading-calendar source unavailable: {type(exc).__name__}") from exc

    records = raw.to_dict("records") if hasattr(raw, "to_dict") else []
    trading_dates = sorted({_date_text(row.get("trade_date")) for row in records if row.get("trade_date") is not None})
    trading_dates = [value for value in trading_dates if value]
    if not trading_dates:
        raise RuntimeError("approved trading-calendar source returned no valid dates")

    committed = _read_rows(root / "configs/project/trading_calendar.csv")
    committed_trading = {row["date"] for row in committed if row.get("is_trading_day") == "true"}
    committed_fixture_conflicts = sorted(committed_trading - set(trading_dates))

    rows = [
        {
            "date": value,
            "is_trading_day": "true",
            "session_note": "regular_source_akshare_sina",
        }
        for value in trading_dates
    ]
    csv_body = _csv_text(rows)
    checksum = hashlib.sha256(csv_body.encode("utf-8")).hexdigest()
    metadata = {
        "status": "VERIFIED",
        "generated_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds"),
        "provider": APPROVED_PROVIDER,
        "function": APPROVED_FUNCTION,
        "approved_evidence_source": True,
        "runtime_authority": "approved_provider_schedule",
        "committed_fixture_role": "deterministic_research_fixture_non_authoritative_for_runtime_schedule",
        "committed_fixture_consistency_status": (
            "MATCH" if not committed_fixture_conflicts else "DIFFERENCES_RECORDED_NON_AUTHORITATIVE"
        ),
        "committed_fixture_conflict_count": len(committed_fixture_conflicts),
        "committed_fixture_conflict_dates": committed_fixture_conflicts,
        "coverage_start": trading_dates[0],
        "coverage_end": trading_dates[-1],
        "latest_confirmed_trading_day": trading_dates[-1],
        "source_observation_count": len(records),
        "calendar_row_count": len(rows),
        "calendar_checksum_sha256": checksum,
        "pit_semantics": "exchange_schedule_evidence_only_no_market_observation_or_future_return",
        "research_only": True,
        "not_for_execution": True,
    }

    output = root / RUNTIME_CALENDAR
    metadata_path = root / RUNTIME_CALENDAR_METADATA
    output.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(output, csv_body)
    _atomic_write(metadata_path, json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    return output


def runtime_calendar_environment(root: Path) -> dict[str, str]:
    root = root.resolve()
    return {
        "ASHARE_TRADING_CALENDAR_PATH": str(root / RUNTIME_CALENDAR),
        "ASHARE_TRADING_CALENDAR_METADATA_PATH": str(root / RUNTIME_CALENDAR_METADATA),
    }


def _date_text(value: object) -> str:
    candidate = str(value)[:10]
    try:
        return date.fromisoformat(candidate).isoformat()
    except ValueError:
        return ""


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _csv_text(rows: list[dict[str, str]]) -> str:
    from io import StringIO

    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=CALENDAR_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def _atomic_write(path: Path, body: str) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        Path(temporary).replace(path)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise

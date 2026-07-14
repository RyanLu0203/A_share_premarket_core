from __future__ import annotations

from datetime import date
import hashlib
import json
import os
from pathlib import Path

from ashare_premarket.core.io import read_csv
from ashare_premarket.data.runtime_calendar import (
    APPROVED_FUNCTION,
    APPROVED_PROVIDER,
    RUNTIME_CALENDAR,
    RUNTIME_CALENDAR_METADATA,
)


class CalendarEvidenceError(ValueError):
    """Raised when configured calendar evidence is unavailable or invalid."""


def trading_calendar(root: Path) -> list[dict[str, str]]:
    path, metadata = _calendar_paths(root)
    rows = read_csv(path)
    _validate_rows(rows)
    if metadata is not None:
        _validate_runtime_metadata(path, metadata, rows)
    return rows


def trading_calendar_status(root: Path, required_date: str | None = None) -> dict[str, object]:
    try:
        path, metadata = _calendar_paths(root)
        rows = read_csv(path)
        _validate_rows(rows)
        payload = _validate_runtime_metadata(path, metadata, rows) if metadata is not None else {}
        coverage_start = rows[0]["date"]
        coverage_end = rows[-1]["date"]
        coverage_ok = not required_date or required_date <= coverage_end
        return {
            "status": "VERIFIED" if coverage_ok else "BLOCKED",
            "freshness_status": "CURRENT" if coverage_ok else "COVERAGE_MISSING",
            "reason": "" if coverage_ok else "TRADING_CALENDAR_COVERAGE_MISSING",
            "source": payload.get("provider", "committed_calendar"),
            "function": payload.get("function", "committed_evidence"),
            "path": path.relative_to(root.resolve()).as_posix(),
            "coverage_start": coverage_start,
            "coverage_end": coverage_end,
            "latest_confirmed_trading_day": max(
                row["date"] for row in rows if row["is_trading_day"] == "true"
            ),
            "checksum_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "generated_at": payload.get("generated_at", "committed"),
            "pit_status": "PASSED_SCHEDULE_EVIDENCE_ONLY",
            "runtime_authority": payload.get("runtime_authority", "committed_fixture"),
            "committed_fixture_consistency_status": payload.get(
                "committed_fixture_consistency_status", "NOT_APPLICABLE"
            ),
            "committed_fixture_conflict_count": payload.get("committed_fixture_conflict_count", 0),
            "committed_fixture_conflict_dates": payload.get("committed_fixture_conflict_dates", []),
        }
    except (CalendarEvidenceError, OSError, json.JSONDecodeError) as exc:
        return {
            "status": "BLOCKED",
            "freshness_status": "INVALID_OR_UNAVAILABLE",
            "reason": "TRADING_CALENDAR_EVIDENCE_INVALID",
            "detail": str(exc),
            "source": "unavailable",
            "coverage_start": "",
            "coverage_end": "",
            "latest_confirmed_trading_day": "",
            "pit_status": "FAIL_CLOSED",
        }


def is_trading_day(root: Path, value: str) -> bool:
    for row in trading_calendar(root):
        if row["date"] == value:
            return row["is_trading_day"] == "true"
    return False


def next_trading_day(root: Path, value: str) -> str:
    current = date.fromisoformat(value)
    for row in trading_calendar(root):
        candidate = date.fromisoformat(row["date"])
        if candidate > current and row["is_trading_day"] == "true":
            return row["date"]
    raise ValueError(f"No next trading day configured after {value}")


def previous_trading_day(root: Path, value: str) -> str:
    current = date.fromisoformat(value)
    for row in reversed(trading_calendar(root)):
        candidate = date.fromisoformat(row["date"])
        if candidate < current and row["is_trading_day"] == "true":
            return row["date"]
    raise ValueError(f"No previous trading day configured before {value}")


def resolve_target_trading_day(root: Path, execution_date: str) -> str:
    if is_trading_day(root, execution_date):
        return execution_date
    return next_trading_day(root, execution_date)


def _calendar_paths(root: Path) -> tuple[Path, Path | None]:
    resolved_root = root.resolve()
    configured = os.environ.get("ASHARE_TRADING_CALENDAR_PATH", "").strip()
    if not configured:
        return resolved_root / "configs/project/trading_calendar.csv", None
    candidate = _confined_path(resolved_root, configured)
    if not candidate.exists():
        raise CalendarEvidenceError("configured runtime trading calendar is unavailable")
    configured_metadata = os.environ.get("ASHARE_TRADING_CALENDAR_METADATA_PATH", "").strip()
    if configured_metadata:
        metadata = _confined_path(resolved_root, configured_metadata)
    elif candidate == resolved_root / RUNTIME_CALENDAR:
        metadata = resolved_root / RUNTIME_CALENDAR_METADATA
    else:
        raise CalendarEvidenceError("configured runtime trading calendar requires metadata")
    if not metadata.exists():
        raise CalendarEvidenceError("runtime trading calendar metadata is unavailable")
    return candidate, metadata


def _confined_path(root: Path, value: str) -> Path:
    candidate = Path(value)
    candidate = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    if candidate != root and root not in candidate.parents:
        raise CalendarEvidenceError("runtime trading calendar evidence must remain inside repository root")
    return candidate


def _validate_rows(rows: list[dict[str, str]]) -> None:
    if not rows:
        raise CalendarEvidenceError("trading calendar has no rows")
    dates = [row.get("date", "") for row in rows]
    if dates != sorted(set(dates)):
        raise CalendarEvidenceError("trading calendar dates must be sorted and unique")
    for row in rows:
        try:
            date.fromisoformat(row.get("date", ""))
        except ValueError as exc:
            raise CalendarEvidenceError("trading calendar contains an invalid date") from exc
        if row.get("is_trading_day") not in {"true", "false"}:
            raise CalendarEvidenceError("trading calendar contains an invalid trading-day flag")
    if not any(row["is_trading_day"] == "true" for row in rows):
        raise CalendarEvidenceError("trading calendar contains no confirmed trading days")


def _validate_runtime_metadata(path: Path, metadata_path: Path, rows: list[dict[str, str]]) -> dict[str, object]:
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    failures = []
    if payload.get("status") != "VERIFIED":
        failures.append("status")
    if payload.get("provider") != APPROVED_PROVIDER or payload.get("function") != APPROVED_FUNCTION:
        failures.append("approved_source")
    if payload.get("runtime_authority") != "approved_provider_schedule":
        failures.append("runtime_authority")
    if payload.get("calendar_checksum_sha256") != actual:
        failures.append("checksum")
    if payload.get("coverage_start") != rows[0]["date"] or payload.get("coverage_end") != rows[-1]["date"]:
        failures.append("coverage")
    if payload.get("calendar_row_count") != len(rows):
        failures.append("row_count")
    conflicts = payload.get("committed_fixture_conflict_dates")
    if not isinstance(conflicts, list) or payload.get("committed_fixture_conflict_count") != len(conflicts):
        failures.append("committed_fixture_conflicts")
    consistency = payload.get("committed_fixture_consistency_status")
    expected_consistency = "MATCH" if not conflicts else "DIFFERENCES_RECORDED_NON_AUTHORITATIVE"
    if consistency != expected_consistency:
        failures.append("committed_fixture_consistency")
    if any(row["is_trading_day"] != "true" for row in rows):
        failures.append("source_calendar_contains_inferred_session")
    if failures:
        raise CalendarEvidenceError(f"runtime trading calendar validation failed: {','.join(failures)}")
    return payload

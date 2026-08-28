"""Fail-closed PIT availability rules for future liquidity evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

SHANGHAI = ZoneInfo("Asia/Shanghai")
SUPPORTED_PROVIDERS = {
    "tushare_pro.daily_basic",
    "baostock.query_history_k_data_plus",
}


@dataclass(frozen=True)
class AvailabilityDecision:
    status: str
    reason: str
    available_at_utc: str | None


def validate_explicit_availability(
    *,
    provider_endpoint: str,
    trade_date: str,
    provider_available_at: str | None,
    decision_cutoff: str,
) -> AvailabilityDecision:
    """Accept only an explicit, timezone-aware timestamp available by cutoff."""

    if provider_endpoint not in SUPPORTED_PROVIDERS:
        return AvailabilityDecision("BLOCKED", "UNSUPPORTED_PROVIDER_ENDPOINT", None)
    if not provider_available_at:
        return AvailabilityDecision("BLOCKED", "ROW_AVAILABLE_AT_MISSING", None)

    try:
        session_date = date.fromisoformat(trade_date)
        available_at = datetime.fromisoformat(provider_available_at)
        cutoff = datetime.fromisoformat(decision_cutoff)
    except ValueError:
        return AvailabilityDecision("BLOCKED", "INVALID_DATE_OR_TIMESTAMP", None)

    if available_at.tzinfo is None or cutoff.tzinfo is None:
        return AvailabilityDecision("BLOCKED", "NAIVE_TIMESTAMP_FORBIDDEN", None)

    local_available = available_at.astimezone(SHANGHAI)
    earliest = datetime.combine(session_date, time(15, 0), tzinfo=SHANGHAI)
    if local_available < earliest:
        return AvailabilityDecision("BLOCKED", "AVAILABLE_BEFORE_SESSION_CLOSE", None)
    if available_at > cutoff:
        return AvailabilityDecision("BLOCKED", "AVAILABLE_AFTER_DECISION_CUTOFF", None)

    return AvailabilityDecision(
        "ACCEPTED_FOR_PIT_REVIEW",
        "EXPLICIT_PROVIDER_TIMESTAMP_WITHIN_CUTOFF",
        available_at.astimezone(ZoneInfo("UTC")).isoformat(),
    )


def documented_provider_contracts() -> list[dict[str, str]]:
    """Describe current documentation evidence without inventing availability."""

    return [
        {
            "provider_endpoint": "tushare_pro.daily_basic",
            "documentation_time_evidence": "trade_day_update_window_15_00_to_17_00",
            "row_available_at_supplied": "false",
            "window_to_row_timestamp_inference_allowed": "false",
            "current_pit_state": "BLOCKED_ROW_AVAILABLE_AT_MISSING",
        },
        {
            "provider_endpoint": "baostock.query_history_k_data_plus",
            "documentation_time_evidence": "no_accepted_row_level_timestamp",
            "row_available_at_supplied": "false",
            "window_to_row_timestamp_inference_allowed": "false",
            "current_pit_state": "BLOCKED_ROW_AVAILABLE_AT_MISSING",
        },
    ]

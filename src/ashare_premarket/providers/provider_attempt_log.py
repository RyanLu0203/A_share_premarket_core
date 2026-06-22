from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.io import write_csv

ATTEMPT_FIELDS = [
    "provider_id",
    "function_name",
    "symbol",
    "date_start",
    "date_end",
    "attempt_ts",
    "network_enabled",
    "status",
    "failure_class",
    "http_status_if_available",
    "response_type_if_available",
    "rows_returned",
    "schema_valid",
    "retry_allowed",
    "fallback_provider",
    "notes",
]


def make_attempt(
    provider_id: str,
    function_name: str,
    symbol: str = "",
    date_start: str = "",
    date_end: str = "",
    network_enabled: bool = False,
    status: str = "FAIL",
    failure_class: str = "UNKNOWN_PROVIDER_FAILURE",
    rows_returned: int = 0,
    schema_valid: bool = False,
    retry_allowed: bool = False,
    response_type: str = "",
    http_status: str = "",
    fallback_provider: str = "",
    notes: str = "",
) -> dict[str, object]:
    return {
        "provider_id": provider_id,
        "function_name": function_name,
        "symbol": symbol,
        "date_start": date_start,
        "date_end": date_end,
        "attempt_ts": "local_runtime",
        "network_enabled": network_enabled,
        "status": status,
        "failure_class": failure_class,
        "http_status_if_available": http_status,
        "response_type_if_available": response_type,
        "rows_returned": rows_returned,
        "schema_valid": schema_valid,
        "retry_allowed": retry_allowed,
        "fallback_provider": fallback_provider,
        "notes": notes,
    }


def write_provider_attempt_log(path: Path, rows: list[dict[str, object]]) -> Path:
    write_csv(path, rows, ATTEMPT_FIELDS)
    return path


def write_provider_attempt_summary(root: Path, rows: list[dict[str, object]]) -> Path:
    path = root / "outputs/audits/akshare_provider_attempt_summary.csv"
    write_provider_attempt_log(path, rows)
    return path

from __future__ import annotations

from pathlib import Path
import json

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
    "request_sequence",
    "batch_request_sequence",
    "market_exchange",
    "endpoint_family",
    "elapsed_seconds",
    "response_byte_length_if_available",
    "latest_returned_trade_date",
    "exception_type",
    "terminal_exception_message",
    "retry_count",
    "accepted",
    "rejection_reason",
    "upstream_source",
    "akshare_version",
    "request_parameters",
    "network_context",
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
    attempt_ts: str = "local_runtime",
    elapsed_seconds: float = 0.0,
    request_parameters: dict[str, object] | None = None,
    endpoint_family: object = "",
    akshare_version: str = "",
    exception_type: str = "",
    terminal_exception_message: str = "",
    network_context: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "provider_id": provider_id,
        "function_name": function_name,
        "symbol": symbol,
        "date_start": date_start,
        "date_end": date_end,
        "attempt_ts": attempt_ts,
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
        "request_sequence": "",
        "batch_request_sequence": "",
        "market_exchange": symbol.partition(".")[2],
        "endpoint_family": endpoint_family,
        "elapsed_seconds": elapsed_seconds,
        "response_byte_length_if_available": "unavailable_at_akshare_dataframe_boundary",
        "latest_returned_trade_date": "",
        "exception_type": exception_type,
        "terminal_exception_message": terminal_exception_message,
        "retry_count": 0,
        "accepted": status == "PASS",
        "rejection_reason": "" if status == "PASS" else failure_class,
        "upstream_source": "Tencent" if function_name == "stock_zh_a_hist_tx" else "East Money" if function_name == "stock_zh_a_hist" else "",
        "akshare_version": akshare_version,
        "request_parameters": json.dumps(request_parameters or {}, sort_keys=True, separators=(",", ":")),
        "network_context": json.dumps(network_context or {}, sort_keys=True, separators=(",", ":")),
    }


def write_provider_attempt_log(path: Path, rows: list[dict[str, object]]) -> Path:
    write_csv(path, rows, ATTEMPT_FIELDS)
    return path


def write_provider_attempt_summary(root: Path, rows: list[dict[str, object]]) -> Path:
    path = root / "outputs/audits/akshare_provider_attempt_summary.csv"
    write_provider_attempt_log(path, rows)
    return path

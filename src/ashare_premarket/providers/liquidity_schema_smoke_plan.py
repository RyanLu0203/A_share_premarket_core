"""Pure-data plan for a future bounded liquidity provider schema smoke.

This module deliberately contains no provider client, credential lookup, network
transport, or execution function.  It describes the only four calls that a
separately authorized runner may make in a future goal.
"""

from __future__ import annotations

from collections import Counter
from typing import Mapping

GOAL_ID = "GOAL-LIQUIDITY-SCHEMA-SMOKE-PLAN-01"
SYMBOLS = ("002475.SZ", "600036.SH")
PROVIDERS = ("tushare_pro", "baostock")
TOTAL_CALL_BUDGET = 4
MAX_CALLS_PER_PROVIDER_SYMBOL = 1
MAX_RETRIES_PER_CALL = 0
PROVIDER_CALLS_AUTHORIZED = False

FAILURE_TAXONOMY = (
    "NOT_AUTHORIZED",
    "CLIENT_UNAVAILABLE",
    "CREDENTIAL_UNAVAILABLE",
    "AUTHENTICATION_FAILED",
    "ENTITLEMENT_DENIED",
    "DNS_FAILURE",
    "CONNECT_TIMEOUT",
    "READ_TIMEOUT",
    "TLS_FAILURE",
    "RATE_LIMITED",
    "PROVIDER_SERVICE_ERROR",
    "EMPTY_RESPONSE",
    "EXPECTED_FIELD_MISSING",
    "UNEXPECTED_FIELD_SET",
    "OUT_OF_SCOPE_SYMBOL",
    "ROW_BUDGET_EXCEEDED",
    "UNSANITIZED_METADATA",
)

SCHEMA_FIXTURE_ACCEPTED = "SYNTHETIC_CONTRACT_FIXTURE_ACCEPTED_NOT_LIVE_VERIFIED"

_EXPECTED_SCHEMAS = {
    "tushare_pro": {
        "endpoint": "daily_basic",
        "expected_fields": (
            "ts_code",
            "trade_date",
            "turnover_rate",
            "turnover_rate_f",
            "float_share",
            "free_share",
        ),
        "units": {
            "ts_code": "provider_security_code",
            "trade_date": "YYYYMMDD",
            "turnover_rate": "percent",
            "turnover_rate_f": "percent",
            "float_share": "ten_thousand_shares",
            "free_share": "ten_thousand_shares",
        },
    },
    "baostock": {
        "endpoint": "query_history_k_data_plus",
        "expected_fields": (
            "date",
            "code",
            "volume",
            "adjustflag",
            "turn",
            "tradestatus",
        ),
        "units": {
            "date": "YYYY-MM-DD",
            "code": "provider_security_code",
            "volume": "shares",
            "adjustflag": "enum_1_hfq_2_qfq_3_none",
            "turn": "percent",
            "tradestatus": "enum_0_suspended_1_trading",
        },
    },
}

_BAOSTOCK_SYMBOLS = {
    "002475.SZ": "sz.002475",
    "600036.SH": "sh.600036",
}

SANITIZED_METADATA_FIELDS = (
    "call_id",
    "provider",
    "endpoint",
    "canonical_symbol",
    "provider_symbol",
    "attempted",
    "call_count",
    "retry_count",
    "status",
    "failure_code",
    "observed_field_names",
    "observed_row_count",
)


def schema_smoke_calls() -> tuple[dict[str, object], ...]:
    """Return the fixed, unauthorized four-call plan as pure metadata."""

    calls: list[dict[str, object]] = []
    for provider in PROVIDERS:
        schema = _EXPECTED_SCHEMAS[provider]
        for symbol in SYMBOLS:
            provider_symbol = (
                symbol if provider == "tushare_pro" else _BAOSTOCK_SYMBOLS[symbol]
            )
            calls.append(
                {
                    "call_id": f"{provider}:{schema['endpoint']}:{symbol}",
                    "provider": provider,
                    "endpoint": schema["endpoint"],
                    "canonical_symbol": symbol,
                    "provider_symbol": provider_symbol,
                    "expected_fields": schema["expected_fields"],
                    "units": dict(schema["units"]),
                    "max_calls": MAX_CALLS_PER_PROVIDER_SYMBOL,
                    "max_retries": MAX_RETRIES_PER_CALL,
                    "provider_calls_authorized": PROVIDER_CALLS_AUTHORIZED,
                    "raw_payload_persistence_allowed": False,
                }
            )
    return tuple(calls)


def validate_plan(calls: tuple[Mapping[str, object], ...] | None = None) -> bool:
    """Fail closed unless the plan is exactly the governed four-call matrix."""

    planned = calls if calls is not None else schema_smoke_calls()
    if len(planned) != TOTAL_CALL_BUDGET:
        return False
    pairs = Counter(
        (str(call.get("provider")), str(call.get("canonical_symbol")))
        for call in planned
    )
    expected_pairs = {(provider, symbol) for provider in PROVIDERS for symbol in SYMBOLS}
    return (
        set(pairs) == expected_pairs
        and all(count == MAX_CALLS_PER_PROVIDER_SYMBOL for count in pairs.values())
        and all(call.get("max_retries") == 0 for call in planned)
        and all(call.get("provider_calls_authorized") is False for call in planned)
        and all(call.get("raw_payload_persistence_allowed") is False for call in planned)
    )


def sanitized_observation_template(call: Mapping[str, object]) -> dict[str, object]:
    """Build the only metadata shape that a future runner may persist."""

    if call.get("call_id") not in {item["call_id"] for item in schema_smoke_calls()}:
        raise ValueError("OUT_OF_SCOPE_CALL")
    return {
        "call_id": call["call_id"],
        "provider": call["provider"],
        "endpoint": call["endpoint"],
        "canonical_symbol": call["canonical_symbol"],
        "provider_symbol": call["provider_symbol"],
        "attempted": False,
        "call_count": 0,
        "retry_count": 0,
        "status": "NOT_AUTHORIZED",
        "failure_code": "NOT_AUTHORIZED",
        "observed_field_names": (),
        "observed_row_count": 0,
    }


def validate_sanitized_metadata(metadata: Mapping[str, object]) -> bool:
    """Accept allowlisted schema observations only; raw values are forbidden."""

    return (
        set(metadata) == set(SANITIZED_METADATA_FIELDS)
        and metadata.get("failure_code") in FAILURE_TAXONOMY
        and isinstance(metadata.get("observed_field_names"), (tuple, list))
        and isinstance(metadata.get("observed_row_count"), int)
        and int(metadata.get("observed_row_count", -1)) >= 0
        and metadata.get("retry_count") == 0
        and metadata.get("call_count") in {0, 1}
    )


def evaluate_observed_field_names(
    provider: str,
    observed_field_names: object,
) -> dict[str, object]:
    """Evaluate field names only, without accepting values or live schema proof.

    This supports sanitized synthetic fixtures and future live smoke metadata.
    Passing a synthetic fixture proves parser-contract readiness only; it never
    changes ``provider_calls_authorized`` or live verification state.
    """

    if provider not in _EXPECTED_SCHEMAS:
        raise ValueError("UNKNOWN_PROVIDER")
    if not isinstance(observed_field_names, (tuple, list)) or any(
        not isinstance(field, str) or not field or field != field.strip()
        for field in observed_field_names
    ):
        raise ValueError("INVALID_FIELD_NAME_LIST")
    observed = tuple(observed_field_names)
    if len(observed) != len(set(observed)):
        raise ValueError("DUPLICATE_FIELD_NAME")
    expected = set(_EXPECTED_SCHEMAS[provider]["expected_fields"])
    actual = set(observed)
    missing = tuple(sorted(expected - actual))
    unexpected = tuple(sorted(actual - expected))
    if missing:
        status = "EXPECTED_FIELD_MISSING"
    elif unexpected:
        status = "UNEXPECTED_FIELD_SET"
    else:
        status = SCHEMA_FIXTURE_ACCEPTED
    return {
        "provider": provider,
        "status": status,
        "expected_field_names": tuple(sorted(expected)),
        "observed_field_names": tuple(sorted(actual)),
        "missing_field_names": missing,
        "unexpected_field_names": unexpected,
        "live_schema_verified": False,
        "provider_calls_authorized": False,
    }

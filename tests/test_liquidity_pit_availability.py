from ashare_premarket.providers.liquidity_pit_availability import (
    documented_provider_contracts,
    validate_explicit_availability,
)


def test_missing_and_naive_availability_fail_closed() -> None:
    missing = validate_explicit_availability(
        provider_endpoint="tushare_pro.daily_basic",
        trade_date="2026-08-28",
        provider_available_at=None,
        decision_cutoff="2026-08-29T08:30:00+08:00",
    )
    assert missing.status == "BLOCKED"
    assert missing.reason == "ROW_AVAILABLE_AT_MISSING"

    naive = validate_explicit_availability(
        provider_endpoint="tushare_pro.daily_basic",
        trade_date="2026-08-28",
        provider_available_at="2026-08-28T16:00:00",
        decision_cutoff="2026-08-29T08:30:00+08:00",
    )
    assert naive.reason == "NAIVE_TIMESTAMP_FORBIDDEN"


def test_explicit_timestamp_must_be_after_close_and_before_cutoff() -> None:
    accepted = validate_explicit_availability(
        provider_endpoint="tushare_pro.daily_basic",
        trade_date="2026-08-28",
        provider_available_at="2026-08-28T16:00:00+08:00",
        decision_cutoff="2026-08-29T08:30:00+08:00",
    )
    assert accepted.status == "ACCEPTED_FOR_PIT_REVIEW"
    assert accepted.available_at_utc == "2026-08-28T08:00:00+00:00"

    too_early = validate_explicit_availability(
        provider_endpoint="baostock.query_history_k_data_plus",
        trade_date="2026-08-28",
        provider_available_at="2026-08-28T14:59:59+08:00",
        decision_cutoff="2026-08-29T08:30:00+08:00",
    )
    assert too_early.reason == "AVAILABLE_BEFORE_SESSION_CLOSE"

    too_late = validate_explicit_availability(
        provider_endpoint="baostock.query_history_k_data_plus",
        trade_date="2026-08-28",
        provider_available_at="2026-08-29T09:00:00+08:00",
        decision_cutoff="2026-08-29T08:30:00+08:00",
    )
    assert too_late.reason == "AVAILABLE_AFTER_DECISION_CUTOFF"


def test_documented_windows_are_not_silently_promoted() -> None:
    rows = documented_provider_contracts()
    assert len(rows) == 2
    assert all(row["row_available_at_supplied"] == "false" for row in rows)
    assert all(
        row["window_to_row_timestamp_inference_allowed"] == "false" for row in rows
    )

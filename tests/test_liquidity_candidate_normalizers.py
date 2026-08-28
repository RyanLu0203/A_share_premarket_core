from datetime import datetime, timezone

import pytest

from ashare_premarket.providers.liquidity_candidate_normalizers import (
    LiquidityCandidateNormalizationError,
    normalize_baostock_history_row,
    normalize_tushare_daily_basic_row,
)


def test_tushare_daily_basic_units_and_explicit_availability() -> None:
    row = normalize_tushare_daily_basic_row(
        {
            "ts_code": "002475.SZ",
            "trade_date": "20260827",
            "free_share": "123.4567",
            "turnover_rate_f": "1.25",
        },
        available_at="2026-08-27T15:30:00+08:00",
        expected_symbol="002475.SZ",
        expected_trade_date="2026-08-27",
    )

    assert row == {
        "symbol": "002475.SZ",
        "trade_date": "2026-08-27",
        "free_float_shares": 1_234_567,
        "turnover_rate": 0.0125,
        "source_provider": "tushare_pro.daily_basic",
        "available_at": "2026-08-27T15:30:00+08:00",
    }


def test_baostock_units_status_and_qfq_mapping() -> None:
    trading = normalize_baostock_history_row(
        {
            "code": "sh.600036",
            "date": "2026-08-27",
            "volume": "123400",
            "turn": "2.5",
            "tradestatus": "1",
            "adjustflag": "2",
        },
        available_at=datetime(2026, 8, 27, 8, 0, tzinfo=timezone.utc),
    )
    assert trading["symbol"] == "600036.SH"
    assert trading["volume"] == 123_400
    assert trading["turnover_rate"] == 0.025
    assert trading["trade_status"] == "trading"
    assert trading["adjustment"] == "qfq"
    assert trading["available_at"] == "2026-08-27T08:00:00+00:00"

    suspended = normalize_baostock_history_row(
        {
            "code": "sz.002475",
            "date": "2026-08-27",
            "volume": 0,
            "turn": 0,
            "tradestatus": 0,
            "adjustflag": "qfq",
        }
    )
    assert suspended["trade_status"] == "suspended"
    assert suspended["available_at"] is None


@pytest.mark.parametrize(
    ("patch", "code"),
    [
        ({"ts_code": "600036.SZ"}, "SYMBOL_EXCHANGE_MISMATCH"),
        ({"trade_date": "20260230"}, "INVALID_TRADE_DATE"),
        ({"free_share": "NaN"}, "INVALID_NUMERIC"),
        ({"free_share": "0"}, "INVALID_NUMERIC_DOMAIN"),
        ({"free_share": "1.00001"}, "INVALID_FREE_SHARE_PRECISION"),
        ({"turnover_rate_f": "-0.1"}, "INVALID_NUMERIC_DOMAIN"),
    ],
)
def test_tushare_fails_closed_on_invalid_identity_date_and_numbers(
    patch: dict[str, object], code: str
) -> None:
    raw: dict[str, object] = {
        "ts_code": "600036.SH",
        "trade_date": "20260827",
        "free_share": "100",
        "turnover_rate_f": "1",
    }
    raw.update(patch)
    with pytest.raises(LiquidityCandidateNormalizationError, match=code):
        normalize_tushare_daily_basic_row(raw)


@pytest.mark.parametrize(
    ("patch", "code"),
    [
        ({"code": "sz.600036"}, "SYMBOL_EXCHANGE_MISMATCH"),
        ({"date": "2026-02-30"}, "INVALID_TRADE_DATE"),
        ({"volume": "1.5"}, "INVALID_VOLUME"),
        ({"volume": "Infinity"}, "INVALID_NUMERIC"),
        ({"turn": -1}, "INVALID_NUMERIC_DOMAIN"),
        ({"tradestatus": "2"}, "INVALID_TRADE_STATUS"),
        ({"adjustflag": "1"}, "ADJUSTMENT_NOT_QFQ"),
    ],
)
def test_baostock_fails_closed_on_invalid_fields(
    patch: dict[str, object], code: str
) -> None:
    raw: dict[str, object] = {
        "code": "sh.600036",
        "date": "2026-08-27",
        "volume": "1000",
        "turn": "1",
        "tradestatus": "1",
        "adjustflag": "2",
    }
    raw.update(patch)
    with pytest.raises(LiquidityCandidateNormalizationError, match=code):
        normalize_baostock_history_row(raw)


@pytest.mark.parametrize(
    "available_at",
    [
        "2026-08-27T15:30:00",
        "2026-08-27T15:00:00+08:00",
        "2026-08-27T06:59:59Z",
        "not-a-timestamp",
    ],
)
def test_available_at_must_be_explicit_timezone_aware_and_after_close(
    available_at: str,
) -> None:
    with pytest.raises(
        LiquidityCandidateNormalizationError,
        match="INVALID_AVAILABLE_AT",
    ):
        normalize_baostock_history_row(
            {
                "code": "sh.600036",
                "date": "2026-08-27",
                "volume": "1000",
                "turn": "1",
                "tradestatus": "1",
                "adjustflag": "2",
            },
            available_at=available_at,
        )


def test_scope_mismatch_and_missing_fields_fail_closed() -> None:
    with pytest.raises(
        LiquidityCandidateNormalizationError,
        match="SYMBOL_SCOPE_MISMATCH",
    ):
        normalize_tushare_daily_basic_row(
            {
                "ts_code": "002475.SZ",
                "trade_date": "20260827",
                "free_share": "100",
                "turnover_rate_f": "1",
            },
            expected_symbol="600036.SH",
        )
    with pytest.raises(
        LiquidityCandidateNormalizationError,
        match="REQUIRED_FIELD_MISSING",
    ):
        normalize_baostock_history_row({"code": "sh.600036"})

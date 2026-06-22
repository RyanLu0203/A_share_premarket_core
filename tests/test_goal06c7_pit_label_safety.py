from __future__ import annotations

from datetime import date, timedelta

import ashare_premarket.providers.provider_ladder as ladder


def _stock_rows(symbol: str, dates: list[str]) -> list[dict[str, object]]:
    return [
        {
            "trade_date": trade_date,
            "symbol": symbol,
            "open": 10 + idx,
            "high": 11 + idx,
            "low": 9 + idx,
            "close": 10 + idx,
            "volume": 1000,
            "amount": 100000,
            "provider_id": "mock",
            "provider_mode": "akshare_direct",
            "source_bundle_id": ladder.BUNDLE_ID,
            "ingest_ts": "test",
            "schema_version": "goal06c7.ohlcv.v1",
            "data_quality_flags": "SOURCE_BACKED",
        }
        for idx, trade_date in enumerate(dates)
    ]


def _benchmark_rows(dates: list[str]) -> list[dict[str, object]]:
    return [
        {
            "trade_date": trade_date,
            "benchmark_symbol": "000300",
            "open": 100 + idx,
            "high": 101 + idx,
            "low": 99 + idx,
            "close": 100 + idx,
            "volume": 1000,
            "amount": 100000,
            "provider_id": "mock",
            "provider_mode": "akshare_direct",
            "source_bundle_id": ladder.BUNDLE_ID,
            "ingest_ts": "test",
            "schema_version": "goal06c7.ohlcv.v1",
            "data_quality_flags": "SOURCE_BACKED",
        }
        for idx, trade_date in enumerate(dates)
    ]


def test_pit_features_use_prior_as_of_date_and_labels_are_forward() -> None:
    dates = [(date(2023, 1, 1) + timedelta(days=offset)).isoformat() for offset in range(40)]
    trading_dates = dates[22:30]
    stock_rows = _stock_rows("600036.SH", dates)
    benchmark_rows = _benchmark_rows(dates)
    pit_rows = ladder._build_pit_rows(stock_rows, benchmark_rows, trading_dates)
    label_rows = ladder._build_label_rows(stock_rows, benchmark_rows, trading_dates)
    stage_rows = ladder._build_stage6c_rows(__import__("pathlib").Path("."), pit_rows, label_rows)
    assert pit_rows
    assert label_rows
    assert stage_rows
    assert all(row["as_of_date"] < row["target_trading_date"] for row in pit_rows)
    assert all(row["label_ready"] is True for row in label_rows)
    assert all(row["leakage_flags"] == "PASS" for row in stage_rows)
    assert all(row["review_only"] is True for row in stage_rows)

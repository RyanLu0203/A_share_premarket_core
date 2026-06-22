from __future__ import annotations

from ashare_premarket.providers.failure_classification import classify_data_quality, classify_provider_success


def test_empty_dataframe_maps_to_zero_rows() -> None:
    result = classify_provider_success(rows_returned=0, schema_valid=True)
    assert result.failure_class == "ZERO_ROWS_RETURNED"
    assert result.failure_layer == "data_quality"


def test_schema_invalid_success_path_maps_to_contract_mismatch() -> None:
    result = classify_provider_success(rows_returned=5, schema_valid=False)
    assert result.failure_class == "CONTRACT_SCHEMA_MISMATCH"


def test_too_few_symbols_dates_and_rows_are_specific() -> None:
    assert classify_data_quality(symbol_count=1, trading_date_count=120, row_count=6000).failure_class == "INSUFFICIENT_SYMBOL_COVERAGE"
    assert classify_data_quality(symbol_count=50, trading_date_count=2, row_count=6000).failure_class == "INSUFFICIENT_DATE_COVERAGE"
    assert classify_data_quality(symbol_count=50, trading_date_count=120, row_count=5).failure_class == "INSUFFICIENT_PANEL_ROWS"


def test_duplicate_missing_and_invalid_values_are_specific() -> None:
    assert classify_data_quality(50, 120, 6000, duplicate_rows=True).failure_class == "DUPLICATE_ROWS_DETECTED"
    assert classify_data_quality(50, 120, 6000, missing_ohlcv=True).failure_class == "MISSING_OHLCV_VALUES"
    assert classify_data_quality(50, 120, 6000, invalid_prices=True).failure_class == "INVALID_PRICE_VALUES"

from __future__ import annotations

from ashare_premarket.alpha_validation.robustness import build_predeclared_slices


def _rows(final_volatility: float) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index in range(12):
        trade_date = f"d{index:02d}"
        for symbol in ("A", "B"):
            rows.append(
                {
                    "date": trade_date,
                    "symbol": symbol,
                    "market_volatility_20d": final_volatility if index >= 10 else float(index),
                    "index_trend_20d": -1.0 if index % 2 else 1.0,
                    "market_breadth_1d": 0.4 if index % 2 else 0.6,
                }
            )
    return rows


def _split() -> dict[str, object]:
    return {
        "final_holdout": {
            "training_dates": tuple(f"d{index:02d}" for index in range(8)),
            "purged_dates": ("d08", "d09"),
            "dates": ("d10", "d11"),
        }
    }


def test_regime_threshold_is_fit_on_development_only_and_slices_are_predeclared() -> None:
    config = {
        "recent_exclusion_dates": 2,
        "rolling_window_dates": 4,
        "rolling_window_step": 2,
        "expanding_window_minimum_dates": 3,
        "expanding_window_step": 3,
        "minimum_history_dates": 6,
        "minimum_observation_fraction": 0.5,
        "broad_market_breadth_threshold": 0.5,
        "volatility_threshold_fit_scope": "DEVELOPMENT_DATES_ONLY",
    }
    low_final = build_predeclared_slices(_rows(-10_000), tuple(f"d{i:02d}" for i in range(12)), _split(), config)
    high_final = build_predeclared_slices(_rows(10_000), tuple(f"d{i:02d}" for i in range(12)), _split(), config)

    assert low_final == high_final
    assert low_final["thresholds"]["market_volatility_median"] == 4.5
    names = {row["slice_id"] for row in low_final["date_slices"]}
    assert {"early_subperiod", "late_subperiod", "exclude_recent", "high_volatility", "low_volatility", "positive_index_trend", "negative_index_trend", "broad_market_breadth", "narrow_market_breadth"} <= names
    assert any(name.startswith("rolling_") for name in names)
    assert any(name.startswith("expanding_") for name in names)
    assert [
        row["date_count"]
        for row in low_final["date_slices"]
        if row["slice_id"].startswith("expanding_")
    ] == [3, 6, 9, 10]
    universe_names = {row["slice_id"] for row in low_final["universe_slices"]}
    assert universe_names == {"all_eligible_symbols", "minimum_history_symbols", "minimum_observation_symbols"}
    assert low_final["preprocessing_slices"] == (
        "raw_missing_exclusion",
        "winsorized_1pct_missing_exclusion",
        "training_median_imputation_when_permitted",
    )

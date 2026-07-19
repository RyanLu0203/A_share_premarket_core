from __future__ import annotations

from collections import defaultdict
from statistics import median
from typing import Mapping, Sequence

from ashare_premarket.quant_foundation.contracts import canonical_checksum


def build_predeclared_slices(
    feature_rows: Sequence[Mapping[str, object]],
    trading_calendar: Sequence[str],
    splits: Mapping[str, object],
    config: Mapping[str, object],
) -> dict[str, object]:
    calendar = tuple(map(str, trading_calendar))
    holdout_dates = set(map(str, dict(splits["final_holdout"])["dates"]))
    development = tuple(date for date in calendar if date not in holdout_dates)
    if not development:
        raise ValueError("goal12_robustness_requires_development_dates")
    context = _date_context(feature_rows)
    volatility_values = [
        float(context[date]["market_volatility_20d"])
        for date in development
        if context.get(date, {}).get("market_volatility_20d") is not None
    ]
    if not volatility_values:
        raise ValueError("goal12_robustness_requires_market_volatility_context")
    volatility_threshold = float(median(volatility_values))
    breadth_threshold = float(config["broad_market_breadth_threshold"])
    midpoint = len(development) // 2
    date_slices: list[dict[str, object]] = [
        _date_slice("early_subperiod", development[:midpoint]),
        _date_slice("late_subperiod", development[midpoint:]),
        _date_slice(
            "exclude_recent",
            calendar[: max(0, len(calendar) - int(config["recent_exclusion_dates"]))],
        ),
        _date_slice(
            "high_volatility",
            tuple(
                date
                for date in development
                if context.get(date, {}).get("market_volatility_20d") is not None
                and float(context[date]["market_volatility_20d"]) > volatility_threshold
            ),
        ),
        _date_slice(
            "low_volatility",
            tuple(
                date
                for date in development
                if context.get(date, {}).get("market_volatility_20d") is not None
                and float(context[date]["market_volatility_20d"]) <= volatility_threshold
            ),
        ),
        _date_slice(
            "positive_index_trend",
            tuple(
                date
                for date in development
                if context.get(date, {}).get("index_trend_20d") is not None
                and float(context[date]["index_trend_20d"]) >= 0
            ),
        ),
        _date_slice(
            "negative_index_trend",
            tuple(
                date
                for date in development
                if context.get(date, {}).get("index_trend_20d") is not None
                and float(context[date]["index_trend_20d"]) < 0
            ),
        ),
        _date_slice(
            "broad_market_breadth",
            tuple(
                date
                for date in development
                if context.get(date, {}).get("market_breadth_1d") is not None
                and float(context[date]["market_breadth_1d"]) >= breadth_threshold
            ),
        ),
        _date_slice(
            "narrow_market_breadth",
            tuple(
                date
                for date in development
                if context.get(date, {}).get("market_breadth_1d") is not None
                and float(context[date]["market_breadth_1d"]) < breadth_threshold
            ),
        ),
    ]
    window = int(config["rolling_window_dates"])
    step = int(config["rolling_window_step"])
    rolling_id = 1
    for start in range(0, max(0, len(development) - window + 1), step):
        date_slices.append(
            _date_slice(
                f"rolling_{rolling_id:02d}", development[start : start + window]
            )
        )
        rolling_id += 1
    expansion_minimum = int(config["expanding_window_minimum_dates"])
    expansion_step = int(config["expanding_window_step"])
    expansion_ends = list(
        range(expansion_minimum, len(development) + 1, expansion_step)
    )
    if development and (not expansion_ends or expansion_ends[-1] != len(development)):
        expansion_ends.append(len(development))
    for expanding_id, end in enumerate(expansion_ends, start=1):
        date_slices.append(
            _date_slice(f"expanding_{expanding_id:02d}", development[:end])
        )

    symbol_dates: dict[str, set[str]] = defaultdict(set)
    for row in feature_rows:
        symbol_dates[str(row["symbol"])].add(str(row["date"]))
    all_symbols = tuple(sorted(symbol_dates))
    minimum_history = int(config["minimum_history_dates"])
    observation_threshold = len(calendar) * float(config["minimum_observation_fraction"])
    universe_slices = [
        _universe_slice("all_eligible_symbols", all_symbols),
        _universe_slice(
            "minimum_history_symbols",
            tuple(
                symbol for symbol in all_symbols if len(symbol_dates[symbol]) >= minimum_history
            ),
        ),
        _universe_slice(
            "minimum_observation_symbols",
            tuple(
                symbol
                for symbol in all_symbols
                if len(symbol_dates[symbol]) >= observation_threshold
            ),
        ),
    ]
    result: dict[str, object] = {
        "slice_version": "goal12_predeclared_robustness_v1",
        "threshold_fit_scope": str(config["volatility_threshold_fit_scope"]),
        "thresholds": {
            "market_volatility_median": _clean(volatility_threshold),
            "broad_market_breadth": breadth_threshold,
            "minimum_history_dates": minimum_history,
            "minimum_observation_fraction": float(config["minimum_observation_fraction"]),
        },
        "date_slices": date_slices,
        "universe_slices": universe_slices,
        "preprocessing_slices": (
            "raw_missing_exclusion",
            "winsorized_1pct_missing_exclusion",
            "training_median_imputation_when_permitted",
        ),
    }
    result["checksum"] = canonical_checksum(result)
    return result


def _date_context(
    rows: Sequence[Mapping[str, object]],
) -> dict[str, dict[str, object]]:
    fields = (
        "market_volatility_20d",
        "index_trend_20d",
        "market_breadth_1d",
    )
    values: dict[str, dict[str, object]] = {}
    for row in rows:
        trade_date = str(row["date"])
        current = {field: row.get(field) for field in fields}
        if trade_date in values and values[trade_date] != current:
            raise ValueError(f"inconsistent_goal12_regime_context:{trade_date}")
        values[trade_date] = current
    return values


def _date_slice(slice_id: str, dates: Sequence[str]) -> dict[str, object]:
    result: dict[str, object] = {
        "slice_id": slice_id,
        "dates": tuple(map(str, dates)),
        "date_count": len(dates),
    }
    result["checksum"] = canonical_checksum(result)
    return result


def _universe_slice(slice_id: str, symbols: Sequence[str]) -> dict[str, object]:
    result: dict[str, object] = {
        "slice_id": slice_id,
        "symbols": tuple(map(str, symbols)),
        "symbol_count": len(symbols),
    }
    result["checksum"] = canonical_checksum(result)
    return result


def _clean(value: float) -> float:
    rounded = round(value, 12)
    return 0.0 if rounded == 0 else rounded

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Mapping, Sequence

from ashare_premarket.quant_foundation.contracts import (
    GovernedSnapshot,
    MarketObservation,
    canonical_checksum,
    validate_research_output_fields,
)

CONFIG_PATH = "configs/quant/goal11_quant_intelligence_v1.json"

FEATURE_COLUMNS = (
    "return_1d",
    "momentum_5d",
    "momentum_20d",
    "momentum_60d",
    "ma_ratio_5d",
    "ma_ratio_20d",
    "ma_ratio_60d",
    "trend_strength_20d",
    "volatility_20d",
    "downside_volatility_20d",
    "drawdown_60d",
    "volatility_regime_60d",
    "rsi_14",
    "macd_line_12_26",
    "macd_signal_9",
    "macd_histogram_12_26_9",
    "bollinger_position_20d",
    "atr_14",
    "volume_change_1d",
    "abnormal_volume_20d",
    "price_volume_correlation_20d",
    "index_trend_20d",
    "market_breadth_1d",
    "market_volatility_20d",
    "market_regime",
)

_FAMILY_COLUMNS = {
    "market_regime": (
        "index_trend_20d",
        "market_breadth_1d",
        "market_volatility_20d",
        "market_regime",
    ),
    "price": (
        "return_1d",
        "momentum_5d",
        "momentum_20d",
        "momentum_60d",
        "ma_ratio_5d",
        "ma_ratio_20d",
        "ma_ratio_60d",
        "trend_strength_20d",
    ),
    "technical": (
        "rsi_14",
        "macd_line_12_26",
        "macd_signal_9",
        "macd_histogram_12_26_9",
        "bollinger_position_20d",
        "atr_14",
    ),
    "volatility": (
        "volatility_20d",
        "downside_volatility_20d",
        "drawdown_60d",
        "volatility_regime_60d",
    ),
    "volume": (
        "volume_change_1d",
        "abnormal_volume_20d",
        "price_volume_correlation_20d",
    ),
}

_MINIMUM_HISTORY = {
    "return_1d": 2,
    "momentum_5d": 6,
    "momentum_20d": 21,
    "momentum_60d": 61,
    "ma_ratio_5d": 5,
    "ma_ratio_20d": 20,
    "ma_ratio_60d": 60,
    "trend_strength_20d": 20,
    "volatility_20d": 21,
    "downside_volatility_20d": 21,
    "drawdown_60d": 60,
    "volatility_regime_60d": 61,
    "rsi_14": 15,
    "macd_line_12_26": 26,
    "macd_signal_9": 34,
    "macd_histogram_12_26_9": 34,
    "bollinger_position_20d": 20,
    "atr_14": 15,
    "volume_change_1d": 2,
    "abnormal_volume_20d": 20,
    "price_volume_correlation_20d": 21,
    "index_trend_20d": 21,
    "market_breadth_1d": 2,
    "market_volatility_20d": 21,
    "market_regime": 21,
}
_MAXIMUM_HISTORY = max(_MINIMUM_HISTORY.values())


def load_feature_config(root: Path) -> dict[str, object]:
    payload = json.loads((root / CONFIG_PATH).read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.0":
        raise ValueError("goal11_config_schema_version_mismatch")
    if payload.get("feature_version") != "goal11_features_v1":
        raise ValueError("goal11_feature_version_mismatch")
    if payload.get("research_only") is not True:
        raise ValueError("goal11_config_must_remain_research_only")
    return payload


def build_feature_rows(
    snapshot: GovernedSnapshot,
    config: Mapping[str, object],
) -> list[dict[str, object]]:
    _validate_config(config)
    by_symbol: dict[str, list[MarketObservation]] = defaultdict(list)
    by_date: dict[str, list[MarketObservation]] = defaultdict(list)
    for observation in snapshot.rows:
        by_symbol[observation.symbol].append(observation)
        by_date[observation.date].append(observation)

    breadth = _breadth_by_date(by_symbol, by_date)
    index_history = _index_history(by_date)
    date_position = {trade_date: index for index, trade_date in enumerate(sorted(by_date))}
    feature_rows: list[dict[str, object]] = []
    for symbol in sorted(by_symbol):
        history = by_symbol[symbol]
        segment_start = 0
        for end in range(1, len(history) + 1):
            if (
                end > 1
                and date_position[history[end - 1].date]
                != date_position[history[end - 2].date] + 1
            ):
                segment_start = end - 1
            observations = history[segment_start:end]
            current = observations[-1]
            values = _feature_values(
                observations,
                index_history.get(current.date, ()),
                breadth.get(current.date),
                config,
            )
            reason_set = set(
                _availability_reasons(
                    observations,
                    values,
                    index_history.get(current.date, ()),
                )
            )
            if segment_start > 0 and len(observations) < _MAXIMUM_HISTORY:
                reason_set.add("SYMBOL_HISTORY_GAP_RESET")
            if date_position[current.date] > 0 and breadth.get(current.date) is None:
                reason_set.add("MARKET_BREADTH_REQUIRES_ALIGNED_CROSS_SECTION")
            reasons = tuple(sorted(reason_set))
            families = tuple(
                family
                for family, columns in sorted(_FAMILY_COLUMNS.items())
                if all(values[column] is not None for column in columns)
            )
            row: dict[str, object] = {
                "symbol": current.symbol,
                "date": current.date,
                "feature_version": str(config["feature_version"]),
                "source_snapshot_id": snapshot.snapshot_id,
                "generation_timestamp": snapshot.generation_timestamp,
                "code_commit": snapshot.code_commit,
                "source_checksum": snapshot.source_checksum,
                "adjustment": snapshot.adjustment,
                **values,
                "available_feature_families": families,
                "availability_reasons": reasons,
                "feature_status": "COMPLETE" if len(families) == len(_FAMILY_COLUMNS) else "PARTIAL",
            }
            validate_research_output_fields(row)
            row["checksum"] = canonical_checksum(row)
            feature_rows.append(row)
    return sorted(feature_rows, key=lambda row: (str(row["date"]), str(row["symbol"])))


def _validate_config(config: Mapping[str, object]) -> None:
    if config.get("feature_version") != "goal11_features_v1" or config.get("research_only") is not True:
        raise ValueError("invalid_goal11_feature_config")


def _feature_values(
    observations: Sequence[MarketObservation],
    index_values: Sequence[float],
    breadth: float | None,
    config: Mapping[str, object],
) -> dict[str, object]:
    prices = [row.close for row in observations]
    volumes = [row.volume for row in observations]
    annualization = math.sqrt(float(config["annualization_factor"]))
    returns = _returns(prices)
    vol20 = _annualized_volatility(returns[-20:], annualization) if len(returns) >= 20 else None
    vol60 = _annualized_volatility(returns[-60:], annualization) if len(returns) >= 60 else None
    macd_line, macd_signal, macd_histogram = _macd(prices)
    market_returns = _returns(list(index_values))
    market_volatility = (
        _annualized_volatility(market_returns[-20:], annualization)
        if len(market_returns) >= 20
        else None
    )
    index_trend = _momentum(index_values, 20)
    regime_config = dict(config["market_regime"])
    market_regime = None
    if index_trend is not None and breadth is not None and market_volatility is not None:
        bull = index_trend >= 0 and breadth >= float(regime_config["breadth_bull_threshold"])
        high_vol = market_volatility > float(regime_config["high_volatility_threshold"])
        market_regime = f"{'BULL' if bull else 'BEAR'}_{'HIGH_VOL' if high_vol else 'CALM'}"
    values: dict[str, object] = {
        "return_1d": _momentum(prices, 1),
        "momentum_5d": _momentum(prices, 5),
        "momentum_20d": _momentum(prices, 20),
        "momentum_60d": _momentum(prices, 60),
        "ma_ratio_5d": _moving_average_ratio(prices, 5),
        "ma_ratio_20d": _moving_average_ratio(prices, 20),
        "ma_ratio_60d": _moving_average_ratio(prices, 60),
        "trend_strength_20d": _trend_strength(prices, 20),
        "volatility_20d": vol20,
        "downside_volatility_20d": _downside_volatility(returns[-20:], annualization) if len(returns) >= 20 else None,
        "drawdown_60d": prices[-1] / max(prices[-60:]) - 1.0 if len(prices) >= 60 else None,
        "volatility_regime_60d": _safe_ratio(vol20, vol60),
        "rsi_14": _rsi(prices, 14),
        "macd_line_12_26": macd_line,
        "macd_signal_9": macd_signal,
        "macd_histogram_12_26_9": macd_histogram,
        "bollinger_position_20d": _bollinger_position(prices, 20),
        "atr_14": _atr(observations, 14),
        "volume_change_1d": _volume_change(volumes),
        "abnormal_volume_20d": _abnormal_volume(volumes, 20),
        "price_volume_correlation_20d": _price_volume_correlation(prices, volumes, 20),
        "index_trend_20d": index_trend,
        "market_breadth_1d": breadth,
        "market_volatility_20d": market_volatility,
        "market_regime": market_regime,
    }
    return {name: _clean(values[name]) for name in FEATURE_COLUMNS}


def _availability_reasons(
    observations: Sequence[MarketObservation],
    values: Mapping[str, object],
    index_values: Sequence[float],
) -> tuple[str, ...]:
    reasons: set[str] = set()
    history = len(observations)
    for name, minimum in _MINIMUM_HISTORY.items():
        if values[name] is None and history < minimum:
            reasons.add(f"INSUFFICIENT_HISTORY:{name.upper()}")
    if history >= 15 and any(row.high is None or row.low is None for row in observations[-15:]):
        reasons.add("ATR_REQUIRES_HIGH_LOW")
    volume_features_missing = any(
        values[name] is None for name in _FAMILY_COLUMNS["volume"]
    )
    if (
        history >= 2
        and volume_features_missing
        and any(row.volume is None for row in observations[-21:])
    ):
        reasons.add("VOLUME_FEATURES_REQUIRE_VOLUME")
    if history >= 21 and len(index_values) < 21:
        reasons.add("MARKET_INDEX_REQUIRES_INDEX_CLOSE")
    if values["volume_change_1d"] is None and history >= 2 and observations[-2].volume == 0:
        reasons.add("VOLUME_CHANGE_REQUIRES_NONZERO_PRIOR_VOLUME")
    if (
        values["price_volume_correlation_20d"] is None
        and history >= 21
        and any(row.volume == 0 for row in observations[-21:])
    ):
        reasons.add("PRICE_VOLUME_CORRELATION_REQUIRES_POSITIVE_VOLUME")
    return tuple(sorted(reasons))


def _breadth_by_date(
    _by_symbol: Mapping[str, Sequence[MarketObservation]],
    by_date: Mapping[str, Sequence[MarketObservation]],
) -> dict[str, float | None]:
    previous: dict[str, float] = {}
    result: dict[str, float | None] = {}
    for trade_date in sorted(by_date):
        rows = by_date[trade_date]
        current_symbols = {row.symbol for row in rows}
        if len(current_symbols) >= 2 and previous and current_symbols == set(previous):
            result[trade_date] = sum(row.close > previous[row.symbol] for row in rows) / len(current_symbols)
        else:
            result[trade_date] = None
        previous = {row.symbol: row.close for row in rows}
    return result


def _index_history(by_date: Mapping[str, Sequence[MarketObservation]]) -> dict[str, tuple[float, ...]]:
    history: list[float] = []
    result: dict[str, tuple[float, ...]] = {}
    for trade_date in sorted(by_date):
        rows = by_date[trade_date]
        if any(row.index_close is None for row in rows):
            history = []
            result[trade_date] = ()
            continue
        values = {float(row.index_close) for row in rows if row.index_close is not None}
        if len(values) > 1:
            raise ValueError(f"inconsistent_index_close_for_date:{trade_date}")
        if len(values) == 1:
            history.append(next(iter(values)))
            result[trade_date] = tuple(history)
        else:
            history = []
            result[trade_date] = ()
    return result


def _returns(values: Sequence[float]) -> list[float]:
    return [values[index] / values[index - 1] - 1.0 for index in range(1, len(values))]


def _momentum(values: Sequence[float], window: int) -> float | None:
    return values[-1] / values[-window - 1] - 1.0 if len(values) > window else None


def _moving_average_ratio(values: Sequence[float], window: int) -> float | None:
    if len(values) < window:
        return None
    mean = sum(values[-window:]) / window
    return values[-1] / mean - 1.0


def _trend_strength(values: Sequence[float], window: int) -> float | None:
    if len(values) < window:
        return None
    sample = values[-window:]
    x_mean = (window - 1) / 2.0
    y_mean = sum(sample) / window
    denominator = sum((index - x_mean) ** 2 for index in range(window))
    slope = sum((index - x_mean) * (value - y_mean) for index, value in enumerate(sample)) / denominator
    return slope / y_mean if y_mean else None


def _annualized_volatility(values: Sequence[float], annualization: float) -> float:
    return _std(values) * annualization


def _downside_volatility(values: Sequence[float], annualization: float) -> float:
    return math.sqrt(sum(min(value, 0.0) ** 2 for value in values) / len(values)) * annualization


def _std(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / len(values))


def _safe_ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None:
        return None
    if denominator == 0:
        return 1.0 if numerator == 0 else None
    return numerator / denominator


def _rsi(values: Sequence[float], window: int) -> float | None:
    if len(values) <= window:
        return None
    changes = [values[index] - values[index - 1] for index in range(len(values) - window, len(values))]
    gains = sum(max(change, 0.0) for change in changes) / window
    losses = sum(max(-change, 0.0) for change in changes) / window
    if losses == 0:
        return 100.0 if gains > 0 else 50.0
    return 100.0 - 100.0 / (1.0 + gains / losses)


def _ema(values: Sequence[float], span: int) -> float:
    alpha = 2.0 / (span + 1.0)
    result = values[0]
    for value in values[1:]:
        result = alpha * value + (1.0 - alpha) * result
    return result


def _macd(values: Sequence[float]) -> tuple[float | None, float | None, float | None]:
    if len(values) < 26:
        return None, None, None
    alpha12 = 2.0 / 13.0
    alpha26 = 2.0 / 27.0
    ema12 = values[0]
    ema26 = values[0]
    lines: list[float] = []
    for index, value in enumerate(values[1:], start=2):
        ema12 = alpha12 * value + (1.0 - alpha12) * ema12
        ema26 = alpha26 * value + (1.0 - alpha26) * ema26
        if index >= 26:
            lines.append(ema12 - ema26)
    line = lines[-1]
    if len(lines) < 9:
        return line, None, None
    signal = _ema(lines, 9)
    return line, signal, line - signal


def _bollinger_position(values: Sequence[float], window: int) -> float | None:
    if len(values) < window:
        return None
    sample = values[-window:]
    mean = sum(sample) / window
    deviation = _std(sample)
    return 0.0 if deviation == 0 else (values[-1] - mean) / (2.0 * deviation)


def _atr(observations: Sequence[MarketObservation], window: int) -> float | None:
    if len(observations) <= window:
        return None
    sample = observations[-window:]
    previous = observations[-window - 1 : -1]
    if any(row.high is None or row.low is None for row in sample):
        return None
    true_ranges = [
        max(
            float(row.high) - float(row.low),
            abs(float(row.high) - prior.close),
            abs(float(row.low) - prior.close),
        )
        for row, prior in zip(sample, previous)
    ]
    return sum(true_ranges) / window


def _volume_change(values: Sequence[float | None]) -> float | None:
    if len(values) < 2 or values[-1] is None or values[-2] in {None, 0}:
        return None
    return float(values[-1]) / float(values[-2]) - 1.0


def _abnormal_volume(values: Sequence[float | None], window: int) -> float | None:
    if len(values) < window or any(value is None for value in values[-window:]):
        return None
    sample = [float(value) for value in values[-window:] if value is not None]
    mean = sum(sample) / window
    return sample[-1] / mean - 1.0 if mean else None


def _price_volume_correlation(
    prices: Sequence[float],
    volumes: Sequence[float | None],
    window: int,
) -> float | None:
    if len(prices) <= window or len(volumes) <= window or any(value in {None, 0} for value in volumes[-window - 1 :]):
        return None
    price_returns = _returns(prices[-window - 1 :])
    volume_values = [float(value) for value in volumes[-window - 1 :] if value is not None]
    volume_changes = _returns(volume_values)
    return _correlation(price_returns, volume_changes)


def _correlation(left: Sequence[float], right: Sequence[float]) -> float:
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    denominator = math.sqrt(
        sum((value - left_mean) ** 2 for value in left)
        * sum((value - right_mean) ** 2 for value in right)
    )
    return 0.0 if denominator == 0 else numerator / denominator


def _clean(value: object) -> object:
    if not isinstance(value, float):
        return value
    rounded = round(value, 12)
    return 0.0 if rounded == 0 else rounded

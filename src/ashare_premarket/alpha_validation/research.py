from __future__ import annotations

import math
from collections import Counter, defaultdict
from statistics import median
from typing import Mapping, Sequence

from ashare_premarket.alpha_validation.statistics import (
    mean,
    pearson_correlation,
    quantile_diagnostics,
    spearman_correlation,
    standard_deviation,
)
from ashare_premarket.quant_foundation.contracts import (
    canonical_checksum,
    validate_research_output_fields,
)


def evaluate_single_factor(
    feature_rows: Sequence[Mapping[str, object]],
    label_rows: Sequence[Mapping[str, object]],
    *,
    feature_name: str,
    direction: int,
    minimum_cross_section: int,
    quantile_count: int,
    top_k: int,
    allowed_dates: set[str] | None = None,
    allowed_symbols: set[str] | None = None,
    preprocessing: str = "raw",
    validate_checksums: bool = True,
) -> dict[str, object]:
    if direction not in {-1, 1}:
        raise ValueError("factor_direction_must_be_predeclared")
    if preprocessing not in {"raw", "winsorized_1pct"}:
        raise ValueError("unsupported_single_factor_preprocessing")
    features = _validated_by_key(feature_rows, "feature", validate_checksums)
    labels = _validated_by_key(label_rows, "label", validate_checksums)
    by_date: dict[str, list[tuple[str, float, float]]] = defaultdict(list)
    opportunity_count = 0
    missing_feature_count = 0
    missing_label_count = 0
    for key, label in labels.items():
        trade_date, symbol = key
        if allowed_dates is not None and trade_date not in allowed_dates:
            continue
        if allowed_symbols is not None and symbol not in allowed_symbols:
            continue
        if key not in features:
            raise ValueError("label_without_matching_goal12_feature")
        opportunity_count += 1
        raw_value = features[key].get(feature_name)
        if raw_value is None:
            missing_feature_count += 1
        if label.get("label_status") != "AVAILABLE" or label.get("forward_return") is None:
            missing_label_count += 1
            continue
        if raw_value is None:
            continue
        value = _finite(raw_value, "non_finite_factor_value") * direction
        realized = _finite(label["forward_return"], "non_finite_forward_return")
        by_date[trade_date].append((symbol, value, realized))

    observations: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []
    zero_variance_count = 0
    evaluable_date_count = 0
    previous_top: set[str] | None = None
    turnovers: list[float] = []
    overlaps: list[float] = []
    symbol_counts: Counter[str] = Counter()
    for trade_date in sorted(by_date):
        rows = sorted(by_date[trade_date])
        if len(rows) < minimum_cross_section:
            skipped.append(
                {"date": trade_date, "row_count": len(rows), "reason": "INSUFFICIENT_CROSS_SECTION"}
            )
            continue
        evaluable_date_count += 1
        if len({row[1] for row in rows}) < 2:
            zero_variance_count += 1
            skipped.append(
                {"date": trade_date, "row_count": len(rows), "reason": "ZERO_FACTOR_VARIANCE"}
            )
            continue
        if preprocessing == "winsorized_1pct":
            rows = _winsorize_rows(rows, 0.01, 0.99)
        symbols = [row[0] for row in rows]
        factors = [row[1] for row in rows]
        realized = [row[2] for row in rows]
        quantiles = quantile_diagnostics(rows, quantile_count=quantile_count)
        effective_k = min(top_k, len(rows))
        top_indices = sorted(
            range(len(rows)), key=lambda index: (-factors[index], symbols[index])
        )[:effective_k]
        current_top = {symbols[index] for index in top_indices}
        turnover = None
        overlap = None
        if previous_top is not None:
            overlap = len(previous_top & current_top) / effective_k
            turnover = 1.0 - overlap
            overlaps.append(overlap)
            turnovers.append(turnover)
        previous_top = current_top
        symbol_counts.update(symbols)
        observation = {
            "date": trade_date,
            "row_count": len(rows),
            "ic": pearson_correlation(factors, realized),
            "rank_ic": spearman_correlation(factors, realized),
            "quantile_top_minus_bottom": quantiles["top_minus_bottom"],
            "bucket_monotonicity": quantiles["monotonicity"],
            "bucket_mean_returns": quantiles["bucket_mean_returns"],
            "rank_tie_rate": _clean(1.0 - len(set(factors)) / len(factors)),
            "ranking_turnover": _clean(turnover) if turnover is not None else None,
            "top_k_overlap": _clean(overlap) if overlap is not None else None,
            "rows": tuple(rows),
        }
        observations.append(observation)

    ic_values = [float(row["ic"]) for row in observations if row["ic"] is not None]
    rank_values = [
        float(row["rank_ic"]) for row in observations if row["rank_ic"] is not None
    ]
    rank_std = standard_deviation(rank_values)
    observation_count = sum(int(row["row_count"]) for row in observations)
    breadth = [int(row["row_count"]) for row in observations]
    result: dict[str, object] = {
        "feature_name": feature_name,
        "direction": direction,
        "preprocessing": preprocessing,
        "valid_date_count": len(observations),
        "observation_row_count": observation_count,
        "opportunity_row_count": opportunity_count,
        "missing_feature_count": missing_feature_count,
        "missing_label_count": missing_label_count,
        "missing_rate": _clean(missing_feature_count / opportunity_count) if opportunity_count else 1.0,
        "label_missing_rate": _clean(missing_label_count / opportunity_count) if opportunity_count else 1.0,
        "zero_variance_date_count": zero_variance_count,
        "zero_variance_rate": _clean(zero_variance_count / evaluable_date_count) if evaluable_date_count else 1.0,
        "ic_mean": mean(ic_values),
        "ic_median": _clean(float(median(ic_values))) if ic_values else None,
        "ic_standard_deviation": standard_deviation(ic_values),
        "rank_ic_mean": mean(rank_values),
        "rank_ic_median": _clean(float(median(rank_values))) if rank_values else None,
        "rank_ic_standard_deviation": rank_std,
        "rank_ic_information_ratio": (
            _clean(float(mean(rank_values)) / rank_std)
            if rank_values and rank_std not in {None, 0.0}
            else None
        ),
        "positive_rank_ic_ratio": _clean(sum(value > 0 for value in rank_values) / len(rank_values)) if rank_values else None,
        "median_breadth": _clean(float(median(breadth))) if breadth else 0.0,
        "effective_cross_sectional_breadth": _clean(sum(breadth) / len(breadth)) if breadth else 0.0,
        "quantile_top_minus_bottom_mean": mean([float(row["quantile_top_minus_bottom"]) for row in observations]),
        "bucket_monotonicity_mean": mean([float(row["bucket_monotonicity"]) for row in observations if row["bucket_monotonicity"] is not None]),
        "rank_tie_rate": mean([float(row["rank_tie_rate"]) for row in observations]),
        "ranking_turnover": mean(turnovers) if turnovers else 0.0,
        "top_k_overlap": mean(overlaps) if overlaps else 1.0,
        "symbol_concentration": _clean(max(symbol_counts.values()) / observation_count) if observation_count else 1.0,
        "date_concentration": _clean(max(breadth) / observation_count) if observation_count else 1.0,
        "by_date": observations,
        "skipped_dates": skipped,
    }
    validate_research_output_fields(result)
    result["checksum"] = canonical_checksum(result)
    return result


def _validated_by_key(
    rows: Sequence[Mapping[str, object]], kind: str, validate_checksums: bool
) -> dict[tuple[str, str], Mapping[str, object]]:
    output: dict[tuple[str, str], Mapping[str, object]] = {}
    for row in rows:
        if validate_checksums:
            expected = canonical_checksum(
                {key: value for key, value in row.items() if key != "checksum"}
            )
            if row.get("checksum") != expected:
                raise ValueError(f"goal12_{kind}_checksum_mismatch")
        key = (str(row.get("date", "")), str(row.get("symbol", "")))
        if key in output:
            raise ValueError(f"duplicate_goal12_{kind}_key")
        output[key] = row
    return output


def _winsorize_rows(
    rows: Sequence[tuple[str, float, float]], lower: float, upper: float
) -> list[tuple[str, float, float]]:
    values = sorted(row[1] for row in rows)
    low = _quantile(values, lower)
    high = _quantile(values, upper)
    return [(symbol, min(max(value, low), high), realized) for symbol, value, realized in rows]


def _quantile(values: Sequence[float], probability: float) -> float:
    position = probability * (len(values) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return values[lower]
    weight = position - lower
    return values[lower] * (1 - weight) + values[upper] * weight


def _finite(value: object, reason: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(reason) from exc
    if not math.isfinite(number):
        raise ValueError(reason)
    return number


def _clean(value: float) -> float:
    rounded = round(value, 12)
    return 0.0 if rounded == 0 else rounded

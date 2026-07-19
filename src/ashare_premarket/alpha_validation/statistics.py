from __future__ import annotations

import math
import random
from statistics import median
from typing import Mapping, Sequence


def pearson_correlation(left: Sequence[float], right: Sequence[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        return None
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    denominator = math.sqrt(
        sum((value - left_mean) ** 2 for value in left)
        * sum((value - right_mean) ** 2 for value in right)
    )
    return None if denominator == 0 else _clean(numerator / denominator)


def spearman_correlation(left: Sequence[float], right: Sequence[float]) -> float | None:
    if len(left) != len(right):
        return None
    return pearson_correlation(_average_ranks(left), _average_ranks(right))


def benjamini_hochberg(p_values: Mapping[str, float]) -> dict[str, float]:
    checked: list[tuple[str, float]] = []
    for key, raw in p_values.items():
        value = float(raw)
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError(f"invalid_p_value:{key}")
        checked.append((str(key), value))
    ordered = sorted(checked, key=lambda item: (item[1], item[0]))
    count = len(ordered)
    adjusted: dict[str, float] = {}
    running = 1.0
    for reverse_index in range(count - 1, -1, -1):
        key, value = ordered[reverse_index]
        rank = reverse_index + 1
        running = min(running, value * count / rank)
        adjusted[key] = _clean(min(1.0, running))
    return {key: adjusted[key] for key in sorted(adjusted)}


def date_bootstrap_interval(
    values: Sequence[float],
    *,
    repetitions: int,
    confidence: float,
    seed: int,
) -> tuple[float, float]:
    sample = _finite_nonempty(values)
    if repetitions <= 0 or not 0.0 < confidence < 1.0:
        raise ValueError("invalid_date_bootstrap_configuration")
    generator = random.Random(seed)
    means = sorted(
        sum(sample[generator.randrange(len(sample))] for _ in sample) / len(sample)
        for _ in range(repetitions)
    )
    tail = (1.0 - confidence) / 2.0
    return _clean(_quantile(means, tail)), _clean(_quantile(means, 1.0 - tail))


def date_sign_flip_pvalue(
    values: Sequence[float], *, repetitions: int, seed: int
) -> float:
    sample = _finite_nonempty(values)
    if repetitions <= 0:
        raise ValueError("invalid_sign_flip_repetitions")
    observed = sum(sample) / len(sample)
    generator = random.Random(seed)
    exceedances = 0
    for _ in range(repetitions):
        null_mean = sum(
            value if generator.getrandbits(1) else -value for value in sample
        ) / len(sample)
        if null_mean >= observed:
            exceedances += 1
    return _clean((exceedances + 1.0) / (repetitions + 1.0))


def quantile_diagnostics(
    rows: Sequence[tuple[str, float, float]], *, quantile_count: int
) -> dict[str, object]:
    if quantile_count < 2 or len(rows) < quantile_count:
        raise ValueError("insufficient_quantile_rows")
    ordered = sorted(rows, key=lambda row: (row[1], row[0]))
    buckets: list[list[float]] = [[] for _ in range(quantile_count)]
    for index, (_, _, realized) in enumerate(ordered):
        bucket = min(quantile_count - 1, index * quantile_count // len(ordered))
        buckets[bucket].append(float(realized))
    means = tuple(_clean(sum(bucket) / len(bucket)) for bucket in buckets)
    medians = tuple(_clean(float(median(bucket))) for bucket in buckets)
    monotonicity = spearman_correlation(
        list(range(quantile_count)), list(means)
    )
    return {
        "bucket_counts": tuple(len(bucket) for bucket in buckets),
        "bucket_mean_returns": means,
        "bucket_median_returns": medians,
        "top_minus_bottom": _clean(means[-1] - means[0]),
        "monotonicity": monotonicity,
    }


def ndcg_at_k(scores: Sequence[float], realized: Sequence[float], k: int) -> float:
    if len(scores) != len(realized) or not scores or k <= 0:
        raise ValueError("invalid_ndcg_inputs")
    ranks = _average_ranks(realized)
    predicted = sorted(range(len(scores)), key=lambda index: (-scores[index], index))[:k]
    ideal = sorted(range(len(realized)), key=lambda index: (-realized[index], index))[:k]

    def dcg(order: Sequence[int]) -> float:
        return sum(
            (2.0 ** ranks[index] - 1.0) / math.log2(position + 2.0)
            for position, index in enumerate(order)
        )

    ideal_value = dcg(ideal)
    return 0.0 if ideal_value == 0 else _clean(dcg(predicted) / ideal_value)


def mean(values: Sequence[float]) -> float | None:
    return _clean(sum(values) / len(values)) if values else None


def standard_deviation(values: Sequence[float]) -> float | None:
    if not values:
        return None
    average = sum(values) / len(values)
    return _clean(math.sqrt(sum((value - average) ** 2 for value in values) / len(values)))


def _average_ranks(values: Sequence[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda item: (item[1], item[0]))
    ranks = [0.0] * len(values)
    index = 0
    while index < len(ordered):
        end = index + 1
        while end < len(ordered) and ordered[end][1] == ordered[index][1]:
            end += 1
        average = (index + end - 1) / 2.0
        for original, _ in ordered[index:end]:
            ranks[original] = average
        index = end
    return ranks


def _finite_nonempty(values: Sequence[float]) -> list[float]:
    sample = [float(value) for value in values]
    if not sample or any(not math.isfinite(value) for value in sample):
        raise ValueError("date_sample_requires_finite_values")
    return sample


def _quantile(values: Sequence[float], probability: float) -> float:
    if len(values) == 1:
        return values[0]
    position = probability * (len(values) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return values[lower]
    weight = position - lower
    return values[lower] * (1.0 - weight) + values[upper] * weight


def _clean(value: float) -> float:
    rounded = round(value, 12)
    return 0.0 if rounded == 0 else rounded

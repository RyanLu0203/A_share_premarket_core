from __future__ import annotations

import hashlib
import random
from typing import Mapping, Sequence

from ashare_premarket.alpha_validation.statistics import (
    date_bootstrap_interval,
    date_sign_flip_pvalue,
    mean,
    spearman_correlation,
)
from ashare_premarket.quant_foundation.contracts import canonical_checksum


def run_null_controls(
    candidate_key: str,
    by_date: Sequence[Mapping[str, object]],
    config: Mapping[str, object],
) -> dict[str, object]:
    observations = [row for row in by_date if row.get("rank_ic") is not None]
    rank_ics = [float(row["rank_ic"]) for row in observations]
    if not rank_ics:
        raise ValueError("null_controls_require_valid_date_metrics")
    base_seed = int(config["base_seed"])
    candidate_seed = _derived_seed(base_seed, candidate_key)
    sign_seed = _derived_seed(candidate_seed, "sign_flip")
    bootstrap_seed = _derived_seed(candidate_seed, "bootstrap")
    shuffle_seed = _derived_seed(candidate_seed, "within_date_shuffle")
    random_seed = _derived_seed(candidate_seed, "random_rank")
    observed = float(mean(rank_ics))
    sign_p = date_sign_flip_pvalue(
        rank_ics,
        repetitions=int(config["sign_flip_repetitions"]),
        seed=sign_seed,
    )
    confidence_interval = date_bootstrap_interval(
        rank_ics,
        repetitions=int(config["date_bootstrap_repetitions"]),
        confidence=float(config["bootstrap_confidence"]),
        seed=bootstrap_seed,
    )
    shuffle_draws = _within_date_draws(
        observations,
        repetitions=int(config["within_date_shuffle_repetitions"]),
        seed=shuffle_seed,
        random_values=False,
    )
    random_draws = _within_date_draws(
        observations,
        repetitions=int(config["random_rank_repetitions"]),
        seed=random_seed,
        random_values=True,
    )
    shuffle_p = _empirical_greater_p(observed, shuffle_draws)
    random_p = _empirical_greater_p(observed, random_draws)
    shifted = _date_shift_control(observations)
    result: dict[str, object] = {
        "candidate_key": str(candidate_key),
        "observed_rank_ic_mean": observed,
        "confidence_interval": confidence_interval,
        "date_sign_flip_p": sign_p,
        "within_date_shuffle_p": shuffle_p,
        "random_rank_p": random_p,
        "conservative_null_p": max(sign_p, shuffle_p, random_p),
        "within_date_shuffle_null_means": tuple(shuffle_draws),
        "random_rank_null_means": tuple(random_draws),
        "invalid_date_shift_rank_ic_mean": shifted,
        "constant_factor_valid_date_count": 0,
        "resampling_unit": "DATE",
        "seed_manifest": {
            "base_seed": base_seed,
            "candidate_seed": candidate_seed,
            "bootstrap_seed": bootstrap_seed,
            "sign_flip_seed": sign_seed,
            "within_date_shuffle_seed": shuffle_seed,
            "random_rank_seed": random_seed,
        },
        "test_counts": {
            "date_bootstrap": int(config["date_bootstrap_repetitions"]),
            "date_sign_flip": int(config["sign_flip_repetitions"]),
            "within_date_shuffle": int(config["within_date_shuffle_repetitions"]),
            "random_rank": int(config["random_rank_repetitions"]),
        },
    }
    result["checksum"] = canonical_checksum(result)
    return result


def _within_date_draws(
    observations: Sequence[Mapping[str, object]],
    *,
    repetitions: int,
    seed: int,
    random_values: bool,
) -> list[float]:
    generator = random.Random(seed)
    draws: list[float] = []
    for _ in range(repetitions):
        date_values: list[float] = []
        for observation in observations:
            rows = list(observation["rows"])
            factors = [float(row[1]) for row in rows]
            realized = [float(row[2]) for row in rows]
            if random_values:
                factors = [generator.random() for _ in factors]
            else:
                generator.shuffle(factors)
            value = spearman_correlation(factors, realized)
            if value is not None:
                date_values.append(value)
        draws.append(float(mean(date_values) or 0.0))
    return draws


def _date_shift_control(observations: Sequence[Mapping[str, object]]) -> float | None:
    shifted_values: list[float] = []
    ordered = sorted(observations, key=lambda row: str(row["date"]))
    for factor_date, label_date in zip(ordered, ordered[1:]):
        factors = {str(row[0]): float(row[1]) for row in factor_date["rows"]}
        labels = {str(row[0]): float(row[2]) for row in label_date["rows"]}
        symbols = sorted(set(factors) & set(labels))
        value = spearman_correlation(
            [factors[symbol] for symbol in symbols],
            [labels[symbol] for symbol in symbols],
        )
        if value is not None:
            shifted_values.append(value)
    return mean(shifted_values)


def _empirical_greater_p(observed: float, draws: Sequence[float]) -> float:
    return round((1 + sum(value >= observed for value in draws)) / (len(draws) + 1), 12)


def _derived_seed(seed: int, label: str) -> int:
    digest = hashlib.sha256(f"{seed}:{label}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")

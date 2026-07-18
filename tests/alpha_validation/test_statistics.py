from __future__ import annotations

import pytest

from ashare_premarket.alpha_validation.statistics import (
    benjamini_hochberg,
    date_bootstrap_interval,
    date_sign_flip_pvalue,
    ndcg_at_k,
    quantile_diagnostics,
)


def test_benjamini_hochberg_is_monotone_and_restores_candidate_keys() -> None:
    adjusted = benjamini_hochberg({"b": 0.04, "a": 0.01, "c": 0.03})

    assert adjusted == {"a": 0.03, "b": 0.04, "c": 0.04}


@pytest.mark.parametrize("bad", [-0.1, 1.1, float("nan")])
def test_benjamini_hochberg_rejects_invalid_probabilities(bad: float) -> None:
    with pytest.raises(ValueError, match="invalid_p_value"):
        benjamini_hochberg({"candidate": bad})


def test_date_level_inference_is_seeded_deterministic_and_not_row_iid() -> None:
    values = [0.10, 0.12, 0.08, 0.09, 0.11, 0.07]
    first = date_bootstrap_interval(values, repetitions=200, confidence=0.95, seed=12041)
    second = date_bootstrap_interval(values, repetitions=200, confidence=0.95, seed=12041)

    assert first == second
    assert first[0] > 0
    assert date_sign_flip_pvalue(values, repetitions=500, seed=12041) < 0.05


def test_quantiles_and_ndcg_have_hand_checked_behavior() -> None:
    diagnostics = quantile_diagnostics(
        [("A", 1.0, -0.02), ("B", 2.0, -0.01), ("C", 3.0, 0.01), ("D", 4.0, 0.04)],
        quantile_count=2,
    )
    assert diagnostics["bucket_counts"] == (2, 2)
    assert diagnostics["bucket_mean_returns"] == (-0.015, 0.025)
    assert diagnostics["top_minus_bottom"] == 0.04
    assert diagnostics["monotonicity"] == 1.0

    assert ndcg_at_k([4.0, 3.0, 2.0, 1.0], [4.0, 3.0, 2.0, 1.0], 4) == 1.0
    assert 0.0 <= ndcg_at_k([1.0, 2.0, 3.0, 4.0], [4.0, 3.0, 2.0, 1.0], 4) < 1.0

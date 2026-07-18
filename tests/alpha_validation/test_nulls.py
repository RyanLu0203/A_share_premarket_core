from __future__ import annotations

from ashare_premarket.alpha_validation.nulls import run_null_controls


def _by_date() -> list[dict[str, object]]:
    return [
        {
            "date": f"d{date_index:02d}",
            "rows": tuple(
                (f"s{symbol_index}", float(symbol_index), float(symbol_index))
                for symbol_index in range(8)
            ),
            "rank_ic": 1.0,
        }
        for date_index in range(20)
    ]


def test_null_controls_are_deterministic_date_aware_and_record_all_seeds() -> None:
    config = {
        "base_seed": 12041,
        "date_bootstrap_repetitions": 200,
        "sign_flip_repetitions": 500,
        "within_date_shuffle_repetitions": 64,
        "random_rank_repetitions": 64,
        "bootstrap_confidence": 0.95,
    }
    first = run_null_controls("factor:5", _by_date(), config)
    second = run_null_controls("factor:5", _by_date(), config)

    assert first == second
    assert first["observed_rank_ic_mean"] == 1.0
    assert first["date_sign_flip_p"] < 0.05
    assert first["within_date_shuffle_p"] < 0.05
    assert first["random_rank_p"] < 0.05
    assert first["conservative_null_p"] == max(
        first["date_sign_flip_p"],
        first["within_date_shuffle_p"],
        first["random_rank_p"],
    )
    assert first["constant_factor_valid_date_count"] == 0
    assert first["seed_manifest"]["base_seed"] == 12041
    assert len(first["within_date_shuffle_null_means"]) == 64
    assert len(first["random_rank_null_means"]) == 64
    assert first["resampling_unit"] == "DATE"

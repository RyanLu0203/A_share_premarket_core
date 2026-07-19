from __future__ import annotations

from ashare_premarket.alpha_validation.folds import build_purged_chronological_splits


def _dates(count: int) -> tuple[str, ...]:
    return tuple(f"d{index:02d}" for index in range(count))


def _config() -> dict[str, object]:
    return {
        "minimum_training_dates": 3,
        "validation_dates": 2,
        "test_dates": 2,
        "final_holdout_dates": 2,
        "maximum_label_horizon": 2,
        "embargo_dates": 0,
        "mode": "EXPANDING_PURGED_CHRONOLOGICAL",
    }


def test_fold_boundaries_are_chronological_disjoint_and_max_horizon_purged() -> None:
    dates = _dates(12)
    result = build_purged_chronological_splits(dates, _config())
    fold = result["folds"][0]

    assert fold["train_dates"] == dates[:3]
    assert fold["purged_dates"] == dates[3:5]
    assert fold["validation_dates"] == dates[5:7]
    assert fold["test_dates"] == dates[7:9]
    assert set(fold["train_dates"]).isdisjoint(fold["validation_dates"])
    assert set(fold["validation_dates"]).isdisjoint(fold["test_dates"])
    assert dates.index(fold["train_dates"][-1]) + 2 < dates.index(
        fold["validation_dates"][0]
    )


def test_final_holdout_is_never_used_for_fitting_or_tuning() -> None:
    dates = _dates(12)
    result = build_purged_chronological_splits(dates, _config())
    final = result["final_holdout"]

    assert final["dates"] == dates[-2:]
    assert final["training_dates"] == dates[:8]
    assert final["purged_dates"] == dates[8:10]
    assert final["used_for_threshold_selection"] is False
    assert final["used_for_feature_selection"] is False
    assert final["used_for_hyperparameter_tuning"] is False
    assert result["random_date_split_used"] is False


def test_every_horizon_uses_the_same_predeclared_maximum_horizon_purge() -> None:
    dates = _dates(12)
    one_day = build_purged_chronological_splits(dates, _config(), label_horizon=1)
    twenty_day = build_purged_chronological_splits(dates, _config(), label_horizon=2)

    assert one_day["folds"] == twenty_day["folds"]
    assert one_day["maximum_label_horizon"] == 2

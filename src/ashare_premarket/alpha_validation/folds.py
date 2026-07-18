from __future__ import annotations

from typing import Mapping, Sequence

from ashare_premarket.quant_foundation.contracts import canonical_checksum


def build_purged_chronological_splits(
    dates: Sequence[str],
    config: Mapping[str, object],
    *,
    label_horizon: int | None = None,
) -> dict[str, object]:
    ordered = tuple(map(str, dates))
    if not ordered or tuple(sorted(set(ordered))) != ordered:
        raise ValueError("split_dates_must_be_unique_and_chronological")
    minimum_training = _positive_int(config, "minimum_training_dates")
    validation_count = _positive_int(config, "validation_dates")
    test_count = _positive_int(config, "test_dates")
    holdout_count = _positive_int(config, "final_holdout_dates")
    maximum_horizon = _positive_int(config, "maximum_label_horizon")
    embargo = int(config.get("embargo_dates", 0))
    if embargo < 0:
        raise ValueError("invalid_split_embargo")
    if label_horizon is not None and not 0 < label_horizon <= maximum_horizon:
        raise ValueError("label_horizon_exceeds_predeclared_maximum")
    if config.get("mode") != "EXPANDING_PURGED_CHRONOLOGICAL":
        raise ValueError("invalid_goal12_split_mode")
    if holdout_count >= len(ordered):
        raise ValueError("insufficient_dates_for_final_holdout")

    development_end = len(ordered) - holdout_count
    cursor = minimum_training + maximum_horizon + embargo
    folds: list[dict[str, object]] = []
    fold_id = 1
    while cursor + validation_count + test_count <= development_end:
        training_end = cursor - maximum_horizon - embargo
        purged_start = training_end
        validation_start = cursor
        validation_end = validation_start + validation_count
        test_end = validation_end + test_count
        fold: dict[str, object] = {
            "fold_id": fold_id,
            "train_dates": ordered[:training_end],
            "purged_dates": ordered[purged_start:validation_start],
            "validation_dates": ordered[validation_start:validation_end],
            "test_dates": ordered[validation_end:test_end],
            "maximum_label_horizon": maximum_horizon,
            "embargo_dates": embargo,
            "training_mode": "EXPANDING_WINDOW",
            "random_date_split_used": False,
        }
        fold["checksum"] = canonical_checksum(fold)
        folds.append(fold)
        cursor += test_count
        fold_id += 1

    holdout_start = development_end
    final_training_end = holdout_start - maximum_horizon - embargo
    if final_training_end < minimum_training:
        raise ValueError("insufficient_purged_training_dates")
    final_holdout: dict[str, object] = {
        "training_dates": ordered[:final_training_end],
        "purged_dates": ordered[final_training_end:holdout_start],
        "dates": ordered[holdout_start:],
        "used_for_threshold_selection": False,
        "used_for_feature_selection": False,
        "used_for_hyperparameter_tuning": False,
    }
    final_holdout["checksum"] = canonical_checksum(final_holdout)
    result: dict[str, object] = {
        "split_version": "goal12_purged_chronological_v1",
        "mode": config["mode"],
        "maximum_label_horizon": maximum_horizon,
        "requested_label_horizon": label_horizon,
        "random_date_split_used": False,
        "folds": folds,
        "final_holdout": final_holdout,
    }
    result["checksum"] = canonical_checksum(result)
    return result


def _positive_int(config: Mapping[str, object], name: str) -> int:
    try:
        value = int(config[name])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid_split_value:{name}") from exc
    if value <= 0:
        raise ValueError(f"invalid_split_value:{name}")
    return value

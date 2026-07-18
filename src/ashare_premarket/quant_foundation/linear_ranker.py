from __future__ import annotations

import math
from collections import defaultdict
from datetime import date
from typing import Mapping, Sequence

from ashare_premarket.quant_foundation.contracts import (
    canonical_checksum,
    validate_research_output_fields,
)


def run_chronological_linear_ranker(
    feature_rows: Sequence[Mapping[str, object]],
    label_rows: Sequence[Mapping[str, object]],
    config: Mapping[str, object],
) -> dict[str, object]:
    model_config = dict(config["linear_ranker"])
    evaluation_config = dict(config["evaluation"])
    columns = tuple(map(str, model_config["feature_columns"]))
    minimum_dates = int(evaluation_config["minimum_training_dates"])
    ridge_lambda = float(model_config["ridge_lambda"])
    features = _validated_features(feature_rows)
    labels = _validated_labels(label_rows, features)

    by_date: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in features.values():
        by_date[str(row["date"])].append(row)

    scores: list[dict[str, object]] = []
    diagnostics: list[dict[str, object]] = []
    for test_date in sorted(by_date):
        test_rows = sorted(by_date[test_date], key=lambda row: str(row["symbol"]))
        training = [
            (feature, labels[key])
            for key, feature in features.items()
            if key in labels
            and str(feature["date"]) < test_date
            and str(labels[key]["label_available_at"]) < test_date
            and all(feature.get(column) is not None for column in columns)
        ]
        training_dates = sorted({str(feature["date"]) for feature, _ in training})
        fit = None
        if len(training_dates) >= minimum_dates:
            fit = _fit_fixed_ridge(training, columns, ridge_lambda)
            diagnostic = {
                "test_date": test_date,
                "training_row_count": len(training),
                "training_date_count": len(training_dates),
                "min_training_feature_date": training_dates[0],
                "max_training_feature_date": training_dates[-1],
                "max_training_label_available_at": max(
                    str(label["label_available_at"]) for _, label in training
                ),
                "ridge_lambda": ridge_lambda,
                "hyperparameter_selection": "PRE_SPECIFIED_NO_TUNING",
                "feature_columns": columns,
                "feature_means": fit["means"],
                "feature_scales": fit["scales"],
                "coefficients": fit["coefficients"],
                "intercept": fit["intercept"],
            }
            diagnostic["checksum"] = canonical_checksum(diagnostic)
            diagnostics.append(diagnostic)

        for row in test_rows:
            missing = sorted(column for column in columns if row.get(column) is None)
            reasons = {f"MISSING_MODEL_FEATURE:{column.upper()}" for column in missing}
            if not missing and fit is None:
                reasons.add("INSUFFICIENT_CHRONOLOGICAL_TRAINING_DATES")
            if reasons:
                model_score = None
                status = "ABSTAINED"
                trained_through = None
                label_available_through = None
                training_date_count = len(training_dates)
            else:
                model_score = _score(row, columns, fit)
                status = "SCORED"
                trained_through = training_dates[-1]
                label_available_through = max(
                    str(label["label_available_at"]) for _, label in training
                )
                training_date_count = len(training_dates)
            score_row: dict[str, object] = {
                "symbol": row["symbol"],
                "date": test_date,
                "model_version": model_config["version"],
                "model_score": model_score,
                "score_status": status,
                "abstention_reasons": tuple(sorted(reasons)),
                "trained_through_date": trained_through,
                "training_label_available_through": label_available_through,
                "training_date_count": training_date_count,
                "source_feature_checksum": row["checksum"],
                "source_snapshot_id": row["source_snapshot_id"],
                "research_only": True,
            }
            validate_research_output_fields(score_row)
            score_row["checksum"] = canonical_checksum(score_row)
            scores.append(score_row)

    result: dict[str, object] = {
        "model_version": model_config["version"],
        "research_only": True,
        "random_split_used": False,
        "hyperparameter_tuning_used": False,
        "final_holdout_tuning_used": False,
        "feature_columns": columns,
        "label_set_checksum": canonical_checksum(
            [labels[key]["checksum"] for key in sorted(labels)]
        ),
        "scores": scores,
        "fit_diagnostics": diagnostics,
    }
    result["checksum"] = canonical_checksum(result)
    return result


def _validated_features(
    rows: Sequence[Mapping[str, object]],
) -> dict[tuple[str, str], Mapping[str, object]]:
    result: dict[tuple[str, str], Mapping[str, object]] = {}
    lineages: set[tuple[str, str, str, str]] = set()
    for row in rows:
        expected = canonical_checksum({key: value for key, value in row.items() if key != "checksum"})
        if row.get("checksum") != expected:
            raise ValueError("feature_row_checksum_mismatch")
        key = (str(row.get("date", "")), str(row.get("symbol", "")))
        if key in result:
            raise ValueError("duplicate_feature_row_key")
        result[key] = row
        lineages.add(
            (
                str(row.get("source_snapshot_id", "")),
                str(row.get("feature_version", "")),
                str(row.get("code_commit", "")),
                str(row.get("adjustment", "")),
            )
        )
    if len(lineages) > 1:
        raise ValueError("mixed_feature_snapshot_lineage")
    return result


def _validated_labels(
    rows: Sequence[Mapping[str, object]],
    features: Mapping[tuple[str, str], Mapping[str, object]],
) -> dict[tuple[str, str], Mapping[str, object]]:
    result: dict[tuple[str, str], Mapping[str, object]] = {}
    for row in rows:
        expected = canonical_checksum({key: value for key, value in row.items() if key != "checksum"})
        if row.get("checksum") != expected:
            raise ValueError("label_row_checksum_mismatch")
        feature_date = str(row.get("date", ""))
        available = str(row.get("label_available_at", ""))
        try:
            parsed_date = date.fromisoformat(feature_date)
            parsed_available = date.fromisoformat(available)
        except ValueError as exc:
            raise ValueError("invalid_label_date") from exc
        if parsed_available <= parsed_date:
            raise ValueError("label_available_not_after_feature_date")
        try:
            forward_return = float(row["forward_return"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("invalid_forward_return_label") from exc
        if not math.isfinite(forward_return):
            raise ValueError("invalid_forward_return_label")
        key = (feature_date, str(row.get("symbol", "")))
        if key in result:
            raise ValueError("duplicate_label_row_key")
        if key not in features:
            raise ValueError("label_without_matching_feature_row")
        if row.get("source_snapshot_id") != features[key].get("source_snapshot_id"):
            raise ValueError("label_feature_snapshot_lineage_mismatch")
        result[key] = row
    return result


def _fit_fixed_ridge(
    training: Sequence[tuple[Mapping[str, object], Mapping[str, object]]],
    columns: Sequence[str],
    ridge_lambda: float,
) -> dict[str, object]:
    matrix = [[float(feature[column]) for column in columns] for feature, _ in training]
    targets = [float(label["forward_return"]) for _, label in training]
    means = [sum(row[index] for row in matrix) / len(matrix) for index in range(len(columns))]
    scales = []
    for index, mean in enumerate(means):
        variance = sum((row[index] - mean) ** 2 for row in matrix) / len(matrix)
        scale = math.sqrt(variance)
        scales.append(scale if scale > 1e-15 else 1.0)
    standardized = [
        [(row[index] - means[index]) / scales[index] for index in range(len(columns))]
        for row in matrix
    ]
    target_mean = sum(targets) / len(targets)
    centered_targets = [target - target_mean for target in targets]
    normal = [
        [
            sum(row[left] * row[right] for row in standardized)
            + (ridge_lambda if left == right else 0.0)
            for right in range(len(columns))
        ]
        for left in range(len(columns))
    ]
    projection = [
        sum(row[index] * target for row, target in zip(standardized, centered_targets))
        for index in range(len(columns))
    ]
    coefficients = _solve(normal, projection)
    return {
        "means": {column: _clean(means[index]) for index, column in enumerate(columns)},
        "scales": {column: _clean(scales[index]) for index, column in enumerate(columns)},
        "coefficients": {
            column: _clean(coefficients[index]) for index, column in enumerate(columns)
        },
        "intercept": _clean(target_mean),
    }


def _solve(matrix: Sequence[Sequence[float]], vector: Sequence[float]) -> list[float]:
    augmented = [list(row) + [vector[index]] for index, row in enumerate(matrix)]
    size = len(augmented)
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) <= 1e-15:
            raise ValueError("ridge_system_singular")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(augmented[row], augmented[column])
            ]
    return [row[-1] for row in augmented]


def _score(
    row: Mapping[str, object],
    columns: Sequence[str],
    fit: Mapping[str, object],
) -> float:
    means = dict(fit["means"])
    scales = dict(fit["scales"])
    coefficients = dict(fit["coefficients"])
    score = float(fit["intercept"])
    for column in columns:
        score += (
            (float(row[column]) - float(means[column]))
            / float(scales[column])
            * float(coefficients[column])
        )
    return _clean(score)


def _clean(value: float) -> float:
    rounded = round(value, 12)
    return 0.0 if rounded == 0 else rounded

from __future__ import annotations

import math
from collections import defaultdict
from typing import Mapping, Sequence

from ashare_premarket.alpha_validation.preprocessing import (
    fit_training_preprocessor,
    transform_row,
)
from ashare_premarket.alpha_validation.statistics import (
    mean,
    ndcg_at_k,
    pearson_correlation,
    spearman_correlation,
    standard_deviation,
)
from ashare_premarket.quant_foundation.contracts import (
    canonical_checksum,
    validate_research_output_fields,
)


def run_purged_fixed_linear_baseline(
    feature_rows: Sequence[Mapping[str, object]],
    label_rows: Sequence[Mapping[str, object]],
    splits: Mapping[str, object],
    model_config: Mapping[str, object],
    metrics_config: Mapping[str, object],
) -> dict[str, object]:
    features = _validated_by_key(feature_rows, "model_feature")
    labels = _validated_by_key(label_rows, "model_label")
    columns = tuple(map(str, model_config["feature_columns"]))
    structural = tuple(
        f"STRUCTURALLY_MISSING_MODEL_FEATURE:{column.upper()}"
        for column in columns
        if not any(row.get(column) is not None for row in features.values())
    )
    if structural:
        return _insufficient_result(model_config, columns, structural)
    if splits.get("random_date_split_used") is not False:
        raise ValueError("goal12_model_requires_chronological_splits")

    diagnostics: list[dict[str, object]] = []
    scores: list[dict[str, object]] = []
    fold_metrics: list[dict[str, object]] = []
    for fold in splits["folds"]:
        fit, diagnostic = _fit_segment(
            features,
            labels,
            tuple(fold["train_dates"]),
            tuple(fold["validation_dates"]) + tuple(fold["test_dates"]),
            columns,
            float(model_config["ridge_lambda"]),
            f"fold_{fold['fold_id']}",
        )
        diagnostics.append(diagnostic)
        validation_scores = _score_segment(
            features,
            labels,
            tuple(fold["validation_dates"]),
            fit,
            columns,
            f"fold_{fold['fold_id']}_validation",
        )
        test_scores = _score_segment(
            features,
            labels,
            tuple(fold["test_dates"]),
            fit,
            columns,
            f"fold_{fold['fold_id']}_test",
        )
        scores.extend(validation_scores)
        scores.extend(test_scores)
        diagnostic["mean_absolute_contribution"] = _mean_absolute_contribution(
            validation_scores + test_scores, columns
        )
        diagnostic["checksum"] = canonical_checksum(
            {key: value for key, value in diagnostic.items() if key != "checksum"}
        )
        fold_metrics.append(
            {
                "fold_id": fold["fold_id"],
                "validation": _evaluate_scores(
                    validation_scores,
                    labels,
                    int(metrics_config["minimum_cross_section"]),
                    int(metrics_config["top_k"]),
                ),
                "test": _evaluate_scores(
                    test_scores,
                    labels,
                    int(metrics_config["minimum_cross_section"]),
                    int(metrics_config["top_k"]),
                ),
            }
        )

    final = dict(splits["final_holdout"])
    final_fit, final_diagnostic = _fit_segment(
        features,
        labels,
        tuple(final["training_dates"]),
        tuple(final["dates"]),
        columns,
        float(model_config["ridge_lambda"]),
        "final_holdout",
    )
    final_scores = _score_segment(
        features,
        labels,
        tuple(final["dates"]),
        final_fit,
        columns,
        "final_holdout",
    )
    final_diagnostic["mean_absolute_contribution"] = _mean_absolute_contribution(
        final_scores, columns
    )
    final_diagnostic["checksum"] = canonical_checksum(
        {key: value for key, value in final_diagnostic.items() if key != "checksum"}
    )
    diagnostics.append(final_diagnostic)
    scores.extend(final_scores)
    result: dict[str, object] = {
        "status": "COMPLETE_RESEARCH_ONLY",
        "model_version": str(model_config["version"]),
        "feature_columns": columns,
        "ridge_lambda": float(model_config["ridge_lambda"]),
        "research_only": True,
        "production_ready": False,
        "random_date_split_used": False,
        "hyperparameter_tuning_used": False,
        "final_holdout_tuning_used": False,
        "primary_missing_policy": "EXCLUDE_NO_SILENT_IMPUTATION",
        "scores": scores,
        "fit_diagnostics": diagnostics,
        "fold_metrics": fold_metrics,
        "final_holdout_metrics": _evaluate_scores(
            final_scores,
            labels,
            int(metrics_config["minimum_cross_section"]),
            int(metrics_config["top_k"]),
        ),
        "coefficient_sign_stability": _coefficient_sign_stability(diagnostics, columns),
        "feature_contribution_stability": _contribution_stability(diagnostics, columns),
        "insufficiency_reasons": (),
    }
    validate_research_output_fields(result)
    result["checksum"] = canonical_checksum(result)
    return result


def _fit_segment(
    features: Mapping[tuple[str, str], Mapping[str, object]],
    labels: Mapping[tuple[str, str], Mapping[str, object]],
    train_dates: tuple[str, ...],
    evaluation_dates: tuple[str, ...],
    columns: tuple[str, ...],
    ridge_lambda: float,
    segment_id: str,
) -> tuple[dict[str, object], dict[str, object]]:
    if not train_dates or not evaluation_dates:
        raise ValueError("empty_goal12_model_segment")
    train_set = set(train_dates)
    training: list[tuple[Mapping[str, object], Mapping[str, object]]] = []
    for key in sorted(features):
        feature = features[key]
        label = labels.get(key)
        if key[0] not in train_set or label is None or label.get("label_status") != "AVAILABLE":
            continue
        if any(feature.get(column) is None for column in columns):
            continue
        available = str(label.get("label_available_at", ""))
        if not available or available >= min(evaluation_dates):
            raise ValueError("goal12_model_training_label_overlaps_evaluation")
        training.append((feature, label))
    if not training:
        raise ValueError("insufficient_purged_model_training_rows")
    preprocessor = fit_training_preprocessor(
        [feature for feature, _ in training],
        columns,
        lower_quantile=0.0,
        upper_quantile=1.0,
        allow_imputation=False,
        maximum_missing_rate=0.0,
    )
    matrix = [transform_row(feature, preprocessor) for feature, _ in training]
    if any(row is None for row in matrix):
        raise ValueError("unexpected_missing_training_transform")
    numeric_matrix = [[float(row[column]) for column in columns] for row in matrix if row]
    targets = [float(label["forward_return"]) for _, label in training]
    fit = _fit_ridge(numeric_matrix, targets, columns, ridge_lambda)
    fit["preprocessor"] = preprocessor
    diagnostic: dict[str, object] = {
        "segment_id": segment_id,
        "fit_scope": "TRAINING_ONLY",
        "training_row_count": len(training),
        "training_date_count": len({str(feature["date"]) for feature, _ in training}),
        "min_training_date": min(str(feature["date"]) for feature, _ in training),
        "max_training_date": max(str(feature["date"]) for feature, _ in training),
        "max_training_label_available_at": max(
            str(label["label_available_at"]) for _, label in training
        ),
        "evaluation_start_date": min(evaluation_dates),
        "preprocessor": preprocessor,
        "coefficients": fit["coefficients"],
        "intercept": fit["intercept"],
        "ridge_lambda": ridge_lambda,
        "hyperparameter_selection": "PRE_SPECIFIED_NO_TUNING",
    }
    diagnostic["checksum"] = canonical_checksum(diagnostic)
    return fit, diagnostic


def _score_segment(
    features: Mapping[tuple[str, str], Mapping[str, object]],
    labels: Mapping[tuple[str, str], Mapping[str, object]],
    dates: tuple[str, ...],
    fit: Mapping[str, object],
    columns: tuple[str, ...],
    segment_id: str,
) -> list[dict[str, object]]:
    date_set = set(dates)
    rows: list[dict[str, object]] = []
    coefficients = dict(fit["coefficients"])
    for key in sorted(features):
        if key[0] not in date_set:
            continue
        label = labels.get(key)
        if label is None or label.get("label_status") != "AVAILABLE":
            continue
        transformed = transform_row(features[key], fit["preprocessor"])
        if transformed is None:
            continue
        contributions = {
            column: _clean(transformed[column] * float(coefficients[column]))
            for column in columns
        }
        score = float(fit["intercept"]) + sum(contributions.values())
        row: dict[str, object] = {
            "date": key[0],
            "symbol": key[1],
            "segment_id": segment_id,
            "model_score": _clean(score),
            "feature_contributions": contributions,
            "source_feature_checksum": features[key]["checksum"],
            "research_only": True,
        }
        row["checksum"] = canonical_checksum(row)
        rows.append(row)
    return rows


def _evaluate_scores(
    scores: Sequence[Mapping[str, object]],
    labels: Mapping[tuple[str, str], Mapping[str, object]],
    minimum_cross_section: int,
    top_k: int,
) -> dict[str, object]:
    by_date: dict[str, list[tuple[str, float, float]]] = defaultdict(list)
    for row in scores:
        key = (str(row["date"]), str(row["symbol"]))
        label = labels[key]
        by_date[key[0]].append((key[1], float(row["model_score"]), float(label["forward_return"])))
    observations: list[dict[str, object]] = []
    previous_top: set[str] | None = None
    for trade_date in sorted(by_date):
        rows = sorted(by_date[trade_date])
        if len(rows) < minimum_cross_section:
            continue
        symbols = [row[0] for row in rows]
        predicted = [row[1] for row in rows]
        realized = [row[2] for row in rows]
        effective_k = min(top_k, len(rows))
        predicted_indices = sorted(
            range(len(rows)), key=lambda index: (-predicted[index], symbols[index])
        )[:effective_k]
        actual_indices = sorted(
            range(len(rows)), key=lambda index: (-realized[index], symbols[index])
        )[:effective_k]
        predicted_top = {symbols[index] for index in predicted_indices}
        actual_top = {symbols[index] for index in actual_indices}
        overlap_actual = len(predicted_top & actual_top)
        consecutive_overlap = (
            None if previous_top is None else len(previous_top & predicted_top) / effective_k
        )
        observations.append(
            {
                "date": trade_date,
                "row_count": len(rows),
                "ic": pearson_correlation(predicted, realized),
                "rank_ic": spearman_correlation(predicted, realized),
                "precision_at_k": _clean(overlap_actual / effective_k),
                "recall_at_k": _clean(overlap_actual / len(actual_top)),
                "ndcg_at_k": ndcg_at_k(predicted, realized, effective_k),
                "top_k_overlap": _clean(consecutive_overlap) if consecutive_overlap is not None else None,
                "ranking_turnover": _clean(1.0 - consecutive_overlap) if consecutive_overlap is not None else None,
                "prediction_dispersion": standard_deviation(predicted),
            }
        )
        previous_top = predicted_top
    rank_ics = [float(row["rank_ic"]) for row in observations if row["rank_ic"] is not None]
    return {
        "observation_date_count": len(observations),
        "observation_row_count": sum(int(row["row_count"]) for row in observations),
        "effective_date_sample_size": len(observations),
        "rank_ic_mean": mean(rank_ics),
        "ic_mean": mean([float(row["ic"]) for row in observations if row["ic"] is not None]),
        "precision_at_k_mean": mean([float(row["precision_at_k"]) for row in observations]),
        "recall_at_k_mean": mean([float(row["recall_at_k"]) for row in observations]),
        "ndcg_at_k_mean": mean([float(row["ndcg_at_k"]) for row in observations]),
        "top_k_overlap_mean": mean([float(row["top_k_overlap"]) for row in observations if row["top_k_overlap"] is not None]) or 1.0,
        "ranking_turnover_mean": mean([float(row["ranking_turnover"]) for row in observations if row["ranking_turnover"] is not None]) or 0.0,
        "prediction_dispersion_mean": mean([float(row["prediction_dispersion"]) for row in observations if row["prediction_dispersion"] is not None]),
        "by_date": observations,
    }


def _fit_ridge(
    matrix: Sequence[Sequence[float]],
    targets: Sequence[float],
    columns: Sequence[str],
    ridge_lambda: float,
) -> dict[str, object]:
    target_mean = sum(targets) / len(targets)
    centered = [target - target_mean for target in targets]
    normal = [
        [
            sum(row[left] * row[right] for row in matrix)
            + (ridge_lambda if left == right else 0.0)
            for right in range(len(columns))
        ]
        for left in range(len(columns))
    ]
    projection = [
        sum(row[index] * target for row, target in zip(matrix, centered))
        for index in range(len(columns))
    ]
    coefficients = _solve(normal, projection)
    return {
        "intercept": _clean(target_mean),
        "coefficients": {
            column: _clean(coefficients[index]) for index, column in enumerate(columns)
        },
    }


def _solve(matrix: Sequence[Sequence[float]], vector: Sequence[float]) -> list[float]:
    augmented = [list(row) + [vector[index]] for index, row in enumerate(matrix)]
    for column in range(len(augmented)):
        pivot = max(range(column, len(augmented)), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) <= 1e-15:
            raise ValueError("goal12_ridge_system_singular")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(len(augmented)):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(augmented[row], augmented[column])
            ]
    return [row[-1] for row in augmented]


def _validated_by_key(
    rows: Sequence[Mapping[str, object]], kind: str
) -> dict[tuple[str, str], Mapping[str, object]]:
    output: dict[tuple[str, str], Mapping[str, object]] = {}
    for row in rows:
        expected = canonical_checksum({key: value for key, value in row.items() if key != "checksum"})
        if row.get("checksum") != expected:
            raise ValueError(f"goal12_{kind}_checksum_mismatch")
        key = (str(row.get("date", "")), str(row.get("symbol", "")))
        if key in output:
            raise ValueError(f"duplicate_goal12_{kind}_key")
        output[key] = row
    return output


def _mean_absolute_contribution(
    scores: Sequence[Mapping[str, object]], columns: Sequence[str]
) -> dict[str, float | None]:
    return {
        column: mean(
            [abs(float(dict(row["feature_contributions"])[column])) for row in scores]
        )
        for column in columns
    }


def _coefficient_sign_stability(
    diagnostics: Sequence[Mapping[str, object]], columns: Sequence[str]
) -> float | None:
    rates: list[float] = []
    for column in columns:
        signs = [
            1 if float(dict(row["coefficients"])[column]) > 0 else -1
            if float(dict(row["coefficients"])[column]) < 0 else 0
            for row in diagnostics
        ]
        rates.append(max(signs.count(-1), signs.count(0), signs.count(1)) / len(signs))
    return mean(rates)


def _contribution_stability(
    diagnostics: Sequence[Mapping[str, object]], columns: Sequence[str]
) -> float | None:
    if len(columns) == 1 or len(diagnostics) < 2:
        return 1.0
    reference = [float(dict(diagnostics[0]["mean_absolute_contribution"])[column] or 0) for column in columns]
    correlations = [
        spearman_correlation(
            reference,
            [float(dict(row["mean_absolute_contribution"])[column] or 0) for column in columns],
        )
        for row in diagnostics[1:]
    ]
    return mean([value for value in correlations if value is not None])


def _insufficient_result(
    config: Mapping[str, object], columns: tuple[str, ...], reasons: tuple[str, ...]
) -> dict[str, object]:
    result: dict[str, object] = {
        "status": "INSUFFICIENT_DATA",
        "model_version": str(config["version"]),
        "feature_columns": columns,
        "research_only": True,
        "production_ready": False,
        "random_date_split_used": False,
        "hyperparameter_tuning_used": False,
        "final_holdout_tuning_used": False,
        "scores": [],
        "fit_diagnostics": [],
        "fold_metrics": [],
        "final_holdout_metrics": None,
        "coefficient_sign_stability": None,
        "feature_contribution_stability": None,
        "insufficiency_reasons": reasons,
    }
    result["checksum"] = canonical_checksum(result)
    return result


def _clean(value: float) -> float:
    rounded = round(value, 12)
    return 0.0 if rounded == 0 else rounded

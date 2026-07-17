from __future__ import annotations

import math
from collections import defaultdict
from datetime import date
from typing import Mapping, Sequence

from ashare_premarket.quant_foundation.contracts import canonical_checksum


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


def spearman_rank_correlation(left: Sequence[float], right: Sequence[float]) -> float | None:
    if len(left) != len(right):
        return None
    return pearson_correlation(_average_ranks(left), _average_ranks(right))


def precision_recall_at_k(
    scores: Sequence[float],
    realized: Sequence[float],
    k: int,
) -> tuple[float, float]:
    if len(scores) != len(realized) or not scores or k <= 0:
        raise ValueError("invalid_precision_recall_inputs")
    effective_k = min(k, len(scores))
    predicted = set(sorted(range(len(scores)), key=lambda index: (-scores[index], index))[:effective_k])
    actual = set(sorted(range(len(realized)), key=lambda index: (-realized[index], index))[:effective_k])
    overlap = len(predicted & actual)
    return _clean(overlap / effective_k), _clean(overlap / len(actual))


def ranking_turnover(previous: set[str], current: set[str]) -> float:
    if not previous and not current:
        return 0.0
    denominator = max(len(previous), len(current))
    return _clean(1.0 - len(previous & current) / denominator)


def build_walk_forward_folds(
    dates: Sequence[str],
    *,
    minimum_training_dates: int,
    test_date_count: int,
) -> list[dict[str, object]]:
    ordered = sorted(set(map(str, dates)))
    if minimum_training_dates <= 0 or test_date_count <= 0:
        raise ValueError("invalid_walk_forward_configuration")
    folds: list[dict[str, object]] = []
    start = minimum_training_dates
    fold_id = 1
    while start < len(ordered):
        test_dates = ordered[start : start + test_date_count]
        if not test_dates:
            break
        folds.append(
            {
                "fold_id": fold_id,
                "train_dates": tuple(ordered[:start]),
                "test_dates": tuple(test_dates),
                "training_mode": "EXPANDING_WINDOW",
                "random_split_used": False,
            }
        )
        start += test_date_count
        fold_id += 1
    return folds


def evaluate_rankings(
    feature_rows: Sequence[Mapping[str, object]],
    alpha_rows: Sequence[Mapping[str, object]],
    linear_score_rows: Sequence[Mapping[str, object]],
    label_rows: Sequence[Mapping[str, object]],
    config: Mapping[str, object],
) -> dict[str, object]:
    features = _validated_rows(feature_rows, "feature")
    alpha = _validated_rows(alpha_rows, "alpha")
    linear = _validated_rows(linear_score_rows, "linear_score")
    labels = _validated_labels(label_rows, features)
    _validate_score_feature_lineage(alpha, features, "alpha")
    _validate_score_feature_lineage(linear, features, "linear_score")
    evaluation_config = dict(config["evaluation"])
    top_k = int(evaluation_config["top_k"])
    minimum_cross_section = int(evaluation_config["minimum_cross_section"])

    streams = {
        "interpretable_alpha": _score_stream(alpha, "alpha_score"),
        "risk_adjusted_alpha": _score_stream(alpha, "risk_adjusted_score"),
        "linear_ranker": _score_stream(linear, "model_score"),
    }
    dates = sorted({key[0] for key in features})
    folds = build_walk_forward_folds(
        dates,
        minimum_training_dates=int(evaluation_config["minimum_training_dates"]),
        test_date_count=int(evaluation_config["walk_forward_test_dates"]),
    )
    policy_metrics = {
        policy: _evaluate_policy(
            scores,
            labels,
            top_k,
            minimum_cross_section,
            dates,
        )
        for policy, scores in streams.items()
    }
    walk_forward_policy_metrics = [
        {
            "fold_id": fold["fold_id"],
            "training_date_count": len(fold["train_dates"]),
            "train_dates_end": max(fold["train_dates"]),
            "test_dates": fold["test_dates"],
            "policy_metrics": {
                policy: _evaluate_policy(
                    scores,
                    labels,
                    top_k,
                    minimum_cross_section,
                    fold["test_dates"],
                )
                for policy, scores in streams.items()
            },
        }
        for fold in folds
    ]
    stability = _feature_stability(
        features,
        folds,
        tuple(map(str, dict(config["linear_ranker"])["feature_columns"])),
    )
    result: dict[str, object] = {
        "evaluation_version": evaluation_config["version"],
        "research_only": True,
        "random_split_used": False,
        "future_leakage_allowed": False,
        "top_k": top_k,
        "walk_forward_folds": folds,
        "walk_forward_policy_metrics": walk_forward_policy_metrics,
        "policy_metrics": policy_metrics,
        "feature_stability": stability,
        "input_checksums": {
            "features": canonical_checksum([features[key]["checksum"] for key in sorted(features)]),
            "alpha": canonical_checksum([alpha[key]["checksum"] for key in sorted(alpha)]),
            "linear_scores": canonical_checksum([linear[key]["checksum"] for key in sorted(linear)]),
            "labels": canonical_checksum([labels[key]["checksum"] for key in sorted(labels)]),
        },
    }
    result["checksum"] = canonical_checksum(result)
    return result


def _evaluate_policy(
    scores: Mapping[tuple[str, str], float],
    labels: Mapping[tuple[str, str], Mapping[str, object]],
    top_k: int,
    minimum_cross_section: int,
    evaluation_dates: Sequence[str],
) -> dict[str, object]:
    by_date: dict[str, list[tuple[str, float, float]]] = defaultdict(list)
    for key, score in scores.items():
        if key in labels:
            by_date[key[0]].append((key[1], score, float(labels[key]["forward_return"])))
    observations: list[dict[str, object]] = []
    skipped_dates: list[dict[str, object]] = []
    previous_top: set[str] | None = None
    turnovers: list[float] = []
    for trade_date in evaluation_dates:
        rows = sorted(by_date[trade_date])
        if len(rows) < minimum_cross_section:
            skipped_dates.append(
                {
                    "date": trade_date,
                    "labeled_score_row_count": len(rows),
                    "minimum_cross_section": minimum_cross_section,
                    "reason": "INSUFFICIENT_SCORED_CROSS_SECTION",
                }
            )
            continue
        symbols = [row[0] for row in rows]
        score_values = [row[1] for row in rows]
        realized = [row[2] for row in rows]
        precision, recall = precision_recall_at_k(score_values, realized, top_k)
        effective_k = min(top_k, len(rows))
        current_top = set(
            symbols[index]
            for index in sorted(
                range(len(rows)), key=lambda index: (-score_values[index], symbols[index])
            )[:effective_k]
        )
        turnover = None if previous_top is None else ranking_turnover(previous_top, current_top)
        if turnover is not None:
            turnovers.append(turnover)
        previous_top = current_top
        observations.append(
            {
                "date": trade_date,
                "row_count": len(rows),
                "ic": pearson_correlation(score_values, realized),
                "rank_ic": spearman_rank_correlation(score_values, realized),
                "precision_at_k": precision,
                "recall_at_k": recall,
                "ranking_turnover": turnover,
            }
        )
    ic_values = [float(row["ic"]) for row in observations if row["ic"] is not None]
    rank_ic_values = [float(row["rank_ic"]) for row in observations if row["rank_ic"] is not None]
    return {
        "observation_date_count": len(observations),
        "observation_row_count": sum(int(row["row_count"]) for row in observations),
        "ic_mean": _mean_or_none(ic_values),
        "ic_stability_std": _std_or_none(ic_values),
        "ic_positive_rate": _positive_rate(ic_values),
        "rank_ic_mean": _mean_or_none(rank_ic_values),
        "rank_ic_stability_std": _std_or_none(rank_ic_values),
        "rank_ic_positive_rate": _positive_rate(rank_ic_values),
        "rank_ic_sign_flip_count": _sign_flips(rank_ic_values),
        "precision_at_k_mean": _mean_or_none([float(row["precision_at_k"]) for row in observations]),
        "recall_at_k_mean": _mean_or_none([float(row["recall_at_k"]) for row in observations]),
        "ranking_turnover_mean": _mean_or_none(turnovers) if turnovers else 0.0,
        "by_date": observations,
        "skipped_dates": skipped_dates,
    }


def _feature_stability(
    features: Mapping[tuple[str, str], Mapping[str, object]],
    folds: Sequence[Mapping[str, object]],
    columns: Sequence[str],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for fold in folds:
        train_dates = set(map(str, fold["train_dates"]))
        test_dates = set(map(str, fold["test_dates"]))
        for column in columns:
            train = [
                float(row[column])
                for (trade_date, _), row in features.items()
                if trade_date in train_dates and row.get(column) is not None
            ]
            test = [
                float(row[column])
                for (trade_date, _), row in features.items()
                if trade_date in test_dates and row.get(column) is not None
            ]
            if not train or not test:
                continue
            train_mean = sum(train) / len(train)
            test_mean = sum(test) / len(test)
            scale = _std(train)
            normalized_shift = abs(test_mean - train_mean) / scale if scale > 0 else abs(test_mean - train_mean)
            output.append(
                {
                    "fold_id": fold["fold_id"],
                    "feature": column,
                    "train_row_count": len(train),
                    "test_row_count": len(test),
                    "train_mean": _clean(train_mean),
                    "test_mean": _clean(test_mean),
                    "normalized_mean_shift": _clean(normalized_shift),
                    "train_dates_end": max(train_dates),
                    "test_dates_start": min(test_dates),
                }
            )
    return output


def _score_stream(
    rows: Mapping[tuple[str, str], Mapping[str, object]],
    score_field: str,
) -> dict[tuple[str, str], float]:
    return {
        key: float(row[score_field])
        for key, row in rows.items()
        if row.get("score_status") == "SCORED" and row.get(score_field) is not None
    }


def _validated_rows(
    rows: Sequence[Mapping[str, object]],
    kind: str,
) -> dict[tuple[str, str], Mapping[str, object]]:
    result: dict[tuple[str, str], Mapping[str, object]] = {}
    for row in rows:
        expected = canonical_checksum({key: value for key, value in row.items() if key != "checksum"})
        if row.get("checksum") != expected:
            raise ValueError(f"{kind}_row_checksum_mismatch")
        key = (str(row.get("date", "")), str(row.get("symbol", "")))
        if key in result:
            raise ValueError(f"duplicate_{kind}_row_key")
        result[key] = row
    return result


def _validated_labels(
    rows: Sequence[Mapping[str, object]],
    features: Mapping[tuple[str, str], Mapping[str, object]],
) -> dict[tuple[str, str], Mapping[str, object]]:
    labels = _validated_rows(rows, "label")
    for key, row in labels.items():
        try:
            feature_date = date.fromisoformat(key[0])
            available = date.fromisoformat(str(row["label_available_at"]))
            value = float(row["forward_return"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("invalid_label_contract") from exc
        if available <= feature_date or not math.isfinite(value):
            raise ValueError("invalid_label_contract")
        if key not in features:
            raise ValueError("label_without_matching_feature_row")
        if row.get("source_snapshot_id") != features[key].get("source_snapshot_id"):
            raise ValueError("label_feature_snapshot_lineage_mismatch")
    return labels


def _validate_score_feature_lineage(
    scores: Mapping[tuple[str, str], Mapping[str, object]],
    features: Mapping[tuple[str, str], Mapping[str, object]],
    kind: str,
) -> None:
    for key, row in scores.items():
        if key not in features:
            raise ValueError(f"{kind}_without_matching_feature_row")
        feature = features[key]
        if row.get("source_snapshot_id") != feature.get("source_snapshot_id"):
            raise ValueError(f"{kind}_feature_snapshot_lineage_mismatch")
        if row.get("source_feature_checksum") != feature.get("checksum"):
            raise ValueError(f"{kind}_feature_checksum_lineage_mismatch")


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


def _mean_or_none(values: Sequence[float]) -> float | None:
    return _clean(sum(values) / len(values)) if values else None


def _std_or_none(values: Sequence[float]) -> float | None:
    return _clean(_std(values)) if values else None


def _std(values: Sequence[float]) -> float:
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / len(values))


def _positive_rate(values: Sequence[float]) -> float | None:
    return _clean(sum(value > 0 for value in values) / len(values)) if values else None


def _sign_flips(values: Sequence[float]) -> int:
    signs = [1 if value > 0 else -1 for value in values if value != 0]
    return sum(left != right for left, right in zip(signs, signs[1:]))


def _clean(value: float) -> float:
    rounded = round(value, 12)
    return 0.0 if rounded == 0 else rounded

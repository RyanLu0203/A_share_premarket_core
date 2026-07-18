from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from ashare_premarket.quant_foundation.alpha import build_interpretable_alpha
from ashare_premarket.quant_foundation.contracts import canonical_checksum
from ashare_premarket.quant_foundation.evaluation import (
    build_walk_forward_folds,
    evaluate_rankings,
    pearson_correlation,
    precision_recall_at_k,
    ranking_turnover,
    spearman_rank_correlation,
)
from ashare_premarket.quant_foundation.features import build_feature_rows, load_feature_config
from ashare_premarket.quant_foundation.linear_ranker import run_chronological_linear_ranker
from .conftest import make_snapshot

ROOT = Path(__file__).resolve().parents[2]


def _labels(features: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in features:
        label: dict[str, object] = {
            "date": row["date"],
            "symbol": row["symbol"],
            "label_available_at": (
                date.fromisoformat(str(row["date"])) + timedelta(days=1)
            ).isoformat(),
            "forward_return": 0.8 * float(row["momentum_20d"] or 0.0)
            + 0.2 * float(row["trend_strength_20d"] or 0.0)
            - 0.1 * float(row["volatility_20d"] or 0.0),
            "label_version": "synthetic_forward_1d_v1",
            "source_snapshot_id": row["source_snapshot_id"],
        }
        label["checksum"] = canonical_checksum(label)
        rows.append(label)
    return rows


def test_ranking_metrics_have_known_values() -> None:
    scores = [3.0, 2.0, 1.0]
    realized = [0.3, 0.2, 0.1]
    assert pearson_correlation(scores, realized) == pytest.approx(1.0)
    assert spearman_rank_correlation(scores, realized) == pytest.approx(1.0)
    assert spearman_rank_correlation(list(reversed(scores)), realized) == pytest.approx(-1.0)
    assert precision_recall_at_k(scores, realized, 1) == (1.0, 1.0)
    assert precision_recall_at_k(list(reversed(scores)), realized, 1) == (0.0, 0.0)
    assert ranking_turnover({"A"}, {"A"}) == 0.0
    assert ranking_turnover({"A"}, {"B"}) == 1.0


def test_walk_forward_folds_are_strictly_chronological_and_expanding() -> None:
    dates = [f"2026-01-{day:02d}" for day in range(1, 31)]
    folds = build_walk_forward_folds(dates, minimum_training_dates=10, test_date_count=5)

    assert len(folds) == 4
    assert all(max(fold["train_dates"]) < min(fold["test_dates"]) for fold in folds)
    assert [len(fold["train_dates"]) for fold in folds] == [10, 15, 20, 25]
    assert all(fold["random_split_used"] is False for fold in folds)


def test_evaluation_compares_all_policies_with_stability_and_turnover() -> None:
    config = load_feature_config(ROOT)
    features = build_feature_rows(make_snapshot(), config)
    labels = _labels(features)
    alpha = build_interpretable_alpha(features, config)
    linear = run_chronological_linear_ranker(features, labels, config)
    result = evaluate_rankings(features, alpha, linear["scores"], labels, config)

    assert result == evaluate_rankings(features, alpha, linear["scores"], labels, config)
    assert result["evaluation_version"] == "goal11_chronological_evaluation_v1"
    assert result["random_split_used"] is False
    assert result["future_leakage_allowed"] is False
    assert set(result["policy_metrics"]) == {
        "interpretable_alpha",
        "linear_ranker",
        "risk_adjusted_alpha",
    }
    for policy in result["policy_metrics"].values():
        assert policy["observation_date_count"] > 0
        assert policy["skipped_dates"]
        assert all(
            row["reason"] == "INSUFFICIENT_SCORED_CROSS_SECTION"
            for row in policy["skipped_dates"]
        )
        assert policy["rank_ic_mean"] is not None
        assert policy["rank_ic_stability_std"] is not None
        assert 0.0 <= policy["precision_at_k_mean"] <= 1.0
        assert 0.0 <= policy["recall_at_k_mean"] <= 1.0
        assert 0.0 <= policy["ranking_turnover_mean"] <= 1.0
    assert result["feature_stability"]
    assert result["walk_forward_policy_metrics"]
    assert all(
        max(fold["train_dates"]) < min(fold["test_dates"])
        for fold in result["walk_forward_folds"]
    )
    for fold, metrics in zip(
        result["walk_forward_folds"],
        result["walk_forward_policy_metrics"],
    ):
        assert metrics["fold_id"] == fold["fold_id"]
        assert metrics["test_dates"] == fold["test_dates"]
        assert set(metrics["policy_metrics"]) == set(result["policy_metrics"])
        assert all(
            row["date"] in fold["test_dates"]
            for policy in metrics["policy_metrics"].values()
            for row in policy["by_date"]
        )
    assert result["checksum"] == canonical_checksum(
        {key: value for key, value in result.items() if key != "checksum"}
    )


def test_evaluation_rejects_tampered_labels() -> None:
    config = load_feature_config(ROOT)
    features = build_feature_rows(make_snapshot(), config)
    labels = _labels(features)
    alpha = build_interpretable_alpha(features, config)
    linear = run_chronological_linear_ranker(features, labels, config)
    labels[-1]["forward_return"] = 5.0
    with pytest.raises(ValueError, match="label_row_checksum_mismatch"):
        evaluate_rankings(features, alpha, linear["scores"], labels, config)


def test_evaluation_rejects_label_feature_lineage_mismatch() -> None:
    config = load_feature_config(ROOT)
    features = build_feature_rows(make_snapshot(), config)
    labels = _labels(features)
    alpha = build_interpretable_alpha(features, config)
    linear = run_chronological_linear_ranker(features, labels, config)
    labels[-1]["source_snapshot_id"] = "different-governed-snapshot"
    labels[-1]["checksum"] = canonical_checksum(
        {key: value for key, value in labels[-1].items() if key != "checksum"}
    )

    with pytest.raises(ValueError, match="label_feature_snapshot_lineage_mismatch"):
        evaluate_rankings(features, alpha, linear["scores"], labels, config)


def test_evaluation_rejects_score_feature_lineage_mismatch() -> None:
    config = load_feature_config(ROOT)
    features = build_feature_rows(make_snapshot(), config)
    labels = _labels(features)
    alpha = build_interpretable_alpha(features, config)
    linear = run_chronological_linear_ranker(features, labels, config)
    alpha[-1]["source_snapshot_id"] = "different-governed-snapshot"
    alpha[-1]["checksum"] = canonical_checksum(
        {key: value for key, value in alpha[-1].items() if key != "checksum"}
    )

    with pytest.raises(ValueError, match="alpha_feature_snapshot_lineage_mismatch"):
        evaluate_rankings(features, alpha, linear["scores"], labels, config)

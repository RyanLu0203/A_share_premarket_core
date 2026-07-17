from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from ashare_premarket.quant_foundation.contracts import canonical_checksum
from ashare_premarket.quant_foundation.features import build_feature_rows, load_feature_config
from ashare_premarket.quant_foundation.linear_ranker import run_chronological_linear_ranker
from .conftest import make_snapshot

ROOT = Path(__file__).resolve().parents[2]


def _labels(features: list[dict[str, object]]) -> list[dict[str, object]]:
    labels: list[dict[str, object]] = []
    for row in features:
        available = (date.fromisoformat(str(row["date"])) + timedelta(days=1)).isoformat()
        momentum = float(row["momentum_20d"] or 0.0)
        trend = float(row["trend_strength_20d"] or 0.0)
        volatility = float(row["volatility_20d"] or 0.0)
        label: dict[str, object] = {
            "date": row["date"],
            "symbol": row["symbol"],
            "label_available_at": available,
            "forward_return": 0.7 * momentum + 0.3 * trend - 0.2 * volatility,
            "label_version": "synthetic_forward_1d_v1",
            "source_snapshot_id": row["source_snapshot_id"],
        }
        label["checksum"] = canonical_checksum(label)
        labels.append(label)
    return labels


def _last_scored(result: dict[str, object]) -> list[dict[str, object]]:
    scores = result["scores"]
    last_date = max(str(row["date"]) for row in scores if row["score_status"] == "SCORED")
    return [row for row in scores if row["date"] == last_date]


def test_linear_ranker_is_fixed_deterministic_and_chronological() -> None:
    config = load_feature_config(ROOT)
    features = build_feature_rows(make_snapshot(), config)
    result = run_chronological_linear_ranker(features, _labels(features), config)
    scored = _last_scored(result)
    diagnostic = result["fit_diagnostics"][-1]

    assert result == run_chronological_linear_ranker(features, _labels(features), config)
    assert result["model_version"] == "goal11_fixed_ridge_ranker_v1"
    assert result["research_only"] is True
    assert all(row["model_score"] is not None for row in scored)
    assert diagnostic["ridge_lambda"] == 1.0
    assert diagnostic["hyperparameter_selection"] == "PRE_SPECIFIED_NO_TUNING"
    assert diagnostic["max_training_feature_date"] < diagnostic["test_date"]
    assert diagnostic["max_training_label_available_at"] < diagnostic["test_date"]
    assert diagnostic["training_date_count"] >= 20
    assert set(diagnostic["coefficients"]) == set(config["linear_ranker"]["feature_columns"])
    assert result["checksum"] == canonical_checksum(
        {key: value for key, value in result.items() if key != "checksum"}
    )


def test_final_holdout_labels_never_affect_final_holdout_scores() -> None:
    config = load_feature_config(ROOT)
    features = build_feature_rows(make_snapshot(), config)
    labels = _labels(features)
    baseline = run_chronological_linear_ranker(features, labels, config)
    final_date = max(str(row["date"]) for row in features)
    changed: list[dict[str, object]] = []
    for original in labels:
        label = dict(original)
        if label["date"] == final_date:
            label["forward_return"] = 999.0
            label["checksum"] = canonical_checksum(
                {key: value for key, value in label.items() if key != "checksum"}
            )
        changed.append(label)
    rerun = run_chronological_linear_ranker(features, changed, config)

    baseline_scores = [row["model_score"] for row in baseline["scores"] if row["date"] == final_date]
    changed_scores = [row["model_score"] for row in rerun["scores"] if row["date"] == final_date]
    assert baseline_scores == changed_scores


def test_linear_ranker_abstains_before_minimum_chronological_history() -> None:
    config = load_feature_config(ROOT)
    features = build_feature_rows(make_snapshot(days=70), config)
    result = run_chronological_linear_ranker(features, _labels(features), config)

    assert not [row for row in result["scores"] if row["score_status"] == "SCORED"]
    assert any(
        "INSUFFICIENT_CHRONOLOGICAL_TRAINING_DATES" in row["abstention_reasons"]
        for row in result["scores"]
    )


def test_linear_ranker_rejects_leaky_or_tampered_labels() -> None:
    config = load_feature_config(ROOT)
    features = build_feature_rows(make_snapshot(), config)
    labels = _labels(features)
    labels[0]["label_available_at"] = labels[0]["date"]
    labels[0]["checksum"] = canonical_checksum(
        {key: value for key, value in labels[0].items() if key != "checksum"}
    )
    with pytest.raises(ValueError, match="label_available_not_after_feature_date"):
        run_chronological_linear_ranker(features, labels, config)
    labels = _labels(features)
    labels[-1]["forward_return"] = 99.0
    with pytest.raises(ValueError, match="label_row_checksum_mismatch"):
        run_chronological_linear_ranker(features, labels, config)


def test_linear_ranker_rejects_mixed_snapshot_lineage() -> None:
    config = load_feature_config(ROOT)
    features = build_feature_rows(make_snapshot(), config)
    labels = _labels(features)
    features[-1]["source_snapshot_id"] = "different-governed-snapshot"
    features[-1]["checksum"] = canonical_checksum(
        {key: value for key, value in features[-1].items() if key != "checksum"}
    )
    labels[-1]["source_snapshot_id"] = "different-governed-snapshot"
    labels[-1]["checksum"] = canonical_checksum(
        {key: value for key, value in labels[-1].items() if key != "checksum"}
    )

    with pytest.raises(ValueError, match="mixed_feature_snapshot_lineage"):
        run_chronological_linear_ranker(features, labels, config)

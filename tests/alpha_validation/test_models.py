from __future__ import annotations

from ashare_premarket.alpha_validation.folds import build_purged_chronological_splits
from ashare_premarket.alpha_validation.models import run_purged_fixed_linear_baseline
from ashare_premarket.quant_foundation.contracts import canonical_checksum


DATES = tuple(f"2026-01-{day:02d}" for day in range(1, 15))
SPLIT_DATES = DATES[:12]
SYMBOLS = ("000001.SZ", "000002.SZ", "600000.SH", "600036.SH")


def _inputs(*, structural_missing: bool = False) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    features: list[dict[str, object]] = []
    labels: list[dict[str, object]] = []
    for date_index, trade_date in enumerate(DATES):
        for symbol_index, symbol in enumerate(SYMBOLS):
            value = float(symbol_index + date_index / 100)
            feature: dict[str, object] = {
                "date": trade_date,
                "symbol": symbol,
                "x": None if structural_missing else value,
            }
            feature["checksum"] = canonical_checksum(feature)
            features.append(feature)
            target_index = date_index + 2
            label: dict[str, object] = {
                "date": trade_date,
                "symbol": symbol,
                "horizon_trading_days": 2,
                "target_date": DATES[target_index] if target_index < len(DATES) else None,
                "label_available_at": DATES[target_index] if target_index < len(DATES) else None,
                "forward_return": value / 100 if target_index < len(DATES) else None,
                "label_status": "AVAILABLE" if target_index < len(DATES) else "MISSING_FUTURE_CALENDAR_DATE",
            }
            label["checksum"] = canonical_checksum(label)
            labels.append(label)
    return features, labels


def _splits() -> dict[str, object]:
    return build_purged_chronological_splits(
        SPLIT_DATES,
        {
            "minimum_training_dates": 3,
            "validation_dates": 2,
            "test_dates": 2,
            "final_holdout_dates": 2,
            "maximum_label_horizon": 2,
            "embargo_dates": 0,
            "mode": "EXPANDING_PURGED_CHRONOLOGICAL",
        },
        label_horizon=2,
    )


def test_fixed_linear_baseline_is_purged_oos_deterministic_and_metric_complete() -> None:
    features, labels = _inputs()
    config = {
        "version": "fixture_fixed_ridge",
        "feature_columns": ["x"],
        "ridge_lambda": 1.0,
    }
    metrics = {"minimum_cross_section": 3, "top_k": 2}

    first = run_purged_fixed_linear_baseline(features, labels, _splits(), config, metrics)
    second = run_purged_fixed_linear_baseline(features, labels, _splits(), config, metrics)

    assert first == second
    assert first["status"] == "COMPLETE_RESEARCH_ONLY"
    assert first["random_date_split_used"] is False
    assert first["hyperparameter_tuning_used"] is False
    assert first["final_holdout_tuning_used"] is False
    assert first["fit_diagnostics"]
    for diagnostic in first["fit_diagnostics"]:
        assert diagnostic["fit_scope"] == "TRAINING_ONLY"
        assert diagnostic["max_training_label_available_at"] < diagnostic["evaluation_start_date"]
        assert diagnostic["preprocessor"]["parameters"]["x"]["mean"] < 2.0
    holdout = first["final_holdout_metrics"]
    assert holdout["rank_ic_mean"] == 1.0
    assert holdout["precision_at_k_mean"] == 1.0
    assert holdout["recall_at_k_mean"] == 1.0
    assert holdout["ndcg_at_k_mean"] == 1.0
    assert holdout["prediction_dispersion_mean"] > 0
    assert holdout["effective_date_sample_size"] == 2
    assert first["coefficient_sign_stability"] == 1.0
    assert first["feature_contribution_stability"] == 1.0


def test_structurally_missing_model_feature_abstains_without_imputation() -> None:
    features, labels = _inputs(structural_missing=True)
    result = run_purged_fixed_linear_baseline(
        features,
        labels,
        _splits(),
        {"version": "fixture", "feature_columns": ["x"], "ridge_lambda": 1.0},
        {"minimum_cross_section": 3, "top_k": 2},
    )

    assert result["status"] == "INSUFFICIENT_DATA"
    assert result["scores"] == []
    assert result["fit_diagnostics"] == []
    assert result["insufficiency_reasons"] == ("STRUCTURALLY_MISSING_MODEL_FEATURE:X",)
    assert result["production_ready"] is False

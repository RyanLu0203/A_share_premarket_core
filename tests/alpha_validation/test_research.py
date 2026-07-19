from __future__ import annotations

from ashare_premarket.alpha_validation.research import evaluate_single_factor
from ashare_premarket.quant_foundation.contracts import canonical_checksum


def _rows() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    features: list[dict[str, object]] = []
    labels: list[dict[str, object]] = []
    for date_index in range(4):
        trade_date = f"2026-01-{date_index + 5:02d}"
        for symbol_index, symbol in enumerate(("000001.SZ", "000002.SZ", "600000.SH", "600036.SH")):
            feature: dict[str, object] = {
                "date": trade_date,
                "symbol": symbol,
                "factor": float(symbol_index + 1),
            }
            feature["checksum"] = canonical_checksum(feature)
            features.append(feature)
            label: dict[str, object] = {
                "date": trade_date,
                "symbol": symbol,
                "horizon_trading_days": 5,
                "forward_return": float(symbol_index - 1) / 100.0,
                "label_status": "AVAILABLE",
            }
            label["checksum"] = canonical_checksum(label)
            labels.append(label)
    return features, labels


def test_single_factor_reports_full_cross_sectional_diagnostics() -> None:
    features, labels = _rows()
    result = evaluate_single_factor(
        features,
        labels,
        feature_name="factor",
        direction=1,
        minimum_cross_section=3,
        quantile_count=2,
        top_k=2,
    )

    assert result["valid_date_count"] == 4
    assert result["observation_row_count"] == 16
    assert result["ic_mean"] == 1.0
    assert result["rank_ic_mean"] == 1.0
    assert result["rank_ic_median"] == 1.0
    assert result["rank_ic_information_ratio"] is None
    assert result["positive_rank_ic_ratio"] == 1.0
    assert result["median_breadth"] == 4.0
    assert result["quantile_top_minus_bottom_mean"] == 0.02
    assert result["bucket_monotonicity_mean"] == 1.0
    assert result["ranking_turnover"] == 0.0
    assert result["top_k_overlap"] == 1.0
    assert result["missing_rate"] == 0.0
    assert result["symbol_concentration"] == 0.25
    assert result["date_concentration"] == 0.25
    assert len(result["by_date"]) == 4


def test_direction_is_predeclared_and_zero_variance_dates_are_not_coerced() -> None:
    features, labels = _rows()
    reversed_result = evaluate_single_factor(
        features,
        labels,
        feature_name="factor",
        direction=-1,
        minimum_cross_section=3,
        quantile_count=2,
        top_k=2,
    )
    assert reversed_result["rank_ic_mean"] == -1.0

    for row in features:
        if row["date"] == "2026-01-05":
            row["factor"] = 1.0
            row["checksum"] = canonical_checksum(
                {key: value for key, value in row.items() if key != "checksum"}
            )
    result = evaluate_single_factor(
        features,
        labels,
        feature_name="factor",
        direction=1,
        minimum_cross_section=3,
        quantile_count=2,
        top_k=2,
    )
    assert result["valid_date_count"] == 3
    assert result["zero_variance_date_count"] == 1
    assert result["zero_variance_rate"] == 0.25
    assert result["skipped_dates"][0]["reason"] == "ZERO_FACTOR_VARIANCE"


def test_missing_feature_values_remain_missing_and_are_counted() -> None:
    features, labels = _rows()
    features[0]["factor"] = None
    features[0]["checksum"] = canonical_checksum(
        {key: value for key, value in features[0].items() if key != "checksum"}
    )
    result = evaluate_single_factor(
        features,
        labels,
        feature_name="factor",
        direction=1,
        minimum_cross_section=3,
        quantile_count=2,
        top_k=2,
    )
    assert result["missing_feature_count"] == 1
    assert result["missing_rate"] == 0.0625
    assert result["observation_row_count"] == 15


def test_structural_feature_missingness_is_one_even_when_some_labels_are_missing() -> None:
    features, labels = _rows()
    for row in features:
        row["factor"] = None
        row["checksum"] = canonical_checksum(
            {key: value for key, value in row.items() if key != "checksum"}
        )
    labels[0]["forward_return"] = None
    labels[0]["label_status"] = "MISSING_TARGET_PRICE"
    labels[0]["checksum"] = canonical_checksum(
        {key: value for key, value in labels[0].items() if key != "checksum"}
    )

    result = evaluate_single_factor(
        features,
        labels,
        feature_name="factor",
        direction=1,
        minimum_cross_section=3,
        quantile_count=2,
        top_k=2,
    )

    assert result["missing_feature_count"] == 16
    assert result["missing_rate"] == 1.0
    assert result["missing_label_count"] == 1

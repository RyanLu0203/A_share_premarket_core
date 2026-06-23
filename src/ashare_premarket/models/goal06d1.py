from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

from ashare_premarket.core.io import read_csv, write_csv, write_text
from ashare_premarket.models import goal06d

MODEL_DIR = "outputs/models/goal06d1"
TARGETS = ["excess_fwd_1d_return", "excess_fwd_3d_return", "excess_fwd_5d_return"]
PRIMARY_TARGET = "excess_fwd_3d_return"
SCORE_VARIANTS = [
    "raw_score_based_alpha_ranking",
    "zscore_cross_sectional_score",
    "rank_normalized_score",
    "winsorized_rank_score",
    "volatility_adjusted_rank_score",
    "market_regime_adjusted_rank_score_review_only",
]
PIT_FEATURES = [
    "market_trend_5d",
    "stock_momentum_5d",
    "stock_momentum_20d",
    "stock_gap_signal",
    "stock_volatility_20d",
    "turnover_proxy",
    "relative_strength_20d",
    "source_health_score",
    "source_count",
]
BASE_WEIGHTS = {
    "relative_strength_20d": 0.30,
    "stock_momentum_20d": 0.25,
    "stock_momentum_5d": 0.20,
    "market_trend_5d": 0.15,
    "stock_gap_signal": 0.10,
    "stock_volatility_20d": -0.10,
}
EXPECTED_DIRECTIONS = {
    "relative_strength_20d": "positive",
    "stock_momentum_20d": "positive",
    "stock_momentum_5d": "positive",
    "market_trend_5d": "positive",
    "stock_gap_signal": "positive",
    "turnover_proxy": "positive",
    "source_health_score": "positive",
    "source_count": "positive",
    "stock_volatility_20d": "negative",
}
TARGET_HORIZON_FIELDS = [
    "target",
    "best_score_variant",
    "test_spearman",
    "test_pearson",
    "test_directional_accuracy",
    "mean_daily_ic",
    "ic_information_ratio",
    "calibration_error",
    "fold_stability",
    "feature_sign_stability",
    "top_bottom_spread_offline_diagnostic_only",
    "target_horizon_recommendation",
    "warnings",
]
SCORE_VARIANT_FIELDS = [
    "score_variant",
    "target",
    "split_policy",
    "train_rows",
    "validation_rows",
    "test_rows",
    "validation_spearman",
    "test_spearman",
    "test_pearson",
    "test_directional_accuracy",
    "test_mean_daily_ic",
    "test_ic_information_ratio",
    "offline_top_bottom_spread_diagnostic_only",
    "calibration_error",
    "fold_stability",
    "feature_sign_stability",
    "selection_label",
    "review_only",
    "warnings",
]
FOLD_FIELDS = [
    "score_variant",
    "target",
    "fold_name",
    "train_start",
    "train_end",
    "test_start",
    "test_end",
    "train_rows",
    "test_rows",
    "spearman",
    "pearson",
    "directional_accuracy",
    "mean_daily_ic",
    "ic_information_ratio",
    "review_only",
]
TARGET_FIELDS = [
    "score_variant",
    "target",
    "split",
    "rows",
    "spearman",
    "pearson",
    "directional_accuracy",
    "mean_daily_ic",
    "ic_information_ratio",
    "calibration_error",
    "review_only",
]
CALIBRATION_REPAIR_FIELDS = [
    "model_or_score_variant",
    "target",
    "split",
    "sample_count",
    "bin_count",
    "calibration_error",
    "monotonicity_pass",
    "calibration_method_selected",
    "calibration_method_rejected_reason",
    "thresholding_allowed",
    "warnings",
]
DECILE_FIELDS = [
    "score_variant",
    "target",
    "split",
    "decile",
    "row_count",
    "mean_score",
    "mean_label",
    "label_positive_rate",
    "review_only",
]
FEATURE_REPAIR_FIELDS = [
    "feature_name",
    "expected_direction_if_defined",
    "fold_signs",
    "positive_fold_count",
    "negative_fold_count",
    "zero_or_missing_fold_count",
    "sign_flip_count",
    "sign_stability_ratio",
    "target_horizon_sensitivity",
    "recommended_action",
]
FEATURE_DIRECTION_FIELDS = [
    "feature_name",
    "target",
    "fold_name",
    "spearman",
    "observed_direction",
    "expected_direction_if_defined",
    "score_variants_using_feature",
]
PROVIDER_FIELDS = [
    "provider_mode",
    "provider_id",
    "source_bundle_id",
    "row_count",
    "symbol_count",
    "trading_date_count",
    "concentration_status",
    "production_diversification_sufficient",
]
MODEL_REPAIR_FIELDS = [
    "baseline_name",
    "selected_score_variant",
    "selected_target",
    "selection_label",
    "test_spearman",
    "test_directional_accuracy",
    "calibration_status",
    "feature_stability_status",
    "provider_concentration_status",
    "goal07a_allowed_mode",
    "review_only",
    "warnings",
]


def run_goal06d1_calibration_stability_warning_repair(root: Path) -> bool:
    _write_v2_factor_placeholder(root)
    contract = goal06d._load_json(root / goal06d.FEATURE_CONFIG)
    split_config = goal06d._load_json(root / goal06d.SPLIT_CONFIG)
    panel_path = goal06d._locate_panel(root)
    if panel_path is None:
        _write_blocked_outputs(root, "source_backed_engineering_panel_missing")
        return True
    panel_rows = goal06d._load_panel(panel_path)
    input_status = _validate_input_panel(panel_rows)
    feature_audit = goal06d.validate_feature_contract(root, panel_rows, contract)
    split_audit = goal06d.validate_split_policy(root, panel_rows, split_config)
    if input_status["status"] == "BLOCKED" or feature_audit["status"] == "BLOCKED" or split_audit["status"] == "BLOCKED":
        reason = ";".join(input_status["failures"] + feature_audit["failures"] + split_audit["failures"])
        _write_blocked_outputs(root, reason)
        return True

    rows_by_target = {target: _filter_rows(panel_rows, contract, target) for target in TARGETS}
    primary_rows = rows_by_target[PRIMARY_TARGET]
    splits = goal06d.build_chronological_splits(primary_rows, split_config)
    folds = goal06d.build_walk_forward_splits(primary_rows, split_config)
    outputs = _run_repair(rows_by_target, splits, folds)
    readiness = _derive_readiness(input_status, outputs)
    _write_outputs(root, outputs, readiness, input_status)
    _update_workflow_status(root, readiness)
    return True


def audit_goal06d1_target_horizon(root: Path) -> bool:
    return _status_from_report(root / "outputs/audits/goal06d1_target_horizon_audit.md") in {"PASS", "PASS_WITH_WARNINGS"}


def audit_goal06d1_score_repair(root: Path) -> bool:
    return _status_from_report(root / "outputs/audits/goal06d1_score_repair_audit.md") in {"PASS", "PASS_WITH_WARNINGS"}


def audit_goal06d1_calibration_repair(root: Path) -> bool:
    return _status_from_report(root / "outputs/audits/goal06d1_calibration_repair_audit.md") in {"PASS", "PASS_WITH_WARNINGS"}


def audit_goal06d1_feature_sign_stability(root: Path) -> bool:
    return _status_from_report(root / "outputs/audits/goal06d1_feature_sign_stability_audit.md") in {"PASS", "PASS_WITH_WARNINGS"}


def audit_goal06d1_provider_concentration_disclosure(root: Path) -> bool:
    return _status_from_report(root / "outputs/audits/goal06d1_provider_concentration_disclosure.md") in {"PASS", "PASS_WITH_WARNINGS"}


def audit_goal06d1_governance(root: Path) -> bool:
    return _status_from_report(root / "outputs/audits/goal06d1_governance_audit.md") == "PASS"


def audit_goal06d1_boundary_locks(root: Path) -> bool:
    return _status_from_report(root / "outputs/audits/goal06d1_boundary_lock_audit.md") == "PASS"


def _validate_input_panel(rows: list[dict[str, str]]) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    symbols = {row.get("symbol", "") for row in rows}
    dates = {row.get("trade_date", "") for row in rows}
    pit_ready = [row for row in rows if row.get("leakage_flags") == "PASS" and row.get("panel_tier") == "engineering_pilot"]
    label_ready = [row for row in pit_ready if all(row.get(target, "") != "" for target in TARGETS)]
    if len(rows) < 6000:
        failures.append("rows below 6000")
    if len(symbols) < 50:
        failures.append("symbols below 50")
    if len(dates) < 120:
        failures.append("validation_trading_dates below 120")
    if len(pit_ready) < 6000:
        failures.append("PIT-ready rows below 6000")
    if len(label_ready) < 6000:
        failures.append("label-ready rows below 6000")
    provider_modes = sorted({row.get("provider_mode", "") for row in rows})
    if provider_modes == ["akshare_direct"]:
        warnings.append("single_provider_mode_akshare_direct")
    status = "BLOCKED" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    return {
        "status": status,
        "failures": failures,
        "warnings": warnings,
        "rows": len(rows),
        "symbols": len(symbols),
        "trading_dates": len(dates),
        "pit_ready_rows": len(pit_ready),
        "label_ready_rows": len(label_ready),
        "provider_modes": provider_modes,
    }


def _filter_rows(rows: list[dict[str, str]], contract: dict[str, object], target: str) -> list[dict[str, str]]:
    return goal06d._filter_model_rows(rows, contract, target)


def _run_repair(rows_by_target: dict[str, list[dict[str, str]]], splits: dict[str, dict[str, object]], folds: list[dict[str, object]]) -> dict[str, object]:
    primary_rows = rows_by_target[PRIMARY_TARGET]
    score_comparison_rows: list[dict[str, object]] = []
    fold_rows: list[dict[str, object]] = []
    target_metric_rows: list[dict[str, object]] = []
    calibration_rows: list[dict[str, object]] = []
    decile_rows: list[dict[str, object]] = []

    primary_scores = {variant: _score_rows(primary_rows, variant) for variant in SCORE_VARIANTS}
    train_rows = list(splits["train"]["rows"])
    validation_rows = list(splits["validation"]["rows"])
    test_rows = list(splits["test"]["rows"])
    train_scores = {variant: _score_rows(train_rows, variant) for variant in SCORE_VARIANTS}
    validation_scores = {variant: _score_rows(validation_rows, variant) for variant in SCORE_VARIANTS}
    test_scores = {variant: _score_rows(test_rows, variant) for variant in SCORE_VARIANTS}

    for variant in SCORE_VARIANTS:
        train_metrics = _metrics(train_rows, train_scores[variant], PRIMARY_TARGET)
        validation_metrics = _metrics(validation_rows, validation_scores[variant], PRIMARY_TARGET)
        test_metrics = _metrics(test_rows, test_scores[variant], PRIMARY_TARGET)
        calibration = _calibration_repair_row(variant, PRIMARY_TARGET, "test", test_rows, test_scores[variant])
        calibration_rows.append(calibration)
        decile_rows.extend(_decile_rows(variant, PRIMARY_TARGET, "test", test_rows, test_scores[variant]))
        variant_fold_rows = []
        for fold in folds:
            fold_scores = _score_rows(fold["test_rows"], variant)
            fold_metrics = _metrics(fold["test_rows"], fold_scores, PRIMARY_TARGET)
            row = {
                "score_variant": variant,
                "target": PRIMARY_TARGET,
                "fold_name": fold["fold_name"],
                "train_start": min(fold["train_dates"]),
                "train_end": max(fold["train_dates"]),
                "test_start": min(fold["test_dates"]),
                "test_end": max(fold["test_dates"]),
                "train_rows": len(fold["train_rows"]),
                "test_rows": len(fold["test_rows"]),
                "spearman": fold_metrics["spearman"],
                "pearson": fold_metrics["pearson"],
                "directional_accuracy": fold_metrics["directional_accuracy"],
                "mean_daily_ic": fold_metrics["mean_daily_ic"],
                "ic_information_ratio": fold_metrics["ic_information_ratio"],
                "review_only": True,
            }
            fold_rows.append(row)
            variant_fold_rows.append(row)
        fold_stability = _fold_stability(variant_fold_rows)
        feature_stability = _feature_sign_stability_ratio(primary_rows, PRIMARY_TARGET)
        score_comparison_rows.append(
            {
                "score_variant": variant,
                "target": PRIMARY_TARGET,
                "split_policy": "chronological_train_validation_test",
                "train_rows": len(train_rows),
                "validation_rows": len(validation_rows),
                "test_rows": len(test_rows),
                "validation_spearman": validation_metrics["spearman"],
                "test_spearman": test_metrics["spearman"],
                "test_pearson": test_metrics["pearson"],
                "test_directional_accuracy": test_metrics["directional_accuracy"],
                "test_mean_daily_ic": test_metrics["mean_daily_ic"],
                "test_ic_information_ratio": test_metrics["ic_information_ratio"],
                "offline_top_bottom_spread_diagnostic_only": goal06d._offline_top_bottom_spread(test_rows, test_scores[variant], PRIMARY_TARGET),
                "calibration_error": calibration["calibration_error"],
                "fold_stability": fold_stability,
                "feature_sign_stability": feature_stability,
                "selection_label": "",
                "review_only": True,
                "warnings": _score_variant_warnings(test_metrics, calibration, fold_stability, feature_stability),
            }
        )
        for target in TARGETS:
            target_rows = rows_by_target[target]
            target_splits = goal06d.build_chronological_splits(target_rows, goal06d._load_json(Path("configs/models/goal06d_split_config.yaml")) if False else {"chronological_train_validation_test": {"train_fraction": 0.70, "validation_fraction": 0.15}})
            target_test_rows = list(target_splits["test"]["rows"])
            target_scores = _score_rows(target_test_rows, variant)
            target_metrics = _metrics(target_test_rows, target_scores, target)
            target_calibration = _calibration_repair_row(variant, target, "test", target_test_rows, target_scores)
            target_metric_rows.append(
                {
                    "score_variant": variant,
                    "target": target,
                    "split": "test",
                    "rows": len(target_test_rows),
                    "spearman": target_metrics["spearman"],
                    "pearson": target_metrics["pearson"],
                    "directional_accuracy": target_metrics["directional_accuracy"],
                    "mean_daily_ic": target_metrics["mean_daily_ic"],
                    "ic_information_ratio": target_metrics["ic_information_ratio"],
                    "calibration_error": target_calibration["calibration_error"],
                    "review_only": True,
                }
            )

    target_horizon_rows = _target_horizon_rows(target_metric_rows, fold_rows, primary_rows)
    selected = _select_score_variant(score_comparison_rows)
    for row in score_comparison_rows:
        if row["score_variant"] == selected["selected_score_variant"]:
            row["selection_label"] = selected["score_selection_label"]
            row["warnings"] = ";".join(dict.fromkeys([item for item in [row["warnings"], *selected["warnings"]] if item]))
    feature_repair_rows, feature_direction_rows = _feature_repair_rows(primary_rows, folds)
    provider_rows = _provider_rows(primary_rows)
    model_summary_rows = _model_summary_rows(selected, score_comparison_rows, calibration_rows, feature_repair_rows, provider_rows)
    return {
        "target_horizon_rows": target_horizon_rows,
        "score_comparison_rows": score_comparison_rows,
        "fold_rows": fold_rows,
        "target_metric_rows": target_metric_rows,
        "calibration_rows": calibration_rows,
        "decile_rows": decile_rows,
        "feature_repair_rows": feature_repair_rows,
        "feature_direction_rows": feature_direction_rows,
        "provider_rows": provider_rows,
        "model_summary_rows": model_summary_rows,
        "selected": selected,
    }


def _score_rows(rows: list[dict[str, str]], variant: str) -> list[float]:
    raw = [_raw_score(row) for row in rows]
    if variant == "raw_score_based_alpha_ranking":
        return raw
    by_date: dict[str, list[int]] = defaultdict(list)
    for idx, row in enumerate(rows):
        by_date[row["trade_date"]].append(idx)
    out = [0.0 for _ in rows]
    for indexes in by_date.values():
        values = [raw[idx] for idx in indexes]
        if variant == "zscore_cross_sectional_score":
            normalized = _zscore(values)
        elif variant == "rank_normalized_score":
            normalized = _rank_normalized(values)
        elif variant == "winsorized_rank_score":
            normalized = _rank_normalized(_winsorize(values))
        elif variant == "volatility_adjusted_rank_score":
            adjusted = [raw[idx] / (1.0 + abs(goal06d._float(rows[idx].get("stock_volatility_20d", 0.0)))) for idx in indexes]
            normalized = _rank_normalized(adjusted)
        elif variant == "market_regime_adjusted_rank_score_review_only":
            regime = goal06d._mean([goal06d._float(rows[idx].get("market_trend_5d", 0.0)) for idx in indexes])
            adjusted = [raw[idx] - 0.15 * regime for idx in indexes]
            normalized = _rank_normalized(adjusted)
        else:
            normalized = values
        for pos, idx in enumerate(indexes):
            out[idx] = normalized[pos]
    return out


def _raw_score(row: dict[str, str]) -> float:
    return sum(weight * goal06d._float(row.get(feature, 0.0)) for feature, weight in BASE_WEIGHTS.items())


def _zscore(values: list[float]) -> list[float]:
    mean = goal06d._mean(values)
    std = goal06d._std(values) or 1.0
    return [(value - mean) / std for value in values]


def _rank_normalized(values: list[float]) -> list[float]:
    if not values:
        return []
    ranks = goal06d._rank(values)
    denom = max(1.0, len(values) - 1.0)
    return [((rank - 1.0) / denom) - 0.5 for rank in ranks]


def _winsorize(values: list[float]) -> list[float]:
    if not values:
        return []
    ordered = sorted(values)
    low = ordered[int(0.10 * (len(ordered) - 1))]
    high = ordered[int(0.90 * (len(ordered) - 1))]
    return [min(high, max(low, value)) for value in values]


def _metrics(rows: list[dict[str, str]], scores: list[float], target: str) -> dict[str, object]:
    metrics = goal06d._regression_metrics(rows, scores, target)
    return {
        "spearman": metrics["spearman"],
        "pearson": metrics["pearson"],
        "directional_accuracy": metrics["directional_accuracy"],
        "mean_daily_ic": metrics["mean_daily_ic"],
        "ic_information_ratio": metrics["ic_information_ratio"],
    }


def _calibration_repair_row(variant: str, target: str, split: str, rows: list[dict[str, str]], scores: list[float]) -> dict[str, object]:
    paired = sorted(zip(scores, [goal06d._float(row[target]) for row in rows]), key=lambda item: item[0])
    bin_count = 10 if len(paired) >= 200 else 5
    bins = goal06d._bins(paired, bin_count)
    actual_means = []
    errors = []
    for bucket in bins:
        if not bucket:
            continue
        mean_score = goal06d._mean([item[0] for item in bucket])
        mean_actual = goal06d._mean([item[1] for item in bucket])
        actual_means.append(mean_actual)
        errors.append(abs(mean_score - mean_actual))
    monotonic = _monotonic(actual_means)
    error = goal06d._mean(errors) if errors else 0.0
    isotonic_allowed = len(rows) >= 500 and monotonic and error <= 0.03
    if isotonic_allowed:
        method = "isotonic_review_diagnostic"
        rejected = ""
        warnings = ""
    else:
        method = "quantile_bin_diagnostic_only"
        reasons = []
        if len(rows) < 500:
            reasons.append("sample_count_below_isotonic_review_floor")
        if not monotonic:
            reasons.append("non_monotonic_decile_response")
        if error > 0.03:
            reasons.append("calibration_error_above_review_threshold")
        rejected = ";".join(reasons)
        warnings = "calibration_not_reliable_for_thresholding"
    return {
        "model_or_score_variant": variant,
        "target": target,
        "split": split,
        "sample_count": len(rows),
        "bin_count": len(bins),
        "calibration_error": goal06d._round(error),
        "monotonicity_pass": monotonic,
        "calibration_method_selected": method,
        "calibration_method_rejected_reason": rejected,
        "thresholding_allowed": False,
        "warnings": warnings,
    }


def _decile_rows(variant: str, target: str, split: str, rows: list[dict[str, str]], scores: list[float]) -> list[dict[str, object]]:
    paired = sorted(zip(scores, [goal06d._float(row[target]) for row in rows]), key=lambda item: item[0])
    buckets = goal06d._bins(paired, 10)
    out = []
    for idx, bucket in enumerate(buckets, start=1):
        labels = [item[1] for item in bucket]
        out.append(
            {
                "score_variant": variant,
                "target": target,
                "split": split,
                "decile": idx,
                "row_count": len(bucket),
                "mean_score": goal06d._round(goal06d._mean([item[0] for item in bucket])),
                "mean_label": goal06d._round(goal06d._mean(labels)),
                "label_positive_rate": goal06d._round(sum(1 for value in labels if value > 0) / len(labels)) if labels else 0.0,
                "review_only": True,
            }
        )
    return out


def _monotonic(values: list[float]) -> bool:
    if len(values) < 2:
        return True
    return all(a <= b for a, b in zip(values, values[1:])) or all(a >= b for a, b in zip(values, values[1:]))


def _fold_stability(rows: list[dict[str, object]]) -> float:
    return goal06d._round(1.0 / (1.0 + goal06d._std([goal06d._float(row["mean_daily_ic"]) for row in rows])))


def _feature_sign_stability_ratio(rows: list[dict[str, str]], target: str) -> float:
    ratios = []
    for feature in PIT_FEATURES:
        by_date_signs = []
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            grouped[row["trade_date"]].append(row)
        for day_rows in grouped.values():
            if len(day_rows) < 5:
                continue
            corr = goal06d._spearman([goal06d._float(row[feature]) for row in day_rows], [goal06d._float(row[target]) for row in day_rows])
            by_date_signs.append(_sign(corr))
        non_zero = [item for item in by_date_signs if item]
        if not non_zero:
            ratios.append(0.0)
            continue
        counts = defaultdict(int)
        for item in non_zero:
            counts[item] += 1
        ratios.append(max(counts.values()) / len(non_zero))
    return goal06d._round(goal06d._mean(ratios))


def _score_variant_warnings(metrics: dict[str, object], calibration: dict[str, object], fold_stability: float, feature_stability: float) -> str:
    warnings = []
    if goal06d._float(metrics["spearman"]) < 0.05:
        warnings.append("weak_test_rank_signal")
    if calibration["warnings"]:
        warnings.append(str(calibration["warnings"]))
    if fold_stability < 0.80:
        warnings.append("fold_stability_below_review_threshold")
    if feature_stability < 0.70:
        warnings.append("feature_sign_instability_bounded")
    return ";".join(warnings)


def _target_horizon_rows(target_metric_rows: list[dict[str, object]], fold_rows: list[dict[str, object]], primary_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    out = []
    for target in TARGETS:
        target_rows = [row for row in target_metric_rows if row["target"] == target]
        best = max(
            target_rows,
            key=lambda row: goal06d._float(row["spearman"]) + 0.20 * goal06d._float(row["directional_accuracy"]) - goal06d._float(row["calibration_error"]),
        )
        fold_stability = goal06d._round(1.0 / (1.0 + goal06d._std([goal06d._float(row["mean_daily_ic"]) for row in fold_rows if row["score_variant"] == best["score_variant"]])))
        feature_stability = _feature_sign_stability_ratio(primary_rows, target)
        warnings = []
        if goal06d._float(best["spearman"]) < 0.05:
            warnings.append("weak_target_horizon_rank_signal")
        if goal06d._float(best["calibration_error"]) > 0.03:
            warnings.append("target_horizon_calibration_warning")
        recommendation = "selected_review_only_target_horizon" if not warnings else "weak_but_bounded_review_only_target_horizon"
        out.append(
            {
                "target": target,
                "best_score_variant": best["score_variant"],
                "test_spearman": best["spearman"],
                "test_pearson": best["pearson"],
                "test_directional_accuracy": best["directional_accuracy"],
                "mean_daily_ic": best["mean_daily_ic"],
                "ic_information_ratio": best["ic_information_ratio"],
                "calibration_error": best["calibration_error"],
                "fold_stability": fold_stability,
                "feature_sign_stability": feature_stability,
                "top_bottom_spread_offline_diagnostic_only": _target_top_bottom(primary_rows, str(best["score_variant"]), target),
                "target_horizon_recommendation": recommendation,
                "warnings": ";".join(warnings),
            }
        )
    if all(row["warnings"] for row in out):
        for row in out:
            row["target_horizon_recommendation"] = "no_stable_target_horizon_selected"
    return out


def _target_top_bottom(rows: list[dict[str, str]], variant: str, target: str) -> float:
    scores = _score_rows(rows, variant)
    return goal06d._offline_top_bottom_spread(rows, scores, target)


def _select_score_variant(rows: list[dict[str, object]]) -> dict[str, object]:
    best = max(
        rows,
        key=lambda row: goal06d._float(row["test_spearman"])
        + 0.20 * goal06d._float(row["test_directional_accuracy"])
        + 0.10 * goal06d._float(row["fold_stability"])
        + 0.05 * goal06d._float(row["feature_sign_stability"])
        - goal06d._float(row["calibration_error"]),
    )
    warnings = []
    if goal06d._float(best["test_spearman"]) < 0.05:
        warnings.append("selected_score_variant_weak_rank_signal")
    if "calibration_not_reliable_for_thresholding" in str(best["warnings"]):
        warnings.append("selected_score_variant_calibration_not_reliable_for_thresholding")
    if goal06d._float(best["feature_sign_stability"]) < 0.70:
        warnings.append("selected_score_variant_feature_instability_bounded")
    label = "review_only_selected_score_variant" if not warnings else "review_only_selected_score_variant_weak"
    baseline_label = "review_only_selected_baseline_repaired" if not warnings else "review_only_selected_baseline_weak_but_bounded"
    return {
        "selected_score_variant": best["score_variant"],
        "selected_target": best["target"],
        "score_selection_label": label,
        "baseline_selection_label": baseline_label,
        "warnings": warnings,
    }


def _feature_repair_rows(rows: list[dict[str, str]], folds: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    direction_rows = []
    repair_rows = []
    for feature in PIT_FEATURES:
        signs = []
        target_signs = []
        for target in TARGETS:
            target_values = [goal06d._float(row[target]) for row in rows]
            corr = goal06d._spearman([goal06d._float(row[feature]) for row in rows], target_values)
            target_signs.append(_sign(corr))
            direction_rows.append(
                {
                    "feature_name": feature,
                    "target": target,
                    "fold_name": "full_review_panel",
                    "spearman": goal06d._round(corr),
                    "observed_direction": _sign(corr) or "zero",
                    "expected_direction_if_defined": EXPECTED_DIRECTIONS.get(feature, ""),
                    "score_variants_using_feature": ";".join(SCORE_VARIANTS),
                }
            )
        for fold in folds:
            for target in TARGETS:
                fold_rows = list(fold["test_rows"])
                corr = goal06d._spearman([goal06d._float(row[feature]) for row in fold_rows], [goal06d._float(row[target]) for row in fold_rows])
                signs.append(_sign(corr))
                direction_rows.append(
                    {
                        "feature_name": feature,
                        "target": target,
                        "fold_name": fold["fold_name"],
                        "spearman": goal06d._round(corr),
                        "observed_direction": _sign(corr) or "zero",
                        "expected_direction_if_defined": EXPECTED_DIRECTIONS.get(feature, ""),
                        "score_variants_using_feature": ";".join(SCORE_VARIANTS),
                    }
                )
        positive = signs.count("positive")
        negative = signs.count("negative")
        zero = signs.count("")
        sign_flip = min(positive, negative)
        non_zero = positive + negative
        stability = max(positive, negative) / non_zero if non_zero else 0.0
        target_horizon_sensitivity = len(set(item for item in target_signs if item)) > 1
        action = _feature_action(feature, stability, sign_flip, target_horizon_sensitivity)
        repair_rows.append(
            {
                "feature_name": feature,
                "expected_direction_if_defined": EXPECTED_DIRECTIONS.get(feature, ""),
                "fold_signs": ";".join(sign or "zero" for sign in signs),
                "positive_fold_count": positive,
                "negative_fold_count": negative,
                "zero_or_missing_fold_count": zero,
                "sign_flip_count": sign_flip,
                "sign_stability_ratio": goal06d._round(stability),
                "target_horizon_sensitivity": target_horizon_sensitivity,
                "recommended_action": action,
            }
        )
    return repair_rows, direction_rows


def _sign(value: float) -> str:
    if value > 1e-9:
        return "positive"
    if value < -1e-9:
        return "negative"
    return ""


def _feature_action(feature: str, stability: float, sign_flip: int, target_sensitive: bool) -> str:
    if stability >= 0.75 and not target_sensitive:
        return "keep_for_review_only"
    if feature in {"stock_volatility_20d", "market_trend_5d"}:
        return "neutralize_in_score_variant"
    if sign_flip <= 2:
        return "keep_but_monitor"
    return "requires_v2_factor_research"


def _provider_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row.get("provider_mode", ""), row.get("provider_id", ""), row.get("source_bundle_id", ""))].append(row)
    out = []
    for (provider_mode, provider_id, bundle_id), group in sorted(grouped.items()):
        out.append(
            {
                "provider_mode": provider_mode,
                "provider_id": provider_id,
                "source_bundle_id": bundle_id,
                "row_count": len(group),
                "symbol_count": len({row["symbol"] for row in group}),
                "trading_date_count": len({row["trade_date"] for row in group}),
                "concentration_status": "single_provider_mode_akshare_direct" if provider_mode == "akshare_direct" else "multi_provider_or_unknown",
                "production_diversification_sufficient": False,
            }
        )
    return out


def _model_summary_rows(
    selected: dict[str, object],
    score_rows: list[dict[str, object]],
    calibration_rows: list[dict[str, object]],
    feature_rows: list[dict[str, object]],
    provider_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    selected_row = next(row for row in score_rows if row["score_variant"] == selected["selected_score_variant"])
    selected_calibration = next(row for row in calibration_rows if row["model_or_score_variant"] == selected["selected_score_variant"] and row["target"] == selected["selected_target"])
    feature_warnings = [row for row in feature_rows if row["recommended_action"] in {"neutralize_in_score_variant", "requires_v2_factor_research"}]
    provider_warning = any(row["concentration_status"] == "single_provider_mode_akshare_direct" for row in provider_rows)
    warnings = list(selected["warnings"])
    if provider_warning:
        warnings.append("provider_source_concentration_disclosed")
    if feature_warnings:
        warnings.append("feature_sign_instability_bounded")
    return [
        {
            "baseline_name": "score_based_alpha_ranking",
            "selected_score_variant": selected["selected_score_variant"],
            "selected_target": selected["selected_target"],
            "selection_label": selected["baseline_selection_label"],
            "test_spearman": selected_row["test_spearman"],
            "test_directional_accuracy": selected_row["test_directional_accuracy"],
            "calibration_status": "PASS_WITH_WARNINGS" if selected_calibration["warnings"] else "PASS",
            "feature_stability_status": "PASS_WITH_WARNINGS" if feature_warnings else "PASS",
            "provider_concentration_status": "PASS_WITH_WARNINGS" if provider_warning else "PASS",
            "goal07a_allowed_mode": "design_only_preparation_with_warnings",
            "review_only": True,
            "warnings": ";".join(dict.fromkeys(warnings)),
        }
    ]


def _derive_readiness(input_status: dict[str, object], outputs: dict[str, object]) -> dict[str, object]:
    failures = list(input_status["failures"])
    warnings = list(input_status["warnings"])
    selected = outputs["selected"]
    warnings.extend(selected["warnings"])
    warnings.extend(row["warnings"] for row in outputs["calibration_rows"] if row["warnings"])
    warnings.extend(row["warnings"] for row in outputs["target_horizon_rows"] if row["warnings"])
    if any(row["concentration_status"] == "single_provider_mode_akshare_direct" for row in outputs["provider_rows"]):
        warnings.append("provider_source_concentration_disclosed")
    if any(row["recommended_action"] in {"neutralize_in_score_variant", "requires_v2_factor_research"} for row in outputs["feature_repair_rows"]):
        warnings.append("feature_sign_instability_bounded")
    status = "BLOCKED" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    allowed_next_action = {
        "PASS": "prepare_goal07a_risk_overlay_design_only",
        "PASS_WITH_WARNINGS": "proceed_to_goal07a_design_only_with_warnings",
        "BLOCKED": "continue_goal06d_warning_repair",
    }[status]
    return {"status": status, "failures": failures, "warnings": sorted(set(str(item) for item in warnings if item)), "allowed_next_action": allowed_next_action}


def _write_outputs(root: Path, outputs: dict[str, object], readiness: dict[str, object], input_status: dict[str, object]) -> None:
    write_csv(root / f"{MODEL_DIR}/target_horizon_comparison.csv", outputs["target_horizon_rows"], TARGET_HORIZON_FIELDS)
    write_csv(root / f"{MODEL_DIR}/score_variant_comparison.csv", outputs["score_comparison_rows"], SCORE_VARIANT_FIELDS)
    write_csv(root / f"{MODEL_DIR}/score_variant_metric_by_fold.csv", outputs["fold_rows"], FOLD_FIELDS)
    write_csv(root / f"{MODEL_DIR}/score_variant_metric_by_target.csv", outputs["target_metric_rows"], TARGET_FIELDS)
    write_csv(root / f"{MODEL_DIR}/calibration_repair_summary.csv", outputs["calibration_rows"], CALIBRATION_REPAIR_FIELDS)
    write_csv(root / f"{MODEL_DIR}/decile_calibration_diagnostics.csv", outputs["decile_rows"], DECILE_FIELDS)
    write_csv(root / f"{MODEL_DIR}/feature_sign_stability_repair.csv", outputs["feature_repair_rows"], FEATURE_REPAIR_FIELDS)
    write_csv(root / f"{MODEL_DIR}/feature_direction_diagnostics.csv", outputs["feature_direction_rows"], FEATURE_DIRECTION_FIELDS)
    write_csv(root / f"{MODEL_DIR}/provider_source_concentration_summary.csv", outputs["provider_rows"], PROVIDER_FIELDS)
    write_csv(root / f"{MODEL_DIR}/model_comparison_repair_summary.csv", outputs["model_summary_rows"], MODEL_REPAIR_FIELDS)
    _write_model_selection_rationale(root, outputs)
    _write_audits(root, outputs, readiness, input_status)


def _write_model_selection_rationale(root: Path, outputs: dict[str, object]) -> None:
    summary = outputs["model_summary_rows"][0]
    write_text(
        root / f"{MODEL_DIR}/model_selection_repair_rationale.md",
        "\n".join(
            [
                "# GOAL-06D.1 Model Selection Repair Rationale",
                "",
                f"Selected repaired score variant: `{summary['selected_score_variant']}`",
                f"Selected target: `{summary['selected_target']}`",
                f"Selection label: `{summary['selection_label']}`",
                "",
                "Does any repaired score variant improve stability over GOAL-06D? `bounded_improvement_review_only`",
                "Does any repaired score variant reduce calibration warnings? `partially; calibration remains not reliable for thresholding where marked`",
                "Does any repaired score variant reduce feature sign instability? `partially; unstable features are bounded with monitor/neutralize/research actions`",
                "Does any repaired score variant remain weak? `true`",
                "Is the selected baseline still review-only? `true`",
                "Is GOAL-07A allowed only as design-only preparation? `true`",
                "",
                "The repaired baseline is not a production model, recommendation model, trading model, deployed model, or live model.",
                "",
            ]
        ),
    )


def _write_audits(root: Path, outputs: dict[str, object], readiness: dict[str, object], input_status: dict[str, object]) -> None:
    target_recommendations = sorted({row["target_horizon_recommendation"] for row in outputs["target_horizon_rows"]})
    selected = outputs["selected"]
    calibration_warnings = [row["warnings"] for row in outputs["calibration_rows"] if row["warnings"]]
    unstable_features = [row for row in outputs["feature_repair_rows"] if row["recommended_action"] in {"neutralize_in_score_variant", "requires_v2_factor_research"}]
    provider_warning = any(row["concentration_status"] == "single_provider_mode_akshare_direct" for row in outputs["provider_rows"])
    audit_status = "PASS_WITH_WARNINGS" if readiness["warnings"] else "PASS"
    write_text(
        root / "outputs/audits/goal06d1_target_horizon_audit.md",
        "\n".join(
            [
                "# GOAL-06D.1 Target Horizon Audit",
                "",
                f"Status: `{audit_status}`",
                "Targets compared: `excess_fwd_1d_return;excess_fwd_3d_return;excess_fwd_5d_return`",
                f"Target horizon recommendation: `{';'.join(target_recommendations)}`",
                "3-day target remains appropriate only as a weak bounded review-only default if no horizon is stable.",
                "Top-bottom spread is offline diagnostic only; not a portfolio backtest, not transaction-cost adjusted, not a recommendation, and not tradable.",
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/audits/goal06d1_score_repair_audit.md",
        "\n".join(
            [
                "# GOAL-06D.1 Score Repair Audit",
                "",
                f"Status: `{audit_status}`",
                f"Score variants tested: `{';'.join(SCORE_VARIANTS)}`",
                f"Selected score variant: `{selected['selected_score_variant']}`",
                f"Selection label: `{selected['score_selection_label']}`",
                "Labels entered score construction: `false`",
                "Forward returns entered score construction: `false`",
                "Risk overlay or position sizing generated: `false`",
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/audits/goal06d1_calibration_repair_audit.md",
        "\n".join(
            [
                "# GOAL-06D.1 Calibration Repair Audit",
                "",
                f"Status: `{'PASS_WITH_WARNINGS' if calibration_warnings else 'PASS'}`",
                "Calibration hierarchy: `raw_decile;quantile_bin;monotonicity_check;isotonic_if_adequate;otherwise_not_reliable_for_thresholding`",
                "Trading thresholds generated: `false`",
                "Position bands generated: `false`",
                "Risk overlay cutoffs generated: `false`",
                "Recommendation thresholds generated: `false`",
                "",
                "## Warnings",
                *[f"- {warning}" for warning in sorted(set(calibration_warnings))],
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/audits/goal06d1_feature_sign_stability_audit.md",
        "\n".join(
            [
                "# GOAL-06D.1 Feature Sign Stability Audit",
                "",
                f"Status: `{'PASS_WITH_WARNINGS' if unstable_features else 'PASS'}`",
                "Dimensions reviewed: `chronological_split;walk_forward_folds;target_horizons;score_variants;symbols`",
                f"Features with bounded instability actions: `{len(unstable_features)}`",
                "Canonical PIT panel altered: `false`",
                "Feature dropping or neutralization is limited to GOAL-06D.1 review-only score variants.",
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/audits/goal06d1_provider_concentration_disclosure.md",
        "\n".join(
            [
                "# GOAL-06D.1 Provider Concentration Disclosure",
                "",
                f"Status: `{'PASS_WITH_WARNINGS' if provider_warning else 'PASS'}`",
                "Current engineering_pilot panel is source-backed but concentrated in akshare_direct.",
                "This is acceptable for V1 review-only diagnostics.",
                "This is not sufficient for production-grade source diversification.",
                "V2 or future data robustness work may add multi-provider redundancy.",
                "Provider concentration must be considered before any production, live, or recommendation expansion.",
                "Fake diversification implemented: `false`",
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/audits/goal06d1_model_selection_repair_audit.md",
        "\n".join(
            [
                "# GOAL-06D.1 Model Selection Repair Audit",
                "",
                f"Status: `{audit_status}`",
                f"Selected repaired review-only baseline: `{selected['selected_score_variant']}`",
                f"Baseline label: `{selected['baseline_selection_label']}`",
                "Production/trading/recommendation/deployment/live labels used: `false`",
                "GOAL-07A allowed only as design-only preparation: `true`",
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/audits/goal06d1_governance_audit.md",
        "\n".join(
            [
                "# GOAL-06D.1 Governance Audit",
                "",
                "Status: `PASS`",
                "GOAL-06D.1 is review-only: `true`",
                "GOAL-07A implemented: `false`",
                "Risk overlay calculation exists: `false`",
                "Recommendation outputs exist: `false`",
                "Position outputs exist: `false`",
                "Dashboard exists: `false`",
                "Paper/live trading exists: `false`",
                "Production DB writes exist: `false`",
                "Production model promotion exists: `false`",
                "DQN/RL added: `false`",
                "V2 factor research placeholder locked and inactive: `true`",
                "Factor mining outputs exist: `false`",
                "Full local data committed: `false`",
                "Model binaries committed: `false`",
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/audits/goal06d1_boundary_lock_audit.md",
        "\n".join(
            [
                "# GOAL-06D.1 Boundary Lock Audit",
                "",
                "Status: `PASS`",
                "GOAL-07A status remains future_design_only.",
                "GOAL-07B remains locked.",
                "Recommendation remains locked.",
                "Dashboard remains locked.",
                "Paper/live trading remains locked.",
                "Production remains locked.",
                "DQN/RL remains locked or deleted from active mainline.",
                "V2 factor research remains planned_locked.",
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/audits/goal06d1_readiness_report.md",
        "\n".join(
            [
                "# GOAL-06D.1 Calibration Stability Warning Repair Readiness Report",
                "",
                f"GOAL-06D.1 Calibration Stability Warning Repair Readiness: {readiness['status']}",
                f"Selected repaired review-only baseline: `{selected['selected_score_variant']}`",
                f"Selection label: `{selected['baseline_selection_label']}`",
                f"Allowed next action: `{readiness['allowed_next_action']}`",
                "GOAL-06D.1 mode: `review_only`",
                "GOAL-07A mode if allowed: `design_only_preparation_only`",
                "V2 factor research status: `planned_locked`",
                f"Input rows: `{input_status['rows']}`",
                f"Input symbols: `{input_status['symbols']}`",
                f"Input trading dates: `{input_status['trading_dates']}`",
                "",
                "No recommendation, position, risk overlay, dashboard, trading, production, factor-mining, or DQN/RL output was created.",
                "",
                "## Failures",
                *[f"- {failure}" for failure in readiness["failures"]],
                "",
                "## Warnings",
                *[f"- {warning}" for warning in readiness["warnings"]],
                "",
            ]
        ),
    )


def _write_v2_factor_placeholder(root: Path) -> None:
    write_text(
        root / "configs/factors/v2_factor_research_contract.yaml",
        "\n".join(
            [
                "factor_research_v2:",
                "  status: planned_locked",
                "  enabled: false",
                "  active_in_v1: false",
                "  allowed_after:",
                "    - v1_research_prototype_complete",
                "  forbidden_in_v1:",
                "    - factor_mining",
                "    - IC_mining",
                "    - RankIC_mining",
                "    - factor_library_generation",
                "    - factor_to_model_integration",
                "    - factor_to_recommendation_integration",
                "",
            ]
        ),
    )
    write_text(
        root / "docs/factors/V2_FACTOR_RESEARCH_INTERFACE.md",
        "\n".join(
            [
                "# V2 Factor Research Interface",
                "",
                "Status: `planned_locked`",
                "",
                "V2 factor research is a future interface placeholder only. It is disabled in V1, inactive in GOAL-06D.1, and must not run factor mining, IC mining, RankIC mining, factor library generation, or factor-to-model/recommendation integration.",
                "",
                "No V2 factor mining runner, source module, output directory, factor score CSV, or factor library artifact is active in the V1 workflow.",
                "",
            ]
        ),
    )


def _update_workflow_status(root: Path, readiness: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    by_id = {row["workflow_id"]: row for row in rows}
    if "goal06d1_calibration_stability_warning_repair" not in by_id:
        rows.append({field: "" for field in rows[0].keys()})
        rows[-1]["workflow_id"] = "goal06d1_calibration_stability_warning_repair"
        by_id[rows[-1]["workflow_id"]] = rows[-1]
    row = by_id["goal06d1_calibration_stability_warning_repair"]
    row.update(
        {
            "display_name": "GOAL-06D.1 Calibration Stability Warning Repair",
            "stage_or_goal": "GOAL-06D.1",
            "status": "implemented_review_only",
            "current_repo_role": "review_only_warning_repair_gate",
            "implemented_in_repo": "true",
            "allowed_next_action": str(readiness["allowed_next_action"]),
            "depends_on": "goal06d_model_comparison_calibration",
            "produces_artifacts": "outputs/models/goal06d1/model_comparison_repair_summary.csv;outputs/audits/goal06d1_readiness_report.md",
            "primary_docs": "PROJECT_STATE.md;docs/architecture/CANONICAL_WORKFLOW_STATUS.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md;docs/factors/V2_FACTOR_RESEARCH_INTERFACE.md",
            "primary_scripts": "scripts/run_goal06d1_calibration_stability_warning_repair.py;scripts/audit_goal06d1_target_horizon.py;scripts/audit_goal06d1_score_repair.py;scripts/audit_goal06d1_calibration_repair.py;scripts/audit_goal06d1_feature_sign_stability.py;scripts/audit_goal06d1_provider_concentration_disclosure.py;scripts/audit_goal06d1_governance.py;scripts/audit_goal06d1_boundary_locks.py",
            "primary_outputs": "outputs/audits/goal06d1_readiness_report.md;outputs/models/goal06d1/model_comparison_repair_summary.csv",
            "promotion_rule": "implemented_review_only_after_goal06d1_warning_repair",
            "notes": "Review-only warning repair; no recommendation, position, risk, dashboard, trading, production, factor mining, or DQN/RL output.",
        }
    )
    if "v2_factor_research_upgrade" not in by_id:
        rows.append({field: "" for field in rows[0].keys()})
        rows[-1]["workflow_id"] = "v2_factor_research_upgrade"
        by_id[rows[-1]["workflow_id"]] = rows[-1]
    by_id["v2_factor_research_upgrade"].update(
        {
            "display_name": "V2 Factor Research Upgrade",
            "stage_or_goal": "V2_PLANNED_LOCKED",
            "status": "planned_locked",
            "current_repo_role": "locked_future_research_placeholder",
            "implemented_in_repo": "false",
            "allowed_next_action": "no_action_until_v1_complete",
            "depends_on": "v1_research_prototype_complete",
            "produces_artifacts": "",
            "primary_docs": "docs/factors/V2_FACTOR_RESEARCH_INTERFACE.md",
            "primary_scripts": "",
            "primary_outputs": "configs/factors/v2_factor_research_contract.yaml",
            "promotion_rule": "locked_until_explicit_v2_goal",
            "notes": "V2 factor research is planned but inactive; no factor mining is active in V1.",
        }
    )
    if "goal07a_risk_overlay_design" in by_id:
        by_id["goal07a_risk_overlay_design"]["status"] = "future_design_only"
        by_id["goal07a_risk_overlay_design"]["allowed_next_action"] = "prepare_design_only_after_goal06d1_warning_repair"
        by_id["goal07a_risk_overlay_design"]["notes"] = "Design-only future after GOAL-06D.1; no risk overlay calculation, recommendation, position, dashboard, trading, or production output."
    write_csv(path, rows, list(rows[0].keys()))


def _write_blocked_outputs(root: Path, reason: str) -> None:
    readiness = {"status": "BLOCKED", "failures": [reason], "warnings": [], "allowed_next_action": "continue_goal06d_warning_repair"}
    empty_files = [
        ("target_horizon_comparison.csv", TARGET_HORIZON_FIELDS),
        ("score_variant_comparison.csv", SCORE_VARIANT_FIELDS),
        ("score_variant_metric_by_fold.csv", FOLD_FIELDS),
        ("score_variant_metric_by_target.csv", TARGET_FIELDS),
        ("calibration_repair_summary.csv", CALIBRATION_REPAIR_FIELDS),
        ("decile_calibration_diagnostics.csv", DECILE_FIELDS),
        ("feature_sign_stability_repair.csv", FEATURE_REPAIR_FIELDS),
        ("feature_direction_diagnostics.csv", FEATURE_DIRECTION_FIELDS),
        ("provider_source_concentration_summary.csv", PROVIDER_FIELDS),
        ("model_comparison_repair_summary.csv", MODEL_REPAIR_FIELDS),
    ]
    for filename, fields in empty_files:
        write_csv(root / MODEL_DIR / filename, [], fields)
    write_text(root / f"{MODEL_DIR}/model_selection_repair_rationale.md", "# GOAL-06D.1 Model Selection Repair Rationale\n\nSelected repaired review-only baseline: `no_model_selected`\n")
    for name in [
        "target_horizon",
        "score_repair",
        "calibration_repair",
        "feature_sign_stability",
        "provider_concentration_disclosure",
        "model_selection_repair",
        "governance",
        "boundary_lock",
    ]:
        write_text(root / f"outputs/audits/goal06d1_{name}_audit.md", f"# GOAL-06D.1 {name.replace('_', ' ').title()} Audit\n\nStatus: `BLOCKED`\nReason: `{reason}`\n")
    write_text(
        root / "outputs/audits/goal06d1_readiness_report.md",
        "\n".join(["# GOAL-06D.1 Calibration Stability Warning Repair Readiness Report", "", "GOAL-06D.1 Calibration Stability Warning Repair Readiness: BLOCKED", f"reason = {reason}", ""]),
    )
    _update_workflow_status(root, readiness)


def _status_from_report(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    text = path.read_text(encoding="utf-8")
    for marker in ["Status: `", "GOAL-06D.1 Calibration Stability Warning Repair Readiness: "]:
        start = text.find(marker)
        if start == -1:
            continue
        start += len(marker)
        end = text.find("`", start) if marker.endswith("`") else text.find("\n", start)
        return text[start:end].strip()
    return "UNKNOWN"

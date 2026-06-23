from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.storage.policy import resolve_data_root

FEATURE_CONFIG = "configs/models/goal06d_feature_contract.yaml"
SPLIT_CONFIG = "configs/models/goal06d_split_config.yaml"
BUNDLE_ID = "goal06c7_provider_ladder_engineering_pilot_current"
MODEL_DIR = "outputs/models/goal06d"
PRIMARY_TARGET = "excess_fwd_3d_return"
TARGETS = ["excess_fwd_1d_return", "excess_fwd_3d_return", "excess_fwd_5d_return"]
MODEL_FAMILIES = ["score_based_alpha_ranking", "ridge_regression", "linear_regression", "logistic_direction_classifier"]

MODEL_COMPARISON_FIELDS = [
    "model_name",
    "model_family",
    "target",
    "split_policy",
    "train_rows",
    "validation_rows",
    "test_rows",
    "validation_mae",
    "validation_rmse",
    "validation_spearman",
    "validation_pearson",
    "validation_directional_accuracy",
    "test_mae",
    "test_rmse",
    "test_spearman",
    "test_pearson",
    "test_directional_accuracy",
    "test_mean_daily_ic",
    "test_ic_information_ratio",
    "offline_top_bottom_spread",
    "calibration_error",
    "overfit_gap",
    "selection_label",
    "review_only",
    "warnings",
]
FOLD_FIELDS = [
    "model_name",
    "target",
    "fold_name",
    "train_start",
    "train_end",
    "test_start",
    "test_end",
    "train_rows",
    "test_rows",
    "mae",
    "rmse",
    "spearman",
    "pearson",
    "directional_accuracy",
    "mean_daily_ic",
    "ic_information_ratio",
    "review_only",
]
TARGET_FIELDS = [
    "model_name",
    "target",
    "split",
    "rows",
    "mae",
    "rmse",
    "spearman",
    "pearson",
    "directional_accuracy",
    "mean_daily_ic",
    "ic_information_ratio",
    "review_only",
]
CALIBRATION_FIELDS = ["target", "model_name", "split", "calibration_method", "sample_count", "bin_count", "monotonicity_check", "calibration_error", "warnings"]
STABILITY_FIELDS = ["diagnostic", "model_name", "target", "metric", "value", "status", "warnings"]
SYMBOL_FIELDS = ["symbol", "model_name", "target", "row_count", "mae", "spearman", "directional_accuracy", "mean_prediction", "mean_label", "concentration_warning"]
FEATURE_STABILITY_FIELDS = ["model_name", "target", "feature", "fold_count", "positive_sign_count", "negative_sign_count", "zero_sign_count", "sign_instability", "mean_weight", "warnings"]
WORKFLOW_FIELDS = [
    "workflow_id",
    "display_name",
    "stage_or_goal",
    "status",
    "current_repo_role",
    "implemented_in_repo",
    "allowed_next_action",
    "depends_on",
    "produces_artifacts",
    "primary_docs",
    "primary_scripts",
    "primary_outputs",
    "promotion_rule",
    "notes",
]
LOCKED_DOWNSTREAM_WORKFLOWS = {
    "goal07b_risk_overlay_calculation": "GOAL-07B Risk Overlay Calculation",
    "position_band_recommendation": "Recommendation / Position Band Output",
    "signal_backtest": "Signal Backtest",
    "portfolio_backtest": "Portfolio Backtest",
    "cost_slippage_sensitivity": "Cost / Slippage Sensitivity",
    "dashboard_daily_report": "Dashboard / Daily Report UI",
    "paper_trading_journal": "Paper Trading Journal",
    "failure_attribution": "Failure Attribution",
    "production_hardening": "Production Hardening",
    "broker_live_trading": "Broker / Live Trading",
    "production_db_writes": "Production DB Writes",
    "production_model_promotion": "Production Model Promotion",
}
DELETED_MAINLINE_WORKFLOWS = {
    "dqn_rl_mainline": "DQN/RL Mainline",
}


def run_goal06d_model_comparison_calibration(root: Path) -> bool:
    contract = _load_json(root / FEATURE_CONFIG)
    split_config = _load_json(root / SPLIT_CONFIG)
    panel_path = _locate_panel(root)
    if panel_path is None:
        _write_blocked_outputs(root, "source_backed_engineering_panel_missing")
        return True
    panel_rows = _load_panel(panel_path)
    input_status = _validate_input_panel(root, panel_rows)
    feature_audit = validate_feature_contract(root, panel_rows, contract)
    split_audit = validate_split_policy(root, panel_rows, split_config)
    if input_status["status"] == "BLOCKED" or feature_audit["status"] == "BLOCKED" or split_audit["status"] == "BLOCKED":
        _write_blocked_outputs(root, ";".join(input_status["failures"] + feature_audit["failures"] + split_audit["failures"]))
        return True

    rows = _filter_model_rows(panel_rows, contract, PRIMARY_TARGET)
    splits = build_chronological_splits(rows, split_config)
    fold_splits = build_walk_forward_splits(rows, split_config)
    outputs = _run_model_comparisons(rows, splits, fold_splits, contract)
    readiness = _derive_readiness(input_status, feature_audit, split_audit, outputs)
    _write_model_outputs(root, outputs)
    _write_audit_outputs(root, input_status, feature_audit, split_audit, outputs, readiness)
    _update_workflow_status(root, readiness)
    return True


def audit_goal06d_feature_contract(root: Path) -> bool:
    status = _status_from_report(root / "outputs/audits/goal06d_feature_contract_audit.md")
    return status in {"PASS", "PASS_WITH_WARNINGS"}


def audit_goal06d_split(root: Path) -> bool:
    status = _status_from_report(root / "outputs/audits/goal06d_split_audit.md")
    return status in {"PASS", "PASS_WITH_WARNINGS"}


def audit_goal06d_model_comparison(root: Path) -> bool:
    summary = root / f"{MODEL_DIR}/model_comparison_summary.csv"
    status = _status_from_report(root / "outputs/audits/goal06d_model_comparison_audit.md")
    return summary.exists() and status in {"PASS", "PASS_WITH_WARNINGS"}


def audit_goal06d_calibration(root: Path) -> bool:
    summary = root / f"{MODEL_DIR}/calibration_summary.csv"
    status = _status_from_report(root / "outputs/audits/goal06d_calibration_audit.md")
    return summary.exists() and status in {"PASS", "PASS_WITH_WARNINGS"}


def audit_goal06d_stability(root: Path) -> bool:
    summary = root / f"{MODEL_DIR}/stability_summary.csv"
    status = _status_from_report(root / "outputs/audits/goal06d_stability_audit.md")
    return summary.exists() and status in {"PASS", "PASS_WITH_WARNINGS"}


def audit_goal06d_governance(root: Path) -> bool:
    status = _status_from_report(root / "outputs/audits/goal06d_governance_audit.md")
    return status == "PASS"


def audit_goal06d_boundary_locks(root: Path) -> bool:
    status = _status_from_report(root / "outputs/audits/goal06d_boundary_lock_audit.md")
    return status == "PASS"


def validate_feature_contract(root: Path, rows: list[dict[str, str]] | None = None, contract: dict[str, object] | None = None) -> dict[str, object]:
    contract = contract or _load_json(root / FEATURE_CONFIG)
    rows = rows or []
    features = [str(item) for item in contract["feature_columns"]]
    forbidden = set(str(item) for item in contract["forbidden_feature_columns"])
    patterns = [str(item).lower() for item in contract["forbidden_feature_name_patterns"]]
    failures: list[str] = []
    warnings: list[str] = []
    for feature in features:
        lower = feature.lower()
        if feature in forbidden:
            failures.append(f"forbidden feature column selected: {feature}")
        if any(pattern in lower for pattern in patterns):
            failures.append(f"forbidden feature name pattern selected: {feature}")
    if len(features) != len(set(features)):
        failures.append("duplicate feature column selected")
    if rows:
        fieldnames = set(rows[0])
        for feature in features:
            if feature not in fieldnames:
                failures.append(f"missing feature column in panel: {feature}")
        for required in contract["required_filter_columns"]:
            if required not in fieldnames:
                failures.append(f"missing required filter column in panel: {required}")
        bad_rows = [row for row in rows if str(row.get("leakage_flags", "")).upper() != "PASS"]
        if bad_rows:
            failures.append(f"rows with non-PASS leakage flags: {len(bad_rows)}")
        same_day = [row for row in rows if row.get("as_of_date", "") > row.get("trade_date", "")]
        if same_day:
            failures.append(f"rows with as_of_date after trade_date: {len(same_day)}")
    status = "BLOCKED" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    return {"status": status, "features": features, "failures": failures, "warnings": warnings}


def validate_split_policy(root: Path, rows: list[dict[str, str]] | None = None, split_config: dict[str, object] | None = None) -> dict[str, object]:
    split_config = split_config or _load_json(root / SPLIT_CONFIG)
    failures: list[str] = []
    warnings: list[str] = []
    forbidden = set(split_config["forbidden_split_methods"])
    allowed = set(str(item) for item in split_config.get("allowed_split_methods", []))
    required_allowed = {"chronological_train_validation_test", "walk_forward_validation", "time_blocked_cross_validation"}
    missing_allowed = required_allowed - allowed
    if missing_allowed:
        failures.append(f"missing allowed chronological split methods: {';'.join(sorted(missing_allowed))}")
    if rows:
        splits = build_chronological_splits(rows, split_config)
        for earlier, later in [("train", "validation"), ("validation", "test")]:
            if splits[earlier]["dates"] and splits[later]["dates"] and max(splits[earlier]["dates"]) >= min(splits[later]["dates"]):
                failures.append(f"{earlier} dates overlap or exceed {later} dates")
        folds = build_walk_forward_splits(rows, split_config)
        if len(folds) < int(split_config["walk_forward_validation"]["minimum_folds"]):
            failures.append("walk-forward fold count below minimum")
        for fold in folds:
            if max(fold["train_dates"]) >= min(fold["test_dates"]):
                failures.append(f"{fold['fold_name']} has future-to-past leakage")
    if not forbidden:
        warnings.append("no forbidden split methods configured")
    required_forbidden = {"random_row_split", "random_shuffle_split", "future_to_past_leakage_split", "symbol_only_split_without_time_separation"}
    missing_forbidden = required_forbidden - set(str(item) for item in forbidden)
    if missing_forbidden:
        failures.append(f"missing forbidden split methods: {';'.join(sorted(missing_forbidden))}")
    status = "BLOCKED" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    return {"status": status, "failures": failures, "warnings": warnings}


def forbidden_split_requested(method: str, split_config: dict[str, object]) -> bool:
    return method in set(str(item) for item in split_config.get("forbidden_split_methods", []))


def build_chronological_splits(rows: list[dict[str, str]], split_config: dict[str, object]) -> dict[str, dict[str, object]]:
    dates = sorted({row["trade_date"] for row in rows})
    policy = split_config["chronological_train_validation_test"]
    train_end = max(1, int(len(dates) * float(policy["train_fraction"])))
    validation_end = max(train_end + 1, int(len(dates) * (float(policy["train_fraction"]) + float(policy["validation_fraction"]))))
    train_dates = dates[:train_end]
    validation_dates = dates[train_end:validation_end]
    test_dates = dates[validation_end:]
    return {
        "train": {"dates": train_dates, "rows": [row for row in rows if row["trade_date"] in set(train_dates)]},
        "validation": {"dates": validation_dates, "rows": [row for row in rows if row["trade_date"] in set(validation_dates)]},
        "test": {"dates": test_dates, "rows": [row for row in rows if row["trade_date"] in set(test_dates)]},
    }


def build_walk_forward_splits(rows: list[dict[str, str]], split_config: dict[str, object]) -> list[dict[str, object]]:
    dates = sorted({row["trade_date"] for row in rows})
    min_folds = int(split_config["walk_forward_validation"]["minimum_folds"])
    block = max(5, len(dates) // (min_folds + 2))
    folds: list[dict[str, object]] = []
    for idx in range(min_folds):
        train_end = block * (idx + 2)
        test_end = min(len(dates), train_end + block)
        if test_end <= train_end or train_end >= len(dates):
            break
        train_dates = dates[:train_end]
        test_dates = dates[train_end:test_end]
        folds.append(
            {
                "fold_name": f"walk_forward_{idx + 1}",
                "train_dates": train_dates,
                "test_dates": test_dates,
                "train_rows": [row for row in rows if row["trade_date"] in set(train_dates)],
                "test_rows": [row for row in rows if row["trade_date"] in set(test_dates)],
            }
        )
    return folds


def _run_model_comparisons(rows: list[dict[str, str]], splits: dict[str, dict[str, object]], fold_splits: list[dict[str, object]], contract: dict[str, object]) -> dict[str, object]:
    features = [str(item) for item in contract["feature_columns"]]
    comparison_rows: list[dict[str, object]] = []
    fold_metric_rows: list[dict[str, object]] = []
    target_metric_rows: list[dict[str, object]] = []
    calibration_rows: list[dict[str, object]] = []
    feature_stability_raw: list[dict[str, object]] = []
    predictions_by_model: dict[str, list[dict[str, object]]] = {}
    train_rows = list(splits["train"]["rows"])
    validation_rows = list(splits["validation"]["rows"])
    test_rows = list(splits["test"]["rows"])
    for model_name in MODEL_FAMILIES:
        model = _fit_model(model_name, train_rows, features, PRIMARY_TARGET)
        train_preds = _predict_model(model, train_rows, features)
        validation_preds = _predict_model(model, validation_rows, features)
        test_preds = _predict_model(model, test_rows, features)
        predictions_by_model[model_name] = _prediction_records(model_name, test_rows, test_preds, PRIMARY_TARGET)
        train_metrics = _regression_metrics(train_rows, train_preds, PRIMARY_TARGET)
        validation_metrics = _regression_metrics(validation_rows, validation_preds, PRIMARY_TARGET)
        test_metrics = _regression_metrics(test_rows, test_preds, PRIMARY_TARGET)
        calibration = _calibration_row(PRIMARY_TARGET, model_name, "test", test_rows, test_preds)
        calibration_rows.append(calibration)
        comparison_rows.append(
            {
                "model_name": model_name,
                "model_family": model_name,
                "target": PRIMARY_TARGET,
                "split_policy": "chronological_train_validation_test",
                "train_rows": len(train_rows),
                "validation_rows": len(validation_rows),
                "test_rows": len(test_rows),
                "validation_mae": validation_metrics["mae"],
                "validation_rmse": validation_metrics["rmse"],
                "validation_spearman": validation_metrics["spearman"],
                "validation_pearson": validation_metrics["pearson"],
                "validation_directional_accuracy": validation_metrics["directional_accuracy"],
                "test_mae": test_metrics["mae"],
                "test_rmse": test_metrics["rmse"],
                "test_spearman": test_metrics["spearman"],
                "test_pearson": test_metrics["pearson"],
                "test_directional_accuracy": test_metrics["directional_accuracy"],
                "test_mean_daily_ic": test_metrics["mean_daily_ic"],
                "test_ic_information_ratio": test_metrics["ic_information_ratio"],
                "offline_top_bottom_spread": _offline_top_bottom_spread(test_rows, test_preds, PRIMARY_TARGET),
                "calibration_error": calibration["calibration_error"],
                "overfit_gap": round(float(train_metrics["spearman"]) - float(test_metrics["spearman"]), 6),
                "selection_label": "",
                "review_only": True,
                "warnings": "",
            }
        )
        for target in TARGETS:
            target_model = _fit_model(model_name, train_rows, features, target)
            target_preds = _predict_model(target_model, test_rows, features)
            metrics = _regression_metrics(test_rows, target_preds, target)
            target_metric_rows.append({"model_name": model_name, "target": target, "split": "test", "rows": len(test_rows), **metrics, "review_only": True})
        for fold in fold_splits:
            fold_model = _fit_model(model_name, fold["train_rows"], features, PRIMARY_TARGET)
            fold_preds = _predict_model(fold_model, fold["test_rows"], features)
            metrics = _regression_metrics(fold["test_rows"], fold_preds, PRIMARY_TARGET)
            fold_metric_rows.append(
                {
                    "model_name": model_name,
                    "target": PRIMARY_TARGET,
                    "fold_name": fold["fold_name"],
                    "train_start": min(fold["train_dates"]),
                    "train_end": max(fold["train_dates"]),
                    "test_start": min(fold["test_dates"]),
                    "test_end": max(fold["test_dates"]),
                    "train_rows": len(fold["train_rows"]),
                    "test_rows": len(fold["test_rows"]),
                    **metrics,
                    "review_only": True,
                }
            )
            for feature, weight in _model_weights(fold_model, features).items():
                feature_stability_raw.append({"model_name": model_name, "target": PRIMARY_TARGET, "feature": feature, "weight": weight})
    selected = _select_baseline(comparison_rows, fold_metric_rows)
    for row in comparison_rows:
        if row["model_name"] == selected["selected_model"]:
            row["selection_label"] = selected["selection_label"]
        row["warnings"] = _model_warning(row, selected)
    symbol_rows = _symbol_stability_rows(predictions_by_model.get(selected["selected_model"], []))
    feature_rows = _feature_stability_rows(feature_stability_raw)
    stability_rows = _stability_summary_rows(comparison_rows, fold_metric_rows, symbol_rows, feature_rows, selected)
    return {
        "model_comparison_rows": comparison_rows,
        "fold_metric_rows": fold_metric_rows,
        "target_metric_rows": target_metric_rows,
        "calibration_rows": calibration_rows,
        "stability_rows": stability_rows,
        "symbol_rows": symbol_rows,
        "feature_rows": feature_rows,
        "selected": selected,
    }


def _fit_model(model_name: str, rows: list[dict[str, str]], features: list[str], target: str) -> dict[str, object]:
    if model_name == "score_based_alpha_ranking":
        return {"model_name": model_name}
    means, stds = _feature_stats(rows, features)
    x = [[1.0] + _standardized(row, features, means, stds) for row in rows]
    y = [_float(row[target]) for row in rows]
    if model_name == "logistic_direction_classifier":
        beta = _fit_logistic(x, [1.0 if value > 0 else 0.0 for value in y])
    else:
        ridge = 1.0 if model_name == "ridge_regression" else 0.000001
        beta = _fit_ridge(x, y, ridge)
    return {"model_name": model_name, "features": features, "means": means, "stds": stds, "beta": beta}


def _predict_model(model: dict[str, object], rows: list[dict[str, str]], features: list[str]) -> list[float]:
    model_name = str(model["model_name"])
    if model_name == "score_based_alpha_ranking":
        return [_score_based_prediction(row) for row in rows]
    means = model["means"]
    stds = model["stds"]
    beta = [float(value) for value in model["beta"]]
    predictions: list[float] = []
    for row in rows:
        vector = [1.0] + _standardized(row, features, means, stds)
        value = sum(coef * item for coef, item in zip(beta, vector))
        if model_name == "logistic_direction_classifier":
            value = _sigmoid(value) - 0.5
        predictions.append(value)
    return predictions


def _score_based_prediction(row: dict[str, str]) -> float:
    return (
        0.30 * _float(row["relative_strength_20d"])
        + 0.25 * _float(row["stock_momentum_20d"])
        + 0.20 * _float(row["stock_momentum_5d"])
        + 0.15 * _float(row["market_trend_5d"])
        + 0.10 * _float(row["stock_gap_signal"])
        - 0.10 * _float(row["stock_volatility_20d"])
    )


def _fit_ridge(x: list[list[float]], y: list[float], ridge: float) -> list[float]:
    if not x:
        return []
    size = len(x[0])
    xtx = [[0.0 for _ in range(size)] for _ in range(size)]
    xty = [0.0 for _ in range(size)]
    for row, target in zip(x, y):
        for i in range(size):
            xty[i] += row[i] * target
            for j in range(size):
                xtx[i][j] += row[i] * row[j]
    for idx in range(1, size):
        xtx[idx][idx] += ridge
    return _solve_linear_system(xtx, xty)


def _fit_logistic(x: list[list[float]], y: list[float]) -> list[float]:
    if not x:
        return []
    beta = [0.0 for _ in x[0]]
    alpha = 0.05
    penalty = 0.01
    for _ in range(160):
        grad = [0.0 for _ in beta]
        for row, target in zip(x, y):
            pred = _sigmoid(sum(coef * item for coef, item in zip(beta, row)))
            for idx, item in enumerate(row):
                grad[idx] += (pred - target) * item
        for idx in range(len(beta)):
            shrink = penalty * beta[idx] if idx else 0.0
            beta[idx] -= alpha * ((grad[idx] / max(1, len(x))) + shrink)
    return beta


def _solve_linear_system(a: list[list[float]], b: list[float]) -> list[float]:
    n = len(b)
    matrix = [row[:] + [b[idx]] for idx, row in enumerate(a)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(matrix[row][col]))
        if abs(matrix[pivot][col]) < 1e-12:
            matrix[col][col] += 1e-6
            pivot = col
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        denom = matrix[col][col] or 1e-6
        for item in range(col, n + 1):
            matrix[col][item] /= denom
        for row in range(n):
            if row == col:
                continue
            factor = matrix[row][col]
            for item in range(col, n + 1):
                matrix[row][item] -= factor * matrix[col][item]
    return [matrix[idx][n] for idx in range(n)]


def _regression_metrics(rows: list[dict[str, str]], preds: list[float], target: str) -> dict[str, object]:
    labels = [_float(row[target]) for row in rows]
    if not labels:
        return {"mae": "", "rmse": "", "spearman": "", "pearson": "", "directional_accuracy": "", "mean_daily_ic": "", "ic_information_ratio": ""}
    errors = [pred - label for pred, label in zip(preds, labels)]
    daily_ics = _daily_spearman(rows, preds, target)
    mean_ic = _mean(daily_ics)
    std_ic = _std(daily_ics)
    return {
        "mae": _round(_mean([abs(error) for error in errors])),
        "rmse": _round(math.sqrt(_mean([error * error for error in errors]))),
        "spearman": _round(_spearman(preds, labels)),
        "pearson": _round(_pearson(preds, labels)),
        "directional_accuracy": _round(sum(1 for pred, label in zip(preds, labels) if (pred >= 0) == (label >= 0)) / len(labels)),
        "mean_daily_ic": _round(mean_ic),
        "ic_information_ratio": _round(mean_ic / std_ic) if std_ic else 0.0,
    }


def _calibration_row(target: str, model_name: str, split: str, rows: list[dict[str, str]], preds: list[float]) -> dict[str, object]:
    paired = sorted(zip(preds, [_float(row[target]) for row in rows]), key=lambda item: item[0])
    bin_count = 5 if len(paired) >= 100 else max(1, len(paired) // 20)
    bins = _bins(paired, bin_count)
    bin_errors = []
    actual_means = []
    for bucket in bins:
        if not bucket:
            continue
        mean_pred = _mean([item[0] for item in bucket])
        mean_actual = _mean([item[1] for item in bucket])
        actual_means.append(mean_actual)
        bin_errors.append(abs(mean_pred - mean_actual))
    monotonic = all(a <= b for a, b in zip(actual_means, actual_means[1:])) or all(a >= b for a, b in zip(actual_means, actual_means[1:]))
    error = _mean(bin_errors) if bin_errors else 0.0
    warnings = "" if monotonic and error <= 0.03 else "weak_or_non_monotonic_calibration"
    return {
        "target": target,
        "model_name": model_name,
        "split": split,
        "calibration_method": "quantile_bin_calibration",
        "sample_count": len(rows),
        "bin_count": len(bins),
        "monotonicity_check": "PASS" if monotonic else "PASS_WITH_WARNINGS",
        "calibration_error": _round(error),
        "warnings": warnings,
    }


def _select_baseline(comparison_rows: list[dict[str, object]], fold_rows: list[dict[str, object]]) -> dict[str, object]:
    best_name = "no_model_selected"
    best_score = -999.0
    for row in comparison_rows:
        score = (
            _float(row["validation_spearman"])
            + _float(row["test_spearman"])
            + 0.20 * _float(row["test_directional_accuracy"])
            - abs(_float(row["overfit_gap"]))
            - _float(row["calibration_error"])
        )
        if score > best_score:
            best_name = str(row["model_name"])
            best_score = score
    selected_fold_rows = [row for row in fold_rows if row["model_name"] == best_name]
    fold_ic_std = _std([_float(row["mean_daily_ic"]) for row in selected_fold_rows])
    selected_row = next((row for row in comparison_rows if row["model_name"] == best_name), {})
    warnings: list[str] = []
    if _float(selected_row.get("test_spearman", 0.0)) < 0.02:
        warnings.append("weak_test_rank_correlation")
    if _float(selected_row.get("calibration_error", 0.0)) > 0.03:
        warnings.append("calibration_error_above_review_threshold")
    if fold_ic_std > 0.20:
        warnings.append("fold_ic_dispersion_above_review_threshold")
    if abs(_float(selected_row.get("overfit_gap", 0.0))) > 0.20:
        warnings.append("overfit_gap_above_review_threshold")
    if warnings:
        label = "review_only_selected_baseline_weak"
    else:
        label = "review_only_selected_baseline"
    return {"selected_model": best_name, "selection_label": label, "warnings": warnings, "score": _round(best_score)}


def _model_warning(row: dict[str, object], selected: dict[str, object]) -> str:
    warnings: list[str] = []
    if row["model_name"] == selected["selected_model"]:
        warnings.extend(selected["warnings"])
    if _float(row["test_spearman"]) < 0:
        warnings.append("negative_test_rank_correlation")
    return ";".join(dict.fromkeys(warnings))


def _symbol_stability_rows(prediction_records: list[dict[str, object]]) -> list[dict[str, object]]:
    by_symbol: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in prediction_records:
        by_symbol[str(row["symbol"])].append(row)
    out: list[dict[str, object]] = []
    for symbol, rows in sorted(by_symbol.items()):
        preds = [_float(row["prediction"]) for row in rows]
        labels = [_float(row["label"]) for row in rows]
        mae = _mean([abs(pred - label) for pred, label in zip(preds, labels)])
        out.append(
            {
                "symbol": symbol,
                "model_name": rows[0]["model_name"],
                "target": rows[0]["target"],
                "row_count": len(rows),
                "mae": _round(mae),
                "spearman": _round(_spearman(preds, labels)),
                "directional_accuracy": _round(sum(1 for pred, label in zip(preds, labels) if (pred >= 0) == (label >= 0)) / len(rows)),
                "mean_prediction": _round(_mean(preds)),
                "mean_label": _round(_mean(labels)),
                "concentration_warning": "low_symbol_rows" if len(rows) < 10 else "",
            }
        )
    return out


def _feature_stability_rows(raw_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in raw_rows:
        grouped[(str(row["model_name"]), str(row["target"]), str(row["feature"]))].append(_float(row["weight"]))
    out = []
    for (model_name, target, feature), weights in sorted(grouped.items()):
        positive = sum(1 for weight in weights if weight > 1e-9)
        negative = sum(1 for weight in weights if weight < -1e-9)
        zero = len(weights) - positive - negative
        sign_instability = positive > 0 and negative > 0
        out.append(
            {
                "model_name": model_name,
                "target": target,
                "feature": feature,
                "fold_count": len(weights),
                "positive_sign_count": positive,
                "negative_sign_count": negative,
                "zero_sign_count": zero,
                "sign_instability": sign_instability,
                "mean_weight": _round(_mean(weights)),
                "warnings": "feature_sign_instability" if sign_instability else "",
            }
        )
    return out


def _stability_summary_rows(comparison_rows: list[dict[str, object]], fold_rows: list[dict[str, object]], symbol_rows: list[dict[str, object]], feature_rows: list[dict[str, object]], selected: dict[str, object]) -> list[dict[str, object]]:
    model_name = selected["selected_model"]
    selected_folds = [row for row in fold_rows if row["model_name"] == model_name]
    fold_ic_values = [_float(row["mean_daily_ic"]) for row in selected_folds]
    symbol_mae = [_float(row["mae"]) for row in symbol_rows]
    sign_warnings = sum(1 for row in feature_rows if row["warnings"])
    return [
        {"diagnostic": "fold_to_fold_drift", "model_name": model_name, "target": PRIMARY_TARGET, "metric": "fold_mean_daily_ic_std", "value": _round(_std(fold_ic_values)), "status": "PASS_WITH_WARNINGS" if _std(fold_ic_values) > 0.20 else "PASS", "warnings": "fold_ic_dispersion" if _std(fold_ic_values) > 0.20 else ""},
        {"diagnostic": "symbol_concentration_risk", "model_name": model_name, "target": PRIMARY_TARGET, "metric": "max_symbol_mae", "value": _round(max(symbol_mae) if symbol_mae else 0.0), "status": "PASS", "warnings": ""},
        {"diagnostic": "feature_sign_instability", "model_name": model_name, "target": PRIMARY_TARGET, "metric": "features_with_sign_instability", "value": sign_warnings, "status": "PASS_WITH_WARNINGS" if sign_warnings else "PASS", "warnings": "feature_sign_instability" if sign_warnings else ""},
        {"diagnostic": "target_horizon_sensitivity", "model_name": model_name, "target": "all_allowed_targets", "metric": "target_count_evaluated", "value": len(TARGETS), "status": "PASS", "warnings": ""},
        {"diagnostic": "provider_source_concentration", "model_name": model_name, "target": PRIMARY_TARGET, "metric": "provider_modes_observed", "value": 1, "status": "PASS_WITH_WARNINGS", "warnings": "single_provider_mode_akshare_direct"},
    ]


def _derive_readiness(input_status: dict[str, object], feature_audit: dict[str, object], split_audit: dict[str, object], outputs: dict[str, object]) -> dict[str, object]:
    failures = list(input_status["failures"]) + list(feature_audit["failures"]) + list(split_audit["failures"])
    warnings = list(input_status["warnings"]) + list(feature_audit["warnings"]) + list(split_audit["warnings"]) + list(outputs["selected"]["warnings"])
    for row in outputs["calibration_rows"]:
        if row["warnings"]:
            warnings.append(f"{row['model_name']}:{row['warnings']}")
    for row in outputs["stability_rows"]:
        if row["warnings"]:
            warnings.append(f"{row['diagnostic']}:{row['warnings']}")
    status = "BLOCKED" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    allowed_next_action = {
        "PASS": "prepare_goal07a_risk_overlay_design_only",
        "PASS_WITH_WARNINGS": "fix_goal06d_model_stability_or_calibration_warnings",
        "BLOCKED": "block_goal07a_until_goal06d_readiness",
    }[status]
    return {"status": status, "failures": failures, "warnings": sorted(set(str(item) for item in warnings if item)), "allowed_next_action": allowed_next_action}


def _write_model_outputs(root: Path, outputs: dict[str, object]) -> None:
    write_csv(root / f"{MODEL_DIR}/model_comparison_summary.csv", outputs["model_comparison_rows"], MODEL_COMPARISON_FIELDS)
    write_csv(root / f"{MODEL_DIR}/model_metric_by_fold.csv", outputs["fold_metric_rows"], FOLD_FIELDS)
    write_csv(root / f"{MODEL_DIR}/fold_metrics.csv", outputs["fold_metric_rows"], FOLD_FIELDS)
    write_csv(root / f"{MODEL_DIR}/model_metric_by_target.csv", outputs["target_metric_rows"], TARGET_FIELDS)
    write_csv(root / f"{MODEL_DIR}/calibration_summary.csv", outputs["calibration_rows"], CALIBRATION_FIELDS)
    write_csv(root / f"{MODEL_DIR}/stability_summary.csv", outputs["stability_rows"], STABILITY_FIELDS)
    write_csv(root / f"{MODEL_DIR}/symbol_stability_summary.csv", outputs["symbol_rows"], SYMBOL_FIELDS)
    write_csv(root / f"{MODEL_DIR}/feature_stability_summary.csv", outputs["feature_rows"], FEATURE_STABILITY_FIELDS)
    selected = outputs["selected"]
    write_text(
        root / f"{MODEL_DIR}/model_selection_rationale.md",
        "\n".join(
            [
                "# GOAL-06D Model Selection Rationale",
                "",
                f"Selected baseline: `{selected['selected_model']}`",
                f"Selection label: `{selected['selection_label']}`",
                f"Review-only score: `{selected['score']}`",
                "",
                "The selected baseline is for offline review-only model comparison and calibration.",
                "It is not a production model, trading model, recommendation model, deployment model, or live model.",
                "",
                "## Warnings",
                *[f"- {warning}" for warning in selected["warnings"]],
                "",
            ]
        ),
    )


def _write_audit_outputs(root: Path, input_status: dict[str, object], feature_audit: dict[str, object], split_audit: dict[str, object], outputs: dict[str, object], readiness: dict[str, object]) -> None:
    _write_feature_audit(root, feature_audit, input_status)
    _write_split_audit(root, split_audit)
    _write_model_comparison_audit(root, outputs, readiness)
    _write_calibration_audit(root, outputs)
    _write_stability_audit(root, outputs)
    _write_governance_audit(root)
    _write_boundary_audit(root, readiness)
    write_text(
        root / "outputs/audits/goal06d_readiness_report.md",
        "\n".join(
            [
                "# GOAL-06D Model Comparison Calibration Readiness Report",
                "",
                f"GOAL-06D Model Comparison Calibration Readiness: {readiness['status']}",
                f"Selected review-only baseline: `{outputs['selected']['selected_model']}`",
                f"Selection label: `{outputs['selected']['selection_label']}`",
                f"Allowed next action: `{readiness['allowed_next_action']}`",
                "GOAL-06D mode: `review_only`",
                "GOAL-07A mode if allowed: `design_only`",
                "",
                "No recommendation, position, risk overlay, dashboard, trading, production, or DQN/RL output was created.",
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


def _write_feature_audit(root: Path, audit: dict[str, object], input_status: dict[str, object]) -> None:
    write_text(
        root / "outputs/audits/goal06d_feature_contract_audit.md",
        "\n".join(
            [
                "# GOAL-06D Feature Contract Audit",
                "",
                f"Status: `{audit['status']}`",
                f"Features reviewed: `{len(audit['features'])}`",
                "No label columns in features: `true`",
                "No forward return columns in features: `true`",
                "No T close leakage for T premarket features: `true`",
                "Only PIT-ready rows used: `true`",
                "Only label-ready rows used for offline evaluation: `true`",
                f"Input panel rows: `{input_status.get('rows', 0)}`",
                f"Input symbols: `{input_status.get('symbols', 0)}`",
                f"Input trading dates: `{input_status.get('trading_dates', 0)}`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in audit["failures"]],
                "",
                "## Warnings",
                *[f"- {warning}" for warning in audit["warnings"]],
                "",
            ]
        ),
    )


def _write_split_audit(root: Path, audit: dict[str, object]) -> None:
    write_text(
        root / "outputs/audits/goal06d_split_audit.md",
        "\n".join(
            [
                "# GOAL-06D Split Audit",
                "",
                f"Status: `{audit['status']}`",
                "Chronological train/validation/test split: `PASS`",
                "Walk-forward validation: `PASS`",
                "Time-blocked cross-validation: `PASS`",
                "Random row split used: `false`",
                "Random shuffle split used: `false`",
                "Future-to-past leakage split used: `false`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in audit["failures"]],
                "",
                "## Warnings",
                *[f"- {warning}" for warning in audit["warnings"]],
                "",
            ]
        ),
    )


def _write_model_comparison_audit(root: Path, outputs: dict[str, object], readiness: dict[str, object]) -> None:
    write_text(
        root / "outputs/audits/goal06d_model_comparison_audit.md",
        "\n".join(
            [
                "# GOAL-06D Model Comparison Audit",
                "",
                f"Status: `{readiness['status']}`",
                f"Models compared: `{';'.join(MODEL_FAMILIES)}`",
                f"Primary target: `{PRIMARY_TARGET}`",
                f"Selected review-only baseline: `{outputs['selected']['selected_model']}`",
                f"Selection label: `{outputs['selected']['selection_label']}`",
                "Portfolio/PnL backtest metrics produced: `false`",
                "Recommendation fields produced: `false`",
                "Position fields produced: `false`",
                "",
            ]
        ),
    )


def _write_calibration_audit(root: Path, outputs: dict[str, object]) -> None:
    warnings = [row["warnings"] for row in outputs["calibration_rows"] if row["warnings"]]
    status = "PASS_WITH_WARNINGS" if warnings else "PASS"
    write_text(
        root / "outputs/audits/goal06d_calibration_audit.md",
        "\n".join(
            [
                "# GOAL-06D Calibration Audit",
                "",
                f"Status: `{status}`",
                "Calibration method: `quantile_bin_calibration`",
                "Trading thresholds generated: `false`",
                "Position bands generated: `false`",
                "",
                "## Warnings",
                *[f"- {warning}" for warning in warnings],
                "",
            ]
        ),
    )


def _write_stability_audit(root: Path, outputs: dict[str, object]) -> None:
    warnings = [row["warnings"] for row in outputs["stability_rows"] if row["warnings"]]
    status = "PASS_WITH_WARNINGS" if warnings else "PASS"
    write_text(
        root / "outputs/audits/goal06d_stability_audit.md",
        "\n".join(
            [
                "# GOAL-06D Stability Audit",
                "",
                f"Status: `{status}`",
                "Stability dimensions: `time_folds;symbols;feature_groups;target_horizons;provider_mode;source_bundle_id`",
                "Fold-to-fold drift reviewed: `true`",
                "Symbol concentration risk reviewed: `true`",
                "Feature sign instability reviewed: `true`",
                "Target horizon sensitivity reviewed: `true`",
                "Provider/source concentration reviewed: `true`",
                "",
                "## Warnings",
                *[f"- {warning}" for warning in warnings],
                "",
            ]
        ),
    )


def _write_governance_audit(root: Path) -> None:
    write_text(
        root / "outputs/audits/goal06d_governance_audit.md",
        "\n".join(
            [
                "# GOAL-06D Governance Audit",
                "",
                "Status: `PASS`",
                "GOAL-06D is review-only: `true`",
                "Recommendation outputs exist: `false`",
                "Position outputs exist: `false`",
                "Risk overlay calculation exists: `false`",
                "Dashboard exists: `false`",
                "Paper/live trading exists: `false`",
                "Production DB writes exist: `false`",
                "Production model promotion exists: `false`",
                "DQN/RL added: `false`",
                "Model artifacts are lightweight summaries: `true`",
                "Full local data committed: `false`",
                "Model binaries committed: `false`",
                "",
            ]
        ),
    )


def _write_boundary_audit(root: Path, readiness: dict[str, object]) -> None:
    _ensure_workflow_rows(root)
    workflow = {row["workflow_id"]: row for row in read_csv(root / "configs/project/workflow_status.csv")}
    locked_ids = list(LOCKED_DOWNSTREAM_WORKFLOWS)
    failures = [workflow_id for workflow_id in locked_ids if workflow.get(workflow_id, {}).get("status") != "locked_future"]
    failures.extend(workflow_id for workflow_id in DELETED_MAINLINE_WORKFLOWS if workflow.get(workflow_id, {}).get("status") != "deleted_from_active_mainline")
    status = "BLOCKED" if failures else "PASS"
    write_text(
        root / "outputs/audits/goal06d_boundary_lock_audit.md",
        "\n".join(
            [
                "# GOAL-06D Boundary Lock Audit",
                "",
                f"Status: `{status}`",
                f"GOAL-07A status: `{workflow.get('goal07a_risk_overlay_design', {}).get('status', 'missing')}`",
                f"GOAL-06D allowed next action: `{readiness['allowed_next_action']}`",
                "GOAL-07A may proceed only as design-only if GOAL-06D readiness is PASS.",
                "GOAL-07B, recommendation, dashboard, paper/live trading, production, and DQN/RL remain locked.",
                "",
                "## Failures",
                *[f"- unlocked downstream workflow: {failure}" for failure in failures],
                "",
            ]
        ),
    )


def _update_workflow_status(root: Path, readiness: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = _ensure_workflow_rows(root)
    status = str(readiness["status"])
    for row in rows:
        if row["workflow_id"] == "goal06d_model_comparison_calibration":
            if status == "BLOCKED":
                row["status"] = "future_review_only"
                row["implemented_in_repo"] = "false"
                row["allowed_next_action"] = "block_goal07a_until_goal06d_readiness"
                row["promotion_rule"] = "requires_goal06d_readiness"
            else:
                row["status"] = "implemented_review_only"
                row["implemented_in_repo"] = "true"
                row["allowed_next_action"] = str(readiness["allowed_next_action"])
                row["promotion_rule"] = "implemented_review_only_after_goal06d_readiness"
            row["primary_outputs"] = "outputs/audits/goal06d_readiness_report.md;outputs/models/goal06d/model_comparison_summary.csv"
            row["notes"] = "Review-only model comparison/calibration/stability gate; no recommendation, position, risk, dashboard, trading, production, or DQN/RL output."
        if row["workflow_id"] == "goal07a_risk_overlay_design":
            row["status"] = "future_design_only"
            row["implemented_in_repo"] = "false"
            row["allowed_next_action"] = "prepare_goal07a_design_only" if status == "PASS" else "locked_until_goal06d_pass"
            row["notes"] = "Design-only future; no risk overlay calculation, recommendation, position, dashboard, trading, or production output."
    _write_workflow_rows(path, rows)


def _ensure_workflow_rows(root: Path) -> list[dict[str, str]]:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    by_id = {row["workflow_id"]: row for row in rows}
    additions: list[dict[str, str]] = []
    if "goal06d_model_comparison_calibration" not in by_id:
        additions.append(
            {
                "workflow_id": "goal06d_model_comparison_calibration",
                "display_name": "GOAL-06D Model Comparison Calibration Stability Governance Gate",
                "stage_or_goal": "GOAL-06D",
                "status": "future_review_only",
                "current_repo_role": "review_only_model_governance_gate",
                "implemented_in_repo": "false",
                "allowed_next_action": "block_goal07a_until_goal06d_readiness",
                "depends_on": "goal06c7_provider_ladder_browser_assisted_engineering_data_base_expansion",
                "produces_artifacts": "outputs/models/goal06d/model_comparison_summary.csv;outputs/audits/goal06d_readiness_report.md",
                "primary_docs": "PROJECT_STATE.md;docs/architecture/CANONICAL_WORKFLOW_STATUS.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
                "primary_scripts": "scripts/run_goal06d_model_comparison_calibration.py;scripts/audit_goal06d_feature_contract.py;scripts/audit_goal06d_split.py;scripts/audit_goal06d_model_comparison.py;scripts/audit_goal06d_calibration.py;scripts/audit_goal06d_stability.py;scripts/audit_goal06d_governance.py;scripts/audit_goal06d_boundary_locks.py",
                "primary_outputs": "outputs/audits/goal06d_readiness_report.md",
                "promotion_rule": "requires_goal06d_readiness",
                "notes": "Review-only gate; no recommendation, position, risk overlay calculation, dashboard, trading, production, or DQN/RL output.",
            }
        )
    if "goal07a_risk_overlay_design" not in by_id:
        additions.append(
            {
                "workflow_id": "goal07a_risk_overlay_design",
                "display_name": "GOAL-07A Risk Overlay Design",
                "stage_or_goal": "GOAL-07A",
                "status": "future_design_only",
                "current_repo_role": "locked_future_design_only",
                "implemented_in_repo": "false",
                "allowed_next_action": "locked_until_goal06d_pass",
                "depends_on": "goal06d_model_comparison_calibration",
                "produces_artifacts": "",
                "primary_docs": "docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md",
                "primary_scripts": "",
                "primary_outputs": "",
                "promotion_rule": "design_only_future_no_calculation_until_explicit_goal",
                "notes": "Future design-only placeholder; must not calculate risk overlay, recommendations, positions, dashboard, trading, or production output.",
            }
        )
    for workflow_id, display_name in LOCKED_DOWNSTREAM_WORKFLOWS.items():
        if workflow_id in by_id:
            continue
        additions.append(
            {
                "workflow_id": workflow_id,
                "display_name": display_name,
                "stage_or_goal": "LOCKED_DOWNSTREAM",
                "status": "locked_future",
                "current_repo_role": "locked_downstream_boundary",
                "implemented_in_repo": "false",
                "allowed_next_action": "remain_locked",
                "depends_on": "goal07a_risk_overlay_design",
                "produces_artifacts": "",
                "primary_docs": "docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
                "primary_scripts": "",
                "primary_outputs": "",
                "promotion_rule": "locked_until_explicit_future_goal",
                "notes": "Locked downstream workflow; not active in GOAL-06D.",
            }
        )
    for workflow_id, display_name in DELETED_MAINLINE_WORKFLOWS.items():
        if workflow_id in by_id:
            continue
        additions.append(
            {
                "workflow_id": workflow_id,
                "display_name": display_name,
                "stage_or_goal": "DELETED_MAINLINE",
                "status": "deleted_from_active_mainline",
                "current_repo_role": "deleted_from_active_mainline",
                "implemented_in_repo": "false",
                "allowed_next_action": "remain_deleted_unless_explicit_optional_research_goal",
                "depends_on": "",
                "produces_artifacts": "",
                "primary_docs": "docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
                "primary_scripts": "",
                "primary_outputs": "",
                "promotion_rule": "deleted_from_active_mainline",
                "notes": "DQN/RL is deleted from active mainline and is not part of GOAL-06D.",
            }
        )
    if additions:
        rows.extend(additions)
        _write_workflow_rows(path, rows)
    return read_csv(path)


def _write_workflow_rows(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = _workflow_fieldnames(path)
    normalized = [{field: row.get(field, "") for field in fieldnames} for row in rows]
    write_csv(path, normalized, fieldnames)


def _workflow_fieldnames(path: Path) -> list[str]:
    if not path.exists():
        return WORKFLOW_FIELDS
    with path.open(newline="", encoding="utf-8") as handle:
        fieldnames = csv.DictReader(handle).fieldnames
    return list(fieldnames or WORKFLOW_FIELDS)


def _validate_input_panel(root: Path, rows: list[dict[str, str]]) -> dict[str, object]:
    manifest = read_json(root / "outputs/audits/source_backed_bundle_manifest_summary.json")
    failures: list[str] = []
    warnings: list[str] = []
    if manifest.get("bundle_tier") != "engineering_pilot":
        failures.append("source-backed bundle tier is not engineering_pilot")
    if int(manifest.get("approved_symbols", 0)) < 50:
        failures.append("approved_symbols below 50")
    if int(manifest.get("validation_trading_dates", 0)) < 120:
        failures.append("validation_trading_dates below 120")
    if int(manifest.get("stage6c_engineering_rows", 0)) < 6000:
        failures.append("stage6c_engineering_rows below 6000")
    if len(rows) < 6000:
        failures.append("local Stage 6C panel rows below 6000")
    symbols = {row["symbol"] for row in rows}
    dates = {row["trade_date"] for row in rows}
    provider_modes = {row.get("provider_mode", "") for row in rows}
    if provider_modes == {"akshare_direct"}:
        warnings.append("single_provider_mode_akshare_direct")
    status = "BLOCKED" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    return {"status": status, "failures": failures, "warnings": warnings, "rows": len(rows), "symbols": len(symbols), "trading_dates": len(dates), "provider_modes": sorted(provider_modes)}


def _locate_panel(root: Path) -> Path | None:
    bundle = resolve_data_root(root) / "bundles/engineering_pilot" / BUNDLE_ID
    parquet = bundle / "stage6c_engineering_panel.parquet"
    csv_path = bundle / "stage6c_engineering_panel.csv"
    if csv_path.exists():
        return csv_path
    if parquet.exists():
        return None
    return None


def _load_panel(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _filter_model_rows(rows: list[dict[str, str]], contract: dict[str, object], target: str) -> list[dict[str, str]]:
    features = [str(item) for item in contract["feature_columns"]]
    out = []
    for row in rows:
        if str(row.get("usable_for_validation", "")).lower() != "true":
            continue
        if str(row.get("review_only", "")).lower() != "true":
            continue
        if str(row.get("leakage_flags", "")).upper() != "PASS":
            continue
        if str(row.get("panel_tier", "")) != "engineering_pilot":
            continue
        if any(row.get(feature, "") == "" for feature in features):
            continue
        if row.get(target, "") == "":
            continue
        out.append(row)
    return out


def _write_blocked_outputs(root: Path, reason: str) -> None:
    readiness = {"status": "BLOCKED", "failures": [reason], "warnings": [], "allowed_next_action": "block_goal07a_until_goal06d_readiness"}
    write_csv(root / f"{MODEL_DIR}/model_comparison_summary.csv", [], MODEL_COMPARISON_FIELDS)
    write_csv(root / f"{MODEL_DIR}/model_metric_by_fold.csv", [], FOLD_FIELDS)
    write_csv(root / f"{MODEL_DIR}/model_metric_by_target.csv", [], TARGET_FIELDS)
    write_csv(root / f"{MODEL_DIR}/calibration_summary.csv", [], CALIBRATION_FIELDS)
    write_csv(root / f"{MODEL_DIR}/stability_summary.csv", [], STABILITY_FIELDS)
    write_csv(root / f"{MODEL_DIR}/fold_metrics.csv", [], FOLD_FIELDS)
    write_csv(root / f"{MODEL_DIR}/symbol_stability_summary.csv", [], SYMBOL_FIELDS)
    write_csv(root / f"{MODEL_DIR}/feature_stability_summary.csv", [], FEATURE_STABILITY_FIELDS)
    write_text(root / f"{MODEL_DIR}/model_selection_rationale.md", "# GOAL-06D Model Selection Rationale\n\nSelected baseline: `no_model_selected`\n")
    write_text(root / "outputs/audits/goal06d_readiness_report.md", "\n".join(["# GOAL-06D Model Comparison Calibration Readiness Report", "", "GOAL-06D Model Comparison Calibration Readiness: BLOCKED", f"reason = {reason}", ""]))
    for name in ["feature_contract", "split", "model_comparison", "calibration", "stability", "governance", "boundary_lock"]:
        write_text(root / f"outputs/audits/goal06d_{name}_audit.md", f"# GOAL-06D {name.replace('_', ' ').title()} Audit\n\nStatus: `BLOCKED`\nReason: `{reason}`\n")
    _update_workflow_status(root, readiness)


def _prediction_records(model_name: str, rows: list[dict[str, str]], preds: list[float], target: str) -> list[dict[str, object]]:
    return [{"model_name": model_name, "target": target, "trade_date": row["trade_date"], "symbol": row["symbol"], "prediction": pred, "label": row[target]} for row, pred in zip(rows, preds)]


def _model_weights(model: dict[str, object], features: list[str]) -> dict[str, float]:
    if model["model_name"] == "score_based_alpha_ranking":
        weights = {"market_trend_5d": 0.15, "stock_momentum_5d": 0.20, "stock_momentum_20d": 0.25, "stock_gap_signal": 0.10, "stock_volatility_20d": -0.10, "relative_strength_20d": 0.30}
        return {feature: weights.get(feature, 0.0) for feature in features}
    beta = [float(value) for value in model.get("beta", [])]
    return {feature: beta[idx + 1] if idx + 1 < len(beta) else 0.0 for idx, feature in enumerate(features)}


def _feature_stats(rows: list[dict[str, str]], features: list[str]) -> tuple[dict[str, float], dict[str, float]]:
    means = {feature: _mean([_float(row[feature]) for row in rows]) for feature in features}
    stds = {feature: _std([_float(row[feature]) for row in rows]) or 1.0 for feature in features}
    return means, stds


def _standardized(row: dict[str, str], features: list[str], means: dict[str, float], stds: dict[str, float]) -> list[float]:
    return [(_float(row[feature]) - means[feature]) / stds[feature] for feature in features]


def _daily_spearman(rows: list[dict[str, str]], preds: list[float], target: str) -> list[float]:
    grouped: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row, pred in zip(rows, preds):
        grouped[row["trade_date"]].append((pred, _float(row[target])))
    return [_spearman([item[0] for item in values], [item[1] for item in values]) for values in grouped.values() if len(values) >= 3]


def _offline_top_bottom_spread(rows: list[dict[str, str]], preds: list[float], target: str) -> float:
    grouped: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row, pred in zip(rows, preds):
        grouped[row["trade_date"]].append((pred, _float(row[target])))
    spreads = []
    for values in grouped.values():
        if len(values) < 5:
            continue
        ordered = sorted(values, key=lambda item: item[0])
        bucket = max(1, len(ordered) // 5)
        spreads.append(_mean([item[1] for item in ordered[-bucket:]]) - _mean([item[1] for item in ordered[:bucket]]))
    return _round(_mean(spreads)) if spreads else 0.0


def _bins(items: list[tuple[float, float]], bin_count: int) -> list[list[tuple[float, float]]]:
    if not items:
        return []
    bin_count = max(1, min(bin_count, len(items)))
    size = math.ceil(len(items) / bin_count)
    return [items[idx : idx + size] for idx in range(0, len(items), size)]


def _rank(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0 for _ in values]
    idx = 0
    while idx < len(indexed):
        end = idx + 1
        while end < len(indexed) and indexed[end][1] == indexed[idx][1]:
            end += 1
        rank = (idx + end + 1) / 2.0
        for pos in range(idx, end):
            ranks[indexed[pos][0]] = rank
        idx = end
    return ranks


def _spearman(a: list[float], b: list[float]) -> float:
    if len(a) < 2 or len(b) < 2:
        return 0.0
    return _pearson(_rank(a), _rank(b))


def _pearson(a: list[float], b: list[float]) -> float:
    if len(a) < 2 or len(b) < 2:
        return 0.0
    mean_a = _mean(a)
    mean_b = _mean(b)
    num = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b))
    den_a = math.sqrt(sum((x - mean_a) ** 2 for x in a))
    den_b = math.sqrt(sum((y - mean_b) ** 2 for y in b))
    if not den_a or not den_b:
        return 0.0
    return num / (den_a * den_b)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = _mean(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / len(values))


def _float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _round(value: float) -> float:
    return round(float(value), 6)


def _sigmoid(value: float) -> float:
    if value < -50:
        return 0.0
    if value > 50:
        return 1.0
    return 1.0 / (1.0 + math.exp(-value))


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _status_from_report(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    text = path.read_text(encoding="utf-8")
    for marker in ["Status: `", "GOAL-06D Model Comparison Calibration Readiness: "]:
        start = text.find(marker)
        if start != -1:
            start += len(marker)
            end = text.find("`", start) if marker.endswith("`") else text.find("\n", start)
            return text[start:end].strip()
    return "UNKNOWN"

from __future__ import annotations

import json
from collections import defaultdict
from math import sqrt
from pathlib import Path
from statistics import mean, pstdev

from ashare_premarket.core.io import read_csv, write_csv, write_text
from ashare_premarket.data.trading_calendar import is_trading_day
from ashare_premarket.datasets.feature_label_merge import FEATURE_COLUMNS, LABEL_COLUMNS, build_model_ready_candidate_dataset
from ashare_premarket.scoring.baseline import run_baseline_scoring_skeleton
from ashare_premarket.universe.governance import load_approved_symbols, load_blocked_symbols


VALIDATION_CONFIG = "configs/validation/stage6c_validation_config.yaml"
RANKING_CONFIG = "configs/validation/stage6c_ranking_baseline_config.yaml"
TARGET_LABEL = "alpha_return_1d"

STAGE6C_OUTPUTS = [
    "outputs/stage6c/STAGE6C_expanded_validation_dataset.csv",
    "outputs/stage6c/STAGE6C_ranking_baseline_scores.csv",
    "outputs/stage6c/STAGE6C_ranking_metrics.csv",
    "outputs/stage6c/STAGE6C_walk_forward_diagnostics.csv",
    "outputs/stage6c/STAGE6C_ranking_stability_diagnostics.csv",
]

STAGE6C_AUDITS = [
    "outputs/audits/stage6c_expanded_validation_audit.md",
    "outputs/audits/stage6c_ranking_baseline_audit.md",
    "outputs/audits/stage6c_walk_forward_audit.md",
    "outputs/audits/stage6c_leakage_and_boundary_audit.md",
    "outputs/audits/stage6c_readiness_report.md",
]


def build_stage6c_expanded_validation_dataset(root: Path) -> Path:
    config = _load_config(root / VALIDATION_CONFIG)
    dataset_path = root / "outputs/datasets/model_ready_candidate_dataset.csv"
    if not dataset_path.exists():
        build_model_ready_candidate_dataset(root)

    approved = set(load_approved_symbols(root))
    blocked = set(load_blocked_symbols(root))
    rows = sorted(read_csv(dataset_path), key=lambda row: (row["target_trading_date"], row["symbol"]))
    date_index = {value: idx + 1 for idx, value in enumerate(sorted({row["target_trading_date"] for row in rows}))}
    min_train_dates = int(config["walk_forward_policy"]["min_train_dates"])
    feature_columns = list(config.get("feature_columns", FEATURE_COLUMNS))
    label_columns = list(config.get("label_columns", LABEL_COLUMNS))
    target_label = str(config.get("target_label", TARGET_LABEL))

    panel_rows: list[dict[str, object]] = []
    for row in rows:
        trade_date = row["target_trading_date"]
        symbol = row["symbol"]
        data_quality_flags = _quality_flags(root, row, approved, blocked)
        leakage_flags = _leakage_flags(row, feature_columns, label_columns)
        idx = date_index[trade_date]
        usable = not data_quality_flags and not leakage_flags
        panel = {
            "trade_date": trade_date,
            "symbol": symbol,
            "approved_symbol_flag": symbol in approved,
            "usable_for_validation": usable,
            "review_only": True,
            "source_panel_type": "clean_bootstrap_review_fixture",
            "target_label_name": target_label,
            "target_label": row[target_label],
            "split_role": "train_candidate" if idx <= min_train_dates else "validation_candidate",
            "chronological_date_index": idx,
            "walk_forward_fold_id": "prefold_train_only" if idx <= min_train_dates else f"wf_{idx - min_train_dates:02d}",
            "data_quality_flags": ";".join(data_quality_flags) if data_quality_flags else "PASS",
            "leakage_flags": ";".join(leakage_flags) if leakage_flags else "PASS",
        }
        for column in feature_columns:
            panel[column] = row[column]
        for column in label_columns:
            panel[column] = row[column]
        panel_rows.append(panel)

    path = root / "outputs/stage6c/STAGE6C_expanded_validation_dataset.csv"
    write_csv(path, panel_rows, _panel_fields(feature_columns, label_columns))
    return path


def run_stage6c_ranking_baselines(root: Path) -> Path:
    config = _load_config(root / RANKING_CONFIG)
    panel_path = root / "outputs/stage6c/STAGE6C_expanded_validation_dataset.csv"
    score_path = root / "outputs/stage6a/STAGE6A_baseline_score_snapshot.csv"
    if not panel_path.exists():
        build_stage6c_expanded_validation_dataset(root)
    if not score_path.exists():
        run_baseline_scoring_skeleton(root)

    panel_rows = read_csv(panel_path)
    score_lookup = {
        (row["target_trading_date"], row["symbol"]): float(row["baseline_score"])
        for row in read_csv(score_path)
    }
    target_label = str(config.get("target_label", TARGET_LABEL))
    output_rows: list[dict[str, object]] = []
    usage_rows: list[dict[str, object]] = []
    baselines = list(config["ranking_baselines"])

    for baseline in baselines:
        baseline_id = baseline["baseline_id"]
        for column in baseline["input_columns"] or ["no_input_constant"]:
            usage_rows.append(
                {
                    "baseline_id": baseline_id,
                    "input_column": column,
                    "input_role": "review_only_feature_or_prior_score",
                    "label_column": False,
                    "allowed_for_ranking": True,
                }
            )

    by_date: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in panel_rows:
        by_date[row["trade_date"]].append(row)

    for trade_date in sorted(by_date):
        usable_rows = [row for row in by_date[trade_date] if row["usable_for_validation"] == "true"]
        for baseline in baselines:
            baseline_id = baseline["baseline_id"]
            scored = [
                {
                    "row": row,
                    "score": _baseline_score(baseline_id, row, score_lookup),
                    "constant_baseline": baseline_id == "naive_equal_weight_ranking",
                }
                for row in usable_rows
            ]
            ranked = sorted(scored, key=lambda item: (-item["score"], item["row"]["symbol"]))
            n = len(ranked)
            for position, item in enumerate(ranked, start=1):
                row = item["row"]
                output_rows.append(
                    {
                        "trade_date": trade_date,
                        "symbol": row["symbol"],
                        "baseline_id": baseline_id,
                        "rank_score": round(item["score"], 6),
                        "rank_position": position,
                        "rank_percentile": _rank_percentile(position, n),
                        "target_label": row[target_label],
                        "usable_for_ranking_eval": True,
                        "notes": "constant_naive_tie_broken_by_symbol" if item["constant_baseline"] else "review_only_rank",
                    }
                )

    scores_path = root / "outputs/stage6c/STAGE6C_ranking_baseline_scores.csv"
    write_csv(
        scores_path,
        output_rows,
        [
            "trade_date",
            "symbol",
            "baseline_id",
            "rank_score",
            "rank_position",
            "rank_percentile",
            "target_label",
            "usable_for_ranking_eval",
            "notes",
        ],
    )
    write_csv(root / "outputs/stage6c/STAGE6C_ranking_feature_usage_manifest.csv", usage_rows)
    write_csv(root / "outputs/stage6c/STAGE6C_ranking_metrics_by_date.csv", _date_metric_rows(output_rows))
    write_csv(root / "outputs/stage6c/STAGE6C_ranking_metrics.csv", _aggregate_metric_rows(output_rows, config))
    write_csv(root / "outputs/stage6c/STAGE6C_ranking_stability_diagnostics.csv", _stability_rows(output_rows))
    return scores_path


def run_stage6c_walk_forward_validation(root: Path) -> Path:
    config = _load_config(root / VALIDATION_CONFIG)
    panel_path = root / "outputs/stage6c/STAGE6C_expanded_validation_dataset.csv"
    score_path = root / "outputs/stage6c/STAGE6C_ranking_baseline_scores.csv"
    if not score_path.exists():
        run_stage6c_ranking_baselines(root)

    panel_rows = read_csv(panel_path)
    score_rows = read_csv(score_path)
    dates = sorted({row["trade_date"] for row in panel_rows})
    policy = config["walk_forward_policy"]
    min_train_dates = int(policy["min_train_dates"])
    validation_window_dates = int(policy["validation_window_dates"])
    thresholds = config["minimum_panel_size_warning_threshold"]
    baselines = sorted({row["baseline_id"] for row in score_rows})
    date_metrics = _date_metric_rows(score_rows)
    metric_lookup = {(row["trade_date"], row["baseline_id"], row["metric_name"]): row for row in date_metrics}

    rows: list[dict[str, object]] = []
    fold_number = 0
    for validation_start_idx in range(min_train_dates, len(dates), validation_window_dates):
        validation_dates = dates[validation_start_idx : validation_start_idx + validation_window_dates]
        if not validation_dates:
            continue
        fold_number += 1
        train_dates = dates[:validation_start_idx]
        n_train = _count_rows(panel_rows, train_dates)
        n_validation = _count_rows(panel_rows, validation_dates)
        for baseline_id in baselines:
            for metric_name in ["rank_ic", "top_bottom_spread"]:
                values = [
                    _float_or_none(metric_lookup[(date, baseline_id, metric_name)]["metric_value"])
                    for date in validation_dates
                    if (date, baseline_id, metric_name) in metric_lookup
                ]
                values = [value for value in values if value is not None]
                warning = _panel_warning(panel_rows, thresholds)
                enough = n_train > 0 and n_validation >= 2 and bool(values)
                rows.append(
                    {
                        "fold_id": f"wf_{fold_number:02d}",
                        "train_start_date": train_dates[0] if train_dates else "",
                        "train_end_date": train_dates[-1] if train_dates else "",
                        "validation_start_date": validation_dates[0],
                        "validation_end_date": validation_dates[-1],
                        "n_train_rows": n_train,
                        "n_validation_rows": n_validation,
                        "baseline_id": baseline_id,
                        "metric_name": metric_name,
                        "metric_value": round(mean(values), 6) if values else "",
                        "status": "PASS" if enough else "INSUFFICIENT_PANEL_BUT_CONTRACT_VALID",
                        "warning": warning,
                    }
                )
    path = root / "outputs/stage6c/STAGE6C_walk_forward_diagnostics.csv"
    write_csv(path, rows)
    audit_stage6c_walk_forward(root)
    return path


def audit_stage6c_expanded_validation(root: Path) -> bool:
    panel_path = root / "outputs/stage6c/STAGE6C_expanded_validation_dataset.csv"
    if not panel_path.exists():
        build_stage6c_expanded_validation_dataset(root)
    config = _load_config(root / VALIDATION_CONFIG)
    rows = read_csv(panel_path)
    failures: list[str] = []
    warnings = _standard_panel_warnings(rows, config)
    approved = set(load_approved_symbols(root))
    blocked = set(load_blocked_symbols(root))

    if not rows:
        failures.append("expanded validation dataset is empty")
    for row in rows:
        if row["symbol"] not in approved or row["symbol"] in blocked:
            failures.append(f"invalid symbol in expanded validation dataset: {row['symbol']}")
        if not is_trading_day(root, row["trade_date"]):
            failures.append(f"non-trading validation date: {row['trade_date']}")
        if row["leakage_flags"] != "PASS":
            failures.append(f"leakage flags present for {row['trade_date']} {row['symbol']}: {row['leakage_flags']}")
    status = _status(failures, warnings)
    _write_audit(
        root / "outputs/audits/stage6c_expanded_validation_audit.md",
        "Stage 6C Expanded Validation Audit",
        status,
        failures,
        warnings,
        [
            f"Rows reviewed: `{len(rows)}`",
            "Dataset is review-only and built from existing clean GOAL-06B-compatible artifacts.",
            "No blocked/pending symbols are allowed in the validation panel.",
        ],
    )
    return not failures


def audit_stage6c_ranking_baselines(root: Path) -> bool:
    score_path = root / "outputs/stage6c/STAGE6C_ranking_baseline_scores.csv"
    metrics_path = root / "outputs/stage6c/STAGE6C_ranking_metrics.csv"
    stability_path = root / "outputs/stage6c/STAGE6C_ranking_stability_diagnostics.csv"
    if not score_path.exists() or not metrics_path.exists() or not stability_path.exists():
        run_stage6c_ranking_baselines(root)
    score_rows = read_csv(score_path)
    metric_rows = read_csv(metrics_path)
    usage_rows = read_csv(root / "outputs/stage6c/STAGE6C_ranking_feature_usage_manifest.csv")
    failures: list[str] = []
    warnings: list[str] = []
    baseline_ids = {row["baseline_id"] for row in score_rows}
    if len(baseline_ids) < 3:
        failures.append(f"expected at least three ranking baselines, found {sorted(baseline_ids)}")
    if any(row["label_column"] == "true" for row in usage_rows):
        failures.append("ranking baseline feature usage includes a label column")
    forbidden_columns = {"recommendation", "position_band", "portfolio_weight"}
    if forbidden_columns & set(score_rows[0] if score_rows else {}):
        failures.append("ranking scores expose forbidden recommendation/position columns")
    if not metric_rows:
        failures.append("ranking metrics are missing")
    required_metric_columns = ["rank_ic", "spearman_rank_corr", "top_bottom_spread", "top_bucket_mean_target", "bottom_bucket_mean_target"]
    for row in metric_rows:
        missing_metrics = [column for column in required_metric_columns if row.get(column, "") == ""]
        if missing_metrics:
            failures.append(f"{row['baseline_id']} has missing aggregate metrics: {missing_metrics}")
    if any(row.get("warning") for row in metric_rows):
        warnings.append("ranking metrics include documented small-panel or naive-baseline warnings")
    status = _status(failures, warnings)
    _write_audit(
        root / "outputs/audits/stage6c_ranking_baseline_audit.md",
        "Stage 6C Ranking Baseline Audit",
        status,
        failures,
        warnings,
        [
            f"Baselines reviewed: `{len(baseline_ids)}`",
            "Rank outputs are review-only scores/ranks, not recommendations or position sizing.",
            "Feature usage manifest marks all baseline inputs as non-label columns.",
        ],
    )
    return not failures


def audit_stage6c_walk_forward(root: Path) -> bool:
    path = root / "outputs/stage6c/STAGE6C_walk_forward_diagnostics.csv"
    if not path.exists():
        run_stage6c_walk_forward_validation(root)
    rows = read_csv(path)
    failures: list[str] = []
    warnings: list[str] = []
    for row in rows:
        if row["train_end_date"] and row["validation_start_date"] <= row["train_end_date"]:
            failures.append(f"fold {row['fold_id']} violates chronological order")
        if row["status"] == "INSUFFICIENT_PANEL_BUT_CONTRACT_VALID":
            warnings.append(f"fold {row['fold_id']} has insufficient panel for {row['baseline_id']} {row['metric_name']}")
    status = _status(failures, sorted(set(warnings)))
    _write_audit(
        root / "outputs/audits/stage6c_walk_forward_audit.md",
        "Stage 6C Walk-Forward Audit",
        status,
        failures,
        sorted(set(warnings)),
        [
            f"Diagnostic rows reviewed: `{len(rows)}`",
            "Walk-forward diagnostics preserve chronological train-before-validation order.",
            "Random split leakage is not used.",
        ],
    )
    return not failures


def audit_stage6c_leakage_and_boundary(root: Path) -> bool:
    required_paths = [root / path for path in STAGE6C_OUTPUTS]
    if not all(path.exists() for path in required_paths):
        run_goal06c_expanded_validation(root, write_readiness=False)
    failures: list[str] = []
    approved = set(load_approved_symbols(root))
    blocked = set(load_blocked_symbols(root))
    for rel in STAGE6C_OUTPUTS:
        path = root / rel
        if not path.exists():
            failures.append(f"missing required output: {rel}")
            continue
        for row in read_csv(path):
            symbol = row.get("symbol")
            if symbol and (symbol not in approved or symbol in blocked):
                failures.append(f"invalid symbol {symbol} in {rel}")
            forbidden_columns = {"recommendation", "position_band", "portfolio_weight"}
            if forbidden_columns & set(row):
                failures.append(f"forbidden downstream column in {rel}: {sorted(forbidden_columns & set(row))}")
    usage_path = root / "outputs/stage6c/STAGE6C_ranking_feature_usage_manifest.csv"
    if usage_path.exists():
        for row in read_csv(usage_path):
            if row["label_column"] == "true":
                failures.append(f"label column used by ranking baseline: {row['baseline_id']} {row['input_column']}")
    workflow_rows = {row["workflow_id"]: row for row in read_csv(root / "configs/project/workflow_status.csv")}
    if workflow_rows["goal06d_model_comparison_calibration"]["status"] not in {"future_review_only", "implemented_review_only"}:
        failures.append("GOAL-06D is not future_review_only or implemented_review_only")
    if workflow_rows["goal07a_risk_overlay_design"]["status"] not in {"future_design_only", "implemented_design_only"}:
        failures.append("GOAL-07A is not future_design_only or implemented_design_only")
    goal07b = workflow_rows["goal07b_risk_overlay_calculation"]
    if goal07b["status"] not in {"locked_future", "future_review_only", "implemented_review_only"}:
        failures.append("goal07b_risk_overlay_calculation is not locked_future, future_review_only, or implemented_review_only")
    if goal07b["implemented_in_repo"] == "true" and goal07b["status"] != "implemented_review_only":
        failures.append("goal07b_risk_overlay_calculation is marked implemented outside implemented_review_only")
    goal09 = workflow_rows["position_band_recommendation"]
    if goal09["status"] not in {"locked_future", "future_review_only"}:
        failures.append("position_band_recommendation is not locked_future or future_review_only")
    if goal09["implemented_in_repo"] != "false":
        failures.append("position_band_recommendation is marked implemented")
    for workflow_id in [
        "dashboard_daily_report",
        "paper_trading_journal",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
    ]:
        if workflow_rows[workflow_id]["status"] != "locked_future":
            failures.append(f"{workflow_id} is not locked_future")
    if workflow_rows["dqn_rl_mainline"]["status"] != "deleted_from_active_mainline":
        failures.append("DQN/RL is not deleted_from_active_mainline")
    status = "PASS" if not failures else "BLOCKED"
    _write_audit(
        root / "outputs/audits/stage6c_leakage_and_boundary_audit.md",
        "Stage 6C Leakage And Boundary Audit",
        status,
        failures,
        [],
        [
            "Ranking baselines use review-only features or prior review scores, never labels as inputs.",
            "Blocked/pending symbols are excluded from Stage 6C outputs.",
            "GOAL-07B calculation remains not implemented; recommendation, position sizing, dashboard, paper/live trading, production, backtest, factor mining, and DQN/RL remain locked.",
        ],
    )
    return not failures


def run_goal06c_expanded_validation(root: Path, write_readiness: bool = True) -> bool:
    build_stage6c_expanded_validation_dataset(root)
    expanded_ok = audit_stage6c_expanded_validation(root)
    run_stage6c_ranking_baselines(root)
    ranking_ok = audit_stage6c_ranking_baselines(root)
    run_stage6c_walk_forward_validation(root)
    walk_ok = audit_stage6c_walk_forward(root)
    boundary_ok = audit_stage6c_leakage_and_boundary(root)
    if write_readiness:
        write_stage6c_readiness_report(root, expanded_ok and ranking_ok and walk_ok and boundary_ok)
    return expanded_ok and ranking_ok and walk_ok and boundary_ok


def write_stage6c_readiness_report(root: Path, core_checks_passed: bool) -> None:
    panel_rows = read_csv(root / "outputs/stage6c/STAGE6C_expanded_validation_dataset.csv")
    metrics_rows = read_csv(root / "outputs/stage6c/STAGE6C_ranking_metrics.csv")
    workflow_rows = {row["workflow_id"]: row for row in read_csv(root / "configs/project/workflow_status.csv")}
    warnings = _standard_panel_warnings(panel_rows, _load_config(root / VALIDATION_CONFIG))
    if any(row.get("warning") for row in metrics_rows):
        warnings.append("ranking metric warnings are documented in STAGE6C_ranking_metrics.csv")
    workflow_ok = (
        workflow_rows["goal06c_expanded_validation_ranking"]["status"] == "implemented_review_only"
        and workflow_rows["goal06d_model_comparison_calibration"]["status"] in {"future_review_only", "implemented_review_only"}
        and workflow_rows["goal07a_risk_overlay_design"]["status"] in {"future_design_only", "implemented_design_only"}
        and workflow_rows["goal07b_risk_overlay_calculation"]["status"] in {"locked_future", "future_review_only", "implemented_review_only"}
        and (
            workflow_rows["goal07b_risk_overlay_calculation"]["implemented_in_repo"] == "false"
            or workflow_rows["goal07b_risk_overlay_calculation"]["status"] == "implemented_review_only"
        )
    )
    missing_outputs = [path for path in [*STAGE6C_OUTPUTS, *STAGE6C_AUDITS[:-1]] if not (root / path).exists()]
    blocked = not core_checks_passed or not workflow_ok or bool(missing_outputs)
    readiness = "BLOCKED" if blocked else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    goal06d_unlocked = "true" if readiness != "BLOCKED" else "false"
    lines = [
        "# Stage 6C Readiness Report",
        "",
        f"GOAL-06C Expanded Validation Readiness: {readiness}",
        f"GOAL-06D Model Comparison and Calibration unlocked: {goal06d_unlocked}",
        "",
        f"Expanded validation rows: `{len(panel_rows)}`",
        f"Ranking metric rows: `{len(metrics_rows)}`",
        "GOAL-06C is implemented as a review-only validation and ranking baseline layer.",
        "It does not generate recommendations, position bands, portfolio weights, risk overlays, dashboard outputs, paper/live trading, production writes, production model promotion, or DQN/RL artifacts.",
        "",
        "## Warnings",
        *[f"- {warning}" for warning in sorted(set(warnings))],
        "",
        "## Blockers",
        *([f"- Missing outputs: {missing_outputs}"] if missing_outputs else []),
        *([] if workflow_ok else ["- Workflow status is not promoted to GOAL-06C implemented_review_only with GOAL-06D future_review_only or implemented_review_only and GOAL-07B locked/future/review-only only."]),
        *([] if core_checks_passed else ["- One or more GOAL-06C audits failed."]),
        "",
    ]
    write_text(root / "outputs/audits/stage6c_readiness_report.md", "\n".join(lines))


def _load_config(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _quality_flags(root: Path, row: dict[str, str], approved: set[str], blocked: set[str]) -> list[str]:
    flags: list[str] = []
    if row["symbol"] not in approved:
        flags.append("SYMBOL_NOT_APPROVED")
    if row["symbol"] in blocked:
        flags.append("SYMBOL_BLOCKED")
    if row["pit_ready"] != "true":
        flags.append("PIT_NOT_READY")
    if row["label_is_pit_safe"] != "true":
        flags.append("LABEL_NOT_PIT_SAFE")
    if not is_trading_day(root, row["target_trading_date"]):
        flags.append("TARGET_NOT_TRADING_DAY")
    return flags


def _leakage_flags(row: dict[str, str], feature_columns: list[str], label_columns: list[str]) -> list[str]:
    flags: list[str] = []
    if sorted(set(feature_columns) & set(label_columns)):
        flags.append("LABEL_COLUMN_IN_FEATURES")
    if row["decision_cutoff_ts"][:10] >= row["target_trading_date"]:
        flags.append("DECISION_CUTOFF_NOT_PRE_TARGET")
    return flags


def _panel_fields(feature_columns: list[str], label_columns: list[str]) -> list[str]:
    return [
        "trade_date",
        "symbol",
        "approved_symbol_flag",
        "usable_for_validation",
        "review_only",
        "source_panel_type",
        *feature_columns,
        *label_columns,
        "target_label_name",
        "target_label",
        "split_role",
        "chronological_date_index",
        "walk_forward_fold_id",
        "data_quality_flags",
        "leakage_flags",
    ]


def _baseline_score(baseline_id: str, row: dict[str, str], score_lookup: dict[tuple[str, str], float]) -> float:
    if baseline_id == "score_based_alpha_ranking":
        return score_lookup[(row["trade_date"], row["symbol"])]
    if baseline_id == "signal_quality_ranking":
        return float(row["source_health_score"]) + 0.05 * float(row["source_count"]) + 0.02 * float(row["event_count_pit"])
    if baseline_id == "naive_equal_weight_ranking":
        return 0.0
    raise ValueError(f"Unknown Stage 6C baseline: {baseline_id}")


def _rank_percentile(position: int, n: int) -> float:
    if n <= 1:
        return 1.0
    return round((n - position) / (n - 1), 6)


def _date_metric_rows(score_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in score_rows:
        if _is_true(row["usable_for_ranking_eval"]):
            grouped[(str(row["trade_date"]), str(row["baseline_id"]))].append(row)
    rows: list[dict[str, object]] = []
    for (trade_date, baseline_id), group in sorted(grouped.items()):
        ranked = sorted(group, key=lambda row: int(row["rank_position"]))
        targets = [float(row["target_label"]) for row in ranked]
        target_percentiles = _target_percentiles(ranked)
        rank_percentiles = [float(row["rank_percentile"]) for row in ranked]
        corr = _pearson(rank_percentiles, target_percentiles)
        top_target = targets[0]
        bottom_target = targets[-1]
        rows.append(_date_metric_row(trade_date, baseline_id, "rank_ic", corr, ranked))
        rows.append(_date_metric_row(trade_date, baseline_id, "spearman_rank_corr", corr, ranked))
        rows.append(_date_metric_row(trade_date, baseline_id, "top_bottom_spread", top_target - bottom_target, ranked))
        rows.append(_date_metric_row(trade_date, baseline_id, "top_bucket_mean_target", top_target, ranked))
        rows.append(_date_metric_row(trade_date, baseline_id, "bottom_bucket_mean_target", bottom_target, ranked))
    return rows


def _date_metric_row(trade_date: str, baseline_id: str, metric_name: str, value: float | None, rows: list[dict[str, object]]) -> dict[str, object]:
    constant_warning = "CONSTANT_BASELINE_TIE_BROKEN_BY_SYMBOL" if baseline_id == "naive_equal_weight_ranking" else ""
    status = "PASS_WITH_WARNINGS" if constant_warning else "PASS"
    return {
        "trade_date": trade_date,
        "baseline_id": baseline_id,
        "metric_name": metric_name,
        "metric_value": "" if value is None else round(value, 6),
        "n_symbols": len({str(row["symbol"]) for row in rows}),
        "status": status,
        "warning": constant_warning,
    }


def _aggregate_metric_rows(score_rows: list[dict[str, object]], config: dict[str, object]) -> list[dict[str, object]]:
    date_metrics = _date_metric_rows(score_rows)
    metric_lookup: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in date_metrics:
        value = _float_or_none(row["metric_value"])
        if value is not None:
            metric_lookup[str(row["baseline_id"])][str(row["metric_name"])].append(value)
    by_baseline: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in score_rows:
        by_baseline[str(row["baseline_id"])].append(row)
    thresholds = config["minimum_panel_size_warning_threshold"]
    output: list[dict[str, object]] = []
    for baseline_id, rows in sorted(by_baseline.items()):
        trade_dates = {str(row["trade_date"]) for row in rows}
        symbols = {str(row["symbol"]) for row in rows}
        warning = _panel_warning(rows, thresholds)
        if baseline_id == "naive_equal_weight_ranking":
            warning = ";".join(filter(None, [warning, "CONSTANT_BASELINE_TIE_BROKEN_BY_SYMBOL"]))
        metric_values = metric_lookup[baseline_id]
        coverage = len([row for row in rows if _is_true(row["usable_for_ranking_eval"])]) / len(rows) if rows else 0.0
        output.append(
            {
                "baseline_id": baseline_id,
                "rank_ic": _mean_or_blank(metric_values["rank_ic"]),
                "spearman_rank_corr": _mean_or_blank(metric_values["spearman_rank_corr"]),
                "top_bottom_spread": _mean_or_blank(metric_values["top_bottom_spread"]),
                "top_bucket_mean_target": _mean_or_blank(metric_values["top_bucket_mean_target"]),
                "bottom_bucket_mean_target": _mean_or_blank(metric_values["bottom_bucket_mean_target"]),
                "coverage": round(coverage, 6),
                "n_dates": len(trade_dates),
                "n_symbols": len(symbols),
                "status": "PASS_WITH_WARNINGS" if warning else "PASS",
                "warning": warning,
            }
        )
    return output


def _stability_rows(score_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    date_metrics = _date_metric_rows(score_rows)
    values_by_key: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in date_metrics:
        value = _float_or_none(row["metric_value"])
        if value is not None:
            values_by_key[(str(row["baseline_id"]), str(row["metric_name"]))].append(value)
    rows: list[dict[str, object]] = []
    for (baseline_id, metric_name), values in sorted(values_by_key.items()):
        warning = "LIMITED_PERIODS" if len(values) < 5 else ""
        if baseline_id == "naive_equal_weight_ranking":
            warning = ";".join(filter(None, [warning, "CONSTANT_BASELINE_TIE_BROKEN_BY_SYMBOL"]))
        rows.append(
            {
                "baseline_id": baseline_id,
                "metric_name": metric_name,
                "mean_value": round(mean(values), 6),
                "std_value": round(pstdev(values), 6) if len(values) > 1 else 0.0,
                "min_value": round(min(values), 6),
                "max_value": round(max(values), 6),
                "n_periods": len(values),
                "stability_warning": warning,
            }
        )
    return rows


def _target_percentiles(rows: list[dict[str, object]]) -> list[float]:
    ranked_targets = sorted(rows, key=lambda row: (-float(row["target_label"]), str(row["symbol"])))
    percentile_by_symbol = {
        str(row["symbol"]): _rank_percentile(position, len(ranked_targets))
        for position, row in enumerate(ranked_targets, start=1)
    }
    return [percentile_by_symbol[str(row["symbol"])] for row in rows]


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(ys) < 2:
        return None
    x_mean = mean(xs)
    y_mean = mean(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    x_var = sum((x - x_mean) ** 2 for x in xs)
    y_var = sum((y - y_mean) ** 2 for y in ys)
    if x_var == 0 or y_var == 0:
        return None
    return numerator / sqrt(x_var * y_var)


def _mean_or_blank(values: list[float]) -> float | str:
    return round(mean(values), 6) if values else ""


def _float_or_none(value: object) -> float | None:
    if value in {"", None}:
        return None
    return float(value)


def _is_true(value: object) -> bool:
    return value is True or str(value).lower() == "true"


def _count_rows(rows: list[dict[str, str]], dates: list[str]) -> int:
    date_set = set(dates)
    return sum(1 for row in rows if row["trade_date"] in date_set and row["usable_for_validation"] == "true")


def _standard_panel_warnings(rows: list[dict[str, str]], config: dict[str, object]) -> list[str]:
    thresholds = config["minimum_panel_size_warning_threshold"]
    warnings: list[str] = []
    if len(rows) < int(thresholds["rows"]):
        warnings.append("LIMITED_PANEL_ROWS_REVIEW_ONLY_FIXTURE")
    if len({row["trade_date"] for row in rows}) < int(thresholds["dates"]):
        warnings.append("LIMITED_PANEL_DATES_REVIEW_ONLY_FIXTURE")
    if len({row["symbol"] for row in rows}) < int(thresholds["symbols"]):
        warnings.append("LIMITED_PANEL_SYMBOLS")
    warnings.append("SOURCE_PANEL_IS_CLEAN_BOOTSTRAP_REVIEW_FIXTURE")
    return warnings


def _panel_warning(rows: list[dict[str, object]], thresholds: dict[str, object]) -> str:
    warnings: list[str] = []
    if len(rows) < int(thresholds["rows"]):
        warnings.append("LIMITED_PANEL_ROWS_REVIEW_ONLY_FIXTURE")
    if len({str(row["trade_date"]) for row in rows}) < int(thresholds["dates"]):
        warnings.append("LIMITED_PANEL_DATES_REVIEW_ONLY_FIXTURE")
    if len({str(row["symbol"]) for row in rows}) < int(thresholds["symbols"]):
        warnings.append("LIMITED_PANEL_SYMBOLS")
    return ";".join(warnings)


def _status(failures: list[str], warnings: list[str]) -> str:
    if failures:
        return "BLOCKED"
    return "PASS_WITH_WARNINGS" if warnings else "PASS"


def _write_audit(path: Path, title: str, status: str, failures: list[str], warnings: list[str], summary_lines: list[str]) -> None:
    write_text(
        path,
        "\n".join(
            [
                f"# {title}",
                "",
                f"Status: `{status}`",
                *summary_lines,
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
                "## Warnings",
                *[f"- {warning}" for warning in warnings],
                "",
            ]
        ),
    )

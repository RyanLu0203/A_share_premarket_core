from __future__ import annotations

import csv
from pathlib import Path

from ashare_premarket.validation.stage6c import audit_stage6c_ranking_baselines, run_stage6c_ranking_baselines


ROOT = Path(__file__).resolve().parents[1]


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_goal06c_ranking_baselines_are_review_only_and_metric_complete() -> None:
    run_stage6c_ranking_baselines(ROOT)
    assert audit_stage6c_ranking_baselines(ROOT)
    scores = _rows("outputs/stage6c/STAGE6C_ranking_baseline_scores.csv")
    metrics = _rows("outputs/stage6c/STAGE6C_ranking_metrics.csv")
    assert {row["baseline_id"] for row in scores} == {
        "score_based_alpha_ranking",
        "signal_quality_ranking",
        "naive_equal_weight_ranking",
    }
    assert {"trade_date", "symbol", "baseline_id", "rank_score", "rank_position", "rank_percentile", "target_label", "usable_for_ranking_eval", "notes"} <= set(scores[0])
    assert all(row["usable_for_ranking_eval"] == "true" for row in scores)
    assert all(row["coverage"] == "1.0" for row in metrics)
    for row in metrics:
        for column in ["rank_ic", "spearman_rank_corr", "top_bottom_spread", "top_bucket_mean_target", "bottom_bucket_mean_target"]:
            assert row[column] != ""


def test_goal06c_ranking_inputs_do_not_use_labels() -> None:
    run_stage6c_ranking_baselines(ROOT)
    usage = _rows("outputs/stage6c/STAGE6C_ranking_feature_usage_manifest.csv")
    assert usage
    assert all(row["label_column"] == "false" for row in usage)
    label_names = {"stock_return_1d", "benchmark_return_1d", "alpha_return_1d", "label_positive"}
    assert not label_names & {row["input_column"] for row in usage}
    forbidden_columns = {"recommendation", "position_band", "portfolio_weight"}
    scores = _rows("outputs/stage6c/STAGE6C_ranking_baseline_scores.csv")
    assert not forbidden_columns & set(scores[0])

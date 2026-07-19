from __future__ import annotations

import copy
from datetime import date, timedelta
from pathlib import Path

from ashare_premarket.alpha_validation.config import load_goal12_config
from ashare_premarket.alpha_validation.data import HistoricalBundle
from ashare_premarket.alpha_validation.pipeline import run_validation_from_bundle
from ashare_premarket.alpha_validation.decisions import ALLOWED_RESEARCH_STATUSES
from ashare_premarket.quant_foundation.contracts import (
    FORBIDDEN_ACTION_FIELDS,
    GovernedSnapshot,
    canonical_checksum,
)
from ashare_premarket.quant_foundation.features import FEATURE_COLUMNS, load_feature_config

ROOT = Path(__file__).resolve().parents[2]


def _bundle() -> HistoricalBundle:
    calendar = tuple(
        (date(2025, 1, 1) + timedelta(days=index)).isoformat()
        for index in range(100)
    )
    symbols = ("000001.SZ", "000002.SZ", "000003.SZ", "600000.SH", "600036.SH")
    rows = []
    for date_index, trade_date in enumerate(calendar):
        for symbol_index, symbol in enumerate(symbols):
            rows.append(
                {
                    "date": trade_date,
                    "available_at": trade_date,
                    "symbol": symbol,
                    "close": 20.0 + symbol_index * 2 + date_index * (0.02 + symbol_index * 0.001),
                    "index_close": 4000.0 + date_index,
                }
            )
    snapshot = GovernedSnapshot.from_rows(
        snapshot_id="goal12-pipeline-fixture",
        cutoff_date=calendar[-1],
        generation_timestamp="2025-04-11T16:00:00+08:00",
        code_commit="a" * 40,
        source_checksum="b" * 64,
        adjustment="qfq",
        rows=rows,
    )
    availability = {
        trade_date: calendar[index + 1] if index + 1 < len(calendar) else None
        for index, trade_date in enumerate(calendar)
    }
    return HistoricalBundle(
        snapshot,
        calendar,
        availability,
        {
            "daily_row_count": len(rows),
            "calendar_date_count": len(calendar),
            "symbol_count": len(symbols),
            "provider": "fixture",
            "amount_semantics": "UNAVAILABLE_NULL_NOT_ZERO",
            "source_fields_available": ("close", "index_close"),
            "survivorship_risk_disclosed": True,
        },
    )


def _config() -> dict[str, object]:
    config = copy.deepcopy(load_goal12_config(ROOT))
    config["splits"].update(
        {
            "minimum_training_dates": 20,
            "validation_dates": 10,
            "test_dates": 10,
            "final_holdout_dates": 20,
        }
    )
    config["metrics"].update({"minimum_cross_section": 3, "top_k": 2})
    config["inference"].update(
        {
            "date_bootstrap_repetitions": 10,
            "sign_flip_repetitions": 10,
            "within_date_shuffle_repetitions": 10,
            "random_rank_repetitions": 10,
        }
    )
    config["robustness"].update(
        {
            "minimum_history_dates": 60,
            "minimum_observation_fraction": 0.5,
            "recent_exclusion_dates": 20,
            "rolling_window_dates": 20,
            "rolling_window_step": 10,
        }
    )
    config["decision_policy"].update(
        {
            "minimum_valid_dates": 20,
            "minimum_observation_rows": 50,
            "minimum_median_breadth": 3,
            "maximum_missing_rate": 0.8,
            "maximum_zero_variance_rate": 0.5,
            "maximum_symbol_concentration": 0.3,
            "maximum_date_concentration": 0.1,
        }
    )
    return config


def test_integrated_pipeline_is_deterministic_complete_and_non_actionable() -> None:
    first = run_validation_from_bundle(
        _bundle(), load_feature_config(ROOT), _config()
    )
    second = run_validation_from_bundle(
        _bundle(), load_feature_config(ROOT), _config()
    )

    assert first == second
    assert first["status"] == "COMPLETE_RESEARCH_ONLY"
    assert first["code_commit"] == "a" * 40
    assert first["production_ready"] is False
    assert first["ready_factor_count"] == 0
    assert first["production_model_promoted"] is False
    assert len(first["feature_rows"]) == 500
    assert len(first["label_rows"]) == 1500
    assert len(first["decisions"]) == len(FEATURE_COLUMNS) + 3
    required_decision_fields = {
        "candidate_id",
        "feature_or_model_version",
        "horizon",
        "research_status",
        "production_ready",
        "evidence_summary",
        "warning_codes",
        "sample_counts",
        "metric_summary",
        "null_comparison",
        "stability_summary",
        "provenance",
        "checksum",
    }
    assert all(required_decision_fields <= row.keys() for row in first["decisions"])
    assert all(row["horizon"] == 5 for row in first["decisions"])
    assert all(row["research_status"] == row["status"] for row in first["decisions"])
    assert all(
        row["provenance"]["code_commit"] == "a" * 40
        for row in first["decisions"]
    )
    assert {row["candidate_id"] for row in first["decisions"]} == set(FEATURE_COLUMNS) | {
        "interpretable_alpha",
        "risk_adjusted_alpha",
        "fixed_linear_ranker",
    }
    assert all(row["status"] in ALLOWED_RESEARCH_STATUSES for row in first["decisions"])
    assert first["fdr_results"]["method"] == "BENJAMINI_HOCHBERG"
    assert first["splits"]["random_date_split_used"] is False
    audit = first["data_audit"]
    assert audit["eligible_feature_date_start"] == "2025-01-01"
    assert audit["eligible_feature_date_end"] == "2025-03-21"
    assert audit["eligible_symbol_breadth"] == {
        "minimum": 5,
        "median": 5.0,
        "maximum": 5,
        "distribution": {"5": 80},
    }
    assert audit["label_counts_by_horizon"]["20"] == {
        "available": 400,
        "missing": 100,
        "available_feature_date_start": "2025-01-01",
        "available_feature_date_end": "2025-03-21",
        "realizable_label_date_start": "2025-01-21",
        "realizable_label_date_end": "2025-04-10",
        "missing_reason_counts": {"EXACT_CALENDAR_HORIZON_UNAVAILABLE": 100},
    }
    primary_return = next(
        row
        for row in first["single_factor_results"]
        if row["candidate_id"] == "return_1d" and row["horizon_trading_days"] == 5
    )
    assert primary_return["full"]["by_date"][-1]["date"] == (
        first["splits"]["final_holdout"]["dates"][-1]
    )
    assert all(
        row["production_ready"] is False for row in first["decisions"]
    )
    combined = {row["candidate_id"]: row for row in first["decisions"]}
    assert combined["interpretable_alpha"]["status"] == "research_insufficient_data"
    assert combined["interpretable_alpha"]["evidence"]["eligibility_reason"] == (
        "STRUCTURALLY_MISSING_ALPHA_FEATURE:ABNORMAL_VOLUME_20D"
    )
    assert combined["fixed_linear_ranker"]["status"] == "research_insufficient_data"
    assert combined["abnormal_volume_20d"]["evidence"]["eligibility_reason"] == (
        "STRUCTURALLY_MISSING_FEATURE:ABNORMAL_VOLUME_20D"
    )
    assert first["checksum"] == canonical_checksum(
        {key: value for key, value in first.items() if key != "checksum"}
    )

    def keys(value: object) -> set[str]:
        if isinstance(value, dict):
            return set(map(str, value)) | set().union(*(keys(item) for item in value.values()))
        if isinstance(value, (list, tuple)):
            return set().union(*(keys(item) for item in value)) if value else set()
        return set()

    assert not (FORBIDDEN_ACTION_FIELDS & {key.lower() for key in keys(first)})

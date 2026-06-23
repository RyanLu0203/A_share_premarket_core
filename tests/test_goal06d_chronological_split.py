from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from ashare_premarket.models.goal06d import build_chronological_splits, build_walk_forward_splits, forbidden_split_requested, validate_split_policy

ROOT = Path(__file__).resolve().parents[1]


def _split_config() -> dict[str, object]:
    return json.loads((ROOT / "configs/models/goal06d_split_config.yaml").read_text(encoding="utf-8"))


def _rows(day_count: int = 30) -> list[dict[str, str]]:
    start = date(2024, 1, 1)
    rows: list[dict[str, str]] = []
    for offset in range(day_count):
        trade_date = (start + timedelta(days=offset)).isoformat()
        for symbol in ["000001.SZ", "000002.SZ", "000003.SZ"]:
            rows.append({"trade_date": trade_date, "symbol": symbol})
    return rows


def test_goal06d_random_splits_are_configured_as_forbidden() -> None:
    split_config = _split_config()

    assert forbidden_split_requested("random_row_split", split_config)
    assert forbidden_split_requested("random_shuffle_split", split_config)
    assert "chronological_train_validation_test" in split_config["allowed_split_methods"]
    assert "walk_forward_validation" in split_config["allowed_split_methods"]
    assert "time_blocked_cross_validation" in split_config["allowed_split_methods"]


def test_goal06d_chronological_split_preserves_time_order() -> None:
    rows = _rows()
    split_config = _split_config()

    audit = validate_split_policy(ROOT, rows, split_config)
    splits = build_chronological_splits(rows, split_config)
    folds = build_walk_forward_splits(rows, split_config)

    assert audit["status"] == "PASS"
    assert max(splits["train"]["dates"]) < min(splits["validation"]["dates"])
    assert max(splits["validation"]["dates"]) < min(splits["test"]["dates"])
    assert len(folds) >= split_config["walk_forward_validation"]["minimum_folds"]
    assert all(max(fold["train_dates"]) < min(fold["test_dates"]) for fold in folds)

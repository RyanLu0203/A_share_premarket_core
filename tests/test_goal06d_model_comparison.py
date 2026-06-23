from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_goal06d_model_comparison_outputs_are_review_only() -> None:
    rows = _rows("outputs/models/goal06d/model_comparison_summary.csv")

    assert {row["model_name"] for row in rows} == {
        "score_based_alpha_ranking",
        "ridge_regression",
        "linear_regression",
        "logistic_direction_classifier",
    }
    assert {row["target"] for row in rows} == {"excess_fwd_3d_return"}
    assert all(row["review_only"] == "true" for row in rows)
    assert any(row["selection_label"].startswith("review_only_selected_baseline") for row in rows)


def test_goal06d_model_comparison_does_not_emit_recommendation_or_position_fields() -> None:
    rows = _rows("outputs/models/goal06d/model_comparison_summary.csv")
    forbidden_columns = {
        "recommendation",
        "buy_sell_hold",
        "position",
        "position_band",
        "portfolio_weight",
        "risk_overlay",
        "production_model",
    }

    assert rows
    assert not forbidden_columns & set(rows[0])
    rationale = (ROOT / "outputs/models/goal06d/model_selection_rationale.md").read_text(encoding="utf-8")
    assert "not a production model" in rationale
    assert "trading model" in rationale
    assert "recommendation model" in rationale

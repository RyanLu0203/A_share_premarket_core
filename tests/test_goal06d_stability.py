from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_goal06d_stability_covers_required_dimensions() -> None:
    rows = _rows("outputs/models/goal06d/stability_summary.csv")
    diagnostics = {row["diagnostic"] for row in rows}

    assert diagnostics == {
        "fold_to_fold_drift",
        "symbol_concentration_risk",
        "feature_sign_instability",
        "target_horizon_sensitivity",
        "provider_source_concentration",
    }
    assert all(row["status"] in {"PASS", "PASS_WITH_WARNINGS"} for row in rows)


def test_goal06d_fold_symbol_and_feature_stability_outputs_exist() -> None:
    fold_rows = _rows("outputs/models/goal06d/fold_metrics.csv")
    symbol_rows = _rows("outputs/models/goal06d/symbol_stability_summary.csv")
    feature_rows = _rows("outputs/models/goal06d/feature_stability_summary.csv")

    assert len(fold_rows) >= 12
    assert len(symbol_rows) >= 50
    assert feature_rows
    assert all(row["review_only"] == "true" for row in fold_rows)
    assert {"market_trend_5d", "source_count"} <= {row["feature"] for row in feature_rows}

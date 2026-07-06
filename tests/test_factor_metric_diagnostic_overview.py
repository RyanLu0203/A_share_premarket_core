from __future__ import annotations

import csv
from pathlib import Path

from ashare_premarket.research.factor_diagnostic_overview import (
    OUTPUT_FIELDS,
    OUTPUT_PATH,
    build_factor_diagnostic_overview,
)

ROOT = Path(__file__).resolve().parents[1]


def _rows() -> list[dict[str, str]]:
    with (ROOT / OUTPUT_PATH).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_diagnostic_overview_builds_over_quant04_outputs() -> None:
    path = build_factor_diagnostic_overview(ROOT)
    assert path.exists()
    rows = _rows()
    assert rows, "expected at least one diagnostic row"
    assert list(rows[0].keys()) == OUTPUT_FIELDS


def test_diagnostic_overview_assigns_no_actionable_or_ready_classification() -> None:
    build_factor_diagnostic_overview(ROOT)
    rows = _rows()
    # It must never fabricate a "ready" classification or promote a factor.
    for row in rows:
        assert row["overall_factor_status"] in {"conditionally_useful", "not_ready", "informative_only", "review_only"}
        assert row["candidate_for_rec_tiering"] == "false"
        assert row["relative_diagnostic_band"] in {"upper_third", "middle_third", "lower_third", "single_group"}
        assert "not_a_signal" in row["non_actionable_disclaimer"]
    # No actionable / signal / order columns leaked into the schema.
    header = " ".join(OUTPUT_FIELDS).lower()
    for forbidden in ("buy", "sell", "hold", "signal", "order", "position", "target_price", "portfolio"):
        assert forbidden not in header


def test_diagnostic_overview_does_not_touch_governance_state() -> None:
    build_factor_diagnostic_overview(ROOT)
    # No premarket signal / recommendation artifact is created.
    assert not (ROOT / "outputs/premarket_signal_v0_5.csv").exists()
    assert not (ROOT / "outputs/premarket_signal_v1.csv").exists()
    # RecTiering stays locked and no ready factor is introduced.
    with (ROOT / "configs/project/workflow_status.csv").open(newline="", encoding="utf-8") as handle:
        workflow = {r["workflow_id"]: r for r in csv.DictReader(handle)}
    rec = workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]
    assert rec["status"] == "locked_future"
    assert rec["implemented_in_repo"] == "false"

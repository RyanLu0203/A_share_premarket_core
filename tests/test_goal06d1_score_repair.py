from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


FORBIDDEN_SCORE_FIELDS = {
    "fwd_1d_return",
    "fwd_3d_return",
    "fwd_5d_return",
    "benchmark_fwd_1d_return",
    "benchmark_fwd_3d_return",
    "benchmark_fwd_5d_return",
    "excess_fwd_1d_return",
    "excess_fwd_3d_return",
    "excess_fwd_5d_return",
    "recommendation",
    "position",
    "risk_overlay_score",
}


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_goal06d1_score_variants_are_review_only_and_no_forbidden_fields() -> None:
    rows = _rows("outputs/models/goal06d1/score_variant_comparison.csv")
    variants = {row["score_variant"] for row in rows}
    assert variants == {
        "raw_score_based_alpha_ranking",
        "zscore_cross_sectional_score",
        "rank_normalized_score",
        "winsorized_rank_score",
        "volatility_adjusted_rank_score",
        "market_regime_adjusted_rank_score_review_only",
    }
    assert all(row["review_only"] == "true" for row in rows)
    for row in rows:
        assert not (FORBIDDEN_SCORE_FIELDS & set(row))
    audit = (ROOT / "outputs/audits/goal06d1_score_repair_audit.md").read_text(encoding="utf-8")
    assert "Labels entered score construction: `false`" in audit
    assert "Forward returns entered score construction: `false`" in audit
    assert "Risk overlay or position sizing generated: `false`" in audit

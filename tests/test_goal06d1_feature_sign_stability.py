from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_goal06d1_feature_sign_repair_does_not_alter_canonical_panel() -> None:
    with (ROOT / "outputs/models/goal06d1/feature_sign_stability_repair.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert {"feature_name", "recommended_action", "sign_stability_ratio"} <= set(rows[0])
    assert {row["recommended_action"] for row in rows} <= {
        "keep_for_review_only",
        "keep_but_monitor",
        "neutralize_in_score_variant",
        "drop_from_score_variant",
        "requires_v2_factor_research",
    }
    audit = (ROOT / "outputs/audits/goal06d1_feature_sign_stability_audit.md").read_text(encoding="utf-8")
    assert "Canonical PIT panel altered: `false`" in audit
    assert "limited to GOAL-06D.1 review-only score variants" in audit

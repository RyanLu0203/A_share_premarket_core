from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.research.goal_factor_failure_attribution01 import (
    MANIFEST, OUTPUTS, audit_goal_factor_failure_attribution01,
    run_goal_factor_failure_attribution01,
)

ROOT = Path(__file__).resolve().parents[1]


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_failure_attribution_is_bounded_deterministic_and_non_promoting() -> None:
    assert run_goal_factor_failure_attribution01(ROOT)
    first = (ROOT / MANIFEST).read_bytes()
    assert run_goal_factor_failure_attribution01(ROOT)
    assert (ROOT / MANIFEST).read_bytes() == first
    assert audit_goal_factor_failure_attribution01(ROOT)
    manifest = json.loads(first)
    assert manifest["candidate_count"] == 120
    assert manifest["ready_factor_count_after"] == 0
    assert manifest["family_count"] >= 4
    assert manifest["effective_symbol_count"] == 41
    assert manifest["effective_date_count"] == 843
    assert manifest["downstream_locks_preserved"] is True
    for key in ("new_factors_constructed", "thresholds_changed", "provider_calls_performed", "goal10d_unlocked", "rec_tiering_unlocked"):
        assert manifest[key] is False
    assert len(_rows(OUTPUTS["matrix"])) == 120
    assert len(_rows(OUTPUTS["criteria"])) == 7
    assert all(r["promotion_allowed"] == "false" for r in _rows(OUTPUTS["families"]))

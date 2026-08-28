from __future__ import annotations
import csv, json
from pathlib import Path
from ashare_premarket.research.goal_alpha_hypothesis_redesign01 import MANIFEST, OUTPUTS, run_goal_alpha_hypothesis_redesign01
ROOT = Path(__file__).resolve().parents[1]
def _rows(path: str):
    with (ROOT/path).open(encoding="utf-8", newline="") as f: return list(csv.DictReader(f))
def test_design_only_hypothesis_reset_is_deterministic_and_locked():
    assert run_goal_alpha_hypothesis_redesign01(ROOT)
    first=(ROOT/MANIFEST).read_bytes()
    assert run_goal_alpha_hypothesis_redesign01(ROOT)
    assert (ROOT/MANIFEST).read_bytes()==first
    m=json.loads(first)
    assert m["frozen_family_count"]==5 and m["frozen_candidate_count"]==120
    assert m["hypothesis_count"]==4 and m["evidence_ready_hypothesis_count"]==0
    assert m["preferred_hypothesis_id"]=="HYP-LIQUIDITY-SHOCK-01"
    for k in ("factor_values_created","thresholds_changed","provider_calls_performed","v2_factor_mining_unlocked","rec_tiering_unlocked"): assert m[k] is False
    assert all(r["status"]=="design_only_evidence_not_ready" for r in _rows(OUTPUTS["registry"]))
    assert all(r["construction_allowed"]=="false" for r in _rows(OUTPUTS["experiments"]))

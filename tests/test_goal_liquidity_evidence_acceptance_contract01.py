import csv,json
from pathlib import Path
from ashare_premarket.research.goal_liquidity_evidence_acceptance_contract01 import MANIFEST,EVALUATION,SCHEMA,run_goal_liquidity_evidence_acceptance_contract01
ROOT=Path(__file__).resolve().parents[1]
def rows(p):
 with (ROOT/p).open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f))
def test_contract_passes_while_current_evidence_fails_closed():
 assert run_goal_liquidity_evidence_acceptance_contract01(ROOT)
 first=(ROOT/MANIFEST).read_bytes();assert run_goal_liquidity_evidence_acceptance_contract01(ROOT);assert first==(ROOT/MANIFEST).read_bytes()
 m=json.loads(first);assert m["goal_status"]=="PASS" and m["current_evidence_status"]=="NOT_READY" and m["accepted_row_count"]==0
 assert m["current_symbol_count"]==41 and m["required_symbol_count"]==100
 assert not m["provider_calls_authorized"] and not m["factor_construction_allowed"]
 assert all(r["status"]=="NOT_READY" for r in rows(EVALUATION))
 assert all(r["silent_imputation_allowed"]=="false" for r in rows(SCHEMA))

import json
from pathlib import Path
import pytest
from ashare_premarket.providers.liquidity_evidence_foundation import MANIFEST,normalize_complete_row,preflight,run_foundation,validate_atomic_bundle
ROOT=Path(__file__).resolve().parents[1]
def sample(symbol="000001.SZ",day="2026-08-01"):
 return {"symbol":symbol,"trade_date":day,"volume":1000,"turnover_rate":0.02,"free_float_shares":1000000,"trade_status":"trading","source_provider":"p1;p2","available_at":"2026-08-01T15:01:00+08:00","adjustment":"qfq","snapshot_id":"s1"}
def test_default_off_preflight_and_foundation_are_blocked_without_calls():
 p=preflight(["000001.SZ"],{"tencent":"verified","baostock":"contract_only_not_live_verified"},False,{})
 assert p.status=="BLOCKED" and "NETWORK_GATE_DISABLED" in p.reasons and "SYMBOL_SCOPE_NOT_EXACT_100" in p.reasons
 assert run_foundation(ROOT);m=json.loads((ROOT/MANIFEST).read_text());assert m["goal_status"]=="PASS" and m["acquisition_preflight_status"]=="BLOCKED" and not m["data_calls_performed"] and m["accepted_rows"]==0
def test_normalizer_and_atomic_bundle_fail_closed():
 assert normalize_complete_row(sample())["volume"]=="1000.00000000"
 with pytest.raises(ValueError,match="REQUIRED_FIELD_MISSING"):normalize_complete_row({"symbol":"000001.SZ"})
 with pytest.raises(ValueError,match="PARTIAL_BATCH"):validate_atomic_bundle([sample()],["000001.SZ","000002.SZ"],["2026-08-01"])
 rows=validate_atomic_bundle([sample("000001.SZ"),sample("000002.SZ")],["000001.SZ","000002.SZ"],["2026-08-01"]);assert len(rows)==2

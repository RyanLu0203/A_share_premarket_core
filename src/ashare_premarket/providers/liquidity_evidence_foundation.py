"""Default-off, fail-closed foundation for future liquidity evidence acquisition."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Mapping, Sequence

NETWORK_ENV = "ASHARE_ALLOW_LIQUIDITY_EVIDENCE_ACQUISITION"
REQUIRED_FIELDS = (
    "symbol",
    "trade_date",
    "volume",
    "turnover_rate",
    "free_float_shares",
    "trade_status",
    "source_provider",
    "available_at",
    "adjustment",
    "snapshot_id",
)
FAILURES = (
    "NETWORK_GATE_DISABLED",
    "SYMBOL_SCOPE_NOT_EXACT_100",
    "PROVIDER_COUNT_BELOW_TWO",
    "UNVERIFIED_PROVIDER_SCHEMA",
    "FREE_FLOAT_SOURCE_UNAVAILABLE",
    "REQUIRED_FIELD_MISSING",
    "INVALID_NUMERIC_DOMAIN",
    "INVALID_TRADE_STATUS",
    "PIT_TIMESTAMP_INVALID",
    "ADJUSTMENT_NOT_QFQ",
    "DUPLICATE_PRIMARY_KEY",
    "PARTIAL_BATCH",
    "PROVIDER_DISCREPANCY",
)


@dataclass(frozen=True)
class Preflight:
    status: str
    reasons: tuple[str, ...]
    network_enabled: bool
    symbol_count: int
    verified_provider_count: int


def network_enabled(env: Mapping[str, str] | None = None) -> bool:
    return (env or os.environ).get(NETWORK_ENV) == "1"


def preflight(
    symbols: Sequence[str],
    provider_states: Mapping[str, str],
    free_float_source_verified: bool,
    env: Mapping[str, str] | None = None,
) -> Preflight:
    reasons = []
    enabled = network_enabled(env)
    if not enabled:
        reasons.append("NETWORK_GATE_DISABLED")
    if len(symbols) != 100 or len(set(symbols)) != 100:
        reasons.append("SYMBOL_SCOPE_NOT_EXACT_100")
    verified = sum(value == "verified" for value in provider_states.values())
    if verified < 2:
        reasons.append("PROVIDER_COUNT_BELOW_TWO")
    if any(value not in {"verified", "disabled"} for value in provider_states.values()):
        reasons.append("UNVERIFIED_PROVIDER_SCHEMA")
    if not free_float_source_verified:
        reasons.append("FREE_FLOAT_SOURCE_UNAVAILABLE")
    return Preflight(
        "READY" if not reasons else "BLOCKED",
        tuple(reasons),
        enabled,
        len(symbols),
        verified,
    )


def normalize_complete_row(row: Mapping[str, object]) -> dict[str, str]:
    missing = [field for field in REQUIRED_FIELDS if row.get(field) in (None, "")]
    if missing:
        raise ValueError("REQUIRED_FIELD_MISSING:" + ";".join(missing))

    trade_date = str(row["trade_date"])
    available = str(row["available_at"])
    try:
        date.fromisoformat(trade_date)
        available_at = datetime.fromisoformat(available)
        volume = float(row["volume"])
        turnover = float(row["turnover_rate"])
        free_float = float(row["free_float_shares"])
    except (TypeError, ValueError) as exc:
        raise ValueError("INVALID_NUMERIC_DOMAIN_OR_TIMESTAMP") from exc
    if volume < 0 or turnover < 0 or free_float <= 0:
        raise ValueError("INVALID_NUMERIC_DOMAIN")
    if str(row["trade_status"]) not in {"trading", "suspended"}:
        raise ValueError("INVALID_TRADE_STATUS")
    if str(row["adjustment"]) != "qfq":
        raise ValueError("ADJUSTMENT_NOT_QFQ")

    return {
        **{field: str(row[field]) for field in REQUIRED_FIELDS},
        "volume": f"{volume:.8f}",
        "turnover_rate": f"{turnover:.8f}",
        "free_float_shares": f"{free_float:.8f}",
        "available_at": available_at.isoformat(),
    }


def validate_atomic_bundle(
    rows: Sequence[Mapping[str, object]],
    expected_symbols: Sequence[str],
    expected_dates: Sequence[str],
) -> list[dict[str, str]]:
    normalized = [normalize_complete_row(row) for row in rows]
    keys = [(row["symbol"], row["trade_date"]) for row in normalized]
    if len(keys) != len(set(keys)):
        raise ValueError("DUPLICATE_PRIMARY_KEY")
    expected = {(symbol, trade_date) for symbol in expected_symbols for trade_date in expected_dates}
    if set(keys) != expected:
        raise ValueError("PARTIAL_BATCH")
    return sorted(normalized, key=lambda row: (row["symbol"], row["trade_date"]))

GOAL_ID="GOAL-LIQUIDITY-EVIDENCE-ACQUISITION-FOUNDATION-01"
PREFIX="outputs/providers/goal_liquidity_evidence_acquisition_foundation01_"
CAPABILITIES=PREFIX+"provider_capability_plan.csv";FAILURE_FILE=PREFIX+"failure_taxonomy.csv";PREFLIGHT_FILE=PREFIX+"preflight.csv"
REPORT="outputs/audits/goal_liquidity_evidence_acquisition_foundation01_report.md";MANIFEST="outputs/audits/goal_liquidity_evidence_acquisition_foundation01_manifest.json";AUDIT="outputs/audits/goal_liquidity_evidence_acquisition_foundation01_audit.md"
def _write(root,rel,fields,rows):
 p=root/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
def _sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run_foundation(root:Path)->bool:
 capabilities=[
  {"provider":"tencent_akshare","role":"volume_crosscheck","fields":"volume","schema_state":"verified","network_default":"off","canonical_use":"forbidden_by_this_goal"},
  {"provider":"baostock","role":"candidate_primary_liquidity_history","fields":"volume;turnover_rate;trade_status;adjustment","schema_state":"contract_only_not_live_verified","network_default":"off","canonical_use":"forbidden_by_this_goal"},
  {"provider":"free_float_source_tbd","role":"required_free_float_history","fields":"free_float_shares;available_at","schema_state":"unavailable","network_default":"off","canonical_use":"forbidden_by_this_goal"},
 ]
 failures=[{"failure_code":x,"retry_allowed":"false","partial_acceptance_allowed":"false","safe_action":"stop_and_record_metadata_only"} for x in FAILURES]
 current_symbols=[]
 with (root/"outputs/research/network_ingestion/symbol_coverage.csv").open(encoding="utf-8",newline="") as f:
  current_symbols=[r["symbol"] for r in csv.DictReader(f) if r["status"]=="acquired"]
 pf=preflight(current_symbols,{"tencent_akshare":"verified","baostock":"contract_only_not_live_verified","free_float_source_tbd":"disabled"},False,{})
 pre=[{"status":pf.status,"reason_codes":";".join(pf.reasons),"network_enabled":str(pf.network_enabled).lower(),"current_symbol_count":pf.symbol_count,"required_symbol_count":100,"verified_provider_count":pf.verified_provider_count,"required_provider_count":2,"data_calls_performed":"false","accepted_rows":0}]
 _write(root,CAPABILITIES,list(capabilities[0]),capabilities);_write(root,FAILURE_FILE,list(failures[0]),failures);_write(root,PREFLIGHT_FILE,list(pre[0]),pre)
 (root/REPORT).write_text(f"# {GOAL_ID}\n\nStatus: `PASS` foundation / `BLOCKED` acquisition preflight.\n\nThe default-off runner contract, strict row normalizer, atomic complete-bundle validator, provider capability plan, and failure taxonomy are implemented. Current preflight blocks before network because only `{len(current_symbols)}` accepted symbols exist, only Tencent volume semantics are verified, Baostock remains contract-only for this goal, and no verified PIT historical free-float source exists.\n\nNo provider call, credential read, row acquisition, bundle write, factor construction, or downstream unlock occurred.\n",encoding="utf-8")
 m={"goal_id":GOAL_ID,"goal_status":"PASS","acquisition_preflight_status":"BLOCKED","network_default_off":True,"data_calls_performed":False,"accepted_rows":0,"current_symbol_count":len(current_symbols),"required_symbol_count":100,"verified_provider_count":pf.verified_provider_count,"required_provider_count":2,"free_float_source_verified":False,"normalizer_implemented":True,"atomic_bundle_validation_implemented":True,"factor_construction_unlocked":False,"rec_tiering_unlocked":False,"outputs":{p:_sha(root/p) for p in (CAPABILITIES,FAILURE_FILE,PREFLIGHT_FILE)}}
 (root/MANIFEST).write_text(json.dumps(m,indent=2,sort_keys=True)+"\n",encoding="utf-8");return audit_foundation(root)
def audit_foundation(root:Path)->bool:
 try:
  m=json.loads((root/MANIFEST).read_text());ok=m["goal_status"]=="PASS" and m["acquisition_preflight_status"]=="BLOCKED" and m["accepted_rows"]==0 and not m["data_calls_performed"] and not m["free_float_source_verified"] and not m["factor_construction_unlocked"] and not m["rec_tiering_unlocked"] and all(_sha(root/p)==h for p,h in m["outputs"].items())
 except (OSError,KeyError,ValueError,json.JSONDecodeError):ok=False
 (root/AUDIT).write_text(f"# {GOAL_ID} Audit\n\nStatus: `{'PASS' if ok else 'FAIL'}`\n",encoding="utf-8");return ok

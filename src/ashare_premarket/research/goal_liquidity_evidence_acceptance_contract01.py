"""Offline contract gate for future PIT-safe liquidity evidence."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
GOAL_ID="GOAL-LIQUIDITY-EVIDENCE-ACCEPTANCE-CONTRACT-01"
DAILY="outputs/research/network_ingestion/daily_panel.csv"
COVERAGE="outputs/research/network_ingestion/symbol_coverage.csv"
PIT="outputs/research/goal_network_evidence_ingestion01_pit_availability_contract.csv"
PREFIX="outputs/research/goal_liquidity_evidence_acceptance_contract01_"
EVALUATION=PREFIX+"current_evidence_evaluation.csv"
SCHEMA=PREFIX+"required_schema.csv"
DECISION=PREFIX+"decision.csv"
REPORT="outputs/audits/goal_liquidity_evidence_acceptance_contract01_report.md"
MANIFEST="outputs/audits/goal_liquidity_evidence_acceptance_contract01_manifest.json"
AUDIT="outputs/audits/goal_liquidity_evidence_acceptance_contract01_audit.md"
REQUIRED=(
 ("symbol","string","primary_key"),("trade_date","date","primary_key"),
 ("volume","float","shares_nonnegative"),("turnover_rate","float","fraction_nonnegative"),
 ("free_float_shares","float","shares_positive"),("trade_status","enum","explicit_not_inferred"),
 ("source_provider","string","lineage"),("available_at","timestamp","pit_required"),
 ("adjustment","enum","qfq_required"),("snapshot_id","string","immutable_lineage"),
)
def _rows(root,rel):
 with (root/rel).open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f))
def _write(root,rel,fields,rows):
 p=root/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
def _sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run_goal_liquidity_evidence_acceptance_contract01(root:Path)->bool:
 daily=_rows(root,DAILY);coverage=_rows(root,COVERAGE);pit=_rows(root,PIT)
 fields=set(daily[0]); acquired=sum(r["status"]=="acquired" for r in coverage)
 providers=sorted({r["source_provider"] for r in daily})
 accepted_fields={"volume","turnover_rate","free_float_shares","trade_status","available_at","adjustment","snapshot_id"}
 evaluation=[]
 checks=[
  ("symbol_breadth",acquired,100,acquired>=100),
  ("independent_provider_count",len(providers),2,len(providers)>=2),
  ("required_liquidity_fields",len(fields & accepted_fields),len(accepted_fields),accepted_fields<=fields),
  ("pit_availability_contract",sum(r["feature_family"]=="liquidity_evidence" for r in pit),1,any(r["feature_family"]=="liquidity_evidence" for r in pit)),
 ]
 for check,current,required,ok in checks:evaluation.append({"check_id":check,"current":current,"required":required,"status":"PASS" if ok else "NOT_READY","blocking":str(not ok).lower()})
 schema=[{"field":f,"type":t,"rule":r,"required":"true","silent_imputation_allowed":"false"} for f,t,r in REQUIRED]
 decision=[{"acceptance_status":"NOT_READY","accepted_row_count":0,"canonical_projection_allowed":"false","factor_construction_allowed":"false","provider_calls_authorized":"false","next_action":"explicit_bounded_evidence_acquisition_goal_required"}]
 _write(root,EVALUATION,list(evaluation[0]),evaluation);_write(root,SCHEMA,list(schema[0]),schema);_write(root,DECISION,list(decision[0]),decision)
 (root/REPORT).write_text(f"# {GOAL_ID}\n\nStatus: `PASS` contract / `NOT_READY` current evidence.\n\nCurrent evidence has `{acquired}` acquired symbols and providers `{';'.join(providers)}`. The committed daily panel lacks accepted volume, turnover rate, free-float shares, trade status, availability, adjustment, and snapshot fields required by this contract. Zero rows are accepted and factor construction remains blocked.\n\nNo network, provider call, credential read, data acquisition, factor construction, threshold search, or downstream unlock occurred.\n",encoding="utf-8")
 m={"goal_id":GOAL_ID,"goal_status":"PASS","current_evidence_status":"NOT_READY","current_symbol_count":acquired,"required_symbol_count":100,"current_provider_count":len(providers),"required_provider_count":2,"accepted_row_count":0,"factor_construction_allowed":False,"provider_calls_performed":False,"provider_calls_authorized":False,"rec_tiering_unlocked":False,"v2_factor_mining_unlocked":False,"inputs":{r:_sha(root/r) for r in (DAILY,COVERAGE,PIT)},"outputs":{r:_sha(root/r) for r in (EVALUATION,SCHEMA,DECISION)}}
 (root/MANIFEST).write_text(json.dumps(m,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 return audit_goal_liquidity_evidence_acceptance_contract01(root)
def audit_goal_liquidity_evidence_acceptance_contract01(root:Path)->bool:
 try:
  m=json.loads((root/MANIFEST).read_text());ok=m["goal_status"]=="PASS" and m["current_evidence_status"]=="NOT_READY" and m["accepted_row_count"]==0 and not any(m[k] for k in ("factor_construction_allowed","provider_calls_performed","provider_calls_authorized","rec_tiering_unlocked","v2_factor_mining_unlocked")) and all(_sha(root/p)==h for p,h in m["outputs"].items())
 except (OSError,KeyError,ValueError,json.JSONDecodeError):ok=False
 (root/AUDIT).write_text(f"# {GOAL_ID} Audit\n\nStatus: `{'PASS' if ok else 'FAIL'}`\n",encoding="utf-8");return ok

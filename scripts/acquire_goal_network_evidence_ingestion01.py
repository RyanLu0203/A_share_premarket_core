"""GOAL-NETWORK-EVIDENCE-INGESTION-01 — authorized network acquisition (run once).

Fetches REAL A-share evidence via the approved, credential-free akshare provider
under the explicit user authorization gate ASHARE_ALLOW_NETWORK_INGESTION=1. It
writes only normalized, bounded research evidence + an audit trail; raw payloads
are never committed and no secrets are persisted. The gate module and all tests
replay the COMMITTED snapshot fully offline (this script is never run by pytest).

Controls: source/function allowlist, network refused unless the gate env var is
set, deterministic retry/backoff, per-source failure classification, acquisition
+ source timestamps, and a checksummed evidence bundle manifest.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "outputs/research/network_ingestion"
NETWORK_ENV = "ASHARE_ALLOW_NETWORK_INGESTION"

# Explicit allowlist of akshare functions permitted for this authorized research goal.
ALLOWLIST = {
    "akshare.stock_zh_a_daily": "credential_free_sina_backadjusted_daily_history",
    "akshare.stock_zh_index_daily": "credential_free_sina_index_daily_history",
    "akshare.stock_zh_a_spot": "credential_free_sina_universe_listing",
}
INDICES = {"sh000300": "csi300", "sh000001": "sse_composite", "sz399001": "szse_component"}
START_DATE, END_DATE = "20230101", "20260630"
SYMBOL_TARGET = 320  # attempt a materially broader universe; honest partial recorded
MAX_RETRIES = 2
TIME_BUDGET_SECONDS = 1000  # stop starting new symbol fetches after this; write what was collected


def _acq_ts() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime())


def _committed_symbols() -> list[str]:
    import glob
    syms: set[str] = set()
    for p in glob.glob(str(ROOT / "outputs/research/goal_quant_research03_refined_evaluation_panel_parts/*.csv")):
        with open(p, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                syms.add(r["symbol"])
    return sorted(syms)


def _to_sina(code_ex: str) -> str:
    code, ex = code_ex.split(".")
    return ("sh" if ex == "SH" else "sz") + code


def _from_sina(sina: str) -> str:
    return f"{sina[2:]}.{'SH' if sina[:2] == 'sh' else 'SZ'}"


def _retry(fn, *, source: str, ident: str, log: list[dict]):
    last = ""
    for attempt in range(1, MAX_RETRIES + 1):
        t0 = time.time()
        try:
            out = fn()
            log.append({"source_id": source, "identifier": ident, "status": "success",
                        "rows": len(out), "attempts": attempt, "elapsed_seconds": round(time.time() - t0, 2), "failure_class": "", "error": ""})
            return out
        except Exception as exc:  # noqa: BLE001
            last = f"{type(exc).__name__}:{str(exc)[:80]}"
            time.sleep(min(2 ** attempt, 5))
    fclass = "connection_reset" if "ConnectionError" in last or "Reset" in last else ("proxy_or_ssl" if "Proxy" in last or "SSL" in last else "other")
    log.append({"source_id": source, "identifier": ident, "status": "failed", "rows": 0,
                "attempts": MAX_RETRIES, "elapsed_seconds": 0, "failure_class": fclass, "error": last})
    return None


def main() -> int:
    if os.environ.get(NETWORK_ENV) != "1":
        print(f"REFUSED: network ingestion requires {NETWORK_ENV}=1 (authorized research context only).")
        return 2
    import akshare as ak  # imported only inside the authorized path

    BUNDLE.mkdir(parents=True, exist_ok=True)
    log: list[dict] = []
    acq_ts = _acq_ts()

    # universe: committed symbols first, then best-effort broaden via sina spot listing
    universe = _committed_symbols()
    sina_universe = [_to_sina(s) for s in universe]
    spot = _retry(lambda: ak.stock_zh_a_spot(), source="akshare.stock_zh_a_spot", ident="universe_listing", log=log)
    if spot is not None and "code" in spot.columns:
        extra = [c for c in spot["code"].astype(str).tolist() if c[:2] in ("sh", "sz") and c not in sina_universe]
        extra = sorted(extra)[: max(0, SYMBOL_TARGET - len(sina_universe))]
        sina_universe = sina_universe + extra
    sina_universe = sina_universe[:SYMBOL_TARGET]

    daily_rows: list[dict] = []
    coverage: list[dict] = []
    t_start = time.time()
    for i, sina in enumerate(sina_universe):
        if time.time() - t_start > TIME_BUDGET_SECONDS:
            print(f"TIME_BUDGET reached at symbol {i}/{len(sina_universe)}; writing collected evidence", flush=True)
            break
        if i % 25 == 0:
            ok = sum(1 for c in coverage if c["status"] == "acquired")
            print(f"progress: {i}/{len(sina_universe)} attempted, {ok} acquired, {round(time.time()-t_start)}s", flush=True)
        df = _retry(lambda s=sina: ak.stock_zh_a_daily(symbol=s, start_date=START_DATE, end_date=END_DATE, adjust="qfq"),
                    source="akshare.stock_zh_a_daily", ident=sina, log=log)
        std = _from_sina(sina)
        if df is None or len(df) == 0:
            coverage.append({"symbol": std, "sina_symbol": sina, "first_date": "", "last_date": "", "n_dates": 0, "status": "failed_or_empty"})
            continue
        recs = df.to_dict("records")
        prev = None
        for rec in recs:
            close = _f(rec.get("close"))
            date = str(rec.get("date"))[:10]
            ret = round((close / prev - 1.0), 8) if (prev and prev > 0 and close is not None) else ""
            daily_rows.append({"symbol": std, "trade_date": date, "close": close, "return_1d": ret,
                               "source_provider": "akshare_sina", "no_lookahead_status": "passed_current_or_past_only"})
            prev = close if close else prev
        coverage.append({"symbol": std, "sina_symbol": sina, "first_date": str(recs[0].get("date"))[:10],
                         "last_date": str(recs[-1].get("date"))[:10], "n_dates": len(recs), "status": "acquired"})

    index_rows: list[dict] = []
    for sym, name in INDICES.items():
        df = _retry(lambda s=sym: ak.stock_zh_index_daily(symbol=s), source="akshare.stock_zh_index_daily", ident=sym, log=log)
        if df is None:
            continue
        recs = [r for r in df.to_dict("records") if START_DATE[:4] <= str(r.get("date"))[:4]]
        prev = None
        for rec in recs:
            close = _f(rec.get("close"))
            date = str(rec.get("date"))[:10]
            ret = round((close / prev - 1.0), 8) if (prev and prev > 0 and close is not None) else ""
            index_rows.append({"index_id": sym, "index_name": name, "trade_date": date, "close": close, "return_1d": ret,
                               "source_provider": "akshare_sina", "no_lookahead_status": "passed_current_or_past_only"})
            prev = close if close else prev

    _write(BUNDLE / "daily_panel.csv", ["symbol", "trade_date", "close", "return_1d", "source_provider", "no_lookahead_status"], daily_rows)
    _write(BUNDLE / "symbol_coverage.csv", ["symbol", "sina_symbol", "first_date", "last_date", "n_dates", "status"], coverage)
    _write(BUNDLE / "index_panel.csv", ["index_id", "index_name", "trade_date", "close", "return_1d", "source_provider", "no_lookahead_status"], index_rows)
    _write(BUNDLE / "acquisition_log.csv", ["source_id", "identifier", "status", "rows", "attempts", "elapsed_seconds", "failure_class", "error"], log)

    acquired = [c for c in coverage if c["status"] == "acquired"]
    all_dates = {r["trade_date"] for r in daily_rows}
    manifest = {
        "goal": "GOAL-NETWORK-EVIDENCE-INGESTION-01", "provider": "akshare_sina",
        "acquisition_timestamp": acq_ts, "network_env_gate": f"{NETWORK_ENV}=1",
        "allowlist": ALLOWLIST, "source_snapshot_end_date": END_DATE, "source_snapshot_start_date": START_DATE,
        "symbols_acquired": len(acquired), "symbols_attempted": len(sina_universe),
        "distinct_trade_dates": len(all_dates), "daily_rows": len(daily_rows), "index_rows": len(index_rows),
        "indices_acquired": sorted({r["index_id"] for r in index_rows}),
        "raw_payloads_committed": False, "secrets_persisted": False,
        "checksums": {
            "daily_panel.csv": _sha256(BUNDLE / "daily_panel.csv"),
            "symbol_coverage.csv": _sha256(BUNDLE / "symbol_coverage.csv"),
            "index_panel.csv": _sha256(BUNDLE / "index_panel.csv"),
        },
    }
    (BUNDLE / "evidence_bundle_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ACQUIRED symbols={len(acquired)}/{len(sina_universe)} dates={len(all_dates)} daily_rows={len(daily_rows)} index_rows={len(index_rows)}")
    return 0


def _f(v):
    try:
        return round(float(v), 6)
    except (TypeError, ValueError):
        return None


def _write(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    sys.exit(main())

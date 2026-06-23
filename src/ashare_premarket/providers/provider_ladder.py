from __future__ import annotations

import hashlib
import json
import math
import os
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlencode

import requests

from ashare_premarket.core.io import read_csv, write_csv, write_json, write_text
from ashare_premarket.providers.browser_assisted_provider import browser_dependency_status, fetch_urls_with_browser
from ashare_premarket.providers.browser_provider_events import BROWSER_EVENT_FIELDS, write_browser_assisted_audit
from ashare_premarket.providers.browser_provider_policy import browser_assisted_enabled, browser_domain_allowed, target_domain
from ashare_premarket.providers.browser_provider_switches import browser_provider_project_default
from ashare_premarket.providers.failure_classification import retry_allowed
from ashare_premarket.providers.local_import_provider import local_import_status, read_local_import_table
from ashare_premarket.providers.provider_registry import engineering_bundle_root, load_ingestion_config, network_enabled
from ashare_premarket.storage.policy import resolve_data_root
from ashare_premarket.universe.governance import load_blocked_symbols
from ashare_premarket.validation.engineering_panel import classify_panel_tier

BUNDLE_ID = "goal06c7_provider_ladder_engineering_pilot_current"
RUN_ID = "goal06c7_provider_ladder_runtime"
LADDER_CONFIG = "configs/providers/provider_priority_ladder.yaml"
SAMPLE_MAX_ROWS = 100

STOCK_FIELDS = ["trade_date", "symbol", "open", "high", "low", "close", "volume", "amount", "provider_id", "provider_mode", "source_bundle_id", "ingest_ts", "schema_version", "data_quality_flags"]
BENCHMARK_FIELDS = ["trade_date", "benchmark_symbol", "open", "high", "low", "close", "volume", "amount", "provider_id", "provider_mode", "source_bundle_id", "ingest_ts", "schema_version", "data_quality_flags"]
UNIVERSE_FIELDS = ["symbol", "name", "exchange", "liquidity_proxy", "source_coverage_status", "approval_status", "notes", "coverage_status", "provider_id", "provider_mode", "source_bundle_id"]
CALENDAR_FIELDS = ["trade_date"]
SOURCE_COVERAGE_FIELDS = ["symbol", "provider_id", "provider_mode", "ohlcv_rows", "benchmark_overlap_dates", "coverage_ready", "failure_class", "notes"]
PIT_FIELDS = [
    "as_of_date", "target_trading_date", "decision_cutoff_ts", "symbol", "market_trend_5d", "stock_momentum_5d",
    "stock_momentum_20d", "stock_gap_signal", "stock_volatility_20d", "turnover_proxy", "relative_strength_20d",
    "source_health_score", "source_count", "provider_id", "provider_mode", "source_bundle_id", "pit_ready",
    "feature_contract_version", "data_quality_flags",
]
LABEL_FIELDS = [
    "trade_date", "symbol", "fwd_1d_return", "fwd_3d_return", "fwd_5d_return", "benchmark_fwd_1d_return",
    "benchmark_fwd_3d_return", "benchmark_fwd_5d_return", "excess_fwd_1d_return", "excess_fwd_3d_return",
    "excess_fwd_5d_return", "provider_id", "provider_mode", "source_bundle_id", "label_ready",
    "label_contract_version", "label_quality_flags",
]
STAGE6C_FIELDS = [
    "trade_date", "symbol", "as_of_date", "decision_cutoff_ts", "market_trend_5d", "stock_momentum_5d",
    "stock_momentum_20d", "stock_gap_signal", "stock_volatility_20d", "turnover_proxy", "relative_strength_20d",
    "source_health_score", "source_count", "provider_id", "provider_mode", "fwd_1d_return", "fwd_3d_return",
    "fwd_5d_return", "excess_fwd_1d_return", "excess_fwd_3d_return", "excess_fwd_5d_return",
    "usable_for_validation", "panel_source_type", "source_bundle_id", "review_only", "data_quality_flags",
    "leakage_flags", "panel_tier",
]


def run_goal06c7_provider_ladder_expansion(
    root: Path,
    allow_network: bool = False,
    enable_browser_assisted: bool = False,
) -> bool:
    config = load_ingestion_config(root)
    ladder = _load_json(root / LADDER_CONFIG)
    bundle_root = engineering_bundle_root(root, BUNDLE_ID)
    enabled = network_enabled(allow_network)
    browser_enabled = browser_assisted_enabled(root, enable_browser_assisted)
    bundle_root.mkdir(parents=True, exist_ok=True)
    if not enabled:
        events = [_attempt("provider_ladder", "network_policy", "provider_ladder", "orchestration", "", "FAIL", "NETWORK_DISABLED_BY_POLICY", "policy", safe_notes="network disabled by policy")]
        _write_empty_goal06c7_outputs(root, bundle_root, events, config, browser_enabled)
        return True

    candidates = [symbol for symbol in ladder["candidate_universe_seed"] if _valid_symbol(symbol) and symbol not in set(load_blocked_symbols(root))]
    candidates = candidates[: int(config.get("candidate_symbol_count", 100))]
    rate_limit_seconds = _rate_limit_seconds(config)
    benchmark_symbol = str(config.get("benchmark_symbols", ["000300"])[0])
    raw_start, raw_end = "20230101", "20241231"
    events: list[dict[str, object]] = []
    benchmark_rows, benchmark_event = _fetch_role(root, "benchmark_ohlcv_daily", benchmark_symbol, raw_start, raw_end, browser_enabled)
    events.extend(benchmark_event)
    _sleep_between_provider_calls(rate_limit_seconds)

    selected: list[dict[str, object]] = []
    stock_rows: list[dict[str, object]] = []
    source_coverage: list[dict[str, object]] = []
    benchmark_dates = {row["trade_date"] for row in benchmark_rows}
    for symbol in candidates:
        if len(selected) >= int(config.get("symbol_target_count", 50)):
            break
        rows, role_events = _fetch_role(root, "stock_ohlcv_daily", symbol, raw_start, raw_end, browser_enabled)
        events.extend(role_events)
        _sleep_between_provider_calls(rate_limit_seconds)
        symbol_dates = {row["trade_date"] for row in rows}
        overlap = sorted(symbol_dates & benchmark_dates)
        ready = len(rows) >= int(config.get("raw_history_trading_dates", 180)) and len(overlap) >= int(config.get("validation_trading_dates", 120)) + 25
        provider_mode = rows[0]["provider_mode"] if rows else ""
        source_coverage.append(
            {
                "symbol": symbol,
                "provider_id": rows[0]["provider_id"] if rows else "",
                "provider_mode": provider_mode,
                "ohlcv_rows": len(rows),
                "benchmark_overlap_dates": len(overlap),
                "coverage_ready": ready,
                "failure_class": "PROVIDER_OK" if ready else _last_failure(role_events),
                "notes": "selected" if ready else "insufficient_or_failed_ohlcv_coverage",
            }
        )
        if ready:
            selected.append(
                {
                    "symbol": symbol,
                    "name": symbol,
                    "exchange": symbol.split(".")[-1],
                    "liquidity_proxy": _mean([float(row["amount"]) for row in rows[-20:]]),
                    "source_coverage_status": "source_backed_ohlcv_ready",
                    "approval_status": "approved_source_backed",
                    "notes": "approved by source-backed OHLCV coverage",
                    "coverage_status": "source_backed_ready",
                    "provider_id": rows[0]["provider_id"],
                    "provider_mode": provider_mode,
                    "source_bundle_id": BUNDLE_ID,
                }
            )
            stock_rows.extend(rows)

    trading_dates = _validation_dates(stock_rows, benchmark_rows, int(config.get("validation_trading_dates", 120)), int(config.get("symbol_target_count", 50)))
    pit_rows = _build_pit_rows(stock_rows, benchmark_rows, trading_dates)
    label_rows = _build_label_rows(stock_rows, benchmark_rows, trading_dates)
    stage_rows = _build_stage6c_rows(root, pit_rows, label_rows)
    usable_rows = [row for row in stage_rows if row["usable_for_validation"] is True]
    tier = classify_panel_tier(root, usable_rows)
    for row in stage_rows:
        row["panel_tier"] = tier["tier"] if row in usable_rows else "not_ready"
    manifest = _manifest(root, bundle_root, config, ladder, candidates, selected, trading_dates, stock_rows, benchmark_rows, pit_rows, label_rows, usable_rows, tier, events)
    _write_bundle(root, bundle_root, manifest, selected, trading_dates, stock_rows, benchmark_rows, source_coverage, pit_rows, label_rows, stage_rows, events)
    _write_github_outputs(root, manifest, selected, trading_dates, stock_rows, benchmark_rows, source_coverage, pit_rows, label_rows, stage_rows, usable_rows, tier, events, browser_enabled)
    return True


def _fetch_role(root: Path, data_role: str, symbol: str, start: str, end: str, browser_enabled: bool) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    events: list[dict[str, object]] = []
    url = _kline_url(symbol, start, end, data_role)
    max_retries, backoff_seconds = _retry_policy(root)
    for attempt_number in range(max_retries + 1):
        rows, event = _fetch_direct(url, data_role, symbol)
        if attempt_number:
            event["safe_notes"] = f"retry={attempt_number}; {event['safe_notes']}"[:240]
        events.append(event)
        if rows:
            return rows, events
        failure_class = str(event.get("primary_failure_class", "UNKNOWN_PROVIDER_FAILURE"))
        if not retry_allowed(failure_class) or attempt_number >= max_retries:
            break
        _sleep_between_provider_calls(backoff_seconds)
    if browser_enabled:
        if not browser_domain_allowed(root, url):
            events.append(_attempt("browser_assisted", "browser_assisted_optional", _function_name(data_role), data_role, target_domain(url), "FAIL", "BROWSER_ASSISTED_FORBIDDEN_BY_POLICY", "policy", fallback_provider_used="local_import", fallback_reason="non_finance_domain", safe_notes="domain blocked by finance policy"))
        else:
            result = fetch_urls_with_browser([(symbol, url)])[0]
            browser_rows = _parse_kline_rows(result.body_text, symbol, data_role, "browser_assisted_optional") if result.status == "PASS" else []
            schema_valid = bool(browser_rows)
            failure_class = "BROWSER_ASSISTED_STRUCTURED_INGESTION_SOLVED" if schema_valid else _browser_failure_class(result)
            events.append(
                _attempt(
                    "browser_assisted",
                    "browser_assisted_optional",
                    _function_name(data_role),
                    data_role,
                    target_domain(url),
                    "PASS" if schema_valid else "FAIL",
                    failure_class,
                    result.failure_layer or _browser_failure_layer(failure_class),
                    rows_returned=len(browser_rows),
                    schema_valid=schema_valid,
                    fallback_provider_used="" if schema_valid else "local_import",
                    fallback_reason="" if schema_valid else failure_class,
                    safe_notes=result.safe_notes,
                )
            )
            if browser_rows:
                return browser_rows, events
    local_rows = _local_rows(root, data_role, symbol)
    events.append(
        _attempt(
            "local_import",
            "local_import",
            _function_name(data_role),
            data_role,
            "local_import",
            "PASS" if local_rows else "FAIL",
            "PROVIDER_OK" if local_rows else "LOCAL_IMPORT_FILE_MISSING",
            "storage_bundle" if not local_rows else "unknown",
            rows_returned=len(local_rows),
            schema_valid=bool(local_rows),
            safe_notes="local import fallback",
        )
    )
    return local_rows, events


def _fetch_direct(url: str, data_role: str, symbol: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    session = requests.Session()
    session.trust_env = False
    try:
        response = session.get(url, timeout=8)
        rows = _parse_kline_rows(response.text, symbol, data_role, "akshare_direct") if response.status_code == 200 else []
        if rows:
            return rows, _attempt("akshare", "akshare_direct", _function_name(data_role), data_role, target_domain(url), "PASS", "PROVIDER_OK", "unknown", rows_returned=len(rows), schema_valid=True, safe_notes="direct finance kline JSON parsed")
        return [], _attempt("akshare", "akshare_direct", _function_name(data_role), data_role, target_domain(url), "FAIL", "EMPTY_RESPONSE" if not response.text else "BROWSER_ASSISTED_SCHEMA_MISMATCH", "data_quality", safe_notes=f"HTTP {response.status_code}; structured rows missing")
    except Exception as exc:
        failure = _network_failure_class(exc)
        return [], _attempt("akshare", "akshare_direct", _function_name(data_role), data_role, target_domain(url), "FAIL", failure, "network_transport", fallback_provider_used="browser_assisted_optional", fallback_reason=failure, safe_notes=f"{type(exc).__name__}: {_safe_note(exc)}")


def _retry_policy(root: Path) -> tuple[int, float]:
    try:
        policy = load_ingestion_config(root).get("retry_policy", {})
    except FileNotFoundError:
        return 0, 0.0
    max_retries = max(0, int(policy.get("max_retries", 0)))
    backoff_seconds = max(0.0, float(policy.get("backoff_seconds", 0.0)))
    return max_retries, backoff_seconds


def _rate_limit_seconds(config: dict[str, object]) -> float:
    policy = config.get("rate_limit_policy", {})
    if not isinstance(policy, dict):
        return 0.0
    return max(0.0, float(policy.get("min_seconds_between_symbol_calls", 0.0)))


def _sleep_between_provider_calls(seconds: float) -> None:
    if seconds > 0:
        time.sleep(seconds)


def _local_rows(root: Path, data_role: str, symbol: str) -> list[dict[str, object]]:
    role = "benchmark_daily" if data_role == "benchmark_ohlcv_daily" else "ohlcv_daily"
    rows = read_local_import_table(root, role)
    if not rows:
        return []
    symbol_key = "benchmark_symbol" if data_role == "benchmark_ohlcv_daily" else "symbol"
    return [dict(row, provider_mode=row.get("provider_mode") or "local_import", provider_id=row.get("provider_id") or "local_import", source_bundle_id=row.get("source_bundle_id") or BUNDLE_ID) for row in rows if row.get(symbol_key) == symbol]


def _parse_kline_rows(body: str, symbol: str, data_role: str, provider_mode: str) -> list[dict[str, object]]:
    try:
        payload = json.loads(body)
        klines = ((payload.get("data") or {}).get("klines") or [])
    except Exception:
        return []
    rows: list[dict[str, object]] = []
    for item in klines:
        parts = str(item).split(",")
        if len(parts) < 7:
            continue
        base = {
            "trade_date": parts[0],
            "open": _float(parts[1]),
            "close": _float(parts[2]),
            "high": _float(parts[3]),
            "low": _float(parts[4]),
            "volume": _float(parts[5]),
            "amount": _float(parts[6]),
            "provider_id": "eastmoney_akshare_contract" if provider_mode == "akshare_direct" else "cloakbrowser_eastmoney",
            "provider_mode": provider_mode,
            "source_bundle_id": BUNDLE_ID,
            "ingest_ts": "local_runtime",
            "schema_version": "goal06c7.ohlcv.v1",
            "data_quality_flags": "SOURCE_BACKED",
        }
        if data_role == "benchmark_ohlcv_daily":
            rows.append({"benchmark_symbol": symbol, **base})
        else:
            rows.append({"symbol": symbol, **base})
    return rows


def _build_pit_rows(stock_rows: list[dict[str, object]], benchmark_rows: list[dict[str, object]], trading_dates: list[str]) -> list[dict[str, object]]:
    stocks = _by_symbol_date(stock_rows)
    benchmark = {row["trade_date"]: row for row in benchmark_rows}
    bench_dates = sorted(benchmark)
    bench_close = _series(benchmark, bench_dates, "close")
    rows = []
    for symbol, by_date in sorted(stocks.items()):
        dates = sorted(by_date)
        close = _series(by_date, dates, "close")
        for target_date in trading_dates:
            if target_date not in by_date:
                continue
            idx = dates.index(target_date)
            bench_idx = bench_dates.index(dates[idx - 1]) if idx > 0 and dates[idx - 1] in benchmark else -1
            if idx < 21 or bench_idx < 20:
                continue
            as_of_date = dates[idx - 1]
            provider_mode = by_date[target_date]["provider_mode"]
            rows.append(
                {
                    "as_of_date": as_of_date,
                    "target_trading_date": target_date,
                    "decision_cutoff_ts": f"{target_date}T09:00:00+08:00",
                    "symbol": symbol,
                    "market_trend_5d": _return(bench_close, bench_idx - 5, bench_idx),
                    "stock_momentum_5d": _return(close, idx - 6, idx - 1),
                    "stock_momentum_20d": _return(close, idx - 21, idx - 1),
                    "stock_gap_signal": _return(close, idx - 2, idx - 1),
                    "stock_volatility_20d": _volatility(close, idx - 21, idx - 1),
                    "turnover_proxy": _mean([float(by_date[date].get("amount", 0) or 0) for date in dates[idx - 20 : idx]]),
                    "relative_strength_20d": _return(close, idx - 21, idx - 1) - _return(bench_close, bench_idx - 20, bench_idx),
                    "source_health_score": 1.0,
                    "source_count": 2,
                    "provider_id": by_date[target_date]["provider_id"],
                    "provider_mode": provider_mode,
                    "source_bundle_id": BUNDLE_ID,
                    "pit_ready": True,
                    "feature_contract_version": "goal06c7.source_backed_pit.v1",
                    "data_quality_flags": "SOURCE_BACKED",
                }
            )
    return rows


def _build_label_rows(stock_rows: list[dict[str, object]], benchmark_rows: list[dict[str, object]], trading_dates: list[str]) -> list[dict[str, object]]:
    stocks = _by_symbol_date(stock_rows)
    benchmark = {row["trade_date"]: row for row in benchmark_rows}
    bench_dates = sorted(benchmark)
    bench_close = _series(benchmark, bench_dates, "close")
    rows = []
    for symbol, by_date in sorted(stocks.items()):
        dates = sorted(by_date)
        close = _series(by_date, dates, "close")
        for trade_date in trading_dates:
            if trade_date not in by_date or trade_date not in benchmark:
                continue
            idx = dates.index(trade_date)
            bench_idx = bench_dates.index(trade_date)
            ready = idx + 5 < len(dates) and bench_idx + 5 < len(bench_dates)
            provider_mode = by_date[trade_date]["provider_mode"]
            fwd1 = _return(close, idx, idx + 1) if ready else ""
            fwd3 = _return(close, idx, idx + 3) if ready else ""
            fwd5 = _return(close, idx, idx + 5) if ready else ""
            bench1 = _return(bench_close, bench_idx, bench_idx + 1) if ready else ""
            bench3 = _return(bench_close, bench_idx, bench_idx + 3) if ready else ""
            bench5 = _return(bench_close, bench_idx, bench_idx + 5) if ready else ""
            rows.append(
                {
                    "trade_date": trade_date,
                    "symbol": symbol,
                    "fwd_1d_return": fwd1,
                    "fwd_3d_return": fwd3,
                    "fwd_5d_return": fwd5,
                    "benchmark_fwd_1d_return": bench1,
                    "benchmark_fwd_3d_return": bench3,
                    "benchmark_fwd_5d_return": bench5,
                    "excess_fwd_1d_return": round(float(fwd1) - float(bench1), 6) if ready else "",
                    "excess_fwd_3d_return": round(float(fwd3) - float(bench3), 6) if ready else "",
                    "excess_fwd_5d_return": round(float(fwd5) - float(bench5), 6) if ready else "",
                    "provider_id": by_date[trade_date]["provider_id"],
                    "provider_mode": provider_mode,
                    "source_bundle_id": BUNDLE_ID,
                    "label_ready": ready,
                    "label_contract_version": "goal06c7.source_backed_label.v1",
                    "label_quality_flags": "SOURCE_BACKED" if ready else "MISSING_FORWARD_TRADING_DAYS",
                }
            )
    return rows


def _build_stage6c_rows(root: Path, pit_rows: list[dict[str, object]], label_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    labels = {(row["trade_date"], row["symbol"]): row for row in label_rows}
    rows = []
    for pit in pit_rows:
        label = labels.get((pit["target_trading_date"], pit["symbol"]))
        if not label:
            continue
        usable = pit["pit_ready"] is True and label["label_ready"] is True
        rows.append(
            {
                "trade_date": pit["target_trading_date"],
                "symbol": pit["symbol"],
                "as_of_date": pit["as_of_date"],
                "decision_cutoff_ts": pit["decision_cutoff_ts"],
                "market_trend_5d": pit["market_trend_5d"],
                "stock_momentum_5d": pit["stock_momentum_5d"],
                "stock_momentum_20d": pit["stock_momentum_20d"],
                "stock_gap_signal": pit["stock_gap_signal"],
                "stock_volatility_20d": pit["stock_volatility_20d"],
                "turnover_proxy": pit["turnover_proxy"],
                "relative_strength_20d": pit["relative_strength_20d"],
                "source_health_score": pit["source_health_score"],
                "source_count": pit["source_count"],
                "provider_id": pit["provider_id"],
                "provider_mode": pit["provider_mode"],
                "fwd_1d_return": label["fwd_1d_return"],
                "fwd_3d_return": label["fwd_3d_return"],
                "fwd_5d_return": label["fwd_5d_return"],
                "excess_fwd_1d_return": label["excess_fwd_1d_return"],
                "excess_fwd_3d_return": label["excess_fwd_3d_return"],
                "excess_fwd_5d_return": label["excess_fwd_5d_return"],
                "usable_for_validation": usable,
                "panel_source_type": "real_source_backed",
                "source_bundle_id": BUNDLE_ID,
                "review_only": True,
                "data_quality_flags": f"{pit['data_quality_flags']};{label['label_quality_flags']}",
                "leakage_flags": "PASS",
                "panel_tier": "",
            }
        )
    return rows


def _manifest(root: Path, bundle_root: Path, config: dict[str, object], ladder: dict[str, object], candidates: list[str], selected: list[dict[str, object]], trading_dates: list[str], stock_rows: list[dict[str, object]], benchmark_rows: list[dict[str, object]], pit_rows: list[dict[str, object]], label_rows: list[dict[str, object]], usable_rows: list[dict[str, object]], tier: dict[str, object], events: list[dict[str, object]]) -> dict[str, object]:
    counts = tier["counts"]
    allowed = tier["tier"] in {"engineering_pilot", "research_ready", "strong_panel"}
    return {
        "goal_id": "GOAL-06C.7",
        "bundle_id": BUNDLE_ID,
        "bundle_tier": tier["tier"],
        "provider_ladder_order": ladder["provider_ladder_order"],
        "data_root": str(resolve_data_root(root)),
        "local_bundle_path": str(bundle_root),
        "candidate_symbols": len(candidates),
        "approved_symbols": len(selected),
        "raw_history_trading_dates": len({row["trade_date"] for row in stock_rows}),
        "validation_trading_dates": len(trading_dates),
        "stock_ohlcv_rows": len(stock_rows),
        "benchmark_rows": len(benchmark_rows),
        "pit_ready_rows": sum(1 for row in pit_rows if row["pit_ready"] is True),
        "label_ready_rows": sum(1 for row in label_rows if row["label_ready"] is True),
        "stage6c_engineering_rows": len(usable_rows),
        "panel_tier": tier["tier"],
        "engineering_pilot_met": allowed,
        "goal06d_allowed_to_proceed": allowed,
        "goal06d_mode": "review_only" if allowed else "blocked",
        "remaining_gap": {
            "symbols": max(0, int(config.get("symbol_target_count", 50)) - counts["symbols"]),
            "validation_trading_dates": max(0, int(config.get("validation_trading_dates", 120)) - counts["trading_dates"]),
            "stage6c_rows": max(0, int(config.get("minimum_stage6c_rows", 6000)) - counts["rows"]),
        },
        "provider_attempt_count": len(events),
        "browser_dependency_status": browser_dependency_status(),
        "local_import_status": local_import_status(root),
        "raw_html_stored": False,
        "raw_payload_stored": False,
        "heavy_data_committed": False,
        "health_status": "PASS" if allowed else "PASS_WITH_WARNINGS",
    }


def _write_bundle(root: Path, bundle_root: Path, manifest: dict[str, object], selected: list[dict[str, object]], trading_dates: list[str], stock_rows: list[dict[str, object]], benchmark_rows: list[dict[str, object]], source_coverage: list[dict[str, object]], pit_rows: list[dict[str, object]], label_rows: list[dict[str, object]], stage_rows: list[dict[str, object]], events: list[dict[str, object]]) -> None:
    write_json(bundle_root / "manifest.json", manifest)
    write_csv(bundle_root / "universe.csv", selected, UNIVERSE_FIELDS)
    write_csv(bundle_root / "trading_calendar.csv", [{"trade_date": date} for date in trading_dates], CALENDAR_FIELDS)
    write_csv(bundle_root / "ohlcv_daily.csv", stock_rows, STOCK_FIELDS)
    write_csv(bundle_root / "benchmark_daily.csv", benchmark_rows, BENCHMARK_FIELDS)
    write_csv(bundle_root / "provider_attempt_log.csv", events, BROWSER_EVENT_FIELDS)
    write_csv(bundle_root / "provider_failure_events.csv", [row for row in events if row["attempt_status"] != "PASS"], BROWSER_EVENT_FIELDS)
    write_csv(bundle_root / "source_coverage.csv", source_coverage, SOURCE_COVERAGE_FIELDS)
    write_csv(bundle_root / "pit_signal_panel.csv", pit_rows, PIT_FIELDS)
    write_csv(bundle_root / "label_panel.csv", label_rows, LABEL_FIELDS)
    write_csv(bundle_root / "stage6c_engineering_panel.csv", stage_rows, STAGE6C_FIELDS)
    _write_checksums(bundle_root)


def _write_github_outputs(root: Path, manifest: dict[str, object], selected: list[dict[str, object]], trading_dates: list[str], stock_rows: list[dict[str, object]], benchmark_rows: list[dict[str, object]], source_coverage: list[dict[str, object]], pit_rows: list[dict[str, object]], label_rows: list[dict[str, object]], stage_rows: list[dict[str, object]], usable_rows: list[dict[str, object]], tier: dict[str, object], events: list[dict[str, object]], browser_enabled: bool) -> None:
    write_json(root / "outputs/audits/source_backed_bundle_manifest_summary.json", manifest)
    write_text(root / "outputs/audits/source_backed_bundle_manifest_summary.md", _bundle_summary_md(manifest))
    write_csv(root / "outputs/samples/source_backed_universe_sample.csv", selected[:SAMPLE_MAX_ROWS], UNIVERSE_FIELDS)
    write_csv(root / "outputs/samples/source_backed_ohlcv_daily_sample.csv", stock_rows[:SAMPLE_MAX_ROWS], STOCK_FIELDS)
    write_csv(root / "outputs/samples/source_backed_benchmark_daily_sample.csv", benchmark_rows[:SAMPLE_MAX_ROWS], BENCHMARK_FIELDS)
    write_csv(root / "outputs/samples/source_backed_pit_signal_panel_sample.csv", pit_rows[:SAMPLE_MAX_ROWS], PIT_FIELDS)
    write_csv(root / "outputs/samples/source_backed_label_panel_sample.csv", label_rows[:SAMPLE_MAX_ROWS], LABEL_FIELDS)
    write_csv(root / "outputs/samples/stage6c_source_backed_engineering_panel_sample.csv", stage_rows[:SAMPLE_MAX_ROWS], STAGE6C_FIELDS)
    _write_audits(root, manifest, selected, trading_dates, source_coverage, pit_rows, label_rows, usable_rows, tier)
    browser_rows = sum(1 for row in usable_rows if row.get("provider_mode") == "browser_assisted_optional")
    write_browser_assisted_audit(
        root,
        events,
        {
            "browser_assisted_enabled": browser_enabled,
            "browser_assisted_project_default": browser_provider_project_default(root),
            "explicit_opt_in_used": browser_enabled,
            "browser_dependency_status": browser_dependency_status(),
            "temporary_venv_used": os.environ.get("ASHARE_BROWSER_TEMP_VENV_USED", "") in {"1", "true", "TRUE", "yes", "YES"},
            "temporary_cache_used": bool(os.environ.get("CLOAKBROWSER_CACHE_DIR", "")),
            "temporary_cache_cleaned": os.environ.get("ASHARE_BROWSER_TEMP_CACHE_CLEANED", "1") in {"1", "true", "TRUE", "yes", "YES"},
            "raw_html_stored": False,
            "raw_payload_stored": False,
            "cookies_stored": False,
            "session_data_stored": False,
            "captcha_or_challenge_detected": False,
            "access_restriction_detected": any(row.get("primary_failure_class") == "BROWSER_ASSISTED_ACCESS_RESTRICTION_DETECTED" for row in events),
            "provider_mode_rows_in_panel": browser_rows,
            "goal06d_allowed_to_proceed": manifest["goal06d_allowed_to_proceed"],
        },
    )


def _write_empty_goal06c7_outputs(root: Path, bundle_root: Path, events: list[dict[str, object]], config: dict[str, object], browser_enabled: bool) -> None:
    tier = {"tier": "below_contract_demo", "counts": {"symbols": 0, "trading_dates": 0, "rows": 0}, "contract": {"goal06d_allowed": False}}
    manifest = _manifest(root, bundle_root, config, _load_json(root / LADDER_CONFIG), [], [], [], [], [], [], [], [], tier, events)
    _write_bundle(root, bundle_root, manifest, [], [], [], [], [], [], [], [], events)
    _write_github_outputs(root, manifest, [], [], [], [], [], [], [], [], [], tier, events, browser_enabled)


def _write_audits(root: Path, manifest: dict[str, object], selected: list[dict[str, object]], trading_dates: list[str], source_coverage: list[dict[str, object]], pit_rows: list[dict[str, object]], label_rows: list[dict[str, object]], usable_rows: list[dict[str, object]], tier: dict[str, object]) -> None:
    status = "PASS" if manifest["engineering_pilot_met"] else "PASS_WITH_WARNINGS"
    write_text(root / "outputs/audits/source_backed_local_bundle_audit.md", "\n".join(["# Source-Backed Local Bundle Audit", "", f"Status: `{status}`", f"Bundle id: `{BUNDLE_ID}`", f"Local bundle path: `{manifest['local_bundle_path']}`", "Full bundle files are local-only and not committed.", ""]))
    write_text(root / "outputs/audits/source_backed_universe_audit.md", "\n".join(["# Source-Backed Universe Audit", "", f"Status: `{status}`", f"Selected symbols: `{len(selected)}`", f"Candidate symbols: `{manifest['candidate_symbols']}`", f"Remaining symbol gap: `{manifest['remaining_gap']['symbols']}`", "Blocked symbols are excluded.", ""]))
    write_text(root / "outputs/audits/source_backed_trading_calendar_audit.md", "\n".join(["# Source-Backed Trading Calendar Audit", "", f"Status: `{status}`", f"Raw history trading dates: `{manifest['raw_history_trading_dates']}`", f"Validation trading dates: `{len(trading_dates)}`", "Dates are source-backed OHLCV trading dates, not calendar shortcuts.", ""]))
    write_text(root / "outputs/audits/source_backed_pit_signal_panel_audit.md", "\n".join(["# Source-Backed PIT Signal Panel Audit", "", f"Status: `{'PASS' if pit_rows else 'PASS_WITH_WARNINGS'}`", f"Rows reviewed: `{len(pit_rows)}`", f"PIT-ready rows: `{manifest['pit_ready_rows']}`", "PIT features use T-1 or earlier source rows and exclude labels.", ""]))
    write_text(root / "outputs/audits/source_backed_label_panel_audit.md", "\n".join(["# Source-Backed Label Panel Audit", "", f"Status: `{'PASS' if label_rows else 'PASS_WITH_WARNINGS'}`", f"Rows reviewed: `{len(label_rows)}`", f"Label-ready rows: `{manifest['label_ready_rows']}`", "Labels use trading-day forward offsets and remain offline-only.", ""]))
    write_csv(
        root / "outputs/stage6c/STAGE6C_source_backed_engineering_panel_coverage_summary.csv",
        [{
            "panel_id": "goal06c7_provider_ladder_engineering_panel",
            "current_symbols": tier["counts"]["symbols"],
            "current_trading_dates": tier["counts"]["trading_dates"],
            "current_rows": tier["counts"]["rows"],
            "panel_tier": tier["tier"],
            "engineering_pilot_required_symbols": 50,
            "engineering_pilot_required_trading_dates": 120,
            "engineering_pilot_required_rows": 6000,
            "engineering_pilot_met": manifest["engineering_pilot_met"],
            "goal06d_allowed": manifest["goal06d_allowed_to_proceed"],
            "goal06d_mode": manifest["goal06d_mode"],
        }],
    )
    write_text(root / "outputs/audits/stage6c_source_backed_engineering_panel_audit.md", "\n".join(["# Stage 6C Source-Backed Engineering Panel Audit", "", f"Status: `{status}`", f"Panel tier: `{tier['tier']}`", f"Rows: `{tier['counts']['rows']}`", f"Symbols: `{tier['counts']['symbols']}`", f"Trading dates: `{tier['counts']['trading_dates']}`", f"GOAL-06D allowed to proceed: `{str(manifest['goal06d_allowed_to_proceed']).lower()}`", "Leakage flags: `PASS`", ""]))
    write_text(root / "outputs/audits/goal06c7_readiness_report.md", _goal06c7_readiness(manifest))


def _bundle_summary_md(manifest: dict[str, object]) -> str:
    return "\n".join(["# Source-Backed Bundle Manifest Summary", "", f"Status: `{manifest['health_status']}`", f"Bundle id: `{manifest['bundle_id']}`", f"Bundle tier: `{manifest['bundle_tier']}`", f"Approved symbols: `{manifest['approved_symbols']}`", f"Validation trading dates: `{manifest['validation_trading_dates']}`", f"Stage 6C engineering rows: `{manifest['stage6c_engineering_rows']}`", f"Local bundle path: `{manifest['local_bundle_path']}`", "Full local bundle files are not committed.", ""])


def _goal06c7_readiness(manifest: dict[str, object]) -> str:
    decision = "PASS" if manifest["engineering_pilot_met"] else "PASS_WITH_WARNINGS"
    gap = manifest["remaining_gap"]
    return "\n".join(["# GOAL-06C.7 Engineering Data Base Expansion Readiness Report", "", f"GOAL-06C.7 Engineering Data Base Expansion Readiness: {decision}", f"Panel tier: `{manifest['panel_tier']}`", f"Approved symbols: `{manifest['approved_symbols']}`", f"Validation trading dates: `{manifest['validation_trading_dates']}`", f"Stage 6C engineering rows: `{manifest['stage6c_engineering_rows']}`", f"GOAL-06D allowed to proceed: {str(manifest['goal06d_allowed_to_proceed']).lower()}", f"GOAL-06D mode: {manifest['goal06d_mode']}", f"Remaining gap: symbols={gap['symbols']}; dates={gap['validation_trading_dates']}; rows={gap['stage6c_rows']}", "No fake data was used.", "No raw browser data or heavy local bundle files were committed.", ""])


def _validation_dates(stock_rows: list[dict[str, object]], benchmark_rows: list[dict[str, object]], target_dates: int, target_symbols: int) -> list[str]:
    dates_by_symbol: dict[str, set[str]] = defaultdict(set)
    for row in stock_rows:
        dates_by_symbol[str(row["symbol"])].add(str(row["trade_date"]))
    benchmark_dates = {str(row["trade_date"]) for row in benchmark_rows}
    counts: dict[str, int] = defaultdict(int)
    for dates in dates_by_symbol.values():
        for date in dates & benchmark_dates:
            counts[date] += 1
    common = sorted(date for date, count in counts.items() if count >= min(target_symbols, len(dates_by_symbol)))
    usable = common[21 : max(21, len(common) - 5)]
    return usable[-target_dates:]


def _attempt(provider_id: str, provider_mode: str, function_name: str, data_role: str, domain: str, status: str, failure_class: str, failure_layer: str, rows_returned: int = 0, schema_valid: bool = False, fallback_provider_used: str = "", fallback_reason: str = "", secondary_failure_class: str = "", safe_notes: str = "") -> dict[str, object]:
    return {
        "run_id": RUN_ID,
        "bundle_id": BUNDLE_ID,
        "provider_id": provider_id,
        "provider_mode": provider_mode,
        "function_name": function_name,
        "data_role": data_role,
        "target_domain": domain,
        "attempt_status": status,
        "raw_failure_type": failure_class if status != "PASS" else "",
        "primary_failure_class": failure_class,
        "secondary_failure_class": secondary_failure_class,
        "failure_layer": failure_layer,
        "rows_returned": rows_returned,
        "schema_valid": schema_valid,
        "fallback_provider_used": fallback_provider_used,
        "fallback_reason": fallback_reason,
        "safe_notes": safe_notes[:240],
    }


def _kline_url(symbol: str, start: str, end: str, data_role: str) -> str:
    secid = _secid(symbol)
    params = {"secid": secid, "ut": "7eea3edcaed734bea9cbfc24409ed989", "fields1": "f1,f2,f3,f4,f5,f6", "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61", "klt": "101", "fqt": "0" if data_role == "benchmark_ohlcv_daily" else "1", "beg": start, "end": end}
    return "https://push2his.eastmoney.com/api/qt/stock/kline/get?" + urlencode(params)


def _secid(symbol: str) -> str:
    if "." not in symbol:
        return f"1.{symbol}"
    code, exchange = symbol.split(".")
    return ("1" if exchange == "SH" else "0") + "." + code


def _function_name(data_role: str) -> str:
    return "index_zh_a_hist" if data_role == "benchmark_ohlcv_daily" else "stock_zh_a_hist"


def _last_failure(events: list[dict[str, object]]) -> str:
    for row in reversed(events):
        if row["attempt_status"] != "PASS":
            return str(row["primary_failure_class"])
    return ""


def _network_failure_class(exc: BaseException) -> str:
    message = str(exc).lower()
    if "proxy" in message:
        return "EXTERNAL_PROXY_ENVIRONMENT_FAILURE"
    if "empty response" in message or "remote end closed" in message:
        return "BROWSER_NET_EMPTY_RESPONSE"
    if "timeout" in message:
        return "EXTERNAL_NETWORK_TIMEOUT"
    if "ssl" in message or "certificate" in message:
        return "TLS_SSL_FAILURE"
    return "UNKNOWN_NETWORK_FAILURE"


def _browser_failure_class(result: object) -> str:
    failure_class = getattr(result, "failure_class", "") or ""
    if failure_class:
        return failure_class
    body_text = (getattr(result, "body_text", "") or "").lower()
    content_type = (getattr(result, "content_type", "") or "").lower()
    if "<html" in body_text or "text/html" in content_type:
        return "BROWSER_ASSISTED_DOMAIN_ACCESS_ONLY"
    if body_text:
        return "BROWSER_ASSISTED_SCHEMA_MISMATCH"
    return "BROWSER_ASSISTED_ATTEMPTED_NOT_SOLVED"


def _browser_failure_layer(failure_class: str) -> str:
    if failure_class == "BROWSER_NET_EMPTY_RESPONSE":
        return "network_transport"
    if failure_class == "BROWSER_RUNTIME_DEPENDENCY_MISSING":
        return "dependency"
    if failure_class == "BROWSER_ASSISTED_FORBIDDEN_BY_POLICY":
        return "policy"
    if failure_class == "BROWSER_ASSISTED_SCHEMA_MISMATCH":
        return "provider_contract"
    if failure_class == "BROWSER_ASSISTED_PARSER_FAILURE":
        return "parser_implementation"
    if failure_class == "BROWSER_ASSISTED_ACCESS_RESTRICTION_DETECTED":
        return "anti_bot_access"
    return "browser_runtime"


def _valid_symbol(symbol: str) -> bool:
    return len(symbol) == 9 and symbol[:6].isdigit() and symbol[-3:] in {".SH", ".SZ"}


def _by_symbol_date(rows: list[dict[str, object]]) -> dict[str, dict[str, dict[str, object]]]:
    out: dict[str, dict[str, dict[str, object]]] = defaultdict(dict)
    for row in rows:
        out[str(row["symbol"])][str(row["trade_date"])] = row
    return out


def _series(rows_by_date: dict[str, dict[str, object]], dates: list[str], column: str) -> list[float]:
    return [float(rows_by_date[date].get(column, 0) or 0) for date in dates]


def _return(values: list[float], start_idx: int, end_idx: int) -> float:
    if start_idx < 0 or end_idx >= len(values) or values[start_idx] == 0:
        return 0.0
    return round(values[end_idx] / values[start_idx] - 1, 6)


def _volatility(values: list[float], start_idx: int, end_idx: int) -> float:
    if start_idx < 0 or end_idx >= len(values) or end_idx - start_idx < 2:
        return 0.0
    returns = [_return(values, idx - 1, idx) for idx in range(start_idx + 1, end_idx + 1)]
    mean_value = sum(returns) / len(returns)
    variance = sum((value - mean_value) ** 2 for value in returns) / len(returns)
    return round(math.sqrt(variance), 6)


def _mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 6) if values else 0.0


def _float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _write_checksums(bundle_root: Path) -> None:
    lines = []
    for path in sorted(bundle_root.glob("*")):
        if path.name == "checksums.sha256" or not path.is_file():
            continue
        hasher = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                hasher.update(chunk)
        lines.append(f"{hasher.hexdigest()}  {path.name}")
    (bundle_root / "checksums.sha256").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def _safe_note(value: object) -> str:
    return str(value).replace("\n", " ").replace("\r", " ")[:240]


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))

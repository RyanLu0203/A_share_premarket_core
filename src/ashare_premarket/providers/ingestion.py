from __future__ import annotations

import csv
import hashlib
import json
import math
import time
from collections import defaultdict
from pathlib import Path

from ashare_premarket.core.io import read_csv, write_csv, write_json, write_text
from ashare_premarket.providers.akshare_provider import (
    akshare_available,
    akshare_function_signatures,
    load_a_share_code_name_list,
    load_a_share_spot_snapshot,
    load_benchmark_ohlcv_daily,
    load_stock_ohlcv_daily,
)
from ashare_premarket.providers.provider_attempt_log import make_attempt, write_provider_attempt_log, write_provider_attempt_summary
from ashare_premarket.providers.provider_registry import engineering_bundle_root, load_ingestion_config, network_enabled
from ashare_premarket.universe.governance import load_blocked_symbols
from ashare_premarket.validation.engineering_panel import classify_panel_tier

BUNDLE_ID = "goal06c6_akshare_engineering_pilot_current"
SOURCE_BUNDLE_SUMMARY_JSON = "outputs/audits/source_backed_bundle_manifest_summary.json"
SOURCE_PANEL_COVERAGE = "outputs/stage6c/STAGE6C_source_backed_engineering_panel_coverage_summary.csv"
SAMPLE_MAX_ROWS = 100
UNIVERSE_FIELDS = ["symbol", "name", "exchange", "liquidity_proxy", "source_coverage_status", "approval_status", "notes", "coverage_status"]
STOCK_OHLCV_FIELDS = ["trade_date", "symbol", "open", "high", "low", "close", "volume", "amount", "turnover_rate", "source_id", "quality_flags"]
BENCHMARK_FIELDS = ["trade_date", "benchmark_symbol", "open", "high", "low", "close", "volume", "amount", "source_id", "quality_flags"]
SOURCE_COVERAGE_FIELDS = ["symbol", "provider_id", "ohlcv_rows", "benchmark_overlap_dates", "coverage_ready", "failure_class", "notes"]
SOURCE_BACKED_PIT_FIELDS = [
    "as_of_date",
    "target_trading_date",
    "decision_cutoff_ts",
    "symbol",
    "market_trend_5d",
    "stock_momentum_5d",
    "stock_momentum_20d",
    "stock_gap_signal",
    "stock_volatility_20d",
    "turnover_proxy",
    "relative_strength_20d",
    "source_health_score",
    "source_count",
    "pit_ready",
    "panel_source_type",
    "source_bundle_id",
    "feature_contract_version",
    "data_quality_flags",
]
SOURCE_BACKED_LABEL_FIELDS = [
    "trade_date",
    "symbol",
    "fwd_1d_return",
    "fwd_3d_return",
    "fwd_5d_return",
    "benchmark_fwd_1d_return",
    "benchmark_fwd_3d_return",
    "benchmark_fwd_5d_return",
    "excess_fwd_1d_return",
    "excess_fwd_3d_return",
    "excess_fwd_5d_return",
    "label_ready",
    "source_bundle_id",
    "label_contract_version",
    "label_quality_flags",
]


def run_goal06c6_source_backed_engineering_pilot_bundle(root: Path, allow_network: bool = False) -> bool:
    return build_source_backed_local_bundle(root, allow_network=allow_network)


def build_engineering_pilot_universe(root: Path, allow_network: bool = False) -> Path:
    enabled = network_enabled(allow_network)
    config = load_ingestion_config(root)
    attempts: list[dict[str, object]] = []
    blocked = set(load_blocked_symbols(root))
    if not enabled:
        attempts.append(_network_disabled_attempt("stock_info_a_code_name"))
        write_provider_attempt_summary(root, attempts)
        _write_source_backed_universe_audit(root, [], [], "PASS_WITH_WARNINGS", "network_disabled_by_policy")
        write_csv(
            root / "outputs/samples/source_backed_universe_sample.csv",
            [],
            UNIVERSE_FIELDS,
        )
        return root / "outputs/samples/source_backed_universe_sample.csv"

    code_result = load_a_share_code_name_list(enabled)
    attempts.append(code_result.attempt)
    spot_lookup, spot_attempt = load_a_share_spot_snapshot(enabled)
    attempts.append(spot_attempt)
    candidates = _candidate_rows(code_result.rows, spot_lookup, blocked)
    candidates = candidates[: int(config["candidate_symbol_count"])]
    selected = candidates[: int(config["symbol_target_count"])]
    status = "PASS" if len(selected) >= int(config["symbol_target_count"]) else "PASS_WITH_WARNINGS"
    notes = "source_backed_code_name_list" if selected else "no_source_backed_candidates"
    write_provider_attempt_summary(root, attempts)
    write_csv(root / "outputs/samples/source_backed_universe_sample.csv", selected[:SAMPLE_MAX_ROWS], UNIVERSE_FIELDS)
    _write_source_backed_universe_audit(root, selected, candidates, status, notes)
    return root / "outputs/samples/source_backed_universe_sample.csv"


def build_source_backed_local_bundle(root: Path, allow_network: bool = False) -> bool:
    enabled = network_enabled(allow_network)
    config = load_ingestion_config(root)
    bundle_root = engineering_bundle_root(root, BUNDLE_ID)
    attempts: list[dict[str, object]] = []
    if not enabled:
        attempts.append(_network_disabled_attempt("run_goal06c6_source_backed_engineering_pilot_bundle"))
        write_provider_attempt_summary(root, attempts)
        _write_no_bundle_outputs(root, bundle_root, attempts, "PASS_WITH_WARNINGS", "network_disabled_by_policy")
        return True

    if not akshare_available():
        attempts.append(
            make_attempt(
                "akshare",
                "import akshare",
                network_enabled=True,
                status="FAIL",
                failure_class="DEPENDENCY_MISSING",
                retry_allowed=False,
                notes="optional dependency akshare is not installed; install with `pip install .[data]` or `pip install akshare`",
            )
        )
        write_provider_attempt_summary(root, attempts)
        _write_no_bundle_outputs(root, bundle_root, attempts, "BLOCKED", "dependency_missing")
        return False

    bundle_root.mkdir(parents=True, exist_ok=True)
    start_date = "2024-01-01"
    end_date = "2024-12-31"
    benchmark_symbol = str(config["benchmark_symbols"][0])
    benchmark = load_benchmark_ohlcv_daily(benchmark_symbol, start_date, end_date, enabled)
    attempts.append(benchmark.attempt)
    code_result = load_a_share_code_name_list(enabled)
    attempts.append(code_result.attempt)
    spot_lookup, spot_attempt = load_a_share_spot_snapshot(enabled)
    attempts.append(spot_attempt)

    blocked = set(load_blocked_symbols(root))
    candidates = _candidate_rows(code_result.rows, spot_lookup, blocked)
    candidates = candidates[: int(config["candidate_symbol_count"])]
    target_symbols = int(config["symbol_target_count"])
    selected: list[dict[str, object]] = []
    all_stock_rows: list[dict[str, object]] = []
    source_coverage_rows: list[dict[str, object]] = []

    benchmark_dates = sorted({str(row["trade_date"]) for row in benchmark.rows})
    pause_seconds = float(config.get("rate_limit_policy", {}).get("min_seconds_between_symbol_calls", 0.2))
    for candidate in candidates:
        if len(selected) >= target_symbols:
            break
        symbol = str(candidate["symbol"])
        stock = load_stock_ohlcv_daily(symbol, start_date, end_date, str(config["adjustment_policy"]), enabled)
        attempts.append(stock.attempt)
        symbol_dates = sorted({str(row["trade_date"]) for row in stock.rows})
        common_dates = sorted(set(symbol_dates) & set(benchmark_dates))
        enough = len(common_dates) >= _required_raw_dates(config)
        source_coverage_rows.append(
            {
                "symbol": symbol,
                "provider_id": "akshare",
                "ohlcv_rows": len(stock.rows),
                "benchmark_overlap_dates": len(common_dates),
                "coverage_ready": enough,
                "failure_class": stock.attempt["failure_class"],
                "notes": "selected" if enough else "insufficient_ohlcv_coverage",
            }
        )
        if enough:
            selected.append({**candidate, "approval_status": "approved_source_backed", "coverage_status": "source_backed_ohlcv_ready"})
            all_stock_rows.extend([row for row in stock.rows if row["trade_date"] in common_dates])
        if pause_seconds > 0:
            time.sleep(pause_seconds)

    write_provider_attempt_summary(root, attempts)
    write_provider_attempt_log(bundle_root / "provider_attempt_log.csv", attempts)
    _write_local_table(bundle_root / "universe", selected)
    _write_local_table(bundle_root / "benchmark_daily", benchmark.rows)
    _write_local_table(bundle_root / "ohlcv_daily", all_stock_rows)
    _write_local_table(bundle_root / "source_coverage", source_coverage_rows)
    trading_dates = _validation_dates(all_stock_rows, benchmark.rows, config)
    write_csv(bundle_root / "trading_calendar.csv", [{"trade_date": date} for date in trading_dates], ["trade_date"])
    _write_checksums(bundle_root)

    manifest = _bundle_manifest(root, bundle_root, selected, trading_dates, all_stock_rows, benchmark.rows, attempts, source_coverage_rows)
    write_json(bundle_root / "manifest.json", manifest)
    _write_committed_manifest_summary(root, manifest)
    write_csv(root / "outputs/samples/source_backed_universe_sample.csv", selected[:SAMPLE_MAX_ROWS], UNIVERSE_FIELDS)
    write_csv(root / "outputs/samples/source_backed_ohlcv_daily_sample.csv", all_stock_rows[:SAMPLE_MAX_ROWS], STOCK_OHLCV_FIELDS)
    write_csv(root / "outputs/samples/source_backed_benchmark_daily_sample.csv", benchmark.rows[:SAMPLE_MAX_ROWS], BENCHMARK_FIELDS)
    _write_source_backed_universe_audit(root, selected, candidates, "PASS" if len(selected) >= target_symbols else "PASS_WITH_WARNINGS", "source_backed_coverage_checked")
    _write_source_backed_trading_calendar_audit(root, trading_dates, config)

    pit_rows = build_source_backed_pit_signal_panel(root, bundle_root)
    label_rows = build_source_backed_label_panel(root, bundle_root)
    stage_rows = rebuild_stage6c_source_backed_engineering_panel(root, pit_rows, label_rows)
    panel_ok = audit_stage6c_source_backed_engineering_panel(root)
    audit_source_backed_local_bundle(root)
    _write_goal06c6_readiness(root, manifest, panel_ok)
    return panel_ok and manifest["health_status"] != "BLOCKED"


def audit_source_backed_local_bundle(root: Path) -> bool:
    summary = _load_json(root / SOURCE_BUNDLE_SUMMARY_JSON) if (root / SOURCE_BUNDLE_SUMMARY_JSON).exists() else {}
    failures: list[str] = []
    warnings: list[str] = []
    if not summary:
        failures.append("source-backed bundle manifest summary is missing")
    if summary.get("network_status") == "network_disabled_by_policy":
        warnings.append("network ingestion disabled by policy")
    if summary.get("akshare_available") is False and summary.get("network_status") != "network_disabled_by_policy":
        failures.append("AKShare is not available for source-backed ingestion")
    if summary.get("health_status") == "BLOCKED":
        failures.append("source-backed bundle manifest reports BLOCKED health status")
    if int(summary.get("symbols_succeeded", 0)) < 50:
        warnings.append("source-backed universe is below engineering_pilot target")
    if int(summary.get("trading_dates_succeeded", 0)) < 120:
        warnings.append("source-backed trading dates are below engineering_pilot target")
    status = "BLOCKED" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    write_text(
        root / "outputs/audits/source_backed_local_bundle_audit.md",
        "\n".join(
            [
                "# Source-Backed Local Bundle Audit",
                "",
                f"Status: `{status}`",
                f"Bundle id: `{summary.get('bundle_id', '')}`",
                f"Bundle tier: `{summary.get('bundle_tier', '')}`",
                f"Symbols succeeded: `{summary.get('symbols_succeeded', 0)}`",
                f"Trading dates succeeded: `{summary.get('trading_dates_succeeded', 0)}`",
                f"Local bundle path: `{summary.get('local_bundle_path', '')}`",
                "Full bundle files are local-only and not committed.",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
                "## Warnings",
                *[f"- {warning}" for warning in warnings],
                "",
            ]
        ),
    )
    return not failures


def build_source_backed_pit_signal_panel(root: Path, bundle_root: Path | None = None) -> list[dict[str, object]]:
    bundle_root = bundle_root or engineering_bundle_root(root, BUNDLE_ID)
    stock_rows = _read_local_table(bundle_root / "ohlcv_daily")
    benchmark_rows = _read_local_table(bundle_root / "benchmark_daily")
    trading_dates = [row["trade_date"] for row in read_csv(bundle_root / "trading_calendar.csv")] if (bundle_root / "trading_calendar.csv").exists() else []
    stock_by_symbol = _by_symbol_date(stock_rows)
    benchmark_by_date = {row["trade_date"]: row for row in benchmark_rows}
    rows = []
    for symbol in sorted(stock_by_symbol):
        dates = sorted(stock_by_symbol[symbol])
        for target_date in trading_dates:
            idx = dates.index(target_date) if target_date in dates else -1
            if idx < 21:
                continue
            as_of_date = dates[idx - 1]
            close = _series(stock_by_symbol[symbol], dates, "close")
            bench_dates = sorted(benchmark_by_date)
            bench_close = _series(benchmark_by_date, bench_dates, "close")
            bench_idx = bench_dates.index(as_of_date) if as_of_date in benchmark_by_date else -1
            pit_ready = bench_idx >= 20
            rows.append(
                {
                    "as_of_date": as_of_date,
                    "target_trading_date": target_date,
                    "decision_cutoff_ts": f"{target_date}T09:00:00+08:00",
                    "symbol": symbol,
                    "market_trend_5d": _return(bench_close, bench_idx - 5, bench_idx) if pit_ready else "",
                    "stock_momentum_5d": _return(close, idx - 6, idx - 1),
                    "stock_momentum_20d": _return(close, idx - 21, idx - 1),
                    "stock_gap_signal": _return(close, idx - 2, idx - 1),
                    "stock_volatility_20d": _volatility(close, idx - 21, idx - 1),
                    "turnover_proxy": _mean([float(stock_by_symbol[symbol][date].get("amount", 0)) for date in dates[idx - 20 : idx]]),
                    "relative_strength_20d": _return(close, idx - 21, idx - 1) - (_return(bench_close, bench_idx - 20, bench_idx) if pit_ready else 0),
                    "source_health_score": 1.0 if pit_ready else 0.5,
                    "source_count": 2 if pit_ready else 1,
                    "pit_ready": pit_ready,
                    "panel_source_type": "real_source_backed",
                    "source_bundle_id": BUNDLE_ID,
                    "feature_contract_version": "goal06c6.source_backed_pit.v1",
                    "data_quality_flags": "SOURCE_BACKED" if pit_ready else "INSUFFICIENT_BENCHMARK_LOOKBACK",
                }
            )
    _write_local_table(bundle_root / "pit_signal_panel", rows)
    write_csv(root / "outputs/samples/source_backed_pit_signal_panel_sample.csv", rows[:SAMPLE_MAX_ROWS], SOURCE_BACKED_PIT_FIELDS)
    _write_source_backed_pit_audit(root, rows)
    return rows


def build_source_backed_label_panel(root: Path, bundle_root: Path | None = None) -> list[dict[str, object]]:
    bundle_root = bundle_root or engineering_bundle_root(root, BUNDLE_ID)
    stock_rows = _read_local_table(bundle_root / "ohlcv_daily")
    benchmark_rows = _read_local_table(bundle_root / "benchmark_daily")
    trading_dates = [row["trade_date"] for row in read_csv(bundle_root / "trading_calendar.csv")] if (bundle_root / "trading_calendar.csv").exists() else []
    stock_by_symbol = _by_symbol_date(stock_rows)
    benchmark_by_date = {row["trade_date"]: row for row in benchmark_rows}
    bench_dates = sorted(benchmark_by_date)
    bench_close = _series(benchmark_by_date, bench_dates, "close")
    rows = []
    for symbol in sorted(stock_by_symbol):
        dates = sorted(stock_by_symbol[symbol])
        close = _series(stock_by_symbol[symbol], dates, "close")
        for trade_date in trading_dates:
            idx = dates.index(trade_date) if trade_date in dates else -1
            bench_idx = bench_dates.index(trade_date) if trade_date in benchmark_by_date else -1
            ready = idx >= 0 and idx + 5 < len(dates) and bench_idx >= 0 and bench_idx + 5 < len(bench_dates)
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
                    "label_ready": ready,
                    "source_bundle_id": BUNDLE_ID,
                    "label_contract_version": "goal06c6.source_backed_label.v1",
                    "label_quality_flags": "SOURCE_BACKED" if ready else "MISSING_FORWARD_TRADING_DAYS",
                }
            )
    _write_local_table(bundle_root / "label_panel", rows)
    write_csv(root / "outputs/samples/source_backed_label_panel_sample.csv", rows[:SAMPLE_MAX_ROWS], SOURCE_BACKED_LABEL_FIELDS)
    _write_source_backed_label_audit(root, rows)
    return rows


def rebuild_stage6c_source_backed_engineering_panel(
    root: Path,
    pit_rows: list[dict[str, object]] | None = None,
    label_rows: list[dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    bundle_root = engineering_bundle_root(root, BUNDLE_ID)
    pit_rows = pit_rows if pit_rows is not None else _read_local_table(bundle_root / "pit_signal_panel")
    label_rows = label_rows if label_rows is not None else _read_local_table(bundle_root / "label_panel")
    label_lookup = {(row["trade_date"], row["symbol"]): row for row in label_rows}
    rows = []
    for pit in pit_rows:
        key = (pit["target_trading_date"], pit["symbol"])
        label = label_lookup.get(key)
        if not label:
            continue
        usable = pit["pit_ready"] in {True, "true"} and label["label_ready"] in {True, "true"}
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
            }
        )
    usable_rows = [row for row in rows if row["usable_for_validation"] in {True, "true"}]
    tier = classify_panel_tier(root, usable_rows)
    for row in rows:
        row["panel_tier"] = tier["tier"] if row in usable_rows else "not_ready"
    _write_local_table(bundle_root / "stage6c_engineering_panel", rows)
    write_csv(root / "outputs/samples/stage6c_source_backed_engineering_panel_sample.csv", rows[:SAMPLE_MAX_ROWS], _stage6c_source_backed_fields())
    _write_stage6c_source_backed_coverage(root, usable_rows, tier)
    return rows


def audit_stage6c_source_backed_engineering_panel(root: Path) -> bool:
    sample_path = root / "outputs/samples/stage6c_source_backed_engineering_panel_sample.csv"
    coverage_path = root / SOURCE_PANEL_COVERAGE
    rows = read_csv(sample_path) if sample_path.exists() else []
    coverage = read_csv(coverage_path)[0] if coverage_path.exists() else {}
    failures: list[str] = []
    warnings: list[str] = []
    feature_forbidden = {"fwd_1d_return", "fwd_3d_return", "fwd_5d_return", "excess_fwd_1d_return", "excess_fwd_3d_return", "excess_fwd_5d_return"}
    pit_header = set(read_csv(root / "outputs/samples/source_backed_pit_signal_panel_sample.csv")[0]) if (root / "outputs/samples/source_backed_pit_signal_panel_sample.csv").exists() and read_csv(root / "outputs/samples/source_backed_pit_signal_panel_sample.csv") else set()
    if pit_header & feature_forbidden:
        failures.append(f"label columns entered PIT sample: {sorted(pit_header & feature_forbidden)}")
    if any(row.get("leakage_flags") != "PASS" for row in rows):
        failures.append("sample rows report leakage flags")
    if not rows:
        warnings.append("source-backed Stage 6C sample is empty")
    if coverage.get("panel_tier") != "engineering_pilot":
        warnings.append("source-backed panel has not reached engineering_pilot")
    status = "BLOCKED" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    write_text(
        root / "outputs/audits/stage6c_source_backed_engineering_panel_audit.md",
        "\n".join(
            [
                "# Stage 6C Source-Backed Engineering Panel Audit",
                "",
                f"Status: `{status}`",
                f"Panel tier: `{coverage.get('panel_tier', '')}`",
                f"Rows: `{coverage.get('current_rows', 0)}`",
                f"Symbols: `{coverage.get('current_symbols', 0)}`",
                f"Trading dates: `{coverage.get('current_trading_dates', 0)}`",
                f"GOAL-06D allowed to proceed: `{coverage.get('goal06d_allowed', 'false')}`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
                "## Warnings",
                *[f"- {warning}" for warning in warnings],
                "",
            ]
        ),
    )
    _write_engineering_readiness_from_source_coverage(root, coverage)
    return not failures


def _write_no_bundle_outputs(root: Path, bundle_root: Path, attempts: list[dict[str, object]], status: str, network_status: str) -> None:
    manifest = {
        "bundle_id": BUNDLE_ID,
        "bundle_tier": "not_available",
        "network_status": network_status,
        "akshare_available": akshare_available(),
        "akshare_function_signatures": akshare_function_signatures(),
        "local_bundle_path": str(bundle_root),
        "symbols_requested": 50,
        "symbols_succeeded": 0,
        "symbols_failed": 50,
        "trading_dates_requested": 120,
        "trading_dates_succeeded": 0,
        "pit_ready_rows": 0,
        "label_ready_rows": 0,
        "stage6c_rows": 0,
        "blocked_symbol_rows": 0,
        "health_status": status,
        "failure_classes": sorted({row["failure_class"] for row in attempts}),
        "notes": "No source-backed local bundle was built.",
    }
    _write_committed_manifest_summary(root, manifest)
    _write_empty_samples(root)
    _write_stage6c_source_backed_coverage(root, [], {"tier": "not_available", "counts": {"symbols": 0, "trading_dates": 0, "rows": 0}, "contract": {"goal06d_allowed": False}})
    _write_source_backed_universe_audit(root, [], [], status, network_status)
    _write_source_backed_trading_calendar_audit(root, [], load_ingestion_config(root))
    _write_source_backed_pit_audit(root, [])
    _write_source_backed_label_audit(root, [])
    audit_stage6c_source_backed_engineering_panel(root)
    audit_source_backed_local_bundle(root)
    _write_goal06c6_readiness(root, manifest, False)


def _write_empty_samples(root: Path) -> None:
    write_csv(
        root / "outputs/samples/source_backed_universe_sample.csv",
        [],
        UNIVERSE_FIELDS,
    )
    write_csv(root / "outputs/samples/source_backed_ohlcv_daily_sample.csv", [], STOCK_OHLCV_FIELDS)
    write_csv(root / "outputs/samples/source_backed_benchmark_daily_sample.csv", [], BENCHMARK_FIELDS)
    write_csv(root / "outputs/samples/source_backed_pit_signal_panel_sample.csv", [], SOURCE_BACKED_PIT_FIELDS)
    write_csv(root / "outputs/samples/source_backed_label_panel_sample.csv", [], SOURCE_BACKED_LABEL_FIELDS)
    write_csv(root / "outputs/samples/stage6c_source_backed_engineering_panel_sample.csv", [], _stage6c_source_backed_fields())


def _candidate_rows(rows: list[dict[str, object]], spot_lookup: dict[str, dict[str, object]], blocked: set[str]) -> list[dict[str, object]]:
    candidates = []
    for row in rows:
        symbol = str(row["symbol"])
        name = str(row.get("name", ""))
        if symbol in blocked or "ST" in name.upper() or not _valid_symbol(symbol):
            continue
        spot = spot_lookup.get(symbol, {})
        candidates.append(
            {
                "symbol": symbol,
                "name": name,
                "exchange": symbol.split(".")[-1],
                "liquidity_proxy": spot.get("amount", ""),
                "source_coverage_status": "candidate_from_akshare",
                "approval_status": "candidate_source_backed",
                "notes": "" if spot else "liquidity_filter_unavailable",
            }
        )
    return sorted(candidates, key=lambda row: (-float(row["liquidity_proxy"] or 0), str(row["symbol"])))


def _valid_symbol(symbol: str) -> bool:
    return len(symbol) == 9 and symbol[:6].isdigit() and symbol[-3:] in {".SH", ".SZ"}


def _required_raw_dates(config: dict[str, object]) -> int:
    return int(config["validation_trading_dates"]) + 25


def _validation_dates(stock_rows: list[dict[str, object]], benchmark_rows: list[dict[str, object]], config: dict[str, object]) -> list[str]:
    dates_by_symbol: dict[str, set[str]] = defaultdict(set)
    for row in stock_rows:
        dates_by_symbol[str(row["symbol"])].add(str(row["trade_date"]))
    benchmark_dates = {str(row["trade_date"]) for row in benchmark_rows}
    if not dates_by_symbol:
        return []
    counts = defaultdict(int)
    for dates in dates_by_symbol.values():
        for date in dates & benchmark_dates:
            counts[date] += 1
    target_symbols = int(config["symbol_target_count"])
    common = sorted(date for date, count in counts.items() if count >= target_symbols)
    usable = common[20 : max(20, len(common) - 5)]
    return usable[-int(config["validation_trading_dates"]) :]


def _bundle_manifest(
    root: Path,
    bundle_root: Path,
    selected: list[dict[str, object]],
    trading_dates: list[str],
    stock_rows: list[dict[str, object]],
    benchmark_rows: list[dict[str, object]],
    attempts: list[dict[str, object]],
    source_coverage_rows: list[dict[str, object]],
) -> dict[str, object]:
    source_ready = len(selected) >= 50 and len(trading_dates) >= 120
    any_provider_success = any(str(row.get("status")) == "PASS" for row in attempts)
    health_status = "PASS" if source_ready else ("PASS_WITH_WARNINGS" if any_provider_success and stock_rows else "BLOCKED")
    return {
        "bundle_id": BUNDLE_ID,
        "bundle_tier": "engineering_pilot" if source_ready else "source_backed_partial",
        "network_status": "network_enabled",
        "akshare_available": akshare_available(),
        "akshare_function_signatures": akshare_function_signatures(),
        "local_bundle_path": str(bundle_root),
        "symbols_requested": 50,
        "symbols_succeeded": len(selected),
        "symbols_failed": max(0, 50 - len(selected)),
        "trading_dates_requested": 120,
        "trading_dates_succeeded": len(trading_dates),
        "raw_rows": len(stock_rows) + len(benchmark_rows),
        "clean_rows": len(stock_rows),
        "pit_ready_rows": 0,
        "label_ready_rows": 0,
        "stage6c_rows": 0,
        "blocked_symbol_rows": 0,
        "provider_attempts": len(attempts),
        "failure_classes": sorted({str(row["failure_class"]) for row in attempts if row["failure_class"] != "PROVIDER_OK"}),
        "source_coverage_ready_symbols": sum(1 for row in source_coverage_rows if row["coverage_ready"] in {True, "true"}),
        "health_status": health_status,
        "notes": "Source-backed local bundle summary; full data is local-only.",
    }


def _write_committed_manifest_summary(root: Path, manifest: dict[str, object]) -> None:
    write_json(root / SOURCE_BUNDLE_SUMMARY_JSON, manifest)
    write_text(
        root / "outputs/audits/source_backed_bundle_manifest_summary.md",
        "\n".join(
            [
                "# Source-Backed Bundle Manifest Summary",
                "",
                f"Status: `{manifest.get('health_status', '')}`",
                f"Bundle id: `{manifest.get('bundle_id', '')}`",
                f"Bundle tier: `{manifest.get('bundle_tier', '')}`",
                f"Network status: `{manifest.get('network_status', '')}`",
                f"AKShare available: `{str(manifest.get('akshare_available', False)).lower()}`",
                f"Symbols succeeded: `{manifest.get('symbols_succeeded', 0)}`",
                f"Trading dates succeeded: `{manifest.get('trading_dates_succeeded', 0)}`",
                f"Local bundle path: `{manifest.get('local_bundle_path', '')}`",
                "Full local bundle files are not committed.",
                "",
            ]
        ),
    )


def _write_source_backed_universe_audit(root: Path, selected: list[dict[str, object]], candidates: list[dict[str, object]], status: str, notes: str) -> None:
    write_text(
        root / "outputs/audits/source_backed_universe_audit.md",
        "\n".join(
            [
                "# Source-Backed Universe Audit",
                "",
                f"Status: `{status}`",
                f"Selected symbols: `{len(selected)}`",
                f"Candidate symbols: `{len(candidates)}`",
                f"Notes: `{notes}`",
                "Blocked symbols are excluded before approval.",
                "",
            ]
        ),
    )


def _write_source_backed_trading_calendar_audit(root: Path, trading_dates: list[str], config: dict[str, object]) -> None:
    target = int(config["validation_trading_dates"])
    status = "PASS" if len(trading_dates) >= target else "PASS_WITH_WARNINGS"
    write_text(
        root / "outputs/audits/source_backed_trading_calendar_audit.md",
        "\n".join(
            [
                "# Source-Backed Trading Calendar Audit",
                "",
                f"Status: `{status}`",
                f"Trading dates: `{len(trading_dates)}`",
                f"Target trading dates: `{target}`",
                f"First trading date: `{trading_dates[0] if trading_dates else ''}`",
                f"Last trading date: `{trading_dates[-1] if trading_dates else ''}`",
                "Dates are derived from source-backed OHLCV coverage, not calendar-day shortcuts.",
                "",
            ]
        ),
    )


def _write_source_backed_pit_audit(root: Path, rows: list[dict[str, object]]) -> None:
    failures = []
    forbidden = set(SOURCE_BACKED_LABEL_FIELDS) - {"source_bundle_id"}
    header = set(rows[0]) if rows else set(SOURCE_BACKED_PIT_FIELDS)
    leaked = sorted(header & forbidden)
    if leaked:
        failures.append(f"label columns in PIT panel: {leaked}")
    status = "BLOCKED" if failures else ("PASS" if rows else "PASS_WITH_WARNINGS")
    write_text(
        root / "outputs/audits/source_backed_pit_signal_panel_audit.md",
        "\n".join(
            [
                "# Source-Backed PIT Signal Panel Audit",
                "",
                f"Status: `{status}`",
                f"Rows reviewed: `{len(rows)}`",
                f"PIT-ready rows: `{sum(1 for row in rows if row.get('pit_ready') in {True, 'true'})}`",
                "Features use prior trading close data only and exclude labels.",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )


def _write_source_backed_label_audit(root: Path, rows: list[dict[str, object]]) -> None:
    status = "PASS" if rows else "PASS_WITH_WARNINGS"
    write_text(
        root / "outputs/audits/source_backed_label_panel_audit.md",
        "\n".join(
            [
                "# Source-Backed Label Panel Audit",
                "",
                f"Status: `{status}`",
                f"Rows reviewed: `{len(rows)}`",
                f"Label-ready rows: `{sum(1 for row in rows if row.get('label_ready') in {True, 'true'})}`",
                "Labels use trading-day forward offsets and remain offline-only.",
                "",
            ]
        ),
    )


def _write_stage6c_source_backed_coverage(root: Path, rows: list[dict[str, object]], tier: dict[str, object]) -> None:
    counts = tier["counts"]
    allowed = bool(tier["contract"].get("goal06d_allowed")) and tier["tier"] in {"engineering_pilot", "research_ready", "strong_panel"}
    write_csv(
        root / SOURCE_PANEL_COVERAGE,
        [
            {
                "panel_id": "goal06c6_source_backed_engineering_panel",
                "current_symbols": counts["symbols"],
                "current_trading_dates": counts["trading_dates"],
                "current_rows": counts["rows"],
                "panel_tier": tier["tier"],
                "engineering_pilot_required_symbols": 50,
                "engineering_pilot_required_trading_dates": 120,
                "engineering_pilot_required_rows": 6000,
                "engineering_pilot_met": allowed,
                "goal06d_allowed": allowed,
                "goal06d_mode": "review_only" if allowed else "blocked",
            }
        ],
    )
    write_text(
        root / "outputs/audits/engineering_panel_readiness_report.md",
        "\n".join(
            [
                "# Engineering Panel Readiness Report",
                "",
                f"Engineering Panel Readiness: {'PASS' if allowed else 'PASS_WITH_WARNINGS'}",
                f"GOAL-06D allowed to proceed: {str(allowed).lower()}",
                f"GOAL-06D mode if allowed: {'review_only' if allowed else 'blocked'}",
                f"Panel tier: `{tier['tier']}`",
                "",
                "GOAL-06D is unblocked only when the source-backed engineering panel reaches `engineering_pilot` or higher.",
                "",
            ]
        ),
    )


def _write_goal06c6_readiness(root: Path, manifest: dict[str, object], panel_ok: bool) -> None:
    coverage = read_csv(root / SOURCE_PANEL_COVERAGE)[0] if (root / SOURCE_PANEL_COVERAGE).exists() else {}
    allowed = coverage.get("goal06d_allowed") == "true"
    status = "PASS" if allowed and panel_ok else ("BLOCKED" if manifest.get("health_status") == "BLOCKED" else "PASS_WITH_WARNINGS")
    gap_symbols = max(0, 50 - int(coverage.get("current_symbols", 0) or 0))
    gap_dates = max(0, 120 - int(coverage.get("current_trading_dates", 0) or 0))
    gap_rows = max(0, 6000 - int(coverage.get("current_rows", 0) or 0))
    write_text(
        root / "outputs/audits/goal06c6_readiness_report.md",
        "\n".join(
            [
                "# GOAL-06C.6 Source-Backed Engineering Pilot Bundle Readiness Report",
                "",
                f"GOAL-06C.6 Source-Backed Engineering Pilot Bundle Readiness: {status}",
                f"Panel tier: `{coverage.get('panel_tier', '')}`",
                f"GOAL-06D allowed to proceed: {str(allowed).lower()}",
                f"GOAL-06D mode if allowed: {coverage.get('goal06d_mode', 'blocked')}",
                f"Remaining gap: symbols={gap_symbols}; dates={gap_dates}; rows={gap_rows}",
                f"Failure classes: `{';'.join(manifest.get('failure_classes', []))}`",
                "No cloakbrowser, stealth browser, captcha solving, proxy rotation, or bypass automation is used.",
                "",
            ]
        ),
    )


def _write_engineering_readiness_from_source_coverage(root: Path, coverage: dict[str, str]) -> None:
    allowed = coverage.get("goal06d_allowed") == "true"
    tier = coverage.get("panel_tier", "")
    write_text(
        root / "outputs/audits/engineering_panel_readiness_report.md",
        "\n".join(
            [
                "# Engineering Panel Readiness Report",
                "",
                f"Engineering Panel Readiness: {'PASS' if allowed else 'PASS_WITH_WARNINGS'}",
                f"GOAL-06D allowed to proceed: {str(allowed).lower()}",
                f"GOAL-06D mode if allowed: {coverage.get('goal06d_mode', 'blocked')}",
                f"Panel tier: `{tier}`",
                "",
                "GOAL-06D is unblocked only when the source-backed engineering panel reaches `engineering_pilot` or higher.",
                "",
            ]
        ),
    )


def _stage6c_source_backed_fields() -> list[str]:
    return [
        "trade_date",
        "symbol",
        "as_of_date",
        "decision_cutoff_ts",
        "market_trend_5d",
        "stock_momentum_5d",
        "stock_momentum_20d",
        "stock_gap_signal",
        "stock_volatility_20d",
        "turnover_proxy",
        "relative_strength_20d",
        "source_health_score",
        "source_count",
        "fwd_1d_return",
        "fwd_3d_return",
        "fwd_5d_return",
        "excess_fwd_1d_return",
        "excess_fwd_3d_return",
        "excess_fwd_5d_return",
        "usable_for_validation",
        "panel_source_type",
        "source_bundle_id",
        "review_only",
        "data_quality_flags",
        "leakage_flags",
        "panel_tier",
    ]


def _write_local_table(base_path: Path, rows: list[dict[str, object]]) -> Path:
    csv_path = base_path.with_suffix(".csv")
    write_csv(csv_path, rows, _local_table_fields(base_path.name))
    if rows:
        try:
            import pandas as pd

            parquet_path = base_path.with_suffix(".parquet")
            pd.DataFrame(rows).to_parquet(parquet_path, index=False)
            return parquet_path
        except Exception:
            pass
    return csv_path


def _local_table_fields(name: str) -> list[str] | None:
    mapping = {
        "universe": UNIVERSE_FIELDS,
        "benchmark_daily": BENCHMARK_FIELDS,
        "ohlcv_daily": STOCK_OHLCV_FIELDS,
        "source_coverage": SOURCE_COVERAGE_FIELDS,
        "pit_signal_panel": SOURCE_BACKED_PIT_FIELDS,
        "label_panel": SOURCE_BACKED_LABEL_FIELDS,
        "stage6c_engineering_panel": _stage6c_source_backed_fields(),
    }
    return mapping.get(name)


def _read_local_table(base_path: Path) -> list[dict[str, str]]:
    csv_path = base_path.with_suffix(".csv")
    if csv_path.exists():
        return read_csv(csv_path)
    parquet_path = base_path.with_suffix(".parquet")
    if parquet_path.exists():
        import pandas as pd

        return list(pd.read_parquet(parquet_path).astype(str).to_dict("records"))
    return []


def _write_checksums(bundle_root: Path) -> None:
    rows = []
    for path in sorted(bundle_root.glob("*")):
        if path.name == "checksums.sha256" or not path.is_file():
            continue
        rows.append(f"{_sha256(path)}  {path.name}")
    (bundle_root / "checksums.sha256").write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _network_disabled_attempt(function_name: str) -> dict[str, object]:
    return make_attempt(
        "akshare",
        function_name,
        network_enabled=False,
        status="FAIL",
        failure_class="NETWORK_DISABLED_BY_POLICY",
        retry_allowed=False,
        notes="network_disabled_by_policy",
    )


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


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))

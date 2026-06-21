from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.io import read_csv, write_csv, write_text
from ashare_premarket.features.pit_signal_store import build_pit_signal_snapshot
from ashare_premarket.universe.governance import load_approved_symbols, load_blocked_symbols

OUTPUT = "outputs/features/engineering_pit_signal_panel_sample.csv"
SOURCE_BUNDLE_ID = "contract_demo_current_clean_bootstrap"
FEATURE_COLUMNS = [
    "market_trend_5d",
    "sector_momentum_5d",
    "stock_gap_signal",
    "event_count_pit",
    "source_health_score",
    "source_count",
]
PIT_FIELDNAMES = [
    "as_of_date",
    "target_trading_date",
    "decision_cutoff_ts",
    "symbol",
    *FEATURE_COLUMNS,
    "pit_ready",
    "panel_source_type",
    "source_bundle_id",
    "data_quality_flags",
]


def build_engineering_pit_signal_panel(root: Path) -> Path:
    source_path = root / "outputs/features/daily_premarket_signal_snapshot.csv"
    if not source_path.exists():
        build_pit_signal_snapshot(root)
    approved = set(load_approved_symbols(root))
    blocked = set(load_blocked_symbols(root))
    rows = []
    for row in sorted(read_csv(source_path), key=lambda item: (item["target_trading_date"], item["symbol"])):
        if row["symbol"] not in approved or row["symbol"] in blocked:
            continue
        rows.append(
            {
                "as_of_date": row["as_of_date"],
                "target_trading_date": row["target_trading_date"],
                "decision_cutoff_ts": row["decision_cutoff_ts"],
                "symbol": row["symbol"],
                "market_trend_5d": row["market_trend_5d"],
                "sector_momentum_5d": row["sector_momentum_5d"],
                "stock_gap_signal": row["stock_gap_signal"],
                "event_count_pit": row["event_count_pit"],
                "source_health_score": row["source_health_score"],
                "source_count": row["source_count"],
                "pit_ready": row["pit_ready"],
                "panel_source_type": "clean_bootstrap_fixture",
                "source_bundle_id": SOURCE_BUNDLE_ID,
                "data_quality_flags": "CLEAN_BOOTSTRAP_FIXTURE;CONTRACT_DEMO",
            }
        )
    path = root / OUTPUT
    write_csv(path, rows, PIT_FIELDNAMES)
    return path


def audit_engineering_pit_signal_panel(root: Path) -> bool:
    path = root / OUTPUT
    if not path.exists():
        build_engineering_pit_signal_panel(root)
    rows = read_csv(path)
    approved = set(load_approved_symbols(root))
    blocked = set(load_blocked_symbols(root))
    failures: list[str] = []
    warnings: list[str] = []
    if not rows:
        failures.append("engineering PIT panel sample is empty")
    if any(row["symbol"] not in approved or row["symbol"] in blocked for row in rows):
        failures.append("engineering PIT panel contains non-approved or blocked symbols")
    label_like_columns = sorted(
        column for column in (rows[0].keys() if rows else PIT_FIELDNAMES)
        if column.startswith("fwd_") or column.endswith("_return") or column.startswith("label")
    )
    if label_like_columns:
        failures.append(f"signal panel includes label-like columns: {label_like_columns}")
    if any(row["panel_source_type"] != "clean_bootstrap_fixture" for row in rows):
        failures.append("unexpected panel_source_type in clean bootstrap sample")
    symbols = {row["symbol"] for row in rows}
    dates = {row["target_trading_date"] for row in rows}
    if len(rows) < 6000 or len(symbols) < 50 or len(dates) < 120:
        warnings.append("engineering PIT panel sample is contract_demo size, not engineering_pilot")
    status = "BLOCKED" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    write_text(
        root / "outputs/audits/engineering_pit_signal_panel_audit.md",
        "\n".join(
            [
                "# Engineering PIT Signal Panel Audit",
                "",
                f"Status: `{status}`",
                f"Rows reviewed: `{len(rows)}`",
                f"Symbols reviewed: `{len(symbols)}`",
                f"Trading dates reviewed: `{len(dates)}`",
                "Logical grain: `target_trading_date + symbol`.",
                "Labels and future returns are excluded from signal features.",
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

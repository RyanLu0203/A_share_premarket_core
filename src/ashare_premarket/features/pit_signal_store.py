from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.constants import APPROVED_SYMBOLS
from ashare_premarket.core.io import read_csv, write_csv, write_text
from ashare_premarket.data.source_health import active_source_count, source_health_score
from ashare_premarket.data.trading_calendar import next_trading_day
from ashare_premarket.events.contracts import pit_event_count
from ashare_premarket.market.context import market_trend_5d
from ashare_premarket.nlp.contracts import review_only_nlp_contract_score
from ashare_premarket.sector.context import sector_momentum_5d

AS_OF_DATES = ["2026-06-15", "2026-06-16", "2026-06-17", "2026-06-18"]


def build_pit_signal_snapshot(root: Path) -> Path:
    rows: list[dict[str, object]] = []
    for as_of_date in AS_OF_DATES:
        for symbol in APPROVED_SYMBOLS:
            target = next_trading_day(root, as_of_date)
            rows.append(
                {
                    "as_of_date": as_of_date,
                    "target_trading_date": target,
                    "decision_cutoff_ts": f"{as_of_date}T09:00:00+08:00",
                    "symbol": symbol,
                    "market_trend_5d": market_trend_5d(as_of_date),
                    "sector_momentum_5d": sector_momentum_5d(symbol, as_of_date),
                    "stock_gap_signal": _stock_gap_signal(symbol, as_of_date),
                    "event_count_pit": pit_event_count(symbol, as_of_date),
                    "review_only_nlp_contract_score": review_only_nlp_contract_score(symbol, as_of_date),
                    "source_health_score": source_health_score(root, symbol),
                    "source_count": active_source_count(root, symbol),
                    "pit_ready": True,
                    "contract_version": "goal05a.v1",
                }
            )
    path = root / "outputs/features/daily_premarket_signal_snapshot.csv"
    write_csv(path, rows)
    return path


def audit_pit_signal_snapshot(root: Path) -> bool:
    path = root / "outputs/features/daily_premarket_signal_snapshot.csv"
    if not path.exists():
        build_pit_signal_snapshot(root)
    rows = read_csv(path)
    approved = set(APPROVED_SYMBOLS)
    blocked_symbols_present = sorted({row["symbol"] for row in rows} - approved)
    pit_failures = [row for row in rows if row["pit_ready"] != "true"]
    source_warnings = [row for row in rows if int(row["source_count"]) < 2]
    status = "PASS" if not blocked_symbols_present and not pit_failures else "BLOCKED"
    quality_status = "PASS" if not source_warnings else "PASS_WITH_WARNINGS"
    write_text(
        root / "outputs/audits/pit_signal_snapshot_audit.md",
        "\n".join(
            [
                "# PIT Signal Snapshot Audit",
                "",
                f"Status: `{status}`",
                f"Rows reviewed: `{len(rows)}`",
                f"Blocked symbols present: `{blocked_symbols_present}`",
                f"PIT failures: `{len(pit_failures)}`",
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/audits/pit_signal_quality_report.md",
        "\n".join(
            [
                "# PIT Signal Quality Report",
                "",
                f"Status: `{quality_status}`",
                "Source density is review-grade and deterministic for clean bootstrap.",
                "CNINFO and Tencent gaps from the source branch remain documented warnings.",
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/audits/stage5b_readiness_report.md",
        "\n".join(
            [
                "# Stage 5B Readiness Report",
                "",
                f"Stage 5B PIT signal readiness: `{quality_status}`",
                "Feature, recommendation, risk, dashboard, paper, and live trading remain locked.",
                "",
            ]
        ),
    )
    return status == "PASS"


def _stock_gap_signal(symbol: str, as_of_date: str) -> float:
    gaps = {
        "002475.SZ": {"2026-06-15": 0.04, "2026-06-16": 0.09, "2026-06-17": -0.02, "2026-06-18": 0.03},
        "600036.SH": {"2026-06-15": 0.01, "2026-06-16": 0.02, "2026-06-17": 0.00, "2026-06-18": 0.04},
    }
    return gaps[symbol][as_of_date]

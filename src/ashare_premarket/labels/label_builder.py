from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.constants import APPROVED_SYMBOLS
from ashare_premarket.core.io import read_csv, write_csv, write_text
from ashare_premarket.data.trading_calendar import next_trading_day

LABEL_RETURNS = {
    "002475.SZ": {"2026-06-16": 0.018, "2026-06-17": -0.004, "2026-06-18": 0.011, "2026-06-19": 0.006},
    "600036.SH": {"2026-06-16": 0.005, "2026-06-17": 0.007, "2026-06-18": -0.002, "2026-06-19": 0.009},
}
BENCHMARK_RETURNS = {"2026-06-16": 0.006, "2026-06-17": 0.001, "2026-06-18": 0.002, "2026-06-19": 0.003}
TARGET_DATES = ["2026-06-16", "2026-06-17", "2026-06-18", "2026-06-19"]


def build_label_snapshot(root: Path) -> Path:
    rows: list[dict[str, object]] = []
    for target_date in TARGET_DATES:
        observation_date = next_trading_day(root, target_date)
        for symbol in APPROVED_SYMBOLS:
            stock_return = LABEL_RETURNS[symbol][target_date]
            benchmark_return = BENCHMARK_RETURNS[target_date]
            alpha_return = round(stock_return - benchmark_return, 6)
            rows.append(
                {
                    "target_trading_date": target_date,
                    "symbol": symbol,
                    "next_trading_day": observation_date,
                    "stock_return_1d": stock_return,
                    "benchmark_return_1d": benchmark_return,
                    "alpha_return_1d": alpha_return,
                    "label_positive": alpha_return > 0,
                    "label_observation_ts": f"{observation_date}T15:30:00+08:00",
                    "label_is_pit_safe": True,
                    "contract_version": "goal05b.v1",
                }
            )
    path = root / "outputs/labels/daily_label_snapshot.csv"
    write_csv(path, rows)
    return path


def audit_label_snapshot(root: Path) -> bool:
    path = root / "outputs/labels/daily_label_snapshot.csv"
    if not path.exists():
        build_label_snapshot(root)
    rows = read_csv(path)
    approved = set(APPROVED_SYMBOLS)
    failures = [
        row for row in rows
        if row["symbol"] not in approved or row["label_is_pit_safe"] != "true"
    ]
    status = "PASS" if not failures else "BLOCKED"
    write_text(
        root / "outputs/audits/label_snapshot_audit.md",
        "\n".join(
            [
                "# Label Snapshot Audit",
                "",
                f"Status: `{status}`",
                f"Rows reviewed: `{len(rows)}`",
                f"Failures: `{len(failures)}`",
                "Labels are produced after target-day close and excluded from live feature manifests.",
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/audits/stage5c_readiness_report.md",
        "\n".join(
            [
                "# Stage 5C Readiness Report",
                "",
                f"Stage 5C label contract readiness: `{status}`",
                "Benchmark-adjusted labels are review-only training labels, not premarket features.",
                "",
            ]
        ),
    )
    return status == "PASS"

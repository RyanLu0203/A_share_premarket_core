from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.io import read_csv, write_csv, write_text
from ashare_premarket.labels.label_builder import build_label_snapshot
from ashare_premarket.universe.governance import load_approved_symbols, load_blocked_symbols

OUTPUT = "outputs/labels/engineering_label_panel_sample.csv"
SOURCE_BUNDLE_ID = "contract_demo_current_clean_bootstrap"
LABEL_FIELDNAMES = [
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


def build_engineering_label_panel(root: Path) -> Path:
    source_path = root / "outputs/labels/daily_label_snapshot.csv"
    if not source_path.exists():
        build_label_snapshot(root)
    approved = set(load_approved_symbols(root))
    blocked = set(load_blocked_symbols(root))
    rows = []
    for row in sorted(read_csv(source_path), key=lambda item: (item["target_trading_date"], item["symbol"])):
        if row["symbol"] not in approved or row["symbol"] in blocked:
            continue
        rows.append(
            {
                "trade_date": row["target_trading_date"],
                "symbol": row["symbol"],
                "fwd_1d_return": row["stock_return_1d"],
                "fwd_3d_return": "",
                "fwd_5d_return": "",
                "benchmark_fwd_1d_return": row["benchmark_return_1d"],
                "benchmark_fwd_3d_return": "",
                "benchmark_fwd_5d_return": "",
                "excess_fwd_1d_return": row["alpha_return_1d"],
                "excess_fwd_3d_return": "",
                "excess_fwd_5d_return": "",
                "label_ready": row["label_is_pit_safe"],
                "source_bundle_id": SOURCE_BUNDLE_ID,
                "label_contract_version": "goal06c5.label_panel.v1",
                "label_quality_flags": "MISSING_3D_LABEL;MISSING_5D_LABEL;CLEAN_BOOTSTRAP_FIXTURE",
            }
        )
    path = root / OUTPUT
    write_csv(path, rows, LABEL_FIELDNAMES)
    return path


def audit_engineering_label_panel(root: Path) -> bool:
    path = root / OUTPUT
    if not path.exists():
        build_engineering_label_panel(root)
    rows = read_csv(path)
    approved = set(load_approved_symbols(root))
    blocked = set(load_blocked_symbols(root))
    failures: list[str] = []
    warnings: list[str] = []
    if not rows:
        failures.append("engineering label panel sample is empty")
    if any(row["symbol"] not in approved or row["symbol"] in blocked for row in rows):
        failures.append("engineering label panel contains non-approved or blocked symbols")
    if any(row["fwd_3d_return"] or row["fwd_5d_return"] for row in rows):
        failures.append("3d/5d labels should not be fabricated in the clean bootstrap sample")
    if any(row["label_ready"] != "true" for row in rows):
        warnings.append("one or more 1d labels are not ready")
    if any("CLEAN_BOOTSTRAP_FIXTURE" in row["label_quality_flags"] for row in rows):
        warnings.append("engineering label panel sample is fixture-backed and missing 3d/5d horizons")
    status = "BLOCKED" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    write_text(
        root / "outputs/audits/engineering_label_panel_audit.md",
        "\n".join(
            [
                "# Engineering Label Panel Audit",
                "",
                f"Status: `{status}`",
                f"Rows reviewed: `{len(rows)}`",
                f"Symbols reviewed: `{len({row['symbol'] for row in rows})}`",
                f"Trading dates reviewed: `{len({row['trade_date'] for row in rows})}`",
                "Logical grain: `trade_date + symbol`.",
                "Only the existing 1d clean-bootstrap label is populated; 3d/5d fields stay blank instead of fabricated.",
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

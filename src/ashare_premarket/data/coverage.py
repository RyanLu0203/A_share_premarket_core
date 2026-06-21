from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from ashare_premarket.core.io import read_csv, write_csv, write_text
from ashare_premarket.features.pit_signal_store import build_pit_signal_snapshot
from ashare_premarket.labels.label_builder import build_label_snapshot

SOURCE_COVERAGE_CONFIG = "configs/providers/source_coverage_config.yaml"
PROVIDER_REGISTRY = "configs/providers/provider_registry.yaml"
PROVIDER_INGESTION_CONTRACT = "configs/providers/provider_ingestion_contract.yaml"


def audit_data_source_coverage(root: Path) -> bool:
    approved = read_csv(root / "configs/universe/approved_symbols.csv")
    blocked = read_csv(root / "configs/universe/blocked_symbols.csv")
    candidates = read_csv(root / "configs/universe/candidate_symbols.csv")
    calendar = read_csv(root / "configs/project/trading_calendar.csv")
    source_rows = read_csv(root / "configs/providers/source_health_contract.csv")
    stage6c = read_csv(root / "outputs/stage6c/STAGE6C_expanded_validation_dataset.csv")
    pit_rows = _ensure_pit_rows(root)
    label_rows = _ensure_label_rows(root)
    targets = _load_json(root / SOURCE_COVERAGE_CONFIG)["engineering_pilot_targets"]

    approved_symbols = sorted(row["symbol"] for row in approved)
    blocked_symbols = {row["symbol"] for row in blocked}
    stage6c_dates = sorted({row["trade_date"] for row in stage6c})
    trading_dates = sorted(row["date"] for row in calendar if row.get("is_trading_day") == "true")
    proposed_candidates = [
        row for row in candidates
        if row.get("approval_status") == "proposed" and row.get("is_blocked") != "true"
    ]
    pit_ready_rows = [row for row in pit_rows if row.get("pit_ready") == "true"]
    label_ready_rows = [row for row in label_rows if row.get("label_is_pit_safe") == "true"]
    blocked_stage_rows = [row for row in stage6c if row["symbol"] in blocked_symbols]
    failures: list[str] = []
    warnings: list[str] = []

    if blocked_stage_rows:
        failures.append("blocked symbols appear in Stage 6C validation rows")
    if len(approved_symbols) < int(targets["symbols"]):
        warnings.append("approved universe is below engineering_pilot symbol target")
    if len(stage6c_dates) < int(targets["trading_dates"]):
        warnings.append("Stage 6C validation dates are below engineering_pilot target")
    if len(stage6c) < int(targets["rows"]):
        warnings.append("Stage 6C rows are below engineering_pilot target")

    _write_source_symbol_matrix(root, source_rows, approved_symbols)
    _write_source_date_matrix(root, source_rows, stage6c_dates, approved_symbols)
    _write_source_field_matrix(root, source_rows)
    _write_symbol_availability_summary(root, source_rows, pit_rows, label_rows, approved_symbols)
    _write_source_availability_summary(root, source_rows, approved_symbols)
    _write_universe_expansion_audit(root, approved_symbols, blocked, proposed_candidates, targets)
    _write_trading_calendar_expansion_audit(root, trading_dates, stage6c_dates, targets)
    _write_provider_ingestion_contract_audit(root)
    _write_source_gap_analysis(
        root,
        approved_count=len(approved_symbols),
        candidate_count=len(proposed_candidates),
        current_dates=len(stage6c_dates),
        current_rows=len(stage6c),
        pit_ready_count=len(pit_ready_rows),
        label_ready_count=len(label_ready_rows),
        targets=targets,
    )

    status = "BLOCKED" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    write_text(
        root / "outputs/audits/data_source_coverage_audit.md",
        "\n".join(
            [
                "# Data Source Coverage Audit",
                "",
                f"Status: `{status}`",
                "",
                f"number of sources: `{len({row['source_id'] for row in source_rows})}`",
                f"number of approved symbols: `{len(approved_symbols)}`",
                f"number of candidate symbols: `{len(proposed_candidates)}`",
                f"number of blocked symbols: `{len(blocked_symbols)}`",
                "",
                f"current_approved_symbols: `{len(approved_symbols)}`",
                f"current_trading_dates: `{len(stage6c_dates)}`",
                f"configured_trading_dates: `{len(trading_dates)}`",
                f"current_pit_ready_rows: `{len(pit_ready_rows)}`",
                f"current_label_ready_rows: `{len(label_ready_rows)}`",
                f"current_stage6c_rows: `{len(stage6c)}`",
                f"target_engineering_pilot_symbols: `{targets['symbols']}`",
                f"target_engineering_pilot_dates: `{targets['trading_dates']}`",
                f"target_engineering_pilot_rows: `{targets['rows']}`",
                f"coverage_gap_to_engineering_pilot: `symbols={max(0, int(targets['symbols']) - len(approved_symbols))};dates={max(0, int(targets['trading_dates']) - len(stage6c_dates))};rows={max(0, int(targets['rows']) - len(stage6c))}`",
                "source_x_field_availability: `outputs/audits/source_field_coverage_matrix.csv`",
                "",
                "The current clean repository has deterministic fixture coverage only. Provider ingestion is contract-defined and network-disabled by default.",
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


def _ensure_pit_rows(root: Path) -> list[dict[str, str]]:
    path = root / "outputs/features/daily_premarket_signal_snapshot.csv"
    if not path.exists():
        build_pit_signal_snapshot(root)
    return read_csv(path)


def _ensure_label_rows(root: Path) -> list[dict[str, str]]:
    path = root / "outputs/labels/daily_label_snapshot.csv"
    if not path.exists():
        build_label_snapshot(root)
    return read_csv(path)


def _write_source_symbol_matrix(root: Path, source_rows: list[dict[str, str]], approved_symbols: list[str]) -> None:
    rows = []
    by_source_symbol = {(row["source_id"], row["symbol"]): row for row in source_rows}
    for source_id in sorted({row["source_id"] for row in source_rows}):
        for symbol in approved_symbols:
            row = by_source_symbol.get((source_id, symbol), {})
            rows.append(
                {
                    "source_id": source_id,
                    "symbol": symbol,
                    "source_category": row.get("authority_class", ""),
                    "available": row.get("last_success_available", "false"),
                    "pit_ready": row.get("pit_ready", "false"),
                    "missing_reason": row.get("warning", ""),
                }
            )
    write_csv(root / "outputs/audits/source_symbol_coverage_matrix.csv", rows)


def _write_source_date_matrix(
    root: Path,
    source_rows: list[dict[str, str]],
    dates: list[str],
    approved_symbols: list[str],
) -> None:
    ready_by_source = defaultdict(set)
    for row in source_rows:
        if row.get("pit_ready") == "true":
            ready_by_source[row["source_id"]].add(row["symbol"])
    rows = []
    for source_id in sorted({row["source_id"] for row in source_rows}):
        for trade_date in dates:
            covered = len(ready_by_source[source_id] & set(approved_symbols))
            rows.append(
                {
                    "source_id": source_id,
                    "trade_date": trade_date,
                    "approved_symbols_covered": covered,
                    "approved_symbol_count": len(approved_symbols),
                    "pit_ready_rows": covered,
                    "availability_scope": "contract_fixture_by_source_symbol",
                }
            )
    write_csv(root / "outputs/audits/source_date_coverage_matrix.csv", rows)


def _write_source_field_matrix(root: Path, source_rows: list[dict[str, str]]) -> None:
    fields_by_category = {
        "announcement_metadata": ["event_count_pit", "review_only_nlp_contract_score"],
        "market_metadata": ["market_trend_5d", "stock_gap_signal"],
        "sector_metadata": ["sector_momentum_5d"],
    }
    rows = []
    for source_id in sorted({row["source_id"] for row in source_rows}):
        scoped = [row for row in source_rows if row["source_id"] == source_id]
        category = scoped[0]["authority_class"] if scoped else ""
        ready = any(row.get("pit_ready") == "true" for row in scoped)
        for field_name in fields_by_category.get(category, ["source_health_score", "source_count"]):
            rows.append(
                {
                    "source_id": source_id,
                    "source_category": category,
                    "field_name": field_name,
                    "available_in_clean_fixture": ready,
                    "availability_scope": "contract_fixture_field_scope",
                }
            )
    write_csv(root / "outputs/audits/source_field_coverage_matrix.csv", rows)


def _write_symbol_availability_summary(
    root: Path,
    source_rows: list[dict[str, str]],
    pit_rows: list[dict[str, str]],
    label_rows: list[dict[str, str]],
    approved_symbols: list[str],
) -> None:
    source_count = defaultdict(int)
    source_total = defaultdict(int)
    pit_count = defaultdict(int)
    label_count = defaultdict(int)
    for row in source_rows:
        source_total[row["symbol"]] += 1
        if row.get("pit_ready") == "true":
            source_count[row["symbol"]] += 1
    for row in pit_rows:
        if row.get("pit_ready") == "true":
            pit_count[row["symbol"]] += 1
    for row in label_rows:
        if row.get("label_is_pit_safe") == "true":
            label_count[row["symbol"]] += 1
    rows = []
    for symbol in approved_symbols:
        total = source_total[symbol]
        ready = source_count[symbol]
        rows.append(
            {
                "symbol": symbol,
                "approval_status": "approved",
                "pit_ready_sources": ready,
                "total_sources": total,
                "source_health_score": round(ready / total, 4) if total else 0,
                "pit_ready_rows": pit_count[symbol],
                "label_ready_rows": label_count[symbol],
                "coverage_status": "contract_fixture_available",
            }
        )
    write_csv(root / "outputs/audits/symbol_data_availability_summary.csv", rows)
    write_csv(root / "outputs/audits/approved_universe_coverage_summary.csv", rows)


def _write_source_availability_summary(root: Path, source_rows: list[dict[str, str]], approved_symbols: list[str]) -> None:
    rows = []
    for source_id in sorted({row["source_id"] for row in source_rows}):
        scoped = [row for row in source_rows if row["source_id"] == source_id and row["symbol"] in approved_symbols]
        ready = [row for row in scoped if row.get("pit_ready") == "true"]
        warnings = [row for row in scoped if row.get("warning")]
        rows.append(
            {
                "source_id": source_id,
                "source_category": scoped[0]["authority_class"] if scoped else "",
                "approved_symbols_covered": len(ready),
                "approved_symbol_count": len(approved_symbols),
                "pit_ready_contract_rows": len(ready),
                "missing_reason_count": len(warnings),
                "source_status": "contract_fixture_available" if ready else "not_available_in_fixture",
            }
        )
    write_csv(root / "outputs/audits/source_availability_summary.csv", rows)


def _write_universe_expansion_audit(
    root: Path,
    approved_symbols: list[str],
    blocked: list[dict[str, str]],
    proposed_candidates: list[dict[str, str]],
    targets: dict[str, object],
) -> None:
    gap = max(0, int(targets["symbols"]) - len(approved_symbols))
    write_text(
        root / "outputs/audits/universe_expansion_audit.md",
        "\n".join(
            [
                "# Universe Expansion Audit",
                "",
                "Status: `PASS_WITH_WARNINGS`",
                f"Approved active symbols: `{len(approved_symbols)}`",
                f"Proposed, not-active candidates in config: `{len(proposed_candidates)}`",
                f"Blocked or pending symbols held out: `{len(blocked)}`",
                f"Gap to engineering_pilot approved symbols: `{gap}`",
                "",
                "Candidate rows are proposals only. They are not active until source coverage, liquidity, suspension/ST, and blocked-symbol checks pass.",
                "",
            ]
        ),
    )


def _write_trading_calendar_expansion_audit(
    root: Path,
    trading_dates: list[str],
    stage6c_dates: list[str],
    targets: dict[str, object],
) -> None:
    gap = max(0, int(targets["trading_dates"]) - len(stage6c_dates))
    first = trading_dates[0] if trading_dates else ""
    last = trading_dates[-1] if trading_dates else ""
    write_text(
        root / "outputs/audits/trading_calendar_expansion_audit.md",
        "\n".join(
            [
                "# Trading Calendar Expansion Audit",
                "",
                "Status: `PASS_WITH_WARNINGS`",
                f"Configured trading dates: `{len(trading_dates)}`",
                f"Configured trading calendar range: `{first}` to `{last}`",
                f"Stage 6C validation dates: `{len(stage6c_dates)}`",
                f"Gap to engineering_pilot validation dates: `{gap}`",
                "",
                "The current calendar is a deterministic contract fixture. Engineering pilot requires at least 120 exchange trading dates.",
                "",
            ]
        ),
    )


def _write_provider_ingestion_contract_audit(root: Path) -> None:
    registry = _load_json(root / PROVIDER_REGISTRY)
    contract = _load_json(root / PROVIDER_INGESTION_CONTRACT)
    providers = list(registry["providers"])
    failures = []
    warnings = []
    if contract.get("network_ingestion_enabled_by_default") is not False:
        failures.append("network ingestion must be disabled by default")
    for provider in providers:
        if provider.get("network_default") != "disabled":
            failures.append(f"{provider['provider_id']} network default is not disabled")
        if provider.get("status") == "contract_defined_not_implemented":
            warnings.append(f"{provider['provider_id']} is contract-defined, not implemented")
    status = "BLOCKED" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    write_text(
        root / "outputs/audits/provider_ingestion_contract_audit.md",
        "\n".join(
            [
                "# Provider Ingestion Contract Audit",
                "",
                f"Status: `{status}`",
                f"Providers checked: `{len(providers)}`",
                "Network ingestion remains optional and disabled by default. No provider success is fabricated.",
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


def _write_source_gap_analysis(
    root: Path,
    approved_count: int,
    candidate_count: int,
    current_dates: int,
    current_rows: int,
    pit_ready_count: int,
    label_ready_count: int,
    targets: dict[str, object],
) -> None:
    target_symbols = int(targets["symbols"])
    target_dates = int(targets["trading_dates"])
    target_rows = int(targets["rows"])
    write_text(
        root / "outputs/audits/source_gap_analysis.md",
        "\n".join(
            [
                "# Source Gap Analysis",
                "",
                "Status: `PASS_WITH_WARNINGS`",
                "",
                "## Current Scope",
                f"- Approved symbols: `{approved_count}`",
                f"- Proposed candidate symbols awaiting source evidence: `{candidate_count}`",
                f"- Stage 6C trading dates: `{current_dates}`",
                f"- PIT-ready rows: `{pit_ready_count}`",
                f"- Label-ready rows: `{label_ready_count}`",
                f"- Stage 6C rows: `{current_rows}`",
                "",
                "## Gap To Engineering Pilot",
                f"- Symbols needed: `{max(0, target_symbols - approved_count)}`",
                f"- Trading dates needed: `{max(0, target_dates - current_dates)}`",
                f"- Rows needed: `{max(0, target_rows - current_rows)}`",
                "",
                "## Expansion Path",
                "1. Materialize a local bundle outside GitHub with at least 50 approved symbols and 120 exchange trading dates.",
                "2. Populate OHLCV, benchmark, announcement metadata, and source coverage tables using optional network ingestion guarded by explicit flags.",
                "3. Rebuild PIT and label panels from the local bundle, then promote only if audits reach `engineering_pilot` or higher.",
                "",
            ]
        ),
    )


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))

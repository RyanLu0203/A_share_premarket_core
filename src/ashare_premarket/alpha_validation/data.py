from __future__ import annotations

import ast
import csv
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from ashare_premarket.quant_foundation.contracts import GovernedSnapshot

_LEAKY_PREFIXES = ("forward_return", "future_", "label", "target")


@dataclass(frozen=True)
class HistoricalBundle:
    snapshot: GovernedSnapshot
    trading_calendar: tuple[str, ...]
    feature_available_at: Mapping[str, str | None]
    metadata: Mapping[str, object]


def load_historical_bundle(
    root: Path,
    config: Mapping[str, object],
    *,
    code_commit: str,
) -> HistoricalBundle:
    repository = root.resolve()
    manifest_path = _safe_path(repository, config, "bundle_manifest_path")
    daily_path = _safe_path(repository, config, "daily_panel_path")
    index_path = _safe_path(repository, config, "index_panel_path")
    coverage_path = _safe_path(repository, config, "symbol_coverage_path")
    qfq_path = _safe_path(repository, config, "qfq_contract_evidence_path")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_goal = str(config["expected_goal"])
    expected_provider = str(config["expected_provider"])
    if manifest.get("goal") != expected_goal:
        raise ValueError("goal12_source_goal_mismatch")
    if manifest.get("provider") != expected_provider:
        raise ValueError("goal12_provider_mismatch")
    _verify_source_checksums(
        manifest,
        (daily_path, index_path, coverage_path),
    )
    if config.get("adjustment") != "qfq" or not _proves_qfq_call(qfq_path):
        raise ValueError("goal12_qfq_contract_not_proven")

    daily = _read_csv(daily_path)
    indices = _read_csv(index_path)
    coverage = _read_csv(coverage_path)
    if not daily or not indices:
        raise ValueError("goal12_historical_bundle_empty")
    _reject_unsafe_daily_schema(daily)
    _validate_rows(daily, expected_provider, "daily")
    _validate_rows(indices, expected_provider, "index")

    benchmark = str(config["benchmark_index_id"])
    benchmark_rows = [row for row in indices if row.get("index_id") == benchmark]
    if not benchmark_rows:
        raise ValueError("goal12_benchmark_index_unavailable")
    index_close: dict[str, float] = {}
    for row in benchmark_rows:
        trade_date = str(row.get("trade_date", ""))
        if trade_date in index_close:
            raise ValueError("duplicate_goal12_index_key")
        index_close[trade_date] = _positive_finite(row.get("close"), "invalid_goal12_index_close")

    daily_keys: set[tuple[str, str]] = set()
    daily_dates: set[str] = set()
    symbols: set[str] = set()
    normalized: list[dict[str, object]] = []
    for row in daily:
        trade_date = str(row.get("trade_date", ""))
        symbol = str(row.get("symbol", ""))
        key = (trade_date, symbol)
        if key in daily_keys:
            raise ValueError("duplicate_goal12_daily_key")
        if trade_date not in index_close:
            raise ValueError("goal12_daily_date_missing_from_benchmark_calendar")
        daily_keys.add(key)
        daily_dates.add(trade_date)
        symbols.add(symbol)
        normalized.append(
            {
                "date": trade_date,
                # GOAL-11 stores an end-of-day observation date. The stricter
                # next-session consumer timestamp is retained separately below.
                "available_at": trade_date,
                "symbol": symbol,
                "close": _positive_finite(row.get("close"), "invalid_goal12_daily_close"),
                "index_close": index_close[trade_date],
            }
        )

    first_date, last_date = min(daily_dates), max(daily_dates)
    calendar = tuple(
        trade_date
        for trade_date in sorted(index_close)
        if first_date <= trade_date <= last_date
    )
    if not daily_dates.issubset(calendar):
        raise ValueError("goal12_calendar_alignment_failure")
    feature_available_at = {
        trade_date: calendar[index + 1] if index + 1 < len(calendar) else None
        for index, trade_date in enumerate(calendar)
    }
    manifest_checksum = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    snapshot = GovernedSnapshot.from_rows(
        snapshot_id=f"goal12:{manifest_checksum[:16]}",
        cutoff_date=last_date,
        generation_timestamp=str(manifest["acquisition_timestamp"]),
        code_commit=code_commit,
        source_checksum=manifest_checksum,
        adjustment="qfq",
        rows=normalized,
    )
    acquired = {row.get("symbol") for row in coverage if row.get("status") == "acquired"}
    metadata: dict[str, object] = {
        "amount_semantics": str(config["amount_semantics"]),
        "availability_semantics": str(config["availability_semantics"]),
        "benchmark_index_id": benchmark,
        "calendar_date_count": len(calendar),
        "daily_row_count": len(daily),
        "manifest_checksum": manifest_checksum,
        "provider": expected_provider,
        "qfq_contract_evidence_path": str(config["qfq_contract_evidence_path"]),
        "source_fields_available": ("close", "index_close"),
        "survivorship_risk_disclosed": bool(
            str(config["survivorship_semantics"]).strip()
        ),
        "symbol_count": len(symbols),
        "coverage_acquired_symbol_count": len(acquired),
    }
    return HistoricalBundle(snapshot, calendar, feature_available_at, metadata)


def _safe_path(root: Path, config: Mapping[str, object], field: str) -> Path:
    path = (root / str(config[field])).resolve()
    if path != root and root not in path.parents:
        raise ValueError(f"goal12_source_path_outside_repository:{field}")
    if not path.is_file():
        raise ValueError(f"goal12_source_file_missing:{field}")
    return path


def _verify_source_checksums(
    manifest: Mapping[str, object], paths: tuple[Path, ...]
) -> None:
    checksums = dict(manifest.get("checksums", {}))
    for path in paths:
        expected = str(checksums.get(path.name, ""))
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if expected != observed:
            raise ValueError(f"goal12_source_checksum_mismatch:{path.name}")


def _proves_qfq_call(path: Path) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeError):
        return False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if not isinstance(function, ast.Attribute) or function.attr != "stock_zh_a_daily":
            continue
        for keyword in node.keywords:
            if keyword.arg == "adjust" and isinstance(keyword.value, ast.Constant):
                if keyword.value.value == "qfq":
                    return True
    return False


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _reject_unsafe_daily_schema(rows: list[dict[str, str]]) -> None:
    fields = tuple(rows[0])
    leaky = sorted(
        field
        for field in fields
        if field.strip().lower().startswith(_LEAKY_PREFIXES)
    )
    if leaky:
        raise ValueError(f"goal12_label_field_in_feature_source:{','.join(leaky)}")
    if "amount" in fields and any(str(row.get("amount", "")).strip() for row in rows):
        raise ValueError("goal12_amount_must_remain_unavailable")


def _validate_rows(rows: list[dict[str, str]], provider: str, kind: str) -> None:
    if any(row.get("source_provider") != provider for row in rows):
        raise ValueError("goal12_provider_mismatch")
    if any(row.get("no_lookahead_status") != "passed_current_or_past_only" for row in rows):
        raise ValueError(f"goal12_{kind}_pit_status_failure")


def _positive_finite(value: object, reason: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(reason) from exc
    if not math.isfinite(number) or number <= 0:
        raise ValueError(reason)
    return number

"""Fail-closed acceptance contract for a future 100-symbol source universe."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import csv
import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping

from ashare_premarket.research.liquidity_universe_100_contract import (
    BLOCKED_SYMBOLS,
    REQUIRED_SYMBOL_COUNT,
    select_liquidity_universe_100,
)


GOAL_ID = "GOAL-LIQUIDITY-CANDIDATE-SOURCE-ACCEPTANCE-01"
PANEL_INPUT = "outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv"
DECISION_OUTPUT = "outputs/research/goal_liquidity_candidate_source_acceptance01_decision.csv"
REPORT = "outputs/audits/goal_liquidity_candidate_source_acceptance01_report.md"
MANIFEST = "outputs/audits/goal_liquidity_candidate_source_acceptance01_manifest.json"
AUDIT = "outputs/audits/goal_liquidity_candidate_source_acceptance01_audit.md"
REQUIRED_FIELDS = (
    "symbol",
    "exchange",
    "security_type",
    "listing_status",
    "source_id",
    "available_at",
)
ALLOWED_SOURCE_CLASSES = frozenset(
    {
        "official_exchange_listing",
        "licensed_security_master",
        "owner_supplied_governed_bundle",
    }
)
FORBIDDEN_FIELD_TOKENS = (
    "future_return",
    "forward_return",
    "factor",
    "alpha",
    "performance",
    "label",
    "target",
)


@dataclass(frozen=True)
class CandidateSourceDecision:
    status: str
    reason: str
    supplied_record_count: int
    eligible_symbol_count: int
    accepted_symbol_count: int
    missing_fields: tuple[str, ...]
    forbidden_fields: tuple[str, ...]
    invalid_record_count: int
    late_record_count: int
    accepted_symbols: tuple[str, ...]
    provider_calls_performed: bool = False


def evaluate_candidate_source(
    records: Iterable[Mapping[str, object]],
    *,
    source_class: str,
    decision_cutoff: str,
) -> CandidateSourceDecision:
    """Accept a source only when its complete PIT-safe universe reaches 100.

    Selection reads identity/governance fields only. Any outcome-like field in
    the supplied schema rejects the complete source, even when its value is
    empty, so later callers cannot silently introduce label leakage.
    """

    rows = list(records)
    cutoff = _timestamp(decision_cutoff)
    if source_class not in ALLOWED_SOURCE_CLASSES:
        return _decision("BLOCKED", "SOURCE_CLASS_NOT_ALLOWED", rows)

    all_fields = {str(field) for row in rows for field in row}
    forbidden = tuple(
        sorted(
            field
            for field in all_fields
            if any(token in field.lower() for token in FORBIDDEN_FIELD_TOKENS)
        )
    )
    missing = tuple(sorted(set(REQUIRED_FIELDS) - all_fields))
    if forbidden:
        return _decision(
            "BLOCKED", "FORBIDDEN_SELECTION_FIELDS_PRESENT", rows,
            forbidden_fields=forbidden,
        )
    if missing:
        return _decision(
            "BLOCKED", "REQUIRED_SOURCE_FIELDS_MISSING", rows,
            missing_fields=missing,
        )

    valid: list[dict[str, object]] = []
    invalid_count = 0
    late_count = 0
    for row in rows:
        if any(row.get(field) in (None, "") for field in REQUIRED_FIELDS):
            invalid_count += 1
            continue
        symbol = str(row["symbol"]).strip().upper()
        exchange = str(row["exchange"]).strip().upper()
        if (
            symbol in BLOCKED_SYMBOLS
            or exchange not in {"SH", "SZ"}
            or not symbol.endswith(f".{exchange}")
            or str(row["security_type"]) != "A_share"
            or str(row["listing_status"]) != "listed"
        ):
            invalid_count += 1
            continue
        try:
            available_at = _timestamp(str(row["available_at"]))
        except ValueError:
            invalid_count += 1
            continue
        if available_at > cutoff:
            late_count += 1
            continue
        valid.append({"symbol": symbol})

    universe = select_liquidity_universe_100(valid)
    if universe.status != "PASS":
        return CandidateSourceDecision(
            status="BLOCKED",
            reason="INSUFFICIENT_PIT_SAFE_ELIGIBLE_SYMBOLS",
            supplied_record_count=len(rows),
            eligible_symbol_count=universe.eligible_symbol_count,
            accepted_symbol_count=0,
            missing_fields=(),
            forbidden_fields=(),
            invalid_record_count=invalid_count,
            late_record_count=late_count,
            accepted_symbols=(),
        )
    return CandidateSourceDecision(
        status="PASS",
        reason="EXACT_100_SOURCE_ACCEPTED",
        supplied_record_count=len(rows),
        eligible_symbol_count=universe.eligible_symbol_count,
        accepted_symbol_count=REQUIRED_SYMBOL_COUNT,
        missing_fields=(),
        forbidden_fields=(),
        invalid_record_count=invalid_count,
        late_record_count=late_count,
        accepted_symbols=universe.accepted_symbols,
    )


def _decision(
    status: str,
    reason: str,
    rows: list[Mapping[str, object]],
    *,
    missing_fields: tuple[str, ...] = (),
    forbidden_fields: tuple[str, ...] = (),
) -> CandidateSourceDecision:
    return CandidateSourceDecision(
        status=status,
        reason=reason,
        supplied_record_count=len(rows),
        eligible_symbol_count=0,
        accepted_symbol_count=0,
        missing_fields=missing_fields,
        forbidden_fields=forbidden_fields,
        invalid_record_count=0,
        late_record_count=0,
        accepted_symbols=(),
    )


def _timestamp(value: str) -> datetime:
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(candidate)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timezone required")
    return parsed


def run_goal(root: Path) -> bool:
    """Evaluate current committed symbol evidence without promoting it."""

    panel_path = root / PANEL_INPUT
    with panel_path.open(encoding="utf-8", newline="") as handle:
        symbols = sorted({row["symbol"] for row in csv.DictReader(handle)})
    current_records = [
        {"symbol": symbol, "source_id": "provider02b_evaluation_panel"}
        for symbol in symbols
    ]
    decision = evaluate_candidate_source(
        current_records,
        source_class="owner_supplied_governed_bundle",
        decision_cutoff="2026-08-28T08:00:00+08:00",
    )
    row = {
        "goal_status": "PASS_WITH_WARNINGS",
        "current_source_status": decision.status,
        "current_source_reason": decision.reason,
        "current_distinct_symbol_count": len(symbols),
        "required_symbol_count": REQUIRED_SYMBOL_COUNT,
        "accepted_symbol_count": decision.accepted_symbol_count,
        "missing_fields": ";".join(decision.missing_fields),
        "forbidden_fields": ";".join(decision.forbidden_fields),
        "partial_universe_emitted": "false",
        "provider_calls_authorized": "false",
        "provider_calls_performed": "false",
        "downstream_unlock": "false",
    }
    output = root / DECISION_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row), lineterminator="\n")
        writer.writeheader()
        writer.writerow(row)
    (root / REPORT).write_text(
        "\n".join(
            [
                f"# {GOAL_ID}",
                "",
                "Status: `PASS_WITH_WARNINGS`; current candidate source `BLOCKED`.",
                "",
                f"The committed Provider02B evaluation panel exposes `{len(symbols)}` "
                "distinct symbols, but it is not an accepted security-master source "
                "and lacks the complete identity, listing-state and PIT availability "
                "contract. No partial 100-symbol universe is emitted.",
                "",
                "No provider call, accepted source row, factor construction, "
                "recommendation tiering or downstream unlock occurred.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    manifest = {
        "goal_id": GOAL_ID,
        "goal_status": "PASS_WITH_WARNINGS",
        "current_source_status": "BLOCKED",
        "current_source_reason": decision.reason,
        "current_distinct_symbol_count": len(symbols),
        "required_symbol_count": REQUIRED_SYMBOL_COUNT,
        "accepted_symbol_count": 0,
        "partial_universe_emitted": False,
        "provider_calls_authorized": False,
        "provider_calls_performed": False,
        "downstream_unlock": False,
        "inputs": {PANEL_INPUT: hashlib.sha256(panel_path.read_bytes()).hexdigest()},
        "outputs": {DECISION_OUTPUT: hashlib.sha256(output.read_bytes()).hexdigest()},
    }
    manifest_path = root / MANIFEST
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return audit_goal(root)


def audit_goal(root: Path) -> bool:
    try:
        manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
        valid = (
            manifest["goal_status"] == "PASS_WITH_WARNINGS"
            and manifest["current_source_status"] == "BLOCKED"
            and manifest["current_source_reason"] == "REQUIRED_SOURCE_FIELDS_MISSING"
            and manifest["current_distinct_symbol_count"] == 50
            and manifest["required_symbol_count"] == 100
            and manifest["accepted_symbol_count"] == 0
            and not manifest["partial_universe_emitted"]
            and not manifest["provider_calls_authorized"]
            and not manifest["provider_calls_performed"]
            and not manifest["downstream_unlock"]
            and all(
                hashlib.sha256((root / path).read_bytes()).hexdigest() == digest
                for path, digest in manifest["inputs"].items()
            )
            and all(
                hashlib.sha256((root / path).read_bytes()).hexdigest() == digest
                for path, digest in manifest["outputs"].items()
            )
        )
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        valid = False
    audit_path = root / AUDIT
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(
        "# GOAL-LIQUIDITY-CANDIDATE-SOURCE-ACCEPTANCE-01 Audit\n\n"
        f"Status: `{'PASS' if valid else 'FAIL'}`.\n",
        encoding="utf-8",
    )
    return valid

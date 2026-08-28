"""Integrate four offline liquidity acquisition-readiness workstreams."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping

from ashare_premarket.providers.liquidity_pit_availability import (
    documented_provider_contracts,
)
from ashare_premarket.providers.liquidity_schema_smoke_plan import (
    evaluate_observed_field_names,
    schema_smoke_calls,
    validate_plan,
)
from ashare_premarket.research.liquidity_universe_100_contract import (
    select_liquidity_universe_100,
)

GOAL_ID = "GOAL-LIQUIDITY-ACQUISITION-READINESS-BATCH-01"

PANEL_INPUT = "outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv"
COVERAGE_INPUT = "outputs/research/network_ingestion/symbol_coverage.csv"
SOURCE_ACCEPTANCE_INPUT = (
    "outputs/audits/goal_liquidity_provider_source_acceptance01_manifest.json"
)

PREFIX = "outputs/providers/goal_liquidity_acquisition_readiness_batch01_"
SMOKE_PLAN = PREFIX + "schema_smoke_plan.csv"
SCHEMA_FIXTURE_ACCEPTANCE = PREFIX + "schema_fixture_acceptance.csv"
NORMALIZER_CONTRACT = PREFIX + "normalizer_contract.csv"
PIT_CONTRACT = PREFIX + "pit_availability_contract.csv"
UNIVERSE_DECISION = PREFIX + "universe100_decision.csv"
READINESS_DECISION = PREFIX + "readiness_decision.csv"
REPORT = "outputs/audits/goal_liquidity_acquisition_readiness_batch01_report.md"
MANIFEST = "outputs/audits/goal_liquidity_acquisition_readiness_batch01_manifest.json"
AUDIT = "outputs/audits/goal_liquidity_acquisition_readiness_batch01_audit.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_csv(
    root: Path,
    relative_path: str,
    fieldnames: Iterable[str],
    rows: Iterable[Mapping[str, object]],
) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(fieldnames),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def normalizer_contract_rows() -> list[dict[str, str]]:
    return [
        {
            "provider_endpoint": "tushare_pro.daily_basic",
            "required_fields": "ts_code;trade_date;free_share;turnover_rate_f",
            "unit_rules": "free_share_x10000;turnover_rate_f_div100",
            "identity_and_date_validation": "strict",
            "available_at_policy": "explicit_timezone_aware_after_close_or_null",
            "implementation_state": "implemented_offline",
        },
        {
            "provider_endpoint": "baostock.query_history_k_data_plus",
            "required_fields": "code;date;volume;turn;tradestatus;adjustflag",
            "unit_rules": "volume_identity;turn_div100;status_map;adjustflag_2_only",
            "identity_and_date_validation": "strict",
            "available_at_policy": "explicit_timezone_aware_after_close_or_null",
            "implementation_state": "implemented_offline",
        },
    ]


def _smoke_rows() -> list[dict[str, object]]:
    rows = []
    for call in schema_smoke_calls():
        rows.append(
            {
                "call_id": call["call_id"],
                "provider": call["provider"],
                "endpoint": call["endpoint"],
                "canonical_symbol": call["canonical_symbol"],
                "provider_symbol": call["provider_symbol"],
                "expected_fields": ";".join(call["expected_fields"]),
                "max_calls": call["max_calls"],
                "max_retries": call["max_retries"],
                "provider_calls_authorized": str(
                    call["provider_calls_authorized"]
                ).lower(),
                "raw_payload_persistence_allowed": str(
                    call["raw_payload_persistence_allowed"]
                ).lower(),
            }
        )
    return rows


def _schema_fixture_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for call in schema_smoke_calls():
        provider = str(call["provider"])
        if provider in seen:
            continue
        seen.add(provider)
        result = evaluate_observed_field_names(provider, list(call["expected_fields"]))
        rows.append(
            {
                "provider": provider,
                "fixture_type": "synthetic_field_names_only",
                "status": result["status"],
                "live_schema_verified": "false",
                "provider_calls_authorized": "false",
                "accepted_provider_rows": 0,
            }
        )
    return rows


def _current_universe_decision(root: Path) -> dict[str, object]:
    with (root / PANEL_INPUT).open(encoding="utf-8", newline="") as handle:
        symbols = sorted({row["symbol"] for row in csv.DictReader(handle)})
    with (root / COVERAGE_INPUT).open(encoding="utf-8", newline="") as handle:
        acquired = [
            row["symbol"]
            for row in csv.DictReader(handle)
            if row["status"] == "acquired"
        ]
    decision = select_liquidity_universe_100(
        [{"symbol": symbol} for symbol in symbols],
        acquired_symbols=acquired,
    )
    return {
        "status": decision.status,
        "eligible_symbol_count": decision.eligible_symbol_count,
        "preferred_acquired_count": decision.preferred_acquired_count,
        "required_symbol_count": decision.required_symbol_count,
        "accepted_symbol_count": len(decision.accepted_symbols),
        "partial_universe_emitted": "false",
        "selection_rule": decision.selection_rule,
        "blocked_symbols_removed": ";".join(decision.blocked_symbols_removed),
        "provider_calls_performed": "false",
    }


def readiness_row(root: Path) -> dict[str, object]:
    universe = _current_universe_decision(root)
    return {
        "goal_status": "PASS_WITH_WARNINGS",
        "schema_smoke_plan_state": "READY_DESIGN_ONLY_NOT_AUTHORIZED",
        "schema_smoke_call_budget": 4,
        "schema_fixture_state": "PASS_SYNTHETIC_NOT_LIVE_VERIFIED",
        "normalizer_state": "IMPLEMENTED_OFFLINE",
        "pit_availability_state": "BLOCKED_ROW_AVAILABLE_AT_MISSING",
        "universe100_state": universe["status"],
        "current_eligible_symbol_count": universe["eligible_symbol_count"],
        "required_symbol_count": universe["required_symbol_count"],
        "provider_calls_authorized": "false",
        "provider_calls_performed": "false",
        "accepted_rows": 0,
        "acquisition_preflight_status": "BLOCKED",
        "factor_construction_unlocked": "false",
        "rec_tiering_unlocked": "false",
        "next_action": "explicit_bounded_schema_smoke_authority_and_100_symbol_source",
    }


def run_goal(root: Path) -> bool:
    smoke = _smoke_rows()
    schema_fixtures = _schema_fixture_rows()
    normalizers = normalizer_contract_rows()
    pit = documented_provider_contracts()
    universe = _current_universe_decision(root)
    readiness = readiness_row(root)

    if not validate_plan():
        return False

    _write_csv(root, SMOKE_PLAN, smoke[0].keys(), smoke)
    _write_csv(
        root,
        SCHEMA_FIXTURE_ACCEPTANCE,
        schema_fixtures[0].keys(),
        schema_fixtures,
    )
    _write_csv(root, NORMALIZER_CONTRACT, normalizers[0].keys(), normalizers)
    _write_csv(root, PIT_CONTRACT, pit[0].keys(), pit)
    _write_csv(root, UNIVERSE_DECISION, universe.keys(), [universe])
    _write_csv(root, READINESS_DECISION, readiness.keys(), [readiness])

    (root / REPORT).write_text(
        "\n".join(
            [
                f"# {GOAL_ID}",
                "",
                "Status: `PASS_WITH_WARNINGS`; acquisition preflight `BLOCKED`.",
                "",
                "Four offline workstreams are integrated: a fixed four-call "
                "schema-smoke design, strict Tushare/Baostock row normalizers, "
                "an explicit PIT availability contract, and an exact-100 "
                "deterministic universe contract.",
                "",
                f"Current committed evidence supplies `{universe['eligible_symbol_count']}` "
                "eligible symbols, including "
                f"`{universe['preferred_acquired_count']}` with acquired deep history. "
                "Because fewer than 100 are available, no partial accepted universe "
                "is emitted. Both provider candidates also lack accepted row-level "
                "availability timestamps.",
                "",
                "Synthetic field-name fixtures pass both provider parser contracts, "
                "but this is not live schema verification and accepts no provider row.",
                "",
                "The schema smoke remains design-only and unauthorized. No provider "
                "call, credential read, raw payload, accepted row, factor construction, "
                "or downstream unlock occurred.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    inputs = [PANEL_INPUT, COVERAGE_INPUT, SOURCE_ACCEPTANCE_INPUT]
    outputs = [
        SMOKE_PLAN,
        SCHEMA_FIXTURE_ACCEPTANCE,
        NORMALIZER_CONTRACT,
        PIT_CONTRACT,
        UNIVERSE_DECISION,
        READINESS_DECISION,
    ]
    manifest = {
        "goal_id": GOAL_ID,
        "goal_status": "PASS_WITH_WARNINGS",
        "acquisition_preflight_status": "BLOCKED",
        "schema_smoke_plan_state": "READY_DESIGN_ONLY_NOT_AUTHORIZED",
        "schema_smoke_call_budget": 4,
        "schema_fixture_state": "PASS_SYNTHETIC_NOT_LIVE_VERIFIED",
        "normalizer_state": "IMPLEMENTED_OFFLINE",
        "pit_availability_state": "BLOCKED_ROW_AVAILABLE_AT_MISSING",
        "universe100_state": universe["status"],
        "current_eligible_symbol_count": universe["eligible_symbol_count"],
        "current_acquired_symbol_count": universe["preferred_acquired_count"],
        "required_symbol_count": universe["required_symbol_count"],
        "accepted_universe_symbol_count": universe["accepted_symbol_count"],
        "partial_universe_emitted": False,
        "provider_calls_authorized": False,
        "provider_calls_performed": False,
        "accepted_rows": 0,
        "factor_construction_unlocked": False,
        "rec_tiering_unlocked": False,
        "inputs": {path: _sha256(root / path) for path in inputs},
        "outputs": {path: _sha256(root / path) for path in outputs},
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
            and manifest["acquisition_preflight_status"] == "BLOCKED"
            and manifest["schema_smoke_plan_state"]
            == "READY_DESIGN_ONLY_NOT_AUTHORIZED"
            and manifest["schema_smoke_call_budget"] == 4
            and manifest["schema_fixture_state"]
            == "PASS_SYNTHETIC_NOT_LIVE_VERIFIED"
            and manifest["normalizer_state"] == "IMPLEMENTED_OFFLINE"
            and manifest["pit_availability_state"]
            == "BLOCKED_ROW_AVAILABLE_AT_MISSING"
            and manifest["universe100_state"] == "BLOCKED"
            and manifest["current_eligible_symbol_count"] == 50
            and manifest["current_acquired_symbol_count"] == 41
            and manifest["required_symbol_count"] == 100
            and manifest["accepted_universe_symbol_count"] == 0
            and not manifest["partial_universe_emitted"]
            and not manifest["provider_calls_authorized"]
            and not manifest["provider_calls_performed"]
            and manifest["accepted_rows"] == 0
            and not manifest["factor_construction_unlocked"]
            and not manifest["rec_tiering_unlocked"]
            and all(
                _sha256(root / path) == expected
                for path, expected in manifest["inputs"].items()
            )
            and all(
                _sha256(root / path) == expected
                for path, expected in manifest["outputs"].items()
            )
        )
    except (OSError, KeyError, ValueError, json.JSONDecodeError):
        valid = False

    audit_path = root / AUDIT
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(
        f"# {GOAL_ID} Audit\n\nStatus: `{'PASS' if valid else 'FAIL'}`\n",
        encoding="utf-8",
    )
    return valid

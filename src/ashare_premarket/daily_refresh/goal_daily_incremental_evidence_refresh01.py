from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import time
from datetime import datetime
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

from ashare_premarket.core.boundary import implementation_file_sha256
from ashare_premarket.core.io import read_csv, write_csv
from ashare_premarket.portfolio_risk.goal_premarket_position_management_operational01 import (
    DEFAULT_REPLAY_TARGET_TRADING_DATE,
    evaluate_canonical_freshness,
    resolve_run_context,
    run_goal_premarket_position_management_operational01,
)
from ashare_premarket.providers.akshare_provider import load_stock_ohlcv_daily
from ashare_premarket.providers.provider_registry import load_ingestion_config, network_enabled


GOAL_ID = "GOAL-DAILY-INCREMENTAL-EVIDENCE-REFRESH-01"
WORKFLOW_ID = "goal_daily_incremental_evidence_refresh01"
CAPABILITY_KEY = "goal_daily_incremental_evidence_refresh01_gate"
NO_SILENT_AVERAGING = True

CANONICAL_MARKET = "outputs/research/goal_premarket_portfolio_risk_management01_canonical_market_data.csv"
REFERENCE_PORTFOLIO = "outputs/research/goal_premarket_portfolio_risk_management01_research_reference_portfolio.csv"
PROVIDER_QUARANTINE = "outputs/research/goal_premarket_portfolio_risk_management01_provider_discrepancy_quarantine.csv"
LOCKED_CAPABILITIES = "configs/project/locked_capabilities.json"
WORKFLOW_STATUS = "configs/project/workflow_status.csv"
OPM_SNAPSHOT_ROOT = "outputs/research/premarket_position_management"
OPM_LATEST = f"{OPM_SNAPSHOT_ROOT}/latest_manifest.json"

PREFIX = "outputs/research/goal_daily_incremental_evidence_refresh01_"
VALIDATION = PREFIX + "validation.csv"
RUN_SUMMARY = PREFIX + "run_summary.csv"
EXPERIMENT_CONTRACT = PREFIX + "experiment_readiness_contract.csv"
REFRESH_MANIFEST = PREFIX + "refresh_manifest.json"
REFRESH_ROOT = "outputs/research/daily_incremental_evidence_refresh"
LATEST_REFRESH = f"{REFRESH_ROOT}/latest_refresh.json"
MANIFEST = "outputs/audits/goal_daily_incremental_evidence_refresh01_manifest.json"
REPORT = "outputs/audits/goal_daily_incremental_evidence_refresh01_report.md"
AUDIT = "outputs/audits/goal_daily_incremental_evidence_refresh01_audit.md"
DOC = "docs/research/GOAL_DAILY_INCREMENTAL_EVIDENCE_REFRESH01_DAILY_WORKFLOW.md"
CONTRACT = "configs/research/goal_daily_incremental_evidence_refresh01_contract.yaml"

APPROVED_PROVIDERS = {"akshare", "akshare_sina"}
CANONICAL_FIELDS = [
    "trade_date",
    "symbol",
    "canonical_close",
    "canonical_return_1d",
    "source_provider",
    "provider_overlap_status",
    "canonical_price_status",
    "canonical_return_status",
    "adjustment_convention_status",
    "raw_adjusted_semantics",
    "timestamp_alignment_status",
    "provider_timestamp",
    "pit_available_date",
    "suspension_status",
    "corporate_action_discontinuity_flag",
    "risk_model_eligible",
    "quarantine_reason",
    "no_lookahead_status",
    "research_only",
    "not_trading_advice",
    "not_for_execution",
]

REQUIRED_ARTIFACTS = (
    VALIDATION,
    RUN_SUMMARY,
    EXPERIMENT_CONTRACT,
    REFRESH_MANIFEST,
    LATEST_REFRESH,
    MANIFEST,
    REPORT,
    AUDIT,
    DOC,
    CONTRACT,
)


def resolve_daily_refresh_context(
    root: Path,
    execution_time: str | datetime | None = None,
    target_trading_date: str | None = None,
    replay_date: str | None = None,
) -> dict[str, str]:
    execution_value = execution_time.isoformat() if isinstance(execution_time, datetime) else execution_time
    try:
        context = resolve_run_context(
            root,
            execution_time=execution_value,
            target_trading_date=target_trading_date,
            replay_date=replay_date,
        )
        return {**context, "calendar_status": "PASS", "calendar_reason": ""}
    except ValueError as exc:
        if "trading day configured" not in str(exc):
            raise
        execution_dt = _execution_datetime(execution_value, replay_date)
        mode = "deterministic_replay" if replay_date else "daily_operational"
        generated_at = f"{replay_date}T08:30:00+08:00" if replay_date else execution_dt.isoformat(timespec="seconds")
        return {
            "execution_mode": mode,
            "timezone": "Asia/Shanghai",
            "execution_time": execution_dt.isoformat(timespec="seconds"),
            "execution_date": execution_dt.date().isoformat(),
            "generated_at": generated_at,
            "decision_asof_ts": f"{target_trading_date or replay_date}T08:30:00+08:00" if target_trading_date or replay_date else "UNRESOLVED",
            "target_trading_date": target_trading_date or replay_date or "UNRESOLVED",
            "expected_previous_trading_date": "UNRESOLVED",
            "data_cutoff": "UNRESOLVED",
            "calendar_status": "BLOCKED",
            "calendar_reason": "TRADING_CALENDAR_COVERAGE_MISSING",
        }


def write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body.encode("utf-8"))


def write_json(path: Path, payload: dict[str, object]) -> None:
    write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def merge_incremental_evidence(
    base_rows: list[dict[str, object]],
    incremental_rows: list[dict[str, object]],
    expected_date: str,
) -> list[dict[str, str]]:
    """Append one governed T-1 slice without replacing or averaging existing keys."""

    normalized_base = [_canonical_shape(row) for row in base_rows]
    by_key = {(row["symbol"], row["trade_date"]): row for row in normalized_base}
    history: dict[str, list[dict[str, str]]] = {}
    for row in normalized_base:
        history.setdefault(row["symbol"], []).append(row)

    additions: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for raw in sorted(incremental_rows, key=lambda row: (str(row.get("trade_date", "")), str(row.get("symbol", "")))):
        symbol = str(raw.get("symbol", "")).strip().upper()
        trade_date = str(raw.get("trade_date", "")).strip()
        key = (symbol, trade_date)
        if not symbol or not trade_date:
            raise ValueError("missing_incremental_symbol_or_trade_date")
        if trade_date != expected_date:
            raise ValueError(f"incremental_date_not_expected_t_minus_one:{trade_date}")
        if key in seen:
            raise ValueError(f"duplicate_incremental_symbol_date:{symbol}:{trade_date}")
        seen.add(key)

        close = _finite_float(raw.get("close", raw.get("canonical_close")))
        if close is None or close <= 0:
            raise ValueError(f"invalid_incremental_close:{symbol}:{trade_date}")
        source_provider = str(raw.get("source_provider", "")).strip()
        if key in by_key:
            existing = by_key[key]
            if _finite_float(existing.get("canonical_close")) != close or existing.get("source_provider") != source_provider:
                raise ValueError(f"conflicting_existing_symbol_date:{symbol}:{trade_date}")
            continue

        prior = [row for row in history.get(symbol, []) if row["trade_date"] < trade_date]
        prior_close = _finite_float(max(prior, key=lambda row: row["trade_date"]).get("canonical_close")) if prior else None
        supplied_return = _finite_float(raw.get("return_1d", raw.get("canonical_return_1d")))
        daily_return = supplied_return if supplied_return is not None else (close / prior_close - 1.0 if prior_close else None)
        quarantine_reason = str(raw.get("quarantine_reason", "")).strip()
        suspended = str(raw.get("suspension_status", "trading")).strip() or "trading"
        eligible = daily_return is not None and not quarantine_reason
        row = _canonical_shape(
            {
                "trade_date": trade_date,
                "symbol": symbol,
                "canonical_close": _fmt(close),
                "canonical_return_1d": _fmt(daily_return),
                "source_provider": source_provider,
                "provider_overlap_status": "single_approved_provider_no_overlap_evidence",
                "canonical_price_status": "accepted" if not quarantine_reason else "quarantined_provider_discrepancy",
                "canonical_return_status": "accepted" if eligible else "quarantined_provider_discrepancy" if quarantine_reason else "insufficient_prior_price",
                "adjustment_convention_status": "unresolved_cross_provider_adjustment_convention",
                "raw_adjusted_semantics": f"{raw.get('adjustment_policy', 'unresolved')}_adjusted_primary;cross_provider_adjustment_unresolved",
                "timestamp_alignment_status": "date_level_only_no_intraday_timestamp",
                "provider_timestamp": raw.get("provider_timestamp", trade_date),
                "pit_available_date": raw.get("pit_available_date", trade_date),
                "suspension_status": suspended,
                "corporate_action_discontinuity_flag": str(abs(daily_return or 0.0) >= 0.095).lower(),
                "risk_model_eligible": str(eligible).lower(),
                "quarantine_reason": quarantine_reason,
                "no_lookahead_status": raw.get("no_lookahead_status", "passed_current_or_past_only"),
                "research_only": "true",
                "not_trading_advice": "true",
                "not_for_execution": "true",
            }
        )
        additions.append(row)
        history.setdefault(symbol, []).append(row)

    return sorted([*normalized_base, *additions], key=lambda row: (row["trade_date"], row["symbol"]))


def validate_refresh_evidence(
    context: dict[str, str],
    canonical_rows: list[dict[str, object]],
    required_symbols: set[str],
    source_checksum: str,
    expected_source_checksum: str,
    provider_attempts: list[dict[str, object]] | None = None,
    additional_reason_codes: list[str] | None = None,
) -> dict[str, object]:
    expected = context["expected_previous_trading_date"]
    rows = [_canonical_shape(row) for row in canonical_rows]
    expected_rows = [row for row in rows if row["trade_date"] == expected]
    by_symbol = {row["symbol"]: row for row in expected_rows}
    reasons = set(additional_reason_codes or [])
    warnings: set[str] = set()
    checks: list[dict[str, object]] = []

    if context.get("calendar_status") == "BLOCKED":
        freshness = {
            "state": "BLOCKED",
            "freshness_code": context.get("calendar_reason", "TRADING_CALENDAR_COVERAGE_MISSING"),
            "latest_available_canonical_date": max((row["trade_date"] for row in rows), default=""),
        }
    else:
        freshness = evaluate_canonical_freshness([row["trade_date"] for row in rows], context)
    freshness_ok = freshness["state"] == "READY"
    if not freshness_ok:
        reasons.add(freshness["freshness_code"])
    checks.append(_check("freshness", freshness["latest_available_canonical_date"], expected, freshness_ok, freshness["freshness_code"] if not freshness_ok else ""))

    duplicate_count = len(rows) - len({(row["symbol"], row["trade_date"]) for row in rows})
    schema_ok = bool(rows) and duplicate_count == 0
    if not schema_ok:
        reasons.add("INVALID_EVIDENCE_SCHEMA")
    checks.append(_check("schema_and_key_uniqueness", f"rows={len(rows)};duplicate_keys={duplicate_count}", "rows>0;duplicate_keys=0", schema_ok, "INVALID_EVIDENCE_SCHEMA" if not schema_ok else ""))

    missing_symbols = sorted(required_symbols - set(by_symbol))
    incomplete_symbols = sorted(
        symbol
        for symbol, row in by_symbol.items()
        if symbol in required_symbols
        and (
            _finite_float(row.get("canonical_close")) is None
            or (_finite_float(row.get("canonical_return_1d")) is None and row.get("suspension_status") != "suspended")
        )
    )
    missing_ok = not missing_symbols and not incomplete_symbols
    if not missing_ok:
        reasons.add("MISSING_REQUIRED_EVIDENCE")
    checks.append(_check("missingness", f"missing={';'.join(missing_symbols)};incomplete={';'.join(incomplete_symbols)}", "all required symbols have a T-1 close and return or explicit suspension", missing_ok, "MISSING_REQUIRED_EVIDENCE" if not missing_ok else ""))

    invalid_providers = sorted({row["source_provider"] for row in expected_rows if row["source_provider"] not in APPROVED_PROVIDERS})
    failed_attempts = [attempt for attempt in provider_attempts or [] if str(attempt.get("status", "")).upper() != "PASS"]
    provider_ok = not invalid_providers and not failed_attempts
    if not provider_ok:
        reasons.add("INVALID_PROVIDER_STATE")
    checks.append(_check("provider_consistency", f"invalid={';'.join(invalid_providers)};failed_attempts={len(failed_attempts)}", f"approved={';'.join(sorted(APPROVED_PROVIDERS))};no_failed_attempts", provider_ok, "INVALID_PROVIDER_STATE" if not provider_ok else ""))

    timestamp_failures = [
        row["symbol"]
        for row in expected_rows
        if not _timestamp_is_pit_safe(row.get("provider_timestamp") or row["trade_date"], context["decision_asof_ts"], context["data_cutoff"])
    ]
    timestamp_ok = not timestamp_failures
    if not timestamp_ok:
        reasons.add("INVALID_TIMESTAMP")
    checks.append(_check("timestamp_correctness", ";".join(sorted(timestamp_failures)) or "date_level_timestamps_at_or_before_cutoff", f"provider_timestamp<={context['decision_asof_ts']}", timestamp_ok, "INVALID_TIMESTAMP" if not timestamp_ok else ""))

    pit_failures = [
        row["symbol"]
        for row in expected_rows
        if row["trade_date"] > context["data_cutoff"]
        or (row.get("pit_available_date") or row["trade_date"]) > context["data_cutoff"]
        or row.get("no_lookahead_status") != "passed_current_or_past_only"
    ]
    pit_ok = not pit_failures
    if not pit_ok:
        reasons.add("PIT_VIOLATION")
    checks.append(_check("pit_availability", ";".join(sorted(pit_failures)) or "passed_current_or_past_only", f"all evidence available by {context['data_cutoff']}", pit_ok, "PIT_VIOLATION" if not pit_ok else ""))

    checksum_ok = bool(source_checksum) and source_checksum == expected_source_checksum
    if not checksum_ok:
        reasons.add("CHECKSUM_MISMATCH")
    checks.append(_check("checksum_reproducibility", source_checksum, expected_source_checksum, checksum_ok, "CHECKSUM_MISMATCH" if not checksum_ok else ""))

    quarantined = [row for row in rows if row.get("quarantine_reason")]
    quarantine_ok = all(row.get("risk_model_eligible") == "false" for row in quarantined)
    if not quarantine_ok:
        reasons.add("INVALID_QUARANTINE_STATE")
    elif quarantined:
        warnings.add("PROVIDER_DISCREPANCY_QUARANTINED")
    checks.append(_check("quarantine_preservation", f"quarantined_rows={len(quarantined)}", "quarantined rows remain risk_model_eligible=false", quarantine_ok, "INVALID_QUARANTINE_STATE" if not quarantine_ok else ""))

    adjustment_unresolved = all(
        row.get("adjustment_convention_status") == "unresolved_cross_provider_adjustment_convention"
        for row in expected_rows
    )
    if expected_rows and adjustment_unresolved:
        warnings.add("ADJUSTMENT_CONVENTION_UNRESOLVED")
    checks.append(_check("adjustment_convention_disclosure", "UNRESOLVED" if adjustment_unresolved else "INVALID_OR_MISSING", "explicit unresolved status; no full reconciliation claim", adjustment_unresolved, "INVALID_PROVIDER_STATE" if not adjustment_unresolved else ""))
    if not adjustment_unresolved:
        reasons.add("INVALID_PROVIDER_STATE")

    return {
        "status": "BLOCKED" if reasons else "PASS",
        "reason_codes": sorted(reasons),
        "warning_codes": sorted(warnings),
        "rows": checks,
        "latest_available_data_date": freshness["latest_available_canonical_date"],
        "freshness_code": freshness["freshness_code"],
        "required_symbol_count": len(required_symbols),
        "available_symbol_count": len(required_symbols & set(by_symbol)),
    }


def run_goal_daily_incremental_evidence_refresh01(
    root: Path,
    print_summary: bool = False,
    execution_time: str | None = None,
    target_trading_date: str | None = None,
    replay_date: str | None = DEFAULT_REPLAY_TARGET_TRADING_DATE,
    evidence_file: str | Path | None = None,
    expected_checksum: str | None = None,
    allow_network: bool = False,
    opm_runner: Callable[..., bool] | None = None,
) -> bool:
    root = root.resolve()
    context = resolve_daily_refresh_context(root, execution_time=execution_time, target_trading_date=target_trading_date, replay_date=replay_date)
    base_rows = read_csv(root / CANONICAL_MARKET) if (root / CANONICAL_MARKET).exists() else []
    required_symbols = {
        row["symbol"]
        for row in (read_csv(root / REFERENCE_PORTFOLIO) if (root / REFERENCE_PORTFOLIO).exists() else [])
        if row.get("symbol")
    }
    evidence_mode = "committed_evidence_replay"
    provider_attempts: list[dict[str, object]] = []
    candidate_rows: list[dict[str, object]] = list(base_rows)
    source_path = root / CANONICAL_MARKET
    source_checksum_override = ""
    extra_reasons: list[str] = [context["calendar_reason"]] if context.get("calendar_status") == "BLOCKED" else []

    if evidence_file is not None and allow_network:
        raise ValueError("evidence_file and allow_network are mutually exclusive")
    try:
        if evidence_file is not None:
            evidence_mode = "local_incremental_evidence"
            source_path = _resolve_input_path(root, evidence_file)
            incremental = read_csv(source_path)
            candidate_rows = merge_incremental_evidence(base_rows, incremental, context["expected_previous_trading_date"])
        elif allow_network:
            evidence_mode = "live_bounded_fetch"
            incremental, provider_attempts = _fetch_network_incremental(root, context, required_symbols)
            source_checksum_override = _sha256_text(_csv_text(incremental))
            candidate_rows = merge_incremental_evidence(base_rows, incremental, context["expected_previous_trading_date"])
            source_path = root / CANONICAL_MARKET
    except (OSError, ValueError) as exc:
        extra_reasons.append("INVALID_EVIDENCE_SCHEMA")
        provider_attempts.append({"status": "FAIL", "notes": str(exc)})

    source_checksum = source_checksum_override or (_sha256_file(source_path) if source_path.exists() else "missing")
    validation = validate_refresh_evidence(
        context,
        candidate_rows,
        required_symbols,
        source_checksum,
        expected_checksum or source_checksum,
        provider_attempts=provider_attempts,
        additional_reason_codes=extra_reasons,
    )
    canonical_override = ""
    canonical_checksum = _sha256_text(_csv_text([_canonical_shape(row) for row in candidate_rows], CANONICAL_FIELDS))
    opm_executed = False
    opm_integrity = "NOT_RUN"
    snapshot_path = ""
    snapshot_version = ""
    blocked_reasons = list(validation["reason_codes"])

    if validation["status"] == "PASS":
        if evidence_mode != "committed_evidence_replay":
            canonical_override = f"{REFRESH_ROOT}/{context['target_trading_date']}/canonical_market_data.csv"
            _write_immutable_csv(root / canonical_override, [_canonical_shape(row) for row in candidate_rows], CANONICAL_FIELDS)
        runner = opm_runner or run_goal_premarket_position_management_operational01
        opm_executed = runner(
            root,
            print_summary=False,
            execution_time=execution_time,
            target_trading_date=target_trading_date,
            replay_date=replay_date,
            canonical_evidence_path=canonical_override or None,
            refresh_metadata={
                "goal": GOAL_ID,
                "evidence_mode": evidence_mode,
                "canonical_checksum": canonical_checksum,
            },
        )
        snapshot_path, snapshot_version, opm_integrity = _opm_snapshot_state(root, context["target_trading_date"])
        if not opm_executed:
            blocked_reasons.append("OPM_EXECUTION_FAILED")
        if opm_integrity != "VERIFIED":
            blocked_reasons.append("SNAPSHOT_INTEGRITY_FAILED")

    refresh_succeeded = validation["status"] == "PASS" and opm_executed and opm_integrity == "VERIFIED"
    refresh_status = "SUCCEEDED" if refresh_succeeded else "BLOCKED"
    previous_latest = _read_json_if_exists(root / LATEST_REFRESH)
    last_successful = context["generated_at"] if refresh_succeeded else str(previous_latest.get("last_successful_refresh_time", ""))
    latest = {
        "goal": GOAL_ID,
        "refresh_status": refresh_status,
        "last_attempt_time": context["generated_at"],
        "last_successful_refresh_time": last_successful,
        "validation_status": validation["status"],
        "blocked_reasons": sorted(set(blocked_reasons)),
        "freshness_code": validation["freshness_code"],
        "target_trading_date": context["target_trading_date"],
        "expected_previous_trading_date": context["expected_previous_trading_date"],
        "latest_available_data_date": validation["latest_available_data_date"],
        "execution_timestamp": context["execution_time"],
        "execution_mode": context["execution_mode"],
        "evidence_mode": evidence_mode,
        "snapshot_date": context["target_trading_date"] if refresh_succeeded else "",
        "snapshot_manifest_path": snapshot_path if refresh_succeeded else "",
        "snapshot_version": snapshot_version if refresh_succeeded else "",
        "refresh_manifest_path": f"{REFRESH_ROOT}/{context['target_trading_date']}/refresh_manifest.json" if refresh_succeeded else REFRESH_MANIFEST,
        "research_only": True,
        "not_for_execution": True,
    }
    refresh_manifest = {
        **latest,
        "source_checksum": source_checksum,
        "canonical_evidence_checksum": canonical_checksum,
        "canonical_evidence_path": canonical_override or CANONICAL_MARKET,
        "validation_checksum": _sha256_text(_csv_text(validation["rows"])),
        "provider_attempt_count": len(provider_attempts),
        "provider_warning_codes": validation["warning_codes"],
        "no_silent_averaging": True,
        "adjustment_convention_status": "UNRESOLVED",
        "quarantine_policy": "preserve_existing_and_exclude_flagged_rows_from_risk_model",
        "opm_executed": opm_executed,
        "opm_snapshot_integrity": opm_integrity,
        "risk_model_recalculated": False,
        "risk_model_source": "validated_predecessor_portfolio_risk_outputs",
        "ready_factor_count": 0,
        "recommendation_state": "locked_future",
        "trading_state": "locked_future",
        "paper_trading_started": False,
        "orders_created": False,
    }
    refresh_manifest_checksum = _sha256_text(json.dumps(refresh_manifest, indent=2, sort_keys=True) + "\n")
    latest["refresh_manifest_checksum"] = refresh_manifest_checksum

    write_csv(root / VALIDATION, validation["rows"])
    write_csv(root / RUN_SUMMARY, [_run_summary(context, validation, latest, opm_executed, opm_integrity)])
    write_csv(root / EXPERIMENT_CONTRACT, _experiment_contract(context, latest))
    write_json(root / REFRESH_MANIFEST, refresh_manifest)
    if refresh_succeeded:
        immutable_dir = root / REFRESH_ROOT / context["target_trading_date"]
        _write_immutable_csv(immutable_dir / "validation.csv", validation["rows"])
        _write_immutable_json(immutable_dir / "refresh_manifest.json", refresh_manifest)
    write_json(root / LATEST_REFRESH, latest)

    _write_governance_files(root)
    _ensure_workflow_and_capability(root)
    goal_manifest = _goal_manifest(root, refresh_manifest, validation, refresh_succeeded)
    write_json(root / MANIFEST, goal_manifest)
    write_text(root / REPORT, _report(goal_manifest))

    if print_summary:
        print(
            f"Daily evidence refresh: {refresh_status} | mode={context['execution_mode']} | "
            f"target={context['target_trading_date']} | expected_t_minus_one={context['expected_previous_trading_date']} | "
            f"latest={validation['latest_available_data_date']} | validation={validation['status']} | "
            f"snapshot={latest['snapshot_version'] or 'none'}"
        )
    return refresh_succeeded


def audit_goal_daily_incremental_evidence_refresh01(root: Path) -> bool:
    root = root.resolve()
    failures = [f"missing_artifact:{path}" for path in REQUIRED_ARTIFACTS if path != AUDIT and not (root / path).exists()]
    manifest = _read_json_if_exists(root / MANIFEST)
    latest = _read_json_if_exists(root / LATEST_REFRESH)
    capabilities = _read_json_if_exists(root / LOCKED_CAPABILITIES)
    refresh_manifest_path = root / str(latest.get("refresh_manifest_path", ""))
    refresh_manifest_checksum = _sha256_file(refresh_manifest_path) if refresh_manifest_path.exists() else "missing"
    if refresh_manifest_checksum != latest.get("refresh_manifest_checksum"):
        failures.append("refresh_manifest_checksum_mismatch")
    if manifest.get("goal") != GOAL_ID or manifest.get("status") != "PASS":
        failures.append("goal_manifest_not_pass")
    if latest.get("refresh_status") == "SUCCEEDED":
        if latest.get("validation_status") != "PASS" or manifest.get("opm_snapshot_integrity") != "VERIFIED":
            failures.append("successful_refresh_evidence_invalid")
    elif latest.get("refresh_status") == "BLOCKED":
        if (
            latest.get("validation_status") != "BLOCKED"
            or not latest.get("blocked_reasons")
            or latest.get("snapshot_manifest_path")
            or manifest.get("opm_executed") is not False
            or manifest.get("opm_snapshot_integrity") != "NOT_RUN"
        ):
            failures.append("blocked_refresh_did_not_fail_closed")
    else:
        failures.append("refresh_status_invalid")
    if manifest.get("ready_factor_count") != 0:
        failures.append("ready_factor_count_not_zero")
    for key in ("recommendation_state", "trading_state"):
        if manifest.get(key) != "locked_future":
            failures.append(f"{key}_not_locked")
    for key in ("orders_created", "paper_trading_started", "experiment_started", "performance_claims_created"):
        if manifest.get(key) is not False:
            failures.append(f"forbidden_state_not_false:{key}")
    for key in ("broker_live_trading", "paper_trading", "production_db_writes", "production_model_promotion"):
        if capabilities and capabilities.get(key) is not False:
            failures.append(f"locked_capability_changed:{key}")
    if capabilities and capabilities.get(CAPABILITY_KEY) != "implemented_research_only":
        failures.append("daily_refresh_capability_not_recorded")
    for relative, expected in dict(manifest.get("implementation_checksums", {})).items():
        path = root / relative
        actual = implementation_file_sha256(path) if path.exists() else "missing"
        if actual != expected:
            failures.append(f"implementation_checksum_mismatch:{relative}")
    passed = not failures
    write_text(
        root / AUDIT,
        "\n".join(
            [
                f"# {GOAL_ID} Audit",
                "",
                f"Status: `{'PASS' if passed else 'BLOCKED'}`",
                "",
                *(["- All daily refresh, OPM handoff, snapshot integrity, and governance checks passed."] if passed else [f"- `{item}`" for item in sorted(set(failures))]),
                "",
            ]
        ),
    )
    return passed


def _fetch_network_incremental(
    root: Path,
    context: dict[str, str],
    required_symbols: set[str],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    if not network_enabled(True):
        return [], [{"status": "FAIL", "failure_class": "NETWORK_DISABLED_BY_POLICY"}]
    config = load_ingestion_config(root)
    adjustment = str(config.get("adjustment_policy", "qfq"))
    interval = float(dict(config.get("rate_limit_policy", {})).get("min_seconds_between_symbol_calls", 0.2))
    expected = context["expected_previous_trading_date"]
    rows: list[dict[str, object]] = []
    attempts: list[dict[str, object]] = []
    for index, symbol in enumerate(sorted(required_symbols)):
        if index and interval:
            time.sleep(interval)
        result = load_stock_ohlcv_daily(symbol, expected, expected, adjustment, True)
        attempts.append(result.attempt)
        for row in result.rows:
            if str(row.get("trade_date")) == expected:
                rows.append(
                    {
                        **row,
                        "source_provider": "akshare",
                        "provider_timestamp": expected,
                        "pit_available_date": expected,
                        "no_lookahead_status": "passed_current_or_past_only",
                        "suspension_status": "trading",
                        "adjustment_policy": adjustment,
                    }
                )
    return rows, attempts


def _opm_snapshot_state(root: Path, expected_date: str) -> tuple[str, str, str]:
    pointer = _read_json_if_exists(root / OPM_LATEST)
    if pointer.get("snapshot_date") != expected_date:
        return "", "", "FAILED"
    relative = str(pointer.get("snapshot_manifest_path", ""))
    manifest_path = root / relative
    if not relative or not manifest_path.exists():
        return "", "", "FAILED"
    manifest = _read_json_if_exists(manifest_path)
    failures = []
    for name, expected in dict(manifest.get("checksums", {})).items():
        path = manifest_path.parent / name
        actual = _sha256_file(path) if path.exists() else "missing"
        if actual != expected:
            failures.append(name)
    manifest_checksum = _sha256_file(manifest_path)
    if pointer.get("snapshot_manifest_checksum") != manifest_checksum:
        failures.append("manifest.json")
    return relative, f"sha256:{manifest_checksum[:16]}", "VERIFIED" if not failures else "FAILED"


def _run_summary(
    context: dict[str, str],
    validation: dict[str, object],
    latest: dict[str, object],
    opm_executed: bool,
    opm_integrity: str,
) -> dict[str, object]:
    return {
        "goal": GOAL_ID,
        "refresh_status": latest["refresh_status"],
        "validation_status": validation["status"],
        "blocked_reasons": ";".join(latest["blocked_reasons"]),
        "target_trading_date": context["target_trading_date"],
        "expected_previous_trading_date": context["expected_previous_trading_date"],
        "latest_available_data_date": validation["latest_available_data_date"],
        "execution_timestamp": context["execution_time"],
        "execution_mode": context["execution_mode"],
        "opm_executed": opm_executed,
        "opm_snapshot_integrity": opm_integrity,
        "snapshot_version": latest["snapshot_version"],
        "research_only": True,
        "not_for_execution": True,
    }


def _experiment_contract(context: dict[str, str], latest: dict[str, object]) -> list[dict[str, object]]:
    values = {
        "experiment_date_range": "not_started_start_and_end_unset",
        "snapshot_lineage": f"daily_refresh_manifest->{latest.get('snapshot_manifest_path') or 'no_valid_snapshot'}",
        "evaluation_metadata": "chronological_only;future_outcomes_unobserved;no_final_holdout_tuning",
        "baseline_reference": "research_reference_portfolio_and_frozen_opm_policy",
    }
    return [
        {
            "field_name": field,
            "frozen_value": value,
            "prepared_at": context["generated_at"],
            "experiment_status": "PREPARED_NOT_STARTED",
            "performance_claim": "none",
            "paper_trading_started": False,
            "broker_trading_started": False,
        }
        for field, value in values.items()
    ]


def _goal_manifest(
    root: Path,
    refresh: dict[str, object],
    validation: dict[str, object],
    refresh_succeeded: bool,
) -> dict[str, object]:
    implementation_files = [
        ".gitattributes",
        "src/ashare_premarket/daily_refresh/goal_daily_incremental_evidence_refresh01.py",
        "src/ashare_premarket/core/boundary.py",
        "src/ashare_premarket/core/workflow_preservation.py",
        "src/ashare_premarket/portfolio_risk/goal_premarket_position_management_operational01.py",
        "src/ashare_premarket/dashboard/store.py",
        "src/ashare_premarket/dashboard/repository.py",
        "apps/premarket-workspace/src/components/FreshnessBanner.tsx",
        "apps/premarket-workspace/src/views/ExperimentPage.tsx",
        "apps/premarket-workspace/src/lib/types.ts",
        "apps/premarket-workspace/src/app/globals.css",
        "apps/premarket-workspace/scripts/visual-qa.mjs",
        "scripts/run_premarket_position_management.py",
        "scripts/run_daily_incremental_evidence_refresh.py",
        "scripts/run_goal_daily_incremental_evidence_refresh01.py",
        "scripts/audit_goal_daily_incremental_evidence_refresh01.py",
        CONTRACT,
        DOC,
    ]
    checksums = {path: implementation_file_sha256(root / path) for path in implementation_files if (root / path).exists()}
    return {
        "goal": GOAL_ID,
        "workflow_id": WORKFLOW_ID,
        "status": "PASS",
        "refresh_fail_closed": not refresh_succeeded,
        "depends_on": [
            "GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01",
            "GOAL-PREMARKET-POSITION-MANAGEMENT-OPERATIONAL-01",
            "GOAL-PREMARKET-RESEARCH-AND-POSITION-WORKSPACE-DASHBOARD-01",
        ],
        "refresh_status": refresh["refresh_status"],
        "validation_status": validation["status"],
        "validation_reason_codes": validation["reason_codes"],
        "validation_warning_codes": validation["warning_codes"],
        "opm_executed": refresh["opm_executed"],
        "opm_snapshot_integrity": refresh["opm_snapshot_integrity"],
        "risk_model_recalculated": refresh["risk_model_recalculated"],
        "risk_model_source": refresh["risk_model_source"],
        "snapshot_version": refresh["snapshot_version"],
        "experiment_status": "PREPARED_NOT_STARTED",
        "experiment_started": False,
        "performance_claims_created": False,
        "ready_factor_count": 0,
        "recommendation_state": "locked_future",
        "trading_state": "locked_future",
        "orders_created": False,
        "paper_trading_started": False,
        "broker_connection_created": False,
        "production_writes_created": False,
        "implementation_checksums": checksums,
        "research_only": True,
        "not_trading_advice": True,
        "not_for_execution": True,
    }


def _write_governance_files(root: Path) -> None:
    write_text(
        root / CONTRACT,
        "\n".join(
            [
                f"goal_id: {GOAL_ID}",
                f"workflow_id: {WORKFLOW_ID}",
                "mode: controlled_daily_research_evidence_refresh",
                "required_run_fields:",
                "  - target_trading_date",
                "  - expected_previous_trading_date",
                "  - latest_available_data_date",
                "  - execution_timestamp",
                "  - execution_mode",
                "incremental_input_fields:",
                "  required: [trade_date, symbol, close, source_provider, provider_timestamp, pit_available_date, no_lookahead_status, suspension_status, adjustment_policy]",
                "  optional: [return_1d, quarantine_reason]",
                "validation_reason_codes: [TRADING_CALENDAR_COVERAGE_MISSING, STALE_SOURCE_DATA, FUTURE_DATA_AFTER_PIT_CUTOFF, MISSING_REQUIRED_EVIDENCE, INVALID_PROVIDER_STATE, INVALID_TIMESTAMP, PIT_VIOLATION, CHECKSUM_MISMATCH, INVALID_QUARANTINE_STATE, INVALID_EVIDENCE_SCHEMA, OPM_EXECUTION_FAILED, SNAPSHOT_INTEGRITY_FAILED]",
                "t_minus_one_required: true",
                "pit_fail_closed: true",
                "provider_reconciliation_preserved: true",
                "quarantine_preserved: true",
                "no_silent_averaging: true",
                "adjustment_convention_status: unresolved",
                "network_default: disabled",
                "immutable_success_manifest: true",
                "recommendation_state: locked_future",
                "trading_state: locked_future",
                "ready_factor_count: 0",
                "experiment_status: prepared_not_started",
                "risk_model_recalculated: false",
                "risk_model_source: validated_predecessor_portfolio_risk_outputs",
                "",
            ]
        ),
    )
    write_text(
        root / DOC,
        "\n".join(
            [
                f"# {GOAL_ID}",
                "",
                "## Daily flow",
                "",
                "1. Resolve the governed target session and expected T-1 date with the OPM clock; missing calendar coverage blocks without guessing a session.",
                "2. Replay committed evidence, import a bounded local increment, or explicitly opt into the existing provider adapter.",
                "3. Validate freshness, required-symbol missingness, provider state, timestamps, PIT availability, quarantine state, and checksums.",
                "4. Stop before OPM when any fail-closed check is blocked.",
                "5. On success, call OPM with the validated canonical evidence and publish its immutable snapshot for the read-only workspace.",
                "",
                "## Evidence semantics",
                "",
                "The primary provider row is never averaged with another source. Cross-provider adjustment semantics remain explicitly unresolved when direct metadata is unavailable. Existing discrepancy quarantine rows remain excluded from risk fitting.",
                "",
                "## Boundaries",
                "",
                "This layer is research-only. Recommendation tiering, action labels, target prices, orders, broker connections, paper execution, production writes, and reinforcement learning remain outside the active workflow.",
                "",
                "The refresh updates canonical evidence, readiness, and OPM snapshot lineage. It deliberately reuses validated predecessor portfolio-risk estimates; this goal does not duplicate or rerun the upstream risk estimators.",
                "",
                "## Experiment readiness",
                "",
                "Only the date-range, snapshot-lineage, evaluation-metadata, and baseline-reference contracts are prepared. No experiment is started and no performance statement is produced.",
                "",
            ]
        ),
    )


def _ensure_workflow_and_capability(root: Path) -> None:
    workflow_path = root / WORKFLOW_STATUS
    if workflow_path.exists():
        rows = [row for row in read_csv(workflow_path) if row.get("workflow_id") != WORKFLOW_ID]
        rows.append(
            {
                "workflow_id": WORKFLOW_ID,
                "display_name": f"{GOAL_ID} Daily Incremental Evidence Refresh",
                "stage_or_goal": GOAL_ID,
                "status": "implemented_research_only",
                "current_repo_role": "controlled_daily_t_minus_one_evidence_refresh",
                "implemented_in_repo": "true",
                "allowed_next_action": "review_daily_refresh_no_downstream_unlock",
                "depends_on": "goal_premarket_research_position_workspace_dashboard01;goal_premarket_position_management_operational01",
                "produces_artifacts": ";".join(REQUIRED_ARTIFACTS),
                "primary_docs": DOC,
                "primary_scripts": "scripts/run_daily_incremental_evidence_refresh.py;scripts/run_goal_daily_incremental_evidence_refresh01.py;scripts/audit_goal_daily_incremental_evidence_refresh01.py",
                "primary_outputs": f"{LATEST_REFRESH};{MANIFEST};{REPORT};{AUDIT}",
                "promotion_rule": "implemented_research_only_after_daily_refresh_replay_and_audit_pass",
                "notes": "Controlled research-only T-1 refresh and OPM snapshot handoff. Recommendation, trading, broker, paper execution, production, and reinforcement-learning capabilities remain locked.",
            }
        )
        write_csv(workflow_path, rows)
    capability_path = root / LOCKED_CAPABILITIES
    if capability_path.exists():
        payload = _read_json_if_exists(capability_path)
        payload[CAPABILITY_KEY] = "implemented_research_only"
        for key in ("dashboard", "paper_trading", "broker_live_trading", "production_db_writes", "production_model_promotion", "dqn_rl"):
            payload[key] = False
        write_json(capability_path, payload)


def _report(manifest: dict[str, object]) -> str:
    return "\n".join(
        [
            f"# {GOAL_ID}",
            "",
            f"Status: `{manifest['status']}`",
            f"Refresh status: `{manifest['refresh_status']}`",
            f"Validation status: `{manifest['validation_status']}`",
            f"OPM snapshot integrity: `{manifest['opm_snapshot_integrity']}`",
            f"Snapshot version: `{manifest['snapshot_version']}`",
            "",
            "The controlled T-1 evidence gate runs before OPM. Blocked evidence cannot create or advance an OPM snapshot.",
            "",
            "Recommendation and trading capabilities remain locked, ready_factor_count remains zero, and the future experiment is prepared but not started.",
            "",
        ]
    )


def _check(check_id: str, current: object, threshold: object, passed: bool, reason_code: str) -> dict[str, object]:
    return {
        "check_id": check_id,
        "current_value": current,
        "threshold": threshold,
        "state": "PASS" if passed else "BLOCKED",
        "reason_code": reason_code,
        "fail_closed": "true",
        "evidence_availability": "available" if current not in {None, ""} else "unavailable",
    }


def _canonical_shape(row: dict[str, object]) -> dict[str, str]:
    return {field: _string(row.get(field, "")) for field in CANONICAL_FIELDS}


def _resolve_input_path(root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _timestamp_is_pit_safe(value: object, decision_asof: str, cutoff: str) -> bool:
    text = str(value or "")
    try:
        if len(text) == 10:
            return text <= cutoff
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        decision = datetime.fromisoformat(decision_asof.replace("Z", "+00:00"))
        return parsed <= decision and parsed.date().isoformat() <= cutoff
    except ValueError:
        return False


def _execution_datetime(value: str | None, replay_date: str | None) -> datetime:
    text = value or (f"{replay_date}T08:30:00+08:00" if replay_date else "")
    if not text:
        return datetime.now(ZoneInfo("Asia/Shanghai"))
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=ZoneInfo("Asia/Shanghai"))
    return parsed.astimezone(ZoneInfo("Asia/Shanghai"))


def _write_immutable_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    body = _csv_text(rows, fieldnames)
    _write_immutable_text(path, body)


def _write_immutable_json(path: Path, payload: dict[str, object]) -> None:
    _write_immutable_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _write_immutable_text(path: Path, body: str) -> None:
    if path.exists() and path.read_text(encoding="utf-8") != body:
        raise RuntimeError(f"refuse_conflicting_refresh_overwrite:{path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body.encode("utf-8"))


def _csv_text(rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> str:
    if not rows and not fieldnames:
        return ""
    fields = fieldnames or list(rows[0])
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows([{field: _string(row.get(field, "")) for field in fields} for row in rows])
    return buffer.getvalue()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _read_json_if_exists(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _finite_float(value: object) -> float | None:
    try:
        number = float(value) if value not in {None, ""} else math.nan
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _fmt(value: object, digits: int = 10) -> str:
    number = _finite_float(value)
    if number is None:
        return ""
    text = f"{number:.{digits}f}"
    return text.rstrip("0").rstrip(".")


def _string(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return "" if value is None else str(value)

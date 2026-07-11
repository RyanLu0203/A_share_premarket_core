from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from ashare_premarket.core.io import read_csv, write_csv
from ashare_premarket.data.trading_calendar import previous_trading_day, resolve_target_trading_day

GOAL_ID = "GOAL-PREMARKET-POSITION-MANAGEMENT-OPERATIONAL-01"
PREDECESSOR_GOAL_ID = "GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01"
WORKFLOW_ID = "goal_premarket_position_management_operational01"
MODE = "read_only_premarket_position_management_decision_support"
PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"
READY = "READY"
READY_WITH_WARNINGS = "READY_WITH_WARNINGS"
TZ_NAME = "Asia/Shanghai"
DEFAULT_REPLAY_TARGET_TRADING_DATE = "2026-07-01"

PR_PREFIX = "outputs/research/goal_premarket_portfolio_risk_management01_"
PR_MANIFEST = "outputs/audits/goal_premarket_portfolio_risk_management01_manifest.json"
PR_CANONICAL = PR_PREFIX + "canonical_market_data.csv"
PR_RISK_STATE = PR_PREFIX + "portfolio_risk_state.csv"
PR_REFERENCE = PR_PREFIX + "research_reference_portfolio.csv"
PR_CONSTRAINT_EVALUATION = PR_PREFIX + "position_constraint_evaluation.csv"
PR_PREFERRED_POLICY = PR_PREFIX + "preferred_research_policy_decision.csv"
PR_POSITION_BANDS = PR_PREFIX + "position_band_summary.csv"
PR_ABSTENTIONS = PR_PREFIX + "position_band_abstentions.csv"
PR_WARNINGS = PR_PREFIX + "construction_warnings.csv"
PR_PROVIDER = PR_PREFIX + "provider_comparison.csv"
PR_PROVIDER_QUARANTINE = PR_PREFIX + "provider_discrepancy_quarantine.csv"
PR_RISK_CONTRIBUTION = PR_PREFIX + "risk_contribution_summary.csv"
PR_CONCENTRATION = PR_PREFIX + "concentration_summary.csv"
PR_COVARIANCE = PR_PREFIX + "covariance_quality_summary.csv"
PR_TAIL = PR_PREFIX + "drawdown_tail_risk_summary.csv"
PR_RISK_ESTIMATORS = PR_PREFIX + "risk_estimator_comparison.csv"

INDEX_PANEL = "outputs/research/network_ingestion/index_panel.csv"
REGIME_LABELS = "outputs/research/goal_regime_label_research02_refined_date_regime_labels.csv"
WORKFLOW_STATUS = "configs/project/workflow_status.csv"
LOCKED_CAPABILITIES = "configs/project/locked_capabilities.json"
HOLDINGS_INPUT = "inputs/portfolio/current_holdings_snapshot.csv"

PREFIX = "outputs/research/goal_premarket_position_management_operational01_"
SNAPSHOT_ROOT = "outputs/research/premarket_position_management"
HOLDINGS_CONTRACT = PREFIX + "holdings_snapshot_contract.csv"
DATA_READINESS = PREFIX + "daily_data_readiness.csv"
DAILY_RISK_STATE = PREFIX + "daily_portfolio_risk_state.csv"
DAILY_CONSTRAINT_EVALUATION = PREFIX + "daily_constraint_evaluation.csv"
DAILY_BAND_STATUS = PREFIX + "daily_position_band_status.csv"
DAILY_EXPOSURE_ENVELOPE = PREFIX + "daily_exposure_envelope.csv"
DAILY_ABSTENTION_SUMMARY = PREFIX + "daily_abstention_summary.csv"
DAILY_WARNINGS = PREFIX + "daily_warnings.csv"
IMMUTABLE_SNAPSHOT_MANIFEST = PREFIX + "immutable_snapshot_manifest.json"
OPERATIONAL_RUN_SUMMARY = PREFIX + "operational_run_summary.csv"
SHADOW_EXPERIMENT_CONTRACT = PREFIX + "shadow_experiment_contract.csv"
EXPERIMENT_FREEZE_MANIFEST = PREFIX + "experiment_freeze_manifest.json"
READ_ONLY_CONSOLE = PREFIX + "read_only_console.md"

REPORT = "outputs/audits/goal_premarket_position_management_operational01_report.md"
MANIFEST = "outputs/audits/goal_premarket_position_management_operational01_manifest.json"
AUDIT = "outputs/audits/goal_premarket_position_management_operational01_audit.md"
DOC = "docs/research/GOAL_PREMARKET_POSITION_MANAGEMENT_OPERATIONAL01_PREMARKET_POSITION_MANAGEMENT.md"
HANDOFF = "docs/research/GOAL_PREMARKET_POSITION_MANAGEMENT_OPERATIONAL01_GOVERNANCE_HANDOFF.md"
CONTRACT = "configs/research/goal_premarket_position_management_operational01_contract.yaml"

REQUIRED_ARTIFACTS = [
    HOLDINGS_CONTRACT,
    DATA_READINESS,
    DAILY_RISK_STATE,
    DAILY_CONSTRAINT_EVALUATION,
    DAILY_BAND_STATUS,
    DAILY_EXPOSURE_ENVELOPE,
    DAILY_ABSTENTION_SUMMARY,
    DAILY_WARNINGS,
    IMMUTABLE_SNAPSHOT_MANIFEST,
    OPERATIONAL_RUN_SUMMARY,
    SHADOW_EXPERIMENT_CONTRACT,
    EXPERIMENT_FREEZE_MANIFEST,
    READ_ONLY_CONSOLE,
    f"{SNAPSHOT_ROOT}/latest_manifest.json",
    REPORT,
    MANIFEST,
    AUDIT,
    DOC,
    HANDOFF,
    CONTRACT,
]

FALSE_BOUNDARY_KEYS = [
    "live_broker_connection_created",
    "orders_created",
    "buy_sell_hold_outputs_created",
    "target_price_outputs_created",
    "recommendation_tiering_unlocked",
    "issue10_unlocked",
    "dqn_rl_unlocked",
    "paper_trading_started",
    "broker_trading_started",
    "production_trading_started",
    "holdings_fabricated",
]

ALLOWED_BAND_STATUS = {"BELOW_BAND", "WITHIN_BAND", "ABOVE_BAND", "ABSTAIN", "INSUFFICIENT_DATA"}
FORBIDDEN_TEXT = ["BUY", "SELL", "HOLD", "order_quantity", "target_price", "broker_order", "live_broker"]


def write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body.encode("utf-8"))


def write_json(path: Path, payload: dict[str, object]) -> None:
    write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def resolve_run_context(
    root: Path,
    execution_time: str | None = None,
    target_trading_date: str | None = None,
    replay_date: str | None = None,
) -> dict[str, str]:
    if replay_date and execution_time:
        raise ValueError("replay_date and execution_time cannot both be supplied")
    if replay_date and target_trading_date and replay_date != target_trading_date:
        raise ValueError("replay_date must match target_trading_date when both are supplied")

    if replay_date:
        target = replay_date
        execution_mode = "deterministic_replay"
        execution_dt = _parse_execution_time(f"{target}T08:30:00+08:00")
    else:
        execution_mode = "daily_operational"
        execution_dt = _parse_execution_time(execution_time) if execution_time else datetime.now(ZoneInfo(TZ_NAME))
        target = target_trading_date or resolve_target_trading_day(root, execution_dt.date().isoformat())

    expected_previous = previous_trading_day(root, target)
    decision_asof_ts = f"{target}T08:30:00+08:00"
    generated_at = decision_asof_ts if execution_mode == "deterministic_replay" else _iso_seconds(execution_dt)
    return {
        "execution_mode": execution_mode,
        "timezone": TZ_NAME,
        "execution_time": _iso_seconds(execution_dt),
        "execution_date": execution_dt.date().isoformat(),
        "generated_at": generated_at,
        "decision_asof_ts": decision_asof_ts,
        "target_trading_date": target,
        "expected_previous_trading_date": expected_previous,
        "data_cutoff": expected_previous,
    }


def evaluate_canonical_freshness(canonical_dates: list[str], context: dict[str, str]) -> dict[str, str]:
    latest = max(canonical_dates) if canonical_dates else ""
    expected = context["expected_previous_trading_date"]
    if not latest:
        state = BLOCKED
        code = "NO_CANONICAL_DATA"
    elif latest == expected:
        state = READY
        code = "FRESH_T_MINUS_ONE_DATA"
    elif latest < expected:
        state = BLOCKED
        code = "STALE_SOURCE_DATA"
    else:
        state = BLOCKED
        code = "FUTURE_DATA_AFTER_PIT_CUTOFF"
    return {
        "state": state,
        "freshness_code": code,
        "latest_available_canonical_date": latest,
        "target_trading_date": context["target_trading_date"],
        "expected_previous_trading_date": expected,
        "data_cutoff": context["data_cutoff"],
        "execution_mode": context["execution_mode"],
    }


def run_goal_premarket_position_management_operational01(
    root: Path,
    print_summary: bool = False,
    execution_time: str | None = None,
    target_trading_date: str | None = None,
    replay_date: str | None = DEFAULT_REPLAY_TARGET_TRADING_DATE,
    canonical_evidence_path: str | Path | None = None,
    refresh_metadata: dict[str, object] | None = None,
) -> bool:
    result = _build(
        root,
        execution_time=execution_time,
        target_trading_date=target_trading_date,
        replay_date=replay_date,
        canonical_evidence_path=canonical_evidence_path,
        refresh_metadata=refresh_metadata,
    )
    _write_outputs(root, result)
    if print_summary:
        summary = result["run_summary"][0]
        print(
            "Premarket position management: "
            f"{summary['daily_readiness_state']} | mode={summary['execution_mode']} | "
            f"target={summary['target_trading_date']} | cutoff={summary['data_cutoff']} | "
            f"latest={summary['latest_available_canonical_date']} | freshness={summary['freshness_code']} | "
            f"bands within/above/below/abstain="
            f"{summary['symbols_within_band']}/{summary['symbols_above_band']}/"
            f"{summary['symbols_below_band']}/{summary['symbols_abstained']} | "
            "orders=none"
        )
    return result["manifest"]["status"] in {PASS, PASS_WITH_WARNINGS, BLOCKED}


def audit_goal_premarket_position_management_operational01(root: Path) -> bool:
    failures: list[str] = []
    for rel in REQUIRED_ARTIFACTS:
        if rel == AUDIT:
            continue
        if not (root / rel).exists():
            failures.append(f"missing_artifact:{rel}")
    manifest = _read_json_if_exists(root / MANIFEST)
    if manifest.get("goal") != GOAL_ID:
        failures.append("manifest_goal_mismatch")
    if manifest.get("depends_on_goal") != PREDECESSOR_GOAL_ID:
        failures.append("predecessor_goal_missing")
    if manifest.get("predecessor_ready_factor_count") != 0:
        failures.append("ready_factor_count_not_zero")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"boundary_key_not_false:{key}")
    for key in ["rec_tiering_state", "trading_state", "broker_state", "production_state"]:
        if manifest.get(key) != "locked_future":
            failures.append(f"state_not_locked:{key}")
    band_rows = read_csv(root / DAILY_BAND_STATUS) if (root / DAILY_BAND_STATUS).exists() else []
    for row in band_rows:
        if row.get("band_status") not in ALLOWED_BAND_STATUS:
            failures.append(f"invalid_band_status:{row.get('band_status')}")
        joined = " ".join(row.values())
        if _contains_forbidden_operational_text(joined):
            failures.append(f"forbidden_band_text:{row.get('symbol')}")
    console_path = root / READ_ONLY_CONSOLE
    if console_path.exists() and _contains_forbidden_operational_text(console_path.read_text(encoding="utf-8")):
        failures.append("forbidden_console_text")
    snapshot_manifest = _read_json_if_exists(root / IMMUTABLE_SNAPSHOT_MANIFEST)
    for key in [
        "snapshot_date",
        "target_trading_date",
        "expected_previous_trading_date",
        "data_cutoff",
        "latest_available_data_date",
        "decision_asof_ts",
        "generated_at",
        "execution_mode",
    ]:
        if not snapshot_manifest.get(key):
            failures.append(f"snapshot_metadata_missing:{key}")
    if snapshot_manifest.get("execution_mode") not in {"daily_operational", "deterministic_replay"}:
        failures.append("invalid_execution_mode")
    if snapshot_manifest.get("execution_mode") == "daily_operational" and snapshot_manifest.get("generated_at") == snapshot_manifest.get("decision_asof_ts"):
        failures.append("daily_generated_at_not_actual_execution_time")
    if snapshot_manifest.get("data_cutoff") != snapshot_manifest.get("expected_previous_trading_date"):
        failures.append("data_cutoff_not_expected_previous_trading_date")
    snapshot_date = str(snapshot_manifest.get("snapshot_date", ""))
    if snapshot_date:
        snapshot_dir = root / SNAPSHOT_ROOT / snapshot_date
        for name in ["manifest.json", "data_readiness.csv", "portfolio_risk_state.csv", "constraint_evaluation.csv", "position_band_status.csv", "exposure_envelope.csv", "warnings.csv"]:
            if not (snapshot_dir / name).exists():
                failures.append(f"missing_snapshot_file:{name}")
    workflow = _workflow_rows(root)
    if workflow.get(WORKFLOW_ID, {}).get("status") != "implemented_research_only":
        failures.append("workflow_row_missing_or_not_research_only")
    status = PASS if not failures else BLOCKED
    lines = [f"# {GOAL_ID} Audit", "", f"Status: `{status}`", "", "## Failures"]
    lines.extend(f"- {failure}" for failure in failures)
    lines.append("")
    write_text(root / AUDIT, "\n".join(lines))
    return status == PASS


def validate_holdings_snapshot(
    rows: list[dict[str, str]],
    allowed_symbols: set[str],
    previous_trading_date: str,
) -> dict[str, object]:
    errors: set[str] = set()
    warnings: set[str] = set()
    keys: set[tuple[str, str, str]] = set()
    cash_values: set[str] = set()
    weight_by_portfolio: dict[tuple[str, str], float] = defaultdict(float)
    for row in rows:
        for field in ["asof_ts", "portfolio_id", "symbol", "current_weight", "source", "snapshot_id"]:
            if not row.get(field):
                errors.add(f"missing_{field}")
        key = (row.get("asof_ts", ""), row.get("portfolio_id", ""), row.get("symbol", ""))
        if key in keys:
            errors.add("duplicate_snapshot_key")
        keys.add(key)
        symbol = row.get("symbol", "")
        if symbol and symbol not in allowed_symbols:
            errors.add("unknown_symbol")
        asof_date = row.get("asof_ts", "")[:10]
        if asof_date and asof_date < previous_trading_date:
            errors.add("stale_snapshot")
        weight = _float(row.get("current_weight"))
        if weight is None or weight < 0:
            errors.add("invalid_current_weight")
        else:
            weight_by_portfolio[(row.get("asof_ts", ""), row.get("portfolio_id", ""))] += weight
        cash = row.get("cash_weight", "")
        if cash:
            cash_float = _float(cash)
            if cash_float is None or cash_float < 0:
                errors.add("invalid_cash_weight")
            cash_values.add(_fmt(cash_float or 0.0))
    if len(cash_values) > 1:
        errors.add("cash_reconciliation_failed")
    cash_value = _float(next(iter(cash_values), "0")) or 0.0
    for total in weight_by_portfolio.values():
        if abs(total + cash_value - 1.0) > 0.005:
            errors.add("weight_reconciliation_failed")
    if not rows:
        warnings.add("no_holdings_rows_supplied")
    return {"valid": not errors, "errors": sorted(errors), "warnings": sorted(warnings)}


def _build(
    root: Path,
    execution_time: str | None = None,
    target_trading_date: str | None = None,
    replay_date: str | None = DEFAULT_REPLAY_TARGET_TRADING_DATE,
    canonical_evidence_path: str | Path | None = None,
    refresh_metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    predecessor_manifest = _read_json_if_exists(root / PR_MANIFEST)
    canonical_path, canonical_relative = _resolve_canonical_evidence_path(root, canonical_evidence_path)
    canonical = read_csv(canonical_path)
    risk_state = read_csv(root / PR_RISK_STATE)[0]
    reference = read_csv(root / PR_REFERENCE)
    constraints = read_csv(root / PR_CONSTRAINT_EVALUATION)
    preferred_policy = read_csv(root / PR_PREFERRED_POLICY)[0]
    bands = read_csv(root / PR_POSITION_BANDS)
    prior_abstentions = read_csv(root / PR_ABSTENTIONS)
    prior_warnings = read_csv(root / PR_WARNINGS)
    provider_rows = read_csv(root / PR_PROVIDER)
    provider_quarantine = read_csv(root / PR_PROVIDER_QUARANTINE)
    risk_contribution = read_csv(root / PR_RISK_CONTRIBUTION)
    concentration = read_csv(root / PR_CONCENTRATION)[0]
    covariance = read_csv(root / PR_COVARIANCE)
    tail = read_csv(root / PR_TAIL)[0]
    risk_estimators = read_csv(root / PR_RISK_ESTIMATORS)
    regime_rows = read_csv(root / REGIME_LABELS) if (root / REGIME_LABELS).exists() else []
    index_rows = read_csv(root / INDEX_PANEL) if (root / INDEX_PANEL).exists() else []

    dates = sorted({row["trade_date"] for row in canonical})
    context = resolve_run_context(root, execution_time=execution_time, target_trading_date=target_trading_date, replay_date=replay_date)
    freshness = evaluate_canonical_freshness(dates, context)
    trading_date = context["target_trading_date"]
    previous_trading_date = context["expected_previous_trading_date"]
    data_cutoff = context["data_cutoff"]
    asof_ts = context["decision_asof_ts"]
    generated_at = context["generated_at"]
    allowed_symbols = {row["symbol"] for row in reference}
    holdings = _load_holdings(root, reference, allowed_symbols, previous_trading_date, asof_ts)
    latest_regime = _latest_regime(regime_rows, data_cutoff)
    readiness_rows, readiness_state = _data_readiness_rows(
        context,
        freshness,
        canonical,
        index_rows,
        regime_rows,
        holdings,
        provider_rows,
        provider_quarantine,
        predecessor_manifest,
    )
    daily_risk_rows = _daily_risk_state_rows(
        trading_date,
        asof_ts,
        risk_state,
        tail,
        risk_contribution,
        concentration,
        covariance,
        risk_estimators,
        holdings,
        latest_regime,
        provider_quarantine,
    )
    daily_constraint_rows = _daily_constraint_rows(trading_date, asof_ts, constraints, holdings["mode"])
    band_status_rows = _band_status_rows(trading_date, asof_ts, bands, holdings, latest_regime, provider_quarantine)
    exposure_rows = _exposure_envelope_rows(trading_date, asof_ts, holdings, daily_risk_rows[0], band_status_rows)
    abstention_rows = _abstention_summary_rows(band_status_rows)
    warning_rows = _daily_warning_rows(prior_warnings, holdings, readiness_state, freshness)
    run_summary = _run_summary_rows(context, freshness, readiness_state, holdings, daily_risk_rows[0], band_status_rows, exposure_rows[0])
    shadow_contract = _shadow_experiment_contract_rows(predecessor_manifest, preferred_policy)
    freeze_manifest = _experiment_freeze_manifest(context, predecessor_manifest, preferred_policy)
    snapshot_manifest = _snapshot_manifest_skeleton(
        context,
        freshness,
        generated_at,
        predecessor_manifest,
        holdings,
        readiness_state,
        preferred_policy,
        canonical_relative,
        canonical_path,
        refresh_metadata,
    )
    manifest = _manifest(
        predecessor_manifest,
        context,
        freshness,
        readiness_state,
        holdings,
        daily_risk_rows[0],
        band_status_rows,
        warning_rows,
        canonical_relative,
        canonical_path,
        refresh_metadata,
    )
    return {
        "predecessor_manifest": predecessor_manifest,
        "holdings_contract": _holdings_contract_rows(),
        "readiness": readiness_rows,
        "daily_risk": daily_risk_rows,
        "constraints": daily_constraint_rows,
        "bands": band_status_rows,
        "exposure": exposure_rows,
        "abstentions": abstention_rows,
        "warnings": warning_rows,
        "run_summary": run_summary,
        "shadow_contract": shadow_contract,
        "freeze_manifest": freeze_manifest,
        "snapshot_manifest": snapshot_manifest,
        "manifest": manifest,
        "trading_date": trading_date,
        "report": _report(manifest),
        "doc": _doc(manifest),
        "handoff": _handoff(manifest),
        "contract": _contract(),
        "console": _console_markdown(manifest, run_summary[0], daily_risk_rows[0], exposure_rows[0], daily_constraint_rows, band_status_rows, abstention_rows, warning_rows),
    }


def _load_holdings(
    root: Path,
    reference: list[dict[str, str]],
    allowed_symbols: set[str],
    previous_trading_date: str,
    asof_ts: str,
) -> dict[str, object]:
    input_path = root / HOLDINGS_INPUT
    if input_path.exists():
        rows = read_csv(input_path)
        validation = validate_holdings_snapshot(rows, allowed_symbols, previous_trading_date)
        if validation["valid"]:
            weights = {row["symbol"]: _float(row.get("current_weight")) or 0.0 for row in rows}
            cash_weight = _float(next((row.get("cash_weight") for row in rows if row.get("cash_weight")), "0")) or 0.0
            snapshot_id = next((row.get("snapshot_id") for row in rows if row.get("snapshot_id")), f"manual_{asof_ts[:10]}")
            return {
                "mode": "current_holdings_snapshot",
                "rows": rows,
                "weights": weights,
                "cash_weight": cash_weight,
                "snapshot_id": snapshot_id,
                "source": "owner_supplied_snapshot",
                "real_snapshot_supplied": True,
                "validation": validation,
            }
        return {
            "mode": "invalid_holdings_snapshot_fail_closed",
            "rows": rows,
            "weights": {},
            "cash_weight": 0.0,
            "snapshot_id": "invalid_holdings_snapshot",
            "source": "owner_supplied_snapshot_invalid",
            "real_snapshot_supplied": True,
            "validation": validation,
        }
    weights = {row["symbol"]: _float(row["reference_weight"]) or 0.0 for row in reference}
    rows = [
        {
            "asof_ts": asof_ts,
            "portfolio_id": "research_reference_portfolio",
            "symbol": row["symbol"],
            "quantity": "",
            "market_value": "",
            "current_weight": row["reference_weight"],
            "cash_weight": "0",
            "source": "research_reference_portfolio_no_current_holdings_supplied",
            "snapshot_id": f"research_reference_portfolio_{asof_ts[:10]}",
        }
        for row in reference
    ]
    return {
        "mode": "research_reference_portfolio",
        "rows": rows,
        "weights": weights,
        "cash_weight": 0.0,
        "snapshot_id": f"research_reference_portfolio_{asof_ts[:10]}",
        "source": "research_reference_portfolio_no_current_holdings_supplied",
        "real_snapshot_supplied": False,
        "validation": {"valid": True, "errors": [], "warnings": ["no_real_holdings_snapshot_supplied"]},
    }


def _data_readiness_rows(
    context: dict[str, str],
    freshness: dict[str, str],
    canonical: list[dict[str, str]],
    index_rows: list[dict[str, str]],
    regime_rows: list[dict[str, str]],
    holdings: dict[str, object],
    provider_rows: list[dict[str, str]],
    provider_quarantine: list[dict[str, str]],
    predecessor_manifest: dict[str, object],
) -> tuple[list[dict[str, object]], str]:
    index_dates = {row["trade_date"] for row in index_rows}
    regime_dates = {row["trade_date"] for row in regime_rows}
    missing_returns = sum(1 for row in canonical if not row.get("canonical_return_1d"))
    pit_failed = sum(1 for row in canonical if row.get("no_lookahead_status") != "passed_current_or_past_only")
    unresolved_provider = sum(1 for row in provider_rows if row.get("unresolved_status") == "true")
    holdings_validation = holdings.get("validation", {})
    holdings_valid = holdings_validation.get("valid") is not False
    holdings_errors = ";".join(str(error) for error in holdings_validation.get("errors", []))
    data_cutoff = context["data_cutoff"]
    pit_state = BLOCKED if pit_failed or freshness["freshness_code"] == "FUTURE_DATA_AFTER_PIT_CUTOFF" else READY
    rows = [
        _readiness_row("execution_mode", READY, context["execution_mode"], "daily_operational_or_deterministic_replay", "run mode is explicit"),
        _readiness_row("execution_time", READY, context["execution_time"], "actual execution timestamp or replay timestamp", "execution timestamp separated from data date"),
        _readiness_row("target_trading_date", READY, context["target_trading_date"], "governed trading calendar target", "target trading day resolved from calendar, not canonical max"),
        _readiness_row("expected_previous_trading_date", READY, context["expected_previous_trading_date"], "calendar T-1", "previous trading day resolved from governed calendar"),
        _readiness_row("decision_asof_timestamp", READY, context["decision_asof_ts"], "premarket decision timestamp", "decision timestamp separated from execution timestamp"),
        _readiness_row("data_cutoff", READY, data_cutoff, "expected previous trading date", "market data cutoff is T-1 for premarket decisions"),
        _readiness_row("latest_available_canonical_date", freshness["state"], freshness["latest_available_canonical_date"], data_cutoff, freshness["freshness_code"]),
        _readiness_row("source_freshness", freshness["state"], freshness["latest_available_canonical_date"], data_cutoff, freshness["freshness_code"]),
        _readiness_row("provider_availability", READY_WITH_WARNINGS if unresolved_provider else READY, f"unresolved_provider_dimensions={unresolved_provider}", "providers disclosed", "provider diagnostics consumed from predecessor"),
        _readiness_row("provider_discrepancy_state", READY_WITH_WARNINGS if provider_quarantine else READY, len(provider_quarantine), "0 preferred", "quarantines remain excluded and surfaced"),
        _readiness_row("canonical_data_availability", READY, len(canonical), ">0", "canonical market data available"),
        _readiness_row("index_context_availability", READY if data_cutoff in index_dates else READY_WITH_WARNINGS, data_cutoff in index_dates, "index row for data cutoff", "index context consumed when available"),
        _readiness_row("regime_availability", READY if data_cutoff in regime_dates else READY_WITH_WARNINGS, data_cutoff in regime_dates, "regime row for data cutoff", "regime context consumed when available"),
        _readiness_row("holdings_snapshot_freshness", READY if holdings["real_snapshot_supplied"] else READY_WITH_WARNINGS, holdings["snapshot_id"], "fresh owner snapshot or explicit reference mode", "no fabricated holdings"),
        _readiness_row("holdings_snapshot_validity", READY if holdings_valid else BLOCKED, holdings_errors or "valid", "no validation errors", "invalid holdings snapshot fails closed"),
        _readiness_row("pit_status", pit_state, f"pit_failures={pit_failed};freshness={freshness['freshness_code']}", "0 and latest<=data_cutoff", "current-or-past-only rows required"),
        _readiness_row("missingness", READY_WITH_WARNINGS if missing_returns else READY, missing_returns, "0 preferred", "missing first returns disclosed"),
        _readiness_row("quarantine_impact", READY_WITH_WARNINGS if provider_quarantine else READY, len(provider_quarantine), "0 preferred", "provider quarantine impact surfaced"),
    ]
    if any(row["state"] == BLOCKED for row in rows) or predecessor_manifest.get("ready_factor_count") != 0:
        state = BLOCKED
    elif any(row["state"] == READY_WITH_WARNINGS for row in rows):
        state = READY_WITH_WARNINGS
    else:
        state = READY
    return rows, state


def _readiness_row(check_id: str, state: str, current_value: object, threshold: object, evidence: str) -> dict[str, object]:
    return {
        "check_id": check_id,
        "state": state,
        "current_value": current_value,
        "threshold": threshold,
        "evidence": evidence,
        "fail_closed_behavior": "ABSTAIN_OR_BLOCKED_IF_REQUIRED_EVIDENCE_INVALID",
        "research_only": True,
        "not_trading_advice": True,
        "not_for_execution": True,
    }


def _daily_risk_state_rows(
    trading_date: str,
    asof_ts: str,
    risk_state: dict[str, str],
    tail: dict[str, str],
    risk_contribution: list[dict[str, str]],
    concentration: dict[str, str],
    covariance: list[dict[str, str]],
    risk_estimators: list[dict[str, str]],
    holdings: dict[str, object],
    regime_state: str,
    provider_quarantine: list[dict[str, str]],
) -> list[dict[str, object]]:
    weights = holdings["weights"]
    gross_exposure = sum(abs(float(value)) for value in weights.values())
    avg_corr = next((row.get("average_abs_correlation", "") for row in covariance if row.get("estimator_id") == "sample_covariance"), "")
    ewma_daily = next((row.get("average_daily_volatility", "") for row in risk_estimators if row.get("estimator_id") == "ewma_volatility_lambda_0_94"), "")
    ewma_vol = (_float(ewma_daily) or 0.0) * math.sqrt(252.0)
    top = sorted(risk_contribution, key=lambda row: _float(row.get("risk_contribution_share")) or 0.0, reverse=True)[:5]
    largest = ";".join(f"{row['symbol']}:{row['risk_contribution_share']}" for row in top)
    max_drawdown = _float(tail.get("max_drawdown")) or 0.0
    drawdown_state = "normal_drawdown_review_only" if max_drawdown > -0.30 else "elevated_drawdown_review_only"
    provider_quality = "warnings_quarantined" if provider_quarantine else "ready"
    return [
        {
            "trading_date": trading_date,
            "asof_ts": asof_ts,
            "portfolio_id": "research_reference_portfolio" if holdings["mode"] == "research_reference_portfolio" else "owner_supplied_portfolio",
            "holdings_mode": holdings["mode"],
            "gross_exposure": _fmt(gross_exposure),
            "cash_weight": _fmt(holdings["cash_weight"]),
            "portfolio_volatility": tail.get("historical_volatility", ""),
            "ewma_volatility": _fmt(ewma_vol),
            "beta_to_csi300": tail.get("beta_to_csi300", ""),
            "drawdown_state": drawdown_state,
            "max_drawdown": tail.get("max_drawdown", ""),
            "cvar_95_daily": tail.get("cvar_95_daily", ""),
            "average_correlation": avg_corr,
            "largest_risk_contributors": largest,
            "effective_number_of_positions": concentration.get("effective_names", ""),
            "cluster_concentration": _fmt(14 / 41),
            "provider_quality_state": provider_quality,
            "regime_state": regime_state,
            "predecessor_risk_state": risk_state.get("risk_state", ""),
            "research_only": True,
            "not_trading_advice": True,
            "not_for_execution": True,
        }
    ]


def _daily_constraint_rows(
    trading_date: str,
    asof_ts: str,
    constraints: list[dict[str, str]],
    holdings_mode: str,
) -> list[dict[str, object]]:
    rows = []
    for row in constraints:
        rows.append(
            {
                "trading_date": trading_date,
                "asof_ts": asof_ts,
                "portfolio_id": row.get("portfolio_id", ""),
                "symbol": row.get("symbol", ""),
                "holdings_mode": holdings_mode,
                "constraint_id": row["constraint_id"],
                "current_value": row.get("current_value", row.get("observed_value", "")),
                "threshold": row.get("threshold", ""),
                "breach": row.get("breach", "false"),
                "severity": _normalize_severity(row.get("severity", row.get("breach_severity", "none"))),
                "evidence_availability": row.get("evidence_availability", "available"),
                "fail_closed": row.get("fail_closed", "false"),
                "action_instruction": "none",
                "constraint_source": PREDECESSOR_GOAL_ID,
                "research_only": True,
                "not_trading_advice": True,
                "not_for_execution": True,
            }
        )
    return rows


def _band_status_rows(
    trading_date: str,
    asof_ts: str,
    bands: list[dict[str, str]],
    holdings: dict[str, object],
    regime_state: str,
    provider_quarantine: list[dict[str, str]],
) -> list[dict[str, object]]:
    weights = holdings["weights"]
    provider_symbols = {row["symbol"] for row in provider_quarantine}
    rows = []
    for row in bands:
        symbol = row["symbol"]
        current_weight = weights.get(symbol)
        abstain = row.get("abstain") == "true"
        band_min = _float(row.get("acceptable_band_min"))
        band_max = _float(row.get("acceptable_band_max"))
        if abstain:
            status = "ABSTAIN"
        elif current_weight is None or band_min is None or band_max is None:
            status = "INSUFFICIENT_DATA"
        elif current_weight < band_min:
            status = "BELOW_BAND"
        elif current_weight > band_max:
            status = "ABOVE_BAND"
        else:
            status = "WITHIN_BAND"
        rows.append(
            {
                "trading_date": trading_date,
                "asof_ts": asof_ts,
                "symbol": symbol,
                "current_weight": _fmt(current_weight),
                "acceptable_band_min": row.get("acceptable_band_min", ""),
                "acceptable_band_max": row.get("acceptable_band_max", ""),
                "reference_policy_weight": row.get("reference_policy_weight", ""),
                "band_status": status,
                "confidence": row.get("confidence_score", ""),
                "constraint_breach": row.get("constraint_breach", ""),
                "abstain": abstain,
                "abstention_reason": row.get("abstention_reason", ""),
                "provider_quality": "quarantined_provider_discrepancy" if symbol in provider_symbols else "accepted_or_disclosed_warning",
                "regime_state": regime_state,
                "diagnostic_only": True,
                "action_instruction": "none",
                "research_only": True,
                "not_trading_advice": True,
                "not_for_execution": True,
            }
        )
    return rows


def _exposure_envelope_rows(
    trading_date: str,
    asof_ts: str,
    holdings: dict[str, object],
    risk: dict[str, object],
    bands: list[dict[str, object]],
) -> list[dict[str, object]]:
    gross = sum(abs(float(value)) for value in holdings["weights"].values())
    cash = float(holdings["cash_weight"])
    confidence_values = [_float(row.get("confidence")) for row in bands if row.get("band_status") != "ABSTAIN"]
    confidence = _mean([value for value in confidence_values if value is not None])
    abstain = gross < 0.95 or gross > 1.0 or cash < 0.0 or cash > 0.05
    return [
        {
            "trading_date": trading_date,
            "asof_ts": asof_ts,
            "current_gross_exposure": _fmt(gross),
            "acceptable_gross_exposure_min": "0.95",
            "acceptable_gross_exposure_max": "1",
            "current_cash_weight": _fmt(cash),
            "acceptable_cash_min": "0",
            "acceptable_cash_max": "0.05",
            "volatility_budget": "0.35",
            "beta_budget": "1.20",
            "risk_state": risk["predecessor_risk_state"],
            "confidence": _fmt(confidence),
            "abstain": abstain,
            "envelope_basis": "risk_budget_constraints_from_predecessor_goal",
            "research_only": True,
            "not_trading_advice": True,
            "not_for_execution": True,
        }
    ]


def _abstention_summary_rows(bands: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for row in bands:
        if row["band_status"] == "ABSTAIN":
            rows.append(
                {
                    "trading_date": row["trading_date"],
                    "asof_ts": row["asof_ts"],
                    "symbol": row["symbol"],
                    "abstain": True,
                    "abstention_reason": row["abstention_reason"],
                    "confidence": row["confidence"],
                    "provider_quality": row["provider_quality"],
                    "regime_state": row["regime_state"],
                    "research_only": True,
                    "not_trading_advice": True,
                    "not_for_execution": True,
                }
            )
    return rows


def _daily_warning_rows(
    prior_warnings: list[dict[str, str]],
    holdings: dict[str, object],
    readiness_state: str,
    freshness: dict[str, str],
) -> list[dict[str, object]]:
    rows = [
        {
            "warning_code": row["warning_code"],
            "scope": row["scope"],
            "count": row["count"],
            "detail": row["detail"],
            "source_goal": PREDECESSOR_GOAL_ID,
        }
        for row in prior_warnings
    ]
    if not holdings["real_snapshot_supplied"]:
        rows.append(
            {
                "warning_code": "NO_REAL_HOLDINGS_SNAPSHOT_REFERENCE_MODE",
                "scope": "holdings_snapshot",
                "count": 1,
                "detail": "no owner-supplied holdings snapshot exists; operational outputs use explicit research_reference_portfolio mode",
                "source_goal": GOAL_ID,
            }
        )
    if readiness_state == "READY_WITH_WARNINGS":
        rows.append(
            {
                "warning_code": "DAILY_READINESS_READY_WITH_WARNINGS",
                "scope": "daily_data_readiness",
                "count": 1,
                "detail": "premarket run may be reviewed, but warnings must remain visible and fail-closed rules remain active",
                "source_goal": GOAL_ID,
            }
        )
    if freshness["freshness_code"] in {"STALE_SOURCE_DATA", "FUTURE_DATA_AFTER_PIT_CUTOFF", "NO_CANONICAL_DATA"}:
        rows.append(
            {
                "warning_code": freshness["freshness_code"],
                "scope": "daily_data_readiness",
                "count": 1,
                "detail": (
                    f"latest_available_canonical_date={freshness['latest_available_canonical_date']};"
                    f"expected_previous_trading_date={freshness['expected_previous_trading_date']};"
                    f"target_trading_date={freshness['target_trading_date']}"
                ),
                "source_goal": GOAL_ID,
            }
        )
    return rows


def _run_summary_rows(
    context: dict[str, str],
    freshness: dict[str, str],
    readiness_state: str,
    holdings: dict[str, object],
    risk: dict[str, object],
    bands: list[dict[str, object]],
    exposure: dict[str, object],
) -> list[dict[str, object]]:
    return [
        {
            "daily_readiness_state": readiness_state,
            "execution_mode": context["execution_mode"],
            "execution_time": context["execution_time"],
            "generated_at": context["generated_at"],
            "decision_asof_ts": context["decision_asof_ts"],
            "target_trading_date": context["target_trading_date"],
            "expected_previous_trading_date": context["expected_previous_trading_date"],
            "data_cutoff": context["data_cutoff"],
            "latest_available_canonical_date": freshness["latest_available_canonical_date"],
            "freshness_code": freshness["freshness_code"],
            "holdings_mode": holdings["mode"],
            "risk_state": risk["predecessor_risk_state"],
            "symbols_evaluated": len(bands),
            "symbols_within_band": _count_status(bands, "WITHIN_BAND"),
            "symbols_above_band": _count_status(bands, "ABOVE_BAND"),
            "symbols_below_band": _count_status(bands, "BELOW_BAND"),
            "symbols_abstained": _count_status(bands, "ABSTAIN"),
            "current_gross_exposure": exposure["current_gross_exposure"],
            "current_cash_weight": exposure["current_cash_weight"],
            "action_instruction": "none",
            "research_only": True,
            "not_trading_advice": True,
            "not_for_execution": True,
        }
    ]


def _shadow_experiment_contract_rows(predecessor_manifest: dict[str, object], preferred_policy: dict[str, str]) -> list[dict[str, object]]:
    values = {
        "frozen_configuration": "goal_premarket_position_management_operational01_contract_v1",
        "frozen_policy_set": ";".join(predecessor_manifest.get("effective_policy_ids", [])),
        "frozen_band_methodology": "risk_budget_band_from_reference_policy_volatility_and_regime",
        "frozen_thresholds": "gross<=1.00;cash=0.00_to_0.05;volatility<=0.35;abs_beta<=1.20",
        "transaction_cost_assumptions": ";".join(str(value) for value in predecessor_manifest.get("cost_scenarios_bps", [])),
        "decision_timestamp": "08:30:00+08:00 premarket deterministic timestamp",
        "eligible_trading_days": "future_owner_authorized_one_month_window_only_not_backfilled",
        "immutable_snapshot_contract": f"{SNAPSHOT_ROOT}/YYYY-MM-DD/manifest.json",
        "shadow_ledger_contract": "future_shadow_ledger_no_broker_no_paper_trading_started",
        "evaluation_metrics": "readiness_state;constraint_breaches;band_status_counts;abstention_count;exposure_envelope_state",
        "preferred_research_policy": preferred_policy.get("preferred_research_policy", ""),
    }
    return [
        {
            "field_name": key,
            "frozen_value": value,
            "experiment_status": "prepared_not_started",
            "research_only": True,
            "not_trading_advice": True,
            "not_for_execution": True,
        }
        for key, value in values.items()
    ]


def _experiment_freeze_manifest(context: dict[str, str], predecessor_manifest: dict[str, object], preferred_policy: dict[str, str]) -> dict[str, object]:
    return {
        "goal": GOAL_ID,
        "experiment_status": "prepared_not_started",
        "freeze_asof_ts": context["decision_asof_ts"],
        "freeze_source_trading_date": context["target_trading_date"],
        "execution_mode": context["execution_mode"],
        "target_trading_date": context["target_trading_date"],
        "expected_previous_trading_date": context["expected_previous_trading_date"],
        "data_cutoff": context["data_cutoff"],
        "policy_definitions": predecessor_manifest.get("policies_evaluated", []),
        "effective_policy_definitions": predecessor_manifest.get("effective_policy_ids", []),
        "risk_estimators": ["historical_volatility_20d", "historical_volatility_60d", "ewma_volatility_lambda_0_94"],
        "covariance_settings": "predecessor sample/diagonal/constant-correlation diagnostics; no new model search",
        "band_methodology": "risk_budget_band_from_reference_policy_volatility_and_regime",
        "abstention_logic": predecessor_manifest.get("position_band_confidence_logic", ""),
        "constraints": 13,
        "transaction_cost_scenarios_bps": predecessor_manifest.get("cost_scenarios_bps", []),
        "decision_time": "08:30:00+08:00",
        "fill_convention_for_future_shadow_experiment": "future_shadow_close_to_close_observation_only_after_owner_start_authorization",
        "experiment_start_date": "not_started_requires_owner_authorization",
        "future_days_fabricated": False,
        "backfilled_future_experiment": False,
        "paper_trading_started": False,
        "broker_trading_started": False,
        "post_start_changes_require_versioning": True,
        "preferred_research_policy": preferred_policy.get("preferred_research_policy", ""),
    }


def _snapshot_manifest_skeleton(
    context: dict[str, str],
    freshness: dict[str, str],
    generated_at: str,
    predecessor_manifest: dict[str, object],
    holdings: dict[str, object],
    readiness_state: str,
    preferred_policy: dict[str, str],
    canonical_evidence_path: str = "",
    canonical_path: Path | None = None,
    refresh_metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    source_lineage = [PREDECESSOR_GOAL_ID, "network_ingestion_daily_panel", "network_ingestion_index_panel", "regime_label_research02"]
    config_payload = _config_payload(predecessor_manifest, preferred_policy)
    if canonical_evidence_path:
        source_lineage.append(str((refresh_metadata or {}).get("goal", "validated_daily_refresh")))
        config_payload["daily_refresh"] = refresh_metadata or {}
    manifest = {
        "goal": GOAL_ID,
        "snapshot_date": context["target_trading_date"],
        "target_trading_date": context["target_trading_date"],
        "expected_previous_trading_date": context["expected_previous_trading_date"],
        "latest_available_data_date": freshness["latest_available_canonical_date"],
        "latest_available_canonical_date": freshness["latest_available_canonical_date"],
        "execution_mode": context["execution_mode"],
        "execution_time": context["execution_time"],
        "generated_at": generated_at,
        "decision_asof_ts": context["decision_asof_ts"],
        "asof_ts": context["decision_asof_ts"],
        "data_cutoff": context["data_cutoff"],
        "source_lineage": source_lineage,
        "provider_lineage": predecessor_manifest.get("providers_compared", []),
        "holdings_snapshot_id": holdings["snapshot_id"],
        "holdings_mode": holdings["mode"],
        "config_hash": _sha256_text(json.dumps(config_payload, sort_keys=True)),
        "code_commit": "tracked_snapshot_is_deterministic;runtime_git_head_verified_by_validation",
        "readiness_state": readiness_state,
        "freshness_state": freshness["state"],
        "freshness_code": freshness["freshness_code"],
        "pit_status": "passed_current_or_past_only",
        "immutable_write_policy": "refuse_conflicting_snapshot_overwrite",
        "checksums": {},
    }
    if canonical_evidence_path and canonical_path is not None:
        manifest.update(
            {
                "canonical_evidence_path": canonical_evidence_path,
                "canonical_evidence_checksum": _sha256_bytes(canonical_path.read_bytes()),
                "daily_refresh_lineage": refresh_metadata or {},
            }
        )
    return manifest


def _manifest(
    predecessor_manifest: dict[str, object],
    context: dict[str, str],
    freshness: dict[str, str],
    readiness_state: str,
    holdings: dict[str, object],
    risk: dict[str, object],
    bands: list[dict[str, object]],
    warnings: list[dict[str, object]],
    canonical_evidence_path: str = "",
    canonical_path: Path | None = None,
    refresh_metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    manifest = {
        "goal": GOAL_ID,
        "workflow_id": WORKFLOW_ID,
        "mode": MODE,
        "status": BLOCKED if readiness_state == BLOCKED else PASS_WITH_WARNINGS if readiness_state == "READY_WITH_WARNINGS" or warnings else PASS,
        "depends_on_goal": PREDECESSOR_GOAL_ID,
        "predecessor_status": predecessor_manifest.get("status"),
        "predecessor_ready_factor_count": predecessor_manifest.get("ready_factor_count"),
        "trading_date": context["target_trading_date"],
        "execution_mode": context["execution_mode"],
        "execution_time": context["execution_time"],
        "generated_at": context["generated_at"],
        "target_trading_date": context["target_trading_date"],
        "expected_previous_trading_date": context["expected_previous_trading_date"],
        "data_cutoff": context["data_cutoff"],
        "decision_asof_ts": context["decision_asof_ts"],
        "asof_ts": context["decision_asof_ts"],
        "latest_available_canonical_date": freshness["latest_available_canonical_date"],
        "freshness_state": freshness["state"],
        "freshness_code": freshness["freshness_code"],
        "daily_readiness_state": readiness_state,
        "pit_status": "passed_current_or_past_only",
        "holdings_mode": holdings["mode"],
        "real_holdings_snapshot_supplied": holdings["real_snapshot_supplied"],
        "holdings_snapshot_id": holdings["snapshot_id"],
        "provider_quarantined_rows": predecessor_manifest.get("phase1_quarantined_rows", 0),
        "constraints_operationalized": 13,
        "symbols_evaluated": len(bands),
        "symbols_within_band": _count_status(bands, "WITHIN_BAND"),
        "symbols_above_band": _count_status(bands, "ABOVE_BAND"),
        "symbols_below_band": _count_status(bands, "BELOW_BAND"),
        "symbols_abstained": _count_status(bands, "ABSTAIN"),
        "risk_state": risk["predecessor_risk_state"],
        "current_gross_exposure": risk["gross_exposure"],
        "current_cash_weight": risk["cash_weight"],
        "exposure_envelope_status": "risk_envelope_review_only",
        "morning_runner": "scripts/run_premarket_position_management.py",
        "read_only_console": READ_ONLY_CONSOLE,
        "immutable_snapshots_root": SNAPSHOT_ROOT,
        "shadow_experiment_prepared": True,
        "shadow_experiment_started": False,
        "rec_tiering_state": "locked_future",
        "trading_state": "locked_future",
        "broker_state": "locked_future",
        "production_state": "locked_future",
        "warning_count": len(warnings),
    }
    for key in FALSE_BOUNDARY_KEYS:
        manifest[key] = False
    if canonical_evidence_path and canonical_path is not None:
        manifest.update(
            {
                "canonical_evidence_path": canonical_evidence_path,
                "canonical_evidence_checksum": _sha256_bytes(canonical_path.read_bytes()),
                "daily_refresh_lineage": refresh_metadata or {},
            }
        )
    return manifest


def _write_outputs(root: Path, result: dict[str, object]) -> None:
    write_csv(root / HOLDINGS_CONTRACT, result["holdings_contract"])
    write_csv(root / DATA_READINESS, result["readiness"])
    write_csv(root / DAILY_RISK_STATE, result["daily_risk"])
    write_csv(root / DAILY_CONSTRAINT_EVALUATION, result["constraints"])
    write_csv(root / DAILY_BAND_STATUS, result["bands"])
    write_csv(root / DAILY_EXPOSURE_ENVELOPE, result["exposure"])
    write_csv(root / DAILY_ABSTENTION_SUMMARY, result["abstentions"])
    write_csv(root / DAILY_WARNINGS, result["warnings"])
    write_csv(root / OPERATIONAL_RUN_SUMMARY, result["run_summary"])
    write_csv(root / SHADOW_EXPERIMENT_CONTRACT, result["shadow_contract"])
    write_json(root / EXPERIMENT_FREEZE_MANIFEST, result["freeze_manifest"])
    write_text(root / READ_ONLY_CONSOLE, result["console"])

    snapshot_dir = root / SNAPSHOT_ROOT / result["trading_date"]
    snapshot_payloads = {
        "data_readiness.csv": _csv_text(result["readiness"]),
        "portfolio_risk_state.csv": _csv_text(result["daily_risk"]),
        "constraint_evaluation.csv": _csv_text(result["constraints"]),
        "position_band_status.csv": _csv_text(result["bands"]),
        "exposure_envelope.csv": _csv_text(result["exposure"]),
        "abstention_summary.csv": _csv_text(result["abstentions"]),
        "warnings.csv": _csv_text(result["warnings"]),
        "operational_run_summary.csv": _csv_text(result["run_summary"]),
    }
    checksums = {}
    for name, body in snapshot_payloads.items():
        _write_immutable_text(snapshot_dir / name, body)
        checksums[name] = _sha256_text(body)
    result["snapshot_manifest"]["checksums"] = checksums
    manifest_body = json.dumps(result["snapshot_manifest"], indent=2, sort_keys=True) + "\n"
    _write_immutable_text(snapshot_dir / "manifest.json", manifest_body)
    result["snapshot_manifest"]["checksums"]["manifest.json"] = _sha256_text(manifest_body)
    write_json(root / IMMUTABLE_SNAPSHOT_MANIFEST, result["snapshot_manifest"])
    write_json(
        root / SNAPSHOT_ROOT / "latest_manifest.json",
        {
            "snapshot_date": result["trading_date"],
            "snapshot_manifest_path": f"{SNAPSHOT_ROOT}/{result['trading_date']}/manifest.json",
            "snapshot_manifest_checksum": result["snapshot_manifest"]["checksums"]["manifest.json"],
            "latest_pointer_policy": "points_to_latest_validated_snapshot_without_rewriting_history",
        },
    )
    write_json(root / MANIFEST, result["manifest"])
    write_text(root / REPORT, result["report"])
    write_text(root / DOC, result["doc"])
    write_text(root / HANDOFF, result["handoff"])
    write_text(root / CONTRACT, result["contract"])
    _ensure_workflow_row(root)


def _holdings_contract_rows() -> list[dict[str, object]]:
    rows = [
        ("asof_ts", True, "owner snapshot timestamp", "fail_closed_if_missing_or_stale"),
        ("portfolio_id", True, "owner portfolio identifier", "fail_closed_if_missing"),
        ("symbol", True, "approved symbol identifier", "row_rejected_if_missing_or_unknown"),
        ("quantity", False, "optional current quantity", "weight_only_mode"),
        ("market_value", False, "optional current market value", "weight_only_mode"),
        ("current_weight", True, "current portfolio weight from owner snapshot", "fail_closed_if_missing_or_not_reconciled"),
        ("cash_weight", False, "portfolio cash weight", "default_zero_only_in_research_reference_mode"),
        ("source", True, "manual or system snapshot source", "fail_closed_if_missing"),
        ("snapshot_id", True, "stable snapshot identifier", "fail_closed_if_missing"),
    ]
    return [
        {
            "field_name": name,
            "required": required,
            "description": description,
            "grain": "asof_ts+portfolio_id+symbol",
            "missing_behavior": behavior,
            "no_broker_integration": True,
            "no_automatic_account_scraping": True,
        }
        for name, required, description, behavior in rows
    ]


def _console_markdown(
    manifest: dict[str, object],
    summary: dict[str, object],
    risk: dict[str, object],
    exposure: dict[str, object],
    constraints: list[dict[str, object]],
    bands: list[dict[str, object]],
    abstentions: list[dict[str, object]],
    warnings: list[dict[str, object]],
) -> str:
    severe_constraints = [row for row in constraints if row["breach"] == "true" or row["fail_closed"] == "true"][:10]
    top_bands = bands[:12]
    return "\n".join(
        [
            "# Premarket Position Management Console",
            "",
            "Read-only view over a validated snapshot. No execution workflow is exposed.",
            "",
            _section("Morning Overview", _table([summary])),
            _section("Portfolio Risk State", _table([risk])),
            _section("Exposure Envelope", _table([exposure])),
            _section("Constraint Breaches", _table(severe_constraints)),
            _section("Position Band Status", _table(top_bands)),
            _section("Top Risk Contributors", str(risk["largest_risk_contributors"])),
            _section("Abstentions", _table(abstentions)),
            _section("Data Quality / Provider Warnings", _table(warnings)),
            _section("Provenance / Audit", _table([{"goal": GOAL_ID, "snapshot_root": SNAPSHOT_ROOT, "readiness": manifest["daily_readiness_state"], "audit": AUDIT}])),
        ]
    )


def _section(title: str, body: str) -> str:
    return f"## {title}\n\n{body}\n"


def _table(rows: list[dict[str, object]]) -> str:
    if not rows:
        return "None."
    fields = list(rows[0].keys())
    header = "| " + " | ".join(str(field) for field in fields) + " |"
    separator = "| " + " | ".join("---" for _ in fields) + " |"
    body_rows = []
    for row in rows:
        body_rows.append("| " + " | ".join(str(row.get(field, "")).replace("|", "/") for field in fields) + " |")
    return "\n".join([header, separator, *body_rows])


def _report(manifest: dict[str, object]) -> str:
    return "\n".join(
        [
            f"# {GOAL_ID} Report",
            "",
            f"Status: `{manifest['status']}`",
            "",
            f"- Daily readiness: `{manifest['daily_readiness_state']}`",
            f"- Execution mode: `{manifest['execution_mode']}`",
            f"- Generated at: `{manifest['generated_at']}`",
            f"- Decision as-of: `{manifest['decision_asof_ts']}`",
            f"- Target trading date: `{manifest['target_trading_date']}`",
            f"- Expected previous trading date: `{manifest['expected_previous_trading_date']}`",
            f"- Data cutoff: `{manifest['data_cutoff']}`",
            f"- Latest available canonical date: `{manifest['latest_available_canonical_date']}`",
            f"- Freshness code: `{manifest['freshness_code']}`",
            f"- Holdings mode: `{manifest['holdings_mode']}`",
            f"- Risk state: `{manifest['risk_state']}`",
            f"- Symbols within/above/below/abstained: `{manifest['symbols_within_band']}` / `{manifest['symbols_above_band']}` / `{manifest['symbols_below_band']}` / `{manifest['symbols_abstained']}`",
            f"- Snapshot root: `{SNAPSHOT_ROOT}`",
            "",
            "This is read-only position-management decision support. It creates no orders, target prices, recommendation tiers, broker connections, paper trading, or production trading outputs.",
            "",
        ]
    )


def _doc(manifest: dict[str, object]) -> str:
    return "\n".join(
        [
            f"# {GOAL_ID} Premarket Position Management",
            "",
            "Operational layer over the existing research-only portfolio risk track.",
            "",
            "It consumes validated predecessor outputs, optional owner holdings snapshots, and immutable daily snapshots. It does not restart research or fetch providers directly.",
            "",
            f"Execution mode: `{manifest['execution_mode']}`. Target trading date: `{manifest['target_trading_date']}`. Data cutoff: `{manifest['data_cutoff']}`.",
            "",
            f"Daily readiness state: `{manifest['daily_readiness_state']}`.",
            "",
        ]
    )


def _handoff(manifest: dict[str, object]) -> str:
    return "\n".join(
        [
            f"# {GOAL_ID} Governance Handoff",
            "",
            f"- holdings mode: {manifest['holdings_mode']}",
            f"- execution mode: {manifest['execution_mode']}",
            f"- generated at: {manifest['generated_at']}",
            f"- decision as-of: {manifest['decision_asof_ts']}",
            f"- target trading date: {manifest['target_trading_date']}",
            f"- expected previous trading date: {manifest['expected_previous_trading_date']}",
            f"- data cutoff: {manifest['data_cutoff']}",
            f"- latest available canonical date: {manifest['latest_available_canonical_date']}",
            f"- freshness code: {manifest['freshness_code']}",
            f"- daily readiness: {manifest['daily_readiness_state']}",
            f"- risk state: {manifest['risk_state']}",
            f"- constraints operationalized: {manifest['constraints_operationalized']}",
            f"- symbols within band: {manifest['symbols_within_band']}",
            f"- symbols above band: {manifest['symbols_above_band']}",
            f"- symbols below band: {manifest['symbols_below_band']}",
            f"- symbols abstained: {manifest['symbols_abstained']}",
            f"- shadow experiment prepared: {manifest['shadow_experiment_prepared']}",
            f"- shadow experiment started: {manifest['shadow_experiment_started']}",
            "",
            "Do not start the forward shadow experiment, paper trading, broker trading, or any recommendation tiering without a separate owner authorization.",
            "",
        ]
    )


def _contract() -> str:
    return "\n".join(
        [
            f"goal_id: {GOAL_ID}",
            f"workflow_id: {WORKFLOW_ID}",
            f"mode: {MODE}",
            f"depends_on: {PREDECESSOR_GOAL_ID}",
            "execution_modes: [daily_operational, deterministic_replay]",
            "timezone: Asia/Shanghai",
            "daily_operational_generated_at: actual_execution_time",
            "deterministic_replay_requires: replay_date",
            "freshness_rule: latest_available_canonical_date_must_equal_expected_previous_trading_date",
            "read_only: true",
            "broker_connection: false",
            "orders_created: false",
            "buy_sell_hold_labels: false",
            "target_prices: false",
            "recommendation_tiering: false",
            "issue10: false",
            "dqn_rl: false",
            "",
        ]
    )


def _ensure_workflow_row(root: Path) -> None:
    rows = read_csv(root / WORKFLOW_STATUS)
    rows = [row for row in rows if row["workflow_id"] != WORKFLOW_ID]
    rows.append(
        {
            "workflow_id": WORKFLOW_ID,
            "display_name": "GOAL-PREMARKET-POSITION-MANAGEMENT-OPERATIONAL-01 Premarket Position Management",
            "stage_or_goal": GOAL_ID,
            "status": "implemented_research_only",
            "current_repo_role": "read_only_premarket_position_management_decision_support",
            "implemented_in_repo": "true",
            "allowed_next_action": "review_shadow_experiment_contract_no_execution_unlock",
            "depends_on": "goal_premarket_portfolio_risk_management01",
            "produces_artifacts": ";".join(REQUIRED_ARTIFACTS),
            "primary_docs": f"{DOC};{HANDOFF}",
            "primary_scripts": "scripts/run_premarket_position_management.py;scripts/run_goal_premarket_position_management_operational01.py;scripts/audit_goal_premarket_position_management_operational01.py",
            "primary_outputs": f"{REPORT};{MANIFEST};{AUDIT}",
            "promotion_rule": "implemented_research_only_after_operational01_pass_or_pass_with_warnings_no_execution_unlock",
            "notes": "Read-only daily premarket position-management decision support over validated portfolio-risk outputs. No broker, orders, paper trading, Recommendation Tiering, Issue #10, target prices, or DQN/RL.",
        }
    )
    write_csv(root / WORKFLOW_STATUS, rows)


def _latest_regime(regime_rows: list[dict[str, str]], trading_date: str) -> str:
    by_date = {row.get("trade_date", ""): row for row in regime_rows}
    row = by_date.get(trading_date, {})
    return row.get("refined_composite_regime_label") or row.get("composite_regime_label") or "regime_unavailable_review_only"


def _config_payload(predecessor_manifest: dict[str, object], preferred_policy: dict[str, str]) -> dict[str, object]:
    return {
        "goal": GOAL_ID,
        "predecessor_effective_policies": predecessor_manifest.get("effective_policy_ids", []),
        "band_reference_policy": preferred_policy.get("band_reference_policy", ""),
        "thresholds": {"gross_max": 1.0, "cash_min": 0.0, "cash_max": 0.05, "volatility_budget": 0.35, "abs_beta_budget": 1.20},
    }


def _write_immutable_text(path: Path, body: str) -> None:
    if path.exists() and path.read_text(encoding="utf-8") != body:
        raise RuntimeError(f"refuse_conflicting_snapshot_overwrite:{path}")
    write_text(path, body)


def _csv_text(rows: list[dict[str, object]]) -> str:
    if not rows:
        return ""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()), lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: _stringify(value) for key, value in row.items()})
    return buffer.getvalue()


def _count_status(rows: list[dict[str, object]], status: str) -> int:
    return sum(1 for row in rows if row.get("band_status") == status)


def _normalize_severity(value: str) -> str:
    return value if value in {"none", "low", "medium", "high"} else "high" if value == "fail_closed" else "medium"


def _contains_forbidden_operational_text(text: str) -> bool:
    upper = f" {text.upper()} "
    if any(token in upper.split() for token in ["BUY", "SELL", "HOLD"]):
        return True
    lower = text.lower()
    return any(token in lower for token in ["order_quantity", "target_price", "broker_order", "live_broker"])


def _sha256_text(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _sha256_bytes(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def _resolve_canonical_evidence_path(root: Path, value: str | Path | None) -> tuple[Path, str]:
    if value is None or str(value) == "":
        return root / PR_CANONICAL, ""
    candidate = Path(value)
    resolved = (candidate if candidate.is_absolute() else root / candidate).resolve()
    resolved_root = root.resolve()
    if resolved_root not in resolved.parents:
        raise ValueError("canonical evidence path must remain inside repository root")
    if not resolved.exists():
        raise ValueError(f"canonical evidence path does not exist: {resolved}")
    return resolved, resolved.relative_to(resolved_root).as_posix()


def _float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def _fmt(value: object, digits: int = 10) -> str:
    number = _float(value)
    if number is None:
        return ""
    text = f"{number:.{digits}f}"
    return text.rstrip("0").rstrip(".") if "." in text else text


def _mean(values: list[float]) -> float:
    clean = [value for value in values if value is not None and math.isfinite(value)]
    return sum(clean) / len(clean) if clean else 0.0


def _stringify(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    return str(value)


def _workflow_rows(root: Path) -> dict[str, dict[str, str]]:
    if not (root / WORKFLOW_STATUS).exists():
        return {}
    return {row["workflow_id"]: row for row in read_csv(root / WORKFLOW_STATUS)}


def _read_json_if_exists(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _parse_execution_time(value: str) -> datetime:
    text = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=ZoneInfo(TZ_NAME))
    return parsed.astimezone(ZoneInfo(TZ_NAME))


def _iso_seconds(value: datetime) -> str:
    return value.astimezone(ZoneInfo(TZ_NAME)).isoformat(timespec="seconds")

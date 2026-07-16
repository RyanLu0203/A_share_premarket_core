from __future__ import annotations

import csv
import hashlib
import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from ashare_premarket.providers.akshare_provider import (
    ProviderResult,
    load_stock_ohlcv_daily,
    load_stock_ohlcv_daily_tencent,
)

POLICY_PATH = "configs/providers/akshare_governed_stock_history_v1.json"
POLICY_ID = "akshare-governed-stock-history-v1"
CONSISTENCY_FIXTURE_PATH = "configs/providers/fixtures/eastmoney_tencent_consistency_v1.csv"
CORPORATE_ACTION_FIXTURE_PATH = "configs/providers/fixtures/tencent_qfq_corporate_action_v2.json"
APPROVED_PRIMARY_FAILURE_CLASSES = {
    "BROWSER_NET_EMPTY_RESPONSE",
    "CONNECTION_RESET",
    "HTTP_429_RATE_LIMITED",
    "HTTP_5XX_PROVIDER_ERROR",
}

Loader = Callable[[str, str, str, str, bool], ProviderResult]


def load_policy(root: Path) -> dict[str, object]:
    payload = json.loads((root / POLICY_PATH).read_text(encoding="utf-8"))
    if payload.get("policy_id") != POLICY_ID:
        raise ValueError("governed_stock_history_policy_id_mismatch")
    if payload.get("allow_per_symbol_source_mixing") is not False or payload.get("allow_silent_fallback") is not False:
        raise ValueError("governed_stock_history_policy_weakens_source_selection")
    if payload.get("adjustment_policy") != "qfq":
        raise ValueError("governed_stock_history_production_adjustment_must_be_qfq")
    if dict(payload.get("non_production_adjustments", {})).get("hfq_runtime_enabled") is not False:
        raise ValueError("governed_stock_history_hfq_must_remain_runtime_disabled")
    return payload


def run_governed_stock_history_batch(
    root: Path,
    required_symbols: set[str],
    expected_trade_date: str,
    network_enabled: bool,
    *,
    primary_loader: Loader = load_stock_ohlcv_daily,
    secondary_loader: Loader = load_stock_ohlcv_daily_tencent,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, object]:
    """Select one upstream for an entire run and fail closed on mixed evidence."""

    policy = load_policy(root)
    consistency = audit_cross_source_fixture(root, policy)
    adjustment = str(policy["adjustment_policy"])
    interval = float(policy["min_seconds_between_symbol_calls"])
    wall_clock = float(policy["max_batch_wall_clock_seconds"])
    started = datetime.now(timezone.utc).isoformat(timespec="milliseconds")

    primary = _run_complete_batch(
        required_symbols,
        expected_trade_date,
        adjustment,
        network_enabled,
        "primary",
        "East Money",
        "stock_zh_a_hist",
        primary_loader,
        interval,
        wall_clock,
        sleep,
    )
    activation = evaluate_secondary_activation(primary, policy)
    secondary: dict[str, object] | None = None
    selected = primary
    state = "PRIMARY_SELECTED" if primary["complete"] else "PRIMARY_BLOCKED_SECONDARY_NOT_APPROVED"
    discarded_primary_rows = 0
    if activation["activated"]:
        discarded_primary_rows = len(primary["rows"])
        secondary = _run_complete_batch(
            required_symbols,
            expected_trade_date,
            adjustment,
            network_enabled,
            "secondary",
            "Tencent",
            "stock_zh_a_hist_tx",
            secondary_loader,
            interval,
            wall_clock,
            sleep,
        )
        for attempt in secondary["attempts"]:
            attempt["request_sequence"] = len(primary["attempts"]) + int(attempt["batch_request_sequence"])
        secondary["source_consistency_result"] = consistency["status"]
        selected = secondary
        state = "SECONDARY_SELECTED" if secondary["complete"] and consistency["status"] == "PASS" else "SECONDARY_BLOCKED"
        if consistency["status"] != "PASS":
            secondary["complete"] = False
            secondary["source_consistency_result"] = "BLOCKED"
    elif not primary["complete"]:
        state = "PRIMARY_BLOCKED_SECONDARY_NOT_APPROVED"

    selected_rows = list(selected["rows"]) if selected["complete"] else []
    selected_source = str(selected["upstream_source"]) if selected["complete"] else ""
    all_attempts = [*primary["attempts"], *(secondary["attempts"] if secondary else [])]
    return {
        "policy_id": POLICY_ID,
        "state": state,
        "started_at": started,
        "finished_at": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "expected_trade_date": expected_trade_date,
        "required_symbols": sorted(required_symbols),
        "required_symbol_count": len(required_symbols),
        "selected_upstream_source": selected_source,
        "selected_upstream_reason": (
            "PRIMARY_COMPLETE_FULL_COVERAGE"
            if state == "PRIMARY_SELECTED"
            else "APPROVED_PRIMARY_ENDPOINT_FAILURE_COMPLETE_SECONDARY_REACQUISITION"
            if state == "SECONDARY_SELECTED"
            else "NO_ELIGIBLE_COMPLETE_SINGLE_UPSTREAM_BATCH"
        ),
        "selected_function": str(selected["function_name"]) if selected_source else "",
        "selected_endpoint_family": str(selected["endpoint_family"]) if selected_source else "",
        "selected_batch_checksum": str(selected["batch_checksum"]) if selected_source else "",
        "selected_rows": selected_rows,
        "selected_attempts": list(selected["attempts"]),
        "all_attempts": all_attempts,
        "primary_batch": primary,
        "secondary_activation": activation,
        "secondary_batch": secondary,
        "source_consistency_contract_version": policy["cross_source_contract_version"],
        "source_consistency_result": consistency,
        "discarded_primary_row_count": discarded_primary_rows,
        "no_per_symbol_mixing": True,
        "full_coverage": bool(selected["complete"]),
        "tls_verification_preserved": True,
        "bounded_attempts": len(all_attempts) <= len(required_symbols) * 2,
    }


def evaluate_secondary_activation(primary: dict[str, object], policy: dict[str, object]) -> dict[str, object]:
    failures = [attempt for attempt in primary["attempts"] if not bool(attempt.get("accepted"))]
    failure_classes = sorted({str(attempt.get("failure_class", "")) for attempt in failures})
    approved = set(str(value) for value in policy["approved_primary_failure_classes"])
    approved_failures = [attempt for attempt in failures if str(attempt.get("failure_class", "")) in approved]
    local_or_unapproved = [attempt for attempt in failures if str(attempt.get("failure_class", "")) not in approved]
    incomplete = float(primary["coverage_ratio"]) < float(policy["required_coverage_ratio"])
    activated = incomplete and bool(approved_failures) and not local_or_unapproved
    if not incomplete:
        reason = "PRIMARY_COMPLETE"
    elif local_or_unapproved:
        reason = "PRIMARY_FAILURE_NOT_APPROVED_FOR_SECONDARY"
    elif not approved_failures:
        reason = "NO_APPROVED_PRIMARY_ENDPOINT_FAILURE"
    else:
        reason = "APPROVED_PRIMARY_ENDPOINT_FAILURE"
    return {
        "activated": activated,
        "reason": reason,
        "primary_coverage_ratio": primary["coverage_ratio"],
        "failure_classes": failure_classes,
        "approved_failure_count": len(approved_failures),
        "unapproved_or_local_failure_count": len(local_or_unapproved),
        "evaluated_after_primary_batch_terminated": True,
    }


def compare_cross_source_rows(
    eastmoney_rows: list[dict[str, object]],
    tencent_rows: list[dict[str, object]],
    tolerances: dict[str, object],
) -> dict[str, object]:
    primary = {(str(row["trade_date"]), str(row["symbol"])): row for row in eastmoney_rows}
    secondary = {(str(row["trade_date"]), str(row["symbol"])): row for row in tencent_rows}
    if len(primary) != len(eastmoney_rows) or len(secondary) != len(tencent_rows):
        return {"status": "BLOCKED", "reason": "DUPLICATE_SOURCE_KEY", "comparisons": []}
    if set(primary) != set(secondary):
        return {"status": "BLOCKED", "reason": "SOURCE_KEY_COVERAGE_MISMATCH", "comparisons": []}
    comparisons: list[dict[str, object]] = []
    failures: list[str] = []
    abs_price = float(tolerances["ohlc_absolute_cny"])
    rel_price = float(tolerances["ohlc_relative"])
    volume_abs = float(tolerances["volume_absolute_provider_units"])
    for key in sorted(primary):
        left, right = primary[key], secondary[key]
        for field in ("open", "high", "low", "close"):
            passed, difference = _within(float(left[field]), float(right[field]), abs_price, rel_price)
            comparisons.append({"trade_date": key[0], "symbol": key[1], "field": field, "absolute_difference": difference, "passed": passed})
            if not passed:
                failures.append(f"{key[0]}:{key[1]}:{field}")
        volume_diff = abs(float(left["volume"]) - float(right["volume"]))
        volume_passed = volume_diff <= volume_abs
        comparisons.append({"trade_date": key[0], "symbol": key[1], "field": "volume", "absolute_difference": volume_diff, "passed": volume_passed})
        if not volume_passed:
            failures.append(f"{key[0]}:{key[1]}:volume")
    return {
        "status": "PASS" if not failures else "BLOCKED",
        "reason": "" if not failures else "CROSS_SOURCE_TOLERANCE_EXCEEDED",
        "failures": failures,
        "comparisons": comparisons,
    }


def audit_cross_source_fixture(root: Path, policy: dict[str, object] | None = None) -> dict[str, object]:
    policy = policy or load_policy(root)
    path = root / CONSISTENCY_FIXTURE_PATH
    corporate_path = root / CORPORATE_ACTION_FIXTURE_PATH
    if not path.exists() or not corporate_path.exists():
        return {"status": "BLOCKED", "reason": "MISSING_VERSIONED_CROSS_SOURCE_FIXTURE"}
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    overlap = [row for row in rows if row.get("fixture_id") == "current_overlap_20260714"]
    try:
        primary = [_fixture_row(row) for row in overlap if row["source"] == "East Money"]
        secondary = [_fixture_row(row) for row in overlap if row["source"] == "Tencent"]
        comparison = compare_cross_source_rows(primary, secondary, dict(policy["cross_source_tolerances"]))
        corporate_fixture = json.loads(corporate_path.read_text(encoding="utf-8"))
        corporate_events = [
            audit_qfq_corporate_action_event(event, corporate_fixture, policy)
            for event in corporate_fixture["events"]
        ]
        exchanges = {str(event["exchange"]) for event in corporate_events if event["status"] == "PASS"}
        required_universe_ok = any(
            event["status"] == "PASS" and bool(event["required_universe"])
            for event in corporate_events
        )
        corporate_ok = (
            bool(corporate_events)
            and all(event["status"] == "PASS" for event in corporate_events)
            and {"SSE", "SZSE"}.issubset(exchanges)
            and required_universe_ok
        )
        amount_semantics_ok = all(
            row["monetary_amount"] == "" and row["semantic_status"] == "akshare_amount_is_volume_true_amount_not_exported"
            for row in overlap
            if row["source"] == "Tencent"
        )
        research_rows = [row for row in rows if row.get("fixture_id") == "corporate_action_20260708"]
        hfq_primary = [_fixture_row(row) for row in research_rows if row["source"] == "East Money" and row["adjustment"] == "hfq"]
        hfq_secondary = [_fixture_row(row) for row in research_rows if row["source"] == "Tencent" and row["adjustment"] == "hfq"]
        hfq_research = compare_cross_source_rows(hfq_primary, hfq_secondary, dict(policy["cross_source_tolerances"]))
    except (KeyError, TypeError, ValueError) as exc:
        return {"status": "BLOCKED", "reason": "INVALID_VERSIONED_CROSS_SOURCE_FIXTURE", "detail": str(exc)}
    status = "PASS" if comparison["status"] == "PASS" and corporate_ok and amount_semantics_ok else "BLOCKED"
    return {
        "status": status,
        "reason": "" if status == "PASS" else "SOURCE_SEMANTIC_OR_QFQ_ADJUSTMENT_CONTRACT_FAILED",
        "fixture_path": CONSISTENCY_FIXTURE_PATH,
        "fixture_checksum": hashlib.sha256(path.read_bytes()).hexdigest(),
        "corporate_action_fixture_path": CORPORATE_ACTION_FIXTURE_PATH,
        "corporate_action_fixture_checksum": hashlib.sha256(corporate_path.read_bytes()).hexdigest(),
        "overlap_key_count": len(primary),
        "ohlcv_volume_result": comparison["status"],
        "production_adjustment_policy": "qfq_only",
        "adjustment_result": "PASS" if corporate_ok else "BLOCKED",
        "qfq_corporate_action_events": corporate_events,
        "qfq_exchange_coverage": sorted(exchanges),
        "qfq_required_universe_event_result": "PASS" if required_universe_ok else "BLOCKED",
        "primary_unavailable_classification": "PRIMARY_CORPORATE_ACTION_EVIDENCE_UNAVAILABLE",
        "hfq_runtime_enabled": False,
        "hfq_research_audit": {
            **hfq_research,
            "production_gate_effect": "NON_BLOCKING_RESEARCH_ONLY",
        },
        "amount_semantics_result": "PASS" if amount_semantics_ok else "BLOCKED",
    }


def audit_qfq_corporate_action_event(
    event: dict[str, object],
    fixture: dict[str, object],
    policy: dict[str, object],
) -> dict[str, object]:
    """Verify a qfq event from authoritative terms and Tencent raw/qfq rows.

    Direct East Money qfq overlap is preferred.  The governed triangulation is
    permitted only when the primary corporate-action row is explicitly
    classified unavailable; it never treats missing primary rows as proof that
    Tencent is invalid and never evaluates hfq for production selection.
    """

    event_id = str(event["event_id"])
    symbol = str(event["symbol"])
    exchange = str(event["exchange"])
    record_date = str(event["record_date"])
    ex_date = str(event["ex_date"])
    post_date = str(event["post_date"])
    authoritative = dict(event["authoritative_evidence"])
    terms = dict(event["terms"])
    calendar = dict(fixture["approved_calendar_evidence"])
    open_dates = list(map(str, calendar["open_dates"]))
    failures: list[str] = []

    if exchange not in {"SSE", "SZSE"} or not str(authoritative.get("url", "")).startswith("https://"):
        failures.append("INVALID_AUTHORITATIVE_COMPANY_OR_EXCHANGE_EVIDENCE")
    if authoritative.get("symbol") != symbol or authoritative.get("record_date") != record_date or authoritative.get("ex_date") != ex_date:
        failures.append("AUTHORITATIVE_EVENT_IDENTITY_MISMATCH")
    if record_date not in open_dates or ex_date not in open_dates or post_date not in open_dates:
        failures.append("APPROVED_CALENDAR_ALIGNMENT_FAILED")
    event_open_dates = [date for date in open_dates if record_date <= date <= post_date]
    if event_open_dates != [record_date, ex_date, post_date]:
        failures.append("EVENT_TRADING_DATE_SEQUENCE_INVALID")

    raw_rows = _event_rows(event, "tencent_unadjusted_rows", symbol)
    qfq_rows = _event_rows(event, "tencent_qfq_rows", symbol)
    expected_dates = {record_date, ex_date, post_date}
    if set(raw_rows) != expected_dates or set(qfq_rows) != expected_dates:
        failures.append("TENCENT_EVENT_DATE_COVERAGE_INCOMPLETE")

    formula_comparisons: list[dict[str, object]] = []
    continuity: dict[str, object] = {"status": "BLOCKED", "reason": "MISSING_EVENT_ROWS"}
    price_tolerance = float(dict(fixture["tolerances"])["formula_price_absolute_cny"])
    return_tolerance = float(dict(fixture["tolerances"])["continuity_return_absolute"])
    if set(raw_rows) == expected_dates and set(qfq_rows) == expected_dates:
        cash = float(terms["effective_cash_per_share"])
        share_ratio = float(terms["effective_share_ratio_per_share"])
        for field in ("open", "high", "low", "close"):
            raw_value = float(raw_rows[record_date][field])
            expected_raw = (raw_value - cash) / (1.0 + share_ratio)
            observed = float(qfq_rows[record_date][field])
            difference = abs(observed - expected_raw)
            passed = difference <= price_tolerance + 1e-12
            formula_comparisons.append(
                {
                    "field": field,
                    "unadjusted": raw_value,
                    "cash_per_share": cash,
                    "share_ratio_per_share": share_ratio,
                    "formula": "(unadjusted-cash_per_share)/(1+share_ratio_per_share)",
                    "expected_qfq_unrounded": round(expected_raw, 10),
                    "observed_qfq": observed,
                    "absolute_difference": round(difference, 10),
                    "tolerance": price_tolerance,
                    "passed": passed,
                }
            )
            if not passed:
                failures.append(f"QFQ_FORMULA_TOLERANCE_EXCEEDED:{field}")
        for date in (ex_date, post_date):
            for field in ("open", "high", "low", "close", "volume"):
                if float(raw_rows[date][field]) != float(qfq_rows[date][field]):
                    failures.append(f"QFQ_POST_EVENT_CONTINUITY_FIELD_MISMATCH:{date}:{field}")
        for date in expected_dates:
            if float(raw_rows[date]["volume"]) != float(qfq_rows[date]["volume"]):
                failures.append(f"QFQ_VOLUME_NOT_INVARIANT:{date}")
        theoretical_reference = (float(raw_rows[record_date]["close"]) - cash) / (1.0 + share_ratio)
        economic_return = float(raw_rows[ex_date]["close"]) / theoretical_reference - 1.0
        qfq_return = float(qfq_rows[ex_date]["close"]) / float(qfq_rows[record_date]["close"]) - 1.0
        return_difference = abs(economic_return - qfq_return)
        continuity_passed = return_difference <= return_tolerance + 1e-12
        continuity = {
            "status": "PASS" if continuity_passed else "BLOCKED",
            "record_unadjusted_close": float(raw_rows[record_date]["close"]),
            "theoretical_ex_reference_unrounded": round(theoretical_reference, 10),
            "observed_record_qfq_close": float(qfq_rows[record_date]["close"]),
            "ex_unadjusted_close": float(raw_rows[ex_date]["close"]),
            "ex_qfq_close": float(qfq_rows[ex_date]["close"]),
            "economic_return": round(economic_return, 10),
            "qfq_return": round(qfq_return, 10),
            "absolute_difference": round(return_difference, 10),
            "tolerance": return_tolerance,
        }
        if not continuity_passed:
            failures.append("QFQ_CONTINUITY_TOLERANCE_EXCEEDED")

    primary_rows = _event_rows(event, "primary_qfq_rows", symbol)
    primary_status = str(event["primary_corporate_action_evidence_status"])
    if primary_rows:
        direct = compare_cross_source_rows(
            list(primary_rows.values()),
            [qfq_rows[key] for key in sorted(qfq_rows)],
            dict(policy["cross_source_tolerances"]),
        )
        evidence_method = "DIRECT_QFQ_OVERLAP"
        if direct["status"] != "PASS":
            failures.append("DIRECT_PRIMARY_QFQ_OVERLAP_FAILED")
    elif primary_status == "PRIMARY_CORPORATE_ACTION_EVIDENCE_UNAVAILABLE":
        direct = {
            "status": "UNAVAILABLE",
            "reason": "PRIMARY_CORPORATE_ACTION_EVIDENCE_UNAVAILABLE",
            "classification": primary_status,
        }
        evidence_method = "GOVERNED_AUTHORITATIVE_TERMS_TRIANGULATION"
    else:
        direct = {"status": "BLOCKED", "reason": "PRIMARY_EVIDENCE_MISSING_WITHOUT_APPROVED_CLASSIFICATION"}
        evidence_method = "NONE"
        failures.append("PRIMARY_EVIDENCE_MISSING_WITHOUT_APPROVED_CLASSIFICATION")

    return {
        "event_id": event_id,
        "symbol": symbol,
        "exchange": exchange,
        "required_universe": bool(event["required_universe"]),
        "status": "PASS" if not failures else "BLOCKED",
        "failure_reasons": sorted(set(failures)),
        "evidence_method": evidence_method,
        "primary_corporate_action_evidence_status": primary_status,
        "direct_qfq_overlap": direct,
        "authoritative_evidence": authoritative,
        "calendar_alignment_result": "PASS" if not any("CALENDAR" in item or "TRADING_DATE" in item for item in failures) else "BLOCKED",
        "unadjusted_structural_result": "PASS" if set(raw_rows) == expected_dates else "BLOCKED",
        "qfq_formula_result": "PASS" if formula_comparisons and all(item["passed"] for item in formula_comparisons) else "BLOCKED",
        "formula_comparisons": formula_comparisons,
        "qfq_continuity": continuity,
    }


def validate_operational_field_contract(
    rows: list[dict[str, object]],
    *,
    require_amount: bool = False,
) -> dict[str, object]:
    """Keep Tencent amount null distinct from observed zero and fail closed on demand."""

    required = ("trade_date", "symbol", "open", "high", "low", "close", "volume")
    failures: list[str] = []
    null_amount = 0
    zero_amount = 0
    for row in rows:
        key = f"{row.get('trade_date', '')}:{row.get('symbol', '')}"
        if any(row.get(field) in {None, ""} for field in required):
            failures.append(f"MISSING_REQUIRED_OPERATIONAL_FIELD:{key}")
        amount = row.get("amount")
        if amount is None:
            null_amount += 1
            if "TENCENT_AMOUNT_UNAVAILABLE" not in str(row.get("quality_flags", "")):
                failures.append(f"NULL_AMOUNT_WITHOUT_QUALITY_FLAG:{key}")
            if require_amount:
                failures.append(f"MISSING_REQUIRED_AMOUNT:{key}")
        elif float(amount) == 0.0:
            zero_amount += 1
    return {
        "status": "PASS" if not failures else "BLOCKED",
        "reason": "" if not failures else "OPERATIONAL_FIELD_CONTRACT_FAILED",
        "failure_reasons": sorted(set(failures)),
        "row_count": len(rows),
        "amount_null_count": null_amount,
        "amount_observed_zero_count": zero_amount,
        "amount_null_is_distinct_from_zero": True,
        "amount_required": require_amount,
    }


def _run_complete_batch(
    required_symbols: set[str],
    expected: str,
    adjustment: str,
    network_enabled: bool,
    batch_role: str,
    upstream_source: str,
    function_name: str,
    loader: Loader,
    interval: float,
    max_wall_clock: float,
    sleep: Callable[[float], None],
) -> dict[str, object]:
    started_monotonic = time.monotonic()
    attempts: list[dict[str, object]] = []
    accepted_rows: list[dict[str, object]] = []
    for sequence, symbol in enumerate(sorted(required_symbols), start=1):
        if sequence > 1 and interval:
            sleep(interval)
        if time.monotonic() - started_monotonic > max_wall_clock:
            attempt = _synthetic_attempt(symbol, sequence, function_name, upstream_source, expected, "BATCH_WALL_CLOCK_EXCEEDED")
            attempts.append(attempt)
            continue
        try:
            result = loader(symbol, expected, expected, adjustment, network_enabled)
        except Exception as exc:
            failure = "SYMBOL_NORMALIZATION_FAILED" if isinstance(exc, ValueError) and "canonical_symbol" in str(exc) else "LOCAL_ADAPTER_EXCEPTION"
            attempt = _synthetic_attempt(symbol, sequence, function_name, upstream_source, expected, failure)
            attempt["exception_type"] = type(exc).__name__
            attempt["terminal_exception_message"] = str(exc)
            attempts.append(attempt)
            continue
        matching = [row for row in result.rows if str(row.get("trade_date")) == expected and str(row.get("symbol")) == symbol]
        accepted = str(result.attempt.get("status", "")).upper() == "PASS" and len(matching) == 1
        rejection = "" if accepted else str(result.attempt.get("failure_class", "")) or "MISSING_EXACT_T_MINUS_ONE_ROW"
        if not accepted and str(result.attempt.get("status", "")).upper() == "PASS":
            rejection = "MISSING_EXACT_T_MINUS_ONE_ROW"
            result.attempt["failure_class"] = rejection
            result.attempt["status"] = "FAIL"
        enriched = {
            **result.attempt,
            "provider_id": "akshare",
            "function_name": function_name,
            "request_sequence": sequence,
            "batch_request_sequence": sequence,
            "retry_count": 0,
            "accepted": accepted,
            "rejection_reason": rejection,
            "upstream_source": upstream_source,
            "endpoint_family": "web.ifzq.gtimg.cn;proxy.finance.qq.com" if function_name.endswith("_tx") else "push2his.eastmoney.com",
            "latest_returned_trade_date": max((str(row.get("trade_date", "")) for row in result.rows), default=""),
        }
        attempts.append(enriched)
        if accepted:
            accepted_rows.append({**matching[0], "upstream_source": upstream_source, "upstream_function": function_name})
    accepted_symbols = {str(row["symbol"]) for row in accepted_rows}
    schema_ok = accepted_symbols == required_symbols and len(accepted_rows) == len(required_symbols)
    pit_ok = all(str(row.get("trade_date")) == expected for row in accepted_rows) and schema_ok
    provenance_fields = ("provider_id", "function_name", "upstream_source", "endpoint_family", "attempt_ts", "akshare_version", "request_parameters")
    provenance_ok = all(all(str(attempt.get(field, "")).strip() for field in provenance_fields) for attempt in attempts)
    rows = sorted(accepted_rows, key=lambda row: (str(row["trade_date"]), str(row["symbol"])))
    field_contract = (
        validate_operational_field_contract(rows)
        if batch_role == "secondary" and schema_ok
        else {
            "status": "PASS_PRIMARY_CANONICAL_SCHEMA" if batch_role == "primary" else "BLOCKED_INCOMPLETE_BATCH",
            "amount_required": False,
        }
    )
    complete = schema_ok and pit_ok and provenance_ok and str(field_contract["status"]).startswith("PASS")
    return {
        "batch_role": batch_role,
        "upstream_source": upstream_source,
        "function_name": function_name,
        "endpoint_family": "web.ifzq.gtimg.cn;proxy.finance.qq.com" if function_name.endswith("_tx") else "push2his.eastmoney.com",
        "adjustment_policy": adjustment,
        "required_symbol_count": len(required_symbols),
        "accepted_symbol_count": len(accepted_symbols),
        "rejected_symbol_count": len(required_symbols - accepted_symbols),
        "coverage_ratio": len(accepted_symbols) / len(required_symbols) if required_symbols else 0.0,
        "complete": complete,
        "schema_result": "PASS" if schema_ok else "BLOCKED",
        "pit_result": "PASS" if pit_ok else "BLOCKED",
        "provenance_result": "PASS" if provenance_ok else "BLOCKED",
        "operational_field_contract": field_contract,
        "source_consistency_result": "PASS_PRIMARY_CANONICAL_SOURCE" if batch_role == "primary" else "PENDING_VERSIONED_FIXTURE_AUDIT",
        "source_dates": sorted({str(row["trade_date"]) for row in rows}),
        "rows": rows,
        "attempts": attempts,
        "batch_checksum": _rows_checksum(rows),
        "elapsed_seconds": round(time.monotonic() - started_monotonic, 6),
        "attempt_count": len(attempts),
        "retry_count": 0,
    }


def _synthetic_attempt(symbol: str, sequence: int, function: str, upstream: str, expected: str, failure: str) -> dict[str, object]:
    return {
        "provider_id": "akshare",
        "function_name": function,
        "symbol": symbol,
        "market_exchange": symbol.partition(".")[2],
        "date_start": expected,
        "date_end": expected,
        "attempt_ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "status": "FAIL",
        "failure_class": failure,
        "request_sequence": sequence,
        "batch_request_sequence": sequence,
        "retry_count": 0,
        "accepted": False,
        "rejection_reason": failure,
        "upstream_source": upstream,
        "rows_returned": 0,
        "schema_valid": False,
    }


def _rows_checksum(rows: list[dict[str, object]]) -> str:
    if not rows:
        return hashlib.sha256(b"").hexdigest()
    fields = sorted({key for row in rows for key in row})
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows([{key: row.get(key, "") for key in fields} for row in rows])
    return hashlib.sha256(output.getvalue().encode("utf-8")).hexdigest()


def _within(left: float, right: float, absolute: float, relative: float) -> tuple[bool, float]:
    difference = abs(left - right)
    threshold = max(absolute, relative * max(abs(left), abs(right)))
    return difference <= threshold + 1e-12, difference


def _fixture_row(row: dict[str, str]) -> dict[str, object]:
    return {
        "trade_date": row["evidence_date"],
        "symbol": row["symbol"],
        **{field: float(row[field]) for field in ("open", "high", "low", "close", "volume")},
    }


def _event_rows(event: dict[str, object], field: str, symbol: str) -> dict[str, dict[str, object]]:
    rows = list(event.get(field, []))
    normalized: dict[str, dict[str, object]] = {}
    for raw in rows:
        row = dict(raw)
        date = str(row["trade_date"])
        if date in normalized:
            raise ValueError(f"duplicate_corporate_action_fixture_date:{field}:{date}")
        normalized[date] = {
            "trade_date": date,
            "symbol": symbol,
            **{name: float(row[name]) for name in ("open", "high", "low", "close", "volume")},
        }
    return normalized

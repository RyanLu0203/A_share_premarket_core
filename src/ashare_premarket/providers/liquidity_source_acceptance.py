"""Offline provider-schema and free-float-source acceptance gate."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping

GOAL_ID = "GOAL-LIQUIDITY-PROVIDER-SOURCE-ACCEPTANCE-01"

SCHEMA_MAPPING_INPUT = "outputs/providers/goal_data_provider02a_provider_schema_mapping.csv"
FOUNDATION_MANIFEST_INPUT = (
    "outputs/audits/goal_liquidity_evidence_acquisition_foundation01_manifest.json"
)

PREFIX = "outputs/providers/goal_liquidity_provider_source_acceptance01_"
SCHEMA_EVALUATION = PREFIX + "provider_schema_evaluation.csv"
FREE_FLOAT_DECISION = PREFIX + "free_float_source_decision.csv"
TEMPORAL_UNIT_CONTRACT = PREFIX + "temporal_unit_contract.csv"
READINESS_DECISION = PREFIX + "readiness_decision.csv"
REPORT = "outputs/audits/goal_liquidity_provider_source_acceptance01_report.md"
MANIFEST = "outputs/audits/goal_liquidity_provider_source_acceptance01_manifest.json"
AUDIT = "outputs/audits/goal_liquidity_provider_source_acceptance01_audit.md"

TUSHARE_DAILY_BASIC_DOC = "https://tushare.pro/document/2?doc_id=32"
BAOSTOCK_PACKAGE_DOC = "https://pypi.org/project/baostock/"


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


def provider_schema_rows() -> list[dict[str, object]]:
    """Return documentation-backed candidates without claiming live verification."""

    return [
        {
            "provider": "tushare_pro",
            "endpoint": "daily_basic",
            "role": "primary_historical_free_float_and_turnover_candidate",
            "official_reference": TUSHARE_DAILY_BASIC_DOC,
            "documented_fields": (
                "ts_code;trade_date;turnover_rate;turnover_rate_f;"
                "float_share;free_share"
            ),
            "schema_evidence_state": "official_documentation_accepted",
            "live_schema_verified": "false",
            "row_available_at_supplied": "false",
            "pit_acceptance_state": "blocked_pending_availability_contract",
            "selection_state": "selected_documentation_candidate",
            "blocking_reasons": (
                "token_and_entitlement_not_verified;live_schema_not_verified;"
                "row_available_at_not_supplied"
            ),
        },
        {
            "provider": "baostock",
            "endpoint": "query_history_k_data_plus",
            "role": "primary_volume_turnover_trade_status_crosscheck_candidate",
            "official_reference": BAOSTOCK_PACKAGE_DOC,
            "documented_fields": "date;code;volume;adjustflag;turn;tradestatus",
            "schema_evidence_state": "official_package_documentation_accepted",
            "live_schema_verified": "false",
            "row_available_at_supplied": "false",
            "pit_acceptance_state": "blocked_pending_availability_contract",
            "selection_state": "selected_documentation_candidate",
            "blocking_reasons": (
                "live_schema_not_verified;row_available_at_not_supplied;"
                "free_float_not_available"
            ),
        },
        {
            "provider": "tencent_akshare",
            "endpoint": "stock_zh_a_hist_tx",
            "role": "existing_volume_semantics_crosscheck",
            "official_reference": "committed_tencent_operational_evidence",
            "documented_fields": "symbol;trade_date;volume;adjustment",
            "schema_evidence_state": "committed_schema_verified",
            "live_schema_verified": "true",
            "row_available_at_supplied": "false",
            "pit_acceptance_state": "existing_t_plus_1_operational_contract_only",
            "selection_state": "retained_crosscheck_not_complete_liquidity_source",
            "blocking_reasons": "turnover_and_free_float_not_available",
        },
    ]


def free_float_source_rows() -> list[dict[str, object]]:
    return [
        {
            "candidate": "tushare_pro.daily_basic",
            "security_scope": "a_share_symbol_trade_date",
            "free_float_field": "free_share",
            "source_unit": "ten_thousand_shares",
            "historical_query_supported_by_documentation": "true",
            "provider_update_window_documented": "trade_day_15_00_to_17_00",
            "row_available_at_supplied": "false",
            "documentation_accepted": "true",
            "live_verified": "false",
            "selected_primary_candidate": "true",
            "acceptance_state": "documentation_accepted_live_and_pit_pending",
        },
        {
            "candidate": "baostock.query_history_k_data_plus",
            "security_scope": "a_share_symbol_trade_date",
            "free_float_field": "",
            "source_unit": "",
            "historical_query_supported_by_documentation": "true",
            "provider_update_window_documented": "not_row_level",
            "row_available_at_supplied": "false",
            "documentation_accepted": "true",
            "live_verified": "false",
            "selected_primary_candidate": "false",
            "acceptance_state": "rejected_as_free_float_source_field_absent",
        },
        {
            "candidate": "owner_supplied_governed_bundle",
            "security_scope": "exact_100_symbol_complete_grid",
            "free_float_field": "free_float_shares",
            "source_unit": "shares",
            "historical_query_supported_by_documentation": "conditional",
            "provider_update_window_documented": "bundle_manifest_required",
            "row_available_at_supplied": "required",
            "documentation_accepted": "true",
            "live_verified": "false",
            "selected_primary_candidate": "false",
            "acceptance_state": "allowed_fallback_no_bundle_present",
        },
    ]


def temporal_unit_rows() -> list[dict[str, object]]:
    return [
        {
            "provider_endpoint": "tushare_pro.daily_basic",
            "source_field": "free_share",
            "canonical_field": "free_float_shares",
            "source_unit": "ten_thousand_shares",
            "normalization": "multiply_by_10000",
            "canonical_unit": "shares",
            "availability_rule": "must_be_explicitly_anchored_before_acceptance",
            "silent_inference_allowed": "false",
        },
        {
            "provider_endpoint": "tushare_pro.daily_basic",
            "source_field": "turnover_rate_f",
            "canonical_field": "turnover_rate",
            "source_unit": "percent",
            "normalization": "divide_by_100",
            "canonical_unit": "fraction",
            "availability_rule": "must_be_explicitly_anchored_before_acceptance",
            "silent_inference_allowed": "false",
        },
        {
            "provider_endpoint": "baostock.query_history_k_data_plus",
            "source_field": "volume",
            "canonical_field": "volume",
            "source_unit": "shares",
            "normalization": "identity",
            "canonical_unit": "shares",
            "availability_rule": "must_be_explicitly_anchored_before_acceptance",
            "silent_inference_allowed": "false",
        },
        {
            "provider_endpoint": "baostock.query_history_k_data_plus",
            "source_field": "turn",
            "canonical_field": "turnover_rate",
            "source_unit": "percent",
            "normalization": "divide_by_100",
            "canonical_unit": "fraction",
            "availability_rule": "must_be_explicitly_anchored_before_acceptance",
            "silent_inference_allowed": "false",
        },
        {
            "provider_endpoint": "baostock.query_history_k_data_plus",
            "source_field": "tradestatus",
            "canonical_field": "trade_status",
            "source_unit": "enum_0_suspended_1_trading",
            "normalization": "map_0_to_suspended_1_to_trading",
            "canonical_unit": "enum",
            "availability_rule": "must_be_explicitly_anchored_before_acceptance",
            "silent_inference_allowed": "false",
        },
        {
            "provider_endpoint": "baostock.query_history_k_data_plus",
            "source_field": "adjustflag",
            "canonical_field": "adjustment",
            "source_unit": "enum_1_hfq_2_qfq_3_none",
            "normalization": "accept_only_2_as_qfq",
            "canonical_unit": "qfq",
            "availability_rule": "must_be_explicitly_anchored_before_acceptance",
            "silent_inference_allowed": "false",
        },
    ]


def readiness_row() -> dict[str, object]:
    return {
        "goal_status": "PASS_WITH_WARNINGS",
        "documentation_candidates_accepted": 2,
        "selected_free_float_candidate": "tushare_pro.daily_basic",
        "selected_liquidity_crosscheck_candidate": (
            "baostock.query_history_k_data_plus"
        ),
        "live_verified_complete_provider_count": 1,
        "required_live_verified_provider_count": 2,
        "provider_availability_contract_accepted": "false",
        "live_pilot_authorized": "false",
        "provider_calls_performed": "false",
        "accepted_rows": 0,
        "acquisition_preflight_status": "BLOCKED",
        "next_action": "request_bounded_schema_smoke_only_after_explicit_authority",
    }


def run_goal(root: Path) -> bool:
    schema_rows = provider_schema_rows()
    source_rows = free_float_source_rows()
    unit_rows = temporal_unit_rows()
    decision = readiness_row()

    _write_csv(root, SCHEMA_EVALUATION, schema_rows[0].keys(), schema_rows)
    _write_csv(root, FREE_FLOAT_DECISION, source_rows[0].keys(), source_rows)
    _write_csv(root, TEMPORAL_UNIT_CONTRACT, unit_rows[0].keys(), unit_rows)
    _write_csv(root, READINESS_DECISION, decision.keys(), [decision])

    (root / REPORT).write_text(
        "\n".join(
            [
                f"# {GOAL_ID}",
                "",
                "Status: `PASS_WITH_WARNINGS` documentation acceptance / "
                "`BLOCKED` acquisition preflight.",
                "",
                "Tushare Pro `daily_basic` is selected as the documented "
                "historical free-float candidate. Baostock "
                "`query_history_k_data_plus` is selected as the documented "
                "volume, turnover, trade-status, and adjustment cross-check.",
                "",
                "Both candidates still lack live schema verification and an "
                "accepted row-level provider availability contract. The "
                "existing Tencent path remains the only live-verified source "
                "and does not provide a complete liquidity bundle.",
                "",
                "No provider call, credential read, raw payload, accepted row, "
                "factor construction, or downstream unlock occurred.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    inputs = [SCHEMA_MAPPING_INPUT, FOUNDATION_MANIFEST_INPUT]
    outputs = [
        SCHEMA_EVALUATION,
        FREE_FLOAT_DECISION,
        TEMPORAL_UNIT_CONTRACT,
        READINESS_DECISION,
    ]
    manifest = {
        "goal_id": GOAL_ID,
        "goal_status": "PASS_WITH_WARNINGS",
        "acquisition_preflight_status": "BLOCKED",
        "documentation_candidates_accepted": 2,
        "selected_free_float_candidate": "tushare_pro.daily_basic",
        "selected_liquidity_crosscheck_candidate": (
            "baostock.query_history_k_data_plus"
        ),
        "live_verified_complete_provider_count": 1,
        "required_live_verified_provider_count": 2,
        "provider_availability_contract_accepted": False,
        "live_pilot_authorized": False,
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
            and manifest["documentation_candidates_accepted"] == 2
            and manifest["selected_free_float_candidate"]
            == "tushare_pro.daily_basic"
            and manifest["live_verified_complete_provider_count"] == 1
            and manifest["required_live_verified_provider_count"] == 2
            and manifest["accepted_rows"] == 0
            and not manifest["provider_availability_contract_accepted"]
            and not manifest["live_pilot_authorized"]
            and not manifest["provider_calls_performed"]
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

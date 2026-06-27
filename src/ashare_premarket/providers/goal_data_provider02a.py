from __future__ import annotations

import importlib
import importlib.util
import inspect
import os
from pathlib import Path
from typing import Any

from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import preserve_later_review_only_capabilities, preserve_later_review_only_workflow_states
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.providers.provider_registry import network_enabled
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-DATA-PROVIDER-02A"
GOAL_NAME = "GOAL-DATA-PROVIDER-02A-MULTI-PROVIDER-CAPABILITY-PROBE-GATE"
MODE = "review_only_multi_provider_capability_probe"
WORKFLOW_ID = "goal_data_provider02a_multi_provider_capability_probe"
GOAL10C_WORKFLOW_ID = "goal10c_backtest_cost_slippage_sensitivity_gate"
GOAL_DATA_PROVIDER02B_WORKFLOW_ID = "goal_data_provider02b_provider_selection_gate"
GOAL_DATA_PANEL02_WORKFLOW_ID = "goal_data_panel02_evaluation_panel_gate"
GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID = "goal_v1_diagnostic_coverage03_multi_provider_diagnostics"
GOAL10B3_WORKFLOW_ID = "goal10b3_recommendation_backtest_revalidation"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
ALLOWED_NEXT = "request_goal_data_provider02b_provider_selection_or_fix_provider02a_warnings"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

PROVIDER_DIR = "outputs/providers"
AUDIT_DIR = "outputs/audits"
CONFIG_DIR = "configs/providers"
DOC_DIR = "docs/providers"

PROBE_PATH = f"{PROVIDER_DIR}/goal_data_provider02a_provider_capability_probe.csv"
SCHEMA_MAPPING_PATH = f"{PROVIDER_DIR}/goal_data_provider02a_provider_schema_mapping.csv"
FAILURE_TAXONOMY_PATH = f"{PROVIDER_DIR}/goal_data_provider02a_provider_failure_taxonomy.csv"
REPORT_PATH = f"{AUDIT_DIR}/goal_data_provider02a_multi_provider_capability_probe_report.md"
MANIFEST_PATH = f"{AUDIT_DIR}/goal_data_provider02a_multi_provider_capability_probe_manifest.json"
AUDIT_PATH = f"{AUDIT_DIR}/goal_data_provider02a_multi_provider_capability_probe_audit.md"
CONTRACT_PATH = f"{CONFIG_DIR}/goal_data_provider02a_provider_ladder_contract.yaml"
DOC_PATH = f"{DOC_DIR}/GOAL_DATA_PROVIDER02A_MULTI_PROVIDER_CAPABILITY_PROBE_GATE.md"

PROBE_START_DATE = "2026-05-11"
PROBE_END_DATE = "2026-06-19"
PROBE_TRADING_DAY_WINDOW = 30

PROVIDERS = [
    "tushare_pro",
    "baostock",
    "akshare",
    "efinance",
    "qstock",
    "yfinance",
    "local_import",
]

PROBE_FIELDS = [
    "provider_name",
    "provider_role",
    "provider_available",
    "network_required",
    "token_required",
    "token_available",
    "probe_status",
    "failure_code",
    "failure_message",
    "tested_symbols",
    "returned_rows",
    "unique_symbols",
    "unique_trade_dates",
    "date_min",
    "date_max",
    "supports_ohlcv",
    "supports_amount",
    "supports_turnover",
    "supports_adjustment",
    "supports_trading_status",
    "supports_st_status",
    "supports_benchmark",
    "supports_valuation",
    "schema_mapping_status",
    "panel_build_readiness",
    "source_priority_recommendation",
]

SCHEMA_MAPPING_FIELDS = [
    "provider_name",
    "source_field",
    "canonical_field",
    "mapping_required",
    "mapping_status",
    "notes",
]

FAILURE_TAXONOMY_FIELDS = [
    "provider_name",
    "failure_code",
    "failure_layer",
    "failure_category",
    "retryable",
    "owner_action",
    "notes",
]

FALSE_BOUNDARY_KEYS = [
    "final_evaluation_panel_created",
    "evaluation_panel_created",
    "recommendation_diagnostics_run",
    "position_band_diagnostics_run",
    "backtests_run",
    "goal10b3_run",
    "goal10c_rerun_by_this_goal",
    "buy_sell_hold_outputs_generated",
    "target_prices_generated",
    "position_sizing_generated",
    "order_quantities_generated",
    "portfolio_weights_generated",
    "portfolio_returns_generated",
    "equity_curves_generated",
    "dashboard_outputs_generated",
    "dashboard_files_generated",
    "html_generated",
    "streamlit_generated",
    "frontend_code_generated",
    "visual_reports_generated",
    "trading_outputs_generated",
    "paper_trading_enabled",
    "live_trading_enabled",
    "broker_integration_enabled",
    "production_db_writes_created",
    "production_model_behavior_created",
    "local_lake_files_created",
    "factor_mining_outputs_created",
    "dqn_rl_outputs_created",
    "raw_provider_payloads_committed",
    "provider_tokens_committed",
    "secrets_logged",
    "approved_universe_expanded",
    "source_backed_panel_materialized",
    "downstream_execution_unlocked_by_this_goal",
]

FORBIDDEN_OUTPUT_DIRS = [
    "outputs/backtests",
    "outputs/equity_curves",
    "outputs/portfolio_returns",
    "outputs/dashboard",
    "outputs/dashboards",
    "outputs/frontend",
    "outputs/streamlit",
    "outputs/visual_reports",
    "outputs/recommendations",
    "outputs/positions",
    "outputs/position_sizing",
    "outputs/position_weights",
    "outputs/orders",
    "outputs/trading",
    "outputs/paper_trading",
    "outputs/live_trading",
    "outputs/broker",
    "outputs/production",
    "outputs/factors",
    "outputs/dqn",
    "outputs/rl",
    "outputs/provider_payloads",
    "outputs/raw_provider_payloads",
    "data/raw",
    "data/bundles",
    "data/lake",
    "data/exports",
]


def run_goal_data_provider02a_multi_provider_capability_probe_gate(root: Path) -> bool:
    result = evaluate_goal_data_provider02a_multi_provider_capability_probe_gate(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal_data_provider02a_multi_provider_capability_probe_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal_data_provider02a_multi_provider_capability_probe_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    probe_rows = _read_csv(root / PROBE_PATH)
    mapping_rows = _read_csv(root / SCHEMA_MAPPING_PATH)
    taxonomy_rows = _read_csv(root / FAILURE_TAXONOMY_PATH)
    workflow = _workflow_rows(root)
    recheck = evaluate_goal_data_provider02a_multi_provider_capability_probe_gate(root)
    failures: list[str] = []

    if not _report_pass_or_warn(report, "GOAL-DATA-PROVIDER-02A Multi-Provider Capability Probe Gate:"):
        failures.append("provider02a_report_not_pass_or_warn")
    if recheck["status"] == BLOCKED:
        failures.extend(f"recheck:{failure}" for failure in recheck["failures"])
    if manifest.get("goal") != GOAL_NAME:
        failures.append("manifest_goal_invalid")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_invalid")
    if manifest.get("status") not in {PASS, PASS_WITH_WARNINGS}:
        failures.append("manifest_status_invalid")
    if manifest.get("provider_count") != len(PROVIDERS):
        failures.append("manifest_provider_count_invalid")
    if manifest.get("probe_schema") != PROBE_FIELDS:
        failures.append("manifest_probe_schema_invalid")
    if manifest.get("providers_probed") != PROVIDERS:
        failures.append("manifest_provider_order_invalid")
    if manifest.get("approved_universe_expanded") is not False:
        failures.append("approved_universe_expanded_not_false")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"manifest_{key}_not_false")
    for key in [
        "review_only_capability_probe_generated",
        "all_required_providers_represented",
        "network_disabled_by_default_supported",
        "tushare_env_only_policy_enforced",
        "qstock_backtest_strategy_modules_not_used",
        "yfinance_auxiliary_not_primary",
        "local_import_fallback_recorded",
        "goal_data_provider02a_workflow_status_after_gate_implemented",
        "goal_data_provider02b_locked_future",
        "goal_data_panel02_locked_future",
        "goal_v1_diagnostic_coverage03_locked_future",
        "goal10b3_locked_future",
        "goal10d_locked_future",
        "dashboard_daily_report_locked_future",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")

    if len(probe_rows) != len(PROVIDERS):
        failures.append("provider_probe_row_count_invalid")
    if probe_rows and list(probe_rows[0]) != PROBE_FIELDS:
        failures.append("provider_probe_schema_invalid")
    provider_names = [row.get("provider_name", "") for row in probe_rows]
    if provider_names != PROVIDERS:
        failures.append("provider_probe_provider_order_invalid")
    if not mapping_rows or list(mapping_rows[0]) != SCHEMA_MAPPING_FIELDS:
        failures.append("schema_mapping_schema_invalid")
    if not taxonomy_rows or list(taxonomy_rows[0]) != FAILURE_TAXONOMY_FIELDS:
        failures.append("failure_taxonomy_schema_invalid")
    by_provider = {row["provider_name"]: row for row in probe_rows}
    if by_provider.get("tushare_pro", {}).get("token_available") == "false":
        if by_provider.get("tushare_pro", {}).get("failure_code") != "tushare_unavailable_missing_token":
            failures.append("tushare_missing_token_failure_code_invalid")
    if by_provider.get("yfinance", {}).get("provider_role") != "auxiliary_only":
        failures.append("yfinance_provider_role_invalid")
    if by_provider.get("yfinance", {}).get("source_priority_recommendation") != "auxiliary_not_primary":
        failures.append("yfinance_priority_invalid")
    if by_provider.get("qstock", {}).get("source_priority_recommendation") == "backtest_or_strategy_module_used":
        failures.append("qstock_forbidden_module_used")
    if by_provider.get("local_import", {}).get("provider_role") != "fallback":
        failures.append("local_import_role_invalid")

    gate = workflow.get(WORKFLOW_ID, {})
    if gate.get("status") != "implemented_review_only":
        failures.append("provider02a_workflow_not_implemented_review_only")
    if gate.get("implemented_in_repo") != "true":
        failures.append("provider02a_workflow_not_marked_implemented")
    if gate.get("depends_on") != GOAL10C_WORKFLOW_ID:
        failures.append("provider02a_depends_on_invalid")
    if gate.get("allowed_next_action") != ALLOWED_NEXT:
        failures.append("provider02a_allowed_next_invalid")
    for workflow_id in [
        GOAL_DATA_PROVIDER02B_WORKFLOW_ID,
        GOAL_DATA_PANEL02_WORKFLOW_ID,
        GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID,
        GOAL10B3_WORKFLOW_ID,
        GOAL10D_WORKFLOW_ID,
        "dashboard_daily_report",
        "signal_backtest",
        "portfolio_backtest",
        "paper_trading_journal",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
    ]:
        downstream = workflow.get(workflow_id, {})
        if downstream.get("status") != "locked_future":
            failures.append(f"{workflow_id}_not_locked_future")
        if downstream.get("implemented_in_repo") != "false":
            failures.append(f"{workflow_id}_marked_implemented")

    for path in _forbidden_outputs_present(root):
        failures.append(f"forbidden_output_path_exists:{path}")

    status = PASS if not failures else BLOCKED
    write_text(
        root / AUDIT_PATH,
        "\n".join(
            [
                "# GOAL-DATA-PROVIDER-02A Multi-Provider Capability Probe Audit",
                "",
                f"Status: `{status}`",
                "",
                f"Provider rows checked: `{len(probe_rows)}`",
                f"Schema mapping rows checked: `{len(mapping_rows)}`",
                f"Failure taxonomy rows checked: `{len(taxonomy_rows)}`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == PASS


def evaluate_goal_data_provider02a_multi_provider_capability_probe_gate(root: Path) -> dict[str, object]:
    approved_symbols = _approved_symbols(root)
    tested_symbols = approved_symbols[:10]
    network_on = network_enabled(False)
    warnings: list[str] = []
    failures: list[str] = []
    if len(tested_symbols) < 5:
        warnings.append("approved_universe_has_fewer_than_5_symbols")
    if not tested_symbols:
        failures.append("approved_universe_empty")

    rows = [
        _probe_tushare(tested_symbols, network_on),
        _probe_baostock(tested_symbols, network_on),
        _probe_akshare(tested_symbols, network_on),
        _probe_efinance(tested_symbols, network_on),
        _probe_qstock(tested_symbols, network_on),
        _probe_yfinance(tested_symbols, network_on),
        _probe_local_import(root, tested_symbols),
    ]
    warnings.extend(_provider_warnings(rows))
    schema_mapping = _schema_mapping_rows(rows)
    failure_taxonomy = _failure_taxonomy_rows(rows)
    workflow = _workflow_rows(root)
    status = BLOCKED if failures else PASS_WITH_WARNINGS if warnings or any(row["probe_status"] != PASS for row in rows) else PASS
    manifest = _manifest(root, status, warnings, failures, rows, schema_mapping, failure_taxonomy, tested_symbols, network_on, workflow)
    return {
        "status": status,
        "warnings": warnings,
        "failures": failures,
        "probe_rows": rows,
        "schema_mapping_rows": schema_mapping,
        "failure_taxonomy_rows": failure_taxonomy,
        "manifest": manifest,
    }


def goal_data_provider02a_valid_capability_probe_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    probe_rows = _read_csv(root / PROBE_PATH)
    return (
        (
            "GOAL-DATA-PROVIDER-02A Multi-Provider Capability Probe Gate: PASS" in report
            or "GOAL-DATA-PROVIDER-02A Multi-Provider Capability Probe Gate: PASS_WITH_WARNINGS" in report
        )
        and "Status: `PASS`" in audit
        and manifest.get("mode") == MODE
        and manifest.get("all_required_providers_represented") is True
        and manifest.get("final_evaluation_panel_created") is False
        and [row.get("provider_name") for row in probe_rows] == PROVIDERS
    )


def goal_data_provider02a_implemented_workflow_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-DATA-PROVIDER-02A Multi-Provider Capability Probe Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_review_only",
        "current_repo_role": "review_only_multi_provider_capability_probe_gate",
        "implemented_in_repo": "true",
        "allowed_next_action": ALLOWED_NEXT,
        "depends_on": GOAL10C_WORKFLOW_ID,
        "produces_artifacts": ";".join([PROBE_PATH, SCHEMA_MAPPING_PATH, FAILURE_TAXONOMY_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, CONTRACT_PATH, DOC_PATH]),
        "primary_docs": f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "scripts/run_goal_data_provider02a_multi_provider_capability_probe_gate.py;scripts/audit_goal_data_provider02a_multi_provider_capability_probe_gate.py",
        "primary_outputs": ";".join([PROBE_PATH, SCHEMA_MAPPING_PATH, FAILURE_TAXONOMY_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH]),
        "promotion_rule": "implemented_review_only_after_goal_data_provider02a_pass_with_warnings",
        "notes": "Review-only multi-provider capability probe for future source-backed panel planning; no panel build, diagnostics, backtest, dashboard, trading, production, broker, local-lake, factor-mining, or DQN/RL output.",
    }


def locked_goal_data_provider02b_patch() -> dict[str, str]:
    return _locked_patch(
        "GOAL-DATA-PROVIDER-02B Provider Selection Gate",
        "GOAL-DATA-PROVIDER-02B",
        "locked_future_provider_selection_gate",
        "remain_locked_until_explicit_goal_data_provider02b_request",
        WORKFLOW_ID,
        "locked_until_explicit_goal_data_provider02b_selection_gate",
        "Future provider selection remains locked; GOAL-DATA-PROVIDER-02A only probes capabilities.",
    )


def locked_goal_data_panel02_patch() -> dict[str, str]:
    return _locked_patch(
        "GOAL-DATA-PANEL-02 Evaluation Panel Gate",
        "GOAL-DATA-PANEL-02",
        "locked_future_evaluation_panel_gate",
        "remain_locked_until_explicit_goal_data_panel02_request",
        GOAL_DATA_PROVIDER02B_WORKFLOW_ID,
        "locked_until_explicit_goal_data_panel02_gate",
        "Future 50-symbol x 120-trading-date evaluation panel remains locked; no panel is built by Provider-02A.",
    )


def locked_goal_v1_diagnostic_coverage03_patch() -> dict[str, str]:
    return _locked_patch(
        "GOAL-V1-DIAGNOSTIC-COVERAGE-03 Multi-Provider Diagnostics",
        "GOAL-V1-DIAGNOSTIC-COVERAGE-03",
        "locked_future_multi_provider_diagnostics",
        "remain_locked_until_explicit_goal_v1_diagnostic_coverage03_request",
        GOAL_DATA_PANEL02_WORKFLOW_ID,
        "locked_until_explicit_goal_v1_diagnostic_coverage03_gate",
        "Future diagnostic coverage over any Provider-02 panel remains locked; Provider-02A creates no risk, recommendation, or position diagnostics.",
    )


def locked_goal10b3_patch() -> dict[str, str]:
    return _locked_patch(
        "GOAL-10B.3 Recommendation Backtest Revalidation",
        "GOAL-10B.3",
        "locked_future_recommendation_revalidation",
        "remain_locked_until_explicit_goal10b3_request",
        GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID,
        "locked_until_explicit_goal10b3_revalidation_gate",
        "Future GOAL-10B.3 remains locked; Provider-02A runs no recommendation diagnostics or backtests.",
    )


def _probe_tushare(symbols: list[str], network_on: bool) -> dict[str, object]:
    token_available = bool(os.environ.get("TUSHARE_TOKEN"))
    allow_tushare = os.environ.get("ASHARE_ALLOW_TUSHARE") == "1"
    package_available = _package_available("tushare")
    row = _base_row("tushare_pro", "primary_candidate", True, True, symbols, provider_available=package_available, token_available=token_available)
    if not token_available:
        return _with_failure(row, "SKIPPED", "tushare_unavailable_missing_token", "TUSHARE_TOKEN is not set; Tushare Pro probe skipped by env-only policy.")
    if not allow_tushare:
        return _with_failure(row, "SKIPPED", "tushare_disabled_by_policy", "ASHARE_ALLOW_TUSHARE=1 is required before Tushare Pro can be probed.")
    if not network_on:
        return _with_failure(row, "SKIPPED", "network_disabled_by_policy", "ASHARE_ALLOW_NETWORK_INGESTION=1 is required before provider network probes.")
    if not package_available:
        return _with_failure(row, "SKIPPED", "provider_package_unavailable", "Optional dependency tushare is not installed.")
    try:
        ts = importlib.import_module("tushare")
        token = os.environ.get("TUSHARE_TOKEN", "")
        if hasattr(ts, "set_token"):
            ts.set_token(token)
        pro = ts.pro_api(token) if token else ts.pro_api()
        counts: list[int] = []
        columns: set[str] = set()
        dates: set[str] = set()
        seen_symbols: set[str] = set()
        calls = [
            ("trade_cal", {"exchange": "", "start_date": _compact_date(PROBE_START_DATE), "end_date": _compact_date(PROBE_END_DATE)}),
            ("stock_basic", {"exchange": "", "list_status": "L", "fields": "ts_code,symbol,name,area,industry,list_date"}),
            ("index_daily", {"ts_code": "000300.SH", "start_date": _compact_date(PROBE_START_DATE), "end_date": _compact_date(PROBE_END_DATE)}),
        ]
        for symbol in symbols[:2]:
            calls.extend(
                [
                    ("daily", {"ts_code": symbol, "start_date": _compact_date(PROBE_START_DATE), "end_date": _compact_date(PROBE_END_DATE)}),
                    ("adj_factor", {"ts_code": symbol, "start_date": _compact_date(PROBE_START_DATE), "end_date": _compact_date(PROBE_END_DATE)}),
                    ("daily_basic", {"ts_code": symbol, "start_date": _compact_date(PROBE_START_DATE), "end_date": _compact_date(PROBE_END_DATE), "fields": "ts_code,trade_date,turnover_rate,pe_ttm,pb"}),
                ]
            )
        permission_or_quota_notes = []
        for name, kwargs in calls:
            try:
                raw = getattr(pro, name)(**kwargs)
            except Exception as exc:  # optional permissions vary by Tushare account
                code = _classify_exception(exc, provider_prefix="tushare")
                if code in {"tushare_permission_or_quota_error", "provider_rate_limited"}:
                    permission_or_quota_notes.append(f"{name}:{_sanitize_message(exc)}")
                    continue
                raise
            count = _row_count(raw)
            counts.append(count)
            columns.update(_columns(raw))
            dates.update(_extract_dates(raw, ["trade_date", "cal_date", "date"]))
            seen_symbols.update(_extract_symbols(raw, ["ts_code", "symbol", "code"]))
        row.update(
            {
                "probe_status": PASS_WITH_WARNINGS if permission_or_quota_notes else PASS,
                "failure_code": "tushare_permission_or_quota_partial" if permission_or_quota_notes else "",
                "failure_message": "; ".join(permission_or_quota_notes)[:240],
                "returned_rows": sum(counts),
                "unique_symbols": len(seen_symbols),
                "unique_trade_dates": len(dates),
                "date_min": min(dates) if dates else "",
                "date_max": max(dates) if dates else "",
                "supports_ohlcv": _has_any(columns, ["open", "high", "low", "close", "vol", "volume"]),
                "supports_amount": _has_any(columns, ["amount"]),
                "supports_turnover": _has_any(columns, ["turnover_rate", "turnover_rate_f"]),
                "supports_adjustment": _has_any(columns, ["adj_factor"]),
                "supports_benchmark": _has_any(columns, ["ts_code"]) and any("000300" in item for item in seen_symbols),
                "supports_valuation": _has_any(columns, ["pe", "pe_ttm", "pb"]),
                "schema_mapping_status": "canonical_mapping_available",
                "panel_build_readiness": _panel_readiness(sum(counts), len(seen_symbols), len(dates)),
                "source_priority_recommendation": "primary_candidate_subject_to_token_permission_quota",
            }
        )
        return row
    except Exception as exc:
        return _with_failure(row, "FAIL", _classify_exception(exc, provider_prefix="tushare"), _sanitize_message(exc))


def _probe_baostock(symbols: list[str], network_on: bool) -> dict[str, object]:
    package_available = _package_available("baostock")
    row = _base_row("baostock", "primary_candidate", True, False, symbols, provider_available=package_available)
    if not package_available:
        return _with_failure(row, "SKIPPED", "provider_package_unavailable", "Optional dependency baostock is not installed.")
    if not network_on:
        return _with_failure(row, "SKIPPED", "network_disabled_by_policy", "ASHARE_ALLOW_NETWORK_INGESTION=1 is required before provider network probes.")
    fields = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,isST"
    try:
        bs = importlib.import_module("baostock")
        login = bs.login()
        if getattr(login, "error_code", "0") != "0":
            return _with_failure(row, "FAIL", "provider_login_failed", _safe_attr(login, "error_msg", "baostock login failed"))
        rows = 0
        dates: set[str] = set()
        seen_symbols: set[str] = set()
        columns = set(fields.split(","))
        try:
            for symbol in symbols[:2]:
                rs = bs.query_history_k_data_plus(
                    _baostock_code(symbol),
                    fields,
                    start_date=PROBE_START_DATE,
                    end_date=PROBE_END_DATE,
                    frequency="d",
                    adjustflag="2",
                )
                if getattr(rs, "error_code", "0") != "0":
                    return _with_failure(row, "FAIL", "provider_query_failed", _safe_attr(rs, "error_msg", "baostock query failed"))
                result_fields = list(getattr(rs, "fields", []) or fields.split(","))
                columns.update(result_fields)
                while rs.next():
                    data = rs.get_row_data()
                    rows += 1
                    item = dict(zip(result_fields, data))
                    if item.get("date"):
                        dates.add(item["date"])
                    if item.get("code"):
                        seen_symbols.add(item["code"])
        finally:
            bs.logout()
        row.update(
            {
                "probe_status": PASS if rows else PASS_WITH_WARNINGS,
                "failure_code": "" if rows else "zero_rows_returned",
                "failure_message": "" if rows else "Baostock query returned zero rows in the bounded smoke window.",
                "returned_rows": rows,
                "unique_symbols": len(seen_symbols),
                "unique_trade_dates": len(dates),
                "date_min": min(dates) if dates else "",
                "date_max": max(dates) if dates else "",
                "supports_ohlcv": {"open", "high", "low", "close", "volume"}.issubset(columns),
                "supports_amount": "amount" in columns,
                "supports_turnover": "turn" in columns,
                "supports_adjustment": "adjustflag" in columns,
                "supports_trading_status": "tradestatus" in columns,
                "supports_st_status": "isST" in columns,
                "supports_valuation": {"peTTM", "pbMRQ"}.issubset(columns),
                "schema_mapping_status": "canonical_mapping_available",
                "panel_build_readiness": _panel_readiness(rows, len(seen_symbols), len(dates)),
                "source_priority_recommendation": "primary_candidate_for_daily_ohlcv_status_valuation",
            }
        )
        return row
    except Exception as exc:
        return _with_failure(row, "FAIL", _classify_exception(exc), _sanitize_message(exc))


def _probe_akshare(symbols: list[str], network_on: bool) -> dict[str, object]:
    package_available = _package_available("akshare")
    row = _base_row("akshare", "primary_candidate", True, False, symbols, provider_available=package_available)
    if not package_available:
        return _with_failure(row, "SKIPPED", "provider_package_unavailable", "Optional dependency akshare is not installed.")
    if not network_on:
        row["supports_ohlcv"] = True
        row["supports_benchmark"] = True
        row["schema_mapping_status"] = "package_available_network_probe_skipped"
        row["source_priority_recommendation"] = "primary_candidate_existing_repo_provider_network_disabled"
        return _with_failure(row, "SKIPPED", "network_disabled_by_policy", "ASHARE_ALLOW_NETWORK_INGESTION=1 is required before provider network probes.")
    try:
        ak = importlib.import_module("akshare")
        rows = 0
        dates: set[str] = set()
        seen_symbols: set[str] = set()
        columns: set[str] = set()
        for symbol in symbols[:2]:
            raw = ak.stock_zh_a_hist(symbol=_plain_symbol(symbol), period="daily", start_date=_compact_date(PROBE_START_DATE), end_date=_compact_date(PROBE_END_DATE), adjust="")
            rows += _row_count(raw)
            columns.update(_columns(raw))
            dates.update(_extract_dates(raw, ["日期", "date", "trade_date"]))
            if _row_count(raw):
                seen_symbols.add(symbol)
        try:
            index_raw = ak.index_zh_a_hist(symbol="000300", period="daily", start_date=_compact_date(PROBE_START_DATE), end_date=_compact_date(PROBE_END_DATE))
            rows += _row_count(index_raw)
            columns.update(_columns(index_raw))
        except Exception:
            index_raw = None
        row.update(
            {
                "probe_status": PASS if rows else PASS_WITH_WARNINGS,
                "failure_code": "" if rows else "zero_rows_returned",
                "failure_message": "" if rows else "AkShare returned zero rows in the bounded smoke window.",
                "returned_rows": rows,
                "unique_symbols": len(seen_symbols),
                "unique_trade_dates": len(dates),
                "date_min": min(dates) if dates else "",
                "date_max": max(dates) if dates else "",
                "supports_ohlcv": _has_any(columns, ["开盘", "收盘", "最高", "最低", "成交量", "open", "close"]),
                "supports_amount": _has_any(columns, ["成交额", "amount"]),
                "supports_turnover": _has_any(columns, ["换手率", "turnover"]),
                "supports_adjustment": True,
                "supports_benchmark": index_raw is not None and _row_count(index_raw) >= 0,
                "schema_mapping_status": "canonical_mapping_available",
                "panel_build_readiness": _panel_readiness(rows, len(seen_symbols), len(dates)),
                "source_priority_recommendation": "primary_candidate_existing_repo_provider",
            }
        )
        return row
    except Exception as exc:
        return _with_failure(row, "FAIL", _classify_exception(exc), _sanitize_message(exc))


def _probe_efinance(symbols: list[str], network_on: bool) -> dict[str, object]:
    package_available = _package_available("efinance")
    row = _base_row("efinance", "primary_candidate", True, False, symbols, provider_available=package_available)
    if not package_available:
        return _with_failure(row, "SKIPPED", "provider_package_unavailable", "Optional dependency efinance is not installed.")
    if not network_on:
        row["schema_mapping_status"] = "chinese_field_mapping_declared_network_probe_skipped"
        row["source_priority_recommendation"] = "primary_candidate_for_future_smoke_after_network_opt_in"
        return _with_failure(row, "SKIPPED", "network_disabled_by_policy", "ASHARE_ALLOW_NETWORK_INGESTION=1 is required before provider network probes.")
    try:
        ef = importlib.import_module("efinance")
        rows = 0
        dates: set[str] = set()
        seen_symbols: set[str] = set()
        columns: set[str] = set()
        stock_module = getattr(ef, "stock")
        for symbol in symbols[:2]:
            raw = stock_module.get_quote_history(_plain_symbol(symbol), beg=_compact_date(PROBE_START_DATE), end=_compact_date(PROBE_END_DATE), klt=101, fqt=1)
            rows += _row_count(raw)
            columns.update(_columns(raw))
            dates.update(_extract_dates(raw, ["日期", "date", "trade_date"]))
            if _row_count(raw):
                seen_symbols.add(symbol)
        row.update(
            {
                "probe_status": PASS if rows else PASS_WITH_WARNINGS,
                "failure_code": "" if rows else "zero_rows_returned",
                "failure_message": "" if rows else "efinance returned zero rows in the bounded smoke window.",
                "returned_rows": rows,
                "unique_symbols": len(seen_symbols),
                "unique_trade_dates": len(dates),
                "date_min": min(dates) if dates else "",
                "date_max": max(dates) if dates else "",
                "supports_ohlcv": _has_any(columns, ["开盘", "收盘", "最高", "最低", "成交量"]),
                "supports_amount": _has_any(columns, ["成交额"]),
                "supports_turnover": _has_any(columns, ["换手率"]),
                "supports_adjustment": True,
                "schema_mapping_status": "canonical_mapping_available",
                "panel_build_readiness": _panel_readiness(rows, len(seen_symbols), len(dates)),
                "source_priority_recommendation": "primary_candidate_after_rate_limit_review",
            }
        )
        return row
    except Exception as exc:
        return _with_failure(row, "FAIL", _classify_exception(exc), _sanitize_message(exc))


def _probe_qstock(symbols: list[str], network_on: bool) -> dict[str, object]:
    package_available = _package_available("qstock")
    row = _base_row("qstock", "data_candidate", True, False, symbols, provider_available=package_available)
    if not package_available:
        return _with_failure(row, "SKIPPED", "provider_package_unavailable", "Optional dependency qstock is not installed.")
    try:
        qs = importlib.import_module("qstock")
        candidates = ["get_data", "get_price", "stock_data", "ths_daily", "stock"]
        available = [name for name in candidates if hasattr(qs, name)]
        data_module_available = any("data" in name.lower() or "price" in name.lower() or "daily" in name.lower() for name in available)
        row.update(
            {
                "supports_ohlcv": data_module_available,
                "schema_mapping_status": "data_module_available_no_backtest_strategy_import",
                "source_priority_recommendation": "data_candidate_only_backtest_strategy_modules_forbidden",
            }
        )
        if not network_on:
            return _with_failure(row, "SKIPPED", "network_disabled_by_policy", "qstock package is available; network data calls skipped by policy.")
        rows = 0
        dates: set[str] = set()
        seen_symbols: set[str] = set()
        columns: set[str] = set()
        for function_name in available[:1]:
            fn = getattr(qs, function_name)
            kwargs = _qstock_kwargs(fn, symbols[:1])
            raw = fn(**kwargs) if kwargs is not None else fn()
            rows += _row_count(raw)
            columns.update(_columns(raw))
            dates.update(_extract_dates(raw, ["date", "日期", "trade_date"]))
            if _row_count(raw):
                seen_symbols.update(symbols[:1])
        row.update(
            {
                "probe_status": PASS if rows else PASS_WITH_WARNINGS,
                "failure_code": "" if rows else "zero_rows_returned",
                "failure_message": "" if rows else "qstock data-module probe returned zero rows.",
                "returned_rows": rows,
                "unique_symbols": len(seen_symbols),
                "unique_trade_dates": len(dates),
                "date_min": min(dates) if dates else "",
                "date_max": max(dates) if dates else "",
                "supports_ohlcv": data_module_available or _has_any(columns, ["open", "close", "开盘", "收盘"]),
                "supports_amount": _has_any(columns, ["amount", "成交额"]),
                "supports_turnover": _has_any(columns, ["turnover", "换手率"]),
                "schema_mapping_status": "data_module_probe_only",
                "panel_build_readiness": _panel_readiness(rows, len(seen_symbols), len(dates)),
            }
        )
        return row
    except Exception as exc:
        return _with_failure(row, "FAIL", _classify_exception(exc), _sanitize_message(exc))


def _probe_yfinance(symbols: list[str], network_on: bool) -> dict[str, object]:
    package_available = _package_available("yfinance")
    row = _base_row("yfinance", "auxiliary_only", True, False, symbols, provider_available=package_available)
    row["source_priority_recommendation"] = "auxiliary_not_primary"
    if not package_available:
        return _with_failure(row, "SKIPPED", "provider_package_unavailable", "Optional dependency yfinance is not installed.")
    if not network_on:
        row["schema_mapping_status"] = "auxiliary_package_available_network_probe_skipped"
        return _with_failure(row, "SKIPPED", "network_disabled_by_policy", "ASHARE_ALLOW_NETWORK_INGESTION=1 is required before provider network probes.")
    try:
        yf = importlib.import_module("yfinance")
        tickers = [_yfinance_symbol(symbol) for symbol in symbols[:2]]
        raw = yf.download(tickers=tickers, start=PROBE_START_DATE, end=PROBE_END_DATE, progress=False, auto_adjust=False, threads=False)
        rows = _row_count(raw)
        row.update(
            {
                "probe_status": PASS if rows else PASS_WITH_WARNINGS,
                "failure_code": "" if rows else "zero_rows_returned",
                "failure_message": "" if rows else "yfinance returned zero rows for A-share ticker/proxy smoke test.",
                "returned_rows": rows,
                "unique_symbols": len(tickers) if rows else 0,
                "unique_trade_dates": rows if rows else 0,
                "supports_ohlcv": rows > 0,
                "supports_amount": False,
                "schema_mapping_status": "auxiliary_ohlcv_mapping_only" if rows else "auxiliary_mapping_unverified",
                "panel_build_readiness": "auxiliary_not_primary",
                "source_priority_recommendation": "auxiliary_not_primary",
            }
        )
        return row
    except Exception as exc:
        return _with_failure(row, "FAIL", _classify_exception(exc), _sanitize_message(exc), source_priority="auxiliary_not_primary")


def _probe_local_import(root: Path, symbols: list[str]) -> dict[str, object]:
    row = _base_row("local_import", "fallback", False, False, symbols, provider_available=True)
    sample_path = root / "outputs/samples/source_backed_ohlcv_daily_sample.csv"
    coverage_path = root / "outputs/stage6c/STAGE6C_source_backed_engineering_panel_coverage_summary.csv"
    rows = read_csv(sample_path) if sample_path.exists() else []
    approved_set = set(symbols)
    matched = [item for item in rows if item.get("symbol") in approved_set]
    dates = {item.get("trade_date", "") for item in matched if item.get("trade_date")}
    seen_symbols = {item.get("symbol", "") for item in matched if item.get("symbol")}
    coverage = read_csv(coverage_path) if coverage_path.exists() else []
    engineering_pilot_ready = False
    if coverage:
        current = coverage[0]
        engineering_pilot_ready = (
            current.get("panel_tier") == "engineering_pilot"
            and current.get("current_symbols") == "50"
            and current.get("current_trading_dates") == "120"
            and current.get("current_rows") == "6000"
        )
    row.update(
        {
            "probe_status": PASS_WITH_WARNINGS,
            "failure_code": "" if matched else "local_import_current_approved_ohlcv_rows_missing",
            "failure_message": "" if matched else "Existing source-backed local OHLCV sample has no rows for the current config-approved symbols; fixture/demo sources are not counted as source-backed evidence.",
            "returned_rows": len(matched),
            "unique_symbols": len(seen_symbols),
            "unique_trade_dates": len(dates),
            "date_min": min(dates) if dates else "",
            "date_max": max(dates) if dates else "",
            "supports_ohlcv": sample_path.exists(),
            "supports_amount": sample_path.exists(),
            "supports_turnover": False,
            "supports_adjustment": False,
            "supports_benchmark": (root / "outputs/samples/source_backed_benchmark_daily_sample.csv").exists(),
            "schema_mapping_status": "committed_source_backed_sample_schema_available" if sample_path.exists() else "local_import_sample_missing",
            "panel_build_readiness": "fallback_engineering_pilot_sample_exists_but_current_approved_symbol_gap" if engineering_pilot_ready else "fallback_not_panel_ready",
            "source_priority_recommendation": "fallback_after_primary_provider_selection",
        }
    )
    return row


def _manifest(
    root: Path,
    status: str,
    warnings: list[str],
    failures: list[str],
    rows: list[dict[str, object]],
    schema_mapping: list[dict[str, object]],
    failure_taxonomy: list[dict[str, object]],
    tested_symbols: list[str],
    network_on: bool,
    workflow: dict[str, dict[str, str]],
) -> dict[str, object]:
    provider_names = [row["provider_name"] for row in rows]
    package_available = {str(row["provider_name"]): row["provider_available"] for row in rows}
    probe_statuses = {str(row["provider_name"]): row["probe_status"] for row in rows}
    payload: dict[str, object] = {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "mode": MODE,
        "status": status,
        "warnings": warnings,
        "failures": failures,
        "provider_count": len(rows),
        "providers_probed": provider_names,
        "provider_package_available": package_available,
        "provider_probe_statuses": probe_statuses,
        "probe_schema": PROBE_FIELDS,
        "tested_symbols": tested_symbols,
        "tested_symbol_count": len(tested_symbols),
        "approved_symbols_available": len(_approved_symbols(root)),
        "approved_universe_minimum_requested": 5,
        "approved_universe_maximum_requested": 10,
        "approved_universe_expanded": False,
        "probe_window_start": PROBE_START_DATE,
        "probe_window_end": PROBE_END_DATE,
        "probe_trading_day_window": PROBE_TRADING_DAY_WINDOW,
        "network_ingestion_enabled": network_on,
        "network_disabled_by_default_supported": True,
        "review_only_capability_probe_generated": status != BLOCKED,
        "all_required_providers_represented": provider_names == PROVIDERS,
        "schema_mapping_row_count": len(schema_mapping),
        "failure_taxonomy_row_count": len(failure_taxonomy),
        "tushare_env_only_policy_enforced": True,
        "tushare_token_available": bool(os.environ.get("TUSHARE_TOKEN")),
        "qstock_backtest_strategy_modules_not_used": True,
        "yfinance_auxiliary_not_primary": True,
        "local_import_fallback_recorded": True,
        "goal_data_provider02a_workflow_status_after_gate": "implemented_review_only",
        "goal_data_provider02a_workflow_status_after_gate_implemented": True,
        "goal_data_provider02b_status_after_goal_data_provider02a": "locked_future",
        "goal_data_provider02b_locked_future": True,
        "goal_data_panel02_status_after_goal_data_provider02a": "locked_future",
        "goal_data_panel02_locked_future": True,
        "goal_v1_diagnostic_coverage03_status_after_goal_data_provider02a": "locked_future",
        "goal_v1_diagnostic_coverage03_locked_future": True,
        "goal10b3_status_after_goal_data_provider02a": "locked_future",
        "goal10b3_locked_future": True,
        "goal10d_status_after_goal_data_provider02a": "locked_future",
        "goal10d_locked_future": True,
        "dashboard_daily_report_status_after_goal_data_provider02a": "locked_future",
        "dashboard_daily_report_locked_future": True,
        "signal_backtest_status_after_goal_data_provider02a": "locked_future",
        "portfolio_backtest_status_after_goal_data_provider02a": "locked_future",
        "workflow_status_before_goal_data_provider02a": workflow.get(WORKFLOW_ID, {}).get("status", "missing"),
    }
    for key in FALSE_BOUNDARY_KEYS:
        payload[key] = False
    return payload


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / PROBE_PATH, result["probe_rows"], PROBE_FIELDS)
    write_csv(root / SCHEMA_MAPPING_PATH, result["schema_mapping_rows"], SCHEMA_MAPPING_FIELDS)
    write_csv(root / FAILURE_TAXONOMY_PATH, result["failure_taxonomy_rows"], FAILURE_TAXONOMY_FIELDS)
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_contract(root, result)
    _write_report(root, result)
    _write_doc(root, result)


def _write_contract(root: Path, result: dict[str, object]) -> None:
    payload = {
        "goal": GOAL_NAME,
        "mode": MODE,
        "review_only": True,
        "network_default": "disabled_unless_ASHARE_ALLOW_NETWORK_INGESTION_1",
        "approved_universe_source": "configs/universe/approved_symbols.csv",
        "probe_window": {"start": PROBE_START_DATE, "end": PROBE_END_DATE, "trading_days": PROBE_TRADING_DAY_WINDOW},
        "providers": [
            {"provider_name": "tushare_pro", "role": "primary_candidate", "requires_token": True, "token_env": "TUSHARE_TOKEN", "allow_env": "ASHARE_ALLOW_TUSHARE"},
            {"provider_name": "baostock", "role": "primary_candidate", "requires_token": False},
            {"provider_name": "akshare", "role": "primary_candidate", "requires_token": False},
            {"provider_name": "efinance", "role": "primary_candidate", "requires_token": False},
            {"provider_name": "qstock", "role": "data_candidate", "forbidden_modules": ["backtest", "strategy"]},
            {"provider_name": "yfinance", "role": "auxiliary_only", "source_priority": "auxiliary_not_primary"},
            {"provider_name": "local_import", "role": "fallback"},
        ],
        "forbidden_outputs": FALSE_BOUNDARY_KEYS,
        "downstream_locks": {
            GOAL_DATA_PROVIDER02B_WORKFLOW_ID: "locked_future",
            GOAL_DATA_PANEL02_WORKFLOW_ID: "locked_future",
            GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID: "locked_future",
            GOAL10B3_WORKFLOW_ID: "locked_future",
            GOAL10D_WORKFLOW_ID: "locked_future",
            "dashboard_daily_report": "locked_future",
        },
    }
    write_json(root / CONTRACT_PATH, payload)


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    rows = result["probe_rows"]
    provider_lines = [
        f"- `{row['provider_name']}`: status `{row['probe_status']}`, failure `{row['failure_code'] or 'none'}`, returned rows `{row['returned_rows']}`, readiness `{row['panel_build_readiness']}`."
        for row in rows
    ]
    write_text(
        root / REPORT_PATH,
        "\n".join(
            [
                "# GOAL-DATA-PROVIDER-02A Multi-Provider Capability Probe Report",
                "",
                f"GOAL-DATA-PROVIDER-02A Multi-Provider Capability Probe Gate: {result['status']}",
                "",
                f"Mode: `{MODE}`",
                f"Network ingestion enabled: `{str(manifest['network_ingestion_enabled']).lower()}`",
                f"Approved symbols tested: `{';'.join(manifest['tested_symbols'])}`",
                f"Probe date window: `{PROBE_START_DATE}` to `{PROBE_END_DATE}` over `{PROBE_TRADING_DAY_WINDOW}` trading-day contract.",
                "",
                "## Provider Results",
                *provider_lines,
                "",
                "## Boundary",
                "- This gate creates provider capability metadata only.",
                "- It does not create a final evaluation panel, recommendation diagnostics, position-band diagnostics, backtests, dashboards, trading, production, broker, local-lake, factor-mining, or DQN/RL outputs.",
                "- Tushare Pro uses only `TUSHARE_TOKEN`, `ASHARE_ALLOW_TUSHARE=1`, and `ASHARE_ALLOW_NETWORK_INGESTION=1`; missing token is recorded as `tushare_unavailable_missing_token`.",
                "- `qstock` is limited to data-module availability; backtest and strategy modules remain forbidden.",
                "- `yfinance` is recorded as `auxiliary_not_primary`.",
                "",
                "## Warnings",
                *[f"- {warning}" for warning in result["warnings"]],
                "",
            ]
        ),
    )


def _write_doc(root: Path, result: dict[str, object]) -> None:
    write_text(
        root / DOC_PATH,
        "\n".join(
            [
                "# GOAL-DATA-PROVIDER-02A Multi-Provider Capability Probe Gate",
                "",
                "GOAL-DATA-PROVIDER-02A is a review-only provider capability probe. It records whether Tushare Pro, Baostock, AkShare, efinance, qstock, yfinance, and local import can plausibly support a future source-backed 50-symbol x 120-trading-date evaluation panel.",
                "",
                "It does not build that panel. It does not create recommendation diagnostics, position-band diagnostics, backtests, equity curves, portfolio returns, dashboards, trading, broker, production, local-lake, factor-mining, or DQN/RL outputs.",
                "",
                "## Provider Rules",
                "",
                "- Tushare Pro requires `TUSHARE_TOKEN`, `ASHARE_ALLOW_TUSHARE=1`, and `ASHARE_ALLOW_NETWORK_INGESTION=1`; missing token records `tushare_unavailable_missing_token`.",
                "- Baostock checks package availability by default and, only with network opt-in, probes login/logout and `query_history_k_data_plus` using the required daily field set.",
                "- AkShare checks package availability and, only with network opt-in, probes A-share daily OHLCV and benchmark/index history.",
                "- efinance checks package availability and maps Chinese quote-history fields into the canonical OHLCV concepts.",
                "- qstock checks data-module availability only; backtest and strategy modules are not used.",
                "- yfinance is auxiliary only and is marked `auxiliary_not_primary`.",
                "- local import is a fallback and cannot substitute fixture/demo rows for source-backed panel readiness.",
                "",
                "## Outputs",
                "",
                f"- `{PROBE_PATH}`",
                f"- `{SCHEMA_MAPPING_PATH}`",
                f"- `{FAILURE_TAXONOMY_PATH}`",
                f"- `{REPORT_PATH}`",
                f"- `{MANIFEST_PATH}`",
                f"- `{AUDIT_PATH}`",
                f"- `{CONTRACT_PATH}`",
                "",
                "## Current Result",
                "",
                f"- Status: `{result['status']}`",
                f"- Providers represented: `{len(result['probe_rows'])}`",
                f"- Network enabled during probe: `{str(result['manifest']['network_ingestion_enabled']).lower()}`",
                f"- Tested symbols: `{';'.join(result['manifest']['tested_symbols'])}`",
                "",
            ]
        ),
    )


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys()) if rows else []
    by_id = {row["workflow_id"]: row for row in rows}
    _upsert_workflow_row(rows, by_id, WORKFLOW_ID, goal_data_provider02a_implemented_workflow_patch(), after=GOAL10C_WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL_DATA_PROVIDER02B_WORKFLOW_ID, locked_goal_data_provider02b_patch(), after=WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL_DATA_PANEL02_WORKFLOW_ID, locked_goal_data_panel02_patch(), after=GOAL_DATA_PROVIDER02B_WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID, locked_goal_v1_diagnostic_coverage03_patch(), after=GOAL_DATA_PANEL02_WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL10B3_WORKFLOW_ID, locked_goal10b3_patch(), after=GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID)
    for workflow_id in [
        GOAL10D_WORKFLOW_ID,
        "dashboard_daily_report",
        "signal_backtest",
        "portfolio_backtest",
        "cost_slippage_sensitivity",
        "paper_trading_journal",
        "failure_attribution",
        "production_hardening",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
    ]:
        if workflow_id in by_id:
            by_id[workflow_id]["status"] = "locked_future"
            by_id[workflow_id]["implemented_in_repo"] = "false"
    if "dashboard_daily_report" in by_id:
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_data_provider02a"
    if "dqn_rl_mainline" in by_id:
        by_id["dqn_rl_mainline"]["status"] = "deleted_from_active_mainline"
        by_id["dqn_rl_mainline"]["implemented_in_repo"] = "false"
    if "v2_factor_research_upgrade" in by_id:
        by_id["v2_factor_research_upgrade"]["status"] = "planned_locked"
        by_id["v2_factor_research_upgrade"]["implemented_in_repo"] = "false"
    preserve_later_review_only_workflow_states(root, by_id)
    if result["status"] != BLOCKED:
        by_id[WORKFLOW_ID].update(goal_data_provider02a_implemented_workflow_patch())
        by_id[GOAL_DATA_PROVIDER02B_WORKFLOW_ID].update(locked_goal_data_provider02b_patch())
        by_id[GOAL_DATA_PANEL02_WORKFLOW_ID].update(locked_goal_data_panel02_patch())
        by_id[GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID].update(locked_goal_v1_diagnostic_coverage03_patch())
        by_id[GOAL10B3_WORKFLOW_ID].update(locked_goal10b3_patch())
        if "dashboard_daily_report" in by_id:
            by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_data_provider02a"
    write_csv(path, rows, fields)


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    if not path.exists():
        return
    payload = read_json(path)
    payload[WORKFLOW_ID] = "implemented_review_only" if result["status"] != BLOCKED else False
    payload[GOAL_DATA_PROVIDER02B_WORKFLOW_ID] = False
    payload[GOAL_DATA_PANEL02_WORKFLOW_ID] = False
    payload[GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID] = False
    payload[GOAL10B3_WORKFLOW_ID] = False
    payload[GOAL10D_WORKFLOW_ID] = False
    for key in [
        "signal_backtest",
        "portfolio_backtest",
        "dashboard",
        "paper_trading",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
        "dqn_rl",
        "factor_mining",
        "local_lake",
    ]:
        payload[key] = False
    preserve_later_review_only_capabilities(root, payload)
    if result["status"] != BLOCKED:
        payload[WORKFLOW_ID] = "implemented_review_only"
        payload[GOAL_DATA_PROVIDER02B_WORKFLOW_ID] = False
        payload[GOAL_DATA_PANEL02_WORKFLOW_ID] = False
        payload[GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID] = False
        payload[GOAL10B3_WORKFLOW_ID] = False
    write_json(path, payload)


def _schema_mapping_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    mappings = {
        "tushare_pro": [("trade_date", "trade_date"), ("ts_code", "symbol"), ("open", "open"), ("high", "high"), ("low", "low"), ("close", "close"), ("vol", "volume"), ("amount", "amount"), ("adj_factor", "adjustment_factor"), ("turnover_rate", "turnover"), ("pe_ttm", "pe_ttm"), ("pb", "pb")],
        "baostock": [("date", "trade_date"), ("code", "symbol"), ("open", "open"), ("high", "high"), ("low", "low"), ("close", "close"), ("volume", "volume"), ("amount", "amount"), ("adjustflag", "adjustment_flag"), ("turn", "turnover"), ("tradestatus", "trading_status"), ("peTTM", "pe_ttm"), ("pbMRQ", "pb"), ("isST", "st_status")],
        "akshare": [("日期", "trade_date"), ("股票代码", "symbol"), ("开盘", "open"), ("最高", "high"), ("最低", "low"), ("收盘", "close"), ("成交量", "volume"), ("成交额", "amount"), ("换手率", "turnover")],
        "efinance": [("日期", "trade_date"), ("股票代码", "symbol"), ("开盘", "open"), ("最高", "high"), ("最低", "low"), ("收盘", "close"), ("成交量", "volume"), ("成交额", "amount"), ("换手率", "turnover")],
        "qstock": [("date", "trade_date"), ("code", "symbol"), ("open", "open"), ("high", "high"), ("low", "low"), ("close", "close"), ("volume", "volume"), ("amount", "amount")],
        "yfinance": [("Date", "trade_date"), ("Open", "open"), ("High", "high"), ("Low", "low"), ("Close", "close"), ("Volume", "volume")],
        "local_import": [("trade_date", "trade_date"), ("symbol", "symbol"), ("open", "open"), ("high", "high"), ("low", "low"), ("close", "close"), ("volume", "volume"), ("amount", "amount")],
    }
    status_by_provider = {str(row["provider_name"]): str(row["schema_mapping_status"]) for row in rows}
    output = []
    for provider, provider_mappings in mappings.items():
        for source_field, canonical_field in provider_mappings:
            output.append(
                {
                    "provider_name": provider,
                    "source_field": source_field,
                    "canonical_field": canonical_field,
                    "mapping_required": True,
                    "mapping_status": status_by_provider.get(provider, "declared"),
                    "notes": "Review-only schema map; no raw provider payload is committed.",
                }
            )
    return output


def _failure_taxonomy_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    for row in rows:
        code = str(row.get("failure_code") or "provider_probe_passed")
        layer, category, retryable, owner_action = _failure_taxonomy(code)
        output.append(
            {
                "provider_name": row["provider_name"],
                "failure_code": code,
                "failure_layer": layer,
                "failure_category": category,
                "retryable": retryable,
                "owner_action": owner_action,
                "notes": row.get("failure_message", "") or "No provider failure recorded.",
            }
        )
    return output


def _base_row(
    provider_name: str,
    provider_role: str,
    network_required: bool,
    token_required: bool,
    symbols: list[str],
    *,
    provider_available: bool,
    token_available: bool = False,
) -> dict[str, object]:
    return {
        "provider_name": provider_name,
        "provider_role": provider_role,
        "provider_available": provider_available,
        "network_required": network_required,
        "token_required": token_required,
        "token_available": token_available,
        "probe_status": "NOT_RUN",
        "failure_code": "",
        "failure_message": "",
        "tested_symbols": ";".join(symbols),
        "returned_rows": 0,
        "unique_symbols": 0,
        "unique_trade_dates": 0,
        "date_min": "",
        "date_max": "",
        "supports_ohlcv": False,
        "supports_amount": False,
        "supports_turnover": False,
        "supports_adjustment": False,
        "supports_trading_status": False,
        "supports_st_status": False,
        "supports_benchmark": False,
        "supports_valuation": False,
        "schema_mapping_status": "not_verified",
        "panel_build_readiness": "not_ready",
        "source_priority_recommendation": "candidate_requires_follow_up",
    }


def _with_failure(
    row: dict[str, object],
    status: str,
    code: str,
    message: str,
    *,
    source_priority: str | None = None,
) -> dict[str, object]:
    row["probe_status"] = status
    row["failure_code"] = code
    row["failure_message"] = _truncate(message)
    if code == "network_disabled_by_policy":
        row["panel_build_readiness"] = "cannot_assess_without_network_opt_in"
    elif code == "provider_package_unavailable":
        row["panel_build_readiness"] = "not_ready_optional_dependency_missing"
    elif code == "tushare_unavailable_missing_token":
        row["panel_build_readiness"] = "not_ready_missing_token"
    elif status == "FAIL":
        row["panel_build_readiness"] = "not_ready_provider_probe_failed"
    if source_priority is not None:
        row["source_priority_recommendation"] = source_priority
    return row


def _provider_warnings(rows: list[dict[str, object]]) -> list[str]:
    warnings = []
    for row in rows:
        if row["probe_status"] != PASS:
            warnings.append(f"{row['provider_name']}:{row['failure_code'] or row['probe_status']}")
    return warnings


def _failure_taxonomy(code: str) -> tuple[str, str, bool, str]:
    if code in {"provider_probe_passed", ""}:
        return "none", "none", False, "none"
    if code in {"network_disabled_by_policy", "tushare_disabled_by_policy"}:
        return "policy", "policy_skip", False, "Enable explicit env gates only if a future goal authorizes network probing."
    if code == "tushare_unavailable_missing_token":
        return "credential", "missing_token", False, "Set TUSHARE_TOKEN outside the repository and opt in explicitly."
    if code == "provider_package_unavailable":
        return "dependency", "optional_dependency_missing", False, "Install optional provider dependency outside committed artifacts."
    if "permission" in code or "quota" in code:
        return "provider_access", "permission_or_quota", False, "Review provider account permissions and quota."
    if "rate" in code:
        return "provider_access", "rate_limited", True, "Retry later or slow future probe cadence."
    if "network" in code or "timeout" in code or "connection" in code:
        return "network_transport", "network_failure", True, "Retry within finance-only network policy."
    if "schema" in code or "column" in code:
        return "provider_contract", "schema_mismatch", False, "Update schema mapping before using provider for panel construction."
    if "zero_rows" in code or "missing" in code:
        return "data_quality", "coverage_gap", False, "Treat as coverage warning; do not fabricate rows."
    return "provider_runtime", "provider_exception", True, "Inspect sanitized provider error and rerun in an opt-in probe."


def _locked_patch(display_name: str, stage_or_goal: str, role: str, allowed_next: str, depends_on: str, promotion_rule: str, notes: str) -> dict[str, str]:
    return {
        "display_name": display_name,
        "stage_or_goal": stage_or_goal,
        "status": "locked_future",
        "current_repo_role": role,
        "implemented_in_repo": "false",
        "allowed_next_action": allowed_next,
        "depends_on": depends_on,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": promotion_rule,
        "notes": notes,
    }


def _upsert_workflow_row(
    rows: list[dict[str, str]],
    by_id: dict[str, dict[str, str]],
    workflow_id: str,
    patch: dict[str, str],
    *,
    after: str,
) -> None:
    if workflow_id in by_id:
        by_id[workflow_id].update(patch)
        return
    insert_at = next((index + 1 for index, item in enumerate(rows) if item["workflow_id"] == after), len(rows))
    row = {"workflow_id": workflow_id, **patch}
    rows.insert(insert_at, row)
    by_id[workflow_id] = row


def _approved_symbols(root: Path) -> list[str]:
    path = root / "configs/universe/approved_symbols.csv"
    if not path.exists():
        return []
    rows = read_csv(path)
    return [row["symbol"] for row in rows if row.get("approval_status") == "approved"]


def _package_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _row_count(raw: Any) -> int:
    if raw is None:
        return 0
    if hasattr(raw, "shape"):
        try:
            return int(raw.shape[0])
        except Exception:
            return 0
    try:
        return len(raw)
    except TypeError:
        return 0


def _columns(raw: Any) -> set[str]:
    if raw is None:
        return set()
    if hasattr(raw, "columns"):
        return {str(column) for column in list(raw.columns)}
    if isinstance(raw, list) and raw and isinstance(raw[0], dict):
        return {str(key) for key in raw[0]}
    if isinstance(raw, dict):
        return {str(key) for key in raw}
    return set()


def _extract_dates(raw: Any, fields: list[str]) -> set[str]:
    return _extract_values(raw, fields)


def _extract_symbols(raw: Any, fields: list[str]) -> set[str]:
    return _extract_values(raw, fields)


def _extract_values(raw: Any, fields: list[str]) -> set[str]:
    values: set[str] = set()
    if raw is None:
        return values
    if hasattr(raw, "to_dict"):
        try:
            records = raw.to_dict("records")
        except Exception:
            records = []
    elif isinstance(raw, list):
        records = raw
    else:
        records = []
    for item in records:
        if not isinstance(item, dict):
            continue
        for field in fields:
            value = item.get(field)
            if value not in {None, ""}:
                values.add(str(value)[:10])
    return values


def _has_any(columns: set[str], names: list[str]) -> bool:
    lowered = {column.lower() for column in columns}
    return any(name.lower() in lowered for name in names)


def _panel_readiness(rows: int, symbols: int, dates: int) -> str:
    if rows >= 6000 and symbols >= 50 and dates >= 120:
        return "panel_ready_candidate"
    if rows > 0 and symbols > 0 and dates >= 20:
        return "candidate_for_future_panel_after_selection"
    if rows > 0:
        return "smoke_rows_returned_insufficient_panel_coverage"
    return "not_ready_no_rows_returned"


def _classify_exception(exc: Exception, provider_prefix: str = "provider") -> str:
    message = str(exc).lower()
    if any(token in message for token in ["permission", "quota", "权限", "积分", "访问频次", "抱歉"]):
        return f"{provider_prefix}_permission_or_quota_error"
    if any(token in message for token in ["rate limit", "429", "too many"]):
        return "provider_rate_limited"
    if any(token in message for token in ["timeout", "timed out"]):
        return "network_timeout"
    if any(token in message for token in ["connection", "dns", "ssl", "proxy", "network"]):
        return "network_transport_failure"
    if any(token in message for token in ["column", "schema", "field", "missing"]):
        return "provider_schema_failure"
    return "provider_runtime_error"


def _sanitize_message(exc: Exception) -> str:
    message = str(exc).replace("\n", " ").replace("\r", " ")
    token = os.environ.get("TUSHARE_TOKEN", "")
    if token:
        message = message.replace(token, "[redacted]")
    return _truncate(message)


def _truncate(message: str, limit: int = 240) -> str:
    return message if len(message) <= limit else message[: limit - 3] + "..."


def _compact_date(value: str) -> str:
    return value.replace("-", "")


def _plain_symbol(symbol: str) -> str:
    return symbol.split(".")[0]


def _baostock_code(symbol: str) -> str:
    code, exchange = symbol.split(".")
    return f"{exchange.lower()}.{code}"


def _yfinance_symbol(symbol: str) -> str:
    code, exchange = symbol.split(".")
    return f"{code}.SS" if exchange == "SH" else f"{code}.SZ"


def _qstock_kwargs(fn: Any, symbols: list[str]) -> dict[str, object] | None:
    signature = inspect.signature(fn)
    kwargs: dict[str, object] = {}
    for candidate in ["code", "symbol", "codes", "stock"]:
        if candidate in signature.parameters:
            kwargs[candidate] = _plain_symbol(symbols[0]) if symbols else "000001"
            break
    for name in ["start", "start_date", "sdate"]:
        if name in signature.parameters:
            kwargs[name] = PROBE_START_DATE
            break
    for name in ["end", "end_date", "edate"]:
        if name in signature.parameters:
            kwargs[name] = PROBE_END_DATE
            break
    return kwargs if kwargs else None


def _safe_attr(value: Any, attr: str, default: str) -> str:
    return _truncate(str(getattr(value, attr, default) or default))


def _forbidden_outputs_present(root: Path) -> list[str]:
    return [path for path in FORBIDDEN_OUTPUT_DIRS if (root / path).exists()]


def _workflow_rows(root: Path) -> dict[str, dict[str, str]]:
    path = root / "configs/project/workflow_status.csv"
    return {row["workflow_id"]: row for row in read_csv(path)} if path.exists() else {}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_csv(path: Path) -> list[dict[str, str]]:
    return read_csv(path) if path.exists() else []


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return read_json(path)
    except Exception:
        return {}


def _report_pass_or_warn(text: str, prefix: str) -> bool:
    return f"{prefix} {PASS}" in text or f"{prefix} {PASS_WITH_WARNINGS}" in text

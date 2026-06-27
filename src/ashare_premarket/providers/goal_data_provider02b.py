from __future__ import annotations

import importlib
import os
from pathlib import Path
from typing import Any

from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import preserve_later_review_only_capabilities, preserve_later_review_only_workflow_states
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.providers.goal_data_provider02a import (
    GOAL10B3_WORKFLOW_ID,
    GOAL10D_WORKFLOW_ID,
    GOAL_DATA_PANEL02_WORKFLOW_ID,
    GOAL_DATA_PROVIDER02B_WORKFLOW_ID,
    GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID,
    PASS,
    PASS_WITH_WARNINGS,
    _approved_symbols,
    _forbidden_outputs_present,
    _report_pass_or_warn,
    _workflow_rows,
)
from ashare_premarket.providers.goal_data_provider02a1 import WORKFLOW_ID as GOAL_DATA_PROVIDER02A1_WORKFLOW_ID
from ashare_premarket.providers.provider_registry import network_enabled
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-DATA-PROVIDER-02B"
GOAL_NAME = "GOAL-DATA-PROVIDER-02B-SOURCE-BACKED-EVALUATION-PANEL-BUILD-GATE"
MODE = "review_only_source_backed_evaluation_panel_build_gate"
WORKFLOW_ID = GOAL_DATA_PROVIDER02B_WORKFLOW_ID
ALLOWED_NEXT = "request_goal_v1_diagnostic_coverage03_or_fix_provider02b_warnings"
BLOCKED = "BLOCKED"

DATASET_DIR = "outputs/datasets"
DIAGNOSTIC_DIR = "outputs/diagnostics"
PROVIDER_DIR = "outputs/providers"
AUDIT_DIR = "outputs/audits"
CONFIG_DIR = "configs/providers"
DOC_DIR = "docs/providers"

PANEL_PATH = f"{DATASET_DIR}/goal_data_provider02b_source_backed_evaluation_panel.csv"
COVERAGE_SUMMARY_PATH = f"{DIAGNOSTIC_DIR}/goal_data_provider02b_panel_coverage_summary.csv"
PROVIDER_USAGE_PATH = f"{PROVIDER_DIR}/goal_data_provider02b_provider_usage_summary.csv"
FAILURE_TAXONOMY_PATH = f"{PROVIDER_DIR}/goal_data_provider02b_provider_failure_taxonomy.csv"
REPORT_PATH = f"{AUDIT_DIR}/goal_data_provider02b_source_backed_panel_report.md"
MANIFEST_PATH = f"{AUDIT_DIR}/goal_data_provider02b_source_backed_panel_manifest.json"
AUDIT_PATH = f"{AUDIT_DIR}/goal_data_provider02b_source_backed_panel_audit.md"
CONTRACT_PATH = f"{CONFIG_DIR}/goal_data_provider02b_panel_build_contract.yaml"
DOC_PATH = f"{DOC_DIR}/GOAL_DATA_PROVIDER02B_SOURCE_BACKED_EVALUATION_PANEL_BUILD_GATE.md"

PANEL_START_DATE = "2025-11-03"
PANEL_END_DATE = "2026-06-18"
TARGET_SYMBOLS = 50
TARGET_TRADE_DATES = 120
TARGET_ROWS = 6000
BENCHMARK_SYMBOL = "000300.SH"
PRIMARY_PROVIDER = "baostock"
CROSSCHECK_PROVIDER = "akshare"

PANEL_FIELDS = [
    "trade_date",
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "pre_close",
    "volume",
    "amount",
    "turnover",
    "pct_chg",
    "adjustment_mode",
    "trading_status",
    "is_st",
    "pe_ttm",
    "pb",
    "benchmark_symbol",
    "benchmark_return_1d",
    "benchmark_return_5d",
    "benchmark_return_20d",
    "forward_return_1d",
    "forward_return_5d",
    "forward_return_20d",
    "benchmark_excess_return_1d",
    "benchmark_excess_return_5d",
    "benchmark_excess_return_20d",
    "label_ready_1d",
    "label_ready_5d",
    "label_ready_20d",
    "source_provider",
    "source_provider_priority",
    "crosscheck_provider",
    "crosscheck_status",
    "source_warning_codes",
    "panel_contract_status",
    "universe_mode",
    "non_actionable_disclaimer",
]

COVERAGE_FIELDS = [
    "metric",
    "observed_value",
    "required_value",
    "status",
    "deficit",
    "notes",
]

PROVIDER_USAGE_FIELDS = [
    "provider_name",
    "provider_role",
    "provider_priority",
    "usage_status",
    "rows_returned",
    "unique_symbols",
    "unique_trade_dates",
    "date_min",
    "date_max",
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
    "recommendation_diagnostics_run",
    "position_band_diagnostics_run",
    "backtests_run",
    "goal_v1_diagnostic_coverage03_run",
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
    "downstream_execution_unlocked_by_this_goal",
    "goal_data_panel02_workflow_implemented_by_this_goal",
]


def run_goal_data_provider02b_source_backed_panel_build_gate(root: Path) -> bool:
    result = evaluate_goal_data_provider02b_source_backed_panel_build_gate(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal_data_provider02b_source_backed_panel_build_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal_data_provider02b_source_backed_panel_build_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    panel_rows = _read_csv(root / PANEL_PATH)
    coverage_rows = _read_csv(root / COVERAGE_SUMMARY_PATH)
    provider_rows = _read_csv(root / PROVIDER_USAGE_PATH)
    taxonomy_rows = _read_csv(root / FAILURE_TAXONOMY_PATH)
    workflow = _workflow_rows(root)
    metrics = _coverage_metrics(panel_rows)
    dc03_evidence_ready = _goal_v1_diagnostic_coverage03_valid(root)
    failures: list[str] = []

    if not _report_pass_or_warn(report, "GOAL-DATA-PROVIDER-02B Source-Backed Evaluation Panel Build Gate:"):
        failures.append("provider02b_report_not_pass_or_warn")
    if manifest.get("goal") != GOAL_NAME:
        failures.append("manifest_goal_invalid")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_invalid")
    if manifest.get("status") not in {PASS, PASS_WITH_WARNINGS}:
        failures.append("manifest_status_invalid")
    if manifest.get("panel_schema") != PANEL_FIELDS:
        failures.append("manifest_panel_schema_invalid")
    if panel_rows and list(panel_rows[0]) != PANEL_FIELDS:
        failures.append("panel_schema_invalid")
    if len(panel_rows) != int(manifest.get("row_count", -1)):
        failures.append("manifest_row_count_mismatch")
    if coverage_rows and list(coverage_rows[0]) != COVERAGE_FIELDS:
        failures.append("coverage_summary_schema_invalid")
    if provider_rows and list(provider_rows[0]) != PROVIDER_USAGE_FIELDS:
        failures.append("provider_usage_schema_invalid")
    if taxonomy_rows and list(taxonomy_rows[0]) != FAILURE_TAXONOMY_FIELDS:
        failures.append("failure_taxonomy_schema_invalid")

    if metrics["row_count"] < TARGET_ROWS:
        failures.append("row_count_below_minimum")
    if metrics["unique_symbols"] < TARGET_SYMBOLS:
        failures.append("unique_symbols_below_minimum")
    if metrics["unique_trade_dates"] < TARGET_TRADE_DATES:
        failures.append("unique_trade_dates_below_minimum")
    if metrics["duplicate_keys"] != 0:
        failures.append("duplicate_trade_date_symbol_keys")
    if metrics["forward_return_1d_coverage"] < 0.90:
        failures.append("forward_return_1d_coverage_below_threshold")
    if metrics["forward_return_5d_coverage"] < 0.85:
        failures.append("forward_return_5d_coverage_below_threshold")
    if metrics["forward_return_20d_coverage"] < 0.70:
        failures.append("forward_return_20d_coverage_below_threshold")
    if metrics["benchmark_excess_return_1d_coverage"] <= 0:
        failures.append("benchmark_excess_return_1d_missing")
    if metrics["benchmark_excess_return_5d_coverage"] <= 0:
        failures.append("benchmark_excess_return_5d_missing")
    if metrics["label_ready_20d_rows"] and metrics["benchmark_excess_return_20d_coverage"] <= 0:
        failures.append("benchmark_excess_return_20d_missing_where_label_ready")
    if manifest.get("demo_fixture_as_final_evidence") is not False:
        failures.append("demo_fixture_as_final_evidence_not_false")
    if manifest.get("source_backed_evaluation_panel_created") is not True:
        failures.append("source_backed_panel_created_not_true")
    if manifest.get("review_only_panel_generated") is not True:
        failures.append("review_only_panel_generated_not_true")
    if manifest.get("universe_mode") != "provider_panel_candidate_universe_review_only":
        failures.append("universe_mode_invalid")
    if manifest.get("goal_data_provider02b_workflow_status_after_gate") != "implemented_review_only":
        failures.append("provider02b_workflow_status_marker_invalid")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"manifest_{key}_not_false")
    for key in [
        "goal_data_panel02_locked_future",
        "goal_v1_diagnostic_coverage03_locked_future",
        "goal10b3_locked_future",
        "goal10d_locked_future",
        "dashboard_daily_report_locked_future",
        "yfinance_auxiliary_not_primary",
        "raw_payloads_never_persisted",
        "provider_tokens_never_persisted",
        "no_duplicate_trade_date_symbol_keys",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")
    if "demo" in _joined_rows(panel_rows).lower() or "fixture" in _joined_rows(panel_rows).lower():
        failures.append("demo_fixture_marker_present_in_panel")

    gate = workflow.get(WORKFLOW_ID, {})
    if gate.get("status") != "implemented_review_only":
        failures.append("provider02b_workflow_not_implemented_review_only")
    if gate.get("implemented_in_repo") != "true":
        failures.append("provider02b_workflow_not_marked_implemented")
    if gate.get("depends_on") != GOAL_DATA_PROVIDER02A1_WORKFLOW_ID:
        failures.append("provider02b_depends_on_invalid")
    if gate.get("allowed_next_action") != ALLOWED_NEXT:
        failures.append("provider02b_allowed_next_invalid")
    for workflow_id in [
        GOAL_DATA_PANEL02_WORKFLOW_ID,
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
    dc03 = workflow.get(GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID, {})
    if dc03_evidence_ready:
        if dc03.get("status") != "implemented_review_only":
            failures.append("goal_v1_diagnostic_coverage03_not_preserved_as_implemented_review_only")
        if dc03.get("implemented_in_repo") != "true":
            failures.append("goal_v1_diagnostic_coverage03_not_marked_implemented")
        if dc03.get("depends_on") != WORKFLOW_ID:
            failures.append("goal_v1_diagnostic_coverage03_dependency_not_provider02b")
    else:
        if dc03.get("status") != "locked_future":
            failures.append("goal_v1_diagnostic_coverage03_not_locked_future")
        if dc03.get("implemented_in_repo") != "false":
            failures.append("goal_v1_diagnostic_coverage03_marked_implemented")
    if workflow.get(GOAL_DATA_PANEL02_WORKFLOW_ID, {}).get("depends_on") != WORKFLOW_ID:
        failures.append("goal_data_panel02_dependency_not_provider02b")

    for path in _forbidden_outputs_present(root):
        failures.append(f"forbidden_output_path_exists:{path}")
    failures.extend(_token_leak_failures(root))

    replay_mode = "no_network_committed_evidence_replay" if not network_enabled(False) else "network_opt_in_source_backed_build_or_replay"
    status = PASS if not failures else BLOCKED
    write_text(
        root / AUDIT_PATH,
        "\n".join(
            [
                "# GOAL-DATA-PROVIDER-02B Source-Backed Evaluation Panel Audit",
                "",
                f"Status: `{status}`",
                f"Replay mode classification: `{replay_mode}`",
                "",
                f"Panel rows checked: `{len(panel_rows)}`",
                f"Unique symbols checked: `{metrics['unique_symbols']}`",
                f"Unique trade dates checked: `{metrics['unique_trade_dates']}`",
                f"Duplicate trade_date + symbol keys: `{metrics['duplicate_keys']}`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == PASS


def evaluate_goal_data_provider02b_source_backed_panel_build_gate(root: Path) -> dict[str, object]:
    network_on = network_enabled(False)
    prior_manifest = _read_json(root / MANIFEST_PATH)
    live_build_performed = False
    warnings: list[str] = []
    failures: list[str] = []
    provider_usage: list[dict[str, object]] = []
    failure_taxonomy: list[dict[str, object]] = []
    panel_rows: list[dict[str, object]] = []
    build_mode = "network_disabled_committed_evidence_replay"

    candidate_symbols, universe_mode, universe_warnings = _candidate_symbols(root)
    warnings.extend(universe_warnings)
    if len(candidate_symbols) < TARGET_SYMBOLS:
        failures.append("candidate_universe_below_50_symbols")

    if network_on and len(candidate_symbols) >= TARGET_SYMBOLS:
        try:
            build = _build_live_baostock_panel(root, candidate_symbols[:TARGET_SYMBOLS], universe_mode)
            panel_rows = build["panel_rows"]
            provider_usage = build["provider_usage"]
            failure_taxonomy = build["failure_taxonomy"]
            warnings.extend(build["warnings"])
            live_build_performed = bool(panel_rows)
            build_mode = "network_opt_in_baostock_primary_live_build"
        except Exception as exc:
            warnings.append(f"baostock_live_build_failed:{_sanitize_message(exc)}")
            failure_taxonomy.append(_failure_row(PRIMARY_PROVIDER, "provider_live_build_failed", "provider_network", "provider_query", True, "retry_or_use_committed_replay", _sanitize_message(exc)))

    if not panel_rows:
        panel_rows = _read_csv(root / PANEL_PATH)
        provider_usage = _read_csv(root / PROVIDER_USAGE_PATH)
        failure_taxonomy = _read_csv(root / FAILURE_TAXONOMY_PATH)
        if panel_rows:
            warnings.append("no_network_committed_evidence_replay" if not network_on else "live_build_unavailable_replayed_committed_panel")
            build_mode = "network_disabled_committed_evidence_replay" if not network_on else "live_build_failed_committed_evidence_replay"
        else:
            failures.append("no_source_backed_panel_available_for_replay")

    coverage_rows, coverage = _coverage_summary(panel_rows)
    contract_status = _panel_contract_status(coverage)
    for row in panel_rows:
        row["panel_contract_status"] = contract_status
    status = BLOCKED if failures or not panel_rows else PASS if contract_status == "source_backed_evaluation_panel_ready_for_dc03" and not warnings else PASS_WITH_WARNINGS
    if contract_status != "source_backed_evaluation_panel_ready_for_dc03":
        warnings.append("source_backed_panel_below_threshold")

    previous_live = bool(prior_manifest.get("source_backed_live_build_performed"))
    manifest = _manifest(
        root,
        status,
        warnings,
        failures,
        panel_rows,
        coverage_rows,
        provider_usage,
        failure_taxonomy,
        coverage,
        candidate_symbols[:TARGET_SYMBOLS],
        universe_mode,
        build_mode,
        network_on,
        live_build_performed or previous_live,
    )
    return {
        "status": status,
        "warnings": warnings,
        "failures": failures,
        "panel_rows": panel_rows,
        "coverage_rows": coverage_rows,
        "provider_usage_rows": provider_usage,
        "failure_taxonomy_rows": failure_taxonomy,
        "manifest": manifest,
    }


def goal_data_provider02b_valid_source_backed_panel_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    panel_rows = _read_csv(root / PANEL_PATH)
    return (
        (
            "GOAL-DATA-PROVIDER-02B Source-Backed Evaluation Panel Build Gate: PASS" in report
            or "GOAL-DATA-PROVIDER-02B Source-Backed Evaluation Panel Build Gate: PASS_WITH_WARNINGS" in report
        )
        and "Status: `PASS`" in audit
        and manifest.get("mode") == MODE
        and manifest.get("source_backed_evaluation_panel_created") is True
        and manifest.get("row_count", 0) >= TARGET_ROWS
        and manifest.get("unique_symbols", 0) >= TARGET_SYMBOLS
        and manifest.get("unique_trade_dates", 0) >= TARGET_TRADE_DATES
        and manifest.get("recommendation_diagnostics_run") is False
        and manifest.get("backtests_run") is False
        and bool(panel_rows)
    )


def goal_data_provider02b_implemented_workflow_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-DATA-PROVIDER-02B Source-Backed Evaluation Panel Build Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_review_only",
        "current_repo_role": "review_only_source_backed_evaluation_panel_build_gate",
        "implemented_in_repo": "true",
        "allowed_next_action": ALLOWED_NEXT,
        "depends_on": GOAL_DATA_PROVIDER02A1_WORKFLOW_ID,
        "produces_artifacts": ";".join([PANEL_PATH, COVERAGE_SUMMARY_PATH, PROVIDER_USAGE_PATH, FAILURE_TAXONOMY_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, CONTRACT_PATH, DOC_PATH]),
        "primary_docs": f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "scripts/run_goal_data_provider02b_source_backed_panel_build_gate.py;scripts/audit_goal_data_provider02b_source_backed_panel_build_gate.py",
        "primary_outputs": ";".join([PANEL_PATH, COVERAGE_SUMMARY_PATH, PROVIDER_USAGE_PATH, FAILURE_TAXONOMY_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH]),
        "promotion_rule": "implemented_review_only_after_goal_data_provider02b_source_backed_panel_pass_with_warnings",
        "notes": "Review-only source-backed evaluation panel build gate; creates normalized panel evidence only and no diagnostics, backtests, dashboard, trading, production, broker, local-lake, factor-mining, or DQN/RL output.",
    }


def locked_goal_data_panel02_patch() -> dict[str, str]:
    return _locked_patch(
        "GOAL-DATA-PANEL-02 Evaluation Panel Gate",
        "GOAL-DATA-PANEL-02",
        "locked_future_evaluation_panel_gate",
        "remain_locked_until_explicit_goal_data_panel02_request_or_documented_supersession",
        WORKFLOW_ID,
        "locked_until_explicit_goal_data_panel02_gate_or_supersession",
        "GOAL-DATA-PROVIDER-02B creates bounded review-only source-backed panel evidence, but the separate GOAL-DATA-PANEL-02 workflow remains locked.",
    )


def locked_goal_v1_diagnostic_coverage03_patch() -> dict[str, str]:
    return _locked_patch(
        "GOAL-V1-DIAGNOSTIC-COVERAGE-03 Multi-Provider Diagnostics",
        "GOAL-V1-DIAGNOSTIC-COVERAGE-03",
        "locked_future_multi_provider_diagnostics",
        "remain_locked_until_explicit_goal_v1_diagnostic_coverage03_request",
        GOAL_DATA_PANEL02_WORKFLOW_ID,
        "locked_until_explicit_goal_v1_diagnostic_coverage03_gate",
        "Future diagnostics over Provider-02B evidence remain locked; GOAL-DATA-PROVIDER-02B creates no risk, recommendation, or position diagnostics.",
    )


def locked_goal10b3_patch() -> dict[str, str]:
    return _locked_patch(
        "GOAL-10B.3 Recommendation Backtest Revalidation",
        "GOAL-10B.3",
        "locked_future_recommendation_revalidation",
        "remain_locked_until_explicit_goal10b3_request",
        GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID,
        "locked_until_explicit_goal10b3_revalidation_gate",
        "GOAL-10B.3 remains locked; GOAL-DATA-PROVIDER-02B creates no recommendation diagnostics or backtests.",
    )


def _build_live_baostock_panel(root: Path, symbols: list[str], universe_mode: str) -> dict[str, object]:
    bs = importlib.import_module("baostock")
    login = bs.login()
    if getattr(login, "error_code", "0") != "0":
        raise RuntimeError(f"baostock login failed: {getattr(login, 'error_msg', '')}")
    fields = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,isST"
    raw_by_symbol: dict[str, list[dict[str, str]]] = {}
    provider_usage: list[dict[str, object]] = []
    failure_taxonomy: list[dict[str, object]] = []
    warnings: list[str] = []
    try:
        for symbol in symbols:
            rs = bs.query_history_k_data_plus(
                _baostock_code(symbol),
                fields,
                start_date=PANEL_START_DATE,
                end_date=PANEL_END_DATE,
                frequency="d",
                adjustflag="3",
            )
            if getattr(rs, "error_code", "0") != "0":
                warnings.append(f"{symbol}:baostock_query_failed")
                failure_taxonomy.append(_failure_row(PRIMARY_PROVIDER, "provider_query_failed", "provider_network", "provider_query", True, "retry_provider_query", getattr(rs, "error_msg", "")))
                continue
            result_fields = list(getattr(rs, "fields", []) or fields.split(","))
            rows: list[dict[str, str]] = []
            while rs.next():
                rows.append(dict(zip(result_fields, rs.get_row_data())))
            raw_by_symbol[symbol] = rows
        benchmark_rows = _query_baostock_benchmark(bs)
    finally:
        bs.logout()

    selected_dates = _selected_label_ready_dates(benchmark_rows)
    benchmark_returns = _future_returns_by_date(benchmark_rows)
    crosscheck = _akshare_crosscheck(symbols[:5], selected_dates)
    panel_rows: list[dict[str, object]] = []
    for symbol, raw_rows in raw_by_symbol.items():
        rows = [row for row in sorted(raw_rows, key=lambda item: item.get("date", "")) if row.get("date") in selected_dates]
        all_rows = sorted(raw_rows, key=lambda item: item.get("date", ""))
        future_returns = _future_returns_by_date(all_rows)
        for row in rows:
            trade_date = row.get("date", "")
            stock_returns = future_returns.get(trade_date, {})
            bench = benchmark_returns.get(trade_date, {})
            warning_codes = ["canonical_approved_universe_below_50"] if universe_mode == "provider_panel_candidate_universe_review_only" else []
            cross_status = _crosscheck_status(symbol, trade_date, row.get("close", ""), crosscheck)
            if cross_status.startswith("not_checked"):
                warning_codes.append("crosscheck_sample_scope_limited")
            panel_rows.append(
                {
                    "trade_date": trade_date,
                    "symbol": symbol,
                    "open": _num(row.get("open")),
                    "high": _num(row.get("high")),
                    "low": _num(row.get("low")),
                    "close": _num(row.get("close")),
                    "pre_close": _num(row.get("preclose")),
                    "volume": _int_text(row.get("volume")),
                    "amount": _num(row.get("amount")),
                    "turnover": _num(row.get("turn")),
                    "pct_chg": _num(row.get("pctChg")),
                    "adjustment_mode": "baostock_adjustflag_3_unadjusted",
                    "trading_status": "trading" if row.get("tradestatus") == "1" else "not_trading",
                    "is_st": "true" if row.get("isST") == "1" else "false",
                    "pe_ttm": _num(row.get("peTTM")),
                    "pb": _num(row.get("pbMRQ")),
                    "benchmark_symbol": BENCHMARK_SYMBOL,
                    "benchmark_return_1d": _fmt(bench.get(1)),
                    "benchmark_return_5d": _fmt(bench.get(5)),
                    "benchmark_return_20d": _fmt(bench.get(20)),
                    "forward_return_1d": _fmt(stock_returns.get(1)),
                    "forward_return_5d": _fmt(stock_returns.get(5)),
                    "forward_return_20d": _fmt(stock_returns.get(20)),
                    "benchmark_excess_return_1d": _fmt(_diff(stock_returns.get(1), bench.get(1))),
                    "benchmark_excess_return_5d": _fmt(_diff(stock_returns.get(5), bench.get(5))),
                    "benchmark_excess_return_20d": _fmt(_diff(stock_returns.get(20), bench.get(20))),
                    "label_ready_1d": stock_returns.get(1) is not None and bench.get(1) is not None,
                    "label_ready_5d": stock_returns.get(5) is not None and bench.get(5) is not None,
                    "label_ready_20d": stock_returns.get(20) is not None and bench.get(20) is not None,
                    "source_provider": PRIMARY_PROVIDER,
                    "source_provider_priority": "1",
                    "crosscheck_provider": CROSSCHECK_PROVIDER,
                    "crosscheck_status": cross_status,
                    "source_warning_codes": ";".join(warning_codes),
                    "panel_contract_status": "pending_contract_evaluation",
                    "universe_mode": universe_mode,
                    "non_actionable_disclaimer": "review_only_panel_not_trading_or_position_output",
                }
            )

    dates = {row["trade_date"] for row in panel_rows}
    provider_usage.append(
        {
            "provider_name": PRIMARY_PROVIDER,
            "provider_role": "primary_panel_builder",
            "provider_priority": 1,
            "usage_status": PASS if panel_rows else BLOCKED,
            "rows_returned": len(panel_rows),
            "unique_symbols": len({row["symbol"] for row in panel_rows}),
            "unique_trade_dates": len(dates),
            "date_min": min(dates) if dates else "",
            "date_max": max(dates) if dates else "",
            "notes": "Primary daily OHLCV, adjustment, trading status, ST status, and valuation source.",
        }
    )
    provider_usage.append(
        {
            "provider_name": CROSSCHECK_PROVIDER,
            "provider_role": "sampled_crosscheck",
            "provider_priority": 2,
            "usage_status": crosscheck["status"],
            "rows_returned": crosscheck["rows_returned"],
            "unique_symbols": crosscheck["unique_symbols"],
            "unique_trade_dates": crosscheck["unique_trade_dates"],
            "date_min": crosscheck["date_min"],
            "date_max": crosscheck["date_max"],
            "notes": crosscheck["notes"],
        }
    )
    provider_usage.extend(_non_primary_provider_usage())
    failure_taxonomy.extend(_provider_failure_taxonomy(provider_usage))
    return {"panel_rows": panel_rows, "provider_usage": provider_usage, "failure_taxonomy": failure_taxonomy, "warnings": warnings}


def _query_baostock_benchmark(bs: Any) -> list[dict[str, str]]:
    rs = bs.query_history_k_data_plus(
        "sh.000300",
        "date,code,close,preclose,pctChg",
        start_date=PANEL_START_DATE,
        end_date=PANEL_END_DATE,
        frequency="d",
        adjustflag="3",
    )
    if getattr(rs, "error_code", "0") != "0":
        raise RuntimeError(f"baostock benchmark query failed: {getattr(rs, 'error_msg', '')}")
    fields = list(getattr(rs, "fields", []) or ["date", "code", "close", "preclose", "pctChg"])
    rows = []
    while rs.next():
        rows.append(dict(zip(fields, rs.get_row_data())))
    return rows


def _akshare_crosscheck(symbols: list[str], selected_dates: set[str]) -> dict[str, object]:
    mapping: dict[tuple[str, str], float] = {}
    try:
        ak = importlib.import_module("akshare")
    except Exception as exc:
        return {
            "status": PASS_WITH_WARNINGS,
            "rows_returned": 0,
            "unique_symbols": 0,
            "unique_trade_dates": 0,
            "date_min": "",
            "date_max": "",
            "notes": f"AkShare unavailable for sampled crosscheck: {_sanitize_message(exc)}",
            "prices": mapping,
        }
    dates: set[str] = set()
    seen_symbols: set[str] = set()
    rows_returned = 0
    try:
        for symbol in symbols:
            raw = ak.stock_zh_a_hist(symbol=_plain_symbol(symbol), period="daily", start_date=_compact_date(PANEL_START_DATE), end_date=_compact_date(PANEL_END_DATE), adjust="")
            records = raw.to_dict("records") if hasattr(raw, "to_dict") else []
            for item in records:
                date_value = str(item.get("\u65e5\u671f", "") or item.get("date", "") or item.get("trade_date", ""))
                if date_value not in selected_dates:
                    continue
                close = _float(item.get("\u6536\u76d8", item.get("close")))
                if close is None:
                    continue
                mapping[(symbol, date_value)] = close
                dates.add(date_value)
                seen_symbols.add(symbol)
                rows_returned += 1
        return {
            "status": PASS if rows_returned else PASS_WITH_WARNINGS,
            "rows_returned": rows_returned,
            "unique_symbols": len(seen_symbols),
            "unique_trade_dates": len(dates),
            "date_min": min(dates) if dates else "",
            "date_max": max(dates) if dates else "",
            "notes": "Sampled close-price crosscheck against unadjusted AkShare rows." if rows_returned else "AkShare returned no sampled crosscheck rows.",
            "prices": mapping,
        }
    except Exception as exc:
        return {
            "status": PASS_WITH_WARNINGS,
            "rows_returned": rows_returned,
            "unique_symbols": len(seen_symbols),
            "unique_trade_dates": len(dates),
            "date_min": min(dates) if dates else "",
            "date_max": max(dates) if dates else "",
            "notes": f"AkShare sampled crosscheck warning: {_sanitize_message(exc)}",
            "prices": mapping,
        }


def _candidate_symbols(root: Path) -> tuple[list[str], str, list[str]]:
    approved = _approved_symbols(root)
    warnings: list[str] = []
    if len(approved) >= TARGET_SYMBOLS:
        return approved, "canonical_approved_universe", warnings
    warnings.append("canonical_approved_universe_below_50_review_only_candidate_used")
    path = root / "outputs/samples/source_backed_universe_sample.csv"
    rows = read_csv(path) if path.exists() else []
    symbols = [row.get("symbol", "") for row in rows if row.get("symbol")]
    deduped = list(dict.fromkeys(symbols))
    return deduped, "provider_panel_candidate_universe_review_only", warnings


def _selected_label_ready_dates(benchmark_rows: list[dict[str, str]]) -> set[str]:
    dates = [row.get("date", "") for row in sorted(benchmark_rows, key=lambda item: item.get("date", "")) if row.get("date")]
    label_ready_dates = dates[:-20] if len(dates) > 20 else dates
    return set(label_ready_dates[-TARGET_TRADE_DATES:])


def _future_returns_by_date(rows: list[dict[str, str]]) -> dict[str, dict[int, float | None]]:
    ordered = [row for row in sorted(rows, key=lambda item: item.get("date", "")) if row.get("date")]
    output: dict[str, dict[int, float | None]] = {}
    closes = [_float(row.get("close")) for row in ordered]
    for index, row in enumerate(ordered):
        base = closes[index]
        values: dict[int, float | None] = {}
        for horizon in [1, 5, 20]:
            future = closes[index + horizon] if index + horizon < len(closes) else None
            values[horizon] = None if base in {None, 0} or future is None else (future / base) - 1
        output[row["date"]] = values
    return output


def _coverage_summary(panel_rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    metrics = _coverage_metrics(panel_rows)
    contract_status = _panel_contract_status(metrics)
    rows = [
        _coverage_row("row_count", metrics["row_count"], TARGET_ROWS, metrics["row_count"] >= TARGET_ROWS, max(0, TARGET_ROWS - metrics["row_count"]), "Normalized panel rows."),
        _coverage_row("unique_symbols", metrics["unique_symbols"], TARGET_SYMBOLS, metrics["unique_symbols"] >= TARGET_SYMBOLS, max(0, TARGET_SYMBOLS - metrics["unique_symbols"]), "Review-only candidate symbols."),
        _coverage_row("unique_trade_dates", metrics["unique_trade_dates"], TARGET_TRADE_DATES, metrics["unique_trade_dates"] >= TARGET_TRADE_DATES, max(0, TARGET_TRADE_DATES - metrics["unique_trade_dates"]), "Label-ready trade dates."),
        _coverage_row("duplicate_trade_date_symbol_keys", metrics["duplicate_keys"], 0, metrics["duplicate_keys"] == 0, metrics["duplicate_keys"], "Duplicate grain check."),
        _coverage_row("missing_ohlcv_fields", metrics["missing_ohlcv_fields"], 0, metrics["missing_ohlcv_fields"] == 0, metrics["missing_ohlcv_fields"], "Open, high, low, close, volume missing cells."),
        _coverage_row("missing_amount", metrics["missing_amount"], 0, metrics["missing_amount"] == 0, metrics["missing_amount"], "Amount missing cells."),
        _coverage_row("missing_turnover", metrics["missing_turnover"], 0, metrics["missing_turnover"] == 0, metrics["missing_turnover"], "Turnover missing cells."),
        _coverage_row("trading_status_coverage", metrics["trading_status_coverage"], 1.0, metrics["trading_status_coverage"] >= 0.99, _coverage_deficit(0.99, metrics["trading_status_coverage"]), "Trading status coverage."),
        _coverage_row("st_status_coverage", metrics["st_status_coverage"], 1.0, metrics["st_status_coverage"] >= 0.99, _coverage_deficit(0.99, metrics["st_status_coverage"]), "ST status coverage."),
        _coverage_row("adjustment_coverage", metrics["adjustment_coverage"], 1.0, metrics["adjustment_coverage"] >= 0.99, _coverage_deficit(0.99, metrics["adjustment_coverage"]), "Adjustment-mode coverage."),
        _coverage_row("benchmark_coverage", metrics["benchmark_coverage"], 1.0, metrics["benchmark_coverage"] >= 0.99, _coverage_deficit(0.99, metrics["benchmark_coverage"]), "Benchmark symbol and returns coverage."),
        _coverage_row("forward_return_1d_coverage", metrics["forward_return_1d_coverage"], 0.90, metrics["forward_return_1d_coverage"] >= 0.90, _coverage_deficit(0.90, metrics["forward_return_1d_coverage"]), "1d label coverage."),
        _coverage_row("forward_return_5d_coverage", metrics["forward_return_5d_coverage"], 0.85, metrics["forward_return_5d_coverage"] >= 0.85, _coverage_deficit(0.85, metrics["forward_return_5d_coverage"]), "5d label coverage."),
        _coverage_row("forward_return_20d_coverage", metrics["forward_return_20d_coverage"], 0.70, metrics["forward_return_20d_coverage"] >= 0.70, _coverage_deficit(0.70, metrics["forward_return_20d_coverage"]), "20d label coverage."),
        _coverage_row("benchmark_excess_return_1d_coverage", metrics["benchmark_excess_return_1d_coverage"], 0.90, metrics["benchmark_excess_return_1d_coverage"] > 0, 0 if metrics["benchmark_excess_return_1d_coverage"] > 0 else 1, "1d benchmark excess availability."),
        _coverage_row("benchmark_excess_return_5d_coverage", metrics["benchmark_excess_return_5d_coverage"], 0.85, metrics["benchmark_excess_return_5d_coverage"] > 0, 0 if metrics["benchmark_excess_return_5d_coverage"] > 0 else 1, "5d benchmark excess availability."),
        _coverage_row("benchmark_excess_return_20d_coverage", metrics["benchmark_excess_return_20d_coverage"], 0.70, metrics["benchmark_excess_return_20d_coverage"] > 0, 0 if metrics["benchmark_excess_return_20d_coverage"] > 0 else 1, "20d benchmark excess availability where label-ready."),
        _coverage_row("cross_provider_price_diff_available", metrics["crosschecked_rows"], 1, metrics["crosschecked_rows"] > 0, 0 if metrics["crosschecked_rows"] > 0 else 1, "AkShare sampled price-difference check."),
        _coverage_row("demo_fixture_detection", 0 if not metrics["demo_fixture_detected"] else 1, 0, not metrics["demo_fixture_detected"], 0 if not metrics["demo_fixture_detected"] else 1, "No demo fixture counted as final evidence."),
        _coverage_row("threshold_classification", contract_status, "source_backed_evaluation_panel_ready_for_dc03", contract_status == "source_backed_evaluation_panel_ready_for_dc03", "" if contract_status == "source_backed_evaluation_panel_ready_for_dc03" else "threshold_deficit_present", "Downstream readiness classification."),
    ]
    return rows, metrics


def _coverage_metrics(panel_rows: list[dict[str, object]]) -> dict[str, Any]:
    row_count = len(panel_rows)
    symbols = {str(row.get("symbol", "")) for row in panel_rows if row.get("symbol")}
    dates = {str(row.get("trade_date", "")) for row in panel_rows if row.get("trade_date")}
    keys = [(str(row.get("trade_date", "")), str(row.get("symbol", ""))) for row in panel_rows]
    duplicate_keys = len(keys) - len(set(keys))
    missing_ohlcv = sum(1 for row in panel_rows for field in ["open", "high", "low", "close", "volume"] if not str(row.get(field, "")))
    missing_amount = sum(1 for row in panel_rows if not str(row.get("amount", "")))
    missing_turnover = sum(1 for row in panel_rows if not str(row.get("turnover", "")))
    return {
        "row_count": row_count,
        "unique_symbols": len(symbols),
        "unique_trade_dates": len(dates),
        "date_min": min(dates) if dates else "",
        "date_max": max(dates) if dates else "",
        "duplicate_keys": duplicate_keys,
        "missing_ohlcv_fields": missing_ohlcv,
        "missing_amount": missing_amount,
        "missing_turnover": missing_turnover,
        "trading_status_coverage": _coverage(panel_rows, "trading_status"),
        "st_status_coverage": _coverage(panel_rows, "is_st"),
        "adjustment_coverage": _coverage(panel_rows, "adjustment_mode"),
        "benchmark_coverage": _coverage(panel_rows, "benchmark_return_1d"),
        "forward_return_1d_coverage": _coverage(panel_rows, "forward_return_1d"),
        "forward_return_5d_coverage": _coverage(panel_rows, "forward_return_5d"),
        "forward_return_20d_coverage": _coverage(panel_rows, "forward_return_20d"),
        "benchmark_excess_return_1d_coverage": _coverage(panel_rows, "benchmark_excess_return_1d"),
        "benchmark_excess_return_5d_coverage": _coverage(panel_rows, "benchmark_excess_return_5d"),
        "benchmark_excess_return_20d_coverage": _coverage(panel_rows, "benchmark_excess_return_20d"),
        "label_ready_1d_rows": sum(1 for row in panel_rows if _truthy(row.get("label_ready_1d"))),
        "label_ready_5d_rows": sum(1 for row in panel_rows if _truthy(row.get("label_ready_5d"))),
        "label_ready_20d_rows": sum(1 for row in panel_rows if _truthy(row.get("label_ready_20d"))),
        "crosschecked_rows": sum(1 for row in panel_rows if str(row.get("crosscheck_status", "")).startswith("checked_")),
        "demo_fixture_detected": "demo" in _joined_rows(panel_rows).lower() or "fixture" in _joined_rows(panel_rows).lower(),
    }


def _manifest(
    root: Path,
    status: str,
    warnings: list[str],
    failures: list[str],
    panel_rows: list[dict[str, object]],
    coverage_rows: list[dict[str, object]],
    provider_usage: list[dict[str, object]],
    failure_taxonomy: list[dict[str, object]],
    coverage: dict[str, object],
    symbols: list[str],
    universe_mode: str,
    build_mode: str,
    network_on: bool,
    live_build_performed: bool,
) -> dict[str, object]:
    contract_status = _panel_contract_status(coverage)
    payload: dict[str, object] = {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "mode": MODE,
        "status": status,
        "warnings": sorted(set(warnings)),
        "failures": failures,
        "build_mode": build_mode,
        "network_opt_in_present": network_on,
        "source_backed_live_build_performed": live_build_performed,
        "no_network_replay_supported": True,
        "replay_mode_classification": "no_network_committed_evidence_replay" if not network_on else "network_opt_in_source_backed_build_or_replay",
        "panel_schema": PANEL_FIELDS,
        "coverage_schema": COVERAGE_FIELDS,
        "provider_usage_schema": PROVIDER_USAGE_FIELDS,
        "failure_taxonomy_schema": FAILURE_TAXONOMY_FIELDS,
        "panel_path": PANEL_PATH,
        "row_count": coverage["row_count"],
        "unique_symbols": coverage["unique_symbols"],
        "unique_trade_dates": coverage["unique_trade_dates"],
        "date_min": coverage["date_min"],
        "date_max": coverage["date_max"],
        "target_unique_symbols": TARGET_SYMBOLS,
        "target_unique_trade_dates": TARGET_TRADE_DATES,
        "target_row_count": TARGET_ROWS,
        "symbol_deficit": max(0, TARGET_SYMBOLS - int(coverage["unique_symbols"])),
        "date_deficit": max(0, TARGET_TRADE_DATES - int(coverage["unique_trade_dates"])),
        "row_deficit": max(0, TARGET_ROWS - int(coverage["row_count"])),
        "forward_return_20d_deficit": _coverage_deficit(0.70, float(coverage["forward_return_20d_coverage"])),
        "provider_coverage_deficit": 0 if int(coverage["row_count"]) >= TARGET_ROWS else max(0, TARGET_ROWS - int(coverage["row_count"])),
        "benchmark_coverage_deficit": _coverage_deficit(0.99, float(coverage["benchmark_coverage"])),
        "panel_contract_status": contract_status,
        "downstream_readiness_for_goal_v1_diagnostic_coverage03": contract_status,
        "universe_mode": universe_mode,
        "candidate_symbols": symbols,
        "approved_symbols_available": len(_approved_symbols(root)),
        "approved_universe_expanded": False,
        "source_backed_evaluation_panel_created": bool(panel_rows),
        "review_only_panel_generated": bool(panel_rows),
        "demo_fixture_as_final_evidence": False,
        "no_duplicate_trade_date_symbol_keys": coverage["duplicate_keys"] == 0,
        "primary_provider": PRIMARY_PROVIDER,
        "crosscheck_provider": CROSSCHECK_PROVIDER,
        "provider_usage_row_count": len(provider_usage),
        "failure_taxonomy_row_count": len(failure_taxonomy),
        "coverage_summary_row_count": len(coverage_rows),
        "yfinance_auxiliary_not_primary": True,
        "raw_payloads_never_persisted": True,
        "provider_tokens_never_persisted": True,
        "normalized_bounded_panel_only": True,
        "goal_data_provider02b_workflow_status_after_gate": "implemented_review_only",
        "goal_data_panel02_status_after_goal_data_provider02b": "locked_future",
        "goal_data_panel02_locked_future": True,
        "goal_v1_diagnostic_coverage03_status_after_goal_data_provider02b": "locked_future",
        "goal_v1_diagnostic_coverage03_locked_future": True,
        "goal10b3_status_after_goal_data_provider02b": "locked_future",
        "goal10b3_locked_future": True,
        "goal10d_status_after_goal_data_provider02b": "locked_future",
        "goal10d_locked_future": True,
        "dashboard_daily_report_status_after_goal_data_provider02b": "locked_future",
        "dashboard_daily_report_locked_future": True,
        "workflow_status_before_goal_data_provider02b": _workflow_rows(root).get(WORKFLOW_ID, {}).get("status", "missing"),
    }
    for key in FALSE_BOUNDARY_KEYS:
        payload[key] = False
    return payload


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / PANEL_PATH, result["panel_rows"], PANEL_FIELDS)
    write_csv(root / COVERAGE_SUMMARY_PATH, result["coverage_rows"], COVERAGE_FIELDS)
    write_csv(root / PROVIDER_USAGE_PATH, result["provider_usage_rows"], PROVIDER_USAGE_FIELDS)
    write_csv(root / FAILURE_TAXONOMY_PATH, result["failure_taxonomy_rows"], FAILURE_TAXONOMY_FIELDS)
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_contract(root)
    _write_report(root, result)
    _write_doc(root, result)


def _write_contract(root: Path) -> None:
    payload = {
        "goal": GOAL_NAME,
        "mode": MODE,
        "review_only": True,
        "network_default": "disabled_committed_evidence_replay",
        "live_build_opt_in": "ASHARE_ALLOW_NETWORK_INGESTION=1",
        "approved_universe_policy": "use_if_at_least_50_else_provider_panel_candidate_universe_review_only",
        "canonical_approved_universe_mutated": False,
        "panel_window": {"start": PANEL_START_DATE, "end": PANEL_END_DATE, "target_trade_dates": TARGET_TRADE_DATES},
        "thresholds": {
            "unique_symbols": TARGET_SYMBOLS,
            "unique_trade_dates": TARGET_TRADE_DATES,
            "row_count": TARGET_ROWS,
            "forward_return_1d_coverage": 0.90,
            "forward_return_5d_coverage": 0.85,
            "forward_return_20d_coverage": 0.70,
        },
        "providers": [
            {"provider_name": "baostock", "role": "primary_panel_builder", "fields": "OHLCV, amount, turnover, adjustment, trading_status, ST status, PE TTM, PB"},
            {"provider_name": "akshare", "role": "sampled_crosscheck_and_fallback"},
            {"provider_name": "efinance", "role": "fallback_after_rate_limit_schema_review"},
            {"provider_name": "yfinance", "role": "auxiliary_only"},
            {"provider_name": "tushare_pro", "role": "optional_token_gated"},
            {"provider_name": "local_import", "role": "fallback_only_if_source_backed_rows_align"},
        ],
        "normalized_panel_schema": PANEL_FIELDS,
        "allowed_outputs": [PANEL_PATH, COVERAGE_SUMMARY_PATH, PROVIDER_USAGE_PATH, FAILURE_TAXONOMY_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH, CONTRACT_PATH],
        "forbidden_outputs": FALSE_BOUNDARY_KEYS,
        "downstream_locks": {
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
    write_text(
        root / REPORT_PATH,
        "\n".join(
            [
                "# GOAL-DATA-PROVIDER-02B Source-Backed Evaluation Panel Build Report",
                "",
                f"GOAL-DATA-PROVIDER-02B Source-Backed Evaluation Panel Build Gate: {result['status']}",
                "",
                f"Mode: `{MODE}`",
                f"Build mode: `{manifest['build_mode']}`",
                f"Replay mode classification: `{manifest['replay_mode_classification']}`",
                f"Panel contract status: `{manifest['panel_contract_status']}`",
                f"Rows: `{manifest['row_count']}`",
                f"Unique symbols: `{manifest['unique_symbols']}`",
                f"Unique trade dates: `{manifest['unique_trade_dates']}`",
                f"Date range: `{manifest['date_min']}` to `{manifest['date_max']}`",
                f"Universe mode: `{manifest['universe_mode']}`",
                f"Forward return 20d deficit: `{manifest['forward_return_20d_deficit']}`",
                "",
                "## Boundary",
                "- This gate creates a bounded normalized source-backed review-only panel only.",
                "- The canonical approved universe is not expanded.",
                "- The separate GOAL-DATA-PANEL-02 workflow remains locked.",
                "- GOAL-V1-DIAGNOSTIC-COVERAGE-03 is not implemented by this panel gate; GOAL-10B.3, GOAL-10D, dashboards, backtests, trading, production, broker, local-lake, factor-mining, and DQN/RL remain locked.",
                "- No raw provider payloads or provider tokens are persisted.",
                "",
                "## Warnings",
                *[f"- {warning}" for warning in result["warnings"]],
                "",
            ]
        ),
    )


def _write_doc(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    write_text(
        root / DOC_PATH,
        "\n".join(
            [
                "# GOAL-DATA-PROVIDER-02B Source-Backed Evaluation Panel Build Gate",
                "",
                "GOAL-DATA-PROVIDER-02B is a review-only source-backed evaluation panel build gate. It may build a bounded normalized A-share panel from live providers when `ASHARE_ALLOW_NETWORK_INGESTION=1` is set, and it may validate committed normalized evidence in no-network replay mode.",
                "",
                "The current canonical approved universe has fewer than 50 symbols, so this gate uses `provider_panel_candidate_universe_review_only` and does not alter `configs/universe/approved_symbols.csv`.",
                "",
                "## Outputs",
                "",
                f"- `{PANEL_PATH}`",
                f"- `{COVERAGE_SUMMARY_PATH}`",
                f"- `{PROVIDER_USAGE_PATH}`",
                f"- `{FAILURE_TAXONOMY_PATH}`",
                f"- `{REPORT_PATH}`",
                f"- `{MANIFEST_PATH}`",
                f"- `{AUDIT_PATH}`",
                f"- `{CONTRACT_PATH}`",
                "",
                "## Current Result",
                "",
                f"- Status: `{result['status']}`",
                f"- Panel contract status: `{manifest['panel_contract_status']}`",
                f"- Rows: `{manifest['row_count']}`",
                f"- Unique symbols: `{manifest['unique_symbols']}`",
                f"- Unique trade dates: `{manifest['unique_trade_dates']}`",
                f"- Date range: `{manifest['date_min']}` to `{manifest['date_max']}`",
                "",
                "## Locked Boundaries",
                "",
                "GOAL-V1-DIAGNOSTIC-COVERAGE-03 is not implemented by this panel gate; it may only be preserved when its own source-backed diagnostic evidence exists. GOAL-10B.3, GOAL-10D, dashboards, signal and portfolio backtests, trading, production, broker, local-lake, factor-mining, and DQN/RL remain locked. This panel is not a recommendation, position, portfolio, or execution output.",
                "",
            ]
        ),
    )


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys()) if rows else []
    by_id = {row["workflow_id"]: row for row in rows}
    _upsert_workflow_row(rows, by_id, WORKFLOW_ID, goal_data_provider02b_implemented_workflow_patch(), after=GOAL_DATA_PROVIDER02A1_WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL_DATA_PANEL02_WORKFLOW_ID, locked_goal_data_panel02_patch(), after=WORKFLOW_ID)
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
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_data_provider02b"
    if "dqn_rl_mainline" in by_id:
        by_id["dqn_rl_mainline"]["status"] = "deleted_from_active_mainline"
        by_id["dqn_rl_mainline"]["implemented_in_repo"] = "false"
    if "v2_factor_research_upgrade" in by_id:
        by_id["v2_factor_research_upgrade"]["status"] = "planned_locked"
        by_id["v2_factor_research_upgrade"]["implemented_in_repo"] = "false"
    preserve_later_review_only_workflow_states(root, by_id)
    if result["status"] != BLOCKED:
        by_id[WORKFLOW_ID].update(goal_data_provider02b_implemented_workflow_patch())
        by_id[GOAL_DATA_PANEL02_WORKFLOW_ID].update(locked_goal_data_panel02_patch())
        by_id[GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID].update(locked_goal_v1_diagnostic_coverage03_patch())
        by_id[GOAL10B3_WORKFLOW_ID].update(locked_goal10b3_patch())
        if "dashboard_daily_report" in by_id:
            by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_data_provider02b"
        preserve_later_review_only_workflow_states(root, by_id)
    write_csv(path, rows, fields)


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    if not path.exists():
        return
    payload = read_json(path)
    payload[WORKFLOW_ID] = "implemented_review_only" if result["status"] != BLOCKED else False
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
        payload[GOAL_DATA_PANEL02_WORKFLOW_ID] = False
        payload[GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID] = False
        payload[GOAL10B3_WORKFLOW_ID] = False
        preserve_later_review_only_capabilities(root, payload)
    write_json(path, payload)


def _upsert_workflow_row(rows: list[dict[str, str]], by_id: dict[str, dict[str, str]], workflow_id: str, patch: dict[str, str], *, after: str) -> None:
    if workflow_id in by_id:
        by_id[workflow_id].update(patch)
        return
    insert_at = next((index + 1 for index, item in enumerate(rows) if item["workflow_id"] == after), len(rows))
    row = {"workflow_id": workflow_id, **patch}
    rows.insert(insert_at, row)
    by_id[workflow_id] = row


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


def _non_primary_provider_usage() -> list[dict[str, object]]:
    return [
        _usage_row("efinance", "fallback_after_rate_limit_schema_review", 3, "not_used_primary_sufficient", "No fallback call needed after Baostock primary panel build."),
        _usage_row("yfinance", "auxiliary_only", 4, "not_primary_auxiliary_only", "Auxiliary only and never primary for A-share panel."),
        _usage_row("tushare_pro", "optional_token_gated", 5, "skipped_missing_token_or_policy", "Requires TUSHARE_TOKEN and explicit Tushare opt-in from environment."),
        _usage_row("qstock", "optional_data_candidate", 6, "not_used_optional_dependency_or_scope", "Backtest and strategy modules are forbidden."),
        _usage_row("local_import", "fallback", 7, "not_used_current_approved_rows_missing", "Fallback only if source-backed rows align; demo fixtures do not count."),
    ]


def _usage_row(provider: str, role: str, priority: int, status: str, notes: str) -> dict[str, object]:
    return {"provider_name": provider, "provider_role": role, "provider_priority": priority, "usage_status": status, "rows_returned": 0, "unique_symbols": 0, "unique_trade_dates": 0, "date_min": "", "date_max": "", "notes": notes}


def _provider_failure_taxonomy(provider_usage: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for row in provider_usage:
        provider = str(row.get("provider_name", ""))
        status = str(row.get("usage_status", ""))
        if status == PASS:
            rows.append(_failure_row(provider, "", "none", "none", False, "none", "Provider used successfully."))
        elif provider == "tushare_pro":
            rows.append(_failure_row(provider, "tushare_unavailable_missing_token_or_policy", "credential_policy", "missing_token_or_opt_in", False, "set_env_only_if_needed", str(row.get("notes", ""))))
        elif provider == "qstock":
            rows.append(_failure_row(provider, "optional_provider_not_used", "dependency_or_scope", "optional_provider", False, "keep_strategy_modules_forbidden", str(row.get("notes", ""))))
        else:
            rows.append(_failure_row(provider, status or "not_used", "provider_ladder", "not_selected", False, "no_action_required", str(row.get("notes", ""))))
    return rows


def _failure_row(provider: str, code: str, layer: str, category: str, retryable: bool, owner_action: str, notes: str) -> dict[str, object]:
    return {
        "provider_name": provider,
        "failure_code": code,
        "failure_layer": layer,
        "failure_category": category,
        "retryable": retryable,
        "owner_action": owner_action,
        "notes": notes[:240],
    }


def _panel_contract_status(metrics: dict[str, object]) -> str:
    ready = (
        int(metrics.get("row_count", 0)) >= TARGET_ROWS
        and int(metrics.get("unique_symbols", 0)) >= TARGET_SYMBOLS
        and int(metrics.get("unique_trade_dates", 0)) >= TARGET_TRADE_DATES
        and int(metrics.get("duplicate_keys", 1)) == 0
        and float(metrics.get("forward_return_1d_coverage", 0)) >= 0.90
        and float(metrics.get("forward_return_5d_coverage", 0)) >= 0.85
        and float(metrics.get("forward_return_20d_coverage", 0)) >= 0.70
        and float(metrics.get("benchmark_excess_return_1d_coverage", 0)) > 0
        and float(metrics.get("benchmark_excess_return_5d_coverage", 0)) > 0
        and float(metrics.get("benchmark_excess_return_20d_coverage", 0)) > 0
        and not bool(metrics.get("demo_fixture_detected", True))
    )
    return "source_backed_evaluation_panel_ready_for_dc03" if ready else "source_backed_panel_below_threshold"


def _coverage(rows: list[dict[str, object]], field: str) -> float:
    if not rows:
        return 0.0
    present = sum(1 for row in rows if str(row.get(field, "")) not in {"", "None", "nan"})
    return present / len(rows)


def _coverage_row(metric: str, observed: object, required: object, ok: bool, deficit: object, notes: str) -> dict[str, object]:
    return {"metric": metric, "observed_value": observed, "required_value": required, "status": PASS if ok else PASS_WITH_WARNINGS, "deficit": deficit, "notes": notes}


def _coverage_deficit(required: float, observed: float) -> float:
    return round(max(0.0, required - observed), 6)


def _crosscheck_status(symbol: str, trade_date: str, close_text: str, crosscheck: dict[str, object]) -> str:
    prices = crosscheck.get("prices", {})
    price = prices.get((symbol, trade_date)) if isinstance(prices, dict) else None
    close = _float(close_text)
    if price is None or close in {None, 0}:
        return "not_checked_sample_scope_or_provider_unavailable"
    diff_pct = abs((float(price) / float(close)) - 1)
    return "checked_close_diff_within_tolerance" if diff_pct <= 0.01 else "checked_close_diff_warning"


def _diff(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return left - right


def _fmt(value: float | None) -> str:
    return "" if value is None else f"{value:.10f}"


def _num(value: object) -> str:
    number = _float(value)
    return "" if number is None else f"{number:.6f}".rstrip("0").rstrip(".")


def _int_text(value: object) -> str:
    number = _float(value)
    return "" if number is None else str(int(number))


def _float(value: object) -> float | None:
    try:
        text = str(value).strip()
        if not text:
            return None
        return float(text)
    except Exception:
        return None


def _truthy(value: object) -> bool:
    return value is True or str(value).lower() == "true"


def _baostock_code(symbol: str) -> str:
    code, exchange = symbol.split(".")
    return f"{exchange.lower()}.{code}"


def _plain_symbol(symbol: str) -> str:
    return symbol.split(".")[0]


def _compact_date(value: str) -> str:
    return value.replace("-", "")


def _sanitize_message(exc: object) -> str:
    return " ".join(str(exc).replace("\n", " ").replace("\r", " ").split())[:240]


def _token_leak_failures(root: Path) -> list[str]:
    token = os.environ.get("TUSHARE_TOKEN", "")
    if not token:
        return []
    failures = []
    for path in [PANEL_PATH, COVERAGE_SUMMARY_PATH, PROVIDER_USAGE_PATH, FAILURE_TAXONOMY_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH, CONTRACT_PATH]:
        full_path = root / path
        if full_path.exists() and token in full_path.read_text(encoding="utf-8"):
            failures.append(f"provider_token_leaked:{path}")
    return failures


def _joined_rows(rows: list[dict[str, object]]) -> str:
    return "\n".join(" ".join(str(value) for value in row.values()) for row in rows)


def _goal_v1_diagnostic_coverage03_valid(root: Path) -> bool:
    try:
        from ashare_premarket.diagnostics.goal_v1_diagnostic_coverage03 import (
            goal_v1_diagnostic_coverage03_valid_source_backed_diagnostics_evidence,
        )

        return goal_v1_diagnostic_coverage03_valid_source_backed_diagnostics_evidence(root)
    except Exception:
        return False


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

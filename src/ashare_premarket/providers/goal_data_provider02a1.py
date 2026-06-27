from __future__ import annotations

import os
from pathlib import Path

from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import preserve_later_review_only_capabilities, preserve_later_review_only_workflow_states
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.providers.goal_data_provider02a import (
    FAILURE_TAXONOMY_FIELDS,
    GOAL10B3_WORKFLOW_ID,
    GOAL10C_WORKFLOW_ID,
    GOAL10D_WORKFLOW_ID,
    GOAL_DATA_PANEL02_WORKFLOW_ID,
    GOAL_DATA_PROVIDER02B_WORKFLOW_ID,
    GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID,
    PASS,
    PASS_WITH_WARNINGS,
    PROBE_END_DATE,
    PROBE_FIELDS,
    PROBE_START_DATE,
    PROBE_TRADING_DAY_WINDOW,
    PROVIDERS,
    SCHEMA_MAPPING_FIELDS,
    _approved_symbols,
    _failure_taxonomy_rows,
    _forbidden_outputs_present,
    _probe_akshare,
    _probe_baostock,
    _probe_efinance,
    _probe_local_import,
    _probe_qstock,
    _probe_tushare,
    _probe_yfinance,
    _report_pass_or_warn,
    _schema_mapping_rows,
    _workflow_rows,
    locked_goal10b3_patch as locked_goal10b3_after_goal_data_provider02a_patch,
    locked_goal_data_panel02_patch as locked_goal_data_panel02_after_goal_data_provider02a_patch,
    locked_goal_v1_diagnostic_coverage03_patch as locked_goal_v1_diagnostic_coverage03_after_goal_data_provider02a_patch,
)
from ashare_premarket.providers.provider_registry import network_enabled
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-DATA-PROVIDER-02A.1"
GOAL_NAME = "GOAL-DATA-PROVIDER-02A.1-NETWORK-OPT-IN-PROVIDER-SMOKE-TEST"
MODE = "review_only_network_opt_in_provider_smoke_test"
WORKFLOW_ID = "goal_data_provider02a1_network_opt_in_provider_smoke_test"
GOAL_DATA_PROVIDER02A_WORKFLOW_ID = "goal_data_provider02a_multi_provider_capability_probe"
ALLOWED_NEXT = "request_goal_data_provider02b_source_backed_panel_build_or_fix_provider02a1_warnings"
BLOCKED = "BLOCKED"

PROVIDER_DIR = "outputs/providers"
AUDIT_DIR = "outputs/audits"
CONFIG_DIR = "configs/providers"
DOC_DIR = "docs/providers"

RESULT_PATH = f"{PROVIDER_DIR}/goal_data_provider02a1_network_smoke_test_results.csv"
SCHEMA_MAPPING_PATH = f"{PROVIDER_DIR}/goal_data_provider02a1_schema_mapping_results.csv"
FAILURE_TAXONOMY_PATH = f"{PROVIDER_DIR}/goal_data_provider02a1_failure_taxonomy.csv"
REPORT_PATH = f"{AUDIT_DIR}/goal_data_provider02a1_network_smoke_test_report.md"
MANIFEST_PATH = f"{AUDIT_DIR}/goal_data_provider02a1_network_smoke_test_manifest.json"
AUDIT_PATH = f"{AUDIT_DIR}/goal_data_provider02a1_network_smoke_test_audit.md"
DOC_PATH = f"{DOC_DIR}/GOAL_DATA_PROVIDER02A1_NETWORK_OPT_IN_PROVIDER_SMOKE_TEST.md"
CONTRACT_PATH = f"{CONFIG_DIR}/goal_data_provider02a1_network_smoke_test_contract.yaml"

RESULT_FIELDS = PROBE_FIELDS + [
    "network_opt_in_present",
    "tushare_opt_in_present",
    "live_access_attempted",
    "smoke_test_data_is_final_panel_evidence",
    "raw_payload_persisted",
    "provider_token_persisted",
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
    "smoke_test_data_treated_as_final_panel_evidence",
    "downstream_execution_unlocked_by_this_goal",
]


def run_goal_data_provider02a1_network_smoke_test(root: Path) -> bool:
    result = evaluate_goal_data_provider02a1_network_smoke_test(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal_data_provider02a1_network_smoke_test(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal_data_provider02a1_network_smoke_test(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    result_rows = _read_csv(root / RESULT_PATH)
    mapping_rows = _read_csv(root / SCHEMA_MAPPING_PATH)
    taxonomy_rows = _read_csv(root / FAILURE_TAXONOMY_PATH)
    workflow = _workflow_rows(root)
    recheck = evaluate_goal_data_provider02a1_network_smoke_test(root)
    dc03_evidence_ready = _goal_v1_diagnostic_coverage03_valid(root)
    goal10b3_evidence_ready = _goal10b3_valid(root)
    failures: list[str] = []

    if not _report_pass_or_warn(report, "GOAL-DATA-PROVIDER-02A.1 Network Opt-In Provider Smoke Test Gate:"):
        failures.append("provider02a1_report_not_pass_or_warn")
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
    if manifest.get("result_schema") != RESULT_FIELDS:
        failures.append("manifest_result_schema_invalid")
    if manifest.get("providers_smoke_tested") != PROVIDERS:
        failures.append("manifest_provider_order_invalid")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"manifest_{key}_not_false")
    for key in [
        "review_only_network_smoke_test_generated",
        "all_required_providers_represented",
        "network_disabled_by_default_supported",
        "network_live_access_only_when_opted_in",
        "tushare_env_only_policy_enforced",
        "qstock_backtest_strategy_modules_not_used",
        "yfinance_auxiliary_not_primary",
        "local_import_fallback_recorded",
        "provider_tokens_never_persisted",
        "raw_payloads_never_persisted",
        "goal_data_provider02a1_workflow_status_after_gate_implemented",
        "goal_data_provider02b_locked_future",
        "goal_data_panel02_locked_future",
        "goal_v1_diagnostic_coverage03_locked_future",
        "goal10b3_locked_future",
        "goal10d_locked_future",
        "dashboard_daily_report_locked_future",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")

    if len(result_rows) != len(PROVIDERS):
        failures.append("provider_smoke_row_count_invalid")
    if result_rows and list(result_rows[0]) != RESULT_FIELDS:
        failures.append("provider_smoke_schema_invalid")
    if [row.get("provider_name", "") for row in result_rows] != PROVIDERS:
        failures.append("provider_smoke_provider_order_invalid")
    if not mapping_rows or list(mapping_rows[0]) != SCHEMA_MAPPING_FIELDS:
        failures.append("schema_mapping_schema_invalid")
    if not taxonomy_rows or list(taxonomy_rows[0]) != FAILURE_TAXONOMY_FIELDS:
        failures.append("failure_taxonomy_schema_invalid")
    by_provider = {row["provider_name"]: row for row in result_rows}
    if by_provider.get("tushare_pro", {}).get("token_available") == "false":
        if by_provider.get("tushare_pro", {}).get("failure_code") != "tushare_unavailable_missing_token":
            failures.append("tushare_missing_token_failure_code_invalid")
    if by_provider.get("yfinance", {}).get("provider_role") != "auxiliary_only":
        failures.append("yfinance_provider_role_invalid")
    if by_provider.get("yfinance", {}).get("source_priority_recommendation") != "auxiliary_not_primary":
        failures.append("yfinance_priority_invalid")
    if by_provider.get("qstock", {}).get("source_priority_recommendation") == "backtest_or_strategy_module_used":
        failures.append("qstock_forbidden_module_used")

    network_opt_in = manifest.get("network_opt_in_present") is True
    for row in result_rows:
        if row.get("provider_name") == "local_import":
            continue
        if row.get("live_access_attempted") == "true" and not network_opt_in:
            failures.append(f"{row['provider_name']}_live_access_without_network_opt_in")

    gate = workflow.get(WORKFLOW_ID, {})
    if gate.get("status") != "implemented_review_only":
        failures.append("provider02a1_workflow_not_implemented_review_only")
    if gate.get("implemented_in_repo") != "true":
        failures.append("provider02a1_workflow_not_marked_implemented")
    if gate.get("depends_on") != GOAL_DATA_PROVIDER02A_WORKFLOW_ID:
        failures.append("provider02a1_depends_on_invalid")
    if gate.get("allowed_next_action") != ALLOWED_NEXT:
        failures.append("provider02a1_allowed_next_invalid")
    if workflow.get(GOAL_DATA_PROVIDER02B_WORKFLOW_ID, {}).get("depends_on") != WORKFLOW_ID:
        failures.append("provider02b_dependency_not_provider02a1")

    provider02b = workflow.get(GOAL_DATA_PROVIDER02B_WORKFLOW_ID, {})
    if provider02b.get("status") not in {"locked_future", "implemented_review_only"}:
        failures.append("goal_data_provider02b_provider_selection_gate_status_invalid")
    elif provider02b.get("status") == "implemented_review_only":
        if provider02b.get("implemented_in_repo") != "true":
            failures.append("goal_data_provider02b_provider_selection_gate_implemented_marker_invalid")
    elif provider02b.get("implemented_in_repo") != "false":
        failures.append("goal_data_provider02b_provider_selection_gate_marked_implemented_while_locked")

    for workflow_id in [
        GOAL_DATA_PANEL02_WORKFLOW_ID,
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

    goal10b3 = workflow.get(GOAL10B3_WORKFLOW_ID, {})
    if goal10b3_evidence_ready:
        if goal10b3.get("status") != "implemented_review_only":
            failures.append("goal10b3_not_preserved_as_implemented_review_only")
        if goal10b3.get("implemented_in_repo") != "true":
            failures.append("goal10b3_not_marked_implemented")
        if goal10b3.get("depends_on") != GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID:
            failures.append("goal10b3_dependency_not_dc03")
    else:
        if goal10b3.get("status") != "locked_future":
            failures.append("goal10b3_not_locked_future")
        if goal10b3.get("implemented_in_repo") != "false":
            failures.append("goal10b3_marked_implemented")

    dc03 = workflow.get(GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID, {})
    if dc03_evidence_ready:
        if dc03.get("status") != "implemented_review_only":
            failures.append("goal_v1_diagnostic_coverage03_not_preserved_as_implemented_review_only")
        if dc03.get("implemented_in_repo") != "true":
            failures.append("goal_v1_diagnostic_coverage03_not_marked_implemented")
        if dc03.get("depends_on") != GOAL_DATA_PROVIDER02B_WORKFLOW_ID:
            failures.append("goal_v1_diagnostic_coverage03_dependency_not_provider02b")
    else:
        if dc03.get("status") != "locked_future":
            failures.append("goal_v1_diagnostic_coverage03_not_locked_future")
        if dc03.get("implemented_in_repo") != "false":
            failures.append("goal_v1_diagnostic_coverage03_marked_implemented")

    for path in _forbidden_outputs_present(root):
        failures.append(f"forbidden_output_path_exists:{path}")
    failures.extend(_token_leak_failures(root))

    status = PASS if not failures else BLOCKED
    write_text(
        root / AUDIT_PATH,
        "\n".join(
            [
                "# GOAL-DATA-PROVIDER-02A.1 Network Opt-In Provider Smoke Test Audit",
                "",
                f"Status: `{status}`",
                "",
                f"Provider rows checked: `{len(result_rows)}`",
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


def evaluate_goal_data_provider02a1_network_smoke_test(root: Path) -> dict[str, object]:
    approved_symbols = _approved_symbols(root)
    tested_symbols = approved_symbols[:10]
    network_on = network_enabled(False)
    warnings: list[str] = []
    failures: list[str] = []
    if len(tested_symbols) < 5:
        warnings.append("approved_universe_too_small")
    if not tested_symbols:
        failures.append("approved_universe_empty")

    rows = [
        _augment_smoke_row(_probe_tushare(tested_symbols, network_on), network_on),
        _augment_smoke_row(_probe_baostock(tested_symbols, network_on), network_on),
        _augment_smoke_row(_probe_akshare(tested_symbols, network_on), network_on),
        _augment_smoke_row(_probe_efinance(tested_symbols, network_on), network_on),
        _augment_smoke_row(_probe_qstock(tested_symbols, network_on), network_on),
        _augment_smoke_row(_probe_yfinance(tested_symbols, network_on), network_on),
        _augment_smoke_row(_probe_local_import(root, tested_symbols), network_on),
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
        "result_rows": rows,
        "schema_mapping_rows": schema_mapping,
        "failure_taxonomy_rows": failure_taxonomy,
        "manifest": manifest,
    }


def goal_data_provider02a1_valid_network_smoke_test_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    rows = _read_csv(root / RESULT_PATH)
    return (
        (
            "GOAL-DATA-PROVIDER-02A.1 Network Opt-In Provider Smoke Test Gate: PASS" in report
            or "GOAL-DATA-PROVIDER-02A.1 Network Opt-In Provider Smoke Test Gate: PASS_WITH_WARNINGS" in report
        )
        and "Status: `PASS`" in audit
        and manifest.get("mode") == MODE
        and manifest.get("all_required_providers_represented") is True
        and manifest.get("final_evaluation_panel_created") is False
        and manifest.get("provider_tokens_never_persisted") is True
        and [row.get("provider_name") for row in rows] == PROVIDERS
    )


def goal_data_provider02a1_implemented_workflow_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-DATA-PROVIDER-02A.1 Network Opt-In Provider Smoke Test",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_review_only",
        "current_repo_role": "review_only_network_opt_in_provider_smoke_test_gate",
        "implemented_in_repo": "true",
        "allowed_next_action": ALLOWED_NEXT,
        "depends_on": GOAL_DATA_PROVIDER02A_WORKFLOW_ID,
        "produces_artifacts": ";".join([RESULT_PATH, SCHEMA_MAPPING_PATH, FAILURE_TAXONOMY_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, CONTRACT_PATH, DOC_PATH]),
        "primary_docs": f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "scripts/run_goal_data_provider02a1_network_smoke_test.py;scripts/audit_goal_data_provider02a1_network_smoke_test.py",
        "primary_outputs": ";".join([RESULT_PATH, SCHEMA_MAPPING_PATH, FAILURE_TAXONOMY_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH]),
        "promotion_rule": "implemented_review_only_after_goal_data_provider02a1_pass_with_warnings",
        "notes": "Review-only network-opt-in provider smoke test; live provider access is attempted only when explicit environment opt-ins are present. No panel, diagnostics, backtest, dashboard, trading, production, broker, local-lake, factor-mining, or DQN/RL output.",
    }


def locked_goal_data_provider02b_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-DATA-PROVIDER-02B Source-Backed Evaluation Panel Build Gate",
        "stage_or_goal": "GOAL-DATA-PROVIDER-02B",
        "status": "locked_future",
        "current_repo_role": "locked_future_source_backed_evaluation_panel_build_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal_data_provider02b_source_backed_panel_build_request",
        "depends_on": WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal_data_provider02b_source_backed_panel_build_gate",
        "notes": "Future source-backed panel build remains locked until explicit GOAL-DATA-PROVIDER-02B request; GOAL-DATA-PROVIDER-02A.1 only smoke-tests opt-in provider access.",
    }


def _augment_smoke_row(row: dict[str, object], network_on: bool) -> dict[str, object]:
    provider = str(row.get("provider_name", ""))
    token_available = bool(row.get("token_available"))
    tushare_opt_in = os.environ.get("ASHARE_ALLOW_TUSHARE") == "1"
    provider_available = bool(row.get("provider_available"))
    live_access_attempted = (
        provider != "local_import"
        and bool(row.get("network_required"))
        and network_on
        and provider_available
        and (provider != "tushare_pro" or (token_available and tushare_opt_in))
    )
    row["network_opt_in_present"] = network_on
    row["tushare_opt_in_present"] = tushare_opt_in
    row["live_access_attempted"] = live_access_attempted
    row["smoke_test_data_is_final_panel_evidence"] = False
    row["raw_payload_persisted"] = False
    row["provider_token_persisted"] = False
    if live_access_attempted and provider == "baostock" and int(row.get("returned_rows") or 0) > 0:
        required_support = [
            "supports_ohlcv",
            "supports_amount",
            "supports_turnover",
            "supports_adjustment",
            "supports_trading_status",
            "supports_st_status",
            "supports_valuation",
        ]
        if not all(bool(row.get(key)) for key in required_support):
            row["probe_status"] = PASS_WITH_WARNINGS
            row["failure_code"] = "provider_schema_mismatch"
            row["failure_message"] = "Baostock returned rows but one or more required canonical support flags were missing."
            row["schema_mapping_status"] = "schema_mismatch_requires_review"
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
    live_attempted = [str(row["provider_name"]) for row in rows if row.get("live_access_attempted") is True]
    payload: dict[str, object] = {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "mode": MODE,
        "status": status,
        "warnings": warnings,
        "failures": failures,
        "provider_count": len(rows),
        "providers_smoke_tested": provider_names,
        "provider_probe_statuses": {str(row["provider_name"]): row["probe_status"] for row in rows},
        "provider_package_available": {str(row["provider_name"]): row["provider_available"] for row in rows},
        "result_schema": RESULT_FIELDS,
        "tested_symbols": tested_symbols,
        "tested_symbol_count": len(tested_symbols),
        "approved_symbols_available": len(_approved_symbols(root)),
        "approved_universe_minimum_requested": 5,
        "approved_universe_maximum_requested": 10,
        "approved_universe_too_small": len(tested_symbols) < 5,
        "approved_universe_expanded": False,
        "smoke_window_start": PROBE_START_DATE,
        "smoke_window_end": PROBE_END_DATE,
        "smoke_trading_day_window": PROBE_TRADING_DAY_WINDOW,
        "network_opt_in_present": network_on,
        "network_disabled_by_default_supported": True,
        "network_live_access_only_when_opted_in": True,
        "live_provider_access_attempted_count": len(live_attempted),
        "live_provider_access_attempted_providers": live_attempted,
        "review_only_network_smoke_test_generated": status != BLOCKED,
        "all_required_providers_represented": provider_names == PROVIDERS,
        "schema_mapping_row_count": len(schema_mapping),
        "failure_taxonomy_row_count": len(failure_taxonomy),
        "tushare_env_only_policy_enforced": True,
        "tushare_token_available": bool(os.environ.get("TUSHARE_TOKEN")),
        "tushare_token_source": "environment_only",
        "qstock_backtest_strategy_modules_not_used": True,
        "yfinance_auxiliary_not_primary": True,
        "local_import_fallback_recorded": True,
        "provider_tokens_never_persisted": True,
        "raw_payloads_never_persisted": True,
        "goal_data_provider02a1_workflow_status_after_gate": "implemented_review_only",
        "goal_data_provider02a1_workflow_status_after_gate_implemented": True,
        "goal_data_provider02b_status_after_goal_data_provider02a1": "locked_future",
        "goal_data_provider02b_locked_future": True,
        "goal_data_panel02_status_after_goal_data_provider02a1": "locked_future",
        "goal_data_panel02_locked_future": True,
        "goal_v1_diagnostic_coverage03_status_after_goal_data_provider02a1": "locked_future",
        "goal_v1_diagnostic_coverage03_locked_future": True,
        "goal10b3_status_after_goal_data_provider02a1": "locked_future",
        "goal10b3_locked_future": True,
        "goal10d_status_after_goal_data_provider02a1": "locked_future",
        "goal10d_locked_future": True,
        "dashboard_daily_report_status_after_goal_data_provider02a1": "locked_future",
        "dashboard_daily_report_locked_future": True,
        "signal_backtest_status_after_goal_data_provider02a1": "locked_future",
        "portfolio_backtest_status_after_goal_data_provider02a1": "locked_future",
        "workflow_status_before_goal_data_provider02a1": workflow.get(WORKFLOW_ID, {}).get("status", "missing"),
    }
    for key in FALSE_BOUNDARY_KEYS:
        payload[key] = False
    return payload


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / RESULT_PATH, result["result_rows"], RESULT_FIELDS)
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
        "tushare_token_source": "environment_only",
        "tushare_required_opt_ins": ["ASHARE_ALLOW_NETWORK_INGESTION=1", "ASHARE_ALLOW_TUSHARE=1", "TUSHARE_TOKEN"],
        "approved_universe_source": "configs/universe/approved_symbols.csv",
        "smoke_window": {"start": PROBE_START_DATE, "end": PROBE_END_DATE, "trading_days": PROBE_TRADING_DAY_WINDOW},
        "providers": [
            {"provider_name": "tushare_pro", "role": "primary_candidate", "requires_token": True, "token_env": "TUSHARE_TOKEN", "allow_env": "ASHARE_ALLOW_TUSHARE"},
            {"provider_name": "baostock", "role": "primary_candidate", "required_fields": "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,isST"},
            {"provider_name": "akshare", "role": "primary_candidate", "tests": ["stock_zh_a_hist", "index_zh_a_hist"]},
            {"provider_name": "efinance", "role": "primary_candidate", "tests": ["stock.get_quote_history"]},
            {"provider_name": "qstock", "role": "optional_data_candidate", "forbidden_modules": ["backtest", "strategy"]},
            {"provider_name": "yfinance", "role": "auxiliary_only", "source_priority": "auxiliary_not_primary"},
            {"provider_name": "local_import", "role": "fallback"},
        ],
        "allowed_outputs": [RESULT_PATH, SCHEMA_MAPPING_PATH, FAILURE_TAXONOMY_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH, CONTRACT_PATH],
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
    rows = result["result_rows"]
    provider_lines = [
        f"- `{row['provider_name']}`: status `{row['probe_status']}`, live access attempted `{str(row['live_access_attempted']).lower()}`, failure `{row['failure_code'] or 'none'}`, returned rows `{row['returned_rows']}`."
        for row in rows
    ]
    write_text(
        root / REPORT_PATH,
        "\n".join(
            [
                "# GOAL-DATA-PROVIDER-02A.1 Network Opt-In Provider Smoke Test Report",
                "",
                f"GOAL-DATA-PROVIDER-02A.1 Network Opt-In Provider Smoke Test Gate: {result['status']}",
                "",
                f"Mode: `{MODE}`",
                f"Network opt-in present: `{str(manifest['network_opt_in_present']).lower()}`",
                f"Live provider access attempted count: `{manifest['live_provider_access_attempted_count']}`",
                f"Approved symbols tested: `{';'.join(manifest['tested_symbols'])}`",
                f"Smoke window: `{PROBE_START_DATE}` to `{PROBE_END_DATE}` over `{PROBE_TRADING_DAY_WINDOW}` trading-day contract.",
                "",
                "## Provider Results",
                *provider_lines,
                "",
                "## Boundary",
                "- This gate creates provider smoke-test metadata only.",
                "- Live provider access is attempted only when explicit environment opt-ins are present.",
                "- Tushare Pro reads `TUSHARE_TOKEN` only from the environment and never persists it.",
                "- No raw provider payloads are persisted.",
                "- Smoke-test data is not final evaluation panel evidence.",
                "- GOAL-DATA-PROVIDER-02B, GOAL-V1-DIAGNOSTIC-COVERAGE-03, and GOAL-10B.3 are implemented only by their own explicit review-only gates when valid evidence exists; GOAL-DATA-PANEL-02, GOAL-10D, dashboards, trading, production, broker, local-lake, factor-mining, and DQN/RL remain locked.",
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
                "# GOAL-DATA-PROVIDER-02A.1 Network Opt-In Provider Smoke Test",
                "",
                "GOAL-DATA-PROVIDER-02A.1 is a review-only network-opt-in provider smoke test. It may attempt live provider access only when `ASHARE_ALLOW_NETWORK_INGESTION=1` is present. Tushare Pro additionally requires `ASHARE_ALLOW_TUSHARE=1` and `TUSHARE_TOKEN` from the environment.",
                "",
                "The gate records provider status, schema mapping status, failure taxonomy, live-access attempt flags, and row/date counts. It does not persist raw provider payloads, provider tokens, final evaluation panel rows, diagnostics, backtests, dashboards, trading, production, broker, local-lake, factor-mining, or DQN/RL outputs.",
                "",
                "## Outputs",
                "",
                f"- `{RESULT_PATH}`",
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
                f"- Providers represented: `{len(result['result_rows'])}`",
                f"- Network opt-in present: `{str(result['manifest']['network_opt_in_present']).lower()}`",
                f"- Live provider access attempted count: `{result['manifest']['live_provider_access_attempted_count']}`",
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
    _upsert_workflow_row(rows, by_id, WORKFLOW_ID, goal_data_provider02a1_implemented_workflow_patch(), after=GOAL_DATA_PROVIDER02A_WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL_DATA_PROVIDER02B_WORKFLOW_ID, locked_goal_data_provider02b_patch(), after=WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL_DATA_PANEL02_WORKFLOW_ID, locked_goal_data_panel02_after_goal_data_provider02a_patch(), after=GOAL_DATA_PROVIDER02B_WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID, locked_goal_v1_diagnostic_coverage03_after_goal_data_provider02a_patch(), after=GOAL_DATA_PANEL02_WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL10B3_WORKFLOW_ID, locked_goal10b3_after_goal_data_provider02a_patch(), after=GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID)
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
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_data_provider02a1"
    if "dqn_rl_mainline" in by_id:
        by_id["dqn_rl_mainline"]["status"] = "deleted_from_active_mainline"
        by_id["dqn_rl_mainline"]["implemented_in_repo"] = "false"
    if "v2_factor_research_upgrade" in by_id:
        by_id["v2_factor_research_upgrade"]["status"] = "planned_locked"
        by_id["v2_factor_research_upgrade"]["implemented_in_repo"] = "false"
    preserve_later_review_only_workflow_states(root, by_id)
    if result["status"] != BLOCKED:
        by_id[WORKFLOW_ID].update(goal_data_provider02a1_implemented_workflow_patch())
        by_id[GOAL_DATA_PROVIDER02B_WORKFLOW_ID].update(locked_goal_data_provider02b_patch())
        by_id[GOAL_DATA_PANEL02_WORKFLOW_ID].update(locked_goal_data_panel02_after_goal_data_provider02a_patch())
        by_id[GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID].update(locked_goal_v1_diagnostic_coverage03_after_goal_data_provider02a_patch())
        by_id[GOAL10B3_WORKFLOW_ID].update(locked_goal10b3_after_goal_data_provider02a_patch())
        if "dashboard_daily_report" in by_id:
            by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_data_provider02a1"
        preserve_later_review_only_workflow_states(root, by_id)
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
        preserve_later_review_only_capabilities(root, payload)
    write_json(path, payload)


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


def _provider_warnings(rows: list[dict[str, object]]) -> list[str]:
    return [f"{row['provider_name']}:{row['failure_code'] or row['probe_status']}" for row in rows if row["probe_status"] != PASS]


def _token_leak_failures(root: Path) -> list[str]:
    token = os.environ.get("TUSHARE_TOKEN", "")
    if not token:
        return []
    failures = []
    for path in [RESULT_PATH, SCHEMA_MAPPING_PATH, FAILURE_TAXONOMY_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH, CONTRACT_PATH]:
        full_path = root / path
        if full_path.exists() and token in full_path.read_text(encoding="utf-8"):
            failures.append(f"provider_token_leaked:{path}")
    return failures


def _goal_v1_diagnostic_coverage03_valid(root: Path) -> bool:
    try:
        from ashare_premarket.diagnostics.goal_v1_diagnostic_coverage03 import (
            goal_v1_diagnostic_coverage03_valid_source_backed_diagnostics_evidence,
        )

        return goal_v1_diagnostic_coverage03_valid_source_backed_diagnostics_evidence(root)
    except Exception:
        return False


def _goal10b3_valid(root: Path) -> bool:
    try:
        from ashare_premarket.backtest.goal10b3 import goal10b3_valid_dc03_revalidation_evidence

        return goal10b3_valid_dc03_revalidation_evidence(root)
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

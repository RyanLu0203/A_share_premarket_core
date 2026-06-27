from __future__ import annotations

from collections import Counter
from pathlib import Path

from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import (
    preserve_later_review_only_capabilities,
    preserve_later_review_only_workflow_states,
)
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.providers.goal_data_provider02b import PANEL_FIELDS, PANEL_PATH as PROVIDER02B_PANEL_PATH
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-V1-DIAGNOSTIC-COVERAGE-03"
GOAL_NAME = "GOAL-V1-DIAGNOSTIC-COVERAGE-03-SOURCE-BACKED-MULTI-SYMBOL-DIAGNOSTICS-GATE"
MODE = "review_only_source_backed_multi_symbol_diagnostics_gate"
WORKFLOW_ID = "goal_v1_diagnostic_coverage03_multi_provider_diagnostics"
GOAL_DATA_PROVIDER02B_WORKFLOW_ID = "goal_data_provider02b_provider_selection_gate"
GOAL_DATA_PANEL02_WORKFLOW_ID = "goal_data_panel02_evaluation_panel_gate"
GOAL10B3_WORKFLOW_ID = "goal10b3_recommendation_backtest_revalidation"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
ALLOWED_NEXT = "request_goal10b3_recommendation_revalidation_or_fix_dc03_tiering_warnings"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

DIAGNOSTICS_DIR = "outputs/diagnostics"
AUDIT_DIR = "outputs/audits"
CONFIG_DIR = "configs/diagnostics"
DOC_DIR = "docs/diagnostics"

RISK_DIAGNOSTICS_PATH = f"{DIAGNOSTICS_DIR}/goal_v1_diagnostic_coverage03_risk_diagnostics.csv"
RECOMMENDATION_DIAGNOSTICS_PATH = f"{DIAGNOSTICS_DIR}/goal_v1_diagnostic_coverage03_recommendation_diagnostics.csv"
POSITION_DIAGNOSTICS_PATH = f"{DIAGNOSTICS_DIR}/goal_v1_diagnostic_coverage03_position_band_diagnostics.csv"
DISTRIBUTION_SUMMARY_PATH = f"{DIAGNOSTICS_DIR}/goal_v1_diagnostic_coverage03_distribution_summary.csv"
REPORT_PATH = f"{AUDIT_DIR}/goal_v1_diagnostic_coverage03_source_backed_diagnostics_report.md"
MANIFEST_PATH = f"{AUDIT_DIR}/goal_v1_diagnostic_coverage03_source_backed_diagnostics_manifest.json"
AUDIT_PATH = f"{AUDIT_DIR}/goal_v1_diagnostic_coverage03_source_backed_diagnostics_audit.md"
DOC_PATH = f"{DOC_DIR}/GOAL_V1_DIAGNOSTIC_COVERAGE03_SOURCE_BACKED_MULTI_SYMBOL_DIAGNOSTICS_GATE.md"
CONTRACT_PATH = f"{CONFIG_DIR}/goal_v1_diagnostic_coverage03_contract.yaml"

TARGET_ROWS = 6000
TARGET_SYMBOLS = 50
TARGET_TRADE_DATES = 120
SOURCE_PANEL = PROVIDER02B_PANEL_PATH
READY_PANEL_STATUS = "source_backed_evaluation_panel_ready_for_dc03"
NON_ACTIONABLE = "diagnostic_only_not_investment_advice_not_trade_instruction"

RISK_FIELDS = [
    "trade_date",
    "symbol",
    "source_panel",
    "risk_severity",
    "risk_state",
    "source_risk_tag",
    "triggered_rule_ids",
    "risk_warning_codes",
    "provider_concentration_disclosure",
    "source_provider",
    "panel_contract_status",
    "diagnostic_mode",
    "non_actionable_disclaimer",
]

RECOMMENDATION_FIELDS = [
    "trade_date",
    "symbol",
    "source_panel",
    "recommendation_eligibility_status",
    "actionability_status",
    "actionability_blocked",
    "blocked_reason_codes",
    "warning_propagation_codes",
    "source_risk_severity",
    "diagnostic_mode",
    "non_actionable_disclaimer",
]

POSITION_FIELDS = [
    "trade_date",
    "symbol",
    "source_panel",
    "position_band_status",
    "position_band_review_label",
    "position_band_blocked",
    "position_band_reason_codes",
    "source_recommendation_eligibility_status",
    "source_risk_severity",
    "diagnostic_mode",
    "non_actionable_disclaimer",
]

DISTRIBUTION_FIELDS = [
    "diagnostic_area",
    "metric",
    "metric_value",
    "row_count",
    "share",
    "status",
    "notes",
]

FALSE_BOUNDARY_KEYS = [
    "canonical_goal07b_rows_created",
    "canonical_goal07b_rows_overwritten",
    "canonical_goal08b_rows_created",
    "canonical_goal08b_rows_overwritten",
    "canonical_goal09_rows_created",
    "canonical_goal09_rows_overwritten",
    "goal10b3_run",
    "goal10c_run",
    "buy_sell_hold_outputs_generated",
    "target_prices_generated",
    "actual_position_sizes_generated",
    "position_sizing_generated",
    "target_weights_generated",
    "portfolio_weights_generated",
    "order_quantities_generated",
    "portfolio_returns_generated",
    "equity_curves_generated",
    "dashboard_outputs_generated",
    "dashboard_files_generated",
    "html_generated",
    "streamlit_generated",
    "frontend_code_generated",
    "visual_reports_generated",
    "trading_outputs_generated",
    "broker_outputs_generated",
    "production_outputs_generated",
    "local_lake_files_created",
    "factor_mining_outputs_created",
    "dqn_rl_outputs_created",
    "new_provider_data_fetched",
    "demo_fixture_used_as_primary_evidence",
    "diagnostic_group_variation_fabricated",
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


def run_goal_v1_diagnostic_coverage03_source_backed_diagnostics_gate(root: Path) -> bool:
    result = evaluate_goal_v1_diagnostic_coverage03_source_backed_diagnostics_gate(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal_v1_diagnostic_coverage03_source_backed_diagnostics_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal_v1_diagnostic_coverage03_source_backed_diagnostics_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    risk_rows = _read_csv(root / RISK_DIAGNOSTICS_PATH)
    recommendation_rows = _read_csv(root / RECOMMENDATION_DIAGNOSTICS_PATH)
    position_rows = _read_csv(root / POSITION_DIAGNOSTICS_PATH)
    distribution_rows = _read_csv(root / DISTRIBUTION_SUMMARY_PATH)
    workflow = _workflow_rows(root)
    goal10b3_evidence_ready = _goal10b3_valid(root)
    failures: list[str] = []

    if not _report_pass_or_warn(report):
        failures.append("dc03_report_not_pass_or_warn")
    if manifest.get("goal") != GOAL_NAME:
        failures.append("manifest_goal_invalid")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_invalid")
    if manifest.get("status") not in {PASS, PASS_WITH_WARNINGS}:
        failures.append("manifest_status_invalid")
    if manifest.get("primary_input_artifact") != SOURCE_PANEL:
        failures.append("manifest_primary_input_invalid")
    if manifest.get("input_artifacts") != [SOURCE_PANEL]:
        failures.append("manifest_input_artifacts_not_panel_only")

    _validate_rows("risk", risk_rows, RISK_FIELDS, failures)
    _validate_rows("recommendation", recommendation_rows, RECOMMENDATION_FIELDS, failures)
    _validate_rows("position", position_rows, POSITION_FIELDS, failures)
    _validate_rows("distribution", distribution_rows, DISTRIBUTION_FIELDS, failures)

    metrics = _metrics(risk_rows)
    if metrics["row_count"] < TARGET_ROWS:
        failures.append("risk_row_count_below_minimum")
    if len(recommendation_rows) < TARGET_ROWS:
        failures.append("recommendation_row_count_below_minimum")
    if len(position_rows) < TARGET_ROWS:
        failures.append("position_row_count_below_minimum")
    if metrics["unique_symbols"] < TARGET_SYMBOLS:
        failures.append("unique_symbols_below_minimum")
    if metrics["unique_trade_dates"] < TARGET_TRADE_DATES:
        failures.append("unique_trade_dates_below_minimum")
    if metrics["duplicate_keys"] != 0:
        failures.append("risk_duplicate_keys_present")
    if _keys(risk_rows) != _keys(recommendation_rows) or _keys(risk_rows) != _keys(position_rows):
        failures.append("diagnostic_family_keys_do_not_match")
    if any(row.get("actionability_status") != "never_actionable" for row in recommendation_rows):
        failures.append("recommendation_actionability_not_never_actionable")
    if any(row.get("actionability_blocked") != "true" for row in recommendation_rows):
        failures.append("recommendation_actionability_not_blocked")
    if any(row.get("position_band_blocked") != "true" for row in position_rows):
        failures.append("position_band_not_blocked")

    for key in [
        "source_panel_used",
        "risk_diagnostics_rows_generated",
        "recommendation_diagnostics_rows_generated",
        "position_band_diagnostics_rows_generated",
        "keys_match_across_diagnostic_families",
        "canonical_goal07b_goal08b_goal09_preserved",
        "goal10b3_locked_future",
        "goal10d_locked_future",
        "dashboard_daily_report_locked_future",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"manifest_{key}_not_false")

    gate = workflow.get(WORKFLOW_ID, {})
    if gate.get("status") != "implemented_review_only":
        failures.append("dc03_workflow_not_implemented_review_only")
    if gate.get("implemented_in_repo") != "true":
        failures.append("dc03_workflow_not_marked_implemented")
    if gate.get("depends_on") != GOAL_DATA_PROVIDER02B_WORKFLOW_ID:
        failures.append("dc03_depends_on_invalid")
    if gate.get("allowed_next_action") != ALLOWED_NEXT:
        failures.append("dc03_allowed_next_invalid")
    for workflow_id in [
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
    else:
        if goal10b3.get("status") != "locked_future":
            failures.append("goal10b3_not_locked_future")
        if goal10b3.get("implemented_in_repo") != "false":
            failures.append("goal10b3_marked_implemented")
    if workflow.get(GOAL10B3_WORKFLOW_ID, {}).get("depends_on") != WORKFLOW_ID:
        failures.append("goal10b3_dependency_not_dc03")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))

    status = PASS if not failures else BLOCKED
    write_text(
        root / AUDIT_PATH,
        "\n".join(
            [
                "# GOAL-V1-DIAGNOSTIC-COVERAGE-03 Source-Backed Diagnostics Audit",
                "",
                f"Status: `{status}`",
                "",
                f"Risk rows: `{len(risk_rows)}`",
                f"Recommendation rows: `{len(recommendation_rows)}`",
                f"Position-band rows: `{len(position_rows)}`",
                f"Unique symbols: `{metrics['unique_symbols']}`",
                f"Unique trade dates: `{metrics['unique_trade_dates']}`",
                f"Duplicate keys: `{metrics['duplicate_keys']}`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == PASS


def evaluate_goal_v1_diagnostic_coverage03_source_backed_diagnostics_gate(root: Path) -> dict[str, object]:
    panel_rows = _read_csv(root / SOURCE_PANEL)
    failures: list[str] = []
    warnings: list[str] = []

    if not panel_rows:
        failures.append("provider02b_panel_missing_or_empty")
    elif list(panel_rows[0]) != PANEL_FIELDS:
        failures.append("provider02b_panel_schema_invalid")
    if "outputs/samples/" in SOURCE_PANEL:
        failures.append("invalid_primary_input_samples_path")
    if any("demo" in " ".join(row.values()).lower() or "fixture" in " ".join(row.values()).lower() for row in panel_rows):
        failures.append("demo_fixture_marker_present_in_provider02b_panel")

    metrics = _metrics(panel_rows)
    if metrics["row_count"] < TARGET_ROWS:
        failures.append("provider02b_panel_row_count_below_6000")
    if metrics["unique_symbols"] < TARGET_SYMBOLS:
        failures.append("provider02b_panel_unique_symbols_below_50")
    if metrics["unique_trade_dates"] < TARGET_TRADE_DATES:
        failures.append("provider02b_panel_unique_trade_dates_below_120")
    if metrics["duplicate_keys"] != 0:
        failures.append("provider02b_panel_duplicate_trade_date_symbol_keys")
    if any(row.get("panel_contract_status") != READY_PANEL_STATUS for row in panel_rows):
        failures.append("provider02b_panel_not_ready_for_dc03")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))

    risk_rows = _risk_rows(panel_rows) if not failures else []
    recommendation_rows = _recommendation_rows(risk_rows) if not failures else []
    position_rows = _position_rows(recommendation_rows) if not failures else []
    distribution_rows, distribution = _distribution_rows(risk_rows, recommendation_rows, position_rows)
    warnings.extend(_distribution_warnings(distribution))
    status = BLOCKED if failures else PASS_WITH_WARNINGS if warnings else PASS
    manifest = _manifest(status, failures, warnings, risk_rows, recommendation_rows, position_rows, distribution_rows, distribution)
    return {
        "status": status,
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "risk_rows": risk_rows,
        "recommendation_rows": recommendation_rows,
        "position_rows": position_rows,
        "distribution_rows": distribution_rows,
        "manifest": manifest,
    }


def goal_v1_diagnostic_coverage03_valid_source_backed_diagnostics_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        _report_pass_or_warn(report)
        and "Status: `PASS`" in audit
        and manifest.get("goal") == GOAL_NAME
        and manifest.get("mode") == MODE
        and manifest.get("primary_input_artifact") == SOURCE_PANEL
        and int(manifest.get("risk_diagnostic_row_count", 0) or 0) >= TARGET_ROWS
        and int(manifest.get("recommendation_diagnostic_row_count", 0) or 0) >= TARGET_ROWS
        and int(manifest.get("position_band_diagnostic_row_count", 0) or 0) >= TARGET_ROWS
        and int(manifest.get("unique_symbols", 0) or 0) >= TARGET_SYMBOLS
        and int(manifest.get("unique_trade_dates", 0) or 0) >= TARGET_TRADE_DATES
        and manifest.get("keys_match_across_diagnostic_families") is True
        and manifest.get("canonical_goal07b_goal08b_goal09_preserved") is True
        and manifest.get("goal10b3_run") is False
        and manifest.get("portfolio_returns_generated") is False
        and manifest.get("dashboard_outputs_generated") is False
    )


def goal_v1_diagnostic_coverage03_implemented_workflow_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-V1-DIAGNOSTIC-COVERAGE-03 Source-Backed Multi-Symbol Diagnostics",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_review_only",
        "current_repo_role": "review_only_source_backed_multi_symbol_diagnostics_gate",
        "implemented_in_repo": "true",
        "allowed_next_action": ALLOWED_NEXT,
        "depends_on": GOAL_DATA_PROVIDER02B_WORKFLOW_ID,
        "produces_artifacts": ";".join([RISK_DIAGNOSTICS_PATH, RECOMMENDATION_DIAGNOSTICS_PATH, POSITION_DIAGNOSTICS_PATH, DISTRIBUTION_SUMMARY_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH, CONTRACT_PATH]),
        "primary_docs": f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "scripts/run_goal_v1_diagnostic_coverage03_source_backed_diagnostics_gate.py;scripts/audit_goal_v1_diagnostic_coverage03_source_backed_diagnostics_gate.py",
        "primary_outputs": ";".join([RISK_DIAGNOSTICS_PATH, RECOMMENDATION_DIAGNOSTICS_PATH, POSITION_DIAGNOSTICS_PATH, DISTRIBUTION_SUMMARY_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH]),
        "promotion_rule": "implemented_review_only_after_goal_v1_diagnostic_coverage03_source_backed_diagnostics_pass_with_warnings",
        "notes": "Review-only diagnostics from the GOAL-DATA-PROVIDER-02B normalized panel. Creates separate non-actionable risk, recommendation eligibility, and position-band diagnostic coverage rows; no canonical GOAL-07B/08B/09 overwrite, backtest, dashboard, trading, production, broker, local-lake, factor-mining, or DQN/RL output.",
    }


def locked_goal10b3_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-10B.3 Recommendation Backtest Revalidation",
        "stage_or_goal": "GOAL-10B.3",
        "status": "locked_future",
        "current_repo_role": "locked_future_recommendation_revalidation",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10b3_request",
        "depends_on": WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal10b3_revalidation_gate",
        "notes": "GOAL-10B.3 is not implemented by DC03 itself; this DC03 gate creates only non-actionable diagnostic coverage rows and does not run recommendation revalidation.",
    }


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / RISK_DIAGNOSTICS_PATH, result["risk_rows"], RISK_FIELDS)
    write_csv(root / RECOMMENDATION_DIAGNOSTICS_PATH, result["recommendation_rows"], RECOMMENDATION_FIELDS)
    write_csv(root / POSITION_DIAGNOSTICS_PATH, result["position_rows"], POSITION_FIELDS)
    write_csv(root / DISTRIBUTION_SUMMARY_PATH, result["distribution_rows"], DISTRIBUTION_FIELDS)
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_contract(root)
    _write_report(root, result)
    _write_doc(root, result)


def _write_contract(root: Path) -> None:
    payload = {
        "goal": GOAL_NAME,
        "mode": MODE,
        "review_only": True,
        "primary_input_artifact": SOURCE_PANEL,
        "forbidden_primary_inputs": [
            "outputs/samples/*",
            "contract_demo_fixture",
            "GOAL-V1-DIAGNOSTIC-COVERAGE-02 evidence",
            "canonical GOAL-08B/GOAL-09 one-symbol diagnostics",
        ],
        "diagnostic_grain": ["trade_date", "symbol"],
        "minimum_coverage": {"rows_per_family": TARGET_ROWS, "unique_symbols": TARGET_SYMBOLS, "unique_trade_dates": TARGET_TRADE_DATES},
        "risk_schema": RISK_FIELDS,
        "recommendation_schema": RECOMMENDATION_FIELDS,
        "position_band_schema": POSITION_FIELDS,
        "distribution_schema": DISTRIBUTION_FIELDS,
        "allowed_outputs": [RISK_DIAGNOSTICS_PATH, RECOMMENDATION_DIAGNOSTICS_PATH, POSITION_DIAGNOSTICS_PATH, DISTRIBUTION_SUMMARY_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH, CONTRACT_PATH],
        "forbidden_outputs": FALSE_BOUNDARY_KEYS,
        "downstream_locks": {
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
                "# GOAL-V1-DIAGNOSTIC-COVERAGE-03 Source-Backed Multi-Symbol Diagnostics Gate",
                "",
                f"GOAL-V1-DIAGNOSTIC-COVERAGE-03 Source-Backed Multi-Symbol Diagnostics Gate: {result['status']}",
                f"Mode: `{MODE}`",
                f"Primary input: `{SOURCE_PANEL}`",
                "",
                "## Coverage",
                f"- Risk diagnostic rows: `{manifest['risk_diagnostic_row_count']}`",
                f"- Recommendation diagnostic rows: `{manifest['recommendation_diagnostic_row_count']}`",
                f"- Position-band diagnostic rows: `{manifest['position_band_diagnostic_row_count']}`",
                f"- Unique symbols: `{manifest['unique_symbols']}`",
                f"- Unique trade dates: `{manifest['unique_trade_dates']}`",
                f"- Date range: `{manifest['date_min']}` to `{manifest['date_max']}`",
                f"- Keys match across diagnostic families: `{str(manifest['keys_match_across_diagnostic_families']).lower()}`",
                f"- Diagnostic group variation status: `{manifest['diagnostic_group_variation_status']}`",
                f"- Recommended next goal: `{manifest['recommended_next_goal']}`",
                "",
                "## Boundary",
                "- Diagnostics are derived only from the GOAL-DATA-PROVIDER-02B normalized source-backed panel.",
                "- Canonical GOAL-07B, GOAL-08B, and GOAL-09 artifacts are preserved and not overwritten.",
                "- Recommendation diagnostics are never actionable and contain no BUY/SELL/HOLD, target price, position size, weight, or order output.",
                "- GOAL-10B.3 is implemented only by its own separate review-only revalidation gate; GOAL-10C, GOAL-10D, dashboards, trading, production, broker, local-lake, factor-mining, and DQN/RL remain locked.",
                "",
                "## Warnings",
                *[f"- {warning}" for warning in result["warnings"]],
                "",
                "## Failures",
                *[f"- {failure}" for failure in result["failures"]],
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
                "# GOAL-V1-DIAGNOSTIC-COVERAGE-03 Source-Backed Multi-Symbol Diagnostics Gate",
                "",
                "GOAL-V1-DIAGNOSTIC-COVERAGE-03 is a review-only diagnostic coverage gate over the committed GOAL-DATA-PROVIDER-02B normalized evaluation panel. It creates separate risk, recommendation eligibility, and position-band diagnostic rows at `trade_date + symbol` grain.",
                "",
                f"Primary input: `{SOURCE_PANEL}`",
                "",
                "## Outputs",
                "",
                f"- `{RISK_DIAGNOSTICS_PATH}`",
                f"- `{RECOMMENDATION_DIAGNOSTICS_PATH}`",
                f"- `{POSITION_DIAGNOSTICS_PATH}`",
                f"- `{DISTRIBUTION_SUMMARY_PATH}`",
                f"- `{REPORT_PATH}`",
                f"- `{MANIFEST_PATH}`",
                f"- `{AUDIT_PATH}`",
                f"- `{CONTRACT_PATH}`",
                "",
                "## Current Coverage",
                "",
                f"- Status: `{result['status']}`",
                f"- Diagnostic rows per family: `{manifest['risk_diagnostic_row_count']}`",
                f"- Unique symbols: `{manifest['unique_symbols']}`",
                f"- Unique trade dates: `{manifest['unique_trade_dates']}`",
                f"- Diagnostic group variation status: `{manifest['diagnostic_group_variation_status']}`",
                f"- Recommended next goal: `{manifest['recommended_next_goal']}`",
                "",
                "## Locked Boundary",
                "",
                "This gate does not overwrite canonical GOAL-07B, GOAL-08B, or GOAL-09 artifacts. It does not run GOAL-10B.3 itself, GOAL-10C, or any backtest, and it creates no portfolio returns, equity curves, dashboards, trading, broker, production, local-lake, factor-mining, or DQN/RL outputs.",
                "",
            ]
        ),
    )


def _manifest(
    status: str,
    failures: list[str],
    warnings: list[str],
    risk_rows: list[dict[str, object]],
    recommendation_rows: list[dict[str, object]],
    position_rows: list[dict[str, object]],
    distribution_rows: list[dict[str, object]],
    distribution: dict[str, object],
) -> dict[str, object]:
    metrics = _metrics(risk_rows)
    variation_available = not (
        distribution["risk_tiering_collapse_detected"]
        or distribution["recommendation_tiering_collapse_detected"]
        or distribution["position_band_tiering_collapse_detected"]
    )
    recommended_next_goal = (
        "GOAL-10B.3"
        if variation_available
        else "GOAL-RISK-TIERING-01 / GOAL-REC-TIERING-01 / GOAL-POSITION-TIERING-01 before GOAL-10B.3"
    )
    dates = sorted({str(row.get("trade_date", "")) for row in risk_rows if row.get("trade_date")})
    symbols = sorted({str(row.get("symbol", "")) for row in risk_rows if row.get("symbol")})
    payload: dict[str, object] = {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "status": status,
        "mode": MODE,
        "allowed_next_action": ALLOWED_NEXT if status != BLOCKED else "repair_goal_v1_diagnostic_coverage03_blockers",
        "recommended_next_goal": recommended_next_goal,
        "primary_input_artifact": SOURCE_PANEL,
        "input_artifacts": [SOURCE_PANEL],
        "forbidden_primary_inputs_used": [],
        "risk_output_path": RISK_DIAGNOSTICS_PATH,
        "recommendation_output_path": RECOMMENDATION_DIAGNOSTICS_PATH,
        "position_output_path": POSITION_DIAGNOSTICS_PATH,
        "distribution_output_path": DISTRIBUTION_SUMMARY_PATH,
        "risk_schema": RISK_FIELDS,
        "recommendation_schema": RECOMMENDATION_FIELDS,
        "position_band_schema": POSITION_FIELDS,
        "distribution_schema": DISTRIBUTION_FIELDS,
        "risk_diagnostic_row_count": len(risk_rows),
        "recommendation_diagnostic_row_count": len(recommendation_rows),
        "position_band_diagnostic_row_count": len(position_rows),
        "distribution_summary_row_count": len(distribution_rows),
        "unique_symbols": metrics["unique_symbols"],
        "symbols": symbols,
        "unique_trade_dates": metrics["unique_trade_dates"],
        "date_min": dates[0] if dates else "",
        "date_max": dates[-1] if dates else "",
        "duplicate_trade_date_symbol_keys": metrics["duplicate_keys"],
        "source_panel_used": bool(risk_rows),
        "risk_diagnostics_rows_generated": bool(risk_rows),
        "recommendation_diagnostics_rows_generated": bool(recommendation_rows),
        "position_band_diagnostics_rows_generated": bool(position_rows),
        "keys_match_across_diagnostic_families": _keys(risk_rows) == _keys(recommendation_rows) == _keys(position_rows),
        "canonical_goal07b_goal08b_goal09_preserved": True,
        "risk_severity_distribution": distribution["risk_severity_distribution"],
        "recommendation_eligibility_status_distribution": distribution["recommendation_eligibility_status_distribution"],
        "actionability_status_distribution": distribution["actionability_status_distribution"],
        "position_band_status_distribution": distribution["position_band_status_distribution"],
        "warning_code_frequency": distribution["warning_code_frequency"],
        "blocked_reason_frequency": distribution["blocked_reason_frequency"],
        "risk_tiering_collapse_detected": distribution["risk_tiering_collapse_detected"],
        "recommendation_tiering_collapse_detected": distribution["recommendation_tiering_collapse_detected"],
        "position_band_tiering_collapse_detected": distribution["position_band_tiering_collapse_detected"],
        "single_group_collapse_detected": distribution["single_group_collapse_detected"],
        "all_high_risk_collapse_detected": distribution["all_high_risk_collapse_detected"],
        "all_blocked_recommendation_collapse_detected": distribution["all_blocked_recommendation_collapse_detected"],
        "all_zero_or_blocked_position_band_collapse_detected": distribution["all_zero_or_blocked_position_band_collapse_detected"],
        "diagnostic_group_variation_status": "diagnostic_group_variation_available" if variation_available else "diagnostic_tiering_collapse_detected",
        "goal_v1_diagnostic_coverage03_status_after_gate": "implemented_review_only" if status != BLOCKED else "locked_future",
        "goal10b3_status_after_goal_v1_diagnostic_coverage03": "locked_future",
        "goal10d_status_after_goal_v1_diagnostic_coverage03": "locked_future",
        "dashboard_daily_report_status_after_goal_v1_diagnostic_coverage03": "locked_future",
        "goal10b3_locked_future": True,
        "goal10d_locked_future": True,
        "dashboard_daily_report_locked_future": True,
        "output_artifacts": [RISK_DIAGNOSTICS_PATH, RECOMMENDATION_DIAGNOSTICS_PATH, POSITION_DIAGNOSTICS_PATH, DISTRIBUTION_SUMMARY_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH, CONTRACT_PATH],
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        **{key: False for key in FALSE_BOUNDARY_KEYS},
    }
    return payload


def _risk_rows(panel_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    provider_counts = Counter(row.get("source_provider", "") for row in panel_rows)
    provider_disclosure = _provider_concentration_disclosure(provider_counts)
    rows: list[dict[str, object]] = []
    for row in sorted(panel_rows, key=lambda item: (item.get("trade_date", ""), item.get("symbol", ""))):
        warning_codes = _warning_codes(row)
        triggered = _risk_rules(row, warning_codes)
        severity = "HIGH" if any(rule.startswith("TRADABILITY") or rule.startswith("PANEL") or rule.startswith("LABEL") for rule in triggered) else "MEDIUM" if warning_codes else "LOW"
        risk_state = "blocked_review_only_source_panel_issue" if severity == "HIGH" else "review_only_warning_propagation" if severity == "MEDIUM" else "review_only_source_panel_clear"
        rows.append(
            {
                "trade_date": row.get("trade_date", ""),
                "symbol": row.get("symbol", ""),
                "source_panel": SOURCE_PANEL,
                "risk_severity": severity,
                "risk_state": risk_state,
                "source_risk_tag": _source_risk_tag(severity, row),
                "triggered_rule_ids": ";".join(triggered),
                "risk_warning_codes": ";".join(warning_codes),
                "provider_concentration_disclosure": provider_disclosure,
                "source_provider": row.get("source_provider", ""),
                "panel_contract_status": row.get("panel_contract_status", ""),
                "diagnostic_mode": MODE,
                "non_actionable_disclaimer": NON_ACTIONABLE,
            }
        )
    return rows


def _recommendation_rows(risk_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in risk_rows:
        high = row.get("risk_severity") == "HIGH"
        status = "blocked_review_only_source_risk" if high else "eligible_for_review_only_revalidation_never_actionable"
        blocked_reasons = ["NON_ACTIONABLE_REVIEW_ONLY", "NO_BUY_SELL_HOLD_OUTPUT"]
        if high:
            blocked_reasons.append("SOURCE_RISK_HIGH")
        rows.append(
            {
                "trade_date": row.get("trade_date", ""),
                "symbol": row.get("symbol", ""),
                "source_panel": SOURCE_PANEL,
                "recommendation_eligibility_status": status,
                "actionability_status": "never_actionable",
                "actionability_blocked": True,
                "blocked_reason_codes": ";".join(blocked_reasons),
                "warning_propagation_codes": row.get("risk_warning_codes", ""),
                "source_risk_severity": row.get("risk_severity", ""),
                "diagnostic_mode": MODE,
                "non_actionable_disclaimer": NON_ACTIONABLE,
            }
        )
    return rows


def _position_rows(recommendation_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in recommendation_rows:
        high = row.get("source_risk_severity") == "HIGH"
        status = "blocked_review_only_high_risk" if high else "blocked_review_only_no_position_output"
        label = "zero_band_review_label_high_risk" if high else "zero_band_review_label_non_actionable"
        reasons = ["NON_ACTIONABLE_REVIEW_ONLY", "NO_POSITION_SIZE_OR_WEIGHT_OUTPUT"]
        if high:
            reasons.append("SOURCE_RISK_HIGH")
        rows.append(
            {
                "trade_date": row.get("trade_date", ""),
                "symbol": row.get("symbol", ""),
                "source_panel": SOURCE_PANEL,
                "position_band_status": status,
                "position_band_review_label": label,
                "position_band_blocked": True,
                "position_band_reason_codes": ";".join(reasons),
                "source_recommendation_eligibility_status": row.get("recommendation_eligibility_status", ""),
                "source_risk_severity": row.get("source_risk_severity", ""),
                "diagnostic_mode": MODE,
                "non_actionable_disclaimer": NON_ACTIONABLE,
            }
        )
    return rows


def _distribution_rows(
    risk_rows: list[dict[str, object]],
    recommendation_rows: list[dict[str, object]],
    position_rows: list[dict[str, object]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    rows.extend(_distribution_for("risk", "risk_severity", risk_rows, "risk_severity", "Risk severity distribution."))
    rows.extend(_distribution_for("risk", "risk_state", risk_rows, "risk_state", "Risk state distribution."))
    rows.extend(_distribution_for("recommendation", "recommendation_eligibility_status", recommendation_rows, "recommendation_eligibility_status", "Recommendation eligibility distribution."))
    rows.extend(_distribution_for("recommendation", "actionability_status", recommendation_rows, "actionability_status", "Actionability status distribution."))
    rows.extend(_distribution_for("position_band", "position_band_status", position_rows, "position_band_status", "Position-band status distribution."))
    rows.extend(_code_frequency_rows("risk", "warning_code_frequency", risk_rows, "risk_warning_codes"))
    rows.extend(_code_frequency_rows("recommendation", "blocked_reason_frequency", recommendation_rows, "blocked_reason_codes"))
    rows.extend(_code_frequency_rows("position_band", "blocked_reason_frequency", position_rows, "position_band_reason_codes"))
    rows.extend(_coverage_distribution_rows(risk_rows, recommendation_rows, position_rows))

    risk_distribution = dict(Counter(str(row.get("risk_severity", "")) for row in risk_rows))
    recommendation_distribution = dict(Counter(str(row.get("recommendation_eligibility_status", "")) for row in recommendation_rows))
    actionability_distribution = dict(Counter(str(row.get("actionability_status", "")) for row in recommendation_rows))
    position_distribution = dict(Counter(str(row.get("position_band_status", "")) for row in position_rows))
    warning_frequency = _counter_codes(risk_rows, "risk_warning_codes")
    blocked_frequency = _counter_codes(recommendation_rows, "blocked_reason_codes") + _counter_codes(position_rows, "position_band_reason_codes")
    collapse = {
        "risk_tiering_collapse_detected": len(risk_distribution) <= 1 or set(risk_distribution) == {"HIGH"},
        "recommendation_tiering_collapse_detected": len(recommendation_distribution) <= 1,
        "position_band_tiering_collapse_detected": len(position_distribution) <= 1,
        "single_group_collapse_detected": any(len(distribution) <= 1 for distribution in [risk_distribution, recommendation_distribution, position_distribution]),
        "all_high_risk_collapse_detected": set(risk_distribution) == {"HIGH"},
        "all_blocked_recommendation_collapse_detected": set(actionability_distribution) == {"never_actionable"},
        "all_zero_or_blocked_position_band_collapse_detected": all(str(row.get("position_band_blocked", "")).lower() == "true" for row in position_rows) if position_rows else False,
    }
    for key, value in collapse.items():
        rows.append(_summary_row("distribution_check", key, str(value).lower(), len(risk_rows), 1.0 if value else 0.0, PASS_WITH_WARNINGS if value else PASS, "Collapse detection status."))
    distribution: dict[str, object] = {
        "risk_severity_distribution": risk_distribution,
        "recommendation_eligibility_status_distribution": recommendation_distribution,
        "actionability_status_distribution": actionability_distribution,
        "position_band_status_distribution": position_distribution,
        "warning_code_frequency": dict(warning_frequency),
        "blocked_reason_frequency": dict(blocked_frequency),
        **collapse,
    }
    return rows, distribution


def _coverage_distribution_rows(
    risk_rows: list[dict[str, object]],
    recommendation_rows: list[dict[str, object]],
    position_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    output = []
    for area, rows in [("risk", risk_rows), ("recommendation", recommendation_rows), ("position_band", position_rows)]:
        metrics = _metrics(rows)
        output.append(_summary_row(area, "row_count", str(metrics["row_count"]), metrics["row_count"], 1.0, PASS if metrics["row_count"] >= TARGET_ROWS else PASS_WITH_WARNINGS, "Rows at trade_date + symbol grain."))
        output.append(_summary_row(area, "unique_symbols", str(metrics["unique_symbols"]), metrics["unique_symbols"], 1.0, PASS if metrics["unique_symbols"] >= TARGET_SYMBOLS else PASS_WITH_WARNINGS, "Symbol coverage."))
        output.append(_summary_row(area, "unique_trade_dates", str(metrics["unique_trade_dates"]), metrics["unique_trade_dates"], 1.0, PASS if metrics["unique_trade_dates"] >= TARGET_TRADE_DATES else PASS_WITH_WARNINGS, "Trade-date coverage."))
        output.append(_summary_row(area, "duplicate_trade_date_symbol_keys", str(metrics["duplicate_keys"]), metrics["duplicate_keys"], 0.0, PASS if metrics["duplicate_keys"] == 0 else BLOCKED, "Duplicate grain check."))
    key_status = _keys(risk_rows) == _keys(recommendation_rows) == _keys(position_rows)
    output.append(_summary_row("family_keys", "keys_match_across_all_three_diagnostic_families", str(key_status).lower(), len(risk_rows), 1.0 if key_status else 0.0, PASS if key_status else BLOCKED, "Required key alignment."))
    return output


def _distribution_for(area: str, metric: str, rows: list[dict[str, object]], field: str, notes: str) -> list[dict[str, object]]:
    total = len(rows)
    counts = Counter(str(row.get(field, "")) for row in rows)
    return [_summary_row(area, metric, value, count, _share(count, total), PASS, notes) for value, count in sorted(counts.items())]


def _code_frequency_rows(area: str, metric: str, rows: list[dict[str, object]], field: str) -> list[dict[str, object]]:
    total = len(rows)
    counts = _counter_codes(rows, field)
    return [_summary_row(area, metric, value, count, _share(count, total), PASS, f"{field} frequency.") for value, count in sorted(counts.items())]


def _summary_row(area: str, metric: str, value: str, count: int, share: float, status: str, notes: str) -> dict[str, object]:
    return {
        "diagnostic_area": area,
        "metric": metric,
        "metric_value": value,
        "row_count": count,
        "share": f"{share:.6f}",
        "status": status,
        "notes": notes,
    }


def _distribution_warnings(distribution: dict[str, object]) -> list[str]:
    warnings: list[str] = []
    if distribution["risk_tiering_collapse_detected"]:
        warnings.append("risk_tiering_collapse_detected")
    if distribution["recommendation_tiering_collapse_detected"]:
        warnings.append("recommendation_tiering_collapse_detected")
    if distribution["position_band_tiering_collapse_detected"]:
        warnings.append("position_band_tiering_collapse_detected")
    if distribution["all_high_risk_collapse_detected"]:
        warnings.append("all_high_risk_collapse_detected")
    if distribution["all_blocked_recommendation_collapse_detected"]:
        warnings.append("all_blocked_recommendation_collapse_detected")
    if distribution["all_zero_or_blocked_position_band_collapse_detected"]:
        warnings.append("all_zero_or_blocked_position_band_collapse_detected")
    if not any(warning.endswith("tiering_collapse_detected") for warning in warnings):
        warnings.append("diagnostic_group_variation_available")
    warnings.append("recommendation_and_position_outputs_remain_never_actionable")
    return warnings


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys()) if rows else []
    by_id = {row["workflow_id"]: row for row in rows}
    patch = goal_v1_diagnostic_coverage03_implemented_workflow_patch()
    if result["status"] == BLOCKED:
        patch.update(
            {
                "status": "locked_future",
                "current_repo_role": "review_only_source_backed_multi_symbol_diagnostics_blocked",
                "implemented_in_repo": "false",
                "allowed_next_action": "repair_goal_v1_diagnostic_coverage03_blockers",
                "produces_artifacts": "",
                "primary_scripts": "",
                "primary_outputs": "",
                "promotion_rule": "locked_until_goal_v1_diagnostic_coverage03_passes",
                "notes": "GOAL-V1-DIAGNOSTIC-COVERAGE-03 is blocked; GOAL-10B.3 must be handled only by its own explicit gate and downstream execution remains locked.",
            }
        )
    _upsert_workflow_row(rows, by_id, WORKFLOW_ID, patch, after=GOAL_DATA_PROVIDER02B_WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL10B3_WORKFLOW_ID, locked_goal10b3_patch(), after=WORKFLOW_ID)
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
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_v1_diagnostic_coverage03"
    if "dqn_rl_mainline" in by_id:
        by_id["dqn_rl_mainline"]["status"] = "deleted_from_active_mainline"
        by_id["dqn_rl_mainline"]["implemented_in_repo"] = "false"
    if "v2_factor_research_upgrade" in by_id:
        by_id["v2_factor_research_upgrade"]["status"] = "planned_locked"
        by_id["v2_factor_research_upgrade"]["implemented_in_repo"] = "false"
    preserve_later_review_only_workflow_states(root, by_id)
    if result["status"] != BLOCKED and WORKFLOW_ID in by_id:
        by_id[WORKFLOW_ID].update(goal_v1_diagnostic_coverage03_implemented_workflow_patch())
        if GOAL10B3_WORKFLOW_ID in by_id and not _goal10b3_valid(root):
            by_id[GOAL10B3_WORKFLOW_ID].update(locked_goal10b3_patch())
    write_csv(path, rows, fields)


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    if not path.exists():
        return
    payload = read_json(path)
    payload[WORKFLOW_ID] = "implemented_review_only" if result["status"] != BLOCKED else False
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
        if not _goal10b3_valid(root):
            payload[GOAL10B3_WORKFLOW_ID] = False
    write_json(path, payload)


def _goal10b3_valid(root: Path) -> bool:
    try:
        from ashare_premarket.backtest.goal10b3 import goal10b3_valid_dc03_revalidation_evidence

        return goal10b3_valid_dc03_revalidation_evidence(root)
    except Exception:
        return False


def _upsert_workflow_row(rows: list[dict[str, str]], by_id: dict[str, dict[str, str]], workflow_id: str, patch: dict[str, str], *, after: str) -> None:
    if workflow_id in by_id:
        by_id[workflow_id].update(patch)
        return
    insert_at = next((index + 1 for index, item in enumerate(rows) if item["workflow_id"] == after), len(rows))
    row = {"workflow_id": workflow_id, **patch}
    rows.insert(insert_at, row)
    by_id[workflow_id] = row


def _risk_rules(row: dict[str, str], warning_codes: list[str]) -> list[str]:
    rules: list[str] = []
    if row.get("panel_contract_status") != READY_PANEL_STATUS:
        rules.append("PANEL_CONTRACT_NOT_READY")
    if row.get("trading_status") != "trading":
        rules.append("TRADABILITY_NOT_TRADING")
    if row.get("label_ready_20d") != "true":
        rules.append("LABEL_20D_NOT_READY")
    for field in ["open", "high", "low", "close", "volume", "amount", "turnover"]:
        if not row.get(field, ""):
            rules.append(f"PANEL_FIELD_MISSING_{field.upper()}")
    if warning_codes:
        rules.append("SOURCE_WARNING_PROPAGATED")
    if row.get("source_provider") == "baostock":
        rules.append("SINGLE_PRIMARY_PROVIDER_DISCLOSURE")
    return sorted(set(rules or ["SOURCE_PANEL_ROW_REVIEWED"]))


def _warning_codes(row: dict[str, str]) -> list[str]:
    raw = [code for code in row.get("source_warning_codes", "").split(";") if code]
    if row.get("crosscheck_status", "").startswith("not_checked"):
        raw.append("crosscheck_sample_scope_limited")
    if row.get("source_provider") == "baostock":
        raw.append("single_primary_provider_baostock")
    raw.append("review_only_dc03_non_actionable")
    return sorted(set(raw))


def _source_risk_tag(severity: str, row: dict[str, str]) -> str:
    if severity == "HIGH":
        return "source_panel_high_review_risk"
    if row.get("source_warning_codes"):
        return "source_panel_warning_review_risk"
    return "source_panel_low_review_risk"


def _provider_concentration_disclosure(provider_counts: Counter[str]) -> str:
    providers = [provider for provider in provider_counts if provider]
    if len(providers) == 1:
        provider = providers[0]
        return f"single_primary_provider:{provider};rows:{provider_counts[provider]}"
    return ";".join(f"{provider}:{count}" for provider, count in sorted(provider_counts.items()))


def _metrics(rows: list[dict[str, object]]) -> dict[str, int]:
    keys = [(str(row.get("trade_date", "")), str(row.get("symbol", ""))) for row in rows]
    return {
        "row_count": len(rows),
        "unique_symbols": len({key[1] for key in keys if key[1]}),
        "unique_trade_dates": len({key[0] for key in keys if key[0]}),
        "duplicate_keys": len(keys) - len(set(keys)),
    }


def _keys(rows: list[dict[str, object]]) -> set[tuple[str, str]]:
    return {(str(row.get("trade_date", "")), str(row.get("symbol", ""))) for row in rows if row.get("trade_date") and row.get("symbol")}


def _counter_codes(rows: list[dict[str, object]], field: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in rows:
        for code in str(row.get(field, "")).split(";"):
            if code:
                counter[code] += 1
    return counter


def _share(count: int, total: int) -> float:
    return 0.0 if total == 0 else count / total


def _validate_rows(name: str, rows: list[dict[str, str]], fields: list[str], failures: list[str]) -> None:
    if not rows:
        failures.append(f"{name}_rows_missing")
    elif list(rows[0]) != fields:
        failures.append(f"{name}_fields_invalid")


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


def _report_pass_or_warn(text: str) -> bool:
    prefix = "GOAL-V1-DIAGNOSTIC-COVERAGE-03 Source-Backed Multi-Symbol Diagnostics Gate:"
    return f"{prefix} {PASS}" in text or f"{prefix} {PASS_WITH_WARNINGS}" in text

from __future__ import annotations

from pathlib import Path

from ashare_premarket.backtest.goal10b1 import goal10b1_valid_coverage_repair_evidence
from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import (
    preserve_later_review_only_capabilities,
    preserve_later_review_only_workflow_states,
)
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-DATA-LABEL-01"
GOAL_NAME = "GOAL-DATA-LABEL-01-FORWARD-RETURN-LABEL-COVERAGE-EXPANSION"
MODE = "review_only_label_coverage_expansion"
WORKFLOW_ID = "goal_data_label01_forward_return_label_coverage_expansion"
GOAL10B1_WORKFLOW_ID = "goal10b1_backtest_coverage_repair_gate"
GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID = "goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"
GOAL10B2_WORKFLOW_ID = "goal10b2_recommendation_backtest_revalidation"
GOAL10C_WORKFLOW_ID = "goal10c_backtest_cost_slippage_sensitivity_gate"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
GOAL_DATA_LABEL01_ALLOWED_NEXT = "request_goal_v1_diagnostic_coverage02_multi_symbol_expansion_or_fix_data_label_warnings"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

STOCK_OHLCV_PATH = "outputs/samples/source_backed_ohlcv_daily_sample.csv"
BENCHMARK_OHLCV_PATH = "outputs/samples/source_backed_benchmark_daily_sample.csv"
GOAL08B_DIAGNOSTICS_PATH = "outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv"
GOAL09_DIAGNOSTICS_PATH = "outputs/position/goal09_review_only_position_band_diagnostics.csv"

LABEL_SAMPLE_PATH = "outputs/labels/goal_data_label01_forward_return_label_coverage_sample.csv"
LABEL_COVERAGE_SUMMARY_PATH = "outputs/labels/goal_data_label01_forward_return_label_coverage_summary.csv"
REPORT_PATH = "outputs/audits/goal_data_label01_forward_return_label_coverage_report.md"
MANIFEST_PATH = "outputs/audits/goal_data_label01_forward_return_label_coverage_manifest.json"
AUDIT_PATH = "outputs/audits/goal_data_label01_forward_return_label_coverage_audit.md"
DOC_PATH = "docs/labels/GOAL_DATA_LABEL01_FORWARD_RETURN_LABEL_COVERAGE_EXPANSION.md"

HORIZONS = [1, 3, 5, 20]

LABEL_SAMPLE_FIELDS = [
    "trade_date",
    "symbol",
    "benchmark_symbol",
    "fwd_1d_return",
    "fwd_3d_return",
    "fwd_5d_return",
    "fwd_20d_return",
    "benchmark_fwd_1d_return",
    "benchmark_fwd_3d_return",
    "benchmark_fwd_5d_return",
    "benchmark_fwd_20d_return",
    "excess_fwd_1d_return",
    "excess_fwd_3d_return",
    "excess_fwd_5d_return",
    "excess_fwd_20d_return",
    "label_ready_1d",
    "label_ready_3d",
    "label_ready_5d",
    "label_ready_20d",
    "label_ready_all_horizons",
    "source_ohlcv_path",
    "benchmark_ohlcv_path",
    "source_provider_id",
    "source_provider_mode",
    "source_bundle_id",
    "label_contract_version",
    "label_quality_flags",
    "review_only",
    "diagnostic_join_ready",
    "non_actionable_disclaimer",
]

COVERAGE_SUMMARY_FIELDS = [
    "horizon",
    "source_rows",
    "label_ready_rows",
    "missing_forward_rows",
    "unique_symbols",
    "unique_trade_dates",
    "date_min",
    "date_max",
    "coverage_status",
]

FALSE_BOUNDARY_KEYS = [
    "new_data_fetched",
    "network_ingestion_run",
    "provider_ingestion_modified",
    "local_bundle_files_committed",
    "local_lake_files_created",
    "raw_provider_payloads_committed",
    "goal07b_rows_created",
    "goal07b_rows_overwritten",
    "goal08b_rows_created",
    "goal08b_rows_overwritten",
    "goal09_rows_created",
    "goal09_rows_overwritten",
    "recommendation_rows_generated",
    "position_rows_generated",
    "buy_sell_hold_outputs_generated",
    "target_prices_generated",
    "position_sizing_generated",
    "actual_position_sizing_generated",
    "order_quantities_generated",
    "target_weights_generated",
    "portfolio_weights_generated",
    "portfolio_returns_generated",
    "equity_curves_generated",
    "portfolio_construction_generated",
    "dashboard_outputs_generated",
    "dashboard_files_generated",
    "html_generated",
    "streamlit_generated",
    "frontend_code_generated",
    "visual_reports_generated",
    "paper_trading_enabled",
    "live_trading_enabled",
    "broker_integration_enabled",
    "production_model_behavior_created",
    "database_writes_created",
    "backtests_run",
    "backtest_execution_run",
    "backtest_performance_rows_generated",
    "signal_backtests_run",
    "portfolio_backtests_run",
    "cost_slippage_outputs_created",
    "factor_mining_outputs_created",
    "dqn_rl_outputs_created",
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
    "data/raw",
    "data/bundles",
    "data/lake",
    "data/exports",
]

WORKFLOW_PRODUCES_ARTIFACTS = ";".join(
    [
        LABEL_SAMPLE_PATH,
        LABEL_COVERAGE_SUMMARY_PATH,
        REPORT_PATH,
        MANIFEST_PATH,
        AUDIT_PATH,
        DOC_PATH,
    ]
)
WORKFLOW_PRIMARY_DOCS = f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md"
WORKFLOW_PRIMARY_SCRIPTS = "scripts/run_goal_data_label01_forward_return_label_coverage_expansion.py;scripts/audit_goal_data_label01_forward_return_label_coverage_expansion.py"
WORKFLOW_PRIMARY_OUTPUTS = ";".join(
    [
        LABEL_SAMPLE_PATH,
        LABEL_COVERAGE_SUMMARY_PATH,
        REPORT_PATH,
        MANIFEST_PATH,
        AUDIT_PATH,
    ]
)
WORKFLOW_NOTES = "Review-only forward-return label coverage expansion from existing committed OHLCV and benchmark samples. It adds 20d label horizon coverage where future bars exist, records that canonical GOAL-08B/GOAL-09 diagnostics do not overlap the expanded labels, and creates no recommendation, position, portfolio, dashboard, trading, production, broker, local-lake, factor-mining, or DQN/RL outputs."


def run_goal_data_label01_forward_return_label_coverage_expansion(root: Path) -> bool:
    result = evaluate_goal_data_label01_forward_return_label_coverage_expansion(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal_data_label01_forward_return_label_coverage_expansion(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal_data_label01_forward_return_label_coverage_expansion(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    label_rows = _read_csv(root / LABEL_SAMPLE_PATH)
    coverage_rows = _read_csv(root / LABEL_COVERAGE_SUMMARY_PATH)
    workflow = _workflow_rows(root)
    recheck = evaluate_goal_data_label01_forward_return_label_coverage_expansion(root)
    failures: list[str] = []

    if not _report_pass_or_warn(report):
        failures.append("goal_data_label01_report_not_pass_or_warn")
    if recheck["status"] == BLOCKED:
        failures.extend(f"recheck:{failure}" for failure in recheck["failures"])
    if manifest.get("goal") != GOAL_NAME:
        failures.append("manifest_goal_invalid")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_invalid")
    if manifest.get("status") not in {PASS, PASS_WITH_WARNINGS}:
        failures.append("manifest_status_invalid")
    for key in [
        "forward_return_label_coverage_expanded",
        "forward_return_20d_labels_generated",
        "used_committed_source_samples_only",
        "label_rows_generated",
        "goal_v1_diagnostic_coverage02_locked_future",
        "goal10b2_locked_future",
        "goal10c_locked_future",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"manifest_{key}_not_false")
    if manifest.get("diagnostic_join_ready") is not False:
        failures.append("manifest_diagnostic_join_ready_not_false")
    if not label_rows:
        failures.append("label_coverage_sample_missing")
    elif set(label_rows[0]) != set(LABEL_SAMPLE_FIELDS):
        failures.append("label_coverage_sample_fields_invalid")
    elif not any(row.get("label_ready_20d") == "true" for row in label_rows):
        failures.append("label_coverage_sample_missing_ready_20d_rows")
    if not coverage_rows:
        failures.append("coverage_summary_missing")
    elif set(coverage_rows[0]) != set(COVERAGE_SUMMARY_FIELDS):
        failures.append("coverage_summary_fields_invalid")
    row = workflow.get(WORKFLOW_ID, {})
    if row.get("status") != "implemented_review_only":
        failures.append("goal_data_label01_workflow_not_implemented_review_only")
    if row.get("implemented_in_repo") != "true":
        failures.append("goal_data_label01_workflow_not_marked_implemented")
    if row.get("depends_on") != GOAL10B1_WORKFLOW_ID:
        failures.append("goal_data_label01_depends_on_invalid")
    if row.get("allowed_next_action") != GOAL_DATA_LABEL01_ALLOWED_NEXT:
        failures.append("goal_data_label01_allowed_next_invalid")
    goal_v1_diagnostic_coverage02_valid = _goal_v1_diagnostic_coverage02_valid(root)
    if goal_v1_diagnostic_coverage02_valid:
        target = workflow.get(GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID, {})
        if target.get("status") != "implemented_review_only":
            failures.append(f"{GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID}_not_preserved_implemented_review_only")
        if target.get("implemented_in_repo") != "true":
            failures.append(f"{GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID}_not_marked_implemented")
        if target.get("depends_on") != WORKFLOW_ID:
            failures.append(f"{GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID}_dependency_invalid")
    else:
        target = workflow.get(GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID, {})
        if target.get("status") != "locked_future":
            failures.append(f"{GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID}_not_locked_future")
        if target.get("implemented_in_repo") != "false":
            failures.append(f"{GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID}_marked_implemented")
        if target.get("depends_on") != WORKFLOW_ID:
            failures.append(f"{GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID}_dependency_invalid")
    for workflow_id, dependency in [
        (GOAL10B2_WORKFLOW_ID, GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID),
        (GOAL10C_WORKFLOW_ID, GOAL10B2_WORKFLOW_ID),
    ]:
        target = workflow.get(workflow_id, {})
        if target.get("status") not in {"locked_future", "implemented_review_only"}:
            failures.append(f"{workflow_id}_invalid_status")
        if target.get("status") == "implemented_review_only":
            if target.get("implemented_in_repo") != "true":
                failures.append(f"{workflow_id}_not_marked_implemented")
        elif target.get("implemented_in_repo") != "false":
            failures.append(f"{workflow_id}_marked_implemented")
        if target.get("depends_on") != dependency:
            failures.append(f"{workflow_id}_dependency_invalid")
    target = workflow.get(GOAL10D_WORKFLOW_ID, {})
    if target.get("status") != "locked_future":
        failures.append(f"{GOAL10D_WORKFLOW_ID}_not_locked_future")
    if target.get("implemented_in_repo") != "false":
        failures.append(f"{GOAL10D_WORKFLOW_ID}_marked_implemented")
    if target.get("depends_on") != GOAL10C_WORKFLOW_ID:
        failures.append(f"{GOAL10D_WORKFLOW_ID}_dependency_invalid")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))

    status = PASS if not failures else BLOCKED
    write_text(
        root / AUDIT_PATH,
        "\n".join(
            [
                "# GOAL-DATA-LABEL-01 Forward-Return Label Coverage Audit",
                "",
                f"Status: `{status}`",
                "",
                f"Label rows generated: `{manifest.get('label_row_count', 0)}`",
                f"20d label-ready rows: `{manifest.get('label_ready_20d_rows', 0)}`",
                f"Diagnostic join ready: `{manifest.get('diagnostic_join_ready', False)}`",
                "Recommendation, position, portfolio, dashboard, trading, production, broker, local-lake, factor-mining, and DQN/RL outputs generated: `false`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == PASS


def evaluate_goal_data_label01_forward_return_label_coverage_expansion(root: Path) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    stock_rows = _read_csv(root / STOCK_OHLCV_PATH)
    benchmark_rows = _read_csv(root / BENCHMARK_OHLCV_PATH)
    goal08b_rows = _read_csv(root / GOAL08B_DIAGNOSTICS_PATH)
    goal09_rows = _read_csv(root / GOAL09_DIAGNOSTICS_PATH)

    if not goal10b1_valid_coverage_repair_evidence(root):
        failures.append("goal10b1_coverage_repair_evidence_not_ready")
    if not stock_rows:
        failures.append("stock_ohlcv_sample_missing_or_empty")
    if not benchmark_rows:
        failures.append("benchmark_ohlcv_sample_missing_or_empty")
    failures.extend(_validate_ohlcv_rows(stock_rows, "stock_ohlcv"))
    failures.extend(_validate_ohlcv_rows(benchmark_rows, "benchmark_ohlcv"))

    label_rows = _build_label_rows(stock_rows, benchmark_rows) if not failures else []
    coverage_rows = _coverage_summary_rows(label_rows)

    if not any(row.get("label_ready_20d") is True for row in label_rows):
        failures.append("no_ready_20d_forward_return_labels")
    if len({row.get("symbol", "") for row in label_rows if row.get("symbol", "")}) < 2:
        warnings.append("single_symbol_label_coverage_remains")
    if _diagnostic_overlap(label_rows, goal08b_rows) == 0:
        warnings.append("goal08b_diagnostics_not_aligned_to_expanded_label_dates")
    if _diagnostic_overlap(label_rows, goal09_rows) == 0:
        warnings.append("goal09_position_diagnostics_not_aligned_to_expanded_label_dates")
    if not _local_bundle_manifest_matches_committed_summary(root):
        warnings.append("local_engineering_bundle_currently_empty_or_stale")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))

    status = BLOCKED if failures else PASS_WITH_WARNINGS if warnings else PASS
    manifest = _manifest(status, failures, warnings, label_rows, coverage_rows, goal08b_rows, goal09_rows)
    return {
        "status": status,
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "label_rows": label_rows,
        "coverage_rows": coverage_rows,
        "manifest": manifest,
    }


def goal_data_label01_valid_forward_return_label_coverage_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        _report_pass_or_warn(report)
        and "Status: `PASS`" in audit
        and manifest.get("goal") == GOAL_NAME
        and manifest.get("mode") == MODE
        and manifest.get("forward_return_label_coverage_expanded") is True
        and manifest.get("forward_return_20d_labels_generated") is True
        and manifest.get("used_committed_source_samples_only") is True
        and manifest.get("diagnostic_join_ready") is False
        and manifest.get("goal_v1_diagnostic_coverage02_locked_future") is True
        and manifest.get("goal10b2_locked_future") is True
        and manifest.get("goal10c_locked_future") is True
        and manifest.get("new_data_fetched") is False
        and manifest.get("backtests_run") is False
        and manifest.get("portfolio_returns_generated") is False
        and manifest.get("dashboard_outputs_generated") is False
    )


def goal_data_label01_implemented_workflow_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-DATA-LABEL-01 Forward-Return Label Coverage Expansion",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_review_only",
        "current_repo_role": "review_only_forward_return_label_coverage_expansion_gate",
        "implemented_in_repo": "true",
        "allowed_next_action": GOAL_DATA_LABEL01_ALLOWED_NEXT,
        "depends_on": GOAL10B1_WORKFLOW_ID,
        "produces_artifacts": WORKFLOW_PRODUCES_ARTIFACTS,
        "primary_docs": WORKFLOW_PRIMARY_DOCS,
        "primary_scripts": WORKFLOW_PRIMARY_SCRIPTS,
        "primary_outputs": WORKFLOW_PRIMARY_OUTPUTS,
        "promotion_rule": "implemented_review_only_after_goal_data_label01_pass_with_warnings",
        "notes": WORKFLOW_NOTES,
    }


def locked_goal_v1_diagnostic_coverage02_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-V1-DIAGNOSTIC-COVERAGE-02 Multi-Symbol Diagnostics Expansion",
        "stage_or_goal": "GOAL-V1-DIAGNOSTIC-COVERAGE-02",
        "status": "locked_future",
        "current_repo_role": "locked_future_multi_symbol_diagnostic_coverage",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal_v1_diagnostic_coverage02_request",
        "depends_on": WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal_v1_diagnostic_coverage02_gate",
        "notes": "Future risk/recommendation/position-band multi-symbol diagnostics expansion remains locked; GOAL-DATA-LABEL-01 creates labels only.",
    }


def locked_goal10b2_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-10B.2 Recommendation Backtest Revalidation",
        "stage_or_goal": "GOAL-10B.2",
        "status": "locked_future",
        "current_repo_role": "locked_future_recommendation_backtest_revalidation",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10b2_request",
        "depends_on": GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal10b2_revalidation_gate",
        "notes": "Future recommendation backtest revalidation remains locked until diagnostics are expanded and aligned to expanded labels.",
    }


def locked_goal10c_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-10C Backtest Cost / Slippage Sensitivity",
        "stage_or_goal": "GOAL-10C",
        "status": "locked_future",
        "current_repo_role": "locked_future_backtest_sensitivity",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10c_request",
        "depends_on": GOAL10B2_WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal10c_position_band_or_sensitivity_gate",
        "notes": "Future GOAL-10C backtest work remains locked; GOAL-DATA-LABEL-01 creates no backtest rows, portfolio returns, or cost/slippage outputs.",
    }


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / LABEL_SAMPLE_PATH, result["label_rows"], LABEL_SAMPLE_FIELDS)
    write_csv(root / LABEL_COVERAGE_SUMMARY_PATH, result["coverage_rows"], COVERAGE_SUMMARY_FIELDS)
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_report(root, result)
    _write_doc(root, result)


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    write_text(
        root / REPORT_PATH,
        "\n".join(
            [
                "# GOAL-DATA-LABEL-01 Forward-Return Label Coverage Expansion",
                "",
                f"GOAL-DATA-LABEL-01 Forward-Return Label Coverage Expansion: {result['status']}",
                f"Mode: `{MODE}`",
                "",
                "## Expansion",
                f"- Source OHLCV sample: `{STOCK_OHLCV_PATH}`",
                f"- Benchmark sample: `{BENCHMARK_OHLCV_PATH}`",
                f"- Label rows generated: `{manifest['label_row_count']}`",
                f"- Symbols covered: `{manifest['label_unique_symbols']}`",
                f"- 20d label-ready rows: `{manifest['label_ready_20d_rows']}`",
                f"- Diagnostic overlap with GOAL-08B: `{manifest['goal08b_expanded_label_overlap_rows']}`",
                f"- Diagnostic overlap with GOAL-09: `{manifest['goal09_expanded_label_overlap_rows']}`",
                "",
                "## Boundary",
                "- Labels were derived only from existing committed OHLCV and benchmark samples.",
                "- GOAL-DATA-LABEL-01 does not fetch data, modify providers, commit local bundles, create local-lake files, create or overwrite GOAL-07B/08B/09 rows, run a backtest, generate performance rows, create portfolio outputs, or unlock dashboard/trading/production paths.",
                "- GOAL-V1-DIAGNOSTIC-COVERAGE-02 may only provide separate non-actionable diagnostic coverage evidence; later GOAL-10B.2/GOAL-10C gates may only preserve review-only non-actionable diagnostics, while GOAL-10D, dashboard, trading, production, broker, local-lake, factor-mining, and DQN/RL remain locked.",
                "",
                "## Next",
                "- GOAL-V1-DIAGNOSTIC-COVERAGE-02 now provides bounded multi-symbol, non-actionable diagnostic coverage from committed Stage 6C approved-symbol evidence; GOAL-10B.2 may only proceed through its explicit review-only revalidation gate and must carry the remaining 20d alignment warning.",
                "",
                "## Failures",
                *[f"- {failure}" for failure in result["failures"]],
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
                "# GOAL-DATA-LABEL-01 Forward-Return Label Coverage Expansion",
                "",
                f"Status: `{result['status']}`",
                "",
                "GOAL-DATA-LABEL-01 expands review-only forward-return label coverage from committed source-backed OHLCV and benchmark samples. It adds 1d, 3d, 5d, and 20d stock, benchmark, and excess-return labels wherever the future trading bars exist.",
                "",
                "The gate is a label coverage step only. It does not expand risk, recommendation, or position-band diagnostics and does not run a backtest.",
                "",
                "## Outputs",
                "",
                f"- `{LABEL_SAMPLE_PATH}`",
                f"- `{LABEL_COVERAGE_SUMMARY_PATH}`",
                f"- `{REPORT_PATH}`",
                f"- `{MANIFEST_PATH}`",
                f"- `{AUDIT_PATH}`",
                "",
                "## Current Coverage",
                "",
                f"- Label rows: `{manifest['label_row_count']}`",
                f"- Unique symbols: `{manifest['label_unique_symbols']}`",
                f"- Unique dates: `{manifest['label_unique_trade_dates']}`",
                f"- 20d label-ready rows: `{manifest['label_ready_20d_rows']}`",
                f"- Diagnostic join ready: `{manifest['diagnostic_join_ready']}`",
                "",
                "## Remaining Gap",
                "",
                "The current committed canonical GOAL-08B/GOAL-09 diagnostic rows do not overlap the expanded label sample by `trade_date + symbol`, and the expanded sample is still single-symbol. GOAL-V1-DIAGNOSTIC-COVERAGE-02 now provides bounded multi-symbol, non-actionable, review-only diagnostic coverage from committed Stage 6C approved-symbol evidence, but 20d multi-symbol alignment remains unavailable and must be propagated by any GOAL-10B.2 review-only revalidation.",
                "",
                "## Locked Boundary",
                "",
                "GOAL-10B.2 and GOAL-10C may only exist as explicit review-only non-actionable diagnostic gates. GOAL-10D, Dashboard / Daily Report UI, signal and portfolio backtest promotion, trading, production, broker integration, local-lake writes, factor-mining, and DQN/RL remain locked.",
                "",
            ]
        ),
    )


def _manifest(
    status: str,
    failures: list[str],
    warnings: list[str],
    label_rows: list[dict[str, object]],
    coverage_rows: list[dict[str, object]],
    goal08b_rows: list[dict[str, str]],
    goal09_rows: list[dict[str, str]],
) -> dict[str, object]:
    symbols = sorted({str(row.get("symbol", "")) for row in label_rows if row.get("symbol", "")})
    dates = sorted({str(row.get("trade_date", "")) for row in label_rows if row.get("trade_date", "")})
    label_ready_20d_rows = sum(1 for row in label_rows if row.get("label_ready_20d") is True)
    return {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "status": status,
        "mode": MODE,
        "allowed_next_action": GOAL_DATA_LABEL01_ALLOWED_NEXT if status != BLOCKED else "repair_goal_data_label01_blockers",
        "recommended_next_goal": "GOAL-V1-DIAGNOSTIC-COVERAGE-02",
        "source_ohlcv_path": STOCK_OHLCV_PATH,
        "benchmark_ohlcv_path": BENCHMARK_OHLCV_PATH,
        "label_output_path": LABEL_SAMPLE_PATH,
        "label_row_count": len(label_rows),
        "label_unique_symbols": len(symbols),
        "label_symbols": symbols,
        "label_unique_trade_dates": len(dates),
        "label_date_min": dates[0] if dates else "",
        "label_date_max": dates[-1] if dates else "",
        "label_ready_1d_rows": sum(1 for row in label_rows if row.get("label_ready_1d") is True),
        "label_ready_3d_rows": sum(1 for row in label_rows if row.get("label_ready_3d") is True),
        "label_ready_5d_rows": sum(1 for row in label_rows if row.get("label_ready_5d") is True),
        "label_ready_20d_rows": label_ready_20d_rows,
        "coverage_summary_rows": len(coverage_rows),
        "forward_return_label_coverage_expanded": status != BLOCKED,
        "forward_return_20d_labels_generated": label_ready_20d_rows > 0,
        "used_committed_source_samples_only": True,
        "local_engineering_bundle_rows_used": 0,
        "label_rows_generated": status != BLOCKED,
        "goal08b_expanded_label_overlap_rows": _diagnostic_overlap(label_rows, goal08b_rows),
        "goal09_expanded_label_overlap_rows": _diagnostic_overlap(label_rows, goal09_rows),
        "diagnostic_join_ready": False,
        "multi_symbol_label_coverage_ready": len(symbols) >= 2,
        "goal_v1_diagnostic_coverage02_status_after_goal_data_label01": "locked_future",
        "goal10b2_status_after_goal_data_label01": "locked_future",
        "goal10c_status_after_goal_data_label01": "locked_future",
        "goal10d_status_after_goal_data_label01": "locked_future",
        "dashboard_daily_report_status_after_goal_data_label01": "locked_future",
        "goal_v1_diagnostic_coverage02_locked_future": True,
        "goal10b2_locked_future": True,
        "goal10c_locked_future": True,
        "goal10d_locked_future": True,
        "dashboard_daily_report_locked_future": True,
        "input_artifacts": [STOCK_OHLCV_PATH, BENCHMARK_OHLCV_PATH, GOAL08B_DIAGNOSTICS_PATH, GOAL09_DIAGNOSTICS_PATH],
        "output_artifacts": [LABEL_SAMPLE_PATH, LABEL_COVERAGE_SUMMARY_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH, DOC_PATH],
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        **{key: False for key in FALSE_BOUNDARY_KEYS},
    }


def _build_label_rows(stock_rows: list[dict[str, str]], benchmark_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    stocks = _by_symbol_date(stock_rows, "symbol")
    benchmarks = _by_symbol_date(benchmark_rows, "benchmark_symbol")
    benchmark_symbol = sorted(benchmarks)[0] if benchmarks else ""
    benchmark_by_date = benchmarks.get(benchmark_symbol, {})
    benchmark_dates = sorted(benchmark_by_date)
    rows: list[dict[str, object]] = []
    for symbol, by_date in sorted(stocks.items()):
        dates = sorted(by_date)
        closes = {date: _float(by_date[date].get("close", "")) for date in dates}
        benchmark_closes = {date: _float(benchmark_by_date.get(date, {}).get("close", "")) for date in benchmark_dates}
        for trade_date in dates:
            stock = by_date[trade_date]
            output: dict[str, object] = {
                "trade_date": trade_date,
                "symbol": symbol,
                "benchmark_symbol": benchmark_symbol,
                "source_ohlcv_path": STOCK_OHLCV_PATH,
                "benchmark_ohlcv_path": BENCHMARK_OHLCV_PATH,
                "source_provider_id": stock.get("provider_id", stock.get("source_id", "")),
                "source_provider_mode": stock.get("provider_mode", ""),
                "source_bundle_id": stock.get("source_bundle_id", ""),
                "label_contract_version": "goal_data_label01.forward_return_label.v1",
                "review_only": True,
                "diagnostic_join_ready": False,
                "non_actionable_disclaimer": "diagnostic_label_only_not_investment_advice_not_trade_instruction",
            }
            ready_all = True
            flags: list[str] = ["SOURCE_BACKED_SAMPLE_DERIVED"]
            for horizon in HORIZONS:
                stock_return = _forward_return(dates, closes, trade_date, horizon)
                benchmark_return = _forward_return(benchmark_dates, benchmark_closes, trade_date, horizon)
                ready = stock_return != "" and benchmark_return != ""
                output[f"fwd_{horizon}d_return"] = stock_return
                output[f"benchmark_fwd_{horizon}d_return"] = benchmark_return
                output[f"excess_fwd_{horizon}d_return"] = _format_return(float(stock_return) - float(benchmark_return)) if ready else ""
                output[f"label_ready_{horizon}d"] = ready
                if not ready:
                    ready_all = False
                    flags.append(f"MISSING_{horizon}D_FORWARD_WINDOW")
            output["label_ready_all_horizons"] = ready_all
            output["label_quality_flags"] = ";".join(sorted(set(flags)))
            rows.append(output)
    return rows


def _coverage_summary_rows(label_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    dates = sorted({str(row.get("trade_date", "")) for row in label_rows if row.get("trade_date", "")})
    symbols = sorted({str(row.get("symbol", "")) for row in label_rows if row.get("symbol", "")})
    rows: list[dict[str, object]] = []
    for horizon in HORIZONS:
        ready = sum(1 for row in label_rows if row.get(f"label_ready_{horizon}d") is True)
        rows.append(
            {
                "horizon": f"{horizon}d",
                "source_rows": len(label_rows),
                "label_ready_rows": ready,
                "missing_forward_rows": max(len(label_rows) - ready, 0),
                "unique_symbols": len(symbols),
                "unique_trade_dates": len(dates),
                "date_min": dates[0] if dates else "",
                "date_max": dates[-1] if dates else "",
                "coverage_status": "ready" if ready else "missing",
            }
        )
    return rows


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys())
    by_id = {row["workflow_id"]: row for row in rows}
    patch = goal_data_label01_implemented_workflow_patch()
    if result["status"] == BLOCKED:
        patch.update(
            {
                "status": "locked_future",
                "current_repo_role": "review_only_label_coverage_expansion_blocked",
                "implemented_in_repo": "false",
                "allowed_next_action": "repair_goal_data_label01_blockers",
                "produces_artifacts": "",
                "primary_scripts": "",
                "primary_outputs": "",
                "promotion_rule": "locked_until_goal_data_label01_passes",
                "notes": "GOAL-DATA-LABEL-01 is blocked; downstream diagnostic and backtest goals remain locked.",
            }
        )
    _upsert_workflow_row(rows, by_id, WORKFLOW_ID, patch, after=GOAL10B1_WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID, locked_goal_v1_diagnostic_coverage02_patch(), after=WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL10B2_WORKFLOW_ID, locked_goal10b2_patch(), after=GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL10C_WORKFLOW_ID, locked_goal10c_patch(), after=GOAL10B2_WORKFLOW_ID)
    if _goal_v1_diagnostic_coverage02_valid(root):
        from ashare_premarket.diagnostics.goal_v1_diagnostic_coverage02 import (
            goal_v1_diagnostic_coverage02_implemented_workflow_patch,
            locked_goal10b2_patch as diagnostic_coverage02_locked_goal10b2_patch,
            locked_goal10c_patch as diagnostic_coverage02_locked_goal10c_patch,
        )

        by_id[GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID].update(goal_v1_diagnostic_coverage02_implemented_workflow_patch())
        by_id[GOAL10B2_WORKFLOW_ID].update(diagnostic_coverage02_locked_goal10b2_patch())
        by_id[GOAL10C_WORKFLOW_ID].update(diagnostic_coverage02_locked_goal10c_patch())
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
    if GOAL10D_WORKFLOW_ID in by_id:
        by_id[GOAL10D_WORKFLOW_ID]["depends_on"] = GOAL10C_WORKFLOW_ID
    if "dashboard_daily_report" in by_id:
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_data_label01"
    if "dqn_rl_mainline" in by_id:
        by_id["dqn_rl_mainline"]["status"] = "deleted_from_active_mainline"
        by_id["dqn_rl_mainline"]["implemented_in_repo"] = "false"
    if "v2_factor_research_upgrade" in by_id:
        by_id["v2_factor_research_upgrade"]["status"] = "planned_locked"
        by_id["v2_factor_research_upgrade"]["implemented_in_repo"] = "false"
    preserve_later_review_only_workflow_states(root, by_id)
    write_csv(path, rows, fields)


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


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    if not path.exists():
        return
    payload = read_json(path)
    payload[WORKFLOW_ID] = "implemented_review_only" if result["status"] != BLOCKED else False
    payload[GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID] = False
    payload[GOAL10B2_WORKFLOW_ID] = False
    payload[GOAL10C_WORKFLOW_ID] = False
    payload[GOAL10D_WORKFLOW_ID] = False
    if _goal_v1_diagnostic_coverage02_valid(root):
        payload[GOAL_V1_DIAGNOSTIC_COVERAGE02_WORKFLOW_ID] = "implemented_review_only"
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
    write_json(path, payload)


def _validate_ohlcv_rows(rows: list[dict[str, str]], role: str) -> list[str]:
    failures: list[str] = []
    required = {"trade_date", "close"}
    if role == "stock_ohlcv":
        required.add("symbol")
    else:
        required.add("benchmark_symbol")
    if rows and not required.issubset(rows[0]):
        missing = sorted(required - set(rows[0]))
        failures.append(f"{role}_missing_fields:{';'.join(missing)}")
    keys = []
    for row in rows:
        symbol = row.get("symbol", row.get("benchmark_symbol", ""))
        key = (row.get("trade_date", ""), symbol)
        if not key[0] or not key[1]:
            failures.append(f"{role}_missing_trade_date_or_symbol")
        if not _is_float(row.get("close", "")):
            failures.append(f"{role}_invalid_close")
        keys.append(key)
    if len(keys) != len(set(keys)):
        failures.append(f"{role}_duplicate_trade_date_symbol")
    return sorted(set(failures))


def _by_symbol_date(rows: list[dict[str, str]], symbol_field: str) -> dict[str, dict[str, dict[str, str]]]:
    output: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        symbol = row.get(symbol_field, "")
        trade_date = row.get("trade_date", "")
        if symbol and trade_date:
            output.setdefault(symbol, {})[trade_date] = row
    return output


def _forward_return(dates: list[str], closes: dict[str, float], trade_date: str, horizon: int) -> str:
    if trade_date not in closes:
        return ""
    try:
        start = dates.index(trade_date)
    except ValueError:
        return ""
    end = start + horizon
    if end >= len(dates):
        return ""
    start_close = closes.get(dates[start])
    end_close = closes.get(dates[end])
    if start_close in {None, 0.0} or end_close is None:
        return ""
    return _format_return((end_close / start_close) - 1.0)


def _diagnostic_overlap(label_rows: list[dict[str, object]], diagnostic_rows: list[dict[str, str]]) -> int:
    keys = {(str(row.get("trade_date", "")), str(row.get("symbol", ""))) for row in label_rows if row.get("trade_date") and row.get("symbol")}
    return sum(1 for row in diagnostic_rows if (row.get("trade_date", ""), row.get("symbol", "")) in keys)


def _local_bundle_manifest_matches_committed_summary(root: Path) -> bool:
    summary = _read_json(root / "outputs/audits/source_backed_bundle_manifest_summary.json")
    local_path = str(summary.get("local_bundle_path", ""))
    if not local_path:
        return False
    manifest = _read_json(Path(local_path) / "manifest.json")
    return int(manifest.get("label_ready_rows", 0) or 0) >= int(summary.get("label_ready_rows", 0) or 0)


def _goal_v1_diagnostic_coverage02_valid(root: Path) -> bool:
    try:
        from ashare_premarket.diagnostics.goal_v1_diagnostic_coverage02 import (
            goal_v1_diagnostic_coverage02_valid_multi_symbol_diagnostic_evidence,
        )

        return goal_v1_diagnostic_coverage02_valid_multi_symbol_diagnostic_evidence(root)
    except Exception:
        return False


def _forbidden_outputs_present(root: Path) -> list[str]:
    return [path for path in FORBIDDEN_OUTPUT_DIRS if (root / path).exists()]


def _workflow_rows(root: Path) -> dict[str, dict[str, str]]:
    path = root / "configs/project/workflow_status.csv"
    if not path.exists():
        return {}
    return {row["workflow_id"]: row for row in read_csv(path)}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    return read_csv(path)


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return read_json(path)
    except Exception:
        return {}


def _report_pass_or_warn(text: str) -> bool:
    prefix = "GOAL-DATA-LABEL-01 Forward-Return Label Coverage Expansion:"
    return f"{prefix} {PASS}" in text or f"{prefix} {PASS_WITH_WARNINGS}" in text


def _format_return(value: float) -> str:
    return f"{value:.6f}"


def _float(raw: str) -> float:
    return float(raw)


def _is_float(raw: str) -> bool:
    try:
        float(raw)
        return True
    except (TypeError, ValueError):
        return False

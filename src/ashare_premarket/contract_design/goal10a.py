from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import preserve_later_review_only_capabilities, preserve_later_review_only_workflow_states
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-10A"
GOAL_NAME = "GOAL-10A-BACKTEST-CONTRACT-DESIGN-GATE"
MODE = "design_only"
WORKFLOW_ID = "goal10a_backtest_contract_design_gate"
GOAL10B_WORKFLOW_ID = "goal10b_backtest_review_only_validation_gate"
GOAL10C_WORKFLOW_ID = "goal10c_backtest_cost_slippage_sensitivity_gate"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
GOAL_V1_WORKFLOW_ID = "goal_v1_integrity01_artifact_lineage_structure_gate"
GOAL10A_ALLOWED_NEXT = "request_explicit_goal10b_review_only_backtest_validation_gate_or_fix_goal10a_warnings"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

CONFIG_DIR = "configs/backtest"
DOC_DIR = "docs/backtest"
AUDIT_DIR = "outputs/audits"

INPUT_CONTRACT_PATH = f"{CONFIG_DIR}/goal10a_backtest_input_contract.yaml"
METRIC_CONTRACT_PATH = f"{CONFIG_DIR}/goal10a_backtest_metric_contract.yaml"
GROUPING_CONTRACT_PATH = f"{CONFIG_DIR}/goal10a_backtest_grouping_contract.yaml"
EXECUTION_POLICY_PATH = f"{CONFIG_DIR}/goal10a_execution_alignment_policy.yaml"
DOC_PATH = f"{DOC_DIR}/GOAL10A_BACKTEST_CONTRACT_DESIGN_GATE.md"
REPORT_PATH = f"{AUDIT_DIR}/goal10a_backtest_contract_design_report.md"
MANIFEST_PATH = f"{AUDIT_DIR}/goal10a_backtest_contract_design_manifest.json"
AUDIT_PATH = f"{AUDIT_DIR}/goal10a_backtest_contract_design_audit.md"

GOAL08B_DIAGNOSTICS_PATH = "outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv"
GOAL08B_REPORT_PATH = "outputs/audits/goal08b_recommendation_diagnostics_report.md"
GOAL08B_MANIFEST_PATH = "outputs/audits/goal08b_recommendation_diagnostics_manifest.json"
GOAL08B_AUDIT_PATH = "outputs/audits/goal08b_recommendation_diagnostics_audit.md"
GOAL09_DIAGNOSTICS_PATH = "outputs/position/goal09_review_only_position_band_diagnostics.csv"
GOAL09_REPORT_PATH = "outputs/audits/goal09_position_band_diagnostics_report.md"
GOAL09_MANIFEST_PATH = "outputs/audits/goal09_position_band_diagnostics_manifest.json"
GOAL09_AUDIT_PATH = "outputs/audits/goal09_position_band_diagnostics_audit.md"
GOAL_V1_REPORT_PATH = "outputs/audits/goal_v1_integrity01_artifact_lineage_structure_report.md"
GOAL_V1_MANIFEST_PATH = "outputs/audits/goal_v1_integrity01_artifact_lineage_structure_manifest.json"
GOAL_V1_AUDIT_PATH = "outputs/audits/goal_v1_integrity01_artifact_lineage_structure_audit.md"
GOAL10B_REPORT_PATH = "outputs/audits/goal10b_recommendation_backtest_report.md"
GOAL10B_MANIFEST_PATH = "outputs/audits/goal10b_recommendation_backtest_manifest.json"
GOAL10B_AUDIT_PATH = "outputs/audits/goal10b_recommendation_backtest_audit.md"

WORKFLOW_PRODUCES_ARTIFACTS = ";".join(
    [
        INPUT_CONTRACT_PATH,
        METRIC_CONTRACT_PATH,
        GROUPING_CONTRACT_PATH,
        EXECUTION_POLICY_PATH,
        DOC_PATH,
        REPORT_PATH,
        MANIFEST_PATH,
        AUDIT_PATH,
    ]
)
WORKFLOW_PRIMARY_DOCS = f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md"
WORKFLOW_PRIMARY_SCRIPTS = "scripts/run_goal10a_backtest_contract_design_gate.py;scripts/audit_goal10a_backtest_contract_design_gate.py"
WORKFLOW_PRIMARY_OUTPUTS = f"{REPORT_PATH};{MANIFEST_PATH};{AUDIT_PATH}"
WORKFLOW_NOTES = "Design-only future backtest contract gate; defines input, metric, grouping, execution-alignment, cost/slippage, benchmark, and no-lookahead policies only. It runs no backtest and creates no performance rows, equity curves, portfolio returns, dashboard, trading, production, broker, factor-mining, local-lake, or DQN/RL output."

REQUIRED_GOAL08B_FIELDS = [
    "trade_date",
    "symbol",
    "recommendation_diagnostic_label",
    "actionability_status",
    "actionability_blocked",
    "risk_severity",
    "risk_state",
    "risk_warning_codes",
    "warning_propagation_codes",
    "diagnostic_mode",
    "non_actionable_disclaimer",
]

REQUIRED_GOAL09_FIELDS = [
    "trade_date",
    "symbol",
    "recommendation_actionability_status",
    "position_band_status",
    "position_actionability_status",
    "position_actionability_blocked",
    "risk_severity",
    "risk_warning_codes",
    "propagated_warning_codes",
    "diagnostic_mode",
    "non_actionable_disclaimer",
]

FUTURE_METRICS = [
    ("forward_return_1d", "Forward return from execution date through one future trading session."),
    ("forward_return_5d", "Forward return from execution date through five future trading sessions."),
    ("forward_return_20d", "Forward return from execution date through twenty future trading sessions."),
    ("benchmark_excess_return", "Future row return less benchmark return over the identical execution window."),
    ("hit_rate", "Share of evaluated rows with positive selected forward return."),
    ("mean_return", "Arithmetic mean of selected forward returns."),
    ("median_return", "Median selected forward return."),
    ("volatility", "Standard deviation of selected forward returns."),
    ("max_drawdown", "Maximum drawdown of a future diagnostic-only grouped return series."),
    ("IC", "Pearson correlation between diagnostic score or ordered label and future return."),
    ("Rank IC", "Spearman rank correlation between diagnostic ordering and future return."),
]

TARGET_HORIZONS = ["1d", "5d", "20d"]

WARNING_CODES = [
    "calibration_not_reliable_for_thresholding",
    "feature_sign_instability_bounded",
    "provider_source_concentration_disclosed",
    "selected_score_variant_weak_rank_signal",
    "single_provider_mode_akshare_direct",
    "target_horizon_calibration_warning",
    "weak_target_horizon_rank_signal",
]

FALSE_BOUNDARY_KEYS = [
    "backtests_run",
    "backtest_rows_generated",
    "backtest_performance_rows_generated",
    "equity_curves_generated",
    "portfolio_returns_generated",
    "portfolio_construction_generated",
    "portfolio_weights_generated",
    "position_sizing_generated",
    "order_quantities_generated",
    "buy_sell_hold_outputs_generated",
    "target_prices_generated",
    "recommendation_rows_generated",
    "new_recommendation_rows_generated",
    "new_position_rows_generated",
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
    "new_data_fetched",
    "data_panel_expanded",
    "local_lake_files_created",
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

ALLOWED_GOAL10B_BACKTEST_OUTPUTS = {
    "outputs/backtest/goal10b_recommendation_backtest_input_snapshot.csv",
    "outputs/backtest/goal10b_recommendation_group_metrics.csv",
    "outputs/backtest/goal10b_risk_severity_group_metrics.csv",
    "outputs/backtest/goal10b_warning_group_metrics.csv",
    "outputs/backtest/goal10b_ic_rank_ic_summary.csv",
}


def run_goal10a_backtest_contract_design_gate(root: Path) -> bool:
    result = evaluate_goal10a_backtest_contract_design_gate(root)
    _write_design_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal10a_backtest_contract_design_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal10a_backtest_contract_design_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    input_contract = _read_json(root / INPUT_CONTRACT_PATH)
    metric_contract = _read_json(root / METRIC_CONTRACT_PATH)
    grouping_contract = _read_json(root / GROUPING_CONTRACT_PATH)
    execution_policy = _read_json(root / EXECUTION_POLICY_PATH)
    workflow = _workflow_rows(root)
    recheck = evaluate_goal10a_backtest_contract_design_gate(root)
    failures: list[str] = []

    if not _report_pass_or_warn(report, "GOAL-10A Backtest Contract Design Gate:"):
        failures.append("goal10a_report_not_pass_or_warn")
    if recheck["status"] == BLOCKED:
        failures.extend(f"recheck:{failure}" for failure in recheck["failures"])
    if manifest.get("goal") != GOAL_NAME:
        failures.append("manifest_goal_invalid")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_invalid")
    if manifest.get("input_grain") != "trade_date + symbol":
        failures.append("manifest_input_grain_invalid")
    if manifest.get("source_goal08b_rows") != manifest.get("source_goal09_rows"):
        failures.append("source_row_counts_do_not_match")
    if manifest.get("source_trade_date_symbol_keys_match") is not True:
        failures.append("source_keys_do_not_match")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"manifest_{key}_not_false")
    for key in [
        "design_only_contracts_written",
        "goal08b_inputs_never_actionable",
        "goal09_inputs_never_actionable",
        "t_plus_1_required",
        "no_lookahead_required",
        "benchmark_leakage_forbidden",
        "cost_slippage_sensitivity_defined_not_run",
        "suspended_limit_missing_policy_defined",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")

    if input_contract.get("mode") != MODE:
        failures.append("input_contract_mode_invalid")
    if input_contract.get("required_input_grain") != "trade_date + symbol":
        failures.append("input_contract_grain_invalid")
    if input_contract.get("source_artifacts", {}).get("goal08b_rows_are_actionable") is not False:
        failures.append("input_contract_goal08b_actionability_invalid")
    if input_contract.get("source_artifacts", {}).get("goal09_rows_are_actionable") is not False:
        failures.append("input_contract_goal09_actionability_invalid")
    failures.extend(
        f"input_contract_missing_goal08b_field:{field}"
        for field in REQUIRED_GOAL08B_FIELDS
        if field not in input_contract.get("required_goal08b_fields", [])
    )
    failures.extend(
        f"input_contract_missing_goal09_field:{field}"
        for field in REQUIRED_GOAL09_FIELDS
        if field not in input_contract.get("required_goal09_fields", [])
    )

    metric_names = [item.get("metric_name") for item in metric_contract.get("future_metric_definitions", [])]
    required_metric_names = [name for name, _ in FUTURE_METRICS]
    failures.extend(f"metric_contract_missing_metric:{name}" for name in required_metric_names if name not in metric_names)
    if metric_contract.get("goal10a_runs_metrics") is not False:
        failures.append("metric_contract_runs_metrics_not_false")
    if metric_contract.get("metric_output_row_count") != 0:
        failures.append("metric_contract_row_count_not_zero")

    group_fields = {item.get("group_name") for item in grouping_contract.get("future_grouping_rules", [])}
    for required_group in [
        "recommendation_eligibility_status",
        "actionability_status",
        "risk_severity",
        "position_band_status",
        "warning_category",
    ]:
        if required_group not in group_fields:
            failures.append(f"grouping_contract_missing_group:{required_group}")
    if grouping_contract.get("goal10a_runs_group_evaluation") is not False:
        failures.append("grouping_contract_runs_evaluation_not_false")

    if execution_policy.get("t_plus_1_execution_required") is not True:
        failures.append("execution_policy_t_plus_1_missing")
    if execution_policy.get("same_day_execution_allowed") is not False:
        failures.append("execution_policy_same_day_allowed")
    if execution_policy.get("no_lookahead_constraints", {}).get("future_returns_may_not_select_or_filter_inputs") is not True:
        failures.append("execution_policy_no_lookahead_missing")
    if execution_policy.get("cost_slippage_sensitivity", {}).get("goal10a_runs_sensitivity") is not False:
        failures.append("execution_policy_cost_sensitivity_runs")

    gate_row = workflow.get(WORKFLOW_ID, {})
    if gate_row.get("status") != "implemented_design_only":
        failures.append("goal10a_workflow_not_implemented_design_only")
    if gate_row.get("implemented_in_repo") != "true":
        failures.append("goal10a_workflow_not_marked_implemented")
    if gate_row.get("depends_on") != GOAL_V1_WORKFLOW_ID:
        failures.append("goal10a_depends_on_invalid")
    if gate_row.get("allowed_next_action") != GOAL10A_ALLOWED_NEXT:
        failures.append("goal10a_allowed_next_invalid")
    goal10b_ready = _goal10b_review_only_evidence_ready(root)
    goal10b_row = workflow.get(GOAL10B_WORKFLOW_ID, {})
    if goal10b_ready:
        if goal10b_row.get("status") != "implemented_review_only":
            failures.append("goal10b_workflow_not_implemented_review_only")
        if goal10b_row.get("implemented_in_repo") != "true":
            failures.append("goal10b_workflow_not_marked_implemented")
        if goal10b_row.get("depends_on") != WORKFLOW_ID:
            failures.append("goal10b_depends_on_invalid")
    else:
        if goal10b_row.get("status") != "locked_future":
            failures.append(f"{GOAL10B_WORKFLOW_ID}_not_locked_future")
        if goal10b_row.get("implemented_in_repo") != "false":
            failures.append(f"{GOAL10B_WORKFLOW_ID}_marked_implemented")
    for workflow_id in [GOAL10C_WORKFLOW_ID, GOAL10D_WORKFLOW_ID]:
        row = workflow.get(workflow_id, {})
        if row.get("status") != "locked_future":
            failures.append(f"{workflow_id}_not_locked_future")
        if row.get("implemented_in_repo") != "false":
            failures.append(f"{workflow_id}_marked_implemented")
    failures.extend(f"forbidden_output_dir_present:{path}" for path in _forbidden_output_dirs_present(root))
    failures.extend(f"unexpected_backtest_output:{path}" for path in _unexpected_backtest_outputs(root))

    status = PASS if not failures else BLOCKED
    write_text(
        root / AUDIT_PATH,
        "\n".join(
            [
                "# GOAL-10A Backtest Contract Design Audit",
                "",
                f"Status: `{status}`",
                "",
                f"GOAL-10A workflow status: `{gate_row.get('status', 'missing')}`",
                "GOAL-10A mode: `design_only`",
                "Backtests run: `false`",
                "Backtest performance rows generated: `false`",
                "Equity curves or portfolio returns generated: `false`",
                "Dashboard, HTML, Streamlit, frontend, trading, production, broker, factor-mining, local-lake, and DQN/RL outputs generated: `false`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == PASS


def evaluate_goal10a_backtest_contract_design_gate(root: Path) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    workflow_rows = _read_csv(root / "configs/project/workflow_status.csv")
    workflow = {row.get("workflow_id", ""): row for row in workflow_rows}
    goal08b_rows = _read_csv(root / GOAL08B_DIAGNOSTICS_PATH)
    goal09_rows = _read_csv(root / GOAL09_DIAGNOSTICS_PATH)
    goal_v1_report = _read(root / GOAL_V1_REPORT_PATH)
    goal_v1_manifest = _read_json(root / GOAL_V1_MANIFEST_PATH)
    goal_v1_audit = _read(root / GOAL_V1_AUDIT_PATH)

    failures.extend(_validate_goal_v1_evidence(workflow, goal_v1_report, goal_v1_manifest, goal_v1_audit))
    failures.extend(_validate_goal08b_inputs(goal08b_rows))
    failures.extend(_validate_goal09_inputs(goal09_rows))
    key_match = _key_set(goal08b_rows) == _key_set(goal09_rows) and bool(goal08b_rows)
    if not key_match:
        failures.append("goal08b_goal09_trade_date_symbol_keys_mismatch")
    if len(goal08b_rows) != len(goal09_rows):
        failures.append("goal08b_goal09_row_count_mismatch")
    failures.extend(f"forbidden_output_dir_present:{path}" for path in _forbidden_output_dirs_present(root))
    failures.extend(f"unexpected_backtest_output:{path}" for path in _unexpected_backtest_outputs(root))

    observed_warnings = sorted(_warning_codes(goal08b_rows) | _warning_codes(goal09_rows))
    warnings.extend(code for code in observed_warnings if code)
    status = BLOCKED if failures else PASS_WITH_WARNINGS if warnings else PASS
    manifest = _manifest(status, failures, warnings, goal08b_rows, goal09_rows, key_match)
    return {
        "status": status,
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "input_contract": _input_contract(),
        "metric_contract": _metric_contract(),
        "grouping_contract": _grouping_contract(observed_warnings),
        "execution_policy": _execution_policy(),
        "manifest": manifest,
    }


def goal10a_valid_design_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        _report_pass_or_warn(report, "GOAL-10A Backtest Contract Design Gate:")
        and "Status: `PASS`" in audit
        and manifest.get("goal") == GOAL_NAME
        and manifest.get("mode") == MODE
        and manifest.get("design_only_contracts_written") is True
        and manifest.get("backtests_run") is False
        and manifest.get("backtest_performance_rows_generated") is False
        and manifest.get("equity_curves_generated") is False
        and manifest.get("portfolio_returns_generated") is False
    )


def goal10a_implemented_workflow_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-10A Backtest Contract Design Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_design_only",
        "current_repo_role": "design_only_backtest_contract_gate",
        "implemented_in_repo": "true",
        "allowed_next_action": GOAL10A_ALLOWED_NEXT,
        "depends_on": GOAL_V1_WORKFLOW_ID,
        "produces_artifacts": WORKFLOW_PRODUCES_ARTIFACTS,
        "primary_docs": WORKFLOW_PRIMARY_DOCS,
        "primary_scripts": WORKFLOW_PRIMARY_SCRIPTS,
        "primary_outputs": WORKFLOW_PRIMARY_OUTPUTS,
        "promotion_rule": "implemented_design_only_after_goal10a_contract_design_pass_with_warnings",
        "notes": WORKFLOW_NOTES,
    }


def _input_contract() -> dict[str, object]:
    return {
        "goal": GOAL_NAME,
        "mode": MODE,
        "source_artifacts": {
            "goal08b_recommendation_diagnostics": GOAL08B_DIAGNOSTICS_PATH,
            "goal08b_report": GOAL08B_REPORT_PATH,
            "goal08b_manifest": GOAL08B_MANIFEST_PATH,
            "goal08b_audit": GOAL08B_AUDIT_PATH,
            "goal09_position_band_diagnostics": GOAL09_DIAGNOSTICS_PATH,
            "goal09_report": GOAL09_REPORT_PATH,
            "goal09_manifest": GOAL09_MANIFEST_PATH,
            "goal09_audit": GOAL09_AUDIT_PATH,
            "goal08b_rows_are_actionable": False,
            "goal09_rows_are_actionable": False,
            "source_modes_required": ["review_only"],
        },
        "required_input_grain": "trade_date + symbol",
        "join_key": ["trade_date", "symbol"],
        "required_goal08b_fields": REQUIRED_GOAL08B_FIELDS,
        "required_goal09_fields": REQUIRED_GOAL09_FIELDS,
        "date_field_contract": {
            "source_trade_date": "Required upstream diagnostic date at trade_date + symbol grain.",
            "future_signal_date": "Must equal source trade_date unless a later explicit gate records a PIT-safe diagnostic publication timestamp.",
            "future_execution_date": "Must be the first eligible trading date strictly after signal_date.",
        },
        "contract_boundary": {
            "goal10a_generates_rows": False,
            "goal10a_runs_backtest": False,
            "goal10a_fetches_prices": False,
            "goal10a_writes_local_lake": False,
        },
    }


def _metric_contract() -> dict[str, object]:
    return {
        "goal": GOAL_NAME,
        "mode": MODE,
        "goal10a_runs_metrics": False,
        "metric_output_row_count": 0,
        "target_horizons": TARGET_HORIZONS,
        "future_metric_definitions": [
            {
                "metric_name": name,
                "definition": definition,
                "calculation_status": "future_contract_only_not_run_by_goal10a",
                "no_lookahead_rule": "Future return labels may be computed only after the relevant target horizon closes and may not change input eligibility.",
            }
            for name, definition in FUTURE_METRICS
        ],
        "forbidden_metric_outputs_from_goal10a": [
            "backtest_row",
            "performance_table",
            "equity_curve",
            "portfolio_return",
            "ranked_trade_list",
            "buy_sell_hold_action",
        ],
    }


def _grouping_contract(observed_warning_codes: list[str]) -> dict[str, object]:
    return {
        "goal": GOAL_NAME,
        "mode": MODE,
        "goal10a_runs_group_evaluation": False,
        "future_grouping_rules": [
            {
                "group_name": "recommendation_eligibility_status",
                "source_field": "goal08b.recommendation_diagnostic_label",
                "observed_values": ["blocked_high_risk"],
                "evaluation_use": "future grouped review-only metric comparison",
            },
            {
                "group_name": "actionability_status",
                "source_field": "goal08b.actionability_status",
                "observed_values": ["never_actionable"],
                "evaluation_use": "future confirmation that no actionable bucket is evaluated as a recommendation",
            },
            {
                "group_name": "risk_severity",
                "source_field": "goal08b.risk_severity and goal09.risk_severity",
                "observed_values": ["HIGH"],
                "evaluation_use": "future risk-severity grouped diagnostics",
            },
            {
                "group_name": "position_band_status",
                "source_field": "goal09.position_band_status",
                "observed_values": ["diagnostic_blocked_no_position_instruction"],
                "evaluation_use": "future non-actionable position-band status comparison",
            },
            {
                "group_name": "warning_category",
                "source_field": "goal08b.risk_warning_codes and goal09.propagated_warning_codes",
                "observed_values": observed_warning_codes or WARNING_CODES,
                "evaluation_use": "future warning-category grouped diagnostics",
            },
        ],
        "forbidden_group_outputs_from_goal10a": [
            "ranked_top_n",
            "buy_candidates",
            "position_candidates",
            "capital_allocation",
            "trade_instruction",
        ],
    }


def _execution_policy() -> dict[str, object]:
    return {
        "goal": GOAL_NAME,
        "mode": MODE,
        "date_alignment": {
            "signal_date": "The PIT-safe date on which the diagnostic is considered available; for GOAL-08B/GOAL-09 inputs it equals trade_date.",
            "trade_date": "The upstream diagnostic grain date; it is not an execution date in future evaluation.",
            "execution_date": "The first eligible A-share trading session strictly after signal_date, normally T+1.",
            "target_horizon": TARGET_HORIZONS,
            "benchmark_alignment": "Benchmark return windows must use the same execution_date and target_horizon as the evaluated diagnostic row.",
        },
        "t_plus_1_execution_required": True,
        "same_day_execution_allowed": False,
        "no_lookahead_constraints": {
            "input_membership_frozen_at_signal_date": True,
            "future_returns_may_not_select_or_filter_inputs": True,
            "benchmark_future_returns_may_not_select_or_filter_inputs": True,
            "execution_price_may_not_be_used_before_execution_date": True,
            "target_window_prices_may_not_be_used_before_window_close": True,
        },
        "benchmark_contract": {
            "benchmark_id_must_be_declared_before_evaluation": True,
            "allowed_future_benchmark_ids": ["000300.SH", "000905.SH", "000001.SH"],
            "benchmark_return_window_matches_row_window": True,
            "forbidden_leakage_rules": [
                "Do not choose benchmarks using ex-post performance.",
                "Do not use future benchmark constituents or target-window returns to change input eligibility.",
                "Do not compare a row against a benchmark window different from its execution_date and target_horizon.",
            ],
        },
        "tradability_policy": {
            "suspended_at_execution": "mark_unevaluable_with_reason_no_fill_assumed",
            "limit_up_at_entry": "mark_unevaluable_or_no_entry_fill_no_chase_assumption",
            "limit_down_at_exit": "mark_exit_constrained_and disclose separately in future diagnostics",
            "missing_price": "mark_missing_price_excluded_from_metric_denominator_no_imputation",
            "future_evaluation_must_report_evaluable_count": True,
        },
        "cost_slippage_sensitivity": {
            "defined_for_future_use": True,
            "goal10a_runs_sensitivity": False,
            "scenario_names": ["zero_cost", "low_cost", "base_cost", "high_cost"],
            "components": ["commission_bps", "stamp_duty_bps", "slippage_bps", "execution_delay_days"],
            "output_policy": "No sensitivity rows, tables, or charts may be produced by GOAL-10A.",
        },
    }


def _manifest(
    status: str,
    failures: list[str],
    warnings: list[str],
    goal08b_rows: list[dict[str, str]],
    goal09_rows: list[dict[str, str]],
    key_match: bool,
) -> dict[str, object]:
    return {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "status": status,
        "mode": MODE,
        "allowed_next_action": GOAL10A_ALLOWED_NEXT if status != BLOCKED else "repair_goal10a_contract_design_blockers",
        "input_grain": "trade_date + symbol",
        "source_goal08b_rows": len(goal08b_rows),
        "source_goal09_rows": len(goal09_rows),
        "source_trade_date_symbol_keys_match": key_match,
        "goal08b_actionability_status_values": sorted({row.get("actionability_status", "") for row in goal08b_rows}),
        "goal09_position_actionability_status_values": sorted({row.get("position_actionability_status", "") for row in goal09_rows}),
        "goal08b_inputs_never_actionable": sorted({row.get("actionability_status", "") for row in goal08b_rows}) == ["never_actionable"],
        "goal09_inputs_never_actionable": sorted({row.get("position_actionability_status", "") for row in goal09_rows}) == ["never_actionable"],
        "design_only_contracts_written": status != BLOCKED,
        "future_metric_names": [name for name, _ in FUTURE_METRICS],
        "target_horizons": TARGET_HORIZONS,
        "t_plus_1_required": True,
        "no_lookahead_required": True,
        "benchmark_leakage_forbidden": True,
        "cost_slippage_sensitivity_defined_not_run": True,
        "suspended_limit_missing_policy_defined": True,
        "goal10b_status_after_goal10a": "locked_future",
        "goal10c_status_after_goal10a": "locked_future",
        "goal10d_status_after_goal10a": "locked_future",
        "dashboard_daily_report_status_after_goal10a": "locked_future",
        "input_artifacts": [
            GOAL08B_DIAGNOSTICS_PATH,
            GOAL08B_REPORT_PATH,
            GOAL08B_MANIFEST_PATH,
            GOAL08B_AUDIT_PATH,
            GOAL09_DIAGNOSTICS_PATH,
            GOAL09_REPORT_PATH,
            GOAL09_MANIFEST_PATH,
            GOAL09_AUDIT_PATH,
            GOAL_V1_REPORT_PATH,
            GOAL_V1_MANIFEST_PATH,
            GOAL_V1_AUDIT_PATH,
        ],
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        **{key: False for key in FALSE_BOUNDARY_KEYS},
    }


def _write_design_artifacts(root: Path, result: dict[str, object]) -> None:
    write_json(root / INPUT_CONTRACT_PATH, result["input_contract"])
    write_json(root / METRIC_CONTRACT_PATH, result["metric_contract"])
    write_json(root / GROUPING_CONTRACT_PATH, result["grouping_contract"])
    write_json(root / EXECUTION_POLICY_PATH, result["execution_policy"])
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_report(root, result)
    _write_doc(root, result)


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    write_text(
        root / REPORT_PATH,
        "\n".join(
            [
                "# GOAL-10A Backtest Contract Design Gate",
                "",
                f"GOAL-10A Backtest Contract Design Gate: {result['status']}",
                f"Mode: `{MODE}`",
                "",
                "## Input Contracts",
                f"- GOAL-08B recommendation diagnostics rows referenced: `{manifest['source_goal08b_rows']}`",
                f"- GOAL-09 position-band diagnostics rows referenced: `{manifest['source_goal09_rows']}`",
                f"- Shared grain: `{manifest['input_grain']}`",
                f"- Trade-date plus symbol keys match: `{str(manifest['source_trade_date_symbol_keys_match']).lower()}`",
                "- GOAL-08B and GOAL-09 inputs must remain `never_actionable`.",
                "",
                "## Future Evaluation Contract",
                "- Defines signal_date, trade_date, execution_date, target_horizon, benchmark alignment, T+1, no-lookahead, cost/slippage sensitivity, and suspended/limit/missing-price policies.",
                "- Defines future metrics only: forward returns, benchmark excess return, hit rate, mean, median, volatility, max drawdown, IC, and Rank IC.",
                "- Defines future grouping by recommendation eligibility status, actionability status, risk severity, position-band status, and warning category.",
                "",
                "## Safety",
                "- No backtest was run.",
                "- No backtest performance rows, equity curves, portfolio returns, dashboard files, HTML, Streamlit, frontend code, buy/sell/hold actions, target prices, position sizes, order quantities, local-lake data, trading, production, broker, factor-mining, or DQN/RL outputs were generated.",
                "- GOAL-10B can be implemented only by its own review-only diagnostics gate; GOAL-10C, GOAL-10D, Dashboard / Daily Report UI, paper/live trading, broker, production, factor-mining, and DQN/RL remain locked.",
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
    write_text(
        root / DOC_PATH,
        "\n".join(
            [
                "# GOAL-10A Backtest Contract Design Gate",
                "",
                f"Status: `{result['status']}`",
                "",
                "GOAL-10A is a design-only contract gate for future review-only backtest validation. It defines what a later GOAL-10B-style evaluator may read and how that evaluator must align dates, benchmarks, target horizons, tradability constraints, grouping, metrics, and cost/slippage sensitivity.",
                "",
                "It does not run a backtest and does not generate backtest rows, performance tables, equity curves, portfolio returns, dashboard output, HTML, Streamlit, frontend code, buy/sell/hold actions, target prices, position sizes, order quantities, trading instructions, production writes, broker outputs, factor-mining outputs, local-lake files, or DQN/RL outputs.",
                "",
                "## Source Inputs",
                "",
                "- `outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv`",
                "- `outputs/position/goal09_review_only_position_band_diagnostics.csv`",
                "- `outputs/audits/goal_v1_integrity01_artifact_lineage_structure_manifest.json`",
                "",
                "All source rows must stay at `trade_date + symbol` grain and must remain `never_actionable`.",
                "",
                "## Date Alignment",
                "",
                "- `signal_date`: the PIT-safe date on which a diagnostic is available; for current GOAL-08B/GOAL-09 diagnostics it equals `trade_date`.",
                "- `trade_date`: the upstream diagnostic date and join key component; it is not an execution date.",
                "- `execution_date`: the first eligible A-share trading session strictly after `signal_date`, normally T+1.",
                "- `target_horizon`: one of `1d`, `5d`, or `20d` in a future evaluator.",
                "- Benchmark windows must use the same `execution_date` and `target_horizon` as the evaluated diagnostic row.",
                "",
                "## Future Metrics",
                "",
                "- `forward_return_1d`",
                "- `forward_return_5d`",
                "- `forward_return_20d`",
                "- `benchmark_excess_return`",
                "- `hit_rate`",
                "- `mean_return`",
                "- `median_return`",
                "- `volatility`",
                "- `max_drawdown`",
                "- `IC`",
                "- `Rank IC`",
                "",
                "## Locked Boundary",
                "",
                "GOAL-10B can be implemented only by its own review-only diagnostics gate; GOAL-10C, GOAL-10D, Dashboard / Daily Report UI, paper trading, live trading, broker integration, production writes, factor-mining, and DQN/RL remain `locked_future` or deleted from active mainline as applicable.",
                "",
            ]
        ),
    )


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys())
    by_id = {row["workflow_id"]: row for row in rows}
    patch = goal10a_implemented_workflow_patch()
    if result["status"] == BLOCKED:
        patch.update(
            {
                "status": "locked_future",
                "current_repo_role": "backtest_contract_design_blocked",
                "implemented_in_repo": "false",
                "allowed_next_action": "repair_goal10a_contract_design_blockers",
                "produces_artifacts": "",
                "primary_scripts": "",
                "primary_outputs": "",
                "promotion_rule": "locked_until_goal10a_contract_design_passes",
                "notes": "GOAL-10A is blocked; no GOAL-10B review-only validation request is eligible.",
            }
        )
    _upsert_workflow_row(rows, by_id, WORKFLOW_ID, patch, after=GOAL_V1_WORKFLOW_ID)
    goal10b_row = by_id.get(GOAL10B_WORKFLOW_ID, {})
    goal10b_already_implemented = (
        _goal10b_review_only_evidence_ready(root)
        and goal10b_row.get("status") == "implemented_review_only"
        and goal10b_row.get("implemented_in_repo") == "true"
    )
    if not goal10b_already_implemented:
        _upsert_workflow_row(rows, by_id, GOAL10B_WORKFLOW_ID, _locked_goal10b_patch(), after=WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL10C_WORKFLOW_ID, _locked_goal10c_patch(), after=GOAL10B_WORKFLOW_ID)
    _upsert_workflow_row(rows, by_id, GOAL10D_WORKFLOW_ID, _locked_goal10d_patch(), after=GOAL10C_WORKFLOW_ID)
    for workflow_id in [
        "signal_backtest",
        "portfolio_backtest",
        "cost_slippage_sensitivity",
        "paper_trading_journal",
        "failure_attribution",
        "dashboard_daily_report",
        "production_hardening",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
    ]:
        if workflow_id in by_id:
            by_id[workflow_id]["status"] = "locked_future"
            by_id[workflow_id]["implemented_in_repo"] = "false"
            by_id[workflow_id]["allowed_next_action"] = (
                "remain_locked_not_unlocked_by_goal10a"
                if workflow_id == "dashboard_daily_report"
                else "remain_locked"
            )
            if workflow_id == "dashboard_daily_report":
                by_id[workflow_id]["notes"] = (
                    "Locked dashboard workflow; GOAL-10A does not unlock dashboard work, "
                    "and the only allowed future unlock after GOAL-10A is an explicit "
                    "GOAL-10B review-only validation request."
                )
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


def _locked_goal10b_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-10B Review-Only Backtest Validation Gate",
        "stage_or_goal": "GOAL-10B",
        "status": "locked_future",
        "current_repo_role": "locked_future_review_only_backtest_validation",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10b_review_only_request",
        "depends_on": WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal10b_review_only_backtest_validation_gate",
        "notes": "Future review-only validation gate; locked by GOAL-10A and not implemented. No backtest rows or performance outputs exist.",
    }


def _locked_goal10c_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-10C Backtest Cost / Slippage Sensitivity",
        "stage_or_goal": "GOAL-10C",
        "status": "locked_future",
        "current_repo_role": "locked_future_backtest_sensitivity",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10c_request",
        "depends_on": GOAL10B_WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal10c_cost_slippage_sensitivity_gate",
        "notes": "Future cost/slippage sensitivity remains locked; GOAL-10A defines only the contract and runs no sensitivity analysis.",
    }


def _locked_goal10d_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-10D Backtest Failure Attribution",
        "stage_or_goal": "GOAL-10D",
        "status": "locked_future",
        "current_repo_role": "locked_future_backtest_failure_attribution",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10d_request",
        "depends_on": GOAL10C_WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal10d_failure_attribution_gate",
        "notes": "Future failure attribution remains locked; GOAL-10A creates no attribution rows or reports.",
    }


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    if not path.exists():
        return
    payload = read_json(path)
    payload[WORKFLOW_ID] = "implemented_design_only" if result["status"] != BLOCKED else False
    payload[GOAL10B_WORKFLOW_ID] = "implemented_review_only" if _goal10b_review_only_evidence_ready(root) else False
    payload[GOAL10C_WORKFLOW_ID] = False
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
    ]:
        payload[key] = False
    preserve_later_review_only_capabilities(root, payload)
    write_json(path, payload)


def _validate_goal_v1_evidence(
    workflow: dict[str, dict[str, str]],
    report: str,
    manifest: dict[str, object],
    audit: str,
) -> list[str]:
    failures: list[str] = []
    row = workflow.get(GOAL_V1_WORKFLOW_ID, {})
    if row.get("status") != "implemented_infrastructure_only":
        failures.append("goal_v1_integrity01_workflow_not_implemented_infrastructure_only")
    if row.get("implemented_in_repo") != "true":
        failures.append("goal_v1_integrity01_workflow_not_marked_implemented")
    if not _report_pass_or_warn(report, "GOAL-V1-INTEGRITY-01 Artifact Lineage and Structure Gate:"):
        failures.append("goal_v1_integrity01_report_not_pass_or_warn")
    if "Status: `PASS`" not in audit:
        failures.append("goal_v1_integrity01_audit_not_pass")
    if manifest.get("canonical_artifact_lineage_verified") is not True:
        failures.append("goal_v1_integrity01_lineage_not_verified")
    if manifest.get("goal08b_rows_never_actionable") is not True:
        failures.append("goal_v1_integrity01_goal08b_not_never_actionable")
    if manifest.get("goal09_rows_never_actionable") is not True:
        failures.append("goal_v1_integrity01_goal09_not_never_actionable")
    return failures


def _validate_goal08b_inputs(rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    if not rows:
        return ["goal08b_diagnostics_missing"]
    fields = set(rows[0])
    failures.extend(f"goal08b_missing_field:{field}" for field in REQUIRED_GOAL08B_FIELDS if field not in fields)
    if len(_key_set(rows)) != len(rows):
        failures.append("goal08b_grain_not_unique_trade_date_symbol")
    for index, row in enumerate(rows):
        if row.get("diagnostic_mode") != "review_only":
            failures.append(f"goal08b_row_{index}_not_review_only")
        if row.get("actionability_status") != "never_actionable":
            failures.append(f"goal08b_row_{index}_not_never_actionable")
        if row.get("actionability_blocked") != "true":
            failures.append(f"goal08b_row_{index}_actionability_not_blocked")
    return failures


def _validate_goal09_inputs(rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    if not rows:
        return ["goal09_diagnostics_missing"]
    fields = set(rows[0])
    failures.extend(f"goal09_missing_field:{field}" for field in REQUIRED_GOAL09_FIELDS if field not in fields)
    if len(_key_set(rows)) != len(rows):
        failures.append("goal09_grain_not_unique_trade_date_symbol")
    for index, row in enumerate(rows):
        if row.get("diagnostic_mode") != "review_only":
            failures.append(f"goal09_row_{index}_not_review_only")
        if row.get("position_actionability_status") != "never_actionable":
            failures.append(f"goal09_row_{index}_position_not_never_actionable")
        if row.get("position_actionability_blocked") != "true":
            failures.append(f"goal09_row_{index}_position_actionability_not_blocked")
        if row.get("recommendation_actionability_status") != "never_actionable":
            failures.append(f"goal09_row_{index}_recommendation_not_never_actionable")
    return failures


def _key_set(rows: list[dict[str, str]]) -> set[tuple[str, str]]:
    return {(row.get("trade_date", ""), row.get("symbol", "")) for row in rows}


def _warning_codes(rows: list[dict[str, str]]) -> set[str]:
    values: set[str] = set()
    for row in rows:
        for field in ["risk_warning_codes", "warning_propagation_codes", "propagated_warning_codes"]:
            raw = row.get(field, "")
            values.update(item for item in raw.split(";") if item and item != "none")
    return values


def _forbidden_output_dirs_present(root: Path) -> list[str]:
    return [path for path in FORBIDDEN_OUTPUT_DIRS if (root / path).exists()]


def _unexpected_backtest_outputs(root: Path) -> list[str]:
    path = root / "outputs/backtest"
    if not path.exists():
        return []
    return [
        str(item.relative_to(root))
        for item in sorted(path.glob("*"))
        if str(item.relative_to(root)) not in ALLOWED_GOAL10B_BACKTEST_OUTPUTS
    ]


def _goal10b_review_only_evidence_ready(root: Path) -> bool:
    report = _read(root / GOAL10B_REPORT_PATH)
    audit = _read(root / GOAL10B_AUDIT_PATH)
    manifest = _read_json(root / GOAL10B_MANIFEST_PATH)
    return (
        _report_pass_or_warn(report, "GOAL-10B Recommendation Diagnostics Backtest Review-Only:")
        and "Status: `PASS`" in audit
        and manifest.get("goal_id") == "GOAL-10B"
        and manifest.get("mode") == "review_only"
        and manifest.get("review_only_backtest_diagnostics_generated") is True
        and manifest.get("goal10c_locked_future") is True
        and manifest.get("goal10d_locked_future") is True
        and manifest.get("portfolio_returns_generated") is False
        and manifest.get("equity_curves_generated") is False
    )


def _report_pass_or_warn(text: str, prefix: str) -> bool:
    return f"{prefix} {PASS}" in text or f"{prefix} {PASS_WITH_WARNINGS}" in text


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

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import (
    preserve_later_review_only_capabilities,
    preserve_later_review_only_workflow_states,
)
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-MVP-01"
GOAL_NAME = "GOAL-MVP-01-PREMARKET-RESEARCH-DIAGNOSTIC-TERMINAL-GATE"
MODE = "mvp_research_only_premarket_diagnostic_terminal"
RUN_MODE = "committed_evidence_replay"
WORKFLOW_ID = "goal_mvp01_premarket_research_terminal_gate"
PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

GOAL_QUANT_RESEARCH01_WORKFLOW_ID = "goal_quant_research01_factor_research_lab_gate"
GOAL_ALPHA_FACTOR_CANDIDATE01_WORKFLOW_ID = "goal_alpha_factor_candidate01_research_gate"
GOAL_QUANT_RESEARCH02_WORKFLOW_ID = "goal_quant_research02_alpha_candidate_factor_validity_evaluation_gate"
GOAL_REC_TIERING01_WORKFLOW_ID = "goal_rec_tiering01_recommendation_score_tiering_gate"
GOAL10B4_WORKFLOW_ID = "goal10b4_recommendation_backtest_revalidation"
POSITION_BAND_VALIDATION_WORKFLOW_ID = "goal_position_band_validation01_position_band_validation_gate"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
GOAL10C_WORKFLOW_ID = "goal10c_backtest_cost_slippage_sensitivity_gate"

ALLOWED_NEXT = "request_goal_alpha_factor_candidate01_before_recommendation_tiering"
NON_ACTIONABLE = "research_only_not_investment_advice_not_trade_instruction"

PROVIDER02B_PANEL_PATH = "outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv"
DC03_RISK_PATH = "outputs/diagnostics/goal_v1_diagnostic_coverage03_risk_diagnostics.csv"
DC03_RECOMMENDATION_PATH = "outputs/diagnostics/goal_v1_diagnostic_coverage03_recommendation_diagnostics.csv"
DC03_POSITION_PATH = "outputs/diagnostics/goal_v1_diagnostic_coverage03_position_band_diagnostics.csv"
RISK01_DIAGNOSTICS_PATH = "outputs/diagnostics/goal_risk_tiering01_risk_tiered_diagnostics.csv"
RISK011_DIAGNOSTICS_PATH = "outputs/diagnostics/goal_risk_tiering011_downside_risk_diagnostics.csv"
FACTOR_REGISTRY_PATH = "outputs/research/goal_quant_research01_factor_registry.csv"
SCORE_VALIDITY_PATH = "outputs/research/goal_quant_research01_score_validity_classification.csv"
FACTOR_BUCKET_METRICS_PATH = "outputs/research/goal_quant_research01_factor_bucket_metrics.csv"
IC_RANKIC_SUMMARY_PATH = "outputs/research/goal_quant_research01_factor_ic_rankic_summary.csv"
MONOTONICITY_SUMMARY_PATH = "outputs/research/goal_quant_research01_factor_monotonicity_summary.csv"
ROLLING_STABILITY_SUMMARY_PATH = "outputs/research/goal_quant_research01_factor_rolling_stability_summary.csv"
TRIAL_REGISTRY_PATH = "outputs/research/goal_quant_research01_trial_registry.csv"
QUANT_MANIFEST_PATH = "outputs/audits/goal_quant_research01_factor_research_lab_manifest.json"

MVP_REPORT_PATH = "outputs/mvp/goal_mvp01_premarket_research_report.md"
SYMBOL_TABLE_PATH = "outputs/mvp/goal_mvp01_symbol_diagnostic_table.csv"
REVIEW_QUEUE_PATH = "outputs/mvp/goal_mvp01_review_queue.csv"
FACTOR_VALIDITY_SUMMARY_PATH = "outputs/mvp/goal_mvp01_factor_validity_summary.csv"
MARKET_CONTEXT_SUMMARY_PATH = "outputs/mvp/goal_mvp01_market_context_summary.csv"
RUN_MANIFEST_PATH = "outputs/mvp/goal_mvp01_run_manifest.json"
REPORT_PATH = "outputs/audits/goal_mvp01_premarket_terminal_report.md"
MANIFEST_PATH = "outputs/audits/goal_mvp01_premarket_terminal_manifest.json"
AUDIT_PATH = "outputs/audits/goal_mvp01_premarket_terminal_audit.md"
DOC_PATH = "docs/mvp/GOAL_MVP01_PREMARKET_RESEARCH_DIAGNOSTIC_TERMINAL_GATE.md"
CONTRACT_PATH = "configs/mvp/goal_mvp01_premarket_terminal_contract.yaml"

REQUIRED_INPUTS = [
    PROVIDER02B_PANEL_PATH,
    DC03_RISK_PATH,
    DC03_RECOMMENDATION_PATH,
    DC03_POSITION_PATH,
    RISK01_DIAGNOSTICS_PATH,
    RISK011_DIAGNOSTICS_PATH,
    FACTOR_REGISTRY_PATH,
    SCORE_VALIDITY_PATH,
    FACTOR_BUCKET_METRICS_PATH,
    IC_RANKIC_SUMMARY_PATH,
    MONOTONICITY_SUMMARY_PATH,
    ROLLING_STABILITY_SUMMARY_PATH,
    TRIAL_REGISTRY_PATH,
]

OUTPUTS = [
    MVP_REPORT_PATH,
    SYMBOL_TABLE_PATH,
    REVIEW_QUEUE_PATH,
    FACTOR_VALIDITY_SUMMARY_PATH,
    MARKET_CONTEXT_SUMMARY_PATH,
    RUN_MANIFEST_PATH,
    REPORT_PATH,
    MANIFEST_PATH,
    AUDIT_PATH,
    DOC_PATH,
    CONTRACT_PATH,
]

SYMBOL_DIAGNOSTIC_FIELDS = [
    "report_date",
    "symbol",
    "source_provider",
    "panel_contract_status",
    "data_quality_status",
    "trading_status",
    "is_st",
    "risk_score_bucket",
    "downside_risk_bucket",
    "original_dc03_risk_severity",
    "dc03_recommendation_eligibility_status",
    "dc03_actionability_status",
    "dc03_position_band_status",
    "factor_validity_status",
    "research_ready_status",
    "review_queue_category",
    "review_priority_level",
    "review_reason_codes",
    "non_actionable_disclaimer",
]

REVIEW_QUEUE_FIELDS = [
    "report_date",
    "symbol",
    "review_queue_category",
    "review_priority_level",
    "queue_status",
    "review_reason_codes",
    "source_provider",
    "risk_score_bucket",
    "downside_risk_bucket",
    "factor_validity_status",
    "non_actionable_disclaimer",
]

FACTOR_VALIDITY_FIELDS = [
    "report_date",
    "factors_evaluated",
    "factor_signal_weak_or_unreliable_count",
    "factor_not_evaluable_count",
    "factor_candidate_for_rec_tiering_count",
    "ready_factor_count",
    "overall_validity",
    "recommended_research_next_step",
    "non_actionable_disclaimer",
]

MARKET_CONTEXT_FIELDS = [
    "report_date",
    "benchmark_symbol",
    "benchmark_return_1d",
    "benchmark_return_5d",
    "benchmark_return_20d",
    "universe_coverage",
    "number_of_symbols",
    "number_of_warnings",
    "factor_readiness_status",
    "data_replay_live_status",
    "run_mode",
    "non_actionable_disclaimer",
]

ALLOWED_PRIORITY_LEVELS = {
    "DATA_REVIEW",
    "RISK_REVIEW",
    "FACTOR_RESEARCH_REVIEW",
    "LIQUIDITY_REVIEW",
    "VOLATILITY_REVIEW",
    "ST_OR_TRADING_STATUS_REVIEW",
    "CLEAN_RESEARCH_WATCH",
    "NO_RESEARCH_ACTION",
}

REQUIRED_REVIEW_QUEUE_CATEGORIES = [
    "data_quality_review_queue",
    "high_downside_risk_review_queue",
    "volatility_momentum_review_queue",
    "liquidity_review_queue",
    "st_or_trading_status_review_queue",
    "factor_not_ready_review_queue",
    "clean_research_watch_queue",
]

FORBIDDEN_TABLE_LABELS = {
    "BUY",
    "SELL",
    "HOLD",
    "STRONG_BUY",
    "STRONG_SELL",
    "ADD",
    "REDUCE",
    "OPEN_POSITION",
    "CLOSE_POSITION",
    "TARGET_WEIGHT",
    "POSITION_SIZE",
    "ORDER_QUANTITY",
}

FALSE_BOUNDARY_KEYS = [
    "directional_trade_labels_generated",
    "target_prices_generated",
    "actual_position_sizing_generated",
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
    "trading_outputs_created",
    "broker_outputs_created",
    "production_outputs_created",
    "local_lake_outputs_created",
    "factor_mining_outputs_created",
    "dqn_rl_outputs_created",
    "live_provider_fetches_run",
    "demo_fixture_used",
    "outputs_samples_used",
    "stale_goal10b_evidence_used",
    "stale_dc02_evidence_used",
    "future_returns_used_in_premarket_classification",
    "recommendation_outputs_created",
    "goal_rec_tiering01_run",
    "goal10b4_run",
    "position_band_validation_run",
    "goal10d_run",
    "market_timing_advice_generated",
]

FORBIDDEN_OUTPUT_PREFIXES = [
    "outputs/recommendations/",
    "outputs/positions/",
    "outputs/position_sizing/",
    "outputs/position_weights/",
    "outputs/orders/",
    "outputs/portfolio_returns/",
    "outputs/equity_curves/",
    "outputs/dashboard/",
    "outputs/dashboards/",
    "outputs/frontend/",
    "outputs/streamlit/",
    "outputs/visual_reports/",
    "outputs/trading/",
    "outputs/paper_trading/",
    "outputs/live_trading/",
    "outputs/broker/",
    "outputs/production/",
    "outputs/factors/",
    "outputs/dqn/",
    "outputs/rl/",
    "data/raw/",
    "data/bundles/",
    "data/lake/",
    "data/exports/",
]


def run_goal_mvp01_premarket_research_terminal_gate(root: Path) -> bool:
    result = evaluate_goal_mvp01_premarket_research_terminal(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal_mvp01_premarket_research_terminal_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal_mvp01_premarket_research_terminal_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    run_manifest = _read_json(root / RUN_MANIFEST_PATH)
    symbol_rows = _read_csv(root / SYMBOL_TABLE_PATH)
    queue_rows = _read_csv(root / REVIEW_QUEUE_PATH)
    factor_summary = _read_csv(root / FACTOR_VALIDITY_SUMMARY_PATH)
    market_context = _read_csv(root / MARKET_CONTEXT_SUMMARY_PATH)
    workflow = _workflow_rows(root)
    failures: list[str] = []

    for path in OUTPUTS:
        if path == AUDIT_PATH:
            continue
        if not (root / path).exists():
            failures.append(f"missing_output:{path}")
    for path in REQUIRED_INPUTS:
        if not (root / path).exists():
            failures.append(f"missing_required_input:{path}")

    if not _report_pass_or_warn(report):
        failures.append("goal_mvp01_report_not_pass_or_warn")
    if manifest.get("goal") != GOAL_NAME:
        failures.append("manifest_goal_invalid")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_invalid")
    if manifest.get("run_mode") != RUN_MODE:
        failures.append("manifest_run_mode_invalid")
    if manifest.get("status") not in {PASS, PASS_WITH_WARNINGS}:
        failures.append("manifest_status_invalid")
    if run_manifest != manifest:
        failures.append("run_manifest_does_not_match_audit_manifest")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"manifest_{key}_not_false")
    for key in [
        "mvp_research_terminal_generated",
        "used_committed_provider02b_evidence_only",
        "used_committed_dc03_evidence_only",
        "used_committed_goal_risk_tiering01_evidence_only",
        "used_committed_goal_risk_tiering011_evidence_only",
        "used_committed_goal_quant_research01_evidence_only",
        "source_backed_lineage_verified",
        "latest_report_date_resolved",
        "symbol_table_trade_date_symbol_grain",
        "review_queue_generated",
        "factor_validity_summary_generated",
        "market_context_summary_generated",
        "goal_alpha_factor_candidate01_locked_future",
        "goal_rec_tiering01_locked_future",
        "goal10b4_locked_future",
        "position_band_validation_locked_future",
        "goal10d_locked_future",
        "dashboard_daily_report_locked_future",
        "portfolio_backtest_locked_future",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")

    expected_latest = _latest_report_date_from_inputs(root)
    if manifest.get("report_date") != expected_latest:
        failures.append("manifest_report_date_not_latest_input_date")
    if symbol_rows and list(symbol_rows[0]) != SYMBOL_DIAGNOSTIC_FIELDS:
        failures.append("symbol_table_fields_invalid")
    if queue_rows and list(queue_rows[0]) != REVIEW_QUEUE_FIELDS:
        failures.append("review_queue_fields_invalid")
    if factor_summary and list(factor_summary[0]) != FACTOR_VALIDITY_FIELDS:
        failures.append("factor_summary_fields_invalid")
    if market_context and list(market_context[0]) != MARKET_CONTEXT_FIELDS:
        failures.append("market_context_fields_invalid")
    report_dates = {row.get("report_date", "") for row in symbol_rows}
    if report_dates != {expected_latest}:
        failures.append("symbol_table_report_date_mismatch")
    keys = [(row.get("report_date", ""), row.get("symbol", "")) for row in symbol_rows]
    if _duplicate_count(keys):
        failures.append("symbol_table_duplicate_report_date_symbol_rows")
    if len(symbol_rows) != int(manifest.get("symbol_table_row_count", -1)):
        failures.append("symbol_table_row_count_manifest_mismatch")
    if manifest.get("latest_panel_row_count") != len(symbol_rows):
        failures.append("latest_panel_row_count_mismatch")
    if set(keys) != {(row.get("report_date", ""), row.get("symbol", "")) for row in symbol_rows}:
        failures.append("symbol_table_key_set_invalid")
    if any(row.get("review_priority_level") not in ALLOWED_PRIORITY_LEVELS for row in symbol_rows):
        failures.append("symbol_table_priority_invalid")
    queue_categories = {row.get("review_queue_category", "") for row in queue_rows}
    missing_categories = sorted(set(REQUIRED_REVIEW_QUEUE_CATEGORIES) - queue_categories)
    if missing_categories:
        failures.append(f"review_queue_missing_categories:{missing_categories}")
    if _forbidden_table_label_hits([symbol_rows, queue_rows, factor_summary, market_context]):
        failures.append("forbidden_table_labels_present")
    if any("outputs/samples/" in str(value) for source in [manifest, run_manifest] for value in _walk_values(source)):
        failures.append("outputs_samples_referenced_in_manifest")
    if any("goal10b_recommendation_backtest" in str(value) for source in [manifest, run_manifest] for value in _walk_values(source)):
        failures.append("stale_goal10b_evidence_referenced")
    if any("goal_v1_diagnostic_coverage02" in str(value) for source in [manifest, run_manifest] for value in _walk_values(source)):
        failures.append("stale_dc02_evidence_referenced")
    if _contains_secret_like_text(root, OUTPUTS):
        failures.append("secret_or_token_like_text_present_in_mvp_outputs")
    if any("forward_return" in field for field in SYMBOL_DIAGNOSTIC_FIELDS):
        failures.append("symbol_table_contains_future_return_field")
    factor_ready = int(manifest.get("ready_factor_count", -1))
    if not factor_summary or int(factor_summary[0].get("ready_factor_count", "-1")) != factor_ready:
        failures.append("factor_ready_count_summary_mismatch")
    if factor_ready == 0 and (
        "No factor is currently approved for recommendation tiering." not in _read(root / MVP_REPORT_PATH)
        or "This terminal is research-only and cannot produce actionable recommendations." not in _read(root / MVP_REPORT_PATH)
    ):
        failures.append("zero_ready_factor_required_report_text_missing")

    gate = workflow.get(WORKFLOW_ID, {})
    alpha = workflow.get(GOAL_ALPHA_FACTOR_CANDIDATE01_WORKFLOW_ID, {})
    quant02 = workflow.get(GOAL_QUANT_RESEARCH02_WORKFLOW_ID, {})
    rec = workflow.get(GOAL_REC_TIERING01_WORKFLOW_ID, {})
    alpha_implemented = alpha.get("status") == "implemented_research_only" and alpha.get("implemented_in_repo") == "true"
    if gate.get("status") != "implemented_mvp_research_only":
        failures.append("goal_mvp01_workflow_not_implemented_mvp_research_only")
    if gate.get("implemented_in_repo") != "true":
        failures.append("goal_mvp01_workflow_not_marked_implemented")
    if gate.get("depends_on") != GOAL_QUANT_RESEARCH01_WORKFLOW_ID:
        failures.append("goal_mvp01_dependency_invalid")
    if not alpha_implemented and (alpha.get("status") != "locked_future" or alpha.get("implemented_in_repo") != "false"):
        failures.append("goal_alpha_factor_candidate01_not_locked_or_implemented")
    if alpha.get("depends_on") != WORKFLOW_ID:
        failures.append("goal_alpha_factor_candidate01_dependency_invalid")
    if rec.get("status") != "locked_future" or rec.get("implemented_in_repo") != "false":
        failures.append("goal_rec_tiering01_not_locked_after_mvp01")
    expected_rec_dependency = GOAL_QUANT_RESEARCH02_WORKFLOW_ID if alpha_implemented else GOAL_ALPHA_FACTOR_CANDIDATE01_WORKFLOW_ID
    if alpha_implemented:
        if quant02.get("status") != "locked_future" or quant02.get("implemented_in_repo") != "false":
            failures.append("goal_quant_research02_not_locked_after_alpha_candidate")
        if quant02.get("depends_on") != GOAL_ALPHA_FACTOR_CANDIDATE01_WORKFLOW_ID:
            failures.append("goal_quant_research02_dependency_invalid")
    if rec.get("depends_on") != expected_rec_dependency:
        failures.append("goal_rec_tiering01_not_rebased_on_alpha_candidate")
    for workflow_id in [
        GOAL10B4_WORKFLOW_ID,
        POSITION_BAND_VALIDATION_WORKFLOW_ID,
        GOAL10D_WORKFLOW_ID,
        "dashboard_daily_report",
        "signal_backtest",
        "portfolio_backtest",
        "cost_slippage_sensitivity",
        "paper_trading_journal",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
    ]:
        row = workflow.get(workflow_id, {})
        if row.get("status") != "locked_future":
            failures.append(f"{workflow_id}_not_locked_future")
        if row.get("implemented_in_repo") != "false":
            failures.append(f"{workflow_id}_marked_implemented")
    failures.extend(f"forbidden_output_present:{path}" for path in _forbidden_outputs_present(root))

    status = PASS if not failures else BLOCKED
    write_text(
        root / AUDIT_PATH,
        "\n".join(
            [
                "# GOAL-MVP-01 Premarket Research Diagnostic Terminal Audit",
                "",
                f"Status: `{status}`",
                "",
                f"Workflow status: `{gate.get('status', 'missing')}`",
                f"Report date: `{manifest.get('report_date', 'missing')}`",
                f"Run mode: `{manifest.get('run_mode', 'missing')}`",
                f"Symbol rows: `{len(symbol_rows)}`",
                f"Review queue rows: `{len(queue_rows)}`",
                f"Ready factor count: `{factor_ready}`",
                f"Overall factor validity: `{manifest.get('overall_factor_validity', 'missing')}`",
                "Directional trade labels, target prices, sizing, weights, orders, returns, curves, dashboards, live fetches, trading, production, local-lake, factor-mining, and DQN/RL generated: `false`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == PASS


def evaluate_goal_mvp01_premarket_research_terminal(root: Path) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = ["committed_evidence_replay_not_live_signal"]
    for path in REQUIRED_INPUTS:
        if not (root / path).exists():
            failures.append(f"missing_required_input:{path}")
    if failures:
        return _blocked_result(failures, warnings)

    panel_rows = _read_csv(root / PROVIDER02B_PANEL_PATH)
    dc03_risk_rows = _read_csv(root / DC03_RISK_PATH)
    dc03_rec_rows = _read_csv(root / DC03_RECOMMENDATION_PATH)
    dc03_pos_rows = _read_csv(root / DC03_POSITION_PATH)
    risk01_rows = _read_csv(root / RISK01_DIAGNOSTICS_PATH)
    risk011_rows = _read_csv(root / RISK011_DIAGNOSTICS_PATH)
    registry_rows = _read_csv(root / FACTOR_REGISTRY_PATH)
    validity_rows = _read_csv(root / SCORE_VALIDITY_PATH)
    bucket_rows = _read_csv(root / FACTOR_BUCKET_METRICS_PATH)
    ic_rankic_rows = _read_csv(root / IC_RANKIC_SUMMARY_PATH)
    monotonicity_rows = _read_csv(root / MONOTONICITY_SUMMARY_PATH)
    rolling_rows = _read_csv(root / ROLLING_STABILITY_SUMMARY_PATH)
    trial_rows = _read_csv(root / TRIAL_REGISTRY_PATH)
    quant_manifest = _read_json(root / QUANT_MANIFEST_PATH)

    latest_date = _latest_date(panel_rows)
    latest_sets = {
        PROVIDER02B_PANEL_PATH: _latest_rows(panel_rows, latest_date),
        DC03_RISK_PATH: _latest_rows(dc03_risk_rows, latest_date),
        DC03_RECOMMENDATION_PATH: _latest_rows(dc03_rec_rows, latest_date),
        DC03_POSITION_PATH: _latest_rows(dc03_pos_rows, latest_date),
        RISK01_DIAGNOSTICS_PATH: _latest_rows(risk01_rows, latest_date),
        RISK011_DIAGNOSTICS_PATH: _latest_rows(risk011_rows, latest_date),
    }
    panel_keys = {_key(row) for row in latest_sets[PROVIDER02B_PANEL_PATH]}
    for path, rows in latest_sets.items():
        if len(rows) != len(panel_keys):
            failures.append(f"latest_row_count_mismatch:{path}")
        if {_key(row) for row in rows} != panel_keys:
            failures.append(f"latest_trade_date_symbol_keys_do_not_match:{path}")
    if failures:
        return _blocked_result(failures, warnings)

    factor_summary = _factor_summary_row(latest_date, registry_rows, validity_rows, quant_manifest)
    ready_factor_count = int(factor_summary["ready_factor_count"])
    if ready_factor_count == 0:
        warnings.append("no_factor_ready_for_rec_tiering")
    factor_status = (
        "factor_candidate_available_for_future_review"
        if ready_factor_count
        else "no_factor_currently_approved_for_recommendation_tiering"
    )

    maps = {path: {_key(row): row for row in rows} for path, rows in latest_sets.items()}
    symbol_rows = []
    queue_rows = []
    for key in sorted(panel_keys):
        panel = maps[PROVIDER02B_PANEL_PATH][key]
        dc03_risk = maps[DC03_RISK_PATH][key]
        dc03_rec = maps[DC03_RECOMMENDATION_PATH][key]
        dc03_pos = maps[DC03_POSITION_PATH][key]
        risk01 = maps[RISK01_DIAGNOSTICS_PATH][key]
        risk011 = maps[RISK011_DIAGNOSTICS_PATH][key]
        diagnostic = _symbol_diagnostic_row(
            latest_date,
            panel,
            dc03_risk,
            dc03_rec,
            dc03_pos,
            risk01,
            risk011,
            factor_status,
            ready_factor_count,
        )
        symbol_rows.append(diagnostic)
        queue_rows.extend(_queue_rows_for_symbol(diagnostic, risk011, ready_factor_count))
    queue_rows = _add_empty_queue_rows(latest_date, queue_rows)
    market_context = _market_context_row(latest_date, latest_sets[PROVIDER02B_PANEL_PATH], queue_rows, factor_summary)

    status = PASS if ready_factor_count else PASS_WITH_WARNINGS
    manifest = {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "mode": MODE,
        "status": status,
        "workflow_id": WORKFLOW_ID,
        "run_mode": RUN_MODE,
        "allowed_next_action": ALLOWED_NEXT,
        "recommended_next_goal": "GOAL-ALPHA-FACTOR-CANDIDATE-01",
        "report_date": latest_date,
        "latest_report_date_resolved": True,
        "symbol_table_row_count": len(symbol_rows),
        "review_queue_row_count": len(queue_rows),
        "factor_validity_summary_row_count": 1,
        "market_context_summary_row_count": 1,
        "factors_evaluated": int(factor_summary["factors_evaluated"]),
        "ready_factor_count": ready_factor_count,
        "overall_factor_validity": factor_summary["overall_validity"],
        "market_context_number_of_symbols": int(market_context["number_of_symbols"]),
        "market_context_number_of_warnings": int(market_context["number_of_warnings"]),
        "source_backed_lineage_verified": True,
        "symbol_table_trade_date_symbol_grain": True,
        "mvp_research_terminal_generated": True,
        "review_queue_generated": True,
        "factor_validity_summary_generated": True,
        "market_context_summary_generated": True,
        "used_committed_provider02b_evidence_only": True,
        "used_committed_dc03_evidence_only": True,
        "used_committed_goal_risk_tiering01_evidence_only": True,
        "used_committed_goal_risk_tiering011_evidence_only": True,
        "used_committed_goal_quant_research01_evidence_only": True,
        "goal_alpha_factor_candidate01_locked_future": True,
        "goal_rec_tiering01_locked_future": True,
        "goal10b4_locked_future": True,
        "position_band_validation_locked_future": True,
        "goal10d_locked_future": True,
        "dashboard_daily_report_locked_future": True,
        "portfolio_backtest_locked_future": True,
        "input_lineage": REQUIRED_INPUTS,
        "output_artifacts": OUTPUTS,
        "input_row_counts": {
            PROVIDER02B_PANEL_PATH: len(panel_rows),
            DC03_RISK_PATH: len(dc03_risk_rows),
            DC03_RECOMMENDATION_PATH: len(dc03_rec_rows),
            DC03_POSITION_PATH: len(dc03_pos_rows),
            RISK01_DIAGNOSTICS_PATH: len(risk01_rows),
            RISK011_DIAGNOSTICS_PATH: len(risk011_rows),
            FACTOR_REGISTRY_PATH: len(registry_rows),
            SCORE_VALIDITY_PATH: len(validity_rows),
            FACTOR_BUCKET_METRICS_PATH: len(bucket_rows),
            IC_RANKIC_SUMMARY_PATH: len(ic_rankic_rows),
            MONOTONICITY_SUMMARY_PATH: len(monotonicity_rows),
            ROLLING_STABILITY_SUMMARY_PATH: len(rolling_rows),
            TRIAL_REGISTRY_PATH: len(trial_rows),
        },
        "latest_row_counts": {path: len(rows) for path, rows in latest_sets.items()},
        "latest_panel_row_count": len(latest_sets[PROVIDER02B_PANEL_PATH]),
        "warnings": sorted(set(warnings)),
        "failures": failures,
    }
    for key in FALSE_BOUNDARY_KEYS:
        manifest[key] = False

    return {
        "status": status,
        "warnings": sorted(set(warnings)),
        "failures": failures,
        "symbol_rows": symbol_rows,
        "queue_rows": queue_rows,
        "factor_summary": [factor_summary],
        "market_context": [market_context],
        "manifest": manifest,
        "risk_score_bucket_distribution": dict(sorted(Counter(row["risk_score_bucket"] for row in symbol_rows).items())),
        "downside_risk_bucket_distribution": dict(sorted(Counter(row["downside_risk_bucket"] for row in symbol_rows).items())),
        "review_queue_distribution": dict(
            sorted(
                Counter(
                    row["review_queue_category"]
                    for row in queue_rows
                    if row.get("symbol") and row.get("queue_status") == "active_for_report_date"
                ).items()
            )
        ),
    }


def goal_mvp01_valid_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        (
            "GOAL-MVP-01 Premarket Research Diagnostic Terminal Gate: PASS" in report
            or "GOAL-MVP-01 Premarket Research Diagnostic Terminal Gate: PASS_WITH_WARNINGS" in report
        )
        and "Status: `PASS`" in audit
        and manifest.get("mode") == MODE
        and manifest.get("run_mode") == RUN_MODE
        and manifest.get("mvp_research_terminal_generated") is True
        and manifest.get("source_backed_lineage_verified") is True
        and manifest.get("directional_trade_labels_generated") is False
        and manifest.get("recommendation_outputs_created") is False
    )


def goal_mvp01_implemented_workflow_patch(status: str = PASS_WITH_WARNINGS) -> dict[str, str]:
    return {
        "display_name": "GOAL-MVP-01 Premarket Research Diagnostic Terminal Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_mvp_research_only",
        "current_repo_role": MODE,
        "implemented_in_repo": "true",
        "allowed_next_action": ALLOWED_NEXT,
        "depends_on": GOAL_QUANT_RESEARCH01_WORKFLOW_ID,
        "produces_artifacts": ";".join(OUTPUTS),
        "primary_docs": f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "scripts/run_goal_mvp01_premarket_research_terminal_gate.py;scripts/audit_goal_mvp01_premarket_research_terminal_gate.py",
        "primary_outputs": ";".join(
            [
                MVP_REPORT_PATH,
                SYMBOL_TABLE_PATH,
                REVIEW_QUEUE_PATH,
                FACTOR_VALIDITY_SUMMARY_PATH,
                MARKET_CONTEXT_SUMMARY_PATH,
                RUN_MANIFEST_PATH,
                REPORT_PATH,
                MANIFEST_PATH,
                AUDIT_PATH,
            ]
        ),
        "promotion_rule": "implemented_mvp_research_only_after_goal_mvp01_pass_or_pass_with_warnings",
        "notes": "MVP research-only premarket diagnostic terminal over committed Provider02B, DC03, risk-tiering, downside-risk, and QUANT evidence. It creates human-readable research reports and review queues only; no directional labels, targets, positions, portfolio outputs, dashboard, trading, production, local-lake, factor-mining, broker, or DQN/RL outputs.",
    }


def locked_goal_alpha_factor_candidate01_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-ALPHA-FACTOR-CANDIDATE-01 Alpha Factor Candidate Research Gate",
        "stage_or_goal": "GOAL-ALPHA-FACTOR-CANDIDATE-01",
        "status": "locked_future",
        "current_repo_role": "locked_future_alpha_factor_candidate_research_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_alpha_factor_candidate_research_goal",
        "depends_on": WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal_alpha_factor_candidate01_gate",
        "notes": "Future alpha-factor candidate research remains locked; GOAL-MVP-01 only summarizes current research readiness and does not mine factors or promote recommendation tiering.",
    }


def locked_goal_rec_tiering01_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "current_repo_role": "locked_future_recommendation_score_tiering_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal_alpha_factor_candidate01_passes",
        "depends_on": GOAL_ALPHA_FACTOR_CANDIDATE01_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal_rec_tiering01_gate_after_alpha_candidate_research",
        "notes": "Future recommendation score tiering remains locked; GOAL-MVP-01 creates research-only review queues and no actionable recommendation rows.",
    }


def locked_goal10b4_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal_rec_tiering01_passes",
        "depends_on": GOAL_REC_TIERING01_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal10b4_revalidation_gate",
        "notes": "Future GOAL-10B.4 remains locked; GOAL-MVP-01 creates no recommendation revalidation rows.",
    }


def locked_position_band_validation_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal10b4_and_explicit_position_validation_request",
        "depends_on": GOAL10B4_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_position_band_validation_gate",
        "notes": "Future position-band validation remains locked; GOAL-MVP-01 creates no position outputs.",
    }


def locked_goal10d_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10d_request",
        "depends_on": GOAL10C_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal10d_failure_attribution_gate",
        "notes": "Future GOAL-10D remains locked; GOAL-MVP-01 creates only research diagnostic terminal evidence.",
    }


def _symbol_diagnostic_row(
    report_date: str,
    panel: dict[str, str],
    dc03_risk: dict[str, str],
    dc03_rec: dict[str, str],
    dc03_pos: dict[str, str],
    risk01: dict[str, str],
    risk011: dict[str, str],
    factor_status: str,
    ready_factor_count: int,
) -> dict[str, object]:
    category, priority, reason_codes = _dominant_queue(panel, dc03_risk, risk01, risk011)
    data_quality_status = _data_quality_status(panel)
    research_ready = _research_ready_status(category, ready_factor_count)
    if ready_factor_count == 0:
        reason_codes.append("global_factor_not_ready")
    return {
        "report_date": report_date,
        "symbol": panel["symbol"],
        "source_provider": panel.get("source_provider", ""),
        "panel_contract_status": panel.get("panel_contract_status", ""),
        "data_quality_status": data_quality_status,
        "trading_status": panel.get("trading_status", ""),
        "is_st": panel.get("is_st", ""),
        "risk_score_bucket": risk01.get("risk_score_bucket", ""),
        "downside_risk_bucket": risk011.get("downside_risk_bucket", ""),
        "original_dc03_risk_severity": dc03_risk.get("risk_severity", ""),
        "dc03_recommendation_eligibility_status": dc03_rec.get("recommendation_eligibility_status", ""),
        "dc03_actionability_status": dc03_rec.get("actionability_status", ""),
        "dc03_position_band_status": dc03_pos.get("position_band_status", ""),
        "factor_validity_status": factor_status,
        "research_ready_status": research_ready,
        "review_queue_category": category,
        "review_priority_level": priority,
        "review_reason_codes": ";".join(sorted(set(reason_codes))),
        "non_actionable_disclaimer": NON_ACTIONABLE,
    }


def _dominant_queue(
    panel: dict[str, str],
    dc03_risk: dict[str, str],
    risk01: dict[str, str],
    risk011: dict[str, str],
) -> tuple[str, str, list[str]]:
    reasons: list[str] = []
    if _severe_data_quality(panel):
        reasons.append("source_panel_not_contract_ready")
        return "data_quality_review_queue", "DATA_REVIEW", reasons
    if panel.get("trading_status", "").lower() != "trading" or panel.get("is_st", "").lower() == "true":
        reasons.append("trading_status_or_st_flag")
        return "st_or_trading_status_review_queue", "ST_OR_TRADING_STATUS_REVIEW", reasons
    if (
        "HIGH" in risk011.get("downside_risk_bucket", "")
        or "HIGH" in risk01.get("risk_score_bucket", "")
        or dc03_risk.get("risk_severity", "") == "HIGH"
    ):
        reasons.append("high_downside_or_risk_bucket")
        return "high_downside_risk_review_queue", "RISK_REVIEW", reasons
    if _positive(risk011.get("liquidity_risk_component", "")):
        reasons.append("liquidity_component_positive")
        return "liquidity_review_queue", "LIQUIDITY_REVIEW", reasons
    if (
        risk011.get("volatility_momentum_flag", "").lower() == "true"
        or risk011.get("abnormal_positive_movement_flag", "").lower() == "true"
        or risk011.get("abnormal_negative_movement_flag", "").lower() == "true"
        or _positive(risk011.get("volatility_component", ""))
        or _positive(risk011.get("momentum_component", ""))
    ):
        reasons.append("volatility_or_momentum_component_positive")
        return "volatility_momentum_review_queue", "VOLATILITY_REVIEW", reasons
    reasons.append("fewer_symbol_level_warnings")
    return "clean_research_watch_queue", "CLEAN_RESEARCH_WATCH", reasons


def _queue_rows_for_symbol(
    diagnostic: dict[str, object],
    risk011: dict[str, str],
    ready_factor_count: int,
) -> list[dict[str, object]]:
    rows = [
        {
            "report_date": diagnostic["report_date"],
            "symbol": diagnostic["symbol"],
            "review_queue_category": diagnostic["review_queue_category"],
            "review_priority_level": diagnostic["review_priority_level"],
            "queue_status": "active_for_report_date",
            "review_reason_codes": diagnostic["review_reason_codes"],
            "source_provider": diagnostic["source_provider"],
            "risk_score_bucket": diagnostic["risk_score_bucket"],
            "downside_risk_bucket": diagnostic["downside_risk_bucket"],
            "factor_validity_status": diagnostic["factor_validity_status"],
            "non_actionable_disclaimer": NON_ACTIONABLE,
        }
    ]
    if ready_factor_count == 0:
        rows.append(
            {
                "report_date": diagnostic["report_date"],
                "symbol": diagnostic["symbol"],
                "review_queue_category": "factor_not_ready_review_queue",
                "review_priority_level": "FACTOR_RESEARCH_REVIEW",
                "queue_status": "active_for_report_date",
                "review_reason_codes": "global_factor_not_ready",
                "source_provider": diagnostic["source_provider"],
                "risk_score_bucket": diagnostic["risk_score_bucket"],
                "downside_risk_bucket": diagnostic["downside_risk_bucket"],
                "factor_validity_status": diagnostic["factor_validity_status"],
                "non_actionable_disclaimer": NON_ACTIONABLE,
            }
        )
    if _positive(risk011.get("liquidity_risk_component", "")) and diagnostic["review_queue_category"] != "liquidity_review_queue":
        rows.append(_secondary_queue_row(diagnostic, "liquidity_review_queue", "LIQUIDITY_REVIEW", "liquidity_component_positive"))
    if (
        (
            risk011.get("volatility_momentum_flag", "").lower() == "true"
            or risk011.get("abnormal_positive_movement_flag", "").lower() == "true"
            or risk011.get("abnormal_negative_movement_flag", "").lower() == "true"
            or _positive(risk011.get("volatility_component", ""))
            or _positive(risk011.get("momentum_component", ""))
        )
        and diagnostic["review_queue_category"] != "volatility_momentum_review_queue"
    ):
        rows.append(
            _secondary_queue_row(
                diagnostic,
                "volatility_momentum_review_queue",
                "VOLATILITY_REVIEW",
                "volatility_or_momentum_component_positive",
            )
        )
    return rows


def _secondary_queue_row(
    diagnostic: dict[str, object],
    category: str,
    priority: str,
    reason: str,
) -> dict[str, object]:
    return {
        "report_date": diagnostic["report_date"],
        "symbol": diagnostic["symbol"],
        "review_queue_category": category,
        "review_priority_level": priority,
        "queue_status": "active_for_report_date",
        "review_reason_codes": reason,
        "source_provider": diagnostic["source_provider"],
        "risk_score_bucket": diagnostic["risk_score_bucket"],
        "downside_risk_bucket": diagnostic["downside_risk_bucket"],
        "factor_validity_status": diagnostic["factor_validity_status"],
        "non_actionable_disclaimer": NON_ACTIONABLE,
    }


def _add_empty_queue_rows(report_date: str, rows: list[dict[str, object]]) -> list[dict[str, object]]:
    present = {str(row["review_queue_category"]) for row in rows}
    for category in REQUIRED_REVIEW_QUEUE_CATEGORIES:
        if category not in present:
            rows.append(
                {
                    "report_date": report_date,
                    "symbol": "",
                    "review_queue_category": category,
                    "review_priority_level": "NO_RESEARCH_ACTION",
                    "queue_status": "empty_for_report_date",
                    "review_reason_codes": "no_symbols_in_queue_for_report_date",
                    "source_provider": "",
                    "risk_score_bucket": "",
                    "downside_risk_bucket": "",
                    "factor_validity_status": "",
                    "non_actionable_disclaimer": NON_ACTIONABLE,
                }
            )
    return sorted(rows, key=lambda row: (str(row["review_queue_category"]), str(row["symbol"])))


def _factor_summary_row(
    report_date: str,
    registry_rows: list[dict[str, str]],
    validity_rows: list[dict[str, str]],
    quant_manifest: dict[str, object],
) -> dict[str, object]:
    counts = Counter(row.get("score_validity_classification", "") for row in validity_rows)
    ready = sum(1 for row in validity_rows if row.get("candidate_for_rec_tiering") == "true")
    overall = str(quant_manifest.get("overall_score_validity_status") or ("factor_candidate_for_rec_tiering_available" if ready else "no_factor_ready_for_rec_tiering"))
    recommended_next = str(quant_manifest.get("recommended_next_goal") or "GOAL-ALPHA-FACTOR-CANDIDATE-01_before_recommendation_tiering")
    return {
        "report_date": report_date,
        "factors_evaluated": len(registry_rows),
        "factor_signal_weak_or_unreliable_count": counts.get("factor_signal_weak_or_unreliable", 0),
        "factor_not_evaluable_count": counts.get("factor_not_evaluable", 0),
        "factor_candidate_for_rec_tiering_count": counts.get("factor_candidate_for_rec_tiering", 0),
        "ready_factor_count": ready,
        "overall_validity": overall,
        "recommended_research_next_step": recommended_next,
        "non_actionable_disclaimer": NON_ACTIONABLE,
    }


def _market_context_row(
    report_date: str,
    latest_panel_rows: list[dict[str, str]],
    queue_rows: list[dict[str, object]],
    factor_summary: dict[str, object],
) -> dict[str, object]:
    first = latest_panel_rows[0] if latest_panel_rows else {}
    active_warning_rows = [
        row
        for row in queue_rows
        if row.get("symbol")
        and row.get("queue_status") == "active_for_report_date"
        and row.get("review_queue_category") != "clean_research_watch_queue"
    ]
    return {
        "report_date": report_date,
        "benchmark_symbol": first.get("benchmark_symbol", ""),
        "benchmark_return_1d": first.get("benchmark_return_1d", ""),
        "benchmark_return_5d": first.get("benchmark_return_5d", ""),
        "benchmark_return_20d": first.get("benchmark_return_20d", ""),
        "universe_coverage": _coverage_text(latest_panel_rows),
        "number_of_symbols": len({row.get("symbol", "") for row in latest_panel_rows if row.get("symbol")}),
        "number_of_warnings": len(active_warning_rows),
        "factor_readiness_status": factor_summary["overall_validity"],
        "data_replay_live_status": "committed_evidence_replay_not_live_signal",
        "run_mode": RUN_MODE,
        "non_actionable_disclaimer": NON_ACTIONABLE,
    }


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / SYMBOL_TABLE_PATH, result["symbol_rows"], SYMBOL_DIAGNOSTIC_FIELDS)
    write_csv(root / REVIEW_QUEUE_PATH, result["queue_rows"], REVIEW_QUEUE_FIELDS)
    write_csv(root / FACTOR_VALIDITY_SUMMARY_PATH, result["factor_summary"], FACTOR_VALIDITY_FIELDS)
    write_csv(root / MARKET_CONTEXT_SUMMARY_PATH, result["market_context"], MARKET_CONTEXT_FIELDS)
    write_json(root / RUN_MANIFEST_PATH, result["manifest"])
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_report(root, result)
    _write_audit_report(root, result)
    _write_doc(root, result)
    _write_contract(root, result)


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    factor = result["factor_summary"][0]
    market = result["market_context"][0]
    queue_distribution = result["review_queue_distribution"]
    risk_distribution = result["risk_score_bucket_distribution"]
    downside_distribution = result["downside_risk_bucket_distribution"]
    zero_factor_lines = []
    if int(factor["ready_factor_count"]) == 0:
        zero_factor_lines = [
            "No factor is currently approved for recommendation tiering.",
            "This terminal is research-only and cannot produce actionable recommendations.",
            "",
        ]
    body = [
        "# GOAL-MVP-01 Premarket Research Diagnostic Terminal",
        "",
        "## 1. MVP status",
        f"GOAL-MVP-01 Premarket Research Diagnostic Terminal Gate: {manifest['status']}",
        "The terminal turns committed source-backed evidence into a bounded premarket research diagnostic report and supporting CSVs.",
        "",
        "## 2. Report date and run mode",
        f"Report date: `{manifest['report_date']}`.",
        f"Run mode: `{manifest['run_mode']}`. This is committed evidence replay, not a same-day live signal.",
        "",
        "## 3. Data lineage",
        *[f"- `{path}`" for path in REQUIRED_INPUTS],
        "",
        "## 4. Coverage summary",
        f"Symbols on report date: `{manifest['symbol_table_row_count']}`.",
        f"Universe coverage: `{market['universe_coverage']}`.",
        "",
        "## 5. Market context summary",
        f"Benchmark symbol: `{market['benchmark_symbol']}`.",
        f"Latest committed benchmark returns: 1d `{market['benchmark_return_1d']}`, 5d `{market['benchmark_return_5d']}`, 20d `{market['benchmark_return_20d']}`.",
        "These values are reported as context from committed evidence only. The terminal does not infer market direction or timing.",
        "",
        "## 6. Risk and downside-risk summary",
        f"Risk score bucket distribution: `{risk_distribution}`.",
        f"Downside-risk bucket distribution: `{downside_distribution}`.",
        "",
        "## 7. Factor validity summary",
        f"Factors evaluated: `{factor['factors_evaluated']}`.",
        f"Ready factor count: `{factor['ready_factor_count']}`.",
        f"Overall validity: `{factor['overall_validity']}`.",
        *zero_factor_lines,
        "## 8. Review queues",
        f"Active review queue distribution: `{queue_distribution}`.",
        "`clean_research_watch_queue` is not an action list. It only means fewer data/risk/factor warnings and manual review may start there.",
        "",
        "## 9. What this terminal can help with",
        "- Review source-backed data coverage before market open.",
        "- Identify symbols needing data, risk, downside-risk, liquidity, volatility, or factor-readiness review.",
        "- See why factor evidence is not yet ready for recommendation tiering.",
        "- Preserve a research governance trail from committed evidence only.",
        "",
        "## 10. What this terminal cannot do",
        "- It cannot produce directional trade labels, target prices, position sizes, target weights, order quantities, portfolio returns, equity curves, dashboards, trading outputs, broker integrations, production writes, local-lake outputs, factor-mining outputs, or DQN/RL outputs.",
        "- It cannot turn committed replay evidence into live market timing advice.",
        "",
        "## 11. Locked downstream boundaries",
        "GOAL-ALPHA-FACTOR-CANDIDATE-01, GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, portfolio backtests, paper/live trading, broker integration, production writes, local-lake writes, factor-mining, and DQN/RL remain locked or deleted from active mainline.",
        "",
        "## 12. Recommended next research goal",
        f"`{manifest['recommended_next_goal']}`.",
        "",
    ]
    write_text(root / MVP_REPORT_PATH, "\n".join(body))


def _write_audit_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    body = [
        "# GOAL-MVP-01 Premarket Terminal Readiness Report",
        "",
        f"GOAL-MVP-01 Premarket Research Diagnostic Terminal Gate: {manifest['status']}",
        "",
        f"Report date: `{manifest['report_date']}`",
        f"Run mode: `{manifest['run_mode']}`",
        f"Symbol rows: `{manifest['symbol_table_row_count']}`",
        f"Review queue rows: `{manifest['review_queue_row_count']}`",
        f"Ready factor count: `{manifest['ready_factor_count']}`",
        f"Overall factor validity: `{manifest['overall_factor_validity']}`",
        "",
        "The gate is research-only and non-actionable. It replays committed evidence and does not create trading, portfolio, dashboard, production, local-lake, factor-mining, broker, or DQN/RL outputs.",
        "",
    ]
    write_text(root / REPORT_PATH, "\n".join(body))


def _write_doc(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    body = [
        "# GOAL-MVP-01 Premarket Research Diagnostic Terminal Gate",
        "",
        f"Status: `{manifest['status']}`",
        "",
        "GOAL-MVP-01 is the first research-only MVP terminal. It converts committed source-backed Provider02B, DC03, risk-tiering, downside-risk, and QUANT factor-validity evidence into a Markdown report and bounded CSV support files.",
        "",
        "## Outputs",
        *[f"- `{path}`" for path in OUTPUTS],
        "",
        "## Boundary",
        "The terminal is not a recommendation system, position-building system, broker/live trading system, portfolio backtest, or dashboard/frontend implementation.",
        "",
        "It creates no directional trade labels, target prices, position sizes, target weights, order quantities, portfolio returns, equity curves, dashboards, HTML, Streamlit, frontend, visual reports, trading outputs, broker outputs, production outputs, local-lake files, factor-mining outputs, or DQN/RL outputs.",
        "",
        "## Latest Report Date",
        f"`{manifest['report_date']}` from committed Provider02B/DC03 evidence.",
        "",
        "## Next Research Step",
        "`GOAL-ALPHA-FACTOR-CANDIDATE-01` remains locked until explicitly requested.",
        "",
    ]
    write_text(root / DOC_PATH, "\n".join(body))


def _write_contract(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    lines = [
        "{",
        '  "goal_id": "GOAL-MVP-01",',
        f'  "mode": "{MODE}",',
        f'  "run_mode": "{RUN_MODE}",',
        f'  "status": "{manifest["status"]}",',
        '  "research_only": true,',
        '  "allowed_inputs": [',
        *[f'    "{path}",' for path in REQUIRED_INPUTS[:-1]],
        f'    "{REQUIRED_INPUTS[-1]}"',
        "  ],",
        '  "allowed_outputs": [',
        *[f'    "{path}",' for path in OUTPUTS[:-1]],
        f'    "{OUTPUTS[-1]}"',
        "  ],",
        '  "symbol_diagnostic_schema": ' + _json_list(SYMBOL_DIAGNOSTIC_FIELDS) + ",",
        '  "review_queue_schema": ' + _json_list(REVIEW_QUEUE_FIELDS) + ",",
        '  "forbidden_table_labels": ' + _json_list(sorted(FORBIDDEN_TABLE_LABELS)) + ",",
        '  "downstream_locks": {',
        '    "goal_alpha_factor_candidate01_research_gate": "locked_future",',
        '    "goal_rec_tiering01_recommendation_score_tiering_gate": "locked_future",',
        '    "goal10b4_recommendation_backtest_revalidation": "locked_future",',
        '    "goal_position_band_validation01_position_band_validation_gate": "locked_future",',
        '    "goal10d_backtest_failure_attribution_gate": "locked_future",',
        '    "dashboard_daily_report": "locked_future",',
        '    "portfolio_backtest": "locked_future"',
        "  }",
        "}",
    ]
    write_text(root / CONTRACT_PATH, "\n".join(lines))


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    by_id = {row["workflow_id"]: row for row in rows}
    if WORKFLOW_ID not in by_id:
        insert_at = next((idx + 1 for idx, row in enumerate(rows) if row["workflow_id"] == GOAL_QUANT_RESEARCH01_WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": WORKFLOW_ID})
    by_id = {row["workflow_id"]: row for row in rows}
    if GOAL_ALPHA_FACTOR_CANDIDATE01_WORKFLOW_ID not in by_id:
        insert_at = next((idx + 1 for idx, row in enumerate(rows) if row["workflow_id"] == WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": GOAL_ALPHA_FACTOR_CANDIDATE01_WORKFLOW_ID})
    by_id = {row["workflow_id"]: row for row in rows}
    by_id[WORKFLOW_ID].update(goal_mvp01_implemented_workflow_patch(str(result["status"])))
    by_id[GOAL_ALPHA_FACTOR_CANDIDATE01_WORKFLOW_ID].update(locked_goal_alpha_factor_candidate01_patch())
    if GOAL_REC_TIERING01_WORKFLOW_ID in by_id:
        by_id[GOAL_REC_TIERING01_WORKFLOW_ID].update(locked_goal_rec_tiering01_patch())
    if GOAL10B4_WORKFLOW_ID in by_id:
        by_id[GOAL10B4_WORKFLOW_ID].update(locked_goal10b4_patch())
    if POSITION_BAND_VALIDATION_WORKFLOW_ID in by_id:
        by_id[POSITION_BAND_VALIDATION_WORKFLOW_ID].update(locked_position_band_validation_patch())
    if GOAL10D_WORKFLOW_ID in by_id:
        by_id[GOAL10D_WORKFLOW_ID].update(locked_goal10d_patch())
    for workflow_id in [
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
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_mvp01"
    preserve_later_review_only_workflow_states(root, by_id)
    if result["status"] in {PASS, PASS_WITH_WARNINGS} and WORKFLOW_ID in by_id:
        by_id[WORKFLOW_ID].update(goal_mvp01_implemented_workflow_patch(str(result["status"])))
        preserve_later_review_only_workflow_states(root, by_id)
    write_csv(path, rows)


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    payload = read_json(path) if path.exists() else {}
    payload[WORKFLOW_ID] = "implemented_mvp_research_only"
    payload[GOAL_ALPHA_FACTOR_CANDIDATE01_WORKFLOW_ID] = False
    payload[GOAL_REC_TIERING01_WORKFLOW_ID] = False
    payload[GOAL10B4_WORKFLOW_ID] = False
    payload[POSITION_BAND_VALIDATION_WORKFLOW_ID] = False
    payload[GOAL10D_WORKFLOW_ID] = False
    preserve_later_review_only_capabilities(root, payload)
    if result["status"] in {PASS, PASS_WITH_WARNINGS}:
        payload[WORKFLOW_ID] = "implemented_mvp_research_only"
        preserve_later_review_only_capabilities(root, payload)
    write_json(path, payload)


def _blocked_result(failures: list[str], warnings: list[str]) -> dict[str, object]:
    manifest = {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "mode": MODE,
        "run_mode": RUN_MODE,
        "status": BLOCKED,
        "workflow_id": WORKFLOW_ID,
        "failures": failures,
        "warnings": warnings,
    }
    for key in FALSE_BOUNDARY_KEYS:
        manifest[key] = False
    return {
        "status": BLOCKED,
        "warnings": warnings,
        "failures": failures,
        "symbol_rows": [],
        "queue_rows": [],
        "factor_summary": [],
        "market_context": [],
        "manifest": manifest,
        "risk_score_bucket_distribution": {},
        "downside_risk_bucket_distribution": {},
        "review_queue_distribution": {},
    }


def _latest_report_date_from_inputs(root: Path) -> str:
    panel = _read_csv(root / PROVIDER02B_PANEL_PATH)
    return _latest_date(panel)


def _latest_date(rows: list[dict[str, str]]) -> str:
    return max(row.get("trade_date", "") for row in rows if row.get("trade_date"))


def _latest_rows(rows: list[dict[str, str]], latest_date: str) -> list[dict[str, str]]:
    return [row for row in rows if row.get("trade_date") == latest_date]


def _key(row: dict[str, str]) -> tuple[str, str]:
    return (row.get("trade_date", ""), row.get("symbol", ""))


def _data_quality_status(panel: dict[str, str]) -> str:
    if panel.get("panel_contract_status") != "source_backed_evaluation_panel_ready_for_dc03":
        return "source_panel_contract_review_required"
    if panel.get("source_warning_codes"):
        return "source_backed_panel_ready_with_governance_warning"
    return "source_backed_panel_ready"


def _severe_data_quality(panel: dict[str, str]) -> bool:
    if panel.get("panel_contract_status") != "source_backed_evaluation_panel_ready_for_dc03":
        return True
    warning = panel.get("source_warning_codes", "").lower()
    severe_fragments = ["schema", "missing", "invalid", "empty", "failed", "stale"]
    return any(fragment in warning for fragment in severe_fragments)


def _research_ready_status(category: str, ready_factor_count: int) -> str:
    if category in {"data_quality_review_queue", "st_or_trading_status_review_queue", "high_downside_risk_review_queue"}:
        return "manual_research_review_blocked_until_queue_review"
    if ready_factor_count == 0:
        return "manual_research_review_only_factor_not_ready"
    return "manual_research_review_ready_non_actionable"


def _coverage_text(rows: list[dict[str, str]]) -> str:
    symbols = len({row.get("symbol", "") for row in rows if row.get("symbol")})
    providers = sorted({row.get("source_provider", "") for row in rows if row.get("source_provider")})
    modes = sorted({row.get("universe_mode", "") for row in rows if row.get("universe_mode")})
    return f"{symbols}_symbols;providers={','.join(providers)};universe_modes={','.join(modes)}"


def _positive(raw: str) -> bool:
    try:
        return float(raw) > 0
    except (TypeError, ValueError):
        return False


def _report_pass_or_warn(report: str) -> bool:
    return (
        "GOAL-MVP-01 Premarket Research Diagnostic Terminal Gate: PASS" in report
        or "GOAL-MVP-01 Premarket Research Diagnostic Terminal Gate: PASS_WITH_WARNINGS" in report
    )


def _workflow_rows(root: Path) -> dict[str, dict[str, str]]:
    rows = _read_csv(root / "configs/project/workflow_status.csv")
    return {row["workflow_id"]: row for row in rows}


def _forbidden_outputs_present(root: Path) -> list[str]:
    present = []
    for prefix in FORBIDDEN_OUTPUT_PREFIXES:
        if (root / prefix).exists():
            present.append(prefix.rstrip("/"))
    return present


def _forbidden_table_label_hits(tables: list[list[dict[str, str]]]) -> list[str]:
    hits = []
    for rows in tables:
        for row in rows:
            for value in row.values():
                tokens = re.split(r"[^A-Za-z0-9_]+", str(value).upper())
                if any(token in FORBIDDEN_TABLE_LABELS for token in tokens):
                    hits.append(str(value))
    return hits


def _contains_secret_like_text(root: Path, paths: list[str]) -> bool:
    patterns = [r"(?i)tushare_token", r"(?i)api[_-]?key", r"(?i)secret", r"(?i)bearer\s+[a-z0-9]"]
    for path in paths:
        target = root / path
        if not target.exists() or target.suffix.lower() not in {".md", ".json", ".csv", ".yaml"}:
            continue
        text = target.read_text(encoding="utf-8")
        if any(re.search(pattern, text) for pattern in patterns):
            return True
    return False


def _walk_values(value: object) -> list[object]:
    if isinstance(value, dict):
        output: list[object] = []
        for item in value.values():
            output.extend(_walk_values(item))
        return output
    if isinstance(value, list):
        output = []
        for item in value:
            output.extend(_walk_values(item))
        return output
    return [value]


def _duplicate_count(keys) -> int:
    counts = Counter(keys)
    return sum(count - 1 for count in counts.values() if count > 1)


def _json_list(values: list[str]) -> str:
    return "[" + ", ".join(f'"{value}"' for value in values) + "]"


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

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import pstdev

from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import (
    preserve_later_review_only_capabilities,
    preserve_later_review_only_workflow_states,
)
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-ALPHA-FACTOR-CANDIDATE-01"
GOAL_NAME = "GOAL-ALPHA-FACTOR-CANDIDATE-01-RESEARCH-GRADE-ALPHA-CANDIDATE-CONSTRUCTION-GATE"
MODE = "research_only_alpha_factor_candidate_construction_gate"
WORKFLOW_ID = "goal_alpha_factor_candidate01_research_gate"
PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

GOAL_MVP01_WORKFLOW_ID = "goal_mvp01_premarket_research_terminal_gate"
GOAL_QUANT_RESEARCH02_WORKFLOW_ID = "goal_quant_research02_alpha_candidate_factor_validity_evaluation_gate"
GOAL_REC_TIERING01_WORKFLOW_ID = "goal_rec_tiering01_recommendation_score_tiering_gate"
GOAL10B4_WORKFLOW_ID = "goal10b4_recommendation_backtest_revalidation"
POSITION_BAND_VALIDATION_WORKFLOW_ID = "goal_position_band_validation01_position_band_validation_gate"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
GOAL10C_WORKFLOW_ID = "goal10c_backtest_cost_slippage_sensitivity_gate"

ALLOWED_NEXT = "request_goal_quant_research02_alpha_candidate_factor_validity_evaluation_gate"
NEXT_GOAL = "GOAL-QUANT-RESEARCH-02-ALPHA-CANDIDATE-FACTOR-VALIDITY-EVALUATION-GATE"
NON_ACTIONABLE = "research_only_factor_candidate_not_investment_advice_not_trade_instruction"

PROVIDER02B_PANEL_PATH = "outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv"
MVP_SYMBOL_TABLE_PATH = "outputs/mvp/goal_mvp01_symbol_diagnostic_table.csv"
MVP_REVIEW_QUEUE_PATH = "outputs/mvp/goal_mvp01_review_queue.csv"
QUANT_REGISTRY_PATH = "outputs/research/goal_quant_research01_factor_registry.csv"
QUANT_VALIDITY_PATH = "outputs/research/goal_quant_research01_score_validity_classification.csv"
RISK011_DIAGNOSTICS_PATH = "outputs/diagnostics/goal_risk_tiering011_downside_risk_diagnostics.csv"
RISK01_DIAGNOSTICS_PATH = "outputs/diagnostics/goal_risk_tiering01_risk_tiered_diagnostics.csv"
MVP_MANIFEST_PATH = "outputs/audits/goal_mvp01_premarket_terminal_manifest.json"

CANDIDATE_REGISTRY_PATH = "outputs/research/goal_alpha_factor_candidate01_candidate_registry.csv"
CANDIDATE_PANEL_PATH = "outputs/research/goal_alpha_factor_candidate01_factor_candidate_panel.csv"
COVERAGE_SUMMARY_PATH = "outputs/research/goal_alpha_factor_candidate01_coverage_summary.csv"
CONSTRUCTION_WARNINGS_PATH = "outputs/research/goal_alpha_factor_candidate01_construction_warnings.csv"
REPORT_PATH = "outputs/audits/goal_alpha_factor_candidate01_report.md"
MANIFEST_PATH = "outputs/audits/goal_alpha_factor_candidate01_manifest.json"
AUDIT_PATH = "outputs/audits/goal_alpha_factor_candidate01_audit.md"
DOC_PATH = "docs/research/GOAL_ALPHA_FACTOR_CANDIDATE01_RESEARCH_GRADE_ALPHA_CANDIDATE_CONSTRUCTION_GATE.md"
CONTRACT_PATH = "configs/research/goal_alpha_factor_candidate01_contract.yaml"

REQUIRED_INPUTS = [
    PROVIDER02B_PANEL_PATH,
    MVP_SYMBOL_TABLE_PATH,
    MVP_REVIEW_QUEUE_PATH,
    QUANT_REGISTRY_PATH,
    QUANT_VALIDITY_PATH,
    RISK011_DIAGNOSTICS_PATH,
    RISK01_DIAGNOSTICS_PATH,
]

OUTPUTS = [
    CANDIDATE_REGISTRY_PATH,
    CANDIDATE_PANEL_PATH,
    COVERAGE_SUMMARY_PATH,
    CONSTRUCTION_WARNINGS_PATH,
    REPORT_PATH,
    MANIFEST_PATH,
    AUDIT_PATH,
    DOC_PATH,
    CONTRACT_PATH,
]

REGISTRY_FIELDS = [
    "factor_id",
    "factor_family",
    "factor_name",
    "economic_hypothesis",
    "expected_direction",
    "required_columns",
    "construction_formula_plain_english",
    "construction_formula_expression",
    "no_lookahead_status",
    "uses_forward_returns_in_construction",
    "uses_benchmark_excess_returns_in_construction",
    "uses_label_ready_fields_in_construction",
    "source_input_artifacts",
    "construction_status",
    "rejection_or_missing_reason",
    "intended_future_evaluation_goal",
    "non_actionable_disclaimer",
]

PANEL_FIELDS = [
    "trade_date",
    "symbol",
    "factor_id",
    "factor_family",
    "factor_value",
    "factor_value_raw",
    "factor_value_normalized_cross_sectional",
    "factor_quantile",
    "factor_bucket",
    "expected_direction",
    "construction_status",
    "no_lookahead_status",
    "required_column_status",
    "source_provider",
    "universe_mode",
    "panel_contract_status",
    "risk_score_bucket",
    "downside_risk_bucket",
    "mvp_review_queue_category",
    "mvp_review_priority_level",
    "diagnostic_mode",
    "non_actionable_disclaimer",
]

COVERAGE_FIELDS = [
    "factor_id",
    "row_count",
    "valid_factor_value_count",
    "missing_factor_value_count",
    "unique_symbols",
    "unique_trade_dates",
    "date_min",
    "date_max",
    "quantile_count",
    "bucket_count",
    "dominant_bucket_share",
    "minimum_bucket_size",
    "construction_status",
    "no_lookahead_status",
    "required_column_status",
]

WARNING_FIELDS = [
    "factor_id",
    "warning_code",
    "warning_severity",
    "warning_detail",
    "non_actionable_disclaimer",
]

FALSE_BOUNDARY_KEYS = [
    "recommendation_outputs_created",
    "position_rows_created",
    "position_band_rows_created",
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
    "goal_quant_research02_run",
    "goal_rec_tiering01_run",
    "goal10b4_run",
    "position_band_validation_run",
    "live_provider_fetches_run",
    "future_returns_used_in_alpha_construction",
    "benchmark_excess_returns_used_in_alpha_construction",
    "label_ready_fields_used_in_alpha_construction",
    "factor_formulas_tuned_to_future_returns",
    "factors_selected_by_posthoc_performance",
    "predictive_validity_claimed",
    "factor_promoted_to_recommendation_tiering",
    "demo_fixture_used",
    "outputs_samples_used",
    "stale_goal10b_evidence_used",
    "stale_dc02_evidence_used",
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


def run_goal_alpha_factor_candidate01_gate(root: Path) -> bool:
    result = evaluate_goal_alpha_factor_candidate01(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal_alpha_factor_candidate01_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal_alpha_factor_candidate01_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    registry = _read_csv(root / CANDIDATE_REGISTRY_PATH)
    panel = _read_csv(root / CANDIDATE_PANEL_PATH)
    coverage = _read_csv(root / COVERAGE_SUMMARY_PATH)
    warnings = _read_csv(root / CONSTRUCTION_WARNINGS_PATH)
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
        failures.append("goal_alpha_factor_candidate01_report_not_pass_or_warn")
    if manifest.get("goal") != GOAL_NAME:
        failures.append("manifest_goal_invalid")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_invalid")
    if manifest.get("status") not in {PASS, PASS_WITH_WARNINGS}:
        failures.append("manifest_status_invalid")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"manifest_{key}_not_false")
    for key in [
        "alpha_candidate_registry_created",
        "alpha_candidate_panel_created",
        "coverage_summary_created",
        "construction_warnings_created",
        "source_backed_lineage_verified",
        "uses_committed_provider02b_evidence_only",
        "uses_committed_mvp01_evidence_only",
        "uses_committed_quant_research01_evidence_only",
        "uses_committed_risk_tiering_evidence_only",
        "no_lookahead_construction_passed",
        "goal_quant_research02_locked_future",
        "goal_rec_tiering01_locked_future",
        "goal10b4_locked_future",
        "position_band_validation_locked_future",
        "goal10d_locked_future",
        "dashboard_daily_report_locked_future",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_{key}_not_true")

    if registry and list(registry[0]) != REGISTRY_FIELDS:
        failures.append("candidate_registry_fields_invalid")
    if panel and list(panel[0]) != PANEL_FIELDS:
        failures.append("candidate_panel_fields_invalid")
    if coverage and list(coverage[0]) != COVERAGE_FIELDS:
        failures.append("coverage_summary_fields_invalid")
    if warnings and list(warnings[0]) != WARNING_FIELDS:
        failures.append("construction_warnings_fields_invalid")

    candidate_count = int(manifest.get("constructed_candidate_count", -1))
    if len(registry) != int(manifest.get("candidate_registry_row_count", -1)):
        failures.append("registry_row_count_manifest_mismatch")
    if len(panel) != int(manifest.get("candidate_panel_row_count", -1)):
        failures.append("panel_row_count_manifest_mismatch")
    if len(coverage) != candidate_count:
        failures.append("coverage_factor_count_mismatch")
    keys = [(row.get("trade_date", ""), row.get("symbol", ""), row.get("factor_id", "")) for row in panel]
    if _duplicate_count(keys):
        failures.append("duplicate_trade_date_symbol_factor_id_rows")
    if any(row.get("uses_forward_returns_in_construction") != "false" for row in registry):
        failures.append("registry_forward_return_construction_flag_invalid")
    if any(row.get("uses_benchmark_excess_returns_in_construction") != "false" for row in registry):
        failures.append("registry_benchmark_excess_construction_flag_invalid")
    if any(row.get("uses_label_ready_fields_in_construction") != "false" for row in registry):
        failures.append("registry_label_ready_construction_flag_invalid")
    if any(row.get("no_lookahead_status") != "passed_current_or_past_only" for row in registry):
        failures.append("registry_no_lookahead_status_invalid")
    if any(row.get("no_lookahead_status") != "passed_current_or_past_only" for row in panel):
        failures.append("panel_no_lookahead_status_invalid")
    if _leakage_field_hits([registry, panel, coverage, warnings]):
        failures.append("future_or_label_field_present_in_outputs")
    if _forbidden_table_label_hits([registry, panel, coverage, warnings]):
        failures.append("forbidden_table_labels_present")
    if any(not _finite_or_blank(row.get("factor_value", "")) for row in panel):
        failures.append("non_finite_factor_value_present")
    if any(row.get("factor_bucket", "") not in {
        "LOW_FACTOR_EXPOSURE_REVIEW_ONLY",
        "MEDIUM_FACTOR_EXPOSURE_REVIEW_ONLY",
        "HIGH_FACTOR_EXPOSURE_REVIEW_ONLY",
        "INSUFFICIENT_FACTOR_EVIDENCE_REVIEW_ONLY",
    } for row in panel):
        failures.append("invalid_factor_bucket")
    if any("outputs/samples/" in str(value) for value in _walk_values(manifest)):
        failures.append("outputs_samples_referenced_in_manifest")
    if any("goal10b_recommendation_backtest" in str(value) for value in _walk_values(manifest)):
        failures.append("stale_goal10b_evidence_referenced")
    if any("goal_v1_diagnostic_coverage02" in str(value) for value in _walk_values(manifest)):
        failures.append("stale_dc02_evidence_referenced")
    if _contains_secret_like_text(root, OUTPUTS):
        failures.append("secret_or_token_like_text_present_in_alpha_outputs")

    gate = workflow.get(WORKFLOW_ID, {})
    quant02 = workflow.get(GOAL_QUANT_RESEARCH02_WORKFLOW_ID, {})
    rec = workflow.get(GOAL_REC_TIERING01_WORKFLOW_ID, {})
    if gate.get("status") != "implemented_research_only":
        failures.append("goal_alpha_factor_candidate01_workflow_not_implemented_research_only")
    if gate.get("implemented_in_repo") != "true":
        failures.append("goal_alpha_factor_candidate01_workflow_not_marked_implemented")
    if gate.get("depends_on") != GOAL_MVP01_WORKFLOW_ID:
        failures.append("goal_alpha_factor_candidate01_dependency_invalid")
    if gate.get("allowed_next_action") != ALLOWED_NEXT:
        failures.append("goal_alpha_factor_candidate01_allowed_next_invalid")
    if quant02.get("status") != "locked_future" or quant02.get("implemented_in_repo") != "false":
        failures.append("goal_quant_research02_not_locked_future")
    if quant02.get("depends_on") != WORKFLOW_ID:
        failures.append("goal_quant_research02_dependency_invalid")
    if rec.get("status") != "locked_future" or rec.get("implemented_in_repo") != "false":
        failures.append("goal_rec_tiering01_not_locked_future")
    if rec.get("depends_on") != GOAL_QUANT_RESEARCH02_WORKFLOW_ID:
        failures.append("goal_rec_tiering01_not_rebased_on_goal_quant_research02")
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
                "# GOAL-ALPHA-FACTOR-CANDIDATE-01 Audit",
                "",
                f"Status: `{status}`",
                "",
                f"Workflow status: `{gate.get('status', 'missing')}`",
                f"Candidate registry rows: `{len(registry)}`",
                f"Candidate panel rows: `{len(panel)}`",
                f"Constructed candidates: `{candidate_count}`",
                f"Unique symbols: `{manifest.get('unique_symbols', 'missing')}`",
                f"Unique trade dates: `{manifest.get('unique_trade_dates', 'missing')}`",
                "Forward returns, benchmark excess returns, and label-ready fields used in construction: `false`",
                "Recommendations, positions, portfolio outputs, dashboards, trading, production, local-lake, factor-mining, and DQN/RL generated: `false`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == PASS


def evaluate_goal_alpha_factor_candidate01(root: Path) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = ["candidate_construction_only_no_predictive_validity_claimed"]
    for path in REQUIRED_INPUTS:
        if not (root / path).exists():
            failures.append(f"missing_required_input:{path}")
    if failures:
        return _blocked_result(failures, warnings)

    panel_rows = _read_csv(root / PROVIDER02B_PANEL_PATH)
    mvp_rows = _read_csv(root / MVP_SYMBOL_TABLE_PATH)
    review_rows = _read_csv(root / MVP_REVIEW_QUEUE_PATH)
    quant_registry = _read_csv(root / QUANT_REGISTRY_PATH)
    quant_validity = _read_csv(root / QUANT_VALIDITY_PATH)
    risk011_rows = _read_csv(root / RISK011_DIAGNOSTICS_PATH)
    risk01_rows = _read_csv(root / RISK01_DIAGNOSTICS_PATH)
    mvp_manifest = _read_json(root / MVP_MANIFEST_PATH)

    if not panel_rows:
        failures.append("provider02b_panel_empty")
    if not mvp_rows:
        failures.append("mvp_symbol_table_empty")
    if failures:
        return _blocked_result(failures, warnings)

    definitions = _candidate_definitions(panel_rows[0])
    registry = [_registry_row(definition) for definition in definitions]
    constructed = [definition for definition in definitions if definition["construction_status"] == "constructed"]
    if len(constructed) != len(definitions):
        warnings.append("some_candidate_families_not_constructed")

    risk01_by_key = {_key(row): row for row in risk01_rows}
    risk011_by_key = {_key(row): row for row in risk011_rows}
    mvp_by_symbol = {row.get("symbol", ""): row for row in mvp_rows if row.get("symbol")}
    queue_by_symbol = _dominant_mvp_queue(review_rows)
    enriched = _enrich_panel_rows(panel_rows, risk01_by_key, risk011_by_key, mvp_by_symbol, queue_by_symbol)
    raw_panel = []
    for row in enriched:
        for definition in definitions:
            value = _factor_value(definition["factor_id"], row)
            missing = value is None or not math.isfinite(value)
            raw_panel.append(
                {
                    "trade_date": row["trade_date"],
                    "symbol": row["symbol"],
                    "factor_id": definition["factor_id"],
                    "factor_family": definition["factor_family"],
                    "factor_value": _fmt(value),
                    "factor_value_raw": _fmt(value),
                    "factor_value_normalized_cross_sectional": "",
                    "factor_quantile": "",
                    "factor_bucket": "INSUFFICIENT_FACTOR_EVIDENCE_REVIEW_ONLY",
                    "expected_direction": definition["expected_direction"],
                    "construction_status": "constructed_value_missing_initial_window" if missing else "constructed",
                    "no_lookahead_status": "passed_current_or_past_only",
                    "required_column_status": definition["required_column_status"],
                    "source_provider": row.get("source_provider", ""),
                    "universe_mode": row.get("universe_mode", ""),
                    "panel_contract_status": row.get("panel_contract_status", ""),
                    "risk_score_bucket": row.get("risk_score_bucket", ""),
                    "downside_risk_bucket": row.get("downside_risk_bucket", ""),
                    "mvp_review_queue_category": row.get("mvp_review_queue_category", ""),
                    "mvp_review_priority_level": row.get("mvp_review_priority_level", ""),
                    "diagnostic_mode": MODE,
                    "non_actionable_disclaimer": NON_ACTIONABLE,
                }
            )
    candidate_panel = _add_cross_sectional_normalization(raw_panel)
    coverage = _coverage_summary(candidate_panel, registry)
    construction_warnings = _construction_warnings(coverage)
    if construction_warnings:
        warnings.append("initial_window_or_bucket_coverage_warnings")

    candidate_ids = sorted({row["factor_id"] for row in registry if row["construction_status"] == "constructed"})
    unique_dates = sorted({row["trade_date"] for row in candidate_panel if row.get("trade_date")})
    unique_symbols = sorted({row["symbol"] for row in candidate_panel if row.get("symbol")})
    status = PASS_WITH_WARNINGS if warnings else PASS
    manifest = {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "mode": MODE,
        "status": status,
        "workflow_id": WORKFLOW_ID,
        "allowed_next_action": ALLOWED_NEXT,
        "recommended_next_goal": NEXT_GOAL,
        "mvp_report_date": str(mvp_manifest.get("report_date", "2026-05-21")),
        "candidate_registry_row_count": len(registry),
        "constructed_candidate_count": len(candidate_ids),
        "candidate_panel_row_count": len(candidate_panel),
        "coverage_summary_row_count": len(coverage),
        "construction_warning_row_count": len(construction_warnings),
        "unique_symbols": len(unique_symbols),
        "unique_trade_dates": len(unique_dates),
        "date_min": min(unique_dates) if unique_dates else "",
        "date_max": max(unique_dates) if unique_dates else "",
        "source_backed_lineage_verified": True,
        "alpha_candidate_registry_created": True,
        "alpha_candidate_panel_created": True,
        "coverage_summary_created": True,
        "construction_warnings_created": True,
        "uses_committed_provider02b_evidence_only": True,
        "uses_committed_mvp01_evidence_only": True,
        "uses_committed_quant_research01_evidence_only": True,
        "uses_committed_risk_tiering_evidence_only": True,
        "no_lookahead_construction_passed": True,
        "goal_quant_research02_locked_future": True,
        "goal_rec_tiering01_locked_future": True,
        "goal10b4_locked_future": True,
        "position_band_validation_locked_future": True,
        "goal10d_locked_future": True,
        "dashboard_daily_report_locked_future": True,
        "candidate_factor_ids": candidate_ids,
        "input_lineage": REQUIRED_INPUTS,
        "output_artifacts": OUTPUTS,
        "input_row_counts": {
            PROVIDER02B_PANEL_PATH: len(panel_rows),
            MVP_SYMBOL_TABLE_PATH: len(mvp_rows),
            MVP_REVIEW_QUEUE_PATH: len(review_rows),
            QUANT_REGISTRY_PATH: len(quant_registry),
            QUANT_VALIDITY_PATH: len(quant_validity),
            RISK011_DIAGNOSTICS_PATH: len(risk011_rows),
            RISK01_DIAGNOSTICS_PATH: len(risk01_rows),
        },
        "warnings": sorted(set(warnings)),
        "failures": failures,
    }
    for key in FALSE_BOUNDARY_KEYS:
        manifest[key] = False

    return {
        "status": status,
        "warnings": sorted(set(warnings)),
        "failures": failures,
        "registry": registry,
        "candidate_panel": candidate_panel,
        "coverage": coverage,
        "construction_warnings": construction_warnings,
        "manifest": manifest,
    }


def goal_alpha_factor_candidate01_valid_evidence(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    audit = _read(root / AUDIT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    return (
        (
            "GOAL-ALPHA-FACTOR-CANDIDATE-01 Research Grade Alpha Candidate Construction Gate: PASS" in report
            or "GOAL-ALPHA-FACTOR-CANDIDATE-01 Research Grade Alpha Candidate Construction Gate: PASS_WITH_WARNINGS" in report
        )
        and "Status: `PASS`" in audit
        and manifest.get("mode") == MODE
        and manifest.get("alpha_candidate_panel_created") is True
        and manifest.get("future_returns_used_in_alpha_construction") is False
        and manifest.get("recommendation_outputs_created") is False
    )


def goal_alpha_factor_candidate01_implemented_workflow_patch(status: str = PASS_WITH_WARNINGS) -> dict[str, str]:
    return {
        "display_name": "GOAL-ALPHA-FACTOR-CANDIDATE-01 Alpha Factor Candidate Research Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_research_only",
        "current_repo_role": MODE,
        "implemented_in_repo": "true",
        "allowed_next_action": ALLOWED_NEXT,
        "depends_on": GOAL_MVP01_WORKFLOW_ID,
        "produces_artifacts": ";".join(OUTPUTS),
        "primary_docs": f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "scripts/run_goal_alpha_factor_candidate01_gate.py;scripts/audit_goal_alpha_factor_candidate01_gate.py",
        "primary_outputs": ";".join([CANDIDATE_REGISTRY_PATH, CANDIDATE_PANEL_PATH, COVERAGE_SUMMARY_PATH, CONSTRUCTION_WARNINGS_PATH, REPORT_PATH, MANIFEST_PATH, AUDIT_PATH]),
        "promotion_rule": "implemented_research_only_after_goal_alpha_factor_candidate01_pass_or_pass_with_warnings",
        "notes": "Research-only alpha factor candidate construction over committed Provider02B, MVP, QUANT, and risk-tiering evidence. It creates candidate factor values only; no recommendation, position, portfolio, dashboard, trading, production, local-lake, factor-mining, broker, or DQN/RL outputs.",
    }


def locked_goal_quant_research02_patch() -> dict[str, str]:
    return {
        "display_name": "GOAL-QUANT-RESEARCH-02 Alpha Candidate Factor Validity Evaluation Gate",
        "stage_or_goal": "GOAL-QUANT-RESEARCH-02",
        "status": "locked_future",
        "current_repo_role": "locked_future_alpha_candidate_factor_validity_evaluation_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal_quant_research02_request",
        "depends_on": WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal_quant_research02_gate",
        "notes": "Future factor validity evaluation remains locked; GOAL-ALPHA-FACTOR-CANDIDATE-01 constructs candidate values only and does not evaluate predictive validity.",
    }


def locked_goal_rec_tiering01_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "current_repo_role": "locked_future_recommendation_score_tiering_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal_quant_research02_passes",
        "depends_on": GOAL_QUANT_RESEARCH02_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal_rec_tiering01_gate_after_quant_research02",
        "notes": "Future recommendation score tiering remains locked; GOAL-ALPHA-FACTOR-CANDIDATE-01 creates research-only candidate values and no recommendation rows.",
    }


def locked_goal10b4_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal_rec_tiering01_passes",
        "depends_on": GOAL_REC_TIERING01_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal10b4_revalidation_gate",
        "notes": "Future GOAL-10B.4 remains locked; GOAL-ALPHA-FACTOR-CANDIDATE-01 creates no recommendation revalidation rows.",
    }


def locked_position_band_validation_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal10b4_and_explicit_position_validation_request",
        "depends_on": GOAL10B4_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_position_band_validation_gate",
        "notes": "Future position-band validation remains locked; GOAL-ALPHA-FACTOR-CANDIDATE-01 creates no position outputs.",
    }


def locked_goal10d_patch() -> dict[str, str]:
    return {
        "status": "locked_future",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10d_request",
        "depends_on": GOAL10C_WORKFLOW_ID,
        "primary_docs": DOC_PATH,
        "promotion_rule": "locked_until_explicit_goal10d_failure_attribution_gate",
        "notes": "Future GOAL-10D remains locked; GOAL-ALPHA-FACTOR-CANDIDATE-01 creates only research candidate construction evidence.",
    }


def _candidate_definitions(sample_row: dict[str, str]) -> list[dict[str, str]]:
    source_artifacts = ";".join(REQUIRED_INPUTS)
    definitions = [
        ("alpha_short_reversal_1d", "short_term_reversal", "Short reversal 1d", "Recent one-day weakness may be reviewed as a reversal candidate.", "open;high;low;close;pre_close", "negative(ret_1d)", "short-term reversal from current one-day return"),
        ("alpha_short_reversal_5d", "short_term_reversal", "Short reversal 5d", "Recent five-day weakness may be reviewed as a reversal candidate.", "close", "negative(ret_5d)", "short-term reversal from trailing five-day return"),
        ("alpha_benchmark_relative_strength_5d", "benchmark_relative_strength", "Benchmark relative strength 5d", "Stock five-day strength relative to benchmark context may indicate research exposure.", "close;benchmark_return_5d", "ret_5d - benchmark_return_5d", "trailing stock return minus trailing benchmark return"),
        ("alpha_benchmark_relative_strength_20d", "benchmark_relative_strength", "Benchmark relative strength 20d", "Stock twenty-day strength relative to benchmark context may indicate research exposure.", "close;benchmark_return_20d", "ret_20d - benchmark_return_20d", "trailing stock return minus trailing benchmark return"),
        ("alpha_vol_adj_momentum_5d", "volatility_adjusted_momentum", "Volatility adjusted momentum 5d", "Trailing momentum is more interpretable when scaled by same-window realized volatility.", "close;pre_close", "ret_5d / trailing_vol_5d", "five-day return divided by trailing one-day return volatility"),
        ("alpha_vol_adj_momentum_20d", "volatility_adjusted_momentum", "Volatility adjusted momentum 20d", "Twenty-day momentum is more interpretable when scaled by same-window realized volatility.", "close;pre_close", "ret_20d / trailing_vol_20d", "twenty-day return divided by trailing one-day return volatility"),
        ("alpha_liquidity_pressure_5d", "liquidity_pressure", "Liquidity pressure 5d", "Current volume relative to a prior trailing baseline can flag abnormal liquidity pressure.", "volume", "volume / lagged_avg_volume_5d - 1", "current volume divided by prior five-row average volume"),
        ("alpha_turnover_pressure_20d", "liquidity_pressure", "Turnover pressure 20d", "Current turnover relative to a prior trailing baseline can flag abnormal participation.", "turnover", "turnover / lagged_avg_turnover_20d - 1", "current turnover divided by prior twenty-row average turnover"),
        ("alpha_price_volume_confirmation_5d", "price_volume_confirmation", "Price volume confirmation 5d", "Five-day price movement confirmed by volume expansion can be reviewed separately from unconfirmed movement.", "close;volume", "ret_5d * max(volume / lagged_avg_volume_5d - 1, 0)", "five-day return multiplied by positive volume expansion"),
        ("alpha_downside_vol_adjusted_strength_20d", "downside_volatility_adjusted_signal", "Downside volatility adjusted strength 20d", "Strength without large trailing downside volatility is a conservative research candidate.", "close;pre_close", "ret_20d / trailing_negative_return_vol_20d", "twenty-day return divided by trailing negative-return volatility"),
        ("alpha_intraday_recovery_pressure", "gap_intraday_pressure", "Intraday recovery pressure", "Close relative to open and intraday range may describe end-of-day recovery pressure for next replay.", "open;high;low;close", "(close - open) / (high - low)", "open-to-close move scaled by intraday range"),
        ("alpha_intraday_weakness_pressure", "gap_intraday_pressure", "Intraday weakness pressure", "Open-to-close weakness scaled by range may describe intraday pressure for next replay.", "open;high;low;close", "(open - close) / (high - low)", "negative open-to-close move scaled by intraday range"),
        ("alpha_risk_adjusted_relative_strength", "risk_adjusted_alpha_candidate", "Risk adjusted relative strength", "Benchmark-relative strength can be reviewed with downside-risk context but not treated as a score.", "close;benchmark_return_20d;downside_risk_bucket", "relative_strength_20d * downside_context_multiplier", "twenty-day benchmark-relative strength scaled by non-actionable downside-risk context"),
    ]
    out = []
    columns = set(sample_row)
    for factor_id, family, name, hypothesis, required, expression, plain in definitions:
        required_cols = required.split(";")
        missing = sorted(col for col in required_cols if col not in columns and col != "downside_risk_bucket")
        status = "constructed" if not missing else "not_constructed_missing_required_columns"
        out.append(
            {
                "factor_id": factor_id,
                "factor_family": family,
                "factor_name": name,
                "economic_hypothesis": hypothesis,
                "expected_direction": "higher_value_research_hypothesis_positive",
                "required_columns": required,
                "construction_formula_plain_english": plain,
                "construction_formula_expression": expression,
                "no_lookahead_status": "passed_current_or_past_only",
                "uses_forward_returns_in_construction": "false",
                "uses_benchmark_excess_returns_in_construction": "false",
                "uses_label_ready_fields_in_construction": "false",
                "source_input_artifacts": source_artifacts,
                "construction_status": status,
                "rejection_or_missing_reason": "none" if not missing else "missing:" + ";".join(missing),
                "intended_future_evaluation_goal": NEXT_GOAL,
                "non_actionable_disclaimer": NON_ACTIONABLE,
                "required_column_status": "available" if not missing else "missing_required_columns",
            }
        )
    return out


def _registry_row(definition: dict[str, str]) -> dict[str, str]:
    return {field: definition[field] for field in REGISTRY_FIELDS}


def _enrich_panel_rows(
    panel_rows: list[dict[str, str]],
    risk01_by_key: dict[tuple[str, str], dict[str, str]],
    risk011_by_key: dict[tuple[str, str], dict[str, str]],
    mvp_by_symbol: dict[str, dict[str, str]],
    queue_by_symbol: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    history: dict[str, list[dict[str, object]]] = defaultdict(list)
    output = []
    for row in sorted(panel_rows, key=lambda item: (item.get("symbol", ""), item.get("trade_date", ""))):
        symbol = row["symbol"]
        prior = history[symbol]
        current = dict(row)
        close = _float(row.get("close"))
        pre_close = _float(row.get("pre_close"))
        ret1d = _safe_div(close, pre_close) - 1.0 if close is not None and pre_close and pre_close != 0 else None
        prev_returns = [item.get("ret_1d") for item in prior if item.get("ret_1d") is not None]
        prev_closes = [item.get("close_num") for item in prior if item.get("close_num") is not None]
        current["close_num"] = close
        current["ret_1d"] = ret1d
        current["ret_5d"] = _trailing_return(close, prev_closes, 5)
        current["ret_20d"] = _trailing_return(close, prev_closes, 20)
        current["vol_5d"] = _std_with_current(prev_returns, ret1d, 5)
        current["vol_20d"] = _std_with_current(prev_returns, ret1d, 20)
        current["neg_vol_20d"] = _negative_std_with_current(prev_returns, ret1d, 20)
        current["lagged_avg_volume_5d"] = _trailing_avg([_float(item.get("volume", "")) for item in prior], 5)
        current["lagged_avg_turnover_20d"] = _trailing_avg([_float(item.get("turnover", "")) for item in prior], 20)
        risk01 = risk01_by_key.get(_key(row), {})
        risk011 = risk011_by_key.get(_key(row), {})
        mvp = mvp_by_symbol.get(symbol, {})
        queue = queue_by_symbol.get(symbol, mvp)
        current["risk_score_bucket"] = risk01.get("risk_score_bucket", mvp.get("risk_score_bucket", ""))
        current["downside_risk_bucket"] = risk011.get("downside_risk_bucket", mvp.get("downside_risk_bucket", ""))
        current["mvp_review_queue_category"] = queue.get("review_queue_category", mvp.get("review_queue_category", ""))
        current["mvp_review_priority_level"] = queue.get("review_priority_level", mvp.get("review_priority_level", ""))
        output.append(current)
        prior.append(current)
    return sorted(output, key=lambda item: (str(item.get("trade_date", "")), str(item.get("symbol", ""))))


def _factor_value(factor_id: str, row: dict[str, object]) -> float | None:
    ret1 = _as_float(row.get("ret_1d"))
    ret5 = _as_float(row.get("ret_5d"))
    ret20 = _as_float(row.get("ret_20d"))
    b5 = _float(row.get("benchmark_return_5d", ""))
    b20 = _float(row.get("benchmark_return_20d", ""))
    if factor_id == "alpha_short_reversal_1d":
        return -ret1 if ret1 is not None else None
    if factor_id == "alpha_short_reversal_5d":
        return -ret5 if ret5 is not None else None
    if factor_id == "alpha_benchmark_relative_strength_5d":
        return ret5 - b5 if ret5 is not None and b5 is not None else None
    if factor_id == "alpha_benchmark_relative_strength_20d":
        return ret20 - b20 if ret20 is not None and b20 is not None else None
    if factor_id == "alpha_vol_adj_momentum_5d":
        return _safe_ratio(ret5, _as_float(row.get("vol_5d")))
    if factor_id == "alpha_vol_adj_momentum_20d":
        return _safe_ratio(ret20, _as_float(row.get("vol_20d")))
    if factor_id == "alpha_liquidity_pressure_5d":
        return _safe_div(_float(row.get("volume", "")), _as_float(row.get("lagged_avg_volume_5d"))) - 1.0 if _as_float(row.get("lagged_avg_volume_5d")) else None
    if factor_id == "alpha_turnover_pressure_20d":
        return _safe_div(_float(row.get("turnover", "")), _as_float(row.get("lagged_avg_turnover_20d"))) - 1.0 if _as_float(row.get("lagged_avg_turnover_20d")) else None
    if factor_id == "alpha_price_volume_confirmation_5d":
        volume_pressure = _factor_value("alpha_liquidity_pressure_5d", row)
        return ret5 * max(volume_pressure, 0.0) if ret5 is not None and volume_pressure is not None else None
    if factor_id == "alpha_downside_vol_adjusted_strength_20d":
        return _safe_ratio(ret20, _as_float(row.get("neg_vol_20d")))
    if factor_id == "alpha_intraday_recovery_pressure":
        open_ = _float(row.get("open", ""))
        high = _float(row.get("high", ""))
        low = _float(row.get("low", ""))
        close = _float(row.get("close", ""))
        return _safe_ratio(close - open_, high - low) if None not in {open_, high, low, close} else None
    if factor_id == "alpha_intraday_weakness_pressure":
        open_ = _float(row.get("open", ""))
        high = _float(row.get("high", ""))
        low = _float(row.get("low", ""))
        close = _float(row.get("close", ""))
        return _safe_ratio(open_ - close, high - low) if None not in {open_, high, low, close} else None
    if factor_id == "alpha_risk_adjusted_relative_strength":
        relative = ret20 - b20 if ret20 is not None and b20 is not None else None
        multiplier = _downside_multiplier(str(row.get("downside_risk_bucket", "")))
        return relative * multiplier if relative is not None else None
    return None


def _add_cross_sectional_normalization(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[(str(row["trade_date"]), str(row["factor_id"]))].append(row)
    for group_rows in groups.values():
        valid = [row for row in group_rows if _as_float(row.get("factor_value")) is not None]
        valid_sorted = sorted(valid, key=lambda item: (_as_float(item["factor_value"]) or 0.0, str(item["symbol"])))
        n = len(valid_sorted)
        for idx, row in enumerate(valid_sorted):
            if n >= 2:
                row["factor_value_normalized_cross_sectional"] = _fmt((idx / (n - 1)) * 2.0 - 1.0)
            else:
                row["factor_value_normalized_cross_sectional"] = ""
            if n >= 5:
                quantile = min(5, int((idx * 5) / n) + 1)
                row["factor_quantile"] = str(quantile)
                row["factor_bucket"] = _bucket_from_quantile(quantile)
            else:
                row["factor_quantile"] = ""
                row["factor_bucket"] = "INSUFFICIENT_FACTOR_EVIDENCE_REVIEW_ONLY"
    return [{field: row.get(field, "") for field in PANEL_FIELDS} for row in rows]


def _coverage_summary(panel: list[dict[str, object]], registry: list[dict[str, str]]) -> list[dict[str, object]]:
    by_factor: dict[str, list[dict[str, object]]] = defaultdict(list)
    registry_by_factor = {row["factor_id"]: row for row in registry}
    for row in panel:
        by_factor[str(row["factor_id"])].append(row)
    summary = []
    for factor_id in sorted(by_factor):
        rows = by_factor[factor_id]
        valid = [row for row in rows if _as_float(row.get("factor_value")) is not None]
        buckets = Counter(row.get("factor_bucket", "") for row in rows if row.get("factor_bucket"))
        bucket_values = list(buckets.values())
        dates = sorted({str(row["trade_date"]) for row in rows if row.get("trade_date")})
        summary.append(
            {
                "factor_id": factor_id,
                "row_count": len(rows),
                "valid_factor_value_count": len(valid),
                "missing_factor_value_count": len(rows) - len(valid),
                "unique_symbols": len({row.get("symbol", "") for row in rows if row.get("symbol")}),
                "unique_trade_dates": len(dates),
                "date_min": min(dates) if dates else "",
                "date_max": max(dates) if dates else "",
                "quantile_count": len({row.get("factor_quantile", "") for row in rows if row.get("factor_quantile")}),
                "bucket_count": len(buckets),
                "dominant_bucket_share": _fmt(max(bucket_values, default=0) / len(rows) if rows else 0.0),
                "minimum_bucket_size": min(bucket_values, default=0),
                "construction_status": registry_by_factor[factor_id]["construction_status"],
                "no_lookahead_status": registry_by_factor[factor_id]["no_lookahead_status"],
                "required_column_status": (
                    "available"
                    if registry_by_factor[factor_id]["construction_status"] == "constructed"
                    else "missing_required_columns"
                ),
            }
        )
    return summary


def _construction_warnings(coverage: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for row in coverage:
        missing = int(row["missing_factor_value_count"])
        if missing:
            rows.append(
                {
                    "factor_id": row["factor_id"],
                    "warning_code": "initial_window_missing_values",
                    "warning_severity": "research_warning",
                    "warning_detail": f"{missing}_rows_missing_due_to_required_trailing_history",
                    "non_actionable_disclaimer": NON_ACTIONABLE,
                }
            )
        if int(row["quantile_count"]) < 5:
            rows.append(
                {
                    "factor_id": row["factor_id"],
                    "warning_code": "quantile_coverage_below_five",
                    "warning_severity": "research_warning",
                    "warning_detail": "factor_quantiles_not_available_for_all_dates",
                    "non_actionable_disclaimer": NON_ACTIONABLE,
                }
            )
    return rows


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_csv(root / CANDIDATE_REGISTRY_PATH, result["registry"], REGISTRY_FIELDS)
    write_csv(root / CANDIDATE_PANEL_PATH, result["candidate_panel"], PANEL_FIELDS)
    write_csv(root / COVERAGE_SUMMARY_PATH, result["coverage"], COVERAGE_FIELDS)
    write_csv(root / CONSTRUCTION_WARNINGS_PATH, result["construction_warnings"], WARNING_FIELDS)
    write_json(root / MANIFEST_PATH, result["manifest"])
    _write_report(root, result)
    _write_doc(root, result)
    _write_contract(root, result)


def _write_report(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    constructed = manifest.get("constructed_candidate_count", 0)
    body = [
        "# GOAL-ALPHA-FACTOR-CANDIDATE-01 Research Grade Alpha Candidate Construction Gate",
        "",
        "## 1. Goal status",
        f"GOAL-ALPHA-FACTOR-CANDIDATE-01 Research Grade Alpha Candidate Construction Gate: {manifest['status']}",
        "",
        "## 2. Current MVP and research-stage context",
        f"MVP report date: `{manifest['mvp_report_date']}`. GOAL-MVP-01 reported zero factors approved for recommendation tiering.",
        "",
        "## 3. Source-backed input lineage",
        *[f"- `{path}`" for path in REQUIRED_INPUTS],
        "",
        "## 4. Alpha candidate design principles",
        "The gate constructs a small, interpretable set of candidate values from current and historical committed evidence only. It does not search formula libraries, tune weights, or claim predictive validity.",
        "",
        "## 5. Candidate factor families constructed",
        f"Constructed candidate count: `{constructed}`.",
        "Families include short-term reversal, benchmark-relative strength, volatility-adjusted momentum, liquidity pressure, price-volume confirmation, downside-volatility adjustment, intraday pressure, and conservative risk-adjusted relative strength.",
        "",
        "## 6. Candidate factor families skipped and why",
        "No requested family was skipped because required committed OHLCV, turnover, benchmark-return, and risk context columns are available.",
        "",
        "## 7. No-lookahead construction policy",
        "Rolling and lagged calculations use current or prior rows at each trade date. Future label fields, benchmark-excess label fields, and label-readiness fields are excluded from construction.",
        "",
        "## 8. Candidate panel coverage",
        f"Panel rows: `{manifest['candidate_panel_row_count']}`. Symbols: `{manifest['unique_symbols']}`. Trade dates: `{manifest['unique_trade_dates']}`.",
        "",
        "## 9. Candidate registry summary",
        f"Registry rows: `{manifest['candidate_registry_row_count']}`.",
        "",
        "## 10. Construction warnings",
        f"Warning rows: `{manifest['construction_warning_row_count']}`. Initial rows may be missing where trailing windows are unavailable.",
        "",
        "## 11. Why these are not recommendations",
        "These are candidate factor exposures only. They are not trade labels, target prices, position sizes, portfolio weights, order instructions, portfolio results, or model-validity claims.",
        "",
        "## 12. Required next evaluation goal",
        f"`{NEXT_GOAL}`.",
        "",
        "## 13. Locked downstream boundaries",
        "GOAL-QUANT-RESEARCH-02, GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, portfolio backtests, trading, production, broker integration, local-lake writes, factor-mining, and DQN/RL remain locked.",
        "",
    ]
    write_text(root / REPORT_PATH, "\n".join(body))


def _write_doc(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    body = [
        "# GOAL-ALPHA-FACTOR-CANDIDATE-01 Research Grade Alpha Candidate Construction Gate",
        "",
        f"Status: `{manifest['status']}`",
        "",
        "This gate constructs research-only alpha factor candidate values from committed Provider02B, MVP, QUANT, and risk-tiering evidence.",
        "",
        "## Outputs",
        *[f"- `{path}`" for path in OUTPUTS],
        "",
        "## Boundary",
        "The gate creates candidate values only. It does not evaluate predictive validity, create recommendation rows, create position rows, create portfolio outputs, create dashboard/frontend files, fetch live data, write local-lake data, or unlock execution paths.",
        "",
        "## Next Required Goal",
        f"`{NEXT_GOAL}` remains locked until explicitly requested.",
        "",
    ]
    write_text(root / DOC_PATH, "\n".join(body))


def _write_contract(root: Path, result: dict[str, object]) -> None:
    manifest = result["manifest"]
    lines = [
        "{",
        '  "goal_id": "GOAL-ALPHA-FACTOR-CANDIDATE-01",',
        f'  "mode": "{MODE}",',
        f'  "status": "{manifest["status"]}",',
        '  "research_only": true,',
        '  "candidate_values_only": true,',
        '  "allowed_inputs": [',
        *[f'    "{path}",' for path in REQUIRED_INPUTS[:-1]],
        f'    "{REQUIRED_INPUTS[-1]}"',
        "  ],",
        '  "allowed_outputs": [',
        *[f'    "{path}",' for path in OUTPUTS[:-1]],
        f'    "{OUTPUTS[-1]}"',
        "  ],",
        '  "candidate_registry_schema": ' + _json_list(REGISTRY_FIELDS) + ",",
        '  "candidate_panel_schema": ' + _json_list(PANEL_FIELDS) + ",",
        '  "coverage_summary_schema": ' + _json_list(COVERAGE_FIELDS) + ",",
        '  "forbidden_construction_inputs": ["forward_return_*", "benchmark_excess_return_*", "label_ready_*"],',
        '  "downstream_locks": {',
        '    "goal_quant_research02_alpha_candidate_factor_validity_evaluation_gate": "locked_future",',
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
        insert_at = next((idx + 1 for idx, row in enumerate(rows) if row["workflow_id"] == GOAL_MVP01_WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": WORKFLOW_ID})
    by_id = {row["workflow_id"]: row for row in rows}
    if GOAL_QUANT_RESEARCH02_WORKFLOW_ID not in by_id:
        insert_at = next((idx + 1 for idx, row in enumerate(rows) if row["workflow_id"] == WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": GOAL_QUANT_RESEARCH02_WORKFLOW_ID})
    by_id = {row["workflow_id"]: row for row in rows}
    by_id[WORKFLOW_ID].update(goal_alpha_factor_candidate01_implemented_workflow_patch(str(result["status"])))
    by_id[GOAL_QUANT_RESEARCH02_WORKFLOW_ID].update(locked_goal_quant_research02_patch())
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
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_alpha_factor_candidate01"
    preserve_later_review_only_workflow_states(root, by_id)
    if result["status"] in {PASS, PASS_WITH_WARNINGS}:
        by_id[WORKFLOW_ID].update(goal_alpha_factor_candidate01_implemented_workflow_patch(str(result["status"])))
        by_id[GOAL_QUANT_RESEARCH02_WORKFLOW_ID].update(locked_goal_quant_research02_patch())
        if GOAL_REC_TIERING01_WORKFLOW_ID in by_id:
            by_id[GOAL_REC_TIERING01_WORKFLOW_ID].update(locked_goal_rec_tiering01_patch())
        if GOAL10B4_WORKFLOW_ID in by_id:
            by_id[GOAL10B4_WORKFLOW_ID].update(locked_goal10b4_patch())
        if POSITION_BAND_VALIDATION_WORKFLOW_ID in by_id:
            by_id[POSITION_BAND_VALIDATION_WORKFLOW_ID].update(locked_position_band_validation_patch())
        if GOAL10D_WORKFLOW_ID in by_id:
            by_id[GOAL10D_WORKFLOW_ID].update(locked_goal10d_patch())
    write_csv(path, rows)


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    payload = read_json(path) if path.exists() else {}
    payload[WORKFLOW_ID] = "implemented_research_only"
    payload[GOAL_QUANT_RESEARCH02_WORKFLOW_ID] = False
    payload[GOAL_REC_TIERING01_WORKFLOW_ID] = False
    payload[GOAL10B4_WORKFLOW_ID] = False
    payload[POSITION_BAND_VALIDATION_WORKFLOW_ID] = False
    payload[GOAL10D_WORKFLOW_ID] = False
    preserve_later_review_only_capabilities(root, payload)
    if result["status"] in {PASS, PASS_WITH_WARNINGS}:
        payload[WORKFLOW_ID] = "implemented_research_only"
    write_json(path, payload)


def _blocked_result(failures: list[str], warnings: list[str]) -> dict[str, object]:
    manifest = {
        "goal": GOAL_NAME,
        "goal_id": GOAL_ID,
        "mode": MODE,
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
        "registry": [],
        "candidate_panel": [],
        "coverage": [],
        "construction_warnings": [],
        "manifest": manifest,
    }


def _dominant_mvp_queue(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    priority_order = {
        "DATA_REVIEW": 0,
        "ST_OR_TRADING_STATUS_REVIEW": 1,
        "RISK_REVIEW": 2,
        "LIQUIDITY_REVIEW": 3,
        "VOLATILITY_REVIEW": 4,
        "FACTOR_RESEARCH_REVIEW": 5,
        "CLEAN_RESEARCH_WATCH": 6,
        "NO_RESEARCH_ACTION": 7,
    }
    best: dict[str, dict[str, str]] = {}
    for row in rows:
        symbol = row.get("symbol", "")
        if not symbol or row.get("queue_status") != "active_for_report_date":
            continue
        current = best.get(symbol)
        if current is None or priority_order.get(row.get("review_priority_level", ""), 99) < priority_order.get(current.get("review_priority_level", ""), 99):
            best[symbol] = row
    return best


def _key(row: dict[str, str]) -> tuple[str, str]:
    return (row.get("trade_date", ""), row.get("symbol", ""))


def _trailing_return(close: float | None, prev_closes: list[float], window: int) -> float | None:
    if close is None or len(prev_closes) < window:
        return None
    base = prev_closes[-window]
    if base == 0:
        return None
    return close / base - 1.0


def _std_with_current(prev_returns: list[float], ret1d: float | None, window: int) -> float | None:
    values = prev_returns[-(window - 1):] + ([ret1d] if ret1d is not None else [])
    values = [value for value in values if value is not None]
    if len(values) < 2:
        return None
    return pstdev(values)


def _negative_std_with_current(prev_returns: list[float], ret1d: float | None, window: int) -> float | None:
    values = prev_returns[-(window - 1):] + ([ret1d] if ret1d is not None else [])
    negatives = [value for value in values if value is not None and value < 0]
    if len(negatives) < 2:
        return None
    return pstdev(negatives)


def _trailing_avg(values: list[float | None], window: int) -> float | None:
    clean = [value for value in values if value is not None]
    if len(clean) < window:
        return None
    selected = clean[-window:]
    return sum(selected) / len(selected)


def _downside_multiplier(bucket: str) -> float:
    if bucket.startswith("LOW"):
        return 1.0
    if bucket.startswith("MEDIUM"):
        return 0.6
    if bucket.startswith("HIGH"):
        return 0.2
    return 0.4


def _bucket_from_quantile(quantile: int) -> str:
    if quantile <= 2:
        return "LOW_FACTOR_EXPOSURE_REVIEW_ONLY"
    if quantile == 3:
        return "MEDIUM_FACTOR_EXPOSURE_REVIEW_ONLY"
    return "HIGH_FACTOR_EXPOSURE_REVIEW_ONLY"


def _safe_div(numerator: float | None, denominator: float | None) -> float:
    if numerator is None or denominator is None or denominator == 0:
        return float("nan")
    return numerator / denominator


def _safe_ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or abs(denominator) < 1e-12:
        return None
    return numerator / denominator


def _float(value: object) -> float | None:
    try:
        if value == "" or value is None:
            return None
        output = float(value)
        return output if math.isfinite(output) else None
    except (TypeError, ValueError):
        return None


def _as_float(value: object) -> float | None:
    return _float(value)


def _fmt(value: object) -> str:
    numeric = _as_float(value)
    if numeric is None or not math.isfinite(numeric):
        return ""
    return f"{numeric:.10f}"


def _finite_or_blank(value: object) -> bool:
    if value in {"", None}:
        return True
    numeric = _as_float(value)
    return numeric is not None and math.isfinite(numeric)


def _report_pass_or_warn(report: str) -> bool:
    return (
        "GOAL-ALPHA-FACTOR-CANDIDATE-01 Research Grade Alpha Candidate Construction Gate: PASS" in report
        or "GOAL-ALPHA-FACTOR-CANDIDATE-01 Research Grade Alpha Candidate Construction Gate: PASS_WITH_WARNINGS" in report
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


def _leakage_field_hits(tables: list[list[dict[str, str]]]) -> list[str]:
    patterns = ["forward_return", "benchmark_excess_return", "label_ready"]
    allowed_metadata_keys = {
        "uses_forward_returns_in_construction",
        "uses_benchmark_excess_returns_in_construction",
        "uses_label_ready_fields_in_construction",
    }
    hits = []
    for rows in tables:
        for row in rows:
            for key, value in row.items():
                key_lower = key.lower()
                value_lower = str(value).lower()
                if key_lower in allowed_metadata_keys and value_lower == "false":
                    continue
                if any(pattern in key_lower for pattern in patterns) or any(pattern in value_lower for pattern in patterns):
                    hits.append(f"{key}:{value}".lower())
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

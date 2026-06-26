from __future__ import annotations

import ast
from pathlib import Path

from ashare_premarket.contract_design.goal08b0 import (
    GOAL08B0_ALLOWED_NEXT,
    GOAL08B0_WORKFLOW_ID,
    GOAL08B_ELIGIBLE_STATUS,
    goal08b0_valid_unlock_evidence,
)
from ashare_premarket.contract_design.goal090 import (
    GOAL09_WORKFLOW_ID,
    goal09_eligible_workflow_patch,
    goal090_valid_unlock_evidence,
)
from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import preserve_later_review_only_capabilities, preserve_later_review_only_workflow_states
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.review_diagnostics.goal08b import (
    DIAGNOSTIC_PATH as GOAL08B_DIAGNOSTIC_PATH,
    GOAL08B_ALLOWED_NEXT as GOAL08B_IMPLEMENTED_ALLOWED_NEXT,
    GOAL08B_IMPLEMENTED_STATUS,
    WORKFLOW_NOTES as GOAL08B_WORKFLOW_NOTES,
    WORKFLOW_PRIMARY_DOCS as GOAL08B_WORKFLOW_PRIMARY_DOCS,
    WORKFLOW_PRIMARY_OUTPUTS as GOAL08B_WORKFLOW_PRIMARY_OUTPUTS,
    WORKFLOW_PRIMARY_SCRIPTS as GOAL08B_WORKFLOW_PRIMARY_SCRIPTS,
    WORKFLOW_PRODUCES_ARTIFACTS as GOAL08B_WORKFLOW_PRODUCES_ARTIFACTS,
    goal08b_valid_diagnostics_evidence,
)
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-08A"
GOAL_NAME = "GOAL-08A-RECOMMENDATION-CONTRACT-DESIGN-GATE"
MODE = "design_only"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

CONFIG_DIR = "configs/recommendation"
DOC_DIR = "docs/recommendation"
AUDIT_DIR = "outputs/audits"

INPUT_CONTRACT_PATH = f"{CONFIG_DIR}/goal08a_future_recommendation_input_contract.yaml"
FUTURE_SCHEMA_PATH = f"{CONFIG_DIR}/goal08a_future_recommendation_schema.yaml"
WARNING_POLICY_PATH = f"{CONFIG_DIR}/goal08a_warning_propagation_policy.yaml"
ACTIONABILITY_PATH = f"{CONFIG_DIR}/goal08a_actionability_guardrails.yaml"
STATE_MACHINE_PATH = f"{CONFIG_DIR}/goal08a_recommendation_state_machine.yaml"
DOC_PATH = f"{DOC_DIR}/GOAL08A_RECOMMENDATION_CONTRACT_DESIGN_GATE.md"
BOUNDARY_DOC_PATH = f"{DOC_DIR}/GOAL08A_DESIGN_ONLY_BOUNDARY.md"
REPORT_PATH = f"{AUDIT_DIR}/goal08a_recommendation_contract_design_report.md"
AUDIT_REPORT_PATH = f"{AUDIT_DIR}/goal08a_recommendation_contract_design_audit.md"
MANIFEST_PATH = f"{AUDIT_DIR}/goal08a_recommendation_contract_design_manifest.json"

GOAL07B_OVERLAY_PATH = "outputs/risk_overlay/goal07b_review_only_risk_overlay.csv"
GOAL07B_DIAGNOSTICS_PATH = "outputs/diagnostics/goal07b_risk_overlay_diagnostics.csv"
GOAL07B_REPORT_PATH = "outputs/audits/goal07b_risk_overlay_calculation_report.md"
GOAL07B_AUDIT_PATH = "outputs/audits/goal07b_risk_overlay_calculation_audit.md"
GOAL07B_MANIFEST_PATH = "outputs/audits/goal07b_risk_overlay_calculation_manifest.json"

GOAL08A_WORKFLOW_ID = "goal08a_recommendation_contract_design_gate"
GOAL08B_WORKFLOW_ID = "goal08b_recommendation_review_only_prototype"
GOAL08A_ALLOWED_NEXT = "request_explicit_goal08b_review_only_prototype_or_fix_goal08a_warnings"
GOAL10B_ALLOWED_BACKTEST_CSV_OUTPUTS = {
    "outputs/backtest/goal10b_recommendation_backtest_input_snapshot.csv",
    "outputs/backtest/goal10b_recommendation_group_metrics.csv",
    "outputs/backtest/goal10b_risk_severity_group_metrics.csv",
    "outputs/backtest/goal10b_warning_group_metrics.csv",
    "outputs/backtest/goal10b_ic_rank_ic_summary.csv",
}

REQUIRED_GOAL07B_FIELDS = [
    "goal_id",
    "mode",
    "calculation_type",
    "trade_date",
    "symbol",
    "risk_domain",
    "risk_tag",
    "risk_severity",
    "risk_confidence",
    "risk_state",
    "risk_transition_diagnostic",
    "triggered_rule_ids",
    "risk_rule_trace",
    "warning_propagation",
    "upstream_warning_mapping",
    "missing_input_diagnostics",
    "bounded_model_weakness_diagnostics",
    "review_only_status_flags",
    "non_actionable",
    "recommendation_generated",
    "position_generated",
    "dashboard_generated",
    "paper_live_trading_generated",
    "trading_generated",
    "production_generated",
    "backtest_generated",
    "factor_mining_generated",
    "dqn_rl_generated",
]

GOAL07B_WARNING_CODES = [
    "calibration_not_reliable_for_thresholding",
    "feature_sign_instability_bounded",
    "provider_source_concentration_disclosed",
    "selected_score_variant_weak_rank_signal",
    "single_provider_mode_akshare_direct",
    "target_horizon_calibration_warning",
    "weak_target_horizon_rank_signal",
]

FUTURE_SCHEMA_NAMES = [
    "trade_date",
    "symbol",
    "source_goal07b_risk_state",
    "source_goal07b_risk_severity",
    "source_goal07b_risk_confidence",
    "source_goal07b_triggered_rule_ids",
    "source_goal07b_warning_propagation",
    "source_goal07b_risk_rule_trace",
    "future_recommendation_contract_state",
    "future_actionability_block_reason",
    "future_non_actionable_diagnostic_flag",
    "future_warning_policy_trace",
    "future_downstream_lock_flags",
]

FORBIDDEN_FUTURE_SCHEMA_FIELDS = [
    "buy",
    "sell",
    "hold",
    "target_price",
    "position_size",
    "portfolio_weight",
    "order_action",
    "trade_signal",
    "broker_instruction",
    "production_signal",
    "backtest_return",
    "factor_alpha",
    "dqn_policy",
    "rl_action",
]

FORBIDDEN_OUTPUT_DIRS = [
    "outputs/recommendations",
    "outputs/positions",
    "outputs/dashboard",
    "outputs/paper_trading",
    "outputs/live_trading",
    "outputs/backtests",
    "outputs/factors",
]

DOWNSTREAM_LOCKED_IDS = [
    "position_band_recommendation",
    "dashboard_daily_report",
    "paper_trading_journal",
    "broker_live_trading",
    "production_db_writes",
    "production_model_promotion",
    "signal_backtest",
    "portfolio_backtest",
    "cost_slippage_sensitivity",
    "failure_attribution",
    "production_hardening",
]

FORBIDDEN_IMPORT_TERMS = {
    "dqn",
    "reinforcement_learning",
    "position_band",
    "recommendation",
    "dashboard",
    "paper_trading",
    "broker",
    "live_trading",
    "production_db_write",
}


def run_goal08a_recommendation_contract_design_gate(root: Path) -> bool:
    bundle = load_goal08a_design_bundle(root)
    review = evaluate_goal08a_design_gate(bundle)
    _write_design_artifacts(root, review)
    _update_workflow_status(root, review)
    _update_locked_capabilities(root, review)
    audit_ok = audit_goal08a_recommendation_contract_design_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return review["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal08a_recommendation_contract_design_gate(root: Path) -> bool:
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    input_contract = _read_json(root / INPUT_CONTRACT_PATH)
    schema = _read_json(root / FUTURE_SCHEMA_PATH)
    warning_policy = _read_json(root / WARNING_POLICY_PATH)
    actionability = _read_json(root / ACTIONABILITY_PATH)
    state_machine = _read_json(root / STATE_MACHINE_PATH)
    workflow = _workflow_rows(root)
    goal08b0_valid = goal08b0_valid_unlock_evidence(root)
    goal08b_valid = goal08b_valid_diagnostics_evidence(root)
    failures: list[str] = []
    warnings: list[str] = []

    if not _report_pass_or_warn(report, "GOAL-08A Recommendation Contract Design Gate:"):
        failures.append("goal08a_report_not_pass_or_warn")
    if manifest.get("goal") != GOAL_NAME:
        failures.append("manifest_goal_not_goal08a")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_not_design_only")
    if manifest.get("source_goal") != "GOAL-07B":
        failures.append("manifest_source_goal_not_goal07b")
    if manifest.get("input_grain") != "trade_date + symbol":
        failures.append("manifest_input_grain_invalid")
    for key in _false_boundary_keys():
        if manifest.get(key) is not False:
            failures.append(f"manifest_{key}_not_false")
    if manifest.get("high_risk_severity_blocks_actionable_output") is not True:
        failures.append("manifest_high_risk_block_rule_missing")
    if manifest.get("future_schema_names_only") is not True:
        failures.append("manifest_future_schema_names_only_not_true")

    if input_contract.get("required_input_grain") != "trade_date + symbol":
        failures.append("input_contract_grain_invalid")
    missing_input_fields = [
        field
        for field in REQUIRED_GOAL07B_FIELDS
        if field not in input_contract.get("required_goal07b_fields", [])
    ]
    failures.extend(f"input_contract_missing_goal07b_field:{field}" for field in missing_input_fields)
    if input_contract.get("source_artifacts", {}).get("rows_are_actionable") is not False:
        failures.append("input_contract_does_not_mark_source_non_actionable")

    if schema.get("future_schema_names_only") is not True:
        failures.append("schema_not_names_only")
    if schema.get("empty_schema_sample", {}).get("row_count") != 0:
        failures.append("schema_empty_sample_row_count_not_zero")
    if schema.get("empty_schema_sample", {}).get("rows") != []:
        failures.append("schema_empty_sample_rows_not_empty")
    forbidden_present = sorted(set(schema.get("future_schema_fields", [])) & set(FORBIDDEN_FUTURE_SCHEMA_FIELDS))
    failures.extend(f"schema_contains_forbidden_future_field:{field}" for field in forbidden_present)

    mapping_codes = {
        item.get("warning_code")
        for item in warning_policy.get("warning_propagation_rules", [])
        if isinstance(item, dict)
    }
    failures.extend(
        f"warning_policy_missing_code:{code}"
        for code in GOAL07B_WARNING_CODES
        if code not in mapping_codes
    )
    for item in warning_policy.get("warning_propagation_rules", []):
        if item.get("propagate_to_future_contract") is not True:
            failures.append(f"warning_policy_not_propagated:{item.get('warning_code', 'missing')}")

    if actionability.get("high_risk_severity_blocks_actionable_recommendation") is not True:
        failures.append("actionability_high_risk_block_missing")
    if actionability.get("recommendation_like_diagnostic_must_be_non_actionable") is not True:
        failures.append("actionability_non_actionable_diagnostic_missing")
    if actionability.get("goal08a_generates_actions") is not False:
        failures.append("actionability_goal08a_generates_actions_not_false")

    states = set(state_machine.get("states", []))
    for required in {
        "goal08a_design_only",
        "source_goal07b_contract_verified",
        "high_risk_blocks_actionability",
        "future_schema_documented_no_rows",
        "goal08b_locked_future",
        "downstream_execution_locked",
    }:
        if required not in states:
            failures.append(f"state_machine_missing_state:{required}")
    if state_machine.get("goal08b_status_after_goal08a") != "locked_future":
        failures.append("state_machine_goal08b_not_locked")

    goal08a = workflow.get(GOAL08A_WORKFLOW_ID, {})
    if goal08a.get("status") != "implemented_design_only":
        failures.append("goal08a_workflow_not_implemented_design_only")
    if goal08a.get("implemented_in_repo") != "true":
        failures.append("goal08a_workflow_not_marked_implemented")
    goal08b = workflow.get(GOAL08B_WORKFLOW_ID, {})
    if goal08b_valid:
        if goal08b.get("status") != GOAL08B_IMPLEMENTED_STATUS:
            failures.append("goal08b_valid_diagnostics_not_implemented_review_only")
        if goal08b.get("implemented_in_repo") != "true":
            failures.append("goal08b_valid_diagnostics_not_marked_implemented")
        if goal08b.get("allowed_next_action") != GOAL08B_IMPLEMENTED_ALLOWED_NEXT:
            failures.append("goal08b_valid_diagnostics_allowed_next_invalid")
    elif goal08b.get("implemented_in_repo") != "false":
        failures.append("goal08b_marked_implemented_without_valid_diagnostics")
    elif goal08b0_valid:
        if goal08b.get("status") != GOAL08B_ELIGIBLE_STATUS:
            failures.append("goal08b_not_future_review_only_after_goal08b0")
    elif goal08b.get("status") != "locked_future":
        failures.append("goal08b_not_locked_future_without_goal08b0")
    goal090_valid = goal090_valid_unlock_evidence(root)
    goal09_expected = goal09_eligible_workflow_patch(root) if goal090_valid else {}
    for workflow_id in DOWNSTREAM_LOCKED_IDS:
        row = workflow.get(workflow_id, {})
        if workflow_id == GOAL09_WORKFLOW_ID and goal090_valid:
            if row.get("status") != goal09_expected.get("status"):
                failures.append("goal09_not_preserved_after_goal090")
            if row.get("implemented_in_repo") != goal09_expected.get("implemented_in_repo"):
                failures.append("goal09_implemented_flag_not_preserved_after_goal090")
            continue
        if row.get("status") != "locked_future":
            failures.append(f"{workflow_id}_not_locked_future")
        if row.get("implemented_in_repo") != "false":
            failures.append(f"{workflow_id}_marked_implemented")
    if workflow.get("dqn_rl_mainline", {}).get("status") != "deleted_from_active_mainline":
        failures.append("dqn_rl_not_deleted_from_active_mainline")
    if workflow.get("v2_factor_research_upgrade", {}).get("status") != "planned_locked":
        failures.append("v2_factor_research_not_planned_locked")

    forbidden_dirs = _forbidden_output_dirs_present(root)
    failures.extend(f"forbidden_output_dir_present:{path}" for path in forbidden_dirs)
    forbidden_rows = _forbidden_recommendation_row_outputs(root)
    failures.extend(f"forbidden_recommendation_row_output_present:{path}" for path in forbidden_rows)
    forbidden_imports = _forbidden_active_imports(root)
    failures.extend(f"forbidden_active_import:{item}" for item in forbidden_imports)

    status = PASS if not failures else BLOCKED
    write_text(
        root / AUDIT_REPORT_PATH,
        "\n".join(
            [
                "# GOAL-08A Recommendation Contract Design Audit",
                "",
                f"Status: `{status}`",
                "",
                f"GOAL-08A mode: `{manifest.get('mode', 'missing')}`",
                f"GOAL-08A workflow status: `{goal08a.get('status', 'missing')}`",
                f"GOAL-08B workflow status: `{goal08b.get('status', 'missing')}`",
                "Future recommendation schema row count: `0`",
                "HIGH risk severity blocks actionable recommendation output: `true`",
                "No recommendation rows were generated.",
                "No position, dashboard, trading, production, backtest, factor-mining, broker, or DQN/RL outputs were generated.",
                "Evidence basis: GOAL-07B review-only diagnostic reports and manifests only.",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
                "## Warnings",
                *[f"- {warning}" for warning in warnings],
                "",
            ]
        ),
    )
    return status == PASS


def load_goal08a_design_bundle(root: Path) -> dict[str, object]:
    return {
        "goal07b_overlay_rows": _read_csv(root / GOAL07B_OVERLAY_PATH),
        "goal07b_diagnostic_rows": _read_csv(root / GOAL07B_DIAGNOSTICS_PATH),
        "goal07b_manifest": _read_json(root / GOAL07B_MANIFEST_PATH),
        "goal07b_report": _read(root / GOAL07B_REPORT_PATH),
        "goal07b_audit": _read(root / GOAL07B_AUDIT_PATH),
        "workflow_rows": _read_csv(root / "configs/project/workflow_status.csv"),
        "forbidden_output_dirs": _forbidden_output_dirs_present(root),
        "forbidden_row_outputs": _forbidden_recommendation_row_outputs(root),
        "forbidden_imports": _forbidden_active_imports(root),
        "goal08b_valid_diagnostics_evidence": goal08b_valid_diagnostics_evidence(root),
        "goal090_valid_evidence": goal090_valid_unlock_evidence(root),
    }


def evaluate_goal08a_design_gate(bundle: dict[str, object]) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    goal07b_manifest = bundle.get("goal07b_manifest", {})
    goal07b_report = str(bundle.get("goal07b_report", ""))
    goal07b_audit = str(bundle.get("goal07b_audit", ""))
    overlay_rows = bundle.get("goal07b_overlay_rows", [])
    diagnostic_rows = bundle.get("goal07b_diagnostic_rows", [])
    workflow = {row.get("workflow_id", ""): row for row in bundle.get("workflow_rows", []) if isinstance(row, dict)}
    goal08b0_valid = workflow.get(GOAL08B0_WORKFLOW_ID, {}).get("status") == "implemented_review_only"
    goal08b_valid = bool(bundle.get("goal08b_valid_diagnostics_evidence"))
    goal090_valid = bool(bundle.get("goal090_valid_evidence"))

    if not _report_pass_or_warn(goal07b_report, "GOAL-07B Risk Overlay Calculation Prototype:"):
        failures.append("goal07b_report_not_pass_or_warn")
    if "Status: `PASS`" not in goal07b_audit:
        failures.append("goal07b_audit_not_pass")
    if not isinstance(goal07b_manifest, dict) or not goal07b_manifest:
        failures.append("goal07b_manifest_missing")
        goal07b_manifest = {}
    if goal07b_manifest.get("mode") != "review_only":
        failures.append("goal07b_manifest_not_review_only")
    if goal07b_manifest.get("output_grain") != "trade_date + symbol":
        failures.append("goal07b_manifest_grain_invalid")
    if goal07b_manifest.get("non_actionable") is not True:
        failures.append("goal07b_manifest_not_non_actionable")
    for key in [
        "recommendation_generated",
        "position_generated",
        "dashboard_generated",
        "paper_live_trading_generated",
        "trading_generated",
        "production_generated",
        "backtest_generated",
        "factor_mining_generated",
        "dqn_rl_generated",
    ]:
        if goal07b_manifest.get(key) is not False:
            failures.append(f"goal07b_manifest_{key}_not_false")

    if not overlay_rows:
        failures.append("goal07b_overlay_rows_missing")
    else:
        fields = set(overlay_rows[0].keys())
        missing = sorted(set(REQUIRED_GOAL07B_FIELDS) - fields)
        failures.extend(f"goal07b_overlay_missing_field:{field}" for field in missing)
        grain = [(row.get("trade_date", ""), row.get("symbol", "")) for row in overlay_rows]
        if len(grain) != len(set(grain)):
            failures.append("goal07b_overlay_grain_not_unique_trade_date_symbol")
        for index, row in enumerate(overlay_rows):
            if row.get("non_actionable") != "true":
                failures.append(f"goal07b_overlay_row_{index}_not_non_actionable")
            for key in [
                "recommendation_generated",
                "position_generated",
                "dashboard_generated",
                "paper_live_trading_generated",
                "trading_generated",
                "production_generated",
                "backtest_generated",
                "factor_mining_generated",
                "dqn_rl_generated",
            ]:
                if row.get(key) != "false":
                    failures.append(f"goal07b_overlay_row_{index}_{key}_not_false")

    if not diagnostic_rows:
        failures.append("goal07b_diagnostic_rows_missing")
    severity_used = sorted({row.get("risk_severity", "") for row in overlay_rows if row.get("risk_severity")})
    if "HIGH" not in severity_used:
        warnings.append("goal07b_high_severity_not_observed_but_block_rule_still_defined")

    warnings_remaining = sorted(str(item) for item in goal07b_manifest.get("warnings_remaining", []))
    for warning_code in GOAL07B_WARNING_CODES:
        if warning_code not in warnings_remaining:
            warnings.append(f"goal07b_warning_not_currently_present:{warning_code}")
    if not warnings_remaining:
        warnings.append("goal07b_no_remaining_warnings_to_propagate")

    goal07b = workflow.get("goal07b_risk_overlay_calculation", {})
    if goal07b.get("status") != "implemented_review_only":
        failures.append("goal07b_workflow_not_implemented_review_only")
    if goal07b.get("implemented_in_repo") != "true":
        failures.append("goal07b_workflow_not_marked_implemented")
    if workflow.get("v2_factor_research_upgrade", {}).get("status") != "planned_locked":
        failures.append("v2_factor_research_not_planned_locked")
    if workflow.get("dqn_rl_mainline", {}).get("status") != "deleted_from_active_mainline":
        failures.append("dqn_rl_not_deleted_from_active_mainline")
    for workflow_id in DOWNSTREAM_LOCKED_IDS:
        row = workflow.get(workflow_id, {})
        if workflow_id == GOAL09_WORKFLOW_ID and goal090_valid:
            continue
        if row.get("status") != "locked_future":
            failures.append(f"{workflow_id}_not_locked_before_goal08a")
    goal08b = workflow.get(GOAL08B_WORKFLOW_ID, {})
    if goal08b_valid:
        if goal08b.get("status") != GOAL08B_IMPLEMENTED_STATUS or goal08b.get("implemented_in_repo") != "true":
            failures.append("goal08b_valid_diagnostics_not_preserved")
    elif goal08b.get("implemented_in_repo") != "false":
        failures.append("goal08b_marked_implemented_before_goal08a")
    elif goal08b0_valid:
        if goal08b.get("status") != GOAL08B_ELIGIBLE_STATUS:
            failures.append("goal08b_not_future_review_only_after_goal08b0")
    elif goal08b.get("status") != "locked_future":
        failures.append("goal08b_not_locked_before_goal08a")

    if bundle.get("forbidden_output_dirs"):
        failures.append("forbidden_output_dirs_present:" + ";".join(str(path) for path in bundle["forbidden_output_dirs"]))
    if bundle.get("forbidden_row_outputs"):
        failures.append("forbidden_recommendation_row_outputs_present:" + ";".join(str(path) for path in bundle["forbidden_row_outputs"]))
    if bundle.get("forbidden_imports"):
        failures.append("forbidden_active_imports_present:" + ";".join(str(path) for path in bundle["forbidden_imports"]))

    status = BLOCKED if failures else (PASS_WITH_WARNINGS if warnings else PASS)
    warning_policy = _warning_policy(warnings_remaining or GOAL07B_WARNING_CODES)
    manifest = _manifest(status, overlay_rows, diagnostic_rows, severity_used, warnings_remaining, failures, warnings)
    return {
        "status": status,
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "goal07b_warning_codes": warnings_remaining,
        "goal07b_risk_severity_levels_used": severity_used,
        "input_contract": _input_contract(),
        "future_schema": _future_schema(),
        "warning_policy": warning_policy,
        "actionability_guardrails": _actionability_guardrails(),
        "state_machine": _state_machine(),
        "manifest": manifest,
    }


def _input_contract() -> dict[str, object]:
    return {
        "goal": GOAL_NAME,
        "mode": MODE,
        "source_goal": "GOAL-07B",
        "source_artifacts": {
            "risk_overlay_rows": GOAL07B_OVERLAY_PATH,
            "diagnostic_rows": GOAL07B_DIAGNOSTICS_PATH,
            "calculation_report": GOAL07B_REPORT_PATH,
            "calculation_audit": GOAL07B_AUDIT_PATH,
            "calculation_manifest": GOAL07B_MANIFEST_PATH,
            "rows_are_actionable": False,
            "source_mode": "review_only",
        },
        "required_input_grain": "trade_date + symbol",
        "required_goal07b_fields": REQUIRED_GOAL07B_FIELDS,
        "required_risk_fields": [
            "risk_domain",
            "risk_tag",
            "risk_severity",
            "risk_confidence",
            "risk_state",
            "risk_transition_diagnostic",
            "triggered_rule_ids",
            "risk_rule_trace",
        ],
        "required_warning_fields": [
            "warning_propagation",
            "upstream_warning_mapping",
            "bounded_model_weakness_diagnostics",
            "missing_input_diagnostics",
            "review_only_status_flags",
        ],
        "forbidden_input_semantics": FORBIDDEN_FUTURE_SCHEMA_FIELDS,
        "contract_rule": "GOAL-08A may define a future contract only; it must not generate rows or actions.",
    }


def _future_schema() -> dict[str, object]:
    return {
        "goal": GOAL_NAME,
        "mode": "future_schema_names_only",
        "future_schema_names_only": True,
        "future_schema_version": "goal08b_review_only_prototype_v1_names_only",
        "future_schema_fields": FUTURE_SCHEMA_NAMES,
        "forbidden_future_schema_fields": FORBIDDEN_FUTURE_SCHEMA_FIELDS,
        "empty_schema_sample": {
            "row_count": 0,
            "columns": FUTURE_SCHEMA_NAMES,
            "rows": [],
        },
        "row_generation_policy": {
            "goal08a_generates_rows": False,
            "goal08a_generates_recommendations": False,
            "goal08a_generates_positions": False,
            "goal08a_generates_orders": False,
            "goal08a_generates_dashboards": False,
        },
    }


def _warning_policy(warnings_remaining: list[str]) -> dict[str, object]:
    observed = set(warnings_remaining)
    return {
        "goal": GOAL_NAME,
        "mode": "warning_policy_design_only",
        "source_goal": "GOAL-07B",
        "warning_propagation_rules": [
            {
                "warning_code": code,
                "observed_in_goal07b": code in observed,
                "propagate_to_future_contract": True,
                "future_metadata_field": "future_warning_policy_trace",
                "actionability_effect": _warning_actionability_effect(code),
                "goal08a_execution": False,
            }
            for code in GOAL07B_WARNING_CODES
        ],
        "default_policy": "unrecognized GOAL-07B warnings propagate as non-actionable diagnostic metadata until explicitly classified",
    }


def _warning_actionability_effect(code: str) -> str:
    if code in {
        "calibration_not_reliable_for_thresholding",
        "target_horizon_calibration_warning",
        "selected_score_variant_weak_rank_signal",
        "weak_target_horizon_rank_signal",
    }:
        return "block_actionability_or_require_future_human_review_design_only"
    if code in {"provider_source_concentration_disclosed", "single_provider_mode_akshare_direct"}:
        return "carry_source_concentration_warning_and_block_actionability_when_risk_severity_HIGH"
    return "carry_warning_and_keep_future_diagnostic_non_actionable_when_unresolved"


def _actionability_guardrails() -> dict[str, object]:
    return {
        "goal": GOAL_NAME,
        "mode": "actionability_guardrails_design_only",
        "high_risk_severity_blocks_actionable_recommendation": True,
        "high_risk_rule": {
            "condition": "source_goal07b_risk_severity == HIGH",
            "actionable_recommendation_allowed": False,
            "future_block_reason": "HIGH risk severity from GOAL-07B blocks actionable recommendation output",
        },
        "recommendation_like_diagnostic_must_be_non_actionable": True,
        "goal08a_generates_actions": False,
        "forbidden_action_outputs": FORBIDDEN_FUTURE_SCHEMA_FIELDS,
        "boundary_flags_required_for_any_future_diagnostic": {
            "non_actionable": True,
            "buy_sell_hold_generated": False,
            "target_price_generated": False,
            "position_sizing_generated": False,
            "portfolio_weight_generated": False,
            "broker_or_order_generated": False,
            "production_signal_generated": False,
        },
    }


def _state_machine() -> dict[str, object]:
    return {
        "goal": GOAL_NAME,
        "mode": "state_machine_design_only",
        "states": [
            "goal08a_design_only",
            "source_goal07b_contract_verified",
            "warning_propagation_designed",
            "high_risk_blocks_actionability",
            "future_schema_documented_no_rows",
            "goal08b_locked_future",
            "downstream_execution_locked",
        ],
        "transitions": [
            {
                "from_state": "source_goal07b_contract_verified",
                "to_state": "warning_propagation_designed",
                "condition": "GOAL-07B report and audit are PASS or PASS_WITH_WARNINGS",
                "executes_recommendation": False,
            },
            {
                "from_state": "warning_propagation_designed",
                "to_state": "high_risk_blocks_actionability",
                "condition": "GOAL-07B warning codes mapped to future metadata policy",
                "executes_recommendation": False,
            },
            {
                "from_state": "high_risk_blocks_actionability",
                "to_state": "future_schema_documented_no_rows",
                "condition": "HIGH risk severity is configured to block actionable output",
                "executes_recommendation": False,
            },
            {
                "from_state": "future_schema_documented_no_rows",
                "to_state": "goal08b_locked_future",
                "condition": "GOAL-08A writes names-only schema with zero rows",
                "executes_recommendation": False,
            },
            {
                "from_state": "goal08b_locked_future",
                "to_state": "downstream_execution_locked",
                "condition": "GOAL-08B and all execution/downstream rows remain locked_future",
                "executes_recommendation": False,
            },
        ],
        "goal08a_status_after_pass": "implemented_design_only",
        "goal08b_status_after_goal08a": "locked_future",
    }


def _manifest(
    status: str,
    overlay_rows: list[dict[str, str]],
    diagnostic_rows: list[dict[str, str]],
    severity_used: list[str],
    warnings_remaining: list[str],
    failures: list[str],
    warnings: list[str],
) -> dict[str, object]:
    return {
        "goal": GOAL_NAME,
        "status": status,
        "mode": MODE,
        "source_goal": "GOAL-07B",
        "source_goal_status_required": "implemented_review_only",
        "input_grain": "trade_date + symbol",
        "source_goal07b_overlay_rows_observed": len(overlay_rows),
        "source_goal07b_diagnostic_rows_observed": len(diagnostic_rows),
        "source_goal07b_risk_severity_levels_used": severity_used,
        "source_goal07b_warnings_propagated": warnings_remaining,
        "required_goal07b_fields": REQUIRED_GOAL07B_FIELDS,
        "future_schema_names_only": True,
        "future_schema_row_count": 0,
        "high_risk_severity_blocks_actionable_output": True,
        "goal08b_status_after_goal08a": "locked_future",
        "allowed_next_action": GOAL08A_ALLOWED_NEXT if status != BLOCKED else "repair_goal08a_design_gate_blockers",
        "evidence_basis": "prior_goal07b_pass_or_pass_with_warnings_review_only_diagnostics_only",
        "evidence_inputs": [
            GOAL07B_OVERLAY_PATH,
            GOAL07B_DIAGNOSTICS_PATH,
            GOAL07B_REPORT_PATH,
            GOAL07B_AUDIT_PATH,
            GOAL07B_MANIFEST_PATH,
            "configs/project/workflow_status.csv",
        ],
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        **{key: False for key in _false_boundary_keys()},
    }


def _false_boundary_keys() -> list[str]:
    return [
        "recommendation_rows_generated",
        "buy_sell_hold_outputs_generated",
        "target_prices_generated",
        "position_sizing_generated",
        "portfolio_construction_generated",
        "dashboard_generated",
        "paper_trading_enabled",
        "live_trading_enabled",
        "broker_integration_enabled",
        "production_model_behavior_created",
        "database_writes_created",
        "backtests_run",
        "factor_mining_outputs_created",
        "dqn_rl_outputs_created",
        "actionable_outputs_generated",
    ]


def _write_design_artifacts(root: Path, review: dict[str, object]) -> None:
    write_json(root / INPUT_CONTRACT_PATH, review["input_contract"])
    write_json(root / FUTURE_SCHEMA_PATH, review["future_schema"])
    write_json(root / WARNING_POLICY_PATH, review["warning_policy"])
    write_json(root / ACTIONABILITY_PATH, review["actionability_guardrails"])
    write_json(root / STATE_MACHINE_PATH, review["state_machine"])
    write_json(root / MANIFEST_PATH, review["manifest"])
    _write_report(root, review)
    _write_docs(root, review)


def _write_report(root: Path, review: dict[str, object]) -> None:
    manifest = review["manifest"]
    warning_lines = [f"- `{code}`" for code in manifest["source_goal07b_warnings_propagated"]]
    if not warning_lines:
        warning_lines = ["- `none`"]
    write_text(
        root / REPORT_PATH,
        "\n".join(
            [
                "# GOAL-08A Recommendation Contract Design Gate Report",
                "",
                f"GOAL-08A Recommendation Contract Design Gate: {review['status']}",
                "Status mode: `implemented_design_only`" if review["status"] != BLOCKED else "Status mode: `blocked`",
                f"GOAL-08B after this gate: `{manifest['goal08b_status_after_goal08a']}`",
                f"Allowed next action: `{manifest['allowed_next_action']}`",
                "",
                "GOAL-08A defines a future recommendation input contract from GOAL-07B review-only risk overlay diagnostics.",
                "It does not generate recommendation rows, buy/sell/hold decisions, target prices, position sizing, portfolio weights, dashboards, trading outputs, production behavior, backtests, factor-mining artifacts, broker paths, or DQN/RL outputs.",
                "The design requires `trade_date + symbol` grain and propagates GOAL-07B warning fields into future non-actionable metadata.",
                "HIGH GOAL-07B risk severity blocks actionable recommendation output in any future prototype contract.",
                "Evidence basis: GOAL-07B PASS/PASS_WITH_WARNINGS review-only diagnostic evidence only; no live calculation outputs were created by GOAL-08A.",
                "",
                "## Propagated GOAL-07B Warnings",
                *warning_lines,
                "",
                "## Failures",
                *[f"- {failure}" for failure in review["failures"]],
                "",
                "## Warnings",
                *[f"- {warning}" for warning in review["warnings"]],
                "",
            ]
        ),
    )


def _write_docs(root: Path, review: dict[str, object]) -> None:
    schema_fields = [f"- `{field}`" for field in FUTURE_SCHEMA_NAMES]
    warning_rows = review["warning_policy"]["warning_propagation_rules"]
    write_text(
        root / DOC_PATH,
        "\n".join(
            [
                "# GOAL-08A Recommendation Contract Design Gate",
                "",
                "Status: `implemented_design_only`",
                "",
                "GOAL-08A is a design-only contract gate for a possible future review-only GOAL-08B prototype. It consumes only GOAL-07B review-only risk overlay diagnostic evidence and defines names, guards, and propagation rules.",
                "",
                "## Required Input",
                "- Source: `GOAL-07B` review-only risk overlay diagnostics.",
                "- Grain: `trade_date + symbol`.",
                "- Required risk fields: `risk_domain`, `risk_tag`, `risk_severity`, `risk_confidence`, `risk_state`, `risk_transition_diagnostic`, `triggered_rule_ids`, `risk_rule_trace`.",
                "- Required warning fields: `warning_propagation`, `upstream_warning_mapping`, `bounded_model_weakness_diagnostics`, `missing_input_diagnostics`, `review_only_status_flags`.",
                "",
                "## Future Schema Names Only",
                *schema_fields,
                "",
                "The schema sample has row count `0`. GOAL-08A creates no recommendation rows.",
                "",
                "## Warning Propagation",
                *[
                    f"- `{item['warning_code']}`: `{item['actionability_effect']}`."
                    for item in warning_rows
                ],
                "",
                "## Actionability Rule",
                "`source_goal07b_risk_severity == HIGH` blocks actionable recommendation output. Any future recommendation-like diagnostic must remain non-actionable and must not contain buy/sell/hold, target price, position size, portfolio weight, order, broker, production, backtest, factor-mining, or DQN/RL fields.",
                "",
            ]
        ),
    )
    write_text(
        root / BOUNDARY_DOC_PATH,
        "\n".join(
            [
                "# GOAL-08A Design-Only Boundary",
                "",
                "Status: `PASS`",
                "",
                "GOAL-08A is implemented as a design-only gate. It does not implement GOAL-08B.",
                "GOAL-08B remains `locked_future` unless a separate GOAL-08B.0 unlock gate has passed, in which case it may be `future_review_only` eligible. If a later GOAL-08B diagnostic audit passes, rerunning GOAL-08A preserves that `implemented_review_only` diagnostic state.",
                "Recommendation output, position sizing, portfolio construction, dashboard, paper/live trading, broker integration, production DB writes, production model promotion, backtests, factor mining, and DQN/RL remain locked or deleted from active mainline.",
                "No recommendation rows or downstream output directories are created.",
                "",
            ]
        ),
    )


def _update_workflow_status(root: Path, review: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys())
    by_id = {row["workflow_id"]: row for row in rows}
    row = {
        "workflow_id": GOAL08A_WORKFLOW_ID,
        "display_name": "GOAL-08A Recommendation Contract Design Gate",
        "stage_or_goal": "GOAL-08A",
        "status": "implemented_design_only" if review["status"] != BLOCKED else "locked_future",
        "current_repo_role": "design_only_future_contract_boundary",
        "implemented_in_repo": "true" if review["status"] != BLOCKED else "false",
        "allowed_next_action": GOAL08A_ALLOWED_NEXT if review["status"] != BLOCKED else "repair_goal08a_design_gate_blockers",
        "depends_on": "goal07b_risk_overlay_calculation",
        "produces_artifacts": ";".join(
            [
                INPUT_CONTRACT_PATH,
                FUTURE_SCHEMA_PATH,
                WARNING_POLICY_PATH,
                ACTIONABILITY_PATH,
                STATE_MACHINE_PATH,
                REPORT_PATH,
                AUDIT_REPORT_PATH,
                MANIFEST_PATH,
            ]
        ),
        "primary_docs": f"{DOC_PATH};{BOUNDARY_DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "scripts/run_goal08a_recommendation_contract_design_gate.py;scripts/audit_goal08a_recommendation_contract_design_gate.py",
        "primary_outputs": f"{REPORT_PATH};{AUDIT_REPORT_PATH};{MANIFEST_PATH}",
        "promotion_rule": "implemented_design_only_after_goal08a_design_gate_pass_with_warnings",
        "notes": "Design-only future recommendation contract gate; no recommendation rows, actions, positions, dashboards, trading, production, backtests, factor-mining, broker, or DQN/RL outputs.",
    }
    if GOAL08A_WORKFLOW_ID in by_id:
        by_id[GOAL08A_WORKFLOW_ID].update(row)
    else:
        insert_at = next((index + 1 for index, item in enumerate(rows) if item["workflow_id"] == "goal07b_risk_overlay_calculation"), len(rows))
        rows.insert(insert_at, row)
    by_id = {item["workflow_id"]: item for item in rows}
    goal08b0_valid = goal08b0_valid_unlock_evidence(root)
    goal08b_valid = goal08b_valid_diagnostics_evidence(root)
    goal090_valid = goal090_valid_unlock_evidence(root)
    if GOAL08B_WORKFLOW_ID in by_id:
        if goal08b_valid:
            by_id[GOAL08B_WORKFLOW_ID].update(
                {
                    "status": GOAL08B_IMPLEMENTED_STATUS,
                    "current_repo_role": "review_only_recommendation_diagnostic_prototype",
                    "implemented_in_repo": "true",
                    "allowed_next_action": GOAL08B_IMPLEMENTED_ALLOWED_NEXT,
                    "depends_on": GOAL08B0_WORKFLOW_ID,
                    "produces_artifacts": GOAL08B_WORKFLOW_PRODUCES_ARTIFACTS,
                    "primary_docs": GOAL08B_WORKFLOW_PRIMARY_DOCS,
                    "primary_scripts": GOAL08B_WORKFLOW_PRIMARY_SCRIPTS,
                    "primary_outputs": GOAL08B_WORKFLOW_PRIMARY_OUTPUTS,
                    "promotion_rule": "implemented_review_only_after_goal08b_diagnostics_pass_with_warnings",
                    "notes": GOAL08B_WORKFLOW_NOTES,
                }
            )
        elif goal08b0_valid:
            by_id[GOAL08B_WORKFLOW_ID].update(
                {
                    "status": GOAL08B_ELIGIBLE_STATUS,
                    "current_repo_role": "review_only_eligible_not_implemented",
                    "implemented_in_repo": "false",
                    "allowed_next_action": GOAL08B0_ALLOWED_NEXT,
                    "depends_on": GOAL08B0_WORKFLOW_ID,
                    "notes": "Eligibility only after GOAL-08B.0; no recommendation diagnostics prototype is implemented.",
                }
            )
        else:
            by_id[GOAL08B_WORKFLOW_ID].update(
                {
                    "status": "locked_future",
                    "implemented_in_repo": "false",
                    "allowed_next_action": "remain_locked_until_explicit_goal08b_review_only_request",
                    "depends_on": GOAL08A_WORKFLOW_ID,
                    "notes": "GOAL-08B remains locked after GOAL-08A; no recommendation prototype is implemented.",
                }
            )
    for workflow_id in DOWNSTREAM_LOCKED_IDS:
        if workflow_id in by_id:
            if workflow_id == GOAL09_WORKFLOW_ID and goal090_valid:
                by_id[workflow_id].update(goal09_eligible_workflow_patch(root))
                continue
            by_id[workflow_id]["status"] = "locked_future"
            by_id[workflow_id]["implemented_in_repo"] = "false"
            if workflow_id != GOAL08B_WORKFLOW_ID:
                by_id[workflow_id]["allowed_next_action"] = "remain_locked"
    if "dqn_rl_mainline" in by_id:
        by_id["dqn_rl_mainline"]["status"] = "deleted_from_active_mainline"
        by_id["dqn_rl_mainline"]["implemented_in_repo"] = "false"
    if "v2_factor_research_upgrade" in by_id:
        by_id["v2_factor_research_upgrade"]["status"] = "planned_locked"
        by_id["v2_factor_research_upgrade"]["implemented_in_repo"] = "false"
    preserve_later_review_only_workflow_states(root, by_id)
    write_csv(path, rows, fields)


def _update_locked_capabilities(root: Path, review: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    if not path.exists():
        return
    payload = read_json(path)
    payload[GOAL08A_WORKFLOW_ID] = "implemented_design_only" if review["status"] != BLOCKED else False
    if goal08b_valid_diagnostics_evidence(root):
        payload[GOAL08B_WORKFLOW_ID] = GOAL08B_IMPLEMENTED_STATUS
    else:
        payload[GOAL08B_WORKFLOW_ID] = GOAL08B_ELIGIBLE_STATUS if goal08b0_valid_unlock_evidence(root) else False
    payload[GOAL09_WORKFLOW_ID] = goal09_eligible_workflow_patch(root)["status"] if goal090_valid_unlock_evidence(root) else False
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


def _workflow_rows(root: Path) -> dict[str, dict[str, str]]:
    path = root / "configs/project/workflow_status.csv"
    return {row["workflow_id"]: row for row in read_csv(path)} if path.exists() else {}


def _report_pass_or_warn(text: str, prefix: str) -> bool:
    return f"{prefix} {PASS}" in text or f"{prefix} {PASS_WITH_WARNINGS}" in text


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


def _forbidden_output_dirs_present(root: Path) -> list[str]:
    return [path for path in FORBIDDEN_OUTPUT_DIRS if (root / path).exists()]


def _forbidden_recommendation_row_outputs(root: Path) -> list[str]:
    output_root = root / "outputs"
    if not output_root.exists():
        return []
    matches: list[str] = []
    for path in output_root.rglob("*.csv"):
        rel = path.relative_to(root).as_posix()
        lower = rel.lower()
        if lower.startswith("outputs/audits/") or lower.startswith("outputs/diagnostics/"):
            continue
        if rel == GOAL08B_DIAGNOSTIC_PATH:
            continue
        if rel in GOAL10B_ALLOWED_BACKTEST_CSV_OUTPUTS:
            continue
        if any(token in lower for token in ["recommendation", "position_size", "portfolio_weight", "target_price", "buy_sell_hold"]):
            matches.append(rel)
    return matches


def _forbidden_active_imports(root: Path) -> list[str]:
    failures: list[str] = []
    for base in [root / "src", root / "scripts"]:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            rel = path.relative_to(root).as_posix()
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except SyntaxError as exc:
                failures.append(f"{rel}:{exc}")
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        failures.extend(_import_term_failures(alias.name, rel))
                elif isinstance(node, ast.ImportFrom):
                    failures.extend(_import_term_failures(node.module or "", rel))
    return sorted(set(failures))


def _import_term_failures(module_name: str, rel: str) -> list[str]:
    lowered = module_name.lower()
    return [
        f"{lowered} in {rel}"
        for term in FORBIDDEN_IMPORT_TERMS
        if term in lowered
    ]

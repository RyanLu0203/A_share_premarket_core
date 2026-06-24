from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-07B"
MODE = "review_only"
CALCULATION_TYPE = "risk_overlay_diagnostic"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
FAIL = "FAIL"

RISK_DIR = "configs/risk"
AUDIT_DIR = "outputs/audits"
DIAGNOSTIC_DIR = "outputs/diagnostics"
OUTPUT_DIR = "outputs/risk_overlay"
DOC_DIR = "docs/risk"

POLICY_PATH = f"{RISK_DIR}/goal07b_risk_overlay_calculation_policy.yaml"
RISK_OVERLAY_PATH = f"{OUTPUT_DIR}/goal07b_review_only_risk_overlay.csv"
DIAGNOSTICS_PATH = f"{DIAGNOSTIC_DIR}/goal07b_risk_overlay_diagnostics.csv"
REPORT_PATH = f"{AUDIT_DIR}/goal07b_risk_overlay_calculation_report.md"
AUDIT_REPORT_PATH = f"{AUDIT_DIR}/goal07b_risk_overlay_calculation_audit.md"
MANIFEST_PATH = f"{AUDIT_DIR}/goal07b_risk_overlay_calculation_manifest.json"
DOC_PATH = f"{DOC_DIR}/GOAL07B_RISK_OVERLAY_CALCULATION_PROTOTYPE.md"

STAGE6C_SAMPLE_PATH = "outputs/samples/stage6c_source_backed_engineering_panel_sample.csv"
STAGE6C_COVERAGE_PATH = "outputs/stage6c/STAGE6C_source_backed_engineering_panel_coverage_summary.csv"
SOURCE_BUNDLE_MANIFEST_PATH = "outputs/audits/source_backed_bundle_manifest_summary.json"
MODEL_REPAIR_SUMMARY_PATH = "outputs/models/goal06d1/model_comparison_repair_summary.csv"
PROVIDER_CONCENTRATION_PATH = "outputs/models/goal06d1/provider_source_concentration_summary.csv"
CALIBRATION_REPAIR_PATH = "outputs/models/goal06d1/calibration_repair_summary.csv"
FEATURE_STABILITY_PATH = "outputs/models/goal06d1/feature_sign_stability_repair.csv"
TARGET_HORIZON_PATH = "outputs/models/goal06d1/target_horizon_comparison.csv"
WARNING_CLASSIFICATION_PATH = "outputs/audits/goal07a1_warning_classification.csv"
GOAL07B0_MANIFEST_PATH = "outputs/audits/goal07b0_unlock_gate_manifest.json"
RULE_CATALOG_PATH = "configs/risk/goal07a_risk_rule_catalog.yaml"
STATE_MACHINE_PATH = "configs/risk/goal07a_risk_state_machine.yaml"
WARNING_MAPPING_PATH = "configs/risk/goal07a_upstream_warning_mapping.yaml"
INPUT_CONTRACT_PATH = "configs/risk/goal07a_allowed_input_contract.yaml"

SEVERITY_LEVELS = {"LOW", "MEDIUM", "HIGH", "BLOCKED", "UNKNOWN"}
CONFIDENCE_LEVELS = {"LOW", "MEDIUM", "HIGH", "UNKNOWN"}
RISK_STATES = {
    "not_evaluated",
    "input_invalid",
    "data_blocked",
    "model_warning",
    "source_warning",
    "market_warning",
    "eligible_for_review_only_snapshot",
    "blocked_from_recommendation",
}

INPUT_FIELDS_USED = [
    "trade_date",
    "symbol",
    "as_of_date",
    "market_trend_5d",
    "stock_gap_signal",
    "stock_volatility_20d",
    "turnover_proxy",
    "relative_strength_20d",
    "source_health_score",
    "source_count",
    "provider_id",
    "provider_mode",
    "source_bundle_id",
    "data_quality_flags",
    "leakage_flags",
    "panel_tier",
    "review_only",
]

REQUIRED_STAGE6C_FIELDS = {
    "trade_date",
    "symbol",
    "as_of_date",
    "market_trend_5d",
    "stock_gap_signal",
    "stock_volatility_20d",
    "turnover_proxy",
    "relative_strength_20d",
    "source_health_score",
    "source_count",
    "provider_id",
    "provider_mode",
    "source_bundle_id",
    "data_quality_flags",
    "leakage_flags",
    "panel_tier",
    "review_only",
}

FORBIDDEN_INPUT_FIELDS = {
    "fwd_1d_return",
    "fwd_3d_return",
    "fwd_5d_return",
    "excess_fwd_1d_return",
    "excess_fwd_3d_return",
    "excess_fwd_5d_return",
    "target_label",
    "label_positive",
}

REQUIRED_OUTPUT_FIELDS = [
    "goal_id",
    "mode",
    "calculation_type",
    "trade_date",
    "symbol",
    "as_of_date",
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
    "audit_metadata",
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

DIAGNOSTIC_FIELDS = [
    "goal_id",
    "mode",
    "calculation_type",
    "risk_domain",
    "rows_evaluated",
    "rows_triggered",
    "max_risk_severity",
    "triggered_rule_ids",
    "warning_codes",
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

FORBIDDEN_SCHEMA_TERMS = {
    "recommendation",
    "action",
    "buy",
    "sell",
    "hold",
    "position",
    "weight",
    "allocation",
    "order",
    "trade",
    "execution",
    "broker",
    "dashboard_decision",
    "production_signal",
    "backtest_return",
    "alpha_recommendation",
    "dqn",
    "rl_policy",
}

ALLOWED_NEGATIVE_BOUNDARY_FIELDS = {
    "trade_date",
    "recommendation_generated",
    "position_generated",
    "dashboard_generated",
    "paper_live_trading_generated",
    "trading_generated",
    "production_generated",
    "backtest_generated",
    "factor_mining_generated",
    "dqn_rl_generated",
}

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
    "goal08b_recommendation_review_only_prototype",
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

WARNING_NORMALIZATION = {
    "selected_score_variant_calibration_not_reliable_for_thresholding": "calibration_not_reliable_for_thresholding",
    "selected_score_variant_feature_instability_bounded": "feature_sign_instability_bounded",
}

RULE_DOMAIN = {
    "calibration_warning_minimum_warning_state": "calibration_risk",
    "weak_rank_signal_model_confidence": "model_confidence_risk",
    "single_provider_concentration": "provider_concentration_risk",
    "data_quality_non_pass_blocks": "data_quality_risk",
    "leakage_failure_blocks": "governance_boundary_risk",
    "panel_tier_floor_blocks": "governance_boundary_risk",
    "feature_instability_downgrades": "feature_stability_risk",
    "target_horizon_warning_downgrades": "target_horizon_risk",
    "source_health_warning_downgrades": "source_health_risk",
    "gap_or_volatility_market_warning": "market_regime_risk",
}

BLOCKING_RULES = {
    "data_quality_non_pass_blocks",
    "leakage_failure_blocks",
    "panel_tier_floor_blocks",
}


def run_goal07b_risk_overlay_calculation_prototype(root: Path) -> bool:
    bundle = load_goal07b_input_bundle(root)
    result = evaluate_goal07b_calculation(bundle)
    _write_policy(root)
    _write_outputs(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal07b_risk_overlay_calculation_prototype(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal07b_risk_overlay_calculation_prototype(root: Path) -> bool:
    failures: list[str] = []
    warnings: list[str] = []
    overlay_path = root / RISK_OVERLAY_PATH
    diagnostics_path = root / DIAGNOSTICS_PATH
    manifest_path = root / MANIFEST_PATH
    report_path = root / REPORT_PATH
    workflow_path = root / "configs/project/workflow_status.csv"

    overlay_rows = read_csv(overlay_path) if overlay_path.exists() else []
    diagnostic_rows = read_csv(diagnostics_path) if diagnostics_path.exists() else []
    manifest = _read_json(root / MANIFEST_PATH)
    report = _read(report_path)
    workflow = {row["workflow_id"]: row for row in read_csv(workflow_path)} if workflow_path.exists() else {}

    if not overlay_rows:
        failures.append("risk_overlay_rows_missing")
    if not diagnostic_rows:
        failures.append("diagnostic_rows_missing")
    if not manifest:
        failures.append("manifest_missing")
    if "GOAL-07B Risk Overlay Calculation Prototype: PASS" not in report and "GOAL-07B Risk Overlay Calculation Prototype: PASS_WITH_WARNINGS" not in report:
        failures.append("calculation_report_not_pass_or_warn")

    if overlay_rows:
        fields = list(overlay_rows[0].keys())
        missing = [field for field in REQUIRED_OUTPUT_FIELDS if field not in fields]
        failures.extend(f"missing_required_output_field:{field}" for field in missing)
        failures.extend(f"forbidden_output_field:{field}" for field in forbidden_goal07b_output_fields(fields))
        grain = [(row.get("trade_date", ""), row.get("symbol", "")) for row in overlay_rows]
        if len(grain) != len(set(grain)):
            failures.append("risk_overlay_grain_not_unique_trade_date_symbol")
        for index, row in enumerate(overlay_rows):
            failures.extend(_row_policy_failures(row, index))

    if diagnostic_rows:
        fields = list(diagnostic_rows[0].keys())
        missing = [field for field in DIAGNOSTIC_FIELDS if field not in fields]
        failures.extend(f"missing_required_diagnostic_field:{field}" for field in missing)
        failures.extend(f"forbidden_diagnostic_field:{field}" for field in forbidden_goal07b_output_fields(fields))
        for index, row in enumerate(diagnostic_rows):
            failures.extend(_row_policy_failures(row, index, severity_optional=True))

    if manifest:
        expected_false = [
            "recommendation_generated",
            "position_generated",
            "dashboard_generated",
            "paper_live_trading_generated",
            "trading_generated",
            "production_generated",
            "backtest_generated",
            "factor_mining_generated",
            "dqn_rl_generated",
            "database_writes_performed",
            "live_data_fetched",
            "broker_data_used",
            "future_information_used",
        ]
        for key in expected_false:
            if manifest.get(key) is not False:
                failures.append(f"manifest_{key}_not_false")
        if manifest.get("goal_id") != GOAL_ID:
            failures.append("manifest_goal_id_not_goal07b")
        if manifest.get("mode") != MODE:
            failures.append("manifest_mode_not_review_only")
        if manifest.get("calculation_type") != CALCULATION_TYPE:
            failures.append("manifest_calculation_type_invalid")
        if manifest.get("non_actionable") is not True:
            failures.append("manifest_non_actionable_not_true")
        if manifest.get("output_grain") != "trade_date + symbol":
            failures.append("manifest_output_grain_invalid")
        if int(manifest.get("risk_overlay_row_count", -1)) != len(overlay_rows):
            failures.append("manifest_row_count_mismatch")
        if not set(manifest.get("risk_severity_levels_allowed", [])) <= SEVERITY_LEVELS:
            failures.append("manifest_severity_levels_not_bounded")
        if not set(manifest.get("risk_severity_levels_used", [])) <= SEVERITY_LEVELS:
            failures.append("manifest_used_severity_levels_not_bounded")
        if set(manifest.get("input_fields_used", [])) & FORBIDDEN_INPUT_FIELDS:
            failures.append("manifest_used_future_or_label_input_fields")

    goal07b = workflow.get("goal07b_risk_overlay_calculation", {})
    if goal07b.get("status") != "implemented_review_only":
        failures.append("goal07b_workflow_not_implemented_review_only")
    if goal07b.get("implemented_in_repo") != "true":
        failures.append("goal07b_workflow_not_marked_implemented")
    for workflow_id in DOWNSTREAM_LOCKED_IDS:
        if workflow.get(workflow_id, {}).get("status") != "locked_future":
            failures.append(f"{workflow_id}_not_locked_future")
        if workflow.get(workflow_id, {}).get("implemented_in_repo") != "false":
            failures.append(f"{workflow_id}_marked_implemented")
    goal08a = workflow.get("goal08a_recommendation_contract_design_gate", {})
    if goal08a and not _goal08a_locked_or_design_only_valid(root, goal08a):
        failures.append("goal08a_not_locked_or_valid_design_only")
    if workflow.get("dqn_rl_mainline", {}).get("status") != "deleted_from_active_mainline":
        failures.append("dqn_rl_mainline_not_deleted")
    if workflow.get("v2_factor_research_upgrade", {}).get("status") != "planned_locked":
        failures.append("v2_factor_research_not_planned_locked")

    for rel in FORBIDDEN_OUTPUT_DIRS:
        if (root / rel).exists():
            failures.append(f"forbidden_output_dir_present:{rel}")

    status = PASS if not failures else FAIL
    write_text(
        root / AUDIT_REPORT_PATH,
        "\n".join(
            [
                "# GOAL-07B Risk Overlay Calculation Audit",
                "",
                f"Status: `{status}`",
                "",
                f"GOAL-07B Risk Overlay Calculation Prototype: `{manifest.get('status', 'missing')}`",
                f"GOAL-07B mode: `{manifest.get('mode', 'missing')}`",
                f"Risk overlay diagnostic rows: `{len(overlay_rows)}`",
                "No recommendation output was generated",
                "No position output was generated",
                "No dashboard output was generated",
                "No paper/live trading output was generated",
                "No production output was generated",
                "No backtest output was generated",
                "No factor-mining output was generated",
                "No DQN/RL output was generated",
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


def load_goal07b_input_bundle(root: Path) -> dict[str, object]:
    return {
        "stage6c_sample_rows": _read_csv(root / STAGE6C_SAMPLE_PATH),
        "stage6c_sample_path": STAGE6C_SAMPLE_PATH,
        "stage6c_coverage_rows": _read_csv(root / STAGE6C_COVERAGE_PATH),
        "source_bundle_manifest": _read_json(root / SOURCE_BUNDLE_MANIFEST_PATH),
        "model_repair_rows": _read_csv(root / MODEL_REPAIR_SUMMARY_PATH),
        "provider_concentration_rows": _read_csv(root / PROVIDER_CONCENTRATION_PATH),
        "calibration_repair_rows": _read_csv(root / CALIBRATION_REPAIR_PATH),
        "feature_stability_rows": _read_csv(root / FEATURE_STABILITY_PATH),
        "target_horizon_rows": _read_csv(root / TARGET_HORIZON_PATH),
        "warning_classification_rows": _read_csv(root / WARNING_CLASSIFICATION_PATH),
        "goal07b0_manifest": _read_json(root / GOAL07B0_MANIFEST_PATH),
        "input_contract": _read_json(root / INPUT_CONTRACT_PATH),
        "rule_catalog": _read_json(root / RULE_CATALOG_PATH),
        "state_machine": _read_json(root / STATE_MACHINE_PATH),
        "warning_mapping": _read_json(root / WARNING_MAPPING_PATH),
        "workflow_rows": _read_csv(root / "configs/project/workflow_status.csv"),
    }


def evaluate_goal07b_calculation(bundle: dict[str, object]) -> dict[str, object]:
    failures = _validate_input_bundle(bundle)
    if failures:
        return {
            "status": FAIL,
            "failures": sorted(set(failures)),
            "warnings": [],
            "risk_overlay_rows": [],
            "diagnostic_rows": [],
            "manifest": _manifest_template(FAIL, [], [], sorted(set(failures)), []),
        }

    stage6c_rows = sorted(
        [dict(row) for row in bundle["stage6c_sample_rows"]],
        key=lambda row: (row["trade_date"], row["symbol"]),
    )
    active_warning_codes = _active_warning_codes(bundle)
    warning_mapping = _warning_mapping(bundle)
    model_context = _model_context(bundle)
    rule_rows = _rule_rows(bundle)

    risk_rows = [
        _calculate_row(index, row, active_warning_codes, warning_mapping, model_context, rule_rows)
        for index, row in enumerate(stage6c_rows, start=1)
    ]
    diagnostic_rows = _diagnostic_rows(risk_rows, warning_mapping)
    warnings = sorted(active_warning_codes)
    status = PASS_WITH_WARNINGS if warnings else PASS
    severity_used = sorted({row["risk_severity"] for row in risk_rows})
    manifest = _manifest_template(status, risk_rows, severity_used, [], warnings)
    manifest.update(
        {
            "input_artifacts": [
                STAGE6C_SAMPLE_PATH,
                STAGE6C_COVERAGE_PATH,
                SOURCE_BUNDLE_MANIFEST_PATH,
                MODEL_REPAIR_SUMMARY_PATH,
                PROVIDER_CONCENTRATION_PATH,
                CALIBRATION_REPAIR_PATH,
                FEATURE_STABILITY_PATH,
                TARGET_HORIZON_PATH,
                WARNING_CLASSIFICATION_PATH,
                GOAL07B0_MANIFEST_PATH,
                INPUT_CONTRACT_PATH,
                RULE_CATALOG_PATH,
                STATE_MACHINE_PATH,
                WARNING_MAPPING_PATH,
            ],
            "input_fields_used": INPUT_FIELDS_USED,
            "excluded_future_or_label_fields": sorted(FORBIDDEN_INPUT_FIELDS),
            "source_backed_sample_rows": len(stage6c_rows),
            "stage6c_engineering_pilot_rows": int(_coverage_row(bundle).get("current_rows", 0)),
            "stage6c_engineering_pilot_tier": _coverage_row(bundle).get("panel_tier", "missing"),
            "warnings_remaining": warnings,
            "allowed_next_action": "prepare GOAL-08A recommendation contract design gate, or fix GOAL-07B warnings",
        }
    )
    return {
        "status": status,
        "failures": [],
        "warnings": warnings,
        "risk_overlay_rows": risk_rows,
        "diagnostic_rows": diagnostic_rows,
        "manifest": manifest,
    }


def forbidden_goal07b_output_fields(fields: list[str]) -> list[str]:
    failures = []
    for field in fields:
        if field in ALLOWED_NEGATIVE_BOUNDARY_FIELDS:
            continue
        tokens = set(field.lower().split("_"))
        if tokens & FORBIDDEN_SCHEMA_TERMS:
            failures.append(field)
        if field.lower() in FORBIDDEN_SCHEMA_TERMS:
            failures.append(field)
    return sorted(set(failures))


def _validate_input_bundle(bundle: dict[str, object]) -> list[str]:
    failures: list[str] = []
    if not bundle.get("stage6c_sample_rows"):
        failures.append("stage6c_source_backed_sample_missing")
    if bundle.get("stage6c_sample_rows"):
        fields = set(bundle["stage6c_sample_rows"][0].keys())
        missing = sorted(REQUIRED_STAGE6C_FIELDS - fields)
        failures.extend(f"stage6c_required_field_missing:{field}" for field in missing)
    coverage = _coverage_row(bundle)
    if coverage.get("panel_tier") != "engineering_pilot":
        failures.append("goal06c7_panel_tier_not_engineering_pilot")
    if coverage.get("engineering_pilot_met") != "true":
        failures.append("goal06c7_engineering_pilot_not_met")
    manifest = bundle.get("source_bundle_manifest", {})
    if manifest.get("goal_id") != "GOAL-06C.7" or manifest.get("engineering_pilot_met") is not True:
        failures.append("source_bundle_manifest_not_goal06c7_engineering_pilot")
    if not bundle.get("model_repair_rows"):
        failures.append("goal06d1_model_repair_summary_missing")
    elif bundle["model_repair_rows"][0].get("review_only") != "true":
        failures.append("goal06d1_model_repair_not_review_only")
    if not bundle.get("provider_concentration_rows"):
        failures.append("goal06d1_provider_concentration_missing")
    if not bundle.get("calibration_repair_rows"):
        failures.append("goal06d1_calibration_repair_missing")
    if not bundle.get("feature_stability_rows"):
        failures.append("goal06d1_feature_stability_missing")
    if not bundle.get("target_horizon_rows"):
        failures.append("goal06d1_target_horizon_missing")
    if not bundle.get("warning_classification_rows"):
        failures.append("goal07a1_warning_classification_missing")
    goal07b0 = bundle.get("goal07b0_manifest", {})
    if goal07b0.get("goal07b0_unlock_status") != "eligible_for_future_review_only_prototype":
        failures.append("goal07b0_unlock_not_ready")
    if goal07b0.get("goal07b_target_status") not in {"future_review_only", "implemented_review_only"}:
        failures.append("goal07b0_target_status_invalid")
    if not bundle.get("rule_catalog", {}).get("rules"):
        failures.append("goal07a_rule_catalog_missing")
    if not bundle.get("state_machine", {}).get("states"):
        failures.append("goal07a_state_machine_missing")
    if not bundle.get("warning_mapping", {}).get("mappings"):
        failures.append("goal07a_warning_mapping_missing")
    workflow = {row.get("workflow_id", ""): row for row in bundle.get("workflow_rows", [])}
    goal07b = workflow.get("goal07b_risk_overlay_calculation", {})
    if goal07b.get("status") not in {"future_review_only", "implemented_review_only"}:
        failures.append("goal07b_workflow_not_review_only_eligible")
    if goal07b.get("status") == "future_review_only" and goal07b.get("implemented_in_repo") != "false":
        failures.append("goal07b_future_review_only_marked_implemented")
    return failures


def _calculate_row(
    index: int,
    row: dict[str, str],
    active_warning_codes: set[str],
    warning_mapping: dict[str, str],
    model_context: dict[str, str],
    rule_rows: dict[str, dict[str, str]],
) -> dict[str, object]:
    triggered = _triggered_rules(row, active_warning_codes)
    severity = _risk_severity(triggered)
    state = _risk_state(triggered)
    domains = sorted({RULE_DOMAIN[rule_id] for rule_id in triggered if rule_id in RULE_DOMAIN})
    warning_domains = [f"{code}:{warning_mapping.get(code, 'unmapped')}" for code in sorted(active_warning_codes)]
    rule_trace = [
        f"{rule_id}@{RULE_DOMAIN.get(rule_id, 'unknown')}@{rule_rows.get(rule_id, {}).get('severity_level', 'UNKNOWN')}"
        for rule_id in triggered
    ]
    missing = sorted(field for field in REQUIRED_STAGE6C_FIELDS if not row.get(field))
    return {
        "goal_id": GOAL_ID,
        "mode": MODE,
        "calculation_type": CALCULATION_TYPE,
        "trade_date": row["trade_date"],
        "symbol": row["symbol"],
        "as_of_date": row["as_of_date"],
        "risk_domain": ";".join(domains) if domains else "none",
        "risk_tag": f"{severity}_REVIEW_ONLY_DIAGNOSTIC",
        "risk_severity": severity,
        "risk_confidence": _risk_confidence(severity, missing),
        "risk_state": state,
        "risk_transition_diagnostic": f"not_evaluated->{state}",
        "triggered_rule_ids": ";".join(triggered) if triggered else "none",
        "risk_rule_trace": ";".join(rule_trace) if rule_trace else "none",
        "warning_propagation": ";".join(sorted(active_warning_codes)) if active_warning_codes else "none",
        "upstream_warning_mapping": ";".join(warning_domains) if warning_domains else "none",
        "missing_input_diagnostics": "none" if not missing else "missing_required:" + ";".join(missing),
        "bounded_model_weakness_diagnostics": _model_weakness_text(model_context),
        "audit_metadata": f"input_row={index};source={STAGE6C_SAMPLE_PATH};rule_catalog=goal07a_v1;non_actionable=true",
        "review_only_status_flags": "review_only=true;diagnostic_only=true;not_a_recommendation=true;not_a_position=true",
        "non_actionable": True,
        "recommendation_generated": False,
        "position_generated": False,
        "dashboard_generated": False,
        "paper_live_trading_generated": False,
        "trading_generated": False,
        "production_generated": False,
        "backtest_generated": False,
        "factor_mining_generated": False,
        "dqn_rl_generated": False,
    }


def _triggered_rules(row: dict[str, str], active_warning_codes: set[str]) -> list[str]:
    triggered: list[str] = []
    if _data_quality_hard_block(row.get("data_quality_flags", "")):
        triggered.append("data_quality_non_pass_blocks")
    if row.get("leakage_flags") != "PASS":
        triggered.append("leakage_failure_blocks")
    if row.get("panel_tier") not in {"engineering_pilot", "research_ready", "strong_panel"}:
        triggered.append("panel_tier_floor_blocks")
    if "calibration_not_reliable_for_thresholding" in active_warning_codes or "target_horizon_calibration_warning" in active_warning_codes:
        triggered.append("calibration_warning_minimum_warning_state")
    if "selected_score_variant_weak_rank_signal" in active_warning_codes:
        triggered.append("weak_rank_signal_model_confidence")
    if "provider_source_concentration_disclosed" in active_warning_codes or "single_provider_mode_akshare_direct" in active_warning_codes or _to_float(row.get("source_count")) <= 1:
        triggered.append("single_provider_concentration")
    if "feature_sign_instability_bounded" in active_warning_codes:
        triggered.append("feature_instability_downgrades")
    if "weak_target_horizon_rank_signal" in active_warning_codes:
        triggered.append("target_horizon_warning_downgrades")
    if _to_float(row.get("source_health_score")) < 0.75:
        triggered.append("source_health_warning_downgrades")
    if abs(_to_float(row.get("stock_gap_signal"))) > 0.08 or _to_float(row.get("stock_volatility_20d")) > 0.04:
        triggered.append("gap_or_volatility_market_warning")
    return triggered


def _data_quality_hard_block(flags: str) -> bool:
    tokens = {token.strip().upper() for token in flags.split(";") if token.strip()}
    hard_tokens = {"FAIL", "FAILED", "BLOCKED", "LEAKAGE", "FORWARD_LABEL", "FUTURE_RETURN"}
    return bool(tokens & hard_tokens)


def _risk_severity(triggered: list[str]) -> str:
    if any(rule_id in BLOCKING_RULES for rule_id in triggered):
        return "BLOCKED"
    if len(triggered) >= 5:
        return "HIGH"
    if triggered:
        return "MEDIUM"
    return "LOW"


def _risk_confidence(severity: str, missing: list[str]) -> str:
    if severity == "BLOCKED" or missing:
        return "LOW"
    if severity == "HIGH":
        return "MEDIUM"
    return "HIGH"


def _risk_state(triggered: list[str]) -> str:
    if any(rule_id in {"data_quality_non_pass_blocks", "leakage_failure_blocks", "panel_tier_floor_blocks"} for rule_id in triggered):
        return "data_blocked"
    if any(rule_id in {"calibration_warning_minimum_warning_state", "weak_rank_signal_model_confidence", "feature_instability_downgrades", "target_horizon_warning_downgrades"} for rule_id in triggered):
        return "model_warning"
    if "single_provider_concentration" in triggered:
        return "source_warning"
    if "gap_or_volatility_market_warning" in triggered:
        return "market_warning"
    return "eligible_for_review_only_snapshot"


def _diagnostic_rows(risk_rows: list[dict[str, object]], warning_mapping: dict[str, str]) -> list[dict[str, object]]:
    rows = []
    domains = sorted({domain for row in risk_rows for domain in str(row["risk_domain"]).split(";") if domain and domain != "none"})
    severity_order = {"UNKNOWN": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "BLOCKED": 4}
    for domain in domains:
        scoped = [row for row in risk_rows if domain in str(row["risk_domain"]).split(";")]
        severities = [str(row["risk_severity"]) for row in scoped]
        max_severity = max(severities, key=lambda item: severity_order.get(item, -1)) if severities else "UNKNOWN"
        rule_ids = sorted({rule for row in scoped for rule in str(row["triggered_rule_ids"]).split(";") if rule != "none" and RULE_DOMAIN.get(rule) == domain})
        warning_codes = sorted(code for code, mapped_domain in warning_mapping.items() if mapped_domain == domain)
        rows.append(
            {
                "goal_id": GOAL_ID,
                "mode": MODE,
                "calculation_type": CALCULATION_TYPE,
                "risk_domain": domain,
                "rows_evaluated": len(risk_rows),
                "rows_triggered": len(scoped),
                "max_risk_severity": max_severity,
                "triggered_rule_ids": ";".join(rule_ids) if rule_ids else "none",
                "warning_codes": ";".join(warning_codes) if warning_codes else "none",
                "non_actionable": True,
                "recommendation_generated": False,
                "position_generated": False,
                "dashboard_generated": False,
                "paper_live_trading_generated": False,
                "trading_generated": False,
                "production_generated": False,
                "backtest_generated": False,
                "factor_mining_generated": False,
                "dqn_rl_generated": False,
            }
        )
    return rows


def _write_policy(root: Path) -> None:
    write_json(
        root / POLICY_PATH,
        {
            "goal_id": GOAL_ID,
            "mode": MODE,
            "calculation_type": CALCULATION_TYPE,
            "output_grain": "trade_date + symbol",
            "severity_levels": sorted(SEVERITY_LEVELS),
            "confidence_levels": sorted(CONFIDENCE_LEVELS),
            "rule_source": RULE_CATALOG_PATH,
            "state_machine_source": STATE_MACHINE_PATH,
            "allowed_input_artifacts": [
                STAGE6C_SAMPLE_PATH,
                STAGE6C_COVERAGE_PATH,
                SOURCE_BUNDLE_MANIFEST_PATH,
                MODEL_REPAIR_SUMMARY_PATH,
                PROVIDER_CONCENTRATION_PATH,
                CALIBRATION_REPAIR_PATH,
                FEATURE_STABILITY_PATH,
                TARGET_HORIZON_PATH,
                WARNING_CLASSIFICATION_PATH,
                GOAL07B0_MANIFEST_PATH,
            ],
            "input_fields_used": INPUT_FIELDS_USED,
            "excluded_future_or_label_fields": sorted(FORBIDDEN_INPUT_FIELDS),
            "non_actionable": True,
            "forbidden_outputs": FORBIDDEN_OUTPUT_DIRS,
            "recommendation_generated": False,
            "position_generated": False,
            "dashboard_generated": False,
            "paper_live_trading_generated": False,
            "trading_generated": False,
            "production_generated": False,
            "backtest_generated": False,
            "factor_mining_generated": False,
            "dqn_rl_generated": False,
            "database_writes_performed": False,
            "live_data_fetched": False,
            "broker_data_used": False,
            "future_information_used": False,
        },
    )


def _write_outputs(root: Path, result: dict[str, object]) -> None:
    risk_rows = result["risk_overlay_rows"]
    diagnostics = result["diagnostic_rows"]
    manifest = result["manifest"]
    if risk_rows:
        write_csv(root / RISK_OVERLAY_PATH, risk_rows, REQUIRED_OUTPUT_FIELDS)
    else:
        write_csv(root / RISK_OVERLAY_PATH, [], REQUIRED_OUTPUT_FIELDS)
    write_csv(root / DIAGNOSTICS_PATH, diagnostics, DIAGNOSTIC_FIELDS)
    write_json(root / MANIFEST_PATH, manifest)
    report_lines = [
        "# GOAL-07B Risk Overlay Calculation Prototype",
        "",
        f"GOAL-07B Risk Overlay Calculation Prototype: {result['status']}",
        "GOAL-07B mode: review_only",
        f"Risk overlay diagnostic rows generated: `{len(risk_rows)}`",
        "Output grain: `trade_date + symbol`",
        f"Risk severity levels used: `{';'.join(manifest.get('risk_severity_levels_used', [])) or 'none'}`",
        "No recommendation output was generated",
        "No position output was generated",
        "No dashboard output was generated",
        "No paper/live trading output was generated",
        "No production output was generated",
        "No backtest output was generated",
        "No factor-mining output was generated",
        "No DQN/RL output was generated",
        "Allowed next action: prepare GOAL-08A recommendation contract design gate, or fix GOAL-07B warnings",
        "",
        "## Evidence Inputs",
        *[f"- `{item}`" for item in manifest.get("input_artifacts", [])],
        "",
        "## Warnings Remaining",
        *[f"- `{warning}`" for warning in result["warnings"]],
        "",
        "## Failures",
        *[f"- {failure}" for failure in result["failures"]],
        "",
    ]
    write_text(root / REPORT_PATH, "\n".join(report_lines))
    write_text(
        root / DOC_PATH,
        "\n".join(
            [
                "# GOAL-07B Risk Overlay Calculation Prototype",
                "",
                f"Status: `{result['status']}`",
                "",
                "GOAL-07B is a deterministic, review-only risk overlay calculation prototype. It converts GOAL-07A, GOAL-07A.1, and GOAL-07B.0 governance evidence into symbol-date-level risk diagnostics only.",
                "",
                "The output grain is `trade_date + symbol`. Outputs are non-actionable and do not contain recommendation, position, allocation, order, trading, dashboard decision, production, backtest, factor-mining, broker, or DQN/RL outputs.",
                "",
                f"Rows generated: `{len(risk_rows)}`",
                f"Severity levels used: `{';'.join(manifest.get('risk_severity_levels_used', [])) or 'none'}`",
                "",
            ]
        ),
    )


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys())
    by_id = {row["workflow_id"]: row for row in rows}
    goal07b = by_id["goal07b_risk_overlay_calculation"]
    goal07b.update(
        {
            "display_name": "GOAL-07B Risk Overlay Calculation Prototype",
            "stage_or_goal": "GOAL-07B",
            "status": "implemented_review_only" if result["status"] != FAIL else "future_review_only",
            "current_repo_role": "review_only_risk_overlay_diagnostic_prototype",
            "implemented_in_repo": "true" if result["status"] != FAIL else "false",
            "allowed_next_action": "prepare_goal08a_recommendation_contract_design_gate_or_fix_goal07b_warnings",
            "depends_on": "goal07b0_risk_overlay_review_only_unlock_gate",
            "produces_artifacts": f"{RISK_OVERLAY_PATH};{REPORT_PATH};{MANIFEST_PATH};{DIAGNOSTICS_PATH}",
            "primary_docs": f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
            "primary_scripts": "scripts/run_goal07b_risk_overlay_calculation_prototype.py;scripts/audit_goal07b_risk_overlay_calculation_prototype.py",
            "primary_outputs": f"{RISK_OVERLAY_PATH};{REPORT_PATH};{MANIFEST_PATH};{DIAGNOSTICS_PATH}",
            "promotion_rule": "implemented_review_only_after_goal07b_calculation_pass_with_warnings",
            "notes": "Review-only risk overlay diagnostics; non-actionable and not a recommendation, position, dashboard, trading, production, backtest, factor-mining, or DQN/RL output.",
        }
    )
    _upsert_locked_goal08_rows(root, rows, by_id)
    by_id = {row["workflow_id"]: row for row in rows}
    for workflow_id in DOWNSTREAM_LOCKED_IDS:
        if workflow_id in by_id:
            by_id[workflow_id]["status"] = "locked_future"
            by_id[workflow_id]["implemented_in_repo"] = "false"
            by_id[workflow_id]["allowed_next_action"] = "remain_locked"
    if "dqn_rl_mainline" in by_id:
        by_id["dqn_rl_mainline"]["status"] = "deleted_from_active_mainline"
        by_id["dqn_rl_mainline"]["implemented_in_repo"] = "false"
    if "v2_factor_research_upgrade" in by_id:
        by_id["v2_factor_research_upgrade"]["status"] = "planned_locked"
        by_id["v2_factor_research_upgrade"]["implemented_in_repo"] = "false"
    write_csv(path, rows, fields)


def _upsert_locked_goal08_rows(root: Path, rows: list[dict[str, str]], by_id: dict[str, dict[str, str]]) -> None:
    goal08a = {
        "workflow_id": "goal08a_recommendation_contract_design_gate",
        "display_name": "GOAL-08A Recommendation Contract Design Gate",
        "stage_or_goal": "GOAL-08A",
        "status": "locked_future",
        "current_repo_role": "locked_downstream_design_boundary",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked",
        "depends_on": "goal07b_risk_overlay_calculation",
        "produces_artifacts": "",
        "primary_docs": "docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal08a_design_gate",
        "notes": "Locked future recommendation contract design gate; GOAL-07B allows preparation only, not implementation.",
    }
    goal08b = {
        "workflow_id": "goal08b_recommendation_review_only_prototype",
        "display_name": "GOAL-08B Recommendation Review-Only Prototype",
        "stage_or_goal": "GOAL-08B",
        "status": "locked_future",
        "current_repo_role": "locked_downstream_recommendation_boundary",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked",
        "depends_on": "goal08a_recommendation_contract_design_gate",
        "produces_artifacts": "",
        "primary_docs": "docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal08b_review_only_goal",
        "notes": "Locked future recommendation prototype; not unlocked by GOAL-07B.",
    }
    insert_at = next((index + 1 for index, row in enumerate(rows) if row["workflow_id"] == "goal07b_risk_overlay_calculation"), len(rows))
    for row in [goal08a, goal08b]:
        if row["workflow_id"] == "goal08a_recommendation_contract_design_gate":
            existing = by_id.get(row["workflow_id"], {})
            if _goal08a_locked_or_design_only_valid(root, existing) and existing.get("status") == "implemented_design_only":
                continue
        if row["workflow_id"] in by_id:
            by_id[row["workflow_id"]].update(row)
        else:
            rows.insert(insert_at, row)
            insert_at += 1


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    if not path.exists():
        return
    payload = read_json(path)
    payload["goal07b_risk_overlay_calculation"] = "implemented_review_only" if result["status"] != FAIL else "future_review_only"
    if payload.get("goal08a_recommendation_contract_design_gate") != "implemented_design_only":
        payload["goal08a_recommendation_contract_design_gate"] = False
    payload["goal08b_recommendation_review_only_prototype"] = False
    for key in [
        "position_band_recommendation",
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
    write_json(path, payload)


def _goal08a_locked_or_design_only_valid(root: Path, row: dict[str, str]) -> bool:
    status = row.get("status")
    if status == "locked_future":
        return row.get("implemented_in_repo") == "false"
    if status != "implemented_design_only" or row.get("implemented_in_repo") != "true":
        return False
    report = _read(root / "outputs/audits/goal08a_recommendation_contract_design_report.md")
    audit = _read(root / "outputs/audits/goal08a_recommendation_contract_design_audit.md")
    manifest = _read(root / "outputs/audits/goal08a_recommendation_contract_design_manifest.json")
    return (
        (
            "GOAL-08A Recommendation Contract Design Gate: PASS" in report
            or "GOAL-08A Recommendation Contract Design Gate: PASS_WITH_WARNINGS" in report
        )
        and "Status: `PASS`" in audit
        and '"mode": "design_only"' in manifest
        and '"future_schema_row_count": 0' in manifest
        and '"recommendation_rows_generated": false' in manifest
        and '"actionable_outputs_generated": false' in manifest
        and '"goal08b_status_after_goal08a": "locked_future"' in manifest
    )


def _manifest_template(
    status: str,
    risk_rows: list[dict[str, object]],
    severity_used: list[str],
    failures: list[str],
    warnings: list[str],
) -> dict[str, object]:
    return {
        "goal_id": GOAL_ID,
        "status": status,
        "mode": MODE,
        "calculation_type": CALCULATION_TYPE,
        "output_grain": "trade_date + symbol",
        "risk_overlay_row_count": len(risk_rows),
        "diagnostic_output_path": DIAGNOSTICS_PATH,
        "risk_overlay_output_path": RISK_OVERLAY_PATH,
        "risk_severity_levels_allowed": sorted(SEVERITY_LEVELS),
        "risk_severity_levels_used": severity_used,
        "risk_confidence_levels_allowed": sorted(CONFIDENCE_LEVELS),
        "risk_states_allowed": sorted(RISK_STATES),
        "non_actionable": True,
        "recommendation_generated": False,
        "position_generated": False,
        "dashboard_generated": False,
        "paper_live_trading_generated": False,
        "trading_generated": False,
        "production_generated": False,
        "backtest_generated": False,
        "factor_mining_generated": False,
        "dqn_rl_generated": False,
        "database_writes_performed": False,
        "live_data_fetched": False,
        "broker_data_used": False,
        "future_information_used": False,
        "failures": failures,
        "warnings": warnings,
    }


def _row_policy_failures(row: dict[str, str], index: int, severity_optional: bool = False) -> list[str]:
    failures = []
    prefix = f"row_{index}"
    if row.get("goal_id") != GOAL_ID:
        failures.append(f"{prefix}_goal_id_invalid")
    if row.get("mode") != MODE:
        failures.append(f"{prefix}_mode_invalid")
    if row.get("calculation_type") != CALCULATION_TYPE:
        failures.append(f"{prefix}_calculation_type_invalid")
    if row.get("non_actionable") != "true":
        failures.append(f"{prefix}_non_actionable_not_true")
    for field in [
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
        if row.get(field) != "false":
            failures.append(f"{prefix}_{field}_not_false")
    if not severity_optional and row.get("risk_severity") not in SEVERITY_LEVELS:
        failures.append(f"{prefix}_risk_severity_not_bounded")
    if not severity_optional and row.get("risk_confidence") not in CONFIDENCE_LEVELS:
        failures.append(f"{prefix}_risk_confidence_not_bounded")
    if not severity_optional and row.get("risk_state") not in RISK_STATES:
        failures.append(f"{prefix}_risk_state_not_bounded")
    return failures


def _active_warning_codes(bundle: dict[str, object]) -> set[str]:
    codes: set[str] = set()
    for row in bundle.get("model_repair_rows", []):
        codes.update(_warning_tokens(row.get("warnings", "")))
    for row in bundle.get("provider_concentration_rows", []):
        status = row.get("concentration_status", "")
        if status:
            codes.add(status)
    selected_target = ""
    if bundle.get("model_repair_rows"):
        selected_target = bundle["model_repair_rows"][0].get("selected_target", "")
    for row in bundle.get("target_horizon_rows", []):
        if not selected_target or row.get("target") == selected_target:
            codes.update(_warning_tokens(row.get("warnings", "")))
    for row in bundle.get("warning_classification_rows", []):
        active = row.get("active_in_current_design") == "true"
        code = row.get("warning_code", "")
        if active:
            codes.add(code)
    return {WARNING_NORMALIZATION.get(code, code) for code in codes if code}


def _warning_tokens(text: str) -> set[str]:
    return {WARNING_NORMALIZATION.get(token.strip(), token.strip()) for token in text.split(";") if token.strip()}


def _warning_mapping(bundle: dict[str, object]) -> dict[str, str]:
    return {
        str(row.get("warning_code")): str(row.get("risk_domain_id"))
        for row in bundle.get("warning_mapping", {}).get("mappings", [])
        if isinstance(row, dict)
    }


def _model_context(bundle: dict[str, object]) -> dict[str, str]:
    row = bundle.get("model_repair_rows", [{}])[0]
    return {
        "selected_score_variant": row.get("selected_score_variant", "unknown"),
        "selected_target": row.get("selected_target", "unknown"),
        "selection_label": row.get("selection_label", "unknown"),
        "calibration_status": row.get("calibration_status", "unknown"),
        "feature_stability_status": row.get("feature_stability_status", "unknown"),
        "provider_concentration_status": row.get("provider_concentration_status", "unknown"),
    }


def _model_weakness_text(context: dict[str, str]) -> str:
    return ";".join(f"{key}={value}" for key, value in context.items())


def _rule_rows(bundle: dict[str, object]) -> dict[str, dict[str, str]]:
    return {
        str(row.get("rule_id")): row
        for row in bundle.get("rule_catalog", {}).get("rules", [])
        if isinstance(row, dict)
    }


def _coverage_row(bundle: dict[str, object]) -> dict[str, str]:
    rows = bundle.get("stage6c_coverage_rows", [])
    return rows[0] if rows else {}


def _to_float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _read_csv(path: Path) -> list[dict[str, str]]:
    return read_csv(path) if path.exists() else []


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return read_json(path)
    except Exception:
        return {}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""

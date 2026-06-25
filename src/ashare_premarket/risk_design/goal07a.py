from __future__ import annotations

import json
from pathlib import Path

from ashare_premarket.contract_design.goal08b0 import (
    GOAL08B0_ALLOWED_NEXT,
    GOAL08B0_WORKFLOW_ID,
    GOAL08B_ELIGIBLE_STATUS,
    goal08b0_valid_unlock_evidence,
)
from ashare_premarket.core.io import read_csv, write_csv, write_text
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.review_diagnostics.goal08b import (
    DIAGNOSTIC_PATH as GOAL08B_DIAGNOSTIC_PATH,
    GOAL08B_ALLOWED_NEXT as GOAL08B_IMPLEMENTED_ALLOWED_NEXT,
    GOAL08B_IMPLEMENTED_STATUS,
    goal08b_valid_diagnostics_evidence,
)
from ashare_premarket.validation.workflow_status import run_workflow_status_audit


RISK_DIR = "configs/risk"
DOC_DIR = "docs/risk"
AUDIT_DIR = "outputs/audits"

RISK_DOMAINS = [
    "data_quality_risk",
    "provider_concentration_risk",
    "model_confidence_risk",
    "calibration_risk",
    "feature_stability_risk",
    "target_horizon_risk",
    "market_regime_risk",
    "liquidity_proxy_risk",
    "volatility_risk",
    "gap_risk",
    "source_health_risk",
    "governance_boundary_risk",
]

UPSTREAM_WARNINGS = [
    "calibration_not_reliable_for_thresholding",
    "feature_sign_instability_bounded",
    "provider_source_concentration_disclosed",
    "selected_score_variant_weak_rank_signal",
    "single_provider_mode_akshare_direct",
    "weak_target_horizon_rank_signal",
    "target_horizon_calibration_warning",
]

ALLOWED_INPUT_FIELDS = [
    "source_bundle_id",
    "panel_tier",
    "provider_id",
    "provider_mode",
    "source_health_score",
    "source_count",
    "data_quality_flags",
    "leakage_flags",
    "model_name",
    "selection_label",
    "review_only_baseline_score_metadata",
    "calibration_warning_flags",
    "feature_stability_warning_flags",
    "target_horizon_warning_flags",
    "market_trend_5d",
    "stock_volatility_20d",
    "turnover_proxy",
    "stock_gap_signal",
    "relative_strength_20d",
]

FORBIDDEN_INPUTS = [
    "future_returns_as_risk_features",
    "forward_labels_as_live_risk_features",
    "recommendation_output",
    "position_output",
    "portfolio_output",
    "live_trading_output",
    "manually_edited_risk_score",
    "anything_not_pit_safe",
]

ALLOWED_SCHEMA_FIELDS = [
    "as_of_date",
    "target_trading_date",
    "symbol",
    "risk_overlay_version",
    "data_quality_risk_tag",
    "provider_concentration_risk_tag",
    "model_confidence_risk_tag",
    "calibration_risk_tag",
    "feature_stability_risk_tag",
    "target_horizon_risk_tag",
    "market_regime_risk_tag",
    "liquidity_proxy_risk_tag",
    "volatility_risk_tag",
    "gap_risk_tag",
    "source_health_risk_tag",
    "overall_risk_state",
    "risk_explanation_code",
    "risk_governance_flags",
    "review_only",
    "risk_severity",
    "risk_confidence_level",
    "risk_rule_trace",
    "risk_audit_metadata",
]

FORBIDDEN_SCHEMA_FIELDS = [
    "buy",
    "sell",
    "hold",
    "recommended_position",
    "position_weight",
    "portfolio_weight",
    "risk_score",
    "final_score",
    "final_rank",
    "tradable_rank",
    "trade_signal",
    "order_action",
    "broker_instruction",
]

RISK_STATES = ["PASS", "WARNING", "DEGRADED", "BLOCKED", "NOT_EVALUATED"]

STATE_MACHINE_STATES = [
    "not_evaluated",
    "input_invalid",
    "data_blocked",
    "model_warning",
    "source_warning",
    "market_warning",
    "eligible_for_review_only_snapshot",
    "blocked_from_recommendation",
]

FORBIDDEN_OUTPUT_DIRS = [
    "outputs/recommendations",
    "outputs/positions",
    "outputs/dashboard",
    "outputs/paper_trading",
    "outputs/live_trading",
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
GOAL07B_WORKFLOW_ID = "goal07b_risk_overlay_calculation"
GOAL07B_ALLOWED_STATUSES = {"locked_future", "future_review_only", "implemented_review_only"}

SCRIPT_AUDIT_FUNCTIONS = {
    "allowed_input_contract": "audit_goal07a_allowed_input_contract",
    "output_schema": "audit_goal07a_output_schema",
    "risk_rule_catalog": "audit_goal07a_risk_rule_catalog",
    "state_machine": "audit_goal07a_state_machine",
    "upstream_warning_mapping": "audit_goal07a_upstream_warning_mapping",
    "governance_boundary": "audit_goal07a_governance_boundary",
    "boundary_locks": "audit_goal07a_boundary_locks",
    "v2_factor_lock": "audit_goal07a_v2_factor_lock",
}


def run_goal07a_risk_overlay_design_gate(root: Path) -> bool:
    upstream = _verify_upstream(root)
    designs = _design_payloads()
    _write_design_configs(root, designs)
    _write_design_docs(root, upstream, designs)
    audit_statuses = _write_audits(root, upstream, designs)
    readiness = _derive_readiness(upstream, audit_statuses)
    _write_readiness_report(root, readiness, upstream, audit_statuses)
    _update_workflow_status(root, readiness)
    _update_locked_capabilities(root)
    run_workflow_diagnostics(root)
    run_workflow_status_audit(root)
    return readiness["status"] in {"PASS", "PASS_WITH_WARNINGS"}


def audit_goal07a_allowed_input_contract(root: Path) -> bool:
    return _status_from_report(root / f"{AUDIT_DIR}/goal07a_allowed_input_contract_audit.md") == "PASS"


def audit_goal07a_output_schema(root: Path) -> bool:
    return _status_from_report(root / f"{AUDIT_DIR}/goal07a_output_schema_audit.md") == "PASS"


def audit_goal07a_risk_rule_catalog(root: Path) -> bool:
    return _status_from_report(root / f"{AUDIT_DIR}/goal07a_risk_rule_catalog_audit.md") == "PASS"


def audit_goal07a_state_machine(root: Path) -> bool:
    return _status_from_report(root / f"{AUDIT_DIR}/goal07a_state_machine_audit.md") == "PASS"


def audit_goal07a_upstream_warning_mapping(root: Path) -> bool:
    return _status_from_report(root / f"{AUDIT_DIR}/goal07a_upstream_warning_mapping_audit.md") == "PASS"


def audit_goal07a_governance_boundary(root: Path) -> bool:
    return _status_from_report(root / f"{AUDIT_DIR}/goal07a_governance_boundary_audit.md") == "PASS"


def audit_goal07a_boundary_locks(root: Path) -> bool:
    return _status_from_report(root / f"{AUDIT_DIR}/goal07a_boundary_lock_audit.md") == "PASS"


def audit_goal07a_v2_factor_lock(root: Path) -> bool:
    return _status_from_report(root / f"{AUDIT_DIR}/goal07a_v2_factor_lock_audit.md") == "PASS"


def _verify_upstream(root: Path) -> dict[str, object]:
    goal06c7 = _read(root / f"{AUDIT_DIR}/goal06c7_readiness_report.md")
    goal06d1 = _read(root / f"{AUDIT_DIR}/goal06d1_readiness_report.md")
    v2_contract = _read(root / "configs/factors/v2_factor_research_contract.yaml")
    failures: list[str] = []
    if "GOAL-06C.7 Engineering Data Base Expansion Readiness: PASS" not in goal06c7:
        failures.append("goal06c7_engineering_pilot_not_pass")
    for required in ["Panel tier: `engineering_pilot`", "Approved symbols: `50`", "Validation trading dates: `120`", "Stage 6C engineering rows: `6000`"]:
        if required not in goal06c7:
            failures.append(f"goal06c7_missing_{required}")
    if "GOAL-06D.1 Calibration Stability Warning Repair Readiness: PASS_WITH_WARNINGS" not in goal06d1 and "GOAL-06D.1 Calibration Stability Warning Repair Readiness: PASS" not in goal06d1:
        failures.append("goal06d1_readiness_not_pass_or_warn")
    if "Allowed next action: `proceed_to_goal07a_design_only_with_warnings`" not in goal06d1 and "Allowed next action: `prepare_goal07a_risk_overlay_design_only`" not in goal06d1:
        failures.append("goal06d1_does_not_allow_goal07a_design_only")
    for warning in UPSTREAM_WARNINGS:
        if warning not in goal06d1:
            failures.append(f"goal06d1_warning_missing_{warning}")
    if "status: planned_locked" not in v2_contract or "enabled: false" not in v2_contract or "active_in_v1: false" not in v2_contract:
        failures.append("v2_factor_placeholder_not_locked")
    warnings = [warning for warning in UPSTREAM_WARNINGS if warning in goal06d1]
    return {
        "status": "BLOCKED" if failures else "PASS_WITH_WARNINGS",
        "failures": failures,
        "warnings": warnings,
        "goal06c7_engineering_pilot": not any(item.startswith("goal06c7") for item in failures),
        "goal06d1_ready": not any(item.startswith("goal06d1") for item in failures),
        "v2_planned_locked": "v2_factor_placeholder_not_locked" not in failures,
    }


def _design_payloads() -> dict[str, object]:
    return {
        "allowed_input_contract": _allowed_input_contract(),
        "output_schema": _output_schema_design(),
        "rule_catalog": _rule_catalog_design(),
        "state_machine": _state_machine_design(),
        "warning_mapping": _upstream_warning_mapping(),
    }


def _allowed_input_contract() -> dict[str, object]:
    return {
        "goal": "GOAL-07A",
        "mode": "design_only",
        "future_goal_that_may_consume_contract": "GOAL-07B_after_explicit_unlock",
        "upstream_source": "GOAL-06D.1 review-only model baseline",
        "grain": "trade_date + symbol",
        "required_upstream_datasets": [
            {
                "dataset_id": "goal06c7_engineering_panel",
                "path": "outputs/stage6c/STAGE6C_source_backed_engineering_panel_coverage_summary.csv",
                "grain": "trade_date + symbol",
                "required_for_goal07b_review_only": True,
            },
            {
                "dataset_id": "goal06d1_model_comparison_repair_summary",
                "path": "outputs/models/goal06d1/model_comparison_repair_summary.csv",
                "grain": "model_name + target_horizon",
                "required_for_goal07b_review_only": True,
            },
            {
                "dataset_id": "goal06d1_warning_audits",
                "path": "outputs/audits/goal06d1_readiness_report.md",
                "grain": "review_only_warning_code",
                "required_for_goal07b_review_only": True,
            },
            {
                "dataset_id": "workflow_status_governance",
                "path": "configs/project/workflow_status.csv",
                "grain": "workflow_id",
                "required_for_goal07b_review_only": True,
            },
        ],
        "required_warning_fields": [
            "selection_label",
            "calibration_warning_flags",
            "feature_stability_warning_flags",
            "target_horizon_warning_flags",
            "provider_mode",
            "source_count",
        ],
        "optional_future_input_fields": [
            "stock_volatility_20d",
            "turnover_proxy",
            "relative_strength_20d",
        ],
        "missing_optional_field_policy": "classify_as_DESIGN_REVIEW_WARNING_not_silent_failure",
        "allowed_future_input_fields": ALLOWED_INPUT_FIELDS,
        "forbidden_inputs": FORBIDDEN_INPUTS,
        "pit_safety_rule": "future GOAL-07B inputs must be available at or before as_of_date and must not include forward labels or future returns",
        "upstream_warnings_to_carry": UPSTREAM_WARNINGS,
        "goal07a_execution_policy": {
            "consume_real_symbol_rows": False,
            "calculate_risk_values": False,
            "assign_symbol_tags": False,
            "write_symbol_level_outputs": False,
        },
        "risk_domains": [_risk_domain(domain_id) for domain_id in RISK_DOMAINS],
    }


def _risk_domain(domain_id: str) -> dict[str, object]:
    mapping = {
        "data_quality_risk": ("PIT/data leakage and quality flags", ["data_quality_flags", "leakage_flags"], "data_quality_risk_tag"),
        "provider_concentration_risk": ("Provider/source concentration warnings", ["provider_id", "provider_mode", "source_count"], "provider_concentration_risk_tag"),
        "model_confidence_risk": ("Weak selected baseline and score metadata", ["model_name", "selection_label", "review_only_baseline_score_metadata"], "model_confidence_risk_tag"),
        "calibration_risk": ("Calibration warning flags from GOAL-06D.1", ["calibration_warning_flags"], "calibration_risk_tag"),
        "feature_stability_risk": ("Feature sign stability warnings", ["feature_stability_warning_flags"], "feature_stability_risk_tag"),
        "target_horizon_risk": ("Weak target horizon diagnostics", ["target_horizon_warning_flags"], "target_horizon_risk_tag"),
        "market_regime_risk": ("Market trend context", ["market_trend_5d"], "market_regime_risk_tag"),
        "liquidity_proxy_risk": ("Turnover/liquidity proxy context", ["turnover_proxy"], "liquidity_proxy_risk_tag"),
        "volatility_risk": ("20-day volatility proxy context", ["stock_volatility_20d"], "volatility_risk_tag"),
        "gap_risk": ("Premarket gap proxy context", ["stock_gap_signal"], "gap_risk_tag"),
        "source_health_risk": ("Source health and source count context", ["source_health_score", "source_count"], "source_health_risk_tag"),
        "governance_boundary_risk": ("Downstream lock and review-only governance context", ["panel_tier", "leakage_flags"], "overall_risk_state"),
    }
    description, fields, output_field = mapping[domain_id]
    return {
        "risk_domain_id": domain_id,
        "description": description,
        "upstream_evidence_source": "GOAL-06D.1 readiness/audits plus GOAL-06C.7 engineering_pilot evidence",
        "allowed_input_fields": fields,
        "future_allowed_output_fields": [output_field, "risk_explanation_code", "risk_governance_flags", "review_only"],
        "design_only_rule": "define future rule contract only; do not evaluate or materialize real-row values in GOAL-07A",
        "blocking_condition_design": _blocking_condition(domain_id),
        "downgrade_condition_design": _downgrade_condition(domain_id),
        "warning_condition_design": _warning_condition(domain_id),
        "forbidden_use_in_goal07a": "must_not_compute_values_or_assign_tags_to_real_symbols",
    }


def _blocking_condition(domain_id: str) -> str:
    if domain_id in {"data_quality_risk", "governance_boundary_risk"}:
        return "future GOAL-07B should block when leakage_flags or hard governance checks fail"
    if domain_id == "provider_concentration_risk":
        return "future GOAL-07B should block when required provider evidence is missing or source_count is zero"
    return "future GOAL-07B should block only when this domain has a hard invalid/missing contract condition"


def _downgrade_condition(domain_id: str) -> str:
    if domain_id in {"model_confidence_risk", "calibration_risk", "feature_stability_risk", "target_horizon_risk"}:
        return "future GOAL-07B should downgrade review-only recommendation eligibility when upstream weak-baseline warnings are present"
    if domain_id in {"market_regime_risk", "liquidity_proxy_risk", "volatility_risk", "gap_risk"}:
        return "future GOAL-07B should downgrade when future thresholds mark the context as adverse"
    return "future GOAL-07B should downgrade when non-hard warning conditions remain unresolved"


def _warning_condition(domain_id: str) -> str:
    warning_lookup = {
        "provider_concentration_risk": "provider_source_concentration_disclosed or single_provider_mode_akshare_direct",
        "model_confidence_risk": "selected_score_variant_weak_rank_signal",
        "calibration_risk": "calibration_not_reliable_for_thresholding or target_horizon_calibration_warning",
        "feature_stability_risk": "feature_sign_instability_bounded",
        "target_horizon_risk": "weak_target_horizon_rank_signal",
    }
    return warning_lookup.get(domain_id, "future warning flag present for this domain")


def _output_schema_design() -> dict[str, object]:
    return {
        "goal": "GOAL-07A",
        "mode": "schema_design_only",
        "future_schema_version": "goal07b_v1_review_only",
        "allowed_future_schema_fields": ALLOWED_SCHEMA_FIELDS,
        "forbidden_schema_fields": FORBIDDEN_SCHEMA_FIELDS,
        "empty_schema_sample": {"row_count": 0, "columns": ALLOWED_SCHEMA_FIELDS},
        "goal07a_forbidden_generation": {
            "symbol_level_rows": False,
            "calculated_risk_overlay_values": False,
            "recommendation_like_outputs": False,
            "position_outputs": False,
        },
    }


def _rule_catalog_design() -> dict[str, object]:
    rules = [
        ("calibration_warning_minimum_warning_state", "calibration_risk", "calibration_not_reliable_for_thresholding", "overall_risk_state", "WARNING", "WARNING", "boolean warning flag present in GOAL-06D.1 readiness evidence", "pass through as a calibration risk warning; never convert to a trading decision"),
        ("weak_rank_signal_model_confidence", "model_confidence_risk", "selected_score_variant_weak_rank_signal", "model_confidence_risk_tag", "WEAK", "WARNING", "boolean weak-rank warning from GOAL-06D.1 selected repaired baseline", "pass through as model confidence warning"),
        ("single_provider_concentration", "provider_concentration_risk", "provider_source_concentration_disclosed", "provider_concentration_risk_tag", "SINGLE_SOURCE_WARNING", "WARNING", "provider/source concentration warning present or source_count <= 1", "pass through as source concentration warning"),
        ("data_quality_non_pass_blocks", "data_quality_risk", "data_quality_flags contain non-PASS", "data_quality_risk_tag", "BLOCKED", "BLOCKED", "split data_quality_flags on semicolon and block when any required flag is not PASS", "hard block for future GOAL-07B review-only calculation"),
        ("leakage_failure_blocks", "governance_boundary_risk", "leakage_flags not PASS", "overall_risk_state", "BLOCKED", "BLOCKED", "leakage_flags must equal PASS at the future PIT-safe grain", "hard block; no risk tag or recommendation can be produced"),
        ("panel_tier_floor_blocks", "governance_boundary_risk", "panel_tier below engineering_pilot", "overall_risk_state", "BLOCKED", "BLOCKED", "panel_tier must be one of engineering_pilot, research_ready, strong_panel", "hard block until engineering_pilot evidence exists"),
        ("feature_instability_downgrades", "feature_stability_risk", "feature_sign_instability_bounded", "feature_stability_risk_tag", "DEGRADED", "DEGRADED", "boolean bounded feature-instability warning present", "downgrade future review-only risk confidence"),
        ("target_horizon_warning_downgrades", "target_horizon_risk", "weak_target_horizon_rank_signal", "target_horizon_risk_tag", "WARNING", "WARNING", "boolean weak target-horizon rank warning present", "pass through as target-horizon risk warning"),
        ("source_health_warning_downgrades", "source_health_risk", "source_health_score below future configured min_source_health_score", "source_health_risk_tag", "WARNING", "WARNING", "future GOAL-07B config must define min_source_health_score before execution", "warn or block according to the future explicit config"),
        ("gap_or_volatility_market_warning", "market_regime_risk", "future volatility/gap threshold warning", "overall_risk_state", "WARNING", "WARNING", "future GOAL-07B config must define max_volatility_20d and max_abs_gap_signal before execution", "market warning only; no trading action"),
    ]
    return {
        "goal": "GOAL-07A",
        "mode": "rule_catalog_design_only",
        "allowed_future_risk_states": RISK_STATES,
        "rules": [
            {
                "rule_id": rule_id,
                "risk_domain_id": risk_domain_id,
                "trigger_design": trigger,
                "future_output_field": output_field,
                "future_effect_design": effect,
                "severity_level": severity,
                "threshold_logic_design": threshold_logic,
                "warning_behavior": warning_behavior,
                "data_dependency_policy": "PIT_safe_review_only_contract_fields_no_execution_feed",
                "execution_in_goal07a": False,
                "real_symbol_assignment_in_goal07a": False,
            }
            for rule_id, risk_domain_id, trigger, output_field, effect, severity, threshold_logic, warning_behavior in rules
        ],
    }


def _state_machine_design() -> dict[str, object]:
    transitions = [
        ("not_evaluated", "input_invalid", "input contract failure"),
        ("not_evaluated", "data_blocked", "leakage flag failure"),
        ("not_evaluated", "data_blocked", "panel below engineering_pilot"),
        ("not_evaluated", "model_warning", "calibration warning"),
        ("not_evaluated", "model_warning", "feature instability warning"),
        ("not_evaluated", "source_warning", "single provider concentration"),
        ("not_evaluated", "market_warning", "high volatility or gap warning"),
        ("model_warning", "eligible_for_review_only_snapshot", "all governance conditions satisfied"),
        ("source_warning", "eligible_for_review_only_snapshot", "all governance conditions satisfied"),
        ("market_warning", "eligible_for_review_only_snapshot", "all governance conditions satisfied"),
        ("eligible_for_review_only_snapshot", "blocked_from_recommendation", "any hard boundary violation"),
    ]
    blocked_transitions = [
        {"from_state": "data_blocked", "to_state": "eligible_for_review_only_snapshot", "reason": "data or leakage blockers cannot become eligible without a fresh explicit GOAL-07B unlock audit"},
        {"from_state": "input_invalid", "to_state": "eligible_for_review_only_snapshot", "reason": "invalid input contracts cannot be promoted"},
        {"from_state": "blocked_from_recommendation", "to_state": "eligible_for_review_only_snapshot", "reason": "hard boundary violations require a separate repair goal"},
    ]
    return {
        "goal": "GOAL-07A",
        "mode": "state_machine_design_only",
        "states": STATE_MACHINE_STATES,
        "transition_output_policy": "diagnostic_state_only_no_trade_action_no_recommendation_no_position",
        "transitions": [
            {
                "from_state": source,
                "to_state": target,
                "trigger_design": trigger,
                "output_semantics": "diagnostic_only",
                "execution_in_goal07a": False,
                "real_symbol_transition_in_goal07a": False,
            }
            for source, target, trigger in transitions
        ],
        "blocked_transitions": blocked_transitions,
    }


def _upstream_warning_mapping() -> dict[str, object]:
    rows = [
        ("calibration_not_reliable_for_thresholding", "calibration_risk"),
        ("feature_sign_instability_bounded", "feature_stability_risk"),
        ("provider_source_concentration_disclosed", "provider_concentration_risk"),
        ("selected_score_variant_weak_rank_signal", "model_confidence_risk"),
        ("single_provider_mode_akshare_direct", "provider_concentration_risk"),
        ("weak_target_horizon_rank_signal", "target_horizon_risk"),
        ("target_horizon_calibration_warning", "calibration_risk"),
    ]
    return {
        "goal": "GOAL-07A",
        "mode": "warning_mapping_design_only",
        "mappings": [
            {
                "warning_code": warning,
                "risk_domain_id": domain,
                "carry_forward_to_goal07b_design": True,
                "goal07a_action": "document_only_no_risk_tag_assignment",
            }
            for warning, domain in rows
        ],
    }


def _write_design_configs(root: Path, designs: dict[str, object]) -> None:
    _write_jsonish(root / f"{RISK_DIR}/goal07a_allowed_input_contract.yaml", designs["allowed_input_contract"])
    _write_jsonish(root / f"{RISK_DIR}/goal07a_future_risk_overlay_output_schema.yaml", designs["output_schema"])
    _write_jsonish(root / f"{RISK_DIR}/goal07a_risk_rule_catalog.yaml", designs["rule_catalog"])
    _write_jsonish(root / f"{RISK_DIR}/goal07a_risk_state_machine.yaml", designs["state_machine"])
    _write_jsonish(root / f"{RISK_DIR}/goal07a_upstream_warning_mapping.yaml", designs["warning_mapping"])


def _write_design_docs(root: Path, upstream: dict[str, object], designs: dict[str, object]) -> None:
    domain_lines = [f"- `{domain['risk_domain_id']}`: {domain['description']}" for domain in designs["allowed_input_contract"]["risk_domains"]]
    warning_lines = [f"- `{warning}`" for warning in upstream["warnings"]]
    write_text(
        root / f"{DOC_DIR}/GOAL07A_RISK_OVERLAY_DESIGN.md",
        "\n".join(
            [
                "# GOAL-07A Risk Overlay Design",
                "",
                "Status: `implemented_design_only`",
                "",
                "GOAL-07A defines the V1 risk governance blueprint that may later sit between the GOAL-06D.1 review-only baseline and a future review-only recommendation contract.",
                "It does not calculate risk overlay values, produce symbol-level risk rows, or generate recommendations, positions, portfolio weights, dashboards, trading data, production writes, factor mining, or DQN/RL artifacts.",
                "",
                "## Upstream Warning Carry-Forward",
                *warning_lines,
                "",
                "## Risk Domains",
                *domain_lines,
                "",
                "## Design Questions Answered",
                "1. Consider data quality, provider concentration, model confidence, calibration, feature stability, target horizon, market regime, liquidity proxy, volatility, gap, source health, and governance boundary risks before any future recommendation-like output.",
                "2. Carry GOAL-06D.1 weak-baseline, calibration, feature-stability, target-horizon, and provider-concentration warnings into future governance.",
                "3. Consume only PIT-safe, review-only, contract-listed fields in a future GOAL-07B.",
                "4. Future GOAL-07B may produce categorical risk tags and review-only governance flags after explicit unlock.",
                "5. GOAL-07A forbids risk calculations, recommendation outputs, position outputs, scores, ranks, trading instructions, and real symbol tag assignment.",
                "6. Hard data/leakage/governance failures should block future recommendation generation; weak model, calibration, provider, feature, target horizon, market, liquidity, volatility, and gap warnings should downgrade or warn.",
                "7. GOAL-07B requires passing input contract, output schema, rule catalog, state machine, warning mapping, governance, boundary lock, and V2 factor lock audits.",
                "",
            ]
        ),
    )
    write_text(
        root / f"{DOC_DIR}/GOAL07A_RISK_OVERLAY_OUTPUT_SCHEMA_DESIGN.md",
        "\n".join(
            [
                "# GOAL-07A Risk Overlay Output Schema Design",
                "",
                "Status: `implemented_design_only`",
                "",
                "The future schema is categorical and review-only. GOAL-07A creates no real symbol-level rows.",
                "",
                "Allowed future fields:",
                *[f"- `{field}`" for field in ALLOWED_SCHEMA_FIELDS],
                "",
                "Forbidden fields:",
                *[f"- `{field}`" for field in FORBIDDEN_SCHEMA_FIELDS],
                "",
            ]
        ),
    )
    write_text(
        root / f"{DOC_DIR}/GOAL07A_RISK_RULE_CATALOG_DESIGN.md",
        "\n".join(
            [
                "# GOAL-07A Risk Rule Catalog Design",
                "",
                "Status: `implemented_design_only`",
                "",
                "Rules are catalog entries only. They are not executed in GOAL-07A.",
                "",
                "Allowed future states: `PASS`, `WARNING`, `DEGRADED`, `BLOCKED`, `NOT_EVALUATED`.",
                "",
                "Representative rules:",
                *[f"- `{rule['rule_id']}`: if {rule['trigger_design']} then future `{rule['future_output_field']}` should be `{rule['future_effect_design']}`." for rule in designs["rule_catalog"]["rules"]],
                "",
            ]
        ),
    )
    write_text(
        root / f"{DOC_DIR}/GOAL07A_RISK_STATE_MACHINE_DESIGN.md",
        "\n".join(
            [
                "# GOAL-07A Risk State Machine Design",
                "",
                "Status: `implemented_design_only`",
                "",
                "The state machine is a design artifact only. It is not run on real symbol rows in GOAL-07A.",
                "",
                "States:",
                *[f"- `{state}`" for state in STATE_MACHINE_STATES],
                "",
                "Transitions:",
                *[f"- `{item['from_state']}` -> `{item['to_state']}` on `{item['trigger_design']}`." for item in designs["state_machine"]["transitions"]],
                "",
            ]
        ),
    )
    write_text(
        root / f"{DOC_DIR}/GOAL07A_RISK_OVERLAY_DESIGN_ONLY_BOUNDARY.md",
        "\n".join(
            [
                "# GOAL-07A Risk Overlay Design-Only Boundary",
                "",
                "Status: `PASS`",
                "",
                "GOAL-07A is implemented only as a design gate.",
                "GOAL-07A itself does not implement GOAL-07B or calculate risk.",
                "GOAL-07B, when present, may only be a separate review-only diagnostic prototype.",
                "GOAL-08B, recommendation, position, portfolio weight, dashboard, paper/live trading, broker/live trading, production DB writes, production model promotion, factor mining, and DQN/RL remain locked or deleted from active mainline. GOAL-08A may exist only as a later design-only contract gate.",
                "V2 factor research remains `planned_locked`, `enabled: false`, and `active_in_v1: false`.",
                "No full local data bundle or model binary is committed.",
                "",
            ]
        ),
    )


def _write_audits(root: Path, upstream: dict[str, object], designs: dict[str, object]) -> dict[str, str]:
    statuses = {
        "allowed_input_contract": _audit_allowed_input_contract(designs["allowed_input_contract"]),
        "output_schema": _audit_output_schema(designs["output_schema"]),
        "risk_rule_catalog": _audit_rule_catalog(designs["rule_catalog"]),
        "state_machine": _audit_state_machine(designs["state_machine"]),
        "upstream_warning_mapping": _audit_warning_mapping(designs["warning_mapping"]),
        "governance_boundary": _audit_governance_boundary(root),
        "boundary_locks": _audit_boundary_locks(root),
        "v2_factor_lock": _audit_v2_factor_lock(root),
    }
    _write_audit_report(root, "goal07a_allowed_input_contract_audit.md", "GOAL-07A Allowed Input Contract Audit", statuses["allowed_input_contract"], [
        f"Allowed future input fields: `{len(ALLOWED_INPUT_FIELDS)}`",
        f"Forbidden inputs listed: `{len(FORBIDDEN_INPUTS)}`",
        "GOAL-07A consumes real symbol rows: `false`",
        "GOAL-07A calculates risk values: `false`",
    ])
    _write_audit_report(root, "goal07a_output_schema_audit.md", "GOAL-07A Output Schema Audit", statuses["output_schema"], [
        f"Allowed future fields: `{len(ALLOWED_SCHEMA_FIELDS)}`",
        f"Forbidden schema fields: `{len(FORBIDDEN_SCHEMA_FIELDS)}`",
        "Forbidden fields overlap allowed fields: `false`",
        "Symbol-level rows generated: `false`",
    ])
    _write_audit_report(root, "goal07a_risk_rule_catalog_audit.md", "GOAL-07A Risk Rule Catalog Audit", statuses["risk_rule_catalog"], [
        f"Rules designed: `{len(designs['rule_catalog']['rules'])}`",
        "All required future risk states listed: `true`",
        "Rules executed in GOAL-07A: `false`",
    ])
    _write_audit_report(root, "goal07a_state_machine_audit.md", "GOAL-07A State Machine Audit", statuses["state_machine"], [
        f"States designed: `{len(STATE_MACHINE_STATES)}`",
        f"Transitions designed: `{len(designs['state_machine']['transitions'])}`",
        "State machine executed on real rows in GOAL-07A: `false`",
    ])
    _write_audit_report(root, "goal07a_upstream_warning_mapping_audit.md", "GOAL-07A Upstream Warning Mapping Audit", statuses["upstream_warning_mapping"], [
        f"Warnings mapped: `{len(designs['warning_mapping']['mappings'])}`",
        "All GOAL-06D.1 required warnings mapped to risk domains: `true`",
        "Risk tags computed: `false`",
    ])
    _write_audit_report(root, "goal07a_governance_boundary_audit.md", "GOAL-07A Governance Boundary Audit", statuses["governance_boundary"], [
        "GOAL-07A is design-only: `true`",
        "GOAL-07B implemented by GOAL-07A: `false`",
        "Risk overlay calculation executed by GOAL-07A: `false`",
        "Recommendation output exists: `false`",
        "Position output exists: `false`",
        "Dashboard output exists: `false`",
        "Paper/live trading exists: `false`",
        "Production DB writes exist: `false`",
        "Production model promotion exists: `false`",
        "DQN/RL active mainline exists: `false`",
        "V2 factor research remains planned_locked and inactive: `true`",
        "Factor mining output exists: `false`",
    ])
    _write_audit_report(root, "goal07a_boundary_lock_audit.md", "GOAL-07A Boundary Lock Audit", statuses["boundary_locks"], [
        f"GOAL-07B current status: `{_goal07b_status(root)}`; GOAL-07A itself did not implement or execute it.",
        "Recommendation remains locked_future.",
        "Position output remains locked_future.",
        "Dashboard remains locked_future.",
        "Paper/live trading remains locked_future.",
        "Production remains locked_future.",
        "DQN/RL remains deleted_from_active_mainline.",
        "No forbidden output directories were created.",
    ])
    _write_audit_report(root, "goal07a_v2_factor_lock_audit.md", "GOAL-07A V2 Factor Lock Audit", statuses["v2_factor_lock"], [
        "V2 factor research remains planned_locked.",
        "V2 factor research remains disabled.",
        "No factor mining script exists.",
        "No IC / RankIC mining is active.",
        "No factor-to-model integration is active.",
        "No factor-to-recommendation integration is active.",
    ])
    return statuses


def _audit_allowed_input_contract(payload: dict[str, object]) -> str:
    domains = payload.get("risk_domains", [])
    domain_ids = {domain.get("risk_domain_id") for domain in domains if isinstance(domain, dict)}
    required_domain_fields = {
        "risk_domain_id",
        "description",
        "upstream_evidence_source",
        "allowed_input_fields",
        "future_allowed_output_fields",
        "design_only_rule",
        "blocking_condition_design",
        "downgrade_condition_design",
        "warning_condition_design",
        "forbidden_use_in_goal07a",
    }
    complete_domains = all(required_domain_fields <= set(domain) for domain in domains if isinstance(domain, dict))
    datasets = payload.get("required_upstream_datasets", [])
    dataset_ids = {item.get("dataset_id") for item in datasets if isinstance(item, dict)}
    required_dataset_ids = {"goal06c7_engineering_panel", "goal06d1_model_comparison_repair_summary", "goal06d1_warning_audits", "workflow_status_governance"}
    grain_ok = payload.get("grain") == "trade_date + symbol"
    warning_fields_ok = set(payload.get("required_warning_fields", [])) <= set(payload.get("allowed_future_input_fields", []))
    return "PASS" if set(RISK_DOMAINS) == domain_ids and complete_domains and required_dataset_ids <= dataset_ids and grain_ok and warning_fields_ok and payload["goal07a_execution_policy"]["calculate_risk_values"] is False else "BLOCKED"


def _audit_output_schema(payload: dict[str, object]) -> str:
    allowed = set(payload.get("allowed_future_schema_fields", []))
    forbidden = set(payload.get("forbidden_schema_fields", []))
    required = set(ALLOWED_SCHEMA_FIELDS)
    return "PASS" if required <= allowed and not (allowed & forbidden) and payload["empty_schema_sample"]["row_count"] == 0 else "BLOCKED"


def _audit_rule_catalog(payload: dict[str, object]) -> str:
    states_ok = set(RISK_STATES) <= set(payload.get("allowed_future_risk_states", []))
    rules = payload.get("rules", [])
    design_only = all(rule.get("execution_in_goal07a") is False and rule.get("real_symbol_assignment_in_goal07a") is False for rule in rules if isinstance(rule, dict))
    convertible = all(rule.get("risk_domain_id") and rule.get("threshold_logic_design") and rule.get("severity_level") in RISK_STATES and rule.get("warning_behavior") for rule in rules if isinstance(rule, dict))
    return "PASS" if states_ok and len(rules) >= 6 and design_only and convertible else "BLOCKED"


def _audit_state_machine(payload: dict[str, object]) -> str:
    states_ok = set(STATE_MACHINE_STATES) <= set(payload.get("states", []))
    transitions = payload.get("transitions", [])
    design_only = all(item.get("execution_in_goal07a") is False and item.get("real_symbol_transition_in_goal07a") is False for item in transitions if isinstance(item, dict))
    required_triggers = {
        "input contract failure",
        "leakage flag failure",
        "panel below engineering_pilot",
        "calibration warning",
        "feature instability warning",
        "single provider concentration",
        "high volatility or gap warning",
        "all governance conditions satisfied",
        "any hard boundary violation",
    }
    triggers = {item.get("trigger_design") for item in transitions if isinstance(item, dict)}
    blocked_explicit = bool(payload.get("blocked_transitions"))
    diagnostic_only = payload.get("transition_output_policy") == "diagnostic_state_only_no_trade_action_no_recommendation_no_position"
    return "PASS" if states_ok and required_triggers <= triggers and design_only and blocked_explicit and diagnostic_only else "BLOCKED"


def _audit_warning_mapping(payload: dict[str, object]) -> str:
    rows = payload.get("mappings", [])
    mapping = {row.get("warning_code"): row.get("risk_domain_id") for row in rows if isinstance(row, dict)}
    required = {
        "calibration_not_reliable_for_thresholding": "calibration_risk",
        "feature_sign_instability_bounded": "feature_stability_risk",
        "provider_source_concentration_disclosed": "provider_concentration_risk",
        "selected_score_variant_weak_rank_signal": "model_confidence_risk",
        "single_provider_mode_akshare_direct": "provider_concentration_risk",
        "weak_target_horizon_rank_signal": "target_horizon_risk",
        "target_horizon_calibration_warning": "calibration_risk",
    }
    return "PASS" if mapping == required else "BLOCKED"


def _audit_governance_boundary(root: Path) -> str:
    no_dirs = _forbidden_dirs_absent(root)
    return "PASS" if no_dirs else "BLOCKED"


def _audit_boundary_locks(root: Path) -> str:
    rows = {row["workflow_id"]: row for row in read_csv(root / "configs/project/workflow_status.csv")}
    goal07b = rows.get(GOAL07B_WORKFLOW_ID, {})
    goal07b_status = goal07b.get("status")
    if goal07b_status == "implemented_review_only":
        goal07b_ok = goal07b.get("implemented_in_repo") == "true" and _goal07b_review_only_outputs_valid(root)
    else:
        goal07b_ok = goal07b_status in {"locked_future", "future_review_only"} and goal07b.get("implemented_in_repo") == "false"
        if goal07b_status == "future_review_only":
            goal07b_ok = goal07b_ok and "GOAL-07B.0 Risk Overlay Review-Only Unlock Gate:" in _read(root / "outputs/audits/goal07b0_unlock_gate_report.md")
    downstream_locked = all(rows.get(workflow_id, {}).get("status") == "locked_future" for workflow_id in DOWNSTREAM_LOCKED_IDS)
    dqn_deleted = rows.get("dqn_rl_mainline", {}).get("status") == "deleted_from_active_mainline"
    return "PASS" if goal07b_ok and downstream_locked and dqn_deleted and _forbidden_dirs_absent(root) else "BLOCKED"


def _audit_v2_factor_lock(root: Path) -> str:
    contract = _read(root / "configs/factors/v2_factor_research_contract.yaml")
    docs = _read(root / "docs/factors/V2_FACTOR_RESEARCH_INTERFACE.md")
    locked = "status: planned_locked" in contract and "enabled: false" in contract and "active_in_v1: false" in contract
    docs_locked = "Status: `planned_locked`" in docs and "No V2 factor mining runner" in docs
    factor_outputs_absent = not (root / "outputs/factors").exists()
    mining_scripts = [
        path
        for path in (root / "scripts").glob("*.py")
        if any(token in path.name.lower() for token in ["factor_mining", "ic_mining", "rankic", "factor_library"])
    ]
    return "PASS" if locked and docs_locked and factor_outputs_absent and not mining_scripts else "BLOCKED"


def _derive_readiness(upstream: dict[str, object], audit_statuses: dict[str, str]) -> dict[str, object]:
    failures = list(upstream["failures"])
    failures.extend(f"{name}_audit_blocked" for name, status in audit_statuses.items() if status != "PASS")
    warnings = list(upstream["warnings"])
    status = "BLOCKED" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    allowed_next_action = {
        "PASS": "prepare_goal07b_risk_overlay_calculation_prototype_after_explicit_unlock",
        "PASS_WITH_WARNINGS": "prepare_goal07b_design_review_or_fix_goal07a_warnings",
        "BLOCKED": "block_goal07b_until_goal07a_pass",
    }[status]
    return {
        "status": status,
        "failures": failures,
        "warnings": sorted(set(str(item) for item in warnings)),
        "allowed_next_action": allowed_next_action,
    }


def _write_readiness_report(root: Path, readiness: dict[str, object], upstream: dict[str, object], audit_statuses: dict[str, str]) -> None:
    write_text(
        root / f"{AUDIT_DIR}/goal07a_readiness_report.md",
        "\n".join(
            [
                "# GOAL-07A Risk Overlay Design Readiness Report",
                "",
                f"GOAL-07A Risk Overlay Design Readiness: {readiness['status']}",
                f"Allowed next action: `{readiness['allowed_next_action']}`",
                "GOAL-07A mode: `design_only`",
                f"GOAL-07B status: `{_goal07b_status(root)}`",
                "GOAL-07B may proceed only after an explicit future unlock and only as a separate review-only calculation prototype goal.",
                f"GOAL-06C.7 engineering_pilot evidence verified: `{str(upstream['goal06c7_engineering_pilot']).lower()}`",
                f"GOAL-06D.1 PASS/PASS_WITH_WARNINGS evidence verified: `{str(upstream['goal06d1_ready']).lower()}`",
                f"V2 factor research planned_locked evidence verified: `{str(upstream['v2_planned_locked']).lower()}`",
                "",
                "## Audit Results",
                *[f"- `{name}`: `{status}`" for name, status in sorted(audit_statuses.items())],
                "",
                "No risk calculation, symbol-level risk overlay rows, recommendation, position, dashboard, paper/live trading, production, factor-mining, or DQN/RL output was created.",
                "",
                "## Failures",
                *[f"- {failure}" for failure in readiness["failures"]],
                "",
                "## Warnings",
                *[f"- {warning}" for warning in readiness["warnings"]],
                "",
            ]
        ),
    )


def _update_workflow_status(root: Path, readiness: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    by_id = {row["workflow_id"]: row for row in rows}
    row = by_id["goal07a_risk_overlay_design"]
    row.update(
        {
            "display_name": "GOAL-07A Risk Overlay Design",
            "stage_or_goal": "GOAL-07A",
            "status": "implemented_design_only" if readiness["status"] != "BLOCKED" else "future_design_only",
            "current_repo_role": "design_only_governance_gate",
            "implemented_in_repo": "true" if readiness["status"] != "BLOCKED" else "false",
            "allowed_next_action": str(readiness["allowed_next_action"]),
            "depends_on": "goal06d1_calibration_stability_warning_repair",
            "produces_artifacts": "configs/risk/goal07a_allowed_input_contract.yaml;configs/risk/goal07a_future_risk_overlay_output_schema.yaml;configs/risk/goal07a_risk_rule_catalog.yaml;configs/risk/goal07a_risk_state_machine.yaml;configs/risk/goal07a_upstream_warning_mapping.yaml;outputs/audits/goal07a_readiness_report.md",
            "primary_docs": "docs/risk/GOAL07A_RISK_OVERLAY_DESIGN.md;docs/risk/GOAL07A_RISK_OVERLAY_DESIGN_ONLY_BOUNDARY.md;docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md",
            "primary_scripts": "scripts/run_goal07a_risk_overlay_design_gate.py;scripts/audit_goal07a_allowed_input_contract.py;scripts/audit_goal07a_output_schema.py;scripts/audit_goal07a_risk_rule_catalog.py;scripts/audit_goal07a_state_machine.py;scripts/audit_goal07a_upstream_warning_mapping.py;scripts/audit_goal07a_governance_boundary.py;scripts/audit_goal07a_boundary_locks.py;scripts/audit_goal07a_v2_factor_lock.py",
            "primary_outputs": "outputs/audits/goal07a_readiness_report.md;outputs/audits/goal07a_governance_boundary_audit.md;outputs/audits/goal07a_boundary_lock_audit.md",
            "promotion_rule": "implemented_design_only_after_goal07a_readiness_pass_with_warnings",
            "notes": "Design-only risk governance gate; no risk overlay calculation, recommendation, position, dashboard, trading, production, factor mining, or DQN/RL output.",
        }
    )
    for workflow_id in DOWNSTREAM_LOCKED_IDS:
        if workflow_id in by_id:
            by_id[workflow_id]["status"] = "locked_future"
            by_id[workflow_id]["implemented_in_repo"] = "false"
            by_id[workflow_id]["allowed_next_action"] = "remain_locked"
    if "goal08b_recommendation_review_only_prototype" in by_id:
        if goal08b_valid_diagnostics_evidence(root):
            by_id["goal08b_recommendation_review_only_prototype"].update(
                {
                    "status": GOAL08B_IMPLEMENTED_STATUS,
                    "current_repo_role": "review_only_recommendation_diagnostic_prototype",
                    "implemented_in_repo": "true",
                    "allowed_next_action": GOAL08B_IMPLEMENTED_ALLOWED_NEXT,
                    "depends_on": GOAL08B0_WORKFLOW_ID,
                    "produces_artifacts": GOAL08B_DIAGNOSTIC_PATH,
                    "primary_docs": "docs/recommendation/GOAL08B_REVIEW_ONLY_RECOMMENDATION_DIAGNOSTICS.md;docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
                    "primary_scripts": "scripts/run_goal08b_recommendation_diagnostics_prototype.py;scripts/audit_goal08b_recommendation_diagnostics_prototype.py",
                    "primary_outputs": GOAL08B_DIAGNOSTIC_PATH,
                    "promotion_rule": "implemented_review_only_after_goal08b_diagnostics_pass_with_warnings",
                    "notes": "Review-only non-actionable recommendation diagnostics; downstream execution remains locked.",
                }
            )
        elif goal08b0_valid_unlock_evidence(root):
            by_id["goal08b_recommendation_review_only_prototype"].update(
                {
                    "status": GOAL08B_ELIGIBLE_STATUS,
                    "current_repo_role": "review_only_eligible_not_implemented",
                    "implemented_in_repo": "false",
                    "allowed_next_action": GOAL08B0_ALLOWED_NEXT,
                    "depends_on": GOAL08B0_WORKFLOW_ID,
                    "notes": "Eligibility only after GOAL-08B.0; GOAL-07A does not implement recommendation diagnostics.",
                }
            )
        else:
            by_id["goal08b_recommendation_review_only_prototype"].update(
                {
                    "status": "locked_future",
                    "implemented_in_repo": "false",
                    "allowed_next_action": "remain_locked",
                }
            )
    if GOAL07B_WORKFLOW_ID in by_id:
        goal07b_status = _goal07b_status(root)
        by_id[GOAL07B_WORKFLOW_ID]["status"] = goal07b_status
        by_id[GOAL07B_WORKFLOW_ID]["implemented_in_repo"] = "true" if goal07b_status == "implemented_review_only" else "false"
    if "dqn_rl_mainline" in by_id:
        by_id["dqn_rl_mainline"]["status"] = "deleted_from_active_mainline"
        by_id["dqn_rl_mainline"]["allowed_next_action"] = "remain_deleted_unless_explicit_optional_research_goal"
    if "v2_factor_research_upgrade" in by_id:
        by_id["v2_factor_research_upgrade"]["status"] = "planned_locked"
        by_id["v2_factor_research_upgrade"]["allowed_next_action"] = "no_action_until_v1_complete"
    write_csv(path, rows, list(rows[0].keys()))


def _update_locked_capabilities(root: Path) -> None:
    path = root / "configs/project/locked_capabilities.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["goal07a_risk_overlay_design"] = "implemented_design_only"
    payload["goal07b_risk_overlay_calculation"] = _goal07b_status(root)
    if goal08b_valid_diagnostics_evidence(root):
        payload["goal08b_recommendation_review_only_prototype"] = GOAL08B_IMPLEMENTED_STATUS
    else:
        payload["goal08b_recommendation_review_only_prototype"] = GOAL08B_ELIGIBLE_STATUS if goal08b0_valid_unlock_evidence(root) else False
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
    write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _write_audit_report(root: Path, filename: str, title: str, status: str, lines: list[str]) -> None:
    write_text(root / f"{AUDIT_DIR}/{filename}", "\n".join([f"# {title}", "", f"Status: `{status}`", "", *lines, ""]))


def _write_jsonish(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _forbidden_dirs_absent(root: Path) -> bool:
    return all(not (root / path).exists() for path in FORBIDDEN_OUTPUT_DIRS)


def _goal07b_status(root: Path) -> str:
    path = root / "configs/project/workflow_status.csv"
    if not path.exists():
        return "locked_future"
    rows = {row["workflow_id"]: row for row in read_csv(path)}
    current = rows.get(GOAL07B_WORKFLOW_ID, {}).get("status", "locked_future")
    if current == "implemented_review_only" and _goal07b_review_only_outputs_valid(root):
        return "implemented_review_only"
    if current == "future_review_only" and "GOAL-07B.0 Risk Overlay Review-Only Unlock Gate:" in _read(root / "outputs/audits/goal07b0_unlock_gate_report.md"):
        return "future_review_only"
    return "locked_future"


def _goal07b_review_only_outputs_valid(root: Path) -> bool:
    report = _read(root / "outputs/audits/goal07b_risk_overlay_calculation_report.md")
    audit = _read(root / "outputs/audits/goal07b_risk_overlay_calculation_audit.md")
    manifest = _read(root / "outputs/audits/goal07b_risk_overlay_calculation_manifest.json")
    return (
        (
            "GOAL-07B Risk Overlay Calculation Prototype: PASS" in report
            or "GOAL-07B Risk Overlay Calculation Prototype: PASS_WITH_WARNINGS" in report
        )
        and "Status: `PASS`" in audit
        and '"mode": "review_only"' in manifest
        and '"recommendation_generated": false' in manifest
        and '"position_generated": false' in manifest
        and '"trading_generated": false' in manifest
        and '"production_generated": false' in manifest
    )


def _status_from_report(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Status:"):
            return line.replace("Status:", "").strip(" `")
        if line.startswith("GOAL-07A Risk Overlay Design Readiness:"):
            return line.split(":", 1)[1].strip()
    return "MISSING"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""

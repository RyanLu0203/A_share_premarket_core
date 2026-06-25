from __future__ import annotations

import json
from pathlib import Path

from ashare_premarket.contract_design.goal090 import GOAL09_WORKFLOW_ID, goal09_eligible_workflow_patch, goal090_valid_unlock_evidence
from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import preserve_later_review_only_workflow_states
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.risk_design.goal07a import (
    DOWNSTREAM_LOCKED_IDS,
    FORBIDDEN_OUTPUT_DIRS,
    GOAL07B_ALLOWED_STATUSES,
    GOAL07B_WORKFLOW_ID,
    RISK_DOMAINS,
    RISK_STATES,
    STATE_MACHINE_STATES,
    UPSTREAM_WARNINGS,
)
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

AUDIT_DIR = "outputs/audits"
RISK_DIR = "configs/risk"
DOC_DIR = "docs/risk"

REVIEW_STATUS_PASS = "PASS"
REVIEW_STATUS_WARN = "PASS_WITH_WARNINGS"
REVIEW_STATUS_FAIL = "FAIL"

GOAL07B_READY = "ready_for_explicit_review_only_unlock"
GOAL07B_NOT_READY = "not_ready_fix_goal07a_warnings"
GOAL07B_BLOCKED = "blocked_due_to_boundary_violation"

ALLOWED_NEXT_ACTION_READY = "request_explicit_goal07b_review_only_unlock"
ALLOWED_NEXT_ACTION_NOT_READY = "repair_goal07a_design_review_warnings_before_goal07b"
ALLOWED_NEXT_ACTION_BLOCKED = "block_goal07b_due_to_boundary_violation"

REQUIRED_DATASET_IDS = {
    "goal06c7_engineering_panel",
    "goal06d1_model_comparison_repair_summary",
    "goal06d1_warning_audits",
    "workflow_status_governance",
}

REQUIRED_WARNING_FIELDS = {
    "selection_label",
    "calibration_warning_flags",
    "feature_stability_warning_flags",
    "target_horizon_warning_flags",
    "provider_mode",
    "source_count",
}

REVIEW_ONLY_OUTPUT_HINTS = {
    "risk_tag",
    "risk_state",
    "risk_severity",
    "risk_confidence",
    "risk_rule_trace",
    "risk_audit_metadata",
    "risk_governance_flags",
    "risk_explanation_code",
    "review_only",
    "as_of_date",
    "target_trading_date",
    "symbol",
    "risk_overlay_version",
}

FORBIDDEN_SCHEMA_TERMS = {
    "buy",
    "sell",
    "hold",
    "recommend",
    "recommended",
    "target_position",
    "position_size",
    "position_weight",
    "portfolio_weight",
    "order_action",
    "broker",
    "execution_instruction",
    "dashboard_decision",
    "production_signal",
    "trade_signal",
    "tradable_rank",
    "final_rank",
    "final_score",
    "risk_score",
}

WARNING_POLICY = {
    "calibration_not_reliable_for_thresholding": "PASS_THROUGH_WARNING",
    "feature_sign_instability_bounded": "PASS_THROUGH_WARNING",
    "provider_source_concentration_disclosed": "PASS_THROUGH_WARNING",
    "selected_score_variant_weak_rank_signal": "PASS_THROUGH_WARNING",
    "single_provider_mode_akshare_direct": "DESIGN_REVIEW_WARNING",
    "weak_target_horizon_rank_signal": "PASS_THROUGH_WARNING",
    "target_horizon_calibration_warning": "PASS_THROUGH_WARNING",
    "missing_required_input_contract_fields": "BLOCKER_FOR_07B",
    "leakage_flags_not_pass": "BLOCKER_FOR_07B",
    "output_schema_forbidden_overlap": "BLOCKER_FOR_07B",
    "state_machine_ambiguity": "BLOCKER_FOR_07B",
    "goal06c7_engineering_pilot_pass": "NOT_APPLICABLE",
}


def run_goal07a1_risk_overlay_design_review_gate(root: Path) -> bool:
    bundle = load_goal07a1_design_bundle(root)
    review = evaluate_goal07a1_design_review(bundle)
    _write_policy(root)
    _write_review_outputs(root, review)
    _update_workflow_status(root, review)
    run_workflow_diagnostics(root)
    run_workflow_status_audit(root)
    return review["status"] in {REVIEW_STATUS_PASS, REVIEW_STATUS_WARN}


def audit_goal07a1_input_contract_readiness(root: Path) -> bool:
    return _status_from_report(root / f"{AUDIT_DIR}/goal07a1_input_contract_readiness_audit.md") == "PASS"


def audit_goal07a1_output_schema_safety(root: Path) -> bool:
    return _status_from_report(root / f"{AUDIT_DIR}/goal07a1_forbidden_schema_overlap_audit.md") == "PASS"


def audit_goal07a1_rule_convertibility(root: Path) -> bool:
    return _status_from_report(root / f"{AUDIT_DIR}/goal07a1_rule_convertibility_audit.md") == "PASS"


def audit_goal07a1_state_machine_review(root: Path) -> bool:
    return _status_from_report(root / f"{AUDIT_DIR}/goal07a1_state_machine_review_audit.md") == "PASS"


def audit_goal07a1_warning_policy(root: Path) -> bool:
    path = root / f"{AUDIT_DIR}/goal07a1_warning_classification.csv"
    if not path.exists():
        return False
    rows = read_csv(path)
    mapping = {row["warning_code"]: row["classification"] for row in rows}
    return all(mapping.get(code) == classification for code, classification in WARNING_POLICY.items())


def audit_goal07a1_boundary_locks(root: Path) -> bool:
    return _status_from_report(root / f"{AUDIT_DIR}/goal07a1_boundary_lock_audit.md") == "PASS"


def load_goal07a1_design_bundle(root: Path) -> dict[str, object]:
    return {
        "input_contract": read_json(root / f"{RISK_DIR}/goal07a_allowed_input_contract.yaml"),
        "output_schema": read_json(root / f"{RISK_DIR}/goal07a_future_risk_overlay_output_schema.yaml"),
        "rule_catalog": read_json(root / f"{RISK_DIR}/goal07a_risk_rule_catalog.yaml"),
        "state_machine": read_json(root / f"{RISK_DIR}/goal07a_risk_state_machine.yaml"),
        "warning_mapping": read_json(root / f"{RISK_DIR}/goal07a_upstream_warning_mapping.yaml"),
        "workflow_rows": read_csv(root / "configs/project/workflow_status.csv"),
        "goal07b0_unlock_report": _read(root / f"{AUDIT_DIR}/goal07b0_unlock_gate_report.md"),
        "goal06c7_readiness": _read(root / f"{AUDIT_DIR}/goal06c7_readiness_report.md"),
        "goal06d_readiness": _read(root / f"{AUDIT_DIR}/goal06d_readiness_report.md"),
        "goal06d1_readiness": _read(root / f"{AUDIT_DIR}/goal06d1_readiness_report.md"),
        "forbidden_output_dirs_present": [path for path in FORBIDDEN_OUTPUT_DIRS if (root / path).exists()],
        "goal090_valid_evidence": goal090_valid_unlock_evidence(root),
        "goal09_expected_workflow_patch": goal09_eligible_workflow_patch(root),
    }


def evaluate_goal07a1_design_review(bundle: dict[str, object]) -> dict[str, object]:
    input_review = review_goal07a1_input_contract(bundle["input_contract"], bundle["warning_mapping"])
    schema_review = review_goal07a1_output_schema(bundle["output_schema"])
    rule_review = review_goal07a1_rule_catalog(bundle["rule_catalog"])
    state_review = review_goal07a1_state_machine(bundle["state_machine"])
    warning_rows = classify_goal07a1_upstream_warnings(bundle.get("goal06c7_readiness", ""), bundle.get("goal06d_readiness", ""), bundle.get("goal06d1_readiness", ""))
    boundary_review = review_goal07a1_boundaries(
        bundle.get("workflow_rows", []),
        bundle.get("forbidden_output_dirs_present", []),
        str(bundle.get("goal07b0_unlock_report", "")),
        bool(bundle.get("goal090_valid_evidence")),
        bundle.get("goal09_expected_workflow_patch", {}),
    )
    goal07b_status = _goal07b_status_from_rows(bundle.get("workflow_rows", []), str(bundle.get("goal07b0_unlock_report", "")))
    reviews = {
        "input_contract": input_review,
        "output_schema": schema_review,
        "rule_catalog": rule_review,
        "state_machine": state_review,
        "boundary_locks": boundary_review,
    }
    failures = []
    warnings = []
    boundary_failures = []
    for name, review in reviews.items():
        failures.extend(f"{name}:{item}" for item in review["failures"])
        warnings.extend(f"{name}:{item}" for item in review["warnings"])
        if name in {"output_schema", "state_machine", "boundary_locks"}:
            boundary_failures.extend(f"{name}:{item}" for item in review["failures"])
    for row in warning_rows:
        if row["classification"] == "BLOCKER_FOR_07B" and row["active_in_current_design"]:
            failures.append(f"warning_policy:{row['warning_code']}")
        elif row["classification"] in {"PASS_THROUGH_WARNING", "DESIGN_REVIEW_WARNING"} and row["active_in_current_design"]:
            warnings.append(f"warning_policy:{row['warning_code']}")
    status = REVIEW_STATUS_FAIL if failures else (REVIEW_STATUS_WARN if warnings else REVIEW_STATUS_PASS)
    if boundary_failures:
        readiness = GOAL07B_BLOCKED
        allowed_next_action = ALLOWED_NEXT_ACTION_BLOCKED
    elif failures:
        readiness = GOAL07B_NOT_READY
        allowed_next_action = ALLOWED_NEXT_ACTION_NOT_READY
    else:
        readiness = GOAL07B_READY
        allowed_next_action = ALLOWED_NEXT_ACTION_READY
    return {
        "status": status,
        "goal07b_unlock_readiness": readiness,
        "allowed_next_action": allowed_next_action,
        "goal07b_remains": goal07b_status,
        "reviews": reviews,
        "warning_classifications": warning_rows,
        "failures": failures,
        "warnings": sorted(set(warnings)),
    }


def review_goal07a1_input_contract(contract: dict[str, object], warning_mapping: dict[str, object]) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    allowed = set(contract.get("allowed_future_input_fields", []))
    datasets = contract.get("required_upstream_datasets", [])
    dataset_ids = {row.get("dataset_id") for row in datasets if isinstance(row, dict)}
    if not REQUIRED_DATASET_IDS <= dataset_ids:
        failures.append("required_upstream_datasets_not_explicit")
    dataset_grains = {str(row.get("grain", "")) for row in datasets if isinstance(row, dict)}
    if contract.get("grain") != "trade_date + symbol" or not any("trade_date" in grain and "symbol" in grain for grain in dataset_grains):
        failures.append("grain_not_trade_date_symbol")
    forbidden_inputs = ";".join(str(item) for item in contract.get("forbidden_inputs", []))
    pit_rule = str(contract.get("pit_safety_rule", ""))
    if "future_returns" not in forbidden_inputs or "forward_labels" not in forbidden_inputs or "must not include forward labels" not in pit_rule:
        failures.append("future_data_leakage_boundary_missing")
    if not REQUIRED_WARNING_FIELDS <= allowed:
        failures.append("required_warning_fields_not_available")
    mapped = {row.get("warning_code") for row in warning_mapping.get("mappings", []) if isinstance(row, dict)}
    if not set(UPSTREAM_WARNINGS) <= mapped:
        failures.append("upstream_warnings_not_traceable")
    optional = set(contract.get("optional_future_input_fields", []))
    missing_optional = sorted(optional - allowed)
    if missing_optional:
        warnings.append("missing_optional_fields:" + ";".join(missing_optional))
    if contract.get("missing_optional_field_policy") != "classify_as_DESIGN_REVIEW_WARNING_not_silent_failure":
        warnings.append("missing_optional_field_policy_not_explicit")
    return _review_result(failures, warnings)


def review_goal07a1_output_schema(schema: dict[str, object]) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    allowed_fields = list(schema.get("allowed_future_schema_fields", []))
    forbidden_fields = set(schema.get("forbidden_schema_fields", []))
    overlap = sorted(set(allowed_fields) & forbidden_fields)
    semantic_hits = sorted(field for field in allowed_fields if _has_forbidden_schema_semantics(field))
    if overlap:
        failures.append("forbidden_schema_overlap:" + ";".join(overlap))
    if semantic_hits:
        failures.append("forbidden_schema_semantics:" + ";".join(semantic_hits))
    if schema.get("empty_schema_sample", {}).get("row_count") != 0:
        failures.append("schema_sample_contains_rows")
    review_only_hints = {hint for field in allowed_fields for hint in REVIEW_ONLY_OUTPUT_HINTS if hint in field or field == hint}
    if "review_only" not in allowed_fields or len(review_only_hints) < 5:
        warnings.append("limited_review_only_metadata")
    return _review_result(failures, warnings)


def review_goal07a1_rule_catalog(catalog: dict[str, object]) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    allowed_states = set(catalog.get("allowed_future_risk_states", []))
    if not set(RISK_STATES) <= allowed_states:
        failures.append("severity_levels_not_finite")
    seen: set[str] = set()
    for rule in catalog.get("rules", []):
        if not isinstance(rule, dict):
            failures.append("rule_not_object")
            continue
        rule_id = str(rule.get("rule_id", ""))
        if not rule_id or rule_id in seen:
            failures.append("unstable_or_duplicate_rule_id")
        seen.add(rule_id)
        domain_count = sum(bool(rule.get(key)) for key in ["risk_domain_id", "composite_risk_domain_id"])
        if domain_count != 1:
            failures.append(f"{rule_id}:domain_mapping_ambiguous")
        elif rule.get("risk_domain_id") and rule.get("risk_domain_id") not in set(RISK_DOMAINS):
            failures.append(f"{rule_id}:unknown_risk_domain")
        if not rule.get("threshold_logic_design"):
            failures.append(f"{rule_id}:threshold_logic_missing")
        if rule.get("severity_level") not in RISK_STATES:
            failures.append(f"{rule_id}:severity_not_finite")
        if not rule.get("warning_behavior"):
            failures.append(f"{rule_id}:warning_behavior_missing")
        dependency_policy = str(rule.get("data_dependency_policy", "")).lower()
        if any(token in dependency_policy for token in ["broker", "live_trading", "production"]):
            failures.append(f"{rule_id}:forbidden_data_dependency")
        if any(_has_forbidden_schema_semantics(str(rule.get(field, ""))) for field in ["future_output_field", "future_effect_design"]):
            failures.append(f"{rule_id}:recommendation_or_position_semantics")
        if rule.get("execution_in_goal07a") is not False or rule.get("real_symbol_assignment_in_goal07a") is not False:
            failures.append(f"{rule_id}:executes_in_goal07a")
    if len(seen) < 6:
        failures.append("too_few_rules")
    return _review_result(failures, warnings)


def review_goal07a1_state_machine(machine: dict[str, object]) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    states = machine.get("states", [])
    state_set = set(states)
    if set(STATE_MACHINE_STATES) != state_set or len(states) != len(state_set):
        failures.append("states_not_finite_or_named")
    transitions = machine.get("transitions", [])
    if not transitions:
        failures.append("transitions_missing")
    for item in transitions:
        if not isinstance(item, dict):
            failures.append("transition_not_object")
            continue
        if item.get("from_state") not in state_set or item.get("to_state") not in state_set or not item.get("trigger_design"):
            failures.append("transition_ambiguous")
        if item.get("execution_in_goal07a") is not False or item.get("real_symbol_transition_in_goal07a") is not False:
            failures.append("symbol_level_transition_executed")
        if item.get("output_semantics") != "diagnostic_only":
            failures.append("transition_output_not_diagnostic_only")
    if not machine.get("blocked_transitions"):
        failures.append("blocked_transitions_not_explicit")
    if machine.get("transition_output_policy") != "diagnostic_state_only_no_trade_action_no_recommendation_no_position":
        failures.append("transition_output_policy_not_review_only")
    return _review_result(failures, warnings)


def classify_goal07a1_upstream_warnings(goal06c7_readiness: str, goal06d_readiness: str, goal06d1_readiness: str) -> list[dict[str, object]]:
    combined = "\n".join([goal06c7_readiness, goal06d_readiness, goal06d1_readiness])
    rows = []
    for code, classification in WARNING_POLICY.items():
        active = code in combined if code in UPSTREAM_WARNINGS else False
        rows.append(
            {
                "warning_code": code,
                "classification": classification,
                "active_in_current_design": active,
                "goal07b_policy": _warning_policy_text(code, classification),
            }
        )
    return rows


def review_goal07a1_boundaries(
    workflow_rows: list[dict[str, str]],
    forbidden_output_dirs_present: list[str],
    goal07b0_unlock_report: str = "",
    goal090_valid: bool = False,
    goal09_expected: object = None,
) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    rows = {row.get("workflow_id", ""): row for row in workflow_rows}
    goal07b = rows.get(GOAL07B_WORKFLOW_ID, {})
    if goal07b.get("status") not in GOAL07B_ALLOWED_STATUSES:
        failures.append("goal07b_not_locked_future_review_only_or_implemented_review_only")
    if goal07b.get("status") == "implemented_review_only" and goal07b.get("implemented_in_repo") != "true":
        failures.append("goal07b_implemented_review_only_not_marked_implemented")
    elif goal07b.get("status") != "implemented_review_only" and goal07b.get("implemented_in_repo") == "true":
        failures.append("goal07b_marked_implemented")
    if goal07b.get("status") == "future_review_only" and "GOAL-07B.0 Risk Overlay Review-Only Unlock Gate:" not in goal07b0_unlock_report:
        failures.append("goal07b_future_review_only_without_goal07b0_evidence")
    for workflow_id in DOWNSTREAM_LOCKED_IDS:
        row = rows.get(workflow_id, {})
        if workflow_id == GOAL09_WORKFLOW_ID and goal090_valid:
            expected = goal09_expected if isinstance(goal09_expected, dict) else {}
            if row.get("status") != expected.get("status") or row.get("implemented_in_repo") != expected.get("implemented_in_repo"):
                failures.append(f"{workflow_id}_not_preserved_after_goal090")
            continue
        if row.get("status") != "locked_future":
            failures.append(f"{workflow_id}_not_locked_future")
    if rows.get("dqn_rl_mainline", {}).get("status") != "deleted_from_active_mainline":
        failures.append("dqn_rl_not_deleted_from_active_mainline")
    if forbidden_output_dirs_present:
        failures.append("forbidden_output_dirs_present:" + ";".join(forbidden_output_dirs_present))
    return _review_result(failures, warnings)


def _write_policy(root: Path) -> None:
    write_json(
        root / f"{RISK_DIR}/goal07a1_design_review_policy.yaml",
        {
            "goal": "GOAL-07A.1",
            "mode": "design_review_only",
            "status_values": [REVIEW_STATUS_PASS, REVIEW_STATUS_WARN, REVIEW_STATUS_FAIL],
            "goal07b_unlock_readiness_values": [GOAL07B_READY, GOAL07B_NOT_READY, GOAL07B_BLOCKED],
            "required_dataset_ids": sorted(REQUIRED_DATASET_IDS),
            "required_warning_fields": sorted(REQUIRED_WARNING_FIELDS),
            "forbidden_schema_terms": sorted(FORBIDDEN_SCHEMA_TERMS),
            "warning_policy": WARNING_POLICY,
            "forbidden_outputs": FORBIDDEN_OUTPUT_DIRS,
            "goal07a1_execution_policy": {
                "calculate_risk_values": False,
                "write_symbol_level_risk_rows": False,
                "implement_goal07b": False,
                "generate_recommendations_or_positions": False,
            },
        },
    )


def _write_review_outputs(root: Path, review: dict[str, object]) -> None:
    _write_report(root, review)
    _write_audit_reports(root, review)
    write_json(
        root / f"{AUDIT_DIR}/goal07a1_unlock_readiness_manifest.json",
        {
            "goal": "GOAL-07A.1",
            "status": review["status"],
            "goal07b_unlock_readiness": review["goal07b_unlock_readiness"],
            "goal07b_remains": review["goal07b_remains"],
            "allowed_next_action": review["allowed_next_action"],
            "failures": review["failures"],
            "warnings": review["warnings"],
            "risk_calculation_performed": False,
            "symbol_level_risk_rows_created": False,
            "recommendation_or_position_output_created": False,
            "dashboard_trading_production_backtest_factor_dqn_output_created": False,
        },
    )
    write_csv(root / f"{AUDIT_DIR}/goal07a1_warning_classification.csv", review["warning_classifications"])
    write_text(
        root / f"{DOC_DIR}/GOAL07A1_RISK_OVERLAY_DESIGN_REVIEW.md",
        "\n".join(
            [
                "# GOAL-07A.1 Risk Overlay Design Review",
                "",
                f"GOAL-07A.1 Risk Overlay Design Review: {review['status']}",
                f"GOAL-07B unlock readiness: {review['goal07b_unlock_readiness']}",
                f"GOAL-07B remains: {review['goal07b_remains']}",
                f"Allowed next action: `{review['allowed_next_action']}`",
                "",
                "This gate reviews GOAL-07A design artifacts only. It does not implement GOAL-07B, calculate risk values, assign real symbol risk tags, or generate recommendation, position, dashboard, paper/live trading, production, backtest, factor-mining, DQN/RL, or broker outputs.",
                "",
                "## Review Scope",
                "- GOAL-07A allowed input contract readiness.",
                "- Future output schema safety.",
                "- Risk rule catalog convertibility.",
                "- State machine review-only executability.",
                "- Upstream warning policy.",
                "- GOAL-07B and downstream lock preservation.",
                "",
            ]
        ),
    )


def _write_report(root: Path, review: dict[str, object]) -> None:
    lines = [
        "# GOAL-07A.1 Risk Overlay Design Review Report",
        "",
        f"GOAL-07A.1 Risk Overlay Design Review: {review['status']}",
        f"GOAL-07B unlock readiness: {review['goal07b_unlock_readiness']}",
        f"GOAL-07B remains: {review['goal07b_remains']}",
        f"Allowed next action: `{review['allowed_next_action']}`",
        "No risk calculation was performed",
        "No recommendation/position/dashboard/paper/live/production/backtest/factor-mining/DQN/RL output was created",
        "",
        "## Review Results",
    ]
    for name, item in review["reviews"].items():
        lines.append(f"- `{name}`: `{item['status']}`; failures `{len(item['failures'])}`; warnings `{len(item['warnings'])}`")
    lines.extend(["", "## Warning Classifications"])
    for row in review["warning_classifications"]:
        lines.append(f"- `{row['warning_code']}`: `{row['classification']}`")
    lines.extend(["", "## Failures"])
    lines.extend(f"- {failure}" for failure in review["failures"])
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {warning}" for warning in review["warnings"])
    lines.append("")
    write_text(root / f"{AUDIT_DIR}/goal07a1_design_review_report.md", "\n".join(lines))


def _write_audit_reports(root: Path, review: dict[str, object]) -> None:
    audit_map = {
        "goal07a1_input_contract_readiness_audit.md": ("GOAL-07A.1 Input Contract Readiness Audit", review["reviews"]["input_contract"]),
        "goal07a1_forbidden_schema_overlap_audit.md": ("GOAL-07A.1 Forbidden Schema Overlap Audit", review["reviews"]["output_schema"]),
        "goal07a1_rule_convertibility_audit.md": ("GOAL-07A.1 Rule Convertibility Audit", review["reviews"]["rule_catalog"]),
        "goal07a1_state_machine_review_audit.md": ("GOAL-07A.1 State Machine Review Audit", review["reviews"]["state_machine"]),
        "goal07a1_boundary_lock_audit.md": ("GOAL-07A.1 Boundary Lock Audit", review["reviews"]["boundary_locks"]),
    }
    for filename, (title, item) in audit_map.items():
        lines = [f"# {title}", "", f"Status: `{item['status']}`", "", "## Failures"]
        lines.extend(f"- {failure}" for failure in item["failures"])
        lines.extend(["", "## Warnings"])
        lines.extend(f"- {warning}" for warning in item["warnings"])
        lines.append("")
        write_text(root / f"{AUDIT_DIR}/{filename}", "\n".join(lines))


def _update_workflow_status(root: Path, review: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    by_id = {row["workflow_id"]: row for row in rows}
    row = {
        "workflow_id": "goal07a1_risk_overlay_design_review_unlock_readiness",
        "display_name": "GOAL-07A.1 Risk Overlay Design Review Unlock Readiness",
        "stage_or_goal": "GOAL-07A.1",
        "status": "implemented_review_only" if review["status"] != REVIEW_STATUS_FAIL else "future_review_only",
        "current_repo_role": "design_review_governance_gate",
        "implemented_in_repo": "true" if review["status"] != REVIEW_STATUS_FAIL else "false",
        "allowed_next_action": str(review["allowed_next_action"]),
        "depends_on": "goal07a_risk_overlay_design",
        "produces_artifacts": "outputs/audits/goal07a1_design_review_report.md;outputs/audits/goal07a1_unlock_readiness_manifest.json;outputs/audits/goal07a1_warning_classification.csv",
        "primary_docs": "docs/risk/GOAL07A1_RISK_OVERLAY_DESIGN_REVIEW.md;docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md",
        "primary_scripts": "scripts/run_goal07a1_risk_overlay_design_review_gate.py;scripts/audit_goal07a1_input_contract_readiness.py;scripts/audit_goal07a1_output_schema_safety.py;scripts/audit_goal07a1_rule_convertibility.py;scripts/audit_goal07a1_state_machine_review.py;scripts/audit_goal07a1_warning_policy.py;scripts/audit_goal07a1_boundary_locks.py",
        "primary_outputs": "outputs/audits/goal07a1_design_review_report.md;outputs/audits/goal07a1_unlock_readiness_manifest.json",
        "promotion_rule": "implemented_review_only_after_goal07a1_design_review_pass_with_warnings",
        "notes": "Review-only design review gate; GOAL-07B may be implemented only by its own diagnostic-only prototype after GOAL-07B.0.",
    }
    if row["workflow_id"] in by_id:
        by_id[row["workflow_id"]].update(row)
    else:
        insert_at = next((index for index, existing in enumerate(rows) if existing["workflow_id"] == "goal07b_risk_overlay_calculation"), len(rows))
        rows.insert(insert_at, row)
    by_id = {existing["workflow_id"]: existing for existing in rows}
    if GOAL07B_WORKFLOW_ID in by_id:
        goal07b_status = _goal07b_status_from_rows(rows, _read(root / f"{AUDIT_DIR}/goal07b0_unlock_gate_report.md"))
        by_id[GOAL07B_WORKFLOW_ID]["status"] = goal07b_status
        by_id[GOAL07B_WORKFLOW_ID]["implemented_in_repo"] = "true" if goal07b_status == "implemented_review_only" else "false"
        if goal07b_status == "implemented_review_only":
            by_id[GOAL07B_WORKFLOW_ID]["allowed_next_action"] = "prepare_goal08a_recommendation_contract_design_gate_or_fix_goal07b_warnings"
        else:
            by_id[GOAL07B_WORKFLOW_ID]["allowed_next_action"] = "await_explicit_goal07b_review_only_calculation_prototype" if goal07b_status == "future_review_only" else "remain_locked"
        by_id[GOAL07B_WORKFLOW_ID]["depends_on"] = "goal07b0_risk_overlay_review_only_unlock_gate" if goal07b_status in {"future_review_only", "implemented_review_only"} else "goal07a1_risk_overlay_design_review_unlock_readiness"
        if goal07b_status == "implemented_review_only":
            by_id[GOAL07B_WORKFLOW_ID]["notes"] = "Review-only risk overlay diagnostics; non-actionable and not a recommendation, position, dashboard, trading, production, backtest, factor-mining, or DQN/RL output."
        else:
            by_id[GOAL07B_WORKFLOW_ID]["notes"] = "GOAL-07B may be implemented_review_only only by its own diagnostic-only prototype; future_review_only eligibility requires GOAL-07B.0 evidence."
    preserve_later_review_only_workflow_states(root, by_id)
    write_csv(path, rows, list(rows[0].keys()))


def _has_forbidden_schema_semantics(field: str) -> bool:
    lowered = field.lower()
    return any(term in lowered for term in FORBIDDEN_SCHEMA_TERMS)


def _warning_policy_text(code: str, classification: str) -> str:
    if classification == "BLOCKER_FOR_07B":
        return "Blocks future GOAL-07B until repaired."
    if classification == "PASS_THROUGH_WARNING":
        return "Pass through into future review-only risk warning metadata."
    if classification == "DESIGN_REVIEW_WARNING":
        return "Keep visible during explicit unlock review; does not create trading action."
    return "No current blocking action."


def _review_result(failures: list[str], warnings: list[str]) -> dict[str, object]:
    return {
        "status": "FAIL" if failures else "PASS",
        "failures": failures,
        "warnings": warnings,
    }


def _goal07b_status_from_rows(workflow_rows: object, goal07b0_unlock_report: str) -> str:
    if not isinstance(workflow_rows, list):
        return "locked_future"
    rows = {row.get("workflow_id", ""): row for row in workflow_rows if isinstance(row, dict)}
    current = rows.get(GOAL07B_WORKFLOW_ID, {}).get("status", "locked_future")
    if current == "implemented_review_only":
        return "implemented_review_only"
    if current == "future_review_only" and "GOAL-07B.0 Risk Overlay Review-Only Unlock Gate:" in goal07b0_unlock_report:
        return "future_review_only"
    return "locked_future"


def _status_from_report(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Status:"):
            return line.replace("Status:", "").strip(" `")
        if line.startswith("GOAL-07A.1 Risk Overlay Design Review:"):
            return line.split(":", 1)[1].strip()
    return "MISSING"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""

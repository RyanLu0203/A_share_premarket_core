from __future__ import annotations

from pathlib import Path

from ashare_premarket.contract_design.goal090 import (
    GOAL09_ELIGIBLE_STATUS,
    GOAL09_WORKFLOW_ID,
    goal09_eligible_workflow_patch,
    goal090_valid_unlock_evidence,
)
from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

AUDIT_DIR = "outputs/audits"
RISK_DIR = "configs/risk"
DOC_DIR = "docs/risk"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

GOAL07B_LOCKED_STATUS = "locked_future"
GOAL07B_ELIGIBLE_STATUS = "future_review_only"
GOAL07B_IMPLEMENTED_STATUS = "implemented_review_only"
GOAL07B0_READY = "eligible_for_future_review_only_prototype"
GOAL07B0_BLOCKED = "blocked_until_prior_review_evidence_passes"
GOAL07B0_ALLOWED_NEXT = "future_goal07b_review_only_calculation_prototype_may_be_requested"
GOAL07B0_BLOCKED_NEXT = "repair_goal07b0_unlock_blockers"

GOAL07A1_READY = "ready_for_explicit_review_only_unlock"

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


def run_goal07b0_risk_overlay_review_only_unlock_gate(root: Path) -> bool:
    bundle = load_goal07b0_unlock_bundle(root)
    review = evaluate_goal07b0_unlock_gate(bundle)
    _write_policy(root)
    _write_unlock_outputs(root, review)
    _update_workflow_status(root, review)
    _update_locked_capabilities(root, review)
    audit_ok = audit_goal07b0_risk_overlay_review_only_unlock_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return review["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal07b0_risk_overlay_review_only_unlock_gate(root: Path) -> bool:
    report = _read(root / f"{AUDIT_DIR}/goal07b0_unlock_gate_report.md")
    manifest = _read_json(root / f"{AUDIT_DIR}/goal07b0_unlock_gate_manifest.json")
    workflow = {row["workflow_id"]: row for row in read_csv(root / "configs/project/workflow_status.csv")}
    failures: list[str] = []
    warnings: list[str] = []

    if "GOAL-07B.0 Risk Overlay Review-Only Unlock Gate: PASS_WITH_WARNINGS" not in report and "GOAL-07B.0 Risk Overlay Review-Only Unlock Gate: PASS" not in report:
        failures.append("unlock_report_not_pass_or_warn")
    if manifest.get("goal07b0_unlock_status") != GOAL07B0_READY:
        failures.append("unlock_manifest_not_ready")
    if manifest.get("goal07b_target_status") not in {GOAL07B_ELIGIBLE_STATUS, GOAL07B_IMPLEMENTED_STATUS}:
        failures.append("goal07b_target_status_not_future_or_implemented_review_only")
    for key in [
        "risk_calculation_performed",
        "symbol_level_risk_rows_created",
        "recommendation_or_position_output_created",
        "dashboard_trading_production_backtest_factor_dqn_output_created",
        "live_calculation_outputs_used",
    ]:
        if manifest.get(key) is not False:
            failures.append(f"{key}_not_false")

    goal07b = workflow.get("goal07b_risk_overlay_calculation", {})
    if goal07b.get("status") == GOAL07B_IMPLEMENTED_STATUS:
        if goal07b.get("implemented_in_repo") != "true":
            failures.append("goal07b_implemented_review_only_not_marked_implemented")
        if not _goal07b_review_only_outputs_valid(root):
            failures.append("goal07b_implemented_review_only_outputs_invalid")
    elif goal07b.get("status") == GOAL07B_ELIGIBLE_STATUS:
        if goal07b.get("implemented_in_repo") != "false":
            failures.append("goal07b_future_review_only_marked_implemented")
    else:
        failures.append("goal07b_workflow_not_future_or_implemented_review_only")
    goal090_valid = goal090_valid_unlock_evidence(root)
    for workflow_id in DOWNSTREAM_LOCKED_IDS:
        row = workflow.get(workflow_id, {})
        if workflow_id == GOAL09_WORKFLOW_ID and goal090_valid:
            if row.get("status") != GOAL09_ELIGIBLE_STATUS or row.get("implemented_in_repo") != "false":
                failures.append(f"{workflow_id}_not_future_review_only_after_goal090")
            continue
        if row.get("status") != GOAL07B_LOCKED_STATUS:
            failures.append(f"{workflow_id}_not_locked_future")
    if workflow.get("dqn_rl_mainline", {}).get("status") != "deleted_from_active_mainline":
        failures.append("dqn_rl_not_deleted_from_active_mainline")
    if _forbidden_output_dirs_present(root):
        failures.append("forbidden_output_dirs_present")
    if _risk_calculation_csv_outputs(root, allow_goal07b_outputs=_goal07b_review_only_outputs_allowed(root)):
        failures.append("risk_calculation_csv_outputs_present")

    status = PASS if not failures else BLOCKED
    write_text(
        root / f"{AUDIT_DIR}/goal07b0_unlock_gate_audit_report.md",
        "\n".join(
            [
                "# GOAL-07B.0 Unlock Gate Audit Report",
                "",
                f"Status: `{status}`",
                "",
                f"GOAL-07B workflow status: `{goal07b.get('status', 'missing')}`",
                f"GOAL-07B implemented in repo: `{goal07b.get('implemented_in_repo', 'missing')}`",
                "Risk calculation performed: `false`",
                "Symbol-level risk rows created: `false`",
                "Recommendation/position/dashboard/trading/production/backtest/factor/DQN outputs created: `false`",
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


def load_goal07b0_unlock_bundle(root: Path) -> dict[str, object]:
    return {
        "goal07a_readiness": _read(root / f"{AUDIT_DIR}/goal07a_readiness_report.md"),
        "goal07a1_review": _read(root / f"{AUDIT_DIR}/goal07a1_design_review_report.md"),
        "goal07a1_manifest": _read_json(root / f"{AUDIT_DIR}/goal07a1_unlock_readiness_manifest.json"),
        "workflow_rows": read_csv(root / "configs/project/workflow_status.csv"),
        "forbidden_output_dirs_present": _forbidden_output_dirs_present(root),
        "risk_calculation_csv_outputs": _risk_calculation_csv_outputs(root, allow_goal07b_outputs=_goal07b_review_only_outputs_allowed(root)),
        "goal090_valid_evidence": goal090_valid_unlock_evidence(root),
    }


def evaluate_goal07b0_unlock_gate(bundle: dict[str, object]) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    goal07a_readiness = str(bundle.get("goal07a_readiness", ""))
    goal07a1_review = str(bundle.get("goal07a1_review", ""))
    goal07a1_manifest = bundle.get("goal07a1_manifest", {})
    workflow_rows = bundle.get("workflow_rows", [])
    workflow = {row.get("workflow_id", ""): row for row in workflow_rows if isinstance(row, dict)}

    if not _report_pass_or_warn(goal07a_readiness, "GOAL-07A Risk Overlay Design Readiness:"):
        failures.append("goal07a_readiness_not_pass_or_warn")
    elif "PASS_WITH_WARNINGS" in goal07a_readiness:
        warnings.append("goal07a_prior_pass_with_warnings")
    if not _report_pass_or_warn(goal07a1_review, "GOAL-07A.1 Risk Overlay Design Review:"):
        failures.append("goal07a1_design_review_not_pass_or_warn")
    elif "PASS_WITH_WARNINGS" in goal07a1_review:
        warnings.append("goal07a1_prior_pass_with_warnings")
    if not isinstance(goal07a1_manifest, dict):
        failures.append("goal07a1_manifest_invalid")
        goal07a1_manifest = {}
    if goal07a1_manifest.get("goal07b_unlock_readiness") != GOAL07A1_READY:
        failures.append("goal07a1_manifest_not_ready_for_unlock")
    for key in [
        "risk_calculation_performed",
        "symbol_level_risk_rows_created",
        "recommendation_or_position_output_created",
        "dashboard_trading_production_backtest_factor_dqn_output_created",
    ]:
        if goal07a1_manifest.get(key) is not False:
            failures.append(f"goal07a1_{key}_not_false")

    if workflow.get("goal07a_risk_overlay_design", {}).get("status") != "implemented_design_only":
        failures.append("goal07a_not_implemented_design_only")
    if workflow.get("goal07a1_risk_overlay_design_review_unlock_readiness", {}).get("status") != "implemented_review_only":
        failures.append("goal07a1_not_implemented_review_only")
    goal07b = workflow.get("goal07b_risk_overlay_calculation", {})
    goal07b_status = goal07b.get("status")
    goal07b_implemented_valid = goal07b_status == GOAL07B_IMPLEMENTED_STATUS and goal07b.get("implemented_in_repo") == "true"
    if goal07b_status not in {GOAL07B_LOCKED_STATUS, GOAL07B_ELIGIBLE_STATUS, GOAL07B_IMPLEMENTED_STATUS}:
        failures.append("goal07b_status_not_locked_eligible_or_implemented_review_only")
    if goal07b.get("implemented_in_repo") == "true" and not goal07b_implemented_valid:
        failures.append("goal07b_marked_implemented_before_unlock")
    goal090_valid = bool(bundle.get("goal090_valid_evidence"))
    for workflow_id in DOWNSTREAM_LOCKED_IDS:
        row = workflow.get(workflow_id, {})
        if workflow_id == GOAL09_WORKFLOW_ID and goal090_valid:
            continue
        if row.get("status") != GOAL07B_LOCKED_STATUS:
            failures.append(f"{workflow_id}_not_locked_future")
    if workflow.get("dqn_rl_mainline", {}).get("status") != "deleted_from_active_mainline":
        failures.append("dqn_rl_not_deleted_from_active_mainline")
    if workflow.get("v2_factor_research_upgrade", {}).get("status") != "planned_locked":
        failures.append("v2_factor_research_not_planned_locked")
    if bundle.get("forbidden_output_dirs_present"):
        failures.append("forbidden_output_dirs_present:" + ";".join(str(path) for path in bundle["forbidden_output_dirs_present"]))
    if bundle.get("risk_calculation_csv_outputs"):
        failures.append("risk_calculation_csv_outputs_present:" + ";".join(str(path) for path in bundle["risk_calculation_csv_outputs"]))

    status = BLOCKED if failures else (PASS_WITH_WARNINGS if warnings else PASS)
    return {
        "status": status,
        "goal07b0_unlock_status": GOAL07B0_BLOCKED if failures else GOAL07B0_READY,
        "goal07b_prior_status": goal07b.get("status", "missing"),
        "goal07b_target_status": GOAL07B_LOCKED_STATUS if failures else (GOAL07B_IMPLEMENTED_STATUS if goal07b_implemented_valid else GOAL07B_ELIGIBLE_STATUS),
        "goal07b_transition_rule": "locked_future_to_future_review_only_or_preserve_implemented_review_only_rerun",
        "allowed_next_action": GOAL07B0_BLOCKED_NEXT if failures else GOAL07B0_ALLOWED_NEXT,
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "evidence_inputs": [
            "outputs/audits/goal07a_readiness_report.md",
            "outputs/audits/goal07a1_design_review_report.md",
            "outputs/audits/goal07a1_unlock_readiness_manifest.json",
            "configs/project/workflow_status.csv",
        ],
    }


def _write_policy(root: Path) -> None:
    write_json(
        root / f"{RISK_DIR}/goal07b0_review_only_unlock_policy.yaml",
        {
            "goal": "GOAL-07B.0",
            "mode": "review_only_unlock_gate",
            "unlocks": "GOAL-07B eligibility only",
            "goal07b_status_after_pass": GOAL07B_ELIGIBLE_STATUS,
            "goal07b_implemented_after_pass": False,
            "required_prior_evidence": [
                "GOAL-07A PASS/PASS_WITH_WARNINGS design readiness",
                "GOAL-07A.1 PASS/PASS_WITH_WARNINGS design review",
                "GOAL-07A.1 ready_for_explicit_review_only_unlock manifest",
            ],
            "forbidden_execution": {
                "risk_calculation": True,
                "symbol_level_risk_rows": True,
                "recommendation_or_position_outputs": True,
                "dashboard_outputs": True,
                "paper_or_live_trading": True,
                "production_db_writes": True,
                "backtests": True,
                "factor_mining": True,
                "dqn_rl": True,
            },
            "evidence_source_policy": "prior_audit_reports_only_no_live_calculation_outputs",
            "forbidden_output_dirs": FORBIDDEN_OUTPUT_DIRS,
        },
    )


def _write_unlock_outputs(root: Path, review: dict[str, object]) -> None:
    lines = [
        "# GOAL-07B.0 Risk Overlay Review-Only Unlock Gate Report",
        "",
        f"GOAL-07B.0 Risk Overlay Review-Only Unlock Gate: {review['status']}",
        f"GOAL-07B.0 unlock status: {review['goal07b0_unlock_status']}",
        f"GOAL-07B prior status: `{review['goal07b_prior_status']}`",
        f"GOAL-07B target status: `{review['goal07b_target_status']}`",
        f"GOAL-07B transition rule: `{review['goal07b_transition_rule']}`",
        f"Allowed next action: `{review['allowed_next_action']}`",
        "",
        "GOAL-07B.0 only grants review-only eligibility or preserves an existing review-only GOAL-07B diagnostic state.",
        "GOAL-07B is not implemented by this gate.",
        "No risk calculation was performed by this gate.",
        "No symbol-level risk overlay rows were created by this gate.",
        "No recommendation, position, dashboard, paper/live trading, production, backtest, factor-mining, broker, or DQN/RL output was created.",
        "Evidence basis: prior PASS/PASS_WITH_WARNINGS design-review reports and manifests only; no live calculation outputs were used.",
        "",
        "## Evidence Inputs",
        *[f"- `{item}`" for item in review["evidence_inputs"]],
        "",
        "## Failures",
        *[f"- {failure}" for failure in review["failures"]],
        "",
        "## Warnings",
        *[f"- {warning}" for warning in review["warnings"]],
        "",
    ]
    write_text(root / f"{AUDIT_DIR}/goal07b0_unlock_gate_report.md", "\n".join(lines))
    write_json(
        root / f"{AUDIT_DIR}/goal07b0_unlock_gate_manifest.json",
        {
            "goal": "GOAL-07B.0-RISK-OVERLAY-REVIEW-ONLY-UNLOCK-GATE",
            "status": review["status"],
            "goal07b0_unlock_status": review["goal07b0_unlock_status"],
            "goal07b_prior_status": review["goal07b_prior_status"],
            "goal07b_target_status": review["goal07b_target_status"],
            "goal07b_transition_rule": review["goal07b_transition_rule"],
            "goal07b_implemented_by_this_gate": False,
            "goal07b_currently_implemented_review_only": review["goal07b_target_status"] == GOAL07B_IMPLEMENTED_STATUS,
            "allowed_next_action": review["allowed_next_action"],
            "evidence_inputs": review["evidence_inputs"],
            "evidence_basis": "prior_pass_or_pass_with_warnings_design_review_evidence_only",
            "failures": review["failures"],
            "warnings": review["warnings"],
            "risk_calculation_performed": False,
            "symbol_level_risk_rows_created": False,
            "recommendation_or_position_output_created": False,
            "dashboard_trading_production_backtest_factor_dqn_output_created": False,
            "live_calculation_outputs_used": False,
        },
    )
    write_text(
        root / f"{DOC_DIR}/GOAL07B0_RISK_OVERLAY_REVIEW_ONLY_UNLOCK_GATE.md",
        "\n".join(
            [
                "# GOAL-07B.0 Risk Overlay Review-Only Unlock Gate",
                "",
                f"Status: `{review['status']}`",
                "",
                "GOAL-07B.0 converts GOAL-07B from `locked_future` to `future_review_only` eligibility only when GOAL-07A and GOAL-07A.1 prior design-review evidence is PASS or PASS_WITH_WARNINGS. If a later GOAL-07B review-only implementation already exists, rerunning this gate preserves that implemented_review_only state.",
                "",
                "It does not implement GOAL-07B, calculate risk values, assign real symbol risk rows, create recommendations or positions, create dashboards, run backtests, write trading or production data, activate factor mining, or create DQN/RL outputs.",
                "",
                "If no GOAL-07B prototype exists yet, the only allowed next step after this gate is a separate future request for a review-only GOAL-07B calculation prototype. If GOAL-07B already exists, its own audit report and workflow row govern the next allowed action.",
                "",
            ]
        ),
    )


def _update_workflow_status(root: Path, review: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys())
    by_id = {row["workflow_id"]: row for row in rows}
    gate_row = {
        "workflow_id": "goal07b0_risk_overlay_review_only_unlock_gate",
        "display_name": "GOAL-07B.0 Risk Overlay Review-Only Unlock Gate",
        "stage_or_goal": "GOAL-07B.0",
        "status": "implemented_review_only" if review["status"] != BLOCKED else "future_review_only",
        "current_repo_role": "review_only_unlock_governance_gate",
        "implemented_in_repo": "true" if review["status"] != BLOCKED else "false",
        "allowed_next_action": str(review["allowed_next_action"]),
        "depends_on": "goal07a1_risk_overlay_design_review_unlock_readiness",
        "produces_artifacts": "outputs/audits/goal07b0_unlock_gate_report.md;outputs/audits/goal07b0_unlock_gate_manifest.json;outputs/audits/goal07b0_unlock_gate_audit_report.md",
        "primary_docs": "docs/risk/GOAL07B0_RISK_OVERLAY_REVIEW_ONLY_UNLOCK_GATE.md;docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md",
        "primary_scripts": "scripts/run_goal07b0_risk_overlay_review_only_unlock_gate.py;scripts/audit_goal07b0_risk_overlay_review_only_unlock_gate.py",
        "primary_outputs": "outputs/audits/goal07b0_unlock_gate_report.md;outputs/audits/goal07b0_unlock_gate_manifest.json;outputs/audits/goal07b0_unlock_gate_audit_report.md",
        "promotion_rule": "implemented_review_only_after_goal07b0_unlock_gate_pass_with_warnings",
        "notes": "Review-only unlock gate; marks GOAL-07B eligible for a future review-only prototype but does not implement risk calculation.",
    }
    if gate_row["workflow_id"] in by_id:
        by_id[gate_row["workflow_id"]].update(gate_row)
    else:
        insert_at = next((index for index, row in enumerate(rows) if row["workflow_id"] == "goal07b_risk_overlay_calculation"), len(rows))
        rows.insert(insert_at, gate_row)
    by_id = {row["workflow_id"]: row for row in rows}
    goal07b = by_id["goal07b_risk_overlay_calculation"]
    if review["goal07b_target_status"] != GOAL07B_IMPLEMENTED_STATUS:
        goal07b.update(
            {
                "display_name": "GOAL-07B Risk Overlay Calculation",
                "stage_or_goal": "GOAL-07B",
                "status": str(review["goal07b_target_status"]),
                "current_repo_role": "review_only_eligible_not_implemented",
                "implemented_in_repo": "false",
                "allowed_next_action": "await_explicit_goal07b_review_only_calculation_prototype",
                "depends_on": "goal07b0_risk_overlay_review_only_unlock_gate",
                "produces_artifacts": "",
                "primary_docs": "docs/risk/GOAL07B0_RISK_OVERLAY_REVIEW_ONLY_UNLOCK_GATE.md;docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
                "primary_scripts": "",
                "primary_outputs": "",
                "promotion_rule": "eligible_for_future_review_only_prototype_after_goal07b0_unlock_gate",
                "notes": "Eligibility only; GOAL-07B calculation is not implemented and no symbol-level risk rows or downstream outputs exist.",
            }
        )
    else:
        goal07b["status"] = GOAL07B_IMPLEMENTED_STATUS
        goal07b["implemented_in_repo"] = "true"
    for workflow_id in DOWNSTREAM_LOCKED_IDS:
        if workflow_id in by_id:
            if workflow_id == GOAL09_WORKFLOW_ID and goal090_valid_unlock_evidence(root):
                by_id[workflow_id].update(goal09_eligible_workflow_patch())
                continue
            by_id[workflow_id]["status"] = GOAL07B_LOCKED_STATUS
            by_id[workflow_id]["implemented_in_repo"] = "false"
            by_id[workflow_id]["allowed_next_action"] = "remain_locked"
    if "dqn_rl_mainline" in by_id:
        by_id["dqn_rl_mainline"]["status"] = "deleted_from_active_mainline"
        by_id["dqn_rl_mainline"]["implemented_in_repo"] = "false"
    if "v2_factor_research_upgrade" in by_id:
        by_id["v2_factor_research_upgrade"]["status"] = "planned_locked"
        by_id["v2_factor_research_upgrade"]["implemented_in_repo"] = "false"
    write_csv(path, rows, fields)


def _update_locked_capabilities(root: Path, review: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    if not path.exists():
        return
    payload = read_json(path)
    payload["goal07b0_risk_overlay_review_only_unlock_gate"] = "implemented_review_only" if review["status"] != BLOCKED else "future_review_only"
    payload["goal07b_risk_overlay_calculation"] = review["goal07b_target_status"]
    payload[GOAL09_WORKFLOW_ID] = GOAL09_ELIGIBLE_STATUS if goal090_valid_unlock_evidence(root) else False
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
    write_json(path, payload)


def _report_pass_or_warn(text: str, prefix: str) -> bool:
    return f"{prefix} {PASS}" in text or f"{prefix} {PASS_WITH_WARNINGS}" in text


def _forbidden_output_dirs_present(root: Path) -> list[str]:
    return [path for path in FORBIDDEN_OUTPUT_DIRS if (root / path).exists()]


def _risk_calculation_csv_outputs(root: Path, allow_goal07b_outputs: bool = False) -> list[str]:
    output_root = root / "outputs"
    if not output_root.exists():
        return []
    matches = []
    for path in output_root.rglob("*.csv"):
        rel = path.relative_to(root).as_posix()
        if allow_goal07b_outputs and rel in {
            "outputs/risk_overlay/goal07b_review_only_risk_overlay.csv",
            "outputs/diagnostics/goal07b_risk_overlay_diagnostics.csv",
        }:
            continue
        lowered = rel.lower()
        if "risk_overlay" in lowered or "risk_calculation" in lowered:
            matches.append(rel)
    return matches


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


def _goal07b_review_only_outputs_allowed(root: Path) -> bool:
    return _goal07b_review_only_outputs_valid(root) or _goal07b_review_only_manifest_non_actionable(root)


def _goal07b_review_only_manifest_non_actionable(root: Path) -> bool:
    manifest = _read_json(root / "outputs/audits/goal07b_risk_overlay_calculation_manifest.json")
    return (
        manifest.get("mode") == "review_only"
        and manifest.get("risk_overlay_output_path") == "outputs/risk_overlay/goal07b_review_only_risk_overlay.csv"
        and manifest.get("diagnostic_output_path") == "outputs/diagnostics/goal07b_risk_overlay_diagnostics.csv"
        and manifest.get("recommendation_generated") is False
        and manifest.get("position_generated") is False
        and manifest.get("dashboard_generated") is False
        and manifest.get("paper_live_trading_generated") is False
        and manifest.get("trading_generated") is False
        and manifest.get("production_generated") is False
        and manifest.get("backtest_generated") is False
        and manifest.get("factor_mining_generated") is False
        and manifest.get("dqn_rl_generated") is False
    )


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return read_json(path)
    except Exception:
        return {}

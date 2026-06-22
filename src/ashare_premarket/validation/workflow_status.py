from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.io import read_csv, write_csv, write_text

ALLOWED_STATUSES = {
    "implemented_active",
    "implemented_review_only",
    "implemented_design_only",
    "future_review_only",
    "future_design_only",
    "locked_future",
    "not_started",
    "deleted_from_active_mainline",
}

DOWNSTREAM_LOCKED_IDS = {
    "goal07b_risk_overlay_calculation",
    "position_band_recommendation",
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
}

REQUIRED_ACTIVE_IDS = {
    "project_operating_system",
    "universe_symbol_governance",
    "data_provider_source_health",
    "context_contract_layers",
    "pit_signal_store",
    "label_builder",
    "benchmark_contract",
    "feature_label_merge",
    "leakage_audit",
    "stage6a_repair_panel",
    "goal06a_baseline_scoring",
    "goal06b_supervised_baseline_gate",
    "validation_verification_diagnostics",
    "safety_gate",
    "adapter_audit",
}


def run_workflow_status_audit(root: Path) -> bool:
    status_path = root / "configs/project/workflow_status.csv"
    rows = read_csv(status_path) if status_path.exists() else []
    failures: list[str] = []
    warnings: list[str] = []

    if not status_path.exists():
        failures.append("workflow_status file is missing")
    if rows:
        failures.extend(_validate_rows(rows))
    else:
        failures.append("workflow_status file has no rows")

    readme = _read(root / "README.md")
    full_roadmap = _read(root / "docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md")
    active_doc = _read(root / "docs/architecture/ACTIVE_WORKFLOW_THROUGH_GOAL06B.md")

    if "## Active Workflow" not in readme or "```mermaid" not in readme:
        failures.append("README does not contain an Active Workflow Mermaid diagram")
    if "-." not in full_roadmap:
        failures.append("full roadmap does not contain dotted future arrows")
    active_mermaid = _first_mermaid_block(active_doc)
    if "GOAL-06C" in active_mermaid:
        failures.append("active workflow doc shows GOAL-06C in active workflow")
    if "Position-Band Recommendation" not in full_roadmap or "locked_future" not in full_roadmap:
        failures.append("full roadmap does not label position-band recommendation as locked_future")
    if "DQN/RL Optional Research Benchmark" not in full_roadmap or "deleted_from_active_mainline" not in full_roadmap:
        failures.append("full roadmap does not label DQN/RL as deleted_from_active_mainline")

    by_id = {row["workflow_id"]: row for row in rows}
    goal06c = by_id.get("goal06c_expanded_validation_ranking", {})
    goal06c5 = by_id.get("goal06c5_engineering_data_coverage_storage_panel_expansion", {})
    goal06c6 = by_id.get("goal06c6_source_backed_engineering_pilot_bundle", {})
    goal06c6a = by_id.get("goal06c6a_scoped_finance_network_failure_taxonomy", {})
    goal06c7 = by_id.get("goal06c7_provider_ladder_browser_assisted_engineering_data_base_expansion", {})
    goal06c_status = goal06c.get("status")
    goal06c5_status = goal06c5.get("status")
    goal06c6_status = goal06c6.get("status")
    goal06c6a_status = goal06c6a.get("status")
    goal06c7_status = goal06c7.get("status")
    if goal06c_status not in {"future_review_only", "implemented_review_only"}:
        failures.append("GOAL-06C block must be future_review_only or implemented_review_only")
    if goal06c_status == "implemented_review_only":
        readiness = _read(root / "outputs/audits/stage6c_readiness_report.md")
        if "GOAL-06C Expanded Validation Readiness: PASS" not in readiness:
            failures.append("GOAL-06C is implemented_review_only without a PASS/PASS_WITH_WARNINGS readiness report")
        if "implemented_review_only" not in full_roadmap:
            failures.append("full roadmap does not label GOAL-06C as implemented_review_only")
    elif "next_allowed_goal_review_only" not in goal06c.get("allowed_next_action", ""):
        failures.append("next allowed goal is not clearly GOAL-06C review-only expanded validation")
    if goal06c5_status != "implemented_review_only":
        failures.append("GOAL-06C.5 must be implemented_review_only")
    else:
        readiness = _read(root / "outputs/audits/engineering_panel_readiness_report.md")
        if "Engineering Panel Readiness: PASS_WITH_WARNINGS" not in readiness and "Engineering Panel Readiness: PASS" not in readiness:
            failures.append("GOAL-06C.5 is implemented_review_only without a PASS/PASS_WITH_WARNINGS engineering panel readiness report")
        if "GOAL-06D allowed to proceed: false" not in readiness:
            failures.append("GOAL-06C.5 must keep GOAL-06D blocked until engineering_pilot")
        if "GOAL-06C.5" not in full_roadmap:
            failures.append("full roadmap does not include GOAL-06C.5")
    if goal06c6_status != "implemented_review_only":
        failures.append("GOAL-06C.6 must be implemented_review_only")
    else:
        readiness = _read(root / "outputs/audits/goal06c6_readiness_report.md")
        if "GOAL-06C.6 Source-Backed Engineering Pilot Bundle Readiness:" not in readiness:
            failures.append("GOAL-06C.6 is implemented_review_only without a readiness report")
        if "Default GOAL-06C.6 AKShare provider ingestion used no browser automation" not in readiness:
            failures.append("GOAL-06C.6 readiness report must state the default AKShare path did not use browser automation")
        if "GOAL-06C.6" not in full_roadmap:
            failures.append("full roadmap does not include GOAL-06C.6")
    if goal06c6a_status != "implemented_review_only":
        failures.append("GOAL-06C.6A must be implemented_review_only")
    else:
        summary = _read(root / "outputs/audits/provider_failure_summary.md")
        network_report = _read(root / "outputs/audits/goal06c6_network_isolation_report.md")
        taxonomy_report = _read(root / "outputs/audits/goal06c6_failure_taxonomy_report.md")
        if "GOAL-06C.6A Network Isolation and Failure Taxonomy Readiness:" not in summary:
            failures.append("GOAL-06C.6A is implemented_review_only without a provider failure summary")
        if "System proxy inheritance allowed: `false`" not in network_report:
            failures.append("GOAL-06C.6A network report must prove proxy inheritance is not allowed")
        if "NETWORK_ERROR" in taxonomy_report:
            failures.append("GOAL-06C.6A taxonomy report must not use generic NETWORK_ERROR")
        if "GOAL-06C.6A" not in full_roadmap:
            failures.append("full roadmap does not include GOAL-06C.6A")
    if goal06c7_status != "implemented_review_only":
        failures.append("GOAL-06C.7 must be implemented_review_only")
    else:
        readiness = _read(root / "outputs/audits/goal06c7_readiness_report.md")
        browser_audit = _read(root / "outputs/audits/browser_assisted_provider_audit.md")
        cleanliness = _read(root / "outputs/audits/workflow_cleanliness_audit.md")
        if "GOAL-06C.7 Engineering Data Base Expansion Readiness:" not in readiness:
            failures.append("GOAL-06C.7 is implemented_review_only without a readiness report")
        if "Browser assisted project default: `false`" not in browser_audit:
            failures.append("GOAL-06C.7 browser audit must prove browser-assisted provider is disabled by default")
        if "Workflow Cleanliness Audit:" not in cleanliness:
            failures.append("GOAL-06C.7 workflow cleanliness audit is missing")
        if "GOAL-06C.7" not in full_roadmap:
            failures.append("full roadmap does not include GOAL-06C.7")
    if by_id.get("goal06d_model_comparison_calibration", {}).get("status") != "future_review_only":
        failures.append("GOAL-06D must remain future_review_only")
    if "engineering_pilot" not in by_id.get("goal06d_model_comparison_calibration", {}).get("allowed_next_action", ""):
        failures.append("GOAL-06D must wait for GOAL-06C.7 engineering_pilot readiness")
    if by_id.get("goal07a_risk_overlay_design", {}).get("status") != "future_design_only":
        failures.append("GOAL-07A must remain future_design_only")

    status = "PASS" if not failures else "BLOCKED"
    table_rows = [_status_table_row(row) for row in rows]
    write_csv(
        root / "outputs/audits/workflow_status_table.csv",
        table_rows,
        [
            "workflow_id",
            "display_name",
            "status",
            "diagram_edge_type",
            "can_promote_now",
            "promotion_blocker",
            "next_required_goal",
        ],
    )
    write_text(
        root / "outputs/audits/workflow_status_audit.md",
        "\n".join(
            [
                "# Workflow Status Audit",
                "",
                f"Workflow Status Audit: {status}",
                "",
                f"Rows checked: `{len(rows)}`",
                f"Failures: `{len(failures)}`",
                f"Warnings: `{len(warnings)}`",
                "",
                f"GOAL-06C status: `{goal06c_status or 'missing'}`.",
                f"GOAL-06C.5 status: `{goal06c5_status or 'missing'}`.",
                f"GOAL-06C.6 status: `{goal06c6_status or 'missing'}`.",
                f"GOAL-06C.6A status: `{goal06c6a_status or 'missing'}`.",
                f"GOAL-06C.7 status: `{goal06c7_status or 'missing'}`.",
                "Next allowed goal after GOAL-06C.7: `GOAL-06D Model Comparison and Calibration` only after provider-ladder source-backed engineering_pilot readiness; currently blocked unless the readiness report says otherwise.",
                "GOAL-06C and later are not represented as `implemented_active`.",
                "Risk overlay calculation, recommendation, dashboard, paper/live trading, production, and DQN/RL remain locked or deleted from active mainline.",
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
    write_text(
        root / "outputs/audits/workflow_diagram_update_report.md",
        "\n".join(
            [
                "# Workflow Diagram Update Report",
                "",
                "Status: `PASS`" if status == "PASS" else "Status: `BLOCKED`",
                "",
                "Updated diagrams are governed by `configs/project/workflow_status.csv`.",
                "Solid arrows represent `implemented_active` workflow through GOAL-06B.",
                "Dotted arrows represent future, design-only, locked, not-started, or deleted-from-mainline workflow blocks.",
                "Workflow promotion requires a readiness report, passing validation/verification, status-file update, diagram update, and downstream-lock review.",
                "",
            ]
        ),
    )
    return status == "PASS"


def _validate_rows(rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    by_id = {row["workflow_id"]: row for row in rows}
    missing_active = sorted(REQUIRED_ACTIVE_IDS - set(by_id))
    if missing_active:
        failures.append(f"missing implemented active rows: {missing_active}")
    for row in rows:
        workflow_id = row["workflow_id"]
        status = row["status"]
        if status not in ALLOWED_STATUSES:
            failures.append(f"{workflow_id} has invalid status `{status}`")
        if workflow_id in REQUIRED_ACTIVE_IDS and status != "implemented_active":
            failures.append(f"{workflow_id} must be implemented_active")
        if workflow_id.startswith("goal06c") or workflow_id.startswith("goal06d"):
            if status == "implemented_active":
                failures.append(f"{workflow_id} is incorrectly implemented_active")
        if workflow_id in DOWNSTREAM_LOCKED_IDS and status != "locked_future":
            failures.append(f"{workflow_id} must remain locked_future")
        if workflow_id == "dqn_rl_mainline" and status != "deleted_from_active_mainline":
            failures.append("dqn_rl_mainline must remain deleted_from_active_mainline")
        if row["implemented_in_repo"] == "true" and status not in {"implemented_active", "implemented_review_only", "implemented_design_only"}:
            failures.append(f"{workflow_id} is marked implemented but has future/deleted status")
    return failures


def _status_table_row(row: dict[str, str]) -> dict[str, object]:
    status = row["status"]
    if status == "implemented_active":
        edge_type = "solid"
        can_promote = False
        blocker = "already implemented active"
    elif status == "implemented_review_only":
        edge_type = "dotted_review_only"
        can_promote = False
        blocker = "already implemented review-only"
    elif status == "deleted_from_active_mainline":
        edge_type = "dotted_side_note"
        can_promote = False
        blocker = "deleted from active mainline; explicit optional research goal required"
    else:
        edge_type = "dotted"
        can_promote = False
        blocker = "requires readiness report PASS/PASS_WITH_WARNINGS plus validation, verification, workflow_status, docs, and PROJECT_STATE updates"
    if row["workflow_id"] == "goal06c_expanded_validation_ranking":
        next_goal = "GOAL-06C.5 engineering data foundation"
    elif row["workflow_id"] == "goal06c5_engineering_data_coverage_storage_panel_expansion":
        next_goal = "GOAL-06C.6 source-backed engineering pilot bundle gate"
    elif row["workflow_id"] == "goal06c6_source_backed_engineering_pilot_bundle":
        next_goal = "GOAL-06C.6A scoped failure taxonomy then GOAL-06D blocked until engineering_pilot"
    elif row["workflow_id"] == "goal06c6a_scoped_finance_network_failure_taxonomy":
        next_goal = "GOAL-06C.7 provider ladder engineering data base expansion"
    elif row["workflow_id"] == "goal06c7_provider_ladder_browser_assisted_engineering_data_base_expansion":
        next_goal = "GOAL-06D blocked until provider-ladder engineering_pilot"
    else:
        next_goal = row["stage_or_goal"]
    return {
        "workflow_id": row["workflow_id"],
        "display_name": row["display_name"],
        "status": status,
        "diagram_edge_type": edge_type,
        "can_promote_now": can_promote,
        "promotion_blocker": blocker,
        "next_required_goal": next_goal,
    }


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _first_mermaid_block(text: str) -> str:
    marker = "```mermaid"
    start = text.find(marker)
    if start == -1:
        return ""
    start += len(marker)
    end = text.find("```", start)
    if end == -1:
        return text[start:]
    return text[start:end]

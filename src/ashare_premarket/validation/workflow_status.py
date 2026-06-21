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
    if by_id.get("goal06c_expanded_validation_ranking", {}).get("status") != "future_review_only":
        failures.append("next allowed GOAL-06C block is not future_review_only")
    if "next_allowed_goal_review_only" not in by_id.get("goal06c_expanded_validation_ranking", {}).get("allowed_next_action", ""):
        failures.append("next allowed goal is not clearly GOAL-06C review-only expanded validation")

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
                "Next allowed goal: `GOAL-06C Expanded Validation and Ranking Baseline` as `future_review_only`.",
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
    elif status == "deleted_from_active_mainline":
        edge_type = "dotted_side_note"
        can_promote = False
        blocker = "deleted from active mainline; explicit optional research goal required"
    else:
        edge_type = "dotted"
        can_promote = False
        blocker = "requires readiness report PASS/PASS_WITH_WARNINGS plus validation, verification, workflow_status, docs, and PROJECT_STATE updates"
    next_goal = "GOAL-06C review-only expanded validation" if row["workflow_id"] == "goal06c_expanded_validation_ranking" else row["stage_or_goal"]
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

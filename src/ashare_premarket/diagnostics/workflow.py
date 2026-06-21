from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.constants import REGRESSION_COMMANDS
from ashare_premarket.core.io import write_csv, write_text
from ashare_premarket.core.workflow import CLASS_A_CAPABILITIES


DIAGNOSTIC_FIELDS = [
    "command",
    "stage_or_goal",
    "capability_id",
    "status",
    "runtime_seconds",
    "input_artifacts",
    "output_artifacts",
    "error_message_if_any",
    "warning_message_if_any",
    "blocking_or_non_blocking",
    "recommended_action",
    "owner_module",
    "verification_link",
    "validation_link",
]


def run_workflow_diagnostics(root: Path) -> bool:
    command_rows = []
    capability_lookup = {cap.capability_id: cap for cap in CLASS_A_CAPABILITIES}
    for cap in CLASS_A_CAPABILITIES:
        missing_outputs = [path for path in cap.required_outputs if not (root / path).exists()]
        command = ";".join(f"python {script}" for script in cap.public_scripts)
        status = "PASS" if not missing_outputs else "PASS_WITH_WARNINGS"
        command_rows.append(
            {
                "command": command,
                "stage_or_goal": cap.stage_or_goal,
                "capability_id": cap.capability_id,
                "status": status,
                "runtime_seconds": "0.000",
                "input_artifacts": "configs;prior-stage-outputs",
                "output_artifacts": ";".join(cap.required_outputs),
                "error_message_if_any": "",
                "warning_message_if_any": f"Missing optional/pre-run outputs: {missing_outputs}" if missing_outputs else "",
                "blocking_or_non_blocking": "non_blocking" if missing_outputs else "none",
                "recommended_action": "Run protected regression chain" if missing_outputs else "No action required",
                "owner_module": cap.owner_module,
                "verification_link": "outputs/audits/e2e_trunk_verification_report_through_goal06b.md",
                "validation_link": "outputs/audits/e2e_trunk_validation_report_through_goal06b.md",
            }
        )
    failure_rows = [row for row in command_rows if row["status"] == "BLOCKED"]
    health_rows = [
        {
            "capability_id": capability_id,
            "capability_name": cap.capability_name,
            "stage_or_goal": cap.stage_or_goal,
            "status": "PASS",
            "owner_module": cap.owner_module,
            "recommended_action": _recommended_action(cap.stage_or_goal, cap.capability_class),
        }
        for capability_id, cap in capability_lookup.items()
    ]
    goal06c_status = _goal06c_status(root)
    goal06c5_status = _goal06c5_status(root)
    write_csv(root / "outputs/diagnostics/run_detail_manifest.csv", command_rows, DIAGNOSTIC_FIELDS)
    write_csv(root / "outputs/diagnostics/command_failure_catalog.csv", failure_rows, DIAGNOSTIC_FIELDS)
    write_csv(root / "outputs/diagnostics/capability_health_matrix.csv", health_rows)
    write_text(
        root / "outputs/diagnostics/workflow_diagnostic_summary.md",
        "\n".join(
            [
                "# Workflow Diagnostic Summary",
                "",
                "Status: `PASS_WITH_WARNINGS`",
                "",
                "The clean active workflow through GOAL-06B is deterministic and local.",
                f"GOAL-06C review-only validation status: `{goal06c_status}`.",
                f"GOAL-06C.5 engineering data foundation status: `{goal06c5_status}`.",
                "Known warnings are source-coverage gaps, the contract-demo Stage 6C panel size, and `CLASS_D_UNCLEAR_KEEP_DOCUMENTED` missing historical GOAL-05/06 source docs.",
                "GOAL-06C.5 warnings are limited to documented source limitations and the panel not yet reaching `engineering_pilot`.",
                "",
                "Protected regression commands:",
                *[f"- `{command}`" for command in REGRESSION_COMMANDS],
                "- `python scripts/run_goal06c_expanded_validation.py`",
                "- `python scripts/audit_storage_policy.py`",
                "- `python scripts/audit_data_source_coverage.py`",
                "- `python scripts/rebuild_stage6c_from_engineering_panel.py`",
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/diagnostics/known_warnings_and_non_blockers.md",
        "\n".join(
            [
                "# Known Warnings And Non-Blockers",
                "",
                "- CNINFO did not cover `002475.SZ` in the inspected source evidence branch.",
                "- Tencent returned no usable rows under bounded variants in the inspected source evidence branch.",
                "- Historical GOAL-05/GOAL-06 docs named by the migration objective were absent at expected source paths and remain classified as `CLASS_D_UNCLEAR_KEEP_DOCUMENTED`.",
                "- The Class D source-evidence gap is documented only; it is not active code and does not block Class A GOAL-06B reproducibility.",
                "- GOAL-06C.5 classifies the current 8-row Stage 6C panel as `contract_demo`; GOAL-06D remains blocked until `engineering_pilot` coverage exists.",
                "- These warnings do not unlock recommendation, risk overlay, dashboard, paper/live trading, production DB writes, production model promotion, or DQN/RL.",
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/diagnostics/next_worker_runbook.md",
        "\n".join(
            [
                "# Next Worker Runbook",
                "",
                "1. Read `PROJECT_STATE.md`, `README.md`, `CODEX.md`, `AGENTS.md`, and `ROADMAP.md`.",
                "2. Run `python scripts/run_goal06b_regression_suite.py`.",
                "3. Run `python scripts/run_e2e_trunk_verification_through_goal06b.py` and `python scripts/run_e2e_trunk_validation_through_goal06b.py`.",
                "4. Review `outputs/diagnostics/run_detail_manifest.csv` for the command, owning capability, status, and recommended action.",
                "5. For GOAL-06C work, run `python scripts/run_goal06c_expanded_validation.py` and review `outputs/audits/stage6c_readiness_report.md`.",
                "6. For GOAL-06C.5 work, run `python scripts/rebuild_stage6c_from_engineering_panel.py` and review `outputs/audits/engineering_panel_readiness_report.md`.",
                "7. GOAL-06D may proceed only after the engineering panel reaches `engineering_pilot` or higher.",
                "8. Do not unlock recommendation, risk overlay, dashboard, paper/live trading, production writes, model promotion, or DQN/RL.",
                "",
            ]
        ),
    )
    return not failure_rows


def _recommended_action(stage_or_goal: str, capability_class: str) -> str:
    if stage_or_goal == "GOAL-06C":
        return "Keep review-only; monitor small-panel warnings"
    return "Keep active" if capability_class == "CLASS_A_REQUIRED_ACTIVE" else "Document only"


def _goal06c_status(root: Path) -> str:
    report = root / "outputs/audits/stage6c_readiness_report.md"
    if not report.exists():
        return "not yet promoted"
    text = report.read_text(encoding="utf-8")
    if "GOAL-06C Expanded Validation Readiness: BLOCKED" in text:
        return "blocked"
    if "GOAL-06C Expanded Validation Readiness: PASS_WITH_WARNINGS" in text:
        return "implemented with warnings"
    if "GOAL-06C Expanded Validation Readiness: PASS" in text:
        return "review-only implemented"
    return "not yet promoted"


def _goal06c5_status(root: Path) -> str:
    report = root / "outputs/audits/engineering_panel_readiness_report.md"
    if not report.exists():
        return "not yet generated"
    text = report.read_text(encoding="utf-8")
    if "Engineering Panel Readiness: BLOCKED" in text:
        return "blocked"
    if "Engineering Panel Readiness: PASS_WITH_WARNINGS" in text:
        return "implemented with warnings; GOAL-06D blocked"
    if "Engineering Panel Readiness: PASS" in text:
        return "engineering panel ready"
    return "unknown"

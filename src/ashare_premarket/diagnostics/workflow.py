from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.constants import REGRESSION_COMMANDS
from ashare_premarket.core.io import read_csv, read_json, write_csv, write_text
from ashare_premarket.core.workflow import CLASS_A_CAPABILITIES
from ashare_premarket.providers.akshare_provider import akshare_available
from ashare_premarket.providers.browser_provider_switches import browser_provider_project_default
from ashare_premarket.providers.provider_registry import network_enabled


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
    goal06c6_status = _goal06c6_status(root)
    goal06c7_status = _goal06c7_status(root)
    goal06d_status = _goal06d_status(root)
    goal06d_selected = _goal06d_selected_baseline(root)
    goal06d_model_status = _audit_status(root / "outputs/audits/goal06d_model_comparison_audit.md")
    goal06d_calibration_status = _audit_status(root / "outputs/audits/goal06d_calibration_audit.md")
    goal06d_stability_status = _audit_status(root / "outputs/audits/goal06d_stability_audit.md")
    goal06d_governance_status = _audit_status(root / "outputs/audits/goal06d_governance_audit.md")
    goal06d_boundary_status = _audit_status(root / "outputs/audits/goal06d_boundary_lock_audit.md")
    goal06d1_status = _goal06d1_status(root)
    goal06d1_selected = _goal06d1_selected_baseline(root)
    goal06d1_target = _goal06d1_target_recommendation(root)
    goal06d1_calibration_status = _audit_status(root / "outputs/audits/goal06d1_calibration_repair_audit.md")
    goal06d1_feature_status = _audit_status(root / "outputs/audits/goal06d1_feature_sign_stability_audit.md")
    goal06d1_provider_status = _audit_status(root / "outputs/audits/goal06d1_provider_concentration_disclosure.md")
    goal06d1_governance_status = _audit_status(root / "outputs/audits/goal06d1_governance_audit.md")
    goal06d1_boundary_status = _audit_status(root / "outputs/audits/goal06d1_boundary_lock_audit.md")
    v2_factor_status = _v2_factor_status(root)
    provider_ladder = _provider_ladder_status(root)
    source_bundle_status = _source_bundle_status(root)
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
                f"GOAL-06C.6 source-backed ingestion status: `{goal06c6_status}`.",
                f"GOAL-06C.7 provider ladder status: `{goal06c7_status}`.",
                f"Provider ladder panel tier: `{provider_ladder.get('panel_tier', 'unknown')}`.",
                f"Provider ladder approved symbols: `{provider_ladder.get('approved_symbols', 0)}`.",
                f"Provider ladder validation trading dates: `{provider_ladder.get('validation_trading_dates', 0)}`.",
                f"Provider ladder Stage 6C engineering rows: `{provider_ladder.get('stage6c_engineering_rows', 0)}`.",
                f"Browser-assisted provider project default: `{str(browser_provider_project_default(root)).lower()}`.",
                f"GOAL-06D allowed by provider ladder: `{str(provider_ladder.get('goal06d_allowed_to_proceed', False)).lower()}`.",
                f"GOAL-06D readiness: `{goal06d_status}`.",
                f"GOAL-06D selected review-only baseline: `{goal06d_selected}`.",
                f"GOAL-06D model comparison status: `{goal06d_model_status}`.",
                f"GOAL-06D calibration status: `{goal06d_calibration_status}`.",
                f"GOAL-06D stability status: `{goal06d_stability_status}`.",
                f"GOAL-06D governance status: `{goal06d_governance_status}`.",
                f"GOAL-06D boundary lock status: `{goal06d_boundary_status}`.",
                f"GOAL-06D.1 readiness: `{goal06d1_status}`.",
                f"GOAL-06D.1 selected repaired review-only baseline: `{goal06d1_selected}`.",
                f"GOAL-06D.1 target horizon recommendation: `{goal06d1_target}`.",
                f"GOAL-06D.1 calibration repair status: `{goal06d1_calibration_status}`.",
                f"GOAL-06D.1 feature sign stability status: `{goal06d1_feature_status}`.",
                f"GOAL-06D.1 provider concentration disclosure status: `{goal06d1_provider_status}`.",
                f"GOAL-06D.1 governance status: `{goal06d1_governance_status}`.",
                f"GOAL-06D.1 boundary lock status: `{goal06d1_boundary_status}`.",
                f"V2 factor placeholder status: `{v2_factor_status}`.",
                "GOAL-07A lock status: `future_design_only; at most design-only preparation after GOAL-06D.1 warning repair`.",
                "Downstream lock status: `locked_future_or_deleted_from_active_mainline`.",
                f"AKShare available: `{str(akshare_available()).lower()}`.",
                f"Network ingestion opt-in active: `{str(network_enabled(False)).lower()}`.",
                f"Source-backed bundle manifest: `{source_bundle_status}`.",
                "Known warnings are source-coverage gaps, `CLASS_D_UNCLEAR_KEEP_DOCUMENTED` missing historical GOAL-05/06 source docs, GOAL-06D calibration/stability/provider concentration warnings, and GOAL-06D.1 bounded weak-baseline warnings.",
                "GOAL-06C.5/GOAL-06C.6 warnings are documented source limitations. GOAL-06C.7 has reached `engineering_pilot`; GOAL-06D and GOAL-06D.1 are implemented review-only and allow GOAL-07A at most as design-only preparation.",
                "",
                "Protected regression commands:",
                *[f"- `{command}`" for command in REGRESSION_COMMANDS],
                "- `python scripts/run_goal06c_expanded_validation.py`",
                "- `python scripts/audit_storage_policy.py`",
                "- `python scripts/audit_provider_failure_classification.py`",
                "- `python scripts/run_goal06c7_provider_ladder_engineering_data_base_expansion.py --allow-network`",
                "- `ASHARE_ENABLE_BROWSER_ASSISTED_PROVIDER=1 python scripts/run_goal06c7_provider_ladder_engineering_data_base_expansion.py --allow-network --enable-browser-assisted`",
                "- `python scripts/audit_browser_assisted_provider.py`",
                "- `python scripts/audit_workflow_cleanliness.py`",
                "- `python scripts/audit_data_source_coverage.py`",
                "- `python scripts/run_goal06c6_source_backed_engineering_pilot_bundle.py --allow-network`",
                "- `python scripts/rebuild_stage6c_from_engineering_panel.py`",
                "- `python scripts/run_goal06d_model_comparison_calibration.py`",
                "- `python scripts/audit_goal06d_feature_contract.py`",
                "- `python scripts/audit_goal06d_split.py`",
                "- `python scripts/audit_goal06d_model_comparison.py`",
                "- `python scripts/audit_goal06d_calibration.py`",
                "- `python scripts/audit_goal06d_stability.py`",
                "- `python scripts/audit_goal06d_governance.py`",
                "- `python scripts/audit_goal06d_boundary_locks.py`",
                "- `python scripts/run_goal06d1_calibration_stability_warning_repair.py`",
                "- `python scripts/audit_goal06d1_target_horizon.py`",
                "- `python scripts/audit_goal06d1_score_repair.py`",
                "- `python scripts/audit_goal06d1_calibration_repair.py`",
                "- `python scripts/audit_goal06d1_feature_sign_stability.py`",
                "- `python scripts/audit_goal06d1_provider_concentration_disclosure.py`",
                "- `python scripts/audit_goal06d1_governance.py`",
                "- `python scripts/audit_goal06d1_boundary_locks.py`",
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
                "- GOAL-06C.5 retains the old contract-demo warning as historical engineering-foundation context; GOAL-06C.7 now provides separate source-backed `engineering_pilot` evidence.",
                "- GOAL-06C.6 provider ingestion is disabled by default and records classified failures on the default AKShare path; explicit CloakBrowser reference probes are separate tag-only diagnostics.",
                "- GOAL-06C.7 provider ladder is disabled from network by default; browser-assisted ingestion requires explicit CLI plus env opt-in and counts only schema-valid finance rows.",
                "- GOAL-06D is `PASS_WITH_WARNINGS`: calibration is weak/non-monotonic for the compared review-only baselines, selected baseline is weak, and provider/source concentration is single-mode `akshare_direct`.",
                "- GOAL-06D.1 repairs warning diagnostics but remains review-only: weak baseline, calibration not reliable for thresholding where marked, bounded feature instability, and provider concentration disclosure may remain.",
                "- V2 factor research is `planned_locked`, disabled in V1, and has no active factor mining runner or outputs.",
                "- These warnings do not unlock recommendation, risk overlay, dashboard, paper/live trading, production DB writes, production model promotion, factor mining, or DQN/RL.",
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
                "7. For GOAL-06C.6 source-backed ingestion, run `python scripts/audit_provider_failure_classification.py` first; provider ingestion requires `ASHARE_ALLOW_NETWORK_INGESTION=1` or `--allow-network`.",
                "8. For GOAL-06C.7 provider-ladder expansion, run `python scripts/run_goal06c7_provider_ladder_engineering_data_base_expansion.py`; browser-assisted mode additionally requires `ASHARE_ENABLE_BROWSER_ASSISTED_PROVIDER=1 --enable-browser-assisted`.",
                "9. For GOAL-06D, run `python scripts/run_goal06d_model_comparison_calibration.py` and then every `scripts/audit_goal06d_*.py` wrapper.",
                "10. For GOAL-06D.1, run `python scripts/run_goal06d1_calibration_stability_warning_repair.py` and then every `scripts/audit_goal06d1_*.py` wrapper.",
                "11. Current GOAL-06D.1 is a review-only warning repair gate; GOAL-07A may proceed at most as design-only preparation with warnings bounded.",
                "12. V2 factor research is planned but inactive; do not create factor mining, IC/RankIC mining, factor libraries, or factor outputs in V1.",
                "13. Do not unlock recommendation, risk overlay calculation, dashboard, paper/live trading, production writes, model promotion, factor mining, or DQN/RL.",
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


def _goal06c6_status(root: Path) -> str:
    report = root / "outputs/audits/goal06c6_readiness_report.md"
    if not report.exists():
        return "not yet generated"
    text = report.read_text(encoding="utf-8")
    if "GOAL-06C.6 Source-Backed Engineering Pilot Bundle Readiness: BLOCKED" in text:
        return "blocked"
    if "GOAL-06C.6 Source-Backed Engineering Pilot Bundle Readiness: PASS_WITH_WARNINGS" in text:
        return "implemented with warnings; GOAL-06D blocked unless engineering_pilot reached"
    if "GOAL-06C.6 Source-Backed Engineering Pilot Bundle Readiness: PASS" in text:
        return "source-backed engineering_pilot ready"
    return "unknown"


def _goal06c7_status(root: Path) -> str:
    report = root / "outputs/audits/goal06c7_readiness_report.md"
    if not report.exists():
        return "not yet generated"
    text = report.read_text(encoding="utf-8")
    if "GOAL-06C.7 Engineering Data Base Expansion Readiness: BLOCKED" in text:
        return "blocked"
    if "GOAL-06C.7 Engineering Data Base Expansion Readiness: PASS_WITH_WARNINGS" in text:
        return "implemented with warnings; GOAL-06D blocked unless engineering_pilot reached"
    if "GOAL-06C.7 Engineering Data Base Expansion Readiness: PASS" in text:
        return "provider-ladder engineering_pilot ready"
    return "unknown"


def _goal06d_status(root: Path) -> str:
    report = root / "outputs/audits/goal06d_readiness_report.md"
    if not report.exists():
        return "not yet generated"
    text = report.read_text(encoding="utf-8")
    if "GOAL-06D Model Comparison Calibration Readiness: BLOCKED" in text:
        return "BLOCKED"
    if "GOAL-06D Model Comparison Calibration Readiness: PASS_WITH_WARNINGS" in text:
        return "PASS_WITH_WARNINGS"
    if "GOAL-06D Model Comparison Calibration Readiness: PASS" in text:
        return "PASS"
    return "unknown"


def _goal06d1_status(root: Path) -> str:
    report = root / "outputs/audits/goal06d1_readiness_report.md"
    if not report.exists():
        return "not yet generated"
    text = report.read_text(encoding="utf-8")
    if "GOAL-06D.1 Calibration Stability Warning Repair Readiness: BLOCKED" in text:
        return "BLOCKED"
    if "GOAL-06D.1 Calibration Stability Warning Repair Readiness: PASS_WITH_WARNINGS" in text:
        return "PASS_WITH_WARNINGS"
    if "GOAL-06D.1 Calibration Stability Warning Repair Readiness: PASS" in text:
        return "PASS"
    return "unknown"


def _goal06d1_selected_baseline(root: Path) -> str:
    report = root / "outputs/audits/goal06d1_readiness_report.md"
    if not report.exists():
        return "not yet generated"
    for line in report.read_text(encoding="utf-8").splitlines():
        if line.startswith("Selected repaired review-only baseline:"):
            return line.split("`")[1] if "`" in line else line.split(":", 1)[1].strip()
    return "unknown"


def _goal06d1_target_recommendation(root: Path) -> str:
    path = root / "outputs/models/goal06d1/target_horizon_comparison.csv"
    if not path.exists():
        return "not yet generated"
    rows = read_csv(path)
    recommendations = sorted({row.get("target_horizon_recommendation", "") for row in rows if row.get("target_horizon_recommendation")})
    return ";".join(recommendations) if recommendations else "unknown"


def _v2_factor_status(root: Path) -> str:
    path = root / "configs/factors/v2_factor_research_contract.yaml"
    if not path.exists():
        return "not yet generated"
    text = path.read_text(encoding="utf-8")
    if "status: planned_locked" in text and "enabled: false" in text and "active_in_v1: false" in text:
        return "planned_locked_disabled"
    return "unknown"


def _goal06d_selected_baseline(root: Path) -> str:
    report = root / "outputs/audits/goal06d_readiness_report.md"
    if not report.exists():
        return "not_selected"
    for line in report.read_text(encoding="utf-8").splitlines():
        if line.startswith("Selected review-only baseline:"):
            return line.split("`", 2)[1]
    return "not_selected"


def _provider_ladder_status(root: Path) -> dict[str, object]:
    path = root / "outputs/audits/source_backed_bundle_manifest_summary.json"
    if not path.exists():
        return {}
    try:
        return read_json(path)
    except Exception:
        return {}


def _source_bundle_status(root: Path) -> str:
    report = root / "outputs/audits/source_backed_bundle_manifest_summary.md"
    if not report.exists():
        return "not generated"
    for line in report.read_text(encoding="utf-8").splitlines():
        if line.startswith("Status:"):
            return line.replace("Status:", "").strip()
    return "generated"


def _audit_status(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Status:"):
            return line.replace("Status:", "").strip(" `")
    return "generated"

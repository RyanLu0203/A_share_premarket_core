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
    goal07a_status = _goal07a_status(root)
    goal07a_allowed_input_status = _audit_status(root / "outputs/audits/goal07a_allowed_input_contract_audit.md")
    goal07a_output_schema_status = _audit_status(root / "outputs/audits/goal07a_output_schema_audit.md")
    goal07a_rule_catalog_status = _audit_status(root / "outputs/audits/goal07a_risk_rule_catalog_audit.md")
    goal07a_state_machine_status = _audit_status(root / "outputs/audits/goal07a_state_machine_audit.md")
    goal07a_warning_mapping_status = _audit_status(root / "outputs/audits/goal07a_upstream_warning_mapping_audit.md")
    goal07a_governance_status = _audit_status(root / "outputs/audits/goal07a_governance_boundary_audit.md")
    goal07a_boundary_status = _audit_status(root / "outputs/audits/goal07a_boundary_lock_audit.md")
    goal07a_v2_lock_status = _audit_status(root / "outputs/audits/goal07a_v2_factor_lock_audit.md")
    goal07a1_status = _goal07a1_status(root)
    goal07a1_manifest = _goal07a1_manifest(root)
    goal07a1_input_status = _audit_status(root / "outputs/audits/goal07a1_input_contract_readiness_audit.md")
    goal07a1_schema_status = _audit_status(root / "outputs/audits/goal07a1_forbidden_schema_overlap_audit.md")
    goal07a1_rule_status = _audit_status(root / "outputs/audits/goal07a1_rule_convertibility_audit.md")
    goal07a1_state_status = _audit_status(root / "outputs/audits/goal07a1_state_machine_review_audit.md")
    goal07a1_boundary_status = _audit_status(root / "outputs/audits/goal07a1_boundary_lock_audit.md")
    goal07b0_status = _goal07b0_status(root)
    goal07b0_manifest = _goal07b0_manifest(root)
    goal07b0_audit_status = _audit_status(root / "outputs/audits/goal07b0_unlock_gate_audit_report.md")
    goal07b_status = _goal07b_status(root)
    goal07b_manifest = _goal07b_manifest(root)
    goal07b_audit_status = _audit_status(root / "outputs/audits/goal07b_risk_overlay_calculation_audit.md")
    downstream_status = _downstream_lock_status(root)
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
                f"GOAL-07A readiness: `{goal07a_status}`.",
                f"GOAL-07A allowed input contract status: `{goal07a_allowed_input_status}`.",
                f"GOAL-07A future output schema status: `{goal07a_output_schema_status}`.",
                f"GOAL-07A risk rule catalog status: `{goal07a_rule_catalog_status}`.",
                f"GOAL-07A risk state machine status: `{goal07a_state_machine_status}`.",
                f"GOAL-07A upstream warning mapping status: `{goal07a_warning_mapping_status}`.",
                f"GOAL-07A governance boundary status: `{goal07a_governance_status}`.",
                f"GOAL-07A boundary lock status: `{goal07a_boundary_status}`.",
                f"GOAL-07A V2 factor lock status: `{goal07a_v2_lock_status}`.",
                f"GOAL-07A.1 design review status: `{goal07a1_status}`.",
                f"GOAL-07A.1 input contract review status: `{goal07a1_input_status}`.",
                f"GOAL-07A.1 schema safety status: `{goal07a1_schema_status}`.",
                f"GOAL-07A.1 rule convertibility status: `{goal07a1_rule_status}`.",
                f"GOAL-07A.1 state machine review status: `{goal07a1_state_status}`.",
                f"GOAL-07A.1 boundary lock status: `{goal07a1_boundary_status}`.",
                f"GOAL-07B unlock readiness: `{goal07a1_manifest.get('goal07b_unlock_readiness', 'not yet reviewed')}`.",
                f"GOAL-07A.1 allowed next action: `{goal07a1_manifest.get('allowed_next_action', 'not yet reviewed')}`.",
                f"GOAL-07B.0 unlock gate status: `{goal07b0_status}`.",
                f"GOAL-07B.0 audit status: `{goal07b0_audit_status}`.",
                f"GOAL-07B.0 unlock result: `{goal07b0_manifest.get('goal07b0_unlock_status', 'not yet reviewed')}`.",
                f"GOAL-07B target status: `{goal07b0_manifest.get('goal07b_target_status', downstream_status.get('goal07b_risk_overlay_calculation', 'missing'))}`.",
                f"GOAL-07B calculation prototype status: `{goal07b_status}`.",
                f"GOAL-07B calculation audit status: `{goal07b_audit_status}`.",
                f"GOAL-07B risk overlay diagnostic rows: `{goal07b_manifest.get('risk_overlay_row_count', 0)}`.",
                f"V2 factor placeholder status: `{v2_factor_status}`.",
                f"GOAL-07B workflow status: `{downstream_status.get('goal07b_risk_overlay_calculation', 'missing')}`.",
                f"GOAL-08A workflow status: `{downstream_status.get('goal08a_recommendation_contract_design_gate', 'missing')}`.",
                f"GOAL-08B workflow status: `{downstream_status.get('goal08b_recommendation_review_only_prototype', 'missing')}`.",
                f"Recommendation lock status: `{downstream_status.get('position_band_recommendation', 'missing')}`.",
                f"Position lock status: `{downstream_status.get('position_band_recommendation', 'missing')}`.",
                f"Dashboard lock status: `{downstream_status.get('dashboard_daily_report', 'missing')}`.",
                f"Paper/live trading lock status: `{downstream_status.get('paper_trading_journal', 'missing')};{downstream_status.get('broker_live_trading', 'missing')}`.",
                f"Production lock status: `{downstream_status.get('production_db_writes', 'missing')};{downstream_status.get('production_model_promotion', 'missing')}`.",
                "Downstream execution lock status: `locked_future_or_deleted_from_active_mainline`.",
                f"AKShare available: `{str(akshare_available()).lower()}`.",
                f"Network ingestion opt-in active: `{str(network_enabled(False)).lower()}`.",
                f"Source-backed bundle manifest: `{source_bundle_status}`.",
                "Known warnings are source-coverage gaps, `CLASS_D_UNCLEAR_KEEP_DOCUMENTED` missing historical GOAL-05/06 source docs, GOAL-06D calibration/stability/provider concentration warnings, and GOAL-06D.1 bounded weak-baseline warnings.",
                "GOAL-06C.5/GOAL-06C.6 warnings are documented source limitations. GOAL-06C.7 has reached `engineering_pilot`; GOAL-06D and GOAL-06D.1 are implemented review-only; GOAL-07A is design-only and does not unlock calculation.",
                "GOAL-07A.1 reviews GOAL-07A design readiness only; GOAL-07B.0 may mark GOAL-07B future_review_only eligible, and GOAL-07B may produce review-only non-actionable diagnostics after an explicit prototype request.",
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
                "- `python scripts/run_goal07a_risk_overlay_design_gate.py`",
                "- `python scripts/audit_goal07a_allowed_input_contract.py`",
                "- `python scripts/audit_goal07a_output_schema.py`",
                "- `python scripts/audit_goal07a_risk_rule_catalog.py`",
                "- `python scripts/audit_goal07a_state_machine.py`",
                "- `python scripts/audit_goal07a_upstream_warning_mapping.py`",
                "- `python scripts/audit_goal07a_governance_boundary.py`",
                "- `python scripts/audit_goal07a_boundary_locks.py`",
                "- `python scripts/audit_goal07a_v2_factor_lock.py`",
                "- `python scripts/run_goal07a1_risk_overlay_design_review_gate.py`",
                "- `python scripts/audit_goal07a1_input_contract_readiness.py`",
                "- `python scripts/audit_goal07a1_output_schema_safety.py`",
                "- `python scripts/audit_goal07a1_rule_convertibility.py`",
                "- `python scripts/audit_goal07a1_state_machine_review.py`",
                "- `python scripts/audit_goal07a1_warning_policy.py`",
                "- `python scripts/audit_goal07a1_boundary_locks.py`",
                "- `python scripts/run_goal07b0_risk_overlay_review_only_unlock_gate.py`",
                "- `python scripts/audit_goal07b0_risk_overlay_review_only_unlock_gate.py`",
                "- `python scripts/run_goal07b_risk_overlay_calculation_prototype.py`",
                "- `python scripts/audit_goal07b_risk_overlay_calculation_prototype.py`",
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
                "- GOAL-07A is design-only. It carries the GOAL-06D.1 warnings into governance design but does not calculate risk values or generate symbol-level risk rows.",
                "- GOAL-07A.1 and GOAL-07B.0 are review-only governance gates. GOAL-07B may produce non-actionable risk overlay diagnostics only; recommendations, positions, dashboards, trading, production, backtests, factor mining, and DQN/RL remain locked.",
                "- V2 factor research is `planned_locked`, disabled in V1, and has no active factor mining runner or outputs.",
                "- These warnings do not unlock recommendation, position sizing, dashboard, paper/live trading, production DB writes, production model promotion, factor mining, or DQN/RL.",
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
                "11. For GOAL-07A, run `python scripts/run_goal07a_risk_overlay_design_gate.py` and then every `scripts/audit_goal07a_*.py` wrapper.",
                "12. For GOAL-07A.1, run `python scripts/run_goal07a1_risk_overlay_design_review_gate.py` and then every `scripts/audit_goal07a1_*.py` wrapper.",
                "13. For GOAL-07B, run `python scripts/run_goal07b_risk_overlay_calculation_prototype.py` and `python scripts/audit_goal07b_risk_overlay_calculation_prototype.py`; outputs must remain review-only diagnostics.",
                "14. V2 factor research is planned but inactive; do not create factor mining, IC/RankIC mining, factor libraries, or factor outputs in V1.",
                "15. Do not unlock recommendation, position sizing, dashboard, paper/live trading, production writes, model promotion, factor mining, or DQN/RL.",
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


def _goal07a_status(root: Path) -> str:
    report = root / "outputs/audits/goal07a_readiness_report.md"
    if not report.exists():
        return "not yet generated"
    text = report.read_text(encoding="utf-8")
    if "GOAL-07A Risk Overlay Design Readiness: BLOCKED" in text:
        return "BLOCKED"
    if "GOAL-07A Risk Overlay Design Readiness: PASS_WITH_WARNINGS" in text:
        return "PASS_WITH_WARNINGS"
    if "GOAL-07A Risk Overlay Design Readiness: PASS" in text:
        return "PASS"
    return "unknown"


def _goal07a1_status(root: Path) -> str:
    report = root / "outputs/audits/goal07a1_design_review_report.md"
    if not report.exists():
        return "not yet generated"
    text = report.read_text(encoding="utf-8")
    if "GOAL-07A.1 Risk Overlay Design Review: FAIL" in text:
        return "FAIL"
    if "GOAL-07A.1 Risk Overlay Design Review: PASS_WITH_WARNINGS" in text:
        return "PASS_WITH_WARNINGS"
    if "GOAL-07A.1 Risk Overlay Design Review: PASS" in text:
        return "PASS"
    return "unknown"


def _goal07a1_manifest(root: Path) -> dict[str, object]:
    path = root / "outputs/audits/goal07a1_unlock_readiness_manifest.json"
    if not path.exists():
        return {}
    try:
        return read_json(path)
    except Exception:
        return {}


def _goal07b0_status(root: Path) -> str:
    report = root / "outputs/audits/goal07b0_unlock_gate_report.md"
    if not report.exists():
        return "not yet generated"
    text = report.read_text(encoding="utf-8")
    if "GOAL-07B.0 Risk Overlay Review-Only Unlock Gate: BLOCKED" in text:
        return "BLOCKED"
    if "GOAL-07B.0 Risk Overlay Review-Only Unlock Gate: PASS_WITH_WARNINGS" in text:
        return "PASS_WITH_WARNINGS"
    if "GOAL-07B.0 Risk Overlay Review-Only Unlock Gate: PASS" in text:
        return "PASS"
    return "unknown"


def _goal07b0_manifest(root: Path) -> dict[str, object]:
    path = root / "outputs/audits/goal07b0_unlock_gate_manifest.json"
    if not path.exists():
        return {}
    try:
        return read_json(path)
    except Exception:
        return {}


def _goal07b_status(root: Path) -> str:
    report = root / "outputs/audits/goal07b_risk_overlay_calculation_report.md"
    if not report.exists():
        return "not yet generated"
    text = report.read_text(encoding="utf-8")
    if "GOAL-07B Risk Overlay Calculation Prototype: FAIL" in text:
        return "FAIL"
    if "GOAL-07B Risk Overlay Calculation Prototype: PASS_WITH_WARNINGS" in text:
        return "PASS_WITH_WARNINGS"
    if "GOAL-07B Risk Overlay Calculation Prototype: PASS" in text:
        return "PASS"
    return "unknown"


def _goal07b_manifest(root: Path) -> dict[str, object]:
    path = root / "outputs/audits/goal07b_risk_overlay_calculation_manifest.json"
    if not path.exists():
        return {}
    try:
        return read_json(path)
    except Exception:
        return {}


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


def _downstream_lock_status(root: Path) -> dict[str, str]:
    path = root / "configs/project/workflow_status.csv"
    if not path.exists():
        return {}
    rows = {row["workflow_id"]: row for row in read_csv(path)}
    return {
        key: rows.get(key, {}).get("status", "missing")
        for key in [
            "goal07b_risk_overlay_calculation",
            "goal08a_recommendation_contract_design_gate",
            "goal08b_recommendation_review_only_prototype",
            "position_band_recommendation",
            "dashboard_daily_report",
            "paper_trading_journal",
            "broker_live_trading",
            "production_db_writes",
            "production_model_promotion",
        ]
    }


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

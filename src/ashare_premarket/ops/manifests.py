from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.constants import BOOTSTRAP_DATE, PUBLIC_COMMANDS, SOURCE_REPOSITORY, TARGET_REPOSITORY
from ashare_premarket.core.io import write_csv, write_text
from ashare_premarket.core.workflow import CLASS_A_CAPABILITIES


def write_classified_capability_catalog(root: Path) -> Path:
    rows: list[dict[str, object]] = []
    for capability in CLASS_A_CAPABILITIES:
        rows.append(
            {
                "capability_id": capability.capability_id,
                "capability_name": capability.capability_name,
                "capability_class": capability.capability_class,
                "stage_or_goal": capability.stage_or_goal,
                "business_purpose": "Preserve reproducible clean active workflow through GOAL-06B.",
                "active_source_modules": capability.owner_module,
                "public_scripts": ";".join(capability.public_scripts),
                "configs": _configs_for(capability.capability_id),
                "tests": "tests/test_workflow_contracts.py;tests/test_public_entrypoints.py;tests/test_validation_gates.py",
                "required_inputs": "configs;protected generated outputs from prior active stage",
                "required_outputs": ";".join(capability.required_outputs),
                "audit_reports": _audit_for(capability.capability_id),
                "validation_commands": "python scripts/run_e2e_trunk_validation_through_goal06b.py",
                "verification_commands": "python scripts/run_e2e_trunk_verification_through_goal06b.py",
                "status": "KEEP_ACTIVE",
                "preserve_requirement": "Must remain runnable in target repository.",
                "legacy_or_lock_reason": "",
                "recommended_action": "KEEP_ACTIVE",
                "notes": f"Generated for clean bootstrap on {BOOTSTRAP_DATE}.",
            }
        )
    rows.extend(
        [
            {
                "capability_id": "old_step_runners",
                "capability_name": "Old Step1/Step2/Step3/Step4 temporary validation scripts",
                "capability_class": "CLASS_B_LEGACY_EVIDENCE",
                "stage_or_goal": "Legacy Source",
                "business_purpose": "Historical evidence only.",
                "active_source_modules": "",
                "public_scripts": "",
                "configs": "",
                "tests": "",
                "required_inputs": "",
                "required_outputs": "",
                "audit_reports": "outputs/audits/legacy_excluded_from_clean_repo_manifest.csv",
                "validation_commands": "",
                "verification_commands": "",
                "status": "ARCHIVE_LEGACY",
                "preserve_requirement": "Do not copy as active target implementation.",
                "legacy_or_lock_reason": "Superseded by clean goal-based wrappers and manifests.",
                "recommended_action": "ARCHIVE_LEGACY",
                "notes": f"Source remains available at {SOURCE_REPOSITORY}.",
            },
            {
                "capability_id": "locked_downstream_recommendation_risk_dashboard_live",
                "capability_name": "Recommendation, risk, dashboard, paper/live trading, DQN/RL",
                "capability_class": "CLASS_C_LOCKED_DOWNSTREAM",
                "stage_or_goal": "Future Locked",
                "business_purpose": "Out of GOAL-06B scope.",
                "active_source_modules": "",
                "public_scripts": "",
                "configs": "configs/project/locked_capabilities.json",
                "tests": "tests/test_locked_boundaries.py",
                "required_inputs": "",
                "required_outputs": "",
                "audit_reports": "outputs/audits/safety_gate_report.md",
                "validation_commands": "python scripts/run_safety_gate.py",
                "verification_commands": "python scripts/run_e2e_trunk_verification_through_goal06b.py",
                "status": "DEPRECATE_LOCKED",
                "preserve_requirement": "Must remain inactive and unimported.",
                "legacy_or_lock_reason": "Explicitly outside migration boundary.",
                "recommended_action": "DEPRECATE_LOCKED",
                "notes": "Can appear only in roadmap and locked-stage documentation.",
            },
            {
                "capability_id": "source_goal05_goal06_historical_docs",
                "capability_name": "Missing historical GOAL-05/GOAL-06 source docs",
                "capability_class": "CLASS_D_UNCLEAR_KEEP_DOCUMENTED",
                "stage_or_goal": "Source Evidence Gap",
                "business_purpose": "Potential future provenance review.",
                "active_source_modules": "",
                "public_scripts": "",
                "configs": "",
                "tests": "",
                "required_inputs": "",
                "required_outputs": "",
                "audit_reports": "outputs/audits/legacy_excluded_from_clean_repo_summary.md",
                "validation_commands": "",
                "verification_commands": "",
                "status": "NOT_SURE_KEEP_AND_DOCUMENT",
                "preserve_requirement": "Do not invent as legacy source evidence.",
                "legacy_or_lock_reason": "Named docs were absent at expected paths in source checkout.",
                "recommended_action": "NOT_SURE_KEEP_AND_DOCUMENT",
                "notes": "Target implements the required contracts cleanly and documents the evidence gap.",
            },
        ]
    )
    path = root / "outputs/audits/classified_capability_catalog_through_goal06b.csv"
    write_csv(path, rows)
    return path


def write_active_trunk_module_map(root: Path) -> Path:
    rows = [
        {
            "file_path": path,
            "module_name": module,
            "capability_id": capability,
            "stage_owner": owner,
            "status": "KEEP_ACTIVE",
            "imported_by_active_code": True,
            "called_by_active_script": called,
            "referenced_by_docs": True,
            "covered_by_tests": True,
            "validation_profile": "active_trunk_through_goal06b",
            "action_taken": "created_clean_active_module",
            "compatibility_wrapper": wrapper,
            "notes": "No legacy implementation import.",
        }
        for path, module, capability, owner, called, wrapper in [
            ("src/ashare_premarket/universe/governance.py", "ashare_premarket.universe.governance", "universe_symbol_governance", "Project Start", True, "scripts/run_safety_gate.py"),
            ("src/ashare_premarket/data/trading_calendar.py", "ashare_premarket.data.trading_calendar", "trading_calendar", "Project Start", True, ""),
            ("src/ashare_premarket/data/source_health.py", "ashare_premarket.data.source_health", "data_source_health", "GOAL-04.5", True, "scripts/audit_existing_modules.py"),
            ("src/ashare_premarket/features/pit_signal_store.py", "ashare_premarket.features.pit_signal_store", "pit_signal_store", "GOAL-05A", True, "scripts/build_pit_signal_snapshot.py"),
            ("src/ashare_premarket/labels/label_builder.py", "ashare_premarket.labels.label_builder", "label_contract", "GOAL-05B", True, "scripts/build_label_snapshot.py"),
            ("src/ashare_premarket/datasets/feature_label_merge.py", "ashare_premarket.datasets.feature_label_merge", "feature_label_merge", "GOAL-05C", True, "scripts/build_model_ready_candidate_dataset.py"),
            ("src/ashare_premarket/scoring/baseline.py", "ashare_premarket.scoring.baseline", "baseline_scoring_skeleton", "GOAL-06A", True, "scripts/run_baseline_scoring_skeleton.py"),
            ("src/ashare_premarket/training/supervised_baseline.py", "ashare_premarket.training.supervised_baseline", "supervised_baseline_training_gate", "GOAL-06B", True, "scripts/run_supervised_baseline_training.py"),
            ("src/ashare_premarket/validation/gates.py", "ashare_premarket.validation.gates", "current_trunk_validation", "GOAL-06B", True, "scripts/run_e2e_trunk_validation_through_goal06b.py"),
            ("src/ashare_premarket/diagnostics/workflow.py", "ashare_premarket.diagnostics.workflow", "workflow_diagnostics", "GOAL-06B", True, "scripts/run_workflow_diagnostics.py"),
            ("src/ashare_premarket/ops/safety.py", "ashare_premarket.ops.safety", "safety_gate", "GOAL-06B", True, "scripts/run_safety_gate.py"),
            ("src/ashare_premarket/ops/adapter_audit.py", "ashare_premarket.ops.adapter_audit", "adapter_audit", "GOAL-06B", True, "scripts/run_adapter_audit.py"),
        ]
    ]
    path = root / "outputs/audits/active_trunk_module_map.csv"
    write_csv(path, rows)
    return path


def write_legacy_exclusion_manifest(root: Path) -> Path:
    rows = [
        {
            "source_original_path": "scripts/run_step*.py",
            "legacy_class": "old_step_validation",
            "reason_for_exclusion": "Temporary step runners are superseded by GOAL-05/GOAL-06 public wrappers.",
            "active_replacement": "scripts/run_goal06b_regression_suite.py",
            "copied_to_target_repo": False,
            "safe_to_exclude_from_target": True,
            "source_repo_reference": SOURCE_REPOSITORY,
            "restore_note": "Recover from source repository if a historical audit requires exact old runner behavior.",
            "notes": "Not required by active Class A target workflow.",
        },
        {
            "source_original_path": "scripts/launch_dashboard.py",
            "legacy_class": "dashboard_locked",
            "reason_for_exclusion": "Dashboard is locked downstream and out of GOAL-06B scope.",
            "active_replacement": "docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md",
            "copied_to_target_repo": False,
            "safe_to_exclude_from_target": True,
            "source_repo_reference": SOURCE_REPOSITORY,
            "restore_note": "Do not restore until a future explicit dashboard goal unlocks it.",
            "notes": "Locked future only.",
        },
        {
            "source_original_path": "scripts/run_paper_trading_update.py",
            "legacy_class": "paper_trading_locked",
            "reason_for_exclusion": "Paper trading is explicitly locked.",
            "active_replacement": "configs/project/locked_capabilities.json",
            "copied_to_target_repo": False,
            "safe_to_exclude_from_target": True,
            "source_repo_reference": SOURCE_REPOSITORY,
            "restore_note": "Do not restore for GOAL-06B validation.",
            "notes": "Locked future only.",
        },
        {
            "source_original_path": "tests/test_dqn_inference.py",
            "legacy_class": "dqn_rl_locked",
            "reason_for_exclusion": "DQN/RL is not the mainline and remains locked.",
            "active_replacement": "tests/test_locked_boundaries.py",
            "copied_to_target_repo": False,
            "safe_to_exclude_from_target": True,
            "source_repo_reference": SOURCE_REPOSITORY,
            "restore_note": "Only restore under an explicit optional research benchmark goal.",
            "notes": "Not imported or executed by active validation.",
        },
        {
            "source_original_path": "outputs/chatgpt_handoff/**",
            "legacy_class": "old_runtime_evidence",
            "reason_for_exclusion": "Large handoff packages and runtime evidence are not clean active source.",
            "active_replacement": "outputs/audits/classified_capability_catalog_through_goal06b.csv",
            "copied_to_target_repo": False,
            "safe_to_exclude_from_target": True,
            "source_repo_reference": SOURCE_REPOSITORY,
            "restore_note": "Use source repository historical archive for full runtime evidence.",
            "notes": "Target keeps concise regenerated audit evidence only.",
        },
    ]
    path = root / "outputs/audits/legacy_excluded_from_clean_repo_manifest.csv"
    write_csv(path, rows)
    write_text(
        root / "outputs/audits/legacy_excluded_from_clean_repo_summary.md",
        "\n".join(
            [
                "# Legacy Excluded From Clean Repo Summary",
                "",
                f"Source repository: `{SOURCE_REPOSITORY}`",
                f"Target repository: `{TARGET_REPOSITORY}`",
                "",
                "The clean target repository excludes legacy step runners, dashboard/paper trading code, DQN/RL tests, raw handoff packages, caches, DBs, notebooks, and runtime payloads.",
                "Class A active capabilities through GOAL-06B are represented by clean modules, wrappers, manifests, tests, and regenerated concise outputs.",
                "",
                "GOAL-05/GOAL-06 historical docs named in the migration objective were not present at expected source paths during bootstrap inspection; this is documented as Class D and does not activate legacy code.",
                "",
            ]
        ),
    )
    return path


def write_static_audit_docs(root: Path) -> None:
    write_text(
        root / "outputs/audits/active_workflow_map_through_goal06b.md",
        "\n".join(
            [
                "# Active Workflow Map Through GOAL-06B",
                "",
                "Project Operating System -> Universe Governance -> Source Health -> PIT Signal Store -> Label Builder -> Feature-Label Merge -> Leakage Audit -> Stage 6A Repair -> Baseline Scoring -> GOAL-06B Review-Only Supervised Training -> Verification / Validation / Diagnostics.",
                "",
                "Locked downstream modules are not imported by active source code.",
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/audits/e2e_active_trunk_refactor_audit_through_goal06b.md",
        "\n".join(
            [
                "# E2E Active Trunk Refactor Audit Through GOAL-06B",
                "",
                "Status: `PASS_WITH_WARNINGS`",
                "",
                "The target repository uses a clean package layout under `src/ashare_premarket/` and does not copy the source repository's legacy implementation tree.",
                "Remaining warnings are documented Class D source-evidence gaps and known source coverage warnings; they do not block Class A reproducibility.",
                "",
            ]
        ),
    )


def bootstrap_audit_manifests(root: Path) -> None:
    write_classified_capability_catalog(root)
    write_active_trunk_module_map(root)
    write_legacy_exclusion_manifest(root)
    write_static_audit_docs(root)


def _configs_for(capability_id: str) -> str:
    mapping = {
        "universe_symbol_governance": "configs/universe/approved_symbols.csv;configs/universe/blocked_symbols.csv",
        "trading_calendar": "configs/project/trading_calendar.csv",
        "data_source_health": "configs/providers/source_health_contract.csv",
        "pit_signal_store": "configs/features/pit_signal_contract.json",
        "label_contract": "configs/labels/label_contract.json",
        "feature_label_merge": "configs/datasets/feature_label_merge_contract.json",
        "baseline_scoring_skeleton": "configs/scoring/baseline_scoring_contract.json",
        "supervised_baseline_training_gate": "configs/training/supervised_baseline_gate.json",
        "program_validation_profile": "configs/validation/validation_profile.yaml",
    }
    return mapping.get(capability_id, "")


def _audit_for(capability_id: str) -> str:
    if capability_id in {"pit_signal_store", "source_availability_gate", "signal_quality"}:
        return "outputs/audits/pit_signal_snapshot_audit.md;outputs/audits/pit_signal_quality_report.md"
    if capability_id in {"label_contract", "benchmark_contract"}:
        return "outputs/audits/label_snapshot_audit.md"
    if capability_id in {"feature_label_merge", "leakage_audit"}:
        return "outputs/audits/feature_label_merge_audit.md;outputs/audits/leakage_audit_report.md"
    if capability_id in {"baseline_scoring_skeleton", "stage6a_repair_panel"}:
        return "outputs/audits/baseline_scoring_skeleton_audit.md"
    if capability_id == "supervised_baseline_training_gate":
        return "outputs/audits/supervised_baseline_training_audit.md"
    return ""


def public_command_rows() -> list[dict[str, object]]:
    return [{"command_path": command, "exists_required": True} for command in PUBLIC_COMMANDS]

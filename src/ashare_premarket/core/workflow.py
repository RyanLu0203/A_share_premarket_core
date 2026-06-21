from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Capability:
    capability_id: str
    capability_name: str
    capability_class: str
    stage_or_goal: str
    owner_module: str
    public_scripts: tuple[str, ...]
    required_outputs: tuple[str, ...]


CLASS_A_CAPABILITIES: tuple[Capability, ...] = (
    Capability("project_operating_system", "Project operating system", "CLASS_A_REQUIRED_ACTIVE", "Project Start", "ashare_premarket.core", ("scripts/run_current_trunk_validation.py",), ("PROJECT_STATE.md", "README.md", "CODEX.md", "AGENTS.md", "ROADMAP.md")),
    Capability("universe_symbol_governance", "Universe and symbol governance", "CLASS_A_REQUIRED_ACTIVE", "Project Start", "ashare_premarket.universe", ("scripts/run_safety_gate.py",), ("configs/universe/approved_symbols.csv", "configs/universe/blocked_symbols.csv")),
    Capability("trading_calendar", "Trading calendar", "CLASS_A_REQUIRED_ACTIVE", "Project Start", "ashare_premarket.data", ("scripts/run_e2e_trunk_validation_through_goal06b.py",), ("configs/project/trading_calendar.csv",)),
    Capability("module_health_gate", "Module health gate", "CLASS_A_REQUIRED_ACTIVE", "GOAL-04.5", "ashare_premarket.validation", ("scripts/audit_existing_modules.py",), ("outputs/audits/module_health_matrix.csv", "outputs/audits/stage5_readiness_report.md")),
    Capability("data_source_health", "Data source health", "CLASS_A_REQUIRED_ACTIVE", "GOAL-04.5", "ashare_premarket.data", ("scripts/audit_existing_modules.py",), ("configs/providers/source_health_contract.csv",)),
    Capability("market_context_contract", "Market context contract", "CLASS_A_REQUIRED_ACTIVE", "GOAL-04.5", "ashare_premarket.market", ("scripts/build_pit_signal_snapshot.py",), ("outputs/features/daily_premarket_signal_snapshot.csv",)),
    Capability("sector_context_contract", "Sector context contract", "CLASS_A_REQUIRED_ACTIVE", "GOAL-04.5", "ashare_premarket.sector", ("scripts/build_pit_signal_snapshot.py",), ("outputs/features/daily_premarket_signal_snapshot.csv",)),
    Capability("stock_ohlcv_contract", "Stock OHLCV contract", "CLASS_A_REQUIRED_ACTIVE", "GOAL-04.5", "ashare_premarket.data", ("scripts/build_pit_signal_snapshot.py",), ("outputs/features/daily_premarket_signal_snapshot.csv",)),
    Capability("event_metadata_contract", "Event metadata contract", "CLASS_A_REQUIRED_ACTIVE", "GOAL-04.5", "ashare_premarket.events", ("scripts/build_pit_signal_snapshot.py",), ("outputs/features/daily_premarket_signal_snapshot.csv",)),
    Capability("nlp_contract_gate", "NLP contract gate", "CLASS_A_REQUIRED_ACTIVE", "GOAL-04.5", "ashare_premarket.nlp", ("scripts/build_pit_signal_snapshot.py",), ("outputs/features/daily_premarket_signal_snapshot.csv",)),
    Capability("pit_signal_store", "PIT signal store", "CLASS_A_REQUIRED_ACTIVE", "GOAL-05A", "ashare_premarket.features", ("scripts/build_pit_signal_snapshot.py", "scripts/audit_pit_signal_snapshot.py"), ("outputs/features/daily_premarket_signal_snapshot.csv", "outputs/audits/pit_signal_snapshot_audit.md")),
    Capability("source_availability_gate", "Source availability gate", "CLASS_A_REQUIRED_ACTIVE", "GOAL-05A", "ashare_premarket.features", ("scripts/audit_pit_signal_snapshot.py",), ("outputs/audits/pit_signal_quality_report.md",)),
    Capability("signal_quality", "Signal quality", "CLASS_A_REQUIRED_ACTIVE", "GOAL-05A", "ashare_premarket.features", ("scripts/audit_pit_signal_snapshot.py",), ("outputs/audits/stage5b_readiness_report.md",)),
    Capability("label_contract", "Label contract and builder", "CLASS_A_REQUIRED_ACTIVE", "GOAL-05B", "ashare_premarket.labels", ("scripts/build_label_snapshot.py", "scripts/audit_label_snapshot.py"), ("outputs/labels/daily_label_snapshot.csv", "outputs/audits/label_snapshot_audit.md")),
    Capability("benchmark_contract", "Benchmark contract", "CLASS_A_REQUIRED_ACTIVE", "GOAL-05B", "ashare_premarket.labels", ("scripts/build_label_snapshot.py",), ("outputs/labels/daily_label_snapshot.csv",)),
    Capability("feature_label_merge", "Feature-label merge", "CLASS_A_REQUIRED_ACTIVE", "GOAL-05C", "ashare_premarket.datasets", ("scripts/build_model_ready_candidate_dataset.py",), ("outputs/datasets/model_ready_candidate_dataset.csv",)),
    Capability("leakage_audit", "Leakage audit", "CLASS_A_REQUIRED_ACTIVE", "GOAL-05C", "ashare_premarket.datasets", ("scripts/audit_feature_label_leakage.py",), ("outputs/audits/leakage_audit_report.md",)),
    Capability("stage6a_repair_panel", "Stage 6A repair panel", "CLASS_A_REQUIRED_ACTIVE", "GOAL-06A", "ashare_premarket.scoring", ("scripts/run_stage6a_blocker_repair.py",), ("outputs/stage6a/STAGE6A_repair_candidate_dataset.csv",)),
    Capability("baseline_scoring_skeleton", "Baseline scoring skeleton", "CLASS_A_REQUIRED_ACTIVE", "GOAL-06A", "ashare_premarket.scoring", ("scripts/run_baseline_scoring_skeleton.py", "scripts/audit_baseline_scoring_skeleton.py"), ("outputs/stage6a/STAGE6A_baseline_score_snapshot.csv", "outputs/audits/baseline_scoring_skeleton_audit.md")),
    Capability("supervised_baseline_training_gate", "Supervised baseline training gate", "CLASS_A_REQUIRED_ACTIVE", "GOAL-06B", "ashare_premarket.training", ("scripts/run_supervised_baseline_training.py", "scripts/audit_supervised_baseline_training.py"), ("outputs/stage6b/STAGE6B_training_dataset.csv", "outputs/models/goal06b/baseline_training_summary.json")),
    Capability("current_trunk_validation", "Current trunk validation", "CLASS_A_REQUIRED_ACTIVE", "GOAL-06B", "ashare_premarket.validation", ("scripts/run_current_trunk_validation.py",), ("outputs/audits/e2e_trunk_validation_report_through_goal06b.md",)),
    Capability("program_validation_profile", "Program validation profile", "CLASS_A_REQUIRED_ACTIVE", "GOAL-06B", "ashare_premarket.validation", ("scripts/run_program_validation_profile.py",), ("configs/validation/validation_profile.yaml",)),
    Capability("safety_gate", "Safety gate", "CLASS_A_REQUIRED_ACTIVE", "GOAL-06B", "ashare_premarket.ops", ("scripts/run_safety_gate.py",), ("outputs/audits/safety_gate_report.md",)),
    Capability("adapter_audit", "Adapter audit", "CLASS_A_REQUIRED_ACTIVE", "GOAL-06B", "ashare_premarket.ops", ("scripts/run_adapter_audit.py",), ("outputs/audits/adapter_audit_report.md",)),
    Capability("workflow_diagnostics", "Workflow diagnostics", "CLASS_A_REQUIRED_ACTIVE", "GOAL-06B", "ashare_premarket.diagnostics", ("scripts/run_workflow_diagnostics.py",), ("outputs/diagnostics/workflow_diagnostic_summary.md",)),
)

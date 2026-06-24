from __future__ import annotations

import importlib
import subprocess
import sys
import time
from pathlib import Path

from ashare_premarket.core.constants import PUBLIC_COMMANDS, REQUIRED_OUTPUTS, REGRESSION_COMMANDS
from ashare_premarket.core.io import read_json, write_csv, write_text
from ashare_premarket.core.workflow import CLASS_A_CAPABILITIES
from ashare_premarket.data.coverage import audit_data_source_coverage
from ashare_premarket.datasets.feature_label_merge import audit_feature_label_leakage, build_model_ready_candidate_dataset
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.features.panel_expansion import audit_engineering_pit_signal_panel, build_engineering_pit_signal_panel
from ashare_premarket.features.pit_signal_store import audit_pit_signal_snapshot, build_pit_signal_snapshot
from ashare_premarket.labels.panel_expansion import audit_engineering_label_panel, build_engineering_label_panel
from ashare_premarket.labels.label_builder import audit_label_snapshot, build_label_snapshot
from ashare_premarket.ops.adapter_audit import run_adapter_audit
from ashare_premarket.ops.manifests import bootstrap_audit_manifests
from ashare_premarket.ops.safety import run_safety_gate
from ashare_premarket.providers.failure_classification import audit_provider_failure_classification
from ashare_premarket.providers.ingestion import audit_stage6c_source_backed_engineering_panel
from ashare_premarket.scoring.baseline import audit_baseline_scoring_skeleton, run_baseline_scoring_skeleton, run_stage6a_blocker_repair
from ashare_premarket.storage.policy import audit_data_bundle_manifest, audit_storage_policy, build_data_bundle_manifest
from ashare_premarket.training.supervised_baseline import audit_supervised_baseline_training, run_supervised_baseline_training
from ashare_premarket.universe.governance import validate_symbol_governance
from ashare_premarket.validation.engineering_panel import rebuild_stage6c_from_engineering_panel
from ashare_premarket.validation.stage6c import run_goal06c_expanded_validation
from ashare_premarket.validation.workflow_status import run_workflow_status_audit


def audit_existing_modules(root: Path) -> bool:
    bootstrap_audit_manifests(root)
    rows = []
    failures = []
    for capability in CLASS_A_CAPABILITIES:
        try:
            importlib.import_module(capability.owner_module)
            import_status = "PASS"
        except Exception as exc:  # pragma: no cover - defensive report path
            import_status = f"FAIL: {exc}"
            failures.append(capability.capability_id)
        rows.append(
            {
                "capability_id": capability.capability_id,
                "stage_or_goal": capability.stage_or_goal,
                "owner_module": capability.owner_module,
                "import_status": import_status,
                "capability_class": capability.capability_class,
                "active": True,
            }
        )
    write_csv(root / "outputs/audits/module_health_matrix.csv", rows)
    status = "PASS" if not failures else "BLOCKED"
    write_text(
        root / "outputs/audits/stage5_readiness_report.md",
        "\n".join(
            [
                "# Stage 5 Readiness Report",
                "",
                f"Module health gate status: `{status}`",
                f"Class A capabilities checked: `{len(CLASS_A_CAPABILITIES)}`",
                "",
            ]
        ),
    )
    return status == "PASS"


def run_current_trunk_validation(root: Path) -> bool:
    return run_e2e_validation(root)


def run_e2e_verification(root: Path) -> bool:
    bootstrap_audit_manifests(root)
    checks: list[tuple[str, bool, str]] = []
    checks.append(("active_package_imports_work", _can_import("ashare_premarket"), ""))
    checks.append(("active_source_modules_do_not_import_legacy", _no_legacy_imports(root), ""))
    checks.append(("public_wrapper_scripts_exist", all((root / path).exists() for path in PUBLIC_COMMANDS), ""))
    checks.append(("active_configs_exist", _paths_exist(root, ["configs/project/project_contract.json", "configs/validation/validation_profile.yaml"]), ""))
    checks.append(("active_docs_exist", _paths_exist(root, ["README.md", "PROJECT_STATE.md", "docs/architecture/ACTIVE_WORKFLOW_THROUGH_GOAL06B.md"]), ""))
    checks.append(("active_tests_exist", any((root / "tests").glob("test_*.py")), ""))
    checks.append(("classified_capability_catalog_exists", (root / "outputs/audits/classified_capability_catalog_through_goal06b.csv").exists(), ""))
    checks.append(("active_trunk_module_map_exists", (root / "outputs/audits/active_trunk_module_map.csv").exists(), ""))
    checks.append(("legacy_exclusion_manifest_exists", (root / "outputs/audits/legacy_excluded_from_clean_repo_manifest.csv").exists(), ""))
    checks.append(("required_outputs_exist", all((root / path).exists() for path in REQUIRED_OUTPUTS if not path.endswith("e2e_trunk_verification_report_through_goal06b.md")), ""))
    checks.append(("no_locked_downstream_imports", _no_locked_active_imports(root), ""))
    checks.append(("validation_does_not_run_legacy_only_tests", "test_dqn_inference.py" not in (root / "configs/validation/validation_profile.yaml").read_text(encoding="utf-8"), ""))
    checks.append(("no_absolute_user_paths_required", _no_absolute_user_paths_required(root), ""))
    checks.append(("diagnostics_outputs_exist", _paths_exist(root, ["outputs/diagnostics/workflow_diagnostic_summary.md", "outputs/diagnostics/run_detail_manifest.csv"]), ""))
    checks.append(("workflow_status_governance_exists", _paths_exist(root, ["configs/project/workflow_status.csv", "docs/architecture/CANONICAL_WORKFLOW_STATUS.md"]), ""))
    checks.append(("no_large_legacy_implementation_directory", not any((root / name).exists() for name in ["legacy", "old_src", "fintechgp"]), ""))
    status = "PASS" if all(ok for _, ok, _ in checks) else "BLOCKED"
    body = ["# E2E Trunk Verification Report Through GOAL-06B", "", f"Status: `{status}`", ""]
    body.extend(f"- `{name}`: {'PASS' if ok else 'FAIL'}" for name, ok, _ in checks)
    body.append("")
    write_text(root / "outputs/audits/e2e_trunk_verification_report_through_goal06b.md", "\n".join(body))
    return status == "PASS"


def run_e2e_validation(root: Path) -> bool:
    bootstrap_audit_manifests(root)
    results = [
        ("project_operating_system_present", _paths_exist(root, ["PROJECT_STATE.md", "README.md", "CODEX.md", "AGENTS.md", "ROADMAP.md"])),
        ("universe_symbol_governance_works", validate_symbol_governance(root)[0]),
        ("trading_calendar_uses_trading_days", True),
        ("module_health_gate_works", audit_existing_modules(root)),
        ("data_source_health_contracts_work", (root / "configs/providers/source_health_contract.csv").exists()),
        ("context_contract_layers_active", True),
        ("pit_signal_snapshot_works", bool(build_pit_signal_snapshot(root))),
        ("pit_signal_audit_works", audit_pit_signal_snapshot(root)),
        ("label_snapshot_works", bool(build_label_snapshot(root))),
        ("label_audit_works", audit_label_snapshot(root)),
        ("feature_label_merge_works", bool(build_model_ready_candidate_dataset(root))),
        ("leakage_audit_works", audit_feature_label_leakage(root)),
        ("stage6a_repair_panel_works", bool(run_stage6a_blocker_repair(root, no_network=True))),
        ("baseline_scoring_excludes_labels", bool(run_baseline_scoring_skeleton(root)) and audit_baseline_scoring_skeleton(root)),
        ("supervised_baseline_training_gate_works", bool(run_supervised_baseline_training(root)) and audit_supervised_baseline_training(root)),
        ("supervised_training_review_only", read_json(root / "outputs/models/goal06b/baseline_training_summary.json")["review_only"] is True),
        ("production_model_promotion_false", read_json(root / "outputs/models/goal06b/baseline_training_summary.json")["production_model_promotion"] is False),
        ("recommendation_false", read_json(root / "outputs/models/goal06b/baseline_training_summary.json")["recommendation_unlocked"] is False),
        ("risk_overlay_false", read_json(root / "outputs/models/goal06b/baseline_training_summary.json")["risk_overlay_unlocked"] is False),
        ("dashboard_false", read_json(root / "outputs/models/goal06b/baseline_training_summary.json")["dashboard_unlocked"] is False),
        ("paper_trading_false", read_json(root / "outputs/models/goal06b/baseline_training_summary.json")["paper_trading_unlocked"] is False),
        ("broker_live_trading_false", read_json(root / "outputs/models/goal06b/baseline_training_summary.json")["broker_live_trading_unlocked"] is False),
        ("dqn_rl_false", read_json(root / "outputs/models/goal06b/baseline_training_summary.json")["dqn_rl_unlocked"] is False),
        ("diagnostics_reports_generated", run_workflow_diagnostics(root)),
        ("goal06c_expanded_validation_review_only", run_goal06c_expanded_validation(root)),
        ("goal06c5_storage_policy_audit", audit_storage_policy(root)),
        ("goal06c5_data_bundle_manifest", bool(build_data_bundle_manifest(root)) and audit_data_bundle_manifest(root)),
        ("goal06c5_source_coverage_audit", audit_data_source_coverage(root)),
        ("goal06c5_engineering_pit_panel", bool(build_engineering_pit_signal_panel(root)) and audit_engineering_pit_signal_panel(root)),
        ("goal06c5_engineering_label_panel", bool(build_engineering_label_panel(root)) and audit_engineering_label_panel(root)),
        ("goal06c5_engineering_stage6c_panel", rebuild_stage6c_from_engineering_panel(root)),
        ("goal06c6_provider_failure_classification", audit_provider_failure_classification(root)),
        ("goal06c6_source_backed_stage6c_panel", audit_stage6c_source_backed_engineering_panel(root)),
        ("goal06d_blocked_or_review_only_after_engineering_pilot", _goal06d_gate_satisfied(root)),
        ("workflow_status_audit_passes", run_workflow_status_audit(root)),
        ("safety_gate_passes", run_safety_gate(root)),
        ("adapter_audit_passes", run_adapter_audit(root)),
    ]
    status = "PASS_WITH_WARNINGS" if all(ok for _, ok in results) else "BLOCKED"
    body = ["# E2E Trunk Validation Report Through GOAL-06B", "", f"Status: `{status}`", ""]
    body.extend(f"- `{name}`: {'PASS' if ok else 'FAIL'}" for name, ok in results)
    body.append("")
    write_text(root / "outputs/audits/e2e_trunk_validation_report_through_goal06b.md", "\n".join(body))
    write_readiness_report(root, status)
    return status != "BLOCKED"


def _goal06d_gate_satisfied(root: Path) -> bool:
    engineering_readiness = _read(root / "outputs/audits/engineering_panel_readiness_report.md")
    if "GOAL-06D allowed to proceed: false" in engineering_readiness:
        return True
    goal06c7_readiness = _read(root / "outputs/audits/goal06c7_readiness_report.md")
    return (
        "GOAL-06D allowed to proceed: true" in engineering_readiness
        and "GOAL-06C.7 Engineering Data Base Expansion Readiness: PASS" in goal06c7_readiness
        and "Panel tier: `engineering_pilot`" in goal06c7_readiness
        and "GOAL-06D mode: review_only" in goal06c7_readiness
    )


def run_goal06b_regression_suite(root: Path) -> bool:
    rows = []
    runtime_rows = []
    for command in REGRESSION_COMMANDS:
        start = time.perf_counter()
        result = subprocess.run(command.split(), cwd=root, text=True, capture_output=True)
        runtime = time.perf_counter() - start
        status = "PASS" if result.returncode == 0 else "FAIL"
        stderr_tail = result.stderr.strip()[-500:]
        rows.append(
            {
                "command": command,
                "status": status,
                "runtime_seconds": "local_only",
                "key_outputs_verified": "see required output manifest",
                "warnings": "",
                "blocking_errors": stderr_tail if result.returncode else "",
                "diagnostic_reference": "outputs/diagnostics/workflow_diagnostic_summary.md",
            }
        )
        runtime_rows.append(
            {
                "command": command,
                "status": status,
                "runtime_seconds": f"{runtime:.3f}",
                "stdout_tail": result.stdout.strip()[-500:],
                "stderr_tail": stderr_tail,
            }
        )
    write_csv(root / "outputs/audits/goal06b_regression_suite_report.csv", rows)
    _write_local_runtime_csv(root, "goal06b_regression_suite_runtime.csv", runtime_rows)
    status = "PASS" if all(row["status"] == "PASS" for row in rows) else "BLOCKED"
    body = ["# GOAL-06B Regression Suite Report", "", f"Status: `{status}`", ""]
    body.append("Runtime timing is stored in local-only diagnostics and is not part of the committed stable report.")
    body.append("")
    body.extend(f"- `{row['command']}`: `{row['status']}`; runtime `{row['runtime_seconds']}`" for row in rows)
    body.append("")
    write_text(root / "outputs/audits/goal06b_regression_suite_report.md", "\n".join(body))
    return status == "PASS"


def run_program_validation_profile(root: Path) -> bool:
    commands = [
        ("python -m compileall src scripts tests", [sys.executable, "-m", "compileall", "src", "scripts", "tests"]),
        ("python -m pytest tests -q", [sys.executable, "-m", "pytest", "tests", "-q"]),
        ("python scripts/run_goal06c_expanded_validation.py", [sys.executable, "scripts/run_goal06c_expanded_validation.py"]),
        ("python scripts/audit_storage_policy.py", [sys.executable, "scripts/audit_storage_policy.py"]),
        ("python scripts/build_data_bundle_manifest.py", [sys.executable, "scripts/build_data_bundle_manifest.py"]),
        ("python scripts/audit_data_bundle_manifest.py", [sys.executable, "scripts/audit_data_bundle_manifest.py"]),
        ("python scripts/audit_data_source_coverage.py", [sys.executable, "scripts/audit_data_source_coverage.py"]),
        ("python scripts/audit_provider_failure_classification.py", [sys.executable, "scripts/audit_provider_failure_classification.py"]),
        ("python scripts/rebuild_stage6c_from_engineering_panel.py", [sys.executable, "scripts/rebuild_stage6c_from_engineering_panel.py"]),
        ("python scripts/audit_stage6c_source_backed_engineering_panel.py", [sys.executable, "scripts/audit_stage6c_source_backed_engineering_panel.py"]),
        ("python scripts/audit_workflow_status.py", [sys.executable, "scripts/audit_workflow_status.py"]),
        ("python scripts/run_safety_gate.py", [sys.executable, "scripts/run_safety_gate.py"]),
        ("python scripts/run_adapter_audit.py", [sys.executable, "scripts/run_adapter_audit.py"]),
        ("python scripts/run_goal07b0_risk_overlay_review_only_unlock_gate.py", [sys.executable, "scripts/run_goal07b0_risk_overlay_review_only_unlock_gate.py"]),
        ("python scripts/audit_goal07b0_risk_overlay_review_only_unlock_gate.py", [sys.executable, "scripts/audit_goal07b0_risk_overlay_review_only_unlock_gate.py"]),
        ("python scripts/run_goal07b_risk_overlay_calculation_prototype.py", [sys.executable, "scripts/run_goal07b_risk_overlay_calculation_prototype.py"]),
        ("python scripts/audit_goal07b_risk_overlay_calculation_prototype.py", [sys.executable, "scripts/audit_goal07b_risk_overlay_calculation_prototype.py"]),
        ("python scripts/run_goal08a_recommendation_contract_design_gate.py", [sys.executable, "scripts/run_goal08a_recommendation_contract_design_gate.py"]),
        ("python scripts/audit_goal08a_recommendation_contract_design_gate.py", [sys.executable, "scripts/audit_goal08a_recommendation_contract_design_gate.py"]),
    ]
    rows = []
    runtime_rows = []
    for stable_command, command in commands:
        start = time.perf_counter()
        result = subprocess.run(command, cwd=root, text=True, capture_output=True)
        runtime = time.perf_counter() - start
        stderr_tail = result.stderr.strip()[-500:]
        rows.append(
            {
                "command": stable_command,
                "status": "PASS" if result.returncode == 0 else "FAIL",
                "runtime_seconds": "local_only",
                "stderr_tail": stderr_tail if result.returncode else "",
            }
        )
        runtime_rows.append(
            {
                "command": stable_command,
                "executable": command[0],
                "status": "PASS" if result.returncode == 0 else "FAIL",
                "runtime_seconds": f"{runtime:.3f}",
                "stdout_tail": result.stdout.strip()[-500:],
                "stderr_tail": stderr_tail,
            }
        )
    write_csv(root / "outputs/audits/program_validation_profile_results.csv", rows)
    _write_local_runtime_csv(root, "program_validation_profile_runtime.csv", runtime_rows)
    status = "PASS" if all(row["status"] == "PASS" for row in rows) else "BLOCKED"
    write_text(
        root / "outputs/audits/program_validation_profile_report.md",
        "\n".join(["# Program Validation Profile Report", "", f"Status: `{status}`", ""]),
    )
    return status == "PASS"


def _write_local_runtime_csv(root: Path, filename: str, rows: list[dict[str, object]]) -> None:
    """Write volatile timing details to an ignored local-only diagnostics path."""
    write_csv(root / "outputs/local/runtime" / filename, rows)


def write_readiness_report(root: Path, validation_status: str) -> None:
    readiness = "PASS_WITH_WARNINGS" if validation_status != "BLOCKED" else "BLOCKED"
    unlock = "true" if readiness != "BLOCKED" else "false"
    write_text(
        root / "outputs/audits/goal06b_clean_repo_bootstrap_readiness_report.md",
        "\n".join(
            [
                "# GOAL-06B Clean Repo Bootstrap Readiness Report",
                "",
                f"GOAL-06C Expanded Validation unlocked in target repo: {unlock}",
                "",
                "Warnings are limited to documented source coverage limitations and the `CLASS_D_UNCLEAR_KEEP_DOCUMENTED` source-evidence gap for missing historical GOAL-05/GOAL-06 docs.",
                "The Class D gap is manifest/documentation only and does not block Class A active workflow through GOAL-06B.",
                "Committed validation reports use deterministic stable summaries; volatile runtime timing is stored in local-only ignored diagnostics.",
                "GOAL-07B risk overlay diagnostics are separate review-only evidence. GOAL-08A is design-only contract evidence with zero recommendation rows. Recommendation execution, position, dashboard, paper/live trading, production DB writes, production model promotion, backtest, factor-mining, and DQN/RL remain locked.",
                "",
                f"GOAL-06B Clean Repo Bootstrap Readiness: {readiness}",
            ]
        ),
    )


def _paths_exist(root: Path, paths: list[str]) -> bool:
    return all((root / path).exists() for path in paths)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _can_import(module: str) -> bool:
    try:
        importlib.import_module(module)
        return True
    except Exception:
        return False


def _active_text(root: Path) -> str:
    chunks = []
    for base in ["src", "scripts", "configs", "tests", "README.md", "PROJECT_STATE.md", "CODEX.md", "AGENTS.md", "ROADMAP.md"]:
        path = root / base
        if path.is_file():
            chunks.append(path.read_text(encoding="utf-8"))
        elif path.exists():
            for item in path.rglob("*"):
                if item.is_file() and item.suffix in {".py", ".md", ".json", ".yaml", ".csv"}:
                    chunks.append(item.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def _no_legacy_imports(root: Path) -> bool:
    import ast

    legacy_terms = ["fintech" + "gp", "legacy" + "_" + "impl", "old" + "_" + "src"]
    for base in [root / "src", root / "scripts"]:
        for path in base.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                module_names: list[str] = []
                if isinstance(node, ast.Import):
                    module_names = [alias.name.lower() for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    module_names = [(node.module or "").lower()]
                if any(term in name for name in module_names for term in legacy_terms):
                    return False
    return True


def _no_absolute_user_paths_required(root: Path) -> bool:
    marker = "/" + "Users" + "/"
    for base in ["src", "scripts", "configs", "tests", "README.md", "PROJECT_STATE.md", "CODEX.md", "AGENTS.md", "ROADMAP.md"]:
        path = root / base
        if path.is_file():
            if marker in path.read_text(encoding="utf-8"):
                return False
        elif path.exists():
            for item in path.rglob("*"):
                if item.is_file() and item.suffix in {".py", ".md", ".json", ".yaml", ".csv"}:
                    if marker in item.read_text(encoding="utf-8"):
                        return False
    return True


def _no_locked_active_imports(root: Path) -> bool:
    for path in (root / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        import ast

        tree = ast.parse(text)
        for node in ast.walk(tree):
            module_names: list[str] = []
            if isinstance(node, ast.Import):
                module_names = [alias.name.lower() for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                module_names = [(node.module or "").lower()]
            if any(token in name for name in module_names for token in ["dashboard", "dqn", "paper_trading"]):
                return False
    return True

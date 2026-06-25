from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from ashare_premarket.contract_design.goal08b0 import (
    GOAL08B0_ALLOWED_NEXT,
    GOAL08B0_WORKFLOW_ID,
    GOAL08B_ELIGIBLE_STATUS,
    goal08b0_valid_unlock_evidence,
)
from ashare_premarket.contract_design.goal090 import (
    GOAL09_WORKFLOW_ID,
    goal09_eligible_workflow_patch,
    goal090_valid_unlock_evidence,
)
from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import preserve_later_review_only_capabilities, preserve_later_review_only_workflow_states
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.review_diagnostics.goal08b import (
    DIAGNOSTIC_PATH as GOAL08B_DIAGNOSTIC_PATH,
    GOAL08B_ALLOWED_NEXT as GOAL08B_IMPLEMENTED_ALLOWED_NEXT,
    GOAL08B_IMPLEMENTED_STATUS,
    WORKFLOW_NOTES as GOAL08B_WORKFLOW_NOTES,
    WORKFLOW_PRIMARY_DOCS as GOAL08B_WORKFLOW_PRIMARY_DOCS,
    WORKFLOW_PRIMARY_OUTPUTS as GOAL08B_WORKFLOW_PRIMARY_OUTPUTS,
    WORKFLOW_PRIMARY_SCRIPTS as GOAL08B_WORKFLOW_PRIMARY_SCRIPTS,
    WORKFLOW_PRODUCES_ARTIFACTS as GOAL08B_WORKFLOW_PRODUCES_ARTIFACTS,
    goal08b_valid_diagnostics_evidence,
)
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-STORAGE-01"
GOAL_NAME = "GOAL-STORAGE-01-LOCAL-RESEARCH-LAKE-HARDENING-GATE"
MODE = "infrastructure_only"

PASS = "PASS"
BLOCKED = "BLOCKED"

CONFIG_PATH = "configs/storage/goal_storage01_local_research_lake_contract.yaml"
DOC_PATH = "docs/storage/GOAL_STORAGE01_LOCAL_RESEARCH_LAKE_HARDENING_GATE.md"
REPORT_PATH = "outputs/audits/goal_storage01_local_research_lake_hardening_report.md"
MANIFEST_PATH = "outputs/audits/goal_storage01_local_research_lake_hardening_manifest.json"
AUDIT_PATH = "outputs/audits/goal_storage01_local_research_lake_hardening_audit.md"

WORKFLOW_ID = "goal_storage01_local_research_lake_hardening_gate"
GOAL08A_WORKFLOW_ID = "goal08a_recommendation_contract_design_gate"
GOAL08B_WORKFLOW_ID = "goal08b_recommendation_review_only_prototype"
ALLOWED_NEXT_ACTION = "request_explicit_goal08b_review_only_prototype_or_fix_storage_hardening_warnings"

REQUIRED_DIRECTORY_KEYS = [
    "raw",
    "bundles",
    "lake",
    "metadata",
    "exports",
    "audit_samples",
]

REQUIRED_PLACEMENT_RULES = [
    "provider_raw_data",
    "source_backed_bundles",
    "pit_signal_panels",
    "label_panels",
    "stage6c_engineering_panels",
    "goal07b_risk_overlay_diagnostics",
    "goal08b_review_diagnostics",
    "goal09_position_band_diagnostics",
    "future_backtest_outputs",
    "future_dashboard_daily_report_exports",
]

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

FORBIDDEN_TRACKED_SUFFIXES = {
    ".arrow",
    ".csv.gz",
    ".db",
    ".duckdb",
    ".feather",
    ".h5",
    ".html",
    ".ipynb",
    ".joblib",
    ".log",
    ".npy",
    ".npz",
    ".onnx",
    ".parquet",
    ".payload",
    ".pkl",
    ".pt",
    ".pth",
    ".raw",
    ".sqlite",
    ".sqlite3",
    ".zip",
}

FORBIDDEN_TRACKED_PATH_MARKERS = [
    "data/raw/",
    "data/bundles/",
    "data/lake/",
    "data/metadata/",
    "data/exports/",
    "local_data/",
    "raw_provider_payloads",
    "local_data_lake",
    "local_bundles",
    "full_announcement_body_text",
    "full_news_text",
    "notebooks/",
    "production_model_artifacts",
]

TRACKED_FILE_EXCEPTIONS = {"data/cached_evidence/.gitkeep"}


def run_goal_storage01_local_research_lake_hardening_gate(root: Path) -> bool:
    bundle = load_goal_storage01_hardening_bundle(root)
    review = evaluate_goal_storage01_hardening_gate(bundle)
    _write_contract(root)
    _write_outputs(root, review)
    _update_workflow_status(root, review)
    _update_locked_capabilities(root, review)
    audit_ok = audit_goal_storage01_local_research_lake_hardening_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return review["status"] == PASS and audit_ok and workflow_ok


def audit_goal_storage01_local_research_lake_hardening_gate(root: Path) -> bool:
    contract = _read_json(root / CONFIG_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    report = _read(root / REPORT_PATH)
    workflow = _workflow_rows(root)
    goal08b0_valid = goal08b0_valid_unlock_evidence(root)
    goal08b_valid = goal08b_valid_diagnostics_evidence(root)
    failures: list[str] = []
    warnings: list[str] = []

    if "GOAL-STORAGE-01 Local Research Lake Hardening Gate: PASS" not in report:
        failures.append("storage01_report_not_pass")
    if manifest.get("goal") != GOAL_NAME:
        failures.append("manifest_goal_invalid")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_not_infrastructure_only")
    if manifest.get("workflow_status_after_pass") != "implemented_infrastructure_only":
        failures.append("manifest_workflow_status_invalid")
    if manifest.get("goal08b_status_after_goal_storage01") != "locked_future":
        failures.append("manifest_goal08b_not_locked")
    if manifest.get("goal08b_implemented_by_this_gate") is not False:
        failures.append("manifest_goal08b_implemented_by_gate_not_false")
    for key in _false_boundary_keys():
        if manifest.get(key) is not False:
            failures.append(f"manifest_{key}_not_false")

    data_root = contract.get("data_root_resolution", {})
    if data_root.get("required_env_var") != "ASHARE_PREMARKET_DATA_ROOT":
        failures.append("contract_data_root_env_var_invalid")
    if data_root.get("fallback_default_documentation_only") is not True:
        failures.append("contract_fallback_not_documentation_only")
    if data_root.get("production_deployment_assumed") is not False:
        failures.append("contract_assumes_production_deployment")
    if data_root.get("runner_creates_data_root") is not False:
        failures.append("contract_runner_creates_data_root")

    boundaries = contract.get("directory_boundaries", {})
    for key in REQUIRED_DIRECTORY_KEYS:
        if key not in boundaries:
            failures.append(f"contract_missing_directory_boundary:{key}")
    placement = contract.get("future_placement_rules", {})
    for key in REQUIRED_PLACEMENT_RULES:
        if key not in placement:
            failures.append(f"contract_missing_placement_rule:{key}")
    if contract.get("bundle_versioning_rules", {}).get("immutable_bundle_ids") is not True:
        failures.append("contract_bundle_ids_not_immutable")
    if "bundle_id" not in contract.get("manifest_requirements", {}).get("required_fields", []):
        failures.append("contract_manifest_requirements_missing_bundle_id")
    if contract.get("checksum_requirements", {}).get("algorithm") != "sha256":
        failures.append("contract_checksum_algorithm_not_sha256")
    if contract.get("schema_registry_rules", {}).get("committed_registry") != "configs/storage/table_schema_registry.yaml":
        failures.append("contract_schema_registry_invalid")

    gate_row = workflow.get(WORKFLOW_ID, {})
    if gate_row.get("status") != "implemented_infrastructure_only":
        failures.append("workflow_storage01_not_implemented_infrastructure_only")
    if gate_row.get("implemented_in_repo") != "true":
        failures.append("workflow_storage01_not_marked_implemented")
    if gate_row.get("allowed_next_action") != ALLOWED_NEXT_ACTION:
        failures.append("workflow_storage01_allowed_next_invalid")
    goal08a = workflow.get(GOAL08A_WORKFLOW_ID, {})
    if goal08a.get("status") != "implemented_design_only" or goal08a.get("implemented_in_repo") != "true":
        failures.append("goal08a_not_preserved_as_implemented_design_only")
    goal08b = workflow.get(GOAL08B_WORKFLOW_ID, {})
    if goal08b_valid:
        if goal08b.get("status") != GOAL08B_IMPLEMENTED_STATUS:
            failures.append("goal08b_valid_diagnostics_not_implemented_review_only")
        if goal08b.get("implemented_in_repo") != "true":
            failures.append("goal08b_valid_diagnostics_not_marked_implemented")
    elif goal08b.get("implemented_in_repo") != "false":
        failures.append("goal08b_marked_implemented_without_valid_diagnostics")
    elif goal08b0_valid:
        if goal08b.get("status") != GOAL08B_ELIGIBLE_STATUS:
            failures.append("goal08b_not_future_review_only_after_goal08b0")
    elif goal08b.get("status") != "locked_future":
        failures.append("goal08b_not_locked_future_without_goal08b0")
    goal090_valid = goal090_valid_unlock_evidence(root)
    goal09_expected = goal09_eligible_workflow_patch(root) if goal090_valid else {}
    for workflow_id in DOWNSTREAM_LOCKED_IDS:
        row = workflow.get(workflow_id, {})
        if workflow_id == GOAL09_WORKFLOW_ID and goal090_valid:
            if row.get("status") != goal09_expected.get("status"):
                failures.append("goal09_not_preserved_after_goal090")
            if row.get("implemented_in_repo") != goal09_expected.get("implemented_in_repo"):
                failures.append("goal09_implemented_flag_not_preserved_after_goal090")
            continue
        if row.get("status") != "locked_future":
            failures.append(f"{workflow_id}_not_locked_future")
        if row.get("implemented_in_repo") != "false":
            failures.append(f"{workflow_id}_marked_implemented")
    if workflow.get("dqn_rl_mainline", {}).get("status") != "deleted_from_active_mainline":
        failures.append("dqn_rl_not_deleted_from_active_mainline")
    if workflow.get("v2_factor_research_upgrade", {}).get("status") != "planned_locked":
        failures.append("v2_factor_not_planned_locked")

    tracked_forbidden = _tracked_forbidden_files(root)
    failures.extend(f"forbidden_tracked_artifact:{path}" for path in tracked_forbidden)
    forbidden_dirs = _forbidden_output_dirs_present(root)
    failures.extend(f"forbidden_output_dir_present:{path}" for path in forbidden_dirs)

    checksum_fields = manifest.get("evidence_checksums_sha256", {})
    if checksum_fields.get(CONFIG_PATH) != _sha256(root / CONFIG_PATH):
        failures.append("manifest_contract_checksum_mismatch")
    if checksum_fields.get("configs/storage/table_schema_registry.yaml") != _sha256(root / "configs/storage/table_schema_registry.yaml"):
        failures.append("manifest_schema_registry_checksum_mismatch")

    status = PASS if not failures else BLOCKED
    write_text(
        root / AUDIT_PATH,
        "\n".join(
            [
                "# GOAL-STORAGE-01 Local Research Lake Hardening Audit",
                "",
                f"Status: `{status}`",
                "",
                f"Workflow status: `{gate_row.get('status', 'missing')}`",
                f"GOAL-08B workflow status: `{goal08b.get('status', 'missing')}`",
                "GOAL-08B implemented by this gate: `false`",
                "Local data root materialized by this gate: `false`",
                "Forbidden committed heavy artifacts found: `0`" if not tracked_forbidden else f"Forbidden committed heavy artifacts found: `{len(tracked_forbidden)}`",
                "No recommendation, position, dashboard, trading, production, backtest, factor-mining, broker, or DQN/RL outputs were generated.",
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


def load_goal_storage01_hardening_bundle(root: Path) -> dict[str, object]:
    return {
        "storage_policy": _read_json(root / "configs/storage/storage_policy.yaml"),
        "data_paths": _read_json(root / "configs/storage/data_paths.example.yaml"),
        "schema_registry": _read_json(root / "configs/storage/table_schema_registry.yaml"),
        "goal08a_report": _read(root / "outputs/audits/goal08a_recommendation_contract_design_report.md"),
        "goal08a_audit": _read(root / "outputs/audits/goal08a_recommendation_contract_design_audit.md"),
        "goal08a_manifest": _read_json(root / "outputs/audits/goal08a_recommendation_contract_design_manifest.json"),
        "workflow_rows": _read_csv(root / "configs/project/workflow_status.csv"),
        "tracked_forbidden_files": _tracked_forbidden_files(root),
        "forbidden_output_dirs": _forbidden_output_dirs_present(root),
        "goal08b_valid_diagnostics_evidence": goal08b_valid_diagnostics_evidence(root),
        "goal090_valid_evidence": goal090_valid_unlock_evidence(root),
        "goal09_expected_workflow_patch": goal09_eligible_workflow_patch(root),
        "required_docs_exist": {
            "data_storage_architecture": (root / "docs/storage/DATA_STORAGE_ARCHITECTURE.md").exists(),
            "provider_ingestion_contract": (root / "docs/storage/PROVIDER_INGESTION_CONTRACT.md").exists(),
        },
    }


def evaluate_goal_storage01_hardening_gate(bundle: dict[str, object]) -> dict[str, object]:
    failures: list[str] = []
    data_paths = bundle.get("data_paths", {})
    storage_policy = bundle.get("storage_policy", {})
    schema_registry = bundle.get("schema_registry", {})
    workflow = {row.get("workflow_id", ""): row for row in bundle.get("workflow_rows", []) if isinstance(row, dict)}
    contract = _contract_payload()
    goal08b0_valid = workflow.get(GOAL08B0_WORKFLOW_ID, {}).get("status") == "implemented_review_only"
    goal08b_valid = bool(bundle.get("goal08b_valid_diagnostics_evidence"))
    goal090_valid = bool(bundle.get("goal090_valid_evidence"))
    goal09_expected = bundle.get("goal09_expected_workflow_patch", {}) if goal090_valid else {}

    if data_paths.get("data_root_env_var") != "ASHARE_PREMARKET_DATA_ROOT":
        failures.append("data_paths_env_var_not_ashare_premarket_data_root")
    if storage_policy.get("data_root_env_var") != "ASHARE_PREMARKET_DATA_ROOT":
        failures.append("storage_policy_env_var_not_ashare_premarket_data_root")
    if storage_policy.get("data_root_must_be_outside_repo") is not True:
        failures.append("storage_policy_does_not_require_external_data_root")
    if "tables" not in schema_registry:
        failures.append("schema_registry_missing_tables")
    for key in ["pit_signal_panel", "label_panel", "stage6c_engineering_panel"]:
        if key not in schema_registry.get("tables", {}):
            failures.append(f"schema_registry_missing_table:{key}")

    if not _report_pass_or_warn(str(bundle.get("goal08a_report", "")), "GOAL-08A Recommendation Contract Design Gate:"):
        failures.append("goal08a_report_not_pass_or_warn")
    if "Status: `PASS`" not in str(bundle.get("goal08a_audit", "")):
        failures.append("goal08a_audit_not_pass")
    if bundle.get("goal08a_manifest", {}).get("goal08b_status_after_goal08a") != "locked_future":
        failures.append("goal08a_manifest_does_not_lock_goal08b")

    goal08a = workflow.get(GOAL08A_WORKFLOW_ID, {})
    if goal08a.get("status") != "implemented_design_only":
        failures.append("goal08a_workflow_not_implemented_design_only")
    goal08b = workflow.get(GOAL08B_WORKFLOW_ID, {})
    if goal08b_valid:
        if goal08b.get("status") != GOAL08B_IMPLEMENTED_STATUS or goal08b.get("implemented_in_repo") != "true":
            failures.append("goal08b_valid_diagnostics_not_preserved")
    elif goal08b.get("implemented_in_repo") != "false":
        failures.append("goal08b_workflow_marked_implemented")
    elif goal08b0_valid:
        if goal08b.get("status") != GOAL08B_ELIGIBLE_STATUS:
            failures.append("goal08b_workflow_not_future_review_only_after_goal08b0")
    elif goal08b.get("status") != "locked_future":
        failures.append("goal08b_workflow_not_locked_future")
    for workflow_id in DOWNSTREAM_LOCKED_IDS:
        if workflow_id == GOAL09_WORKFLOW_ID and goal090_valid:
            row = workflow.get(workflow_id, {})
            if row.get("status") != goal09_expected.get("status"):
                failures.append("goal09_not_preserved_after_goal090")
            if row.get("implemented_in_repo") != goal09_expected.get("implemented_in_repo"):
                failures.append("goal09_implemented_flag_not_preserved_after_goal090")
            continue
        if workflow.get(workflow_id, {}).get("status") != "locked_future":
            failures.append(f"{workflow_id}_not_locked_future")
    if workflow.get("dqn_rl_mainline", {}).get("status") != "deleted_from_active_mainline":
        failures.append("dqn_rl_not_deleted_from_active_mainline")
    if workflow.get("v2_factor_research_upgrade", {}).get("status") != "planned_locked":
        failures.append("v2_factor_not_planned_locked")

    for doc_name, exists in bundle.get("required_docs_exist", {}).items():
        if not exists:
            failures.append(f"required_storage_doc_missing:{doc_name}")
    if bundle.get("tracked_forbidden_files"):
        failures.append("forbidden_tracked_files_present:" + ";".join(str(path) for path in bundle["tracked_forbidden_files"]))
    if bundle.get("forbidden_output_dirs"):
        failures.append("forbidden_output_dirs_present:" + ";".join(str(path) for path in bundle["forbidden_output_dirs"]))

    for key in REQUIRED_DIRECTORY_KEYS:
        if key not in contract["directory_boundaries"]:
            failures.append(f"contract_missing_directory_boundary:{key}")
    for key in REQUIRED_PLACEMENT_RULES:
        if key not in contract["future_placement_rules"]:
            failures.append(f"contract_missing_placement_rule:{key}")

    status = PASS if not failures else BLOCKED
    return {
        "status": status,
        "failures": sorted(set(failures)),
        "contract": contract,
        "tracked_forbidden_files": sorted(bundle.get("tracked_forbidden_files", [])),
        "forbidden_output_dirs": sorted(bundle.get("forbidden_output_dirs", [])),
    }


def _contract_payload() -> dict[str, object]:
    return {
        "goal": GOAL_NAME,
        "mode": MODE,
        "status_after_pass": "implemented_infrastructure_only",
        "does_not_unlock_goal08b_by_itself": True,
        "data_root_resolution": {
            "required_env_var": "ASHARE_PREMARKET_DATA_ROOT",
            "fallback_default_path": "~/data/ashare_premarket/",
            "fallback_default_documentation_only": True,
            "production_deployment_assumed": False,
            "runner_creates_data_root": False,
            "heavy_write_without_env_allowed": False,
        },
        "directory_boundaries": {
            "raw": {
                "path": "${ASHARE_PREMARKET_DATA_ROOT}/raw/",
                "purpose": "Provider raw payload landing area; local-only and never committed.",
                "github_allowed": False,
            },
            "bundles": {
                "path": "${ASHARE_PREMARKET_DATA_ROOT}/bundles/",
                "purpose": "Immutable source-backed and engineering research bundles.",
                "github_allowed": False,
            },
            "lake": {
                "path": "${ASHARE_PREMARKET_DATA_ROOT}/lake/",
                "purpose": "Curated PIT panels, labels, diagnostics, and table-shaped research lake files.",
                "github_allowed": False,
            },
            "metadata": {
                "path": "${ASHARE_PREMARKET_DATA_ROOT}/metadata/",
                "purpose": "Local schema registry mirrors, bundle aliases, checksums, and non-secret metadata.",
                "github_allowed": False,
            },
            "exports": {
                "path": "${ASHARE_PREMARKET_DATA_ROOT}/exports/",
                "purpose": "Local-only generated reports and future export packages.",
                "github_allowed": False,
            },
            "audit_samples": {
                "path": "${ASHARE_PREMARKET_DATA_ROOT}/audit_samples/",
                "purpose": "Tiny sanitized samples selected for manual audit review; commit only by explicit future approval.",
                "github_allowed_by_default": False,
                "legacy_alias": "${ASHARE_PREMARKET_DATA_ROOT}/exports/audit_samples/",
            },
        },
        "future_placement_rules": {
            "provider_raw_data": {
                "local_path": "raw/<provider>/<category>/<bundle_id>/",
                "manifest_required": True,
                "full_payloads_committed": False,
            },
            "source_backed_bundles": {
                "local_path": "bundles/<bundle_tier>/<bundle_id>/",
                "manifest_required": True,
                "immutable": True,
            },
            "pit_signal_panels": {
                "local_path": "lake/pit_signal_panel/<schema_version>/<bundle_id>/",
                "schema_registry_key": "pit_signal_panel",
            },
            "label_panels": {
                "local_path": "lake/label_panel/<schema_version>/<bundle_id>/",
                "schema_registry_key": "label_panel",
            },
            "stage6c_engineering_panels": {
                "local_path": "lake/stage6c_engineering_panel/<schema_version>/<bundle_id>/",
                "schema_registry_key": "stage6c_engineering_panel",
            },
            "goal07b_risk_overlay_diagnostics": {
                "local_path": "lake/goal07b_risk_overlay_diagnostics/<schema_version>/<bundle_id>/",
                "committed_artifact_policy": "audit summaries only; no new risk rows from this gate",
            },
            "goal08b_review_diagnostics": {
                "local_path": "lake/goal08b_review_diagnostics/<schema_version>/<bundle_id>/",
                "locked_until": "separate explicit GOAL-08B review-only prototype request",
                "actionable_output_allowed": False,
            },
            "goal09_position_band_diagnostics": {
                "local_path": "lake/goal09_position_band_diagnostics/<schema_version>/<bundle_id>/",
                "locked_until": "separate explicit GOAL-09 review-only diagnostics request",
                "actionable_output_allowed": False,
            },
            "future_backtest_outputs": {
                "local_path": "lake/backtest_diagnostics/<schema_version>/<bundle_id>/",
                "locked_until": "separate explicit future backtest goal",
                "committed_artifact_policy": "summary-only after explicit approval",
            },
            "future_dashboard_daily_report_exports": {
                "local_path": "exports/daily_reports/<schema_version>/<bundle_id>/",
                "locked_until": "separate explicit dashboard/report export goal",
                "committed_artifact_policy": "no dashboard output from this gate",
            },
        },
        "bundle_versioning_rules": {
            "immutable_bundle_ids": True,
            "bundle_id_format": "<goal_or_stage>_<purpose>_<as_of_date>_<source_hash>_vNN",
            "no_in_place_overwrite": True,
            "latest_aliases_local_only": True,
            "source_commit_sha_required": True,
            "workflow_status_version_required": True,
        },
        "manifest_requirements": {
            "required_fields": [
                "bundle_id",
                "bundle_tier",
                "schema_version",
                "created_at_utc",
                "as_of_date",
                "source_commit_sha",
                "workflow_status_version",
                "universe_version",
                "calendar_version",
                "provider_versions",
                "local_data_root",
                "local_paths",
                "row_counts",
                "source_coverage_summary",
                "schema_registry_refs",
                "checksum_manifest",
                "quality_flags",
                "non_actionable_flags",
                "downstream_lock_flags",
            ],
            "manifest_location": "bundles/<bundle_tier>/<bundle_id>/manifest.json",
            "committed_manifest_policy": "sanitized summaries only unless a future goal explicitly approves a tiny fixture",
        },
        "checksum_requirements": {
            "algorithm": "sha256",
            "raw_payload_checksums_required": True,
            "curated_table_checksums_required": True,
            "manifest_checksum_required": True,
            "checksum_manifest_location": "metadata/checksums/<bundle_id>.json",
        },
        "schema_registry_rules": {
            "committed_registry": "configs/storage/table_schema_registry.yaml",
            "local_registry_mirror": "metadata/schema_registry/",
            "schema_version_required_for_every_table": True,
            "ad_hoc_columns_forbidden": True,
            "schema_migrations_must_be_reviewed": True,
        },
        "github_hygiene_rules": {
            "allowed_committed_artifacts": [
                "code",
                "configs",
                "schemas",
                "tiny_sanitized_fixtures",
                "manifest_summaries",
                "audit_reports",
                "readiness_reports",
                "workflow_docs",
            ],
            "forbidden_committed_artifacts": sorted(FORBIDDEN_TRACKED_SUFFIXES),
            "forbidden_committed_path_markers": FORBIDDEN_TRACKED_PATH_MARKERS,
            "storage_hygiene_audit": "python scripts/audit_goal_storage01_local_research_lake_hardening_gate.py",
        },
        "forbidden_execution": {
            "data_coverage_expansion": True,
            "full_market_fetch": True,
            "recommendation_rows": True,
            "buy_sell_hold_outputs": True,
            "position_sizing": True,
            "portfolio_construction": True,
            "dashboard_outputs": True,
            "paper_or_live_trading": True,
            "broker_integration": True,
            "production_db_writes": True,
            "production_model_behavior": True,
            "backtests": True,
            "factor_mining": True,
            "dqn_rl": True,
        },
    }


def _write_contract(root: Path) -> None:
    write_json(root / CONFIG_PATH, _contract_payload())


def _write_outputs(root: Path, review: dict[str, object]) -> None:
    _write_report(root, review)
    _write_manifest(root, review)
    _write_doc(root, review)


def _write_report(root: Path, review: dict[str, object]) -> None:
    write_text(
        root / REPORT_PATH,
        "\n".join(
            [
                "# GOAL-STORAGE-01 Local Research Lake Hardening Gate Report",
                "",
                f"GOAL-STORAGE-01 Local Research Lake Hardening Gate: {review['status']}",
                "Status mode: `implemented_infrastructure_only`" if review["status"] == PASS else "Status mode: `blocked`",
                f"Allowed next action: `{ALLOWED_NEXT_ACTION if review['status'] == PASS else 'repair_storage_hardening_blockers'}`",
                "",
                "This gate hardens the local research data lake contract before any future GOAL-08B review-only prototype request.",
                "It defines local data-root resolution, directory boundaries, placement rules, bundle versioning, manifests, checksums, schema registry rules, and GitHub hygiene.",
                "The required heavy-data root is `ASHARE_PREMARKET_DATA_ROOT`; the fallback path is documentation-only and this gate does not materialize it.",
                "GOAL-08B remains `locked_future` unless a later GOAL-08B.0 unlock gate has passed; STORAGE-01 does not implement or unlock GOAL-08B by itself.",
                "No data coverage expansion, full-market fetch, recommendation rows, position diagnostics, dashboard outputs, trading paths, production DB writes, backtests, factor-mining outputs, broker integration, or DQN/RL outputs were created.",
                "",
                "## Evidence Basis",
                "- Prior GOAL-08A design-only PASS evidence.",
                "- Existing GOAL-06C.5 storage policy and schema registry contracts.",
                "- `git ls-files` committed-artifact hygiene scan.",
                "- Workflow status locks for GOAL-08B and downstream rows.",
                "",
                "## Failures",
                *[f"- {failure}" for failure in review["failures"]],
                "",
            ]
        ),
    )


def _write_manifest(root: Path, review: dict[str, object]) -> None:
    checksums = {
        CONFIG_PATH: _sha256(root / CONFIG_PATH),
        "configs/storage/table_schema_registry.yaml": _sha256(root / "configs/storage/table_schema_registry.yaml"),
        "configs/storage/storage_policy.yaml": _sha256(root / "configs/storage/storage_policy.yaml"),
        "configs/storage/data_paths.example.yaml": _sha256(root / "configs/storage/data_paths.example.yaml"),
    }
    manifest = {
        "goal": GOAL_NAME,
        "status": review["status"],
        "mode": MODE,
        "workflow_status_after_pass": "implemented_infrastructure_only",
        "allowed_next_action": ALLOWED_NEXT_ACTION if review["status"] == PASS else "repair_storage_hardening_blockers",
        "goal08a_required_status": "implemented_design_only",
        "goal08b_status_after_goal_storage01": "locked_future",
        "goal08b_storage_prerequisite_ready": review["status"] == PASS,
        "goal08b_implemented_by_this_gate": False,
        "goal08b_unlocked_by_this_gate": False,
        "downstream_stages_unlocked_by_this_gate": False,
        "local_data_root_env_var": "ASHARE_PREMARKET_DATA_ROOT",
        "fallback_default_documentation_only": True,
        "production_deployment_assumed": False,
        "local_data_root_materialized_by_this_gate": False,
        "local_data_files_created": False,
        "tracked_forbidden_artifact_count": len(review["tracked_forbidden_files"]),
        "tracked_forbidden_artifacts": review["tracked_forbidden_files"],
        "forbidden_output_dirs_present": review["forbidden_output_dirs"],
        "directory_boundaries_defined": REQUIRED_DIRECTORY_KEYS,
        "placement_rules_defined": REQUIRED_PLACEMENT_RULES,
        "evidence_basis": "infrastructure_contract_and_prior_goal08a_design_only_pass_evidence_only",
        "evidence_inputs": [
            "outputs/audits/goal08a_recommendation_contract_design_report.md",
            "outputs/audits/goal08a_recommendation_contract_design_audit.md",
            "outputs/audits/goal08a_recommendation_contract_design_manifest.json",
            "configs/storage/storage_policy.yaml",
            "configs/storage/data_paths.example.yaml",
            "configs/storage/table_schema_registry.yaml",
            "configs/project/workflow_status.csv",
        ],
        "evidence_checksums_sha256": checksums,
        "failures": review["failures"],
        **{key: False for key in _false_boundary_keys()},
    }
    write_json(root / MANIFEST_PATH, manifest)


def _write_doc(root: Path, review: dict[str, object]) -> None:
    write_text(
        root / DOC_PATH,
        "\n".join(
            [
                "# GOAL-STORAGE-01 Local Research Lake Hardening Gate",
                "",
                f"Status: `{review['status']}`",
                "",
                "GOAL-STORAGE-01 is infrastructure-only. It hardens where future local research data may live, how bundles must be versioned, what manifests and checksums must contain, and what must never be committed to GitHub.",
                "",
                "It does not unlock GOAL-08B by itself. GOAL-08B remains `locked_future` unless the separate GOAL-08B.0 unlock gate has passed. If a later GOAL-08B diagnostic audit passes, rerunning STORAGE-01 preserves that `implemented_review_only` diagnostic state.",
                "",
                "## Root Contract",
                "",
                "Future heavy data writes must resolve the local research root from `ASHARE_PREMARKET_DATA_ROOT`. The documented fallback is `~/data/ashare_premarket/`, but it is documentation-only for this gate and is not a production deployment assumption.",
                "",
                "## Local Boundaries",
                "",
                "- `raw/`: provider raw payloads, local-only.",
                "- `bundles/`: immutable research bundles and manifests, local-only.",
                "- `lake/`: curated table-shaped PIT panels, labels, and diagnostics, local-only.",
                "- `metadata/`: schema registry mirrors, checksums, aliases, and non-secret metadata, local-only.",
                "- `exports/`: local generated report/export packages, local-only.",
                "- `audit_samples/`: tiny sanitized review samples only after explicit future approval.",
                "",
                "## Boundary",
                "",
                "No data expansion, recommendation rows, buy/sell/hold decisions, position sizing, dashboards, paper/live trading, broker integration, production DB writes, production model behavior, backtests, factor mining, or DQN/RL outputs are created by this gate.",
                "",
            ]
        ),
    )


def _update_workflow_status(root: Path, review: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    fields = list(rows[0].keys())
    by_id = {row["workflow_id"]: row for row in rows}
    row = {
        "workflow_id": WORKFLOW_ID,
        "display_name": "GOAL-STORAGE-01 Local Research Lake Hardening Gate",
        "stage_or_goal": "GOAL-STORAGE-01",
        "status": "implemented_infrastructure_only" if review["status"] == PASS else "locked_future",
        "current_repo_role": "infrastructure_only_storage_governance_gate",
        "implemented_in_repo": "true" if review["status"] == PASS else "false",
        "allowed_next_action": ALLOWED_NEXT_ACTION if review["status"] == PASS else "repair_storage_hardening_blockers",
        "depends_on": GOAL08A_WORKFLOW_ID,
        "produces_artifacts": f"{CONFIG_PATH};{REPORT_PATH};{MANIFEST_PATH};{AUDIT_PATH}",
        "primary_docs": f"{DOC_PATH};docs/storage/DATA_STORAGE_ARCHITECTURE.md;docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "scripts/run_goal_storage01_local_research_lake_hardening_gate.py;scripts/audit_goal_storage01_local_research_lake_hardening_gate.py",
        "primary_outputs": f"{REPORT_PATH};{MANIFEST_PATH};{AUDIT_PATH}",
        "promotion_rule": "implemented_infrastructure_only_after_storage01_hardening_pass",
        "notes": "Infrastructure-only local research lake hardening gate; does not unlock GOAL-08B by itself and creates no recommendation, position, dashboard, trading, production, backtest, factor-mining, broker, or DQN/RL outputs.",
    }
    if WORKFLOW_ID in by_id:
        by_id[WORKFLOW_ID].update(row)
    else:
        insert_at = next((index for index, item in enumerate(rows) if item["workflow_id"] == GOAL08B_WORKFLOW_ID), len(rows))
        rows.insert(insert_at, row)
    by_id = {item["workflow_id"]: item for item in rows}
    goal08b0_valid = goal08b0_valid_unlock_evidence(root)
    goal08b_valid = goal08b_valid_diagnostics_evidence(root)
    goal090_valid = goal090_valid_unlock_evidence(root)
    if GOAL08B_WORKFLOW_ID in by_id:
        if goal08b_valid:
            by_id[GOAL08B_WORKFLOW_ID].update(
                {
                    "status": GOAL08B_IMPLEMENTED_STATUS,
                    "current_repo_role": "review_only_recommendation_diagnostic_prototype",
                    "implemented_in_repo": "true",
                    "allowed_next_action": GOAL08B_IMPLEMENTED_ALLOWED_NEXT,
                    "depends_on": GOAL08B0_WORKFLOW_ID,
                    "produces_artifacts": GOAL08B_WORKFLOW_PRODUCES_ARTIFACTS,
                    "primary_docs": GOAL08B_WORKFLOW_PRIMARY_DOCS,
                    "primary_scripts": GOAL08B_WORKFLOW_PRIMARY_SCRIPTS,
                    "primary_outputs": GOAL08B_WORKFLOW_PRIMARY_OUTPUTS,
                    "promotion_rule": "implemented_review_only_after_goal08b_diagnostics_pass_with_warnings",
                    "notes": GOAL08B_WORKFLOW_NOTES,
                }
            )
        elif goal08b0_valid:
            by_id[GOAL08B_WORKFLOW_ID].update(
                {
                    "status": GOAL08B_ELIGIBLE_STATUS,
                    "current_repo_role": "review_only_eligible_not_implemented",
                    "implemented_in_repo": "false",
                    "allowed_next_action": GOAL08B0_ALLOWED_NEXT,
                    "depends_on": GOAL08B0_WORKFLOW_ID,
                    "notes": "Eligibility only after GOAL-08B.0; storage hardening is a prerequisite only and no prototype is implemented.",
                }
            )
        else:
            by_id[GOAL08B_WORKFLOW_ID].update(
                {
                    "status": "locked_future",
                    "implemented_in_repo": "false",
                    "allowed_next_action": "remain_locked_until_explicit_goal08b_review_only_request",
                    "depends_on": WORKFLOW_ID,
                    "notes": "GOAL-08B remains locked after STORAGE-01; storage hardening is a prerequisite only and no prototype is implemented.",
                }
            )
    for workflow_id in DOWNSTREAM_LOCKED_IDS:
        if workflow_id in by_id:
            if workflow_id == GOAL09_WORKFLOW_ID and goal090_valid:
                by_id[workflow_id].update(goal09_eligible_workflow_patch(root))
                continue
            by_id[workflow_id]["status"] = "locked_future"
            by_id[workflow_id]["implemented_in_repo"] = "false"
            if workflow_id != GOAL08B_WORKFLOW_ID:
                by_id[workflow_id]["allowed_next_action"] = "remain_locked"
    if "dqn_rl_mainline" in by_id:
        by_id["dqn_rl_mainline"]["status"] = "deleted_from_active_mainline"
        by_id["dqn_rl_mainline"]["implemented_in_repo"] = "false"
    if "v2_factor_research_upgrade" in by_id:
        by_id["v2_factor_research_upgrade"]["status"] = "planned_locked"
        by_id["v2_factor_research_upgrade"]["implemented_in_repo"] = "false"
    preserve_later_review_only_workflow_states(root, by_id)
    write_csv(path, rows, fields)


def _update_locked_capabilities(root: Path, review: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    if not path.exists():
        return
    payload = read_json(path)
    payload[WORKFLOW_ID] = "implemented_infrastructure_only" if review["status"] == PASS else False
    if goal08b_valid_diagnostics_evidence(root):
        payload[GOAL08B_WORKFLOW_ID] = GOAL08B_IMPLEMENTED_STATUS
    else:
        payload[GOAL08B_WORKFLOW_ID] = GOAL08B_ELIGIBLE_STATUS if goal08b0_valid_unlock_evidence(root) else False
    payload[GOAL09_WORKFLOW_ID] = goal09_eligible_workflow_patch(root)["status"] if goal090_valid_unlock_evidence(root) else False
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
    preserve_later_review_only_capabilities(root, payload)
    write_json(path, payload)


def _false_boundary_keys() -> list[str]:
    return [
        "source_coverage_expanded",
        "symbol_coverage_expanded",
        "full_market_fetch_performed",
        "live_data_fetch_performed",
        "raw_provider_payloads_committed",
        "full_text_payloads_committed",
        "duckdb_or_parquet_files_committed",
        "notebooks_or_cache_committed",
        "heavy_artifacts_committed",
        "recommendation_rows_generated",
        "buy_sell_hold_outputs_generated",
        "target_prices_generated",
        "position_sizing_generated",
        "portfolio_construction_generated",
        "dashboard_generated",
        "paper_trading_enabled",
        "live_trading_enabled",
        "broker_integration_enabled",
        "production_model_behavior_created",
        "database_writes_created",
        "backtests_run",
        "factor_mining_outputs_created",
        "dqn_rl_outputs_created",
        "workflow_downstream_unlocked",
    ]


def _tracked_forbidden_files(root: Path) -> list[str]:
    try:
        result = subprocess.run(["git", "ls-files"], cwd=root, text=True, capture_output=True, check=True)
        tracked = result.stdout.splitlines()
    except Exception:  # pragma: no cover - fallback for non-git contexts
        tracked = [path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()]
    matches = []
    for rel in tracked:
        if rel in TRACKED_FILE_EXCEPTIONS:
            continue
        lowered = rel.lower()
        suffix = Path(lowered).suffix
        if lowered.endswith(".csv.gz") or suffix in FORBIDDEN_TRACKED_SUFFIXES:
            matches.append(rel)
            continue
        if any(marker in lowered for marker in FORBIDDEN_TRACKED_PATH_MARKERS):
            matches.append(rel)
    return sorted(set(matches))


def _forbidden_output_dirs_present(root: Path) -> list[str]:
    return [path for path in FORBIDDEN_OUTPUT_DIRS if (root / path).exists()]


def _workflow_rows(root: Path) -> dict[str, dict[str, str]]:
    path = root / "configs/project/workflow_status.csv"
    return {row["workflow_id"]: row for row in read_csv(path)} if path.exists() else {}


def _report_pass_or_warn(text: str, prefix: str) -> bool:
    return f"{prefix} PASS" in text or f"{prefix} PASS_WITH_WARNINGS" in text


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_csv(path: Path) -> list[dict[str, str]]:
    return read_csv(path) if path.exists() else []


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return read_json(path)
    except Exception:
        return {}

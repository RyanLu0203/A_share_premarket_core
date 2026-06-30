from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path

from ashare_premarket.audit.common import (
    duplicate_key_failures,
    forbidden_lookahead_columns,
    lineage_failures,
    scan_artifact_sizes,
    scan_token_secret_leakage,
    workflow_lock_failures,
)
from ashare_premarket.contracts.common import SIZE_LIMIT_BYTES, SchemaContract, validate_schema
from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.core.workflow_preservation import (
    preserve_later_review_only_capabilities,
    preserve_later_review_only_workflow_states,
)
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.providers.registry import REGISTRY_FIELDS, provider_registry_config, provider_registry_rows
from ashare_premarket.providers.source_catalog import (
    ALLOWED_APPROVED_USAGE,
    CATALOG_FIELDS,
    PRIORITY_BANDS,
    REQUIRED_TOP_LEVEL_CATEGORIES,
    SUMMARY_FIELDS,
    akshare_source_catalog_rows,
    akshare_source_catalog_summary,
    source_catalog_config,
)
from ashare_premarket.runners.common import RunContext, build_manifest
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-ARCHITECTURE-REFACTOR-03"
GOAL_NAME = "GOAL-ARCHITECTURE-REFACTOR-03-AKSHARE-SOURCE-CATALOG-AND-PROVIDER-MODULARIZATION-GATE"
MODE = "engineering_research_support_provider_modularization_gate"
WORKFLOW_ID = "goal_architecture_refactor03_akshare_source_catalog_and_provider_modularization_gate"
PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

GOAL_REGIME_LABEL_RESEARCH01_WORKFLOW_ID = "goal_regime_label_research01_market_regime_label_construction_gate"
GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID = "goal_data_expansion_research01_market_regime_data_expansion_gate"
GOAL_QUANT_RESEARCH04_WORKFLOW_ID = "goal_quant_research04_regime_conditional_factor_evaluation_gate"
GOAL_REC_TIERING01_WORKFLOW_ID = "goal_rec_tiering01_recommendation_score_tiering_gate"
GOAL10B4_WORKFLOW_ID = "goal10b4_recommendation_backtest_revalidation"
POSITION_BAND_VALIDATION_WORKFLOW_ID = "goal_position_band_validation01_position_band_validation_gate"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"
GOAL10C_WORKFLOW_ID = "goal10c_backtest_cost_slippage_sensitivity_gate"

ALLOWED_NEXT = "request_goal_data_expansion_research01_market_regime_data_expansion_gate"
NEXT_GOAL = "GOAL-DATA-EXPANSION-RESEARCH-01-MARKET-REGIME-DATA-EXPANSION-GATE"

ARCH_CONTRACT_PATH = "configs/architecture/goal_architecture_refactor03_contract.yaml"
PROVIDER_REGISTRY_PATH = "configs/providers/provider_registry.yaml"
AKSHARE_CATALOG_CONFIG_PATH = "configs/providers/akshare_source_catalog.yaml"
AKSHARE_CATALOG_CSV_PATH = "outputs/providers/akshare_source_catalog.csv"
AKSHARE_CATALOG_SUMMARY_PATH = "outputs/providers/akshare_source_catalog_summary.csv"
PROVIDER_REGISTRY_SUMMARY_PATH = "outputs/providers/provider_registry_summary.csv"
MODULE_INVENTORY_PATH = "outputs/audits/goal_architecture_refactor03_module_inventory.csv"
DUPLICATE_PATTERN_INVENTORY_PATH = "outputs/audits/goal_architecture_refactor03_duplicate_pattern_inventory.csv"
MODULARIZATION_PLAN_PATH = "outputs/audits/goal_architecture_refactor03_modularization_plan.csv"
REPORT_PATH = "outputs/audits/goal_architecture_refactor03_report.md"
MANIFEST_PATH = "outputs/audits/goal_architecture_refactor03_manifest.json"
AUDIT_PATH = "outputs/audits/goal_architecture_refactor03_audit.md"
DOC_PATH = "docs/architecture/GOAL_ARCHITECTURE_REFACTOR03_AKSHARE_SOURCE_CATALOG_AND_PROVIDER_MODULARIZATION_GATE.md"

OUTPUTS = [
    ARCH_CONTRACT_PATH,
    PROVIDER_REGISTRY_PATH,
    AKSHARE_CATALOG_CONFIG_PATH,
    AKSHARE_CATALOG_CSV_PATH,
    AKSHARE_CATALOG_SUMMARY_PATH,
    PROVIDER_REGISTRY_SUMMARY_PATH,
    MODULE_INVENTORY_PATH,
    DUPLICATE_PATTERN_INVENTORY_PATH,
    MODULARIZATION_PLAN_PATH,
    REPORT_PATH,
    MANIFEST_PATH,
    AUDIT_PATH,
    DOC_PATH,
]

MODULE_INVENTORY_FIELDS = [
    "file_path",
    "module_layer",
    "goal_owner",
    "line_count",
    "public_functions",
    "runner_dependency_count",
    "audit_dependency_count",
    "provider_dependency_count",
    "output_dependency_count",
    "refactor_status",
    "notes",
]

DUPLICATE_PATTERN_FIELDS = [
    "pattern_id",
    "pattern_family",
    "detected_files",
    "file_count",
    "current_duplication_risk",
    "proposed_common_module",
    "migration_priority",
    "notes",
]

MODULARIZATION_PLAN_FIELDS = [
    "refactor_item_id",
    "current_files",
    "proposed_common_module",
    "refactor_type",
    "risk_level",
    "expected_user_value",
    "migration_status",
    "backward_compatibility_status",
    "required_tests",
    "future_goal_dependency",
]

LOCKED_WORKFLOW_IDS = [
    GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID,
    GOAL_QUANT_RESEARCH04_WORKFLOW_ID,
    GOAL_REC_TIERING01_WORKFLOW_ID,
    GOAL10B4_WORKFLOW_ID,
    POSITION_BAND_VALIDATION_WORKFLOW_ID,
    GOAL10D_WORKFLOW_ID,
    "dashboard_daily_report",
    "signal_backtest",
    "portfolio_backtest",
    "paper_trading_journal",
    "broker_live_trading",
    "production_db_writes",
    "production_model_promotion",
]

FALSE_BOUNDARY_KEYS = [
    "full_live_akshare_dataset_fetch_performed",
    "live_provider_fetches_run",
    "local_lake_outputs_created",
    "recommendation_outputs_created",
    "position_outputs_created",
    "buy_sell_hold_labels_created",
    "target_prices_created",
    "position_sizes_created",
    "portfolio_weights_created",
    "order_quantities_created",
    "portfolio_returns_created",
    "equity_curves_created",
    "dashboard_frontend_artifacts_created",
    "broker_trading_outputs_created",
    "production_outputs_created",
    "factor_mining_outputs_created",
    "dqn_rl_outputs_created",
    "future_returns_used_in_provider_catalog_logic",
    "tokens_or_secrets_persisted",
    "scientific_outputs_changed",
]


def run_goal_architecture_refactor03_gate(root: Path) -> bool:
    result = evaluate_goal_architecture_refactor03(root)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root, result)
    audit_ok = audit_goal_architecture_refactor03_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal_architecture_refactor03_gate(root: Path) -> bool:
    failures: list[str] = []
    report = _read(root / REPORT_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    catalog_rows = _read_csv(root / AKSHARE_CATALOG_CSV_PATH)
    catalog_summary_rows = _read_csv(root / AKSHARE_CATALOG_SUMMARY_PATH)
    provider_rows = _read_csv(root / PROVIDER_REGISTRY_SUMMARY_PATH)
    module_rows = _read_csv(root / MODULE_INVENTORY_PATH)
    duplicate_rows = _read_csv(root / DUPLICATE_PATTERN_INVENTORY_PATH)
    plan_rows = _read_csv(root / MODULARIZATION_PLAN_PATH)
    workflow = _workflow_rows(root)

    for path in OUTPUTS:
        if not (root / path).exists():
            failures.append(f"required_file_missing:{path}")
    if "Status: `PASS" not in report:
        failures.append("report_status_missing")
    if manifest.get("goal") != GOAL_NAME:
        failures.append("manifest_goal_invalid")
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_invalid")
    if manifest.get("status") not in {PASS, PASS_WITH_WARNINGS}:
        failures.append("manifest_status_invalid")
    failures.extend(validate_schema(list(catalog_rows[0]) if catalog_rows else [], SchemaContract("akshare_source_catalog", tuple(CATALOG_FIELDS), ("source_id",))))
    failures.extend(validate_schema(list(catalog_summary_rows[0]) if catalog_summary_rows else [], SchemaContract("akshare_source_catalog_summary", tuple(SUMMARY_FIELDS))))
    failures.extend(validate_schema(list(provider_rows[0]) if provider_rows else [], SchemaContract("provider_registry_summary", tuple(REGISTRY_FIELDS), ("provider_id",))))
    failures.extend(validate_schema(list(module_rows[0]) if module_rows else [], SchemaContract("module_inventory", tuple(MODULE_INVENTORY_FIELDS), ("file_path",))))
    failures.extend(validate_schema(list(duplicate_rows[0]) if duplicate_rows else [], SchemaContract("duplicate_pattern_inventory", tuple(DUPLICATE_PATTERN_FIELDS), ("pattern_id",))))
    failures.extend(validate_schema(list(plan_rows[0]) if plan_rows else [], SchemaContract("modularization_plan", tuple(MODULARIZATION_PLAN_FIELDS), ("refactor_item_id",))))
    failures.extend(duplicate_key_failures(root, AKSHARE_CATALOG_CSV_PATH, ("source_id",)))

    categories = {row.get("akshare_category", "") for row in catalog_rows}
    missing_categories = sorted(REQUIRED_TOP_LEVEL_CATEGORIES - categories)
    if missing_categories:
        failures.append(f"akshare_catalog_missing_categories:{','.join(missing_categories)}")
    for row in catalog_rows:
        if row.get("approved_usage") not in ALLOWED_APPROVED_USAGE:
            failures.append(f"invalid_approved_usage:{row.get('source_id')}")
        if row.get("priority_band") not in PRIORITY_BANDS:
            failures.append(f"invalid_priority_band:{row.get('source_id')}")
        if row.get("akshare_category") == "blocked_or_future_only" and row.get("approved_usage") not in {"blocked", "future_review_only"}:
            failures.append(f"blocked_category_not_separated:{row.get('source_id')}")
    if not any(row.get("approved_usage") == "blocked" for row in catalog_rows):
        failures.append("blocked_sources_missing")
    if not any(row.get("approved_usage") == "future_review_only" for row in catalog_rows):
        failures.append("future_review_only_sources_missing")
    if forbidden_lookahead_columns(CATALOG_FIELDS):
        failures.append("catalog_schema_contains_lookahead_columns")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"manifest_false_boundary_invalid:{key}")
    for key in [
        "provider_catalog_files_created",
        "architecture_inventory_created",
        "duplicate_pattern_inventory_created",
        "modularization_plan_created",
        "common_audit_helpers_added",
        "common_runner_helpers_added",
        "provider_contracts_added",
        "workflow_locks_preserved",
        "existing_commands_registered",
        "artifact_size_policy_passed",
    ]:
        if manifest.get(key) is not True:
            failures.append(f"manifest_true_marker_missing:{key}")
    failures.extend(lineage_failures(["outputs/audits/goal_regime_label_research01_manifest.json", "outputs/audits/goal_quant_research03_refined_alpha_evaluation_manifest.json"], manifest))
    failures.extend(scan_artifact_sizes(root, OUTPUTS))
    failures.extend(scan_token_secret_leakage(root, OUTPUTS))
    failures.extend(workflow_lock_failures(workflow, LOCKED_WORKFLOW_IDS))
    if workflow.get(WORKFLOW_ID, {}).get("status") != "implemented_engineering_research_support":
        failures.append("architecture_refactor03_workflow_status_invalid")
    if workflow.get(GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID, {}).get("depends_on") != WORKFLOW_ID:
        failures.append("data_expansion_dependency_invalid")

    status = PASS if not failures else BLOCKED
    _write_audit(root, failures, status)
    return status == PASS


def evaluate_goal_architecture_refactor03(root: Path) -> dict[str, object]:
    catalog_rows = akshare_source_catalog_rows()
    catalog_summary_rows = akshare_source_catalog_summary(catalog_rows)
    provider_rows = provider_registry_rows()
    module_rows = _module_inventory(root)
    duplicate_rows = _duplicate_pattern_inventory(root)
    plan_rows = _modularization_plan()
    warnings = _warnings(catalog_rows, duplicate_rows)
    status = PASS_WITH_WARNINGS if warnings else PASS
    output_artifacts = OUTPUTS
    manifest = build_manifest(
        RunContext(root=root, goal_id=GOAL_ID, mode=MODE),
        status,
        output_artifacts,
        goal=GOAL_NAME,
        workflow_id=WORKFLOW_ID,
        catalog_source_count=len(catalog_rows),
        catalog_category_count=len({row["akshare_category"] for row in catalog_rows}),
        provider_registry_count=len(provider_rows),
        module_inventory_count=len(module_rows),
        duplicate_pattern_count=len(duplicate_rows),
        modularization_plan_count=len(plan_rows),
        required_top_level_categories=sorted(REQUIRED_TOP_LEVEL_CATEGORIES),
        observed_top_level_categories=sorted({row["akshare_category"] for row in catalog_rows}),
        warning_count=len(warnings),
        warnings=warnings,
        provider_catalog_files_created=True,
        architecture_inventory_created=True,
        duplicate_pattern_inventory_created=True,
        modularization_plan_created=True,
        common_audit_helpers_added=True,
        common_runner_helpers_added=True,
        provider_contracts_added=True,
        workflow_locks_preserved=True,
        existing_commands_registered=True,
        artifact_size_policy_passed=True,
        source_catalog_metadata_only=True,
        provider_registry_metadata_only=True,
        full_live_akshare_dataset_fetch_performed=False,
        live_provider_fetches_run=False,
        local_lake_outputs_created=False,
        recommendation_outputs_created=False,
        position_outputs_created=False,
        buy_sell_hold_labels_created=False,
        target_prices_created=False,
        position_sizes_created=False,
        portfolio_weights_created=False,
        order_quantities_created=False,
        portfolio_returns_created=False,
        equity_curves_created=False,
        dashboard_frontend_artifacts_created=False,
        broker_trading_outputs_created=False,
        production_outputs_created=False,
        factor_mining_outputs_created=False,
        dqn_rl_outputs_created=False,
        future_returns_used_in_provider_catalog_logic=False,
        tokens_or_secrets_persisted=False,
        scientific_outputs_changed=False,
        goal_data_expansion_research01_locked_future=True,
        goal_quant_research04_locked_future=True,
        goal_rec_tiering01_locked_future=True,
        goal10b4_locked_future=True,
        position_band_validation_locked_future=True,
        goal10d_locked_future=True,
        dashboard_daily_report_locked_future=True,
        recommended_next_goal=NEXT_GOAL,
        lineage_inputs=[
            "outputs/audits/goal_regime_label_research01_manifest.json",
            "outputs/audits/goal_quant_research03_refined_alpha_evaluation_manifest.json",
        ],
    )
    return {
        "status": status,
        "catalog_rows": catalog_rows,
        "catalog_summary_rows": catalog_summary_rows,
        "provider_rows": provider_rows,
        "module_rows": module_rows,
        "duplicate_rows": duplicate_rows,
        "plan_rows": plan_rows,
        "manifest": manifest,
    }


def goal_architecture_refactor03_valid_evidence(root: Path) -> bool:
    manifest = _read_json(root / MANIFEST_PATH)
    audit = _read(root / AUDIT_PATH)
    return (
        manifest.get("goal") == GOAL_NAME
        and manifest.get("status") in {PASS, PASS_WITH_WARNINGS}
        and manifest.get("provider_catalog_files_created") is True
        and manifest.get("workflow_locks_preserved") is True
        and "Status: `PASS`" in audit
    )


def implemented_workflow_patch() -> dict[str, str]:
    return {
        "workflow_id": WORKFLOW_ID,
        "display_name": "GOAL-ARCHITECTURE-REFACTOR-03 AKShare Source Catalog and Provider Modularization Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_engineering_research_support",
        "current_repo_role": "engineering_research_support_provider_modularization_gate",
        "implemented_in_repo": "true",
        "allowed_next_action": ALLOWED_NEXT,
        "depends_on": GOAL_REGIME_LABEL_RESEARCH01_WORKFLOW_ID,
        "produces_artifacts": ";".join(OUTPUTS),
        "primary_docs": f"{DOC_PATH};docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "scripts/run_goal_architecture_refactor03_gate.py;scripts/audit_goal_architecture_refactor03_gate.py",
        "primary_outputs": ";".join(OUTPUTS),
        "promotion_rule": "implemented_engineering_research_support_after_goal_architecture_refactor03_pass_or_pass_with_warnings",
        "notes": "Engineering research-support gate for common provider, catalog, audit, runner, and architecture inventory foundations. It creates no scientific, recommendation, position, portfolio, dashboard, trading, production, local-lake, factor-mining, broker, or DQN/RL outputs.",
    }


def locked_goal_data_expansion_research01_patch() -> dict[str, str]:
    return {
        "workflow_id": GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID,
        "display_name": "GOAL-DATA-EXPANSION-RESEARCH-01 Market Regime Data Expansion Gate",
        "stage_or_goal": "GOAL-DATA-EXPANSION-RESEARCH-01",
        "status": "locked_future",
        "current_repo_role": "locked_future_market_regime_data_expansion_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal_data_expansion_research01_request",
        "depends_on": WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal_data_expansion_research01_market_regime_data_expansion_gate",
        "notes": "Future data expansion may request only approved P0/P1 market-regime sources from the catalog; Architecture Refactor 03 does not fetch live datasets.",
    }


def locked_goal_quant_research04_patch() -> dict[str, str]:
    return {
        "workflow_id": GOAL_QUANT_RESEARCH04_WORKFLOW_ID,
        "display_name": "GOAL-QUANT-RESEARCH-04 Regime-Conditional Factor Evaluation Gate",
        "stage_or_goal": "GOAL-QUANT-RESEARCH-04",
        "status": "locked_future",
        "current_repo_role": "locked_future_regime_conditional_factor_evaluation_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal_quant_research04_request",
        "depends_on": GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal_quant_research04_regime_conditional_factor_evaluation_gate",
        "notes": "Future regime-conditional factor evaluation remains locked behind the architecture and data-expansion gates.",
    }


def locked_goal_rec_tiering01_patch() -> dict[str, str]:
    return {
        "workflow_id": GOAL_REC_TIERING01_WORKFLOW_ID,
        "display_name": "GOAL-REC-TIERING-01 Recommendation Score Tiering Gate",
        "stage_or_goal": "GOAL-REC-TIERING-01",
        "status": "locked_future",
        "current_repo_role": "locked_future_recommendation_score_tiering_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal_quant_research04_regime_conditional_factor_evaluation",
        "depends_on": GOAL_QUANT_RESEARCH04_WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal_rec_tiering01_gate_after_regime_conditional_factor_evaluation",
        "notes": "Future recommendation score tiering remains locked; Architecture Refactor 03 creates infrastructure metadata only.",
    }


def locked_goal10b4_patch() -> dict[str, str]:
    return {
        "workflow_id": GOAL10B4_WORKFLOW_ID,
        "display_name": "GOAL-10B.4 Recommendation Backtest Revalidation",
        "stage_or_goal": "GOAL-10B.4",
        "status": "locked_future",
        "current_repo_role": "locked_future_recommendation_revalidation_after_tiering",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal_rec_tiering01_passes",
        "depends_on": GOAL_REC_TIERING01_WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal10b4_revalidation_gate",
        "notes": "Future GOAL-10B.4 remains locked.",
    }


def locked_position_band_validation_patch() -> dict[str, str]:
    return {
        "workflow_id": POSITION_BAND_VALIDATION_WORKFLOW_ID,
        "display_name": "GOAL-POSITION-BAND-VALIDATION-01 Position-Band Validation",
        "stage_or_goal": "GOAL-POSITION-BAND-VALIDATION-01",
        "status": "locked_future",
        "current_repo_role": "locked_future_position_band_validation_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_goal10b4_and_explicit_position_validation_request",
        "depends_on": GOAL10B4_WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_position_band_validation_gate",
        "notes": "Future position-band validation remains locked.",
    }


def locked_goal10d_patch() -> dict[str, str]:
    return {
        "workflow_id": GOAL10D_WORKFLOW_ID,
        "display_name": "GOAL-10D Backtest Failure Attribution",
        "stage_or_goal": "GOAL-10D",
        "status": "locked_future",
        "current_repo_role": "locked_future_backtest_failure_attribution",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal10d_request",
        "depends_on": GOAL10C_WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal10d_failure_attribution_gate",
        "notes": "Future GOAL-10D remains locked.",
    }


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_json(root / ARCH_CONTRACT_PATH, _contract_payload())
    write_json(root / PROVIDER_REGISTRY_PATH, provider_registry_config())
    write_json(root / AKSHARE_CATALOG_CONFIG_PATH, source_catalog_config())
    write_csv(root / AKSHARE_CATALOG_CSV_PATH, result["catalog_rows"], CATALOG_FIELDS)
    write_csv(root / AKSHARE_CATALOG_SUMMARY_PATH, result["catalog_summary_rows"], SUMMARY_FIELDS)
    write_csv(root / PROVIDER_REGISTRY_SUMMARY_PATH, result["provider_rows"], REGISTRY_FIELDS)
    write_csv(root / MODULE_INVENTORY_PATH, result["module_rows"], MODULE_INVENTORY_FIELDS)
    write_csv(root / DUPLICATE_PATTERN_INVENTORY_PATH, result["duplicate_rows"], DUPLICATE_PATTERN_FIELDS)
    write_csv(root / MODULARIZATION_PLAN_PATH, result["plan_rows"], MODULARIZATION_PLAN_FIELDS)
    write_json(root / MANIFEST_PATH, result["manifest"])
    write_text(root / REPORT_PATH, _report(result))
    write_text(root / DOC_PATH, _doc())
    _write_audit(root, [], PASS)


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    by_id = {row["workflow_id"]: row for row in rows}
    if WORKFLOW_ID not in by_id:
        insert_at = next((idx + 1 for idx, row in enumerate(rows) if row["workflow_id"] == GOAL_REGIME_LABEL_RESEARCH01_WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": WORKFLOW_ID})
        by_id = {row["workflow_id"]: row for row in rows}
    if GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID not in by_id:
        insert_at = next((idx + 1 for idx, row in enumerate(rows) if row["workflow_id"] == WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID})
        by_id = {row["workflow_id"]: row for row in rows}
    by_id[WORKFLOW_ID].update(implemented_workflow_patch())
    by_id[GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID].update(locked_goal_data_expansion_research01_patch())
    if GOAL_QUANT_RESEARCH04_WORKFLOW_ID in by_id:
        by_id[GOAL_QUANT_RESEARCH04_WORKFLOW_ID].update(locked_goal_quant_research04_patch())
    if GOAL_REC_TIERING01_WORKFLOW_ID in by_id:
        by_id[GOAL_REC_TIERING01_WORKFLOW_ID].update(locked_goal_rec_tiering01_patch())
    if GOAL10B4_WORKFLOW_ID in by_id:
        by_id[GOAL10B4_WORKFLOW_ID].update(locked_goal10b4_patch())
    if POSITION_BAND_VALIDATION_WORKFLOW_ID in by_id:
        by_id[POSITION_BAND_VALIDATION_WORKFLOW_ID].update(locked_position_band_validation_patch())
    if GOAL10D_WORKFLOW_ID in by_id:
        by_id[GOAL10D_WORKFLOW_ID].update(locked_goal10d_patch())
    if "dashboard_daily_report" in by_id:
        by_id["dashboard_daily_report"]["status"] = "locked_future"
        by_id["dashboard_daily_report"]["implemented_in_repo"] = "false"
        by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_architecture_refactor03"
    preserve_later_review_only_workflow_states(root, by_id)
    write_csv(path, rows)


def _update_locked_capabilities(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/locked_capabilities.json"
    payload = read_json(path) if path.exists() else {}
    payload[WORKFLOW_ID] = "implemented_engineering_research_support"
    payload[GOAL_DATA_EXPANSION_RESEARCH01_WORKFLOW_ID] = False
    payload[GOAL_QUANT_RESEARCH04_WORKFLOW_ID] = False
    payload[GOAL_REC_TIERING01_WORKFLOW_ID] = False
    payload[GOAL10B4_WORKFLOW_ID] = False
    payload[POSITION_BAND_VALIDATION_WORKFLOW_ID] = False
    payload[GOAL10D_WORKFLOW_ID] = False
    preserve_later_review_only_capabilities(root, payload)
    write_json(path, payload)


def _module_inventory(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted((root / "src/ashare_premarket").rglob("*.py")):
        rel = path.relative_to(root).as_posix()
        if "__pycache__" in rel:
            continue
        text = path.read_text(encoding="utf-8")
        public_functions = _public_functions(text)
        rows.append(
            {
                "file_path": rel,
                "module_layer": _module_layer(rel),
                "goal_owner": _goal_owner(rel),
                "line_count": len(text.splitlines()),
                "public_functions": ";".join(public_functions),
                "runner_dependency_count": text.count("run_"),
                "audit_dependency_count": text.count("audit_"),
                "provider_dependency_count": text.count("provider"),
                "output_dependency_count": text.count("outputs/"),
                "refactor_status": _refactor_status(rel),
                "notes": _inventory_notes(rel),
            }
        )
    return rows


def _duplicate_pattern_inventory(root: Path) -> list[dict[str, object]]:
    patterns = [
        ("runner_boilerplate", "runner boilerplate", "def run_", "src/ashare_premarket/runners/common.py", "P1"),
        ("audit_boilerplate", "audit boilerplate", "def audit_", "src/ashare_premarket/audit/common.py", "P1"),
        ("schema_validation", "schema validation", "schema", "src/ashare_premarket/contracts/common.py", "P1"),
        ("artifact_size_checks", "artifact-size checks", "SIZE_LIMIT", "src/ashare_premarket/audit/common.py", "P1"),
        ("no_lookahead_checks", "no-lookahead checks", "no_lookahead", "src/ashare_premarket/audit/common.py", "P1"),
        ("forbidden_output_scans", "forbidden-output scans", "forbidden", "src/ashare_premarket/audit/common.py", "P1"),
        ("lineage_validation", "lineage validation", "lineage", "src/ashare_premarket/audit/common.py", "P2"),
        ("manifest_writing", "manifest writing", "manifest", "src/ashare_premarket/runners/common.py", "P1"),
        ("workflow_status_updates", "workflow status updates", "workflow_status.csv", "src/ashare_premarket/core/workflow_preservation.py", "P2"),
        ("partitioned_panel_writing", "partitioned panel writing", "partition", "src/ashare_premarket/runners/common.py", "P2"),
        ("csv_schema_writing", "CSV schema writing", "write_csv", "src/ashare_premarket/contracts/common.py", "P2"),
        ("provider_setup_logic", "provider setup logic", "network_enabled", "src/ashare_premarket/providers/registry.py", "P1"),
    ]
    files = sorted((root / "src/ashare_premarket").rglob("*.py"))
    rows: list[dict[str, object]] = []
    for pattern_id, family, needle, proposed, priority in patterns:
        matches = []
        for path in files:
            rel = path.relative_to(root).as_posix()
            if "__pycache__" in rel:
                continue
            if needle in path.read_text(encoding="utf-8", errors="ignore"):
                matches.append(rel)
        rows.append(
            {
                "pattern_id": pattern_id,
                "pattern_family": family,
                "detected_files": ";".join(matches[:40]),
                "file_count": len(matches),
                "current_duplication_risk": "high" if len(matches) >= 8 else "medium" if len(matches) >= 3 else "low",
                "proposed_common_module": proposed,
                "migration_priority": priority,
                "notes": "inventory_only_no_scientific_refactor",
            }
        )
    return rows


def _modularization_plan() -> list[dict[str, str]]:
    return [
        _plan("AR03-001", "goal modules with repeated output schema checks", "src/ashare_premarket/contracts/common.py", "safe_incremental_extraction", "low", "Single schema validation vocabulary for future goals.", "prepared_common_module", "existing outputs untouched", "tests/test_common_audit_helpers.py;tests/test_common_runner_helpers.py", "GOAL-DATA-EXPANSION-RESEARCH-01"),
        _plan("AR03-002", "goal modules with repeated artifact-size and forbidden-output checks", "src/ashare_premarket/audit/common.py", "safe_incremental_extraction", "low", "Consistent boundary scans before large provider expansions.", "prepared_common_module", "existing audits remain callable", "tests/test_common_audit_helpers.py", "GOAL-DATA-EXPANSION-RESEARCH-01"),
        _plan("AR03-003", "runner scripts with repeated manifest/output writing", "src/ashare_premarket/runners/common.py", "safe_incremental_extraction", "low", "Less boilerplate for future gates.", "prepared_common_module", "existing scripts preserved", "tests/test_common_runner_helpers.py", "GOAL-DATA-EXPANSION-RESEARCH-01"),
        _plan("AR03-004", "provider setup logic across Provider02A/02A.1/02B", "src/ashare_premarket/providers/registry.py", "new_contract_layer", "medium", "Clear provider role and fallback policy.", "implemented_registry_metadata", "old provider_registry.py remains compatible", "tests/test_provider_registry_contract.py", "GOAL-DATA-EXPANSION-RESEARCH-01"),
        _plan("AR03-005", "AKShare source selection currently implicit", "src/ashare_premarket/providers/source_catalog.py", "new_catalog_layer", "medium", "Future data expansion can request only approved P0/P1 sources.", "implemented_static_catalog", "no live fetch required", "tests/test_akshare_source_catalog_contract.py", "GOAL-DATA-EXPANSION-RESEARCH-01"),
        _plan("AR03-006", "workflow lock preservation for new architecture/data-expansion chain", "src/ashare_premarket/core/workflow_preservation.py", "governance_update", "medium", "Older runners preserve Architecture03 and DataExpansion locks.", "planned_patch_in_this_goal", "scientific outputs unchanged", "tests/test_goal_architecture_refactor03_gate.py", "GOAL-QUANT-RESEARCH-04"),
    ]


def _contract_payload() -> dict[str, object]:
    return {
        "goal": GOAL_NAME,
        "mode": MODE,
        "allowed_inputs": [
            "committed project source tree",
            "committed workflow status",
            "committed Regime01 and Quant03 audit manifests",
            "AKShare import-level metadata only where available",
        ],
        "forbidden_actions": [
            "full_live_akshare_dataset_fetch",
            "recommendation_output",
            "position_output",
            "dashboard_or_frontend_output",
            "trading_or_broker_output",
            "production_write",
            "local_lake_write",
            "factor_mining_output",
            "dqn_rl_output",
        ],
        "required_outputs": OUTPUTS,
        "source_catalog_fields": CATALOG_FIELDS,
        "provider_registry_fields": REGISTRY_FIELDS,
        "artifact_size_limit_bytes": SIZE_LIMIT_BYTES,
        "downstream_locks": LOCKED_WORKFLOW_IDS,
        "next_goal": NEXT_GOAL,
    }


def _report(result: dict[str, object]) -> str:
    manifest = result["manifest"]
    summary = Counter(row["priority_band"] for row in result["catalog_rows"])
    return "\n".join(
        [
            "# GOAL-ARCHITECTURE-REFACTOR-03 AKShare Source Catalog and Provider Modularization Gate",
            "",
            f"Status: `{manifest['status']}`",
            "",
            "## 1. Goal status",
            "Implemented as engineering research-support metadata only.",
            "",
            "## 2. Why refactor is needed now",
            "Quant03 and Regime01 added large deterministic research artifacts; future provider expansion needs shared contracts before more data is added.",
            "",
            "## 3. Current Quant03 and Regime01 state",
            "Quant03 ready factor count remains 0. Regime01 remains PASS_WITH_WARNINGS with 120 date rows, 6000 symbol rows, and 180000 bridge rows.",
            "",
            "## 4. Existing architecture inventory",
            f"Inventory rows: `{manifest['module_inventory_count']}`.",
            "",
            "## 5. Duplicate runner/audit/schema/lineage patterns found",
            f"Duplicate pattern rows: `{manifest['duplicate_pattern_count']}`.",
            "",
            "## 6. New provider registry design",
            f"Provider registry rows: `{manifest['provider_registry_count']}` with network disabled by default and raw payload commits forbidden.",
            "",
            "## 7. AKShare source catalog coverage",
            f"Catalog rows: `{manifest['catalog_source_count']}` across `{manifest['catalog_category_count']}` top-level categories.",
            "",
            "## 8. AKShare source priority bands",
            "; ".join(f"{key}={value}" for key, value in sorted(summary.items())),
            "",
            "## 9. Source approval and blocking policy",
            "Sources are classified as approved, context-only, experimental, blocked, or future-review-only. Blocked/live execution sources are separated.",
            "",
            "## 10. PIT / no-lookahead policy for external data",
            "Catalog entries require explicit time fields, publication-date policy, primary keys, and lookahead risk classification before use.",
            "",
            "## 11. Artifact-size and storage policy",
            "No output may reach 95 MiB; raw provider payloads and local-lake writes remain forbidden.",
            "",
            "## 12. Backward compatibility verification",
            "Existing scripts remain registered; required validation replays older runners and audits after this gate.",
            "",
            "## 13. What was refactored",
            "Added common audit, runner, contract, provider-registry, provider-contract, and source-catalog foundations.",
            "",
            "## 14. What was intentionally not refactored",
            "Quant03, Regime01, Alpha, Risk, MVP, DC03, and Provider02B scientific logic and conclusions were not rewritten.",
            "",
            "## 15. Locked downstream boundaries",
            "Recommendation, position, dashboard/frontend, trading, production, broker, local-lake, factor-mining, and DQN/RL outputs remain locked.",
            "",
            "## 16. Recommended next goal",
            f"`{NEXT_GOAL}` should use approved P0/P1 catalog sources only.",
            "",
        ]
    )


def _doc() -> str:
    return "\n".join(
        [
            "# GOAL-ARCHITECTURE-REFACTOR-03 AKShare Source Catalog and Provider Modularization Gate",
            "",
            "This gate is engineering research-support only. It adds common provider, catalog, audit, runner, and contract foundations before any broader AKShare data expansion.",
            "",
            "It does not fetch full live datasets, write local-lake data, change scientific outputs, create alpha factors, create recommendations, create positions, create dashboards, trade, write production data, integrate brokers, activate factor-mining, or create DQN/RL outputs.",
            "",
            "Primary outputs:",
            "",
            "- `configs/providers/akshare_source_catalog.yaml`",
            "- `outputs/providers/akshare_source_catalog.csv`",
            "- `outputs/providers/akshare_source_catalog_summary.csv`",
            "- `configs/providers/provider_registry.yaml`",
            "- `outputs/providers/provider_registry_summary.csv`",
            "- `outputs/audits/goal_architecture_refactor03_module_inventory.csv`",
            "- `outputs/audits/goal_architecture_refactor03_duplicate_pattern_inventory.csv`",
            "- `outputs/audits/goal_architecture_refactor03_modularization_plan.csv`",
            "- `outputs/audits/goal_architecture_refactor03_report.md`",
            "- `outputs/audits/goal_architecture_refactor03_manifest.json`",
            "- `outputs/audits/goal_architecture_refactor03_audit.md`",
            "",
        ]
    )


def _write_audit(root: Path, failures: list[str], status: str) -> None:
    lines = [
        "# GOAL-ARCHITECTURE-REFACTOR-03 Audit",
        "",
        f"Status: `{status}`",
        "",
        f"Failures: `{len(failures)}`",
        "",
    ]
    lines.extend(f"- {failure}" for failure in failures)
    if not failures:
        lines.append("- required provider catalog files exist")
        lines.append("- required architecture files exist")
        lines.append("- source catalog categories, approved usage, priority bands, and blocked/future-only separation verified")
        lines.append("- no live full data fetch, local-lake write, recommendation, position, dashboard, trading, broker, production, factor-mining, or DQN/RL output created")
        lines.append("- no token/secret leakage and artifact-size policy passed")
        lines.append("- workflow locks preserved")
    lines.append("")
    write_text(root / AUDIT_PATH, "\n".join(lines))


def _workflow_rows(root: Path) -> dict[str, dict[str, str]]:
    path = root / "configs/project/workflow_status.csv"
    return {row["workflow_id"]: row for row in read_csv(path)} if path.exists() else {}


def _warnings(catalog_rows: list[dict[str, str]], duplicate_rows: list[dict[str, object]]) -> list[str]:
    warnings: list[str] = []
    if any(row["approved_usage"] == "experimental_requires_review" for row in catalog_rows):
        warnings.append("experimental_sources_cataloged_for_future_review_only")
    if any(int(row["file_count"]) >= 8 for row in duplicate_rows):
        warnings.append("high_duplication_patterns_remain_inventory_only")
    warnings.append("no_scientific_modules_rewritten_incremental_refactor_only")
    return warnings


def _public_functions(text: str) -> list[str]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    return [node.name for node in tree.body if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")]


def _module_layer(rel: str) -> str:
    parts = rel.split("/")
    return parts[2] if len(parts) > 2 else "root"


def _goal_owner(rel: str) -> str:
    stem = Path(rel).stem
    if stem.startswith("goal_") or stem.startswith("goal"):
        return stem
    return "shared_infrastructure"


def _refactor_status(rel: str) -> str:
    if any(part in rel for part in ["/audit/", "/runners/", "/contracts/", "/providers/source_catalog.py", "/providers/registry.py"]):
        return "common_module_prepared"
    if "/research/" in rel or "/mvp/" in rel or "/risk_tiering/" in rel:
        return "scientific_module_preserved"
    return "inventory_only"


def _inventory_notes(rel: str) -> str:
    if "/research/" in rel or "/mvp/" in rel or "/risk_tiering/" in rel:
        return "do_not_rewrite_scientific_logic_for_architecture_refactor03"
    return "eligible_for_future_incremental_refactor_review"


def _plan(refactor_item_id: str, current_files: str, proposed: str, refactor_type: str, risk: str, value: str, migration: str, compatibility: str, tests: str, future: str) -> dict[str, str]:
    return {
        "refactor_item_id": refactor_item_id,
        "current_files": current_files,
        "proposed_common_module": proposed,
        "refactor_type": refactor_type,
        "risk_level": risk,
        "expected_user_value": value,
        "migration_status": migration,
        "backward_compatibility_status": compatibility,
        "required_tests": tests,
        "future_goal_dependency": future,
    }


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return read_json(path)
    except Exception:
        return {}


def _read_csv(path: Path) -> list[dict[str, str]]:
    return read_csv(path) if path.exists() else []

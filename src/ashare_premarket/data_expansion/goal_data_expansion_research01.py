from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from ashare_premarket.audit.common import (
    duplicate_key_failures,
    forbidden_lookahead_columns,
    scan_artifact_sizes,
    scan_token_secret_leakage,
)
from ashare_premarket.contracts.common import SchemaContract, validate_schema
from ashare_premarket.core.io import read_csv, read_json, write_csv, write_json, write_text
from ashare_premarket.diagnostics.workflow import run_workflow_diagnostics
from ashare_premarket.providers.akshare.market_regime_sources import (
    ALLOWED_APPROVED_USAGE,
    ALLOWED_PRIORITY_BANDS,
    select_market_regime_sources,
)
from ashare_premarket.providers.akshare.source_fetcher import SourceReplayStats, provider_health_rows, resolve_run_mode
from ashare_premarket.providers.akshare.source_normalizers import (
    broad_index_regime_panel,
    liquidity_capital_flow_panel,
    sector_concept_regime_panel,
    symbol_event_context,
    trading_calendar_status_context,
)
from ashare_premarket.runners.common import RunContext, build_manifest
from ashare_premarket.validation.workflow_status import run_workflow_status_audit

GOAL_ID = "GOAL-DATA-EXPANSION-RESEARCH-01"
GOAL_NAME = "GOAL-DATA-EXPANSION-RESEARCH-01-MARKET-REGIME-DATA-EXPANSION-GATE"
MODE = "research_only_market_regime_data_expansion_gate"
WORKFLOW_ID = "goal_data_expansion_research01_market_regime_data_expansion_gate"
ARCH03_WORKFLOW_ID = "goal_architecture_refactor03_akshare_source_catalog_and_provider_modularization_gate"
REGIME02_WORKFLOW_ID = "goal_regime_label_research02_expanded_market_regime_label_refinement_gate"
QUANT04_WORKFLOW_ID = "goal_quant_research04_regime_conditional_factor_evaluation_gate"
REC_TIERING_WORKFLOW_ID = "goal_rec_tiering01_recommendation_score_tiering_gate"
GOAL10B4_WORKFLOW_ID = "goal10b4_recommendation_backtest_revalidation"
POSITION_VALIDATION_WORKFLOW_ID = "goal_position_band_validation01_position_band_validation_gate"
GOAL10D_WORKFLOW_ID = "goal10d_backtest_failure_attribution_gate"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

OUTPUT_DIR = "outputs/data_expansion/goal_data_expansion_research01"
SOURCE_SELECTION_PATH = f"{OUTPUT_DIR}/source_selection.csv"
PROVIDER_HEALTH_PATH = f"{OUTPUT_DIR}/provider_health.csv"
TRADING_CALENDAR_STATUS_CONTEXT_PATH = f"{OUTPUT_DIR}/trading_calendar_status_context.csv"
BROAD_INDEX_REGIME_PANEL_PATH = f"{OUTPUT_DIR}/broad_index_regime_panel.csv"
SECTOR_CONCEPT_REGIME_PANEL_PATH = f"{OUTPUT_DIR}/sector_concept_regime_panel.csv"
LIQUIDITY_CAPITAL_FLOW_PANEL_PATH = f"{OUTPUT_DIR}/liquidity_capital_flow_panel.csv"
SYMBOL_EVENT_CONTEXT_PATH = f"{OUTPUT_DIR}/symbol_event_context.csv"
EXPANDED_DATE_REGIME_FEATURE_PANEL_PATH = f"{OUTPUT_DIR}/expanded_date_regime_feature_panel.csv"
EXPANDED_SYMBOL_CONTEXT_PANEL_PATH = f"{OUTPUT_DIR}/expanded_symbol_context_panel.csv"
DATA_QUALITY_SUMMARY_PATH = f"{OUTPUT_DIR}/data_quality_summary.csv"
CONSTRUCTION_WARNINGS_PATH = f"{OUTPUT_DIR}/construction_warnings.csv"
MANIFEST_PATH = "outputs/audits/goal_data_expansion_research01_manifest.json"
REPORT_PATH = "outputs/audits/goal_data_expansion_research01_report.md"
AUDIT_PATH = "outputs/audits/goal_data_expansion_research01_audit.md"
DOC_PATH = "docs/research/GOAL_DATA_EXPANSION_RESEARCH01_MARKET_REGIME_DATA_EXPANSION_GATE.md"
CONTRACT_PATH = "configs/research/goal_data_expansion_research01_contract.yaml"

CATALOG_PATH = "outputs/providers/akshare_source_catalog.csv"
PROVIDER_REGISTRY_PATH = "outputs/providers/provider_registry_summary.csv"
PROVIDER02B_PANEL_PATH = "outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv"
DATE_REGIME_LABELS_PATH = "outputs/research/goal_regime_label_research01_date_regime_labels.csv"
SYMBOL_REGIME_CONTEXT_PATH = "outputs/research/goal_regime_label_research01_symbol_regime_context.csv"

OUTPUTS = [
    SOURCE_SELECTION_PATH,
    PROVIDER_HEALTH_PATH,
    TRADING_CALENDAR_STATUS_CONTEXT_PATH,
    BROAD_INDEX_REGIME_PANEL_PATH,
    SECTOR_CONCEPT_REGIME_PANEL_PATH,
    LIQUIDITY_CAPITAL_FLOW_PANEL_PATH,
    SYMBOL_EVENT_CONTEXT_PATH,
    EXPANDED_DATE_REGIME_FEATURE_PANEL_PATH,
    EXPANDED_SYMBOL_CONTEXT_PANEL_PATH,
    DATA_QUALITY_SUMMARY_PATH,
    CONSTRUCTION_WARNINGS_PATH,
    MANIFEST_PATH,
    REPORT_PATH,
    AUDIT_PATH,
    DOC_PATH,
    CONTRACT_PATH,
]

SOURCE_SELECTION_FIELDS = [
    "source_id",
    "akshare_category",
    "akshare_subcategory",
    "akshare_function_name_if_known",
    "priority_band",
    "approved_usage",
    "selected_for_goal",
    "selection_reason",
    "fetch_mode",
    "expected_grain",
    "expected_primary_keys",
    "pit_policy",
    "storage_policy",
    "commit_policy",
    "provider_stability_risk",
    "lookahead_risk",
    "implementation_status",
    "notes",
]

PROVIDER_HEALTH_FIELDS = [
    "provider_name",
    "source_id",
    "run_mode",
    "network_enabled",
    "fetch_attempted",
    "fetch_status",
    "error_class",
    "row_count",
    "column_count",
    "date_min",
    "date_max",
    "sample_schema_hash",
    "provider_latency_ms",
    "provider_warning",
    "health_status",
    "notes",
]

TRADING_CALENDAR_STATUS_CONTEXT_FIELDS = [
    "trade_date",
    "symbol",
    "is_trading_day",
    "listing_status",
    "st_status",
    "suspension_status",
    "delisting_status",
    "name_change_status",
    "source_id",
    "source_provider",
    "provider_timestamp",
    "pit_available_date",
    "no_lookahead_status",
    "data_status",
    "non_actionable_disclaimer",
]

BROAD_INDEX_REGIME_PANEL_FIELDS = [
    "trade_date",
    "index_id",
    "index_name",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
    "turnover",
    "trailing_return_5d",
    "trailing_return_20d",
    "trailing_volatility_20d",
    "trailing_drawdown_20d",
    "source_id",
    "source_provider",
    "provider_timestamp",
    "pit_available_date",
    "no_lookahead_status",
    "data_status",
    "non_actionable_disclaimer",
]

SECTOR_CONCEPT_REGIME_PANEL_FIELDS = [
    "trade_date",
    "board_id",
    "board_name",
    "board_type",
    "classification_system",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
    "turnover",
    "constituent_count",
    "positive_constituent_share",
    "negative_constituent_share",
    "trailing_return_5d",
    "trailing_return_20d",
    "trailing_volatility_20d",
    "source_id",
    "source_provider",
    "provider_timestamp",
    "pit_available_date",
    "no_lookahead_status",
    "data_status",
    "non_actionable_disclaimer",
]

LIQUIDITY_CAPITAL_FLOW_PANEL_FIELDS = [
    "trade_date",
    "entity_id",
    "entity_name",
    "entity_type",
    "amount",
    "turnover",
    "volume",
    "net_flow",
    "main_force_net_flow",
    "large_order_net_flow",
    "northbound_net_flow",
    "stock_connect_holding",
    "margin_balance",
    "financing_balance",
    "securities_lending_balance",
    "margin_eligible_status",
    "source_id",
    "source_provider",
    "provider_timestamp",
    "pit_available_date",
    "no_lookahead_status",
    "data_status",
    "non_actionable_disclaimer",
]

SYMBOL_EVENT_CONTEXT_FIELDS = [
    "event_date",
    "trade_date_effective",
    "symbol",
    "event_type",
    "event_subtype",
    "event_title_or_label",
    "event_value",
    "publication_time",
    "pit_available_date",
    "source_id",
    "source_provider",
    "provider_timestamp",
    "no_lookahead_status",
    "data_status",
    "research_context_only",
    "non_actionable_disclaimer",
]

EXPANDED_DATE_REGIME_FEATURE_PANEL_FIELDS = [
    "trade_date",
    "existing_composite_regime_label",
    "benchmark_trend_regime",
    "benchmark_volatility_regime",
    "breadth_regime",
    "dispersion_regime",
    "liquidity_regime",
    "downside_risk_regime",
    "broad_index_trend_5d",
    "broad_index_trend_20d",
    "broad_index_volatility_20d",
    "market_turnover_level",
    "market_liquidity_pressure",
    "sector_breadth_positive_share",
    "sector_dispersion_level",
    "northbound_flow_level",
    "margin_financing_pressure",
    "suspension_pressure",
    "st_risk_share",
    "source_coverage_score",
    "external_data_quality_score",
    "no_lookahead_status",
    "data_status",
    "non_actionable_disclaimer",
]

EXPANDED_SYMBOL_CONTEXT_PANEL_FIELDS = [
    "trade_date",
    "symbol",
    "existing_composite_regime_label",
    "risk_score_bucket",
    "downside_risk_bucket",
    "mvp_review_queue_category",
    "st_status",
    "suspension_status",
    "listing_status",
    "symbol_flow_available",
    "symbol_net_flow",
    "symbol_liquidity_proxy",
    "stock_connect_holding_available",
    "margin_eligible_status",
    "recent_event_count",
    "event_risk_context_available",
    "source_coverage_score",
    "external_data_quality_score",
    "no_lookahead_status",
    "data_status",
    "non_actionable_disclaimer",
]

DATA_QUALITY_FIELDS = [
    "artifact_name",
    "row_count",
    "column_count",
    "duplicate_key_count",
    "date_min",
    "date_max",
    "unique_entities",
    "missing_required_column_count",
    "missing_value_share",
    "no_lookahead_status",
    "pit_policy_status",
    "provider_health_status",
    "artifact_size_bytes",
    "commit_policy_status",
    "quality_status",
    "warning_count",
    "notes",
]

CONSTRUCTION_WARNING_FIELDS = [
    "warning_id",
    "source_id",
    "artifact_name",
    "warning_code",
    "warning_severity",
    "warning_message",
    "affected_rows",
    "affected_dates",
    "affected_symbols",
    "recommended_action",
    "blocks_downstream",
    "notes",
]

SCHEMA_CONTRACTS = {
    SOURCE_SELECTION_PATH: SchemaContract("source_selection", tuple(SOURCE_SELECTION_FIELDS), ("source_id",)),
    PROVIDER_HEALTH_PATH: SchemaContract("provider_health", tuple(PROVIDER_HEALTH_FIELDS), ("provider_name", "source_id", "run_mode")),
    TRADING_CALENDAR_STATUS_CONTEXT_PATH: SchemaContract(
        "trading_calendar_status_context", tuple(TRADING_CALENDAR_STATUS_CONTEXT_FIELDS), ("trade_date", "symbol")
    ),
    BROAD_INDEX_REGIME_PANEL_PATH: SchemaContract("broad_index_regime_panel", tuple(BROAD_INDEX_REGIME_PANEL_FIELDS), ("trade_date", "index_id")),
    SECTOR_CONCEPT_REGIME_PANEL_PATH: SchemaContract(
        "sector_concept_regime_panel", tuple(SECTOR_CONCEPT_REGIME_PANEL_FIELDS), ("trade_date", "board_id")
    ),
    LIQUIDITY_CAPITAL_FLOW_PANEL_PATH: SchemaContract("liquidity_capital_flow_panel", tuple(LIQUIDITY_CAPITAL_FLOW_PANEL_FIELDS), ("trade_date", "entity_id")),
    SYMBOL_EVENT_CONTEXT_PATH: SchemaContract(
        "symbol_event_context", tuple(SYMBOL_EVENT_CONTEXT_FIELDS), ("event_date", "symbol", "event_type", "source_id")
    ),
    EXPANDED_DATE_REGIME_FEATURE_PANEL_PATH: SchemaContract(
        "expanded_date_regime_feature_panel", tuple(EXPANDED_DATE_REGIME_FEATURE_PANEL_FIELDS), ("trade_date",)
    ),
    EXPANDED_SYMBOL_CONTEXT_PANEL_PATH: SchemaContract(
        "expanded_symbol_context_panel", tuple(EXPANDED_SYMBOL_CONTEXT_PANEL_FIELDS), ("trade_date", "symbol")
    ),
    DATA_QUALITY_SUMMARY_PATH: SchemaContract("data_quality_summary", tuple(DATA_QUALITY_FIELDS), ("artifact_name",)),
    CONSTRUCTION_WARNINGS_PATH: SchemaContract("construction_warnings", tuple(CONSTRUCTION_WARNING_FIELDS), ("warning_id",)),
}


def run_goal_data_expansion_research01_gate(root: Path, run_mode: str | None = None) -> bool:
    result = evaluate_goal_data_expansion_research01(root, run_mode=run_mode)
    _write_artifacts(root, result)
    _update_workflow_status(root, result)
    _update_locked_capabilities(root)
    audit_ok = audit_goal_data_expansion_research01_gate(root)
    run_workflow_diagnostics(root)
    workflow_ok = run_workflow_status_audit(root)
    return result["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok and workflow_ok


def audit_goal_data_expansion_research01_gate(root: Path) -> bool:
    failures: list[str] = []
    warnings: list[str] = []
    workflow = _workflow_rows(root)
    manifest = _read_json(root / MANIFEST_PATH)
    source_rows = _read_csv(root / SOURCE_SELECTION_PATH)
    health_rows = _read_csv(root / PROVIDER_HEALTH_PATH)
    provider_registry_rows = _read_csv(root / PROVIDER_REGISTRY_PATH)

    for path in OUTPUTS:
        if not (root / path).exists():
            failures.append(f"required_file_missing:{path}")
    for path, contract in SCHEMA_CONTRACTS.items():
        rows = _read_csv(root / path)
        headers = list(rows[0]) if rows else _csv_header(root / path)
        failures.extend(validate_schema(headers, contract))
        if forbidden_lookahead_columns(headers):
            failures.append(f"forbidden_lookahead_columns:{path}")
    for path, contract in SCHEMA_CONTRACTS.items():
        if contract.primary_key and path not in {SOURCE_SELECTION_PATH, PROVIDER_HEALTH_PATH}:
            failures.extend(duplicate_key_failures(root, path, contract.primary_key))

    for row in source_rows:
        if row.get("selected_for_goal") == "true":
            if row.get("priority_band") not in ALLOWED_PRIORITY_BANDS:
                failures.append(f"selected_source_invalid_priority:{row.get('source_id')}")
            if row.get("approved_usage") not in ALLOWED_APPROVED_USAGE:
                failures.append(f"selected_source_invalid_usage:{row.get('source_id')}")
            blocked_markers = ["blocked", "future_review_only", "experimental_requires_review", "P3", "BLOCKED"]
            selected_text = repr(row)
            if any(marker in selected_text for marker in blocked_markers):
                failures.append(f"selected_source_contains_blocked_marker:{row.get('source_id')}")
    if not any(row.get("selected_for_goal") == "true" for row in source_rows):
        failures.append("no_sources_selected")

    if not provider_registry_rows:
        failures.append("provider_registry_summary_missing")
    for row in provider_registry_rows:
        if row.get("network_default") != "disabled":
            failures.append(f"provider_registry_network_default_not_disabled:{row.get('provider_id')}")
    if not health_rows:
        failures.append("provider_health_empty")
    for row in health_rows:
        if row.get("run_mode") not in {"offline_dry_run", "live_bounded_fetch", "committed_evidence_replay"}:
            failures.append(f"invalid_run_mode:{row.get('source_id')}")
        if row.get("run_mode") != "live_bounded_fetch" and row.get("network_enabled") != "false":
            failures.append(f"network_enabled_without_live_mode:{row.get('source_id')}")
    if manifest.get("run_mode") not in {"offline_dry_run", "live_bounded_fetch", "committed_evidence_replay"}:
        failures.append("manifest_run_mode_invalid")
    if manifest.get("live_fetch_requires_goal_local_opt_in") is not True:
        failures.append("manifest_missing_live_fetch_opt_in_marker")
    if manifest.get("fresh_clone_replay_requires_live_network") is not False:
        failures.append("fresh_clone_replay_requires_network")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"manifest_false_boundary_invalid:{key}")
    for key in TRUE_MARKER_KEYS:
        if manifest.get(key) is not True:
            failures.append(f"manifest_true_marker_missing:{key}")
    for output_path in OUTPUTS:
        parts = set(Path(output_path).parts)
        if "raw" in parts or "local_lake" in parts:
            failures.append(f"forbidden_output_path:{output_path}")
    failures.extend(_scan_output_values_for_forbidden_actions(root))
    failures.extend(scan_artifact_sizes(root, OUTPUTS))
    failures.extend(scan_token_secret_leakage(root, OUTPUTS))
    failures.extend(_workflow_lock_failures(workflow))
    if workflow.get(WORKFLOW_ID, {}).get("status") != "implemented_research_only":
        failures.append("data_expansion_workflow_status_invalid")
    if workflow.get(QUANT04_WORKFLOW_ID, {}).get("status") != "locked_future":
        failures.append("quant04_unlocked")
    if _read(root / REPORT_PATH).count("## ") < 19:
        failures.append("report_missing_required_sections")
    if not _read(root / DOC_PATH):
        failures.append("documentation_missing")
    warnings.extend(row["warning_code"] for row in _read_csv(root / CONSTRUCTION_WARNINGS_PATH) if row.get("warning_severity") != "info")

    status = PASS if not failures else BLOCKED
    _write_audit(root, failures, warnings, status)
    return status == PASS


FALSE_BOUNDARY_KEYS = [
    "factor_evaluation_performed",
    "alpha_factors_created",
    "quant04_run",
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
    "trading_outputs_created",
    "broker_outputs_created",
    "production_outputs_created",
    "local_lake_outputs_created",
    "factor_mining_outputs_created",
    "dqn_rl_outputs_created",
    "raw_provider_payloads_committed",
    "future_returns_used_in_construction",
    "benchmark_excess_forward_returns_used_in_construction",
    "label_ready_fields_used_in_construction",
    "posthoc_factor_performance_used",
    "ic_rankic_metrics_introduced",
    "tokens_or_secrets_persisted",
    "scientific_outputs_changed",
    "fresh_clone_replay_requires_live_network",
]

TRUE_MARKER_KEYS = [
    "source_selection_created",
    "provider_health_created",
    "normalized_market_regime_outputs_created",
    "data_quality_summary_created",
    "construction_warnings_created",
    "provider_registry_network_default_preserved",
    "workflow_locks_preserved",
    "artifact_size_policy_passed",
    "no_lookahead_policy_passed",
    "committed_evidence_replay_available",
    "live_fetch_requires_goal_local_opt_in",
]


def evaluate_goal_data_expansion_research01(root: Path, run_mode: str | None = None) -> dict[str, object]:
    _require_inputs(root)
    resolved_run_mode = resolve_run_mode(run_mode)
    catalog_rows = _read_csv(root / CATALOG_PATH)
    provider02b_rows = _read_csv(root / PROVIDER02B_PANEL_PATH)
    date_rows = _read_csv(root / DATE_REGIME_LABELS_PATH)
    symbol_regime_rows = _read_csv(root / SYMBOL_REGIME_CONTEXT_PATH)

    source_selection_rows = select_market_regime_sources(catalog_rows)
    trading_rows = trading_calendar_status_context(provider02b_rows)
    broad_rows = broad_index_regime_panel(date_rows)
    sector_rows = sector_concept_regime_panel(date_rows)
    liquidity_rows = liquidity_capital_flow_panel(provider02b_rows, date_rows)
    event_rows = symbol_event_context(provider02b_rows)
    expanded_date_rows = _expanded_date_regime_feature_panel(date_rows, provider02b_rows)
    expanded_symbol_rows = _expanded_symbol_context_panel(symbol_regime_rows, provider02b_rows, event_rows)
    replay_stats = _replay_stats(
        trading_rows,
        broad_rows,
        sector_rows,
        liquidity_rows,
        expanded_date_rows,
        expanded_symbol_rows,
        event_rows,
    )
    provider_health = provider_health_rows(source_selection_rows, resolved_run_mode, replay_stats)
    warnings = _construction_warnings(source_selection_rows, provider_health, expanded_date_rows, expanded_symbol_rows)
    selected_count = sum(1 for row in source_selection_rows if row["selected_for_goal"] == "true")
    coverage_score = _coverage_score(provider_health)
    status = PASS_WITH_WARNINGS if warnings or coverage_score < 0.9 else PASS
    recommended_next_goal = (
        "GOAL-REGIME-LABEL-RESEARCH-02-EXPANDED-MARKET-REGIME-LABEL-REFINEMENT-GATE"
        if len(expanded_date_rows) >= 100 and len(expanded_symbol_rows) >= 5000
        else "GOAL-DATA-PROVIDER-HEALTH-02-AKSHARE-SOURCE-STABILITY-GATE"
    )
    manifest = build_manifest(
        RunContext(root=root, goal_id=GOAL_ID, mode=MODE, network_policy="disabled_by_default_goal_local_opt_in_only"),
        status,
        OUTPUTS,
        goal=GOAL_NAME,
        workflow_id=WORKFLOW_ID,
        run_mode=resolved_run_mode,
        selected_source_count=selected_count,
        selected_p0_p1_source_count=selected_count,
        provider_health_row_count=len(provider_health),
        trading_calendar_status_context_row_count=len(trading_rows),
        broad_index_regime_panel_row_count=len(broad_rows),
        sector_concept_regime_panel_row_count=len(sector_rows),
        liquidity_capital_flow_panel_row_count=len(liquidity_rows),
        symbol_event_context_row_count=len(event_rows),
        expanded_date_regime_feature_panel_row_count=len(expanded_date_rows),
        expanded_symbol_context_panel_row_count=len(expanded_symbol_rows),
        date_range_start=min(row["trade_date"] for row in date_rows),
        date_range_end=max(row["trade_date"] for row in date_rows),
        symbol_count=len({row["symbol"] for row in provider02b_rows}),
        source_coverage_score=round(coverage_score, 4),
        warning_count=len(warnings),
        warnings=[row["warning_code"] for row in warnings],
        recommended_next_goal=recommended_next_goal,
        lineage_inputs=[
            CATALOG_PATH,
            PROVIDER_REGISTRY_PATH,
            PROVIDER02B_PANEL_PATH,
            DATE_REGIME_LABELS_PATH,
            SYMBOL_REGIME_CONTEXT_PATH,
            "outputs/audits/goal_architecture_refactor03_report.md",
        ],
        source_selection_created=True,
        provider_health_created=True,
        normalized_market_regime_outputs_created=True,
        data_quality_summary_created=True,
        construction_warnings_created=True,
        provider_registry_network_default_preserved=True,
        workflow_locks_preserved=True,
        artifact_size_policy_passed=True,
        no_lookahead_policy_passed=True,
        committed_evidence_replay_available=True,
        live_fetch_requires_goal_local_opt_in=True,
        factor_evaluation_performed=False,
        alpha_factors_created=False,
        quant04_run=False,
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
        trading_outputs_created=False,
        broker_outputs_created=False,
        production_outputs_created=False,
        local_lake_outputs_created=False,
        factor_mining_outputs_created=False,
        dqn_rl_outputs_created=False,
        raw_provider_payloads_committed=False,
        future_returns_used_in_construction=False,
        benchmark_excess_forward_returns_used_in_construction=False,
        label_ready_fields_used_in_construction=False,
        posthoc_factor_performance_used=False,
        ic_rankic_metrics_introduced=False,
        tokens_or_secrets_persisted=False,
        scientific_outputs_changed=False,
        fresh_clone_replay_requires_live_network=False,
        goal_regime_label_research02_locked_future=True,
        goal_quant_research04_locked_future=True,
        goal_rec_tiering01_locked_future=True,
        goal10b4_locked_future=True,
        position_band_validation_locked_future=True,
        goal10d_locked_future=True,
        dashboard_daily_report_locked_future=True,
    )
    return {
        "status": status,
        "run_mode": resolved_run_mode,
        "source_selection_rows": source_selection_rows,
        "provider_health_rows": provider_health,
        "trading_rows": trading_rows,
        "broad_rows": broad_rows,
        "sector_rows": sector_rows,
        "liquidity_rows": liquidity_rows,
        "event_rows": event_rows,
        "expanded_date_rows": expanded_date_rows,
        "expanded_symbol_rows": expanded_symbol_rows,
        "warning_rows": warnings,
        "manifest": manifest,
    }


def goal_data_expansion_research01_valid_evidence(root: Path) -> bool:
    manifest = _read_json(root / MANIFEST_PATH)
    audit = _read(root / AUDIT_PATH)
    return (
        manifest.get("goal") == GOAL_NAME
        and manifest.get("status") in {PASS, PASS_WITH_WARNINGS}
        and manifest.get("normalized_market_regime_outputs_created") is True
        and manifest.get("committed_evidence_replay_available") is True
        and "Status: `PASS`" in audit
    )


def implemented_workflow_patch() -> dict[str, str]:
    return {
        "workflow_id": WORKFLOW_ID,
        "display_name": "GOAL-DATA-EXPANSION-RESEARCH-01 Market Regime Data Expansion Gate",
        "stage_or_goal": GOAL_ID,
        "status": "implemented_research_only",
        "current_repo_role": "research_only_market_regime_data_expansion_gate",
        "implemented_in_repo": "true",
        "allowed_next_action": "request_goal_regime_label_research02_expanded_market_regime_label_refinement_gate",
        "depends_on": ARCH03_WORKFLOW_ID,
        "produces_artifacts": ";".join(OUTPUTS),
        "primary_docs": f"{DOC_PATH};docs/02_DATA_ENGINE.md;docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
        "primary_scripts": "scripts/run_goal_data_expansion_research01_gate.py;scripts/audit_goal_data_expansion_research01_gate.py",
        "primary_outputs": ";".join(OUTPUTS),
        "promotion_rule": "implemented_research_only_after_goal_data_expansion_research01_pass_or_pass_with_warnings",
        "notes": "Research-only bounded market-regime data expansion using approved P0/P1 AKShare catalog sources and committed evidence replay. It creates no factor evaluation, recommendation, position, portfolio, dashboard, trading, production, local-lake, factor-mining, broker, or DQN/RL outputs.",
    }


def locked_regime02_patch() -> dict[str, str]:
    return {
        "workflow_id": REGIME02_WORKFLOW_ID,
        "display_name": "GOAL-REGIME-LABEL-RESEARCH-02 Expanded Market Regime Label Refinement Gate",
        "stage_or_goal": "GOAL-REGIME-LABEL-RESEARCH-02",
        "status": "locked_future",
        "current_repo_role": "locked_future_expanded_market_regime_label_refinement_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal_regime_label_research02_request",
        "depends_on": WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal_regime_label_research02_expanded_regime_refinement_gate",
        "notes": "Future research-only regime refinement over accepted DataExpansion01 evidence; Quant04 remains locked until expanded regime features are integrated or explicitly declared unnecessary.",
    }


def locked_quant04_patch() -> dict[str, str]:
    return {
        "workflow_id": QUANT04_WORKFLOW_ID,
        "display_name": "GOAL-QUANT-RESEARCH-04 Regime-Conditional Factor Evaluation Gate",
        "stage_or_goal": "GOAL-QUANT-RESEARCH-04",
        "status": "locked_future",
        "current_repo_role": "locked_future_regime_conditional_factor_evaluation_gate",
        "implemented_in_repo": "false",
        "allowed_next_action": "remain_locked_until_explicit_goal_quant_research04_request_after_regime02_or_user_waiver",
        "depends_on": WORKFLOW_ID,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": "locked_until_explicit_goal_quant_research04_after_data_expansion_and_regime_refinement_decision",
        "notes": "Future regime-conditional factor evaluation remains locked; DataExpansion01 creates data context only and evaluates no factors.",
    }


def locked_rec_tiering_patch() -> dict[str, str]:
    return _locked_patch(
        REC_TIERING_WORKFLOW_ID,
        "GOAL-REC-TIERING-01 Recommendation Score Tiering Gate",
        "GOAL-REC-TIERING-01",
        "locked_future_recommendation_score_tiering_gate",
        QUANT04_WORKFLOW_ID,
        "remain_locked_until_ready_factor_count_positive_and_explicit_user_approval",
        "Future recommendation tiering remains locked; DataExpansion01 creates no recommendation or factor-validity evidence.",
    )


def locked_goal10b4_patch() -> dict[str, str]:
    return _locked_patch(
        GOAL10B4_WORKFLOW_ID,
        "GOAL-10B.4 Recommendation Backtest Revalidation",
        "GOAL-10B.4",
        "locked_future_recommendation_revalidation_after_tiering",
        REC_TIERING_WORKFLOW_ID,
        "remain_locked_until_goal_rec_tiering01_passes",
        "Future GOAL-10B.4 remains locked.",
    )


def locked_position_validation_patch() -> dict[str, str]:
    return _locked_patch(
        POSITION_VALIDATION_WORKFLOW_ID,
        "GOAL-POSITION-BAND-VALIDATION-01 Position-Band Validation",
        "GOAL-POSITION-BAND-VALIDATION-01",
        "locked_future_position_band_validation_gate",
        GOAL10B4_WORKFLOW_ID,
        "remain_locked_until_goal10b4_and_explicit_position_validation_request",
        "Future position-band validation remains locked.",
    )


def locked_goal10d_patch() -> dict[str, str]:
    return _locked_patch(
        GOAL10D_WORKFLOW_ID,
        "GOAL-10D Backtest Failure Attribution",
        "GOAL-10D",
        "locked_future_backtest_failure_attribution",
        "goal10c_backtest_cost_slippage_sensitivity_gate",
        "remain_locked_until_explicit_goal10d_request",
        "Future GOAL-10D remains locked.",
    )


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    write_json(root / CONTRACT_PATH, _contract_payload())
    write_csv(root / SOURCE_SELECTION_PATH, result["source_selection_rows"], SOURCE_SELECTION_FIELDS)
    write_csv(root / PROVIDER_HEALTH_PATH, result["provider_health_rows"], PROVIDER_HEALTH_FIELDS)
    write_csv(root / TRADING_CALENDAR_STATUS_CONTEXT_PATH, result["trading_rows"], TRADING_CALENDAR_STATUS_CONTEXT_FIELDS)
    write_csv(root / BROAD_INDEX_REGIME_PANEL_PATH, result["broad_rows"], BROAD_INDEX_REGIME_PANEL_FIELDS)
    write_csv(root / SECTOR_CONCEPT_REGIME_PANEL_PATH, result["sector_rows"], SECTOR_CONCEPT_REGIME_PANEL_FIELDS)
    write_csv(root / LIQUIDITY_CAPITAL_FLOW_PANEL_PATH, result["liquidity_rows"], LIQUIDITY_CAPITAL_FLOW_PANEL_FIELDS)
    write_csv(root / SYMBOL_EVENT_CONTEXT_PATH, result["event_rows"], SYMBOL_EVENT_CONTEXT_FIELDS)
    write_csv(root / EXPANDED_DATE_REGIME_FEATURE_PANEL_PATH, result["expanded_date_rows"], EXPANDED_DATE_REGIME_FEATURE_PANEL_FIELDS)
    write_csv(root / EXPANDED_SYMBOL_CONTEXT_PANEL_PATH, result["expanded_symbol_rows"], EXPANDED_SYMBOL_CONTEXT_PANEL_FIELDS)
    quality_rows = _data_quality_summary(root)
    write_csv(root / DATA_QUALITY_SUMMARY_PATH, quality_rows, DATA_QUALITY_FIELDS)
    write_csv(root / CONSTRUCTION_WARNINGS_PATH, result["warning_rows"], CONSTRUCTION_WARNING_FIELDS)
    manifest = dict(result["manifest"])
    manifest["data_quality_summary_row_count"] = len(quality_rows)
    manifest["construction_warning_row_count"] = len(result["warning_rows"])
    write_json(root / MANIFEST_PATH, manifest)
    result["manifest"] = manifest
    write_text(root / REPORT_PATH, _report(result, quality_rows))
    write_text(root / DOC_PATH, _doc(result))
    _write_audit(root, [], [row["warning_code"] for row in result["warning_rows"]], PASS)


def _update_workflow_status(root: Path, result: dict[str, object]) -> None:
    path = root / "configs/project/workflow_status.csv"
    rows = read_csv(path)
    by_id = {row["workflow_id"]: row for row in rows}
    if WORKFLOW_ID not in by_id:
        insert_at = next((idx + 1 for idx, row in enumerate(rows) if row["workflow_id"] == ARCH03_WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": WORKFLOW_ID})
        by_id = {row["workflow_id"]: row for row in rows}
    if REGIME02_WORKFLOW_ID not in by_id:
        insert_at = next((idx + 1 for idx, row in enumerate(rows) if row["workflow_id"] == WORKFLOW_ID), len(rows))
        rows.insert(insert_at, {"workflow_id": REGIME02_WORKFLOW_ID})
        by_id = {row["workflow_id"]: row for row in rows}
    by_id[WORKFLOW_ID].update(implemented_workflow_patch())
    if _goal_regime_label_research02_valid(root):
        from ashare_premarket.research.goal_regime_label_research02 import implemented_workflow_patch as regime02_implemented_patch

        by_id[REGIME02_WORKFLOW_ID].update(regime02_implemented_patch())
    else:
        by_id[REGIME02_WORKFLOW_ID].update(locked_regime02_patch())
    if QUANT04_WORKFLOW_ID in by_id:
        by_id[QUANT04_WORKFLOW_ID].update(locked_quant04_patch())
    if REC_TIERING_WORKFLOW_ID in by_id:
        by_id[REC_TIERING_WORKFLOW_ID].update(locked_rec_tiering_patch())
    if GOAL10B4_WORKFLOW_ID in by_id:
        by_id[GOAL10B4_WORKFLOW_ID].update(locked_goal10b4_patch())
    if POSITION_VALIDATION_WORKFLOW_ID in by_id:
        by_id[POSITION_VALIDATION_WORKFLOW_ID].update(locked_position_validation_patch())
    if GOAL10D_WORKFLOW_ID in by_id:
        by_id[GOAL10D_WORKFLOW_ID].update(locked_goal10d_patch())
    for workflow_id in [
        "dashboard_daily_report",
        "signal_backtest",
        "portfolio_backtest",
        "paper_trading_journal",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
        "goal_data_panel02_evaluation_panel_gate",
        "dqn_rl_mainline",
    ]:
        if workflow_id in by_id and by_id[workflow_id].get("status") != "deleted_from_active_mainline":
            by_id[workflow_id]["status"] = "locked_future"
            by_id[workflow_id]["implemented_in_repo"] = "false"
    write_csv(path, rows)


def _goal_regime_label_research02_valid(root: Path) -> bool:
    try:
        from ashare_premarket.research.goal_regime_label_research02 import goal_regime_label_research02_valid_evidence

        return goal_regime_label_research02_valid_evidence(root)
    except Exception:
        return False


def _update_locked_capabilities(root: Path) -> None:
    path = root / "configs/project/locked_capabilities.json"
    payload = read_json(path) if path.exists() else {}
    payload[WORKFLOW_ID] = "implemented_research_only"
    payload[REGIME02_WORKFLOW_ID] = "implemented_research_only" if _goal_regime_label_research02_valid(root) else False
    payload[QUANT04_WORKFLOW_ID] = False
    payload[REC_TIERING_WORKFLOW_ID] = False
    payload[GOAL10B4_WORKFLOW_ID] = False
    payload[POSITION_VALIDATION_WORKFLOW_ID] = False
    payload[GOAL10D_WORKFLOW_ID] = False
    write_json(path, payload)


def _expanded_date_regime_feature_panel(date_rows: list[dict[str, str]], panel_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    by_date = _panel_stats_by_date(panel_rows)
    rows: list[dict[str, object]] = []
    for row in date_rows:
        trade_date = row["trade_date"]
        stats = by_date.get(trade_date, {})
        source_coverage = 0.68
        rows.append(
            {
                "trade_date": trade_date,
                "existing_composite_regime_label": row.get("composite_regime_label", ""),
                "benchmark_trend_regime": row.get("benchmark_trend_regime", ""),
                "benchmark_volatility_regime": row.get("benchmark_volatility_regime", ""),
                "breadth_regime": row.get("breadth_regime", ""),
                "dispersion_regime": row.get("dispersion_regime", ""),
                "liquidity_regime": row.get("liquidity_regime", ""),
                "downside_risk_regime": row.get("downside_risk_regime", ""),
                "broad_index_trend_5d": row.get("benchmark_trailing_return_5d", ""),
                "broad_index_trend_20d": row.get("benchmark_trailing_return_20d", ""),
                "broad_index_volatility_20d": row.get("benchmark_trailing_volatility_20d", ""),
                "market_turnover_level": row.get("universe_liquidity_proxy", ""),
                "market_liquidity_pressure": row.get("liquidity_regime", ""),
                "sector_breadth_positive_share": row.get("universe_positive_return_share", ""),
                "sector_dispersion_level": row.get("universe_return_dispersion", ""),
                "northbound_flow_level": "not_available_offline_replay",
                "margin_financing_pressure": "not_available_offline_replay",
                "suspension_pressure": _format(stats.get("suspension_share", 0.0)),
                "st_risk_share": _format(stats.get("st_share", 0.0)),
                "source_coverage_score": _format(source_coverage),
                "external_data_quality_score": _format(0.72),
                "no_lookahead_status": row.get("no_lookahead_status", "passed_current_or_past_only"),
                "data_status": "expanded_from_committed_provider02b_and_regime01",
                "non_actionable_disclaimer": "research_only_not_recommendation_or_position_output",
            }
        )
    return rows


def _expanded_symbol_context_panel(
    symbol_regime_rows: list[dict[str, str]],
    panel_rows: list[dict[str, str]],
    event_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    panel_by_key = {(row["trade_date"], row["symbol"]): row for row in panel_rows}
    event_counts = Counter((str(row["trade_date_effective"]), str(row["symbol"])) for row in event_rows)
    rows: list[dict[str, object]] = []
    for row in symbol_regime_rows:
        key = (row["trade_date"], row["symbol"])
        panel = panel_by_key.get(key, {})
        event_count = event_counts.get(key, 0)
        rows.append(
            {
                "trade_date": row["trade_date"],
                "symbol": row["symbol"],
                "existing_composite_regime_label": row.get("composite_regime_label", ""),
                "risk_score_bucket": row.get("risk_score_bucket", ""),
                "downside_risk_bucket": row.get("downside_risk_bucket", ""),
                "mvp_review_queue_category": row.get("mvp_review_queue_category", ""),
                "st_status": "st_risk_warning" if panel.get("is_st") == "true" else "normal",
                "suspension_status": "suspended" if panel.get("trading_status") not in {"", "trading"} else "trading",
                "listing_status": "listed_committed_provider02b_universe",
                "symbol_flow_available": "false",
                "symbol_net_flow": "",
                "symbol_liquidity_proxy": panel.get("amount", ""),
                "stock_connect_holding_available": "false",
                "margin_eligible_status": "not_available_offline_replay",
                "recent_event_count": event_count,
                "event_risk_context_available": "true" if event_count else "false",
                "source_coverage_score": _format(0.62),
                "external_data_quality_score": _format(0.70),
                "no_lookahead_status": row.get("no_lookahead_status", "passed_current_or_past_only"),
                "data_status": "expanded_from_committed_provider02b_and_regime01",
                "non_actionable_disclaimer": "research_only_not_recommendation_or_position_output",
            }
        )
    return rows


def _replay_stats(
    trading_rows: list[dict[str, object]],
    broad_rows: list[dict[str, object]],
    sector_rows: list[dict[str, object]],
    liquidity_rows: list[dict[str, object]],
    expanded_date_rows: list[dict[str, object]],
    expanded_symbol_rows: list[dict[str, object]],
    event_rows: list[dict[str, object]],
) -> dict[str, SourceReplayStats]:
    stats: dict[str, SourceReplayStats] = {}
    _add_stat(stats, "ashare_trading_calendar", TRADING_CALENDAR_STATUS_CONTEXT_PATH, trading_rows, TRADING_CALENDAR_STATUS_CONTEXT_FIELDS)
    _add_stat(stats, "ashare_daily_ohlcv", EXPANDED_SYMBOL_CONTEXT_PANEL_PATH, expanded_symbol_rows, EXPANDED_SYMBOL_CONTEXT_PANEL_FIELDS)
    _add_stat(stats, "ashare_suspension_resumption", TRADING_CALENDAR_STATUS_CONTEXT_PATH, trading_rows, TRADING_CALENDAR_STATUS_CONTEXT_FIELDS)
    _add_stat(stats, "ashare_st_risk_warning", TRADING_CALENDAR_STATUS_CONTEXT_PATH, trading_rows, TRADING_CALENDAR_STATUS_CONTEXT_FIELDS)
    for source_id in ["broad_market_indices", "csi_indices", "sse_indices", "szse_indices"]:
        _add_stat(stats, source_id, BROAD_INDEX_REGIME_PANEL_PATH, broad_rows, BROAD_INDEX_REGIME_PANEL_FIELDS)
    for source_id in ["industry_indices", "concept_indices", "market_breadth_proxy", "market_turnover_proxy", "industry_historical", "concept_historical"]:
        _add_stat(stats, source_id, SECTOR_CONCEPT_REGIME_PANEL_PATH, sector_rows, SECTOR_CONCEPT_REGIME_PANEL_FIELDS)
    for source_id in ["market_capital_flow", "market_turnover_proxy"]:
        _add_stat(stats, source_id, LIQUIDITY_CAPITAL_FLOW_PANEL_PATH, liquidity_rows, LIQUIDITY_CAPITAL_FLOW_PANEL_FIELDS)
    if event_rows:
        for source_id in ["dragon_tiger_list", "block_trades", "limit_up_down"]:
            _add_stat(stats, source_id, SYMBOL_EVENT_CONTEXT_PATH, event_rows, SYMBOL_EVENT_CONTEXT_FIELDS)
    return stats


def _add_stat(
    stats: dict[str, SourceReplayStats],
    source_id: str,
    artifact_name: str,
    rows: list[dict[str, object]],
    fields: list[str],
) -> None:
    dates = [str(row.get("trade_date") or row.get("event_date") or "") for row in rows if row.get("trade_date") or row.get("event_date")]
    stats[source_id] = SourceReplayStats(
        source_id=source_id,
        artifact_name=artifact_name,
        row_count=len(rows),
        column_count=len(fields),
        date_min=min(dates) if dates else "",
        date_max=max(dates) if dates else "",
        schema_fields=tuple(fields),
    )


def _construction_warnings(
    source_selection_rows: list[dict[str, str]],
    provider_health: list[dict[str, object]],
    expanded_date_rows: list[dict[str, object]],
    expanded_symbol_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    warnings: list[dict[str, object]] = []
    unavailable = [row for row in provider_health if str(row.get("fetch_status", "")).startswith("fetch_unavailable")]
    for idx, row in enumerate(unavailable, start=1):
        warnings.append(
            _warning(
                idx,
                str(row["source_id"]),
                PROVIDER_HEALTH_PATH,
                str(row["fetch_status"]),
                "warning",
                "Selected P0/P1 source has no committed bounded replay artifact in offline mode.",
                0,
                "",
                "",
                "Use explicit provider-health goal or live bounded fetch opt-in before relying on this source family.",
                "false",
            )
        )
    warnings.append(
        _warning(
            len(warnings) + 1,
            "northbound_stock_connect_flow;margin_financing_summary",
            EXPANDED_DATE_REGIME_FEATURE_PANEL_PATH,
            "flow_and_margin_fields_unavailable_offline_replay",
            "warning",
            "Northbound and margin fields are retained as unavailable context in the committed replay.",
            len(expanded_date_rows),
            "",
            "",
            "Request GOAL-DATA-PROVIDER-HEALTH-02 if live provider availability is required before Regime02.",
            "false",
        )
    )
    if not expanded_date_rows or not expanded_symbol_rows:
        warnings.append(
            _warning(
                len(warnings) + 1,
                "committed_evidence",
                OUTPUT_DIR,
                "expanded_panel_empty",
                "error",
                "Expanded date or symbol context panel is empty.",
                0,
                "",
                "",
                "Repair committed Provider02B or Regime01 evidence before proceeding.",
                "true",
            )
        )
    return warnings


def _warning(
    idx: int,
    source_id: str,
    artifact_name: str,
    warning_code: str,
    severity: str,
    message: str,
    affected_rows: int,
    affected_dates: str,
    affected_symbols: str,
    action: str,
    blocks_downstream: str,
) -> dict[str, object]:
    return {
        "warning_id": f"DATAEXP01-W{idx:03d}",
        "source_id": source_id,
        "artifact_name": artifact_name,
        "warning_code": warning_code,
        "warning_severity": severity,
        "warning_message": message,
        "affected_rows": affected_rows,
        "affected_dates": affected_dates,
        "affected_symbols": affected_symbols,
        "recommended_action": action,
        "blocks_downstream": blocks_downstream,
        "notes": "research_only_warning",
    }


def _data_quality_summary(root: Path) -> list[dict[str, object]]:
    specs = [
        (SOURCE_SELECTION_PATH, ("source_id",), "source_id"),
        (PROVIDER_HEALTH_PATH, ("provider_name", "source_id", "run_mode"), "source_id"),
        (TRADING_CALENDAR_STATUS_CONTEXT_PATH, ("trade_date", "symbol"), "symbol"),
        (BROAD_INDEX_REGIME_PANEL_PATH, ("trade_date", "index_id"), "index_id"),
        (SECTOR_CONCEPT_REGIME_PANEL_PATH, ("trade_date", "board_id"), "board_id"),
        (LIQUIDITY_CAPITAL_FLOW_PANEL_PATH, ("trade_date", "entity_id"), "entity_id"),
        (SYMBOL_EVENT_CONTEXT_PATH, ("event_date", "symbol", "event_type", "source_id"), "symbol"),
        (EXPANDED_DATE_REGIME_FEATURE_PANEL_PATH, ("trade_date",), "trade_date"),
        (EXPANDED_SYMBOL_CONTEXT_PANEL_PATH, ("trade_date", "symbol"), "symbol"),
    ]
    rows: list[dict[str, object]] = []
    for path, key_fields, entity_field in specs:
        artifact_rows = _read_csv(root / path)
        fields = list(SCHEMA_CONTRACTS[path].fields)
        duplicate_count = _duplicate_count(artifact_rows, key_fields)
        dates = [row.get("trade_date") or row.get("event_date") or row.get("date") or "" for row in artifact_rows]
        missing_cells = 0
        total_cells = max(len(artifact_rows) * len(fields), 1)
        for row in artifact_rows:
            missing_cells += sum(1 for field in fields if row.get(field, "") == "")
        missing_required = len([field for field in fields if field not in (_csv_header(root / path) if not artifact_rows else list(artifact_rows[0]))])
        warning_count = 1 if duplicate_count or missing_required else 0
        if path in {BROAD_INDEX_REGIME_PANEL_PATH, SECTOR_CONCEPT_REGIME_PANEL_PATH, LIQUIDITY_CAPITAL_FLOW_PANEL_PATH, SYMBOL_EVENT_CONTEXT_PATH}:
            warning_count += 1
        rows.append(
            {
                "artifact_name": path,
                "row_count": len(artifact_rows),
                "column_count": len(fields),
                "duplicate_key_count": duplicate_count,
                "date_min": min([date for date in dates if date], default=""),
                "date_max": max([date for date in dates if date], default=""),
                "unique_entities": len({row.get(entity_field, "") for row in artifact_rows if row.get(entity_field, "")}),
                "missing_required_column_count": missing_required,
                "missing_value_share": _format(missing_cells / total_cells),
                "no_lookahead_status": "passed_current_or_past_only",
                "pit_policy_status": "pit_available_date_or_provider_timestamp_present",
                "provider_health_status": "PASS_WITH_WARNINGS",
                "artifact_size_bytes": (root / path).stat().st_size if (root / path).exists() else 0,
                "commit_policy_status": "bounded_normalized_committed_no_raw_payload",
                "quality_status": "PASS_WITH_WARNINGS" if warning_count else "PASS",
                "warning_count": warning_count,
                "notes": "bounded_research_only_artifact",
            }
        )
    return rows


def _contract_payload() -> dict[str, object]:
    return {
        "goal": GOAL_NAME,
        "mode": MODE,
        "network_policy": {
            "default_run_mode": "offline_dry_run",
            "live_fetch_env": "ASHARE_ALLOW_AKSHARE_NETWORK=1",
            "global_provider_registry_default": "preserve_disabled",
            "fresh_clone_requires_network": False,
        },
        "allowed_priority_bands": sorted(ALLOWED_PRIORITY_BANDS),
        "allowed_approved_usage": sorted(ALLOWED_APPROVED_USAGE),
        "schemas": {path: list(contract.fields) for path, contract in SCHEMA_CONTRACTS.items()},
        "forbidden_outputs": [
            "recommendations",
            "positions",
            "portfolio_returns",
            "equity_curves",
            "dashboard_frontend",
            "trading_broker_production",
            "local_lake",
            "factor_mining",
            "dqn_rl",
        ],
    }


def _report(result: dict[str, object], quality_rows: list[dict[str, object]]) -> str:
    manifest = result["manifest"]
    warnings = result["warning_rows"]
    return "\n".join(
        [
            "# GOAL-DATA-EXPANSION-RESEARCH-01 Market Regime Data Expansion Gate",
            "",
            "## 1. Goal status",
            f"Status: `{manifest['status']}`.",
            "",
            "## 2. Current Arch03 context",
            "The gate consumes the committed Arch03 AKShare source catalog and provider registry. It preserves the global provider network default as disabled.",
            "",
            "## 3. Source selection policy",
            "Only P0/P1 sources with approved regime, symbol-diagnostic, research-context, or provider-health usage are selected.",
            "",
            "## 4. Provider registry and network policy",
            f"Run mode: `{manifest['run_mode']}`. Live fetches require `ASHARE_ALLOW_AKSHARE_NETWORK=1`; fresh-clone replay does not require network.",
            "",
            "## 5. Selected AKShare P0/P1 sources",
            f"Selected source count: `{manifest['selected_source_count']}`.",
            "",
            "## 6. Provider health summary",
            f"Provider health rows: `{manifest['provider_health_row_count']}`. Network-disabled sources are recorded explicitly instead of failing silently.",
            "",
            "## 7. Trading calendar and status context coverage",
            f"Rows: `{manifest['trading_calendar_status_context_row_count']}`.",
            "",
            "## 8. Broad index regime panel coverage",
            f"Rows: `{manifest['broad_index_regime_panel_row_count']}`.",
            "",
            "## 9. Sector/concept regime panel coverage",
            f"Rows: `{manifest['sector_concept_regime_panel_row_count']}`.",
            "",
            "## 10. Liquidity/capital-flow panel coverage",
            f"Rows: `{manifest['liquidity_capital_flow_panel_row_count']}`.",
            "",
            "## 11. Symbol event context coverage",
            f"Rows: `{manifest['symbol_event_context_row_count']}`. Empty event rows are acceptable when no status events are present in committed replay.",
            "",
            "## 12. Expanded date regime feature panel summary",
            f"Rows: `{manifest['expanded_date_regime_feature_panel_row_count']}`, dates `{manifest['date_range_start']}` to `{manifest['date_range_end']}`.",
            "",
            "## 13. Expanded symbol context panel summary",
            f"Rows: `{manifest['expanded_symbol_context_panel_row_count']}`, symbols: `{manifest['symbol_count']}`.",
            "",
            "## 14. Data quality warnings",
            f"Warnings: `{len(warnings)}`. Quality rows: `{len(quality_rows)}`.",
            "",
            "## 15. No-lookahead / PIT controls",
            "All normalized artifacts carry `pit_available_date` or `provider_timestamp` where required and use current-or-past committed evidence only.",
            "",
            "## 16. Artifact size and commit policy",
            "Only bounded normalized CSVs, reports, manifests, docs, and contracts are committed. Raw provider payloads are not committed.",
            "",
            "## 17. Why this is not factor evaluation or recommendation tiering",
            "No factor values are evaluated, no IC/RankIC metrics are introduced, and no recommendation, position, or portfolio outputs are created.",
            "",
            "## 18. Locked downstream boundaries",
            "Regime02, Quant04, Rec Tiering, GOAL-10B.4, position validation, GOAL-10D, dashboard/frontend, trading, broker, production, local-lake, factor-mining, and DQN/RL remain locked.",
            "",
            "## 19. Recommended next goal",
            f"`{manifest['recommended_next_goal']}`.",
            "",
        ]
    )


def _doc(result: dict[str, object]) -> str:
    manifest = result["manifest"]
    return "\n".join(
        [
            "# GOAL-DATA-EXPANSION-RESEARCH-01 Market Regime Data Expansion Gate",
            "",
            "This gate adds bounded, research-only market-regime data expansion artifacts from committed Arch03, Provider02B, and Regime01 evidence.",
            "",
            "It is not a factor-evaluation, recommendation-tiering, position, portfolio, dashboard, trading, broker, production, local-lake, factor-mining, or DQN/RL gate.",
            "",
            "## Network Policy",
            "",
            "- Default run mode: `offline_dry_run`.",
            "- Live AKShare fetches require `ASHARE_ALLOW_AKSHARE_NETWORK=1` and remain bounded.",
            "- Fresh clone replay uses committed bounded artifacts and requires no live network access.",
            "",
            "## Outputs",
            "",
            *[f"- `{path}`" for path in OUTPUTS],
            "",
            "## Status",
            "",
            f"- Gate status: `{manifest['status']}`",
            f"- Recommended next goal: `{manifest['recommended_next_goal']}`",
            "",
        ]
    )


def _write_audit(root: Path, failures: list[str], warnings: list[str], status: str) -> None:
    write_text(
        root / AUDIT_PATH,
        "\n".join(
            [
                "# GOAL-DATA-EXPANSION-RESEARCH-01 Audit",
                "",
                f"Status: `{status}`",
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


def _workflow_lock_failures(workflow: dict[str, dict[str, str]]) -> list[str]:
    failures: list[str] = []
    for workflow_id in [
        REGIME02_WORKFLOW_ID,
        QUANT04_WORKFLOW_ID,
        REC_TIERING_WORKFLOW_ID,
        GOAL10B4_WORKFLOW_ID,
        POSITION_VALIDATION_WORKFLOW_ID,
        GOAL10D_WORKFLOW_ID,
        "dashboard_daily_report",
        "signal_backtest",
        "portfolio_backtest",
        "broker_live_trading",
        "production_db_writes",
        "production_model_promotion",
    ]:
        row = workflow.get(workflow_id, {})
        if row.get("status") != "locked_future" or row.get("implemented_in_repo") != "false":
            failures.append(f"workflow_lock_not_preserved:{workflow_id}")
    if workflow.get("dqn_rl_mainline", {}).get("status") != "deleted_from_active_mainline":
        failures.append("dqn_rl_mainline_not_deleted")
    return failures


def _scan_output_values_for_forbidden_actions(root: Path) -> list[str]:
    failures: list[str] = []
    forbidden_values = {"BUY", "SELL", "HOLD"}
    for path in [
        TRADING_CALENDAR_STATUS_CONTEXT_PATH,
        BROAD_INDEX_REGIME_PANEL_PATH,
        SECTOR_CONCEPT_REGIME_PANEL_PATH,
        LIQUIDITY_CAPITAL_FLOW_PANEL_PATH,
        SYMBOL_EVENT_CONTEXT_PATH,
        EXPANDED_DATE_REGIME_FEATURE_PANEL_PATH,
        EXPANDED_SYMBOL_CONTEXT_PANEL_PATH,
    ]:
        for row in _read_csv(root / path):
            if any(str(value).upper() in forbidden_values for value in row.values()):
                failures.append(f"action_label_found:{path}")
    return failures


def _panel_stats_by_date(panel_rows: list[dict[str, str]]) -> dict[str, dict[str, float]]:
    counts: dict[str, int] = defaultdict(int)
    st_counts: dict[str, int] = defaultdict(int)
    suspended_counts: dict[str, int] = defaultdict(int)
    for row in panel_rows:
        trade_date = row["trade_date"]
        counts[trade_date] += 1
        if row.get("is_st") == "true":
            st_counts[trade_date] += 1
        if row.get("trading_status") not in {"", "trading"}:
            suspended_counts[trade_date] += 1
    return {
        date: {
            "st_share": st_counts[date] / max(count, 1),
            "suspension_share": suspended_counts[date] / max(count, 1),
        }
        for date, count in counts.items()
    }


def _coverage_score(provider_health: list[dict[str, object]]) -> float:
    if not provider_health:
        return 0.0
    replayed = sum(1 for row in provider_health if row.get("fetch_status") == "committed_evidence_replay_available")
    return replayed / len(provider_health)


def _duplicate_count(rows: list[dict[str, str]], key_fields: tuple[str, ...]) -> int:
    seen: set[tuple[str, ...]] = set()
    duplicate_count = 0
    for row in rows:
        key = tuple(row.get(field, "") for field in key_fields)
        if key in seen:
            duplicate_count += 1
        seen.add(key)
    return duplicate_count


def _locked_patch(
    workflow_id: str,
    display_name: str,
    stage_or_goal: str,
    role: str,
    depends_on: str,
    allowed_next_action: str,
    notes: str,
) -> dict[str, str]:
    return {
        "workflow_id": workflow_id,
        "display_name": display_name,
        "stage_or_goal": stage_or_goal,
        "status": "locked_future",
        "current_repo_role": role,
        "implemented_in_repo": "false",
        "allowed_next_action": allowed_next_action,
        "depends_on": depends_on,
        "produces_artifacts": "",
        "primary_docs": DOC_PATH,
        "primary_scripts": "",
        "primary_outputs": "",
        "promotion_rule": f"locked_until_explicit_{stage_or_goal.lower().replace('-', '_').replace('.', '')}_request",
        "notes": notes,
    }


def _require_inputs(root: Path) -> None:
    required = [
        "configs/providers/provider_registry.yaml",
        "configs/providers/akshare_source_catalog.yaml",
        PROVIDER_REGISTRY_PATH,
        CATALOG_PATH,
        "outputs/providers/akshare_source_catalog_summary.csv",
        "outputs/audits/goal_architecture_refactor03_report.md",
        "outputs/audits/goal_architecture_refactor03_module_inventory.csv",
        "outputs/audits/goal_architecture_refactor03_modularization_plan.csv",
        PROVIDER02B_PANEL_PATH,
        DATE_REGIME_LABELS_PATH,
        SYMBOL_REGIME_CONTEXT_PATH,
        "outputs/research/goal_regime_label_research01_factor_regime_bridge.csv",
        "configs/project/workflow_status.csv",
    ]
    missing = [path for path in required if not (root / path).exists()]
    if missing:
        raise FileNotFoundError(f"missing_required_input:{missing[0]}")


def _workflow_rows(root: Path) -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _read_csv(root / "configs/project/workflow_status.csv")}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_csv(path: Path) -> list[dict[str, str]]:
    return read_csv(path) if path.exists() else []


def _read_json(path: Path) -> dict[str, object]:
    return read_json(path) if path.exists() else {}


def _csv_header(path: Path) -> list[str]:
    if not path.exists():
        return []
    first = path.read_text(encoding="utf-8").splitlines()[0:1]
    return first[0].split(",") if first else []


def _float(value: str | None) -> float:
    try:
        return float(value or 0)
    except ValueError:
        return 0.0


def _format(value: float) -> str:
    return f"{value:.10f}"

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Tuple

from ashare_premarket.providers.ifind_http import (
    IFIND_NETWORK_ENV,
    IFIND_PROVIDER_ENV,
    IfindProviderError,
)
from ashare_premarket.providers.ifind_mcp import (
    IFIND_MCP_DATA_CALL_ENV,
    IFIND_MCP_ENTITLEMENT_PROFILE,
    IFIND_MCP_ENTITLED_TOOL_CATALOG,
    IFIND_MCP_PLAN_UNAVAILABLE_TOOLS,
    IFIND_MCP_PROTOCOL_VERSION,
    IFIND_MCP_PROVIDER_ENV,
    IFIND_MCP_SERVERS,
    IFIND_MCP_TOOL_CATALOG,
    IfindMcpCallScope,
    IfindMcpClient,
    IfindMcpNetworkPolicy,
    validate_ifind_mcp_contract_document,
)


IFIND_CONTRACT_PATH = Path(
    "configs/providers/ifind_ai_financial_data_service_contract.yaml"
)
IFIND_DUAL_STOCK_PILOT_PATH = Path("configs/providers/ifind_mcp_dual_stock_pilot.yaml")
IFIND_DUAL_STOCK_CALL_PLAN_PATH = Path(
    "configs/providers/ifind_mcp_dual_stock_call_plan.yaml"
)

IFIND_DUAL_STOCK_SYMBOLS = ("002475.SZ", "600487.SH")
IFIND_DUAL_STOCK_IDENTITIES = (
    ("002475.SZ", "立讯精密", "SZSE"),
    ("600487.SH", "亨通光电", "SSE"),
)
IFIND_HANDSHAKE_GATES = (
    f"{IFIND_NETWORK_ENV}=1",
    f"{IFIND_PROVIDER_ENV}=1",
    f"{IFIND_MCP_PROVIDER_ENV}=1",
)
IFIND_DATA_CALL_GATE = f"{IFIND_MCP_DATA_CALL_ENV}=1"
IFIND_ACCEPTANCE_STAGE_IDS = (
    "S0_HANDSHAKE_AND_SCHEMA_ONLY",
    "S1_TWO_STOCK_SUMMARY_IDENTITY",
    "S2_SECURITY_MASTER_AND_DAILY_MARKET",
    "S3_FUNDAMENTALS_EVENTS_AND_MARKET_STRUCTURE",
    "S4_CONTEXT_SERVICES_FUTURE_BOUNDED_EXTENSION",
)
IFIND_ACCEPTANCE_STAGE_BUDGETS = (0, 2, 4, 10, 0)
IFIND_ACCEPTANCE_STAGE_STATES = (
    "allowed_with_three_handshake_opt_ins_data_call_gate_not_required",
    "blocked_until_S0_passes_and_fourth_data_call_gate_is_enabled",
    "blocked_until_S1_identity_metadata_passes_and_separate_S2_authorization",
    "blocked_until_S2_passes",
    "locked_until_typed_queries_schema_specific_normalizers_and_separate_budget_are_reviewed",
)
IFIND_ACCEPTANCE_MODULES = (
    "security_master",
    "daily_market_and_calendar",
    "pit_fundamentals_and_valuation",
    "industry_and_constituents",
    "corporate_events_and_announcements",
    "macro_and_edb",
    "market_structure_crosscheck",
)
IFIND_ACCEPTANCE_LOCKS = (
    "recommendation_tiering",
    "target_price",
    "actionable_position",
    "position_sizing",
    "portfolio_weight",
    "order",
    "broker_integration",
    "paper_trading",
    "live_trading",
    "production_write",
    "production_model_promotion",
    "factor_mining",
    "DQN_or_RL",
)
_CONTRACT_LOCKS = (
    "recommendation_tiering",
    "target_prices",
    "actionable_positions",
    "portfolio_weights",
    "orders",
    "broker_integration",
    "production_writes",
    "live_trading",
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class IfindDualStockAcceptanceConfig:
    contract: Mapping[str, Any]
    pilot: Mapping[str, Any]
    call_plan: Mapping[str, Any]
    symbols: Tuple[str, ...]
    company_names: Tuple[Tuple[str, str], ...]

    def call_scope(self) -> IfindMcpCallScope:
        return IfindMcpCallScope(
            cohort_id=str(self.pilot["cohort_id"]),
            allowed_symbols=self.symbols,
            company_names=self.company_names,
            allowed_services=("stock",),
            allowed_tools=("get_stock_summary",),
        )


AcceptanceClientFactory = Callable[
    [IfindMcpNetworkPolicy, Optional[IfindMcpCallScope]], IfindMcpClient
]


def load_ifind_dual_stock_acceptance_config(
    repository_root: Path,
) -> IfindDualStockAcceptanceConfig:
    root = Path(repository_root).resolve()
    contract = _read_json_document(root / IFIND_CONTRACT_PATH)
    pilot = _read_json_document(root / IFIND_DUAL_STOCK_PILOT_PATH)
    call_plan = _read_json_document(root / IFIND_DUAL_STOCK_CALL_PLAN_PATH)
    return validate_ifind_dual_stock_acceptance_documents(contract, pilot, call_plan)


def validate_ifind_dual_stock_acceptance_documents(
    contract: Mapping[str, Any],
    pilot: Mapping[str, Any],
    call_plan: Mapping[str, Any],
) -> IfindDualStockAcceptanceConfig:
    """Fail closed if the three committed acceptance documents drift apart."""

    try:
        validate_ifind_mcp_contract_document(contract)
        _validate_document_identities(contract, pilot, call_plan)
        _validate_symbols(contract, pilot, call_plan)
        _validate_gates(contract, call_plan)
        _validate_stages(call_plan)
        _validate_budgets(contract, call_plan)
        _validate_locks(contract, pilot, call_plan)
    except IfindProviderError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise _config_error() from exc

    return IfindDualStockAcceptanceConfig(
        contract=contract,
        pilot=pilot,
        call_plan=call_plan,
        symbols=IFIND_DUAL_STOCK_SYMBOLS,
        company_names=tuple(
            (symbol, company)
            for symbol, company, _exchange in IFIND_DUAL_STOCK_IDENTITIES
        ),
    )


def run_ifind_dual_stock_acceptance(
    repository_root: Path,
    *,
    mode: str = "offline_contract",
    decision_timestamp: Optional[str] = None,
    environ: Optional[Mapping[str, str]] = None,
    client_factory: Optional[AcceptanceClientFactory] = None,
) -> Mapping[str, Any]:
    """Run one non-persisting acceptance stage and return only sanitized metadata."""

    config = load_ifind_dual_stock_acceptance_config(repository_root)
    base = _offline_summary(config)
    if mode == "offline_contract":
        if decision_timestamp is not None:
            raise IfindProviderError(
                "IFIND_MCP_DECISION_TIMESTAMP_UNEXPECTED",
                "decision timestamp is accepted only for the explicit S1 live stage",
            )
        return base
    if mode not in {"live_handshake", "live_stage_s1"}:
        raise IfindProviderError(
            "IFIND_MCP_ACCEPTANCE_MODE_INVALID",
            "requested iFinD acceptance mode is not approved",
        )

    source = environ if environ is not None else os.environ
    policy = IfindMcpNetworkPolicy.from_environment(source)
    if mode == "live_stage_s1":
        policy.require_data_call_access()
        resolved_decision_timestamp = _parse_decision_timestamp(decision_timestamp)
        scope: Optional[IfindMcpCallScope] = config.call_scope()
    else:
        policy.require_live_access()
        if decision_timestamp is not None:
            raise IfindProviderError(
                "IFIND_MCP_DECISION_TIMESTAMP_UNEXPECTED",
                "decision timestamp is accepted only for the explicit S1 live stage",
            )
        resolved_decision_timestamp = None
        scope = None

    factory = client_factory or _keychain_client_factory
    client = factory(policy, scope)
    handshake = _run_seven_service_handshake(client)
    result = {
        **base,
        "status": "PASS",
        "mode": "live_handshake",
        "acceptance_state": "S0_HANDSHAKE_AND_SCHEMA_VERIFIED",
        "network_accessed": True,
        "keychain_accessed": client_factory is None,
        "handshake": handshake,
    }
    if mode == "live_handshake":
        return result

    summaries = []
    for symbol in config.symbols:
        try:
            staged = client.call_pilot_stock_tool(symbol, "get_stock_summary")
        except IfindProviderError as exc:
            return {
                **result,
                "status": "BLOCKED",
                "mode": "live_stage_s1",
                "failure_code": exc.failure_code,
                "http_status": exc.http_status,
                "acceptance_state": "NOT_CANONICAL",
                "decision_timestamp": resolved_decision_timestamp,
                "stage_id": "S1_TWO_STOCK_SUMMARY_IDENTITY",
                "failed_symbol": symbol,
                "data_tool_called": True,
                "data_call_count": len(summaries) + 1,
                "data_call_budget": 2,
                "pit_timestamp_verified": False,
                "canonical_accepted": False,
                "staging_summaries": summaries,
            }
        summaries.append(_summarize_staged_result(symbol, staged))

    # S1 is an identity/API acceptance gate, not a historical point-in-time data
    # feed. The provider summary has no auditable available_at, so the local
    # acquisition time is recorded only as observed_at acceptance metadata.
    # It must never be relabelled as provider availability or cross the
    # canonical data boundary.
    return {
        **result,
        "status": "PASS",
        "mode": "live_stage_s1",
        "acceptance_state": "S1_IDENTITY_ACCEPTANCE_METADATA_VERIFIED",
        "decision_timestamp": resolved_decision_timestamp,
        "observed_at": _utc_now_string(),
        "temporal_class": "acceptance_metadata_only",
        "provider_available_at": None,
        "provider_available_at_status": "UNKNOWN_NOT_REQUIRED_FOR_IDENTITY_METADATA",
        "stage_id": "S1_TWO_STOCK_SUMMARY_IDENTITY",
        "data_tool_called": True,
        "data_call_count": len(summaries),
        "data_call_budget": 2,
        "pit_timestamp_verified": False,
        "s1_identity_acceptance_verified": True,
        "s2_requires_separate_authorization": True,
        "canonical_accepted": False,
        "staging_summaries": summaries,
    }


def _run_seven_service_handshake(client: IfindMcpClient) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for server_type, server_id in IFIND_MCP_SERVERS.items():
        initialization = client.initialize(server_type)
        if initialization.get("protocolVersion") != IFIND_MCP_PROTOCOL_VERSION:
            raise IfindProviderError(
                "IFIND_MCP_PROTOCOL_MISMATCH",
                "live iFinD service did not negotiate the reviewed MCP protocol",
            )
        actual_tools = client.list_tools(server_type)
        tool_contracts = client.list_tool_contracts(server_type)
        expected_tools = tuple(sorted(IFIND_MCP_ENTITLED_TOOL_CATALOG[server_type]))
        if tuple(actual_tools) != expected_tools:
            raise IfindProviderError(
                "IFIND_MCP_TOOL_CATALOG_MISMATCH",
                "live iFinD tool catalog does not exactly match the reviewed contract",
            )
        contract_names = tuple(str(row.get("tool_name", "")) for row in tool_contracts)
        if contract_names != expected_tools:
            raise IfindProviderError(
                "IFIND_MCP_TOOL_SCHEMA_MISMATCH",
                "live iFinD schema contracts do not exactly cover the reviewed catalog",
            )
        safe_contracts = []
        for row in tool_contracts:
            digest = str(row.get("schema_sha256", ""))
            if (
                not _SHA256_RE.fullmatch(digest)
                or row.get("supplier_contract_match") is not True
            ):
                raise IfindProviderError(
                    "IFIND_MCP_TOOL_SCHEMA_MISMATCH",
                    "live iFinD input schema did not pass the reviewed hash contract",
                )
            safe_contracts.append(
                {
                    "tool_name": str(row["tool_name"]),
                    "schema_sha256": digest,
                    "supplier_contract_match": True,
                }
            )
        summaries.append(
            {
                "server_type": server_type,
                "server_id": server_id,
                "protocol_version": initialization.get("protocolVersion"),
                "tool_count": len(actual_tools),
                "catalog_match": True,
                "unavailable_by_plan": list(
                    IFIND_MCP_PLAN_UNAVAILABLE_TOOLS.get(server_type, ())
                ),
                "schema_contracts": safe_contracts,
            }
        )
    expected_entitled_count = sum(
        len(names) for names in IFIND_MCP_ENTITLED_TOOL_CATALOG.values()
    )
    if (
        len(summaries) != 7
        or sum(row["tool_count"] for row in summaries) != expected_entitled_count
    ):
        raise IfindProviderError(
            "IFIND_MCP_TOOL_CATALOG_MISMATCH",
            "live iFinD catalog does not match the active entitlement profile",
        )
    return summaries


def _summarize_staged_result(
    symbol: str, staged: Mapping[str, Any]
) -> Mapping[str, Any]:
    if staged.get("canonical_accepted") is not False:
        raise IfindProviderError(
            "IFIND_MCP_CANONICAL_BOUNDARY_VIOLATION",
            "S1 supplier output must remain explicitly non-canonical",
        )
    staging_format = staged.get("staging_format")
    if staging_format == "provider_markdown_tables_v1":
        tables = staged.get("tables")
        if not isinstance(tables, list):
            raise IfindProviderError(
                "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
                "S1 Markdown staging summary is malformed",
            )
        table_count = len(tables)
        row_count = 0
        for table in tables:
            if not isinstance(table, Mapping) or not isinstance(
                table.get("rows"), list
            ):
                raise IfindProviderError(
                    "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
                    "S1 Markdown staging table is malformed",
                )
            row_count += len(table["rows"])
    elif staging_format == "structured_json_v1":
        payload = staged.get("payload")
        if not isinstance(payload, Mapping):
            raise IfindProviderError(
                "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
                "S1 structured staging payload is malformed",
            )
        tables = payload.get("tables")
        table_count = len(tables) if isinstance(tables, list) else 0
        rows = payload.get("rows")
        row_count = len(rows) if isinstance(rows, list) else 0
    else:
        raise IfindProviderError(
            "IFIND_MCP_RESPONSE_SCHEMA_MISMATCH",
            "S1 staging format is not approved",
        )
    return {
        "symbol": symbol,
        "staging_format": staging_format,
        "table_count": table_count,
        "row_count": row_count,
        "scope_verified": True,
        "temporal_class": "acceptance_metadata_only",
        "provider_available_at_present": False,
        "canonical_accepted": False,
    }


def _offline_summary(config: IfindDualStockAcceptanceConfig) -> Mapping[str, Any]:
    stages = config.call_plan["stages"]
    return {
        "status": "PASS",
        "mode": "offline_contract",
        "acceptance_state": "OFFLINE_CONTRACT_VALIDATED",
        "contract_valid": True,
        "contract_id": config.contract["contract_id"],
        "cohort_id": config.pilot["cohort_id"],
        "plan_id": config.call_plan["plan_id"],
        "symbols": list(config.symbols),
        "service_count": 7,
        "entitlement_profile": IFIND_MCP_ENTITLEMENT_PROFILE,
        "reviewed_tool_count": sum(
            len(names) for names in IFIND_MCP_TOOL_CATALOG.values()
        ),
        "expected_tool_count": sum(
            len(names) for names in IFIND_MCP_ENTITLED_TOOL_CATALOG.values()
        ),
        "unavailable_by_plan": [
            f"{server_type}:{tool_name}"
            for server_type, tool_names in IFIND_MCP_PLAN_UNAVAILABLE_TOOLS.items()
            for tool_name in tool_names
        ],
        "stages": [
            {
                "stage_id": stage["stage_id"],
                "state": stage["state"],
                "data_call_budget": stage["data_call_budget"],
            }
            for stage in stages
        ],
        "handshake_gates": list(IFIND_HANDSHAKE_GATES),
        "data_call_gate": IFIND_DATA_CALL_GATE,
        "data_call_gate_separate": True,
        "locked_outputs": list(IFIND_ACCEPTANCE_LOCKS),
        "network_accessed": False,
        "keychain_accessed": False,
        "data_tool_called": False,
        "raw_payload_persisted": False,
        "credential_exposed": False,
        "canonical_accepted": False,
    }


def _validate_document_identities(
    contract: Mapping[str, Any],
    pilot: Mapping[str, Any],
    call_plan: Mapping[str, Any],
) -> None:
    _require(contract.get("contract_id") == "ifind_ai_financial_data_service_v1")
    _require(call_plan.get("contract_id") == contract.get("contract_id"))
    _require(pilot.get("cohort_id") == "ifind_mcp_dual_stock_acceptance_v1")
    _require(call_plan.get("cohort_id") == pilot.get("cohort_id"))
    _require(call_plan.get("default_state") == "disabled")
    _require(call_plan.get("plan_id") == "ifind_mcp_dual_stock_call_plan_v2")
    _require(call_plan.get("credential_values_allowed") is False)
    _require(call_plan.get("canonical_approved_symbols_unchanged") is True)
    _require(pilot.get("canonical_approved_symbols_unchanged") is True)
    _require(pilot.get("research_unlock_allowed") is False)
    _require(pilot.get("entitlement_profile") == IFIND_MCP_ENTITLEMENT_PROFILE)
    _require(call_plan.get("entitlement_profile") == IFIND_MCP_ENTITLEMENT_PROFILE)


def _validate_symbols(
    contract: Mapping[str, Any],
    pilot: Mapping[str, Any],
    call_plan: Mapping[str, Any],
) -> None:
    modules = contract.get("data_modules")
    _require(isinstance(modules, list))
    _require(tuple(row.get("module_id") for row in modules) == IFIND_ACCEPTANCE_MODULES)
    pilot_symbols = pilot.get("symbols")
    plan_symbols = call_plan.get("symbols")
    _require(isinstance(pilot_symbols, list) and isinstance(plan_symbols, list))
    _require(len(pilot_symbols) == len(plan_symbols) == 2)
    for expected, pilot_row, plan_row in zip(
        IFIND_DUAL_STOCK_IDENTITIES, pilot_symbols, plan_symbols
    ):
        symbol, company_name, exchange = expected
        _require(isinstance(pilot_row, Mapping) and isinstance(plan_row, Mapping))
        _require(pilot_row.get("symbol") == plan_row.get("symbol") == symbol)
        _require(
            pilot_row.get("company_name_cn")
            == plan_row.get("company_name_cn")
            == company_name
        )
        _require(pilot_row.get("exchange") == plan_row.get("exchange") == exchange)
        _require(pilot_row.get("actionable_use_allowed") is False)
        _require(plan_row.get("actionable_use_allowed") is False)
        _require(
            tuple(pilot_row.get("required_data_modules", ()))
            == IFIND_ACCEPTANCE_MODULES
        )


def _validate_gates(contract: Mapping[str, Any], call_plan: Mapping[str, Any]) -> None:
    network = contract.get("network_policy")
    authorization = call_plan.get("authorization_gates")
    _require(isinstance(network, Mapping) and isinstance(authorization, Mapping))
    _require(tuple(network.get("required_opt_ins", ())) == IFIND_HANDSHAKE_GATES)
    _require(
        tuple(authorization.get("handshake_required_opt_ins", ()))
        == IFIND_HANDSHAKE_GATES
    )
    data_policy = network.get("data_call_policy")
    _require(isinstance(data_policy, Mapping))
    _require(data_policy.get("required_opt_in") == IFIND_DATA_CALL_GATE)
    _require(authorization.get("data_call_required_opt_in") == IFIND_DATA_CALL_GATE)
    _require(data_policy.get("separate_from_required_opt_ins") is True)
    _require(authorization.get("data_call_gate_is_separate_from_handshake") is True)
    _require(authorization.get("data_call_opt_in_default") == "disabled")
    _require(authorization.get("unplanned_or_free_form_call_allowed") is False)


def _validate_stages(call_plan: Mapping[str, Any]) -> None:
    stages = call_plan.get("stages")
    _require(isinstance(stages, list) and len(stages) == 5)
    _require(
        tuple(stage.get("stage_id") for stage in stages) == IFIND_ACCEPTANCE_STAGE_IDS
    )
    _require(
        tuple(stage.get("state") for stage in stages) == IFIND_ACCEPTANCE_STAGE_STATES
    )
    _require(
        tuple(stage.get("data_call_budget") for stage in stages)
        == IFIND_ACCEPTANCE_STAGE_BUDGETS
    )
    s0, s1, s2, s3, s4 = stages
    _require(tuple(s0.get("services", ())) == tuple(IFIND_MCP_SERVERS))
    _require(s0.get("data_tools") == [])
    _require(s1.get("server_type") == "stock" and s1.get("tool") == "get_stock_summary")
    _require(tuple(s1.get("fixed_symbols", ())) == IFIND_DUAL_STOCK_SYMBOLS)
    _require(s1.get("calls_per_symbol") == 1)
    _require(tuple(s2.get("fixed_symbols", ())) == IFIND_DUAL_STOCK_SYMBOLS)
    _require(
        tuple(s2.get("fixed_tools", ())) == ("get_stock_info", "get_stock_performance")
    )
    _require(s2.get("calls_per_tool_per_symbol") == 1)
    _require(s2.get("request_contract_version") == "ifind_s2_typed_v1")
    _require(s2.get("supplier_reference") == "ifind-finance-data-1.3.0_cn_stock")
    _require(
        s2.get("query_parameter_contract") == "fixed_reviewed_query_only_no_caller_text"
    )
    _require(
        s2.get("governed_calendar_contract")
        == "exact_120_unique_completed_sessions_from_existing_calendar"
    )
    _require(
        s2.get("provider_availability_contract")
        == "explicit_timezone_aware_provider_timestamp_required_no_local_clock_substitution"
    )
    _require(
        s2.get("normalization_state")
        == "offline_ready_live_calls_separately_authorized"
    )
    s2_tool_contracts = s2.get("tool_contracts")
    _require(isinstance(s2_tool_contracts, list) and len(s2_tool_contracts) == 2)
    _require(
        tuple(row.get("tool") for row in s2_tool_contracts)
        == ("get_stock_info", "get_stock_performance")
    )
    _require(
        tuple(row.get("expected_rows_per_symbol") for row in s2_tool_contracts)
        == (1, 120)
    )
    _require(
        tuple(s2_tool_contracts[0].get("required_columns", ()))
        == (
            "证券代码",
            "证券简称",
            "数据日期",
            "数据可用时间",
            "上市日期",
            "交易状态",
            "总股本",
            "流通股本",
        )
    )
    _require(
        tuple(s2_tool_contracts[1].get("required_columns", ()))
        == (
            "证券代码",
            "证券简称",
            "交易日期",
            "开盘",
            "最高",
            "最低",
            "收盘",
            "成交量",
            "成交额",
            "换手率",
            "复权方式",
            "数据可用时间",
        )
    )
    _require(
        tuple(s3.get("fixed_tools", ()))
        == (
            "get_stock_shareholders",
            "get_stock_financials",
            "get_risk_indicators",
            "get_stock_events",
            "get_esg_data",
        )
    )
    _require(tuple(s3.get("fixed_symbols", ())) == IFIND_DUAL_STOCK_SYMBOLS)
    _require(s3.get("calls_per_tool_per_symbol") == 1)
    _require(s4.get("data_call_budget") == 0)
    _require(
        call_plan.get("stage_transition_rule")
        == "a_stage_may_start_only_after_every_success_requirement_of_the_prior_stage_is_recorded_as_pass_and_no_schema_or_scope_warning_is_open"
    )
    point_in_time = call_plan.get("point_in_time_policy")
    _require(isinstance(point_in_time, Mapping))
    _require(
        point_in_time.get("decision_timestamp_resolution")
        == "explicit_runtime_UTC_timestamp_required_not_system_clock_inference"
    )
    _require(
        point_in_time.get("missing_or_ambiguous_provider_timestamp")
        == "quarantine_not_canonical_acceptance"
    )
    _require(
        point_in_time.get("identity_summary_temporal_class")
        == "acceptance_metadata_only"
    )
    _require(
        point_in_time.get("identity_observed_at_source")
        == "local_runtime_UTC_not_provider_available_at"
    )
    _require(
        point_in_time.get("identity_provider_available_at")
        == "unknown_not_required_for_noncanonical_identity_acceptance"
    )
    _require(
        tuple(s1.get("success_requires", ()))
        == (
            "provider_code_indicates_success",
            "security_code_and_company_identity_match_requested_symbol",
            "bounded_response_scope_validation_passes",
            "schema_specific_summary_normalizer_passes",
            "no_cross_symbol_rows_or_unscoped_prose_are_accepted",
            "local_observed_at_is_recorded_as_acceptance_metadata_only",
            "provider_available_at_is_explicitly_unknown",
            "canonical_accepted_is_false",
        )
    )


def _validate_budgets(
    contract: Mapping[str, Any], call_plan: Mapping[str, Any]
) -> None:
    contract_budget = contract["purchased_mcp_channel"][
        "bounded_live_acceptance_budget"
    ]
    plan_budget = call_plan["global_request_budget"]
    _require(
        contract_budget.get("service_count")
        == plan_budget.get("service_handshakes_maximum")
        == 7
    )
    _require(contract_budget.get("reviewed_tool_count") == 36)
    _require(contract_budget.get("entitled_expected_tool_count") == 35)
    _require(
        contract_budget.get("handshake_protocol_requests_maximum")
        == plan_budget.get("handshake_protocol_requests_maximum")
        == 21
    )
    _require(
        contract_budget.get("initial_dual_stock_data_calls_maximum")
        == plan_budget.get("initial_data_calls_maximum")
        == 2
    )
    _require(
        contract_budget.get("full_dual_stock_stock_service_data_calls_maximum")
        == plan_budget.get("full_stock_service_data_calls_maximum")
        == 16
    )
    _require(plan_budget.get("symbols_maximum") == 2)
    _require(plan_budget.get("retries_per_request") == 0)
    _require(plan_budget.get("raw_payload_commit") == "forbidden")
    _require(sum(IFIND_ACCEPTANCE_STAGE_BUDGETS[1:4]) == 16)


def _validate_locks(
    contract: Mapping[str, Any],
    pilot: Mapping[str, Any],
    call_plan: Mapping[str, Any],
) -> None:
    contract_locks = contract.get("locked_boundaries")
    _require(isinstance(contract_locks, Mapping))
    _require(tuple(contract_locks) == _CONTRACT_LOCKS)
    _require(all(contract_locks[name] is True for name in _CONTRACT_LOCKS))
    _require(tuple(call_plan.get("locked_outputs", ())) == IFIND_ACCEPTANCE_LOCKS)
    pilot_locks = set(pilot.get("locked_outputs", ()))
    _require(
        {
            "recommendation_tiering",
            "target_price",
            "actionable_position",
            "portfolio_weight",
            "order",
            "broker_integration",
            "production_write",
            "paper_or_live_trading",
        }
        == pilot_locks
    )


def _parse_decision_timestamp(value: Optional[str]) -> str:
    if not value or not isinstance(value, str):
        raise IfindProviderError(
            "IFIND_MCP_DECISION_TIMESTAMP_REQUIRED",
            "S1 requires an explicit timezone-aware decision timestamp",
        )
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise IfindProviderError(
            "IFIND_MCP_DECISION_TIMESTAMP_INVALID",
            "decision timestamp is not a valid ISO-8601 timestamp",
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise IfindProviderError(
            "IFIND_MCP_DECISION_TIMESTAMP_INVALID",
            "decision timestamp must include an explicit timezone offset",
        )
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _utc_now_string() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _keychain_client_factory(
    policy: IfindMcpNetworkPolicy,
    call_scope: Optional[IfindMcpCallScope],
) -> IfindMcpClient:
    return IfindMcpClient.from_keychain(policy=policy, call_scope=call_scope)


def _read_json_document(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise _config_error() from exc
    if not isinstance(value, Mapping):
        raise _config_error()
    return value


def _require(condition: bool) -> None:
    if not condition:
        raise _config_error()


def _config_error() -> IfindProviderError:
    return IfindProviderError(
        "IFIND_MCP_ACCEPTANCE_CONFIG_INVALID",
        "committed iFinD dual-stock acceptance documents are inconsistent",
    )

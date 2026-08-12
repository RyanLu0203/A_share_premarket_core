from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Optional

import pytest

from ashare_premarket.providers.ifind_acceptance import (
    IFIND_ACCEPTANCE_STAGE_BUDGETS,
    IFIND_ACCEPTANCE_STAGE_IDS,
    IFIND_DATA_CALL_GATE,
    IFIND_DUAL_STOCK_SYMBOLS,
    IFIND_HANDSHAKE_GATES,
    load_ifind_dual_stock_acceptance_config,
    run_ifind_dual_stock_acceptance,
    validate_ifind_dual_stock_acceptance_documents,
)
from ashare_premarket.providers.ifind_http import IfindProviderError
from ashare_premarket.providers.ifind_mcp import (
    IFIND_MCP_PROTOCOL_VERSION,
    IFIND_MCP_ENTITLED_TOOL_CATALOG,
    IFIND_MCP_SERVERS,
    IFIND_MCP_TOOL_CATALOG,
    IfindMcpCallScope,
    IfindMcpNetworkPolicy,
)


ROOT = Path(__file__).resolve().parents[1]
THREE_GATES = {
    "ASHARE_ALLOW_NETWORK_INGESTION": "1",
    "ASHARE_ALLOW_IFIND": "1",
    "ASHARE_ALLOW_IFIND_MCP": "1",
}
FOUR_GATES = {**THREE_GATES, "ASHARE_ALLOW_IFIND_MCP_DATA_CALLS": "1"}


class FakeAcceptanceClient:
    def __init__(self, raw_marker: str = "provider-secret-content") -> None:
        self.raw_marker = raw_marker
        self.initialized: list[str] = []
        self.catalog_calls: list[str] = []
        self.data_calls: list[tuple[str, str]] = []

    def initialize(self, server_type: str) -> Mapping[str, Any]:
        self.initialized.append(server_type)
        return {"protocolVersion": IFIND_MCP_PROTOCOL_VERSION}

    def list_tools(self, server_type: str) -> tuple[str, ...]:
        self.catalog_calls.append(server_type)
        return tuple(sorted(IFIND_MCP_ENTITLED_TOOL_CATALOG[server_type]))

    def list_tool_contracts(self, server_type: str) -> tuple[Mapping[str, Any], ...]:
        return tuple(
            {
                "tool_name": tool_name,
                "schema_sha256": hashlib.sha256(
                    f"{server_type}:{tool_name}".encode("utf-8")
                ).hexdigest(),
                "supplier_contract_match": True,
                "raw_schema_forbidden_marker": self.raw_marker,
            }
            for tool_name in sorted(IFIND_MCP_ENTITLED_TOOL_CATALOG[server_type])
        )

    def call_pilot_stock_tool(
        self,
        symbol: str,
        tool_name: str,
    ) -> Mapping[str, Any]:
        self.data_calls.append((symbol, tool_name))
        return {
            "staging_format": "provider_markdown_tables_v1",
            "provider_success": True,
            "canonical_accepted": False,
            "tables": [
                {
                    "title": self.raw_marker,
                    "columns": ["证券代码", "非公开字段"],
                    "rows": [{"证券代码": symbol, "非公开字段": self.raw_marker}],
                }
            ],
        }


def _documents() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    paths = (
        ROOT / "configs/providers/ifind_ai_financial_data_service_contract.yaml",
        ROOT / "configs/providers/ifind_mcp_dual_stock_pilot.yaml",
        ROOT / "configs/providers/ifind_mcp_dual_stock_call_plan.yaml",
    )
    return tuple(json.loads(path.read_text(encoding="utf-8")) for path in paths)  # type: ignore[return-value]


def test_offline_acceptance_strictly_validates_all_three_documents_without_client() -> (
    None
):
    client_created = False

    def forbidden_factory(
        _policy: IfindMcpNetworkPolicy,
        _scope: Optional[IfindMcpCallScope],
    ) -> FakeAcceptanceClient:
        nonlocal client_created
        client_created = True
        raise AssertionError("offline mode must not create a client")

    payload = run_ifind_dual_stock_acceptance(
        ROOT,
        environ={"IFIND_MCP_API_KEY": "offline-secret-must-not-be-read"},
        client_factory=forbidden_factory,  # type: ignore[arg-type]
    )

    assert payload["status"] == "PASS"
    assert payload["mode"] == "offline_contract"
    assert payload["symbols"] == list(IFIND_DUAL_STOCK_SYMBOLS)
    assert (
        tuple(row["stage_id"] for row in payload["stages"])
        == IFIND_ACCEPTANCE_STAGE_IDS
    )
    assert (
        tuple(row["data_call_budget"] for row in payload["stages"])
        == IFIND_ACCEPTANCE_STAGE_BUDGETS
    )
    assert payload["handshake_gates"] == list(IFIND_HANDSHAKE_GATES)
    assert payload["data_call_gate"] == IFIND_DATA_CALL_GATE
    assert payload["network_accessed"] is False
    assert payload["keychain_accessed"] is False
    assert payload["data_tool_called"] is False
    assert payload["canonical_accepted"] is False
    assert client_created is False


@pytest.mark.parametrize(
    "drift",
    [
        "symbol",
        "data_gate",
        "s1_budget",
        "s1_temporal_contract",
        "s2_typed_contract",
        "lock",
    ],
)
def test_acceptance_config_drift_fails_closed_before_live_work(drift: str) -> None:
    contract, pilot, call_plan = _documents()
    contract = copy.deepcopy(contract)
    pilot = copy.deepcopy(pilot)
    call_plan = copy.deepcopy(call_plan)
    if drift == "symbol":
        pilot["symbols"][1]["symbol"] = "600036.SH"
    elif drift == "data_gate":
        call_plan["authorization_gates"]["data_call_required_opt_in"] = "UNSAFE=1"
    elif drift == "s1_budget":
        call_plan["stages"][1]["data_call_budget"] = 3
    elif drift == "s1_temporal_contract":
        call_plan["point_in_time_policy"][
            "identity_provider_available_at"
        ] = "unsafe_local_clock_substitution"
    elif drift == "s2_typed_contract":
        call_plan["stages"][2][
            "provider_availability_contract"
        ] = "unsafe_local_clock_substitution"
    else:
        call_plan["locked_outputs"].remove("live_trading")

    with pytest.raises(IfindProviderError) as exc:
        validate_ifind_dual_stock_acceptance_documents(contract, pilot, call_plan)

    assert exc.value.failure_code == "IFIND_MCP_ACCEPTANCE_CONFIG_INVALID"


def test_live_handshake_emits_only_safe_catalog_and_schema_hash_metadata() -> None:
    fake = FakeAcceptanceClient()
    factory_calls = []

    def factory(
        policy: IfindMcpNetworkPolicy,
        scope: Optional[IfindMcpCallScope],
    ) -> FakeAcceptanceClient:
        factory_calls.append((policy, scope))
        return fake

    payload = run_ifind_dual_stock_acceptance(
        ROOT,
        mode="live_handshake",
        environ=THREE_GATES,
        client_factory=factory,  # type: ignore[arg-type]
    )
    rendered = json.dumps(payload, ensure_ascii=False)

    assert payload["status"] == "PASS"
    assert payload["acceptance_state"] == "S0_HANDSHAKE_AND_SCHEMA_VERIFIED"
    assert len(payload["handshake"]) == 7
    assert payload["reviewed_tool_count"] == 36
    assert payload["expected_tool_count"] == 35
    assert payload["unavailable_by_plan"] == ["edb:search_edb"]
    assert sum(row["tool_count"] for row in payload["handshake"]) == 35
    assert fake.initialized == list(IFIND_MCP_SERVERS)
    assert fake.catalog_calls == list(IFIND_MCP_SERVERS)
    assert factory_calls[0][1] is None
    assert fake.raw_marker not in rendered
    assert "raw_schema_forbidden_marker" not in rendered
    assert "session" not in rendered.lower()
    for service in payload["handshake"]:
        for schema in service["schema_contracts"]:
            assert set(schema) == {
                "tool_name",
                "schema_sha256",
                "supplier_contract_match",
            }


def test_live_s1_accepts_exact_dual_identity_as_metadata_without_canonical_pit() -> (
    None
):
    fake = FakeAcceptanceClient()
    captured_scope: Optional[IfindMcpCallScope] = None

    def factory(
        _policy: IfindMcpNetworkPolicy,
        scope: Optional[IfindMcpCallScope],
    ) -> FakeAcceptanceClient:
        nonlocal captured_scope
        captured_scope = scope
        return fake

    payload = run_ifind_dual_stock_acceptance(
        ROOT,
        mode="live_stage_s1",
        decision_timestamp="2026-08-07T15:00:00+08:00",
        environ=FOUR_GATES,
        client_factory=factory,  # type: ignore[arg-type]
    )
    rendered = json.dumps(payload, ensure_ascii=False)

    assert payload["status"] == "PASS"
    assert "failure_code" not in payload
    assert payload["acceptance_state"] == ("S1_IDENTITY_ACCEPTANCE_METADATA_VERIFIED")
    assert payload["decision_timestamp"] == "2026-08-07T07:00:00Z"
    assert payload["observed_at"].endswith("Z")
    assert payload["temporal_class"] == "acceptance_metadata_only"
    assert payload["provider_available_at"] is None
    assert payload["provider_available_at_status"] == (
        "UNKNOWN_NOT_REQUIRED_FOR_IDENTITY_METADATA"
    )
    assert payload["data_call_count"] == payload["data_call_budget"] == 2
    assert payload["pit_timestamp_verified"] is False
    assert payload["s1_identity_acceptance_verified"] is True
    assert payload["s2_requires_separate_authorization"] is True
    assert payload["canonical_accepted"] is False
    assert fake.data_calls == [
        ("002475.SZ", "get_stock_summary"),
        ("600487.SH", "get_stock_summary"),
    ]
    assert captured_scope is not None
    assert captured_scope.allowed_symbols == IFIND_DUAL_STOCK_SYMBOLS
    assert captured_scope.allowed_tools == ("get_stock_summary",)
    assert payload["staging_summaries"] == [
        {
            "symbol": "002475.SZ",
            "staging_format": "provider_markdown_tables_v1",
            "table_count": 1,
            "row_count": 1,
            "scope_verified": True,
            "temporal_class": "acceptance_metadata_only",
            "provider_available_at_present": False,
            "canonical_accepted": False,
        },
        {
            "symbol": "600487.SH",
            "staging_format": "provider_markdown_tables_v1",
            "table_count": 1,
            "row_count": 1,
            "scope_verified": True,
            "temporal_class": "acceptance_metadata_only",
            "provider_available_at_present": False,
            "canonical_accepted": False,
        },
    ]
    assert fake.raw_marker not in rendered


def test_live_s1_requires_fourth_gate_and_timezone_before_client_creation() -> None:
    client_created = False

    def forbidden_factory(
        _policy: IfindMcpNetworkPolicy,
        _scope: Optional[IfindMcpCallScope],
    ) -> FakeAcceptanceClient:
        nonlocal client_created
        client_created = True
        raise AssertionError("client must not be created")

    with pytest.raises(IfindProviderError) as exc:
        run_ifind_dual_stock_acceptance(
            ROOT,
            mode="live_stage_s1",
            decision_timestamp="2026-08-07T15:00:00+08:00",
            environ=THREE_GATES,
            client_factory=forbidden_factory,  # type: ignore[arg-type]
        )
    assert exc.value.failure_code == "IFIND_MCP_DATA_CALLS_DISABLED_BY_POLICY"
    assert client_created is False

    with pytest.raises(IfindProviderError) as exc:
        run_ifind_dual_stock_acceptance(
            ROOT,
            mode="live_stage_s1",
            decision_timestamp="2026-08-07T15:00:00",
            environ=FOUR_GATES,
            client_factory=forbidden_factory,  # type: ignore[arg-type]
        )
    assert exc.value.failure_code == "IFIND_MCP_DECISION_TIMESTAMP_INVALID"
    assert client_created is False


def test_live_s1_truthfully_counts_a_provider_response_rejected_during_staging() -> (
    None
):
    class RejectedFirstResponseClient(FakeAcceptanceClient):
        def call_pilot_stock_tool(
            self, symbol: str, tool_name: str
        ) -> Mapping[str, Any]:
            self.data_calls.append((symbol, tool_name))
            raise IfindProviderError(
                "IFIND_MCP_RESPONSE_SCOPE_UNVERIFIED",
                "fixture response cannot cross the accepted scope boundary",
            )

    fake = RejectedFirstResponseClient()

    payload = run_ifind_dual_stock_acceptance(
        ROOT,
        mode="live_stage_s1",
        decision_timestamp="2026-08-12T16:38:14+08:00",
        environ=FOUR_GATES,
        client_factory=lambda _policy, _scope: fake,  # type: ignore[arg-type]
    )

    assert payload["status"] == "BLOCKED"
    assert payload["failure_code"] == "IFIND_MCP_RESPONSE_SCOPE_UNVERIFIED"
    assert payload["failed_symbol"] == "002475.SZ"
    assert payload["data_tool_called"] is True
    assert payload["data_call_count"] == 1
    assert payload["data_call_budget"] == 2
    assert payload["staging_summaries"] == []
    assert fake.data_calls == [("002475.SZ", "get_stock_summary")]


def test_acceptance_cli_defaults_offline_and_does_not_render_environment_secret() -> (
    None
):
    secret = "offline-cli-secret-never-render"
    environment = dict(os.environ)
    environment["IFIND_MCP_API_KEY"] = secret
    for gate in (
        "ASHARE_ALLOW_NETWORK_INGESTION",
        "ASHARE_ALLOW_IFIND",
        "ASHARE_ALLOW_IFIND_MCP",
        "ASHARE_ALLOW_IFIND_MCP_DATA_CALLS",
    ):
        environment.pop(gate, None)

    completed = subprocess.run(
        [sys.executable, "scripts/run_ifind_mcp_dual_stock_acceptance.py"],
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert completed.returncode == 0
    assert payload["status"] == "PASS"
    assert payload["mode"] == "offline_contract"
    assert payload["keychain_accessed"] is False
    assert payload["network_accessed"] is False
    assert secret not in completed.stdout
    assert secret not in completed.stderr
    assert (
        load_ifind_dual_stock_acceptance_config(ROOT).symbols
        == IFIND_DUAL_STOCK_SYMBOLS
    )

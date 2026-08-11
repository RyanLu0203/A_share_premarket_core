"""Credential-safe iFinD MCP contract and bounded handshake probe."""

from __future__ import annotations

import argparse
import json

from _bootstrap import ROOT

from ashare_premarket.providers.ifind_http import IfindProviderError
from ashare_premarket.providers.ifind_mcp import (
    IFIND_MCP_SERVICE_CATALOG,
    IFIND_MCP_SERVERS,
    IFIND_MCP_TOOL_CATALOG,
    IfindMcpApiKey,
    IfindMcpClient,
    IfindMcpKeychainLoader,
    IfindMcpNetworkPolicy,
    ifind_mcp_readiness,
    validate_ifind_mcp_contract_document,
    write_ifind_mcp_probe_status,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the purchased iFinD MCP/API Key channel without printing credentials "
            "or calling a financial-data tool."
        )
    )
    parser.add_argument(
        "--live-handshake",
        action="store_true",
        help="Initialize one approved MCP service and list entitled tools; performs no tools/call request.",
    )
    parser.add_argument(
        "--server",
        choices=sorted(IFIND_MCP_SERVERS),
        default="stock",
        help="Approved service used by the bounded live handshake (default: stock).",
    )
    parser.add_argument(
        "--credential-source",
        choices=("keychain", "environment"),
        default="keychain",
        help="Credential delivery mechanism for a live handshake; values are never rendered.",
    )
    parser.add_argument(
        "--write-local-status",
        action="store_true",
        help=(
            "Write only allowlisted, credential-free probe metadata under outputs/local; "
            "raw schemas, provider payloads, and credentials are never persisted."
        ),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    contract_path = (
        ROOT / "configs/providers/ifind_ai_financial_data_service_contract.yaml"
    )
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        print(_render_failure("IFIND_CONTRACT_INVALID"))
        return 1
    try:
        validate_ifind_mcp_contract_document(contract)
    except IfindProviderError:
        print(_render_failure("IFIND_CONTRACT_INVALID"))
        return 1

    result = {
        "status": "PASS",
        "mode": "offline_contract",
        "contract_valid": True,
        "readiness": ifind_mcp_readiness(),
        "services": [dict(row) for row in IFIND_MCP_SERVICE_CATALOG],
        "token_value_exposed": False,
        "token_persisted": False,
        "data_tool_called": False,
    }
    if not args.live_handshake:
        return _finish(result, 0, args.write_local_status)

    policy = IfindMcpNetworkPolicy.from_environment()
    try:
        policy.require_live_access()
        credential = (
            IfindMcpKeychainLoader().load()
            if args.credential_source == "keychain"
            else IfindMcpApiKey.from_environment()
        )
        client = IfindMcpClient(api_key=credential, policy=policy)
        initialization = client.initialize(args.server)
        actual_tools = client.list_tools(args.server)
        tool_contracts = client.list_tool_contracts(args.server)
        expected_tools = tuple(IFIND_MCP_TOOL_CATALOG[args.server])
        missing = sorted(set(expected_tools) - set(actual_tools))
        unexpected = sorted(set(actual_tools) - set(expected_tools))
    except IfindProviderError as exc:
        result.update(
            {
                "status": "BLOCKED",
                "mode": "live_handshake",
                "failure_code": exc.failure_code,
                "http_status": exc.http_status,
            }
        )
        return _finish(result, 1, args.write_local_status)
    except Exception:
        result.update(
            {
                "status": "BLOCKED",
                "mode": "live_handshake",
                "failure_code": "IFIND_MCP_PROBE_INTERNAL_ERROR",
            }
        )
        return _finish(result, 1, args.write_local_status)

    catalog_verified = not missing
    schema_verified = all(row["supplier_contract_match"] for row in tool_contracts)
    handshake_verified = catalog_verified and schema_verified
    result.update(
        {
            "status": "PASS" if handshake_verified else "BLOCKED",
            "mode": "live_handshake",
            "server": args.server,
            "protocol_version": initialization.get("protocolVersion"),
            "actual_tool_count": len(actual_tools),
            "expected_tool_count": len(expected_tools),
            "expected_tools_present": catalog_verified,
            "input_schema_contracts": list(tool_contracts),
            "input_schemas_verified": schema_verified,
            "missing_expected_tools": missing,
            "unexpected_tool_names": unexpected,
            "live_handshake_verified": handshake_verified,
        }
    )
    if not catalog_verified:
        result["failure_code"] = "IFIND_MCP_TOOL_CATALOG_MISMATCH"
    elif not schema_verified:
        result["failure_code"] = "IFIND_MCP_TOOL_SCHEMA_MISMATCH"
    return _finish(result, 0 if handshake_verified else 1, args.write_local_status)


def _render_failure(failure_code: str) -> str:
    return json.dumps(
        {
            "status": "BLOCKED",
            "failure_code": failure_code,
            "token_value_exposed": False,
            "token_persisted": False,
            "data_tool_called": False,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def _finish(result: dict[str, object], exit_code: int, write_local_status: bool) -> int:
    if write_local_status:
        write_ifind_mcp_probe_status(ROOT, result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

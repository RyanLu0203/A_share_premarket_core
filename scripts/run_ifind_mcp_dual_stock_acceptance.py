"""Offline-first, credential-safe dual-stock iFinD MCP acceptance runner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional, Sequence

from _bootstrap import ROOT

from ashare_premarket.providers.ifind_acceptance import (
    run_ifind_dual_stock_acceptance,
)
from ashare_premarket.providers.ifind_http import IfindProviderError
from ashare_premarket.providers.ifind_mcp import (
    reclassify_ifind_mcp_s1_probe_status,
    write_ifind_mcp_probe_status,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the bounded 002475.SZ/600487.SH iFinD acceptance plan. "
            "The default is offline and never reads Keychain or uses the network."
        )
    )
    live = parser.add_mutually_exclusive_group()
    live.add_argument(
        "--live-handshake",
        action="store_true",
        help=(
            "Read the dedicated Keychain item and run initialize/tools/list for all "
            "seven services; no tools/call request is permitted."
        ),
    )
    live.add_argument(
        "--reclassify-existing-s1-status",
        action="store_true",
        help=(
            "Offline-only migration of the exact two-call PIT-blocked local S1 "
            "status to non-canonical identity acceptance metadata."
        ),
    )
    live.add_argument(
        "--live-stage-s1",
        action="store_true",
        help=(
            "After a same-run seven-service S0 pass, call fixed get_stock_summary "
            "once for each accepted pilot symbol and return only non-canonical "
            "identity acceptance metadata."
        ),
    )
    parser.add_argument(
        "--decision-timestamp",
        help=(
            "Timezone-aware ISO-8601 decision timestamp required by --live-stage-s1; "
            "the system clock is never inferred."
        ),
    )
    parser.add_argument(
        "--write-local-status",
        action="store_true",
        help=(
            "For a successful S0 or S1 run, write bounded credential-free status "
            "metadata under outputs/local for the read-only Workspace."
        ),
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.live_stage_s1 and not args.decision_timestamp:
        return _print_failure(
            "live_stage_s1",
            "IFIND_MCP_DECISION_TIMESTAMP_REQUIRED",
        )
    if not args.live_stage_s1 and args.decision_timestamp:
        return _print_failure(
            "offline_contract" if not args.live_handshake else "live_handshake",
            "IFIND_MCP_DECISION_TIMESTAMP_UNEXPECTED",
        )
    if args.reclassify_existing_s1_status:
        if args.write_local_status:
            return _print_failure(
                "offline_contract",
                "IFIND_MCP_LOCAL_STATUS_MODE_INVALID",
            )
        try:
            target = reclassify_ifind_mcp_s1_probe_status(Path(ROOT))
        except IfindProviderError as exc:
            return _print_failure("offline_contract", exc.failure_code)
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "mode": "offline_contract",
                    "acceptance_state": (
                        "S1_IDENTITY_ACCEPTANCE_METADATA_VERIFIED"
                    ),
                    "local_status_updated": True,
                    "path": str(target.relative_to(ROOT)),
                    "network_accessed": False,
                    "keychain_accessed": False,
                    "canonical_accepted": False,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0
    if args.write_local_status and not (args.live_handshake or args.live_stage_s1):
        return _print_failure(
            "live_stage_s1" if args.live_stage_s1 else "offline_contract",
            "IFIND_MCP_LOCAL_STATUS_MODE_INVALID",
        )

    mode = (
        "live_stage_s1"
        if args.live_stage_s1
        else "live_handshake" if args.live_handshake else "offline_contract"
    )
    try:
        result = run_ifind_dual_stock_acceptance(
            ROOT,
            mode=mode,
            decision_timestamp=args.decision_timestamp,
        )
    except IfindProviderError as exc:
        return _print_failure(mode, exc.failure_code, exc.http_status)
    except Exception:
        return _print_failure(mode, "IFIND_MCP_ACCEPTANCE_INTERNAL_ERROR")

    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if args.write_local_status:
        handshake = result.get("handshake", [])
        status_payload = {
            "status": result.get("status"),
            "mode": result.get("mode"),
            "acceptance_state": result.get("acceptance_state"),
            "temporal_class": result.get("temporal_class"),
            "provider_available_at_status": result.get(
                "provider_available_at_status"
            ),
            "identity_observed_at": result.get("observed_at"),
            "actual_tool_count": sum(
                int(row.get("tool_count", 0)) for row in handshake
            ),
            "expected_tool_count": int(result.get("expected_tool_count", 0)),
            "data_call_count": result.get("data_call_count"),
            "staged_symbol_count": len(result.get("staging_summaries", [])),
            "live_handshake_verified": True,
            "input_schemas_verified": True,
            "data_tool_called": result.get("data_tool_called") is True,
            "s1_identity_acceptance_verified": result.get(
                "s1_identity_acceptance_verified"
            )
            is True,
            "s2_requires_separate_authorization": result.get(
                "s2_requires_separate_authorization"
            )
            is True,
            "canonical_accepted": False,
        }
        write_ifind_mcp_probe_status(
            Path(ROOT),
            status_payload,
        )
    return 0 if result.get("status") == "PASS" else 1


def _print_failure(
    mode: str,
    failure_code: str,
    http_status: Optional[int] = None,
) -> int:
    payload = {
        "status": "BLOCKED",
        "mode": mode,
        "acceptance_state": "NOT_CANONICAL",
        "failure_code": failure_code,
        "http_status": http_status,
        "network_access_status": "not_claimed_on_failure",
        "data_tool_called": False,
        "raw_payload_persisted": False,
        "credential_exposed": False,
        "canonical_accepted": False,
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

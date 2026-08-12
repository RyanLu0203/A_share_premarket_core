from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from ashare_premarket.dashboard.repositories.base import WorkspaceRepositoryBase
from ashare_premarket.data.trading_calendar import trading_calendar_status
from ashare_premarket.providers.ifind_mcp import (
    IFIND_MCP_DATA_MODULES,
    IFIND_MCP_SERVICE_CATALOG,
    ifind_mcp_readiness,
    read_ifind_mcp_probe_status,
)
from ashare_premarket.providers.ifind_s2 import (
    IFIND_S2_ADJUSTMENT_MODE,
    IFIND_S2_DATA_CALL_BUDGET,
    IFIND_S2_DAILY_SESSION_COUNT,
    IFIND_S2_FIXED_TOOLS,
    IFIND_S2_PREFLIGHT_STATE,
)


class SystemEvidenceRepository(WorkspaceRepositoryBase):
    def market_context(self, snapshot_date: str | None = None) -> dict[str, Any]:
        manifest = self.store.snapshot_manifest(snapshot_date)
        cutoff = str(manifest["data_cutoff"])
        index_rows = [
            row
            for row in self.store.csv(
                "outputs/research/network_ingestion/index_panel.csv"
            )
            if row.get("trade_date", "") <= cutoff
        ]
        latest = self._latest_by_key(index_rows, "index_id")
        regimes = [
            row
            for row in self.store.csv(
                "outputs/research/goal_regime_label_research02_refined_date_regime_labels.csv"
            )
            if row.get("trade_date", "") <= cutoff
        ]
        return {
            "indices": list(latest.values()),
            "regime": regimes[-1] if regimes else None,
            "data_cutoff": cutoff,
            "freshness": manifest.get("freshness_code"),
            "macro_news_available": False,
            "research_only": True,
        }

    def data_quality(self, snapshot_date: str | None = None) -> dict[str, Any]:
        selected = snapshot_date or self.store.latest_snapshot_date()
        return {
            "status": (
                self.status("replay", selected)
                if snapshot_date
                else self.status("live")
            ),
            "readiness_checks": list(
                self.store.snapshot_csv("data_readiness.csv", selected)
            ),
            "quality_summary": list(
                self.store.csv(
                    "outputs/data_expansion/goal_data_expansion_research01/data_quality_summary.csv"
                )
            ),
            "quarantine": list(self._provider_quarantine()),
            "ifind_readiness": _safe_ifind_readiness(self.root),
            "ifind_mcp_services": [
                dict(service) for service in IFIND_MCP_SERVICE_CATALOG
            ],
            "ifind_data_modules": [dict(module) for module in IFIND_MCP_DATA_MODULES],
            "ifind_pilot_acceptance": self.store.json(
                "configs/providers/ifind_mcp_dual_stock_pilot.yaml"
            ),
        }

    def provider_health(self, snapshot_date: str | None = None) -> dict[str, Any]:
        selected = snapshot_date or self.store.latest_snapshot_date()
        manifest = self.store.snapshot_manifest(selected)
        result = {
            "canonical_decision": "akshare_sina_primary_with_baostock_overlap_diagnostics",
            "comparison": list(
                self.store.csv(
                    "outputs/research/goal_premarket_portfolio_risk_management01_provider_comparison.csv"
                )
            ),
            "quarantine": list(self._provider_quarantine()),
            "provider_usage": list(
                self.store.csv(
                    "outputs/providers/goal_data_provider02b_provider_usage_summary.csv"
                )
            ),
            "provider_health": list(
                self.store.csv(
                    "outputs/data_expansion/goal_data_expansion_research01/provider_health.csv"
                )
            ),
            "adjustment_convention_status": "UNRESOLVED",
            "no_silent_averaging": True,
            "provider_lineage": list(manifest.get("provider_lineage", [])),
            "source_freshness": {
                "snapshot_date": selected,
                "latest_available_data_date": manifest.get(
                    "latest_available_data_date"
                ),
                "freshness_code": manifest.get("freshness_code"),
            },
            "trading_calendar": trading_calendar_status(
                self.root,
                datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat(),
            ),
            "ifind_readiness": _safe_ifind_readiness(self.root),
            "ifind_mcp_services": [
                dict(service) for service in IFIND_MCP_SERVICE_CATALOG
            ],
            "ifind_data_modules": [dict(module) for module in IFIND_MCP_DATA_MODULES],
            "ifind_pilot_acceptance": self.store.json(
                "configs/providers/ifind_mcp_dual_stock_pilot.yaml"
            ),
            "snapshot_date": selected,
        }
        if snapshot_date is not None:
            return result
        operational = self._operational_refresh_context()
        return {
            **result,
            **operational,
            "canonical_decision": "tencent_operational_primary_via_akshare_stock_zh_a_hist_tx",
            "adjustment_convention_status": "QFQ_ONLY",
            "provider_lineage": (
                [operational["operational_provider"]]
                if operational.get("operational_provider")
                else []
            ),
            "historical_research_provider_lineage": list(
                manifest.get("provider_lineage", [])
            ),
            "source_freshness": {
                "snapshot_date": selected,
                "latest_available_data_date": result["source_freshness"][
                    "latest_available_data_date"
                ],
                "freshness_code": result["source_freshness"]["freshness_code"],
                "source_dates": operational.get("source_dates", []),
            },
        }

    def experiment(self) -> dict[str, Any]:
        contract = {
            row["field_name"]: row["frozen_value"]
            for row in self.store.csv(
                "outputs/research/goal_premarket_position_management_operational01_shadow_experiment_contract.csv"
            )
        }
        freeze = self.store.json(
            "outputs/research/goal_premarket_position_management_operational01_experiment_freeze_manifest.json"
        )
        refresh_contract = {
            row["field_name"]: row["frozen_value"]
            for row in self.store.csv(
                "outputs/research/goal_daily_incremental_evidence_refresh01_experiment_readiness_contract.csv"
            )
        }
        return {
            "status": "PREPARED_NOT_STARTED",
            "contract": contract,
            "daily_refresh_contract": refresh_contract,
            "freeze_manifest": freeze,
            "observations": [],
            "empty_state": "NO FORWARD EXPERIMENT OBSERVATIONS YET",
            "research_only": True,
        }

    def snapshots(self) -> dict[str, Any]:
        rows = []
        for date in self.store.snapshot_dates():
            manifest = self.store.snapshot_manifest(date)
            verified, failures = self.store.verify_snapshot(date)
            rows.append(
                {
                    **manifest,
                    "snapshot_version": self.store.snapshot_version(date),
                    "snapshot_integrity": "VERIFIED" if verified else "FAILED",
                    "checksum_failures": failures,
                }
            )
        resolution = self.store.resolve_snapshot()
        return {
            "latest": resolution["selected_date"],
            "latest_resolution": resolution,
            "historical_replay_status": (
                "AVAILABLE"
                if any(row["snapshot_integrity"] == "VERIFIED" for row in rows)
                else "BLOCKED"
            ),
            "snapshots": rows,
        }

    def provenance(self, snapshot_date: str | None = None) -> dict[str, Any]:
        selected = snapshot_date or self.store.latest_snapshot_date()
        manifest = self.store.snapshot_manifest(selected)
        workflow = next(
            (
                row
                for row in self.store.csv("configs/project/workflow_status.csv")
                if row.get("workflow_id")
                == "goal_premarket_position_management_operational01"
            ),
            {},
        )
        workspace_audit = self.store.json(
            "outputs/audits/goal_premarket_research_position_workspace_dashboard01_manifest.json"
        )
        result = {
            "snapshot": manifest,
            "source_lineage": manifest.get("source_lineage", []),
            "provider_lineage": manifest.get("provider_lineage", []),
            "config_hash": manifest.get("config_hash"),
            "code_commit": manifest.get("code_commit"),
            "checksums": manifest.get("checksums", {}),
            "pit_status": manifest.get("pit_status"),
            "goal_lineage": [
                "GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01",
                "GOAL-PREMARKET-POSITION-MANAGEMENT-OPERATIONAL-01",
                "GOAL-PREMARKET-RESEARCH-AND-POSITION-WORKSPACE-DASHBOARD-01",
                "GOAL-DAILY-INCREMENTAL-EVIDENCE-REFRESH-01",
            ],
            "daily_refresh": self.store.refresh_status(),
            "audit_status": workspace_audit.get("status", "UNAVAILABLE"),
            "workflow_state": workflow,
            "research_only": True,
        }
        if snapshot_date is not None:
            return result
        operational = self._operational_refresh_context()
        return {
            **result,
            **operational,
            "code_commit": operational["runtime_code_commit"],
            "operational_source_lineage": (
                [
                    f"AKShare::{operational['operational_function']}",
                    f"{operational['operational_provider']}::{operational['operational_endpoint_family']}",
                ]
                if operational.get("operational_provider")
                and operational.get("operational_function")
                else []
            ),
            "historical_research_provider_lineage": list(
                manifest.get("provider_lineage", [])
            ),
        }

    def watchlist_seed(self) -> dict[str, Any]:
        return {
            "storage": "browser_local_storage",
            "server_writes": False,
            "symbols": [
                row["symbol"]
                for row in self.stocks()
                if row.get("portfolio_membership_state") == "REFERENCE_PORTFOLIO_MEMBER"
            ][:8],
        }


def _safe_ifind_readiness(root: Path) -> dict[str, Any]:
    """Project iFinD readiness into a credential-safe dashboard contract."""

    readiness = ifind_mcp_readiness()
    probe = read_ifind_mcp_probe_status(root)
    return {
        "provider_id": readiness["provider_id"],
        "provider_name": readiness["provider_name"],
        "product_name": readiness["product_name"],
        "channel_id": readiness["channel_id"],
        "interface_mode": readiness["interface_mode"],
        "base_url": readiness["base_url"],
        "protocol_version": readiness["protocol_version"],
        "readiness_state": readiness["readiness_state"],
        "network_opt_in": readiness["network_opt_in"],
        "provider_opt_in": readiness["provider_opt_in"],
        "mcp_opt_in": readiness["mcp_opt_in"],
        "data_call_opt_in": readiness["data_call_opt_in"],
        "live_access_allowed": readiness["live_access_allowed"],
        "credential_delivery_policy": readiness["credential_delivery_policy"],
        "credential_verified": readiness["credential_verified"],
        "keychain_lookup_available": readiness["keychain_lookup_available"],
        "raw_payload_commit_allowed": readiness["raw_payload_commit_allowed"],
        "local_token_persistence_allowed": readiness["local_token_persistence_allowed"],
        "supported_service_count": readiness["supported_service_count"],
        "entitlement_profile": readiness["entitlement_profile"],
        "reviewed_tool_count": readiness["reviewed_tool_count"],
        "expected_tool_count": readiness["expected_tool_count"],
        "unavailable_by_plan_count": readiness["unavailable_by_plan_count"],
        "unavailable_by_plan": readiness["unavailable_by_plan"],
        "data_module_count": len(IFIND_MCP_DATA_MODULES),
        "last_probe_status": probe["status"],
        "last_probe_mode": probe["mode"],
        "last_probe_server": probe.get("server"),
        "last_probe_failure_code": probe.get("failure_code"),
        "last_probe_http_status": probe.get("http_status"),
        "last_probe_observed_at": probe.get("observed_at"),
        "last_handshake_verified": probe["live_handshake_verified"],
        "last_input_schemas_verified": probe["input_schemas_verified"],
        "last_data_tool_called": probe["data_tool_called"],
        "last_data_call_count": probe.get("data_call_count"),
        "last_failed_symbol": probe.get("failed_symbol"),
        "s1_acceptance_state": probe.get("acceptance_state"),
        "s1_temporal_class": probe.get("temporal_class"),
        "s1_provider_available_at_status": probe.get("provider_available_at_status"),
        "s1_provider_available_at_verified": probe.get(
            "provider_available_at_verified"
        ),
        "s1_identity_observed_at": probe.get("identity_observed_at"),
        "s1_staged_symbol_count": probe.get("staged_symbol_count"),
        "s1_identity_acceptance_verified": probe.get("s1_identity_acceptance_verified"),
        "s2_requires_separate_authorization": probe.get(
            "s2_requires_separate_authorization"
        ),
        "s2_offline_foundation_state": (
            IFIND_S2_PREFLIGHT_STATE
            if probe.get("s1_identity_acceptance_verified") is True
            else "BLOCKED_UNTIL_S1_ACCEPTED"
        ),
        "s2_fixed_tools": list(IFIND_S2_FIXED_TOOLS),
        "s2_data_call_budget": IFIND_S2_DATA_CALL_BUDGET,
        "s2_daily_session_count": IFIND_S2_DAILY_SESSION_COUNT,
        "s2_adjustment_mode": IFIND_S2_ADJUSTMENT_MODE,
        "s2_live_calls_authorized": False,
        "s2_provider_schema_accepted": False,
        "ifind_canonical_accepted": probe.get("canonical_accepted") is True,
    }

from __future__ import annotations

from typing import Any

from ashare_premarket.dashboard.repositories.base import WorkspaceRepositoryBase


class SystemEvidenceRepository(WorkspaceRepositoryBase):
    def market_context(self, snapshot_date: str | None = None) -> dict[str, Any]:
        manifest = self.store.snapshot_manifest(snapshot_date)
        cutoff = str(manifest["data_cutoff"])
        index_rows = [row for row in self.store.csv("outputs/research/network_ingestion/index_panel.csv") if row.get("trade_date", "") <= cutoff]
        latest = self._latest_by_key(index_rows, "index_id")
        regimes = [row for row in self.store.csv("outputs/research/goal_regime_label_research02_refined_date_regime_labels.csv") if row.get("trade_date", "") <= cutoff]
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
            "status": self.status("replay", selected),
            "readiness_checks": list(self.store.snapshot_csv("data_readiness.csv", selected)),
            "quality_summary": list(self.store.csv("outputs/data_expansion/goal_data_expansion_research01/data_quality_summary.csv")),
            "quarantine": list(self._provider_quarantine()),
        }

    def provider_health(self, snapshot_date: str | None = None) -> dict[str, Any]:
        selected = snapshot_date or self.store.latest_snapshot_date()
        manifest = self.store.snapshot_manifest(selected)
        return {
            "canonical_decision": "akshare_sina_primary_with_baostock_overlap_diagnostics",
            "comparison": list(self.store.csv("outputs/research/goal_premarket_portfolio_risk_management01_provider_comparison.csv")),
            "quarantine": list(self._provider_quarantine()),
            "provider_usage": list(self.store.csv("outputs/providers/goal_data_provider02b_provider_usage_summary.csv")),
            "provider_health": list(self.store.csv("outputs/data_expansion/goal_data_expansion_research01/provider_health.csv")),
            "adjustment_convention_status": "UNRESOLVED",
            "no_silent_averaging": True,
            "provider_lineage": list(manifest.get("provider_lineage", [])),
            "source_freshness": {
                "snapshot_date": selected,
                "latest_available_data_date": manifest.get("latest_available_data_date"),
                "freshness_code": manifest.get("freshness_code"),
            },
            "snapshot_date": selected,
        }

    def experiment(self) -> dict[str, Any]:
        contract = {row["field_name"]: row["frozen_value"] for row in self.store.csv("outputs/research/goal_premarket_position_management_operational01_shadow_experiment_contract.csv")}
        freeze = self.store.json("outputs/research/goal_premarket_position_management_operational01_experiment_freeze_manifest.json")
        refresh_contract = {row["field_name"]: row["frozen_value"] for row in self.store.csv("outputs/research/goal_daily_incremental_evidence_refresh01_experiment_readiness_contract.csv")}
        return {"status": "PREPARED_NOT_STARTED", "contract": contract, "daily_refresh_contract": refresh_contract, "freeze_manifest": freeze, "observations": [], "empty_state": "NO FORWARD EXPERIMENT OBSERVATIONS YET", "research_only": True}

    def snapshots(self) -> dict[str, Any]:
        rows = []
        for date in self.store.snapshot_dates():
            manifest = self.store.snapshot_manifest(date)
            verified, failures = self.store.verify_snapshot(date)
            rows.append({**manifest, "snapshot_version": self.store.snapshot_version(date), "snapshot_integrity": "VERIFIED" if verified else "FAILED", "checksum_failures": failures})
        return {"latest": self.store.latest_snapshot_date(), "snapshots": rows}

    def provenance(self, snapshot_date: str | None = None) -> dict[str, Any]:
        selected = snapshot_date or self.store.latest_snapshot_date()
        manifest = self.store.snapshot_manifest(selected)
        workflow = next((row for row in self.store.csv("configs/project/workflow_status.csv") if row.get("workflow_id") == "goal_premarket_position_management_operational01"), {})
        workspace_audit = self.store.json("outputs/audits/goal_premarket_research_position_workspace_dashboard01_manifest.json")
        return {
            "snapshot": manifest,
            "source_lineage": manifest.get("source_lineage", []),
            "provider_lineage": manifest.get("provider_lineage", []),
            "config_hash": manifest.get("config_hash"),
            "code_commit": manifest.get("code_commit"),
            "checksums": manifest.get("checksums", {}),
            "pit_status": manifest.get("pit_status"),
            "goal_lineage": ["GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01", "GOAL-PREMARKET-POSITION-MANAGEMENT-OPERATIONAL-01", "GOAL-PREMARKET-RESEARCH-AND-POSITION-WORKSPACE-DASHBOARD-01", "GOAL-DAILY-INCREMENTAL-EVIDENCE-REFRESH-01"],
            "daily_refresh": self.store.refresh_status(),
            "audit_status": workspace_audit.get("status", "UNAVAILABLE"),
            "workflow_state": workflow,
            "research_only": True,
        }

    def watchlist_seed(self) -> dict[str, Any]:
        return {"storage": "browser_local_storage", "server_writes": False, "symbols": [row["symbol"] for row in self.stocks()[:8]]}

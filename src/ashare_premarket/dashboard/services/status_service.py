from __future__ import annotations

from datetime import datetime
from typing import Any

from ashare_premarket.daily_refresh.goal_daily_incremental_evidence_refresh01 import resolve_daily_refresh_context
from ashare_premarket.dashboard.repositories.base import HOLDINGS_MODE_LABEL, WorkspaceRepositoryBase, _float
from ashare_premarket.portfolio_risk.goal_premarket_position_management_operational01 import (
    evaluate_canonical_freshness,
)


class WorkspaceStatusService(WorkspaceRepositoryBase):
    def status(
        self,
        mode: str = "live",
        snapshot_date: str | None = None,
        execution_time: datetime | str | None = None,
    ) -> dict[str, Any]:
        selected = snapshot_date or self.store.latest_snapshot_date()
        manifest = self.store.snapshot_manifest(selected)
        verified, checksum_failures = self.store.verify_snapshot(selected)
        refresh = self.store.refresh_status()
        if mode == "replay":
            result = {
                "execution_mode": "deterministic_replay",
                "execution_time": manifest.get("execution_time"),
                "generated_at": manifest.get("generated_at"),
                "decision_asof_ts": manifest.get("decision_asof_ts"),
                "snapshot_date": selected,
                "target_trading_date": manifest.get("target_trading_date"),
                "expected_previous_trading_date": manifest.get("expected_previous_trading_date"),
                "data_cutoff": manifest.get("data_cutoff"),
                "latest_available_data_date": manifest.get("latest_available_data_date"),
                "readiness_state": manifest.get("readiness_state"),
                "freshness_code": manifest.get("freshness_code"),
                "current_panels_enabled": manifest.get("freshness_state") == "READY",
            }
        elif mode == "live":
            execution = execution_time.isoformat() if isinstance(execution_time, datetime) else execution_time
            context = resolve_daily_refresh_context(self.root, execution_time=execution, replay_date=None)
            if context.get("calendar_status") == "BLOCKED":
                freshness = {
                    "state": "BLOCKED",
                    "freshness_code": context["calendar_reason"],
                    "latest_available_canonical_date": max(self.store.canonical_dates(selected), default=""),
                }
            else:
                freshness = evaluate_canonical_freshness(list(self.store.canonical_dates(selected)), context)
            result = {
                **context,
                "snapshot_date": selected,
                "latest_available_data_date": freshness["latest_available_canonical_date"],
                "readiness_state": "BLOCKED" if freshness["state"] == "BLOCKED" else manifest.get("readiness_state"),
                "freshness_code": freshness["freshness_code"],
                "current_panels_enabled": freshness["state"] != "BLOCKED",
            }
        else:
            raise ValueError("mode must be 'live' or 'replay'")
        if mode == "live" and (refresh.get("refresh_status") == "BLOCKED" or refresh.get("refresh_manifest_integrity") == "FAILED"):
            result["readiness_state"] = "BLOCKED"
            result["current_panels_enabled"] = False
        refresh_reasons = refresh.get("blocked_reasons", [])
        if not isinstance(refresh_reasons, list):
            refresh_reasons = [str(refresh_reasons)] if refresh_reasons else []
        if refresh.get("refresh_manifest_integrity") == "FAILED":
            refresh_reasons = [*refresh_reasons, "REFRESH_MANIFEST_CHECKSUM_MISMATCH"]
        if result.get("readiness_state") == "BLOCKED" and result.get("freshness_code") not in refresh_reasons:
            refresh_reasons = [*refresh_reasons, result.get("freshness_code")]
        return {
            **result,
            "provider_state": "WARNINGS_QUARANTINED",
            "holdings_mode": HOLDINGS_MODE_LABEL,
            "portfolio_id": "research_reference_portfolio",
            "snapshot_integrity": "VERIFIED" if verified else "FAILED",
            "snapshot_checksum_failures": checksum_failures,
            "latest_refresh_status": refresh.get("refresh_status", "NOT_RUN"),
            "last_successful_refresh_time": refresh.get("last_successful_refresh_time", ""),
            "data_freshness_badge": result.get("freshness_code", "UNAVAILABLE") if mode == "live" else refresh.get("freshness_code", result.get("freshness_code", "UNAVAILABLE")),
            "refresh_validation_status": refresh.get("validation_status", "NOT_RUN"),
            "refresh_manifest_integrity": refresh.get("refresh_manifest_integrity", "UNAVAILABLE"),
            "refresh_blocked_reasons": refresh_reasons,
            "snapshot_version": refresh.get("snapshot_version") if refresh.get("snapshot_date") == selected else self.store.snapshot_version(selected),
            "research_only": True,
            "not_trading_advice": True,
            "not_for_execution": True,
        }

    def command_center(self, mode: str = "live", snapshot_date: str | None = None) -> dict[str, Any]:
        status = self.status(mode, snapshot_date)
        selected = status["snapshot_date"]
        risk = self._snapshot_risk(selected)
        constraints = self.portfolio_constraints(selected)
        abstentions = self.portfolio_abstentions(selected)
        bands = self.portfolio_bands(selected)
        return {
            "status": status,
            "kpis": {
                "readiness_state": status["readiness_state"],
                "portfolio_risk_state": risk.get("predecessor_risk_state"),
                "gross_exposure": _float(risk.get("gross_exposure")),
                "cash_weight": _float(risk.get("cash_weight")),
                "portfolio_volatility": _float(risk.get("portfolio_volatility")),
                "beta": _float(risk.get("beta_to_csi300")),
                "constraint_breaches": sum(row["breach_count"] for row in constraints["summary"]),
                "abstentions": abstentions["count"],
                "snapshot_timestamp": risk.get("asof_ts"),
            },
            "position_distribution": bands["distribution"],
            "top_risk_contributors": risk.get("largest_risk_contributors", "").split(";") if risk else [],
            "warnings": list(self.store.snapshot_csv("warnings.csv", selected)),
            "exposure": self.store.snapshot_csv("exposure_envelope.csv", selected)[0],
            "provider_health": self.provider_health(selected),
            "risk_history": [self._snapshot_risk(date) for date in self.store.snapshot_dates()],
        }

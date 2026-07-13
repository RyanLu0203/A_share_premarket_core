from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from ashare_premarket.dashboard.analytics import display_correlation_matrix
from ashare_premarket.dashboard.repositories.base import (
    HOLDINGS_MODE_LABEL,
    WorkspaceRepositoryBase,
    _bool,
    _float,
    _max_severity,
    _reason_dimension,
)


class PortfolioRepository(WorkspaceRepositoryBase):
    def portfolio_overview(self, snapshot_date: str | None = None) -> dict[str, Any]:
        selected = snapshot_date or self.store.latest_snapshot_date()
        risk_state = self._snapshot_risk(selected)
        positions = self.portfolio_bands(selected)["rows"]
        contributions = {row["symbol"]: _float(row.get("risk_contribution_share")) for row in self._risk_contributions()}
        for row in positions:
            row["risk_contribution"] = contributions.get(row["symbol"])
        top_symbols = [
            symbol
            for symbol, _ in sorted(contributions.items(), key=lambda item: item[1] or 0.0, reverse=True)[:12]
        ]
        cutoff = str(self.store.snapshot_manifest(selected)["data_cutoff"])
        return {
            "portfolio_mode": HOLDINGS_MODE_LABEL,
            "risk_state": risk_state,
            "positions": positions,
            "correlation_matrix": display_correlation_matrix(self.store.canonical_rows(selected), top_symbols, cutoff),
            "clusters": list(self._cluster_summary()),
            "exposure": self.store.snapshot_csv("exposure_envelope.csv", selected)[0],
            "snapshot_date": selected,
            "research_only": True,
        }

    def portfolio_bands(self, snapshot_date: str | None = None) -> dict[str, Any]:
        rows = [self._typed_band(row) for row in self.store.snapshot_csv("position_band_status.csv", snapshot_date)]
        identity = self._identity_map()
        contributions = {
            row["symbol"]: _float(row.get("risk_contribution_share"))
            for row in self._risk_contributions()
        }
        for row in rows:
            row["display_name"] = identity.get(row["symbol"], {}).get("name") or row["symbol"]
            row["risk_contribution"] = contributions.get(row["symbol"])
        counts = Counter(row["band_status"] for row in rows)
        return {"rows": rows, "distribution": dict(sorted(counts.items())), "allowed_states": ["BELOW_BAND", "WITHIN_BAND", "ABOVE_BAND", "ABSTAIN", "INSUFFICIENT_DATA"]}

    def portfolio_risk(self, snapshot_date: str | None = None) -> dict[str, Any]:
        selected = snapshot_date or self.store.latest_snapshot_date()
        return {
            "state": self._snapshot_risk(selected),
            "contributions": list(self._risk_contributions()),
            "drawdown_tail": list(self.store.csv("outputs/research/goal_premarket_portfolio_risk_management01_drawdown_tail_risk_summary.csv")),
            "policy_comparison": list(self.store.csv("outputs/research/goal_premarket_portfolio_risk_management01_policy_risk_comparison.csv")),
            "policy_catalog": list(self.store.csv("outputs/research/goal_premarket_portfolio_risk_management01_policy_catalog.csv")),
            "clusters": list(self._cluster_summary()),
            "history": [self._snapshot_risk(date) for date in self.store.snapshot_dates()],
            "research_only": True,
        }

    def portfolio_constraints(self, snapshot_date: str | None = None) -> dict[str, Any]:
        details = list(self.store.snapshot_csv("constraint_evaluation.csv", snapshot_date))
        catalog = {row["constraint_id"]: row for row in self.store.csv("outputs/research/goal_premarket_portfolio_risk_management01_position_constraint_catalog.csv")}
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in details:
            grouped[row["constraint_id"]].append(row)
        summary = []
        for constraint_id, rows in grouped.items():
            breached = [row for row in rows if _bool(row.get("breach"))]
            fail_closed = any(_bool(row.get("fail_closed")) for row in rows)
            availability = sorted({row.get("evidence_availability", "") for row in rows})
            if breached and fail_closed:
                state = "FAIL_CLOSED"
            elif breached:
                state = "BREACH"
            elif any(value.startswith("unavailable") for value in availability):
                state = "UNAVAILABLE"
            elif any(row.get("severity") not in {"", "none"} for row in rows):
                state = "WARNING"
            else:
                state = "PASS"
            numeric = [_float(row.get("current_value")) for row in rows]
            numeric = [value for value in numeric if value is not None]
            summary.append(
                {
                    "constraint_id": constraint_id,
                    "description": catalog.get(constraint_id, {}).get("description"),
                    "current_value": max(numeric) if numeric else rows[0].get("current_value"),
                    "threshold": rows[0].get("threshold"),
                    "breach": bool(breached),
                    "breach_count": len(breached),
                    "severity": _max_severity(row.get("severity", "") for row in rows),
                    "evidence_availability": availability,
                    "fail_closed": fail_closed,
                    "state": state,
                    "substantive": _bool(catalog.get(constraint_id, {}).get("substantive_constraint")),
                }
            )
        return {"summary": summary, "details": details, "constraint_count": len(summary), "substantive_constraint_count": sum(1 for row in summary if row["substantive"])}

    def portfolio_abstentions(self, snapshot_date: str | None = None) -> dict[str, Any]:
        rows = []
        for raw in self.store.snapshot_csv("abstention_summary.csv", snapshot_date):
            reasons = [reason for reason in raw.get("abstention_reason", "").split(";") if reason]
            rows.append(
                {
                    **raw,
                    "abstain": _bool(raw.get("abstain")),
                    "confidence": _float(raw.get("confidence")),
                    "reason_codes": reasons,
                    "provider_discrepancy": _reason_dimension(reasons, "unresolved_provider_discrepancy"),
                    "regime_instability": _reason_dimension(reasons, "sparse_or_unstable_regime_evidence"),
                    "covariance_sensitivity": _reason_dimension(reasons, "unstable_covariance_sensitivity"),
                    "band_sensitivity": _reason_dimension(reasons, "unstable_band_sensitivity"),
                    "history_sufficiency": _reason_dimension(reasons, "insufficient_history"),
                    "data_availability": _reason_dimension(reasons, "constraint_data_insufficiency"),
                }
            )
        return {"rows": rows, "count": len(rows), "reason_distribution": dict(sorted(Counter(reason for row in rows for reason in row["reason_codes"]).items()))}

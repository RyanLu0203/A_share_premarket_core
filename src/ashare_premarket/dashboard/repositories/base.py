from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

from ashare_premarket.dashboard.repositories.snapshot_repository import (
    CommittedEvidenceStore,
)


UNAVAILABLE_REASON = "field is not present in committed evidence"
HOLDINGS_MODE_LABEL = "RESEARCH REFERENCE PORTFOLIO"
FUNDAMENTAL_FIELDS = (
    "pe_ttm",
    "pe_static",
    "pb",
    "ps",
    "pcf",
    "dividend_yield",
    "revenue",
    "revenue_yoy",
    "net_profit",
    "net_profit_yoy",
    "eps",
    "roe",
    "roa",
    "gross_margin",
    "net_margin",
    "debt_ratio",
    "current_ratio",
    "quick_ratio",
    "net_debt",
    "operating_cash_flow",
    "free_cash_flow",
    "cfo_net_income",
)


class WorkspaceRepositoryBase:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.store = CommittedEvidenceStore(self.root)

    def _stock_row(self, symbol: str, snapshot_date: str | None) -> dict[str, Any]:
        row = next(
            (item for item in self.stocks(snapshot_date) if item["symbol"] == symbol),
            None,
        )
        if row is None:
            raise KeyError(f"unknown symbol: {symbol}")
        return row

    def _ensure_symbol(self, symbol: str, snapshot_date: str | None = None) -> None:
        if symbol not in {row["symbol"] for row in self.stocks(snapshot_date)}:
            raise KeyError(f"unknown symbol: {symbol}")

    def _identity_map(self) -> dict[str, dict[str, str]]:
        identities = {
            row["symbol"]: dict(row)
            for row in self.store.csv("configs/universe/candidate_symbols.csv")
            if row.get("name")
        }
        pilot = self.store.json("configs/providers/ifind_mcp_dual_stock_pilot.yaml")
        for row in pilot.get("symbols", []):
            if not isinstance(row, dict) or not row.get("symbol"):
                continue
            identities.setdefault(
                str(row["symbol"]),
                {
                    "symbol": str(row["symbol"]),
                    "name": str(row.get("company_name_cn", "")),
                    "sector": "",
                    "source_date": str(pilot.get("as_of_date", "")),
                    "identity_source": "ifind_mcp_dual_stock_pilot",
                },
            )
        return identities

    def _latest_by_symbol(
        self, rows: tuple[dict[str, str], ...], cutoff: str
    ) -> dict[str, dict[str, str]]:
        return self._latest_by_key(
            [row for row in rows if row.get("trade_date", "") <= cutoff], "symbol"
        )

    @staticmethod
    def _latest_by_key(
        rows: list[dict[str, str]] | tuple[dict[str, str], ...], key: str
    ) -> dict[str, dict[str, str]]:
        result: dict[str, dict[str, str]] = {}
        for row in sorted(rows, key=lambda item: item.get("trade_date", "")):
            result[row[key]] = row
        return result

    def _latest_panel(self, symbol: str, cutoff: str = "9999-12-31") -> dict[str, str]:
        return self._latest_by_symbol(self.store.provider_panel_rows(), cutoff).get(
            symbol, {}
        )

    def _panel_value(self, row: dict[str, str], field: str) -> dict[str, Any]:
        value = row.get(field)
        if value in {None, ""}:
            return self._unavailable()
        typed: Any = _bool(value) if value in {"true", "false"} else _float(value)
        if typed is None:
            typed = value
        return self._available(
            typed,
            row.get("trade_date"),
            row.get("source_provider"),
            row.get("crosscheck_status") or "EVIDENCE_BACKED",
        )

    @staticmethod
    def _available(
        value: Any,
        asof_date: str | None,
        source: str | None,
        quality_status: str = "EVIDENCE_BACKED",
    ) -> dict[str, Any]:
        if value is None or value == "":
            return WorkspaceRepositoryBase._unavailable()
        return {
            "value": value,
            "asof_date": asof_date,
            "source": source,
            "availability": "AVAILABLE",
            "quality_status": quality_status,
            "reason": None,
        }

    @staticmethod
    def _unavailable(reason: str = UNAVAILABLE_REASON) -> dict[str, Any]:
        return {
            "value": None,
            "asof_date": None,
            "source": None,
            "availability": "UNAVAILABLE",
            "quality_status": "NO_COMMITTED_EVIDENCE",
            "reason": reason,
        }

    def _snapshot_risk(self, snapshot_date: str) -> dict[str, str]:
        rows = self.store.snapshot_csv("portfolio_risk_state.csv", snapshot_date)
        return dict(rows[0]) if rows else {}

    def _risk_contributions(self) -> tuple[dict[str, str], ...]:
        return self.store.csv(
            "outputs/research/goal_premarket_portfolio_risk_management01_risk_contribution_summary.csv"
        )

    def _cluster_summary(self) -> tuple[dict[str, str], ...]:
        return self.store.csv(
            "outputs/research/goal_premarket_portfolio_risk_management01_correlation_cluster_summary.csv"
        )

    def _provider_quarantine(self) -> tuple[dict[str, str], ...]:
        return self.store.csv(
            "outputs/research/goal_premarket_portfolio_risk_management01_provider_discrepancy_quarantine.csv"
        )

    def _operational_refresh_context(self) -> dict[str, Any]:
        """Return bounded live acquisition identity without changing research lineage."""
        refresh = self.store.refresh_status(self.store.latest_snapshot_date())
        upstream = refresh.get("upstream_acquisition", {})
        upstream = upstream if isinstance(upstream, dict) else {}
        batch = upstream.get("operational_batch", {})
        batch = batch if isinstance(batch, dict) else {}
        observability = refresh.get("daily_operational_observability", {})
        observability = observability if isinstance(observability, dict) else {}
        refresh_path = str(refresh.get("refresh_manifest_path", ""))
        refresh_checksum = ""
        if refresh_path:
            candidate = (self.root / refresh_path).resolve()
            if (
                candidate != self.root
                and self.root in candidate.parents
                and candidate.is_file()
            ):
                refresh_checksum = hashlib.sha256(candidate.read_bytes()).hexdigest()
        return {
            "execution_mode": refresh.get("execution_mode"),
            "evidence_mode": refresh.get("evidence_mode"),
            "operational_provider": upstream.get("selected_upstream_source"),
            "operational_function": upstream.get("selected_function"),
            "operational_endpoint_family": upstream.get("selected_endpoint_family"),
            "operational_policy_id": upstream.get("policy_id"),
            "operational_adjustment": batch.get("adjustment_policy"),
            "operational_batch_checksum": upstream.get("selected_batch_checksum"),
            "canonical_checksum": refresh.get("canonical_evidence_checksum"),
            "snapshot_id": refresh.get("snapshot_id"),
            "snapshot_checksum": refresh.get("snapshot_checksum"),
            "refresh_manifest_checksum": refresh_checksum,
            "accepted_symbol_count": batch.get("accepted_symbol_count"),
            "rejected_symbol_count": batch.get("rejected_symbol_count"),
            "required_symbol_count": batch.get("required_symbol_count"),
            "source_dates": batch.get("source_dates", []),
            "amount_availability": observability.get("amount_availability"),
            "east_money_canonical_request_count": upstream.get(
                "east_money_canonical_request_count"
            ),
            "single_canonical_source": upstream.get("single_canonical_source"),
            "automatic_failback_to_east_money": upstream.get(
                "automatic_failback_to_east_money"
            ),
            "no_per_symbol_mixing": upstream.get("no_per_symbol_mixing"),
            "independent_verification_status": (
                upstream.get("independent_verification", {}).get("status")
                if isinstance(upstream.get("independent_verification"), dict)
                else None
            ),
            "runtime_code_commit": os.environ.get(
                "ASHARE_RUNTIME_CODE_COMMIT", "UNAVAILABLE"
            ),
        }

    @staticmethod
    def _typed_band(row: dict[str, str]) -> dict[str, Any]:
        return {
            **row,
            "current_weight": _float(row.get("current_weight")),
            "acceptable_band_min": _float(row.get("acceptable_band_min")),
            "acceptable_band_max": _float(row.get("acceptable_band_max")),
            "reference_policy_weight": _float(row.get("reference_policy_weight")),
            "confidence": _float(row.get("confidence")),
            "constraint_breach": row.get("constraint_breach"),
            "abstain": _bool(row.get("abstain")),
        }


def _float(value: str | None) -> float | None:
    try:
        return float(value) if value not in {None, ""} else None
    except ValueError:
        return None


def _bool(value: str | None) -> bool:
    return str(value).lower() == "true"


def _exchange(symbol: str) -> str:
    return (
        "Shanghai Stock Exchange"
        if symbol.endswith(".SH")
        else "Shenzhen Stock Exchange"
    )


def _board(symbol: str) -> str:
    code = symbol.split(".")[0]
    if code.startswith("300"):
        return "ChiNext"
    if code.startswith("688"):
        return "STAR Market"
    return "Shanghai Main Board" if symbol.endswith(".SH") else "Shenzhen Main Board"


def _max_severity(values: Any) -> str:
    rank = {
        "": 0,
        "none": 0,
        "low": 1,
        "medium": 2,
        "warning": 2,
        "high": 3,
        "critical": 4,
    }
    return max(values, key=lambda value: rank.get(value, 1), default="none")


def _reason_dimension(reasons: list[str], reason: str) -> str:
    return "AFFECTED" if reason in reasons else "NOT_TRIGGERED_BY_COMMITTED_EVIDENCE"

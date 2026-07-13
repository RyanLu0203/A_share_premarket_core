from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from ashare_premarket.dashboard.analytics import display_correlation_matrix
from ashare_premarket.dashboard.store import CommittedEvidenceStore
from ashare_premarket.daily_refresh.goal_daily_incremental_evidence_refresh01 import resolve_daily_refresh_context
from ashare_premarket.portfolio_risk.goal_premarket_position_management_operational01 import (
    evaluate_canonical_freshness,
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


class PremarketWorkspaceRepository:
    """Normalized read-only view models over validated committed evidence."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.store = CommittedEvidenceStore(self.root)

    def status(
        self,
        mode: str = "live",
        snapshot_date: str | None = None,
        execution_time: datetime | str | None = None,
    ) -> dict[str, Any]:
        context: dict[str, Any] = {}
        if mode == "live":
            execution = execution_time.isoformat() if isinstance(execution_time, datetime) else execution_time
            context = resolve_daily_refresh_context(self.root, execution_time=execution, replay_date=None)
            target = str(context.get("target_trading_date", ""))
            selected = snapshot_date or self.store.snapshot_date_at_or_before(target) or self.store.latest_snapshot_date()
        else:
            selected = snapshot_date or self.store.latest_snapshot_date()
        manifest = self.store.snapshot_manifest(selected)
        verified, checksum_failures = self.store.verify_snapshot(selected)
        refresh = self.store.refresh_status(selected if mode == "replay" else None)
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

    def stocks(self, snapshot_date: str | None = None) -> list[dict[str, Any]]:
        selected = snapshot_date or self.store.latest_snapshot_date()
        manifest = self.store.snapshot_manifest(selected)
        cutoff = str(manifest["latest_available_data_date"])
        bands = {row["symbol"]: row for row in self.store.snapshot_csv("position_band_status.csv", selected)}
        risk = {row["symbol"]: row for row in self._risk_contributions()}
        abstentions = {row["symbol"]: row for row in self.store.snapshot_csv("abstention_summary.csv", selected)}
        latest_canonical = self._latest_by_symbol(self.store.canonical_rows(selected), cutoff)
        latest_panel = self._latest_by_symbol(self.store.provider_panel_rows(), cutoff)
        identity = self._identity_map()
        rows: list[dict[str, Any]] = []
        for symbol in sorted(bands):
            band = bands[symbol]
            canonical = latest_canonical.get(symbol, {})
            panel = latest_panel.get(symbol, {})
            known = identity.get(symbol, {})
            company = known.get("name", "")
            industry = known.get("sector", "")
            latest_date = canonical.get("trade_date")
            latest_source = canonical.get("source_provider")
            rows.append(
                {
                    "symbol": symbol,
                    "display_name": company or symbol,
                    "company_name": self._available(company, known.get("source_date"), "configs/universe/candidate_symbols.csv") if company else self._unavailable(),
                    "company_name_en": self._available(company, known.get("source_date"), "configs/universe/candidate_symbols.csv") if company else self._unavailable(),
                    "exchange": self._available(_exchange(symbol), latest_date, "symbol_suffix", "DERIVED"),
                    "board": self._available(_board(symbol), latest_date, "symbol_prefix", "DERIVED"),
                    "industry": self._available(industry, known.get("source_date"), "configs/universe/candidate_symbols.csv") if industry else self._unavailable(),
                    "industry_level1": self._available(
                        industry,
                        known.get("source_date"),
                        "configs/universe/candidate_symbols.csv",
                        "CONFIGURED_UNIVERSE_SECTOR",
                    )
                    if industry
                    else self._unavailable(),
                    "industry_level2": self._unavailable("no level-2 industry classification is present in committed evidence"),
                    "latest_price": self._available(_float(canonical.get("canonical_close")), latest_date, latest_source),
                    "price_change": self._available(_float(canonical.get("canonical_return_1d")), latest_date, latest_source),
                    "market_cap": self._unavailable(),
                    "pe_ttm": self._panel_value(panel, "pe_ttm"),
                    "pb": self._panel_value(panel, "pb"),
                    "current_weight": _float(band.get("current_weight")),
                    "band_min": _float(band.get("acceptable_band_min")),
                    "band_max": _float(band.get("acceptable_band_max")),
                    "reference_weight": _float(band.get("reference_policy_weight")),
                    "band_status": band.get("band_status"),
                    "risk_contribution": _float(risk.get(symbol, {}).get("risk_contribution_share")),
                    "confidence": _float(band.get("confidence")),
                    "abstain": _bool(band.get("abstain")),
                    "abstention_reason": abstentions.get(symbol, {}).get("abstention_reason") or None,
                    "provider_quality": band.get("provider_quality"),
                    "portfolio_mode": HOLDINGS_MODE_LABEL,
                    "research_only": True,
                }
            )
        return rows

    def stock(self, symbol: str, snapshot_date: str | None = None) -> dict[str, Any]:
        stock = self._stock_row(symbol, snapshot_date)
        detail = {
            **stock,
            "listing_date": self._unavailable(),
            "st_status": self._panel_value(self._latest_panel(symbol), "is_st"),
            "trading_status": self._panel_value(self._latest_panel(symbol), "trading_status"),
            "total_shares": self._unavailable(),
            "float_shares": self._unavailable(),
            "float_market_cap": self._unavailable(),
            "free_float_market_cap": self._unavailable(),
            "provider_lineage": ["akshare_sina", "baostock"],
            "freshness_state": self.status("replay", snapshot_date)["freshness_code"],
        }
        return detail

    def stock_market(self, symbol: str, snapshot_date: str | None = None) -> dict[str, Any]:
        stock = self._stock_row(symbol, snapshot_date)
        cutoff = str(self.store.snapshot_manifest(snapshot_date).get("data_cutoff"))
        candles = [
            {
                "trade_date": row["trade_date"],
                "open": _float(row.get("open")),
                "high": _float(row.get("high")),
                "low": _float(row.get("low")),
                "close": _float(row.get("close")),
                "volume": _float(row.get("volume")),
                "amount": _float(row.get("amount")),
                "turnover": _float(row.get("turnover")),
                "source": row.get("source_provider"),
                "quality": row.get("crosscheck_status"),
            }
            for row in self.store.provider_panel_rows()
            if row.get("symbol") == symbol and row.get("trade_date", "") <= cutoff
        ]
        candles.sort(key=lambda row: row["trade_date"])
        panel = self._latest_panel(symbol, cutoff)
        quality_markers = dict(sorted(Counter(str(row.get("quality") or "UNKNOWN") for row in candles).items()))
        discrepancy_markers = [
            row
            for row in self._provider_quarantine()
            if row.get("symbol") == symbol and row.get("trade_date", "") <= cutoff
        ]
        regimes = [
            {
                "trade_date": row.get("trade_date"),
                "regime": row.get("refined_composite_regime_label"),
                "confidence_tier": row.get("regime_confidence_tier"),
                "quality_status": row.get("regime_refinement_status"),
            }
            for row in self.store.csv("outputs/research/goal_regime_label_research02_refined_date_regime_labels.csv")
            if row.get("trade_date", "") <= cutoff
        ][-60:]
        return {
            "symbol": symbol,
            "latest_close": stock["latest_price"],
            "latest_return": stock["price_change"],
            "candles": candles,
            "candlestick_latest_date": candles[-1]["trade_date"] if candles else None,
            "candlestick_source": "baostock_unadjusted" if candles else None,
            "quality_markers": quality_markers,
            "provider_discrepancy_markers": discrepancy_markers,
            "regime_strip": regimes,
            "previous_close": self._panel_value(panel, "pre_close"),
            "open": self._panel_value(panel, "open"),
            "high": self._panel_value(panel, "high"),
            "low": self._panel_value(panel, "low"),
            "volume": self._panel_value(panel, "volume"),
            "amount": self._panel_value(panel, "amount"),
            "turnover": self._panel_value(panel, "turnover"),
            "amplitude": self._unavailable("amplitude is not committed as a validated field"),
            "limit_up_price": self._unavailable(),
            "limit_down_price": self._unavailable(),
            "high_52_week": self._unavailable(),
            "low_52_week": self._unavailable(),
            "live_quote_available": False,
            "research_only": True,
        }

    def stock_fundamentals(self, symbol: str) -> dict[str, Any]:
        self._ensure_symbol(symbol)
        panel = self._latest_panel(symbol)
        result = {field: self._unavailable() for field in FUNDAMENTAL_FIELDS}
        result["pe_ttm"] = self._panel_value(panel, "pe_ttm")
        result["pb"] = self._panel_value(panel, "pb")
        return {"symbol": symbol, **result, "research_only": True}

    def stock_risk(self, symbol: str, snapshot_date: str | None = None) -> dict[str, Any]:
        self._ensure_symbol(symbol)
        risk = next((row for row in self._risk_contributions() if row["symbol"] == symbol), {})
        band = next((row for row in self.store.snapshot_csv("position_band_status.csv", snapshot_date) if row["symbol"] == symbol), {})
        quarantine = [row for row in self._provider_quarantine() if row.get("symbol") == symbol]
        return {
            "symbol": symbol,
            "volatility_20d": self._unavailable(),
            "volatility_60d": self._available(_float(risk.get("volatility_60d")), risk.get("asof_date"), "GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01"),
            "ewma_volatility": self._unavailable("only portfolio-level EWMA volatility is committed"),
            "beta": self._unavailable("only portfolio-level beta is committed"),
            "drawdown": self._unavailable("only portfolio-level drawdown is committed"),
            "cvar_95": self._unavailable("only portfolio-level CVaR is committed"),
            "marginal_risk_contribution": self._unavailable(),
            "component_risk_contribution": self._available(_float(risk.get("risk_contribution_share")), risk.get("asof_date"), "GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01"),
            "correlation_cluster": self._unavailable("only aggregate cluster counts are committed"),
            "provider_quality": band.get("provider_quality"),
            "quarantine_state": "QUARANTINED_PROVIDER_DISCREPANCY" if quarantine else "NOT_QUARANTINED",
            "quarantine_evidence": quarantine,
            "research_only": True,
        }

    def stock_position(self, symbol: str, snapshot_date: str | None = None) -> dict[str, Any]:
        self._ensure_symbol(symbol)
        band = next(row for row in self.store.snapshot_csv("position_band_status.csv", snapshot_date) if row["symbol"] == symbol)
        constraints = [row for row in self.store.snapshot_csv("constraint_evaluation.csv", snapshot_date) if row.get("symbol") == symbol]
        return {
            **self._typed_band(band),
            "abstention_reason_codes": [reason for reason in band.get("abstention_reason", "").split(";") if reason],
            "constraints": constraints,
            "portfolio_mode": HOLDINGS_MODE_LABEL,
        }

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

    def quant_capabilities(self) -> dict[str, Any]:
        rerun = self.store.json("outputs/audits/goal_factor_readiness_rerun02_manifest.json")
        quant04 = self.store.json("outputs/audits/goal_quant_research04_manifest.json")
        statuses = Counter(row.get("overall_factor_status") for row in self.store.csv("outputs/research/goal_quant_research04_factor_overall_status.csv"))
        decision_reasons = {
            row.get("candidate_id", ""): row
            for row in self.store.csv("outputs/research/goal_factor_readiness_rerun02_readiness_decision_reasons.csv")
        }
        candidate_rows = [
            {**row, **decision_reasons.get(row.get("candidate_id", ""), {})}
            for row in self.store.csv("outputs/research/goal_factor_readiness_rerun02_factor_readiness_status.csv")
        ]
        return {
            "ready_factor_count": 0,
            "alpha_overview_state": "LOCKED_NO_READY_FACTORS",
            "factor_monitor_state": "LOCKED_NO_READY_FACTORS",
            "ic_rankic_lab_state": "BLOCKED_PENDING_READY_FACTOR",
            "factor_correlation_state": "LOCKED_NO_READY_FACTORS",
            "candidate_diagnostics_state": "LOCKED_READ_ONLY_HISTORICAL",
            "recommendation_tiering_state": "locked_future",
            "issue_10_state": "locked",
            "candidate_readiness": {
                "evaluated": int(rerun.get("candidates_evaluated", 0)),
                "ready": int(rerun.get("ready_factor_count", 0)),
                "conditionally_useful": int(rerun.get("conditionally_useful_candidate_count", 0)),
                "not_ready": int(rerun.get("candidates_evaluated", 0)) - int(rerun.get("ready_factor_count", 0)),
            },
            "quant04_refined_factors": {
                "evaluated": int(quant04.get("evaluated_refined_factor_count", 0)),
                "ready": int(quant04.get("ready_factor_count", 0)),
                "conditionally_useful": statuses.get("conditionally_useful", 0),
                "not_ready": statuses.get("not_ready", 0),
            },
            "unlock_conditions": ["scientifically ready factor evidence", "explicit owner authorization"],
            "factor_table_contract": ["factor", "IC", "RankIC", "IR", "sign stability", "horizon stability", "regime consistency", "OOS status", "readiness"],
            "candidate_rows": candidate_rows,
            "market_regime_context_available": True,
            "factor_regime_analysis_locked": True,
            "research_only": True,
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
        current = self.stocks()
        current_symbols = {row["symbol"] for row in current}
        identity = self._identity_map()
        approved = {row["symbol"]: row for row in self.store.csv("configs/universe/approved_symbols.csv") if row.get("approval_status") == "approved"}
        configured = {row["symbol"]: row for row in self.store.csv("configs/universe/candidate_symbols.csv") if row.get("symbol")}
        eligible = sorted(set(approved) | {symbol for symbol, row in configured.items() if row.get("universe_group") == "blocked_pending"})
        candidates = []
        for symbol in eligible:
            if symbol in current_symbols:
                continue
            known = identity.get(symbol, {})
            name = known.get("name") or symbol
            sector = known.get("sector") or approved.get(symbol, {}).get("sector")
            blocked_pending = configured.get(symbol, {}).get("universe_group") == "blocked_pending"
            state = "BLOCKED_PENDING_OBSERVATION_ONLY" if blocked_pending else "EVIDENCE_PENDING"
            reason = "blocked/pending symbol is observation-only and excluded from active outputs" if blocked_pending else "approved watchlist candidate is not present in the latest validated OPM snapshot"
            unavailable = self._unavailable(reason)
            candidates.append(
                {
                    "symbol": symbol,
                    "display_name": name,
                    "company_name": self._available(name, None, "configs/universe/candidate_symbols.csv", "APPROVED_CONFIG"),
                    "exchange": self._available(_exchange(symbol), None, "symbol_suffix", "DERIVED"),
                    "board": self._available(_board(symbol), None, "symbol_prefix", "DERIVED"),
                    "industry": self._available(sector, None, "configs/universe/approved_symbols.csv", "APPROVED_CONFIG"),
                    "latest_price": unavailable,
                    "price_change": unavailable,
                    "market_cap": unavailable,
                    "pe_ttm": unavailable,
                    "pb": unavailable,
                    "current_weight": None,
                    "band_min": None,
                    "band_max": None,
                    "band_status": state,
                    "risk_contribution": None,
                    "confidence": None,
                    "abstain": True,
                    "abstention_reason": "blocked_pending_observation_only" if blocked_pending else "not_in_current_validated_snapshot",
                    "provider_quality": state,
                    "governance_status": "blocked_pending" if blocked_pending else "approved_evidence_pending",
                    "observation_only": True,
                    "portfolio_mode": HOLDINGS_MODE_LABEL,
                    "research_only": True,
                }
            )
        return {
            "storage": "browser_local_storage",
            "server_writes": False,
            "symbols": [row["symbol"] for row in current[:8]],
            "candidates": candidates,
            "eligible_symbols": sorted(current_symbols | {row["symbol"] for row in candidates}),
        }

    def _stock_row(self, symbol: str, snapshot_date: str | None) -> dict[str, Any]:
        row = next((item for item in self.stocks(snapshot_date) if item["symbol"] == symbol), None)
        if row is None:
            raise KeyError(f"unknown symbol: {symbol}")
        return row

    def _ensure_symbol(self, symbol: str) -> None:
        if symbol not in {row["symbol"] for row in self.stocks()}:
            raise KeyError(f"unknown symbol: {symbol}")

    def _identity_map(self) -> dict[str, dict[str, str]]:
        return {
            row["symbol"]: dict(row)
            for row in self.store.csv("configs/universe/candidate_symbols.csv")
            if row.get("name")
        }

    def _latest_by_symbol(self, rows: tuple[dict[str, str], ...], cutoff: str) -> dict[str, dict[str, str]]:
        return self._latest_by_key([row for row in rows if row.get("trade_date", "") <= cutoff], "symbol")

    @staticmethod
    def _latest_by_key(rows: list[dict[str, str]] | tuple[dict[str, str], ...], key: str) -> dict[str, dict[str, str]]:
        result: dict[str, dict[str, str]] = {}
        for row in sorted(rows, key=lambda item: item.get("trade_date", "")):
            result[row[key]] = row
        return result

    def _latest_panel(self, symbol: str, cutoff: str = "9999-12-31") -> dict[str, str]:
        return self._latest_by_symbol(self.store.provider_panel_rows(), cutoff).get(symbol, {})

    def _panel_value(self, row: dict[str, str], field: str) -> dict[str, Any]:
        value = row.get(field)
        if value in {None, ""}:
            return self._unavailable()
        typed: Any = _bool(value) if value in {"true", "false"} else _float(value)
        if typed is None:
            typed = value
        return self._available(typed, row.get("trade_date"), row.get("source_provider"), row.get("crosscheck_status") or "EVIDENCE_BACKED")

    @staticmethod
    def _available(value: Any, asof_date: str | None, source: str | None, quality_status: str = "EVIDENCE_BACKED") -> dict[str, Any]:
        if value is None or value == "":
            return PremarketWorkspaceRepository._unavailable()
        return {"value": value, "asof_date": asof_date, "source": source, "availability": "AVAILABLE", "quality_status": quality_status, "reason": None}

    @staticmethod
    def _unavailable(reason: str = UNAVAILABLE_REASON) -> dict[str, Any]:
        return {"value": None, "asof_date": None, "source": None, "availability": "UNAVAILABLE", "quality_status": "NO_COMMITTED_EVIDENCE", "reason": reason}

    def _snapshot_risk(self, snapshot_date: str) -> dict[str, str]:
        rows = self.store.snapshot_csv("portfolio_risk_state.csv", snapshot_date)
        return dict(rows[0]) if rows else {}

    def _risk_contributions(self) -> tuple[dict[str, str], ...]:
        return self.store.csv("outputs/research/goal_premarket_portfolio_risk_management01_risk_contribution_summary.csv")

    def _cluster_summary(self) -> tuple[dict[str, str], ...]:
        return self.store.csv("outputs/research/goal_premarket_portfolio_risk_management01_correlation_cluster_summary.csv")

    def _provider_quarantine(self) -> tuple[dict[str, str], ...]:
        return self.store.csv("outputs/research/goal_premarket_portfolio_risk_management01_provider_discrepancy_quarantine.csv")

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
    return "Shanghai Stock Exchange" if symbol.endswith(".SH") else "Shenzhen Stock Exchange"


def _board(symbol: str) -> str:
    code = symbol.split(".")[0]
    if code.startswith("300"):
        return "ChiNext"
    if code.startswith("688"):
        return "STAR Market"
    return "Shanghai Main Board" if symbol.endswith(".SH") else "Shenzhen Main Board"


def _max_severity(values: Any) -> str:
    rank = {"": 0, "none": 0, "low": 1, "medium": 2, "warning": 2, "high": 3, "critical": 4}
    return max(values, key=lambda value: rank.get(value, 1), default="none")


def _reason_dimension(reasons: list[str], reason: str) -> str:
    return "AFFECTED" if reason in reasons else "NOT_TRIGGERED_BY_COMMITTED_EVIDENCE"

from __future__ import annotations

from collections import Counter
from typing import Any

from ashare_premarket.dashboard.repositories.base import (
    FUNDAMENTAL_FIELDS,
    HOLDINGS_MODE_LABEL,
    WorkspaceRepositoryBase,
    _board,
    _bool,
    _exchange,
    _float,
)


class StockRepository(WorkspaceRepositoryBase):
    def stocks(self, snapshot_date: str | None = None) -> list[dict[str, Any]]:
        selected = snapshot_date or self.store.latest_snapshot_date()
        manifest = self.store.snapshot_manifest(selected)
        cutoff = str(manifest["latest_available_data_date"])
        bands = {
            row["symbol"]: row
            for row in self.store.snapshot_csv("position_band_status.csv", selected)
        }
        risk = {row["symbol"]: row for row in self._risk_contributions()}
        abstentions = {
            row["symbol"]: row
            for row in self.store.snapshot_csv("abstention_summary.csv", selected)
        }
        latest_canonical = self._latest_by_symbol(
            self.store.canonical_rows(selected), cutoff
        )
        latest_panel = self._latest_by_symbol(self.store.provider_panel_rows(), cutoff)
        identity = self._identity_map()
        pilot_contract = self.store.json(
            "configs/providers/ifind_mcp_dual_stock_pilot.yaml"
        )
        pilot_symbols = {
            str(row["symbol"]): dict(row)
            for row in pilot_contract.get("symbols", [])
            if isinstance(row, dict) and row.get("symbol")
        }
        rows: list[dict[str, Any]] = []
        for symbol in sorted(set(bands) | set(pilot_symbols)):
            band = bands.get(symbol, {})
            canonical = latest_canonical.get(symbol, {})
            panel = latest_panel.get(symbol, {})
            known = identity.get(symbol, {})
            pilot = pilot_symbols.get(symbol, {})
            configured_name = known.get("name", "")
            company_name_cn = str(pilot.get("company_name_cn") or configured_name)
            company_name_en = (
                configured_name
                if not pilot or configured_name != company_name_cn
                else ""
            )
            industry = known.get("sector", "")
            latest_date = canonical.get("trade_date") or panel.get("trade_date")
            latest_source = canonical.get("source_provider") or panel.get(
                "source_provider"
            )
            latest_price = _float(canonical.get("canonical_close"))
            if latest_price is None:
                latest_price = _float(panel.get("close"))
            latest_return = _float(canonical.get("canonical_return_1d"))
            if latest_return is None:
                panel_pct_change = _float(panel.get("pct_chg"))
                latest_return = (
                    panel_pct_change / 100.0 if panel_pct_change is not None else None
                )
            in_reference_portfolio = bool(band)
            rows.append(
                {
                    "symbol": symbol,
                    "display_name": company_name_cn or symbol,
                    "company_name": (
                        self._available(
                            company_name_cn,
                            (
                                pilot_contract.get("as_of_date")
                                if pilot
                                else known.get("source_date")
                            ),
                            (
                                pilot.get("official_identity_evidence")
                                if pilot
                                else "configs/universe/candidate_symbols.csv"
                            ),
                            (
                                "OFFICIAL_IDENTITY_VERIFIED"
                                if pilot
                                else "EVIDENCE_BACKED"
                            ),
                        )
                        if company_name_cn
                        else self._unavailable()
                    ),
                    "company_name_en": (
                        self._available(
                            company_name_en,
                            known.get("source_date"),
                            "configs/universe/candidate_symbols.csv",
                        )
                        if company_name_en
                        else (
                            self._unavailable(
                                "English company name is not yet accepted for this pilot security"
                            )
                            if pilot
                            else self._unavailable()
                        )
                    ),
                    "exchange": self._available(
                        _exchange(symbol), latest_date, "symbol_suffix", "DERIVED"
                    ),
                    "board": self._available(
                        _board(symbol), latest_date, "symbol_prefix", "DERIVED"
                    ),
                    "industry": (
                        self._available(
                            industry,
                            known.get("source_date"),
                            "configs/universe/candidate_symbols.csv",
                        )
                        if industry
                        else self._unavailable()
                    ),
                    "industry_level1": (
                        self._available(
                            industry,
                            known.get("source_date"),
                            "configs/universe/candidate_symbols.csv",
                            "CONFIGURED_UNIVERSE_SECTOR",
                        )
                        if industry
                        else self._unavailable()
                    ),
                    "industry_level2": self._unavailable(
                        "no level-2 industry classification is present in committed evidence"
                    ),
                    "latest_price": self._available(
                        latest_price, latest_date, latest_source
                    ),
                    "price_change": self._available(
                        latest_return, latest_date, latest_source
                    ),
                    "market_cap": self._unavailable(),
                    "pe_ttm": self._panel_value(panel, "pe_ttm"),
                    "pb": self._panel_value(panel, "pb"),
                    "current_weight": _float(band.get("current_weight")),
                    "band_min": _float(band.get("acceptable_band_min")),
                    "band_max": _float(band.get("acceptable_band_max")),
                    "reference_weight": _float(band.get("reference_policy_weight")),
                    "band_status": band.get("band_status")
                    or "NOT_IN_REFERENCE_PORTFOLIO",
                    "risk_contribution": _float(
                        risk.get(symbol, {}).get("risk_contribution_share")
                    ),
                    "confidence": _float(band.get("confidence")),
                    "abstain": (
                        _bool(band.get("abstain")) if in_reference_portfolio else None
                    ),
                    "abstention_reason": abstentions.get(symbol, {}).get(
                        "abstention_reason"
                    )
                    or None,
                    "provider_quality": band.get("provider_quality")
                    or pilot.get(
                        "pilot_acceptance_state",
                        "SECURITY_FOUNDATION_ONLY",
                    ),
                    "portfolio_membership_state": (
                        "REFERENCE_PORTFOLIO_MEMBER"
                        if in_reference_portfolio
                        else "NOT_IN_REFERENCE_PORTFOLIO"
                    ),
                    "security_browsing_state": (
                        "IFIND_DUAL_STOCK_PILOT"
                        if pilot
                        else "COMMITTED_REFERENCE_PORTFOLIO_SECURITY"
                    ),
                    "pilot_acceptance_state": pilot.get("pilot_acceptance_state"),
                    "portfolio_mode": (
                        HOLDINGS_MODE_LABEL
                        if in_reference_portfolio
                        else "SECURITY RESEARCH FOUNDATION ONLY"
                    ),
                    "research_only": True,
                }
            )
        return rows

    def stock(self, symbol: str, snapshot_date: str | None = None) -> dict[str, Any]:
        stock = self._stock_row(symbol, snapshot_date)
        selected = snapshot_date or self.store.latest_snapshot_date()
        manifest = self.store.snapshot_manifest(selected)
        cutoff = str(
            manifest.get("data_cutoff") or manifest.get("latest_available_data_date")
        )
        latest_panel = self._latest_panel(symbol, cutoff)
        operational = (
            self._operational_refresh_context() if snapshot_date is None else {}
        )
        detail = {
            **stock,
            "listing_date": self._unavailable(),
            "st_status": self._panel_value(latest_panel, "is_st"),
            "trading_status": self._panel_value(latest_panel, "trading_status"),
            "total_shares": self._unavailable(),
            "float_shares": self._unavailable(),
            "float_market_cap": self._unavailable(),
            "free_float_market_cap": self._unavailable(),
            "provider_lineage": (
                ["akshare_sina", "baostock"]
                if latest_panel
                else ["ifind_live_acceptance_pending"]
            ),
            "freshness_state": (
                self.status("replay", snapshot_date)["freshness_code"]
                if snapshot_date
                else self.status("live")["freshness_code"]
            ),
        }
        if snapshot_date is None:
            detail.update(
                {
                    "historical_research_provider_lineage": [
                        "akshare_sina",
                        "baostock",
                    ],
                    "operational_provider": operational.get("operational_provider"),
                    "operational_function": operational.get("operational_function"),
                    "operational_adjustment": operational.get("operational_adjustment"),
                }
            )
        return detail

    def stock_market(
        self, symbol: str, snapshot_date: str | None = None
    ) -> dict[str, Any]:
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
        quality_markers = dict(
            sorted(
                Counter(str(row.get("quality") or "UNKNOWN") for row in candles).items()
            )
        )
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
            for row in self.store.csv(
                "outputs/research/goal_regime_label_research02_refined_date_regime_labels.csv"
            )
            if row.get("trade_date", "") <= cutoff
        ][-60:]
        result = {
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
            "amplitude": self._unavailable(
                "amplitude is not committed as a validated field"
            ),
            "limit_up_price": self._unavailable(),
            "limit_down_price": self._unavailable(),
            "high_52_week": self._unavailable(),
            "low_52_week": self._unavailable(),
            "live_quote_available": False,
            "research_only": True,
        }
        if snapshot_date is None:
            result.update(
                {
                    "historical_chart_source": (
                        "baostock_unadjusted" if candles else None
                    ),
                    "historical_chart_data_cutoff": cutoff,
                    "current_operational_provider": self._operational_refresh_context().get(
                        "operational_provider"
                    ),
                }
            )
        return result

    def stock_fundamentals(self, symbol: str) -> dict[str, Any]:
        self._ensure_symbol(symbol)
        selected = self.store.latest_snapshot_date()
        cutoff = str(self.store.snapshot_manifest(selected).get("data_cutoff"))
        panel = self._latest_panel(symbol, cutoff)
        result = {field: self._unavailable() for field in FUNDAMENTAL_FIELDS}
        result["pe_ttm"] = self._panel_value(panel, "pe_ttm")
        result["pb"] = self._panel_value(panel, "pb")
        return {"symbol": symbol, **result, "research_only": True}

    def stock_risk(
        self, symbol: str, snapshot_date: str | None = None
    ) -> dict[str, Any]:
        self._ensure_symbol(symbol, snapshot_date)
        risk = next(
            (row for row in self._risk_contributions() if row["symbol"] == symbol), {}
        )
        band = next(
            (
                row
                for row in self.store.snapshot_csv(
                    "position_band_status.csv", snapshot_date
                )
                if row["symbol"] == symbol
            ),
            {},
        )
        quarantine = [
            row for row in self._provider_quarantine() if row.get("symbol") == symbol
        ]
        return {
            "symbol": symbol,
            "volatility_20d": self._unavailable(),
            "volatility_60d": self._available(
                _float(risk.get("volatility_60d")),
                risk.get("asof_date"),
                "GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01",
            ),
            "ewma_volatility": self._unavailable(
                "only portfolio-level EWMA volatility is committed"
            ),
            "beta": self._unavailable("only portfolio-level beta is committed"),
            "drawdown": self._unavailable("only portfolio-level drawdown is committed"),
            "cvar_95": self._unavailable("only portfolio-level CVaR is committed"),
            "marginal_risk_contribution": self._unavailable(),
            "component_risk_contribution": self._available(
                _float(risk.get("risk_contribution_share")),
                risk.get("asof_date"),
                "GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01",
            ),
            "correlation_cluster": self._unavailable(
                "only aggregate cluster counts are committed"
            ),
            "provider_quality": band.get("provider_quality"),
            "quarantine_state": (
                "QUARANTINED_PROVIDER_DISCREPANCY" if quarantine else "NOT_QUARANTINED"
            ),
            "quarantine_evidence": quarantine,
            "risk_research_state": (
                "REFERENCE_PORTFOLIO_RISK_EVIDENCE"
                if risk
                else "RESEARCH_NOT_RUN_FOR_SECURITY_FOUNDATION"
            ),
            "portfolio_membership_state": (
                "REFERENCE_PORTFOLIO_MEMBER" if band else "NOT_IN_REFERENCE_PORTFOLIO"
            ),
            "research_only": True,
        }

    def stock_position(
        self, symbol: str, snapshot_date: str | None = None
    ) -> dict[str, Any]:
        self._ensure_symbol(symbol, snapshot_date)
        band = next(
            (
                row
                for row in self.store.snapshot_csv(
                    "position_band_status.csv", snapshot_date
                )
                if row["symbol"] == symbol
            ),
            {},
        )
        if not band:
            return {
                "symbol": symbol,
                "current_weight": None,
                "reference_policy_weight": None,
                "acceptable_band_min": None,
                "acceptable_band_max": None,
                "band_status": "NOT_IN_REFERENCE_PORTFOLIO",
                "confidence": None,
                "constraint_breach": None,
                "abstain": None,
                "abstention_reason_codes": [],
                "constraints": [],
                "portfolio_membership_state": "NOT_IN_REFERENCE_PORTFOLIO",
                "position_research_state": "POSITION_RESEARCH_NOT_RUN",
                "actionable_use_allowed": False,
                "portfolio_mode": "SECURITY RESEARCH FOUNDATION ONLY",
            }
        constraints = [
            row
            for row in self.store.snapshot_csv(
                "constraint_evaluation.csv", snapshot_date
            )
            if row.get("symbol") == symbol
        ]
        return {
            **self._typed_band(band),
            "abstention_reason_codes": [
                reason
                for reason in band.get("abstention_reason", "").split(";")
                if reason
            ],
            "constraints": constraints,
            "portfolio_membership_state": "REFERENCE_PORTFOLIO_MEMBER",
            "position_research_state": "REFERENCE_PORTFOLIO_DIAGNOSTIC_ONLY",
            "actionable_use_allowed": False,
            "portfolio_mode": HOLDINGS_MODE_LABEL,
        }

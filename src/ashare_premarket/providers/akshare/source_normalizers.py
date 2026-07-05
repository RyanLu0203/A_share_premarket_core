from __future__ import annotations

from collections import defaultdict


NON_ACTIONABLE = "research_only_not_recommendation_or_position_output"


def trading_calendar_status_context(panel_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in panel_rows:
        trade_date = row["trade_date"]
        symbol = row["symbol"]
        rows.append(
            {
                "trade_date": trade_date,
                "symbol": symbol,
                "is_trading_day": "true",
                "listing_status": "listed_committed_provider02b_universe",
                "st_status": "st_risk_warning" if row.get("is_st") == "true" else "normal",
                "suspension_status": "suspended" if row.get("trading_status") != "trading" else "trading",
                "delisting_status": "not_observed_in_committed_panel",
                "name_change_status": "not_available_offline_replay",
                "source_id": "ashare_trading_calendar;ashare_daily_ohlcv;ashare_st_risk_warning;ashare_suspension_resumption",
                "source_provider": row.get("source_provider", "committed_evidence"),
                "provider_timestamp": trade_date,
                "pit_available_date": trade_date,
                "no_lookahead_status": "passed_current_or_past_only",
                "data_status": "committed_evidence_replay",
                "non_actionable_disclaimer": NON_ACTIONABLE,
            }
        )
    return rows


def broad_index_regime_panel(date_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    index_specs = [
        ("000300.SH", "CSI 300", "csi_indices"),
        ("000001.SH", "SSE Composite proxy", "sse_indices"),
        ("399001.SZ", "Shenzhen Component proxy", "szse_indices"),
    ]
    for row in date_rows:
        for index_id, index_name, source_id in index_specs:
            rows.append(
                {
                    "trade_date": row["trade_date"],
                    "index_id": index_id,
                    "index_name": index_name,
                    "open": "",
                    "high": "",
                    "low": "",
                    "close": "",
                    "volume": "",
                    "amount": "",
                    "turnover": "",
                    "trailing_return_5d": row.get("benchmark_trailing_return_5d", ""),
                    "trailing_return_20d": row.get("benchmark_trailing_return_20d", ""),
                    "trailing_volatility_20d": row.get("benchmark_trailing_volatility_20d", ""),
                    "trailing_drawdown_20d": "",
                    "source_id": source_id,
                    "source_provider": row.get("source_provider", "committed_evidence"),
                    "provider_timestamp": row["trade_date"],
                    "pit_available_date": row["trade_date"],
                    "no_lookahead_status": row.get("no_lookahead_status", "passed_current_or_past_only"),
                    "data_status": "committed_regime_label_proxy_no_raw_index_ohlcv",
                    "non_actionable_disclaimer": NON_ACTIONABLE,
                }
            )
    return rows


def sector_concept_regime_panel(date_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in date_rows:
        specs = [
            ("market_breadth_proxy", "Market breadth derived proxy", "derived_market_breadth", "market_breadth_proxy"),
            ("market_dispersion_proxy", "Market dispersion derived proxy", "derived_market_dispersion", "industry_indices"),
            ("market_liquidity_proxy", "Market liquidity derived proxy", "derived_market_liquidity", "market_turnover_proxy"),
        ]
        for board_id, board_name, board_type, source_id in specs:
            rows.append(
                {
                    "trade_date": row["trade_date"],
                    "board_id": board_id,
                    "board_name": board_name,
                    "board_type": board_type,
                    "classification_system": "committed_provider02b_cross_section_proxy",
                    "open": "",
                    "high": "",
                    "low": "",
                    "close": "",
                    "volume": "",
                    "amount": "",
                    "turnover": row.get("universe_liquidity_proxy", "") if "liquidity" in board_id else "",
                    "constituent_count": row.get("valid_symbol_count", ""),
                    "positive_constituent_share": row.get("universe_positive_return_share", ""),
                    "negative_constituent_share": row.get("universe_negative_return_share", ""),
                    "trailing_return_5d": row.get("benchmark_trailing_return_5d", ""),
                    "trailing_return_20d": row.get("benchmark_trailing_return_20d", ""),
                    "trailing_volatility_20d": row.get("benchmark_trailing_volatility_20d", ""),
                    "source_id": source_id,
                    "source_provider": row.get("source_provider", "committed_evidence"),
                    "provider_timestamp": row["trade_date"],
                    "pit_available_date": row["trade_date"],
                    "no_lookahead_status": row.get("no_lookahead_status", "passed_current_or_past_only"),
                    "data_status": "derived_from_committed_provider02b_and_regime01",
                    "non_actionable_disclaimer": NON_ACTIONABLE,
                }
            )
    return rows


def liquidity_capital_flow_panel(panel_rows: list[dict[str, str]], date_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    amount_by_date: dict[str, float] = defaultdict(float)
    volume_by_date: dict[str, float] = defaultdict(float)
    turnover_by_date: dict[str, float] = defaultdict(float)
    count_by_date: dict[str, int] = defaultdict(int)
    for row in panel_rows:
        trade_date = row["trade_date"]
        amount_by_date[trade_date] += _float(row.get("amount"))
        volume_by_date[trade_date] += _float(row.get("volume"))
        turnover_by_date[trade_date] += _float(row.get("turnover"))
        count_by_date[trade_date] += 1
    rows: list[dict[str, object]] = []
    for row in date_rows:
        trade_date = row["trade_date"]
        count = max(count_by_date.get(trade_date, 0), 1)
        rows.append(
            {
                "trade_date": trade_date,
                "entity_id": "market",
                "entity_name": "A-share committed provider02b universe",
                "entity_type": "market",
                "amount": _format(amount_by_date.get(trade_date, 0.0)),
                "turnover": _format(turnover_by_date.get(trade_date, 0.0) / count),
                "volume": _format(volume_by_date.get(trade_date, 0.0)),
                "net_flow": "",
                "main_force_net_flow": "",
                "large_order_net_flow": "",
                "northbound_net_flow": "",
                "stock_connect_holding": "",
                "margin_balance": "",
                "financing_balance": "",
                "securities_lending_balance": "",
                "margin_eligible_status": "not_available_offline_replay",
                "source_id": "market_turnover_proxy;market_capital_flow",
                "source_provider": row.get("source_provider", "committed_evidence"),
                "provider_timestamp": trade_date,
                "pit_available_date": trade_date,
                "no_lookahead_status": row.get("no_lookahead_status", "passed_current_or_past_only"),
                "data_status": "derived_liquidity_proxy_from_committed_panel",
                "non_actionable_disclaimer": NON_ACTIONABLE,
            }
        )
    return rows


def symbol_event_context(panel_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in panel_rows:
        events: list[tuple[str, str, str]] = []
        if row.get("is_st") == "true":
            events.append(("risk_warning_status", "st_status", "ST risk warning observed in committed panel"))
        if row.get("trading_status") and row.get("trading_status") != "trading":
            events.append(("trading_status", "suspension_status", f"trading_status={row.get('trading_status')}"))
        for event_type, subtype, label in events:
            rows.append(
                {
                    "event_date": row["trade_date"],
                    "trade_date_effective": row["trade_date"],
                    "symbol": row["symbol"],
                    "event_type": event_type,
                    "event_subtype": subtype,
                    "event_title_or_label": label,
                    "event_value": "1",
                    "publication_time": row["trade_date"],
                    "pit_available_date": row["trade_date"],
                    "source_id": "ashare_st_risk_warning;ashare_suspension_resumption",
                    "source_provider": row.get("source_provider", "committed_evidence"),
                    "provider_timestamp": row["trade_date"],
                    "no_lookahead_status": "passed_current_or_past_only",
                    "data_status": "committed_status_context",
                    "research_context_only": "true",
                    "non_actionable_disclaimer": NON_ACTIONABLE,
                }
            )
    return rows


def _float(value: str | None) -> float:
    try:
        return float(value or 0)
    except ValueError:
        return 0.0


def _format(value: float) -> str:
    return f"{value:.10f}"


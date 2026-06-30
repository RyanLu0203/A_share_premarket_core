from __future__ import annotations

from collections import Counter

CATALOG_FIELDS = [
    "source_id",
    "akshare_category",
    "akshare_subcategory",
    "akshare_function_name_if_known",
    "source_description",
    "expected_grain",
    "expected_time_field",
    "expected_symbol_field",
    "expected_primary_keys",
    "expected_update_frequency",
    "point_in_time_risk_level",
    "publication_date_required",
    "survivorship_bias_risk",
    "lookahead_risk",
    "provider_stability_risk",
    "estimated_data_volume",
    "approved_usage",
    "priority_band",
    "allowed_pipeline_stage",
    "storage_policy",
    "commit_policy",
    "audit_requirements",
    "downstream_goal_candidates",
    "implementation_status",
    "notes",
]

SUMMARY_FIELDS = [
    "summary_type",
    "summary_key",
    "source_count",
    "approved_usage_values",
    "priority_bands",
    "notes",
]

ALLOWED_APPROVED_USAGE = {
    "approved_for_provider_health_only",
    "approved_for_research_context",
    "approved_for_regime_label",
    "approved_for_symbol_diagnostics",
    "approved_for_factor_candidate_construction",
    "approved_for_posthoc_factor_evaluation",
    "research_context_only",
    "experimental_requires_review",
    "blocked",
    "future_review_only",
}

PRIORITY_BANDS = {
    "P0_market_regime_core",
    "P1_symbol_context_and_event",
    "P2_macro_fundamental_medium_term",
    "P3_context_only_or_experimental",
    "BLOCKED_boundary_or_pit_risk",
}

REQUIRED_TOP_LEVEL_CATEGORIES = {
    "A_share_core_market_data",
    "index_and_regime_data",
    "sector_industry_concept_data",
    "liquidity_and_capital_flow_data",
    "fundamental_and_corporate_event_data",
    "trading_microstructure_and_event_data",
    "macro_rates_bonds_fx_data",
    "fund_etf_qdii_data",
    "futures_commodities_energy_options_data",
    "news_nlp_policy_alternative_data",
    "blocked_or_future_only",
}


def akshare_source_catalog_rows() -> list[dict[str, str]]:
    rows = [
        _row("ashare_realtime_quotes", "A_share_core_market_data", "A-share real-time quotes", "stock_zh_a_spot_em", "Current A-share quote snapshot for provider health and future liquidity context.", "symbol_snapshot", "snapshot_time", "symbol", "symbol,snapshot_time", "intra_day", "medium", "false", "medium", "medium", "medium", "medium", "approved_for_provider_health_only", "P0_market_regime_core", "provider_health_only", "metadata_or_bounded_snapshot_only", "commit_summary_only", "schema drift, timestamp presence, no trading fields", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", "Do not use as final research evidence without timestamp and replay contract."),
        _row("ashare_daily_ohlcv", "A_share_core_market_data", "A-share historical daily OHLCV", "stock_zh_a_hist", "Daily OHLCV and turnover for approved symbols.", "trade_date_symbol", "trade_date", "symbol", "trade_date,symbol", "daily", "low", "false", "medium", "low", "medium", "high", "approved_for_regime_label", "P0_market_regime_core", "future_data_expansion_review_only", "bounded_normalized_panel_only", "commit_bounded_normalized_summary_only", "schema, duplicate key, PIT date, artifact size", "GOAL-DATA-EXPANSION-RESEARCH-01;GOAL-QUANT-RESEARCH-04", "cataloged_not_fetched", "Primary future AKShare market-regime candidate."),
        _row("ashare_adjusted_prices", "A_share_core_market_data", "A-share adjusted prices", "stock_zh_a_hist", "Forward/backward adjusted daily price views.", "trade_date_symbol", "trade_date", "symbol", "trade_date,symbol,adjustment_mode", "daily", "medium", "false", "medium", "medium", "medium", "high", "future_review_only", "P1_symbol_context_and_event", "future_review_only_after_adjustment_contract", "bounded_normalized_panel_only", "commit_bounded_normalized_summary_only", "adjustment policy and no-lookahead audit", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", "Adjustment semantics must be locked before research use."),
        _row("ashare_premarket_auction", "A_share_core_market_data", "premarket or auction data if available", "stock_zh_a_hist_pre_min_em", "Pre-open minute/auction-like data where exposed by provider.", "timestamp_symbol", "event_timestamp", "symbol", "event_timestamp,symbol", "intra_day", "high", "true", "medium", "high", "high", "very_high", "experimental_requires_review", "P3_context_only_or_experimental", "experimental_metadata_only", "local_only_no_commit_raw", "commit_metadata_only", "timestamp, exchange calendar, size, provider stability", "future_explicit_microstructure_goal", "cataloged_not_fetched", "Not approved for current research evidence."),
        _row("ashare_suspension_resumption", "A_share_core_market_data", "suspension / resumption", "stock_zh_a_stop_em", "Suspended or stopped A-share symbol metadata.", "event_date_symbol", "event_date", "symbol", "event_date,symbol", "daily", "medium", "true", "medium", "medium", "medium", "medium", "approved_for_symbol_diagnostics", "P0_market_regime_core", "future_data_expansion_review_only", "bounded_event_table_only", "commit_bounded_normalized_summary_only", "event date, publication date if available, duplicate key", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", "Useful for tradability and coverage filters."),
        _row("ashare_st_risk_warning", "A_share_core_market_data", "ST / risk warning", "stock_zh_a_st_em", "Special treatment and risk-warning symbol list.", "date_symbol", "as_of_date", "symbol", "as_of_date,symbol", "daily", "medium", "true", "high", "medium", "medium", "medium", "approved_for_symbol_diagnostics", "P0_market_regime_core", "future_data_expansion_review_only", "bounded_status_table_only", "commit_bounded_normalized_summary_only", "as-of date and survivorship audit", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", "Use only with as-of status dates."),
        _row("ashare_trading_calendar", "A_share_core_market_data", "trading calendar", "tool_trade_date_hist_sina", "Exchange trading calendar for alignment.", "trade_date", "trade_date", "", "trade_date", "daily", "low", "false", "low", "low", "medium", "low", "approved_for_regime_label", "P0_market_regime_core", "calendar_contract", "small_reference_table", "commit_allowed_if_bounded", "calendar completeness and monotonic date audit", "GOAL-DATA-EXPANSION-RESEARCH-01;GOAL-QUANT-RESEARCH-04", "cataloged_not_fetched", "Safe core alignment source when bounded."),
        _row("ashare_listing_status", "A_share_core_market_data", "listing status", "stock_info_a_code_name", "Current code/name universe list.", "symbol", "as_of_date", "symbol", "symbol,as_of_date", "daily", "medium", "true", "high", "medium", "medium", "medium", "future_review_only", "P0_market_regime_core", "universe_governance_review", "bounded_metadata_only", "commit_summary_only", "survivorship and as-of date audit", "future_universe_expansion_goal", "cataloged_not_fetched", "Current lists are survivorship-prone unless archived by date."),
        _row("ashare_delisting_status", "A_share_core_market_data", "delisting status", "stock_zh_a_new_em", "Listing and delisting/new-stock metadata where available.", "event_date_symbol", "event_date", "symbol", "event_date,symbol", "daily", "medium", "true", "high", "medium", "medium", "medium", "future_review_only", "P1_symbol_context_and_event", "universe_governance_review", "bounded_event_table_only", "commit_summary_only", "event date and survivorship audit", "future_universe_expansion_goal", "cataloged_not_fetched", "Needs source-specific semantics before use."),
        _row("ashare_name_changes", "A_share_core_market_data", "name changes", "stock_info_change_name", "Symbol name-change history if available.", "event_date_symbol", "event_date", "symbol", "event_date,symbol", "event_driven", "medium", "true", "medium", "medium", "medium", "medium", "research_context_only", "P1_symbol_context_and_event", "context_metadata_only", "bounded_event_table_only", "commit_summary_only", "event date and symbol mapping audit", "future_universe_expansion_goal", "cataloged_not_fetched", "Context only until mapping is audited."),
        _row("market_overview", "A_share_core_market_data", "market overview", "stock_zh_a_spot_em", "Market-wide quote and turnover aggregate from current snapshot.", "snapshot", "snapshot_time", "", "snapshot_time", "intra_day", "medium", "false", "low", "medium", "medium", "medium", "approved_for_provider_health_only", "P0_market_regime_core", "provider_health_only", "metadata_or_bounded_snapshot_only", "commit_summary_only", "timestamp and aggregate definition audit", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", "Snapshot-only unless replayable as-of data exists."),
        _row("broad_market_indices", "index_and_regime_data", "broad market indices", "index_zh_a_hist", "Broad A-share index OHLCV such as CSI 300 or major exchange indices.", "trade_date_index", "trade_date", "index_symbol", "trade_date,index_symbol", "daily", "low", "false", "low", "low", "medium", "low", "approved_for_regime_label", "P0_market_regime_core", "future_data_expansion_review_only", "bounded_index_panel_only", "commit_bounded_normalized_summary_only", "schema, duplicate key, PIT date", "GOAL-DATA-EXPANSION-RESEARCH-01;GOAL-QUANT-RESEARCH-04", "cataloged_not_fetched", "Core regime source."),
        _row("csi_indices", "index_and_regime_data", "CSI indices", "index_zh_a_hist", "CSI index history for market and style regime context.", "trade_date_index", "trade_date", "index_symbol", "trade_date,index_symbol", "daily", "low", "false", "low", "low", "medium", "medium", "approved_for_regime_label", "P0_market_regime_core", "future_data_expansion_review_only", "bounded_index_panel_only", "commit_bounded_normalized_summary_only", "index membership and schema audit", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", "Approved only as index-level context."),
        _row("sse_indices", "index_and_regime_data", "SSE indices", "index_zh_a_hist", "SSE index history.", "trade_date_index", "trade_date", "index_symbol", "trade_date,index_symbol", "daily", "low", "false", "low", "low", "medium", "medium", "approved_for_regime_label", "P0_market_regime_core", "future_data_expansion_review_only", "bounded_index_panel_only", "commit_bounded_normalized_summary_only", "schema and duplicate key audit", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", ""),
        _row("szse_indices", "index_and_regime_data", "SZSE indices", "index_zh_a_hist", "SZSE index history.", "trade_date_index", "trade_date", "index_symbol", "trade_date,index_symbol", "daily", "low", "false", "low", "low", "medium", "medium", "approved_for_regime_label", "P0_market_regime_core", "future_data_expansion_review_only", "bounded_index_panel_only", "commit_bounded_normalized_summary_only", "schema and duplicate key audit", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", ""),
        _row("industry_indices", "index_and_regime_data", "industry indices", "stock_board_industry_hist_em", "Industry board/index historical data.", "trade_date_industry", "trade_date", "industry_code", "trade_date,industry_code", "daily", "medium", "false", "medium", "medium", "medium", "high", "approved_for_regime_label", "P0_market_regime_core", "future_data_expansion_review_only", "bounded_sector_panel_only", "commit_bounded_normalized_summary_only", "classification version and duplicate key audit", "GOAL-DATA-EXPANSION-RESEARCH-01;GOAL-QUANT-RESEARCH-04", "cataloged_not_fetched", "Useful for breadth and dispersion by sector."),
        _row("concept_indices", "index_and_regime_data", "concept indices", "stock_board_concept_hist_em", "Concept board/index historical data.", "trade_date_concept", "trade_date", "concept_code", "trade_date,concept_code", "daily", "medium", "false", "medium", "medium", "medium", "high", "approved_for_research_context", "P0_market_regime_core", "future_data_expansion_review_only", "bounded_sector_panel_only", "commit_bounded_normalized_summary_only", "classification version and concept churn audit", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", "Context until concept taxonomy stability is verified."),
        _row("style_indices", "index_and_regime_data", "style indices where available", "index_zh_a_hist", "Style and size proxy indices where provider exposes symbols.", "trade_date_index", "trade_date", "index_symbol", "trade_date,index_symbol", "daily", "medium", "false", "medium", "medium", "medium", "medium", "research_context_only", "P0_market_regime_core", "future_review_only", "bounded_index_panel_only", "commit_summary_only", "index definition audit", "GOAL-QUANT-RESEARCH-04", "cataloged_not_fetched", "Needs explicit symbol list."),
        _row("index_valuation", "index_and_regime_data", "index valuation", "stock_zh_index_value_csindex", "Index valuation indicators.", "date_index_metric", "date", "index_symbol", "date,index_symbol,metric", "daily", "medium", "true", "medium", "medium", "medium", "medium", "approved_for_research_context", "P2_macro_fundamental_medium_term", "future_review_only", "bounded_metric_table_only", "commit_summary_only", "publication date and vendor lag audit", "future_regime_context_goal", "cataloged_not_fetched", "Medium-term context, not premarket signal by itself."),
        _row("market_breadth_proxy", "index_and_regime_data", "market breadth proxy", "stock_zh_a_spot_em", "Breadth proxy from current or archived universe returns.", "trade_date", "trade_date", "", "trade_date", "daily", "medium", "false", "medium", "medium", "medium", "medium", "approved_for_regime_label", "P0_market_regime_core", "future_data_expansion_review_only", "derived_from_bounded_panel", "commit_derived_summary_only", "constituent availability and no-lookahead audit", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", "Prefer derived from committed daily panel over live snapshot."),
        _row("market_turnover_proxy", "index_and_regime_data", "market turnover proxy", "stock_zh_a_spot_em", "Market turnover/liquidity proxy.", "trade_date", "trade_date", "", "trade_date", "daily", "medium", "false", "medium", "medium", "medium", "medium", "approved_for_regime_label", "P0_market_regime_core", "future_data_expansion_review_only", "derived_from_bounded_panel", "commit_derived_summary_only", "volume/amount schema and no-lookahead audit", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", "Prefer derived from daily committed panel."),
        _row("industry_board_quotes", "sector_industry_concept_data", "industry board quotes", "stock_board_industry_spot_em", "Industry board quote snapshot.", "industry_snapshot", "snapshot_time", "industry_code", "snapshot_time,industry_code", "intra_day", "medium", "false", "medium", "medium", "medium", "medium", "approved_for_provider_health_only", "P1_symbol_context_and_event", "provider_health_only", "metadata_or_bounded_snapshot_only", "commit_summary_only", "timestamp and schema audit", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", "Snapshot only without archive."),
        _row("concept_board_quotes", "sector_industry_concept_data", "concept board quotes", "stock_board_concept_spot_em", "Concept board quote snapshot.", "concept_snapshot", "snapshot_time", "concept_code", "snapshot_time,concept_code", "intra_day", "medium", "false", "medium", "medium", "medium", "medium", "approved_for_provider_health_only", "P1_symbol_context_and_event", "provider_health_only", "metadata_or_bounded_snapshot_only", "commit_summary_only", "timestamp and schema audit", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", "Snapshot only without archive."),
        _row("industry_historical", "sector_industry_concept_data", "industry historical data", "stock_board_industry_hist_em", "Industry board historical OHLCV.", "trade_date_industry", "trade_date", "industry_code", "trade_date,industry_code", "daily", "medium", "false", "medium", "medium", "medium", "high", "approved_for_regime_label", "P0_market_regime_core", "future_data_expansion_review_only", "bounded_sector_panel_only", "commit_bounded_normalized_summary_only", "classification and duplicate key audit", "GOAL-DATA-EXPANSION-RESEARCH-01;GOAL-QUANT-RESEARCH-04", "cataloged_not_fetched", ""),
        _row("concept_historical", "sector_industry_concept_data", "concept historical data", "stock_board_concept_hist_em", "Concept board historical OHLCV.", "trade_date_concept", "trade_date", "concept_code", "trade_date,concept_code", "daily", "medium", "false", "medium", "medium", "medium", "high", "approved_for_research_context", "P1_symbol_context_and_event", "future_data_expansion_review_only", "bounded_sector_panel_only", "commit_bounded_normalized_summary_only", "concept taxonomy churn audit", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", ""),
        _row("industry_capital_flow", "sector_industry_concept_data", "industry capital flow", "stock_fund_flow_industry", "Industry capital flow.", "trade_date_industry", "trade_date", "industry_code", "trade_date,industry_code", "daily", "medium", "true", "medium", "medium", "medium", "medium", "approved_for_research_context", "P1_symbol_context_and_event", "future_review_only", "bounded_flow_table_only", "commit_summary_only", "publication timestamp and schema audit", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", "Use as context until stable history verified."),
        _row("concept_capital_flow", "sector_industry_concept_data", "concept capital flow", "stock_fund_flow_concept", "Concept capital flow.", "trade_date_concept", "trade_date", "concept_code", "trade_date,concept_code", "daily", "medium", "true", "medium", "medium", "medium", "medium", "research_context_only", "P1_symbol_context_and_event", "future_review_only", "bounded_flow_table_only", "commit_summary_only", "publication timestamp and taxonomy audit", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", ""),
        _row("industry_classification", "sector_industry_concept_data", "industry classification", "stock_board_industry_cons_em", "Industry constituent membership.", "as_of_date_symbol_industry", "as_of_date", "symbol", "as_of_date,symbol,industry_code", "daily", "high", "true", "high", "high", "medium", "high", "future_review_only", "P1_symbol_context_and_event", "classification_governance_review", "bounded_membership_table_only", "commit_summary_only", "as-of membership and survivorship audit", "future_universe_or_sector_goal", "cataloged_not_fetched", "Membership history must be PIT-safe before research use."),
        _row("individual_stock_capital_flow", "liquidity_and_capital_flow_data", "individual stock capital flow", "stock_fund_flow_individual", "Individual stock capital flow.", "trade_date_symbol", "trade_date", "symbol", "trade_date,symbol", "daily", "medium", "true", "medium", "medium", "medium", "high", "approved_for_symbol_diagnostics", "P1_symbol_context_and_event", "future_data_expansion_review_only", "bounded_flow_table_only", "commit_summary_only", "timestamp, duplicate key, provider drift", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", "Potential liquidity stress context."),
        _row("main_force_flow", "liquidity_and_capital_flow_data", "main-force flow", "stock_fund_flow_individual", "Main-force flow fields where exposed.", "trade_date_symbol", "trade_date", "symbol", "trade_date,symbol", "daily", "high", "true", "medium", "high", "high", "high", "experimental_requires_review", "P3_context_only_or_experimental", "experimental_metadata_only", "bounded_flow_table_only", "commit_metadata_only", "vendor definition and timestamp audit", "future_liquidity_research_goal", "cataloged_not_fetched", "Vendor-defined flow field; not approved as factor."),
        _row("large_order_flow", "liquidity_and_capital_flow_data", "large-order flow", "stock_fund_flow_big_deal", "Large-order flow where available.", "trade_date_symbol", "trade_date", "symbol", "trade_date,symbol", "daily", "high", "true", "medium", "high", "high", "high", "experimental_requires_review", "P3_context_only_or_experimental", "experimental_metadata_only", "bounded_flow_table_only", "commit_metadata_only", "vendor definition and timestamp audit", "future_liquidity_research_goal", "cataloged_not_fetched", ""),
        _row("market_capital_flow", "liquidity_and_capital_flow_data", "market capital flow", "stock_fund_flow_individual", "Market aggregate flow proxy.", "trade_date", "trade_date", "", "trade_date", "daily", "medium", "true", "low", "medium", "medium", "medium", "approved_for_research_context", "P0_market_regime_core", "future_data_expansion_review_only", "derived_or_bounded_summary", "commit_summary_only", "aggregation and timestamp audit", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", ""),
        _row("northbound_stock_connect_flow", "liquidity_and_capital_flow_data", "northbound / Stock Connect flow", "stock_hsgt_fund_flow_summary_em", "Northbound/Stock Connect fund-flow summary.", "trade_date_market", "trade_date", "market", "trade_date,market", "daily", "medium", "true", "low", "medium", "medium", "medium", "approved_for_regime_label", "P0_market_regime_core", "future_data_expansion_review_only", "bounded_flow_summary_only", "commit_bounded_normalized_summary_only", "publication date and schema audit", "GOAL-DATA-EXPANSION-RESEARCH-01;GOAL-QUANT-RESEARCH-04", "cataloged_not_fetched", "Stable candidate for regime context when available."),
        _row("stock_connect_holdings", "liquidity_and_capital_flow_data", "Stock Connect holdings", "stock_hsgt_hold_stock_em", "Stock Connect holding data.", "date_symbol", "date", "symbol", "date,symbol", "daily", "high", "true", "medium", "medium", "medium", "high", "research_context_only", "P1_symbol_context_and_event", "future_review_only", "bounded_holdings_table_only", "commit_summary_only", "publication date and ownership lag audit", "future_context_goal", "cataloged_not_fetched", ""),
        _row("margin_financing_summary", "liquidity_and_capital_flow_data", "financing and securities lending summary", "stock_margin_sse", "Margin financing/securities lending summary.", "trade_date_market", "trade_date", "market", "trade_date,market", "daily", "medium", "true", "low", "medium", "medium", "medium", "approved_for_regime_label", "P0_market_regime_core", "future_data_expansion_review_only", "bounded_margin_summary_only", "commit_bounded_normalized_summary_only", "publication lag and schema audit", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", "Regime leverage context candidate."),
        _row("margin_financing_detail", "liquidity_and_capital_flow_data", "financing and securities lending detail", "stock_margin_detail_sse", "Margin financing detail by symbol.", "trade_date_symbol", "trade_date", "symbol", "trade_date,symbol", "daily", "medium", "true", "medium", "medium", "medium", "high", "approved_for_symbol_diagnostics", "P1_symbol_context_and_event", "future_review_only", "bounded_margin_detail_only", "commit_summary_only", "publication lag, duplicate key, symbol coverage", "future_context_goal", "cataloged_not_fetched", ""),
        _row("margin_eligible_securities", "liquidity_and_capital_flow_data", "margin-eligible securities", "stock_margin_underlying_info_szse", "Margin-eligible securities list.", "as_of_date_symbol", "as_of_date", "symbol", "as_of_date,symbol", "daily", "medium", "true", "high", "medium", "medium", "medium", "future_review_only", "P1_symbol_context_and_event", "universe_governance_review", "bounded_status_table_only", "commit_summary_only", "as-of date and survivorship audit", "future_context_goal", "cataloged_not_fetched", ""),
        _row("financial_statements", "fundamental_and_corporate_event_data", "financial statements", "stock_financial_report_sina", "Balance sheet, income statement, and cash-flow data families.", "report_period_symbol_statement", "report_period", "symbol", "report_period,symbol,statement_type", "quarterly", "high", "true", "high", "high", "medium", "high", "future_review_only", "P2_macro_fundamental_medium_term", "future_fundamental_research_review", "bounded_fundamental_table_only", "commit_summary_only", "announcement date, restatement, and PIT audit", "future_fundamental_context_goal", "cataloged_not_fetched", "Not used for premarket regime labels without PIT publication dates."),
        _row("valuation_indicators", "fundamental_and_corporate_event_data", "valuation indicators", "stock_a_indicator_lg", "Valuation and key indicators.", "date_symbol_metric", "date", "symbol", "date,symbol,metric", "daily_or_periodic", "medium", "true", "medium", "medium", "medium", "high", "approved_for_research_context", "P2_macro_fundamental_medium_term", "future_review_only", "bounded_metric_table_only", "commit_summary_only", "publication lag and field definition audit", "future_fundamental_context_goal", "cataloged_not_fetched", ""),
        _row("dividend_rights_issue", "fundamental_and_corporate_event_data", "dividend and rights issue", "stock_history_dividend_detail", "Dividend and rights issue events.", "event_date_symbol", "event_date", "symbol", "event_date,symbol,event_type", "event_driven", "medium", "true", "medium", "medium", "medium", "medium", "research_context_only", "P1_symbol_context_and_event", "future_event_context_review", "bounded_event_table_only", "commit_summary_only", "ex-date, announcement date, duplicate key", "future_event_context_goal", "cataloged_not_fetched", ""),
        _row("shareholding_structure", "fundamental_and_corporate_event_data", "shareholding structure", "stock_zh_a_gbjg_em", "Share capital and holding structure.", "report_period_symbol", "report_period", "symbol", "report_period,symbol", "quarterly", "high", "true", "medium", "high", "medium", "medium", "future_review_only", "P2_macro_fundamental_medium_term", "future_review_only", "bounded_fundamental_table_only", "commit_summary_only", "report date and publication date audit", "future_fundamental_context_goal", "cataloged_not_fetched", ""),
        _row("top_shareholders", "fundamental_and_corporate_event_data", "top shareholders", "stock_gdfx_top_10_em", "Top shareholder table.", "report_period_symbol_holder", "report_period", "symbol", "report_period,symbol,holder_name", "quarterly", "high", "true", "medium", "high", "medium", "high", "future_review_only", "P2_macro_fundamental_medium_term", "future_review_only", "bounded_fundamental_table_only", "commit_summary_only", "publication date and entity normalization audit", "future_fundamental_context_goal", "cataloged_not_fetched", ""),
        _row("shareholder_count", "fundamental_and_corporate_event_data", "shareholder count", "stock_zh_a_gdhs_detail_em", "Shareholder count history.", "report_date_symbol", "report_date", "symbol", "report_date,symbol", "periodic", "medium", "true", "medium", "medium", "medium", "medium", "approved_for_symbol_diagnostics", "P1_symbol_context_and_event", "future_event_context_review", "bounded_event_table_only", "commit_summary_only", "publication date and duplicate key audit", "future_context_goal", "cataloged_not_fetched", ""),
        _row("insider_holding_changes", "fundamental_and_corporate_event_data", "insider / executive holding changes", "stock_hold_management_detail_em", "Executive or insider holding changes.", "event_date_symbol_person", "event_date", "symbol", "event_date,symbol,person", "event_driven", "high", "true", "medium", "high", "medium", "medium", "research_context_only", "P1_symbol_context_and_event", "future_event_context_review", "bounded_event_table_only", "commit_summary_only", "publication date and entity normalization audit", "future_event_context_goal", "cataloged_not_fetched", ""),
        _row("pledges_goodwill_repurchase_unlock", "fundamental_and_corporate_event_data", "pledges / goodwill / repurchase / restricted share unlock", "stock_restricted_release_queue_em", "Corporate event families for pledges, goodwill, repurchase, and unlocks.", "event_date_symbol_event", "event_date", "symbol", "event_date,symbol,event_type", "event_driven", "high", "true", "medium", "high", "medium", "medium", "research_context_only", "P1_symbol_context_and_event", "future_event_context_review", "bounded_event_table_only", "commit_summary_only", "publication date and event taxonomy audit", "future_event_context_goal", "cataloged_not_fetched", ""),
        _row("earnings_calendar", "fundamental_and_corporate_event_data", "earnings forecast / bulletin / report calendar", "stock_yjbb_em", "Earnings report calendar and summary families.", "event_date_symbol", "event_date", "symbol", "event_date,symbol", "event_driven", "high", "true", "medium", "high", "medium", "medium", "approved_for_symbol_diagnostics", "P1_symbol_context_and_event", "future_event_context_review", "bounded_event_table_only", "commit_summary_only", "calendar publication date and PIT audit", "future_event_context_goal", "cataloged_not_fetched", ""),
        _row("company_announcements", "fundamental_and_corporate_event_data", "company announcements / major contracts / lawsuits / guarantees / research visits", "stock_zh_a_disclosure_report_cninfo", "Announcement metadata and corporate-event text references.", "publication_time_symbol_announcement", "publication_time", "symbol", "publication_time,symbol,announcement_id", "event_driven", "high", "true", "medium", "high", "medium", "very_high", "research_context_only", "P1_symbol_context_and_event", "metadata_only_no_full_text", "metadata_only_no_raw_text_commit", "commit_metadata_summary_only", "publication timestamp, full-text exclusion, duplicate key", "future_event_context_goal", "cataloged_not_fetched", "Full announcement text remains out of repo."),
        _row("limit_up_down", "trading_microstructure_and_event_data", "limit-up / limit-down related data", "stock_zt_pool_em", "Limit-up/down event pools where available.", "trade_date_symbol_event", "trade_date", "symbol", "trade_date,symbol,event_type", "daily", "medium", "false", "medium", "medium", "medium", "medium", "approved_for_symbol_diagnostics", "P1_symbol_context_and_event", "future_event_context_review", "bounded_event_table_only", "commit_summary_only", "event definition and duplicate key audit", "GOAL-DATA-EXPANSION-RESEARCH-01", "cataloged_not_fetched", "Tradability context only."),
        _row("dragon_tiger_list", "trading_microstructure_and_event_data", "Dragon Tiger List", "stock_lhb_detail_em", "Dragon Tiger List event details.", "trade_date_symbol", "trade_date", "symbol", "trade_date,symbol", "daily", "medium", "false", "medium", "medium", "medium", "high", "approved_for_symbol_diagnostics", "P1_symbol_context_and_event", "future_event_context_review", "bounded_event_table_only", "commit_summary_only", "schema, event date, duplicate key", "future_event_context_goal", "cataloged_not_fetched", ""),
        _row("block_trades", "trading_microstructure_and_event_data", "block trades", "stock_dzjy_detail_em", "Block trade details.", "trade_date_symbol_trade", "trade_date", "symbol", "trade_date,symbol,trade_id", "daily", "medium", "false", "medium", "medium", "medium", "high", "approved_for_symbol_diagnostics", "P1_symbol_context_and_event", "future_event_context_review", "bounded_event_table_only", "commit_summary_only", "schema, trade id, duplicate key", "future_event_context_goal", "cataloged_not_fetched", ""),
        _row("new_high_low_heat_attention", "trading_microstructure_and_event_data", "new highs / new lows / heat / attention indices", "stock_hot_rank_em", "Market heat and attention style datasets.", "timestamp_symbol", "timestamp", "symbol", "timestamp,symbol,source_metric", "intra_day_or_daily", "high", "true", "medium", "high", "high", "high", "experimental_requires_review", "P3_context_only_or_experimental", "experimental_metadata_only", "metadata_only", "commit_metadata_only", "timestamp, source definition, no sentiment leakage", "future_context_goal", "cataloged_not_fetched", "Not approved as factor input."),
        _row("chip_distribution", "trading_microstructure_and_event_data", "chip distribution if available", "stock_cyq_em", "Chip distribution style provider metric.", "trade_date_symbol", "trade_date", "symbol", "trade_date,symbol", "daily", "high", "true", "medium", "high", "high", "high", "experimental_requires_review", "P3_context_only_or_experimental", "experimental_metadata_only", "metadata_only", "commit_metadata_only", "vendor definition and PIT audit", "future_context_goal", "cataloged_not_fetched", "Experimental only."),
        _row("analyst_ratings_reports", "trading_microstructure_and_event_data", "analyst ratings / research reports", "stock_rank_forecast_cninfo", "Analyst ratings or research-report metadata.", "publication_time_symbol_report", "publication_time", "symbol", "publication_time,symbol,report_id", "event_driven", "high", "true", "medium", "high", "medium", "high", "research_context_only", "P3_context_only_or_experimental", "metadata_only_no_full_text", "metadata_only_no_raw_text_commit", "commit_metadata_summary_only", "publication timestamp and full-text exclusion audit", "future_context_goal", "cataloged_not_fetched", "Context only."),
        _row("macro_china_indicators", "macro_rates_bonds_fx_data", "macro China indicators / PMI / CPI / PPI / money supply / social financing", "macro_china_cpi", "China macro indicator families.", "release_date_indicator", "release_date", "", "release_date,indicator", "monthly", "medium", "true", "low", "medium", "medium", "low", "approved_for_research_context", "P2_macro_fundamental_medium_term", "future_macro_context_review", "bounded_macro_table_only", "commit_summary_only", "release date and revision audit", "future_regime_context_goal", "cataloged_not_fetched", "Medium-term context only."),
        _row("interest_rates_shibor", "macro_rates_bonds_fx_data", "interest rates / SHIBOR / interbank rates", "rate_interbank", "Rates and SHIBOR style datasets.", "date_rate", "date", "", "date,rate_name", "daily", "medium", "true", "low", "medium", "medium", "medium", "approved_for_research_context", "P2_macro_fundamental_medium_term", "future_macro_context_review", "bounded_rate_table_only", "commit_summary_only", "release timestamp and schema audit", "future_regime_context_goal", "cataloged_not_fetched", ""),
        _row("treasury_yield_bond_market", "macro_rates_bonds_fx_data", "treasury yield / bond market data", "bond_zh_us_rate", "Treasury yield and bond market proxy data.", "date_curve", "date", "", "date,curve_name,maturity", "daily", "medium", "true", "low", "medium", "medium", "medium", "approved_for_research_context", "P2_macro_fundamental_medium_term", "future_macro_context_review", "bounded_rate_table_only", "commit_summary_only", "release timestamp and curve definition audit", "future_regime_context_goal", "cataloged_not_fetched", ""),
        _row("rmb_fx_usd_proxy", "macro_rates_bonds_fx_data", "RMB FX / USD index proxy", "currency_boc_sina", "RMB FX and USD proxy data.", "date_pair", "date", "fx_pair", "date,fx_pair", "daily", "medium", "true", "low", "medium", "medium", "medium", "approved_for_research_context", "P2_macro_fundamental_medium_term", "future_macro_context_review", "bounded_fx_table_only", "commit_summary_only", "timestamp and source definition audit", "future_regime_context_goal", "cataloged_not_fetched", ""),
        _row("public_funds", "fund_etf_qdii_data", "public fund data", "fund_open_fund_info_em", "Public fund metadata and NAV families.", "date_fund", "date", "fund_code", "date,fund_code", "daily", "medium", "true", "medium", "medium", "medium", "high", "research_context_only", "P2_macro_fundamental_medium_term", "future_context_review", "bounded_fund_table_only", "commit_summary_only", "publication date and schema audit", "future_context_goal", "cataloged_not_fetched", ""),
        _row("etf_data", "fund_etf_qdii_data", "ETF data", "fund_etf_hist_em", "ETF history for market context.", "date_fund", "date", "fund_code", "date,fund_code", "daily", "medium", "false", "medium", "medium", "medium", "high", "approved_for_research_context", "P2_macro_fundamental_medium_term", "future_context_review", "bounded_fund_table_only", "commit_summary_only", "schema and duplicate key audit", "future_regime_context_goal", "cataloged_not_fetched", ""),
        _row("fund_holdings_flow_qdii", "fund_etf_qdii_data", "fund holdings / fund flow / QDII", "fund_portfolio_hold_em", "Fund holdings, flows, and QDII context.", "report_period_fund_symbol", "report_period", "fund_code", "report_period,fund_code,holding_symbol", "periodic", "high", "true", "medium", "high", "medium", "high", "research_context_only", "P2_macro_fundamental_medium_term", "future_context_review", "bounded_fund_table_only", "commit_summary_only", "publication date and holdings lag audit", "future_context_goal", "cataloged_not_fetched", ""),
        _row("commodity_futures", "futures_commodities_energy_options_data", "commodity futures", "futures_zh_daily_sina", "Commodity futures history.", "date_contract", "date", "contract", "date,contract", "daily", "medium", "false", "low", "medium", "medium", "high", "approved_for_research_context", "P2_macro_fundamental_medium_term", "future_macro_context_review", "bounded_futures_table_only", "commit_summary_only", "contract mapping and roll policy audit", "future_regime_context_goal", "cataloged_not_fetched", ""),
        _row("financial_futures_options", "futures_commodities_energy_options_data", "financial futures / options", "futures_hist_daily_cffex", "Financial futures and options datasets.", "date_contract", "date", "contract", "date,contract", "daily", "high", "false", "low", "medium", "medium", "high", "future_review_only", "P2_macro_fundamental_medium_term", "future_review_only", "bounded_derivative_table_only", "commit_summary_only", "contract, expiry, and roll policy audit", "future_regime_context_goal", "cataloged_not_fetched", "Needs derivative contract governance before use."),
        _row("energy_gold_copper_oil_coal_iron_ore", "futures_commodities_energy_options_data", "energy / gold / copper / oil / coal / iron ore proxies", "futures_global_hist_em", "Commodity and energy proxy families.", "date_proxy", "date", "proxy_symbol", "date,proxy_symbol", "daily", "medium", "false", "low", "medium", "medium", "medium", "approved_for_research_context", "P2_macro_fundamental_medium_term", "future_macro_context_review", "bounded_proxy_table_only", "commit_summary_only", "proxy definition and timestamp audit", "future_regime_context_goal", "cataloged_not_fetched", ""),
        _row("stock_news", "news_nlp_policy_alternative_data", "individual stock news", "stock_news_em", "Individual stock news metadata.", "publication_time_symbol_article", "publication_time", "symbol", "publication_time,symbol,article_id", "event_driven", "high", "true", "medium", "high", "high", "very_high", "research_context_only", "P3_context_only_or_experimental", "metadata_only_no_full_text", "metadata_only_no_raw_text_commit", "commit_metadata_summary_only", "publication timestamp, full-text exclusion, source terms", "future_context_goal", "cataloged_not_fetched", "No raw full news text in repo."),
        _row("financial_news_policy", "news_nlp_policy_alternative_data", "financial news / policy uncertainty", "news_economic_baidu", "Financial news and policy context metadata.", "publication_time_topic", "publication_time", "", "publication_time,source,article_id", "event_driven", "high", "true", "low", "high", "high", "very_high", "research_context_only", "P3_context_only_or_experimental", "metadata_only_no_full_text", "metadata_only_no_raw_text_commit", "commit_metadata_summary_only", "publication timestamp and no full text audit", "future_context_goal", "cataloged_not_fetched", ""),
        _row("nlp_interfaces", "news_nlp_policy_alternative_data", "NLP interfaces", "", "Sentiment or NLP-derived interfaces.", "model_output", "publication_time", "symbol_or_topic", "publication_time,symbol_or_topic,model_id", "event_driven", "very_high", "true", "medium", "very_high", "high", "very_high", "blocked", "BLOCKED_boundary_or_pit_risk", "blocked", "not_allowed", "do_not_commit", "PIT, model provenance, and sentiment validation unavailable", "none", "blocked", "Unverified sentiment features are blocked."),
        _row("alternative_migration_high_frequency", "news_nlp_policy_alternative_data", "alternative data / migration data / high-frequency data", "", "Alternative, migration, and unbounded high-frequency raw data.", "varies", "timestamp", "varies", "varies", "varies", "very_high", "true", "high", "very_high", "high", "very_high", "blocked", "BLOCKED_boundary_or_pit_risk", "blocked", "not_allowed", "do_not_commit", "PIT and volume risks exceed current boundary", "none", "blocked", "Blocked unless a future explicit governed goal narrows scope."),
        _row("trading_broker_live_execution", "blocked_or_future_only", "real trading interfaces / broker/live trading interfaces", "", "Any trading, broker, order, account, or live execution interface.", "not_applicable", "", "", "", "not_applicable", "very_high", "true", "high", "very_high", "high", "varies", "blocked", "BLOCKED_boundary_or_pit_risk", "blocked", "not_allowed", "do_not_commit", "project boundary lock audit", "none", "blocked", "Explicitly outside project boundary."),
        _row("crypto_unapproved", "blocked_or_future_only", "crypto data unless explicitly approved for macro context", "crypto_js_spot", "Crypto data families.", "date_asset", "date", "asset", "date,asset", "varies", "high", "true", "medium", "high", "medium", "high", "future_review_only", "BLOCKED_boundary_or_pit_risk", "future_review_only", "not_allowed_without_macro_context_review", "do_not_commit", "macro relevance and boundary review", "none", "future_review_only", "Not approved except possible future macro context review."),
        _row("sources_without_pit_control", "blocked_or_future_only", "sources lacking timestamp or publication-date control", "", "Any source without usable date/time or publication-date controls.", "varies", "", "", "", "varies", "very_high", "true", "high", "very_high", "varies", "varies", "blocked", "BLOCKED_boundary_or_pit_risk", "blocked", "not_allowed", "do_not_commit", "PIT control missing", "none", "blocked", "Blocked by no-lookahead policy."),
    ]
    return rows


def akshare_source_catalog_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    summary: list[dict[str, str]] = []
    for summary_type, field in [
        ("category", "akshare_category"),
        ("approved_usage", "approved_usage"),
        ("priority_band", "priority_band"),
    ]:
        counts = Counter(row[field] for row in rows)
        for key, count in sorted(counts.items()):
            matching = [row for row in rows if row[field] == key]
            summary.append(
                {
                    "summary_type": summary_type,
                    "summary_key": key,
                    "source_count": str(count),
                    "approved_usage_values": ";".join(sorted({row["approved_usage"] for row in matching})),
                    "priority_bands": ";".join(sorted({row["priority_band"] for row in matching})),
                    "notes": "metadata_only_catalog_no_live_fetch",
                }
            )
    return summary


def source_catalog_config() -> dict[str, object]:
    rows = akshare_source_catalog_rows()
    return {
        "catalog_id": "goal_architecture_refactor03_akshare_source_catalog",
        "mode": "metadata_only_no_live_fetch",
        "allowed_approved_usage_values": sorted(ALLOWED_APPROVED_USAGE),
        "priority_bands": sorted(PRIORITY_BANDS),
        "required_top_level_categories": sorted(REQUIRED_TOP_LEVEL_CATEGORIES),
        "source_count": len(rows),
        "sources": rows,
        "policies": {
            "network_fetch": "forbidden_by_this_goal",
            "full_live_dataset_fetch": "forbidden_by_this_goal",
            "raw_payload_commit": "forbidden",
            "local_lake_write": "forbidden",
            "pit_control": "required_before_research_use",
            "next_goal_scope": "GOAL-DATA-EXPANSION-RESEARCH-01 may request only approved P0/P1 market-regime sources",
        },
    }


def _row(
    source_id: str,
    category: str,
    subcategory: str,
    function_name: str,
    description: str,
    grain: str,
    time_field: str,
    symbol_field: str,
    primary_keys: str,
    update_frequency: str,
    pit_risk: str,
    publication_required: str,
    survivorship_risk: str,
    lookahead_risk: str,
    stability_risk: str,
    volume: str,
    approved_usage: str,
    priority_band: str,
    stage: str,
    storage_policy: str,
    commit_policy: str,
    audit_requirements: str,
    downstream: str,
    implementation_status: str,
    notes: str,
) -> dict[str, str]:
    return {
        "source_id": source_id,
        "akshare_category": category,
        "akshare_subcategory": subcategory,
        "akshare_function_name_if_known": function_name,
        "source_description": description,
        "expected_grain": grain,
        "expected_time_field": time_field,
        "expected_symbol_field": symbol_field,
        "expected_primary_keys": primary_keys,
        "expected_update_frequency": update_frequency,
        "point_in_time_risk_level": pit_risk,
        "publication_date_required": publication_required,
        "survivorship_bias_risk": survivorship_risk,
        "lookahead_risk": lookahead_risk,
        "provider_stability_risk": stability_risk,
        "estimated_data_volume": volume,
        "approved_usage": approved_usage,
        "priority_band": priority_band,
        "allowed_pipeline_stage": stage,
        "storage_policy": storage_policy,
        "commit_policy": commit_policy,
        "audit_requirements": audit_requirements,
        "downstream_goal_candidates": downstream,
        "implementation_status": implementation_status,
        "notes": notes,
    }

import { fireEvent, render, screen } from "@testing-library/react";

import { AbstentionCenterPage } from "@/views/AbstentionCenterPage";
import { CommandCenterPage } from "@/views/CommandCenterPage";
import { ConstraintMonitorPage } from "@/views/ConstraintMonitorPage";
import { PortfolioOverviewPage } from "@/views/PortfolioOverviewPage";
import { PositionBandsPage } from "@/views/PositionBandsPage";
import { QuantWorkspacePage } from "@/views/QuantWorkspacePage";
import { RiskMonitorPage } from "@/views/RiskMonitorPage";
import { SnapshotHistoryPage } from "@/views/SnapshotHistoryPage";
import { StockDetailPage } from "@/views/StockDetailPage";
import { StockExplorerPage } from "@/views/StockExplorerPage";
import { DataQualityPage, ProvenancePage } from "@/views/SystemEvidencePage";
import { WatchlistPage } from "@/views/WatchlistPage";

vi.mock("@/components/EvidenceCharts", () => ({
  AllocationTreemap: () => <div role="img" aria-label="Holdings allocation treemap" />,
  CorrelationHeatmap: () => <div role="img" aria-label="Display-only correlation heatmap" />,
  PolicyRiskChart: () => <div role="img" aria-label="Policy risk comparison" />,
  RiskContributionChart: () => <div role="img" aria-label="Largest component risk contributions" />,
}));

const evidenceUnavailable = {
  value: null,
  asof_date: null,
  source: null,
  availability: "UNAVAILABLE" as const,
  quality_status: "NO_COMMITTED_EVIDENCE",
  reason: "field is not present in committed evidence",
};

const status = {
  readiness_state: "BLOCKED",
  freshness_code: "STALE_SOURCE_DATA",
  target_trading_date: "2026-07-09",
  expected_previous_trading_date: "2026-07-08",
  latest_available_data_date: "2026-06-30",
  data_cutoff: "2026-07-08",
  execution_mode: "daily_operational",
};

describe("functional workspace pages", () => {
  it("puts freshness before command-center metrics", () => {
    render(<CommandCenterPage data={{status, kpis: {gross_exposure: 1, cash_weight: 0, portfolio_volatility: 0.21, beta: 1.16, constraint_breaches: 3, abstentions: 12, portfolio_risk_state: "normal_risk_review_only", snapshot_timestamp: "2026-07-01T08:30:00+08:00"}, position_distribution: {WITHIN_BAND: 29, ABSTAIN: 12}, top_risk_contributors: [], warnings: [], exposure: {}, risk_history: []}} />);
    expect(screen.getByRole("alert")).toHaveTextContent("STALE_SOURCE_DATA");
    expect(screen.getByText("Gross exposure")).toBeVisible();
    expect(screen.getAllByText("12").length).toBeGreaterThan(0);
  });

  it("persists watchlist additions and supports removal", () => {
    render(<WatchlistPage seed={["000333.SZ"]} stocks={[{symbol: "000333.SZ", display_name: "Midea Group", exchange: {value: "Shenzhen"}, board: {value: "Main"}, industry: {value: "Home Appliances"}, latest_price: {value: 72.1}, price_change: {value: 0.01}, market_cap: evidenceUnavailable, pe_ttm: {value: 15}, pb: {value: 2}, current_weight: 0.02, band_min: 0.01, band_max: 0.03, band_status: "WITHIN_BAND", risk_contribution: 0.02, confidence: 1, abstain: false, provider_quality: "accepted"}, {symbol: "002475.SZ", display_name: "Luxshare Precision", exchange: {value: "Shenzhen"}, board: {value: "Main"}, industry: {value: "Electronics"}, latest_price: {value: 30}, price_change: {value: -0.01}, market_cap: evidenceUnavailable, pe_ttm: {value: 20}, pb: {value: 3}, current_weight: 0.02, band_min: 0.01, band_max: 0.03, band_status: "WITHIN_BAND", risk_contribution: 0.02, confidence: 1, abstain: false, provider_quality: "accepted"}]} />);
    expect(screen.getByText("Market cap")).toBeVisible();
    expect(screen.getByText("Band min")).toBeVisible();
    expect(screen.getByText("Abstain")).toBeVisible();
    fireEvent.change(screen.getByLabelText("Add symbol"), {target: {value: "002475.SZ"}});
    fireEvent.click(screen.getByRole("button", {name: "Add to watchlist"}));
    expect(screen.getByText("Luxshare Precision")).toBeVisible();
    fireEvent.click(screen.getByRole("button", {name: "Remove 000333.SZ"}));
    expect(screen.queryByText("Midea Group")).not.toBeInTheDocument();
  });

  it("filters stock explorer evidence by governed categories", () => {
    render(<StockExplorerPage data={{count: 2, rows: [
      {symbol: "000333.SZ", display_name: "Midea Group", exchange: {value: "Shenzhen"}, board: {value: "Main"}, industry: {value: "Home Appliances"}, latest_price: {value: 72.1}, price_change: {value: 0.01}, market_cap: evidenceUnavailable, pe_ttm: {value: 15}, pb: {value: 2}, current_weight: 0.02, band_status: "WITHIN_BAND", abstain: false, provider_quality: "accepted"},
      {symbol: "000157.SZ", display_name: "Zoomlion", exchange: {value: "Shenzhen"}, board: {value: "Main"}, industry: {value: "Machinery"}, latest_price: {value: 7.1}, price_change: {value: -0.01}, market_cap: evidenceUnavailable, pe_ttm: evidenceUnavailable, pb: evidenceUnavailable, current_weight: 0, band_status: "ABSTAIN", abstain: true, provider_quality: "quarantined"},
    ]}} />);
    fireEvent.change(screen.getByLabelText("Band status filter"), {target: {value: "ABSTAIN"}});
    expect(screen.getByText("Zoomlion")).toBeVisible();
    expect(screen.queryByText("Midea Group")).not.toBeInTheDocument();
    expect(screen.getByLabelText("Provider quality filter")).toBeVisible();
  });

  it("shows stock tabs and evidence-backed unavailable fundamentals", () => {
    render(<StockDetailPage detail={{symbol: "000333.SZ", display_name: "Midea Group", company_name: {value: "Midea Group", availability: "AVAILABLE"}, exchange: {value: "Shenzhen", availability: "AVAILABLE"}, board: {value: "Main", availability: "AVAILABLE"}, industry: {value: "Home Appliances", availability: "AVAILABLE"}, latest_price: {value: 72.1, asof_date: "2026-06-30", source: "akshare_sina", availability: "AVAILABLE"}, price_change: {value: 0.01, availability: "AVAILABLE"}, current_weight: 0.02, band_min: 0.01, band_max: 0.03, band_status: "WITHIN_BAND", confidence: 1, abstain: false, provider_lineage: ["akshare_sina", "baostock"], freshness_state: "FRESH_T_MINUS_ONE_DATA", listing_date: evidenceUnavailable, st_status: evidenceUnavailable, trading_status: evidenceUnavailable, total_shares: evidenceUnavailable, float_shares: evidenceUnavailable, market_cap: evidenceUnavailable, float_market_cap: evidenceUnavailable, free_float_market_cap: evidenceUnavailable}} market={{candles: [], candlestick_latest_date: "2026-05-21", latest_close: {value: 72.1}, latest_return: {value: 0.01}}} fundamentals={{pe_ttm: {value: 15, availability: "AVAILABLE", asof_date: "2026-05-21", source: "baostock", quality_status: "evidence", reason: null}, pb: {value: 2, availability: "AVAILABLE", asof_date: "2026-05-21", source: "baostock", quality_status: "evidence", reason: null}, revenue: evidenceUnavailable, roe: evidenceUnavailable}} risk={{quarantine_state: "NOT_QUARANTINED"}} position={{band_status: "WITHIN_BAND", abstain: false, constraints: []}} />);
    expect(screen.getByRole("tab", {name: "Fundamentals"})).toBeVisible();
    const fundamentalsTab = screen.getByRole("tab", {name: "Fundamentals"});
    fireEvent.mouseDown(fundamentalsTab, {button: 0, ctrlKey: false});
    expect(screen.getAllByText("UNAVAILABLE").length).toBeGreaterThan(0);
    expect(screen.getByText("Revenue")).toBeVisible();
  });

  it("renders governed bands, fail-closed constraints, and abstention reasons", () => {
    const {rerender} = render(<PositionBandsPage data={{rows: [{symbol: "000157.SZ", current_weight: 0.02, acceptable_band_min: 0.01, acceptable_band_max: 0.03, reference_policy_weight: 0.02, band_status: "ABSTAIN", confidence: 0.82, constraint_breach: "none", abstain: true, provider_quality: "quarantined"}], distribution: {ABSTAIN: 1}, allowed_states: ["BELOW_BAND", "WITHIN_BAND", "ABOVE_BAND", "ABSTAIN", "INSUFFICIENT_DATA"]}} />);
    expect(screen.getAllByText("ABSTAIN").length).toBeGreaterThan(0);
    rerender(<ConstraintMonitorPage data={{constraint_count: 13, substantive_constraint_count: 7, summary: [{constraint_id: "liquidity_limit", current_value: null, threshold: "available", breach: true, breach_count: 1, severity: "high", evidence_availability: ["unavailable_no_volume_or_amount_field"], fail_closed: true, state: "FAIL_CLOSED", substantive: true}], details: []}} />);
    expect(screen.getAllByText("FAIL_CLOSED").length).toBeGreaterThan(0);
    rerender(<AbstentionCenterPage data={{count: 1, reason_distribution: {unresolved_provider_discrepancy: 1}, rows: [{symbol: "000157.SZ", abstain: true, confidence: 0.82, provider_quality: "quarantined", regime_state: "unavailable", reason_codes: ["unresolved_provider_discrepancy"]}]}} />);
    expect(screen.getAllByText("unresolved_provider_discrepancy").length).toBeGreaterThan(0);
  });

  it("selects immutable snapshots and keeps quant pages locked", () => {
    const select = vi.fn();
    const {rerender} = render(<SnapshotHistoryPage data={{latest: "2026-07-01", snapshots: [{snapshot_date: "2026-07-01", execution_mode: "deterministic_replay", execution_time: "2026-07-01T08:30:00+08:00", target_trading_date: "2026-07-01", data_cutoff: "2026-06-30", latest_available_data_date: "2026-06-30", freshness_code: "FRESH_T_MINUS_ONE_DATA", readiness_state: "READY_WITH_WARNINGS", config_hash: "abc", snapshot_integrity: "VERIFIED"}]}} onSelect={select} />);
    fireEvent.click(screen.getByRole("button", {name: "Open snapshot 2026-07-01"}));
    expect(select).toHaveBeenCalledWith("2026-07-01");
    rerender(<QuantWorkspacePage pageId={17} capabilities={{ready_factor_count: 0, recommendation_tiering_state: "locked_future", issue_10_state: "locked", candidate_readiness: {evaluated: 120, ready: 0, conditionally_useful: 0, not_ready: 120}, quant04_refined_factors: {evaluated: 30, ready: 0, conditionally_useful: 21, not_ready: 9}, factor_table_contract: [], candidate_rows: []}} />);
    expect(screen.getByText("Issue #10: locked")).toBeVisible();
    expect(screen.getByText("ready_factor_count = 0")).toBeVisible();
  });

  it("renders required portfolio and risk evidence surfaces", () => {
    const position = {symbol: "000333.SZ", display_name: "Midea Group", current_weight: 0.02, reference_policy_weight: 0.02, risk_contribution: 0.03, band_status: "WITHIN_BAND", confidence: 1};
    const {rerender} = render(<PortfolioOverviewPage data={{portfolio_mode: "RESEARCH REFERENCE PORTFOLIO", risk_state: {gross_exposure: 1, cash_weight: 0, portfolio_volatility: 0.2, beta_to_csi300: 1, max_drawdown: -0.1, effective_number_of_positions: 20}, exposure: {}, positions: [position], correlation_matrix: {symbols: [], values: []}, clusters: []}} />);
    expect(screen.getByRole("img", {name: "Holdings allocation treemap"})).toBeVisible();
    expect(screen.getByRole("img", {name: "Largest component risk contributions"})).toBeVisible();
    rerender(<RiskMonitorPage data={{state: {portfolio_volatility: 0.2, ewma_volatility: 0.2, beta_to_csi300: 1, average_correlation: 0.3, cvar_95_daily: -0.02, max_drawdown: -0.1, effective_number_of_positions: 20, cluster_concentration: 0.3}, contributions: [position], policy_comparison: [], policy_catalog: [], clusters: [], history: [{trading_date: "2026-07-01", predecessor_risk_state: "normal"}]}} />);
    expect(screen.getByText("Max drawdown")).toBeVisible();
    expect(screen.getByText("Effective positions")).toBeVisible();
    expect(screen.getByText("Risk-state history")).toBeVisible();
    expect(screen.getByRole("heading", {name: "Cluster concentration"})).toBeVisible();
  });

  it("shows locked factor-correlation structure and candidate failure evidence", () => {
    const capabilities = {ready_factor_count: 0, recommendation_tiering_state: "locked_future", issue_10_state: "locked", candidate_readiness: {evaluated: 1, ready: 0, conditionally_useful: 0, not_ready: 1}, quant04_refined_factors: {evaluated: 1, ready: 0, conditionally_useful: 0, not_ready: 1}, factor_table_contract: [], candidate_rows: [{candidate_id: "candidate-a", readiness_status: "not_ready", decision_summary: "not_ready_failed:sign_stability"}]};
    const {rerender} = render(<QuantWorkspacePage pageId={15} capabilities={capabilities} />);
    expect(screen.getByText("Correlation heatmap")).toBeVisible();
    expect(screen.getByText("Cluster tree")).toBeVisible();
    expect(screen.getByText("Redundancy diagnostics")).toBeVisible();
    rerender(<QuantWorkspacePage pageId={16} capabilities={capabilities} />);
    expect(screen.getByText("not_ready_failed:sign_stability")).toBeVisible();
  });

  it("surfaces freshness and provenance fields without inventing values", () => {
    const qualityStatus = {...status, readiness_state: "READY_WITH_WARNINGS"};
    const {rerender} = render(<DataQualityPage data={{status: qualityStatus, readiness_checks: [], quality_summary: [], quarantine: []}} />);
    expect(screen.getByText("Expected T-1")).toBeVisible();
    expect(screen.getByText("Readiness state definitions")).toBeVisible();
    rerender(<ProvenancePage data={{snapshot: {snapshot_date: "2026-07-01", code_commit: "abc"}, audit_status: "PASS", pit_status: "passed", config_hash: "config-sha", source_lineage: ["source-a"], provider_lineage: ["provider-a"], goal_lineage: ["goal-a"], checksums: {}, workflow_state: {status: "implemented"}}} />);
    expect(screen.getByText("Source lineage")).toBeVisible();
    expect(screen.getByText("config-sha")).toBeVisible();
  });
});

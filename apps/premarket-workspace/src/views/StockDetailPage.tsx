"use client";

import * as Tabs from "@radix-ui/react-tabs";

import { DenseTable } from "@/components/DenseTable";
import { PriceVolumeChart } from "@/components/PriceVolumeChart";
import { StockSymbolSearch, type StockSearchItem } from "@/components/StockSymbolSearch";
import { PageHeader, Panel, StatusBadge } from "@/components/ui";
import { UnavailableValue } from "@/components/UnavailableValue";
import { formatNumber, formatPercent } from "@/lib/format";
import type { CandleRow, ProviderDiscrepancyMarker } from "@/lib/api/contracts";
import type { EvidenceValue, WorkspaceStatus } from "@/lib/types";

type Detail = Record<string, unknown> & {symbol: string; display_name: string};

interface StockDetailPageProps {
  detail: Detail;
  market: Record<string, unknown>;
  fundamentals: Record<string, unknown>;
  risk: Record<string, unknown>;
  position: Record<string, unknown>;
  stocks?: StockSearchItem[];
  initialTab?: "overview" | "chart";
  mode?: "live" | "replay";
  status?: WorkspaceStatus;
  onSymbolSelect?: (symbol: string) => void;
}

export function StockDetailPage({detail, market, fundamentals, risk, position, stocks = [], initialTab = "overview", mode = "live", status, onSymbolSelect}: StockDetailPageProps) {
  const priceChange = Number(readValue(detail.price_change));
  const regimeRows = Array.isArray(market.regime_strip) ? market.regime_strip as Array<Record<string, unknown>> : [];
  const latestRegime = regimeRows.at(-1) ?? {};
  const qualityMarkers = record(market.quality_markers);
  const discrepancies = Array.isArray(market.provider_discrepancy_markers) ? market.provider_discrepancy_markers as ProviderDiscrepancyMarker[] : [];
  const constraints = Array.isArray(position.constraints) ? position.constraints as Array<Record<string, unknown>> : [];
  const candles = Array.isArray(market.candles) ? market.candles as CandleRow[] : [];
  const cutoff = String(market.candlestick_latest_date ?? status?.data_cutoff ?? "UNAVAILABLE");
  const historicalSource = String(market.historical_chart_source ?? market.candlestick_source ?? "UNAVAILABLE");
  const operationalSource = String(detail.operational_provider ?? market.current_operational_provider ?? readSource(detail.latest_price) ?? "UNAVAILABLE");
  const freshness = status?.freshness_code ?? String(detail.freshness_state ?? "UNAVAILABLE");
  const portfolioMembership = String(detail.portfolio_membership_state ?? "UNAVAILABLE");
  const abstentionState = detail.abstain === null || detail.abstain === undefined
    ? "NOT_APPLICABLE"
    : Boolean(detail.abstain) ? "ABSTAIN" : "NOT_ABSTAIN";
  return <div className="page-stack">
    <PageHeader
      eyebrow="04 / INSTRUMENT WORKSPACE"
      title={detail.display_name}
      meta={`${detail.symbol} / ${readValue(detail.exchange)} / ${readValue(detail.board)}`}
      actions={<div className="stock-header-actions">
        {stocks.length && onSymbolSelect ? <StockSymbolSearch stocks={stocks} selectedSymbol={detail.symbol} onSelect={onSymbolSelect} /> : null}
        <div className="stock-price"><strong>{formatNumber(readValue(detail.latest_price))}</strong><span className={priceChange >= 0 ? "price-up" : "price-down"}>{formatPercent(readValue(detail.price_change))}</span><small>Validated {readDate(detail.latest_price)} / {readSource(detail.latest_price)}</small></div>
      </div>}
    />
    <div className="stock-summary">
      <Summary label="Industry" value={readValue(detail.industry)} />
      <Summary label="Latest validated close" value={readValue(market.latest_close) ?? readValue(detail.latest_price)} format="number" />
      <Summary label="Latest validated return" value={readValue(market.latest_return) ?? readValue(detail.price_change)} format="percent" />
      <Summary label="Data cutoff" value={cutoff} />
      <Summary label="Operational provider" value={operationalSource} />
      <div><span>Freshness</span><StatusBadge state={freshness} /></div>
      <Summary label="Portfolio weight" value={detail.current_weight} format="percent" />
      <Summary label="Risk contribution" value={detail.risk_contribution} format="percent" />
      <div><span>Portfolio membership</span><StatusBadge state={portfolioMembership} /></div>
      <div><span>Band status</span><StatusBadge state={String(detail.band_status)} /></div>
      <div><span>Abstention</span><StatusBadge state={abstentionState} /></div>
    </div>
    <Tabs.Root defaultValue={initialTab} className="stock-tabs">
      <Tabs.List aria-label="Stock detail views"><Tabs.Trigger value="overview">Overview</Tabs.Trigger><Tabs.Trigger value="market">Market</Tabs.Trigger><Tabs.Trigger value="fundamentals">Fundamentals</Tabs.Trigger><Tabs.Trigger value="chart">Price chart</Tabs.Trigger><Tabs.Trigger value="risk">Risk</Tabs.Trigger><Tabs.Trigger value="position">Position management</Tabs.Trigger></Tabs.List>
      <Tabs.Content value="overview"><EvidenceSection title="Identity & capital structure" values={pick(detail, ["company_name", "company_name_en", "exchange", "board", "industry", "industry_level1", "industry_level2", "listing_date", "st_status", "trading_status", "total_shares", "float_shares", "market_cap", "float_market_cap", "free_float_market_cap"])} /></Tabs.Content>
      <Tabs.Content value="market"><EvidenceSection title="Market evidence" values={pick(market, ["previous_close", "open", "high", "low", "latest_close", "latest_return", "volume", "amount", "turnover", "amplitude", "limit_up_price", "limit_down_price", "high_52_week", "low_52_week"])} /></Tabs.Content>
      <Tabs.Content value="fundamentals"><EvidenceSection title="Fundamentals" values={fundamentals} /></Tabs.Content>
      <Tabs.Content value="chart">
        <Panel title="Daily candlestick and volume" meta={`T-1 committed evidence through ${cutoff}`}>
          <div className="chart-semantics-banner"><strong>NOT A LIVE QUOTE</strong><span>{mode === "replay" ? "DETERMINISTIC REPLAY SNAPSHOT" : "LIVE READINESS VIEW OVER COMMITTED DATA"}</span><StatusBadge state={freshness} /></div>
          <div className="chart-evidence-strip">
            <EvidenceMarker label="Current operational provider" value={operationalSource} detail={`${String(detail.operational_function ?? "UNAVAILABLE")} / ${String(detail.operational_adjustment ?? "UNAVAILABLE")}`} />
            <EvidenceMarker label="Historical chart panel" value={historicalSource} detail={`Research-only history through ${cutoff}; not the current operational acquisition batch`} />
            <EvidenceMarker label="Data quality" value={formatMarkerCounts(qualityMarkers)} />
            <EvidenceMarker label="Provider discrepancies" value={String(discrepancies.length)} detail={discrepancies.length ? "Amber DQ markers identify affected dates" : "No committed discrepancy marker for this symbol"} />
            <EvidenceMarker label="Validated regime context" value={String(latestRegime.regime ?? "UNAVAILABLE")} detail={`${String(latestRegime.trade_date ?? "UNAVAILABLE")} / ${String(latestRegime.confidence_tier ?? "UNAVAILABLE")}`} />
          </div>
          <PriceVolumeChart rows={candles} discrepancies={discrepancies} />
        </Panel>
      </Tabs.Content>
      <Tabs.Content value="risk"><EvidenceSection title="Risk evidence" values={pick(risk, ["risk_research_state", "portfolio_membership_state", "volatility_20d", "volatility_60d", "ewma_volatility", "beta", "drawdown", "cvar_95", "marginal_risk_contribution", "component_risk_contribution", "correlation_cluster", "provider_quality", "quarantine_state"])} /></Tabs.Content>
      <Tabs.Content value="position"><div className="page-stack"><Panel title="Position management" meta={`${String(position.portfolio_membership_state ?? "UNAVAILABLE")} / ${String(position.position_research_state ?? "UNAVAILABLE")}`}><dl className="metric-list"><div><dt>Current weight</dt><dd>{formatPercent(position.current_weight)}</dd></div><div><dt>Reference policy weight</dt><dd>{formatPercent(position.reference_policy_weight)}</dd></div><div><dt>Band minimum</dt><dd>{formatPercent(position.acceptable_band_min)}</dd></div><div><dt>Band maximum</dt><dd>{formatPercent(position.acceptable_band_max)}</dd></div><div><dt>Band status</dt><dd>{String(position.band_status ?? "N/A")}</dd></div><div><dt>Confidence</dt><dd>{formatPercent(position.confidence)}</dd></div><div><dt>Constraint breach</dt><dd>{String(position.constraint_breach ?? "none")}</dd></div><div><dt>Abstain</dt><dd>{position.abstain === null || position.abstain === undefined ? "NOT APPLICABLE" : String(position.abstain)}</dd></div><div><dt>Abstention reasons</dt><dd>{Array.isArray(position.abstention_reason_codes) && position.abstention_reason_codes.length ? position.abstention_reason_codes.join(" / ") : "none"}</dd></div><div><dt>Actionable use</dt><dd>{position.actionable_use_allowed === false ? "FORBIDDEN" : "UNAVAILABLE"}</dd></div></dl></Panel><Panel title="Constraint evidence"><DenseTable rows={constraints} columns={[{key: "constraint_id", label: "Constraint"}, {key: "current_value", label: "Current"}, {key: "threshold", label: "Threshold"}, {key: "breach", label: "Breach"}, {key: "severity", label: "Severity"}, {key: "evidence_availability", label: "Evidence"}, {key: "fail_closed", label: "Fail closed"}]} compact /></Panel></div></Tabs.Content>
    </Tabs.Root>
  </div>;
}

function Summary({label, value, format}: {label: string; value: unknown; format?: "number" | "percent"}) {
  const rendered = value === null || value === undefined || value === "" ? "UNAVAILABLE" : format === "number" ? formatNumber(value) : format === "percent" ? formatPercent(value) : String(value);
  return <div><span>{label}</span><strong>{rendered}</strong></div>;
}

function EvidenceMarker({label, value, detail}: {label: string; value: string; detail?: string}) {
  return <div><span>{label}</span><strong>{value}</strong>{detail ? <small>{detail}</small> : null}</div>;
}

function EvidenceSection({title, values}: {title: string; values: Record<string, unknown>}) {
  return <Panel title={title}><div className="evidence-grid">{Object.entries(values).filter(([key]) => key !== "symbol" && key !== "research_only").map(([key, value]) => <UnavailableValue key={key} label={key === "revenue" ? "Revenue" : key.replaceAll("_", " ")} evidence={normalizeEvidence(value)} />)}</div></Panel>;
}

function normalizeEvidence(value: unknown): EvidenceValue {
  if (value && typeof value === "object" && "availability" in value) return value as EvidenceValue;
  if (value !== null && value !== undefined && value !== "") return {value: value as string | number | boolean, asof_date: null, source: null, availability: "AVAILABLE", quality_status: "EVIDENCE_BACKED", reason: null};
  return {value: null, asof_date: null, source: null, availability: "UNAVAILABLE", quality_status: "NO_COMMITTED_EVIDENCE", reason: "field is not present in committed evidence"};
}

function formatMarkerCounts(markers: Record<string, unknown>): string {
  const entries = Object.entries(markers);
  return entries.length ? entries.map(([key, value]) => `${key}:${String(value)}`).join(" / ") : "UNAVAILABLE";
}

function pick(source: Record<string, unknown>, keys: string[]) {return Object.fromEntries(keys.map((key) => [key, source[key]]));}
function record(value: unknown): Record<string, unknown> {return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : {};}
function readValue(value: unknown) {return value && typeof value === "object" && "value" in value ? (value as {value: unknown}).value : value;}
function readDate(value: unknown) {return value && typeof value === "object" && "asof_date" in value ? String((value as {asof_date: unknown}).asof_date) : "N/A";}
function readSource(value: unknown) {return value && typeof value === "object" && "source" in value ? String((value as {source: unknown}).source) : "N/A";}

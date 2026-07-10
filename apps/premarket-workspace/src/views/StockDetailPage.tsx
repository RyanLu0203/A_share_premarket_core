"use client";

import * as Tabs from "@radix-ui/react-tabs";

import { DenseTable } from "@/components/DenseTable";
import { PriceVolumeChart } from "@/components/PriceVolumeChart";
import { PageHeader, Panel, StatusBadge } from "@/components/ui";
import { UnavailableValue } from "@/components/UnavailableValue";
import { formatNumber, formatPercent } from "@/lib/format";
import type { EvidenceValue } from "@/lib/types";

type Detail = Record<string, unknown> & {symbol: string; display_name: string};

export function StockDetailPage({detail, market, fundamentals, risk, position}: {detail: Detail; market: Record<string, unknown>; fundamentals: Record<string, unknown>; risk: Record<string, unknown>; position: Record<string, unknown>}) {
  const priceChange = Number(readValue(detail.price_change));
  const regimeRows = Array.isArray(market.regime_strip) ? market.regime_strip as Array<Record<string, unknown>> : [];
  const latestRegime = regimeRows.at(-1) ?? {};
  const qualityMarkers = market.quality_markers && typeof market.quality_markers === "object" ? market.quality_markers as Record<string, unknown> : {};
  const discrepancies = Array.isArray(market.provider_discrepancy_markers) ? market.provider_discrepancy_markers : [];
  const constraints = Array.isArray(position.constraints) ? position.constraints as Array<Record<string, unknown>> : [];
  return <div className="page-stack"><PageHeader eyebrow="04 / INSTRUMENT WORKSPACE" title={detail.display_name} meta={`${detail.symbol} / ${readValue(detail.exchange)} / ${readValue(detail.board)}`} actions={<div className="stock-price"><strong>{formatNumber(readValue(detail.latest_price))}</strong><span className={priceChange >= 0 ? "price-up" : "price-down"}>{formatPercent(readValue(detail.price_change))}</span><small>{readDate(detail.latest_price)} / {readSource(detail.latest_price)}</small></div>} />
    <div className="stock-summary"><div><span>Industry</span><strong>{String(readValue(detail.industry) ?? "N/A")}</strong></div><div><span>Provider lineage</span><strong>{Array.isArray(detail.provider_lineage) ? detail.provider_lineage.join(" / ") : "N/A"}</strong></div><div><span>Freshness</span><StatusBadge state={String(detail.freshness_state)} /></div><div><span>Current weight</span><strong>{formatPercent(detail.current_weight)}</strong></div><div><span>Acceptable band</span><strong>{formatPercent(detail.band_min)} - {formatPercent(detail.band_max)}</strong></div><div><span>Band status</span><StatusBadge state={String(detail.band_status)} /></div><div><span>Confidence</span><strong>{formatPercent(detail.confidence)}</strong></div><div><span>Abstention</span><StatusBadge state={Boolean(detail.abstain) ? "ABSTAIN" : "NOT_ABSTAIN"} /></div></div>
    <Tabs.Root defaultValue="overview" className="stock-tabs"><Tabs.List aria-label="Stock detail views"><Tabs.Trigger value="overview">Overview</Tabs.Trigger><Tabs.Trigger value="market">Market</Tabs.Trigger><Tabs.Trigger value="fundamentals">Fundamentals</Tabs.Trigger><Tabs.Trigger value="chart">Price chart</Tabs.Trigger><Tabs.Trigger value="risk">Risk</Tabs.Trigger><Tabs.Trigger value="position">Position management</Tabs.Trigger></Tabs.List>
      <Tabs.Content value="overview"><EvidenceSection title="Identity & capital structure" values={pick(detail, ["company_name", "company_name_en", "exchange", "board", "industry", "industry_level1", "industry_level2", "listing_date", "st_status", "trading_status", "total_shares", "float_shares", "market_cap", "float_market_cap", "free_float_market_cap"])} /></Tabs.Content>
      <Tabs.Content value="market"><EvidenceSection title="Market evidence" values={pick(market, ["previous_close", "open", "high", "low", "latest_close", "latest_return", "volume", "amount", "turnover", "amplitude", "limit_up_price", "limit_down_price", "high_52_week", "low_52_week"])} /></Tabs.Content>
      <Tabs.Content value="fundamentals"><EvidenceSection title="Fundamentals" values={fundamentals} /></Tabs.Content>
      <Tabs.Content value="chart"><Panel title="Candlestick & volume" meta={`Evidence through ${String(market.candlestick_latest_date ?? "N/A")}`}><div className="chart-evidence-strip"><div><span>Regime strip</span><strong>{String(latestRegime.regime ?? "UNAVAILABLE")}</strong><small>{String(latestRegime.trade_date ?? "N/A")} / {String(latestRegime.confidence_tier ?? "N/A")}</small></div><div><span>Data quality markers</span><strong>{Object.entries(qualityMarkers).map(([key, value]) => `${key}:${String(value)}`).join(" / ") || "UNAVAILABLE"}</strong></div><div><span>Provider discrepancy markers</span><strong>{discrepancies.length}</strong></div></div><PriceVolumeChart rows={Array.isArray(market.candles) ? market.candles : []} /></Panel></Tabs.Content>
      <Tabs.Content value="risk"><EvidenceSection title="Risk evidence" values={pick(risk, ["volatility_20d", "volatility_60d", "ewma_volatility", "beta", "drawdown", "cvar_95", "marginal_risk_contribution", "component_risk_contribution", "correlation_cluster", "provider_quality", "quarantine_state"])} /></Tabs.Content>
      <Tabs.Content value="position"><div className="page-stack"><Panel title="Position management"><dl className="metric-list"><div><dt>Current weight</dt><dd>{formatPercent(position.current_weight)}</dd></div><div><dt>Reference policy weight</dt><dd>{formatPercent(position.reference_policy_weight)}</dd></div><div><dt>Band minimum</dt><dd>{formatPercent(position.acceptable_band_min)}</dd></div><div><dt>Band maximum</dt><dd>{formatPercent(position.acceptable_band_max)}</dd></div><div><dt>Band status</dt><dd>{String(position.band_status ?? "N/A")}</dd></div><div><dt>Confidence</dt><dd>{formatPercent(position.confidence)}</dd></div><div><dt>Constraint breach</dt><dd>{String(position.constraint_breach ?? "none")}</dd></div><div><dt>Abstain</dt><dd>{String(position.abstain ?? false)}</dd></div><div><dt>Abstention reasons</dt><dd>{Array.isArray(position.abstention_reason_codes) && position.abstention_reason_codes.length ? position.abstention_reason_codes.join(" / ") : "none"}</dd></div></dl></Panel><Panel title="Constraint evidence"><DenseTable rows={constraints} columns={[{key: "constraint_id", label: "Constraint"}, {key: "current_value", label: "Current"}, {key: "threshold", label: "Threshold"}, {key: "breach", label: "Breach"}, {key: "severity", label: "Severity"}, {key: "evidence_availability", label: "Evidence"}, {key: "fail_closed", label: "Fail closed"}]} compact /></Panel></div></Tabs.Content>
    </Tabs.Root>
  </div>;
}

function EvidenceSection({title, values}: {title: string; values: Record<string, unknown>}) {
  return <Panel title={title}><div className="evidence-grid">{Object.entries(values).filter(([key]) => key !== "symbol" && key !== "research_only").map(([key, value]) => <UnavailableValue key={key} label={key === "revenue" ? "Revenue" : key.replaceAll("_", " ")} evidence={normalizeEvidence(value)} />)}</div></Panel>;
}

function normalizeEvidence(value: unknown): EvidenceValue {
  if (value && typeof value === "object" && "availability" in value) return value as EvidenceValue;
  if (value !== null && value !== undefined && value !== "") return {value: value as string | number | boolean, asof_date: null, source: null, availability: "AVAILABLE", quality_status: "EVIDENCE_BACKED", reason: null};
  return {value: null, asof_date: null, source: null, availability: "UNAVAILABLE", quality_status: "NO_COMMITTED_EVIDENCE", reason: "field is not present in committed evidence"};
}

function pick(source: Record<string, unknown>, keys: string[]) {return Object.fromEntries(keys.map((key) => [key, source[key]]));}
function readValue(value: unknown) {return value && typeof value === "object" && "value" in value ? (value as {value: unknown}).value : value;}
function readDate(value: unknown) {return value && typeof value === "object" && "asof_date" in value ? String((value as {asof_date: unknown}).asof_date) : "N/A";}
function readSource(value: unknown) {return value && typeof value === "object" && "source" in value ? String((value as {source: unknown}).source) : "N/A";}

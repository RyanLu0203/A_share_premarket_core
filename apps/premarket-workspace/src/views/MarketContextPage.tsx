import { KpiCard, PageHeader, Panel, StatusBadge } from "@/components/ui";
import { formatNumber, formatPercent, humanize } from "@/lib/format";

export function MarketContextPage({data}: {data: Record<string, unknown>}) {
  const indices = Array.isArray(data.indices) ? data.indices as Array<Record<string, unknown>> : [];
  const regime = isRecord(data.regime) ? data.regime : {};
  const regimeFields = Object.entries(regime).filter(([key]) => key.endsWith("_regime") || key === "refined_composite_regime_label");
  return <div className="page-stack">
    <PageHeader eyebrow="05 / MARKET EVIDENCE" title="Market Context" meta={`Cutoff ${String(data.data_cutoff ?? "N/A")} / Macro and news evidence unavailable`} />
    <div className="kpi-grid compact">{indices.map((row) => <KpiCard key={String(row.index_id)} label={humanize(String(row.index_name))} value={formatNumber(row.close)} state={Number(row.return_1d) >= 0 ? "UP" : "DOWN"} timestamp={String(row.trade_date)} />)}<KpiCard label="Market volatility" value={regime.broad_index_volatility_20d} format="percent" timestamp={String(regime.trade_date ?? "N/A")} /><KpiCard label="Data freshness" value={data.freshness} state={String(data.freshness ?? "UNAVAILABLE")} timestamp={String(data.data_cutoff ?? "N/A")} /></div>
    <div className="dashboard-grid two-one">
      <Panel title="Refined market regime" meta="Research-only context"><div className="regime-grid">{regimeFields.map(([key, value]) => <div key={key}><span>{humanize(key)}</span><StatusBadge state={String(value)} /></div>)}</div></Panel>
      <Panel title="Context quality"><dl className="metric-list"><div><dt>Confidence tier</dt><dd>{String(regime.regime_confidence_tier ?? "N/A")}</dd></div><div><dt>Source coverage</dt><dd>{formatPercent(regime.source_coverage_score)}</dd></div><div><dt>External quality</dt><dd>{formatPercent(regime.external_data_quality_score)}</dd></div><div><dt>No lookahead</dt><dd>{String(regime.no_lookahead_status ?? "N/A")}</dd></div></dl></Panel>
      <Panel title="Index evidence" className="span-two"><div className="index-strip">{indices.map((row) => <article key={String(row.index_id)}><span>{String(row.index_id)}</span><strong>{formatNumber(row.close)}</strong><b className={Number(row.return_1d) >= 0 ? "price-up" : "price-down"}>{formatPercent(row.return_1d)}</b><small>{String(row.source_provider)} / {String(row.trade_date)}</small></article>)}</div></Panel>
    </div>
  </div>;
}

function isRecord(value: unknown): value is Record<string, unknown> {return Boolean(value) && typeof value === "object" && !Array.isArray(value);}

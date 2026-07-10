import { FreshnessBanner } from "@/components/FreshnessBanner";
import { KpiCard, PageHeader, Panel, StatusBadge } from "@/components/ui";
import { formatNumber, formatPercent, humanize } from "@/lib/format";
import type { WorkspaceStatus } from "@/lib/types";

interface CommandCenterData {
  status: WorkspaceStatus;
  kpis: Record<string, unknown>;
  position_distribution: Record<string, number>;
  top_risk_contributors: string[];
  warnings: Array<Record<string, string>>;
  exposure: Record<string, string>;
  provider_health?: Record<string, unknown>;
  risk_history: Array<Record<string, string>>;
}

export function CommandCenterPage({data}: {data: CommandCenterData}) {
  const kpi = data.kpis;
  const providerHealth = data.provider_health ?? {};
  const timestamp = String(kpi.snapshot_timestamp ?? "");
  const staleWarning = data.status.current_panels_enabled === false ? "STALE SNAPSHOT EVIDENCE" : undefined;
  const providerComparisons = Array.isArray(providerHealth.comparison) ? providerHealth.comparison.length : 0;
  const quarantinedRows = Array.isArray(providerHealth.quarantine) ? providerHealth.quarantine.length : 0;
  return <div className="page-stack">
    <PageHeader eyebrow="01 / MORNING CONTROL" title="Command Center" meta="Validated snapshot state / Local research only" />
    <FreshnessBanner status={data.status} />
    <div className="kpi-grid">
      <KpiCard label="Readiness state" value={data.status.readiness_state} state={data.status.readiness_state} timestamp={timestamp} warning={staleWarning} />
      <KpiCard label="Portfolio risk state" value={humanize(String(kpi.portfolio_risk_state ?? "N/A"))} state={String(kpi.portfolio_risk_state ?? "UNAVAILABLE")} timestamp={timestamp} warning={staleWarning} />
      <KpiCard label="Gross exposure" value={kpi.gross_exposure} format="percent" state="SNAPSHOT" timestamp={timestamp} warning={staleWarning} />
      <KpiCard label="Cash weight" value={kpi.cash_weight} format="percent" state="SNAPSHOT" timestamp={timestamp} warning={staleWarning} />
      <KpiCard label="Portfolio volatility" value={kpi.portfolio_volatility} format="percent" state="SNAPSHOT" timestamp={timestamp} warning={staleWarning} />
      <KpiCard label="Beta" value={kpi.beta} state="SNAPSHOT" timestamp={timestamp} warning={staleWarning} />
      <KpiCard label="Constraint breaches" value={kpi.constraint_breaches} state={Number(kpi.constraint_breaches) ? "BREACH" : "PASS"} timestamp={timestamp} warning={staleWarning} />
      <KpiCard label="Abstentions" value={kpi.abstentions} state={Number(kpi.abstentions) ? "ABSTAIN" : "PASS"} timestamp={timestamp} warning={staleWarning} />
    </div>
    <div className="dashboard-grid two-one">
      <Panel title="Portfolio risk trend" meta={`${data.risk_history.length} validated snapshot${data.risk_history.length === 1 ? "" : "s"}`}><div className="single-point-trend"><span>{data.risk_history[0]?.trading_date ?? "N/A"}</span><strong>{formatPercent(data.risk_history[0]?.portfolio_volatility)}</strong><small>Annualized portfolio volatility</small></div></Panel>
      <Panel title="Exposure envelope"><dl className="metric-list"><div><dt>Gross</dt><dd>{formatPercent(data.exposure.current_gross_exposure)}</dd></div><div><dt>Allowed</dt><dd>{formatPercent(data.exposure.acceptable_gross_exposure_min)} - {formatPercent(data.exposure.acceptable_gross_exposure_max)}</dd></div><div><dt>Volatility budget</dt><dd>{formatPercent(data.exposure.volatility_budget)}</dd></div></dl></Panel>
      <Panel title="Position status distribution"><div className="distribution-list">{Object.entries(data.position_distribution).map(([state, count]) => <div key={state}><StatusBadge state={state} /><strong>{count}</strong><span style={{width: `${Math.min(100, count * 2.4)}%`}} /></div>)}</div></Panel>
      <Panel title="Top risk contributors"><ol className="ranked-list">{data.top_risk_contributors.length ? data.top_risk_contributors.map((item) => <li key={item}>{item}</li>) : <li>No committed rows</li>}</ol></Panel>
      <Panel title="Data / Provider Health"><dl className="metric-list"><div><dt>Diagnostics</dt><dd>{providerComparisons}</dd></div><div><dt>Quarantined rows</dt><dd>{quarantinedRows}</dd></div><div><dt>Adjustment convention</dt><dd>{String(providerHealth.adjustment_convention_status ?? "UNAVAILABLE")}</dd></div><div><dt>Silent averaging</dt><dd>{providerHealth.no_silent_averaging === true ? "DISABLED" : "UNKNOWN"}</dd></div></dl></Panel>
      <Panel title="Critical warnings" className="span-two"><div className="warning-list">{data.warnings.map((warning) => <article key={warning.warning_code}><StatusBadge state="WARNING" /><div><strong>{warning.warning_code}</strong><p>{warning.detail}</p></div><b>{formatNumber(warning.count, 0)}</b></article>)}</div></Panel>
    </div>
  </div>;
}

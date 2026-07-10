import Link from "next/link";

import { AllocationTreemap, CorrelationHeatmap, RiskContributionChart } from "@/components/EvidenceCharts";
import { DenseTable, type DenseColumn } from "@/components/DenseTable";
import { KpiCard, PageHeader, Panel, StatusBadge } from "@/components/ui";
import { formatPercent } from "@/lib/format";

type Position = Record<string, unknown> & {symbol: string; band_status: string};

export function PortfolioOverviewPage({data}: {data: Record<string, unknown>}) {
  const risk = record(data.risk_state);
  const exposure = record(data.exposure);
  const positions = array(data.positions) as Position[];
  const matrix = record(data.correlation_matrix);
  const columns: DenseColumn<Position>[] = [
    {key: "symbol", label: "Symbol", render: (row) => <Link href={`/stocks/${row.symbol}`}>{row.symbol}</Link>},
    {key: "current_weight", label: "Weight", render: (row) => formatPercent(row.current_weight)},
    {key: "reference_policy_weight", label: "Reference", render: (row) => formatPercent(row.reference_policy_weight)},
    {key: "risk_contribution", label: "Risk contribution", render: (row) => formatPercent(row.risk_contribution)},
    {key: "band_status", label: "Band", render: (row) => <StatusBadge state={row.band_status} />},
    {key: "confidence", label: "Confidence", render: (row) => formatPercent(row.confidence)},
  ];
  return <div className="page-stack"><PageHeader eyebrow="06 / REFERENCE PORTFOLIO" title="Portfolio Overview" meta={`${String(data.portfolio_mode)} / Research-only diagnostic holdings`} />
    <div className="portfolio-mode-banner"><StatusBadge state={String(data.portfolio_mode)} /><strong>Diagnostic holdings only</strong><span>No real current holdings or execution path is connected.</span></div>
    <div className="kpi-grid compact"><KpiCard label="Gross exposure" value={Number(risk.gross_exposure)} format="percent" /><KpiCard label="Cash" value={Number(risk.cash_weight)} format="percent" /><KpiCard label="Volatility" value={Number(risk.portfolio_volatility)} format="percent" /><KpiCard label="Beta to CSI 300" value={risk.beta_to_csi300} /><KpiCard label="Max drawdown" value={Number(risk.max_drawdown)} format="percent" /><KpiCard label="Effective positions" value={risk.effective_number_of_positions} /></div>
    <div className="dashboard-grid equal"><Panel title="Holdings allocation" meta="Validated reference weights"><AllocationTreemap rows={positions} /></Panel><Panel title="Risk contribution" meta="Component contribution shares"><RiskContributionChart rows={positions} /></Panel></div>
    <div className="dashboard-grid equal"><Panel title="Exposure envelope"><dl className="metric-list"><div><dt>Gross range</dt><dd>{formatPercent(exposure.acceptable_gross_exposure_min)} - {formatPercent(exposure.acceptable_gross_exposure_max)}</dd></div><div><dt>Cash range</dt><dd>{formatPercent(exposure.acceptable_cash_min)} - {formatPercent(exposure.acceptable_cash_max)}</dd></div><div><dt>Volatility budget</dt><dd>{formatPercent(exposure.volatility_budget)}</dd></div><div><dt>Beta budget</dt><dd>{String(exposure.beta_budget ?? "N/A")}</dd></div></dl></Panel><Panel title="Correlation clusters"><div className="cluster-list">{array(data.clusters).map((item) => {const row = record(item); return <article key={String(row.cluster_id)}><StatusBadge state={String(row.cluster_id)} /><strong>{String(row.symbol_count)}</strong><span>symbols</span><small>{String(row.cluster_rule)}</small></article>;})}</div></Panel></div>
    <Panel title="Correlation matrix" meta={`${String(matrix.asof_date ?? "N/A")} / ${String(matrix.derivation ?? "display only")} / Not a decision input`}><CorrelationHeatmap matrix={matrix} /></Panel>
    <Panel title="Position evidence" meta={`${positions.length} symbols`}><DenseTable rows={positions} columns={columns} searchPlaceholder="Search reference positions" compact /></Panel>
  </div>;
}

function record(value: unknown): Record<string, unknown> {return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : {};}
function array(value: unknown): unknown[] {return Array.isArray(value) ? value : [];}

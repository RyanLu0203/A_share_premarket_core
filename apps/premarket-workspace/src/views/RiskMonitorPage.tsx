import { PolicyRiskChart, RiskContributionChart } from "@/components/EvidenceCharts";
import { DenseTable, type DenseColumn } from "@/components/DenseTable";
import { KpiCard, PageHeader, Panel, StatusBadge } from "@/components/ui";
import { formatPercent, humanize } from "@/lib/format";

type Row = Record<string, unknown>;

export function RiskMonitorPage({data}: {data: Record<string, unknown>}) {
  const state = record(data.state);
  const contributions = array(data.contributions);
  const policies = array(data.policy_comparison);
  const catalog = array(data.policy_catalog);
  const clusters = array(data.clusters);
  const history = array(data.history);
  const contributionColumns: DenseColumn<Row>[] = [{key: "symbol", label: "Symbol"}, {key: "reference_weight", label: "Weight", render: (row) => formatPercent(row.reference_weight)}, {key: "volatility_60d", label: "60d volatility", render: (row) => formatPercent(row.volatility_60d)}, {key: "risk_contribution_share", label: "Risk contribution", render: (row) => formatPercent(row.risk_contribution_share)}, {key: "risk_contribution_status", label: "Method"}];
  const catalogColumns: DenseColumn<Row>[] = [{key: "policy_id", label: "Policy"}, {key: "policy_family", label: "Family"}, {key: "covariance_assumption", label: "Covariance"}, {key: "clustering_assumption", label: "Clustering"}, {key: "effective_distinct_policy", label: "Distinct", render: (row) => <StatusBadge state={String(row.effective_distinct_policy) === "true" ? "DISTINCT" : "DUPLICATE"} />}, {key: "equivalence_disclosure", label: "Equivalence disclosure"}];
  return <div className="page-stack"><PageHeader eyebrow="08 / RISK EVIDENCE" title="Risk Monitor" meta="Chronological research evaluation / No alpha / No execution instruction" />
    <div className="kpi-grid compact"><KpiCard label="Portfolio volatility" value={Number(state.portfolio_volatility)} format="percent" /><KpiCard label="EWMA volatility" value={Number(state.ewma_volatility)} format="percent" /><KpiCard label="Beta" value={state.beta_to_csi300} /><KpiCard label="Average correlation" value={Number(state.average_correlation)} format="percent" /><KpiCard label="CVaR 95 daily" value={Number(state.cvar_95_daily)} format="percent" /><KpiCard label="Max drawdown" value={Number(state.max_drawdown)} format="percent" /><KpiCard label="Effective positions" value={state.effective_number_of_positions} /><KpiCard label="Cluster concentration" value={Number(state.cluster_concentration)} format="percent" /><KpiCard label="Risk state" value={humanize(String(state.predecessor_risk_state ?? "N/A"))} state="REVIEW_ONLY" /></div>
    <div className="dashboard-grid equal"><Panel title="Policy comparison" meta={`${policies.length} evaluated / duplicate policies disclosed`}><PolicyRiskChart rows={policies} /></Panel><Panel title="Component risk"><RiskContributionChart rows={contributions} /></Panel></div>
    <Panel title="Pre-specified policy catalog" meta="Diagonal ERC is not counted as independent evidence when equivalent to inverse volatility"><DenseTable rows={catalog} columns={catalogColumns} searchPlaceholder="Search policy assumptions" compact /></Panel>
    <Panel title="Risk contribution evidence"><DenseTable rows={contributions} columns={contributionColumns} searchPlaceholder="Search component risk" compact /></Panel>
    <div className="dashboard-grid equal"><Panel title="Risk-state history"><DenseTable rows={history} columns={[{key: "trading_date", label: "Date"}, {key: "predecessor_risk_state", label: "Risk state", render: (row) => <StatusBadge state={String(row.predecessor_risk_state)} />}, {key: "portfolio_volatility", label: "Volatility", render: (row) => formatPercent(row.portfolio_volatility)}, {key: "max_drawdown", label: "Drawdown", render: (row) => formatPercent(row.max_drawdown)}, {key: "cluster_concentration", label: "Cluster concentration", render: (row) => formatPercent(row.cluster_concentration)}]} compact /></Panel><Panel title="Cluster concentration"><DenseTable rows={clusters} columns={[{key: "cluster_id", label: "Cluster"}, {key: "symbol_count", label: "Symbols"}, {key: "cluster_rule", label: "Rule"}, {key: "constraint_usage", label: "Constraint usage"}]} compact /></Panel></div>
  </div>;
}

function record(value: unknown): Row {return value && typeof value === "object" && !Array.isArray(value) ? value as Row : {};}
function array(value: unknown): Row[] {return Array.isArray(value) ? value as Row[] : [];}

import { DenseTable, type DenseColumn } from "@/components/DenseTable";
import { QuantLockedState } from "@/components/QuantLockedState";
import { KpiCard, PageHeader, Panel, StatusBadge } from "@/components/ui";

type Capabilities = {
  ready_factor_count: number;
  recommendation_tiering_state: string;
  issue_10_state: string;
  candidate_readiness: Record<string, number>;
  quant04_refined_factors: Record<string, number>;
  factor_table_contract: string[];
  candidate_rows: Array<Record<string, unknown>>;
};

const titleByPage: Record<number, string> = {11: "Alpha Overview", 12: "Factor Monitor", 13: "IC / RankIC Lab", 14: "Regime Analysis", 15: "Factor Correlation", 16: "Candidate Diagnostics", 17: "Recommendation Tiering"};

export function QuantWorkspacePage({pageId, capabilities, marketContext}: {pageId: number; capabilities: Capabilities; marketContext?: Record<string, unknown>}) {
  const title = titleByPage[pageId] ?? "Quant Research";
  if (pageId === 11) return <div className="page-stack"><PageHeader eyebrow="11 / QUANT RESEARCH" title={title} /><QuantLockedState title={title} readyFactorCount={capabilities.ready_factor_count} state="LOCKED_NO_READY_FACTORS" /><div className="kpi-grid"><KpiCard label="Candidates evaluated" value={capabilities.candidate_readiness.evaluated} /><KpiCard label="Ready" value={capabilities.candidate_readiness.ready} /><KpiCard label="Conditionally useful" value={capabilities.quant04_refined_factors.conditionally_useful} /><KpiCard label="Not ready" value={capabilities.candidate_readiness.not_ready} /></div></div>;
  if (pageId === 15) return <div className="page-stack"><PageHeader eyebrow="15 / QUANT RESEARCH" title={title} /><QuantLockedState title={title} readyFactorCount={capabilities.ready_factor_count} state="LOCKED_NO_READY_FACTORS" /><div className="placeholder-grid">{["Correlation heatmap", "Cluster tree", "Redundancy diagnostics"].map((label) => <Panel key={label} title={label}><span className="locked-placeholder">LOCKED_NO_READY_FACTORS / NO FACTOR MATRIX</span></Panel>)}</div></div>;
  if (pageId === 16) {
    const columns: DenseColumn<Record<string, unknown>>[] = [
      {key: "candidate_id", label: "Candidate"}, {key: "factor_family", label: "Family"}, {key: "readiness_transform", label: "Transform"}, {key: "readiness_status", label: "Readiness", render: (row) => <StatusBadge state={String(row.readiness_status)} />}, {key: "decision_summary", label: "Failure reasons"}, {key: "holdout_mean_ic_1d", label: "Historical holdout IC"}, {key: "holdout_rank_ic_1d", label: "Historical RankIC"}, {key: "provider_robustness_status", label: "Provider"},
    ];
    return <div className="page-stack"><PageHeader eyebrow="16 / READ-ONLY HISTORICAL" title={title} meta={`${capabilities.candidate_readiness.evaluated} candidates / No promotion controls`} /><QuantLockedState title={title} readyFactorCount={0} state="LOCKED_READ_ONLY_HISTORICAL" /><DenseTable rows={capabilities.candidate_rows} columns={columns} searchPlaceholder="Search historical candidates" /></div>;
  }
  if (pageId === 14) return <div className="page-stack"><PageHeader eyebrow="14 / REGIME CONTEXT" title={title} /><Panel title="AVAILABLE MARKET REGIME CONTEXT"><pre className="data-pre">{JSON.stringify(marketContext ?? {}, null, 2)}</pre></Panel><QuantLockedState title="Factor x Regime Analysis" readyFactorCount={0} state="LOCKED_NO_READY_FACTORS" /></div>;
  if (pageId === 17) return <div className="page-stack"><PageHeader eyebrow="17 / GOVERNANCE LOCK" title={title} /><QuantLockedState title={title} readyFactorCount={0} state={capabilities.recommendation_tiering_state} /><Panel title="Authorization state"><dl className="metric-list"><div><dt>GOAL-REC-TIERING-01</dt><dd>not authorized</dd></div><div><dt>Issue #10</dt><dd>locked</dd></div><div><dt>Ready factors</dt><dd>0</dd></div></dl><p className="lock-note">Issue #10: {capabilities.issue_10_state}</p></Panel></div>;
  return <div className="page-stack"><PageHeader eyebrow={`${String(pageId).padStart(2, "0")} / QUANT RESEARCH`} title={title} /><QuantLockedState title={title} readyFactorCount={capabilities.ready_factor_count} state={pageId === 13 ? "BLOCKED_PENDING_READY_FACTOR" : "LOCKED_NO_READY_FACTORS"} />{pageId === 12 ? <Panel title="Future table contract"><div className="contract-fields">{capabilities.factor_table_contract.map((field) => <code key={field}>{field}</code>)}</div></Panel> : null}{pageId === 13 ? <div className="placeholder-grid">{["IC time series", "RankIC time series", "IC distribution", "Rolling IC", "Horizon comparison"].map((label) => <Panel key={label} title={label}><span className="locked-placeholder">BLOCKED_PENDING_READY_FACTOR</span></Panel>)}</div> : null}</div>;
}

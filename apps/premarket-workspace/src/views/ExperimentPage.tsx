import { DenseTable, type DenseColumn } from "@/components/DenseTable";
import { EmptyState, PageHeader, Panel, StatusBadge } from "@/components/ui";

type Row = Record<string, unknown>;

export function ExperimentPage({pageId, data}: {pageId: 18 | 19; data: Record<string, unknown>}) {
  const observations = Array.isArray(data.observations) ? data.observations as Row[] : [];
  if (pageId === 19) return <div className="page-stack"><PageHeader eyebrow="19 / FORWARD RECORD" title="Experiment History" meta="Immutable observations only" /><Panel title="Observation history" meta={`${observations.length} rows`}>{observations.length ? <DenseTable rows={observations} columns={columnsFor(observations)} /> : <EmptyState title={String(data.empty_state ?? "NO FORWARD EXPERIMENT OBSERVATIONS YET")} detail="The frozen shadow protocol is prepared but has not started collecting forward evidence." />}</Panel></div>;
  const contract = data.contract && typeof data.contract === "object" ? Object.entries(data.contract as Record<string, unknown>).map(([field, value]) => ({field, value: String(value)})) : [];
  const refreshContract = data.daily_refresh_contract && typeof data.daily_refresh_contract === "object" ? Object.entries(data.daily_refresh_contract as Record<string, unknown>).map(([field, value]) => ({field, value: String(value)})) : [];
  return <div className="page-stack"><PageHeader eyebrow="18 / SHADOW PROTOCOL" title="Shadow Experiment" meta="Frozen protocol / No live orders / No recommendation output" /><div className="summary-strip"><div><StatusBadge state={String(data.status ?? "UNKNOWN")} /><strong>{observations.length}</strong><span>observations</span></div></div><div className="dashboard-grid two-one"><Panel title="Frozen contract"><DenseTable rows={contract} columns={[{key: "field", label: "Field"}, {key: "value", label: "Frozen value"}]} compact /></Panel><Panel title="Governance boundary"><dl className="metric-list"><div><dt>Execution</dt><dd>none</dd></div><div><dt>Broker connection</dt><dd>none</dd></div><div><dt>Recommendation tiering</dt><dd>locked</dd></div><div><dt>Current status</dt><dd>{String(data.status)}</dd></div></dl></Panel><Panel title="Daily refresh experiment readiness" className="span-two"><DenseTable rows={refreshContract} columns={[{key: "field", label: "Field"}, {key: "value", label: "Frozen value"}]} compact /></Panel></div></div>;
}

function columnsFor(rows: Row[]): DenseColumn<Row>[] {return Object.keys(rows[0] ?? {}).slice(0, 10).map((key) => ({key, label: key.replaceAll("_", " ")}));}

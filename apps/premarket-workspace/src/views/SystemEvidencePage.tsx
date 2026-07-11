import { DenseTable, type DenseColumn } from "@/components/DenseTable";
import { EmptyState, KpiCard, PageHeader, Panel, StatusBadge } from "@/components/ui";
import { formatPercent } from "@/lib/format";

type Row = Record<string, unknown>;

export function DataQualityPage({data}: {data: Record<string, unknown>}) {
  const checks = rows(data.readiness_checks);
  const summary = rows(data.quality_summary);
  const quarantine = rows(data.quarantine);
  const status = record(data.status);
  return <div className="page-stack"><PageHeader eyebrow="20 / EVIDENCE QUALITY" title="Data Quality" meta="PIT, freshness, completeness, and quarantine diagnostics" />
    <div className="kpi-grid compact"><KpiCard label="Readiness checks" value={checks.length} /><KpiCard label="Quality artifacts" value={summary.length} /><KpiCard label="Quarantine rows" value={quarantine.length} state={quarantine.length ? "WARNING" : "PASS"} /><KpiCard label="Latest status" value={status.readiness_state} state={String(status.readiness_state)} /><KpiCard label="Target trading date" value={status.target_trading_date} /><KpiCard label="Expected T-1" value={status.expected_previous_trading_date} /><KpiCard label="Latest available" value={status.latest_available_data_date} /><KpiCard label="PIT / cutoff" value={status.data_cutoff} /></div>
    <Panel title="Readiness state definitions"><div className="state-definition-grid"><div><StatusBadge state="READY" /><span>Required evidence is current and available.</span></div><div><StatusBadge state="READY_WITH_WARNINGS" /><span>Usable snapshot with disclosed non-blocking warnings.</span></div><div><StatusBadge state="ABSTAIN" /><span>Evidence does not support a precise band.</span></div><div><StatusBadge state="BLOCKED" /><span>Current-state interpretation is disabled.</span></div></div></Panel>
    <Panel title="Readiness matrix"><DenseTable rows={checks} columns={[{key: "check_id", label: "Check"}, {key: "state", label: "State", render: (row) => <StatusBadge state={String(row.state)} />}, {key: "current_value", label: "Current"}, {key: "threshold", label: "Threshold"}, {key: "evidence", label: "Evidence"}, {key: "fail_closed_behavior", label: "Fail closed"}]} compact /></Panel>
    <Panel title="Committed artifact quality"><DenseTable rows={summary} columns={[{key: "artifact_name", label: "Artifact"}, {key: "row_count", label: "Rows"}, {key: "missing_value_share", label: "Missing", render: (row) => formatPercent(row.missing_value_share)}, {key: "pit_policy_status", label: "PIT"}, {key: "provider_health_status", label: "Provider"}, {key: "quality_status", label: "State", render: (row) => <StatusBadge state={String(row.quality_status)} />}]} compact /></Panel>
    <Panel title="Quarantine evidence"><DenseTable rows={quarantine} columns={autoColumns(quarantine, 9)} compact /></Panel>
  </div>;
}

export function ProviderHealthPage({data}: {data: Record<string, unknown>}) {
  const comparison = rows(data.comparison);
  const quarantine = rows(data.quarantine);
  const usage = rows(data.provider_usage);
  const health = rows(data.provider_health);
  const freshness = record(data.source_freshness);
  return <div className="page-stack"><PageHeader eyebrow="21 / PROVIDER RECONCILIATION" title="Provider Health" meta={String(data.canonical_decision ?? "N/A")} /><div className="kpi-grid compact"><KpiCard label="Diagnostics" value={comparison.length} /><KpiCard label="Quarantined discrepancies" value={quarantine.length} state={quarantine.length ? "WARNING" : "PASS"} /><KpiCard label="Adjustment convention" value={data.adjustment_convention_status} state="UNRESOLVED" /><KpiCard label="Silent averaging" value={data.no_silent_averaging ? "DISABLED" : "UNKNOWN"} state={data.no_silent_averaging ? "PASS" : "WARNING"} /><KpiCard label="Latest provider data" value={freshness.latest_available_data_date} /><KpiCard label="Source freshness" value={freshness.freshness_code} state={String(freshness.freshness_code ?? "UNAVAILABLE")} /></div>
    <Panel title="Provider lineage"><div className="contract-fields">{Array.isArray(data.provider_lineage) ? data.provider_lineage.map((provider) => <code key={String(provider)}>{String(provider)}</code>) : <span>UNAVAILABLE</span>}</div></Panel>
    <Panel title="Cross-provider diagnostics" meta="Price and return discrepancies remain separate"><DenseTable rows={comparison} columns={[{key: "diagnostic_dimension", label: "Dimension"}, {key: "comparison_id", label: "Comparison"}, {key: "overlap_rows", label: "Overlap"}, {key: "mean_abs_diff", label: "Mean abs diff"}, {key: "max_abs_diff", label: "Max abs diff"}, {key: "missing_date_difference_count", label: "Missing dates"}, {key: "adjustment_convention_status", label: "Adjustment"}, {key: "status", label: "State", render: (row) => <StatusBadge state={String(row.status)} />}]} compact /></Panel><Panel title="Deterministic quarantine reasons"><DenseTable rows={quarantine} columns={autoColumns(quarantine, 10)} compact /></Panel><div className="dashboard-grid equal"><Panel title="Provider usage"><DenseTable rows={usage} columns={autoColumns(usage, 7)} compact /></Panel><Panel title="Fetch health"><DenseTable rows={health} columns={[{key: "provider_name", label: "Provider"}, {key: "source_id", label: "Source"}, {key: "fetch_status", label: "Fetch"}, {key: "row_count", label: "Rows"}, {key: "health_status", label: "Health", render: (row) => <StatusBadge state={String(row.health_status)} />}]} compact /></Panel></div></div>;
}

export function ProvenancePage({data}: {data: Record<string, unknown>}) {
  const snapshot = record(data.snapshot);
  const checksums = record(data.checksums);
  const checksumRows = Object.entries(checksums).map(([artifact, digest]) => ({artifact, sha256: String(digest)}));
  return <div className="page-stack"><PageHeader eyebrow="23 / TRACEABILITY" title="Provenance & Audit" meta="Immutable snapshot lineage and checksums" /><div className="kpi-grid compact"><KpiCard label="Audit" value={data.audit_status} state={String(data.audit_status)} /><KpiCard label="PIT status" value={data.pit_status} state={String(data.pit_status)} /><KpiCard label="Snapshot" value={snapshot.snapshot_date} /><KpiCard label="Config hash" value={data.config_hash} /><KpiCard label="Code commit" value={snapshot.code_commit ?? data.code_commit} /></div><div className="dashboard-grid equal"><Panel title="Source lineage"><ol className="lineage-list">{Array.isArray(data.source_lineage) ? data.source_lineage.map((source) => <li key={String(source)}>{String(source)}</li>) : <li>UNAVAILABLE</li>}</ol></Panel><Panel title="Provider lineage"><div className="contract-fields">{Array.isArray(data.provider_lineage) ? data.provider_lineage.map((provider) => <code key={String(provider)}>{String(provider)}</code>) : <EmptyState title="No provider lineage" />}</div></Panel><Panel title="Goal lineage"><ol className="lineage-list">{Array.isArray(data.goal_lineage) ? data.goal_lineage.map((goal) => <li key={String(goal)}>{String(goal)}</li>) : <li>N/A</li>}</ol></Panel></div><Panel title="Artifact checksums" meta={`${checksumRows.length} immutable entries`}><DenseTable rows={checksumRows} columns={[{key: "artifact", label: "Artifact"}, {key: "sha256", label: "SHA-256"}]} compact /></Panel><Panel title="Workflow state"><pre className="data-pre">{JSON.stringify(data.workflow_state ?? {}, null, 2)}</pre></Panel></div>;
}

function rows(value: unknown): Row[] {return Array.isArray(value) ? value as Row[] : [];}
function record(value: unknown): Row {return value && typeof value === "object" && !Array.isArray(value) ? value as Row : {};}
function autoColumns(value: Row[], max: number): DenseColumn<Row>[] {return value.length ? Object.keys(value[0]).slice(0, max).map((key) => ({key, label: key.replaceAll("_", " ")})) : [{key: "state", label: "State", render: () => <span>No rows</span>}];}

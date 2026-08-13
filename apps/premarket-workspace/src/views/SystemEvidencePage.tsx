import { DenseTable, type DenseColumn } from "@/components/DenseTable";
import { EmptyState, KpiCard, PageHeader, Panel, StatusBadge } from "@/components/ui";
import { formatPercent } from "@/lib/format";

type Row = Record<string, unknown>;

export function DataQualityPage({data}: {data: Record<string, unknown>}) {
  const checks = rows(data.readiness_checks);
  const summary = rows(data.quality_summary);
  const quarantine = rows(data.quarantine);
  const status = record(data.status);
  const ifindReadiness = record(data.ifind_readiness);
  const ifindServices = rows(data.ifind_mcp_services);
  const ifindModules = rows(data.ifind_data_modules);
  const ifindPilot = record(data.ifind_pilot_acceptance);
  return <div className="page-stack"><PageHeader eyebrow="20 / EVIDENCE QUALITY" title="Data Quality" meta="PIT, freshness, completeness, and quarantine diagnostics" />
    <div className="kpi-grid compact"><KpiCard label="Execution mode" value={status.execution_mode} /><KpiCard label="Operational provider" value={status.operational_provider ?? "HISTORICAL REPLAY"} /><KpiCard label="Readiness checks" value={checks.length} /><KpiCard label="Quality artifacts" value={summary.length} /><KpiCard label="Quarantine rows" value={quarantine.length} state={quarantine.length ? "WARNING" : "PASS"} /><KpiCard label="Latest status" value={status.readiness_state} state={String(status.readiness_state)} /><KpiCard label="Target trading date" value={status.target_trading_date} /><KpiCard label="Expected T-1" value={status.expected_previous_trading_date} /><KpiCard label="Latest available" value={status.latest_available_data_date} /><KpiCard label="PIT / cutoff" value={status.data_cutoff} /></div>
    <IfindFoundationEvidence readiness={ifindReadiness} services={ifindServices} modules={ifindModules} pilot={ifindPilot} />
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
  const calendar = record(data.trading_calendar);
  const ifindReadiness = record(data.ifind_readiness);
  const ifindServices = rows(data.ifind_mcp_services);
  const ifindModules = rows(data.ifind_data_modules);
  const ifindPilot = record(data.ifind_pilot_acceptance);
  return <div className="page-stack"><PageHeader eyebrow="21 / PROVIDER RECONCILIATION" title="Provider Health" meta={String(data.canonical_decision ?? "N/A")} /><div className="kpi-grid compact"><KpiCard label="Operational provider" value={data.operational_provider ?? "HISTORICAL REPLAY"} /><KpiCard label="AKShare function" value={data.operational_function ?? "N/A"} /><KpiCard label="Accepted / rejected" value={`${String(data.accepted_symbol_count ?? "N/A")} / ${String(data.rejected_symbol_count ?? "N/A")}`} /><KpiCard label="East Money canonical requests" value={data.east_money_canonical_request_count ?? "N/A"} state={data.east_money_canonical_request_count === 0 ? "PASS" : "BLOCKED"} /><KpiCard label="Diagnostics" value={comparison.length} /><KpiCard label="Quarantined discrepancies" value={quarantine.length} state={quarantine.length ? "WARNING" : "PASS"} /><KpiCard label="Adjustment convention" value={data.adjustment_convention_status} state={data.adjustment_convention_status === "QFQ_ONLY" ? "PASS" : "UNRESOLVED"} /><KpiCard label="Amount contract" value={data.amount_availability ?? "N/A"} /><KpiCard label="Silent averaging" value={data.no_silent_averaging ? "DISABLED" : "UNKNOWN"} state={data.no_silent_averaging ? "PASS" : "WARNING"} /><KpiCard label="Latest provider data" value={freshness.latest_available_data_date} /><KpiCard label="Source freshness" value={freshness.freshness_code} state={String(freshness.freshness_code ?? "UNAVAILABLE")} /><KpiCard label="Calendar evidence" value={calendar.status ?? "UNAVAILABLE"} state={String(calendar.status ?? "UNAVAILABLE")} /><KpiCard label="Calendar coverage" value={calendar.coverage_end ?? "UNAVAILABLE"} warning={String(calendar.freshness_status ?? "UNAVAILABLE")} /></div>
    <IfindFoundationEvidence readiness={ifindReadiness} services={ifindServices} modules={ifindModules} pilot={ifindPilot} />
    <Panel title="Current operational provider lineage"><div className="contract-fields">{Array.isArray(data.provider_lineage) ? data.provider_lineage.map((provider) => <code key={String(provider)}>{String(provider)}</code>) : <span>UNAVAILABLE</span>}</div></Panel>
    {Array.isArray(data.historical_research_provider_lineage) ? <Panel title="Historical research provider lineage" meta="Separate from the current canonical refresh"><div className="contract-fields">{data.historical_research_provider_lineage.map((provider) => <code key={String(provider)}>{String(provider)}</code>)}</div></Panel> : null}
    <Panel title="Cross-provider diagnostics" meta="Price and return discrepancies remain separate"><DenseTable rows={comparison} columns={[{key: "diagnostic_dimension", label: "Dimension"}, {key: "comparison_id", label: "Comparison"}, {key: "overlap_rows", label: "Overlap"}, {key: "mean_abs_diff", label: "Mean abs diff"}, {key: "max_abs_diff", label: "Max abs diff"}, {key: "missing_date_difference_count", label: "Missing dates"}, {key: "adjustment_convention_status", label: "Adjustment"}, {key: "status", label: "State", render: (row) => <StatusBadge state={String(row.status)} />}]} compact /></Panel><Panel title="Deterministic quarantine reasons"><DenseTable rows={quarantine} columns={autoColumns(quarantine, 10)} compact /></Panel><div className="dashboard-grid equal"><Panel title="Provider usage"><DenseTable rows={usage} columns={autoColumns(usage, 7)} compact /></Panel><Panel title="Fetch health"><DenseTable rows={health} columns={[{key: "provider_name", label: "Provider"}, {key: "source_id", label: "Source"}, {key: "fetch_status", label: "Fetch"}, {key: "row_count", label: "Rows"}, {key: "health_status", label: "Health", render: (row) => <StatusBadge state={String(row.health_status)} />}]} compact /></Panel></div></div>;
}

function IfindFoundationEvidence({readiness, services, modules, pilot}: {readiness: Row; services: Row[]; modules: Row[]; pilot: Row}) {
  const state = String(readiness.readiness_state ?? "UNAVAILABLE");
  const credentialVerified = readiness.credential_verified === true;
  const liveAccessAllowed = readiness.live_access_allowed === true;
  const networkOptIn = readiness.network_opt_in === true;
  const providerOptIn = readiness.provider_opt_in === true;
  const mcpOptIn = readiness.mcp_opt_in === true;
  const dataCallOptIn = readiness.data_call_opt_in === true;
  const lastProbeStatus = String(readiness.last_probe_status ?? "NOT_RUN");
  const lastProbeFailure = String(readiness.last_probe_failure_code ?? "NONE");
  const pilotSymbols = rows(pilot.symbols);
  return <>
    <Panel title="iFinD AI financial data service readiness" meta={`${String(readiness.interface_mode ?? "UNAVAILABLE")} / Keychain-safe MCP contract`}>
      <div className="kpi-grid compact">
        <KpiCard label="Provider" value={readiness.provider_name ?? "同花顺 iFinD"} />
        <KpiCard label="Product" value={readiness.product_name ?? "AI 金融数据服务"} />
        <KpiCard label="Readiness" value={state} state={state} />
        <KpiCard label="Credential delivery" value={readiness.credential_delivery_policy ?? "UNAVAILABLE"} />
        <KpiCard label="Credential verified" value={credentialVerified ? "VERIFIED" : "PENDING HANDSHAKE"} state={credentialVerified ? "PASS" : "PENDING"} />
        <KpiCard label="Protocol" value={readiness.protocol_version ?? "UNAVAILABLE"} />
        <KpiCard label="Live access" value={liveAccessAllowed ? "ALLOWED" : "DISABLED"} state={liveAccessAllowed ? "READY" : "DISABLED"} />
        <KpiCard label="Network opt-in" value={networkOptIn ? "ENABLED" : "DISABLED"} />
        <KpiCard label="Provider opt-in" value={providerOptIn ? "ENABLED" : "DISABLED"} />
        <KpiCard label="MCP opt-in" value={mcpOptIn ? "ENABLED" : "DISABLED"} />
        <KpiCard label="Data-call opt-in" value={dataCallOptIn ? "ENABLED" : "DISABLED"} state={dataCallOptIn ? "WARNING" : "PASS"} />
        <KpiCard label="Last external probe" value={lastProbeStatus} state={lastProbeStatus} />
        <KpiCard label="Last probe result" value={lastProbeFailure} state={lastProbeFailure === "NONE" ? "PASS" : "BLOCKED"} />
        <KpiCard label="Last probe HTTP" value={readiness.last_probe_http_status ?? "N/A"} />
        <KpiCard label="Last probe observed" value={readiness.last_probe_observed_at ?? "NOT RUN"} />
        <KpiCard label="Live handshake" value={readiness.last_handshake_verified === true ? "VERIFIED" : "NOT VERIFIED"} state={readiness.last_handshake_verified === true ? "PASS" : "PENDING"} />
        <KpiCard label="Live input schemas" value={readiness.last_input_schemas_verified === true ? "VERIFIED" : "NOT VERIFIED"} state={readiness.last_input_schemas_verified === true ? "PASS" : "PENDING"} />
        <KpiCard label="Last data tool call" value={readiness.last_data_tool_called === true ? "YES" : "NO"} state={readiness.last_data_tool_called === true ? "WARNING" : "PASS"} />
        <KpiCard label="Last data call count" value={readiness.last_data_call_count ?? 0} />
        <KpiCard label="Last failed symbol" value={readiness.last_failed_symbol ?? "NONE"} />
        <KpiCard label="S1 identity acceptance" value={readiness.s1_identity_acceptance_verified === true ? "VERIFIED" : "NOT VERIFIED"} state={readiness.s1_identity_acceptance_verified === true ? "PASS" : "PENDING"} />
        <KpiCard label="S1 temporal class" value={readiness.s1_temporal_class ?? "UNAVAILABLE"} />
        <KpiCard label="Provider available_at" value={readiness.s1_provider_available_at_verified === true ? "VERIFIED" : "UNKNOWN"} state={readiness.s1_provider_available_at_verified === true ? "PASS" : "WARNING"} />
        <KpiCard label="Identity observed_at" value={readiness.s1_identity_observed_at ?? "NOT RECORDED"} />
        <KpiCard label="S1 staged symbols" value={readiness.s1_staged_symbol_count ?? 0} />
        <KpiCard label="iFinD canonical rows" value={readiness.ifind_canonical_accepted === true ? readiness.s2_normalized_row_count ?? 0 : 0} state={readiness.ifind_canonical_accepted === true ? "PASS" : "PENDING"} />
        <KpiCard label="S2 authorization" value={readiness.s2_last_status === "PASS" ? "COMPLETED" : readiness.s2_requires_separate_authorization === true ? "REQUIRED" : "LOCKED"} state={readiness.s2_last_status === "PASS" ? "PASS" : "PENDING"} />
        <KpiCard label="S2 offline foundation" value={readiness.s2_offline_foundation_state ?? "UNAVAILABLE"} state={readiness.s2_offline_foundation_state === "S2_OFFLINE_FOUNDATION_READY_AUTHORIZATION_REQUIRED" ? "READY" : "PENDING"} />
        <KpiCard label="S2 fixed tools" value={Array.isArray(readiness.s2_fixed_tools) ? readiness.s2_fixed_tools.join(" + ") : "UNAVAILABLE"} />
        <KpiCard label="S2 call budget" value={readiness.s2_data_call_budget ?? 0} />
        <KpiCard label="S2 daily sessions" value={readiness.s2_daily_session_count ?? 0} />
        <KpiCard label="S2 adjustment" value={readiness.s2_adjustment_mode ?? "UNAVAILABLE"} state={readiness.s2_adjustment_mode === "qfq" ? "PASS" : "PENDING"} />
        <KpiCard label="S2 live calls" value={readiness.s2_live_calls_authorized === true ? "AUTHORIZED" : "NOT AUTHORIZED"} state={readiness.s2_live_calls_authorized === true ? "WARNING" : "PASS"} />
        <KpiCard label="S2 last run" value={readiness.s2_last_status ?? "NOT RUN"} state={String(readiness.s2_last_status ?? "PENDING")} />
        <KpiCard label="S2 acceptance" value={readiness.s2_acceptance_state ?? "NOT ACCEPTED"} state={readiness.s2_canonical_accepted === true ? "PASS" : "PENDING"} />
        <KpiCard label="S2 failure" value={readiness.s2_failure_code ?? "NONE"} state={readiness.s2_failure_code ? "BLOCKED" : "PASS"} />
        <KpiCard label="S2 failure layer" value={readiness.s2_failure_stage ?? "NOT CAPTURED"} state={readiness.s2_failure_stage ? "BLOCKED" : "PENDING"} />
        <KpiCard label="S2 failure reason" value={readiness.s2_failure_reason ?? "NOT CAPTURED"} state={readiness.s2_failure_reason ? "BLOCKED" : "PENDING"} />
        <KpiCard label="S2 response shape" value={readiness.s2_response_shape_sha256 ? String(readiness.s2_response_shape_sha256).slice(0, 12) : "NOT CAPTURED"} warning="Metadata-only fingerprint; no provider values or raw payload" />
        <KpiCard label="S2 parsed shape" value={`${String(readiness.s2_shape_table_count ?? 0)} tables / ${String(readiness.s2_shape_column_count ?? 0)} columns / ${String(readiness.s2_shape_row_count ?? 0)} rows`} />
        <KpiCard label="S2 missing reviewed fields" value={Array.isArray(readiness.s2_missing_required_columns) && readiness.s2_missing_required_columns.length ? readiness.s2_missing_required_columns.join("; ") : "NONE RECORDED"} />
        <KpiCard label="S2 diagnostic raw payload" value={readiness.s2_diagnostic_raw_payload_persisted === true ? "INVALID" : "NOT PERSISTED"} state={readiness.s2_diagnostic_raw_payload_persisted === true ? "BLOCKED" : "PASS"} />
        <KpiCard label="S2 failed scope" value={readiness.s2_failed_symbol ? `${String(readiness.s2_failed_symbol)} / ${String(readiness.s2_failed_tool ?? "UNKNOWN")}` : "NONE"} />
        <KpiCard label="S2 calls used" value={`${String(readiness.s2_data_call_count ?? 0)} / ${String(readiness.s2_data_call_budget ?? 4)}`} />
        <KpiCard label="S2 normalized rows" value={readiness.s2_normalized_row_count ?? 0} />
        <KpiCard label="S2 bundle" value={readiness.s2_bundle_id ?? "NOT PERSISTED"} state={readiness.s2_bundle_persisted === true ? "PASS" : "PENDING"} />
        <KpiCard label="S2 manifest integrity" value={readiness.s2_bundle_manifest_sha256 ? String(readiness.s2_bundle_manifest_sha256).slice(0, 12) : "NOT ANCHORED"} state={readiness.s2_bundle_manifest_sha256 ? "PASS" : "PENDING"} />
        <KpiCard label="S2 Workspace integrity" value={readiness.s2_workspace_bundle_integrity_state ?? "NOT ACCEPTED"} state={readiness.s2_workspace_bundle_integrity_state === "PASS" ? "PASS" : "PENDING"} warning={readiness.s2_workspace_bundle_failure_code ? String(readiness.s2_workspace_bundle_failure_code) : undefined} />
        <KpiCard label="S2 Workspace bundle rows" value={`${String(readiness.s2_workspace_bundle_row_count ?? 0)} rows / ${String(readiness.s2_workspace_bundle_artifact_count ?? 0)} artifacts`} />
        <KpiCard label="S2 observed" value={readiness.s2_observed_at ?? "NOT RUN"} />
        <KpiCard label="S2 provider schema" value={readiness.s2_provider_schema_accepted === true ? "ACCEPTED" : "NOT ACCEPTED"} state={readiness.s2_provider_schema_accepted === true ? "PASS" : "PENDING"} />
        <KpiCard label="MCP services" value={readiness.supported_service_count ?? services.length} />
        <KpiCard label="Entitlement profile" value={readiness.entitlement_profile ?? "UNAVAILABLE"} />
        <KpiCard label="Reviewed / entitled tools" value={`${String(readiness.reviewed_tool_count ?? 0)} / ${String(readiness.expected_tool_count ?? 0)}`} />
        <KpiCard label="Unavailable by plan" value={readiness.unavailable_by_plan_count ?? 0} warning={Array.isArray(readiness.unavailable_by_plan) ? readiness.unavailable_by_plan.join(", ") : "NONE"} />
        <KpiCard label="Data modules" value={readiness.data_module_count ?? modules.length} />
        <KpiCard label="Raw payload commit" value={readiness.raw_payload_commit_allowed === false ? "FORBIDDEN" : "UNAVAILABLE"} state="PASS" />
        <KpiCard label="Local token persistence" value={readiness.local_token_persistence_allowed === false ? "FORBIDDEN" : "UNAVAILABLE"} state="PASS" />
      </div>
    </Panel>
    <Panel title="iFinD MCP service contract" meta={`${services.length} supplier services / No tools/call from this view`}>
      <DenseTable rows={services} columns={[
        {key: "server_type", label: "Service"},
        {key: "server_id", label: "Server ID"},
        {key: "endpoint_path", label: "Approved path"},
        {key: "reviewed_tool_count", label: "Reviewed tools"},
        {key: "expected_tool_count", label: "Entitled tools"},
        {key: "unavailable_by_plan", label: "Unavailable by plan"},
        {key: "implementation_state", label: "State", render: (row) => <StatusBadge state={String(row.implementation_state)} />},
      ]} searchPlaceholder="Search iFinD MCP services" compact />
    </Panel>
    <Panel title="iFinD data module readiness" meta={`${modules.length} governed modules / No recommendation or execution output`}>
      <DenseTable rows={modules} columns={[
        {key: "priority", label: "Priority"},
        {key: "module_id", label: "Module ID"},
        {key: "display_name", label: "Module"},
        {key: "mcp_services", label: "MCP services"},
        {key: "mcp_tools", label: "Reviewed tools"},
        {key: "intended_fields", label: "Intended fields"},
        {key: "pit_requirement", label: "PIT requirement"},
        {key: "known_gap", label: "Acceptance gap"},
        {key: "dashboard_surface", label: "Dashboard surface"},
        {key: "implementation_state", label: "State", render: (row) => <StatusBadge state={String(row.implementation_state)} />},
      ]} searchPlaceholder="Search iFinD data modules" compact />
    </Panel>
    <Panel title="iFinD dual-stock acceptance cohort" meta={`${String(pilot.cohort_id ?? "UNAVAILABLE")} / Canonical approved-symbol baseline unchanged`}>
      <DenseTable rows={pilotSymbols} columns={[
        {key: "symbol", label: "Symbol"},
        {key: "company_name_cn", label: "Company"},
        {key: "exchange", label: "Exchange"},
        {key: "existing_governance_state", label: "Governance"},
        {key: "pilot_acceptance_state", label: "Pilot state", render: (row) => <StatusBadge state={String(row.pilot_acceptance_state)} />},
        {key: "required_data_modules", label: "Required modules", render: (row) => Array.isArray(row.required_data_modules) ? row.required_data_modules.length : 0},
        {key: "actionable_use_allowed", label: "Actionable use", render: (row) => row.actionable_use_allowed === false ? "FORBIDDEN" : "UNAVAILABLE"},
      ]} searchPlaceholder="Search pilot symbols" compact />
    </Panel>
  </>;
}

export function ProvenancePage({data}: {data: Record<string, unknown>}) {
  const snapshot = record(data.snapshot);
  const checksums = record(data.checksums);
  const checksumRows = Object.entries(checksums).map(([artifact, digest]) => ({artifact, sha256: String(digest)}));
  return <div className="page-stack"><PageHeader eyebrow="23 / TRACEABILITY" title="Provenance & Audit" meta="Immutable snapshot lineage and checksums" /><div className="kpi-grid compact"><KpiCard label="Audit" value={data.audit_status} state={String(data.audit_status)} /><KpiCard label="PIT status" value={data.pit_status} state={String(data.pit_status)} /><KpiCard label="Snapshot ID" value={data.snapshot_id ?? snapshot.snapshot_date} /><KpiCard label="Operational provider" value={data.operational_provider ?? "HISTORICAL REPLAY"} /><KpiCard label="Batch checksum" value={data.operational_batch_checksum ?? "N/A"} /><KpiCard label="Snapshot checksum" value={data.snapshot_checksum ?? "N/A"} /><KpiCard label="Manifest checksum" value={data.refresh_manifest_checksum ?? "N/A"} /><KpiCard label="Config hash" value={data.config_hash} /><KpiCard label="Code commit" value={data.code_commit ?? snapshot.code_commit} /></div><div className="dashboard-grid equal"><Panel title="Operational source lineage"><ol className="lineage-list">{Array.isArray(data.operational_source_lineage) ? data.operational_source_lineage.map((source) => <li key={String(source)}>{String(source)}</li>) : <li>HISTORICAL REPLAY</li>}</ol></Panel><Panel title="Source lineage" meta="Immutable snapshot model inputs"><ol className="lineage-list">{Array.isArray(data.source_lineage) ? data.source_lineage.map((source) => <li key={String(source)}>{String(source)}</li>) : <li>UNAVAILABLE</li>}</ol></Panel><Panel title="Historical research providers"><div className="contract-fields">{Array.isArray(data.provider_lineage) ? data.provider_lineage.map((provider) => <code key={String(provider)}>{String(provider)}</code>) : <EmptyState title="No provider lineage" />}</div></Panel><Panel title="Goal lineage"><ol className="lineage-list">{Array.isArray(data.goal_lineage) ? data.goal_lineage.map((goal) => <li key={String(goal)}>{String(goal)}</li>) : <li>N/A</li>}</ol></Panel></div><Panel title="Artifact checksums" meta={`${checksumRows.length} immutable entries`}><DenseTable rows={checksumRows} columns={[{key: "artifact", label: "Artifact"}, {key: "sha256", label: "SHA-256"}]} compact /></Panel><Panel title="Workflow state"><pre className="data-pre">{JSON.stringify(data.workflow_state ?? {}, null, 2)}</pre></Panel></div>;
}

function rows(value: unknown): Row[] {return Array.isArray(value) ? value as Row[] : [];}
function record(value: unknown): Row {return value && typeof value === "object" && !Array.isArray(value) ? value as Row : {};}
function autoColumns(value: Row[], max: number): DenseColumn<Row>[] {return value.length ? Object.keys(value[0]).slice(0, max).map((key) => ({key, label: key.replaceAll("_", " ")})) : [{key: "state", label: "State", render: () => <span>No rows</span>}];}

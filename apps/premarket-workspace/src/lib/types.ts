export type Availability = "AVAILABLE" | "UNAVAILABLE";

export interface EvidenceValue<T = string | number | boolean> {
  value: T | null;
  asof_date: string | null;
  source: string | null;
  availability: Availability;
  quality_status: string;
  reason: string | null;
}

export interface WorkspaceStatus {
  readiness_state: string;
  freshness_code: string;
  target_trading_date: string;
  expected_previous_trading_date: string;
  latest_available_data_date: string;
  data_cutoff: string;
  execution_mode: string;
  snapshot_date?: string;
  execution_time?: string;
  provider_state?: string;
  holdings_mode?: string;
  current_panels_enabled?: boolean;
  latest_refresh_status?: string;
  last_successful_refresh_time?: string;
  data_freshness_badge?: string;
  refresh_validation_status?: string;
  refresh_manifest_integrity?: string;
  refresh_blocked_reasons?: string[];
  snapshot_version?: string;
  system_readiness_status?: string;
  historical_replay_status?: string;
  research_dashboard_status?: string;
  research_panels_enabled?: boolean;
  quant_page_status?: string;
  snapshot_resolution_status?: string;
  snapshot_resolution_warnings?: string[];
  snapshot_pointer_date?: string;
  snapshot_latest_discovered_date?: string;
  snapshot_stale?: boolean;
  calendar_status?: string;
  calendar_source?: string;
  calendar_coverage_end?: string;
  calendar_freshness_status?: string;
  calendar_evidence_status?: string;
}

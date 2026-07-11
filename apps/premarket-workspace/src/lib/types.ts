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
}

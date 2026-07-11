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
}

import type { EvidenceValue } from "@/lib/types";

export interface SnapshotIndexResponse {
  latest: string;
  snapshots: Array<{snapshot_date: string}>;
}

export interface StockSummary extends Record<string, unknown> {
  symbol: string;
  display_name: string;
}

export interface StockListResponse {
  count: number;
  rows: StockSummary[];
}

export interface StockDetailResponse extends StockSummary {
  latest_price?: EvidenceValue<number>;
  price_change?: EvidenceValue<number>;
  provider_lineage?: string[];
  freshness_state?: string;
}

export interface CandleRow {
  trade_date?: string;
  open?: number | null;
  high?: number | null;
  low?: number | null;
  close?: number | null;
  volume?: number | null;
  amount?: number | null;
  turnover?: number | null;
  source?: string | null;
  quality?: string | null;
}

export interface ProviderDiscrepancyMarker extends Record<string, unknown> {
  trade_date?: string;
}

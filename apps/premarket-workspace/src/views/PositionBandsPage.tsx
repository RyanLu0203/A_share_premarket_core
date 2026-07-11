"use client";

import { useState } from "react";
import Link from "next/link";

import { DenseTable, type DenseColumn } from "@/components/DenseTable";
import { PageHeader, StatusBadge } from "@/components/ui";
import { formatPercent } from "@/lib/format";

type Band = Record<string, unknown> & {symbol: string; band_status: string};

export function PositionBandsPage({data}: {data: {rows: Band[]; distribution: Record<string, number>; allowed_states: string[]}}) {
  const [filter, setFilter] = useState("ALL");
  const rows = filter === "ALL" ? data.rows : data.rows.filter((row) => row.band_status === filter);
  const columns: DenseColumn<Band>[] = [
    {key: "symbol", label: "Symbol", render: (row) => <Link href={`/stocks/${row.symbol}`}>{row.symbol}</Link>},
    {key: "display_name", label: "Name"},
    {key: "current_weight", label: "Current", render: (row) => formatPercent(row.current_weight)},
    {key: "acceptable_band_min", label: "Band min", render: (row) => formatPercent(row.acceptable_band_min)},
    {key: "acceptable_band_max", label: "Band max", render: (row) => formatPercent(row.acceptable_band_max)},
    {key: "reference_policy_weight", label: "Reference", render: (row) => formatPercent(row.reference_policy_weight)},
    {key: "band_status", label: "Status", render: (row) => <StatusBadge state={row.band_status} />},
    {key: "confidence", label: "Confidence", render: (row) => formatPercent(row.confidence)},
    {key: "risk_contribution", label: "Risk contribution", render: (row) => formatPercent(row.risk_contribution)},
    {key: "constraint_breach", label: "Constraint"},
    {key: "abstain", label: "Abstain", render: (row) => <StatusBadge state={Boolean(row.abstain) ? "ABSTAIN" : "NOT_ABSTAIN"} />},
    {key: "provider_quality", label: "Provider"},
  ];
  return <div className="page-stack"><PageHeader eyebrow="07 / POSITION MANAGEMENT" title="Position Bands" meta="Research-only acceptable ranges / No directional instruction" actions={<label className="select-control"><span>Band status</span><select value={filter} onChange={(event) => setFilter(event.target.value)}><option>ALL</option>{data.allowed_states.map((state) => <option key={state}>{state}</option>)}</select></label>} /><div className="summary-strip">{Object.entries(data.distribution).map(([state, count]) => <div key={state}><StatusBadge state={state} /><strong>{count}</strong></div>)}</div><DenseTable rows={rows} columns={columns} searchPlaceholder="Search band evidence" /></div>;
}

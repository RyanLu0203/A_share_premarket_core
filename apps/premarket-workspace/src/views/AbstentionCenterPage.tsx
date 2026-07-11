import { Link2 } from "lucide-react";
import Link from "next/link";

import { DenseTable, type DenseColumn } from "@/components/DenseTable";
import { PageHeader, Panel, StatusBadge } from "@/components/ui";
import { formatPercent } from "@/lib/format";

type Abstention = Record<string, unknown> & {symbol: string; reason_codes: string[]};

export function AbstentionCenterPage({data}: {data: {count: number; reason_distribution: Record<string, number>; rows: Abstention[]}}) {
  const columns: DenseColumn<Abstention>[] = [
    {key: "symbol", label: "Symbol", render: (row) => <Link href={`/stocks/${row.symbol}`}>{row.symbol}<Link2 aria-hidden="true" /></Link>},
    {key: "reason_codes", label: "Reason codes", render: (row) => <div className="reason-codes">{row.reason_codes.map((reason) => <code key={reason}>{reason}</code>)}</div>},
    {key: "confidence", label: "Confidence", render: (row) => formatPercent(row.confidence)},
    {key: "provider_discrepancy", label: "Provider discrepancy"},
    {key: "regime_instability", label: "Regime instability"},
    {key: "covariance_sensitivity", label: "Covariance sensitivity"},
    {key: "band_sensitivity", label: "Band sensitivity"},
    {key: "history_sufficiency", label: "History sufficiency"},
    {key: "data_availability", label: "Data availability"},
    {key: "provider_quality", label: "Provider quality"},
    {key: "abstain", label: "State", render: () => <StatusBadge state="ABSTAIN" />},
  ];
  return <div className="page-stack"><PageHeader eyebrow="10 / EVIDENCE SUFFICIENCY" title="Abstention Center" meta={`${data.count} symbols without a precise band`} /><Panel title="Reason distribution"><div className="reason-distribution">{Object.entries(data.reason_distribution).map(([reason, count]) => <div key={reason}><code>{reason}</code><strong>{count}</strong></div>)}</div></Panel><DenseTable rows={data.rows} columns={columns} searchPlaceholder="Search abstentions" /></div>;
}

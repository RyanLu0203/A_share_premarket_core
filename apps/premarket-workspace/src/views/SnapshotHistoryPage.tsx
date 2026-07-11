import { ExternalLink } from "lucide-react";

import { DenseTable, type DenseColumn } from "@/components/DenseTable";
import { PageHeader, StatusBadge } from "@/components/ui";

type Snapshot = Record<string, unknown> & {snapshot_date: string};

export function SnapshotHistoryPage({data, onSelect}: {data: {latest: string; snapshots: Snapshot[]}; onSelect: (snapshot: string) => void}) {
  const columns: DenseColumn<Snapshot>[] = [
    {key: "snapshot_date", label: "Snapshot"},
    {key: "execution_mode", label: "Mode"},
    {key: "execution_time", label: "Execution time"},
    {key: "target_trading_date", label: "Target"},
    {key: "data_cutoff", label: "Cutoff"},
    {key: "latest_available_data_date", label: "Latest data"},
    {key: "freshness_code", label: "Freshness", render: (row) => <StatusBadge state={String(row.freshness_code)} />},
    {key: "readiness_state", label: "Readiness", render: (row) => <StatusBadge state={String(row.readiness_state)} />},
    {key: "config_hash", label: "Config hash"},
    {key: "checksums", label: "Checksums", render: (row) => `${row.checksums && typeof row.checksums === "object" ? Object.keys(row.checksums).length : 0} artifacts`},
    {key: "snapshot_integrity", label: "Integrity", render: (row) => <StatusBadge state={String(row.snapshot_integrity)} />},
    {key: "open", label: "", render: (row) => <button className="icon-button" aria-label={`Open snapshot ${row.snapshot_date}`} onClick={() => onSelect(row.snapshot_date)}><ExternalLink aria-hidden="true" /></button>},
  ];
  return <div className="page-stack"><PageHeader eyebrow="22 / IMMUTABLE HISTORY" title="Snapshot History" meta={`Latest validated snapshot ${data.latest}`} /><DenseTable rows={data.snapshots} columns={columns} searchPlaceholder="Search snapshots" /></div>;
}

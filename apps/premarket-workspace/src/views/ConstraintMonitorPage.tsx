import { DenseTable, type DenseColumn } from "@/components/DenseTable";
import { KpiCard, PageHeader, StatusBadge } from "@/components/ui";
import { formatNumber } from "@/lib/format";

type Constraint = Record<string, unknown> & {constraint_id: string; state: string};

export function ConstraintMonitorPage({data}: {data: {constraint_count: number; substantive_constraint_count: number; summary: Constraint[]; details: Array<Record<string, unknown>>}}) {
  const columns: DenseColumn<Constraint>[] = [
    {key: "constraint_id", label: "Constraint"},
    {key: "current_value", label: "Current", render: (row) => formatNumber(row.current_value, 4)},
    {key: "threshold", label: "Threshold"},
    {key: "breach", label: "Breach", render: (row) => String(row.breach)},
    {key: "severity", label: "Severity"},
    {key: "evidence_availability", label: "Evidence", render: (row) => Array.isArray(row.evidence_availability) ? row.evidence_availability.join(" / ") : String(row.evidence_availability)},
    {key: "fail_closed", label: "Fail closed", render: (row) => String(row.fail_closed)},
    {key: "state", label: "State", render: (row) => <StatusBadge state={row.state} />},
  ];
  return <div className="page-stack"><PageHeader eyebrow="09 / CONTROL BOUNDARIES" title="Constraint Monitor" meta="All operationalized research constraints" /><div className="kpi-grid compact"><KpiCard label="Constraints" value={data.constraint_count} /><KpiCard label="Substantive" value={data.substantive_constraint_count} /><KpiCard label="Fail closed" value={data.summary.filter((row) => row.state === "FAIL_CLOSED").length} state="FAIL_CLOSED" /><KpiCard label="Breaches" value={data.summary.filter((row) => Boolean(row.breach)).length} state="BREACH" /></div><DenseTable rows={data.summary} columns={columns} searchPlaceholder="Search constraints" /></div>;
}

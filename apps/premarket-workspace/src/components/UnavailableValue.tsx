import type { EvidenceValue } from "@/lib/types";

export function UnavailableValue({label, evidence}: {label: string; evidence: EvidenceValue}) {
  if (evidence.availability === "AVAILABLE") {
    return (
      <div className="evidence-value">
        <span>{label}</span>
        <strong>{String(evidence.value)}</strong>
        <small>{evidence.asof_date ?? "No date"} / {evidence.source ?? "Unknown source"}</small>
      </div>
    );
  }
  return (
    <div className="evidence-value is-unavailable">
      <span>{label}</span>
      <strong>N/A</strong>
      <b>UNAVAILABLE</b>
      <small>{evidence.reason}</small>
    </div>
  );
}

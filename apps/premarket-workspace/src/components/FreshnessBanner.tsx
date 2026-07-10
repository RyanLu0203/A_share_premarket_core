import { AlertTriangle, ArrowRight, Clock3, Database } from "lucide-react";

import type { WorkspaceStatus } from "@/lib/types";

export function FreshnessBanner({status}: {status: WorkspaceStatus}) {
  const blocked = status.readiness_state === "BLOCKED";
  return (
    <section className={`freshness-banner ${blocked ? "is-blocked" : "is-ready"}`} role={blocked ? "alert" : "status"}>
      <div className="freshness-verdict">
        {blocked ? <AlertTriangle aria-hidden="true" /> : <Database aria-hidden="true" />}
        <div>
          <span className="eyebrow">DATA READINESS</span>
          <strong>{status.readiness_state}</strong>
          <span className="freshness-code">{status.freshness_code}</span>
        </div>
      </div>
      <div className="evidence-timeline" aria-label="Data freshness timeline">
        <TimelineNode label="Target trading date" value={status.target_trading_date} />
        <ArrowRight aria-hidden="true" />
        <TimelineNode label="Expected T-1" value={status.expected_previous_trading_date} />
        <ArrowRight aria-hidden="true" />
        <TimelineNode label="Latest available" value={status.latest_available_data_date} stale={blocked} />
      </div>
      <div className="freshness-meta"><Clock3 aria-hidden="true" /> Cutoff {status.data_cutoff} / {status.execution_mode}</div>
    </section>
  );
}

function TimelineNode({label, value, stale = false}: {label: string; value: string; stale?: boolean}) {
  return <div className={`timeline-node ${stale ? "is-stale" : ""}`}><span>{label}</span><strong>{value}</strong></div>;
}

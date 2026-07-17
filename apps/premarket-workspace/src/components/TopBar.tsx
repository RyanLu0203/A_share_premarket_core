import { CalendarClock, Database, Radio, RotateCcw } from "lucide-react";

import type { WorkspaceStatus } from "@/lib/types";

interface TopBarProps {
  pageTitle: string;
  status: WorkspaceStatus;
  mode: "live" | "replay";
  snapshots: string[];
  onModeChange: (mode: "live" | "replay") => void;
  onSnapshotChange: (snapshot: string) => void;
}

export function TopBar({pageTitle, status, mode, snapshots, onModeChange, onSnapshotChange}: TopBarProps) {
  return (
    <header className="topbar">
      <div className="brand-lockup">
        <span className="brand-mark">AS</span>
        <div><strong>A-Share Premarket Workspace</strong><span>{pageTitle}</span></div>
      </div>
      <div className="topbar-context">
        <Context label="Portfolio" value={status.holdings_mode ?? "RESEARCH REFERENCE PORTFOLIO"} />
        <label className="context-block snapshot-select">
          <span>Snapshot</span>
          <select value={status.snapshot_date ?? snapshots[0] ?? ""} onChange={(event) => onSnapshotChange(event.target.value)} disabled={mode === "live"}>
            {snapshots.map((snapshot) => <option key={snapshot}>{snapshot}</option>)}
          </select>
        </label>
        <Context label="Target" value={status.target_trading_date} />
        <Context label="Latest data" value={status.latest_available_data_date} />
        <Context label="Readiness" value={status.readiness_state} tone={status.readiness_state === "BLOCKED" ? "critical" : "warning"} />
        <Context label="Provider" value={status.operational_provider ?? status.provider_state ?? "UNKNOWN"} tone={status.operational_provider ? "neutral" : "warning"} />
      </div>
      <div className="mode-cluster">
        <div className="segmented-control" aria-label="Execution mode">
          <button className={mode === "live" ? "is-active" : ""} onClick={() => onModeChange("live")} aria-label="Live readiness"><Radio aria-hidden="true" />Live</button>
          <button className={mode === "replay" ? "is-active" : ""} onClick={() => onModeChange("replay")} aria-label="Deterministic replay"><RotateCcw aria-hidden="true" />Replay</button>
        </div>
        <span className={`mode-badge ${mode}`}><CalendarClock aria-hidden="true" />{mode === "replay" ? "DETERMINISTIC REPLAY" : "DAILY OPERATIONAL"}</span>
      </div>
    </header>
  );
}

function Context({label, value, tone = "neutral"}: {label: string; value: string; tone?: "neutral" | "warning" | "critical"}) {
  const fieldClass = label === "Provider" ? "context-provider" : "";
  return <div className={`context-block tone-${tone} ${fieldClass}`}><span>{label}</span><strong>{label === "Latest data" ? <Database aria-hidden="true" /> : null}{value}</strong></div>;
}

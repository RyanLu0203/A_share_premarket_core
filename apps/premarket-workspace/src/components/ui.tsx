import { AlertCircle, Database, LoaderCircle } from "lucide-react";
import type { ReactNode } from "react";

import { formatNumber } from "@/lib/format";

export function PageHeader({eyebrow, title, meta, actions}: {eyebrow: string; title: string; meta?: string; actions?: ReactNode}) {
  return <header className="page-header"><div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1>{meta ? <p>{meta}</p> : null}</div>{actions ? <div className="page-actions">{actions}</div> : null}</header>;
}

export function Panel({title, meta, children, className = ""}: {title: string; meta?: string; children: ReactNode; className?: string}) {
  return <section className={`panel ${className}`}><header><div><h2>{title}</h2>{meta ? <span>{meta}</span> : null}</div></header><div className="panel-body">{children}</div></section>;
}

export function KpiCard({label, value, state, timestamp, warning, format = "plain"}: {label: string; value: unknown; state?: string; timestamp?: string; warning?: string; format?: "plain" | "percent"}) {
  const rendered = format === "percent" && typeof value === "number" ? `${(value * 100).toFixed(2)}%` : formatNumber(value);
  const longValue = String(rendered).length > 16 && !String(rendered).includes(" ");
  return <article className={`kpi-card ${longValue ? "is-long" : ""}`}><span>{label}</span><strong>{rendered}</strong>{state ? <StatusBadge state={state} /> : null}{timestamp ? <small>{timestamp}</small> : null}{warning ? <small className="kpi-warning">{warning}</small> : null}</article>;
}

export function StatusBadge({state}: {state: string}) {
  const tone = state.toLowerCase().replaceAll("_", "-");
  return <span className={`status-badge status-${tone}`}>{state}</span>;
}

export function EmptyState({title, detail}: {title: string; detail?: string}) {
  return <div className="empty-state"><Database aria-hidden="true" /><strong>{title}</strong>{detail ? <span>{detail}</span> : null}</div>;
}

export function LoadingState() {
  return <div className="loading-state" role="status"><LoaderCircle aria-hidden="true" /><span>Loading validated evidence</span></div>;
}

export function ErrorState({message}: {message: string}) {
  return <div className="error-state" role="alert"><AlertCircle aria-hidden="true" /><strong>Evidence unavailable</strong><span>{message}</span></div>;
}

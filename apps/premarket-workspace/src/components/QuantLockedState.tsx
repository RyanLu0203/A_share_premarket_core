import { LockKeyhole } from "lucide-react";

export function QuantLockedState({title, readyFactorCount, state}: {title: string; readyFactorCount: number; state: string}) {
  return (
    <section className="locked-state" aria-label={`${title} locked state`}>
      <LockKeyhole aria-hidden="true" />
      <div><span className="eyebrow">QUANT RESEARCH</span><h2>{title}</h2></div>
      <strong>LOCKED</strong>
      <code>ready_factor_count = {readyFactorCount}</code>
      <p>{state}</p>
    </section>
  );
}

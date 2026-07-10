import { ShieldAlert } from "lucide-react";


export function BlockedCurrentStateNotice() {
  return <section className="blocked-current-state" role="alert"><ShieldAlert aria-hidden="true" /><div><strong>CURRENT-STATE PANELS DISABLED</strong><span>Values below are immutable snapshot evidence, not a current operational state. Deterministic replay remains available.</span></div></section>;
}

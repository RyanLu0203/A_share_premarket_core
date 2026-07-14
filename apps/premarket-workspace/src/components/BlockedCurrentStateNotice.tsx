import { ShieldAlert } from "lucide-react";


export function BlockedCurrentStateNotice() {
  return <section className="blocked-current-state" role="alert"><ShieldAlert aria-hidden="true" /><div><strong>LIVE OPERATIONAL READINESS BLOCKED</strong><span>Research snapshot panels remain available with warning and are not a current operational state. Verified historical replay remains available.</span></div></section>;
}

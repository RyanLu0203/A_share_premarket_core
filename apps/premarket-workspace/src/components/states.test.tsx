import { render, screen } from "@testing-library/react";

import { FreshnessBanner } from "@/components/FreshnessBanner";
import { BlockedCurrentStateNotice } from "@/components/BlockedCurrentStateNotice";
import { QuantLockedState } from "@/components/QuantLockedState";
import { UnavailableValue } from "@/components/UnavailableValue";

describe("governed workspace states", () => {
  it("surfaces stale evidence as a blocking timeline", () => {
    render(
      <FreshnessBanner
        status={{
          readiness_state: "BLOCKED",
          freshness_code: "STALE_SOURCE_DATA",
          target_trading_date: "2026-07-09",
          expected_previous_trading_date: "2026-07-08",
          latest_available_data_date: "2026-06-30",
          data_cutoff: "2026-07-08",
          execution_mode: "daily_operational",
          latest_refresh_status: "BLOCKED",
          last_successful_refresh_time: "2026-07-01T08:30:00+08:00",
          data_freshness_badge: "STALE_SOURCE_DATA",
          refresh_validation_status: "BLOCKED",
          refresh_blocked_reasons: ["STALE_SOURCE_DATA"],
          snapshot_version: "sha256:abc123",
        }}
      />,
    );
    expect(screen.getByRole("alert")).toHaveTextContent("BLOCKED");
    expect(screen.getByRole("alert")).toHaveTextContent("STALE_SOURCE_DATA");
    expect(screen.getByText("2026-07-08")).toBeVisible();
    expect(screen.getByText("2026-06-30")).toBeVisible();
    expect(screen.getByText("Refresh BLOCKED")).toBeVisible();
    expect(screen.getByText("Validation BLOCKED")).toBeVisible();
    expect(screen.getByText("STALE_SOURCE_DATA", {selector: ".refresh-blocked-reason"})).toBeVisible();
    expect(screen.getByText("sha256:abc123")).toBeVisible();
  });

  it("marks live current-state panels disabled while preserving replay evidence", () => {
    render(<BlockedCurrentStateNotice />);
    expect(screen.getByRole("alert")).toHaveTextContent("CURRENT-STATE PANELS DISABLED");
    expect(screen.getByRole("alert")).toHaveTextContent("immutable snapshot evidence");
  });

  it("renders missing fundamentals without fallback numbers", () => {
    render(
      <UnavailableValue
        label="Revenue"
        evidence={{
          value: null,
          asof_date: null,
          source: null,
          availability: "UNAVAILABLE",
          quality_status: "NO_COMMITTED_EVIDENCE",
          reason: "field is not present in committed evidence",
        }}
      />,
    );
    expect(screen.getByText("N/A")).toBeVisible();
    expect(screen.getByText("UNAVAILABLE")).toBeVisible();
    expect(screen.getByText(/not present in committed evidence/)).toBeVisible();
  });

  it("keeps recommendation tiering locked at zero ready factors", () => {
    render(<QuantLockedState title="Recommendation Tiering" readyFactorCount={0} state="locked_future" />);
    expect(screen.getByText("LOCKED")).toBeVisible();
    expect(screen.getByText("ready_factor_count = 0")).toBeVisible();
    expect(screen.queryByText(/BUY|SELL|HOLD/)).not.toBeInTheDocument();
  });
});

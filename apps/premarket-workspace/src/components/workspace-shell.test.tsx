import { fireEvent, render, screen } from "@testing-library/react";

import { TopBar } from "@/components/TopBar";
import { resolveWorkspacePage } from "@/views/resolveWorkspacePage";
import type { WorkspaceStatus } from "@/lib/types";

const replayStatus: WorkspaceStatus = {
  readiness_state: "READY_WITH_WARNINGS",
  freshness_code: "FRESH_T_MINUS_ONE_DATA",
  target_trading_date: "2026-07-01",
  expected_previous_trading_date: "2026-06-30",
  latest_available_data_date: "2026-06-30",
  data_cutoff: "2026-06-30",
  execution_mode: "deterministic_replay",
  snapshot_date: "2026-07-01",
  provider_state: "WARNINGS_QUARANTINED",
  holdings_mode: "RESEARCH REFERENCE PORTFOLIO",
};

describe("workspace application shell", () => {
  it("shows every governed global context field", () => {
    render(
      <TopBar
        pageTitle="Command Center"
        status={replayStatus}
        mode="replay"
        snapshots={["2026-07-01"]}
        onModeChange={() => undefined}
        onSnapshotChange={() => undefined}
      />,
    );
    expect(screen.getByText("A-Share Premarket Workspace")).toBeVisible();
    expect(screen.getByText("RESEARCH REFERENCE PORTFOLIO")).toBeVisible();
    expect(screen.getAllByText("2026-07-01").length).toBeGreaterThan(0);
    expect(screen.getByText("DETERMINISTIC REPLAY")).toBeVisible();
    expect(screen.getByText("2026-06-30")).toBeVisible();
    expect(screen.getByText("READY_WITH_WARNINGS")).toBeVisible();
    expect(screen.getByText("WARNINGS_QUARANTINED")).toBeVisible();
  });

  it("switches execution mode through a segmented control", () => {
    const onModeChange = vi.fn();
    render(
      <TopBar
        pageTitle="Command Center"
        status={replayStatus}
        mode="replay"
        snapshots={["2026-07-01"]}
        onModeChange={onModeChange}
        onSnapshotChange={() => undefined}
      />,
    );
    fireEvent.click(screen.getByRole("button", {name: "Live readiness"}));
    expect(onModeChange).toHaveBeenCalledWith("live");
  });

  it("resolves available, locked, hybrid, and symbol-detail routes", () => {
    expect(resolveWorkspacePage("/").pageId).toBe(1);
    expect(resolveWorkspacePage("/stocks/000333.SZ")).toMatchObject({pageId: 4, symbol: "000333.SZ"});
    expect(resolveWorkspacePage("/quant/regime")).toMatchObject({pageId: 14, kind: "HYBRID"});
    expect(resolveWorkspacePage("/quant/recommendation-tiering")).toMatchObject({pageId: 17, kind: "LOCKED"});
    expect(resolveWorkspacePage("/system/provenance").pageId).toBe(23);
  });
});

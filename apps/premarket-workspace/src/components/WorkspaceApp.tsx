"use client";

import { useEffect, useMemo, useState } from "react";
import { usePathname } from "next/navigation";

import { FreshnessBanner } from "@/components/FreshnessBanner";
import { BlockedCurrentStateNotice } from "@/components/BlockedCurrentStateNotice";
import { Sidebar } from "@/components/Sidebar";
import { TopBar } from "@/components/TopBar";
import { ErrorState, LoadingState } from "@/components/ui";
import { usePageEvidence } from "@/hooks/usePageEvidence";
import { fetchWorkspaceJson, withQuery } from "@/lib/api";
import { navigationItemForPath } from "@/lib/navigation";
import type { WorkspaceStatus } from "@/lib/types";
import { AbstentionCenterPage } from "@/views/AbstentionCenterPage";
import { CommandCenterPage } from "@/views/CommandCenterPage";
import { ConstraintMonitorPage } from "@/views/ConstraintMonitorPage";
import { ExperimentPage } from "@/views/ExperimentPage";
import { MarketContextPage } from "@/views/MarketContextPage";
import { PortfolioOverviewPage } from "@/views/PortfolioOverviewPage";
import { PositionBandsPage } from "@/views/PositionBandsPage";
import { QuantWorkspacePage } from "@/views/QuantWorkspacePage";
import { resolveWorkspacePage } from "@/views/resolveWorkspacePage";
import { RiskMonitorPage } from "@/views/RiskMonitorPage";
import { SnapshotHistoryPage } from "@/views/SnapshotHistoryPage";
import { StockDetailPage } from "@/views/StockDetailPage";
import { StockExplorerPage } from "@/views/StockExplorerPage";
import { DataQualityPage, ProvenancePage, ProviderHealthPage } from "@/views/SystemEvidencePage";
import { WatchlistPage } from "@/views/WatchlistPage";

const emptyStatus: WorkspaceStatus = {
  readiness_state: "LOADING",
  freshness_code: "AWAITING_LOCAL_API",
  target_trading_date: "N/A",
  expected_previous_trading_date: "N/A",
  latest_available_data_date: "N/A",
  data_cutoff: "N/A",
  execution_mode: "local_research_only",
  holdings_mode: "RESEARCH REFERENCE PORTFOLIO",
};

export function WorkspaceApp() {
  const pathname = usePathname() || "/";
  const resolved = resolveWorkspacePage(pathname);
  const item = navigationItemForPath(pathname);
  const [mode, setMode] = useState<"live" | "replay">("live");
  const [snapshots, setSnapshots] = useState<string[]>([]);
  const [snapshotDate, setSnapshotDate] = useState<string>();
  const [status, setStatus] = useState<WorkspaceStatus>(emptyStatus);
  const [statusError, setStatusError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    void fetchWorkspaceJson<{latest: string; snapshots: Array<{snapshot_date: string}>}>("/api/snapshots", controller.signal)
      .then((result) => {
        const dates = result.snapshots.map((snapshot) => snapshot.snapshot_date);
        setSnapshots(dates);
        setSnapshotDate((current) => current ?? result.latest);
      })
      .catch((reason: unknown) => setStatusError(reason instanceof Error ? reason.message : String(reason)));
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    const path = withQuery("/api/status", {mode, snapshot_date: snapshotDate});
    void fetchWorkspaceJson<WorkspaceStatus>(path, controller.signal)
      .then((result) => {setStatus(result); setStatusError(null);})
      .catch((reason: unknown) => {if (!controller.signal.aborted) setStatusError(reason instanceof Error ? reason.message : String(reason));});
    return () => controller.abort();
  }, [mode, snapshotDate]);

  const evidence = usePageEvidence(resolved.pageId, resolved.symbol, mode, snapshotDate);
  const view = useMemo(() => renderPage(resolved.pageId, evidence.data, resolved.symbol, (selected) => {setMode("replay"); setSnapshotDate(selected);}), [evidence.data, resolved.pageId, resolved.symbol]);

  return <div className="workspace-shell">
    <Sidebar pathname={pathname} />
    <div className="workspace-main">
      <TopBar pageTitle={item.label} status={status} mode={mode} snapshots={snapshots} onModeChange={setMode} onSnapshotChange={setSnapshotDate} />
      <main className="workspace-content">
        {statusError ? <ErrorState message={`Local API status unavailable: ${statusError}`} /> : null}
        {status.readiness_state === "BLOCKED" && resolved.pageId !== 1 ? <FreshnessBanner status={status} /> : null}
        {mode === "live" && status.current_panels_enabled === false && resolved.pageId !== 1 ? <BlockedCurrentStateNotice /> : null}
        {evidence.loading ? <LoadingState /> : evidence.error ? <ErrorState message={evidence.error} /> : view}
      </main>
      <footer className="workspace-footer">LOCAL RESEARCH-ONLY WORKSPACE / NOT TRADING ADVICE / NOT FOR EXECUTION</footer>
    </div>
  </div>;
}

function renderPage(pageId: number, data: Record<string, unknown>, symbol: string | undefined, onSnapshot: (date: string) => void) {
  switch (pageId) {
    case 1: return <CommandCenterPage data={data.command as React.ComponentProps<typeof CommandCenterPage>["data"]} />;
    case 2: return <WatchlistPage seed={record(data.watchlist).symbols as string[] ?? []} stocks={(record(data.stocks).rows ?? []) as React.ComponentProps<typeof WatchlistPage>["stocks"]} />;
    case 3: return <StockExplorerPage data={data.stocks as React.ComponentProps<typeof StockExplorerPage>["data"]} />;
    case 4: return <StockDetailPage detail={record(data.detail) as React.ComponentProps<typeof StockDetailPage>["detail"]} market={record(data.market)} fundamentals={record(data.fundamentals)} risk={record(data.risk)} position={record(data.position)} />;
    case 5: return <MarketContextPage data={record(data.marketContext)} />;
    case 6: return <PortfolioOverviewPage data={record(data.portfolio)} />;
    case 7: return <PositionBandsPage data={data.bands as React.ComponentProps<typeof PositionBandsPage>["data"]} />;
    case 8: return <RiskMonitorPage data={record(data.risk)} />;
    case 9: return <ConstraintMonitorPage data={data.constraints as React.ComponentProps<typeof ConstraintMonitorPage>["data"]} />;
    case 10: return <AbstentionCenterPage data={data.abstentions as React.ComponentProps<typeof AbstentionCenterPage>["data"]} />;
    case 11: case 12: case 13: case 14: case 15: case 16: case 17: return <QuantWorkspacePage pageId={pageId} capabilities={data.capabilities as React.ComponentProps<typeof QuantWorkspacePage>["capabilities"]} marketContext={record(data.marketContext)} />;
    case 18: case 19: return <ExperimentPage pageId={pageId} data={record(data.experiment)} />;
    case 20: return <DataQualityPage data={record(data.quality)} />;
    case 21: return <ProviderHealthPage data={record(data.provider)} />;
    case 22: return <SnapshotHistoryPage data={data.snapshots as React.ComponentProps<typeof SnapshotHistoryPage>["data"]} onSelect={onSnapshot} />;
    case 23: return <ProvenancePage data={record(data.provenance)} />;
    default: return <ErrorState message={`Unknown workspace page ${pageId}${symbol ? ` for ${symbol}` : ""}`} />;
  }
}

function record(value: unknown): Record<string, unknown> {return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : {};}

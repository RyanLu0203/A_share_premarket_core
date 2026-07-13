"use client";

import { useCallback, useMemo } from "react";

import { useWorkspaceRequest } from "@/hooks/useWorkspaceRequest";
import { workspaceApi } from "@/lib/api/client";
import { endpointPlanForPage } from "@/lib/api/page-plan";
import { withQuery } from "@/lib/api/routes";

const EMPTY_EVIDENCE: Record<string, unknown> = {};

export function usePageEvidence(pageId: number, symbol: string | undefined, mode: "live" | "replay", snapshotDate: string | undefined) {
  const requestKey = `${pageId}:${symbol ?? ""}:${mode}:${snapshotDate ?? ""}`;
  const plan = useMemo(() => endpointPlanForPage(pageId, symbol).map((item) => ({
    ...item,
    path: withQuery(item.path, {
        mode: pageId === 1 ? mode : undefined,
        snapshot_date: snapshotDate,
    }),
  })), [mode, pageId, snapshotDate, symbol]);
  const request = useCallback((signal: AbortSignal) => workspaceApi.bundle(plan, signal), [plan]);
  return useWorkspaceRequest(requestKey, request, EMPTY_EVIDENCE);
}

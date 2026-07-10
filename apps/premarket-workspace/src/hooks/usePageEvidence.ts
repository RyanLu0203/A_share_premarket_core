"use client";

import { useEffect, useState } from "react";

import { fetchWorkspaceJson, withQuery } from "@/lib/api";
import { endpointPlanForPage } from "@/lib/page-data";

export function usePageEvidence(pageId: number, symbol: string | undefined, mode: "live" | "replay", snapshotDate: string | undefined) {
  const requestKey = `${pageId}:${symbol ?? ""}:${mode}:${snapshotDate ?? ""}`;
  const [result, setResult] = useState<{requestKey: string; data: Record<string, unknown>; error: string | null}>({requestKey: "", data: {}, error: null});

  useEffect(() => {
    const controller = new AbortController();
    const plan = endpointPlanForPage(pageId, symbol);
    Promise.all(plan.map(async (item) => {
      const path = withQuery(item.path, {
        mode: pageId === 1 ? mode : undefined,
        snapshot_date: snapshotDate,
      });
      return [item.key, await fetchWorkspaceJson<unknown>(path, controller.signal)] as const;
    }))
      .then((entries) => setResult({requestKey, data: Object.fromEntries(entries), error: null}))
      .catch((reason: unknown) => {
        if (!controller.signal.aborted) setResult({requestKey, data: {}, error: reason instanceof Error ? reason.message : String(reason)});
      });
    return () => controller.abort();
  }, [mode, pageId, requestKey, snapshotDate, symbol]);

  return {
    data: result.data,
    loading: result.requestKey !== requestKey,
    error: result.requestKey === requestKey ? result.error : null,
  };
}

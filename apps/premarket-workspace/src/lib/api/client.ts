import type { SnapshotIndexResponse } from "@/lib/api/contracts";
import { apiRoutes, withQuery } from "@/lib/api/routes";
import type { WorkspaceStatus } from "@/lib/types";

const API_BASE = (process.env.NEXT_PUBLIC_PREMARKET_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

export interface EndpointPlanItem {
  key: string;
  path: string;
}

export class WorkspaceApiClient {
  async get<T>(path: string, signal?: AbortSignal): Promise<T> {
    const response = await fetch(`${API_BASE}${path}`, {
      method: "GET",
      headers: {Accept: "application/json"},
      cache: "no-store",
      signal,
    });
    if (!response.ok) {
      let detail = `${response.status} ${response.statusText}`;
      try {
        const body = await response.json() as {detail?: string};
        detail = body.detail ?? detail;
      } catch {
        // The status line remains the reliable fallback for a non-JSON response.
      }
      throw new Error(detail);
    }
    return response.json() as Promise<T>;
  }

  async bundle(plan: EndpointPlanItem[], signal?: AbortSignal): Promise<Record<string, unknown>> {
    const entries = await Promise.all(plan.map(async (item) => [item.key, await this.get<unknown>(item.path, signal)] as const));
    return Object.fromEntries(entries);
  }

  snapshots(signal?: AbortSignal): Promise<SnapshotIndexResponse> {
    return this.get<SnapshotIndexResponse>(apiRoutes.snapshots, signal);
  }

  status(mode: "live" | "replay", snapshotDate: string | undefined, signal?: AbortSignal): Promise<WorkspaceStatus> {
    return this.get<WorkspaceStatus>(withQuery(apiRoutes.status, {mode, snapshot_date: snapshotDate}), signal);
  }
}

export const workspaceApi = new WorkspaceApiClient();

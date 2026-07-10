const API_BASE = (process.env.NEXT_PUBLIC_PREMARKET_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

export async function fetchWorkspaceJson<T>(path: string, signal?: AbortSignal): Promise<T> {
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
      // The status line remains the most reliable error if the body is not JSON.
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export function withQuery(path: string, values: Record<string, string | undefined>): string {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(values)) {
    if (value) query.set(key, value);
  }
  const encoded = query.toString();
  return encoded ? `${path}?${encoded}` : path;
}

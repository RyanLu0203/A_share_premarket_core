"use client";

import { useEffect, useState } from "react";

export function useWorkspaceRequest<T>(requestKey: string, request: (signal: AbortSignal) => Promise<T>, initialData: T) {
  const [result, setResult] = useState<{requestKey: string; data: T; error: string | null}>({requestKey: "", data: initialData, error: null});

  useEffect(() => {
    const controller = new AbortController();
    void request(controller.signal)
      .then((data) => setResult({requestKey, data, error: null}))
      .catch((reason: unknown) => {
        if (!controller.signal.aborted) {
          setResult({requestKey, data: initialData, error: reason instanceof Error ? reason.message : String(reason)});
        }
      });
    return () => controller.abort();
  }, [initialData, request, requestKey]);

  return {
    data: result.data,
    loading: result.requestKey !== requestKey,
    error: result.requestKey === requestKey ? result.error : null,
  };
}

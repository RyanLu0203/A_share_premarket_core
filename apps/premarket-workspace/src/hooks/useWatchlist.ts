"use client";

import { useCallback, useState } from "react";

const STORAGE_KEY = "ashare-premarket-watchlist-v1";

export function useWatchlist(seed: string[] = []) {
  const [symbols, setSymbols] = useState<string[]>(() => {
    if (typeof window === "undefined") return seed;
    const saved = window.localStorage.getItem(STORAGE_KEY);
    if (!saved) return seed;
    try {
      const parsed = JSON.parse(saved);
      return Array.isArray(parsed) ? parsed.filter((value): value is string => typeof value === "string") : seed;
    } catch {
      return seed;
    }
  });

  const update = useCallback((next: string[]) => {
    const unique = [...new Set(next.map((symbol) => symbol.trim().toUpperCase()).filter(Boolean))];
    setSymbols(unique);
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(unique));
  }, []);

  return {
    symbols,
    add: useCallback((symbol: string) => update([...symbols, symbol]), [symbols, update]),
    remove: useCallback((symbol: string) => update(symbols.filter((item) => item !== symbol)), [symbols, update]),
  };
}

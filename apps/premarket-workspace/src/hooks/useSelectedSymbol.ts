"use client";

import { useCallback, useEffect, useSyncExternalStore } from "react";

import { normalizeSymbol } from "@/lib/api/routes";

export const DEFAULT_SELECTED_SYMBOL = "000333.SZ";
export const SELECTED_SYMBOL_STORAGE_KEY = "premarket-workspace:selected-symbol";
const SELECTED_SYMBOL_EVENT = "premarket-workspace:selected-symbol-change";

export function useSelectedSymbol(routeSymbol: string | undefined) {
  const normalizedRoute = routeSymbol ? normalizeSymbol(routeSymbol) : undefined;
  const storedSymbol = useSyncExternalStore(subscribe, readStoredSymbol, () => DEFAULT_SELECTED_SYMBOL);

  useEffect(() => {
    if (normalizedRoute && normalizedRoute !== localStorage.getItem(SELECTED_SYMBOL_STORAGE_KEY)) writeStoredSymbol(normalizedRoute);
  }, [normalizedRoute]);

  const selectSymbol = useCallback((symbol: string) => writeStoredSymbol(normalizeSymbol(symbol)), []);
  return {selectedSymbol: normalizedRoute ?? storedSymbol, selectSymbol};
}

function subscribe(callback: () => void): () => void {
  window.addEventListener("storage", callback);
  window.addEventListener(SELECTED_SYMBOL_EVENT, callback);
  return () => {
    window.removeEventListener("storage", callback);
    window.removeEventListener(SELECTED_SYMBOL_EVENT, callback);
  };
}

function readStoredSymbol(): string {
  if (typeof window === "undefined") return DEFAULT_SELECTED_SYMBOL;
  const value = localStorage.getItem(SELECTED_SYMBOL_STORAGE_KEY);
  return value ? normalizeSymbol(value) : DEFAULT_SELECTED_SYMBOL;
}

function writeStoredSymbol(symbol: string): void {
  localStorage.setItem(SELECTED_SYMBOL_STORAGE_KEY, symbol);
  window.dispatchEvent(new Event(SELECTED_SYMBOL_EVENT));
}

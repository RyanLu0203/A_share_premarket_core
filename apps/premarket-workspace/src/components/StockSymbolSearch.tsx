"use client";

import { Search } from "lucide-react";
import { FormEvent, useState } from "react";

import { normalizeSymbol } from "@/lib/api/routes";

export interface StockSearchItem {
  symbol: string;
  display_name: string;
}

export function StockSymbolSearch({stocks, selectedSymbol, onSelect}: {stocks: StockSearchItem[]; selectedSymbol: string; onSelect: (symbol: string) => void}) {
  const [query, setQuery] = useState("");
  const [error, setError] = useState<string | null>(null);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const match = findStockMatch(stocks, query);
    if (!match) {
      setError("No committed stock matches this search.");
      return;
    }
    setError(null);
    setQuery("");
    onSelect(match.symbol);
  };

  return <form className="stock-symbol-search" role="search" onSubmit={submit}>
    <label>
      <span className="sr-only">Search stocks by symbol or company</span>
      <Search aria-hidden="true" />
      <input
        aria-label="Search stocks by symbol or company"
        list="stock-symbol-options"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder={`${selectedSymbol} or company`}
      />
    </label>
    <datalist id="stock-symbol-options">
      {stocks.map((stock) => <option key={stock.symbol} value={`${stock.symbol} - ${stock.display_name}`} />)}
    </datalist>
    <button type="submit">Open chart</button>
    {error ? <span role="alert">{error}</span> : null}
  </form>;
}

export function findStockMatch(stocks: StockSearchItem[], query: string): StockSearchItem | undefined {
  if (!query.trim()) return undefined;
  const normalized = normalizeSymbol(query);
  const exactSymbol = normalized.split(" - ")[0];
  const lowered = query.trim().toLowerCase();
  return stocks.find((stock) => normalizeSymbol(stock.symbol) === exactSymbol)
    ?? stocks.find((stock) => stock.display_name.toLowerCase() === lowered)
    ?? stocks.find((stock) => stock.display_name.toLowerCase().includes(lowered) || normalizeSymbol(stock.symbol).includes(normalized));
}

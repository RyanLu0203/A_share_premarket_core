"use client";

import { Plus, X } from "lucide-react";
import { useState } from "react";

import { DenseTable, type DenseColumn } from "@/components/DenseTable";
import { PageHeader, StatusBadge } from "@/components/ui";
import { formatNumber, formatPercent, evidenceValue } from "@/lib/format";
import { useWatchlist } from "@/hooks/useWatchlist";

type Stock = Record<string, unknown> & {symbol: string; display_name: string};

export function WatchlistPage({seed, stocks}: {seed: string[]; stocks: Stock[]}) {
  const watchlist = useWatchlist(seed);
  const [symbol, setSymbol] = useState("");
  const [message, setMessage] = useState("");
  const [bandFilter, setBandFilter] = useState("ALL");
  const [abstentionFilter, setAbstentionFilter] = useState("ALL");
  const watchlistRows = watchlist.symbols.map((item) => stocks.find((stock) => stock.symbol === item)).filter((stock): stock is Stock => Boolean(stock));
  const rows = watchlistRows.filter((row) => (bandFilter === "ALL" || row.band_status === bandFilter) && (abstentionFilter === "ALL" || String(Boolean(row.abstain)) === abstentionFilter));
  const columns: DenseColumn<Stock>[] = [
    {key: "symbol", label: "Symbol"},
    {key: "display_name", label: "Company"},
    {key: "latest_price", label: "Latest", render: (row) => formatNumber(evidenceValue(row.latest_price))},
    {key: "price_change", label: "Change", render: (row) => <span className={Number(evidenceValue(row.price_change)) >= 0 ? "price-up" : "price-down"}>{formatPercent(evidenceValue(row.price_change))}</span>},
    {key: "market_cap", label: "Market cap", render: (row) => formatNumber(evidenceValue(row.market_cap))},
    {key: "pe_ttm", label: "PE TTM", render: (row) => formatNumber(evidenceValue(row.pe_ttm))},
    {key: "pb", label: "PB", render: (row) => formatNumber(evidenceValue(row.pb))},
    {key: "industry", label: "Industry", render: (row) => String(evidenceValue(row.industry) ?? "UNAVAILABLE")},
    {key: "current_weight", label: "Weight", render: (row) => formatPercent(row.current_weight)},
    {key: "band_min", label: "Band min", render: (row) => formatPercent(row.band_min)},
    {key: "band_max", label: "Band max", render: (row) => formatPercent(row.band_max)},
    {key: "band_status", label: "Band", render: (row) => <StatusBadge state={String(row.band_status)} />},
    {key: "risk_contribution", label: "Risk contribution", render: (row) => formatPercent(row.risk_contribution)},
    {key: "confidence", label: "Confidence", render: (row) => formatPercent(row.confidence)},
    {key: "abstain", label: "Abstain", render: (row) => <StatusBadge state={Boolean(row.abstain) ? "ABSTAIN" : "NOT_ABSTAIN"} />},
    {key: "provider_quality", label: "Provider"},
    {key: "remove", label: "", render: (row) => <button className="icon-button" aria-label={`Remove ${row.symbol}`} onClick={() => watchlist.remove(row.symbol)}><X aria-hidden="true" /></button>},
  ];
  return <div className="page-stack">
    <PageHeader eyebrow="02 / OBSERVATION BASKET" title="My Watchlist" meta="Browser-local only / No simulated positions, trades, weights, returns, or recommendations" actions={<div><form className="inline-form" onSubmit={(event) => {event.preventDefault(); const input = symbol.trim(); const match = stocks.find((stock) => stock.symbol === input.toUpperCase() || stock.display_name.toLocaleLowerCase() === input.toLocaleLowerCase()); if (match) {watchlist.add(match.symbol); setSymbol(""); setMessage(`${match.symbol} added`);} else {setMessage("Symbol is not eligible for the observation basket");}}}><label><span className="sr-only">Add symbol</span><input aria-label="Add symbol" value={symbol} onChange={(event) => event.target.value.length < 32 && setSymbol(event.target.value)} placeholder="002475.SZ" /></label><button type="submit" aria-label="Add to watchlist"><Plus aria-hidden="true" />Add</button></form><span aria-live="polite" className="form-feedback">{message}</span></div>} />
    <div className="filter-bar"><label><span>Band status</span><select aria-label="Watchlist band filter" value={bandFilter} onChange={(event) => setBandFilter(event.target.value)}><option value="ALL">All bands</option>{Array.from(new Set(watchlistRows.map((row) => String(row.band_status)))).sort().map((value) => <option key={value}>{value}</option>)}</select></label><label><span>Abstention</span><select aria-label="Watchlist abstention filter" value={abstentionFilter} onChange={(event) => setAbstentionFilter(event.target.value)}><option value="ALL">All states</option><option value="true">ABSTAIN</option><option value="false">NOT_ABSTAIN</option></select></label></div>
    <DenseTable rows={rows} columns={columns} searchPlaceholder="Search watchlist" />
  </div>;
}

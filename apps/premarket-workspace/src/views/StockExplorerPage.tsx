"use client";

import Link from "next/link";
import { ExternalLink, RotateCcw } from "lucide-react";
import { useState } from "react";

import { DenseTable, type DenseColumn } from "@/components/DenseTable";
import { PageHeader, StatusBadge } from "@/components/ui";
import { evidenceValue, formatNumber, formatPercent } from "@/lib/format";

type Stock = Record<string, unknown> & {symbol: string; display_name: string};

export function StockExplorerPage({data}: {data: {rows: Stock[]; count: number}}) {
  const [filters, setFilters] = useState({exchange: "ALL", board: "ALL", industry: "ALL", portfolio: "ALL", band: "ALL", abstention: "ALL", provider: "ALL"});
  const rows = data.rows.filter((row) => {
    const values = {
      exchange: String(evidenceValue(row.exchange) ?? "UNAVAILABLE"),
      board: String(evidenceValue(row.board) ?? "UNAVAILABLE"),
      industry: String(evidenceValue(row.industry) ?? "UNAVAILABLE"),
      portfolio: Number(row.current_weight) > 0 ? "IN_PORTFOLIO" : "NO_WEIGHT",
      band: String(row.band_status),
      abstention: Boolean(row.abstain) ? "ABSTAIN" : "NOT_ABSTAIN",
      provider: String(row.provider_quality ?? "UNAVAILABLE"),
    };
    return Object.entries(filters).every(([key, selected]) => selected === "ALL" || values[key as keyof typeof values] === selected);
  });
  const columns: DenseColumn<Stock>[] = [
    {key: "symbol", label: "Symbol", render: (row) => <Link href={`/stocks/${row.symbol}`}>{row.symbol}<ExternalLink aria-hidden="true" /></Link>},
    {key: "display_name", label: "Company"},
    {key: "exchange", label: "Exchange", render: (row) => String(evidenceValue(row.exchange) ?? "N/A")},
    {key: "board", label: "Board", render: (row) => String(evidenceValue(row.board) ?? "N/A")},
    {key: "industry", label: "Industry", render: (row) => String(evidenceValue(row.industry) ?? "N/A")},
    {key: "latest_price", label: "Latest", render: (row) => formatNumber(evidenceValue(row.latest_price))},
    {key: "price_change", label: "Change", render: (row) => <span className={Number(evidenceValue(row.price_change)) >= 0 ? "price-up" : "price-down"}>{formatPercent(evidenceValue(row.price_change))}</span>},
    {key: "market_cap", label: "Market cap", render: (row) => evidenceValue(row.market_cap) == null ? <span className="unavailable-inline">N/A</span> : formatNumber(evidenceValue(row.market_cap))},
    {key: "pe_ttm", label: "PE TTM", render: (row) => formatNumber(evidenceValue(row.pe_ttm))},
    {key: "pb", label: "PB", render: (row) => formatNumber(evidenceValue(row.pb))},
    {key: "band_status", label: "Band", render: (row) => <StatusBadge state={String(row.band_status)} />},
    {key: "provider_quality", label: "Provider quality"},
  ];
  const update = (key: keyof typeof filters, value: string) => setFilters((current) => ({...current, [key]: value}));
  return <div className="page-stack"><PageHeader eyebrow="03 / SECURITY MASTER" title="Stock Explorer" meta={`${data.count} evidence-backed symbols / ${rows.length} visible / Missing fundamentals remain unavailable`} />
    <div className="filter-bar explorer-filters">
      <FilterSelect label="Exchange" value={filters.exchange} values={options(data.rows, (row) => evidenceValue(row.exchange))} onChange={(value) => update("exchange", value)} />
      <FilterSelect label="Board" value={filters.board} values={options(data.rows, (row) => evidenceValue(row.board))} onChange={(value) => update("board", value)} />
      <FilterSelect label="Industry" value={filters.industry} values={options(data.rows, (row) => evidenceValue(row.industry))} onChange={(value) => update("industry", value)} />
      <FilterSelect label="Portfolio status" value={filters.portfolio} values={["IN_PORTFOLIO", "NO_WEIGHT"]} onChange={(value) => update("portfolio", value)} />
      <FilterSelect label="Band status" value={filters.band} values={options(data.rows, (row) => row.band_status)} onChange={(value) => update("band", value)} />
      <FilterSelect label="Abstention" value={filters.abstention} values={["ABSTAIN", "NOT_ABSTAIN"]} onChange={(value) => update("abstention", value)} />
      <FilterSelect label="Provider quality" value={filters.provider} values={options(data.rows, (row) => row.provider_quality)} onChange={(value) => update("provider", value)} />
      <button className="icon-button" aria-label="Reset stock filters" title="Reset stock filters" onClick={() => setFilters({exchange: "ALL", board: "ALL", industry: "ALL", portfolio: "ALL", band: "ALL", abstention: "ALL", provider: "ALL"})}><RotateCcw aria-hidden="true" /></button>
    </div>
    <DenseTable rows={rows} columns={columns} searchPlaceholder="Search symbol, company, board, or industry" />
  </div>;
}

function FilterSelect({label, value, values, onChange}: {label: string; value: string; values: string[]; onChange: (value: string) => void}) {
  return <label><span>{label}</span><select aria-label={`${label} filter`} value={value} onChange={(event) => onChange(event.target.value)}><option value="ALL">All</option>{values.map((option) => <option key={option}>{option}</option>)}</select></label>;
}

function options(rows: Stock[], read: (row: Stock) => unknown): string[] {
  return Array.from(new Set(rows.map((row) => String(read(row) ?? "UNAVAILABLE")))).sort();
}

"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { Time } from "lightweight-charts";

import type { CandleRow, ProviderDiscrepancyMarker } from "@/lib/api/contracts";

export type ChartRange = 20 | 60 | 120 | 250 | "ALL";
export const CHART_RANGES: readonly ChartRange[] = [20, 60, 120, 250, "ALL"];

export function selectRangeRows<T>(rows: T[], range: ChartRange): T[] {
  return range === "ALL" ? rows : rows.slice(-range);
}

export function PriceVolumeChart({rows, discrepancies = [], emptyReason}: {rows: CandleRow[]; discrepancies?: ProviderDiscrepancyMarker[]; emptyReason?: string}) {
  const container = useRef<HTMLDivElement>(null);
  const [timeframe, setTimeframe] = useState<ChartRange>(60);
  const visibleRows = useMemo(() => selectRangeRows(rows, timeframe), [rows, timeframe]);
  const [selectedDate, setSelectedDate] = useState<string>();
  const selectedRow = visibleRows.find((row) => row.trade_date === selectedDate) ?? visibleRows.at(-1);

  useEffect(() => {
    if (!container.current || visibleRows.length === 0) return;
    let disposed = false;
    let cleanup = () => undefined;
    void import("lightweight-charts").then(({CandlestickSeries, ColorType, HistogramSeries, createChart, createSeriesMarkers}) => {
      if (disposed || !container.current) return;
      const chart = createChart(container.current, {
        height: container.current.clientHeight || 520,
        layout: {background: {type: ColorType.Solid, color: "#101a2b"}, textColor: "#b8c4d8"},
        grid: {vertLines: {color: "#223149"}, horzLines: {color: "#223149"}},
        rightPriceScale: {borderColor: "#314158"},
        timeScale: {borderColor: "#314158", timeVisible: false},
        crosshair: {vertLine: {color: "#7ec2ff"}, horzLine: {color: "#7ec2ff"}},
      });
      const candles = chart.addSeries(CandlestickSeries, {
        upColor: "#d95763",
        downColor: "#2f9e72",
        wickUpColor: "#d95763",
        wickDownColor: "#2f9e72",
        borderVisible: false,
      }, 0);
      const volume = chart.addSeries(HistogramSeries, {
        priceFormat: {type: "volume"},
        priceScaleId: "volume",
        priceLineVisible: false,
        lastValueVisible: false,
      }, 1);
      const validCandles = visibleRows.filter(isValidCandle);
      candles.setData(validCandles.map((row) => ({
        time: row.trade_date as Time,
        open: row.open as number,
        high: row.high as number,
        low: row.low as number,
        close: row.close as number,
      })));
      volume.setData(validCandles.filter((row) => typeof row.volume === "number").map((row) => ({
        time: row.trade_date as Time,
        value: row.volume as number,
        color: (row.close as number) >= (row.open as number) ? "#d9576399" : "#2f9e7299",
      })));
      const discrepancyDates = new Set(discrepancies.map((row) => row.trade_date).filter(Boolean));
      createSeriesMarkers(candles, validCandles.filter((row) => discrepancyDates.has(row.trade_date)).map((row) => ({
        time: row.trade_date as Time,
        position: "aboveBar" as const,
        color: "#f4b942",
        shape: "circle" as const,
        text: "DQ",
      })));
      const panes = chart.panes();
      panes[0]?.setHeight(360);
      panes[1]?.setHeight(125);
      chart.timeScale().fitContent();
      const crosshair = (event: {time?: Time}) => {
        const key = timeKey(event.time);
        setSelectedDate(key);
      };
      chart.subscribeCrosshairMove(crosshair);
      const observer = new ResizeObserver(([entry]) => chart.applyOptions({width: entry.contentRect.width}));
      observer.observe(container.current);
      cleanup = () => {observer.disconnect(); chart.remove();};
    });
    return () => {disposed = true; cleanup();};
  }, [discrepancies, visibleRows]);

  if (rows.length === 0) return <div className="chart-empty">{emptyReason || "No committed candlestick evidence for this symbol."}</div>;
  const requested = timeframe === "ALL" ? rows.length : timeframe;
  return <div className="price-chart-stack">
    <div className="chart-toolbar">
      <div className="segmented-control chart-timeframe" aria-label="Chart timeframe">
        {CHART_RANGES.map((value) => <button key={value} aria-label={value === "ALL" ? "ALL" : `${value}D`} className={timeframe === value ? "is-active" : ""} onClick={() => setTimeframe(value)}>{value === "ALL" ? "ALL" : `${value}D`}</button>)}
      </div>
      <span>{visibleRows.length} of {requested} committed sessions available</span>
    </div>
    <ChartTooltip row={selectedRow} />
    <div className="chart-canvas-frame">
      <div className="chart-pane-label candle-pane-label">Daily price / CNY</div>
      <div ref={container} className="price-volume-chart" role="img" aria-label="Daily candlestick chart with synchronized volume pane" />
      <div className="chart-pane-label volume-pane-label">Daily volume / shares</div>
    </div>
    <div className="chart-legend"><span><i className="legend-up" />Up session</span><span><i className="legend-down" />Down session</span><span><i className="legend-discrepancy" />Provider discrepancy</span></div>
  </div>;
}

function ChartTooltip({row}: {row: CandleRow | undefined}) {
  const values: Array<[string, unknown, "number" | "compact" | "percent"]> = [
    ["Open", row?.open, "number"],
    ["High", row?.high, "number"],
    ["Low", row?.low, "number"],
    ["Close", row?.close, "number"],
    ["Volume", row?.volume, "compact"],
    ["Amount", row?.amount, "compact"],
    ["Turnover", row?.turnover, "percent"],
  ];
  return <div className="chart-tooltip" aria-live="polite">
    <div><span>Selected date</span><strong>{row?.trade_date ?? "UNAVAILABLE"}</strong></div>
    {values.map(([label, value, kind]) => <div key={label}><span>{label}</span><strong>{formatChartValue(value, kind)}</strong></div>)}
    <div><span>Provider</span><strong>{row?.source ?? "UNAVAILABLE"}</strong></div>
    <div><span>Quality</span><strong>{row?.quality ?? "UNAVAILABLE"}</strong></div>
  </div>;
}

function isValidCandle(row: CandleRow): boolean {
  return Boolean(row.trade_date) && [row.open, row.high, row.low, row.close].every((value) => typeof value === "number");
}

function timeKey(time: Time | undefined): string | undefined {
  if (typeof time === "string") return time;
  if (time && typeof time === "object" && "year" in time) {
    return `${time.year}-${String(time.month).padStart(2, "0")}-${String(time.day).padStart(2, "0")}`;
  }
  return undefined;
}

function formatChartValue(value: unknown, kind: "number" | "compact" | "percent"): string {
  if (typeof value !== "number" || !Number.isFinite(value)) return "UNAVAILABLE";
  if (kind === "compact") return new Intl.NumberFormat("en-US", {notation: "compact", maximumFractionDigits: 2}).format(value);
  if (kind === "percent") return `${value.toFixed(4)}%`;
  return value.toFixed(2);
}

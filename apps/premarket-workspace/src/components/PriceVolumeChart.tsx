"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { Time } from "lightweight-charts";

interface CandleRow {
  trade_date?: string;
  open?: number | null;
  high?: number | null;
  low?: number | null;
  close?: number | null;
  volume?: number | null;
}

export function PriceVolumeChart({rows}: {rows: CandleRow[]}) {
  const container = useRef<HTMLDivElement>(null);
  const [timeframe, setTimeframe] = useState<20 | 60 | "ALL">(60);
  const visibleRows = useMemo(() => timeframe === "ALL" ? rows : rows.slice(-timeframe), [rows, timeframe]);

  useEffect(() => {
    if (!container.current || visibleRows.length === 0) return;
    let disposed = false;
    let cleanup = () => undefined;
    void import("lightweight-charts").then(({CandlestickSeries, ColorType, HistogramSeries, createChart}) => {
      if (disposed || !container.current) return;
      const chart = createChart(container.current, {
        height: 420,
        layout: {background: {type: ColorType.Solid, color: "#101a2b"}, textColor: "#b8c4d8"},
        grid: {vertLines: {color: "#223149"}, horzLines: {color: "#223149"}},
        rightPriceScale: {borderColor: "#314158"},
        timeScale: {borderColor: "#314158", timeVisible: false},
      });
      const candles = chart.addSeries(CandlestickSeries, {upColor: "#d95763", downColor: "#2f9e72", wickUpColor: "#d95763", wickDownColor: "#2f9e72", borderVisible: false});
      const volume = chart.addSeries(HistogramSeries, {priceFormat: {type: "volume"}, priceScaleId: "volume", color: "#4da3ff"});
      chart.priceScale("volume").applyOptions({scaleMargins: {top: 0.78, bottom: 0}});
      const valid = visibleRows.filter((row) => row.trade_date && [row.open, row.high, row.low, row.close].every((value) => typeof value === "number"));
      candles.setData(valid.map((row) => ({time: row.trade_date as Time, open: row.open as number, high: row.high as number, low: row.low as number, close: row.close as number})));
      volume.setData(valid.map((row) => ({time: row.trade_date as Time, value: row.volume ?? 0, color: (row.close ?? 0) >= (row.open ?? 0) ? "#d9576388" : "#2f9e7288"})));
      chart.timeScale().fitContent();
      const observer = new ResizeObserver(([entry]) => chart.applyOptions({width: entry.contentRect.width}));
      observer.observe(container.current);
      cleanup = () => {observer.disconnect(); chart.remove();};
    });
    return () => {disposed = true; cleanup();};
  }, [visibleRows]);

  if (rows.length === 0) return <div className="chart-empty">No committed candlestick evidence for this symbol.</div>;
  return <div className="price-chart-stack"><div className="segmented-control chart-timeframe" aria-label="Chart timeframe">{([20, 60, "ALL"] as const).map((value) => <button key={value} className={timeframe === value ? "is-active" : ""} onClick={() => setTimeframe(value)}>{value === "ALL" ? "All" : `${value}D`}</button>)}</div><div ref={container} className="price-volume-chart" role="img" aria-label="Candlestick and volume chart" /></div>;
}

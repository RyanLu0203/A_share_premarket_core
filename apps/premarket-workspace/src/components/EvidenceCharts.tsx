"use client";

import dynamic from "next/dynamic";
import type { EChartsOption } from "echarts";

const ReactECharts = dynamic(() => import("echarts-for-react"), {ssr: false});

const textColor = "#b8c4d8";
const axisColor = "#314158";

export function EvidenceChart({option, label, height = 300}: {option: EChartsOption; label: string; height?: number}) {
  return <div className="evidence-chart" role="img" aria-label={label} style={{height}}><ReactECharts option={option} notMerge lazyUpdate style={{height: "100%", width: "100%"}} /></div>;
}

export function PolicyRiskChart({rows}: {rows: Array<Record<string, unknown>>}) {
  const names = rows.map((row) => String(row.policy_id ?? "unknown"));
  const option: EChartsOption = {
    animation: false,
    tooltip: {trigger: "axis"},
    legend: {textStyle: {color: textColor}, top: 0},
    grid: {left: 54, right: 18, top: 42, bottom: 76},
    xAxis: {type: "category", data: names, axisLabel: {color: textColor, rotate: 24}, axisLine: {lineStyle: {color: axisColor}}},
    yAxis: {type: "value", axisLabel: {color: textColor, formatter: (value: number) => `${(value * 100).toFixed(0)}%`}, splitLine: {lineStyle: {color: axisColor}}},
    series: [
      {name: "Volatility", type: "bar", data: rows.map((row) => number(row.annualized_volatility)), itemStyle: {color: "#4da3ff"}},
      {name: "Max drawdown", type: "bar", data: rows.map((row) => Math.abs(number(row.max_drawdown))), itemStyle: {color: "#f4b942"}},
      {name: "CVaR 95", type: "bar", data: rows.map((row) => Math.abs(number(row.cvar_95_daily))), itemStyle: {color: "#e85d75"}},
    ],
  };
  return <EvidenceChart option={option} label="Policy risk comparison" height={340} />;
}

export function AllocationTreemap({rows}: {rows: Array<Record<string, unknown>>}) {
  const palette = ["#4da3ff", "#2f9e72", "#d95763", "#f4b942", "#8b7ed8", "#46a6a6"];
  const data = rows
    .filter((row) => number(row.current_weight) > 0)
    .map((row, index) => ({
      name: String(row.display_name ?? row.symbol ?? "unknown"),
      value: number(row.current_weight),
      symbol: String(row.symbol ?? ""),
      itemStyle: {color: palette[index % palette.length]},
    }));
  const option: EChartsOption = {
    animation: false,
    tooltip: {formatter: (params) => {
      const item = params as {data?: {name?: string; symbol?: string; value?: number}};
      return `${item.data?.name ?? "N/A"}<br/>${item.data?.symbol ?? ""}<br/>${((item.data?.value ?? 0) * 100).toFixed(2)}%`;
    }},
    series: [{type: "treemap", roam: false, nodeClick: false, breadcrumb: {show: false}, label: {show: true, color: "#e8eef8", formatter: "{b}"}, upperLabel: {show: false}, data}],
  };
  return <EvidenceChart option={option} label="Holdings allocation treemap" height={360} />;
}

export function CorrelationHeatmap({matrix}: {matrix: Record<string, unknown>}) {
  const symbols = Array.isArray(matrix.symbols) ? matrix.symbols.map(String) : [];
  const values = Array.isArray(matrix.values) ? matrix.values as number[][] : [];
  const data = values.flatMap((row, y) => row.map((value, x) => [x, y, value]));
  const option: EChartsOption = {
    animation: false,
    tooltip: {position: "top"},
    grid: {left: 90, right: 34, top: 20, bottom: 92},
    xAxis: {type: "category", data: symbols, axisLabel: {color: textColor, rotate: 45}, axisLine: {lineStyle: {color: axisColor}}},
    yAxis: {type: "category", data: symbols, axisLabel: {color: textColor}, axisLine: {lineStyle: {color: axisColor}}},
    visualMap: {min: -1, max: 1, calculable: false, orient: "horizontal", left: "center", bottom: 4, textStyle: {color: textColor}, inRange: {color: ["#2f8f6d", "#172236", "#d95763"]}},
    series: [{name: "Correlation", type: "heatmap", data, label: {show: false}, emphasis: {itemStyle: {borderColor: "#ffffff", borderWidth: 1}}}],
  };
  return <EvidenceChart option={option} label="Display-only correlation heatmap" height={460} />;
}

export function RiskContributionChart({rows}: {rows: Array<Record<string, unknown>>}) {
  const top = [...rows].sort((a, b) => riskContribution(b) - riskContribution(a)).slice(0, 12).reverse();
  const option: EChartsOption = {
    animation: false,
    grid: {left: 82, right: 26, top: 14, bottom: 34},
    xAxis: {type: "value", axisLabel: {color: textColor, formatter: (value: number) => `${(value * 100).toFixed(1)}%`}, splitLine: {lineStyle: {color: axisColor}}},
    yAxis: {type: "category", data: top.map((row) => String(row.symbol)), axisLabel: {color: textColor}, axisLine: {lineStyle: {color: axisColor}}},
    series: [{type: "bar", data: top.map(riskContribution), itemStyle: {color: "#4da3ff"}}],
  };
  return <EvidenceChart option={option} label="Largest component risk contributions" height={360} />;
}

function number(value: unknown): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function riskContribution(row: Record<string, unknown>): number {
  return number(row.risk_contribution_share ?? row.risk_contribution);
}

import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";

import { CHART_RANGES, PriceVolumeChart, selectRangeRows } from "@/components/PriceVolumeChart";

const chartMocks = vi.hoisted(() => {
  const candleSeries = {setData: vi.fn()};
  const volumeSeries = {setData: vi.fn()};
  const addSeries = vi.fn<(definition: string, options?: unknown, paneIndex?: number) => typeof candleSeries | typeof volumeSeries>((definition) => definition === "CandlestickSeries" ? candleSeries : volumeSeries);
  const setHeight = vi.fn();
  return {
    candleSeries,
    volumeSeries,
    addSeries,
    setHeight,
    subscribeCrosshairMove: vi.fn(),
    createSeriesMarkers: vi.fn(),
    remove: vi.fn(),
    applyOptions: vi.fn(),
  };
});

vi.mock("lightweight-charts", () => ({
  CandlestickSeries: "CandlestickSeries",
  ColorType: {Solid: "solid"},
  HistogramSeries: "HistogramSeries",
  createSeriesMarkers: chartMocks.createSeriesMarkers,
  createChart: () => ({
    addSeries: chartMocks.addSeries,
    applyOptions: chartMocks.applyOptions,
    panes: () => [{setHeight: chartMocks.setHeight}, {setHeight: chartMocks.setHeight}],
    remove: chartMocks.remove,
    subscribeCrosshairMove: chartMocks.subscribeCrosshairMove,
    timeScale: () => ({fitContent: vi.fn()}),
  }),
}));

class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

const rows = [
  {trade_date: "2026-05-19", open: 80, high: 82, low: 79, close: 81, volume: 1000, amount: 81000, turnover: 0.2, source: "baostock", quality: "accepted"},
  {trade_date: "2026-05-20", open: 81, high: 83, low: 80, close: 82, volume: 1200, amount: 98400, turnover: 0.3, source: "baostock", quality: "accepted"},
  {trade_date: "2026-05-21", open: 82, high: 84, low: 81, close: 83, volume: 1400, amount: 116200, turnover: 0.4, source: "baostock", quality: "accepted"},
];

describe("price and volume chart", () => {
  beforeAll(() => {global.ResizeObserver = ResizeObserverMock as unknown as typeof ResizeObserver;});
  beforeEach(() => vi.clearAllMocks());

  it("supports every specified range without inventing unavailable history", () => {
    expect(CHART_RANGES).toEqual([20, 60, 120, 250, "ALL"]);
    expect(selectRangeRows(Array.from({length: 300}, (_, index) => ({trade_date: String(index)})), 250)).toHaveLength(250);
    expect(selectRangeRows(rows, "ALL")).toEqual(rows);
  });

  it("renders candles and volume in separate panes with an OHLCV tooltip", async () => {
    render(<PriceVolumeChart rows={rows} discrepancies={[{trade_date: "2026-05-20"}]} />);

    await waitFor(() => expect(chartMocks.addSeries).toHaveBeenCalledTimes(2));
    expect(chartMocks.addSeries.mock.calls[0][2]).toBe(0);
    expect(chartMocks.addSeries.mock.calls[1][2]).toBe(1);
    expect(chartMocks.candleSeries.setData).toHaveBeenCalled();
    expect(chartMocks.volumeSeries.setData).toHaveBeenCalled();
    expect(chartMocks.createSeriesMarkers).toHaveBeenCalled();
    expect(screen.getByText("2026-05-21")).toBeVisible();
    expect(screen.getByText("Volume")).toBeVisible();
    expect(screen.getByText("Amount")).toBeVisible();
    expect(screen.getByText("Turnover")).toBeVisible();

    fireEvent.click(screen.getByRole("button", {name: "250D"}));
    expect(screen.getByText("3 of 250 committed sessions available")).toBeVisible();

    const callback = chartMocks.subscribeCrosshairMove.mock.calls.at(-1)?.[0] as ((event: {time?: string}) => void);
    act(() => callback({time: "2026-05-19"}));
    expect(screen.getByText("2026-05-19")).toBeVisible();
  });

  it("shows an explicit unavailable state", () => {
    render(<PriceVolumeChart rows={[]} />);
    expect(screen.getByText("No committed candlestick evidence for this symbol.")).toBeVisible();
  });
});

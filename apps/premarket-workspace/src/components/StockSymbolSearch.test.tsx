import { fireEvent, render, screen } from "@testing-library/react";

import { findStockMatch, StockSymbolSearch } from "@/components/StockSymbolSearch";

const stocks = [
  {symbol: "000333.SZ", display_name: "Midea Group"},
  {symbol: "002475.SZ", display_name: "Luxshare Precision"},
];

describe("stock symbol search", () => {
  it("does not select a default stock for an empty query", () => {
    expect(findStockMatch(stocks, "   ")).toBeUndefined();
  });

  it("selects a stock by company name", () => {
    const onSelect = vi.fn();
    render(<StockSymbolSearch stocks={stocks} selectedSymbol="000333.SZ" onSelect={onSelect} />);

    fireEvent.change(screen.getByLabelText("Search stocks by symbol or company"), {target: {value: "Luxshare Precision"}});
    fireEvent.submit(screen.getByRole("search"));
    expect(onSelect).toHaveBeenCalledWith("002475.SZ");
  });
});

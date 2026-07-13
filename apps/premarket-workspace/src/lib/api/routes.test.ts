import { API_ROUTE_TEMPLATES, apiRoutes, normalizeSymbol, withQuery } from "@/lib/api/routes";

describe("canonical frontend API routes", () => {
  it("normalizes stock symbols and builds the governed stock bundle", () => {
    expect(normalizeSymbol(" 000333.sz ")).toBe("000333.SZ");
    expect(apiRoutes.stock("000333.sz")).toBe("/api/stocks/000333.SZ");
    expect(apiRoutes.stockMarket("000333.sz")).toBe("/api/stocks/000333.SZ/market");
    expect(apiRoutes.stockFundamentals("000333.sz")).toBe("/api/stocks/000333.SZ/fundamentals");
    expect(apiRoutes.stockRisk("000333.sz")).toBe("/api/stocks/000333.SZ/risk");
    expect(apiRoutes.stockPosition("000333.sz")).toBe("/api/stocks/000333.SZ/position");
  });

  it("keeps replay and snapshot parameters deterministic", () => {
    expect(withQuery(apiRoutes.status, {mode: "replay", snapshot_date: "2026-07-01"})).toBe(
      "/api/status?mode=replay&snapshot_date=2026-07-01",
    );
    expect(withQuery(apiRoutes.stocks, {mode: undefined, snapshot_date: undefined})).toBe("/api/stocks");
  });

  it("declares all 22 public backend route templates once", () => {
    expect(Object.values(API_ROUTE_TEMPLATES)).toHaveLength(22);
    expect(new Set(Object.values(API_ROUTE_TEMPLATES)).size).toBe(22);
  });
});

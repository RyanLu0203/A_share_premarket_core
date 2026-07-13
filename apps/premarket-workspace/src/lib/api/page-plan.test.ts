import { endpointPlanForPage } from "@/lib/api/page-plan";

describe("typed workspace page request plans", () => {
  it("maps every governed page to read-only API evidence", () => {
    for (let pageId = 1; pageId <= 23; pageId += 1) {
      const plan = endpointPlanForPage(pageId, "000333.SZ");
      expect(plan.length).toBeGreaterThan(0);
      expect(plan.every((item) => item.path.startsWith("/api/"))).toBe(true);
    }
  });

  it("loads the complete stock workspace bundle", () => {
    expect(endpointPlanForPage(4, "000333.sz")).toEqual([
      {key: "detail", path: "/api/stocks/000333.SZ"},
      {key: "market", path: "/api/stocks/000333.SZ/market"},
      {key: "fundamentals", path: "/api/stocks/000333.SZ/fundamentals"},
      {key: "risk", path: "/api/stocks/000333.SZ/risk"},
      {key: "position", path: "/api/stocks/000333.SZ/position"},
      {key: "stocks", path: "/api/stocks"},
    ]);
  });
});

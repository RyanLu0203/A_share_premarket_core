export interface EndpointPlanItem {
  key: string;
  path: string;
}

const singleEndpoint: Record<number, EndpointPlanItem> = {
  1: {key: "command", path: "/api/command-center"},
  3: {key: "stocks", path: "/api/stocks"},
  5: {key: "marketContext", path: "/api/market/context"},
  6: {key: "portfolio", path: "/api/portfolio/overview"},
  7: {key: "bands", path: "/api/portfolio/bands"},
  8: {key: "risk", path: "/api/portfolio/risk"},
  9: {key: "constraints", path: "/api/portfolio/constraints"},
  10: {key: "abstentions", path: "/api/portfolio/abstentions"},
  18: {key: "experiment", path: "/api/experiment"},
  19: {key: "experiment", path: "/api/experiment"},
  20: {key: "quality", path: "/api/data-quality"},
  21: {key: "provider", path: "/api/provider-health"},
  22: {key: "snapshots", path: "/api/snapshots"},
  23: {key: "provenance", path: "/api/provenance"},
};

export function endpointPlanForPage(pageId: number, symbol = "000333.SZ"): EndpointPlanItem[] {
  if (pageId === 2) {
    return [
      {key: "watchlist", path: "/api/watchlists"},
      {key: "stocks", path: "/api/stocks"},
    ];
  }
  if (pageId === 4) {
    const encoded = encodeURIComponent(symbol.toUpperCase());
    return [
      {key: "detail", path: `/api/stocks/${encoded}`},
      {key: "market", path: `/api/stocks/${encoded}/market`},
      {key: "fundamentals", path: `/api/stocks/${encoded}/fundamentals`},
      {key: "risk", path: `/api/stocks/${encoded}/risk`},
      {key: "position", path: `/api/stocks/${encoded}/position`},
    ];
  }
  if (pageId >= 11 && pageId <= 17) {
    const plan = [{key: "capabilities", path: "/api/quant/capabilities"}];
    if (pageId === 14) plan.push({key: "marketContext", path: "/api/market/context"});
    return plan;
  }
  return singleEndpoint[pageId] ? [singleEndpoint[pageId]] : [{key: "command", path: "/api/command-center"}];
}

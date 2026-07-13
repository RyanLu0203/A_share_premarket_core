import type { EndpointPlanItem } from "@/lib/api/client";
import { apiRoutes } from "@/lib/api/routes";

const singleEndpoint: Record<number, EndpointPlanItem> = {
  1: {key: "command", path: apiRoutes.commandCenter},
  3: {key: "stocks", path: apiRoutes.stocks},
  5: {key: "marketContext", path: apiRoutes.marketContext},
  6: {key: "portfolio", path: apiRoutes.portfolioOverview},
  7: {key: "bands", path: apiRoutes.portfolioBands},
  8: {key: "risk", path: apiRoutes.portfolioRisk},
  9: {key: "constraints", path: apiRoutes.portfolioConstraints},
  10: {key: "abstentions", path: apiRoutes.portfolioAbstentions},
  18: {key: "experiment", path: apiRoutes.experiment},
  19: {key: "experiment", path: apiRoutes.experiment},
  20: {key: "quality", path: apiRoutes.dataQuality},
  21: {key: "provider", path: apiRoutes.providerHealth},
  22: {key: "snapshots", path: apiRoutes.snapshots},
  23: {key: "provenance", path: apiRoutes.provenance},
};

export function endpointPlanForPage(pageId: number, symbol = "000333.SZ"): EndpointPlanItem[] {
  if (pageId === 2) return [{key: "watchlist", path: apiRoutes.watchlists}, {key: "stocks", path: apiRoutes.stocks}];
  if (pageId === 4) {
    return [
      {key: "detail", path: apiRoutes.stock(symbol)},
      {key: "market", path: apiRoutes.stockMarket(symbol)},
      {key: "fundamentals", path: apiRoutes.stockFundamentals(symbol)},
      {key: "risk", path: apiRoutes.stockRisk(symbol)},
      {key: "position", path: apiRoutes.stockPosition(symbol)},
      {key: "stocks", path: apiRoutes.stocks},
    ];
  }
  if (pageId >= 11 && pageId <= 17) {
    const plan: EndpointPlanItem[] = [{key: "capabilities", path: apiRoutes.quantCapabilities}];
    if (pageId === 14) plan.push({key: "marketContext", path: apiRoutes.marketContext});
    return plan;
  }
  return singleEndpoint[pageId] ? [singleEndpoint[pageId]] : [{key: "command", path: apiRoutes.commandCenter}];
}

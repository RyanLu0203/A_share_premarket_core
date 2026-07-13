export const API_ROUTE_TEMPLATES = {
  health: "/api/health",
  status: "/api/status",
  commandCenter: "/api/command-center",
  watchlists: "/api/watchlists",
  stocks: "/api/stocks",
  stock: "/api/stocks/{symbol}",
  stockMarket: "/api/stocks/{symbol}/market",
  stockFundamentals: "/api/stocks/{symbol}/fundamentals",
  stockRisk: "/api/stocks/{symbol}/risk",
  stockPosition: "/api/stocks/{symbol}/position",
  portfolioOverview: "/api/portfolio/overview",
  portfolioBands: "/api/portfolio/bands",
  portfolioRisk: "/api/portfolio/risk",
  portfolioConstraints: "/api/portfolio/constraints",
  portfolioAbstentions: "/api/portfolio/abstentions",
  marketContext: "/api/market/context",
  quantCapabilities: "/api/quant/capabilities",
  experiment: "/api/experiment",
  dataQuality: "/api/data-quality",
  providerHealth: "/api/provider-health",
  snapshots: "/api/snapshots",
  provenance: "/api/provenance",
} as const;

export function normalizeSymbol(symbol: string): string {
  return symbol.trim().toUpperCase();
}

function forSymbol(template: string, symbol: string): string {
  return template.replace("{symbol}", encodeURIComponent(normalizeSymbol(symbol)));
}

export const apiRoutes = {
  ...API_ROUTE_TEMPLATES,
  stock: (symbol: string) => forSymbol(API_ROUTE_TEMPLATES.stock, symbol),
  stockMarket: (symbol: string) => forSymbol(API_ROUTE_TEMPLATES.stockMarket, symbol),
  stockFundamentals: (symbol: string) => forSymbol(API_ROUTE_TEMPLATES.stockFundamentals, symbol),
  stockRisk: (symbol: string) => forSymbol(API_ROUTE_TEMPLATES.stockRisk, symbol),
  stockPosition: (symbol: string) => forSymbol(API_ROUTE_TEMPLATES.stockPosition, symbol),
};

export function withQuery(path: string, values: Record<string, string | undefined>): string {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(values)) {
    if (value) query.set(key, value);
  }
  const encoded = query.toString();
  return encoded ? `${path}?${encoded}` : path;
}

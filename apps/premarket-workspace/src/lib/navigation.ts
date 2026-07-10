import {
  Activity,
  BarChart3,
  BellRing,
  Blocks,
  BookMarked,
  Boxes,
  BrainCircuit,
  ChartCandlestick,
  CircleGauge,
  ClipboardCheck,
  DatabaseZap,
  FileClock,
  FlaskConical,
  Gauge,
  HeartPulse,
  History,
  Layers3,
  ListFilter,
  LockKeyhole,
  Radar,
  Search,
  ShieldCheck,
  type LucideIcon,
} from "lucide-react";

export type PageState = "AVAILABLE" | "LOCKED" | "HYBRID";

export interface NavigationItem {
  id: number;
  label: string;
  path: string;
  icon: LucideIcon;
  state: PageState;
}

export interface NavigationGroup {
  label: string;
  items: NavigationItem[];
}

export const navigationGroups: NavigationGroup[] = [
  {label: "COMMAND CENTER", items: [{id: 1, label: "Command Center", path: "/", icon: CircleGauge, state: "AVAILABLE"}]},
  {
    label: "MARKET & STOCKS",
    items: [
      {id: 2, label: "My Watchlist", path: "/watchlist", icon: BookMarked, state: "AVAILABLE"},
      {id: 3, label: "Stock Explorer", path: "/stocks", icon: Search, state: "AVAILABLE"},
      {id: 4, label: "Stock Detail", path: "/stocks/000333.SZ", icon: ChartCandlestick, state: "AVAILABLE"},
      {id: 5, label: "Market Context", path: "/market-context", icon: Radar, state: "AVAILABLE"},
    ],
  },
  {
    label: "POSITION MANAGEMENT",
    items: [
      {id: 6, label: "Portfolio Overview", path: "/portfolio", icon: Layers3, state: "AVAILABLE"},
      {id: 7, label: "Position Bands", path: "/position-bands", icon: Gauge, state: "AVAILABLE"},
      {id: 8, label: "Risk Monitor", path: "/risk-monitor", icon: Activity, state: "AVAILABLE"},
      {id: 9, label: "Constraint Monitor", path: "/constraints", icon: ShieldCheck, state: "AVAILABLE"},
      {id: 10, label: "Abstention Center", path: "/abstentions", icon: BellRing, state: "AVAILABLE"},
    ],
  },
  {
    label: "QUANT RESEARCH",
    items: [
      {id: 11, label: "Alpha Overview", path: "/quant/alpha", icon: LockKeyhole, state: "LOCKED"},
      {id: 12, label: "Factor Monitor", path: "/quant/factors", icon: BrainCircuit, state: "LOCKED"},
      {id: 13, label: "IC / RankIC Lab", path: "/quant/ic-rankic", icon: BarChart3, state: "LOCKED"},
      {id: 14, label: "Regime Analysis", path: "/quant/regime", icon: Blocks, state: "LOCKED"},
      {id: 15, label: "Factor Correlation", path: "/quant/correlation", icon: Boxes, state: "LOCKED"},
      {id: 16, label: "Candidate Diagnostics", path: "/quant/candidates", icon: ListFilter, state: "LOCKED"},
      {id: 17, label: "Recommendation Tiering", path: "/quant/recommendation-tiering", icon: LockKeyhole, state: "LOCKED"},
    ],
  },
  {
    label: "EXPERIMENT",
    items: [
      {id: 18, label: "Shadow Experiment", path: "/experiment/shadow", icon: FlaskConical, state: "AVAILABLE"},
      {id: 19, label: "Experiment History", path: "/experiment/history", icon: History, state: "AVAILABLE"},
    ],
  },
  {
    label: "SYSTEM",
    items: [
      {id: 20, label: "Data Quality", path: "/system/data-quality", icon: DatabaseZap, state: "AVAILABLE"},
      {id: 21, label: "Provider Health", path: "/system/provider-health", icon: HeartPulse, state: "AVAILABLE"},
      {id: 22, label: "Snapshot History", path: "/system/snapshots", icon: FileClock, state: "AVAILABLE"},
      {id: 23, label: "Provenance & Audit", path: "/system/provenance", icon: ClipboardCheck, state: "AVAILABLE"},
    ],
  },
];

export const flattenNavigation = (groups: NavigationGroup[]) => groups.flatMap((group) => group.items);

export const pageRegistry = Object.fromEntries(
  flattenNavigation(navigationGroups).map((item) => [item.id, item]),
) as Record<number, NavigationItem>;

export function navigationItemForPath(pathname: string): NavigationItem {
  if (pathname.startsWith("/stocks/") && pathname !== "/stocks") {
    return pageRegistry[4];
  }
  return flattenNavigation(navigationGroups).find((item) => item.path === pathname) ?? pageRegistry[1];
}

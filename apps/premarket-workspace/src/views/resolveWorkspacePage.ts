import { flattenNavigation, navigationGroups, type PageState } from "@/lib/navigation";

export interface ResolvedWorkspacePage {
  pageId: number;
  kind: PageState;
  symbol?: string;
  view?: "chart";
}

export function resolveWorkspacePage(pathname: string): ResolvedWorkspacePage {
  if (pathname.startsWith("/stocks/") && pathname.split("/")[2]) {
    const segments = pathname.split("/");
    return {
      pageId: 4,
      kind: "AVAILABLE",
      symbol: decodeURIComponent(segments[2]).toUpperCase(),
      view: segments[3] === "chart" ? "chart" : undefined,
    };
  }
  const item = flattenNavigation(navigationGroups).find((candidate) => candidate.path === pathname);
  if (!item) return {pageId: 1, kind: "AVAILABLE"};
  if (item.id === 14) return {pageId: 14, kind: "HYBRID"};
  return {pageId: item.id, kind: item.state};
}

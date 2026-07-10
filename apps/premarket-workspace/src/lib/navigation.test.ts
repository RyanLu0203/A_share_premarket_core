import { flattenNavigation, navigationGroups, pageRegistry } from "@/lib/navigation";

describe("workspace navigation", () => {
  it("registers all 23 issue pages exactly once", () => {
    const pages = flattenNavigation(navigationGroups);
    expect(pages).toHaveLength(23);
    expect(new Set(pages.map((page) => page.id)).size).toBe(23);
    expect(Object.keys(pageRegistry)).toHaveLength(23);
  });

  it("keeps every factor-dependent quant surface locked", () => {
    const quant = navigationGroups.find((group) => group.label === "QUANT RESEARCH");
    expect(quant?.items).toHaveLength(7);
    expect(quant?.items.filter((item) => item.state === "LOCKED")).toHaveLength(7);
  });
});

import { act, renderHook } from "@testing-library/react";

import { useWatchlist } from "@/hooks/useWatchlist";

describe("local watchlist", () => {
  beforeEach(() => localStorage.clear());

  it("adds and removes symbols while persisting browser-local state", () => {
    const { result } = renderHook(() => useWatchlist(["000333.SZ"]));
    act(() => result.current.add("002475.SZ"));
    expect(result.current.symbols).toEqual(["000333.SZ", "002475.SZ"]);
    expect(JSON.parse(localStorage.getItem("ashare-premarket-watchlist-v1") ?? "[]")).toEqual([
      "000333.SZ",
      "002475.SZ",
    ]);
    act(() => result.current.remove("000333.SZ"));
    expect(result.current.symbols).toEqual(["002475.SZ"]);
  });
});

import { act, renderHook, waitFor } from "@testing-library/react";

import { SELECTED_SYMBOL_STORAGE_KEY, useSelectedSymbol } from "@/hooks/useSelectedSymbol";

describe("selected stock state", () => {
  beforeEach(() => localStorage.clear());

  it("restores a selected symbol while navigating away from the stock route", async () => {
    localStorage.setItem(SELECTED_SYMBOL_STORAGE_KEY, "002475.SZ");
    const {result} = renderHook(() => useSelectedSymbol(undefined));

    await waitFor(() => expect(result.current.selectedSymbol).toBe("002475.SZ"));
  });

  it("lets the deep-linked route become the persisted source of truth", async () => {
    const {result, rerender} = renderHook(({routeSymbol}) => useSelectedSymbol(routeSymbol), {
      initialProps: {routeSymbol: "000333.sz" as string | undefined},
    });

    await waitFor(() => expect(result.current.selectedSymbol).toBe("000333.SZ"));
    await waitFor(() => expect(localStorage.getItem(SELECTED_SYMBOL_STORAGE_KEY)).toBe("000333.SZ"));

    act(() => result.current.selectSymbol("002475.sz"));
    rerender({routeSymbol: undefined});
    expect(result.current.selectedSymbol).toBe("002475.SZ");
  });
});

import { fireEvent, render, screen } from "@testing-library/react";

import { DenseTable } from "@/components/DenseTable";


describe("DenseTable pagination", () => {
  it("paginates large evidence tables without parsing or truncating rows", () => {
    const rows = Array.from({length: 25}, (_, index) => ({id: index, label: `row-${index}`}));
    render(<DenseTable rows={rows} columns={[{key: "label", label: "Label"}]} />);

    expect(screen.getByText("row-0")).toBeVisible();
    expect(screen.queryByText("row-24")).not.toBeInTheDocument();
    expect(screen.getByText("Page 1 of 2")).toBeVisible();

    fireEvent.click(screen.getByRole("button", {name: "Next table page"}));
    expect(screen.getByText("row-24")).toBeVisible();
    expect(screen.getByText("Page 2 of 2")).toBeVisible();
  });

  it("shows an explicit empty state when no evidence rows match", () => {
    render(<DenseTable rows={[]} columns={[{key: "label", label: "Label"}]} />);

    expect(screen.getByText("NO COMMITTED EVIDENCE ROWS MATCH THIS VIEW")).toBeVisible();
  });

  it("searches evidence values nested inside provenance objects", () => {
    const rows = [
      {symbol: "000333.SZ", industry: {value: "Home Appliances", source: "configured"}},
      {symbol: "000001.SZ", industry: {value: "Banking", source: "configured"}},
    ];
    render(<DenseTable rows={rows} columns={[{key: "symbol", label: "Symbol"}, {key: "industry", label: "Industry"}]} searchPlaceholder="Search securities" />);

    fireEvent.change(screen.getByRole("textbox", {name: "Search securities"}), {target: {value: "Home Appliances"}});

    expect(screen.getByText("000333.SZ")).toBeVisible();
    expect(screen.queryByText("000001.SZ")).not.toBeInTheDocument();
    expect(screen.getByText("1-1 / 1 filtered / 2 rows")).toBeVisible();
  });
});

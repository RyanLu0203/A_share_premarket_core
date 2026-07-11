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
});

import { render, screen } from "@testing-library/react";

import { RiskContributionChart } from "@/components/EvidenceCharts";


vi.mock("next/dynamic", () => ({
  default: () => ({option}: {option: unknown}) => <pre data-testid="chart-option">{JSON.stringify(option)}</pre>,
}));

describe("evidence chart view models", () => {
  it("uses the portfolio risk_contribution alias instead of rendering zero bars", () => {
    render(<RiskContributionChart rows={[
      {symbol: "000001.SZ", risk_contribution: 0.04},
      {symbol: "000002.SZ", risk_contribution: 0.02},
    ]} />);

    const option = JSON.parse(screen.getByTestId("chart-option").textContent ?? "{}") as {series: Array<{data: number[]}>};
    expect(option.series[0].data).toEqual([0.02, 0.04]);
  });
});

# GOAL-V1-DIAGNOSTIC-COVERAGE-03 Source-Backed Multi-Symbol Diagnostics Gate

GOAL-V1-DIAGNOSTIC-COVERAGE-03 is a review-only diagnostic coverage gate over the committed GOAL-DATA-PROVIDER-02B normalized evaluation panel. It creates separate risk, recommendation eligibility, and position-band diagnostic rows at `trade_date + symbol` grain.

Primary input: `outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv`

## Outputs

- `outputs/diagnostics/goal_v1_diagnostic_coverage03_risk_diagnostics.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage03_recommendation_diagnostics.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage03_position_band_diagnostics.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage03_distribution_summary.csv`
- `outputs/audits/goal_v1_diagnostic_coverage03_source_backed_diagnostics_report.md`
- `outputs/audits/goal_v1_diagnostic_coverage03_source_backed_diagnostics_manifest.json`
- `outputs/audits/goal_v1_diagnostic_coverage03_source_backed_diagnostics_audit.md`
- `configs/diagnostics/goal_v1_diagnostic_coverage03_contract.yaml`

## Current Coverage

- Status: `PASS_WITH_WARNINGS`
- Diagnostic rows per family: `6000`
- Unique symbols: `50`
- Unique trade dates: `120`
- Diagnostic group variation status: `diagnostic_group_variation_available`
- Recommended next goal: `GOAL-10B.3`

## Locked Boundary

This gate does not overwrite canonical GOAL-07B, GOAL-08B, or GOAL-09 artifacts. It does not run GOAL-10B.3, GOAL-10C, or any backtest, and it creates no portfolio returns, equity curves, dashboards, trading, broker, production, local-lake, factor-mining, or DQN/RL outputs.

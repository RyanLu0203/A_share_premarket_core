# GOAL-10B.2 Recommendation Backtest Revalidation

Status: `PASS_WITH_WARNINGS`

GOAL-10B.2 is a review-only recommendation diagnostic revalidation gate over GOAL-V1-DIAGNOSTIC-COVERAGE-02 multi-symbol rows. It does not create actionable recommendations, trades, positions, portfolios, equity curves, dashboards, production outputs, or local-lake artifacts.

## Inputs

- `outputs/diagnostics/goal_v1_diagnostic_coverage02_recommendation_diagnostics.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage02_risk_diagnostics.csv`

## Outputs

- `outputs/backtest/goal10b2_revalidation_input_snapshot.csv`
- `outputs/backtest/goal10b2_recommendation_status_metrics.csv`
- `outputs/backtest/goal10b2_symbol_metrics.csv`
- `outputs/backtest/goal10b2_horizon_coverage.csv`
- `outputs/audits/goal10b2_recommendation_backtest_revalidation_report.md`
- `outputs/audits/goal10b2_recommendation_backtest_revalidation_manifest.json`
- `outputs/audits/goal10b2_recommendation_backtest_revalidation_audit.md`

## Result

- Snapshot rows: `8`
- Unique symbols: `2`
- 20d rows available: `0`

Current DC02 rows support bounded 1d review-only diagnostics for two approved symbols. 3d, 5d, and 20d forward returns remain unavailable, so the gate reports `PASS_WITH_WARNINGS` and keeps downstream execution paths locked.

## Locked Boundary

GOAL-10D, Dashboard / Daily Report UI, signal backtest promotion, portfolio backtest, paper trading, live trading, broker integration, production writes, factor-mining, local-lake writes, and DQN/RL remain locked or deleted from active mainline.

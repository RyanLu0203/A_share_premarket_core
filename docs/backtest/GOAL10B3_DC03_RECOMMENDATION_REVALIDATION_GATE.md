# GOAL-10B.3 DC03 Recommendation Revalidation Gate

Status: `PASS_WITH_WARNINGS`

GOAL-10B.3 is a review-only recommendation revalidation gate over GOAL-V1-DIAGNOSTIC-COVERAGE-03 source-backed recommendation and risk diagnostics joined to the committed GOAL-DATA-PROVIDER-02B panel at `trade_date + symbol` grain.

## Inputs

- `outputs/diagnostics/goal_v1_diagnostic_coverage03_recommendation_diagnostics.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage03_risk_diagnostics.csv`
- `outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv`

## Outputs

- `outputs/backtest/goal10b3_dc03_revalidation_input_snapshot.csv`
- `outputs/backtest/goal10b3_recommendation_group_metrics.csv`
- `outputs/backtest/goal10b3_risk_severity_group_metrics.csv`
- `outputs/backtest/goal10b3_symbol_metrics.csv`
- `outputs/backtest/goal10b3_horizon_coverage.csv`
- `outputs/backtest/goal10b3_group_imbalance_diagnostics.csv`
- `outputs/audits/goal10b3_dc03_recommendation_revalidation_report.md`
- `outputs/audits/goal10b3_dc03_recommendation_revalidation_manifest.json`
- `outputs/audits/goal10b3_dc03_recommendation_revalidation_audit.md`
- `configs/backtest/goal10b3_dc03_revalidation_contract.yaml`

## Result

- Snapshot rows: `6000`
- Unique symbols: `50`
- Unique trade dates: `120`
- Recommendation group variation available: `true`
- Signal classification: `recommendation_revalidation_signal_weak_or_unreliable`
- Recommended next goal: `GOAL-RISK-TIERING-01 / GOAL-REC-TIERING-01 before position-band validation`

The current DC03 evidence supports full 1d/5d/20d label coverage, but the recommendation grouping is severely imbalanced: one group contains 5,990 of 6,000 rows and the blocked source-risk group contains 10 rows. IC/RankIC is not computed because there is no valid numeric recommendation score in the categorical, never-actionable DC03 contract.

## Locked Boundary

GOAL-10D, Dashboard / Daily Report UI, signal backtest promotion, portfolio backtest, paper trading, live trading, broker integration, production writes, factor-mining, local-lake writes, and DQN/RL remain locked or deleted from active mainline.

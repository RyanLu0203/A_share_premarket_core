# GOAL-10B Recommendation Diagnostics Backtest Review-Only

Status: `PASS_WITH_WARNINGS`

GOAL-10B is a review-only diagnostic gate that evaluates whether GOAL-08B non-actionable recommendation eligibility diagnostics have observable forward-return separation under the GOAL-10A input, metric, grouping, and T+1/no-lookahead contracts.

It is not an actionable recommendation, signal backtest workflow promotion, portfolio backtest, trading system, dashboard, or production path.

## Source Inputs

- `outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv`
- `outputs/samples/stage6c_source_backed_engineering_panel_sample.csv`
- `configs/backtest/goal10a_backtest_input_contract.yaml`
- `configs/backtest/goal10a_backtest_metric_contract.yaml`
- `configs/backtest/goal10a_backtest_grouping_contract.yaml`
- `configs/backtest/goal10a_execution_alignment_policy.yaml`

GOAL-08B rows remain `never_actionable`. The GOAL-10B join preserves the `trade_date + symbol` signal grain and uses the next available same-symbol label date as the diagnostic execution date.

## Outputs

- `outputs/backtest/goal10b_recommendation_backtest_input_snapshot.csv`
- `outputs/backtest/goal10b_recommendation_group_metrics.csv`
- `outputs/backtest/goal10b_risk_severity_group_metrics.csv`
- `outputs/backtest/goal10b_warning_group_metrics.csv`
- `outputs/backtest/goal10b_ic_rank_ic_summary.csv`
- `outputs/audits/goal10b_recommendation_backtest_report.md`
- `outputs/audits/goal10b_recommendation_backtest_manifest.json`
- `outputs/audits/goal10b_recommendation_backtest_audit.md`

## Warnings

The current committed label sample supports 1d and 5d forward-return diagnostics, but not 20d. The final signal row has no next available execution label in the bounded sample. GOAL-08B also has a single recommendation eligibility bucket and single risk-severity bucket, so IC/Rank IC is explicitly marked `not_computed` rather than fabricated.

## Locked Boundary

GOAL-10C, GOAL-10D, Dashboard / Daily Report UI, signal backtest promotion, portfolio backtest, cost/slippage sensitivity, paper trading, live trading, broker integration, production writes, factor-mining, local-lake writes, and DQN/RL remain locked or deleted from active mainline.

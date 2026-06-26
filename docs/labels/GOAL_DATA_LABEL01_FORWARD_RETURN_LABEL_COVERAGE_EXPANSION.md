# GOAL-DATA-LABEL-01 Forward-Return Label Coverage Expansion

Status: `PASS_WITH_WARNINGS`

GOAL-DATA-LABEL-01 expands review-only forward-return label coverage from committed source-backed OHLCV and benchmark samples. It adds 1d, 3d, 5d, and 20d stock, benchmark, and excess-return labels wherever the future trading bars exist.

The gate is a label coverage step only. It does not expand risk, recommendation, or position-band diagnostics and does not run a backtest.

## Outputs

- `outputs/labels/goal_data_label01_forward_return_label_coverage_sample.csv`
- `outputs/labels/goal_data_label01_forward_return_label_coverage_summary.csv`
- `outputs/audits/goal_data_label01_forward_return_label_coverage_report.md`
- `outputs/audits/goal_data_label01_forward_return_label_coverage_manifest.json`
- `outputs/audits/goal_data_label01_forward_return_label_coverage_audit.md`

## Current Coverage

- Label rows: `100`
- Unique symbols: `1`
- Unique dates: `100`
- 20d label-ready rows: `80`
- Diagnostic join ready: `False`

## Remaining Gap

The current committed diagnostic rows do not overlap the expanded label sample by `trade_date + symbol`, and the expanded sample is still single-symbol. GOAL-V1-DIAGNOSTIC-COVERAGE-02 must create multi-symbol, non-actionable, review-only diagnostic coverage before GOAL-10B.2 revalidation.

## Locked Boundary

GOAL-10B.2, GOAL-10C, GOAL-10D, Dashboard / Daily Report UI, signal and portfolio backtests, trading, production, broker integration, local-lake writes, factor-mining, and DQN/RL remain locked.

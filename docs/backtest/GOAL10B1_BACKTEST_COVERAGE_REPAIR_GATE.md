# GOAL-10B.1 Backtest Coverage Repair Gate

Status: `PASS_WITH_WARNINGS`

GOAL-10B.1 is a review-only coverage and group-variation repair gate for GOAL-10B. It investigates whether the GOAL-10B warnings can be repaired using only existing contract-valid artifacts already committed to the repository.

It does not fetch data, expand the panel, create new recommendation diagnostics, create position rows, run portfolio backtests, or create dashboard/frontend outputs.

## Findings

- GOAL-10B used `outputs/samples/stage6c_source_backed_engineering_panel_sample.csv` because it is the primary existing Stage6C source-backed label source in the GOAL-10B loader.
- That source is a bounded sample with one symbol and no 20d forward-return fields.
- Existing alternate committed label files either have the same one-symbol coverage, no GOAL-08B symbol/date overlap, or lack the required 5d/20d fields.
- GOAL-08B has one recommendation group (`blocked_high_risk`), one actionability status (`never_actionable`), and one risk-severity bucket (`HIGH`), so recommendation/risk group variation cannot be repaired by changing label files.

## Outputs

- `outputs/backtest/goal10b1_coverage_repair_diagnostic_summary.csv`
- `outputs/backtest/goal10b1_recommendation_distribution_audit.csv`
- `outputs/backtest/goal10b1_label_source_coverage_audit.csv`
- `outputs/audits/goal10b1_backtest_coverage_repair_report.md`
- `outputs/audits/goal10b1_backtest_coverage_repair_manifest.json`
- `outputs/audits/goal10b1_backtest_coverage_repair_audit.md`

## Repair Decision

`coverage_repair_not_possible_with_current_artifacts`

GOAL-10B.1 does not write repaired snapshots or repaired group metrics because doing so would fabricate variation or coverage that is absent from the current contract-valid artifacts.

## Follow-on Label Coverage Step

GOAL-DATA-LABEL-01 follows this gate only as review-only label coverage expansion from existing committed OHLCV and benchmark samples. It may add 20d forward-return label coverage where future bars exist, but it does not create new GOAL-08B or GOAL-09 diagnostics and does not run GOAL-10B.2 or GOAL-10C backtests.

## Locked Boundary

GOAL-V1-DIAGNOSTIC-COVERAGE-02, GOAL-10B.2, GOAL-10C, GOAL-10D, Dashboard / Daily Report UI, signal backtest promotion, portfolio backtest, cost/slippage sensitivity, paper/live trading, live trading, broker integration, production writes, factor-mining, local-lake writes, and DQN/RL remain locked or deleted from active mainline.

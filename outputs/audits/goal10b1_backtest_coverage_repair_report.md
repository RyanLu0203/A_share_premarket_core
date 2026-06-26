# GOAL-10B.1 Backtest Coverage and Group Variation Repair Gate

GOAL-10B.1 Backtest Coverage and Group Variation Repair Gate: PASS_WITH_WARNINGS
Mode: `review_only`

## Investigation
- GOAL-10B label source: `outputs/samples/stage6c_source_backed_engineering_panel_sample.csv`
- Candidate label sources audited: `6`
- GOAL-08B rows: `100`
- GOAL-08B symbols: `1`
- GOAL-08B recommendation groups: `1`
- GOAL-08B risk-severity groups: `1`
- GOAL-10B evaluable rows: `99`

## Repair Decision
- `coverage_repair_not_possible_with_current_artifacts`
- Current artifacts do not contain an existing contract-valid source that both improves GOAL-10B label coverage and creates recommendation/risk group variation.
- GOAL-08B itself contains one symbol, one recommendation label, one actionability status, and one risk-severity bucket, so group variation cannot be repaired by swapping label files.

## Boundary
- GOAL-10B.1 is review-only diagnostics over existing committed artifacts.
- No new data fetch, panel expansion, provider change, GOAL-08B row, GOAL-09 row, BUY/SELL/HOLD output, target price, position sizing, portfolio return, equity curve, dashboard, trading, production, broker, local-lake, factor-mining, or DQN/RL output was created.
- GOAL-10C, GOAL-10D, Dashboard / Daily Report UI, signal backtest promotion, portfolio backtest, cost/slippage sensitivity, paper/live trading, broker, production, factor-mining, local-lake, and DQN/RL remain locked.

## Recommended Next Gate
- `future_data_label_coverage_expansion_gate` should be requested before attempting GOAL-10C or any broader backtest diagnostics.

## Failures

## Warnings
- coverage_repair_not_possible_with_current_artifacts
- goal08b_ranking_variation_not_available
- goal08b_single_recommendation_group
- goal08b_single_risk_severity
- no_existing_forward_return_20d_label_source
- single_symbol_goal08b_diagnostics

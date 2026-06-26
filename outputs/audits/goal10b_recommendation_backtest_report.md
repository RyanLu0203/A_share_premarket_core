# GOAL-10B Recommendation Diagnostics Backtest Review-Only

GOAL-10B Recommendation Diagnostics Backtest Review-Only: PASS_WITH_WARNINGS
Mode: `review_only`

## Input Alignment
- GOAL-08B recommendation diagnostics rows: `100`
- Input snapshot rows: `100`
- Evaluable T+1 rows: `99`
- Label source: `outputs/samples/stage6c_source_backed_engineering_panel_sample.csv`
- Signal date equals the upstream GOAL-08B `trade_date`; execution date is the next available label date for the same symbol.

## Diagnostics
- Recommendation group metric rows: `1`
- Risk-severity group metric rows: `1`
- Warning group metric rows: `7`
- IC/Rank IC status: `not_computed`

## Boundary
- Outputs are non-actionable review-only diagnostics.
- No BUY/SELL/HOLD, target prices, position sizing, order quantities, target weights, portfolio weights, portfolio returns, equity curves, portfolio construction, dashboards, HTML, Streamlit, frontend, trading, production, broker, factor-mining, local-lake, or DQN/RL outputs were generated.
- GOAL-10C, GOAL-10D, Dashboard / Daily Report UI, paper/live trading, broker, production, factor-mining, local-lake, and DQN/RL remain locked.

## Failures

## Warnings
- insufficient_ranking_variation
- insufficient_recommendation_group_variation
- insufficient_risk_severity_variation
- missing_forward_return_20d
- missing_t_plus_1_label_rows_excluded
- single_symbol_label_coverage

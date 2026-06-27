# GOAL-10B.2 Recommendation Backtest Revalidation

GOAL-10B.2 Recommendation Backtest Revalidation: PASS_WITH_WARNINGS
Mode: `review_only_recommendation_backtest_revalidation`

## Revalidation Scope
- DC02 recommendation rows: `8`
- Unique symbols: `2`
- Unique trade dates: `4`
- Recommendation metric rows: `1`
- Symbol metric rows: `2`

## Boundary
- Outputs are non-actionable review-only diagnostics over committed DC02 rows.
- No BUY/SELL/HOLD, target prices, position sizing, order quantities, portfolio weights, portfolio returns, equity curves, dashboards, HTML, Streamlit, frontend, trading, production, broker, factor-mining, local-lake, or DQN/RL outputs were generated.
- GOAL-10D, Dashboard / Daily Report UI, signal and portfolio backtests, paper/live trading, broker, production, factor-mining, local-lake, and DQN/RL remain locked.

## Failures

## Warnings
- missing_forward_return_20d
- missing_forward_return_3d
- missing_forward_return_5d
- single_recommendation_status_group
- single_risk_severity_group

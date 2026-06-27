# GOAL-10C Cost / Slippage Sensitivity Gate

GOAL-10C Cost / Slippage Sensitivity Gate: PASS_WITH_WARNINGS
Mode: `review_only_position_band_cost_slippage_sensitivity`

## Sensitivity Scope
- Position-band input rows: `8`
- Sensitivity rows: `24`
- Cost scenarios: `3`

## Boundary
- Outputs are non-actionable row-level review-only diagnostics.
- No BUY/SELL/HOLD, target prices, position sizing, order quantities, target weights, portfolio weights, portfolio returns, equity curves, dashboards, HTML, Streamlit, frontend, trading, production, broker, factor-mining, local-lake, or DQN/RL outputs were generated.
- GOAL-10D, Dashboard / Daily Report UI, signal and portfolio backtests, paper/live trading, broker, production, factor-mining, local-lake, and DQN/RL remain locked.

## Failures

## Warnings
- missing_forward_return_20d
- row_level_sensitivity_not_portfolio_backtest
- single_position_band_status_group

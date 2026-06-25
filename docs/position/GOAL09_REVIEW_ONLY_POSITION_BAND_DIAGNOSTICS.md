# GOAL-09 Review-Only Position-Band Diagnostics

Status: `PASS_WITH_WARNINGS`

GOAL-09 is implemented only as a review-only, non-actionable position-band diagnostics prototype.

It consumes prior GOAL-08B recommendation diagnostics and GOAL-07B risk overlay diagnostics at `trade_date + symbol` grain. It writes a small diagnostic CSV under `outputs/position/` and does not create actual position recommendations.

## Boundary

- `diagnostic_mode` is always `review_only`.
- `position_actionability_status` is always `never_actionable`.
- `position_band_status` never contains an actual position instruction.
- HIGH GOAL-07B risk severity remains blocked.
- GOAL-08B warning codes and GOAL-07B risk warning codes propagate into the diagnostic output.
- No position size, portfolio weight, target weight, order quantity, capital allocation amount, buy/sell/hold action, target price, expected return for action, dashboard, trading, production, backtest, factor-mining, broker, local-lake, or DQN/RL output is created.

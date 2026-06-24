# GOAL-07B Risk Overlay Calculation Prototype

Status: `PASS_WITH_WARNINGS`

GOAL-07B is a deterministic, review-only risk overlay calculation prototype. It converts GOAL-07A, GOAL-07A.1, and GOAL-07B.0 governance evidence into symbol-date-level risk diagnostics only.

The output grain is `trade_date + symbol`. Outputs are non-actionable and do not contain recommendation, position, allocation, order, trading, dashboard decision, production, backtest, factor-mining, broker, or DQN/RL outputs.

Rows generated: `100`
Severity levels used: `HIGH`

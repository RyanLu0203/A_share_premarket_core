# GOAL-10A Backtest Contract Design Gate

Status: `PASS_WITH_WARNINGS`

GOAL-10A is a design-only contract gate for future review-only backtest validation. It defines what a later GOAL-10B-style evaluator may read and how that evaluator must align dates, benchmarks, target horizons, tradability constraints, grouping, metrics, and cost/slippage sensitivity.

It does not run a backtest and does not generate backtest rows, performance tables, equity curves, portfolio returns, dashboard output, HTML, Streamlit, frontend code, buy/sell/hold actions, target prices, position sizes, order quantities, trading instructions, production writes, broker outputs, factor-mining outputs, local-lake files, or DQN/RL outputs.

## Source Inputs

- `outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv`
- `outputs/position/goal09_review_only_position_band_diagnostics.csv`
- `outputs/audits/goal_v1_integrity01_artifact_lineage_structure_manifest.json`

All source rows must stay at `trade_date + symbol` grain and must remain `never_actionable`.

## Date Alignment

- `signal_date`: the PIT-safe date on which a diagnostic is available; for current GOAL-08B/GOAL-09 diagnostics it equals `trade_date`.
- `trade_date`: the upstream diagnostic date and join key component; it is not an execution date.
- `execution_date`: the first eligible A-share trading session strictly after `signal_date`, normally T+1.
- `target_horizon`: one of `1d`, `5d`, or `20d` in a future evaluator.
- Benchmark windows must use the same `execution_date` and `target_horizon` as the evaluated diagnostic row.

## Future Metrics

- `forward_return_1d`
- `forward_return_5d`
- `forward_return_20d`
- `benchmark_excess_return`
- `hit_rate`
- `mean_return`
- `median_return`
- `volatility`
- `max_drawdown`
- `IC`
- `Rank IC`

## Locked Boundary

GOAL-10B, GOAL-10C, GOAL-10D, Dashboard / Daily Report UI, paper trading, live trading, broker integration, production writes, factor-mining, and DQN/RL remain `locked_future` or deleted from active mainline as applicable.

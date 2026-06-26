# GOAL-10A Backtest Contract Design Gate

GOAL-10A Backtest Contract Design Gate: PASS_WITH_WARNINGS
Mode: `design_only`

## Input Contracts
- GOAL-08B recommendation diagnostics rows referenced: `100`
- GOAL-09 position-band diagnostics rows referenced: `100`
- Shared grain: `trade_date + symbol`
- Trade-date plus symbol keys match: `true`
- GOAL-08B and GOAL-09 inputs must remain `never_actionable`.

## Future Evaluation Contract
- Defines signal_date, trade_date, execution_date, target_horizon, benchmark alignment, T+1, no-lookahead, cost/slippage sensitivity, and suspended/limit/missing-price policies.
- Defines future metrics only: forward returns, benchmark excess return, hit rate, mean, median, volatility, max drawdown, IC, and Rank IC.
- Defines future grouping by recommendation eligibility status, actionability status, risk severity, position-band status, and warning category.

## Safety
- No backtest was run.
- No backtest performance rows, equity curves, portfolio returns, dashboard files, HTML, Streamlit, frontend code, buy/sell/hold actions, target prices, position sizes, order quantities, local-lake data, trading, production, broker, factor-mining, or DQN/RL outputs were generated.
- GOAL-10B, GOAL-10C, GOAL-10D, Dashboard / Daily Report UI, paper/live trading, broker, production, factor-mining, and DQN/RL remain locked.

## Failures

## Warnings
- calibration_not_reliable_for_thresholding
- feature_sign_instability_bounded
- provider_source_concentration_disclosed
- selected_score_variant_weak_rank_signal
- single_provider_mode_akshare_direct
- target_horizon_calibration_warning
- weak_target_horizon_rank_signal

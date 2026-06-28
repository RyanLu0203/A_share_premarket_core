# GOAL-QUANT-RESEARCH-01 Factor Research Lab

GOAL-QUANT-RESEARCH-01 Factor Research Lab: PASS_WITH_WARNINGS

## 1. Current Project Stage
The project has entered a research-only factor validity stage after Provider02B, DC03, GOAL-10B.3, GOAL-RISK-TIERING-01, and GOAL-RISK-TIERING-01.1 produced source-backed diagnostics with weak or unreliable score semantics.

## 2. Why The Project Has Entered Deep Quant Research
Prior risk and downside-risk scores have usable row coverage but weak directional evidence. This gate evaluates factor semantics before any recommendation tiering or position validation.

## 3. Source-Backed Evidence Lineage
- `outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage03_risk_diagnostics.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage03_recommendation_diagnostics.csv`
- `outputs/diagnostics/goal_risk_tiering01_risk_tiered_diagnostics.csv`
- `outputs/diagnostics/goal_risk_tiering01_distribution_summary.csv`
- `outputs/backtest/goal_risk_tiering01_risk_tier_forward_return_metrics.csv`
- `outputs/diagnostics/goal_risk_tiering011_downside_risk_diagnostics.csv`
- `outputs/diagnostics/goal_risk_tiering011_component_contribution_summary.csv`
- `outputs/diagnostics/goal_risk_tiering011_distribution_summary.csv`
- `outputs/backtest/goal_risk_tiering011_downside_risk_forward_return_metrics.csv`
- `outputs/backtest/goal10b3_recommendation_group_metrics.csv`
- `outputs/backtest/goal10b3_group_imbalance_diagnostics.csv`

## 4. Factor Research Methodology
The lab builds factor values from committed upstream evidence, assigns buckets and quantiles, evaluates post-hoc forward and benchmark-excess returns, computes IC/RankIC when numeric, checks monotonicity, rolling stability, group imbalance, no-lookahead status, trial registration, and anti-overfitting controls.

## 5. Factor Registry Summary
Factors registered: `11`.

## 6. Score/Factor Candidates Evaluated
- `risk_score_numeric`: `factor_signal_weak_or_unreliable`
- `downside_risk_score_numeric`: `factor_signal_weak_or_unreliable`
- `volatility_component`: `factor_signal_weak_or_unreliable`
- `momentum_component`: `factor_signal_weak_or_unreliable`
- `abnormal_positive_movement_flag`: `factor_not_evaluable`
- `abnormal_negative_movement_flag`: `factor_signal_weak_or_unreliable`
- `provider_crosscheck_component`: `factor_signal_weak_or_unreliable`
- `data_quality_risk_component`: `factor_not_evaluable`
- `liquidity_risk_component`: `factor_signal_weak_or_unreliable`
- `trading_status_risk_component`: `factor_not_evaluable`
- `st_status_risk_component`: `factor_not_evaluable`

## 7. Bucket And Quantile Diagnostics
Bucket metric rows: `115`.

## 8. Forward-Return And Benchmark-Excess-Return Results
Forward returns and benchmark-excess returns are used only after factor assignment for post-hoc diagnostics.

## 9. IC / RankIC Results
IC/RankIC rows: `11`.

## 10. Monotonicity And Spread Results
Monotonicity rows: `11`.

## 11. Rolling Stability Results
Rolling stability rows: `11`.

## 12. Regime Split Availability
Regime split is classified as `regime_split_not_evaluable` because committed evidence does not include a trailing benchmark state series suitable for no-lookahead regime tags.

## 13. Trial Registry And Anti-Overfitting Controls
Every factor candidate is recorded in the trial registry. The policy forbids tuning weights to forward returns, unregistered repeated rule search, single-horizon promotion, promotion without stability checks, promotion without no-lookahead audit, promotion from collapsed buckets, and any use of portfolio returns or equity curves.

## 14. Score Validity Classification
Classification counts: `{'factor_not_evaluable': 4, 'factor_signal_weak_or_unreliable': 7}`.

## 15. Whether Any Factor Is Ready For REC-TIERING-01
Ready factor count: `0`.
Overall validity: `no_factor_ready_for_rec_tiering`.

## 16. Recommended Next Goal
`GOAL-ALPHA-FACTOR-CANDIDATE-01_before_recommendation_tiering`.

## Locked Boundary
GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, portfolio backtests, paper/live trading, broker integration, production writes, local-lake writes, factor-mining, and DQN/RL remain locked or deleted from active mainline.

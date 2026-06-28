# GOAL-RISK-TIERING-01.1 Downside Risk Repair Gate

GOAL-RISK-TIERING-01.1 Downside Risk Repair Gate: PASS_WITH_WARNINGS
Mode: `review_only_risk_score_directionality_downside_repair_gate`

## Repair Scope
- Downside-risk rows: `6000`
- Unique symbols: `50`
- Unique trade dates: `120`
- Downside bucket distribution: `{'LOW_DOWNSIDE_RISK_REVIEW_ONLY': 3864, 'MEDIUM_DOWNSIDE_RISK_REVIEW_ONLY': 1887, 'HIGH_DOWNSIDE_RISK_REVIEW_ONLY': 239, 'INSUFFICIENT_DOWNSIDE_EVIDENCE_REVIEW_ONLY': 10}`
- Dominant bucket share: `0.6440000000`
- Original HIGH bucket volatility/momentum dominated: `true`
- Original HIGH volatility/momentum dominated share: `0.7877697842`
- Signal classification: `downside_risk_tiering_signal_weak_or_unreliable`
- Recommended next action: `another_deterministic_governance_risk_rule_review_before_goal_rec_tiering01`

## No-Lookahead Boundary
- Downside score construction excludes all `forward_return_*`, `benchmark_excess_return_*`, and `label_ready_*` fields.
- Forward returns are used only for post-hoc group evaluation metrics after deterministic downside buckets are assigned.
- Score weights are deterministic governance rules and are not tuned to maximize forward returns.

## Locked Boundary
- GOAL-RISK-TIERING-01 and DC03 artifacts are not overwritten.
- No recommendation rows, position rows, BUY/SELL/HOLD outputs, target prices, position sizing, order quantities, portfolio weights, portfolio returns, equity curves, dashboards, HTML, Streamlit, frontend, trading, production, broker, local-lake, factor-mining, or DQN/RL outputs were generated.
- GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, signal and portfolio backtests, paper/live trading, broker, production, factor-mining, local-lake, and DQN/RL remain locked.

## Failures

## Warnings
- downside_risk_bucket_distribution
- downside_risk_tiering_signal_weak_or_unreliable
- minimum_bucket_size_warning
- original_high_bucket_volatility_momentum_dominated

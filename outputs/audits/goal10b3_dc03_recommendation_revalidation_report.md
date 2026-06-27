# GOAL-10B.3 DC03 Recommendation Revalidation Gate

GOAL-10B.3 DC03 Recommendation Revalidation Gate: PASS_WITH_WARNINGS
Mode: `review_only_dc03_recommendation_revalidation_gate`

## Revalidation Scope
- DC03 recommendation rows joined to Provider02B panel rows: `6000`
- Unique symbols: `50`
- Unique trade dates: `120`
- Recommendation groups: `2`
- Risk severity groups: `2`
- Dominant recommendation group share: `0.9983333333`
- Signal classification: `recommendation_revalidation_signal_weak_or_unreliable`
- Recommended next goal: `GOAL-RISK-TIERING-01 / GOAL-REC-TIERING-01 before position-band validation`

## Boundary
- Outputs are non-actionable review-only diagnostics over committed DC03 and Provider02B evidence.
- No BUY/SELL/HOLD, target prices, position sizing, order quantities, portfolio weights, portfolio returns, equity curves, dashboards, HTML, Streamlit, frontend, trading, production, broker, factor-mining, local-lake, or DQN/RL outputs were generated.
- GOAL-10D, Dashboard / Daily Report UI, signal and portfolio backtests, paper/live trading, broker, production, factor-mining, local-lake, and DQN/RL remain locked.

## Failures

## Warnings
- group_imbalance_warning
- ic_rankic_availability
- ic_rankic_unavailable_non_numeric_categorical_recommendation_label
- recommendation_revalidation_signal_weak_or_unreliable
- risk_group_imbalance_warning
- small_blocked_group_warning

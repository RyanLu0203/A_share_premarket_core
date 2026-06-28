# GOAL-RISK-TIERING-01 Risk Severity Numeric Score Tiering Gate

GOAL-RISK-TIERING-01 Risk Severity Numeric Score Tiering Gate: PASS_WITH_WARNINGS
Mode: `review_only_risk_severity_numeric_score_tiering_gate`

## Tiering Scope
- Risk-tiered rows: `6000`
- Unique symbols: `50`
- Unique trade dates: `120`
- Risk score bucket distribution: `{'LOW_RISK_REVIEW_ONLY': 2891, 'MEDIUM_RISK_REVIEW_ONLY': 2821, 'HIGH_RISK_REVIEW_ONLY': 278, 'INSUFFICIENT_EVIDENCE_REVIEW_ONLY': 10}`
- Original DC03 risk severity distribution: `{'MEDIUM': 5990, 'HIGH': 10}`
- Dominant bucket share: `0.4818333333`
- Signal classification: `risk_tiering_signal_weak_or_unreliable`
- Recommended next action: `adjust_deterministic_governance_risk_rules_before_goal_rec_tiering01`

## No-Lookahead Boundary
- Numeric risk score construction excludes all `forward_return_*`, `benchmark_excess_return_*`, and `label_ready_*` fields.
- Forward returns are used only for post-hoc group evaluation metrics after the deterministic risk buckets are assigned.
- Score weights are deterministic governance rules and are not tuned to maximize forward returns.

## Locked Boundary
- Canonical GOAL-07B and DC03 risk diagnostics are not overwritten.
- No recommendation rows, position rows, BUY/SELL/HOLD outputs, target prices, position sizing, order quantities, portfolio weights, portfolio returns, equity curves, dashboards, HTML, Streamlit, frontend, trading, production, broker, local-lake, factor-mining, or DQN/RL outputs were generated.
- GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, signal and portfolio backtests, paper/live trading, broker, production, factor-mining, local-lake, and DQN/RL remain locked.

## Failures

## Warnings
- minimum_bucket_size_warning
- risk_score_bucket_distribution
- risk_tiering_signal_weak_or_unreliable

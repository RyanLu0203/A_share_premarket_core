# GOAL-07A Risk State Machine Design

Status: `implemented_design_only`

The state machine is a design artifact only. It is not run on real symbol rows in GOAL-07A.

States:
- `not_evaluated`
- `input_invalid`
- `data_blocked`
- `model_warning`
- `source_warning`
- `market_warning`
- `eligible_for_review_only_snapshot`
- `blocked_from_recommendation`

Transitions:
- `not_evaluated` -> `input_invalid` on `input contract failure`.
- `not_evaluated` -> `data_blocked` on `leakage flag failure`.
- `not_evaluated` -> `data_blocked` on `panel below engineering_pilot`.
- `not_evaluated` -> `model_warning` on `calibration warning`.
- `not_evaluated` -> `model_warning` on `feature instability warning`.
- `not_evaluated` -> `source_warning` on `single provider concentration`.
- `not_evaluated` -> `market_warning` on `high volatility or gap warning`.
- `model_warning` -> `eligible_for_review_only_snapshot` on `all governance conditions satisfied`.
- `source_warning` -> `eligible_for_review_only_snapshot` on `all governance conditions satisfied`.
- `market_warning` -> `eligible_for_review_only_snapshot` on `all governance conditions satisfied`.
- `eligible_for_review_only_snapshot` -> `blocked_from_recommendation` on `any hard boundary violation`.

# GOAL-08A Recommendation Contract Design Gate

Status: `implemented_design_only`

GOAL-08A is a design-only contract gate for a possible future review-only GOAL-08B prototype. It consumes only GOAL-07B review-only risk overlay diagnostic evidence and defines names, guards, and propagation rules.

## Required Input
- Source: `GOAL-07B` review-only risk overlay diagnostics.
- Grain: `trade_date + symbol`.
- Required risk fields: `risk_domain`, `risk_tag`, `risk_severity`, `risk_confidence`, `risk_state`, `risk_transition_diagnostic`, `triggered_rule_ids`, `risk_rule_trace`.
- Required warning fields: `warning_propagation`, `upstream_warning_mapping`, `bounded_model_weakness_diagnostics`, `missing_input_diagnostics`, `review_only_status_flags`.

## Future Schema Names Only
- `trade_date`
- `symbol`
- `source_goal07b_risk_state`
- `source_goal07b_risk_severity`
- `source_goal07b_risk_confidence`
- `source_goal07b_triggered_rule_ids`
- `source_goal07b_warning_propagation`
- `source_goal07b_risk_rule_trace`
- `future_recommendation_contract_state`
- `future_actionability_block_reason`
- `future_non_actionable_diagnostic_flag`
- `future_warning_policy_trace`
- `future_downstream_lock_flags`

The schema sample has row count `0`. GOAL-08A creates no recommendation rows.

## Warning Propagation
- `calibration_not_reliable_for_thresholding`: `block_actionability_or_require_future_human_review_design_only`.
- `feature_sign_instability_bounded`: `carry_warning_and_keep_future_diagnostic_non_actionable_when_unresolved`.
- `provider_source_concentration_disclosed`: `carry_source_concentration_warning_and_block_actionability_when_risk_severity_HIGH`.
- `selected_score_variant_weak_rank_signal`: `block_actionability_or_require_future_human_review_design_only`.
- `single_provider_mode_akshare_direct`: `carry_source_concentration_warning_and_block_actionability_when_risk_severity_HIGH`.
- `target_horizon_calibration_warning`: `block_actionability_or_require_future_human_review_design_only`.
- `weak_target_horizon_rank_signal`: `block_actionability_or_require_future_human_review_design_only`.

## Actionability Rule
`source_goal07b_risk_severity == HIGH` blocks actionable recommendation output. Any future recommendation-like diagnostic must remain non-actionable and must not contain buy/sell/hold, target price, position size, portfolio weight, order, broker, production, backtest, factor-mining, or DQN/RL fields.

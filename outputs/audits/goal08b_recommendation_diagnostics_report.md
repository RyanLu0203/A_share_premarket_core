# GOAL-08B Recommendation Diagnostics Prototype

GOAL-08B Recommendation Diagnostics Prototype: PASS_WITH_WARNINGS
GOAL-08B mode: `review_only`
Recommendation diagnostic rows generated: `100`
Output grain: `trade_date + symbol`
Actionability status: `never_actionable`
Outputs are non-actionable diagnostics only.
No buy/sell/hold recommendations, target prices, expected returns for action, position sizes, portfolio weights, dashboards, paper/live trading paths, broker outputs, production behavior, backtests, factor-mining outputs, local lake files, or DQN/RL outputs were created.
Allowed next action: `request_explicit_goal09_position_band_review_only_unlock_or_fix_goal08b_warnings`

## Evidence Inputs
- `outputs/risk_overlay/goal07b_review_only_risk_overlay.csv`
- `outputs/audits/goal07b_risk_overlay_calculation_report.md`
- `outputs/audits/goal07b_risk_overlay_calculation_audit.md`
- `outputs/audits/goal07b_risk_overlay_calculation_manifest.json`
- `outputs/audits/goal08a_recommendation_contract_design_report.md`
- `outputs/audits/goal08a_recommendation_contract_design_audit.md`
- `outputs/audits/goal08a_recommendation_contract_design_manifest.json`
- `configs/recommendation/goal08a_future_recommendation_input_contract.yaml`
- `configs/recommendation/goal08a_warning_propagation_policy.yaml`
- `configs/recommendation/goal08a_actionability_guardrails.yaml`
- `configs/recommendation/goal08a_recommendation_state_machine.yaml`
- `outputs/audits/goal_storage01_local_research_lake_hardening_report.md`
- `outputs/audits/goal_storage01_local_research_lake_hardening_audit.md`
- `outputs/audits/goal_storage01_local_research_lake_hardening_manifest.json`
- `outputs/audits/goal08b0_recommendation_review_only_unlock_report.md`
- `outputs/audits/goal08b0_recommendation_review_only_unlock_audit.md`
- `outputs/audits/goal08b0_recommendation_review_only_unlock_manifest.json`

## Diagnostic Labels Used
- `blocked_high_risk`

## Remaining Warnings
- `calibration_not_reliable_for_thresholding`
- `feature_sign_instability_bounded`
- `provider_source_concentration_disclosed`
- `selected_score_variant_weak_rank_signal`
- `single_provider_mode_akshare_direct`
- `target_horizon_calibration_warning`
- `weak_target_horizon_rank_signal`

## Failures

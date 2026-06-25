# GOAL-09 Position-Band Diagnostics Prototype

GOAL-09 Position-Band Diagnostics Prototype: PASS_WITH_WARNINGS
GOAL-09 mode: `review_only`
Position-band diagnostic rows generated: `100`
Output grain: `trade_date + symbol`
Position actionability status: `never_actionable`
Outputs are non-actionable diagnostics only and are not position recommendations.
No actual position sizes, portfolio weights, target weights, order quantities, buy/sell/hold actions, target prices, expected returns for action, dashboards, paper/live trading paths, broker outputs, production behavior, backtests, factor-mining outputs, local lake files, or DQN/RL outputs were created.
Allowed next action: `fix_goal09_position_band_warnings_before_any_downstream_request`

## Evidence Inputs
- `outputs/risk_overlay/goal07b_review_only_risk_overlay.csv`
- `outputs/audits/goal07b_risk_overlay_calculation_report.md`
- `outputs/audits/goal07b_risk_overlay_calculation_audit.md`
- `outputs/audits/goal07b_risk_overlay_calculation_manifest.json`
- `outputs/audits/goal08a_recommendation_contract_design_report.md`
- `outputs/audits/goal08a_recommendation_contract_design_audit.md`
- `outputs/audits/goal08a_recommendation_contract_design_manifest.json`
- `outputs/audits/goal_storage01_local_research_lake_hardening_report.md`
- `outputs/audits/goal_storage01_local_research_lake_hardening_audit.md`
- `outputs/audits/goal_storage01_local_research_lake_hardening_manifest.json`
- `outputs/audits/goal08b0_recommendation_review_only_unlock_report.md`
- `outputs/audits/goal08b0_recommendation_review_only_unlock_audit.md`
- `outputs/audits/goal08b0_recommendation_review_only_unlock_manifest.json`
- `outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv`
- `outputs/audits/goal08b_recommendation_diagnostics_report.md`
- `outputs/audits/goal08b_recommendation_diagnostics_audit.md`
- `outputs/audits/goal08b_recommendation_diagnostics_manifest.json`
- `outputs/audits/goal090_position_band_review_only_unlock_report.md`
- `outputs/audits/goal090_position_band_review_only_unlock_audit.md`
- `outputs/audits/goal090_position_band_review_only_unlock_manifest.json`

## Position-Band Diagnostic Labels Used
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

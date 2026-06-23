# GOAL-07A Risk Rule Catalog Design

Status: `implemented_design_only`

Rules are catalog entries only. They are not executed in GOAL-07A.

Allowed future states: `PASS`, `WARNING`, `DEGRADED`, `BLOCKED`, `NOT_EVALUATED`.

Representative rules:
- `calibration_warning_minimum_warning_state`: if calibration_not_reliable_for_thresholding then future `overall_risk_state` should be `WARNING`.
- `weak_rank_signal_model_confidence`: if selected_score_variant_weak_rank_signal then future `model_confidence_risk_tag` should be `WEAK`.
- `single_provider_concentration`: if provider_source_concentration_disclosed then future `provider_concentration_risk_tag` should be `SINGLE_SOURCE_WARNING`.
- `data_quality_non_pass_blocks`: if data_quality_flags contain non-PASS then future `data_quality_risk_tag` should be `BLOCKED`.
- `leakage_failure_blocks`: if leakage_flags not PASS then future `overall_risk_state` should be `BLOCKED`.
- `panel_tier_floor_blocks`: if panel_tier below engineering_pilot then future `overall_risk_state` should be `BLOCKED`.
- `feature_instability_downgrades`: if feature_sign_instability_bounded then future `feature_stability_risk_tag` should be `DEGRADED`.
- `target_horizon_warning_downgrades`: if weak_target_horizon_rank_signal then future `target_horizon_risk_tag` should be `WARNING`.
- `source_health_warning_downgrades`: if source_health_score below future review threshold then future `source_health_risk_tag` should be `WARNING`.
- `gap_or_volatility_market_warning`: if future volatility/gap threshold warning then future `overall_risk_state` should be `WARNING`.

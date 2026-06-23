# GOAL-07A Risk Overlay Output Schema Design

Status: `implemented_design_only`

The future schema is categorical and review-only. GOAL-07A creates no real symbol-level rows.

Allowed future fields:
- `as_of_date`
- `target_trading_date`
- `symbol`
- `risk_overlay_version`
- `data_quality_risk_tag`
- `provider_concentration_risk_tag`
- `model_confidence_risk_tag`
- `calibration_risk_tag`
- `feature_stability_risk_tag`
- `target_horizon_risk_tag`
- `market_regime_risk_tag`
- `liquidity_proxy_risk_tag`
- `volatility_risk_tag`
- `gap_risk_tag`
- `source_health_risk_tag`
- `overall_risk_state`
- `risk_explanation_code`
- `risk_governance_flags`
- `review_only`

Forbidden fields:
- `buy`
- `sell`
- `hold`
- `recommended_position`
- `position_weight`
- `portfolio_weight`
- `risk_score`
- `final_score`
- `final_rank`
- `tradable_rank`
- `trade_signal`
- `order_action`
- `broker_instruction`

# GOAL-07A Risk Overlay Design

Status: `implemented_design_only`

GOAL-07A defines the V1 risk governance blueprint that may later sit between the GOAL-06D.1 review-only baseline and a future review-only recommendation contract.
It does not calculate risk overlay values, produce symbol-level risk rows, or generate recommendations, positions, portfolio weights, dashboards, trading data, production writes, factor mining, or DQN/RL artifacts.

## Upstream Warning Carry-Forward
- `calibration_not_reliable_for_thresholding`
- `feature_sign_instability_bounded`
- `provider_source_concentration_disclosed`
- `selected_score_variant_weak_rank_signal`
- `single_provider_mode_akshare_direct`
- `weak_target_horizon_rank_signal`
- `target_horizon_calibration_warning`

## Risk Domains
- `data_quality_risk`: PIT/data leakage and quality flags
- `provider_concentration_risk`: Provider/source concentration warnings
- `model_confidence_risk`: Weak selected baseline and score metadata
- `calibration_risk`: Calibration warning flags from GOAL-06D.1
- `feature_stability_risk`: Feature sign stability warnings
- `target_horizon_risk`: Weak target horizon diagnostics
- `market_regime_risk`: Market trend context
- `liquidity_proxy_risk`: Turnover/liquidity proxy context
- `volatility_risk`: 20-day volatility proxy context
- `gap_risk`: Premarket gap proxy context
- `source_health_risk`: Source health and source count context
- `governance_boundary_risk`: Downstream lock and review-only governance context

## Design Questions Answered
1. Consider data quality, provider concentration, model confidence, calibration, feature stability, target horizon, market regime, liquidity proxy, volatility, gap, source health, and governance boundary risks before any future recommendation-like output.
2. Carry GOAL-06D.1 weak-baseline, calibration, feature-stability, target-horizon, and provider-concentration warnings into future governance.
3. Consume only PIT-safe, review-only, contract-listed fields in a future GOAL-07B.
4. Future GOAL-07B may produce categorical risk tags and review-only governance flags after explicit unlock.
5. GOAL-07A forbids risk calculations, recommendation outputs, position outputs, scores, ranks, trading instructions, and real symbol tag assignment.
6. Hard data/leakage/governance failures should block future recommendation generation; weak model, calibration, provider, feature, target horizon, market, liquidity, volatility, and gap warnings should downgrade or warn.
7. GOAL-07B requires passing input contract, output schema, rule catalog, state machine, warning mapping, governance, boundary lock, and V2 factor lock audits.

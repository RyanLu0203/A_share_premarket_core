# GOAL-09.1 Warning Review and Dashboard Readiness

Status: `PASS_WITH_WARNINGS`

GOAL-09.1 is a review/readiness-only gate. It classifies GOAL-09 warning codes and defines the constraints any future GOAL-DASHBOARD-00 contract/layout design gate must honor.

It does not implement a dashboard and does not generate dashboard outputs, HTML, Streamlit, frontend code, or visual reports.

## Warning Classification

- `calibration_not_reliable_for_thresholding`: `dashboard_blocking_banner`
- `feature_sign_instability_bounded`: `row_level_and_summary_warning`
- `provider_source_concentration_disclosed`: `provider_concentration_banner`
- `selected_score_variant_weak_rank_signal`: `dashboard_blocking_banner`
- `single_provider_mode_akshare_direct`: `provider_concentration_banner`
- `target_horizon_calibration_warning`: `dashboard_blocking_banner`
- `weak_target_horizon_rank_signal`: `dashboard_blocking_banner`

## Future Dashboard Contract Requirements

- Future dashboard views must be `review_only` and `never_actionable`.
- Future dashboard views may display only audited GOAL-07B risk diagnostics, GOAL-08B recommendation diagnostics, GOAL-09 position-band diagnostics, warning propagation, actionability flags, and audit metadata.
- Future dashboard views must show non-actionable disclaimers globally and at row level.
- Future dashboard views must show all propagated warning codes.
- Future dashboard views must not display ranked Top-N, buy-candidate, position-candidate, or action-oriented lists.
- Future dashboard views must not include buy/sell/hold, target price, expected return for action, position size, portfolio weight, target weight, order quantity, trade action, or execution fields.
- Paper/live trading, broker integration, production, backtest, factor-mining, local-lake, and DQN/RL remain locked.

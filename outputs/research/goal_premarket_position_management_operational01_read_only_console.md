# Premarket Position Management Console

Read-only view over a validated snapshot. No execution workflow is exposed.

## Morning Overview

| daily_readiness_state | execution_mode | execution_time | generated_at | decision_asof_ts | target_trading_date | expected_previous_trading_date | data_cutoff | latest_available_canonical_date | freshness_code | holdings_mode | risk_state | symbols_evaluated | symbols_within_band | symbols_above_band | symbols_below_band | symbols_abstained | current_gross_exposure | current_cash_weight | action_instruction | research_only | not_trading_advice | not_for_execution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| READY_WITH_WARNINGS | deterministic_replay | 2026-07-01T08:30:00+08:00 | 2026-07-01T08:30:00+08:00 | 2026-07-01T08:30:00+08:00 | 2026-07-01 | 2026-06-30 | 2026-06-30 | 2026-06-30 | FRESH_T_MINUS_ONE_DATA | research_reference_portfolio | normal_risk_review_only | 41 | 29 | 0 | 0 | 12 | 0.9999999999 | 0 | none | True | True | True |

## Portfolio Risk State

| trading_date | asof_ts | portfolio_id | holdings_mode | gross_exposure | cash_weight | portfolio_volatility | ewma_volatility | beta_to_csi300 | drawdown_state | max_drawdown | cvar_95_daily | average_correlation | largest_risk_contributors | effective_number_of_positions | cluster_concentration | provider_quality_state | regime_state | predecessor_risk_state | research_only | not_trading_advice | not_for_execution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | research_reference_portfolio | research_reference_portfolio | 0.9999999999 | 0 | 0.2143067911 | 0.4750279654 | 1.1623355098 | normal_drawdown_review_only | -0.2775916142 | -0.027051004 | 0.233708303 | 300502.SZ:0.0754710803;002916.SZ:0.0568428868;000725.SZ:0.0512617372;002812.SZ:0.0479527014;000938.SZ:0.0452208573 | 41 | 0.3414634146 | warnings_quarantined | regime_unavailable_review_only | normal_risk_review_only | True | True | True |

## Exposure Envelope

| trading_date | asof_ts | current_gross_exposure | acceptable_gross_exposure_min | acceptable_gross_exposure_max | current_cash_weight | acceptable_cash_min | acceptable_cash_max | volatility_budget | beta_budget | risk_state | confidence | abstain | envelope_basis | research_only | not_trading_advice | not_for_execution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 0.9999999999 | 0.95 | 1 | 0 | 0 | 0.05 | 0.35 | 1.20 | normal_risk_review_only | 1 | False | risk_budget_constraints_from_predecessor_goal | True | True | True |

## Constraint Breaches

| trading_date | asof_ts | portfolio_id | symbol | holdings_mode | constraint_id | current_value | threshold | breach | severity | evidence_availability | fail_closed | action_instruction | constraint_source | research_only | not_trading_advice | not_for_execution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | research_reference_portfolio |  | research_reference_portfolio | research_reference_only_without_holdings | current_holdings_not_supplied | valid_snapshot_required | true | high | unavailable_no_current_holdings_snapshot | true | none | GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01 | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | research_reference_portfolio |  | research_reference_portfolio | cash_buffer_band | unavailable_no_current_cash_snapshot | 0.00_to_0.05 | true | high | unavailable_no_current_holdings_or_cash_snapshot | true | none | GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01 | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | research_reference_portfolio |  | research_reference_portfolio | liquidity_limit | unavailable_no_volume_or_amount_field | capacity_from_volume_or_amount | true | high | unavailable_no_volume_or_amount_field | true | none | GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01 | True | True | True |

## Position Band Status

| trading_date | asof_ts | symbol | current_weight | acceptable_band_min | acceptable_band_max | reference_policy_weight | band_status | confidence | constraint_breach | abstain | abstention_reason | provider_quality | regime_state | diagnostic_only | action_instruction | research_only | not_trading_advice | not_for_execution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 000002.SZ | 0.0243902439 | 0.0090384392 | 0.0361537569 | 0.0225960981 | WITHIN_BAND | 1 | not_evaluated_no_current_holdings | False |  | accepted_or_disclosed_warning | regime_unavailable_review_only | True | none | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 000063.SZ | 0.0243902439 | 0.0075912801 | 0.0303651205 | 0.0189782003 | WITHIN_BAND | 1 | not_evaluated_no_current_holdings | False |  | accepted_or_disclosed_warning | regime_unavailable_review_only | True | none | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 000100.SZ | 0.0243902439 | 0.01033336 | 0.0413334401 | 0.0258334001 | WITHIN_BAND | 1 | not_evaluated_no_current_holdings | False |  | accepted_or_disclosed_warning | regime_unavailable_review_only | True | none | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 000157.SZ | 0.0243902439 |  |  | 0.0306748169 | ABSTAIN | 0.82 | not_evaluated_no_current_holdings | True | unresolved_provider_discrepancy | quarantined_provider_discrepancy | regime_unavailable_review_only | True | none | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 000166.SZ | 0.0243902439 | 0.0129850895 | 0.0519403581 | 0.0324627238 | WITHIN_BAND | 1 | not_evaluated_no_current_holdings | False |  | accepted_or_disclosed_warning | regime_unavailable_review_only | True | none | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 000333.SZ | 0.0243902439 | 0.0136336316 | 0.0545345263 | 0.0340840789 | WITHIN_BAND | 1 | not_evaluated_no_current_holdings | False |  | accepted_or_disclosed_warning | regime_unavailable_review_only | True | none | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 000338.SZ | 0.0243902439 |  |  | 0.0271400045 | ABSTAIN | 0.7 | not_evaluated_no_current_holdings | True | sparse_or_unstable_regime_evidence | accepted_or_disclosed_warning | regime_unavailable_review_only | True | none | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 000425.SZ | 0.0243902439 | 0.0100426588 | 0.0401706353 | 0.025106647 | WITHIN_BAND | 1 | not_evaluated_no_current_holdings | False |  | accepted_or_disclosed_warning | regime_unavailable_review_only | True | none | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 000568.SZ | 0.0243902439 | 0.0095281293 | 0.0381125173 | 0.0238203233 | WITHIN_BAND | 1 | not_evaluated_no_current_holdings | False |  | accepted_or_disclosed_warning | regime_unavailable_review_only | True | none | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 000596.SZ | 0.0243902439 | 0.0094689631 | 0.0378758524 | 0.0236724078 | WITHIN_BAND | 1 | not_evaluated_no_current_holdings | False |  | accepted_or_disclosed_warning | regime_unavailable_review_only | True | none | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 000651.SZ | 0.0243902439 |  |  | 0.0331880887 | ABSTAIN | 0.82 | not_evaluated_no_current_holdings | True | unresolved_provider_discrepancy | quarantined_provider_discrepancy | regime_unavailable_review_only | True | none | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 000725.SZ | 0.0243902439 |  |  | 0.0323409163 | ABSTAIN | 0.7 | not_evaluated_no_current_holdings | True | sparse_or_unstable_regime_evidence | accepted_or_disclosed_warning | regime_unavailable_review_only | True | none | True | True | True |

## Top Risk Contributors

300502.SZ:0.0754710803;002916.SZ:0.0568428868;000725.SZ:0.0512617372;002812.SZ:0.0479527014;000938.SZ:0.0452208573

## Abstentions

| trading_date | asof_ts | symbol | abstain | abstention_reason | confidence | provider_quality | regime_state | research_only | not_trading_advice | not_for_execution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 000157.SZ | True | unresolved_provider_discrepancy | 0.82 | quarantined_provider_discrepancy | regime_unavailable_review_only | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 000338.SZ | True | sparse_or_unstable_regime_evidence | 0.7 | accepted_or_disclosed_warning | regime_unavailable_review_only | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 000651.SZ | True | unresolved_provider_discrepancy | 0.82 | quarantined_provider_discrepancy | regime_unavailable_review_only | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 000725.SZ | True | sparse_or_unstable_regime_evidence | 0.7 | accepted_or_disclosed_warning | regime_unavailable_review_only | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 000895.SZ | True | unresolved_provider_discrepancy | 0.82 | quarantined_provider_discrepancy | regime_unavailable_review_only | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 000938.SZ | True | sparse_or_unstable_regime_evidence | 0.7 | accepted_or_disclosed_warning | regime_unavailable_review_only | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 002415.SZ | True | unresolved_provider_discrepancy | 0.82 | quarantined_provider_discrepancy | regime_unavailable_review_only | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 002812.SZ | True | sparse_or_unstable_regime_evidence;unresolved_provider_discrepancy | 0.52 | quarantined_provider_discrepancy | regime_unavailable_review_only | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 002821.SZ | True | sparse_or_unstable_regime_evidence | 0.7 | accepted_or_disclosed_warning | regime_unavailable_review_only | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 002916.SZ | True | sparse_or_unstable_regime_evidence | 0.7 | accepted_or_disclosed_warning | regime_unavailable_review_only | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 300033.SZ | True | sparse_or_unstable_regime_evidence;unresolved_provider_discrepancy;unstable_band_sensitivity | 0.34 | quarantined_provider_discrepancy | regime_unavailable_review_only | True | True | True |
| 2026-07-01 | 2026-07-01T08:30:00+08:00 | 300502.SZ | True | sparse_or_unstable_regime_evidence;unstable_band_sensitivity | 0.52 | accepted_or_disclosed_warning | regime_unavailable_review_only | True | True | True |

## Data Quality / Provider Warnings

| warning_code | scope | count | detail | source_goal |
| --- | --- | --- | --- | --- |
| MATERIAL_PROVIDER_DISCREPANCIES_QUARANTINED | phase1_provider_reconciliation | 6 | material baostock/akshare-sina forward-return differences excluded from risk fitting | GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01 |
| ADJUSTMENT_CONVENTION_UNRESOLVED | phase1_provider_reconciliation | 1 | committed old panel lacks close/raw-adjusted metadata, so close-price and adjustment reconciliation remain disclosed but unresolved | GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01 |
| DUPLICATE_POLICY_EXPOSURE_DISCLOSED | phase4_policy_selection | 1 | diagonal ERC is mathematically equivalent to inverse-volatility under the current diagonal proxy | GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01 |
| NO_SINGLE_ROBUST_POLICY_WINNER | phase4_policy_selection | 1 | top risk-first policy scores are close; band reference remains conservative research-only | GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01 |
| POSITION_BAND_ABSTENTIONS_PRESENT | phase5_position_bands | 12 | symbols with insufficient confidence or constraint blockers abstain from precise bands | GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01 |
| NO_REAL_HOLDINGS_SNAPSHOT_REFERENCE_MODE | holdings_snapshot | 1 | no owner-supplied holdings snapshot exists; operational outputs use explicit research_reference_portfolio mode | GOAL-PREMARKET-POSITION-MANAGEMENT-OPERATIONAL-01 |
| DAILY_READINESS_READY_WITH_WARNINGS | daily_data_readiness | 1 | premarket run may be reviewed, but warnings must remain visible and fail-closed rules remain active | GOAL-PREMARKET-POSITION-MANAGEMENT-OPERATIONAL-01 |

## Provenance / Audit

| goal | snapshot_root | readiness | audit |
| --- | --- | --- | --- |
| GOAL-PREMARKET-POSITION-MANAGEMENT-OPERATIONAL-01 | outputs/research/premarket_position_management | READY_WITH_WARNINGS | outputs/audits/goal_premarket_position_management_operational01_audit.md |

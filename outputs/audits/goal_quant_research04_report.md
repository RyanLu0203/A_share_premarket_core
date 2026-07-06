# GOAL-QUANT-RESEARCH-04 Regime-Conditional Factor Evaluation Gate

## 1. Goal status
GOAL-QUANT-RESEARCH-04 Regime-Conditional Factor Evaluation Gate: PASS_WITH_WARNINGS

## 2. What this gate does
Evaluates the 30 refined Candidate02 factors CONDITIONED on the reconciled Regime02 refined market-regime labels, using committed Provider02B forward returns only post-hoc. It is research-only and creates no recommendation, position, portfolio, or trading outputs.

## 3. Source-backed input lineage
- `outputs/research/goal_regime_label_research02_refined_factor_regime_bridge.csv`
- `outputs/research/goal_regime_label_research02_refined_date_regime_labels.csv`
- `outputs/research/goal_alpha_factor_candidate02_refined_candidate_registry.csv`
- `outputs/research/goal_alpha_factor_candidate02_refined_candidate_panel.csv`
- `outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv`

## 4. No-lookahead / point-in-time policy
Factor values and regime labels are committed current-or-past evidence. Forward returns and benchmark-excess returns are consumed only to compute post-hoc IC/RankIC, spread, and stability metrics; they are never inputs to factor values or regime labels. No production predictive validity is claimed.

## 5. Evaluated coverage
Factors: `30`; informative + all regime labels: `6`; distinct date regimes: `['insufficient_composite_regime_evidence_review_only', 'liquidity_stress_review_only', 'mixed_uncertain_review_only', 'risk_off_high_vol_review_only', 'risk_on_high_vol_review_only', 'risk_on_low_vol_review_only']`.

## 6. Regime-conditional evaluation summary
Rows (factor x regime): `180`. Status distribution: `{'conditionally_useful': 26, 'not_ready': 154}`.

## 7. Factor stability & predictive-usefulness classification
Per-factor overall status distribution: `{'conditionally_useful': 21, 'not_ready': 9}`.

## 8. Leakage / PIT checks
Checks: `5`; all pass: `True`.

## 9. Sample-size validity
Regime-conditional cells below the `500`-valid-row threshold (or non-informative regimes) are classified not_ready by insufficient sample.

## 10. Regime transition sensitivity
Transition-sensitivity rows: `30` (review-only regime dispersion, not a market-timing signal).

## 11. Factor decisions
ready_factor_count: `0`; conditionally_useful factors: `21`; ready factor ids: `[]`.

## 12. Why this does not unlock recommendation tiering
Recommendation tiering (GOAL-REC-TIERING-01) remains locked_future and is unlocked only when ready_factor_count is positive AND the User explicitly approves. This gate does not create actionable outputs or unlock any downstream stage.

## 13. Locked downstream boundaries
GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, portfolio backtests, trading, production, local-lake, broker, factor-mining, and DQN/RL remain locked.

## 14. Recommended next goal
`no_downstream_unlock_ready_factor_count_zero`.

# GOAL-QUANT-RESEARCH-02 Alpha Candidate Factor Validity Evaluation Gate

## 1. Goal status
GOAL-QUANT-RESEARCH-02 Alpha Candidate Factor Validity Evaluation Gate: PASS_WITH_WARNINGS

## 2. Current MVP and alpha-candidate context
GOAL-ALPHA-FACTOR-CANDIDATE-01 constructed 13 research-only candidate factors over 50 symbols and 120 dates. This gate evaluates those candidates only after construction is complete.

## 3. Source-backed evidence lineage
- `outputs/research/goal_alpha_factor_candidate01_candidate_registry.csv`
- `outputs/research/goal_alpha_factor_candidate01_factor_candidate_panel.csv`
- `outputs/research/goal_alpha_factor_candidate01_coverage_summary.csv`
- `outputs/research/goal_alpha_factor_candidate01_construction_warnings.csv`
- `outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv`
- `outputs/mvp/goal_mvp01_symbol_diagnostic_table.csv`
- `outputs/mvp/goal_mvp01_review_queue.csv`
- `outputs/research/goal_quant_research01_factor_registry.csv`
- `outputs/research/goal_quant_research01_score_validity_classification.csv`
- `outputs/research/goal_quant_research01_trial_registry.csv`

## 4. Alpha candidates evaluated
Factors evaluated: `13`.

## 5. Coverage and bucket diagnostics
Coverage rows: `13`. Bucket metric rows: `116`.

## 6. Forward-return and benchmark-excess-return metrics
Forward returns and benchmark-excess returns from Provider02B are used only post-hoc after candidate values, quantiles, and buckets already exist.

## 7. IC / RankIC diagnostics
IC/RankIC rows: `13`.

## 8. Monotonicity and spread diagnostics
Monotonicity rows: `13`.

## 9. Rolling stability diagnostics
The gate evaluates 20-date rolling windows, 40-date rolling windows, first-half/second-half splits, and calendar-month windows when enough dates are available.

## 10. Horizon consistency diagnostics
Horizon consistency rows: `13`.

## 11. Score validity classification
Classification counts: `{'factor_requires_redefinition': 2, 'factor_signal_weak_or_unreliable': 11}`.

## 12. Factor readiness for recommendation tiering
Ready factor count: `0`.
Overall validity: `no_factor_ready_for_rec_tiering`.

## 13. Trial registry and anti-overfitting controls
Every alpha candidate is recorded as a trial. The policy forbids formula tuning to forward returns, unregistered repeated search, single-horizon promotion, promotion without stability checks, and portfolio-return or equity-curve selection.

## 14. Locked downstream boundaries
GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, portfolio backtests, trading, production, local-lake, broker, factor-mining, and DQN/RL remain locked.

## 15. Recommended next goal
`GOAL-ALPHA-FACTOR-CANDIDATE-02_or_GOAL-ALPHA-RESEARCH-REFINEMENT-01`.

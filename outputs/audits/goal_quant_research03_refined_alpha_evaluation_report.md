# GOAL-QUANT-RESEARCH-03 Refined Alpha Factor Validity Evaluation Gate

## 1. Goal status
GOAL-QUANT-RESEARCH-03 Refined Alpha Factor Validity Evaluation Gate: PASS_WITH_WARNINGS

## 2. Current Candidate02 context
GOAL-ALPHA-FACTOR-CANDIDATE-02 constructed 30 refined alpha candidates over 50 symbols and 120 dates. This gate evaluates those refined values only after construction is complete.

## 3. Source-backed evidence lineage
- `outputs/research/goal_alpha_factor_candidate02_refined_candidate_registry.csv`
- `outputs/research/goal_alpha_factor_candidate02_refined_candidate_panel.csv`
- `outputs/research/goal_alpha_factor_candidate02_coverage_summary.csv`
- `outputs/research/goal_alpha_factor_candidate02_construction_warnings.csv`
- `outputs/research/goal_alpha_factor_candidate02_trial_registry.csv`
- `outputs/research/goal_alpha_factor_candidate02_intraday_redefinition_status.csv`
- `outputs/research/goal_quant_research02_alpha_evaluation_panel.csv`
- `outputs/research/goal_quant_research02_alpha_factor_score_validity_classification.csv`
- `outputs/research/goal_quant_research02_alpha_factor_ic_rankic_summary.csv`
- `outputs/research/goal_quant_research02_alpha_factor_monotonicity_summary.csv`
- `outputs/research/goal_quant_research02_alpha_factor_rolling_stability_summary.csv`
- `outputs/research/goal_quant_research02_alpha_factor_horizon_consistency_summary.csv`
- `outputs/research/goal_quant_research02_alpha_factor_bucket_metrics.csv`
- `outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv`
- `outputs/mvp/goal_mvp01_symbol_diagnostic_table.csv`
- `outputs/mvp/goal_mvp01_review_queue.csv`
- `outputs/diagnostics/goal_risk_tiering01_risk_tiered_diagnostics.csv`
- `outputs/diagnostics/goal_risk_tiering011_downside_risk_diagnostics.csv`

## 4. Refined alpha candidates evaluated
Refined factors evaluated: `30`.
Evaluation panel rows: `180000`.

## 5. Coverage and bucket diagnostics
Coverage rows: `30`. Bucket metric rows: `270`.

## 6. Forward-return and benchmark-excess-return metrics
Forward returns and benchmark-excess returns from Provider02B are used only post-hoc after refined factor values, quantiles, and buckets already exist.

## 7. IC / RankIC diagnostics
IC/RankIC rows: `30`.

## 8. Monotonicity and spread diagnostics
Monotonicity rows: `30`.

## 9. Rolling stability diagnostics
The gate evaluates 20-date rolling windows, 40-date rolling windows, first-half/second-half splits, and calendar-month windows when enough dates are available.

## 10. Horizon consistency diagnostics
Horizon consistency rows: `30`.

## 11. Refinement improvement diagnostics versus Quant02 source factors
Improvement rows: `30`. Improvement counts: `{'refined_candidate_not_improved': 9, 'refined_candidate_partially_improved': 20, 'refined_candidate_too_sparse': 1}`.

## 12. Score validity classification
Classification counts: `{'factor_signal_weak_or_unreliable': 29, 'factor_too_sparse_after_refinement': 1}`.

## 13. Factor readiness for recommendation tiering
Ready factor count: `0`.
Overall validity: `no_refined_factor_ready_but_partial_improvement_available`.

## 14. Trial registry and anti-overfitting controls
Every refined alpha candidate is recorded as a trial. The policy forbids formula tuning to forward returns, altering refined definitions from post-hoc results, unregistered repeated search, single-horizon promotion, and portfolio-return or equity-curve selection.

## 15. Artifact size and partitioning policy
The refined evaluation panel is partitioned under `outputs/research/goal_quant_research03_refined_evaluation_panel_parts/`. The per-artifact size limit is `99614720` bytes and the recorded maximum output artifact size is `20419350` bytes.

## 16. Locked downstream boundaries
GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, portfolio backtests, trading, production, local-lake, broker, factor-mining, and DQN/RL remain locked.

## 17. Recommended next goal
`GOAL-DATA-EXPANSION-RESEARCH-01_or_GOAL-REGIME-LABEL-RESEARCH-01`.

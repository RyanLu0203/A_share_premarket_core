# GOAL-REGIME-LABEL-RESEARCH-02 Expanded Market Regime Label Refinement Gate

## 1. Goal status
GOAL-REGIME-LABEL-RESEARCH-02 Expanded Market Regime Label Refinement Gate: PASS_WITH_WARNINGS

## 2. Current DataExpansion01 context
GOAL-DATA-EXPANSION-RESEARCH-01 produced committed broad-index, sector/concept, liquidity, and expanded date/symbol regime evidence over offline replay. This gate refines the Regime01 labels using that expanded evidence only.

## 3. Why refined regime labels are needed
Refined labels cross-check the single-benchmark Regime01 composite against broad-index and sector cross-sections, adding a research confidence tier. They are conditioning context only, not market timing signals.

## 4. Source-backed input lineage
- `outputs/research/goal_regime_label_research01_date_regime_labels.csv`
- `outputs/research/goal_regime_label_research01_symbol_regime_context.csv`
- `outputs/data_expansion/goal_data_expansion_research01/expanded_date_regime_feature_panel.csv`
- `outputs/data_expansion/goal_data_expansion_research01/expanded_symbol_context_panel.csv`

## 5. No-lookahead refinement policy
Refinement uses only current-date or trailing committed Regime01 and DataExpansion01 evidence. Future returns, benchmark-excess forward returns, label-ready fields, and post-hoc factor performance are excluded, and no factor predictive validity is evaluated.

## 6. Regime dimensions refined
Dimensions: `benchmark_trend, benchmark_volatility, breadth, dispersion, liquidity, downside_risk, composite`.

## 7. Refined date-level regime coverage
Refined date rows: `120` over `120` dates.

## 8. Refined symbol-level regime context coverage
Refined symbol rows: `6000` over `50` symbols.

## 9. Expanded cross-source agreement summary
Agreement rows: `18`. Dimensions covered: `{'benchmark_trend': 3, 'benchmark_volatility': 3, 'breadth': 3, 'dispersion': 3, 'downside_risk': 3, 'liquidity': 3}`.

## 10. Regime confidence tier distribution
Confidence tiers: `{'high_confidence_review_only': 117, 'medium_confidence_review_only': 3}`.

## 11. Refined regime transition summary
Transition rows: `50`.

## 12. Refined regime-factor bridge summary
Bridge rows: `180000` across `30` refined factors. The bridge carries no forward returns, benchmark-excess returns, IC/RankIC, hit rates, portfolio returns, recommendation labels, or position fields.

## 13. Construction warnings
Warning rows: `6`. Warning codes: `['expanded_cross_source_divergence', 'expanded_evidence_unavailable_offline_replay', 'refined_regime_dimension_not_constructed', 'sparse_refined_regime_label']`.

## 14. External data quality context
Source coverage score: `0.68`; external data quality score: `0.72`. Offline-unavailable flow and margin evidence is treated as missing, not zero.

## 15. Why this is not factor evaluation or recommendation tiering
Refined regime labels are rule-based research context only. The gate does not evaluate factor predictive validity, does not optimize labels against future returns or factor performance, and does not promote factors to recommendation tiering.

## 16. Locked downstream boundaries
GOAL-QUANT-RESEARCH-04, GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, portfolio backtests, trading, production, local-lake, broker, factor-mining, and DQN/RL remain locked.

## 17. Recommended next goal
`GOAL-QUANT-RESEARCH-04-REGIME-CONDITIONAL-FACTOR-EVALUATION-GATE`.

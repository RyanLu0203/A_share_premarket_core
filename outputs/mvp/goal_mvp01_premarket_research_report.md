# GOAL-MVP-01 Premarket Research Diagnostic Terminal

## 1. MVP status
GOAL-MVP-01 Premarket Research Diagnostic Terminal Gate: PASS_WITH_WARNINGS
The terminal turns committed source-backed evidence into a bounded premarket research diagnostic report and supporting CSVs.

## 2. Report date and run mode
Report date: `2026-05-21`.
Run mode: `committed_evidence_replay`. This is committed evidence replay, not a same-day live signal.

## 3. Data lineage
- `outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage03_risk_diagnostics.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage03_recommendation_diagnostics.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage03_position_band_diagnostics.csv`
- `outputs/diagnostics/goal_risk_tiering01_risk_tiered_diagnostics.csv`
- `outputs/diagnostics/goal_risk_tiering011_downside_risk_diagnostics.csv`
- `outputs/research/goal_quant_research01_factor_registry.csv`
- `outputs/research/goal_quant_research01_score_validity_classification.csv`
- `outputs/research/goal_quant_research01_factor_bucket_metrics.csv`
- `outputs/research/goal_quant_research01_factor_ic_rankic_summary.csv`
- `outputs/research/goal_quant_research01_factor_monotonicity_summary.csv`
- `outputs/research/goal_quant_research01_factor_rolling_stability_summary.csv`
- `outputs/research/goal_quant_research01_trial_registry.csv`

## 4. Coverage summary
Symbols on report date: `50`.
Universe coverage: `50_symbols;providers=baostock;universe_modes=provider_panel_candidate_universe_review_only`.

## 5. Market context summary
Benchmark symbol: `000300.SH`.
Latest committed benchmark returns: 1d `0.0129618931`, 5d `0.0274122987`, 20d `0.0331377307`.
These values are reported as context from committed evidence only. The terminal does not infer market direction or timing.

## 6. Risk and downside-risk summary
Risk score bucket distribution: `{'HIGH_RISK_REVIEW_ONLY': 2, 'LOW_RISK_REVIEW_ONLY': 14, 'MEDIUM_RISK_REVIEW_ONLY': 34}`.
Downside-risk bucket distribution: `{'HIGH_DOWNSIDE_RISK_REVIEW_ONLY': 11, 'LOW_DOWNSIDE_RISK_REVIEW_ONLY': 15, 'MEDIUM_DOWNSIDE_RISK_REVIEW_ONLY': 24}`.

## 7. Factor validity summary
Factors evaluated: `11`.
Ready factor count: `0`.
Overall validity: `no_factor_ready_for_rec_tiering`.
No factor is currently approved for recommendation tiering.
This terminal is research-only and cannot produce actionable recommendations.

## 8. Review queues
Active review queue distribution: `{'clean_research_watch_queue': 11, 'factor_not_ready_review_queue': 50, 'high_downside_risk_review_queue': 13, 'liquidity_review_queue': 11, 'volatility_momentum_review_queue': 28}`.
`clean_research_watch_queue` is not an action list. It only means fewer data/risk/factor warnings and manual review may start there.

## 9. What this terminal can help with
- Review source-backed data coverage before market open.
- Identify symbols needing data, risk, downside-risk, liquidity, volatility, or factor-readiness review.
- See why factor evidence is not yet ready for recommendation tiering.
- Preserve a research governance trail from committed evidence only.

## 10. What this terminal cannot do
- It cannot produce directional trade labels, target prices, position sizes, target weights, order quantities, portfolio returns, equity curves, dashboards, trading outputs, broker integrations, production writes, local-lake outputs, factor-mining outputs, or DQN/RL outputs.
- It cannot turn committed replay evidence into live market timing advice.

## 11. Locked downstream boundaries
GOAL-ALPHA-FACTOR-CANDIDATE-01, GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, portfolio backtests, paper/live trading, broker integration, production writes, local-lake writes, factor-mining, and DQN/RL remain locked or deleted from active mainline.

## 12. Recommended next research goal
`GOAL-ALPHA-FACTOR-CANDIDATE-01`.

# GOAL-QUANT-RESEARCH-02 Alpha Candidate Factor Validity Evaluation Gate

Status: `PASS_WITH_WARNINGS`

This gate is research-only. It evaluates the 13 GOAL-ALPHA-FACTOR-CANDIDATE-01 factors with committed Provider02B labels used only as post-hoc evaluation outcomes.

## Outputs
- `outputs/research/goal_quant_research02_alpha_evaluation_panel.csv`
- `outputs/research/goal_quant_research02_alpha_factor_coverage_summary.csv`
- `outputs/research/goal_quant_research02_alpha_factor_bucket_metrics.csv`
- `outputs/research/goal_quant_research02_alpha_factor_ic_rankic_summary.csv`
- `outputs/research/goal_quant_research02_alpha_factor_monotonicity_summary.csv`
- `outputs/research/goal_quant_research02_alpha_factor_rolling_stability_summary.csv`
- `outputs/research/goal_quant_research02_alpha_factor_horizon_consistency_summary.csv`
- `outputs/research/goal_quant_research02_alpha_factor_score_validity_classification.csv`
- `outputs/research/goal_quant_research02_trial_registry.csv`

## Method
The gate joins alpha candidate values to Provider02B forward-return labels, computes coverage, bucket metrics, IC/RankIC, monotonicity, rolling stability, horizon consistency, score validity classification, and a trial registry.

## Result
- Factors evaluated: `13`
- Evaluation rows: `78000`
- Ready factor count: `0`
- Overall validity: `no_factor_ready_for_rec_tiering`
- Recommended next goal: `GOAL-ALPHA-FACTOR-CANDIDATE-02_or_GOAL-ALPHA-RESEARCH-REFINEMENT-01`

## Locked Boundary
No recommendation rows, position rows, BUY/SELL/HOLD labels, target prices, position sizes, weights, orders, portfolio returns, equity curves, dashboards, HTML, Streamlit, frontend, visual reports, trading outputs, broker outputs, production outputs, local-lake files, factor-mining outputs, or DQN/RL outputs are created.

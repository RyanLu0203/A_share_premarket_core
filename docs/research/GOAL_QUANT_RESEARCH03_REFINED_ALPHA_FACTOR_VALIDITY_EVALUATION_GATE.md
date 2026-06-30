# GOAL-QUANT-RESEARCH-03 Refined Alpha Factor Validity Evaluation Gate

Status: `PASS_WITH_WARNINGS`

This gate is research-only. It evaluates the 30 GOAL-ALPHA-FACTOR-CANDIDATE-02 refined factors with committed Provider02B labels used only as post-hoc evaluation outcomes.

## Outputs
- `outputs/research/goal_quant_research03_refined_evaluation_panel_index.csv`
- `outputs/research/goal_quant_research03_refined_factor_coverage_summary.csv`
- `outputs/research/goal_quant_research03_refined_factor_bucket_metrics.csv`
- `outputs/research/goal_quant_research03_refined_factor_ic_rankic_summary.csv`
- `outputs/research/goal_quant_research03_refined_factor_monotonicity_summary.csv`
- `outputs/research/goal_quant_research03_refined_factor_rolling_stability_summary.csv`
- `outputs/research/goal_quant_research03_refined_factor_horizon_consistency_summary.csv`
- `outputs/research/goal_quant_research03_refined_factor_improvement_summary.csv`
- `outputs/research/goal_quant_research03_refined_factor_score_validity_classification.csv`
- `outputs/research/goal_quant_research03_trial_registry.csv`
- `outputs/research/goal_quant_research03_refined_evaluation_panel_parts/*.csv`

## Method
The gate joins refined candidate values to Provider02B forward-return labels, computes coverage, bucket metrics, IC/RankIC, monotonicity, rolling stability, horizon consistency, score validity, improvement versus Quant02 source factors, and a trial registry.

## Result
- Refined factors evaluated: `30`
- Evaluation rows: `180000`
- Ready factor count: `0`
- Overall validity: `no_refined_factor_ready_but_partial_improvement_available`
- Recommended next goal: `GOAL-DATA-EXPANSION-RESEARCH-01_or_GOAL-REGIME-LABEL-RESEARCH-01`

## Locked Boundary
No recommendation rows, position rows, BUY/SELL/HOLD labels, target prices, position sizes, weights, orders, portfolio returns, equity curves, dashboards, HTML, Streamlit, frontend, visual reports, trading outputs, broker outputs, production outputs, local-lake files, factor-mining outputs, or DQN/RL outputs are created.

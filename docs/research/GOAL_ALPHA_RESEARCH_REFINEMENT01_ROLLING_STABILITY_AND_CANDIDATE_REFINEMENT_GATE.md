# GOAL-ALPHA-RESEARCH-REFINEMENT-01 Rolling Stability and Candidate Refinement Gate

Status: `PASS_WITH_WARNINGS`

This gate is research-only. It diagnoses Quant02 rolling instability and writes proposed refined candidate designs without constructing or evaluating refined factor panels.

## Outputs
- `outputs/research/goal_alpha_research_refinement01_instability_attribution.csv`
- `outputs/research/goal_alpha_research_refinement01_conditional_stability_summary.csv`
- `outputs/research/goal_alpha_research_refinement01_refined_candidate_designs.csv`
- `outputs/research/goal_alpha_research_refinement01_intraday_redefinition_plan.csv`
- `outputs/research/goal_alpha_research_refinement01_trial_registry_update.csv`

## Method
The gate analyzes aligned and inverse rolling windows, sign flips, half/month behavior, conditional stability slices, and intraday pressure bucket imbalance using committed Quant02, Alpha Candidate 01, Provider02B, and MVP evidence.

## Result
- Promising candidates diagnosed: `6`
- Refined candidate design rows: `30`
- Intraday redefinition rows: `4`
- Recommended next goal: `GOAL-ALPHA-FACTOR-CANDIDATE-02`

## Locked Boundary
No refined factor panel, recommendation rows, position rows, BUY/SELL/HOLD labels, target prices, position sizes, weights, orders, portfolio returns, equity curves, dashboards, HTML, Streamlit, frontend, visual reports, trading outputs, broker outputs, production outputs, local-lake files, factor-mining outputs, or DQN/RL outputs are created.

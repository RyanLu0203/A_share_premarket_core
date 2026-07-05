# GOAL-QUANT-RESEARCH-04 Regime-Conditional Factor Evaluation Gate

Status: `PASS_WITH_WARNINGS`

This gate evaluates refined alpha factors conditioned on committed Regime02 refined regime labels, research-only and no-lookahead.

## Network Policy
Offline committed-evidence replay only. No live provider fetches; provider network default remains disabled.

## Outputs
- `outputs/research/goal_quant_research04_regime_conditional_evaluation_summary.csv`
- `outputs/research/goal_quant_research04_factor_overall_status.csv`
- `outputs/research/goal_quant_research04_regime_transition_sensitivity.csv`
- `outputs/research/goal_quant_research04_leakage_pit_checks.csv`
- `outputs/research/goal_quant_research04_construction_warnings.csv`

## Method
For each (factor, regime) the gate computes regime-conditional coverage, IC/RankIC, top-minus-bottom benchmark-excess spread, directional alignment, and month-window sign stability, then assigns a three-state status (not_ready / conditionally_useful / ready). Per-factor status aggregates across regimes; a factor is a rec-tiering candidate only when it is 'ready' in a sufficiently sampled regime.

## Result
- Factor x regime rows: `180`
- ready_factor_count: `0`
- Recommended next goal: `no_downstream_unlock_ready_factor_count_zero`

## Locked Boundary
Regime-conditional evaluation is research context only. It is not a trading signal, recommendation, position, portfolio, dashboard, production, local-lake, factor-mining, broker, or DQN/RL output, and it does not unlock recommendation tiering.

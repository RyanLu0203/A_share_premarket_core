# GOAL-REGIME-LABEL-RESEARCH-02 Expanded Market Regime Label Refinement Gate

Status: `PASS_WITH_WARNINGS`

This gate refines the deterministic no-lookahead Regime01 market regime labels by integrating committed DataExpansion01 expanded regime evidence only.

## Network Policy
Offline committed-evidence replay only. No live provider fetches are performed and provider network default remains disabled.

## Outputs
- `outputs/research/goal_regime_label_research02_refined_date_regime_labels.csv`
- `outputs/research/goal_regime_label_research02_refined_symbol_regime_context.csv`
- `outputs/research/goal_regime_label_research02_refined_regime_coverage_summary.csv`
- `outputs/research/goal_regime_label_research02_refined_regime_transition_summary.csv`
- `outputs/research/goal_regime_label_research02_expanded_agreement_summary.csv`
- `outputs/research/goal_regime_label_research02_refined_factor_regime_bridge.csv`
- `outputs/research/goal_regime_label_research02_construction_warnings.csv`

## Method
Regime01 per-dimension labels are cross-checked against DataExpansion01 broad-index trend/volatility, sector breadth/dispersion, and market liquidity-pressure evidence. Divergent dimensions are conservatively neutralized before the refined composite is recomputed, and a research confidence tier records how many expanded dimensions agree.

## Result
- Refined date-level rows: `120`
- Refined symbol-level rows: `6000`
- Refined bridge rows: `180000`
- Recommended next goal: `GOAL-QUANT-RESEARCH-04-REGIME-CONDITIONAL-FACTOR-EVALUATION-GATE`

## Locked Boundary
Refined regime labels are research conditioning labels only. They are not market timing signals, trading signals, recommendations, positions, portfolios, dashboards, production outputs, local-lake outputs, factor-mining outputs, broker outputs, or DQN/RL outputs, and no factor predictive validity is evaluated.

# GOAL-V1-DIAGNOSTIC-COVERAGE-03 Source-Backed Multi-Symbol Diagnostics Gate

GOAL-V1-DIAGNOSTIC-COVERAGE-03 Source-Backed Multi-Symbol Diagnostics Gate: PASS_WITH_WARNINGS
Mode: `review_only_source_backed_multi_symbol_diagnostics_gate`
Primary input: `outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv`

## Coverage
- Risk diagnostic rows: `6000`
- Recommendation diagnostic rows: `6000`
- Position-band diagnostic rows: `6000`
- Unique symbols: `50`
- Unique trade dates: `120`
- Date range: `2025-11-19` to `2026-05-21`
- Keys match across diagnostic families: `true`
- Diagnostic group variation status: `diagnostic_group_variation_available`
- Recommended next goal: `GOAL-10B.3`

## Boundary
- Diagnostics are derived only from the GOAL-DATA-PROVIDER-02B normalized source-backed panel.
- Canonical GOAL-07B, GOAL-08B, and GOAL-09 artifacts are preserved and not overwritten.
- Recommendation diagnostics are never actionable and contain no BUY/SELL/HOLD, target price, position size, weight, or order output.
- GOAL-10B.3 is implemented only by its own separate review-only revalidation gate; GOAL-10C, GOAL-10D, dashboards, trading, production, broker, local-lake, factor-mining, and DQN/RL remain locked.

## Warnings
- all_blocked_recommendation_collapse_detected
- all_zero_or_blocked_position_band_collapse_detected
- diagnostic_group_variation_available
- recommendation_and_position_outputs_remain_never_actionable

## Failures

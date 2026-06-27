# GOAL-V1-DIAGNOSTIC-COVERAGE-02 Multi-Symbol Diagnostics Expansion

GOAL-V1-DIAGNOSTIC-COVERAGE-02 Multi-Symbol Diagnostics Expansion: PASS_WITH_WARNINGS
Mode: `review_only_multi_symbol_diagnostic_coverage_expansion`

## Coverage
- Source Stage 6C sample: `outputs/stage6c/STAGE6C_engineering_expanded_validation_dataset_sample.csv`
- Risk diagnostic rows: `8`
- Recommendation diagnostic rows: `8`
- Position-band diagnostic rows: `8`
- Unique symbols: `2`
- Unique trade dates: `4`
- Keys match across diagnostic families: `true`

## Boundary
- Diagnostics are derived only from existing committed Stage 6C approved-symbol evidence.
- Canonical GOAL-07B, GOAL-08B, and GOAL-09 artifacts are preserved and not overwritten.
- All recommendation and position-band outputs are `never_actionable` and are not buy/sell/hold actions, target prices, position sizes, weights, orders, or portfolio instructions.
- GOAL-10B.2 and GOAL-10C may only exist as explicit review-only non-actionable diagnostic gates over this bounded coverage. GOAL-10D, Dashboard / Daily Report UI, signal and portfolio backtest promotion, trading, production, broker, local-lake, factor-mining, and DQN/RL remain locked.

## Warnings
- canonical_goal08b_not_aligned_to_multi_symbol_diagnostics
- canonical_goal09_not_aligned_to_multi_symbol_diagnostics
- forward_return_20d_not_available_for_multi_symbol_diagnostics
- forward_return_3d_5d_incomplete_in_multi_symbol_source
- goal_data_label01_no_trade_date_symbol_overlap_with_multi_symbol_diagnostics
- multi_symbol_source_uses_contract_demo_fixture

## Failures

# GOAL-V1-DIAGNOSTIC-COVERAGE-02 Multi-Symbol Diagnostics Expansion

Status: `PASS_WITH_WARNINGS`

GOAL-V1-DIAGNOSTIC-COVERAGE-02 creates a bounded review-only diagnostic coverage bridge for the next revalidation request. It uses the committed Stage 6C approved-symbol sample to generate separate non-actionable risk, recommendation, and position-band diagnostic coverage rows at `trade_date + symbol` grain.

It does not overwrite the canonical GOAL-07B, GOAL-08B, or GOAL-09 artifacts and does not run any backtest.

## Outputs

- `outputs/diagnostics/goal_v1_diagnostic_coverage02_risk_diagnostics.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage02_recommendation_diagnostics.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage02_position_band_diagnostics.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage02_coverage_summary.csv`
- `outputs/audits/goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_report.md`
- `outputs/audits/goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_manifest.json`
- `outputs/audits/goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_audit.md`

## Current Coverage

- Diagnostic rows per family: `8`
- Unique symbols: `2`
- Unique trade dates: `4`
- Forward-return 20d available: `false`
- Multi-horizon backtest ready: `false`

## Locked Boundary

GOAL-10B.2 and GOAL-10C may only exist as explicit review-only non-actionable diagnostic gates over this bounded coverage. GOAL-10D, Dashboard / Daily Report UI, signal and portfolio backtest promotion, trading, production, broker integration, local-lake writes, factor-mining, and DQN/RL remain locked.

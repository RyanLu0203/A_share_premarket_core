# GOAL-RISK-TIERING-01 Risk Severity And Numeric Score Tiering Gate

Status: `PASS_WITH_WARNINGS`

GOAL-RISK-TIERING-01 is a review-only risk severity tiering gate over committed GOAL-V1-DIAGNOSTIC-COVERAGE-03 risk rows and the GOAL-DATA-PROVIDER-02B source-backed evaluation panel. It creates a separate non-actionable risk-tiering artifact and does not overwrite canonical GOAL-07B or DC03 risk diagnostics.

## Inputs

- `outputs/diagnostics/goal_v1_diagnostic_coverage03_risk_diagnostics.csv`
- `outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv`
- `outputs/backtest/goal10b3_group_imbalance_diagnostics.csv`
- `outputs/backtest/goal10b3_recommendation_group_metrics.csv`

## Outputs

- `outputs/diagnostics/goal_risk_tiering01_risk_tiered_diagnostics.csv`
- `outputs/diagnostics/goal_risk_tiering01_distribution_summary.csv`
- `outputs/backtest/goal_risk_tiering01_risk_tier_forward_return_metrics.csv`
- `outputs/audits/goal_risk_tiering01_risk_tiering_report.md`
- `outputs/audits/goal_risk_tiering01_risk_tiering_manifest.json`
- `outputs/audits/goal_risk_tiering01_risk_tiering_audit.md`
- `configs/risk/goal_risk_tiering01_contract.yaml`

## Score Construction

The numeric risk score is deterministic and governance-first. It uses DC03 risk severity, source quality warnings, trading status, ST status, missing OHLCV/amount/turnover checks, liquidity proxies, crosscheck/provider concentration warnings, current 1d move magnitude, trailing 5d/20d return magnitude from prior/current panel closes, and a trailing volatility proxy from prior/current `pct_chg` values.

The score does not use `forward_return_*`, `benchmark_excess_return_*`, or `label_ready_*` fields. Those fields are used only in the post-hoc forward-return metric output.

## Result

- Risk-tiered rows: `6000`
- Bucket distribution: `{'LOW_RISK_REVIEW_ONLY': 2891, 'MEDIUM_RISK_REVIEW_ONLY': 2821, 'HIGH_RISK_REVIEW_ONLY': 278, 'INSUFFICIENT_EVIDENCE_REVIEW_ONLY': 10}`
- Dominant bucket share: `0.4818333333`
- Minimum bucket size warning: `true`
- Collapse detected: `false`
- Signal classification: `risk_tiering_signal_weak_or_unreliable`
- Recommended next goal: `adjust_deterministic_governance_risk_rules_before_goal_rec_tiering01`

## Locked Boundary

GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, signal backtest promotion, portfolio backtest, paper trading, live trading, broker integration, production writes, factor-mining, local-lake writes, and DQN/RL remain locked or deleted from active mainline.

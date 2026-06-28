# GOAL-RISK-TIERING-01.1 Downside Risk Repair Gate

Status: `PASS_WITH_WARNINGS`

GOAL-RISK-TIERING-01.1 is a review-only directionality repair gate for the prior numeric risk score. It creates a separate downside-focused diagnostic artifact and does not overwrite GOAL-RISK-TIERING-01, DC03, GOAL-07B, recommendation, or position outputs.

## Inputs

- `outputs/diagnostics/goal_risk_tiering01_risk_tiered_diagnostics.csv`
- `outputs/diagnostics/goal_risk_tiering01_distribution_summary.csv`
- `outputs/backtest/goal_risk_tiering01_risk_tier_forward_return_metrics.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage03_risk_diagnostics.csv`
- `outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv`

## Outputs

- `outputs/diagnostics/goal_risk_tiering011_downside_risk_diagnostics.csv`
- `outputs/diagnostics/goal_risk_tiering011_component_contribution_summary.csv`
- `outputs/diagnostics/goal_risk_tiering011_distribution_summary.csv`
- `outputs/backtest/goal_risk_tiering011_downside_risk_forward_return_metrics.csv`
- `outputs/audits/goal_risk_tiering011_downside_risk_repair_report.md`
- `outputs/audits/goal_risk_tiering011_downside_risk_repair_manifest.json`
- `outputs/audits/goal_risk_tiering011_downside_risk_repair_audit.md`
- `configs/risk/goal_risk_tiering011_contract.yaml`

## Repair Logic

The repair reconstructs deterministic component contributions from the source-backed panel: data quality, liquidity, trading status, ST status, downside price action from current/trailing information available at `trade_date`, volatility, momentum, provider/crosscheck, and universe governance.

Momentum and abnormal positive movement are tracked separately and do not add to the downside score. Volatility contributes only a small bounded amount so the repaired score is not merely a volatility/momentum score. Future-return and benchmark-excess fields are excluded from construction and used only for post-hoc evaluation.

## Result

- Downside-risk rows: `6000`
- Bucket distribution: `{'LOW_DOWNSIDE_RISK_REVIEW_ONLY': 3864, 'MEDIUM_DOWNSIDE_RISK_REVIEW_ONLY': 1887, 'HIGH_DOWNSIDE_RISK_REVIEW_ONLY': 239, 'INSUFFICIENT_DOWNSIDE_EVIDENCE_REVIEW_ONLY': 10}`
- Dominant bucket share: `0.6440000000`
- Minimum bucket size warning: `true`
- Collapse detected: `false`
- Original HIGH volatility/momentum dominated: `true`
- Signal classification: `downside_risk_tiering_signal_weak_or_unreliable`
- Recommended next goal: `another_deterministic_governance_risk_rule_review_before_goal_rec_tiering01`

## Locked Boundary

GOAL-REC-TIERING-01, GOAL-10B.4, position-band validation, GOAL-10D, Dashboard / Daily Report UI, signal backtest promotion, portfolio backtest, paper trading, live trading, broker integration, production writes, factor-mining, local-lake writes, and DQN/RL remain locked or deleted from active mainline.

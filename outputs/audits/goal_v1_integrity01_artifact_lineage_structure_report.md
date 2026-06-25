# GOAL-V1-INTEGRITY-01 Artifact Lineage and Structure Gate

GOAL-V1-INTEGRITY-01 Artifact Lineage and Structure Gate: PASS_WITH_WARNINGS
Mode: `infrastructure_integrity_only`

## Artifact Lineage
- GOAL-07B risk overlay diagnostics rows: `100`
- GOAL-08B recommendation diagnostics rows: `100`
- GOAL-09 position-band diagnostics rows: `100`
- Trade-date plus symbol keys match across canonical diagnostic outputs: `true`
- GOAL-09.1 dashboard-readiness warning policy and audit evidence are present.

## Source Of Truth
- `workflow_status.csv`, README, PROJECT_STATE, ROADMAP, CODEX, AGENTS, and architecture docs are checked for current-state consistency.
- Dashboard / Daily Report UI remains `locked_future`.
- GOAL-DASHBOARD-00 may still be explicitly requested next only as a future design/contract gate.

## Safety
- Future dashboard inputs are limited to canonical review-only diagnostics and audit metadata.
- No dashboard output, HTML, Streamlit, frontend code, visual report, new risk row, new recommendation row, new position row, schema change, position sizing, portfolio weight, target weight, order quantity, buy/sell/hold action, target price, trading, production, backtest, factor-mining, broker, local-lake, or DQN/RL output was created.

## Failures

## Warnings
- calibration_not_reliable_for_thresholding
- feature_sign_instability_bounded
- provider_source_concentration_disclosed
- selected_score_variant_weak_rank_signal
- single_provider_mode_akshare_direct
- target_horizon_calibration_warning
- weak_target_horizon_rank_signal

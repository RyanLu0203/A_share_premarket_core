# Project State

Last updated: 2026-06-21

## Current Stage

Status: `PASS_WITH_WARNINGS` pending final remote HEAD verification.

This repository is the clean active workflow source of truth for the A-share
pre-market alpha diagnosis and risk-aware position-building decision support
system through GOAL-06B.

Chinese identity: A 股盘前 Alpha 诊断 + 风险约束建仓决策支持系统。

## Repository Roles

- Target repository: `RyanLu0203/A_share_premarket_core`
- Source repository: `RyanLu0203/A_share_market_analysis_and_prediction`
- Source role: historical legacy/evidence reference only
- Migration type: selective clean bootstrap, not mirror migration

## Active Boundary

Implemented and protected:

- project operating system
- universe and symbol governance
- trading calendar
- source health and context contracts
- PIT signal store
- label builder and benchmark contract
- feature-label merge
- leakage audit
- Stage 6A repair panel
- GOAL-06A baseline scoring skeleton
- GOAL-06B review-only supervised baseline training gate
- verification, validation, regression, safety, adapter, and diagnostics gates

## Universe

Approved:

- `002475.SZ`
- `600036.SH`

Blocked/pending:

- `000625.SZ`
- `000858.SZ`
- `601138.SH`
- `601208.SH`

Blocked symbols must never reach active connector or generated workflow outputs.

## Lock Status

Still locked:

- GOAL-06C implementation
- GOAL-06D
- GOAL-07A / GOAL-07B
- recommendation or position-band output
- risk overlay calculation
- dashboard
- paper trading
- broker/live trading
- production DB writes
- production model promotion
- DQN/RL

GOAL-06C may begin only as a future review-only expanded validation task if
`outputs/audits/goal06b_clean_repo_bootstrap_readiness_report.md` explicitly
unlocks it.

## Current Evidence Chain

The protected regenerated outputs live under:

- `outputs/audits/`
- `outputs/features/`
- `outputs/labels/`
- `outputs/datasets/`
- `outputs/stage6a/`
- `outputs/stage6b/`
- `outputs/models/goal06b/`
- `outputs/diagnostics/`

Key GitHub locations after push:

- `https://github.com/RyanLu0203/A_share_premarket_core/blob/main/outputs/audits/goal06b_clean_repo_bootstrap_readiness_report.md`
- `https://github.com/RyanLu0203/A_share_premarket_core/blob/main/outputs/audits/classified_capability_catalog_through_goal06b.csv`
- `https://github.com/RyanLu0203/A_share_premarket_core/blob/main/outputs/diagnostics/workflow_diagnostic_summary.md`

## Known Warnings

- Source evidence reported CNINFO coverage for `600036.SH`, but not
  `002475.SZ`.
- Source evidence reported no usable Tencent rows under bounded variants.
- The historical GOAL-05/GOAL-06 docs named in the migration objective were not
  present at expected source paths during inspection; this is documented as
  `CLASS_D_UNCLEAR_KEEP_DOCUMENTED`.

These warnings do not affect Class A active workflow reproducibility through
GOAL-06B and do not unlock downstream modules.

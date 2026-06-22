# Project State

Last updated: 2026-06-22

## Current Stage

Status: `PASS_WITH_WARNINGS` for GOAL-06C expanded validation and ranking
baseline gate. Warnings are limited to small clean-bootstrap review fixture
size; leakage and downstream boundary audits pass. GOAL-06C.5 is implemented as
a review-only engineering data foundation gate. GOAL-06C.6 is implemented as a
source-backed AKShare/provider ingestion gate with network disabled by default.
The panel remains below `engineering_pilot` unless the source-backed bundle
audit explicitly proves 50 symbols, 120 trading dates, and 6000 usable rows;
GOAL-06D remains blocked until then.

This repository is the clean active workflow source of truth for the A-share
pre-market alpha diagnosis and risk-aware position-building decision support
system through GOAL-06B, with GOAL-06C implemented as a review-only validation
extension.

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
- GOAL-06C review-only expanded validation and ranking baseline gate
- GOAL-06C.5 storage, data bundle, source coverage, and engineering panel gate
- GOAL-06C.6 provider failure classification, AKShare optional ingestion, and
  source-backed engineering pilot bundle gate
- verification, validation, regression, safety, adapter, and diagnostics gates
- canonical workflow status governance and workflow status audit

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

Implemented review-only:

- GOAL-06C expanded validation and ranking baseline
- GOAL-06C.5 engineering data coverage, storage, and panel expansion gate
- GOAL-06C.6 source-backed engineering pilot bundle ingestion gate

Future review-only:

- GOAL-06D model comparison and calibration, blocked until GOAL-06C.6 reaches a
  source-backed `engineering_pilot` panel

Still locked:

- GOAL-07A / GOAL-07B
- recommendation or position-band output
- risk overlay calculation
- dashboard
- paper trading
- broker/live trading
- production DB writes
- production model promotion
- DQN/RL

GOAL-06D may begin only as a future review-only model comparison/calibration
task if GOAL-06C.6 readiness explicitly allows it after source-backed
`engineering_pilot` coverage. The current readiness report keeps GOAL-06D
blocked unless that threshold is met.

## Current Evidence Chain

The protected regenerated outputs live under:

- `outputs/audits/`
- `outputs/features/`
- `outputs/labels/`
- `outputs/datasets/`
- `outputs/stage6a/`
- `outputs/stage6b/`
- `outputs/stage6c/`
- `outputs/models/goal06b/`
- `outputs/diagnostics/`

Key GitHub locations after push:

- `https://github.com/RyanLu0203/A_share_premarket_core/blob/main/outputs/audits/goal06b_clean_repo_bootstrap_readiness_report.md`
- `https://github.com/RyanLu0203/A_share_premarket_core/blob/main/outputs/audits/classified_capability_catalog_through_goal06b.csv`
- `https://github.com/RyanLu0203/A_share_premarket_core/blob/main/outputs/diagnostics/workflow_diagnostic_summary.md`

## Runtime Artifact Policy

Committed audit summaries are stable and deterministic. Volatile command timing
is written to local-only ignored files under `outputs/local/runtime/`, so normal
validation runs do not dirty tracked reports only because `runtime_seconds`
changed.

## Python Support

Python `>=3.9` is supported for the clean GOAL-06B workflow. The fresh-clone
audit verified the workflow under Python `3.9.21`.

## Workflow Status Governance

Canonical status contract:

- `configs/project/workflow_status.csv`

Future goals must update that file, README diagrams, architecture diagrams, and
`PROJECT_STATE.md` before any workflow block can move from dotted/future to
implemented. GOAL-06C, GOAL-06C.5, and GOAL-06C.6 are now
`implemented_review_only`; GOAL-06D remains future review-only and blocked until
source-backed `engineering_pilot`.

## Known Warnings

- Source evidence reported CNINFO coverage for `600036.SH`, but not
  `002475.SZ`.
- Source evidence reported no usable Tencent rows under bounded variants.
- The historical GOAL-05/GOAL-06 docs named in the migration objective were not
  present at expected source paths during inspection; this is documented as
  `CLASS_D_UNCLEAR_KEEP_DOCUMENTED`.
- GOAL-06C uses the small clean-bootstrap review fixture: 8 rows, 4 trading
  dates, and 2 approved symbols.
- GOAL-06C.5 proves that the current panel is still `contract_demo`; expansion
  requires at least 50 approved symbols, 120 trading dates, and 6000 rows.
- GOAL-06C.6 provider ingestion is network-disabled by default. If AKShare or
  provider access fails, the failure is classified and GOAL-06D stays blocked.
- Cloakbrowser, stealth browser automation, captcha solving, and proxy rotation
  are not used.

These warnings do not affect Class A active workflow reproducibility through
GOAL-06C review-only validation and do not unlock downstream modules.

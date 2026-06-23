# Project State

Last updated: 2026-06-23

## Current Stage

Status: `PASS` for GOAL-06C.7 provider-ladder engineering data base expansion.
The latest explicit network-enabled run reached `engineering_pilot`: 50
approved symbols, 120 validation trading dates, and 6000 usable Stage 6C rows.
GOAL-06C expanded validation remains review-only; leakage and downstream
boundary audits pass. GOAL-06C.5 is implemented as a review-only engineering
data foundation gate. GOAL-06C.6 is implemented as a source-backed
AKShare/provider ingestion gate with network disabled by default. GOAL-06C.6A
is implemented as a scoped finance-only network isolation and provider failure
taxonomy gate.
GOAL-06C.7 is implemented as a review-only provider-ladder engineering data
base expansion gate. Its provider ladder is `akshare_direct`,
`browser_assisted_optional`, `local_import`, and
`future_vendor_data_placeholder`. The browser-assisted provider is disabled by
default, requires both `ASHARE_ENABLE_BROWSER_ASSISTED_PROVIDER=1` and
`--enable-browser-assisted`, dynamically imports the runtime only after opt-in,
and counts only schema-valid finance rows. Domain access alone is classified
separately and does not count as ingestion success.
The panel remains below `engineering_pilot` unless the source-backed bundle
audit explicitly proves 50 symbols, 120 trading dates, and 6000 usable rows.
The current GOAL-06C.7 readiness report proves that threshold. GOAL-06D may
therefore proceed only as future review-only model comparison/calibration work;
GOAL-07A and everything downstream remain locked.

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
- GOAL-06C.6A finance-only network isolation evidence, provider failure event
  log, failure summary, and owner/action taxonomy reports
- GOAL-06C.6A explicit CloakBrowser reference probe evidence for tagging which
  current provider-access failures are solved, partially solved, or not solved
  by that reference path
- GOAL-06C.7 provider ladder with optional browser-assisted finance ingestion,
  local import fallback, source-backed local bundle evidence, browser provider
  audit, and workflow cleanliness audit
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
- GOAL-06C.6A scoped finance network isolation and provider failure taxonomy
  gate (`PASS_WITH_WARNINGS` while AKShare remains externally blocked)
- GOAL-06C.7 provider ladder engineering data base expansion gate
  (`PASS`; current provider-ladder bundle reached `engineering_pilot`)

Future review-only:

- GOAL-06D model comparison and calibration. GOAL-06C.7 now satisfies the
  `engineering_pilot` entry condition, so GOAL-06D may proceed only as
  review-only future work.

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
task. After GOAL-06C.7, the authoritative readiness check is
`outputs/audits/goal06c7_readiness_report.md`; the current report is `PASS` and
allows only GOAL-06D review-only work. It does not unlock risk, recommendation,
dashboard, paper/live trading, production, or DQN/RL.

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
- `https://github.com/RyanLu0203/A_share_premarket_core/blob/main/outputs/audits/provider_failure_events.csv`
- `https://github.com/RyanLu0203/A_share_premarket_core/blob/main/outputs/audits/provider_failure_summary.md`

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
implemented. GOAL-06C, GOAL-06C.5, GOAL-06C.6, GOAL-06C.6A, and GOAL-06C.7 are now
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
- GOAL-06C.6A proves finance-only scoped proxy-env cleanup and parent
  environment restoration. The current AKShare failure is a specific external
  network/proxy failure, not a project parser/schema failure and not a generic
  `NETWORK_ERROR`.
- The default GOAL-06C.6/GOAL-06C.6A provider ingestion gate uses direct
  AKShare/local-import paths. The explicit CloakBrowser reference probe is
  separate, opt-in, tag-only, sanitized, and does not unlock GOAL-06D or any
  downstream module by itself.
- GOAL-06C.7 upgraded the reference idea into a controlled provider ladder and
  reached `engineering_pilot` in the latest explicit network-enabled run.
  Browser-assisted ingestion remains opt-in, finance-domain-only, sanitized,
  and non-default; `BROWSER_ASSISTED_DOMAIN_ACCESS_ONLY`,
  `BROWSER_NET_EMPTY_RESPONSE`, and
  `BROWSER_ASSISTED_STRUCTURED_INGESTION_SOLVED` are distinct labels. In the
  latest GOAL-06C.7 run the engineering panel was solved by `akshare_direct`;
  the temporary CloakBrowser runtime probe was interrupted at binary download,
  so it is not counted as source-backed ingestion for this panel. Existing
  `cloakbrowser_reference_*` solved-problem tags remain preserved as reference
  evidence only.

These warnings do not affect Class A active workflow reproducibility through
GOAL-06C.7 review-only validation and do not unlock downstream modules beyond
GOAL-06D review-only entry.

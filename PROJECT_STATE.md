# Project State

Last updated: 2026-06-24

## Current Stage

Status: `PASS_WITH_WARNINGS` for GOAL-07A design-only risk overlay governance.
Status: `PASS_WITH_WARNINGS` for GOAL-07A.1 risk overlay design review and GOAL-07B explicit unlock readiness.
Status: `PASS_WITH_WARNINGS` for GOAL-07B.0 review-only unlock gate. GOAL-07B
is now implemented as a deterministic `implemented_review_only` risk overlay
calculation prototype that writes non-actionable symbol-date diagnostics only.
GOAL-06C.7 provider-ladder engineering data base expansion remains `PASS`; the
latest explicit network-enabled run reached `engineering_pilot`: 50 approved
symbols, 120 validation trading dates, and 6000 usable Stage 6C rows.
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
The current GOAL-06C.7 readiness report proves the `engineering_pilot`
threshold. GOAL-06D and GOAL-06D.1 have run only as review-only model
comparison/calibration/stability/warning-repair governance. GOAL-06D.1 selected
`raw_score_based_alpha_ranking` as a weak but bounded review-only baseline and
allowed GOAL-07A only as design-only preparation with warnings. GOAL-07A is now
`implemented_design_only`; it defines contracts, schemas, rule catalog, state
machine, upstream-warning mapping, and governance audits only. GOAL-07B.0
unlocks eligibility only; GOAL-07B now consumes that design evidence as a
review-only diagnostic prototype. GOAL-08A/GOAL-08B and all recommendation,
position, dashboard, trading, production, backtest, factor-mining, and DQN/RL
paths remain locked.

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
- GOAL-06D review-only model comparison, calibration, stability diagnostics,
  governance audit, and downstream boundary lock audit (`PASS_WITH_WARNINGS`)
- GOAL-06D.1 review-only calibration/stability warning repair and V2 factor
  placeholder lock (`PASS_WITH_WARNINGS`)
- GOAL-07A risk overlay design-only contracts, rule catalog, state machine,
  upstream warning mapping, governance boundary, and V2 lock audit
- GOAL-07A.1 risk overlay design review, warning classification, forbidden
  schema overlap audit, and GOAL-07B explicit unlock readiness manifest
- GOAL-07B.0 review-only unlock gate, based only on prior
  PASS/PASS_WITH_WARNINGS design-review evidence
- GOAL-07B review-only risk overlay calculation prototype with deterministic
  non-actionable `trade_date + symbol` diagnostics
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
- GOAL-06D model comparison/calibration/stability/governance gate
  (`PASS_WITH_WARNINGS`; selected weak review-only baseline:
  `score_based_alpha_ranking`)
- GOAL-06D.1 calibration/stability warning repair gate (`PASS_WITH_WARNINGS`;
  selected weak but bounded repaired baseline:
  `raw_score_based_alpha_ranking`)
- GOAL-07A.1 risk overlay design review gate (`PASS_WITH_WARNINGS`; GOAL-07B
  was ready for an explicit review-only unlock)
- GOAL-07B.0 risk overlay review-only unlock gate (`PASS_WITH_WARNINGS`;
  preserves GOAL-07B eligibility and remains an unlock-only gate)
- GOAL-07B risk overlay calculation prototype (`PASS_WITH_WARNINGS`;
  `implemented_review_only`; 100 review-only diagnostic rows at
  `trade_date + symbol` grain)

Implemented design-only:

- GOAL-07A risk overlay design gate (`PASS_WITH_WARNINGS`; contracts, schemas,
  rule catalog, state machine, upstream-warning mapping, and audits only)

Still locked:

- GOAL-08A recommendation contract design gate
- GOAL-08B recommendation review-only prototype
- recommendation or position-band output
- dashboard
- paper trading
- broker/live trading
- production DB writes
- production model promotion
- DQN/RL

GOAL-07A has run only as design-only risk overlay governance. GOAL-07A.1 has
run only as review-only design review governance. GOAL-07B.0 remains an
unlock-only review gate. GOAL-07B writes:

- `outputs/risk_overlay/goal07b_review_only_risk_overlay.csv`
- `outputs/diagnostics/goal07b_risk_overlay_diagnostics.csv`
- `outputs/audits/goal07b_risk_overlay_calculation_report.md`
- `outputs/audits/goal07b_risk_overlay_calculation_manifest.json`
- `outputs/audits/goal07b_risk_overlay_calculation_audit.md`

The GOAL-07B prototype propagates existing weak-baseline, calibration, feature
stability, target-horizon, and provider-concentration warnings into review-only
risk diagnostics. It does not generate recommendations, positions,
dashboards, paper/live trading, production writes, backtests, factor-mining
outputs, broker outputs, or DQN/RL outputs.

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
- `outputs/models/goal06d/`
- `outputs/models/goal06d1/`
- `configs/risk/`
- `docs/risk/`
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
`PROJECT_STATE.md` before any workflow block can move status. GOAL-06C,
GOAL-06C.5, GOAL-06C.6, GOAL-06C.6A, GOAL-06C.7, GOAL-06D, GOAL-06D.1,
GOAL-07A.1, GOAL-07B.0, and GOAL-07B are `implemented_review_only`; GOAL-07A is
`implemented_design_only`. GOAL-07B is diagnostic-only and non-actionable.
GOAL-08A, GOAL-08B, recommendation, position, dashboard, trading, production,
V2 factor-mining, and DQN/RL paths remain locked or deleted from active
mainline.

## Known Warnings

- Source evidence reported CNINFO coverage for `600036.SH`, but not
  `002475.SZ`.
- Source evidence reported no usable Tencent rows under bounded variants.
- The historical GOAL-05/GOAL-06 docs named in the migration objective were not
  present at expected source paths during inspection; this is documented as
  `CLASS_D_UNCLEAR_KEEP_DOCUMENTED`.
- GOAL-06C uses the small clean-bootstrap review fixture: 8 rows, 4 trading
  dates, and 2 approved symbols.
- GOAL-06C.5 preserves the historical `contract_demo` warning for the earlier
  small engineering-foundation panel; GOAL-06C.7 now separately proves
  source-backed `engineering_pilot`.
- GOAL-06C.6 provider ingestion is network-disabled by default. Provider access
  failures are still classified precisely, but GOAL-06C.7 now supplies the
  engineering_pilot evidence used by GOAL-06D.
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
- GOAL-06D selected `score_based_alpha_ranking` only as a weak review-only
  baseline. Calibration is weak/non-monotonic for compared baselines and
  provider/source concentration remains single-mode `akshare_direct`.

GOAL-06D.1 repairs these warnings as a review-only diagnostic layer. It compares
target horizons, bounded score variants, calibration reliability, feature sign
stability, and provider/source concentration. GOAL-07A carries these warnings
into design-only risk governance as `PASS_WITH_WARNINGS`; it does not calculate
risk, assign risk tags to real symbols, recommend positions, produce trading
signals, activate dashboards, promote models, or unlock production.

V2 factor research is documented only as `planned_locked`. No V2 factor mining,
IC/RankIC mining, factor library generation, factor outputs, or factor-to-model
integration is active in V1.

These warnings do not affect Class A active workflow reproducibility through
GOAL-06D.1 review-only validation and do not unlock any downstream
recommendation, position, dashboard, trading, production, V2 factor-mining, or
DQN/RL module.

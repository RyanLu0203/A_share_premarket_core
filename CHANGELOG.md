# Changelog

## 2026-06-22 - GOAL-06C.6A

- Added scoped finance-only network isolation evidence with temporary provider
  proxy-env cleanup and parent environment restoration checks.
- Expanded provider failure taxonomy across policy, dependency, transport,
  HTTP access, anti-bot, schema, parser, data quality, PIT/label, storage, and
  workflow governance layers.
- Added machine-readable provider failure events, summary JSON/Markdown,
  network isolation reports, and failure taxonomy reports.
- Classified the current explicit AKShare failure as
  `FINANCE_DIRECT_CHILD_ENV_CLEANED_BUT_PROVIDER_STILL_PROXY_FAILED`, not a
  generic network error; GOAL-06D remains blocked.
- Added mock-only tests for ProxyError, timeout, DNS, TLS, HTTP 403/429/5xx,
  captcha/challenge, schema/parser, data quality, PIT/label, storage, and
  workflow-governance failures.

## 2026-06-22 - GOAL-06C.6

- Added provider failure classification, AKShare optional provider wrappers,
  source-backed bundle orchestration, and public GOAL-06C.6 wrappers.
- Added source-backed universe, bundle, PIT panel, label panel, Stage 6C panel,
  and readiness audit outputs with small GitHub samples only.
- Added no-network-safe tests for provider classification, network opt-in,
  optional AKShare import behavior, bundle artifact hygiene, PIT/label leakage,
  and downstream locks.
- Kept network ingestion disabled by default and kept GOAL-06D blocked unless a
  source-backed panel reaches `engineering_pilot`.
- Did not add cloakbrowser, stealth browser automation, captcha solving, proxy
  rotation, recommendation, risk, dashboard, paper/live trading, production, or
  DQN/RL capability.

## 2026-06-21 - GOAL-06C.5

- Added local research storage policy, data bundle manifest contracts, provider
  ingestion contracts, and heavy-artifact hygiene coverage.
- Added source, universe, trading calendar, and provider coverage audits.
- Added engineering PIT signal, label, and Stage 6C panel samples with readiness
  reports and replacement-path audit.
- Classified the current panel as `contract_demo`, not `engineering_pilot`, and
  kept GOAL-06D blocked.
- Added GOAL-06C.5 public wrappers, tests, docs, and workflow status governance.

## 2026-06-21 - GOAL-06C

- Added review-only expanded validation panel, ranking baselines, ranking
  metrics, walk-forward diagnostics, and stability diagnostics.
- Added GOAL-06C public wrappers, configs, audits, readiness report, and tests.
- Promoted `goal06c_expanded_validation_ranking` to
  `implemented_review_only` in `configs/project/workflow_status.csv`.
- Kept GOAL-06D as future review-only and all recommendation, risk, dashboard,
  paper/live trading, production, and DQN/RL boundaries locked.

## 2026-06-21 - GOAL-DOCS-01

- Added canonical workflow status contract at
  `configs/project/workflow_status.csv`.
- Added workflow status audit wrapper and generated governance audit outputs.
- Updated README and architecture diagrams so implemented blocks use solid
  arrows and future/locked/deleted blocks use dotted references.
- Added the Workflow Promotion Rule to README, CODEX, AGENTS, and canonical
  architecture docs.
- Kept GOAL-06C as future review-only and all downstream locked modules locked.

## 2026-06-21 - GOAL-HYGIENE-01

- Split volatile runtime timings out of committed validation reports and into
  ignored local diagnostics under `outputs/local/runtime/`.
- Made stable regression and program validation reports deterministic across
  normal reruns.
- Added runtime artifact policy documentation.
- Clarified Python `>=3.9` support after fresh-clone verification passed under
  Python `3.9.21`.
- Kept the missing historical GOAL-05/GOAL-06 source-doc gap documented as
  `CLASS_D_UNCLEAR_KEEP_DOCUMENTED`.

## 2026-06-21

- Bootstrapped the clean private target repository for active workflow through
  GOAL-06B.
- Added clean package architecture under `src/ashare_premarket/`.
- Added public compatibility wrappers through the GOAL-06B boundary.
- Added classified capability catalog, active trunk module map, and legacy
  exclusion manifest generation.
- Added diagnostics outputs and runbook.
- Added verification, validation, regression, safety, and adapter gates.
- Preserved downstream locks for recommendation, risk, dashboard, paper/live
  trading, production DB writes, production model promotion, and DQN/RL.

## Source Evidence

The historical source repository remains available as
`RyanLu0203/A_share_market_analysis_and_prediction`. It is no longer the active
workflow source of truth after this clean bootstrap is pushed.

# Changelog

## 2026-06-24 - GOAL-STORAGE-01 Local Research Lake Hardening Gate

- Implemented GOAL-STORAGE-01 as an infrastructure-only local research lake
  hardening gate.
- Added the storage governance module, runner, audit wrapper, config contract,
  docs, manifest, workflow-status governance, diagnostics integration, and
  focused tests.
- Defined `ASHARE_PREMARKET_DATA_ROOT` root resolution, documentation-only
  fallback behavior, local `raw/`, `bundles/`, `lake/`, `metadata/`, `exports/`,
  and `audit_samples/` boundaries, placement rules, bundle versioning, manifest
  requirements, SHA-256 checksum rules, schema registry rules, and GitHub
  hygiene rules.
- Kept GOAL-08B and all downstream execution paths locked; generated no local
  lake files, recommendation diagnostics, position diagnostics, dashboards,
  trading, production, backtest, factor-mining, broker, or DQN/RL outputs.

## 2026-06-24 - GOAL-08A Recommendation Contract Design Gate

- Implemented GOAL-08A only as a design-only future recommendation contract
  gate.
- Added the GOAL-08A runner, audit wrapper, design module, configs, docs,
  manifest, workflow-status governance, diagnostics integration, and focused
  tests.
- Defined the GOAL-07B `trade_date + symbol` input contract, required risk and
  warning fields, warning propagation, and HIGH-risk actionability block.
- Wrote names-only future schema evidence with zero rows and no recommendation
  output.
- Kept GOAL-08B, recommendation execution, position, dashboard, paper/live
  trading, production, backtest, factor-mining, broker, and DQN/RL outputs
  locked or absent.

## 2026-06-24 - GOAL-07B Risk Overlay Calculation Prototype

- Implemented GOAL-07B as a deterministic review-only risk overlay diagnostic
  prototype.
- Generated 100 non-actionable diagnostic rows at `trade_date + symbol` grain
  under `outputs/risk_overlay/goal07b_review_only_risk_overlay.csv`.
- Added the GOAL-07B runner, audit wrapper, policy, report, manifest,
  diagnostics output, docs, workflow-status governance, and focused tests.
- Propagated GOAL-06D.1 / GOAL-07A.1 weak-baseline, calibration, feature
  stability, target-horizon, and provider-concentration warnings into bounded
  risk diagnostics.
- Kept GOAL-08A, GOAL-08B, recommendation, position, dashboard, paper/live
  trading, production, backtest, factor-mining, broker, and DQN/RL outputs
  locked or absent.

## 2026-06-24 - GOAL-07B.0 Risk Overlay Review-Only Unlock Gate

- Added a strict GOAL-07B.0 review-only unlock gate based only on prior
  GOAL-07A and GOAL-07A.1 PASS/PASS_WITH_WARNINGS evidence.
- Moved GOAL-07B from `locked_future` to `future_review_only` eligibility while
  keeping `implemented_in_repo=false`.
- Added the GOAL-07B.0 runner, audit wrapper, policy, report, manifest, docs,
  workflow-status governance, diagnostics, and focused tests.
- Created no risk calculation rows, symbol-level risk overlay rows,
  recommendations, positions, dashboards, trading, production, backtest,
  factor-mining, broker, or DQN/RL outputs.

## 2026-06-24 - GOAL-07A.1 Risk Overlay Design Review Unlock Readiness

- Added a review-only GOAL-07A.1 gate that checks GOAL-07A input contracts, future output schema safety, rule convertibility, state machine executability, warning policy, and downstream locks.
- Added GOAL-07B unlock readiness manifest and warning classification table.
- Marked GOAL-07B ready only for a future explicit review-only unlock request while keeping GOAL-07B `locked_future`.
- Kept risk calculation, recommendation, position, dashboard, paper/live trading, production, backtest, factor mining, broker integration, and DQN/RL outputs absent.

## 2026-06-23 - GOAL-07A Risk Overlay Design-Only Gate

- Added GOAL-07A design-only risk governance contracts under `configs/risk/`
  and `docs/risk/`.
- Defined V1 risk domains, allowed future PIT-safe inputs, future output schema,
  rule catalog, state machine, and upstream warning mapping.
- Added GOAL-07A runner, audit wrappers, focused tests, workflow status,
  diagnostics, and readiness report.
- Carried GOAL-06D.1 weak-baseline, calibration, feature-stability,
  target-horizon, and provider-concentration warnings into risk design.
- Kept GOAL-07B, risk calculation, recommendation, position, dashboard,
  paper/live trading, production, V2 factor mining, and DQN/RL locked.

## 2026-06-23 - GOAL-06D.1 Calibration Stability Warning Repair

- Added GOAL-06D.1 review-only warning repair for target horizon selection,
  PIT-safe score variants, calibration reliability, feature sign stability, and
  provider/source concentration disclosure.
- Selected a repaired review-only score baseline as weak but bounded; remaining
  calibration warnings are marked not reliable for thresholding where
  appropriate.
- Added a locked V2 factor research placeholder. V2 factor mining, IC/RankIC
  mining, factor library generation, and factor integration remain inactive in
  V1.
- Kept GOAL-07A limited to future design-only preparation with warnings; no
  recommendation, position, risk overlay, dashboard, trading, production,
  factor-mining, or DQN/RL output was created.

## 2026-06-23 - GOAL-06D Review-Only Model Comparison Gate

- Added GOAL-06D feature/split contracts, review-only model comparison runner,
  calibration/stability/governance audits, public wrappers, and focused tests.
- Used the GOAL-06C.7 `engineering_pilot` source-backed panel from the local
  bundle: 50 approved symbols, 120 validation dates, and 6000 rows.
- Compared `score_based_alpha_ranking`, `ridge_regression`,
  `linear_regression`, and `logistic_direction_classifier` against
  `excess_fwd_3d_return`, with auxiliary target diagnostics for 1d/3d/5d
  excess forward returns.
- Wrote only lightweight review artifacts under `outputs/models/goal06d/` and
  `outputs/audits/goal06d_*`; no row-level recommendation, position, risk,
  dashboard, trading, production DB, production model, model binary, or DQN/RL
  artifact was created.
- GOAL-06D readiness is `PASS_WITH_WARNINGS`: selected
  `score_based_alpha_ranking` as a weak review-only baseline; calibration and
  feature/provider concentration warnings remain. GOAL-07A remains
  future-design-only and locked until warnings are fixed by a later explicit
  goal.

## 2026-06-23 - GOAL-06C.7 Engineering Pilot Reached

- Added configured direct-provider retry and rate limiting to the GOAL-06C.7
  provider ladder so recoverable finance endpoint failures are retried and
  recorded as separate attempt events.
- Expanded the candidate A-share seed universe and reran explicit
  network-enabled provider-ladder ingestion.
- Reached `engineering_pilot` with 50 approved symbols, 120 validation trading
  dates, and 6000 usable Stage 6C engineering rows.
- Preserved the optional browser-assisted path as explicit opt-in only. The
  current GOAL-06C.7 panel was solved by `akshare_direct`; the temporary
  CloakBrowser runtime probe was interrupted during binary download and was not
  counted as ingestion success.
- Updated GOAL-06D governance so only future review-only model
  comparison/calibration may proceed after GOAL-06C.7 PASS. Risk,
  recommendation, dashboard, paper/live trading, production, and DQN/RL remain
  locked.

## 2026-06-22 - GOAL-06C.7 Provider Ladder Engineering Data Base Expansion

- Added a deterministic provider ladder:
  `akshare_direct`, `browser_assisted_optional`, `local_import`, and
  `future_vendor_data_placeholder`.
- Added explicit browser-assisted provider policy, switches, audit events, and
  wrappers. Browser-assisted ingestion is disabled by default, dynamic-import
  only, finance-domain scoped, and requires both env and CLI opt-in.
- Classified browser-assisted outcomes separately, including
  `BROWSER_NET_EMPTY_RESPONSE`, `BROWSER_ASSISTED_DOMAIN_ACCESS_ONLY`, and
  `BROWSER_ASSISTED_STRUCTURED_INGESTION_SOLVED`; domain access alone is not
  ingestion success.
- Added source-backed local bundle outputs under the local data root, bounded
  GitHub samples, GOAL-06C.7 readiness, browser provider audit, and workflow
  cleanliness audit.
- Kept GOAL-06D and all downstream recommendation, risk, dashboard,
  paper/live trading, production, and DQN/RL modules locked unless the
  provider-ladder bundle reaches `engineering_pilot`.

## 2026-06-22 - GOAL-06C.6A CloakBrowser Reference Probe

- Added an explicit, opt-in CloakBrowser reference probe that tags current
  provider access failures as ingestion-solved, domain-access-only, or
  attempted-not-solved with specific remaining failure classes.
- Ran the probe from a temporary venv and external cache; no default dependency,
  raw HTML, screenshots, cookies, payload bodies, or browser cache were added to
  the repository.
- Tagged `index_zh_a_hist` as
  `SOLVED_BY_CLOAKBROWSER_REFERENCE_INGESTION`,
  `stock_info_a_code_name` as
  `SOLVED_BY_CLOAKBROWSER_REFERENCE_DOMAIN_ACCESS_ONLY`, and
  `stock_zh_a_spot_em` as
  `CLOAKBROWSER_REFERENCE_ATTEMPTED_NOT_SOLVED_EMPTY_RESPONSE`.
- Kept the default AKShare provider path unchanged and kept GOAL-06D and all
  downstream modules locked.

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
- Did not add browser automation as a default dependency or provider path, and
  did not add captcha solving, proxy rotation, recommendation, risk, dashboard,
  paper/live trading, production, or DQN/RL capability.

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

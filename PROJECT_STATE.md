# Project State

Last updated: 2026-07-18

## GOAL-12 ALPHA VALIDATION, ROBUSTNESS AND RESEARCH APPROVAL

GOAL-12 implements a deterministic research-only falsification layer over the
merged GOAL-11 foundation. The governed full run covers 34,543 rows, 41
symbols, 823 common-horizon signal dates, exact qfq 1D/5D/20D labels, 51
BH-FDR hypotheses, five purged chronological folds, a 126-date final holdout,
date-level nulls, and 33 robustness slices per eligible factor.

- Final statuses: 17 `research_rejected`, 11
  `research_insufficient_data`, and zero supported/weak/unstable candidates.
- Historical OHLC/volume is unavailable. Four features and all three combined
  candidates are therefore structurally insufficient; no substitute data or
  imputation is fabricated.
- `production_ready=false`, `ready_factor_count=0`, 14 canonical interfaces,
  22 GET routes, zero write routes, and every recommendation/execution lock
  remain unchanged.
- Full generated evidence remains checksummed and ignored under
  `outputs/local/goal12`; the committed conclusion is
  `docs/quant/GOAL12_ALPHA_VALIDATION_FINDINGS.md`.
- GOAL-13 remains blocked. The next responsible research gate is governed
  historical OHLCV/volume and PIT-universe evidence remediation followed by a
  frozen-contract GOAL-12 rerun.

## GOAL-11 QUANT INTELLIGENCE FOUNDATION

GOAL-11 adds a deterministic, research-only quantitative intelligence
foundation over explicitly governed market-data snapshots.

- Feature construction covers price, volatility, technical, volume, and
  market-regime families. Missing OHLCV or index evidence remains unavailable
  with deterministic reason codes; no values are fabricated.
- Every feature row carries symbol, date, feature version, source snapshot ID,
  generation timestamp, code commit, and checksum lineage.
- The interpretable alpha is fixed as momentum plus trend plus volume strength
  minus risk penalty. A fixed-ridge linear ranker provides one deterministic
  baseline without tuning on the final holdout.
- Evaluation is chronological and walk-forward only, with Rank IC, IC
  stability, precision/recall at K, time/feature stability, and turnover.
- Outputs are local research evidence under ignored `outputs/local`; no
  datasets, snapshots, model binaries, logs, notebooks, or runtime artifacts
  are committed.
- The existing 14 canonical interfaces, 22 GET-only API routes, 23 workspace
  pages, production locks, and `ready_factor_count = 0` remain unchanged. The
  optional research dashboard is deferred to preserve those exact contracts.

## FINAL-MACOS-DEPLOYMENT-API-UI-REPAIR

The final macOS deployment review found three bounded integration defects in
the merged Issue #36 state. Repair work is isolated on
`codex/final-macos-deployment-api-ui-repair`; it is not yet a deployment claim.

- Live read-only API and frontend views now identify Tencent /
  `stock_zh_a_hist_tx` / qfq, the amount-null contract, accepted and rejected
  counts, East Money canonical request count, batch/canonical/snapshot/refresh
  checksums, snapshot ID, and the runtime deployment commit. Historical replay
  responses preserve their prior architecture baseline and separately label
  the older research provider/chart lineage.
- The launchd workspace runner uses the validated Next.js standalone
  production server by default, with copied static/public build assets and no
  `next start` compatibility warning. Development mode remains explicit
  opt-in, and startup exports the authoritative repository root and
  40-character Git commit to the read-only backend provenance surface.
- The macOS daily wrapper preserves committed mutable research baselines while
  retaining ignored dated immutable live evidence and local observability. An
  explicit `--force-network-reacquisition` option supports a second complete
  bounded network run and never treats `already_refreshed` as idempotency proof.
- OpenAPI remains 22 GET routes with zero writes; historical API architecture
  hashes remain unchanged. Recommendation, trading, broker, production-model,
  factor-mining, and DQN/RL capabilities remain locked.
- Python 3.12 compileall passes, the warning-free full suite is `463 passed`,
  the canonical profile is `117/117 PASS`, the workspace audit is `PASS`, and
  frontend lint, typecheck, `35/35` tests, and production build pass.

## GOAL-TENCENT-PRIMARY-OPERATIONAL-HARDENING-01

Issue #36 is implemented on
`codex/tencent-primary-operational-hardening` from authoritative
`project-current` commit `040048b557f62837fce72ecde2cccba4615d42d7`.

- AKShare `stock_zh_a_hist_tx` / Tencent is the explicit operational primary
  and is called directly for every canonical refresh. East Money is blocked
  from canonical refresh: its canonical request count is exactly zero, it has
  no automatic failback path, and its separately invoked health probe is
  disabled by default and cannot influence canonical rows, checksums,
  selection, freshness, coverage, snapshots, or status.
- Complete-run source integrity is mandatory. A partial Tencent batch, mixed
  source, schema/order drift, malformed or empty response, stale/future or
  duplicate row, invalid OHLC/finite/volume evidence, interruption, timeout,
  DNS/TLS failure, or final-symbol failure blocks the run and preserves the
  last valid immutable snapshot.
- Tencent's sixth AKShare export is volume in `手`. Canonical monetary `amount`
  is explicitly null/unavailable, never copied from volume, and never
  zero-filled. The versioned consumer inventory proves enabled downstream
  consumers either preserve null or fail closed when amount is required.
- Production adjustment is qfq only. Corporate-action verification remains
  independently bounded and never contributes rows to the Tencent canonical
  batch. hfq is `UNSUPPORTED_DISABLED`.
- SH, SZ/ChiNext, and governed BJ symbol mapping is explicit. The current
  governed 41-symbol universe contains no BJ symbol; the installed AKShare
  Tencent function does not yield its expected schema for BJ, so any future BJ
  admission fails closed as `TENCENT_BJ_UPSTREAM_UNSUPPORTED` until separately
  governed evidence exists.
- Two genuine complete network runs resolved target `2026-07-16` and T-1
  `2026-07-15`, selected Tencent immediately, accepted 41/41 rows from exactly
  one canonical source, made zero East Money canonical requests, and produced
  identical normalized batch checksum
  `596b0861a3abff07a4fc0e7342bfc17934a7586328d259b810a718a105384f96`.
  Snapshot ID is `opm:2026-07-16:fa3ea3c250c3c317`; snapshot checksum is
  `fa3ea3c250c3c317d86906383f724079c1d338f89aa9a5df0adb8dbc0122fb25`;
  idempotency is
  `PASS_IDENTICAL_NORMALIZED_BATCH_AND_IMMUTABLE_SNAPSHOT` without an
  `already_refreshed` shortcut.
- Deployment, launchd installation, and service startup are outside this
  issue. Recommendation, trading, broker, production-model, factor-mining,
  and DQN/RL capabilities remain locked.

## GOAL-GOVERNED-AKSHARE-TENCENT-SECONDARY-UPSTREAM-01

Issue #34 is `IMPLEMENTED_RESEARCH_ONLY_PASS` on
`codex/governed-akshare-tencent-secondary-upstream`, based exactly on the
authoritative PR #33 merge `c7a271fefe12936266de73fedfad233869e4d79e`.

- AKShare remains the application provider. East Money
  `stock_zh_a_hist` remains primary and Tencent `stock_zh_a_hist_tx` is the
  only governed secondary candidate.
- Source selection is once per complete run. The bounded East Money batch must
  terminate before evaluation; an approved endpoint failure may launch one
  complete Tencent reacquisition, and every partial primary row is discarded.
  Per-symbol mixing and silent fallback are prohibited.
- Approved activation classes are `BROWSER_NET_EMPTY_RESPONSE`,
  `CONNECTION_RESET`, `HTTP_429_RATE_LIMITED`, and
  `HTTP_5XX_PROVIDER_ERROR`. TLS, proxy, symbol, schema, stale-date, PIT,
  checksum, calendar, and other local/integrity failures never activate the
  secondary.
- Tencent mapping is explicit for SH, SZ/ChiNext, and BJ symbols. AKShare
  1.18.64 labels Tencent's sixth exported field `amount`, but bounded overlap
  evidence proves it is volume in `手` at scale 1 to East Money `成交量`.
  The official function discards Tencent's monetary-amount field;
  canonical monetary amount is therefore explicitly unavailable and is never
  zero-filled or inferred.
- Versioned tolerances are OHLC absolute `0.01 CNY` or relative `0.0005`,
  exact volume equality in provider units, and a diagnostic-only raw Tencent
  monetary-amount comparison of `100 CNY` absolute or `1e-6` relative. This
  diagnostic amount is not exposed as canonical provider output.
- Production adjustment is qfq only. Ordinary SSE/SZSE/ChiNext overlap and
  authoritative-terms corporate-action triangulation for SSE `603836.SH` and
  required-universe SZSE `000333.SZ` pass formula, continuity, calendar, and
  tolerance gates. Missing primary corporate rows are classified
  `PRIMARY_CORPORATE_ACTION_EVIDENCE_UNAVAILABLE`. hfq remains disabled and its
  600036.SH discrepancy is non-blocking research evidence only.
- Request evidence records global and batch sequence, function, upstream,
  endpoint family, parameters, timing, HTTP evidence when exposed, rows,
  latest date, exception, acceptance, rejection, retry count, AKShare version,
  network scope, and batch checksum. Snapshot and refresh writes use atomic
  replace with immutable conflict guards.
- Two complete live runs selected Tencent for all 41 current T-1 rows with no
  mixing. Batch checksum is `a95459ff4be28e5acf48c7fb056490f470034d6949599119da8fa8277b95f5b5`;
  snapshot checksum is `8bb115499856585595e1f6e625bbea3e8d6de7c89a067992c2af9fe62685e3d2`;
  idempotency is `PASS_IDENTICAL_NORMALIZED_BATCH_AND_IMMUTABLE_SNAPSHOT`.
- The duplicate 12.4 MB full canonical materialization remains local and
  ignored. A committed 41-row T-1 delta plus a versioned base+delta commitment
  reconstructs its checksum exactly for fresh-clone snapshot verification.
- Python 3.12 compileall passes, full Python is `448 passed`, and the canonical
  profile is `117/117 PASS`. Architecture, safety, workflow, adapter, PIT,
  leakage, provider-failure, and macOS prerequisite checks pass.
- All recommendation, target-price, order, trading, broker, production-model,
  factor-mining, and DQN/RL capabilities remain locked. No launchd agent or
  frontend/backend service is installed or started by this goal.
- Requirement-by-requirement completion audit:
  `docs/operations/ISSUE34_REQUIREMENT_COMPLETION_AUDIT_2026-07-15.md`.
- The five truthful read-only API projection changes caused by the second
  snapshot are deliberately reconciled; OpenAPI, 22-GET/zero-write topology,
  historical replay, and all downstream locks are unchanged.

## GOAL-MACOS-LIVE-REFRESH-AND-PROVIDER-RECOVERY-01

The authoritative PR #32 merge was verified at
`d3563eab97f4e422d3da9a6e32430510d4043867`, including fix commit
`7f54f24f1e62f3509f4297162e21c2ef27ffb322`. Recovery work is isolated on
`codex/macos-live-refresh-and-provider-recovery`.

- Code repair: the macOS runner now passes `replay_date=None` explicitly, so a
  live run cannot inherit the goal runner's deterministic replay default.
- Network repair: direct provider calls remove upper/lowercase proxy variables,
  disable Requests environment/system proxy rediscovery for the scoped call,
  restore process state, keep TLS verification and a 30-second timeout, and
  preserve proxy use only behind explicit authorization.
- Calendar: approved AKShare/Sina evidence is `VERIFIED`, covers
  `1990-12-19` through `2026-12-31`, contains 8,797 sessions, has checksum
  `db13387fd42cb1ef98bbde07a12d2f8c64c438eeea940926d4ec49b2a5263d14`,
  keeps `2026-06-19` closed, and resolves target `2026-07-15` with T-1
  `2026-07-14`.
- Deployment status: `BLOCKED_PARTIAL_PROVIDER_AVAILABILITY`. After
  Shadowrocket split routing was verified for `push2his.eastmoney.com`, the
  approved calendar sync still passed and resolved target `2026-07-15` with
  T-1 `2026-07-14`. The exact unwrapped AKShare request still attempted
  `127.0.0.1:1082`, while the application child-process provider path did not
  and instead connected directly to synthetic `198.18.0.39:443` over `utun4`.
  The bounded live refresh accepted 7 of 41 required T-1 rows and blocked on
  34 missing/failed provider rows. No snapshot was created and no launch agents
  or services were installed or started.
- Request diagnosis: the canonical successes clustered at positions 27, 30,
  and 32-36, but a controlled matrix made both previously successful and
  failed symbols fail identically in isolated processes, after pauses, with
  existing session behavior, with a reused session, and through the exact
  application provider wrapper in fresh child processes. All 20 requests ended
  before HTTP status as `ConnectionError(RemoteDisconnected)`. Root cause is
  classified `INTERMITTENT_STRUCTURAL_PRIMARY_UPSTREAM_REMOTE_CLOSE`; no
  pacing/retry or symbol-normalization code change is justified.
- Upstream governance: PR #33 recorded an inactive AKShare Tencent proposal.
  Issue #34 subsequently supplied the explicit authority and acceptance
  contract for the separate governed implementation described above.
- Architecture baseline: the two blocked daily-refresh artifact hashes and the
  `/api/experiment` and `/api/provenance` hashes that consume them are
  deliberately reconciled. The other 20 GET response hashes, OpenAPI,
  canonical market data, and immutable snapshot hashes remain unchanged.
  Deterministic replay tests restore all seven mutable operational files.
- Validation: compileall passes, the full Python suite is `412 passed`, and the
  canonical profile is `117/117 PASS`. Architecture parity is exact while the
  current operational refresh remains `BLOCKED` with no snapshot. Safety,
  workflow, adapter, PIT, leakage, destructive-change, and macOS prerequisite
  checks pass.
- Next goal: a specification-only, non-activated run-level East Money-to-
  Tencent complete-batch failover contract is recorded at
  `docs/governance/NEXT_GOAL_GOVERNED_AKSHARE_SECONDARY_UPSTREAM.md`.
- Governance: no replay was represented as live data, no silent fallback was
  used, and recommendation, trading, broker, production, factor-mining, and
  DQN/RL boundaries remain locked.
- Recovery evidence:
  `docs/operations/MACOS_LIVE_REFRESH_PROVIDER_RECOVERY_2026-07-15.md`.

## GOAL-RUNTIME-CALENDAR-SOURCE-AUTHORITY-FIX-01

The macOS live-calendar integration found that the deterministic committed
research fixture marks `2026-06-19` as a trading day, while the approved
AKShare/Sina schedule and official SSE/SZSE Dragon Boat Festival notices mark
that date as closed.

- Status: `PASS` on `codex/runtime-calendar-source-authority-fix`, pending
  human PR review; deployment remains blocked until the fix is merged into
  `project-current`.
- Runtime authority: only the approved provider schedule supplies runtime
  trading sessions. The committed fixture remains unchanged and continues to
  serve deterministic historical research replay only.
- Provenance: committed-fixture disagreements are recorded explicitly in
  ignored runtime metadata and exposed through calendar status; they are not
  silently converted into sessions.
- Integrity: source identity, checksum, coverage, row count, atomic write, PIT
  schedule semantics, and configured-evidence fail-closed validation remain
  required.
- Validation: 406 Python tests, the canonical validation profile, the live
  calendar-only approved-provider integration, and global/workspace/daily
  replay audits pass.
- Governance: `ready_factor_count = 0`; recommendation, action labels,
  trading, broker, paper execution, production, factor mining, and DQN/RL
  remain locked or absent.

## GOAL-RUNTIME-OPERATIONAL-RESTORATION-01

Issue #30 restores the bounded local runtime on top of the PR #29 global
codebase consolidation without reverting or bypassing the refactored
interfaces.

- Status: `PASS` on `codexmax/issue-30`, pending human PR review.
- Calendar: the committed fixture remains unchanged. An ignored runtime
  calendar is synchronized from the approved AKShare/Sina exchange calendar
  only with explicit network authorization. Only source-returned sessions are
  marked as trading days; checksum, provenance, coverage, and PIT metadata are
  verified before use. Missing or invalid configured runtime evidence fails
  closed without falling back silently.
- Snapshot resolution: explicit replay requires a checksum-verified immutable
  snapshot. Live resolution is date-bounded and deterministic, validates the
  latest pointer and every selected snapshot, exposes stale/invalid pointer
  recovery, and marks any older research fallback as system-blocking.
- macOS: user-level launchd support runs the local read-only workspace and a
  weekday 07:45 calendar/evidence refresh. The daily runner performs only the
  approved calendar sync, bounded T-1 evidence refresh, and research-only OPM
  snapshot handoff.
- Dashboard: operational system readiness may be `BLOCKED` while verified
  historical replay remains `AVAILABLE` and research panels remain
  `AVAILABLE_WITH_WARNING`. Quant pages remain governance-locked.
- `ready_factor_count = 0`; RecTiering, Recommendation, BUY/SELL/HOLD,
  trading, broker, paper execution, production, factor mining, and DQN/RL
  remain locked or absent.

Operational documentation:
`docs/operations/MACOS_LAUNCHD_DAILY_REFRESH.md`.

## Codex Operating System Gate

GOAL-CODEX-OPERATING-SYSTEM-01 is implemented as a governance-only Codex Max
onboarding and Git operating-system gate.

- Authoritative remote branch: `project-current`.
- Latest confirmed remote commit:
  `6b9fbab29a2ca49703d46fc8360f8bb9e8917120`.
- Remote checkpoint branch: `checkpoint/arch03-stable-310559`.
- Remote checkpoint tag: `checkpoint-arch03-stable-310559`.
- Stable checkpoint commit: `310559ae18bbf203e795c1d66bc7181a6b11c14a`.
- Local bundle backup is user-private only and is not a Codex Max dependency.
- Current scientific status: review-only/research-only evidence remains
  unchanged; no scientific output or conclusion is changed by this gate.
- Ready factor count: `0`.
- Latest regime status: Regime01 implemented.
- Latest architecture status: Arch03 implemented.
- Provider/source catalog status: AKShare source catalog 70 rows; provider
  registry network disabled by default.
- Current blockers: no factor is ready for recommendation tiering; downstream
  recommendation tiering, position validation, dashboards, trading,
  production, local-lake, factor-mining, and DQN/RL remain locked.
- Next allowed governance goal:
  `GOAL-CODEX-MAX-ONBOARDING-SMOKE-01-REMOTE-WINDOWS-GITHUB-ONLY-COMPLIANCE-GATE`.
- Next allowed Codex Max smoke goal:
  `GOAL-CODEX-MAX-ONBOARDING-SMOKE-01-REMOTE-WINDOWS-GITHUB-ONLY-COMPLIANCE-GATE`.
- Next allowed data/research goal after the smoke test:
  `GOAL-DATA-EXPANSION-RESEARCH-01`.
- Locked downstream stages: GOAL-REC-TIERING-01 until `ready_factor_count > 0`
  and explicit user approval, GOAL-10B.4, position-band validation, GOAL-10D,
  dashboard/frontend, trading, broker, production, portfolio backtest,
  local-lake, factor-mining, and DQN/RL.
- Codex Max remote Windows GitHub-only constraint: Codex Max may use only
  GitHub repository code, docs, configs, committed outputs/audits, and remote
  branches/tags. It must not rely on local Mac paths, local bundles, local
  provider caches, local-lake data, or uncommitted local state.

## GOAL-PREMARKET-RESEARCH-AND-POSITION-WORKSPACE-DASHBOARD-01

Issue #24 implements one goal-specific local research workspace over the merged
PR #23 operational position-management evidence.

- Status: `PASS`.
- Branch target: `project-current`; predecessor PR #23 is merged.
- Interface: 23 governed pages in `apps/premarket-workspace`.
- API: 22 FastAPI GET routes and zero write routes.
- Source snapshot: `2026-07-01`, checksum status `VERIFIED`.
- Current evidence: 41 symbols, 41 position-band rows, 12 abstentions,
  13 constraints, and 7 substantive constraints.
- Current live readiness fails closed as `BLOCKED / STALE_SOURCE_DATA`; the
  immutable replay remains explicitly selectable.
- `ready_factor_count = 0`; Alpha, Factor Monitor, IC/RankIC, factor
  correlation, Recommendation Tiering, and Issue #10 stay locked as specified.
- Missing fundamentals are `N/A / UNAVAILABLE`; no market, fundamental,
  factor, Alpha, IC/RankIC, or recommendation evidence is fabricated.
- Browser watchlists use local storage only. Broker connections, orders, paper
  trading, production writes, and production promotion remain absent.
- The goal-specific capability is `implemented_research_only`.
- The generic `dashboard` capability remains `false`, and
  `dashboard_daily_report` remains `locked_future`.

Run with `python scripts/run_premarket_workspace.py`. Deterministic goal and
audit evidence are under
`outputs/audits/goal_premarket_research_position_workspace_dashboard01_*`.

## GOAL-DAILY-INCREMENTAL-EVIDENCE-REFRESH-01

The controlled daily research evidence refresh is implemented on top of the
portfolio-risk, OPM01, and named local workspace goals.

- Status: `PASS`; committed deterministic refresh: `SUCCEEDED`.
- Clock: target `2026-07-01`, expected T-1 `2026-06-30`, latest evidence
  `2026-06-30`, mode `deterministic_replay`.
- Evidence modes: committed replay, bounded local incremental CSV, and explicit
  network opt-in through the existing AKShare adapter. Network remains disabled
  by default and raw provider responses are not committed.
- Validation runs before OPM and fails closed for missing trading-calendar
  coverage, stale or future data, required-symbol missingness, provider
  failures, timestamp/PIT violations, invalid quarantine state, and checksum
  mismatch. It does not guess an unconfigured exchange session.
- Provider rules remain primary-source/no-averaging. Existing discrepancy
  quarantine is preserved, and cross-provider adjustment convention remains
  explicitly `UNRESOLVED` where metadata is unavailable.
- Successful refreshes call OPM01 and verify the immutable snapshot before the
  latest refresh pointer advances. Failed refreshes publish a blocked reason
  without advancing the latest valid OPM snapshot.
- The daily layer does not duplicate upstream risk estimators. OPM reuses the
  validated predecessor portfolio-risk outputs, and this limitation is
  recorded in refresh provenance.
- The workspace surfaces latest refresh state, last successful time, freshness,
  validation, blocked reasons, and snapshot version.
- Future experiment contracts cover only date range, snapshot lineage,
  evaluation metadata, and baseline reference. Status remains
  `PREPARED_NOT_STARTED`; no observations or performance claims exist.
- `ready_factor_count = 0`; Recommendation Tiering, recommendation outputs,
  trading, broker, paper execution, production writes, and DQN/RL remain
  locked or absent.

Operational command: `python scripts/run_daily_incremental_evidence_refresh.py`.

Deterministic governance commands:

- `python scripts/run_goal_daily_incremental_evidence_refresh01.py`
- `python scripts/audit_goal_daily_incremental_evidence_refresh01.py`

## GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01

GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01 is implemented as a bounded
research-only portfolio risk and position-management track over committed
expanded evidence.

- Status: `PASS_WITH_WARNINGS`.
- Provider reconciliation: 4,910 baostock/akshare-sina overlap rows checked;
  six material discrepancies were quarantined from risk-model fitting.
- Canonical risk dataset: 34,543 canonical rows, 843 dates, 41 symbols,
  34,496 eligible risk rows, and three index context series.
- Current holdings mode: no real current holdings snapshot was supplied; the
  system runs in `research_reference_portfolio_mode` and does not fabricate
  holdings.
- Risk state: `normal_risk_review_only` for the research reference portfolio.
- Constraint engine: six non-actionable research constraints implemented, with
  current-holdings-missing fail-closed behavior.
- Policies compared: `equal_weight`, `inverse_volatility`,
  `minimum_variance_diagonal`, and `equal_risk_contribution_diagonal` under
  chronological walk-forward, final holdout, bounded cost, turnover, and regime
  stability diagnostics.
- Preferred policy outcome: `no_single_robust_winner`; `inverse_volatility` is
  used only as a conservative research band reference.
- Position-band output: 41 symbols have research-only acceptable risk bands,
  zero target weights, zero order instructions, and zero recommendation output.
- Ready factor count remains `0`; GOAL-REC-TIERING-01, GOAL-10B.4, position
  validation, GOAL-10D, dashboard/frontend, trading, broker, production,
  portfolio backtest, local-lake, factor-mining, and DQN/RL remain locked.

## GOAL-FACTOR-READINESS-RERUN-02

GOAL-FACTOR-READINESS-RERUN-02 is implemented as a research-only expanded
evidence readiness rerun over the committed GOAL-NETWORK-EVIDENCE-INGESTION-01
bundle.

- Status: `PASS_WITH_WARNINGS`.
- Evidence consumed: 34,543 `akshare_sina` daily rows, 843 stock trading dates,
  41 acquired symbols out of 50 attempted governed symbols, and three index
  context series (`sh000001`, `sh000300`, `sz399001`).
- Bundle checksums were verified against
  `outputs/research/goal_network_evidence_ingestion01_evidence_bundle_manifest.json`.
- Old/new panel relationship: old Readiness01 panel 180,000 rows over 120
  dates; reconstructed Rerun02 panel 1,036,290 source-factor/refinement rows
  over 843 dates.
- Candidates evaluated: 120 fixed-threshold candidates using the existing
  STRONG_IC, MIN_VALID_ROWS, holdout, sign-stability, aligned-horizon, and
  walk-forward rules.
- Readiness result: `ready_factor_count_before = 0`,
  `ready_factor_count_after = 0`; all 120 candidates are `not_ready`.
- Old/new transitions: 63 candidates lost prior `conditionally_useful` status;
  57 remained `not_ready`.
- Provider robustness: 4,910 old baostock/new akshare-sina overlap rows were
  checked; six >2% discrepancy warnings were recorded.
- Index context contribution: all nine fixed index-context checks are
  `weak_or_unstable_context`.
- GOAL-REC-TIERING-01 remains `locked_future`; no workflow status or locked
  capability was modified, and no recommendation, position, dashboard, trading,
  production, local-lake, factor-mining, broker, or DQN/RL output was created.

## Stable Repository Checkpoint

GOAL-REPOSITORY-CHECKPOINT-01 is implemented as a governance-only checkpoint
gate for the Arch03 stable point.

- Current stable commit: `310559ae18bbf203e795c1d66bc7181a6b11c14a`
- Authoritative Codex Max entrypoint branch: `project-current`
- Frozen checkpoint branch: `checkpoint/arch03-stable-310559`
- Annotated checkpoint tag: `checkpoint-arch03-stable-310559`
- User-private local bundle backup exists outside GitHub; it is not a Codex
  Max onboarding input or validation dependency.
- Latest factor status: ready factor count remains 0.
- Latest regime status: Regime01 implemented.
- Latest architecture status: Arch03 implemented.
- Provider/source catalog status: AKShare source catalog 70 rows; provider
  registry network disabled by default.
- Next planned governance goal: `GOAL-CODEX-OPERATING-SYSTEM-01`.
- Next research/data goal after governance:
  `GOAL-DATA-EXPANSION-RESEARCH-01`.

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
review-only diagnostic prototype. GOAL-08A is implemented only as a names-only
future recommendation contract design gate with zero rows. GOAL-STORAGE-01 is
implemented as an infrastructure-only local research lake hardening gate
(`PASS`); it does not unlock GOAL-08B by itself or create local lake data.
GOAL-08B.0 is implemented as a review-only unlock gate (`PASS_WITH_WARNINGS`).
GOAL-08B is now implemented only as a review-only non-actionable
recommendation diagnostics prototype (`PASS_WITH_WARNINGS`): it writes 100
deterministic `trade_date + symbol` diagnostic rows from GOAL-07B risk
diagnostics and GOAL-08A contract rules. It does not create actionable
recommendations, buy/sell/hold outputs, target prices, expected returns for
action, position sizing, portfolio weights, dashboards, trading paths,
production behavior, backtests, factor-mining outputs, local lake files, broker
outputs, or DQN/RL outputs.
GOAL-09.0 is implemented as a review-only unlock gate (`PASS_WITH_WARNINGS`).
It uses only prior GOAL-07B, GOAL-08A, GOAL-STORAGE-01, GOAL-08B.0, and
GOAL-08B PASS/PASS_WITH_WARNINGS evidence. GOAL-09 position-band diagnostics
are now implemented only as a review-only non-actionable diagnostics prototype
(`PASS_WITH_WARNINGS`): it writes deterministic `trade_date + symbol`
diagnostic rows, preserves `position_actionability_status=never_actionable`,
and creates no actual position rows, position sizing, portfolio weights, target
weights, order quantities, buy/sell/hold outputs, target prices, dashboards,
trading paths, production behavior, backtests, factor-mining outputs, local
lake files, broker outputs, or DQN/RL outputs.
GOAL-09.1 is implemented as a review/readiness-only warning classification and
dashboard-readiness gate (`PASS_WITH_WARNINGS`). It classifies the remaining
GOAL-09 warnings for future dashboard display contracts, allows only a future
explicit GOAL-DASHBOARD-00 design/contract gate request, and keeps Dashboard /
Daily Report UI `locked_future`. It creates no dashboard output, HTML,
Streamlit, frontend code, visual reports, new recommendation rows, new position
rows, trading paths, production behavior, backtests, factor-mining outputs,
local lake files, broker outputs, or DQN/RL outputs.
GOAL-V1-INTEGRITY-01 is implemented as an infrastructure-only artifact-lineage
and structure gate (`PASS_WITH_WARNINGS`). It verifies the review-only V1 chain
from GOAL-07B risk diagnostics through GOAL-08B recommendation diagnostics,
GOAL-09 position-band diagnostics, and GOAL-09.1 dashboard-readiness evidence.
It creates no new risk rows, recommendation rows, position rows, dashboard
outputs, HTML, Streamlit, frontend code, visual reports, local lake files,
trading paths, production behavior, backtests, factor-mining outputs, broker
outputs, or DQN/RL outputs. Dashboard / Daily Report UI remains `locked_future`;
only a future explicit GOAL-DASHBOARD-00 design/contract gate request is now
eligible.
GOAL-10A is implemented as a design-only future backtest contract gate
(`PASS_WITH_WARNINGS`). It consumes only prior GOAL-08B non-actionable
recommendation diagnostics, GOAL-09 non-actionable position-band diagnostics,
and GOAL-V1-INTEGRITY-01 lineage evidence to define future input, date
alignment, T+1/no-lookahead, metric, grouping, benchmark, cost/slippage, and
tradability policies. It runs no backtest, creates no performance rows, equity
curves, portfolio returns, dashboard output, HTML, Streamlit, frontend code,
trading path, production behavior, broker output, factor-mining output, local
lake file, or DQN/RL output. GOAL-10B is implemented only by its own
review-only diagnostic gate, and GOAL-10B.2/GOAL-10C are implemented only by
their own review-only non-actionable diagnostic gates. GOAL-10D, Dashboard /
Daily Report UI, paper/live trading, broker, production, factor-mining, and
DQN/RL remain locked.
GOAL-10B is implemented as a review-only recommendation diagnostics backtest
(`PASS_WITH_WARNINGS`). It joins GOAL-08B non-actionable recommendation
diagnostics to existing PIT-safe forward-return labels using GOAL-10A T+1
alignment and writes grouped diagnostic metrics plus IC/RankIC availability
evidence only. It creates no BUY/SELL/HOLD actions, target prices, position
sizing, portfolio weights, portfolio returns, equity curves, dashboard output,
trading path, production behavior, broker output, factor-mining output, local
lake file, or DQN/RL output. GOAL-10C, GOAL-10D, Dashboard / Daily Report UI,
paper/live trading, broker, production, factor-mining, and DQN/RL remain locked
unless an explicit later gate implements a review-only diagnostic. In the
current state, GOAL-10C has proceeded only as review-only non-actionable
row-level sensitivity diagnostics, and GOAL-10D remains locked.
GOAL-10B.1 is implemented as a review-only coverage and group-variation repair
gate (`PASS_WITH_WARNINGS`). It audits existing label, Stage6C, GOAL-08B, and
GOAL-10B artifacts only, determines that repair is not possible with current
artifacts, and records `coverage_repair_not_possible_with_current_artifacts`.
It creates no repaired backtest snapshot, repaired group metrics, new
recommendation rows, new position rows, data fetch, panel expansion, portfolio
returns, equity curves, dashboard output, trading path, production behavior,
broker output, factor-mining output, local lake file, or DQN/RL output.
GOAL-DATA-LABEL-01 is implemented as a review-only forward-return label
coverage expansion gate (`PASS_WITH_WARNINGS`). It derives 100 deterministic
label rows from existing committed OHLCV and benchmark samples only, including
1d, 3d, 5d, and 20d stock, benchmark, and excess-return labels where future
bars exist; 80 rows are 20d-label-ready. It remains single-symbol and does not
yet overlap GOAL-08B or GOAL-09 diagnostics by `trade_date + symbol`.
GOAL-V1-DIAGNOSTIC-COVERAGE-02 is implemented as a review-only multi-symbol
diagnostic coverage expansion gate (`PASS_WITH_WARNINGS`). It derives 8
non-actionable diagnostic rows per family for risk, recommendation, and
position-band coverage from existing committed Stage 6C approved-symbol sample
evidence only. It does not overwrite canonical GOAL-07B/08B/09 artifacts and
does not run a backtest. Because multi-symbol 20d label alignment is still
unavailable, GOAL-10B.2 revalidation proceeds only as bounded review-only
diagnostics with warnings.
GOAL-10B.2 is implemented as a review-only recommendation backtest
revalidation gate (`PASS_WITH_WARNINGS`). It consumes GOAL-V1-DIAGNOSTIC-
COVERAGE-02 recommendation and risk diagnostics, writes an 8-row input
snapshot plus recommendation-status, symbol, and horizon-coverage diagnostic
metrics, and keeps every row non-actionable. It creates no BUY/SELL/HOLD
actions, target prices, positions, portfolio returns, equity curves,
dashboards, trading paths, production behavior, broker output, factor-mining
output, local lake file, or DQN/RL output.
GOAL-10C is implemented as a review-only position-band cost/slippage
sensitivity gate (`PASS_WITH_WARNINGS`). It consumes GOAL-V1-DIAGNOSTIC-
COVERAGE-02 position-band diagnostics and GOAL-10B.2 readiness evidence, writes
8 input snapshot rows, 24 row-level cost/slippage sensitivity rows, and 3 group
metric rows, all non-actionable. It creates no actual positions, sizing,
weights, orders, portfolio returns, equity curves, dashboards, trading paths,
production behavior, broker output, factor-mining output, local lake file, or
DQN/RL output. GOAL-10D, Dashboard / Daily Report UI, signal and portfolio
backtest promotion, paper/live trading, broker, production, local-lake,
factor-mining, and DQN/RL remain locked or deleted from active mainline.
GOAL-DATA-PROVIDER-02A is implemented as a review-only multi-provider
capability probe gate (`PASS_WITH_WARNINGS`). It records provider availability,
schema mapping, and failure taxonomy metadata for Tushare Pro, Baostock,
AkShare, efinance, qstock, yfinance auxiliary, and local import fallback over
the current approved-symbol smoke universe and a 30-trading-day contract
window. It creates no final evaluation panel, recommendation diagnostics,
position-band diagnostics, backtest rows, portfolio returns, equity curves,
dashboards, trading paths, production behavior, broker output, local lake file,
factor-mining output, or DQN/RL output. GOAL-DATA-PROVIDER-02B,
GOAL-V1-DIAGNOSTIC-COVERAGE-03, and GOAL-10B.3 are implemented only by their
own later review-only gates. GOAL-DATA-PANEL-02, GOAL-10D, Dashboard / Daily
Report UI, signal and portfolio backtest promotion, paper/live trading, broker,
production, local-lake, factor-mining, and DQN/RL remain locked or deleted from
active mainline.
GOAL-DATA-PROVIDER-02A.1 is implemented as a review-only network-opt-in
provider smoke test gate (`PASS_WITH_WARNINGS`). It records live-access attempt
metadata for Tushare Pro, Baostock, AkShare, efinance, qstock, yfinance
auxiliary, and local import fallback. Live provider access is attempted only
when `ASHARE_ALLOW_NETWORK_INGESTION=1` is present; Tushare additionally
requires `ASHARE_ALLOW_TUSHARE=1` and `TUSHARE_TOKEN` from the environment.
It persists no provider token, raw payload, final evaluation panel,
recommendation diagnostic, position-band diagnostic, backtest row, portfolio
return, equity curve, dashboard, trading path, production behavior, broker
output, local lake file, factor-mining output, or DQN/RL output.
GOAL-DATA-PROVIDER-02B is implemented as a review-only source-backed
evaluation panel build gate (`PASS_WITH_WARNINGS`). It writes a bounded
normalized panel artifact for future review-only diagnostics planning:
6000 rows, 50 symbols, and 120 trade dates, with provider usage, coverage,
failure-taxonomy, manifest, report, and audit evidence. The gate records a
candidate provider-panel universe when the canonical approved universe is below
the required 50 symbols; it does not promote that candidate universe into the
approved trading universe or into GOAL-DATA-PANEL-02. It creates no
recommendation diagnostic, position-band diagnostic, backtest row, portfolio
return, equity curve, dashboard, trading path, production behavior, broker
output, local lake file, factor-mining output, or DQN/RL output.
GOAL-V1-DIAGNOSTIC-COVERAGE-03 is implemented as a review-only source-backed
multi-symbol diagnostics gate (`PASS_WITH_WARNINGS`). It consumes only the
GOAL-DATA-PROVIDER-02B normalized panel and writes separate non-actionable
risk, recommendation eligibility, and position-band diagnostics at
`trade_date + symbol` grain: 6000 rows per family, 50 symbols, and 120 trade
dates. Natural group variation is available: risk severity is 5990 MEDIUM /
10 HIGH, recommendation eligibility is 5990 review-only revalidation eligible /
10 blocked by source risk, and position-band status is 5990 blocked
non-actionable / 10 blocked high-risk. It preserves canonical GOAL-07B/08B/09
artifacts and creates no BUY/SELL/HOLD output, target prices, actual position
sizes, weights, orders, portfolio returns, equity curves, dashboards, trading
paths, production behavior, broker output, local lake file, factor-mining
output, or DQN/RL output.
GOAL-10B.3 is implemented as a review-only DC03 recommendation revalidation
gate (`PASS_WITH_WARNINGS`). It consumes only GOAL-V1-DIAGNOSTIC-COVERAGE-03
recommendation/risk diagnostics and the GOAL-DATA-PROVIDER-02B source-backed
panel, writes a 6000-row input snapshot plus recommendation, risk-severity,
symbol, horizon-coverage, and group-imbalance diagnostics, and keeps every row
non-actionable. It records full 1d/5d/20d label coverage, but classifies the
signal as `recommendation_revalidation_signal_weak_or_unreliable` because one
recommendation group dominates 5990 of 6000 rows, the blocked group has only
10 rows, and IC/RankIC is unavailable without a numeric recommendation score.
It recommends GOAL-RISK-TIERING-01 / GOAL-REC-TIERING-01 before any
position-band validation. It creates no BUY/SELL/HOLD output, target price,
position size, weight, order, portfolio return, equity curve, dashboard,
trading path, production behavior, broker output, local lake file,
factor-mining output, or DQN/RL output.
GOAL-RISK-TIERING-01 is implemented as a review-only risk severity and numeric
score tiering gate (`PASS_WITH_WARNINGS`). It consumes only DC03 risk
diagnostics, the GOAL-DATA-PROVIDER-02B source-backed panel, and GOAL-10B.3
imbalance evidence, and writes a separate 6000-row non-actionable risk-tiered
diagnostic artifact. Bucket distribution is 2891 LOW, 2821 MEDIUM, 278 HIGH,
and 10 INSUFFICIENT_EVIDENCE review-only rows; the 10-row insufficient bucket
keeps the result at `risk_tiering_signal_weak_or_unreliable`. Score
construction excludes `forward_return_*`, `benchmark_excess_return_*`, and
`label_ready_*`; those fields are used only for post-hoc group evaluation.
Canonical GOAL-07B and DC03 risk diagnostics are not overwritten.
GOAL-RISK-TIERING-01.1 is implemented as a review-only risk-score
directionality and downside-risk repair gate (`PASS_WITH_WARNINGS`). It
consumes only GOAL-RISK-TIERING-01 diagnostics/distribution/forward metrics,
DC03 risk diagnostics, and the GOAL-DATA-PROVIDER-02B source-backed panel, then
writes separate non-actionable downside-risk diagnostics, component
contribution, distribution, and post-hoc forward-return metric evidence. It
separates volatility/momentum and abnormal movement flags from the downside
score, excludes `forward_return_*`, `benchmark_excess_return_*`, and
`label_ready_*` from score construction, uses future returns only after bucket
assignment for post-hoc evaluation, and records
`downside_risk_tiering_signal_weak_or_unreliable`. GOAL-RISK-TIERING-01 and
DC03 artifacts are not overwritten.
GOAL-QUANT-RESEARCH-01 is implemented as a research-only factor research lab
and score validity gate (`PASS_WITH_WARNINGS`). It consumes only committed
Provider02B, DC03, GOAL-10B.3, GOAL-RISK-TIERING-01, and
GOAL-RISK-TIERING-01.1 evidence, evaluates 11 candidate factor definitions
over a 66000-row `trade_date + symbol + factor_id` panel, and writes factor
registry, bucket, IC/RankIC, monotonicity, rolling-stability, regime
availability, trial-registry, and score-validity diagnostics only. It uses
forward returns only after factor assignment for post-hoc evaluation, records
anti-overfitting controls, creates no recommendation rows, position rows,
portfolio outputs, dashboards, trading paths, production behavior, local-lake
files, broker outputs, factor-mining outputs, or DQN/RL outputs, and currently
classifies the state as `no_factor_ready_for_rec_tiering`.
GOAL-MVP-01 is implemented as a research-only premarket diagnostic terminal
(`PASS_WITH_WARNINGS`). It consumes only committed Provider02B, DC03,
GOAL-RISK-TIERING-01, GOAL-RISK-TIERING-01.1, and GOAL-QUANT-RESEARCH-01
evidence, resolves the latest report date as `2026-05-21`, and writes a
Markdown research report, 50-row symbol diagnostic table, review queue,
factor-validity summary, market-context summary, and run/audit manifests only.
It explicitly states that no factor is currently approved for recommendation
tiering and that the terminal is research-only. It creates no actionable
recommendations, positions, portfolio outputs, dashboard/frontend files,
trading paths, production behavior, local-lake files, broker outputs,
factor-mining outputs, or DQN/RL outputs.
GOAL-ALPHA-FACTOR-CANDIDATE-01 is implemented as a research-only alpha factor
candidate construction gate (`PASS_WITH_WARNINGS`). It consumes only committed
Provider02B, MVP, Quant Research, and risk-tiering evidence, writes a 13-row
candidate registry, 78000-row normalized candidate panel, coverage summary,
construction warnings, contract, docs, manifest, report, and audit evidence,
and excludes future returns, benchmark-excess returns, and label-ready fields
from factor construction. It creates no recommendation rows, position rows,
portfolio outputs, dashboard/frontend files, trading paths, production
behavior, local-lake files, broker outputs, factor-mining outputs, DQN/RL
outputs, or predictive-validity claims.
GOAL-QUANT-RESEARCH-02 is implemented as a research-only alpha candidate
factor validity evaluation gate (`PASS_WITH_WARNINGS`). It consumes committed
GOAL-ALPHA-FACTOR-CANDIDATE-01 and Provider02B evidence, writes a 78000-row
alpha evaluation panel plus coverage, bucket, IC/RankIC, monotonicity, rolling
stability, horizon consistency, score-validity, trial-registry, contract, docs,
manifest, report, and audit evidence. Forward returns and benchmark-excess
returns are used only post-hoc after factor values already exist. Ready factor
count is `0`, so the recommended next step is GOAL-ALPHA-FACTOR-CANDIDATE-02
or GOAL-ALPHA-RESEARCH-REFINEMENT-01 before recommendation tiering. It creates
no recommendation rows, position rows, portfolio outputs, dashboard/frontend
files, trading paths, production behavior, local-lake files, broker outputs,
factor-mining outputs, DQN/RL outputs, or production predictive-validity
claims.
GOAL-ALPHA-RESEARCH-REFINEMENT-01 is implemented as a research-only rolling
stability and candidate refinement gate (`PASS_WITH_WARNINGS`). It consumes
only committed Quant02, Alpha Candidate 01, Provider02B, and MVP evidence,
diagnoses 6 promising rolling-unstable alpha candidates, writes 120
conditional-stability rows, 30 proposed refined candidate design rows, 4
intraday redefinition rows, and 34 trial-registry update rows. All proposed
designs are marked not evaluated and not accepted downstream. It creates no
refined factor panel, recommendation rows, position rows, portfolio outputs,
dashboard/frontend files, trading paths, production behavior, local-lake files,
broker outputs, factor-mining outputs, DQN/RL outputs, or predictive-validity
claims.
GOAL-ALPHA-FACTOR-CANDIDATE-02 is implemented as a research-only refined alpha
candidate construction gate (`PASS_WITH_WARNINGS`). It consumes only committed
GOAL-ALPHA-RESEARCH-REFINEMENT-01, GOAL-ALPHA-FACTOR-CANDIDATE-01, Quant02,
Provider02B, MVP, and risk-tiering evidence, writes a 30-row refined candidate
registry, 180000-row refined candidate panel, 30-row coverage summary,
74-row construction warning table, 4-row intraday redefinition status, 30-row
trial registry, contract, docs, report, manifest, and audit evidence. It uses
only current-or-past committed inputs, keeps future returns, benchmark-excess
returns, and label-ready fields out of construction, marks all downstream
acceptance flags false, and creates no predictive-validity evaluation,
recommendation rows, position rows, portfolio outputs, dashboard/frontend
files, trading paths, production behavior, local-lake files, broker outputs,
factor-mining outputs, DQN/RL outputs, or promotion claims.
GOAL-QUANT-RESEARCH-03 is implemented as a research-only refined alpha factor
validity evaluation gate (`PASS_WITH_WARNINGS`). It consumes only committed
Candidate02, Quant02, Provider02B, MVP, and risk-tiering evidence, evaluates
30 refined factors over 180000 partitioned evaluation rows, writes coverage,
bucket, IC/RankIC, monotonicity, rolling-stability, horizon-consistency,
improvement, score-validity, trial-registry, contract, docs, report, manifest,
and audit evidence, and records ready factor count `0` with partial improvement
available. Forward returns and benchmark-excess returns are used only post-hoc
after refined values and buckets already exist. It creates no recommendation
rows, position rows, portfolio outputs, dashboard/frontend files, trading
paths, production behavior, local-lake files, broker outputs, factor-mining
outputs, DQN/RL outputs, or production predictive-validity claims.
GOAL-REGIME-LABEL-RESEARCH-01 is implemented as a research-only market regime
label construction gate (`PASS_WITH_WARNINGS`). It consumes committed
Provider02B, Quant03, Candidate02, MVP, and risk-tiering evidence only, writes
120 date-level regime labels, 6000 symbol-level regime context rows, a
180000-row factor-regime bridge, coverage, transition, warning, contract,
docs, report, manifest, and audit evidence. Regime labels use current-date or
trailing benchmark trend, benchmark volatility, cross-sectional breadth,
dispersion, liquidity, downside-risk, and composite regime rules only. Future
returns, benchmark-excess forward returns, label-ready fields, and post-hoc
factor performance are excluded from label construction. It creates no market
timing signal, recommendation rows, position rows, portfolio outputs,
dashboard/frontend files, trading paths, production behavior, local-lake files,
broker outputs, factor-mining outputs, DQN/RL outputs, or predictive-validity
claims.
GOAL-ARCHITECTURE-REFACTOR-03 is implemented as an engineering research-support
AKShare source catalog and provider modularization gate (`PASS_WITH_WARNINGS`).
It writes provider registry metadata, AKShare source catalog metadata,
architecture inventory, duplicate-pattern inventory, modularization plan,
common audit/runner/contract/provider helper modules, docs, report, manifest,
and audit evidence only. It does not fetch full live AKShare datasets, write
local-lake data, change scientific outputs, create alpha factors, create
recommendations, create positions, create portfolio output, create
dashboard/frontend files, trade, write production data, integrate brokers,
activate factor-mining, or create DQN/RL outputs.
GOAL-DATA-EXPANSION-RESEARCH-01, GOAL-REC-TIERING-01,
GOAL-10B.4, position-band validation,
GOAL-DATA-PANEL-02, GOAL-10D, Dashboard / Daily Report UI, signal and
portfolio backtest promotion, paper/live trading, broker, production,
local-lake, factor-mining, and DQN/RL remain locked or deleted from active
mainline.

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
- GOAL-08A recommendation contract design-only gate with names-only future
  schema, warning propagation policy, HIGH-risk actionability block, and zero
  recommendation rows
- GOAL-STORAGE-01 local research lake hardening gate with data-root,
  directory-boundary, placement, manifest, checksum, schema-registry, and
  GitHub hygiene rules
- GOAL-08B.0 recommendation review-only unlock gate using prior GOAL-07B,
  GOAL-08A, and GOAL-STORAGE-01 evidence only
- GOAL-08B non-actionable recommendation diagnostics prototype with 100
  deterministic review-only `trade_date + symbol` diagnostic rows
- GOAL-09.0 position-band review-only unlock gate using prior GOAL-08B
  non-actionable diagnostics evidence only
- GOAL-09 non-actionable position-band diagnostics prototype with
  deterministic review-only `trade_date + symbol` diagnostic rows
- GOAL-09.1 position-band warning review and dashboard-readiness gate with
  future dashboard contract constraints only
- GOAL-V1-INTEGRITY-01 artifact-lineage and structure integrity gate over the
  GOAL-07B -> GOAL-08B -> GOAL-09 -> GOAL-09.1 review-only chain
- GOAL-10A backtest contract design gate for future review-only validation
  contract rules only, with no backtest execution or performance rows
- GOAL-10B recommendation diagnostics backtest review-only prototype with
  grouped non-actionable forward-return diagnostics and IC/RankIC availability
  evidence only
- GOAL-10B.1 backtest coverage repair gate with existing-artifact coverage,
  distribution, and label-source diagnostics only
- GOAL-DATA-LABEL-01 forward-return label coverage expansion from committed
  OHLCV and benchmark samples only
- GOAL-V1-DIAGNOSTIC-COVERAGE-02 multi-symbol non-actionable diagnostic
  coverage expansion from committed Stage 6C approved-symbol evidence only
- GOAL-10B.2 recommendation backtest revalidation diagnostics over bounded
  GOAL-V1-DIAGNOSTIC-COVERAGE-02 rows only
- GOAL-10C row-level cost/slippage sensitivity diagnostics over bounded
  position-band rows only
- GOAL-DATA-PROVIDER-02A provider capability metadata only
- GOAL-DATA-PROVIDER-02A.1 network opt-in provider smoke-test metadata only
- GOAL-DATA-PROVIDER-02B bounded source-backed evaluation panel evidence only
- GOAL-V1-DIAGNOSTIC-COVERAGE-03 source-backed non-actionable diagnostic
  coverage from the 02B panel only
- GOAL-REGIME-LABEL-RESEARCH-01 research-only no-lookahead market regime label
  construction from committed Provider02B, Quant03, Candidate02, MVP, and
  risk-tiering evidence only
- GOAL-ARCHITECTURE-REFACTOR-03 engineering research-support AKShare source
  catalog, provider registry, architecture inventory, and common helper
  foundation only
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
- GOAL-08B.0 recommendation review-only unlock gate (`PASS_WITH_WARNINGS`;
  `implemented_review_only`; unlock-only evidence, no recommendation
  diagnostics rows created by that gate)
- GOAL-08B recommendation diagnostics prototype (`PASS_WITH_WARNINGS`;
  `implemented_review_only`; 100 non-actionable diagnostic rows at
  `trade_date + symbol` grain)
- GOAL-09.0 position-band review-only unlock gate (`PASS_WITH_WARNINGS`;
  `implemented_review_only`; unlock-only evidence, no position-band rows)
- GOAL-09 position-band diagnostics prototype (`PASS_WITH_WARNINGS`;
  `implemented_review_only`; non-actionable diagnostic rows at
  `trade_date + symbol` grain)
- GOAL-09.1 position-band warning review and dashboard-readiness gate
  (`PASS_WITH_WARNINGS`; `implemented_review_only`; no dashboard outputs)
- GOAL-10B recommendation diagnostics backtest review-only prototype
  (`PASS_WITH_WARNINGS`; `implemented_review_only`; non-actionable grouped
  forward-return diagnostics only)
- GOAL-10B.1 backtest coverage and group-variation repair gate
  (`PASS_WITH_WARNINGS`; `implemented_review_only`; existing-artifact coverage
  diagnostics only; no repaired rows or metrics)
- GOAL-DATA-LABEL-01 forward-return label coverage expansion
  (`PASS_WITH_WARNINGS`; `implemented_review_only`; committed-sample label
  coverage only; no diagnostic rows or backtests)
- GOAL-V1-DIAGNOSTIC-COVERAGE-02 multi-symbol diagnostics expansion
  (`PASS_WITH_WARNINGS`; `implemented_review_only`; 8 non-actionable risk,
  recommendation, and position-band diagnostic coverage rows per family; no
  canonical diagnostic overwrite and no backtests)
- GOAL-10B.2 recommendation backtest revalidation (`PASS_WITH_WARNINGS`;
  `implemented_review_only`; bounded non-actionable recommendation
  revalidation diagnostics only)
- GOAL-10C cost/slippage sensitivity (`PASS_WITH_WARNINGS`;
  `implemented_review_only`; row-level non-actionable position-band sensitivity
  diagnostics only)
- GOAL-DATA-PROVIDER-02A multi-provider capability probe
  (`PASS_WITH_WARNINGS`; `implemented_review_only`; provider capability
  metadata only; no evaluation panel)
- GOAL-DATA-PROVIDER-02A.1 network opt-in provider smoke test
  (`PASS_WITH_WARNINGS`; `implemented_review_only`; opt-in smoke-test metadata
  only; no final panel)
- GOAL-DATA-PROVIDER-02B source-backed evaluation panel build gate
  (`PASS_WITH_WARNINGS`; `implemented_review_only`; bounded normalized
  source-backed panel evidence only; no diagnostics, backtests, dashboards, or
  execution outputs)
- GOAL-V1-DIAGNOSTIC-COVERAGE-03 source-backed multi-symbol diagnostics gate
  (`PASS_WITH_WARNINGS`; `implemented_review_only`; separate non-actionable
  risk, recommendation eligibility, and position-band diagnostics from 02B
  panel evidence only)
- GOAL-10B.3 DC03 recommendation revalidation gate (`PASS_WITH_WARNINGS`;
  `implemented_review_only`; non-actionable group/symbol/horizon diagnostics
  from DC03 plus Provider02B evidence only; weak/unreliable signal warning)
- GOAL-RISK-TIERING-01 risk severity numeric score tiering gate
  (`PASS_WITH_WARNINGS`; `implemented_review_only`; separate non-actionable
  risk-tier diagnostics only; future returns excluded from score construction)
- GOAL-RISK-TIERING-01.1 downside-risk repair gate (`PASS_WITH_WARNINGS`;
  `implemented_review_only`; separate non-actionable downside-risk diagnostics
  only; future returns excluded from score construction)
- GOAL-QUANT-RESEARCH-01 factor research lab and score validity gate
  (`PASS_WITH_WARNINGS`; `implemented_research_only`; research-only factor
  validity diagnostics over committed Provider02B/DC03/risk-tiering evidence
  only; no factor ready for recommendation tiering)
- GOAL-MVP-01 premarket research diagnostic terminal (`PASS_WITH_WARNINGS`;
  `implemented_mvp_research_only`; committed-evidence replay only)
- GOAL-ALPHA-FACTOR-CANDIDATE-01 alpha factor candidate construction
  (`PASS_WITH_WARNINGS`; `implemented_research_only`; no predictive-validity
  evaluation)
- GOAL-QUANT-RESEARCH-02 alpha candidate validity evaluation
  (`PASS_WITH_WARNINGS`; `implemented_research_only`; ready factor count 0)
- GOAL-ALPHA-RESEARCH-REFINEMENT-01 rolling-stability attribution and refined
  candidate design planning (`PASS_WITH_WARNINGS`; `implemented_research_only`)
- GOAL-ALPHA-FACTOR-CANDIDATE-02 refined alpha candidate construction
  (`PASS_WITH_WARNINGS`; `implemented_research_only`; 180000 refined panel
  rows and all downstream acceptance flags false)
- GOAL-QUANT-RESEARCH-03 refined alpha validity evaluation
  (`PASS_WITH_WARNINGS`; `implemented_research_only`; ready factor count 0)
- GOAL-REGIME-LABEL-RESEARCH-01 market regime label construction
  (`PASS_WITH_WARNINGS`; `implemented_research_only`; date, symbol, and
  factor-regime bridge context only)
- GOAL-QUANT-RESEARCH-04 regime-conditional factor evaluation
  (`PASS_WITH_WARNINGS`; `implemented_research_only`; ready factor count 0;
  21 factors conditionally useful; does not unlock recommendation tiering)

Implemented engineering research-support:

- GOAL-ARCHITECTURE-REFACTOR-03 AKShare source catalog and provider
  modularization gate (`PASS_WITH_WARNINGS`;
  `implemented_engineering_research_support`; provider/source catalog,
  registry, inventory, common helper, docs, manifest, and audit artifacts only)

Implemented design-only:

- GOAL-07A risk overlay design gate (`PASS_WITH_WARNINGS`; contracts, schemas,
  rule catalog, state machine, upstream-warning mapping, and audits only)
- GOAL-08A recommendation contract design gate (`PASS`; names-only future
  contract and actionability guardrails only; zero recommendation rows)
- GOAL-10A backtest contract design gate (`PASS_WITH_WARNINGS`; future input,
  metric, grouping, execution alignment, benchmark, cost/slippage, and
  tradability contracts only; no backtest execution or performance rows)

Implemented infrastructure-only:

- GOAL-STORAGE-01 local research lake hardening gate (`PASS`; storage contract,
  hygiene audit, and workflow lock preservation only)
- GOAL-V1-INTEGRITY-01 artifact-lineage and structure gate
  (`PASS_WITH_WARNINGS`; canonical review-only V1 chain integrity evidence only)

Still locked:

- actionable recommendation or position-band output
- position sizing and portfolio weights
- GOAL-DATA-EXPANSION-RESEARCH-01 market regime data expansion
- GOAL-DATA-PANEL-02 evaluation panel build
- GOAL-10D failure attribution
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

GOAL-08A writes only design evidence:

- `configs/recommendation/goal08a_future_recommendation_input_contract.yaml`
- `configs/recommendation/goal08a_future_recommendation_schema.yaml`
- `configs/recommendation/goal08a_warning_propagation_policy.yaml`
- `configs/recommendation/goal08a_actionability_guardrails.yaml`
- `configs/recommendation/goal08a_recommendation_state_machine.yaml`
- `outputs/audits/goal08a_recommendation_contract_design_report.md`
- `outputs/audits/goal08a_recommendation_contract_design_manifest.json`
- `outputs/audits/goal08a_recommendation_contract_design_audit.md`

The GOAL-08A schema sample has row count `0`; it defines that future HIGH
GOAL-07B risk severity blocks actionable recommendation output, but it does not
generate recommendations, positions, dashboards, trading outputs, production
behavior, backtests, factor-mining outputs, broker outputs, or DQN/RL outputs.

GOAL-STORAGE-01 writes only infrastructure governance evidence:

- `configs/storage/goal_storage01_local_research_lake_contract.yaml`
- `docs/storage/GOAL_STORAGE01_LOCAL_RESEARCH_LAKE_HARDENING_GATE.md`
- `outputs/audits/goal_storage01_local_research_lake_hardening_report.md`
- `outputs/audits/goal_storage01_local_research_lake_hardening_manifest.json`
- `outputs/audits/goal_storage01_local_research_lake_hardening_audit.md`

The STORAGE-01 contract requires future heavy data roots to resolve from
`ASHARE_PREMARKET_DATA_ROOT`; the fallback path is documentation-only for this
gate. It defines `raw/`, `bundles/`, `lake/`, `metadata/`, `exports/`, and
`audit_samples/` boundaries, bundle versioning, manifest and checksum rules,
schema registry governance, and GitHub hygiene. It generated no local data lake,
raw provider payloads, recommendation diagnostics, position diagnostics,
dashboards, backtests, production writes, factor-mining outputs, broker outputs,
or DQN/RL outputs.

GOAL-08B.0 writes only unlock-governance evidence:

- `configs/recommendation/goal08b0_review_only_unlock_policy.yaml`
- `docs/recommendation/GOAL08B0_RECOMMENDATION_REVIEW_ONLY_UNLOCK_GATE.md`
- `outputs/audits/goal08b0_recommendation_review_only_unlock_report.md`
- `outputs/audits/goal08b0_recommendation_review_only_unlock_manifest.json`
- `outputs/audits/goal08b0_recommendation_review_only_unlock_audit.md`

GOAL-08B.0 uses prior GOAL-07B, GOAL-08A, and GOAL-STORAGE-01
PASS/PASS_WITH_WARNINGS evidence only. It generated no recommendation
diagnostics rows, recommendation rows, buy/sell/hold outputs, target prices,
positions, portfolio weights, dashboards, trading paths, production behavior,
backtests, factor-mining outputs, local lake files, broker outputs, or DQN/RL
outputs.

GOAL-08B writes only non-actionable recommendation diagnostic evidence:

- `configs/recommendation/goal08b_review_only_diagnostics_policy.yaml`
- `docs/recommendation/GOAL08B_REVIEW_ONLY_RECOMMENDATION_DIAGNOSTICS.md`
- `outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv`
- `outputs/audits/goal08b_recommendation_diagnostics_report.md`
- `outputs/audits/goal08b_recommendation_diagnostics_manifest.json`
- `outputs/audits/goal08b_recommendation_diagnostics_audit.md`

GOAL-08B consumes prior GOAL-07B risk overlay diagnostics, GOAL-08A
design-only contract evidence, GOAL-STORAGE-01 infrastructure evidence, and
GOAL-08B.0 unlock evidence. Its output grain is `trade_date + symbol`;
`actionability_status` is always `never_actionable`, and
`actionability_blocked` is always `true`. It generates no actionable
recommendation rows, buy/sell/hold outputs, target prices, expected returns for
action, position sizing, portfolio weights, dashboards, trading paths,
production behavior, backtests, factor-mining outputs, local lake files, broker
outputs, or DQN/RL outputs.

GOAL-09.0 writes only unlock-governance evidence:

- `configs/position/goal090_position_band_review_only_unlock_policy.yaml`
- `docs/position/GOAL090_POSITION_BAND_REVIEW_ONLY_UNLOCK_GATE.md`
- `outputs/audits/goal090_position_band_review_only_unlock_report.md`
- `outputs/audits/goal090_position_band_review_only_unlock_manifest.json`
- `outputs/audits/goal090_position_band_review_only_unlock_audit.md`

GOAL-09.0 uses prior PASS/PASS_WITH_WARNINGS review-only, design-only, and
infrastructure-only evidence only. It generated no position-band diagnostic
rows, position rows, position sizing, portfolio weights, buy/sell/hold outputs,
target prices, expected returns for action, dashboards, trading paths,
production behavior, backtests, factor-mining outputs, local lake files, broker
outputs, or DQN/RL outputs. It does not implement GOAL-09 by itself.

GOAL-09 writes only non-actionable position-band diagnostic evidence:

- `configs/position/goal09_review_only_position_band_diagnostics_policy.yaml`
- `docs/position/GOAL09_REVIEW_ONLY_POSITION_BAND_DIAGNOSTICS.md`
- `outputs/position/goal09_review_only_position_band_diagnostics.csv`
- `outputs/audits/goal09_position_band_diagnostics_report.md`
- `outputs/audits/goal09_position_band_diagnostics_manifest.json`
- `outputs/audits/goal09_position_band_diagnostics_audit.md`

GOAL-09 consumes prior GOAL-08B non-actionable recommendation diagnostics and
GOAL-07B risk overlay diagnostics only. Its position-band diagnostic rows are
review-only, non-actionable, and not position recommendations. It creates no
actual position rows, position sizing, portfolio weights, target weights, order
quantities, buy/sell/hold outputs, target prices, expected returns for action,
dashboards, trading paths, production behavior, backtests, factor-mining
outputs, local lake files, broker outputs, or DQN/RL outputs.

GOAL-09.1 writes only warning-review and dashboard-readiness evidence:

- `configs/dashboard/goal091_dashboard_readiness_warning_policy.yaml`
- `docs/dashboard/GOAL091_POSITION_BAND_WARNING_REVIEW_AND_DASHBOARD_READINESS.md`
- `outputs/audits/goal091_dashboard_readiness_report.md`
- `outputs/audits/goal091_dashboard_readiness_manifest.json`
- `outputs/audits/goal091_dashboard_readiness_audit.md`

GOAL-09.1 classifies the remaining GOAL-09 warnings into
`dashboard_blocking_banner`, `provider_concentration_banner`, and
`row_level_and_summary_warning` groups. It defines that future dashboard
contracts must preserve `review_only`, `never_actionable`, and non-actionable
disclaimers, must show all propagated warnings, and must not display ranked
Top-N, buy-candidate, position-candidate, or action-oriented fields. It does
not create `outputs/dashboard`, dashboard files, new recommendation rows, new
position rows, position sizing, weights, orders, trading paths, production
behavior, backtests, factor-mining outputs, local lake files, broker outputs,
or DQN/RL outputs.

GOAL-V1-INTEGRITY-01 writes only artifact-lineage and structure evidence:

- `configs/validation/goal_v1_integrity01_artifact_lineage_contract.yaml`
- `docs/validation/GOAL_V1_INTEGRITY01_ARTIFACT_LINEAGE_STRUCTURE_GATE.md`
- `outputs/audits/goal_v1_integrity01_artifact_lineage_structure_report.md`
- `outputs/audits/goal_v1_integrity01_artifact_lineage_structure_manifest.json`
- `outputs/audits/goal_v1_integrity01_artifact_lineage_structure_audit.md`

GOAL-V1-INTEGRITY-01 verifies only prior GOAL-07B, GOAL-08B, GOAL-09, and
GOAL-09.1 PASS/PASS_WITH_WARNINGS evidence, confirms canonical row lineage and
non-actionability, and records that future dashboard contracts may read only
canonical diagnostics and audit metadata. It creates no dashboard output, HTML,
Streamlit, frontend code, visual reports, new risk rows, new recommendation
rows, new position rows, local lake files, trading paths, production behavior,
backtests, factor-mining outputs, broker outputs, or DQN/RL outputs.

GOAL-10A writes only design-only future backtest contract evidence:

- `configs/backtest/goal10a_backtest_input_contract.yaml`
- `configs/backtest/goal10a_backtest_metric_contract.yaml`
- `configs/backtest/goal10a_backtest_grouping_contract.yaml`
- `configs/backtest/goal10a_execution_alignment_policy.yaml`
- `docs/backtest/GOAL10A_BACKTEST_CONTRACT_DESIGN_GATE.md`
- `outputs/audits/goal10a_backtest_contract_design_report.md`
- `outputs/audits/goal10a_backtest_contract_design_manifest.json`
- `outputs/audits/goal10a_backtest_contract_design_audit.md`

GOAL-10A defines future review-only backtest contracts from GOAL-08B
recommendation diagnostics and GOAL-09 position-band diagnostics only. It does
not fetch prices, expand the data panel, run a backtest, create performance
rows, create equity curves, create portfolio returns, create cost/slippage
outputs, generate actionable recommendations, create position sizing, create
dashboard files, write local lake data, write trading or production data,
activate factor mining, integrate a broker, or create DQN/RL outputs.

GOAL-10B writes only review-only recommendation diagnostics backtest evidence:

- `outputs/backtest/goal10b_recommendation_backtest_input_snapshot.csv`
- `outputs/backtest/goal10b_recommendation_group_metrics.csv`
- `outputs/backtest/goal10b_risk_severity_group_metrics.csv`
- `outputs/backtest/goal10b_warning_group_metrics.csv`
- `outputs/backtest/goal10b_ic_rank_ic_summary.csv`
- `docs/backtest/GOAL10B_RECOMMENDATION_BACKTEST_REVIEW_ONLY.md`
- `outputs/audits/goal10b_recommendation_backtest_report.md`
- `outputs/audits/goal10b_recommendation_backtest_manifest.json`
- `outputs/audits/goal10b_recommendation_backtest_audit.md`

GOAL-10B uses existing committed label evidence only. It does not fetch data,
expand the panel, overwrite GOAL-07B/08B/09 diagnostics, make upstream rows
actionable, create portfolio returns or equity curves, run portfolio
construction, create dashboards, write local lake/trading/production data,
activate factor mining, integrate a broker, or create DQN/RL outputs.

GOAL-10B.1 writes only review-only coverage repair diagnostic evidence:

- `outputs/backtest/goal10b1_coverage_repair_diagnostic_summary.csv`
- `outputs/backtest/goal10b1_recommendation_distribution_audit.csv`
- `outputs/backtest/goal10b1_label_source_coverage_audit.csv`
- `docs/backtest/GOAL10B1_BACKTEST_COVERAGE_REPAIR_GATE.md`
- `outputs/audits/goal10b1_backtest_coverage_repair_report.md`
- `outputs/audits/goal10b1_backtest_coverage_repair_manifest.json`
- `outputs/audits/goal10b1_backtest_coverage_repair_audit.md`

GOAL-10B.1 uses existing committed artifacts only. It does not fetch data,
expand the panel, alter provider behavior, create new GOAL-08B/GOAL-09 rows,
write repaired snapshots or repaired metrics when repair is unsupported, create
portfolio returns or equity curves, create dashboards, write local
lake/trading/production data, activate factor mining, integrate a broker, or
create DQN/RL outputs.

GOAL-DATA-LABEL-01 writes only review-only forward-return label coverage
evidence:

- `outputs/labels/goal_data_label01_forward_return_label_coverage_sample.csv`
- `outputs/labels/goal_data_label01_forward_return_label_coverage_summary.csv`
- `docs/labels/GOAL_DATA_LABEL01_FORWARD_RETURN_LABEL_COVERAGE_EXPANSION.md`
- `outputs/audits/goal_data_label01_forward_return_label_coverage_report.md`
- `outputs/audits/goal_data_label01_forward_return_label_coverage_manifest.json`
- `outputs/audits/goal_data_label01_forward_return_label_coverage_audit.md`

GOAL-DATA-LABEL-01 uses existing committed OHLCV and benchmark samples only. It
does not fetch data, expand the provider panel, create or overwrite
GOAL-07B/GOAL-08B/GOAL-09 diagnostics, run backtests, create performance rows,
create portfolio returns or equity curves, create dashboards, write local
lake/trading/production data, activate factor mining, integrate a broker, or
create DQN/RL outputs.

GOAL-V1-DIAGNOSTIC-COVERAGE-02 writes only review-only multi-symbol diagnostic
coverage evidence:

- `outputs/diagnostics/goal_v1_diagnostic_coverage02_risk_diagnostics.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage02_recommendation_diagnostics.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage02_position_band_diagnostics.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage02_coverage_summary.csv`
- `docs/diagnostics/GOAL_V1_DIAGNOSTIC_COVERAGE02_MULTI_SYMBOL_DIAGNOSTICS_EXPANSION.md`
- `outputs/audits/goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_report.md`
- `outputs/audits/goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_manifest.json`
- `outputs/audits/goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_audit.md`

GOAL-V1-DIAGNOSTIC-COVERAGE-02 uses existing committed Stage 6C approved-symbol
evidence only. It does not overwrite canonical GOAL-07B/GOAL-08B/GOAL-09
diagnostics, run backtests, create performance rows, create portfolio returns
or equity curves, create dashboards, write local lake/trading/production data,
activate factor mining, integrate a broker, or create DQN/RL outputs.

## Current Evidence Chain

The protected regenerated outputs live under:

- `outputs/audits/`
- `outputs/features/`
- `outputs/labels/`
- `outputs/datasets/`
- `outputs/stage6a/`
- `outputs/stage6b/`
- `outputs/stage6c/`
- `outputs/backtest/`
- `outputs/models/goal06b/`
- `outputs/models/goal06d/`
- `outputs/models/goal06d1/`
- `configs/risk/`
- `configs/recommendation/`
- `configs/position/`
- `configs/storage/`
- `configs/validation/`
- `configs/backtest/`
- `docs/risk/`
- `docs/recommendation/`
- `docs/storage/`
- `docs/validation/`
- `docs/backtest/`
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
GOAL-07A.1, GOAL-07B.0, GOAL-07B, GOAL-08B.0, GOAL-08B, GOAL-09.0,
GOAL-09, GOAL-09.1, GOAL-10B, GOAL-10B.1, GOAL-DATA-LABEL-01,
GOAL-V1-DIAGNOSTIC-COVERAGE-02, GOAL-10B.2, GOAL-10C,
GOAL-DATA-PROVIDER-02A, GOAL-DATA-PROVIDER-02A.1,
GOAL-DATA-PROVIDER-02B, and GOAL-V1-DIAGNOSTIC-COVERAGE-03 are
`implemented_review_only`; GOAL-07A, GOAL-08A, and
GOAL-10A are `implemented_design_only`; GOAL-STORAGE-01 and
GOAL-V1-INTEGRITY-01 are
`implemented_infrastructure_only`. GOAL-07B is
diagnostic-only and non-actionable. GOAL-08A is names-only design evidence with
zero recommendation rows. STORAGE-01 hardens storage only and does not unlock
GOAL-08B by itself. GOAL-08B is non-actionable diagnostic-only evidence.
GOAL-09.0 is unlock-only evidence. GOAL-09 is non-actionable review-only
position-band diagnostics only. GOAL-09.1 is warning-review/dashboard-readiness
evidence only. GOAL-V1-INTEGRITY-01 is artifact-lineage/structure evidence only;
GOAL-10A is future backtest contract design evidence only; GOAL-10B is
non-actionable review-only recommendation diagnostics backtest evidence only;
GOAL-10B.1 is coverage repair diagnostics only; GOAL-DATA-LABEL-01 is label
coverage evidence only; GOAL-V1-DIAGNOSTIC-COVERAGE-02 is non-actionable
multi-symbol diagnostic coverage only; GOAL-10B.2 is non-actionable
recommendation revalidation diagnostics only; GOAL-10C is non-actionable
position-band cost/slippage sensitivity diagnostics only; GOAL-DATA-PROVIDER-02A
is provider capability metadata only and does not build a panel;
GOAL-DATA-PROVIDER-02A.1 is opt-in provider smoke-test metadata only and does
not build a panel; GOAL-DATA-PROVIDER-02B is bounded source-backed evaluation
panel evidence only; GOAL-V1-DIAGNOSTIC-COVERAGE-03 is non-actionable
source-backed diagnostic coverage only; GOAL-10B.3 is non-actionable DC03
recommendation revalidation diagnostics only and does not unlock position
validation, dashboards, or execution; GOAL-DATA-PANEL-02 and GOAL-10D remain
`locked_future`. Dashboard / Daily Report UI
remains `locked_future`. Actionable recommendation, actual position, dashboard, trading, production, V2
factor-mining, and DQN/RL paths remain locked or deleted from active mainline.

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

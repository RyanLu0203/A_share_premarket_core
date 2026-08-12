# Roadmap

## 2026-08-12 iFinD accepted S0 and dual identity checkpoint

S0 is complete: 7/7 services and 35/35 tools in the active personal/trial
entitlement passed live schema validation. The full reviewed 36-tool catalog is
retained; enterprise-only `edb:search_edb` is unavailable by plan. Earlier S1
scope, supplier-column and query-contract failures were repaired fail-closed.
After PR #49 merged, one bounded run called Luxshare and Hengtong exactly once
each with no retry. Both identity rows passed symbol scope, configured company
identity and response-schema checks. S1 overall remains
`BLOCKED / NOT_CANONICAL` because the summary has no auditable provider
`available_at`. The next step is an offline temporal-contract decision, not an
additional paid-data call. S2-S4 and all research promotion remain locked.

## 2026-08-09 iFinD Data and Workspace Foundation

The purchased provider is Tonghuashun iFinD **AI Financial Data Service**.
The purchased access mode is **MCP/API Key**. This checkpoint adds an
offline-first, Keychain-safe Streamable HTTP client for seven services and 36
reviewed supplier tools, preserves QuantAPI HTTPS as an optional second
channel, defines a seven-module data contract, canonical normalization/PIT
validation, immutable external bundle rules, and sanitized MCP readiness on
the existing Data Quality and Provider Health pages. It does not claim live
entitlement, schema, coverage, or data acceptance and does not start new factor
research.

Delivery order from this checkpoint:

1. Preserve the accepted S0 baseline: seven services, 35/35 active entitled
   tools/schemas and zero S0 data calls; keep the old exposed value forbidden.
2. Treat enterprise-only `edb:search_edb` as unavailable by plan while
   retaining it in the 36-tool reviewed supplier catalog.
3. Preserve the verified S1 identity/scope/schema result for exactly
   `002475.SZ` and `600487.SH`: two calls, no retry and no canonical rows.
4. Review whether identity-only acceptance metadata may use local
   `observed_at` while explicitly leaving provider `available_at` unknown. Do
   not weaken PIT requirements for market, fundamental or event data.
5. Run S2 only after the S1 temporal-contract decision: security master and
   bounded 120-day market evidence. Luxshare already has 120 Provider02B
   dates; Hengtong remains
   identity-only until accepted iFinD evidence exists.
6. Run S3 for audited fundamentals, ownership, risk, events and ESG fields,
   normalizing immutable checksummed bundles below the external data root.
7. Keep S4 market context and all research promotion locked until calendar,
   PIT/revision, missingness, units, adjustment, coverage and cross-provider
   reconciliation pass. Never substitute fabricated values for a failed gate.

Repository publishing order:

1. Review and merge this branch into `project-current`.
2. Change the GitHub default branch from stale `main` to `project-current`.
3. Keep `main` read-only or retire it through a separately approved repository
   governance change; do not maintain a second independent landing page.

Recommendation tiering, target prices, actionable positions, portfolio
weights, orders, broker integration, production writes, and live trading stay
locked regardless of provider availability.

The existing Issue #24 Workspace is not a GOAL-DASHBOARD-00 promotion. Generic
Dashboard / Daily Report UI remains `locked_future`; any future
GOAL-DASHBOARD-00 design/contract gate requires a separate explicit decision.

## 2026-07-17 GOAL-11 Checkpoint

`GOAL-11-QUANT-INTELLIGENCE-FOUNDATION` is implemented research-only as a
reproducible point-in-time feature, scoring, linear-baseline, evaluation, and
risk-adjustment layer. It consumes only governed snapshots and keeps generated
research evidence under ignored `outputs/local`.

The checkpoint does not promote a factor, recommendation, position, order,
broker, paper/live trading, or production path. `ready_factor_count` remains
zero; the existing workspace/API surface and all production locks stay exact.

## 2026-07-10 Issue #24 Checkpoint

`GOAL-PREMARKET-RESEARCH-AND-POSITION-WORKSPACE-DASHBOARD-01` is implemented
research-only on top of the merged operational position-management goal. The
checkpoint includes 23 pages, 22 GET-only API routes, immutable replay,
fail-closed live freshness, portfolio/risk/constraint/abstention views,
provider and provenance diagnostics, and explicitly locked quant surfaces.

The named workspace is not a generic downstream promotion. The generic
`dashboard` capability remains `false` and `dashboard_daily_report` remains
`locked_future`. Recommendation Tiering can proceed only under its own future
explicit authorization and scientifically ready factor evidence.

## Current Checkpoint

- GOAL-REPOSITORY-CHECKPOINT-01 Arch03 stable snapshot is the stable rollback
  checkpoint, not the current working HEAD.
- Stable commit: `310559ae18bbf203e795c1d66bc7181a6b11c14a`.
- Authoritative entrypoint branch: `project-current`.
- Frozen checkpoint branch: `checkpoint/arch03-stable-310559`.
- Annotated checkpoint tag: `checkpoint-arch03-stable-310559`.
- User-private local bundle backup exists outside GitHub; it is not a Codex
  Max dependency.

Current path:

1. DataExpansion01 → Regime02 → Quant04 is implemented research-only and
   records `ready_factor_count = 0`.
2. The named Issue #24 Workspace is a read-only research interface and GOAL-11
   is implemented research-only; Daily Refresh is the separate governed
   operational path.
3. Resolve external iFinD MCP authentication, then complete S0-S3 entitlement,
   schema, PIT and data acceptance plus the existing Workspace read models.
4. Resume research only over accepted versioned snapshots.
5. Rec Tiering remains conditional on `ready_factor_count > 0` and explicit
   user approval.

Generic Dashboard promotion, trading, broker, production, portfolio backtest,
factor-mining, and DQN/RL remain locked.

## Codex Operating System Path

- Current checkpoint node: GOAL-REPOSITORY-CHECKPOINT-01 at stable rollback
  commit `310559ae18bbf203e795c1d66bc7181a6b11c14a`.
- Immediate next goal: `GOAL-CODEX-OPERATING-SYSTEM-01`.
- First Codex Max smoke goal:
  `GOAL-CODEX-MAX-ONBOARDING-SMOKE-01-REMOTE-WINDOWS-GITHUB-ONLY-COMPLIANCE-GATE`.
- Next data goal: review the S1 identity-only `observed_at`/`available_at`
  contract offline; S2-S3 remain blocked until that decision is explicit.
- Next research goal: GOAL-11/alpha research over accepted versioned iFinD
  snapshots only; DataExpansion01, Regime02, and Quant04 are already complete.
- Rec Tiering unlock condition: `ready_factor_count > 0` and explicit user
  approval.
- Dashboard unlock condition: explicit user approval for a future dashboard
  design/contract gate.
- Trading, broker, and production remain locked.
- Rollback reference: branch `checkpoint/arch03-stable-310559`, tag
  `checkpoint-arch03-stable-310559`.
- Local bundle backup is a user-private rollback backup only, not a Codex Max
  dependency.

## Implemented Active

- Project operating system.
- Universe and symbol governance.
- Trading calendar.
- Source health and context contracts.
- PIT signal snapshot.
- Label snapshot and benchmark contract.
- Feature-label merge and leakage audit.
- Stage 6A repair panel.
- GOAL-06A baseline scoring skeleton.
- GOAL-06B review-only supervised baseline training gate.
- GOAL-06C review-only expanded validation and ranking baseline gate.
- GOAL-06C.5 engineering data coverage, local storage, data bundle, and panel
  expansion gate.
- GOAL-06C.6 source-backed AKShare/provider engineering pilot bundle ingestion
  gate, network-disabled by default.
- GOAL-06C.6A scoped finance network isolation and provider failure taxonomy
  gate; network failures are classified by specific subtype.
- GOAL-06C.6A CloakBrowser reference probe for opt-in, sanitized, tag-only
  provider-access diagnostics.
- GOAL-06C.7 provider ladder engineering data base expansion gate with
  optional browser-assisted ingestion disabled by default.
- GOAL-06D review-only model comparison/calibration/stability/governance gate
  (`PASS_WITH_WARNINGS`; weak selected baseline
  `score_based_alpha_ranking`).
- GOAL-06D.1 review-only calibration/stability warning repair gate
  (`PASS_WITH_WARNINGS`; weak repaired score baseline bounded and documented).
- GOAL-07A risk overlay design-only governance gate (`PASS_WITH_WARNINGS`;
  no risk calculation, recommendation, position, dashboard, trading,
  production, factor-mining, or DQN/RL output).
- GOAL-07A.1 risk overlay design review unlock-readiness gate
  (`PASS_WITH_WARNINGS`; GOAL-07B ready for explicit review-only unlock).
- GOAL-07B.0 risk overlay review-only unlock gate (`PASS_WITH_WARNINGS`;
  preserves GOAL-07B eligibility and remains unlock-only).
- GOAL-07B risk overlay calculation prototype (`PASS_WITH_WARNINGS`;
  implemented_review_only non-actionable diagnostics at `trade_date + symbol`
  grain).
- GOAL-08A recommendation contract design gate (`PASS`; implemented_design_only
  names-only future schema, warning propagation, HIGH-risk actionability block,
  and zero recommendation rows).
- GOAL-STORAGE-01 local research lake hardening gate (`PASS`;
  implemented_infrastructure_only storage governance and GitHub hygiene only).
- GOAL-08B.0 recommendation review-only unlock gate (`PASS_WITH_WARNINGS`;
  implemented_review_only unlock-only evidence, no recommendation diagnostics
  rows created by that gate).
- GOAL-08B non-actionable recommendation diagnostics prototype
  (`PASS_WITH_WARNINGS`; implemented_review_only diagnostics at
  `trade_date + symbol` grain).
- GOAL-09.0 position-band review-only unlock gate (`PASS_WITH_WARNINGS`;
  implemented_review_only unlock-only evidence, no position-band rows).
- GOAL-09 position-band diagnostics prototype (`PASS_WITH_WARNINGS`;
  implemented_review_only non-actionable diagnostics at `trade_date + symbol`
  grain).
- GOAL-09.1 position-band warning review and dashboard-readiness gate
  (`PASS_WITH_WARNINGS`; implemented_review_only warning classification and
  future dashboard contract constraints only, no dashboard outputs).
- GOAL-V1-INTEGRITY-01 artifact-lineage and structure gate
  (`PASS_WITH_WARNINGS`; implemented_infrastructure_only canonical V1 chain
  integrity only, no dashboard or new diagnostic rows).
- GOAL-10A backtest contract design gate (`PASS_WITH_WARNINGS`;
  implemented_design_only future review-only validation contract only, no
  backtest execution or performance rows).
- GOAL-10B recommendation diagnostics backtest review-only prototype
  (`PASS_WITH_WARNINGS`; implemented_review_only non-actionable grouped
  forward-return diagnostics and IC/RankIC availability evidence only).
- GOAL-10B.1 backtest coverage and group-variation repair gate
  (`PASS_WITH_WARNINGS`; implemented_review_only coverage diagnostics over
  existing artifacts only; repair not possible with current artifacts).
- GOAL-DATA-LABEL-01 forward-return label coverage expansion
  (`PASS_WITH_WARNINGS`; implemented_review_only label coverage from committed
  OHLCV and benchmark samples only; no diagnostics or backtests).
- GOAL-V1-DIAGNOSTIC-COVERAGE-02 multi-symbol diagnostics expansion
  (`PASS_WITH_WARNINGS`; implemented_review_only non-actionable diagnostic
  coverage rows from committed Stage 6C evidence only).
- GOAL-10B.2 recommendation backtest revalidation (`PASS_WITH_WARNINGS`;
  implemented_review_only bounded non-actionable revalidation diagnostics).
- GOAL-10C cost/slippage sensitivity (`PASS_WITH_WARNINGS`;
  implemented_review_only row-level non-actionable position-band sensitivity).
- GOAL-DATA-PROVIDER-02A multi-provider capability probe
  (`PASS_WITH_WARNINGS`; implemented_review_only provider capability metadata
  only; no panel build).
- GOAL-DATA-PROVIDER-02A.1 network opt-in provider smoke test
  (`PASS_WITH_WARNINGS`; implemented_review_only opt-in smoke-test metadata
  only; no panel build).
- GOAL-DATA-PROVIDER-02B source-backed evaluation panel build
  (`PASS_WITH_WARNINGS`; implemented_review_only bounded source-backed panel
  evidence only; no diagnostics or backtests).
- GOAL-V1-DIAGNOSTIC-COVERAGE-03 source-backed multi-symbol diagnostics
  (`PASS_WITH_WARNINGS`; implemented_review_only non-actionable risk,
  recommendation eligibility, and position-band diagnostics from 02B panel
  evidence only).
- GOAL-10B.3 DC03 recommendation revalidation (`PASS_WITH_WARNINGS`;
  implemented_review_only non-actionable revalidation diagnostics from DC03
  plus Provider02B evidence only; signal currently weak/unreliable due group
  imbalance and unavailable numeric-score IC/RankIC).
- GOAL-RISK-TIERING-01 risk severity numeric score tiering
  (`PASS_WITH_WARNINGS`; implemented_review_only separate non-actionable
  risk-tier diagnostics from DC03 plus Provider02B evidence only; future
  returns excluded from score construction).
- GOAL-RISK-TIERING-01.1 downside risk repair
  (`PASS_WITH_WARNINGS`; implemented_review_only separate non-actionable
  downside-risk diagnostics from GOAL-RISK-TIERING-01 plus DC03/Provider02B
  evidence only; volatility/momentum separated and future returns excluded
  from score construction).
- GOAL-QUANT-RESEARCH-01 factor research lab and score validity gate
  (`PASS_WITH_WARNINGS`; implemented_research_only factor registry,
  evaluation-panel, IC/RankIC, monotonicity, stability, trial-registry, and
  score-validity diagnostics from committed evidence only; no factor ready for
  recommendation tiering).
- GOAL-MVP-01 premarket research diagnostic terminal
  (`PASS_WITH_WARNINGS`; implemented_mvp_research_only committed-evidence
  replay report, symbol diagnostic table, review queues, factor-validity
  summary, and market-context summary only; no actionable outputs or UI).
- GOAL-ALPHA-FACTOR-CANDIDATE-01 alpha factor candidate construction
  (`PASS_WITH_WARNINGS`; implemented_research_only candidate registry,
  normalized candidate panel, coverage summary, and construction warnings from
  committed evidence only; no predictive-validity evaluation, recommendation,
  position, portfolio, dashboard, trading, production, local-lake,
  factor-mining, broker, or DQN/RL outputs).
- GOAL-QUANT-RESEARCH-02 alpha-candidate factor validity evaluation
  (`PASS_WITH_WARNINGS`; implemented_research_only 78,000-row alpha evaluation
  panel, coverage, bucket metrics, IC/RankIC, monotonicity, rolling stability,
  horizon consistency, score-validity classification, and trial registry from
  committed evidence only; ready factor count 0).
- GOAL-ALPHA-RESEARCH-REFINEMENT-01 rolling stability and candidate refinement
  (`PASS_WITH_WARNINGS`; implemented_research_only instability attribution,
  conditional stability slicing, refined candidate design definitions,
  intraday redefinition plan, and trial-registry update from committed evidence
  only; no refined factor panel or predictive-validity claim).
- GOAL-ALPHA-FACTOR-CANDIDATE-02 refined alpha candidate construction
  (`PASS_WITH_WARNINGS`; implemented_research_only 30 refined candidates and
  180000 refined panel rows from committed evidence only; no predictive
  validity evaluation or downstream promotion).
- GOAL-QUANT-RESEARCH-03 refined alpha factor validity evaluation
  (`PASS_WITH_WARNINGS`; implemented_research_only 30 refined factors over
  committed evidence; ready factor count 0 and no recommendation-tiering
  promotion).
- GOAL-REGIME-LABEL-RESEARCH-01 market regime label construction
  (`PASS_WITH_WARNINGS`; implemented_research_only date-level regime labels,
  symbol-level regime context, and factor-regime bridge from committed
  evidence only; no market timing, recommendations, positions, backtests, UI,
  trading, production, local-lake, factor-mining, broker, or DQN/RL outputs).
- GOAL-ARCHITECTURE-REFACTOR-03 AKShare source catalog and provider
  modularization (`PASS_WITH_WARNINGS`;
  implemented_engineering_research_support provider/source catalog, registry,
  inventory, common helper, docs, manifest, and audit artifacts only).
- Verification, validation, regression, safety, adapter, and diagnostics gates.
- GOAL-HYGIENE-01 deterministic runtime artifact policy.
- GOAL-DOCS-01 canonical workflow status governance.

## Next Allowed Work

GOAL-07A has implemented the risk overlay blueprint only as design governance.
GOAL-07A.1 completed the GOAL-07B unlock-readiness design review, and
GOAL-07B.0 completed the explicit review-only unlock gate. GOAL-07B now
implements a deterministic review-only risk overlay calculation prototype.
GOAL-08A now implements only a design-only future recommendation contract gate.
GOAL-STORAGE-01 now implements only an infrastructure hardening gate for the
local research lake contract and does not unlock GOAL-08B by itself.
GOAL-08B.0 completed the explicit review-only unlock gate. GOAL-08B now
implements only a deterministic non-actionable recommendation diagnostics
prototype with 100 `trade_date + symbol` rows. GOAL-09.0 completed the
explicit position-band review-only unlock gate. GOAL-09 now implements only a
deterministic non-actionable position-band diagnostics prototype at
`trade_date + symbol` grain. GOAL-09.1 now implements only warning
classification and dashboard-readiness evidence. GOAL-V1-INTEGRITY-01 now
implements only artifact-lineage and structure integrity over GOAL-07B,
GOAL-08B, GOAL-09, and GOAL-09.1 evidence. GOAL-10A now implements only a
design-only future backtest contract gate from GOAL-08B and GOAL-09
diagnostics; it defines input, date alignment, T+1/no-lookahead, metrics,
grouping, benchmark, cost/slippage, and tradability rules but runs no backtest.
GOAL-10B now implements only a deterministic review-only recommendation
diagnostics backtest over GOAL-08B rows and existing PIT-safe forward-return
labels. It writes grouped diagnostics and IC/RankIC availability evidence only;
GOAL-10B.1 now implements only review-only coverage repair diagnostics over
current artifacts, records `coverage_repair_not_possible_with_current_artifacts`,
and writes no repaired rows or metrics. GOAL-DATA-LABEL-01 now implements only
review-only forward-return label coverage expansion from committed samples; it
writes 100 label rows, 80 with 20d labels, but current GOAL-08B/GOAL-09
diagnostics are not yet aligned to those labels. GOAL-V1-DIAGNOSTIC-COVERAGE-02
now implements only review-only multi-symbol diagnostic coverage from committed
Stage 6C approved-symbol evidence; it writes 8 non-actionable diagnostic rows
per family and keeps canonical GOAL-07B/08B/09 artifacts unchanged. GOAL-10B.2
now implements only review-only recommendation backtest revalidation over DC02
rows, and GOAL-10C now implements only review-only row-level position-band
cost/slippage sensitivity. GOAL-DATA-PROVIDER-02A now implements only a
review-only multi-provider capability probe over Tushare Pro, Baostock,
AkShare, efinance, qstock, yfinance auxiliary, and local import fallback; it
writes provider metadata only and does not build an evaluation panel.
GOAL-DATA-PROVIDER-02A.1 now implements only a review-only network-opt-in
provider smoke test; it attempts live access only with explicit environment
opt-ins, persists no provider token or raw payload, and does not build an
evaluation panel.
GOAL-DATA-PROVIDER-02B now implements only a review-only source-backed
evaluation panel build gate; it writes bounded normalized panel evidence and
provider/coverage audit metadata, but does not create diagnostics, backtests,
dashboards, trading, production, local-lake, broker, factor-mining, or DQN/RL
outputs. GOAL-V1-DIAGNOSTIC-COVERAGE-03 now implements only review-only
source-backed diagnostic coverage over the 02B panel; it writes separate
non-actionable risk, recommendation eligibility, and position-band diagnostics
and preserves canonical GOAL-07B/08B/09 artifacts. GOAL-10B.3 now implements
only review-only DC03 recommendation revalidation diagnostics and records
`recommendation_revalidation_signal_weak_or_unreliable`; GOAL-RISK-TIERING-01
now implements only separate non-actionable numeric risk tiering diagnostics,
records `risk_tiering_signal_weak_or_unreliable`; GOAL-RISK-TIERING-01.1 now
implements only separate non-actionable downside-risk repair diagnostics,
records `downside_risk_tiering_signal_weak_or_unreliable`, and leaves
GOAL-REC-TIERING-01 for a future explicit gate before GOAL-10B.4 or any
position-band validation. GOAL-QUANT-RESEARCH-01 now implements only a
research-only factor lab over committed Provider02B, DC03, GOAL-10B.3,
GOAL-RISK-TIERING-01, and GOAL-RISK-TIERING-01.1 evidence. GOAL-MVP-01 now
implements only a research-only premarket diagnostic terminal from committed
evidence replay. GOAL-ALPHA-FACTOR-CANDIDATE-01 now implements only
research-only candidate alpha construction from committed Provider02B, MVP,
Quant Research, and risk-tiering evidence. GOAL-QUANT-RESEARCH-02 now
implements only research-only alpha candidate validity evaluation from
committed evidence, finds ready factor count 0, and recommends
GOAL-ALPHA-FACTOR-CANDIDATE-02 or GOAL-ALPHA-RESEARCH-REFINEMENT-01 before
recommendation tiering. GOAL-ALPHA-RESEARCH-REFINEMENT-01 now implements only
research-only rolling-stability attribution and refined candidate design
planning from committed evidence, diagnoses 6 promising candidates, writes 30
refined design rows, and leaves every design not evaluated and not accepted
downstream. GOAL-ALPHA-FACTOR-CANDIDATE-02 now implements only research-only
refined alpha candidate construction from committed evidence, writes 30
refined candidates and 180000 refined panel rows, and leaves every downstream
acceptance flag false. GOAL-QUANT-RESEARCH-03 now implements only
research-only refined alpha factor validity evaluation from committed evidence,
evaluates 30 refined factors over partitioned rows, records ready factor count
0 with partial improvement available, and leaves every downstream acceptance
flag false. GOAL-REGIME-LABEL-RESEARCH-01 now implements only research-only
market regime label construction from committed Provider02B, Quant03,
Candidate02, MVP, and risk-tiering evidence; it writes date, symbol, and
factor-regime bridge context only and excludes future returns and post-hoc
factor performance from construction. GOAL-ARCHITECTURE-REFACTOR-03 now
implements only engineering research-support provider catalog and
modularization metadata. DataExpansion01, Regime02, and Quant04 subsequently
implemented research-only without producing a ready factor.
GOAL-REC-TIERING-01, GOAL-10B.4, GOAL-POSITION-BAND-VALIDATION-01,
GOAL-DATA-PANEL-02, and GOAL-10D remain locked. The named Issue #24 read-only
Workspace is implemented, while generic Dashboard / Daily Report promotion
remains `locked_future`.
No actionable recommendation execution, actual position output, generic dashboard promotion,
paper/live trading, production DB writes, production model promotion, backtest
execution, backtest rows, factor mining, broker, local lake, or DQN/RL is
unlocked.

V2 factor research is planned but inactive. It remains `planned_locked` until a
future explicit V2 goal; no factor mining, IC/RankIC mining, factor library
generation, or factor integration is active in V1.

Future goals must also update `configs/project/workflow_status.csv` and the
workflow diagrams before any future block is promoted.

## Locked Future

- Actual position recommendations, position sizing, target weights,
  order quantities, portfolio-weight output, and capital allocation.
- GOAL-DATA-PANEL-02 evaluation panel build.
- GOAL-REC-TIERING-01 recommendation score tiering.
- GOAL-10B.4 recommendation revalidation after tiering.
- GOAL-POSITION-BAND-VALIDATION-01 position-band validation.
- GOAL-10D failure attribution.
- Signal and portfolio backtests.
- Cost/slippage sensitivity execution.
- Paper trading journal.
- Failure attribution.
- Dashboard / daily report.
- Production hardening.
- Broker/live trading.
- Production DB writes.
- DQN/RL optional research benchmark.
- V2 factor research upgrade (`planned_locked`; inactive in V1).

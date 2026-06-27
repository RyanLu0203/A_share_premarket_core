# Project State

Last updated: 2026-06-27

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
factor-mining output, or DQN/RL output. GOAL-DATA-PANEL-02,
GOAL-V1-DIAGNOSTIC-COVERAGE-03, GOAL-10B.3, GOAL-10D,
Dashboard / Daily Report UI, signal and portfolio backtest promotion,
paper/live trading, broker, production, local-lake, factor-mining, and DQN/RL
remain locked or deleted from active mainline.
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
GOAL-DATA-PANEL-02, GOAL-V1-DIAGNOSTIC-COVERAGE-03, GOAL-10B.3, GOAL-10D,
Dashboard / Daily Report UI, signal and portfolio backtest promotion,
paper/live trading, broker, production, local-lake, factor-mining, and DQN/RL
remain locked or deleted from active mainline.

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
- GOAL-DATA-PANEL-02 evaluation panel build
- GOAL-V1-DIAGNOSTIC-COVERAGE-03 multi-provider diagnostics
- GOAL-10B.3 recommendation revalidation
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
GOAL-V1-DIAGNOSTIC-COVERAGE-02, GOAL-10B.2, GOAL-10C, and
GOAL-DATA-PROVIDER-02A, and GOAL-DATA-PROVIDER-02A.1 are
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
panel evidence only and does not unlock diagnostics, backtests, dashboards, or
execution; GOAL-DATA-PANEL-02, GOAL-V1-DIAGNOSTIC-COVERAGE-03, GOAL-10B.3,
and GOAL-10D remain `locked_future`. Dashboard / Daily Report UI
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

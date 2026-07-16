# 02 Data Engine

The clean target workflow does not fetch provider payloads during validation. It
uses deterministic, sanitized contracts to preserve the active Class A behavior
needed through GOAL-06B.

GOAL-06C.5 adds a local research data-store contract and data coverage audit
layer without enabling network ingestion by default. GOAL-06C.6 adds optional
AKShare/source-backed ingestion, still disabled by default and guarded by
`ASHARE_ALLOW_NETWORK_INGESTION=1` or `--allow-network`. Heavy provider data,
raw payloads, local bundles, Parquet lake files, DuckDB/SQLite databases, logs,
and notebooks stay outside GitHub.

GOAL-STORAGE-01 hardens that storage boundary as an infrastructure-only gate.
Future heavy data writes must resolve from `ASHARE_PREMARKET_DATA_ROOT`; the
fallback path is documentation-only for this gate. The local research lake
contract defines `raw/`, `bundles/`, `lake/`, `metadata/`, `exports/`, and
`audit_samples/` boundaries plus bundle versioning, manifest, checksum, schema
registry, placement, and GitHub hygiene rules. It does not fetch data, expand
coverage, materialize a local lake, or unlock GOAL-08B by itself. GOAL-08B.0
uses STORAGE-01 only as prior infrastructure evidence for future-review-only
eligibility and still creates no local lake files. GOAL-08B writes only a small
committed non-actionable diagnostic CSV under `outputs/recommendation/`; it
does not write to `data/lake`, local bundles, raw payload roots, or production
storage. GOAL-09.0 writes only unlock-governance evidence under
`outputs/audits/` and `configs/position/`. GOAL-09 writes only a small
committed non-actionable position-band diagnostic CSV under `outputs/position/`;
it does not write actual position rows, local lake files, raw payload roots, or
production storage. GOAL-09.1 writes only dashboard-readiness warning policy,
documentation, manifest, report, and audit evidence under `configs/dashboard/`,
`docs/dashboard/`, and `outputs/audits/`; it does not create dashboard outputs,
HTML, Streamlit, frontend code, visual reports, new recommendation rows, new
position rows, local lake files, raw payload roots, or production storage.
GOAL-V1-INTEGRITY-01 writes only artifact-lineage structure contract,
documentation, manifest, report, and audit evidence under `configs/validation/`,
`docs/validation/`, and `outputs/audits/`; it does not create dashboard outputs,
new risk rows, new recommendation rows, new position rows, local lake files, raw
payload roots, cache inputs, notebooks, or production storage.
GOAL-10A writes only design-only future backtest contract evidence under
`configs/backtest/`, `docs/backtest/`, and `outputs/audits/`. It reads only
GOAL-08B recommendation diagnostics, GOAL-09 position-band diagnostics, and
GOAL-V1-INTEGRITY-01 audit metadata as prior evidence. It does not fetch prices,
expand the data panel, write local lake files, create backtest rows, create
equity curves, create portfolio returns, create dashboard outputs, or write
production storage.
GOAL-10B writes only small review-only recommendation diagnostic backtest
evidence under `outputs/backtest/`, `docs/backtest/`, and `outputs/audits/`.
It reads GOAL-08B diagnostics and existing PIT-safe label samples only. It does
not fetch data, expand the panel, write local lake files, create portfolio
returns, create equity curves, create dashboard outputs, or write production
storage.
GOAL-10B.1 writes only small review-only coverage repair diagnostic evidence
under `outputs/backtest/`, `docs/backtest/`, and `outputs/audits/`. It reads
existing GOAL-10B, GOAL-08B, label, and Stage6C artifacts only, records that
repair is not possible with current artifacts, and does not fetch data, expand
the panel, create repaired rows or metrics, write local lake files, create
portfolio returns, create equity curves, create dashboard outputs, or write
production storage.
GOAL-DATA-LABEL-01 writes only small review-only forward-return label coverage
evidence under `outputs/labels/`, `docs/labels/`, and `outputs/audits/`. It
reads existing committed OHLCV and benchmark samples only, adds 1d, 3d, 5d,
and 20d stock, benchmark, and excess-return label fields where future bars
exist, and does not fetch data, expand provider coverage, create or overwrite
GOAL-07B/GOAL-08B/GOAL-09 diagnostics, run backtests, write local lake files,
create portfolio returns, create equity curves, create dashboard outputs, or
write production storage.
GOAL-V1-DIAGNOSTIC-COVERAGE-02 writes only small review-only multi-symbol
diagnostic coverage evidence under `outputs/diagnostics/`, `docs/diagnostics/`,
and `outputs/audits/`. It reads existing committed Stage 6C approved-symbol
evidence only, creates separate non-actionable risk, recommendation, and
position-band diagnostic coverage rows, preserves canonical GOAL-07B/GOAL-08B/
GOAL-09 artifacts, and does not fetch data, run backtests, write local lake
files, create portfolio returns, create equity curves, create dashboard outputs,
or write production storage.
GOAL-DATA-PROVIDER-02A writes only review-only provider capability metadata
under `outputs/providers/`, `configs/providers/`, `docs/providers/`, and
`outputs/audits/`. It probes or records Tushare Pro, Baostock, AkShare,
efinance, qstock, yfinance auxiliary, and local import fallback readiness over
the current approved-symbol smoke universe and a 30-trading-day contract
window. Network provider calls remain disabled by default unless explicitly
enabled by policy; Tushare Pro requires an external `TUSHARE_TOKEN` and
explicit opt-in. Provider-02A does not expand the approved universe, fetch or
commit raw payloads, build a final evaluation panel, create diagnostics, run
backtests, write local lake files, create portfolio returns, create equity
curves, create dashboard outputs, or write production storage.
GOAL-DATA-PROVIDER-02A.1 writes only review-only network-opt-in provider
smoke-test metadata under the same provider/audit/doc/config boundaries. Live
provider access is attempted only when `ASHARE_ALLOW_NETWORK_INGESTION=1` is
present. Tushare Pro additionally requires `ASHARE_ALLOW_TUSHARE=1` and
`TUSHARE_TOKEN` read from the environment only. The gate records live-access
attempt flags, schema mapping status, and failure taxonomy; it never prints or
persists provider tokens, never commits raw provider payloads, and never treats
smoke-test rows as final evaluation panel evidence.
GOAL-DATA-PROVIDER-02B writes only review-only source-backed panel evidence
under `outputs/datasets/`, `outputs/diagnostics/`, `outputs/providers/`,
`configs/providers/`, `docs/providers/`, and `outputs/audits/`. It produces a
bounded normalized panel artifact for future review-only diagnostics planning,
plus coverage, provider usage, failure-taxonomy, report, manifest, and audit
metadata. It does not promote GOAL-DATA-PANEL-02, expand the approved trading
universe, run diagnostics, run backtests, write local lake files, create
portfolio returns, create equity curves, create dashboard outputs, persist raw
provider payloads or provider tokens, or write production storage.
GOAL-V1-DIAGNOSTIC-COVERAGE-03 writes only review-only source-backed
diagnostic coverage evidence under `outputs/diagnostics/`,
`configs/diagnostics/`, `docs/diagnostics/`, and `outputs/audits/`. It consumes
only the committed GOAL-DATA-PROVIDER-02B normalized panel, creates separate
non-actionable risk, recommendation eligibility, and position-band diagnostics
at `trade_date + symbol` grain, and preserves canonical GOAL-07B/08B/09
artifacts. It does not promote GOAL-DATA-PANEL-02, run portfolio backtests,
write local lake files, create portfolio returns, create equity curves, create
dashboard outputs, fetch new provider data, persist raw payloads or provider
tokens, or write production storage. GOAL-10B.3 consumes this DC03 evidence
only through its separate review-only recommendation revalidation gate.
GOAL-RISK-TIERING-01 writes only separate review-only risk severity numeric
score tiering diagnostics under `outputs/diagnostics/`, `outputs/backtest/`,
`configs/risk/`, `docs/risk/`, and `outputs/audits/`. It consumes committed
DC03 risk diagnostics, the GOAL-DATA-PROVIDER-02B source-backed panel, and
GOAL-10B.3 imbalance evidence only. It excludes future returns from score
construction, uses forward returns only for post-hoc group metrics, preserves
canonical GOAL-07B and DC03 risk artifacts, and does not fetch data, write
local lake files, create recommendation rows, position rows, portfolios,
dashboard outputs, trading paths, production storage, broker output,
factor-mining output, or DQN/RL output.
GOAL-RISK-TIERING-01.1 writes only separate review-only downside-risk repair
diagnostics under `outputs/diagnostics/`, `outputs/backtest/`, `configs/risk/`,
`docs/risk/`, and `outputs/audits/`. It consumes committed GOAL-RISK-TIERING-01,
DC03, and GOAL-DATA-PROVIDER-02B evidence only. It reconstructs deterministic
component contributions, separates volatility/momentum flags from downside
score construction, excludes future returns and label readiness fields from the
score, uses future returns only for post-hoc group metrics, preserves
GOAL-RISK-TIERING-01 and DC03 artifacts, and does not fetch data, write local
lake files, create recommendation rows, position rows, portfolios, dashboard
outputs, trading paths, production storage, broker output, factor-mining
output, or DQN/RL output.
GOAL-QUANT-RESEARCH-01 writes only research-only factor validity diagnostics
under `outputs/research/`, `configs/research/`, `docs/research/`, and
`outputs/audits/`. It consumes committed Provider02B, DC03, GOAL-10B.3,
GOAL-RISK-TIERING-01, and GOAL-RISK-TIERING-01.1 evidence only. It excludes
future returns from factor construction, uses future returns only after factor
assignment for post-hoc diagnostics, records trial and anti-overfitting
controls, and does not fetch data, write local lake files, create
recommendation rows, position rows, portfolios, dashboard outputs, trading
paths, production storage, broker output, factor-mining output, or DQN/RL
output.
GOAL-MVP-01 writes only research-only premarket diagnostic terminal evidence
under `outputs/mvp/`, `configs/mvp/`, `docs/mvp/`, and `outputs/audits/`. It
consumes committed Provider02B, DC03, GOAL-RISK-TIERING-01,
GOAL-RISK-TIERING-01.1, and GOAL-QUANT-RESEARCH-01 evidence only, resolves the
latest report date from committed evidence, and creates a Markdown report,
symbol diagnostic table, review queue, factor-validity summary, market-context
summary, and manifests. It does not fetch data, write local lake files, create
recommendation rows, position rows, portfolios, dashboard/frontend outputs,
trading paths, production storage, broker output, factor-mining output, or
DQN/RL output.
GOAL-ALPHA-FACTOR-CANDIDATE-01 writes only research-only alpha candidate
construction evidence under `outputs/research/`, `configs/research/`,
`docs/research/`, and `outputs/audits/`. It consumes committed Provider02B,
MVP, Quant Research, and risk-tiering evidence only; excludes future returns,
benchmark-excess returns, and label-ready fields from construction; and creates
candidate values, coverage summaries, and construction warnings only. It does
not fetch data, write local lake files, create recommendation rows, position
rows, portfolios, dashboard/frontend outputs, trading paths, production
storage, broker output, factor-mining output, DQN/RL output, or predictive
validity claims.
GOAL-QUANT-RESEARCH-02 writes only research-only alpha candidate validity
evaluation evidence under `outputs/research/`, `configs/research/`,
`docs/research/`, and `outputs/audits/`. It consumes committed
GOAL-ALPHA-FACTOR-CANDIDATE-01, Provider02B, MVP, and GOAL-QUANT-RESEARCH-01
evidence only. Forward-return and benchmark-excess-return fields are used only
post-hoc after factor values and buckets already exist. It creates no
recommendation rows, position rows, portfolios, dashboard/frontend outputs,
trading paths, production storage, broker output, local-lake output,
factor-mining output, DQN/RL output, or production predictive-validity claims.
GOAL-ALPHA-RESEARCH-REFINEMENT-01 writes only research-only rolling-stability
attribution and candidate refinement design evidence under `outputs/research/`,
`configs/research/`, `docs/research/`, and `outputs/audits/`. It consumes
committed Quant02, Alpha Candidate 01, Provider02B, and MVP evidence only. It
may use forward-return and benchmark-excess-return fields only for post-hoc
diagnostic attribution after source factor values already exist, and it does
not use them in refined factor construction. It creates no refined factor
panel, recommendation rows, position rows, portfolios, dashboard/frontend
outputs, trading paths, production storage, broker output, local-lake output,
factor-mining output, DQN/RL output, or predictive-validity claims.
GOAL-ALPHA-FACTOR-CANDIDATE-02 writes only research-only refined alpha
candidate construction evidence under `outputs/research/`,
`configs/research/`, `docs/research/`, and `outputs/audits/`. It consumes
committed Alpha Refinement 01, Alpha Candidate 01, Quant02, Provider02B, MVP,
and risk-tiering evidence only. It excludes future returns,
benchmark-excess-return fields, and label-ready fields from refined candidate
construction and creates no post-hoc validity evaluation, recommendation rows,
position rows, portfolios, dashboard/frontend outputs, trading paths,
production storage, broker output, local-lake output, factor-mining output,
DQN/RL output, or predictive-validity claims.
GOAL-QUANT-RESEARCH-03 writes only research-only refined alpha validity
evaluation evidence under `outputs/research/`, `configs/research/`,
`docs/research/`, and `outputs/audits/`. It consumes committed Candidate02,
Quant02, Provider02B, MVP, risk-tiering, and DC03 evidence only. Forward-return
and benchmark-excess-return fields are used only post-hoc after refined factor
values, quantiles, and buckets already exist. Its refined evaluation panel is
partitioned when needed so no committed artifact exceeds the 95 MiB policy,
and it creates no recommendation rows, position rows, portfolios,
dashboard/frontend outputs, trading paths, production storage, broker output,
local-lake output, factor-mining output, DQN/RL output, or production
predictive-validity claims.
GOAL-REGIME-LABEL-RESEARCH-01 writes only research-only market regime label
construction evidence under `outputs/research/`, `configs/research/`,
`docs/research/`, and `outputs/audits/`. It consumes committed Provider02B,
Quant03, Candidate02, MVP, and risk-tiering evidence only. It uses current-date
or trailing benchmark trend, benchmark volatility, cross-sectional breadth,
dispersion, liquidity, downside-risk, and composite regime rules, and excludes
future returns, benchmark-excess forward returns, label-ready fields, and
post-hoc factor performance from label construction. It creates no market
timing signal, recommendation rows, position rows, portfolio outputs,
dashboard/frontend files, trading paths, production storage, broker output,
local-lake output, factor-mining output, DQN/RL output, or predictive-validity
claim.
GOAL-ARCHITECTURE-REFACTOR-03 writes only provider/source catalog and
architecture modularization metadata under `configs/providers/`,
`outputs/providers/`, `configs/architecture/`, `docs/architecture/`, and
`outputs/audits/`. It catalogues AKShare source candidates, provider registry
roles, common audit/runner/contract/provider helper surfaces, module inventory,
duplicate patterns, and a future modularization plan. It does not fetch full
live AKShare datasets, write local-lake data, change scientific outputs,
construct alpha factors, create diagnostics, recommendations, positions,
portfolio output, dashboard/frontend files, trading paths, production storage,
broker output, factor-mining output, or DQN/RL output. GOAL-DATA-EXPANSION-
RESEARCH-01 remains a locked future gate.
timing signal, recommendation rows, position rows, portfolios, dashboard/
frontend outputs, trading paths, production storage, broker output, local-lake
output, factor-mining output, DQN/RL output, or predictive-validity claims.

## Active Contracts

- Approved-symbol-only universe boundary.
- Source health contract with source-origin labels.
- Trading-day calendar contract.
- Market, sector, stock, event, and review-only NLP contract layers.
- PIT signal snapshot with decision cutoff timestamps.
- Label snapshot generated after target-day close.
- Feature-label merge with explicit excluded-column manifest.
- Leakage audit that prevents labels from entering scoring features.
- Storage policy, bundle manifest, provider ingestion contract, and engineering
  panel readiness audits.
- Provider failure classification and source-backed bundle manifest summaries.
- GOAL-STORAGE-01 local research lake hardening contract and hygiene audit.
- GOAL-09.0 position-band review-only unlock audit evidence with no local data
  writes.
- GOAL-09 review-only position-band diagnostic evidence under
  `outputs/position/` only.
- GOAL-09.1 warning-review and dashboard-readiness evidence under
  `configs/dashboard/`, `docs/dashboard/`, and `outputs/audits/` only.
- GOAL-V1-INTEGRITY-01 artifact-lineage and structure evidence under
  `configs/validation/`, `docs/validation/`, and `outputs/audits/` only.
- GOAL-10A future backtest contract evidence under `configs/backtest/`,
  `docs/backtest/`, and `outputs/audits/` only.
- GOAL-10B recommendation diagnostic backtest evidence under
  `outputs/backtest/`, `docs/backtest/`, and `outputs/audits/` only.
- GOAL-10B.1 coverage repair diagnostic evidence under `outputs/backtest/`,
  `docs/backtest/`, and `outputs/audits/` only.
- GOAL-DATA-LABEL-01 forward-return label coverage evidence under
  `outputs/labels/`, `docs/labels/`, and `outputs/audits/` only.
- GOAL-DATA-PROVIDER-02A provider capability metadata under
  `outputs/providers/`, `configs/providers/`, `docs/providers/`, and
  `outputs/audits/` only.
- GOAL-DATA-PROVIDER-02A.1 network-opt-in provider smoke-test metadata under
  `outputs/providers/`, `configs/providers/`, `docs/providers/`, and
  `outputs/audits/` only.
- GOAL-DATA-PROVIDER-02B source-backed panel evidence under
  `outputs/datasets/`, `outputs/diagnostics/`, `outputs/providers/`,
  `configs/providers/`, `docs/providers/`, and `outputs/audits/` only.
- GOAL-V1-DIAGNOSTIC-COVERAGE-03 source-backed diagnostic coverage evidence
  under `outputs/diagnostics/`, `configs/diagnostics/`, `docs/diagnostics/`,
  and `outputs/audits/` only.
- GOAL-RISK-TIERING-01 risk-tier diagnostic evidence under
  `outputs/diagnostics/`, `outputs/backtest/`, `configs/risk/`, `docs/risk/`,
  and `outputs/audits/` only.
- GOAL-RISK-TIERING-01.1 downside-risk repair diagnostic evidence under
  `outputs/diagnostics/`, `outputs/backtest/`, `configs/risk/`, `docs/risk/`,
  and `outputs/audits/` only.
- GOAL-QUANT-RESEARCH-01 factor research evidence under `outputs/research/`,
  `configs/research/`, `docs/research/`, and `outputs/audits/` only.
- GOAL-MVP-01 premarket terminal evidence under `outputs/mvp/`,
  `configs/mvp/`, `docs/mvp/`, and `outputs/audits/` only.
- GOAL-ALPHA-FACTOR-CANDIDATE-01 alpha candidate evidence under
  `outputs/research/`, `configs/research/`, `docs/research/`, and
  `outputs/audits/` only.
- GOAL-QUANT-RESEARCH-02 alpha validity evaluation evidence under
  `outputs/research/`, `configs/research/`, `docs/research/`, and
  `outputs/audits/` only.
- GOAL-ALPHA-RESEARCH-REFINEMENT-01 rolling-stability attribution and refined
  candidate design evidence under `outputs/research/`, `configs/research/`,
  `docs/research/`, and `outputs/audits/` only.
- GOAL-ALPHA-FACTOR-CANDIDATE-02 refined alpha candidate construction evidence
  under `outputs/research/`, `configs/research/`, `docs/research/`, and
  `outputs/audits/` only.
- GOAL-QUANT-RESEARCH-03 refined alpha validity evaluation evidence under
  `outputs/research/`, `configs/research/`, `docs/research/`, and
  `outputs/audits/` only.
- GOAL-REGIME-LABEL-RESEARCH-01 market regime label construction evidence
  under `outputs/research/`, `configs/research/`, `docs/research/`, and
  `outputs/audits/` only.
- GOAL-ARCHITECTURE-REFACTOR-03 source catalog, provider registry, module
  inventory, duplicate-pattern inventory, and modularization plan evidence
  under `configs/providers/`, `outputs/providers/`, `configs/architecture/`,
  `docs/architecture/`, and `outputs/audits/` only.

## Source Evidence Warnings

### Issue #36 operational stock-history contract

- Canonical daily refresh uses only AKShare `stock_zh_a_hist_tx` / Tencent and
  requires a complete single-source current-T-1 qfq batch.
- East Money is excluded from canonical refresh. Its separate probe is
  disabled by default, bounded, and cannot affect rows, selection, checksums,
  snapshots, freshness, coverage, or success status.
- The Tencent sixth exported field is volume in `手`; canonical monetary amount
  remains null/unavailable. Volume is never copied into amount and unavailable
  amount is never represented as zero.
- Exact field order, schema, symbol mapping, unique keys, dates, finite values,
  OHLC relationships, volume, PIT, provenance, full coverage, qfq, and separate
  independent verification all fail closed.
- Governed BJ mapping is validated syntactically. BJ is outside the current
  enabled 41-symbol universe, and the current Tencent AKShare endpoint does not
  return its expected BJ schema; a future BJ admission therefore fails closed
  pending separately approved evidence.

- CNINFO did not cover `002475.SZ` in inspected source evidence.
- Tencent returned no usable rows under bounded variants.
- These warnings are documented and do not block deterministic GOAL-06B
  reproduction in the clean repo.
- Current GOAL-06C.5 coverage is a fixture: 2 approved symbols, 4 Stage 6C
  validation dates, and 8 rows. Engineering pilot requires at least 50 symbols,
  120 trading dates, and 6000 rows.
- GOAL-06C.6 either builds a source-backed local bundle or records classified
  provider/no-network failures. The default GOAL-06C.6/GOAL-06C.6A provider
  path remains direct AKShare/local-import. The explicit CloakBrowser reference
  probe is opt-in, tag-only, sanitized, and separates ingestion-solved,
  domain-access-only, dependency, HTTP/access, anti-bot, and browser/network
  failures.

## Safety Rules

- Do not fetch or commit raw provider payloads.
- Do not use ingestion time as publish time.
- Do not convert post-target labels into premarket features.
- Do not treat provider availability as symbol approval.
- Do not unlock actionable recommendation, risk, position sizing, dashboard,
  paper/live trading, production writes, model promotion, or DQN/RL.
- Do not treat STORAGE-01 as permission to create recommendation diagnostics,
  position diagnostics, backtests, dashboards, local lake files, or production
  DB behavior.
- Do not treat GOAL-09 diagnostic rows as actual position rows, position
  sizing, portfolio weights, target weights, order quantities, or trading
  instructions.
- Do not treat GOAL-09.1 dashboard-readiness evidence as permission to create
  dashboard files, dashboard outputs, HTML, Streamlit, frontend code, visual
  reports, new recommendation rows, new position rows, or local lake files.
- Do not treat GOAL-V1-INTEGRITY-01 artifact-lineage evidence as permission to
  create dashboard files, new diagnostic rows, local lake files, raw provider
  payloads, cache-backed inputs, notebooks, or production storage.
- Do not treat GOAL-10A backtest contract evidence as permission to run a
  backtest, generate performance rows, fetch price data, create equity curves,
  create portfolio returns, write local lake data, create dashboards, or write
  production storage.
- Do not treat GOAL-10B review-only diagnostic evidence as permission to create
  BUY/SELL/HOLD actions, target prices, position sizing, portfolio weights,
  portfolio returns, equity curves, dashboards, local lake data, trading,
  production, broker, factor-mining, or DQN/RL outputs.
- Do not treat GOAL-10B.1 coverage repair evidence as permission to fetch data,
  expand panels, create repaired rows or metrics without contract-valid support,
  create new recommendation or position rows, run portfolio backtests, create
  dashboards, or unlock execution paths.
- Do not treat GOAL-DATA-LABEL-01 label coverage evidence as permission to
  create or overwrite canonical diagnostics, run production backtests, create
  portfolio outputs, write local-lake data, create dashboards, or unlock
  trading, production, broker, factor-mining, or DQN/RL paths.
- Do not treat GOAL-V1-DIAGNOSTIC-COVERAGE-02 diagnostic coverage evidence as
  permission to create actionable recommendations, create actual positions,
  create portfolio outputs, write local-lake data, create dashboards, or unlock
  trading, production, broker, factor-mining, or DQN/RL paths. GOAL-10B.2 and
  GOAL-10C may consume DC02 rows only through their explicit review-only
  diagnostic gates.
- Do not treat GOAL-10B.2 recommendation revalidation diagnostics or GOAL-10C
  cost/slippage sensitivity diagnostics as permission to create actionable
  recommendations, positions, sizing, weights, orders, portfolio returns,
  equity curves, dashboards, local-lake data, trading, production, broker,
  factor-mining, or DQN/RL outputs.
- Do not treat GOAL-RISK-TIERING-01 risk-tier diagnostics as permission to
  create recommendation rows, actual positions, sizing, weights, orders,
  portfolio returns, equity curves, dashboards, local-lake data, trading,
  production, broker, factor-mining, or DQN/RL outputs. Future returns must
  remain out of risk score construction.
- Do not treat GOAL-RISK-TIERING-01.1 downside-risk repair diagnostics as
  permission to overwrite GOAL-RISK-TIERING-01 or DC03 artifacts, create
  recommendation rows, actual positions, sizing, weights, orders, portfolio
  returns, equity curves, dashboards, local-lake data, trading, production,
  broker, factor-mining, or DQN/RL outputs. Future returns must remain out of
  downside-risk score construction.
- Do not treat GOAL-QUANT-RESEARCH-01 factor validity diagnostics as
  permission to create recommendation rows, REC-TIERING outputs, actual
  positions, sizing, weights, orders, portfolio returns, equity curves,
  dashboards, local-lake data, trading, production, broker, factor-mining, or
  DQN/RL outputs. Future returns must remain out of factor construction.
- Do not treat GOAL-DATA-PROVIDER-02A provider capability metadata as
  permission to select a provider, expand the approved universe, build an
  evaluation panel, create new diagnostics, run backtests, fetch or commit raw
  payloads, write local-lake data, create dashboards, or unlock trading,
  production, broker, factor-mining, or DQN/RL paths.
- Do not treat GOAL-DATA-PROVIDER-02A.1 network smoke-test metadata as
  permission to select a provider, build a final evaluation panel, treat smoke
  rows as panel evidence, create diagnostics, run backtests, persist raw
  payloads or tokens, write local-lake data, create dashboards, or unlock
  trading, production, broker, factor-mining, or DQN/RL paths.
- Do not treat GOAL-DATA-PROVIDER-02B source-backed panel evidence as
  permission to promote GOAL-DATA-PANEL-02, create recommendation diagnostics,
  create position-band diagnostics, run backtests, create portfolio returns,
  create equity curves, persist raw payloads or tokens, write local-lake data,
  create dashboards, or unlock trading, production, broker, factor-mining, or
  DQN/RL paths.
- Do not treat GOAL-V1-DIAGNOSTIC-COVERAGE-03 diagnostic coverage evidence as
  permission to overwrite canonical GOAL-07B/08B/09 artifacts, run portfolio
  backtests, create actionable recommendations, create actual positions, create
  portfolio outputs, write local-lake data, create dashboards, or unlock
  trading, production, broker, factor-mining, or DQN/RL paths. GOAL-10B.3 uses
  DC03 evidence only for non-actionable revalidation diagnostics.

## Issue #24 Read-Only Workspace Projection

The Issue #24 workspace adds no new market, fundamental, factor, Alpha,
IC/RankIC, recommendation, position, or order data. `CommittedEvidenceStore`
allowlists and caches committed CSV/JSON inputs, validates immutable snapshot
checksums, and prevents path escape. `PremarketWorkspaceRepository` normalizes
those sources into display contracts, including explicit `UNAVAILABLE` values.

The FastAPI layer exposes 22 GET routes and no write methods. The frontend may
format, sort, filter, and visualize returned evidence, but it may not calculate
covariance, risk contribution, policy selection, position bands, constraints,
readiness, provider selection, factor validity, or recommendations. The one
server-derived correlation matrix is display-only and carries
`decision_input=false`.

Provider price and return discrepancy diagnostics remain separate. Adjustment
convention is explicitly unresolved and provider values are never silently
averaged. Browser-local watchlists are configuration only and are not part of
the data engine or repository state.

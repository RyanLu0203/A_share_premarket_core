# 02 Data Engine

## 2026-08-25 control-plane clarification

The current program decision is maintained in
`docs/governance/CURRENT_DECISION.md`. iFinD S2 remains an independent,
default-off provider-acceptance track. This governance checkpoint authorizes
no retry, network access, Keychain read, provider-data acceptance, canonical
panel change, or research use of iFinD evidence.

GOAL-FACTOR-FAILURE-ATTRIBUTION-01 consumes only previously committed Rerun02
and Quant04 diagnostics. It performs no provider request and changes no data,
PIT, label, canonical-panel, or storage contract.

GOAL-ALPHA-HYPOTHESIS-REDESIGN-01 identifies future liquidity evidence
requirements but performs no acquisition and changes no provider or data
contract. Its preferred hypothesis remains blocked pending a separately
approved evidence-acceptance contract.

GOAL-LIQUIDITY-EVIDENCE-ACCEPTANCE-CONTRACT-01 now defines that contract. It
passes as infrastructure, but current evidence is `NOT_READY` and accepted
rows remain zero. External acquisition still requires separate authority.

GOAL-LIQUIDITY-EVIDENCE-ACQUISITION-FOUNDATION-01 implements the default-off
preflight and atomic bundle mechanics. It does not activate a provider. Current
schema/source readiness blocks before network and preserves zero accepted rows.

GOAL-LIQUIDITY-PROVIDER-SOURCE-ACCEPTANCE-01 accepts only documentation-level
source contracts. Tushare Pro `daily_basic` supplies the documented
`free_share` and free-float turnover candidates; Baostock history supplies the
documented volume, turnover, trade-status, and adjustment cross-check. Source
units are explicitly normalized, but row-level provider availability and live
schemas remain unaccepted. No provider was called and acquisition remains
blocked.

The multi-workstream readiness batch adds pure Tushare/Baostock normalizers,
a fixed but unauthorized four-call schema plan, explicit provider-availability
validation, and an exact-100 universe contract. The current 50 eligible
symbols are insufficient, so the selector returns no accepted partial list.
Missing row-level availability also blocks PIT acceptance. Zero provider rows
or canonical data are created.

## 2026-08-13 iFinD S2 offline response-contract hardening

The prior `IFIND_MCP_RESPONSE_SCHEMA_MISMATCH` remains a truthful but generic
historical result. Because that run intentionally retained neither raw response
nor safe shape metadata, its exact failing layer and provider columns cannot be
reconstructed offline. The current checkpoint therefore does not relabel it.

Future failures are divided into fixed JSON-RPC, MCP result, provider envelope,
provider Markdown, S2 table-selection, semantic and normalization stages. Only
allowlisted reasons, bounded counts, fixed required-field presence and
value-independent structural SHA-256 values may enter the sanitized S2 status.
No provider value, response text, body hash, credential, header, query, path or
raw exception is preserved.

The parser now handles narrowly reviewed representation variants without
weakening the typed data contract. A future accepted bundle is readable only
from one explicit external root and only when its PASS status anchors the exact
bundle id and manifest hash. The reader revalidates four artifacts, 242 rows,
private permissions, path confinement, file and normalized checksums,
schema/recomputed-request/license lineage, primary keys, numeric domains,
explicit share/yuan/percentage units, exact symbols, QFQ, the exact governed
120-session calendar, one provider availability timestamp per batch and PIT.
Any failure produces zero rows.
Live accepted evidence is projected as one complete provider panel; immutable
replay and non-S2 modules remain unchanged.

This work was entirely offline and did not read Keychain. Another provider
call still requires a new explicit authorization.

## 2026-08-12 iFinD S2 live result

After PR #54 deployment, the one authorized S2 run passed the same-client
seven-service/35-schema S0 but the first `002475.SZ:get_stock_info` response
failed the reviewed response schema contract. The runner stopped at 1/4 calls
with zero retry. It did not call Hengtong or either performance tool and wrote
zero raw, normalized or canonical rows. Provider Health records only the safe
failure code and scope. Offline response-contract diagnosis is required before
any separately reauthorized call; S3-S4 and Research remain locked.

## 2026-08-12 iFinD S2 execution boundary

The owner authorized one S2 batch with at most four fixed calls and zero retry.
The runner must first repeat the accepted seven-service S0 in the same client
session. It then calls only `get_stock_info` and `get_stock_performance` once
per acceptance symbol. The first scope, schema, row-count, QFQ, governed-
calendar, numeric, availability or PIT failure stops the batch. No partial
batch is written. A complete pass writes only 242 normalized rows atomically
below the explicit external paid-data root; raw provider responses and
credentials are never persisted. S3, S4 and Research remain locked.

## 2026-08-12 iFinD live entitlement checkpoint

One governed S0 run accepted all seven MCP services and all 35 tools exposed by
the personal/trial entitlement, including their live input schemas. The full
reviewed catalog remains 36; `edb:search_edb` is enterprise-only and therefore
`UNAVAILABLE_BY_PLAN`. Earlier response-scope, supplier code/name inversion and
over-broad query failures were repaired fail-closed. After PR #49 merged, one
owner-authorized S1 again passed same-run S0 and called the fixed cohort exactly
twice with no retry. Luxshare and Hengtong each returned one bounded identity
row; symbol scope, company identity and schema verified for both. Call-plan v2
accepts those rows only as `acceptance_metadata_only`: local runtime
`observed_at` is provenance, provider `available_at` remains unknown,
`pit_timestamp_verified=false`, and `canonical_accepted=false`. Only the exact
prior safe local status may be migrated offline. S2 requires separate
authorization; S3-S4 and research remain locked.

## 2026-08-09 iFinD AI Financial Data Service Plane

The paid-data extension uses Tonghuashun iFinD **AI Financial Data Service**
through the purchased Streamable HTTP MCP/API Key channel. Seven exact services
and 36 supplier-documented tools are locally contracted; the existing QuantAPI
HTTPS adapter is optional if separately entitled. iFinD is an additional
governed provider, not a replacement for the current fail-closed Tencent
operational T-1 path and not a direct UI dependency.

The adapter and contracts cover seven canonical modules:

| Priority | Module | Canonical grain | Mandatory temporal control |
| --- | --- | --- | --- |
| P0 | Security master | `symbol + as_of_date` | `available_at` and versioned classification |
| P0 | Daily market/calendar | history: `trade_date + symbol`; calendar: `trade_date + market_code` | `data_cutoff`, adjustment and T-1 validation |
| P0 | PIT fundamentals/valuation | `symbol + metric + report_period + revision` | announcement, availability and revision timestamps |
| P1 | Industry/constituents | `symbol + classification + effective period` | historical membership; no present-day backfill |
| P1 | Corporate events/announcement metadata | `symbol + event_id` | publication timestamp; full text not committed |
| P1 | Macro/EDB | `series + observation + revision` | release date and revision policy |
| P1 | Market-structure cross-check | `trade_date + entity + metric` | vendor definition and source timestamp |

All requests are disabled by default. Live MCP access requires
`ASHARE_ALLOW_NETWORK_INGESTION=1`, `ASHARE_ALLOW_IFIND=1`, and
`ASHARE_ALLOW_IFIND_MCP=1` for a handshake. Any `tools/call` additionally
requires the separately authorized, default-off
`ASHARE_ALLOW_IFIND_MCP_DATA_CALLS=1`. The MCP API Key comes from macOS
Keychain by default, or `IFIND_MCP_API_KEY` only on an approved no-Keychain
runtime. No key value may enter a response, log, manifest, committed artifact,
or Dashboard payload. Dashboard readiness inspects only the configured
credential-delivery policy; it never reads Keychain secret material or reports
whether a key exists.

The bounded dual-stock S0-S4 call plan is machine-validated before any live
work. An optional Git-ignored local probe status carries only allowlisted
failure/catalog metadata into Provider Health; it never contains Keychain
values, authorization headers, raw schemas, or provider response bodies.

The MCP client fixes the supplier's unsafe sample behavior: TLS verification is
mandatory, redirects/system proxies are disabled, the host/port/path catalog is
exact, JSON and SSE are bounded, session ids are validated, and free-form tool
text is non-canonical. Tool calls remain default-off after the accepted S0.

The old exposed value remains permanently forbidden. External authentication
and S0 are accepted for 7/7 services and 35/35 personal/trial entitled
tools/schemas. The latest bounded S1 called Luxshare and Hengtong exactly once
each; both one-row identity responses passed scope, company and schema checks.
They remain non-canonical because the supplier summary has no auditable
provider availability timestamp. The approved v2 contract records local
`observed_at` only for acceptance provenance and explicitly leaves provider
`available_at` unknown. This does not relax any canonical PIT rule.

Naive timestamps are rejected by default. A caller may explicitly declare
`Asia/Shanghai` only after confirming the returned field semantics; canonical
timestamps are then converted to UTC. Date-only market/report fields are
compared to availability and cutoff in the `Asia/Shanghai` business timezone,
including the midnight boundary. The daily-history and trading-calendar
responses use separate source-specific grains so calendar rows never require a
fabricated symbol or adjustment mode.

Every accepted row is mapped to a canonical schema, validated at its declared
grain, checked against the PIT cutoff, tagged with request/schema/provider and
license lineage, and checksummed. Immutable normalized bundles may be written
only below an explicitly configured
`ASHARE_PREMARKET_DATA_ROOT/normalized/ifind`; its directories use `0700` and
files use `0600`. Raw paid payloads and
full paid datasets remain ignored local evidence. The Dashboard consumes only
accepted read models. Entitlement and live schema validation have passed at
S0; Provider Health reports only sanitized acceptance metadata and the current
PIT-blocked S1 state, never provider values or credentials.

The first bounded acceptance cohort is `002475.SZ` and `600487.SH`. Security
browseability is independent of reference-portfolio membership: both symbols
can be opened in the 23-page, 22-GET-route, zero-write Workspace, while
membership and data-acceptance states remain explicit. `002475.SZ` has 120
existing committed Provider02B trading-day rows; `600487.SH` has only a pilot
identity and must remain empty until accepted iFinD evidence exists. No empty
state may be converted into a recommendation, position, target price, order or
trading signal.

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
RESEARCH-01, GOAL-REGIME-LABEL-RESEARCH-02, and GOAL-QUANT-RESEARCH-04 later
implemented research-only over committed evidence; they did not unlock
Recommendation Tiering or any execution path.
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

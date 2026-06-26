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

## Source Evidence Warnings

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
  dashboards, or unlock GOAL-10C.

# GOAL-PREMARKET-RESEARCH-AND-POSITION-WORKSPACE-DASHBOARD-01

## Scope

This goal implements the Issue #24 local A-Share Premarket Workspace. It is a production-quality research interface over committed, validated evidence. It is not a trading terminal, recommendation system, broker client, or production service.

The goal-specific workspace authorization does not unlock the generic `dashboard_daily_report` workflow. The generic `dashboard` capability remains `false`.

## Architecture

The frontend is `apps/premarket-workspace`, built with Next.js, React, TypeScript, TanStack Table, ECharts, and Lightweight Charts. The backend is the GET-only FastAPI application in `src/ashare_premarket/dashboard`.

The API reads fixed internal repository artifacts through a root-confined `CommittedEvidenceStore`; no endpoint accepts a file path. It verifies immutable snapshot checksums before exposing snapshot integrity. It has no POST, PUT, PATCH, or DELETE route. Watchlist changes are browser-local and never written to repository or server state.

The browser does not calculate covariance, risk contribution, factor validity, position bands, constraint status, provider selection, readiness, or recommendations. The display correlation heatmap is derived on the server from validated canonical returns, marked `decision_input=false`, and is not used to alter any research conclusion.

## Page Map

| ID | Page | State |
|---:|---|---|
| 1 | Command Center | available |
| 2 | Watchlist | available; browser-local configuration |
| 3 | Stock Explorer | available |
| 4 | Stock Detail | available |
| 5 | Market Context | available |
| 6 | Portfolio Overview | available |
| 7 | Position Bands | available |
| 8 | Risk Monitor | available |
| 9 | Constraint Monitor | available |
| 10 | Abstention Center | available |
| 11 | Alpha Overview | locked; zero ready factors |
| 12 | Factor Monitor | locked; zero ready factors |
| 13 | IC / RankIC Lab | blocked pending a ready factor |
| 14 | Regime Analysis | market context available; factor-by-regime locked |
| 15 | Factor Correlation | locked; zero ready factors |
| 16 | Candidate Diagnostics | historical read-only; no promotion controls |
| 17 | Recommendation Tiering | locked; Issue #10 remains locked |
| 18 | Shadow Experiment | prepared, not started |
| 19 | Experiment History | immutable empty state until observations exist |
| 20 | Data Quality | available |
| 21 | Provider Health | available |
| 22 | Snapshot History | available |
| 23 | Provenance & Audit | available |

## Evidence Semantics

- Market and price evidence shows its provider and as-of date.
- Fundamentals absent from committed evidence render as `N/A / UNAVAILABLE`; they are never invented.
- Current live readiness fails closed when T-1 evidence is stale. The latest immutable replay remains selectable and clearly labeled.
- Current operational evidence identifies Tencent / AKShare
  `stock_zh_a_hist_tx`, qfq, amount-null semantics, source counts, checksums,
  and runtime commit. Historical research provider/chart lineage remains
  separately labeled; its legacy adjustment diagnostic may remain
  `UNRESOLVED`. No provider values are silently averaged.
- Position bands and abstentions are the outputs of the predecessor research goals. The UI does not reinterpret them as buy, sell, hold, target-weight, or order instructions.
- Diagonal ERC equivalence is disclosed in the policy catalog. Effective distinct policies are identified by the predecessor evidence.

## Local Run

Install the Python package and frontend dependencies, produce the validated
frontend build, then run:

```powershell
python scripts/run_premarket_workspace.py --check
npm.cmd run build --prefix apps/premarket-workspace
python scripts/run_premarket_workspace.py
```

The launcher runs `.next/standalone/server.js` with its generated static/public
assets by default. `--frontend-mode development` is an explicit
local-development opt-in and is not used by the approved launchd job.

The workspace is served at `http://127.0.0.1:3000`. The read-only API documentation is at `http://127.0.0.1:8000/docs`. Stop both local processes with `Ctrl+C`.

Individual services can be checked with:

```powershell
python scripts/run_premarket_workspace_api.py --check
Set-Location apps/premarket-workspace
npm.cmd run typecheck
npm.cmd run lint
npm.cmd test
npm.cmd run build
```

## Governance

`ready_factor_count` remains zero. Alpha, promoted factors, IC/RankIC claims, recommendation tiering, Issue #10 outputs, target prices, broker connectivity, orders, paper trading, production database writes, production promotion, and DQN/RL remain locked or absent.

The deterministic goal evidence is generated and audited with:

```powershell
python scripts/run_goal_premarket_research_position_workspace_dashboard01.py
python scripts/audit_goal_premarket_research_position_workspace_dashboard01.py
```

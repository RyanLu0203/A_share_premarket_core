# Dependency And Duplication Report

## Dependency Direction

Baseline Python analysis found 151 modules and 442 internal edges. Two strongly connected
groups exist:

1. A historical workflow-preservation cycle spanning 33 goal modules.
2. `providers.failure_events` and `providers.failure_classification`.

Neither cycle includes the active workspace API or frontend. Both are attached to historical
goal evidence and are classified `DEPRECATE` for future extraction rather than modified in
this goal. The new `domain`, `application`, `interfaces`, and dashboard read-model packages
must be acyclic and are covered by a forbidden-direction test.

Provider dynamic imports are deliberate network-optional boundaries. The two frontend dynamic
imports load ECharts and Lightweight Charts only. They are retained.

## Duplicate Groups

AST normalization found 139 exact duplicate Python function-body groups. The largest exact
group is 32 copies of optional JSON reading; separate name counting finds 38 `_read_csv`,
40 `_read_json`, 28 `_report_pass_or_warn`, and 16 `_fmt` definitions.

Most are embedded in checksummed historical goal modules. Replacing them globally would force
large manifest-chain churn and violate the no-scientific-rewrite boundary. They are recorded
for a later evidence-migration goal, not silently modified here.

The active duplicate groups selected for this goal are:

| Group | Baseline | Resolution |
|---|---|---|
| API path strings | Backend decorators plus 27 frontend/test literals | One machine registry, one generated/typed frontend route map, consistency audit |
| API request planning | `api.ts`, `page-data.ts`, `usePageEvidence.ts` | One typed workspace client and one hook |
| Snapshot reading | `dashboard/store.py` mixed with facade concerns | Focused snapshot repository plus compatibility wrapper |
| Dashboard read models | One 672-line class | Stock, portfolio, system repositories and status/capability services |
| FastAPI concerns | One 126-line route/application module | Focused routers, one app factory, one error layer |
| Selected-symbol state | Route, hardcoded sidebar path, watchlist-local state | URL-backed selected symbol with local persistence and shared navigation |

## Oversized Modules

The repository contains 34 source modules above 1,000 lines. Most are stable scientific or
historical goal modules. This goal does not fragment them without behavior evidence. The
active dashboard repository is below 1,000 lines but combines six responsibilities and is the
highest-value safe decomposition target.

## Frontend Dependency Findings

- One catch-all Next.js page dispatches all 23 governed pages.
- `WorkspaceApp -> usePageEvidence -> page-data/api` is the request chain.
- Stock detail dynamically loads Lightweight Charts.
- The stock chart drops amount, turnover, source, and quality already returned by the API.
- Volume uses an overlay scale rather than a dedicated pane.
- No selected-date tooltip or provider discrepancy marker is linked to chart time.
- There is no breakpoint below 1050px.

## Scientific And Replay Boundaries

The dashboard currently mixes immutable OPM snapshot files with committed global provider,
risk, and regime evidence. This is disclosed. Changing the snapshot schema or republishing
historical evidence is outside this refactor. The final parity report must prove exact OPM
payload equality and disclose implementation-checksum-only changes in workspace/daily
governance manifests.


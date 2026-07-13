# Final Architecture Report

## Result

Active architecture consolidation and stock-chart workspace completion.

The active workspace now has explicit domain, application, dashboard read-model, interface, and
governance boundaries. Stable scientific and historical modules remain in place where relocation
would create checksum and behavior risk.

This work does not claim that all repository bloat or all duplicate historical code was removed.

The machine source of truth is `configs/project/canonical_interfaces.json`. The public doctor is
`python -m ashare_premarket doctor`. The local workspace remains
`python scripts/run_premarket_workspace.py`.

## Before And After

| Measure | Baseline | Final |
|---|---:|---:|
| Production files | 376 | 413 |
| Production LOC | 79,014 | 80,305 |
| Public API routes | 22 GET / 0 write | 22 GET / 0 write |
| Frontend pages | 23 | 23 |
| Frontend tests | 25 | 35 |
| Obsolete internal files | 3 present | 3 deleted |
| Deleted internal LOC | 0 | 97 |
| Active duplication/ambiguity groups consolidated | 0 | 6 |
| Largest active workspace repository | 670 lines | 195 lines |
| Monolithic API implementation | 127 lines | 3-line wrapper; largest router 43 lines |
| Monolithic evidence store | 137 lines | 3-line wrapper; focused store 136 lines |
| Frontend API literal sources | 27 literals across request code/tests | 1 typed route map plus consistency audit |
| Dependencies added/removed | N/A | 0 / 0 |

Production files and LOC increase because the authorized selected-stock chart, typed contracts,
package boundaries, goal replay, and stronger tests are additive. The reduction claim is scoped to
unnecessary and duplicate active code: three internal files and 97 lines are deleted, three old
Python implementations become wrappers, API literals have one source, loading/error behavior has
one hook, and selected-symbol normalization/state has one owner.

## Canonical Boundaries

- `domain/quant_contracts`: future factor evidence protocol, locked at zero ready factors.
- `application/workspace`: compatibility-stable workspace facade.
- `dashboard/repositories`: snapshot, stock, portfolio, and system evidence reads.
- `dashboard/services`: status/freshness and capability views.
- `interfaces/api`: app factory, one error translator, and focused routers.
- `interfaces/cli`: program doctor.
- `apps/premarket-workspace/src/lib/api`: typed contracts, client, route map, and page plans.
- `governance/goal_global_codebase_consolidation_stock_chart01.py`: parity and lock replay.

The three old Python imports remain object-identity wrappers. The three removed frontend files were
internal and have no active references. Full details are in `COMPATIBILITY_MATRIX.csv`.

## Stock Chart Workspace

`/stocks/{symbol}/chart` is a stable deep link. Selection can originate from Watchlist, Stock
Explorer, Stock Detail search, or a direct URL and persists across navigation. The workspace shows
daily candles, a dedicated volume pane, amount, turnover, OHLCV crosshair detail, source and quality,
provider discrepancy markers, validated regime context, data cutoff, freshness/live/replay state,
portfolio weight, risk contribution, band state, and abstention state.

The supported ranges are 20D, 60D, 120D, 250D, and ALL. Only 120 sessions are committed, so 250D
states partial availability. The chart uses the existing Lightweight Charts dependency and has no
action, recommendation, target-price, or order markers.

## Parity And Locks

The final parity runner compares five critical artifacts, canonical OpenAPI, and all 22 API
responses to baseline SHA-256 values. Every comparison is exact. Snapshot schema and all accepted
scientific/operational semantics are unchanged.

`ready_factor_count` remains 0 with `LOCKED_NO_READY_FACTORS`. Recommendation Tiering, trading,
broker, paper execution, production, and DQN/RL remain locked.

## Deferred Debt

- Historical duplicate reader groups remain in checksummed goal modules.
- Historical scripts remain where removal requires separate ownership and evidence review.
- Checksummed dependency cycles remain in historical Python modules.
- Compatibility-only V0/provider evidence remains preserved.

Removing this debt without a dedicated evidence migration would violate the safe-deletion rules;
that migration is outside this PR.

## Rollback

Revert this branch's commits in reverse order. The base is
`e17a114aec8ea2f2f29259e5508e123f0f5486cc`; no accepted snapshot or historical evidence was
deleted or rewritten.

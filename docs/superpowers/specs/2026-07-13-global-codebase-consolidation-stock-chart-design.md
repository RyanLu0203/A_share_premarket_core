# Global Codebase Consolidation And Stock Chart Design

This design records the owner-approved attachment for
`GOAL-GLOBAL-CODEBASE-CONSOLIDATION-AND-STOCK-CHART-WORKSPACE-01`.

## Architecture

Preserve stable scientific goal modules. Establish explicit `domain`, `application`,
`interfaces`, dashboard read-model, and validation boundaries around the active operational
workspace. Use a machine interface registry for canonical commands, paths, and lock sources.
Keep current public imports and scripts as thin wrappers where implementation ownership moves.

## Backend

Split snapshot access, stock read models, portfolio read models, system evidence, status,
capabilities, API application assembly, routers, and error translation. API routers remain
GET-only and perform no scientific calculation or provider fetch. Existing route and response
parity is mandatory.

## Frontend

Use one typed client backed by the route registry. Keep URL identity authoritative for stock
deep links and persist the last selected symbol locally for navigation. Complete the existing
Lightweight Charts view with 20D/60D/120D/250D/ALL controls, explicit partial availability,
separate candle and volume panes, selected-date tooltip, amount/turnover, provider quality,
discrepancy markers, and validated regime context. No action markers or technical signals are
created.

## Governance

Add a protocol-only factor evidence extension whose active provider returns
`LOCKED_NO_READY_FACTORS` and zero ready factors. Keep Recommendation Tiering, recommendations,
trading, broker, paper execution, production, factor mining, and DQN/RL locked. Reconcile stale
prose to machine governance without changing scientific conclusions.

## Verification

Use TDD for registry, boundary, wrapper, repository, client, selected-symbol, and chart work.
Require raw and semantic parity, full Python/frontend validation, Playwright screenshots, and a
remote fresh clone. The PR remains draft until all checks pass and is never self-merged.


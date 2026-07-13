# Refactor Migration Plan

## Strategy

Use an incremental compatibility-first refactor. Stable scientific modules and accepted output
schemas stay in place. Active workspace responsibilities move behind preserved imports, and
frontend chart capability is completed using the existing Lightweight Charts dependency.

## Commit Sequence

1. Baseline architecture, interface, dependency, duplication, deletion, and parity inventory.
2. Canonical machine registry, program doctor, package-boundary tests, and public command repair.
3. Dashboard snapshot/read-model decomposition and focused FastAPI routers with wrappers.
4. Typed frontend API client and deletion of superseded internal request modules.
5. Selected-stock state, search, chart ranges, dedicated volume pane, tooltip, quality markers,
   regime context, and responsive states.
6. Locked factor-evidence protocol, governance reconciliation, parity artifacts, goal runner,
   audits, visual QA, and fresh-clone evidence.

## Migration Rules

- Write failing focused tests before each implementation slice.
- Preserve all 22 GET paths and zero write paths.
- Preserve the 23-page inventory and all locked Quant surfaces.
- Keep old Python import paths as wrappers.
- Do not add a chart or state-management dependency.
- Do not change portfolio calculations, thresholds, risk policies, snapshot schemas, or accepted
  scientific conclusions.
- Treat implementation checksum changes as governance metadata; compare all operational fields
  separately and require exact parity.
- Delete only candidates marked `DELETE` after all references move and replacement tests pass.

## Verification Checkpoints

| Checkpoint | Verification |
|---|---|
| Registry | doctor JSON, 22 route constants, frontend/backend consistency, all public commands exist |
| Backend | focused Python tests, OpenAPI paths/hash, 22 canonical response hashes |
| Frontend client | Vitest registry/client tests, typecheck, lint |
| Chart | component tests for five ranges, panes, tooltip, markers, unavailable states |
| Governance | ready factor zero and every downstream execution lock unchanged |
| Parity | OPM/daily/workspace semantic and raw hash report |
| Final | full Pytest, profile, audits, Playwright, remote fresh clone |

## Rollback

The branch starts at `e17a114aec8ea2f2f29259e5508e123f0f5486cc`. Each commit is independently
reviewable. Reverting commits in reverse order restores the baseline without moving the frozen
checkpoint branch/tag, rewriting history, or deleting accepted evidence.

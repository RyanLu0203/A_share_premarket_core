# Global Codebase Consolidation And Stock Chart Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Consolidate active repository interfaces and complete the selected-stock chart while preserving scientific, operational, API, snapshot, and governance behavior.

**Architecture:** Stable scientific modules remain in place. New package boundaries own the interface registry, workspace application facade, dashboard read repositories/services, FastAPI routers, and locked factor-evidence protocol; compatibility wrappers preserve old imports.

**Tech Stack:** Python 3.9, FastAPI, pytest, Next.js 16, React 19, TypeScript 5.9, Vitest, Playwright, Lightweight Charts 5.2.

## Global Constraints

- Base is `e17a114aec8ea2f2f29259e5508e123f0f5486cc` from `project-current`.
- Keep exactly 22 public GET API paths and zero write paths.
- Keep all 23 frontend pages and all existing documented commands.
- Add no chart or state-management dependency.
- Keep `ready_factor_count = 0` and every execution capability locked.
- Do not change portfolio calculations, thresholds, schemas, or accepted conclusions.
- Use `TEMP`/`TMP` outside the protected Windows user temp directory for full pytest/profile.

### Task 1: Canonical Registry And Doctor

**Files:** create `configs/project/canonical_interfaces.json`, `src/ashare_premarket/interfaces/registry.py`, `src/ashare_premarket/interfaces/cli/doctor.py`, `src/ashare_premarket/__main__.py`, `scripts/run_program_doctor.py`; modify `core/constants.py`; test `tests/test_global_refactor01_architecture.py`.

**Interfaces:** produce `load_interface_registry(root)`, `api_paths()`, and `run_doctor(root, as_json)`.

- [ ] Write tests asserting 22 unique GET paths, command existence, lock-source resolution, doctor output, and complete `PUBLIC_COMMANDS`.
- [ ] Run the focused test and confirm missing modules/commands fail.
- [ ] Implement the JSON registry, loader, CLI, module entrypoint, and compatibility script.
- [ ] Run focused tests and compileall.
- [ ] Commit `feat: add canonical program interface registry`.

### Task 2: Workspace Backend Decomposition

**Files:** create `application/workspace/repository.py`, `dashboard/repositories/*.py`, `dashboard/services/*.py`, `interfaces/api/app.py`, `interfaces/api/errors.py`, `interfaces/api/routers/*.py`; replace `dashboard/api.py`, `dashboard/repository.py`, and `dashboard/store.py` with wrappers.

**Interfaces:** old `create_app`, `PremarketWorkspaceRepository`, and `CommittedEvidenceStore` imports remain valid.

- [ ] Add tests for wrapper identity, snapshot cache/pointer behavior, repository ownership, GET-only enforcement, OpenAPI paths/hash, and all 22 response hashes.
- [ ] Run tests and confirm decomposition modules are missing.
- [ ] Move methods by responsibility without changing method bodies or response shapes.
- [ ] Split routes with one app factory and one error translator; use registry paths.
- [ ] Run focused tests, workspace goal runner/audit, and API launcher check.
- [ ] Commit `refactor: decompose workspace backend interfaces`.

### Task 3: Locked Factor Extension

**Files:** create `domain/quant_contracts/factor_evidence.py` and `dashboard/services/capability_service.py`; test architecture and capability response parity.

**Interfaces:** produce `FactorEvidenceProvider`, `FactorEvidenceSnapshot`, and `LockedFactorEvidenceProvider`.

- [ ] Add tests requiring zero ready factors and `LOCKED_NO_READY_FACTORS`.
- [ ] Implement protocol and locked provider only; wire capability service without changing response hashes.
- [ ] Run focused tests and verify Quant pages remain locked.
- [ ] Commit with the backend decomposition if the change is not independently reviewable.

### Task 4: Typed Frontend Client

**Files:** create `src/lib/api-routes.ts`, `src/lib/workspace-api.ts`, and tests; modify `usePageEvidence.ts` and `WorkspaceApp.tsx`; delete `api.ts`, `page-data.ts`, and `page-data.test.ts`.

**Interfaces:** produce `API_ROUTES`, `workspaceApi`, `pageRequestPlan`, and `loadPageEvidence`.

- [ ] Add failing route-registry, query, replay/live, and page-plan tests.
- [ ] Implement the typed client and migrate all callers.
- [ ] Delete superseded internal files and prove no references remain.
- [ ] Run typecheck, lint, and frontend tests.
- [ ] Commit `refactor: consolidate workspace API client`.

### Task 5: Selected Symbol And Chart Workspace

**Files:** create `hooks/useSelectedStock.ts`, `components/StockSelector.tsx`, and chart tests; modify `Sidebar.tsx`, `WorkspaceApp.tsx`, `WatchlistPage.tsx`, `StockExplorerPage.tsx`, `StockDetailPage.tsx`, `PriceVolumeChart.tsx`, `navigation.ts`, `globals.css`, and visual QA.

**Interfaces:** URL `/stocks/{symbol}` is authoritative; local storage key only restores navigation. Chart range is `20 | 60 | 120 | 250 | ALL`.

- [ ] Add failing tests for symbol/company search, watchlist/explorer links, persistence, synchronization, five ranges, partial 250D disclosure, two panes, selected-date tooltip, markers, and unavailable volume.
- [ ] Implement selection without a state library.
- [ ] Implement separate Lightweight Charts panes, crosshair data, amount/turnover/source/quality, discrepancy markers, and regime strip.
- [ ] Add responsive 760px behavior and stable chart dimensions.
- [ ] Run frontend checks and Playwright at required viewports/ranges/states.
- [ ] Commit `feat: complete selected stock chart workspace`.

### Task 6: Governance, Parity, And Goal Evidence

**Files:** create `docs/architecture/CANONICAL_PROGRAM_INTERFACES.md`, `COMPATIBILITY_MATRIX.csv`, goal contract/runner/audit/parity files; modify governance prose, workflow state, locks, Issue24/PR26 checksum inventories, and docs.

**Interfaces:** produce one goal runner and one audit that cover dependency, route, deletion, compatibility, Alpha lock, secret/path, and forbidden-action checks.

- [ ] Reconcile stale branch/commit and named-workspace lock prose without unlocking generic dashboard.
- [ ] Generate semantic parity excluding only implementation checksum metadata and require raw OPM payload parity.
- [ ] Run workspace and daily goal runners to refresh authorized implementation checksums.
- [ ] Run full Python/frontend/visual/audit matrix and three adversarial reviews.
- [ ] Push all commits, run remote fresh-clone verification, update Draft PR, and stop unmerged.


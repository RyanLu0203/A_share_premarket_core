# Baseline Architecture Inventory

Goal: `GOAL-GLOBAL-CODEBASE-CONSOLIDATION-AND-STOCK-CHART-WORKSPACE-01`

## Source And Lineage

- Repository: `RyanLu0203/A_share_premarket_core`
- Authoritative branch: `project-current`
- Baseline commit: `e17a114aec8ea2f2f29259e5508e123f0f5486cc`
- Baseline tree: `cc6889afe599d49a53a91efd3a53b40624151288`
- PR #26: merged at `e17a114aec8ea2f2f29259e5508e123f0f5486cc`
- Refactor branch: `codex-max/global-codebase-consolidation-stock-chart01`
- Baseline worktree: clean before and after validation

The baseline was read only with respect to accepted source and evidence. Runner-generated
working-tree changes were compared with committed artifacts and restored after validation.

## Validation Baseline

| Gate | Result |
|---|---|
| `python -m compileall -q .` | PASS, 5.02 seconds |
| `python -m pytest tests -q` | PASS, 383 tests in 1201.88 seconds |
| Frontend typecheck | PASS |
| Frontend lint | PASS |
| Frontend Vitest | PASS, 25 tests in 8 files |
| Frontend production build | PASS |
| Program validation profile | PASS, 115/115 commands in 1242.7 seconds |
| Portfolio-risk runner and audit | PASS |
| OPM01 runner and audit | PASS |
| Workspace runner and audit | PASS |
| Daily-refresh runner and audit | PASS |
| Safety, adapter, workflow, destructive, GitHub-only, Windows | PASS |
| PIT, engineering PIT, leakage, Rerun02 | PASS |
| Playwright visual QA | PASS, 7 screenshots at 1440/1280/1024 |
| Secret patterns | 0 matches |
| Credential-like tracked files | 0 files |
| Forbidden action/output filenames | 0 files |

The machine `TEMP` directory denied pytest access on this Windows host. Baseline validation
used an external writable `TEMP`/`TMP` directory. A focused reproduction proved that this
was an environment ACL issue, not a repository test failure.

## Code And Package Inventory

The production metric scope is `src/ashare_premarket/**/*.py`, `scripts/*.py`, and
non-test TypeScript/TSX/CSS under `apps/premarket-workspace/src`.

| Metric | Baseline |
|---|---:|
| Production files | 376 |
| Production LOC | 79,014 |
| Python package modules | 151 |
| Python internal import edges | 442 |
| Python strongly connected dependency groups | 2 |
| Frontend TypeScript/TSX modules | 47 |
| Frontend alias import edges | 106 |
| Dynamic Python import sites | 16 |
| Dynamic frontend imports | 2 |
| Python scripts | 185 |
| `run_*.py` scripts | 71 |
| `audit_*.py` scripts | 96 |

Current ownership is organized around scientific goal modules, shared `core`, provider and
validation infrastructure, the OPM/portfolio-risk application path, a combined dashboard
read repository, one FastAPI module, and one Next.js workspace. Stable scientific modules
remain in place because moving them would invalidate checksummed historical evidence without
improving the active workspace boundary.

## Largest Production Modules

| LOC | Module |
|---:|---|
| 4,751 | `src/ashare_premarket/validation/workflow_status.py` |
| 1,933 | `src/ashare_premarket/research/goal_quant_research03.py` |
| 1,898 | `src/ashare_premarket/portfolio_risk/goal_premarket_portfolio_risk_management01.py` |
| 1,781 | `src/ashare_premarket/research/goal_quant_research01.py` |
| 1,743 | `src/ashare_premarket/risk_tiering/goal_risk_tiering011.py` |
| 1,634 | `src/ashare_premarket/core/workflow_preservation.py` |
| 672 | `src/ashare_premarket/dashboard/repository.py` |

This goal targets the active 672-line dashboard repository and 126-line API module. It does
not use a repository-wide file move to disguise unchanged complexity.

## API And Frontend Surface

- FastAPI public surface: 22 GET routes, 0 write routes.
- OpenAPI canonical JSON SHA-256:
  `9d9d4814721de2c864907c0f57c39217346b61069fdca8892ab792fa5373e017`.
- Workspace page inventory: 23 governed pages.
- Frontend API path literals: 27 across runtime and tests.
- Lightweight Charts is already installed and is the only candlestick library.
- The stock chart currently supports 20D, 60D, and ALL only.
- The committed stock panel has 120 sessions for the representative stock; 250D must disclose
  partial availability rather than imply 250 observations.
- Candles already carry OHLC, volume, amount, turnover, source, and quality. The current chart
  discards amount, turnover, source, and quality and renders missing volume as zero.

## Snapshot Contracts

The immutable `2026-07-01` OPM snapshot contains these checksummed CSV contracts:

- `abstention_summary.csv`
- `constraint_evaluation.csv`
- `data_readiness.csv`
- `exposure_envelope.csv`
- `operational_run_summary.csv`
- `portfolio_risk_state.csv`
- `position_band_status.csv`
- `warnings.csv`

The exact headers and baseline hashes are recorded in `baseline_metrics.json`. The snapshot
manifest and latest pointer were byte-identical after Pytest, direct replay, and the complete
validation profile.

## Governance Baseline

- `ready_factor_count = 0`
- Generic dashboard capability: `false`
- Named research workspace: `implemented_research_only`
- Recommendation Tiering: locked
- Recommendation outputs: absent
- Trading: locked
- Broker: locked
- Paper execution: locked
- Production writes and promotion: locked
- Factor mining: locked
- DQN/RL: locked

Five absolute Mac paths remain only as explicit historical private-bundle governance
references. They are allowlisted evidence of what runtime code must not use. Required runtime
absolute user paths are zero.

## Baseline Risks

1. `CommittedEvidenceStore` and the dashboard facade combine snapshot reading, fallback path
   selection, freshness, formatting, stock, portfolio, and system views.
2. The 22 API routes, error translation, and repository creation are in one module.
3. Public command roles are not machine-classified and `PUBLIC_COMMANDS` omits 22 existing
   scripts added by later goals.
4. Governance prose contains stale commit, branch, dashboard-lock, DataExpansion, and Quant04
   statements that disagree with machine state.
5. The selected stock is route-local; the sidebar resets to a hardcoded symbol and watchlist
   rows do not open stock detail.
6. Two historical dependency cycles and broad optional-reader duplication remain. They are
   checksummed historical paths and are not safe deletion targets for this goal.

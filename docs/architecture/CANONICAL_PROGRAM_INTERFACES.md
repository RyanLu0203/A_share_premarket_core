# Canonical Program Interfaces

`configs/project/canonical_interfaces.json` is the machine-readable source of truth. The
authoritative branch is `project-current`; `main` is not a deployment source. Schema `1.1` keeps
`command` as the platform-neutral default and adds optional `platform_commands`; the loader remains
compatible with schema `1.0` registries.

| Interface | Purpose | Canonical command | Module | Input contract | Output contract | Network behavior | Live/replay behavior | Expected failure | Visibility |
|---|---|---|---|---|---|---|---|---|---|
| Program doctor | Identify current interfaces and locks | `python -m ashare_premarket doctor` | `ashare_premarket.interfaces.cli.doctor` | Repository root, optional `--json` | Commands, routes, snapshot, refresh and locks | None | Read-only introspection | Reports missing registry/evidence/git metadata | Public |
| Local workspace | Launch API and frontend | `python scripts/run_premarket_workspace.py` | `scripts.run_premarket_workspace` | Loopback host/ports, optional `--check` | Workspace and API URLs | Loopback only | Launches both; check launches neither | Fails on missing npm/API/frontend contract | Public |
| Workspace API | Serve committed evidence | `python scripts/run_premarket_workspace_api.py` | `ashare_premarket.interfaces.api.app` | Loopback host/port, optional `--check` | FastAPI schema and 22 GET routes | Loopback only | Live-readiness and replay query modes | Fails closed if route contract cannot load | Public |
| Workspace frontend | Present read-only evidence | `npm run dev --prefix apps/premarket-workspace` | `apps/premarket-workspace` | `NEXT_PUBLIC_PREMARKET_API_URL` | Next.js workspace | Configured loopback API only | Shared live/replay and snapshot parameters | Fails on missing dependencies/API | Public |
| Daily refresh | Validate T-1 evidence and conditional OPM handoff | `python scripts/run_daily_incremental_evidence_refresh.py` | `ashare_premarket.daily_refresh.goal_daily_incremental_evidence_refresh01` | Clock, bounded evidence, explicit network opt-in | Refresh status and immutable handoff | Disabled by default | Daily operational with replay support | Fails closed without advancing OPM | Public |
| Daily replay | Reproduce accepted refresh evidence | `python scripts/run_goal_daily_incremental_evidence_refresh01.py` | `ashare_premarket.daily_refresh.goal_daily_incremental_evidence_refresh01` | Committed replay evidence | Refresh manifest and audit inputs | None | Deterministic replay | Records blocked reasons without invented dates | Public |
| OPM01 | Run read-only position management | `python scripts/run_premarket_position_management.py` | `ashare_premarket.portfolio_risk.goal_premarket_position_management_operational01` | Clock, replay date, holdings and refresh manifest | Immutable research-only snapshot | None | Operational and explicit replay | Fails on stale/incomplete evidence | Public |
| OPM01 replay | Reproduce the accepted OPM snapshot | `python scripts/run_goal_premarket_position_management_operational01.py --replay-date 2026-07-01` | `ashare_premarket.portfolio_risk.goal_premarket_position_management_operational01` | Governed replay date | Checksummed snapshot and audit evidence | None | Deterministic replay | Fails on predecessor/integrity drift | Public |
| Workspace replay | Regenerate workspace governance evidence | `python scripts/run_goal_premarket_research_position_workspace_dashboard01.py` | `ashare_premarket.dashboard.goal_premarket_research_position_workspace_dashboard01` | Committed source and evidence | Workspace manifest/report | None | Governance replay only | Fails on checksums, locks, routes or integrity | Public |
| Program validation | Run the canonical validation profile | `python scripts/run_program_validation_profile.py` | `ashare_premarket.validation.gates` | Clean repository and dependencies | Command-by-command PASS/FAIL profile | Providers disabled | Deterministic replay-heavy profile | Returns nonzero on any failed gate | Public |
| Experiment contract | Inspect future experiment preparation | `GET http://127.0.0.1:8000/api/experiment` | `PremarketWorkspaceRepository.experiment` | Running read-only API | `PREPARED_NOT_STARTED`, zero observations | Loopback GET only | Read-only in either mode | Explicit unavailable/not-started state | Public |
| Safety gate | Verify locked boundaries | `python scripts/run_safety_gate.py` | `ashare_premarket.ops.safety` | Repository tree and governance | PASS/BLOCKED report | None | Deterministic audit | Returns nonzero on forbidden imports/outputs/states | Public |
| Global refactor replay | Regenerate this goal's parity evidence | `python scripts/run_goal_global_codebase_consolidation_stock_chart01.py` | `ashare_premarket.governance.goal_global_codebase_consolidation_stock_chart01` | Baseline metrics, registry, source and evidence | Manifest, exact parity JSON and report | None | Deterministic architecture replay | Returns nonzero on interface/parity/deletion/chart/lock drift | Public |
| Global refactor audit | Independently audit this goal | `python scripts/audit_goal_global_codebase_consolidation_stock_chart01.py` | `ashare_premarket.governance.goal_global_codebase_consolidation_stock_chart01` | Committed goal evidence and current source | PASS/BLOCKED audit | None | Deterministic audit | Returns nonzero when facts differ from evidence | Public |

## Frontend Platform Commands

The universal canonical frontend command is the POSIX/macOS-compatible
`npm run dev --prefix apps/premarket-workspace`. The registry also exposes explicit platform
commands:

- POSIX/macOS: `npm run dev --prefix apps/premarket-workspace`
- Windows: `npm.cmd run dev --prefix apps/premarket-workspace`

The Windows executable suffix is an alternative for Windows shells, not the universal interface.

## Compatibility Entry Points

The old Python imports `ashare_premarket.dashboard.api`,
`ashare_premarket.dashboard.repository`, and `ashare_premarket.dashboard.store` are thin
compatibility wrappers. New code uses `ashare_premarket.interfaces.api.app`,
`ashare_premarket.application.workspace.repository`, and
`ashare_premarket.dashboard.repositories.snapshot_repository` respectively.

The frontend route `/stocks/{symbol}/chart` is additive. All previously accepted frontend paths,
22 API paths, snapshot directories, latest pointers, daily/OPM commands, and audit commands remain
valid.

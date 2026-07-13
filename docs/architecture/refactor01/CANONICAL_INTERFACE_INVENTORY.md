# Canonical Interface Inventory

This is the pre-refactor inventory. The final source of truth will be the machine registry
and `docs/architecture/CANONICAL_PROGRAM_INTERFACES.md`.

| Interface | Current command | Module | Role | Current ambiguity |
|---|---|---|---|---|
| Local workspace | `python scripts/run_premarket_workspace.py` | `scripts/run_premarket_workspace.py` | service | Correct launcher, but confused with goal runner |
| Workspace check | `python scripts/run_premarket_workspace.py --check` | same | environment validation | Does not print all canonical interfaces or locks |
| Workspace API | `python scripts/run_premarket_workspace_api.py` | `ashare_premarket.dashboard.api` | service | API implementation and route registry are combined |
| Frontend only | `npm.cmd run dev -- --hostname 127.0.0.1 --port 3000` | `apps/premarket-workspace` | service | API URL must be supplied separately |
| Daily operation | `python scripts/run_daily_incremental_evidence_refresh.py` | daily refresh application | live/replay operational | Name resembles deterministic goal runner |
| Daily deterministic replay | `python scripts/run_goal_daily_incremental_evidence_refresh01.py` | daily refresh goal | governance replay | Regenerates evidence; not the normal daily command |
| OPM01 operation | `python scripts/run_premarket_position_management.py` | OPM application | live/replay operational | Confused with goal runner |
| OPM01 deterministic replay | `python scripts/run_goal_premarket_position_management_operational01.py --replay-date 2026-07-01` | OPM goal | governance replay | Explicit replay date is required for reproducibility |
| Immutable snapshot generation | OPM01 operation after freshness validation | OPM application | artifact producer | No independent public snapshot writer is intended |
| Workspace goal replay | `python scripts/run_goal_premarket_research_position_workspace_dashboard01.py` | workspace goal | governance replay | Does not launch the UI |
| Program validation | `python scripts/run_program_validation_profile.py` | validation | audit | Long-running and includes full Pytest |
| Safety gate | `python scripts/run_safety_gate.py` | ops | audit | Canonical and retained |
| Adapter audit | `python scripts/run_adapter_audit.py` | ops | audit | Canonical and retained |
| Deterministic experiment preparation | GET `/api/experiment` | workspace repository | read-only contract | Prepared, not started; no observations |

## API Paths

The baseline has exactly 22 public `/api/` paths. All are GET-only:

`/api/health`, `/api/status`, `/api/command-center`, `/api/watchlists`,
`/api/stocks`, `/api/stocks/{symbol}`, `/api/stocks/{symbol}/market`,
`/api/stocks/{symbol}/fundamentals`, `/api/stocks/{symbol}/risk`,
`/api/stocks/{symbol}/position`, `/api/portfolio/overview`,
`/api/portfolio/bands`, `/api/portfolio/risk`, `/api/portfolio/constraints`,
`/api/portfolio/abstentions`, `/api/market/context`, `/api/quant/capabilities`,
`/api/experiment`, `/api/data-quality`, `/api/provider-health`, `/api/snapshots`,
and `/api/provenance`.

## Compatibility Policy

- Existing documented commands remain valid.
- Existing API and frontend paths remain valid.
- `ashare_premarket.dashboard.api.create_app`,
  `ashare_premarket.dashboard.repository.PremarketWorkspaceRepository`, and
  `ashare_premarket.dashboard.store.CommittedEvidenceStore` remain importable through thin
  wrappers after decomposition.
- Operational and deterministic goal commands remain separate because their mode and side
  effect contracts differ.
- The V0 diagnostic viewer remains compatibility-only historical evidence in this goal. It is
  not deleted because its test, documentation, and manifest form a checksummed historical set.


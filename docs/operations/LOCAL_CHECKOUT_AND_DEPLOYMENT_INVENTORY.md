# Local Checkout and Deployment Inventory

**Observed and consolidated:** 2026-08-09
**Scope:** local macOS checkout, deployment, rollback, supplier-reference and
duplicate-file boundaries

The owner explicitly requested a single same-prefix top-level Desktop entry.
The consolidation is complete: `/Users/luxinyu/Desktop/A_share_premarket_core`
is the only Desktop path beginning `A_share_premarket_core`. No checkout,
bundle, credential or evidence file was deleted.

## Current placement

| Boundary | Current role |
| --- | --- |
| `/Users/luxinyu/Desktop/A_share_premarket_core` | Only top-level active development checkout |
| `/.local/legacy-checkouts/2026-08-09/` | Ignored, recoverable placement for six historical Git checkouts and one rollback-evidence directory; dirty status counts were preserved |
| `/.local/rollback/` | Ignored private checkpoint bundle |
| `/.local/vendor/ifind/` | Ignored reference-only supplier Skill and MCP RTF; mode hardened to owner-only |
| `/.local/quarantine/` | Ignored, recoverable placement for generated duplicate outputs and inactive Git index copies |
| `/Users/luxinyu/Library/Application Support/AsharePremarket/deployment` | Stable deployment root; unchanged and still used by loaded services |

The supplier Skill is not installed or executed. Its unsafe sample client and
the RTF containing historical credential material remain reference-only under
the ignored owner-only boundary.

The committed guard `python scripts/audit_local_workspace_boundary.py` fails
closed if a future same-prefix sibling appears. `AGENTS.md` and `CODEX.md`
forbid agents from creating new Desktop sibling checkouts.

## Pre-consolidation point-in-time evidence

The tables below preserve the roles and dirty states observed immediately
before the authorized move. Their paths are historical; their contents now
live under the ignored local boundaries above.

## Keep

| Path | Approx. size | Observed Git state | Role |
| --- | ---: | --- | --- |
| `/Users/luxinyu/Desktop/A_share_premarket_core` | 2.0 GiB | active feature branch; expected current changes | Active development checkout for the present work |
| `/Users/luxinyu/Library/Application Support/AsharePremarket/deployment` | 1.7 GiB | clean `project-current` at `25273bb` | Stable non-TCC deployment root used by the loaded macOS services |
| `/Users/luxinyu/Desktop/A_share_premarket_core_checkpoint_310559.bundle` | about 16 MiB | private Git bundle, outside the repository | User-private rollback evidence; not a runtime or Codex Max dependency |

The Application Support deployment and its LaunchAgents must not be repointed
or removed as part of repository cleanup. A new release should be deployed by
the governed deployment workflow only after review and acceptance.

## Clean archive candidates, subject to owner approval

| Path | Approx. size | Observed state | Required check before archive/removal |
| --- | ---: | --- | --- |
| `/Users/luxinyu/Desktop/A_share_premarket_core_current` | 1.9 GiB | clean Git checkout | Confirm no shell, editor, service, or worktree depends on it; record its exact commit and remote |
| `/Users/luxinyu/Desktop/A_share_premarket_core_deployment_repair` | 1.2 GiB | clean linked worktree at `be22ea4` | Remove through Git worktree governance, never by blind recursive deletion |
| `/Users/luxinyu/Desktop/A_share_premarket_core_current.rollback-pre-pr32-20260714` | 1.6 GiB | clean rollback checkout | Confirm the private bundle and remote refs provide sufficient rollback coverage |
| `/Users/luxinyu/Desktop/A_share_premarket_core_current.rollback-evidence-pre-pr38-20260717T1100` | 12 MiB | non-Git rollback evidence | Inspect contents and retention need before any move or deletion |

These are candidates only. “Clean” means no Git working-tree changes at the
inspection time; it does not prove that the directory is unused or disposable.

## Dirty copies: do not delete or archive yet

| Path | Approx. size | Observed Git state | Risk |
| --- | ---: | --- | --- |
| `/Users/luxinyu/Desktop/A_share_premarket_core_deploy` | 1.8 GiB | about 100 status entries on `codex/local-mac-deployment` | May contain uncommitted deployment/runtime evidence |
| `/Users/luxinyu/Desktop/A_share_premarket_core_runtime` | 1.8 GiB | about 98 status entries on `project-current` | May contain local runtime data and user changes |
| `/Users/luxinyu/Desktop/A_share_premarket_core_ops` | 1.8 GiB | dirty and four commits ahead of its recorded `origin/project-current` | Contains branch history and at least one working-tree change |

These dirty states were preserved through the move. Before any future deletion,
each copy still needs a separate review of tracked changes, untracked files,
ignore status, branch-only commits and private/runtime evidence. Credentials,
raw provider data, caches, logs, databases and local-lake contents must not be
committed merely to make an archived checkout clean.

## Consolidation verification

- The linked deployment-repair worktree was moved with Git worktree governance
  and repaired after its common repository moved.
- Clean checkouts remained clean; dirty checkout status counts remained
  `100`, `1`, and `98` respectively.
- The stable Application Support deployment and its running services were not
  stopped, repointed or modified.
- Generated `* 2.*` output copies and inactive `.git/index N` copies were moved
  into quarantine rather than deleted.
- Future cleanup of the recoverable local archive still requires an explicit
  owner decision; no broad recursive deletion is authorized.

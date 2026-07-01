# GOAL-CODEX-OPERATING-SYSTEM-01 Report

## 1. Goal Status

Status: `PASS_WITH_WARNINGS`.

GOAL-CODEX-OPERATING-SYSTEM-01 is implemented as a governance-only, remote
Windows-compatible, GitHub-only Codex Max onboarding gate.

## 2. Why Codex Max Remote Windows GitHub-Only Rules Are Needed

Codex Max may run outside the user's Mac environment. It needs a clear GitHub
entrypoint, cross-platform command expectations, and review rules that prevent
local path assumptions, local cache dependence, unreviewed state changes, and
downstream unlock drift.

## 3. Current Remote Branch And Commit

- Authoritative remote repository: `RyanLu0203/A_share_premarket_core`
- Authoritative remote branch: `project-current`
- Latest confirmed remote commit before this gate:
  `e216aac7cac188f401e970a03defca73b11aa449`

## 4. Current Checkpoint Branch/Tag

- Remote checkpoint branch: `checkpoint/arch03-stable-310559`
- Remote checkpoint tag: `checkpoint-arch03-stable-310559`
- Stable Arch03 commit: `310559ae18bbf203e795c1d66bc7181a6b11c14a`

## 5. Local Bundle User-Private Status

The local bundle backup is user-private only. It is not a Codex Max input,
onboarding dependency, validation dependency, data source, or rollback
requirement.

## 6. Current Implemented Goals

Provider02B, DC03, GOAL-10B.3, Risk01/Risk011, Quant01, MVP01, Alpha
Candidate 01, Quant02, Alpha Refinement 01, Alpha Candidate 02, Quant03,
Regime01, Arch03, and GOAL-REPOSITORY-CHECKPOINT-01 remain implemented.

## 7. Current Locked Goals

GOAL-CODEX-MAX-ONBOARDING-SMOKE-01, DataExpansion, Quant04, Rec Tiering,
GOAL-10B.4, position-band validation, GOAL-10D, dashboard/frontend, trading,
broker, production, portfolio backtest, local-lake, factor-mining, and DQN/RL
remain locked or deleted from active mainline.

## 8. User / Main Codex / Codex Max Authority Model

User is final authority. Main Codex is program brain, reviewer, integrator, and
workflow controller. Codex Max is a high-capacity executor for explicitly
assigned goals only.

## 9. GitHub-Only Source Policy

Codex Max may use only GitHub repository code, docs, configs, committed outputs
and audit artifacts, and remote branches/tags. It may not rely on local Mac
paths, local bundles, local data lakes, local provider caches, local-only
environment variables, or uncommitted local state.

## 10. Windows Compatibility Policy

Codex Max-required scripts and instructions must use cross-platform Python,
`pathlib`, UTF-8, and `python -m` style validation where possible. Required
steps must not depend on bash-only commands, `chmod`, symlinks, POSIX-only
absolute paths, or case-sensitive filesystem behavior.

## 11. Codex Max Remote Operating Protocol

Codex Max clones from GitHub, checks out `project-current`, reads the
authoritative state files, executes only an explicitly assigned goal, works on
`codex-max/<goal-id>`, pushes that branch, produces a standardized handoff, and
leaves clean git status.

## 12. Main Codex Review Protocol

Main Codex verifies branch lineage, base branch, GitHub-only source use,
Windows compatibility, workflow status, project state consistency, locked
boundaries, forbidden outputs, evidence deletion, validation, scans, and
fresh-clone evidence when required.

## 13. Git Branch And PR Policy

Codex Max starts from `project-current`, works on `codex-max/<goal-id>`, and
does not push directly to `project-current` unless explicitly authorized. PRs
must disclose goal, base, worker branch, validation, output scope, locked
boundaries, destructive changes, and handoff.

## 14. Authoritative State Files

Authoritative state files are `CODEX.md`, `AGENTS.md`, `PROJECT_STATE.md`,
`ROADMAP.md`, `configs/project/workflow_status.csv`, governance queue and
boundary docs, GitHub-only and Windows policy docs, remote protocol docs, and
current project snapshots.

## 15. Project State Update Policy

Scientific goals update their own reports/audits/manifests. Project-wide state
updates must remain consistent with workflow status and require Main Codex
review before merge when Codex Max performs them.

## 16. Destructive Change Policy

Deleting source, tests, docs, configs, scripts, workflow rows, committed
evidence, or audit outputs requires explicit user approval. Force pushes and
history rewrites remain prohibited.

## 17. New Codex Max Onboarding Path

The next Codex Max goal is
`GOAL-CODEX-MAX-ONBOARDING-SMOKE-01-REMOTE-WINDOWS-GITHUB-ONLY-COMPLIANCE-GATE`.

## 18. Required Validation Matrix

Required validation includes compileall, pytest, Codex OS audit,
GitHub-only source audit, Windows compatibility audit, destructive-change
audit, project snapshot generation, branch state check, checkpoint audit,
Arch03 runner/audit, program validation profile, safety gate, adapter audit,
workflow diagnostics, workflow status audit, and the explicit forbidden-output,
secret, no-lookahead, governance, size, dashboard, recommendation, and position
scans.

## 19. Governance Files Added Or Updated

Root entrypoints, governance docs, GitHub templates, CODEOWNERS, workflow
status, current snapshots, and governance audit/report/manifest/inventory
evidence were added or updated.

## 20. Governance Scripts Added

- `scripts/audit_codex_operating_system01.py`
- `scripts/audit_github_only_source_policy.py`
- `scripts/audit_windows_compatibility_policy.py`
- `scripts/audit_destructive_changes.py`
- `scripts/generate_project_snapshot.py`
- `scripts/check_latest_branch_state.py`

## 21. Boundaries Preserved

No scientific outputs, factor classifications, ready factor count, provider
evidence, downstream locks, recommendation outputs, position outputs,
portfolio outputs, dashboard/frontend artifacts, trading, broker, production,
local-lake, factor-mining, or DQN/RL outputs are changed or created.

## 22. Recommended Next Goal

`GOAL-CODEX-MAX-ONBOARDING-SMOKE-01-REMOTE-WINDOWS-GITHUB-ONLY-COMPLIANCE-GATE`.

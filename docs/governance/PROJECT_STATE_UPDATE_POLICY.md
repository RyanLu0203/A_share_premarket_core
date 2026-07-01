# Project State Update Policy

Authoritative state updates must be intentional, consistent, and reviewable.

- Scientific goal outputs update their own report, audit, and manifest.
- Authoritative project state updates must be consistent with
  `configs/project/workflow_status.csv`.
- Codex Max may not update project-wide state unless the assigned goal
  explicitly requires it.
- If Codex Max updates project-wide state, Main Codex must review consistency
  before merge.
- Any discrepancy must be reported as `needs_user_decision`.

Project-wide state includes `CODEX.md`, `AGENTS.md`, `PROJECT_STATE.md`,
`ROADMAP.md`, `configs/project/workflow_status.csv`, governance queue/boundary
docs, and current project snapshots.

# Branching And PR Policy

## Branches

- Authoritative entry branch: `project-current`.
- Stable rollback branch: `checkpoint/arch03-stable-310559`.
- Stable rollback tag: `checkpoint-arch03-stable-310559`.
- Stable rollback commit: `310559ae18bbf203e795c1d66bc7181a6b11c14a`.

Codex Max starts from `project-current` unless the user explicitly instructs
otherwise. Codex Max must not start from stale `main` by default. Codex Max
work must use `codex-max/<goal-id>` unless explicitly authorized otherwise.

## Commits And Pushes

- Commit only files required for the assigned goal.
- Do not commit local bundle backups, raw payloads, private logs, credentials,
  notebooks, databases, caches, or oversized files.
- Push the assigned `codex-max/<goal-id>` branch for review.
- Do not push directly to `project-current` unless explicitly authorized.
- Do not force push or rewrite history without explicit user approval.

## Pull Requests

PRs must include the goal ID, base commit, changed files, outputs, validation,
locked-boundary confirmation, destructive-change disclosure, and handoff
summary.

# GitHub Only Source Policy

GitHub is the only authoritative source for Codex Max.

## Authoritative Sources

- Authoritative code source: remote branch `project-current`.
- Authoritative data and evidence sources are committed repository artifacts
  only:
  - `configs/**`
  - `docs/**`
  - `outputs/audits/**`
  - `outputs/research/**`
  - `outputs/providers/**`
  - `outputs/diagnostics/**`
  - `outputs/mvp/**`
  - `outputs/datasets/**`

## Prohibited Sources

Codex Max must not rely on:

- local Mac files
- `/Users/luxinyu` paths
- local bundle backups
- local uncommitted data
- local provider caches
- local-lake data
- local-only environment variables
- stale default `main`

Codex Max must not fetch live provider data unless an assigned future goal
explicitly allows network opt-in. Provider registry network remains disabled by
default.

Any future data expansion must write bounded, audited artifacts back to GitHub
and must obey file-size limits.

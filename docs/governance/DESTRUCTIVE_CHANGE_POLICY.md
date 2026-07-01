# Destructive Change Policy

Destructive changes require explicit user approval before implementation.

## Destructive Changes

- Deleting source files, tests, docs, configs, or scripts.
- Deleting committed evidence or audit outputs.
- Removing workflow rows.
- Rewriting scientific conclusions.
- Force-pushing or rewriting history.
- Replacing committed project state with incompatible state.
- Large deletion sets without a documented user approval note.

## Default Action

If approval is absent, preserve the file, report the conflict, and request a
user decision. Codex Max cannot approve destructive changes for itself.

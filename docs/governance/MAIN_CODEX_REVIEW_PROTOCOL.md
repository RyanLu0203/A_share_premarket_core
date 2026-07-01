# Main Codex Review Protocol

Main Codex reviews Codex Max output before user merge or unlock decisions.

## Review Checklist

- Verify worker branch is `codex-max/*` unless explicitly authorized.
- Verify base branch is `project-current`.
- Verify no stale `main` use.
- Verify branch and base commit.
- Verify commit lineage and remote head.
- Verify no local Mac path dependency.
- Verify no local bundle dependency.
- Verify no local-lake dependency.
- Verify only GitHub committed sources were used.
- Verify `configs/project/workflow_status.csv` changes.
- Verify `PROJECT_STATE.md` consistency.
- Verify `ROADMAP.md` consistency.
- Verify locked boundaries remain locked.
- Verify no forbidden outputs were created.
- Verify no committed evidence was deleted.
- Verify no stale/demo fixture use.
- Verify no-lookahead and future-return leakage scans.
- Verify artifact size limits.
- Verify Windows-compatible commands and paths.
- Verify validation logs and command output.
- Verify fresh-clone result when required.

## Review Outcomes

Main Codex records one outcome:

- `merge_recommended`
- `request_changes`
- `reject`
- `needs_user_decision`

The user remains final authority for merge, unlock, destructive-change, and
scientific-conclusion decisions.

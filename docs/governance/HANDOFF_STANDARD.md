# Handoff Standard

The standard structure every Codex Max goal handoff must follow, so Main Codex and the User can review any goal consistently. Governance only.

## Required handoff fields

A handoff (`outputs/handoffs/<goal-id>_handoff.md`) must include:

- **Repository, base branch, base commit, work branch, commit** (final SHA on the work branch).
- **Files read** — the authoritative files consulted, in the required reading order when the goal defines one.
- **Confirmations**: GitHub-only source; Windows-compatible operation; remote checkpoint refs unchanged; local bundle/lake/cache not used.
- **Validation commands run and result** — each command with its real exit code; overall PASS / PASS_WITH_WARNINGS / FAIL.
- **Locked-boundary result** — the locks verified from the committed HEAD `workflow_status.csv`, plus `ready_factor_count`.
- **Warnings** — every non-blocking warning, including environmental ones (validation residue reverted, transient network flakes, eol noise).
- **Readiness** — whether the goal's objective is met and what, if anything, remains.
- **Explicit statements** (verbatim, all required):
  - No scientific outputs were changed.
  - No workflow locks were changed.
  - Codex Max did not choose the next goal.
  - Local Mac paths, local bundle, local lake, and local cache are prohibited; Codex Max must not use them.
  - No token or credential was printed, saved, logged, committed, echoed, requested, or exposed.

## Companion evidence

Each goal also produces:

- `outputs/audits/<goal-id>_report.md` — the full report (goal status, root cause if a repair, files changed, validation table, lock verification, forbidden-output scan, credential result, final git status, recommended next action).
- `outputs/audits/<goal-id>_manifest.json` — machine-readable manifest with at minimum: `goal_id`, `run_mode`, `repository`, `branch`, `commit`, `base_branch`, `work_branch`, `files_changed`, `validation_commands`, `validation_status`, `workflow_locks_preserved`, `ready_factor_count_observed`, `forbidden_outputs_created`, `github_only_source_confirmed`, `windows_compatible_confirmed`, `local_mac_path_used`, `local_bundle_used`, `local_lake_used`, `local_provider_cache_used`, `token_or_credential_exposed`, `recommended_next_action`, `non_actionable_disclaimer`.

## Operating note: validation is not read-only

Replayed gate runners rewrite tracked artifacts in place, and some embed environment-dependent values (provider availability, local data root, runner-generated text). Therefore:

1. Run validation, then **revert all residue** (`git restore` / `git clean` on `outputs/`, `configs/`, `docs/`, `data/`).
2. Stage **only** the files the goal intended to change.
3. Confirm final `git status` is clean and the commit contains exactly the intended file set.
4. Never run `git restore` while a validation job is still writing — it corrupts the run.

## Final-response fields

When reporting a goal to the User, return: Branch, Commit, Base, Validation, Files changed, Warnings, Credential exposure (and Root cause fixed: yes/no for repair goals).

# Pull Request Review Checklist

Standalone checklist Main Codex (and any reviewer) applies before a PR into `project-current` is approved. Mirrors and expands the inline checklist in `.github/PULL_REQUEST_TEMPLATE.md`. Governance only.

## A. Lineage and branch discipline

- [ ] Base branch is `project-current`.
- [ ] Base commit equals the commit stated in the goal Issue.
- [ ] Worker branch is `codex-max/<goal-id>` (unless explicitly authorized otherwise).
- [ ] No direct push to `project-current`; no force push; no history rewrite.
- [ ] Reviewer is not the PR author (no self-approval).

## B. Scope and boundaries

- [ ] Only files allowed by the Issue were changed; unexpected changes are explained.
- [ ] No workflow locks changed: DataExpansion, Quant04, RecTiering, GOAL-10B.4, position-band validation, GOAL-10D, dashboard/frontend remain `locked_future`.
- [ ] Trading, broker, production, local-lake, factor-mining remain locked; DQN/RL remains deleted from active mainline; V2 factor mining remains `planned_locked`.
- [ ] `ready_factor_count` unchanged (0 unless the User authorized a change).
- [ ] No scientific conclusions, factor classifications, provider evidence, or generated scientific evidence changed by a mechanics/governance goal.
- [ ] Checkpoint branch/tag unchanged (`checkpoint/arch03-stable-310559`, `checkpoint-arch03-stable-310559` → `310559ae18bbf203e795c1d66bc7181a6b11c14a`).

## C. Forbidden outputs

- [ ] No recommendation rows, position rows, BUY/SELL/HOLD, target prices/weights, portfolio weights/returns/equity curves, or order quantities.
- [ ] No dashboard/frontend artifacts.
- [ ] No live data fetched; provider network remains disabled by default.
- [ ] No committed file ≥ 95 MiB.
- [ ] No committed evidence deleted; no stale/demo fixtures used.

## D. Source-of-truth and environment

- [ ] Only GitHub-committed artifacts used as sources.
- [ ] Codex Max must not rely on any local Mac path, local bundle, local lake, or local provider cache; these are prohibited as dependencies.
- [ ] Windows compatibility respected; no unsafe `str(Path.relative_to(root))` repo-path comparison patterns (`audit_windows_compatibility_policy.py` passes).

## E. Validation evidence

- [ ] Required validation commands were run on Windows with real exit codes recorded.
- [ ] pytest, `run_program_validation_profile.py`, and `audit_workflow_status.py` pass (or only documented, non-blocking warnings remain).
- [ ] Any environmental warnings (validation residue reverted, transient network flakes) are documented and shown to pass on a clean tree.
- [ ] Handoff, report, and manifest are attached and internally consistent.

## F. Credential hygiene

- [ ] No token or credential printed, saved, logged, committed, echoed, or exposed.
- [ ] Remote uses plain HTTPS with no embedded credentials.

## Outcome

- [ ] **Approve** — all boxes checked, or unchecked boxes are explicitly justified and accepted by the User.
- [ ] **Request changes** — one or more boundary or validation items fail.

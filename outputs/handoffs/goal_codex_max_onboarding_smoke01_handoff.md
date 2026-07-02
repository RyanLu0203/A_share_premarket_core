# GOAL-CODEX-MAX-ONBOARDING-SMOKE-01 Handoff

- Repository: `RyanLu0203/A_share_premarket_core` (GitHub, plain HTTPS)
- Base branch: `project-current`
- Base commit: `823b50619aca52723d4bcfc7542674a697af60af` (verified equal to `origin/project-current` before any file creation)
- Work branch: `codex-max/onboarding-smoke01` (the only branch pushed; nothing pushed to `project-current`)
- Commit: one commit containing only the three allowed smoke evidence files, message `Add Codex Max onboarding smoke evidence`

## Files read (required order, all 23 in full)

CODEX.md; AGENTS.md; PROJECT_STATE.md; ROADMAP.md; configs/project/workflow_status.csv; docs/governance/NEW_CODEX_ONBOARDING.md; docs/governance/CODEX_MAX_REMOTE_WINDOWS_PROTOCOL.md; docs/governance/CODEX_MAX_OPERATING_PROTOCOL.md; docs/governance/GITHUB_ONLY_SOURCE_POLICY.md; docs/governance/WINDOWS_COMPATIBILITY_POLICY.md; docs/governance/MAIN_CODEX_REVIEW_PROTOCOL.md; docs/governance/PROJECT_AUTHORITY_MODEL.md; docs/governance/GOAL_QUEUE.md; docs/governance/LOCKED_BOUNDARIES.md; docs/governance/AUTHORITATIVE_STATE_FILES.md; docs/governance/PROJECT_STATE_UPDATE_POLICY.md; docs/governance/REMOTE_CHECKPOINT_AND_ROLLBACK_POLICY.md; outputs/audits/current_project_snapshot.md; outputs/audits/goal_codex_operating_system01_report.md; outputs/audits/goal_repository_checkpoint01_report.md; outputs/audits/goal_architecture_refactor03_report.md; outputs/audits/goal_regime_label_research01_report.md; outputs/audits/goal_quant_research03_refined_alpha_evaluation_report.md

## Confirmations

- GitHub-only source: CONFIRMED. Only GitHub-committed artifacts used; no local Mac paths, no local git bundle, no local data lake, no local provider cache, no uncommitted local state, no stale `main`.
- Windows-compatible operation: CONFIRMED for onboarding and evidence production (remote Windows, Python 3.9.13). Two environment notes (session temp directory redirection; Windows MAX_PATH avoidance via short temp path) are documented in the report and changed no repo file.
- Remote checkpoint: branch `checkpoint/arch03-stable-310559` and annotated tag `checkpoint-arch03-stable-310559` both still resolve to `310559ae18bbf203e795c1d66bc7181a6b11c14a`; untouched.
- Local bundle: user-private only, not visible from this environment, not used, not a dependency.

## Validation commands run and result

compileall PASS; pytest FAIL (105 failed / 171 passed); audit_codex_operating_system01 PASS; audit_github_only_source_policy PASS; audit_windows_compatibility_policy PASS; audit_destructive_changes PASS; check_latest_branch_state BLOCKED pre-push (upstream missing, expected; re-run after push); audit_repository_checkpoint01 PASS (pristine tree); run_program_validation_profile FAIL (79/115 replayed commands non-PASS); run_safety_gate PASS; run_adapter_audit PASS; run_workflow_diagnostics PASS; audit_workflow_status FAIL; plus audit_feature_label_leakage PASS (no-lookahead scan).

**Validation result: FAIL in this Windows environment, with a single fully diagnosed root cause** — a Windows path-separator defect in `src/ashare_premarket/validation/workflow_status.py` (`_unexpected_goal10b_backtest_outputs` compares backslash `relative_to` strings against a forward-slash allowlist, so `run_workflow_status_audit()` always returns False on Windows and cascades through pytest and the validation profile). Verified by an in-memory POSIX-comparison patch that makes the audit pass on the pristine tree. ~20 similar `relative_to` usages under `src/` need the same sweep. No source file was modified by this smoke goal. See report section 15 (W1–W5) for the full warning list, including that replayed gate runners rewrite ~190 tracked files in place during validation runs (all runtime mutations were reverted before commit).

## Locked-boundary result

All locks preserved and verified from the committed HEAD `configs/project/workflow_status.csv`: DataExpansion, Quant04, Rec Tiering, GOAL-10B.4, position-band validation, GOAL-10D, dashboard/frontend, paper/live trading, broker, production DB writes, production model promotion, signal/portfolio backtests all `locked_future`; DQN/RL `deleted_from_active_mainline`; V2 factor mining `planned_locked`; local-lake prohibited per LOCKED_BOUNDARIES.md. Ready factor count remains `0`.

## Readiness

- Codex Max is ready for assigned development goals in governance/compliance terms (onboarding, branch discipline, lock preservation, evidence production all demonstrated).
- Codex Max is NOT yet ready for Windows-based development goals that require the full validation suite, until the W1 path-separator repair goal is authorized and merged.

## Explicit statements

- No scientific outputs were changed.
- No workflow locks were changed.
- Codex Max did not choose the next goal; the recommended next action (review, then a W1 repair goal before GOAL-DATA-EXPANSION-RESEARCH-01) is a recommendation for Main Codex review only.
- No local Mac paths, no local bundle, no local lake, and no local cache were used.
- No token or credential was printed, saved, logged, committed, echoed, requested, or exposed.

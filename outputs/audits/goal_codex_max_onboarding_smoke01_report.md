# GOAL-CODEX-MAX-ONBOARDING-SMOKE-01 Report

Remote Windows, GitHub-only compliance gate. Smoke test only: no research, data expansion, modeling, recommendation, dashboard, or trading work was performed.

## 1. Goal status

- GOAL-CODEX-MAX-ONBOARDING-SMOKE-01 = `completed_smoke_test` / `PASS_WITH_WARNINGS`
- Validation result in this environment: `FAIL` (3 of 13 required commands fail; one fully diagnosed root cause, documented in section 15; no validation was bypassed; no replacement commands were invented; DataExpansion was NOT started)

## 2. Codex Max role acknowledgement

Codex Max operated as a high-capacity executor for this explicitly assigned goal only. User remains final authority; Main Codex remains program brain, reviewer, integrator, and workflow controller. Codex Max did not choose any next goal, did not unlock any workflow stage, did not delete committed evidence, and did not rewrite any prior scientific conclusion.

## 3. GitHub-only source confirmation

- Repository cloned over plain HTTPS from `https://github.com/RyanLu0203/A_share_premarket_core.git`.
- Authoritative base: remote branch `project-current` at commit `823b50619aca52723d4bcfc7542674a697af60af` (verified equal to `origin/project-current` after `git fetch --all --tags`).
- Only GitHub-committed artifacts were used as code, config, docs, and evidence sources.
- Not used: local Mac paths (`/Users/luxinyu/...`), local git bundle backups, local data lake, local provider caches, local uncommitted files, local-only environment variables, stale default `main` (never checked out).

## 4. Windows-compatible environment confirmation

- Environment: remote Windows (win32), Git Bash + PowerShell available, Python 3.9.13 (`requires-python >= 3.9` satisfied), pytest 8.4.2.
- Environment note A: the per-user default temp directory was not writable in this sandboxed session; `TMP`/`TEMP` were redirected to a short local directory outside the repository for all test/validation runs.
- Environment note B: an initial redirected temp path that was too long triggered Windows `MAX_PATH` failures (`WinError 206`) inside test fixtures; resolved by using a short temp path. Neither note modified any repository file.

## 5. Files read (in required order)

1. CODEX.md
2. AGENTS.md
3. PROJECT_STATE.md
4. ROADMAP.md
5. configs/project/workflow_status.csv
6. docs/governance/NEW_CODEX_ONBOARDING.md
7. docs/governance/CODEX_MAX_REMOTE_WINDOWS_PROTOCOL.md
8. docs/governance/CODEX_MAX_OPERATING_PROTOCOL.md
9. docs/governance/GITHUB_ONLY_SOURCE_POLICY.md
10. docs/governance/WINDOWS_COMPATIBILITY_POLICY.md
11. docs/governance/MAIN_CODEX_REVIEW_PROTOCOL.md
12. docs/governance/PROJECT_AUTHORITY_MODEL.md
13. docs/governance/GOAL_QUEUE.md
14. docs/governance/LOCKED_BOUNDARIES.md
15. docs/governance/AUTHORITATIVE_STATE_FILES.md
16. docs/governance/PROJECT_STATE_UPDATE_POLICY.md
17. docs/governance/REMOTE_CHECKPOINT_AND_ROLLBACK_POLICY.md
18. outputs/audits/current_project_snapshot.md
19. outputs/audits/goal_codex_operating_system01_report.md
20. outputs/audits/goal_repository_checkpoint01_report.md
21. outputs/audits/goal_architecture_refactor03_report.md
22. outputs/audits/goal_regime_label_research01_report.md
23. outputs/audits/goal_quant_research03_refined_alpha_evaluation_report.md

All 23 files exist and were read in full.

## 6. Branch and commit verification

- Base branch: `project-current`; base commit `823b50619aca52723d4bcfc7542674a697af60af` == `origin/project-current` (verified before any file creation).
- Work branch: `codex-max/onboarding-smoke01`, created from the verified base commit.
- Stale `main` was not used at any point.

## 7. Remote checkpoint verification

- Remote branch `checkpoint/arch03-stable-310559` -> `310559ae18bbf203e795c1d66bc7181a6b11c14a` (exact match).
- Remote annotated tag `checkpoint-arch03-stable-310559` (tag object `0ba05956d11336636e1482bef30d873c5dfe79ee`) peels (`^{}`) to `310559ae18bbf203e795c1d66bc7181a6b11c14a` (exact match).
- Both refs are unchanged and were not modified by this goal.

## 8. Local bundle non-dependency confirmation

The user-private bundle backup is not visible from this environment and was not used, referenced, or required. `scripts/audit_repository_checkpoint01.py` records the expected warning "user-private bundle not visible from this environment" and still passes; the bundle is documented as user-private only and is not a Codex Max input, onboarding dependency, or validation dependency.

## 9. Workflow lock verification

Verified from the committed HEAD version of `configs/project/workflow_status.csv` (not from a runtime-mutated working copy; see warning W2):

| workflow_id | status |
| --- | --- |
| goal_data_expansion_research01_market_regime_data_expansion_gate | locked_future |
| goal_quant_research04_regime_conditional_factor_evaluation_gate | locked_future |
| goal_rec_tiering01_recommendation_score_tiering_gate | locked_future |
| goal10b4_recommendation_backtest_revalidation | locked_future |
| goal_position_band_validation01_position_band_validation_gate | locked_future |
| goal10d_backtest_failure_attribution_gate | locked_future |
| dashboard_daily_report | locked_future |
| paper_trading_journal | locked_future |
| broker_live_trading | locked_future |
| production_db_writes | locked_future |
| production_model_promotion | locked_future |
| signal_backtest | locked_future |
| portfolio_backtest | locked_future |
| dqn_rl_mainline | deleted_from_active_mainline |
| v2_factor_research_upgrade (factor mining) | planned_locked |

Local-lake usage remains prohibited per docs/governance/LOCKED_BOUNDARIES.md and GITHUB_ONLY_SOURCE_POLICY.md. No lock was changed by this goal: the final commit contains only the three allowed evidence files.

## 10. Current implemented goals

Per PROJECT_STATE.md / CODEX.md / current_project_snapshot.md: Provider02B, DC03, GOAL-10B.3, Risk01/Risk011, Quant01, MVP01, Alpha Candidate 01, Quant02, Alpha Refinement 01, Alpha Candidate 02, Quant03, Regime01, Arch03, GOAL-REPOSITORY-CHECKPOINT-01, GOAL-CODEX-OPERATING-SYSTEM-01 — all in documented restricted modes (review-only / research-only / design-only / infrastructure-only / governance-only), mostly `PASS_WITH_WARNINGS`.

## 11. Current locked goals

DataExpansion (GOAL-DATA-EXPANSION-RESEARCH-01), Quant04, Rec Tiering (GOAL-REC-TIERING-01), GOAL-10B.4, position-band validation (GOAL-POSITION-BAND-VALIDATION-01), GOAL-10D, GOAL-DATA-PANEL-02, dashboard/frontend (Dashboard / Daily Report UI), signal/portfolio backtests, paper/live trading, broker, production DB writes, production model promotion, local-lake, factor-mining (V2, planned_locked), DQN/RL (deleted_from_active_mainline). All remain locked or deleted; none were unlocked by this goal.

## 12. Current ready factor status

Ready factor count = `0` (PROJECT_STATE.md; GOAL-QUANT-RESEARCH-02 and GOAL-QUANT-RESEARCH-03 reports; current_project_snapshot.md). Not changed by this goal.

## 13. Provider and AKShare catalog status

- `configs/providers/provider_registry.yaml` exists; `network_default: "disabled"`; opt-in requires `ASHARE_ALLOW_NETWORK_INGESTION=1`; 4 provider entries.
- `configs/providers/akshare_source_catalog.yaml` exists; mode `metadata_only_no_live_fetch`; 70 source rows (matches the "AKShare source catalog 70 rows" claim in PROJECT_STATE.md).
- No live data and no full AKShare data were fetched by this goal.

## 14. Validation commands run

All final results are from runs started on a pristine worktree with real (unpiped) exit codes:

| # | Command | Result |
| --- | --- | --- |
| 1 | python -m compileall -q . | PASS (exit 0) |
| 2 | python -m pytest tests -q | FAIL (exit 1; 105 failed / 171 passed; root cause W1) |
| 3 | python scripts/audit_codex_operating_system01.py | PASS |
| 4 | python scripts/audit_github_only_source_policy.py | PASS |
| 5 | python scripts/audit_windows_compatibility_policy.py | PASS (but see W3) |
| 6 | python scripts/audit_destructive_changes.py | PASS |
| 7 | python scripts/check_latest_branch_state.py | BLOCKED before push (upstream missing — expected for a new work branch; see W4) |
| 8 | python scripts/audit_repository_checkpoint01.py | PASS (pristine tree; expected bundle-visibility warning only) |
| 9 | python scripts/run_program_validation_profile.py | FAIL (exit 1; 79 of 115 replayed commands non-PASS; root cause W1) |
| 10 | python scripts/run_safety_gate.py | PASS |
| 11 | python scripts/run_adapter_audit.py | PASS |
| 12 | python scripts/run_workflow_diagnostics.py | PASS |
| 13 | python scripts/audit_workflow_status.py | FAIL (exit 1; root cause W1) |
| + | python scripts/audit_feature_label_leakage.py (no-lookahead scan) | PASS |

Audit coverage confirmation for required scan classes: forbidden-output scan (audit_repository_checkpoint01 + run_safety_gate + audit_destructive_changes, PASS); demo/stale fixture scans (implemented in src backtest/diagnostics modules, exercised by the pytest suite and gate audits); row-count scans (per-goal audits replayed by the validation profile); token/secret scan (safety gate raw-payload checks, provider no-token-print policies, plus a manual pattern scan of the three new evidence files); no-lookahead / future-return leakage scan (audit_feature_label_leakage.py, PASS); GitHub-only scan (PASS); Windows compatibility scan (PASS, with gap W3); artifact size scan >= 95 MiB (checkpoint audit, PASS); dashboard/frontend artifact scan (checkpoint audit .html check + .gitignore, PASS); recommendation/position output scan (checkpoint audit forbidden paths + lock verification, PASS).

## 15. Warnings, missing commands, or failures

- **W1 (root cause of all three validation failures): Windows path-separator defect in the repo's own validation code.** `_unexpected_goal10b_backtest_outputs` in `src/ashare_premarket/validation/workflow_status.py` compares `str(Path.relative_to(root))` — which yields backslash-separated paths on Windows — against a forward-slash allowlist. Every committed file under `outputs/backtest/` is therefore reported as "unexpected", `run_workflow_status_audit()` returns False on any Windows machine, and every gate runner that ends with that audit returns False. This cascades into: pytest 105/276 failures, `audit_workflow_status.py` exit 1, and `run_program_validation_profile.py` exit 1 (79/115 non-PASS). Diagnosis was verified: an in-memory patch of only this helper (POSIX-normalized comparison) makes `run_workflow_status_audit()` return True on the pristine tree. Approximately 20 additional `str(...relative_to(root))` usages without `.as_posix()` exist under `src/` and should be swept in the same repair goal. No source file was modified by this smoke goal.
- **W2: validation is not read-only.** Replayed gate runners rewrite ~190 tracked files in place during pytest/profile runs (configs/project/workflow_status.csv, configs/project/locked_capabilities.json, docs, committed outputs). When a gate evaluation fails — as it does on Windows due to W1 — the rewritten content differs from the committed content, leaving a dirty worktree, and one interrupted early run truncated regenerated CSVs. All runtime mutations were fully reverted with `git restore` / `git clean` before commit; the committed state files are byte-identical to the base commit. Main Codex should be aware of this behavior when validation is run on any non-primary environment.
- **W3:** `audit_windows_compatibility_policy.py` passes but does not detect W1 — a coverage gap in the Windows compatibility scan.
- **W4:** `check_latest_branch_state.py` reports BLOCKED before push because the new work branch has no upstream yet; it is re-run after pushing `codex-max/onboarding-smoke01` and the post-push result is reported in the handoff message.
- **W5:** session temp-directory notes (section 4).
- No required command was missing. No replacement commands were invented. Validation was not bypassed. DataExpansion was not started.

## 16. Forbidden-boundary confirmation

Created by this goal: nothing beyond the three allowed evidence files. Specifically NOT created: recommendation rows, position rows, BUY/SELL/HOLD, target prices, target weights, portfolio weights, order quantities, portfolio returns or equity curves, dashboard/frontend artifacts, trading/broker/production/local-lake/factor-mining/DQN-RL outputs. No live or full AKShare data fetched. No file >= 95 MiB committed. No force push. No history rewrite. Checkpoint branch/tag untouched. Nothing pushed to `project-current`.

## 17. Credential and token non-exposure confirmation

The remote URL is plain HTTPS with no embedded credentials; authentication is handled by the OS credential manager outside the repository. No GitHub token or credential was printed, saved, logged, echoed, requested, committed, or included in any output. The three evidence files were pattern-scanned for token/credential material before commit.

## 18. What was not changed

Source code; scientific outputs; factor outputs and classifications; risk outputs; recommendation outputs; position outputs; provider evidence; historical reports and manifests; checkpoint refs; workflow locks; CODEX.md; AGENTS.md; PROJECT_STATE.md; ROADMAP.md; configs/project/workflow_status.csv; governance docs. Ready factor count unchanged (0). Only the three allowed files were created and committed.

## 19. Whether Codex Max is ready for assigned development goals

- Governance and compliance readiness: **YES** — GitHub-only onboarding, branch discipline, lock preservation, evidence production, and credential hygiene all demonstrated.
- Windows validation readiness: **NOT YET** — until W1 is repaired, the full pytest suite and validation profile cannot pass on Windows, so development goals that require full validation should not be assigned to a Windows environment.

## 20. Recommended next action for Main Codex review

Review this smoke evidence. If accepted, authorize a small, explicitly scoped repair goal to fix W1 (POSIX-normalize the path comparison in `_unexpected_goal10b_backtest_outputs` and sweep the ~20 similar `relative_to` usages), re-run this smoke validation to confirm a green suite on Windows, and only then consider assigning GOAL-DATA-EXPANSION-RESEARCH-01. Codex Max will not proceed to any next goal without explicit assignment.

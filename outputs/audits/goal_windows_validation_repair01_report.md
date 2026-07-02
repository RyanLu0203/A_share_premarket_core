# GOAL-WINDOWS-VALIDATION-REPAIR-01 Report

Path Normalization and Audit Coverage Gate. Narrow validation repair only: no DataExpansion, Quant04, RecTiering, dashboard, trading, broker, production, local-lake, factor-mining, or DQN/RL work; no scientific outputs, factor classifications, ready factor count, recommendation/position outputs, or workflow locks changed.

## 1. Goal status

- GOAL-WINDOWS-VALIDATION-REPAIR-01 = `completed` / `PASS`
- The Windows validation failure discovered by GOAL-CODEX-MAX-ONBOARDING-SMOKE-01 is fixed and re-verified: the full pytest suite, `audit_workflow_status.py`, and `run_program_validation_profile.py` now pass on Windows.

## 2. Root cause

On Windows, repo-relative paths produced by `str(Path.relative_to(root))` use backslash separators, while the allowlists they are compared against are forward-slash string literals. `_unexpected_goal10b_backtest_outputs` in `src/ashare_premarket/validation/workflow_status.py` therefore misclassified every valid committed `outputs/backtest/` file as unexpected, `run_workflow_status_audit()` returned False on any Windows machine, and every gate runner that finishes with that audit returned False — cascading into 105 pytest failures, `audit_workflow_status.py` exit 1, and `run_program_validation_profile.py` exit 1 (79/115 replayed commands non-PASS). Eight sibling gate modules contained the same comparison pattern, and three more modules embedded native-separator relative paths into generated evidence content.

## 3. Files changed

Source repair (12 files):
- src/ashare_premarket/validation/workflow_status.py (root cause)
- src/ashare_premarket/backtest/goal10b.py (also removed the redundant `str(Path(item))` allowlist wrapper that only masked the mismatch on the comparison side)
- src/ashare_premarket/backtest/goal10b1.py
- src/ashare_premarket/backtest/goal10b2.py
- src/ashare_premarket/backtest/goal10b3.py
- src/ashare_premarket/backtest/goal10c.py
- src/ashare_premarket/contract_design/goal10a.py
- src/ashare_premarket/risk_tiering/goal_risk_tiering01.py
- src/ashare_premarket/risk_tiering/goal_risk_tiering011.py
- src/ashare_premarket/research/goal_quant_research03.py (panel part paths written into evidence)
- src/ashare_premarket/research/goal_regime_label_research01.py (oversized-output listing)
- src/ashare_premarket/runners/common.py (partitioned-CSV written-paths listing)

Audit coverage and tests:
- scripts/audit_windows_compatibility_policy.py (new source scan, section 7)
- tests/test_windows_path_normalization.py (new, section 6)

Evidence files: this report, the manifest, and the handoff.

## 4. Path normalization method used

`Path.relative_to(root).as_posix()` inline at every call site — the goal's preferred primitive and the repo's own dominant idiom (26 pre-existing call sites already use exactly this form, e.g. in workflow_cleanliness). A helper was considered (`core/paths.py` already exposes `rel()`); it was deliberately NOT used because `rel()` applies `resolve()` to both arguments, which (a) differs behaviorally from the original code if any repo directory is a junction/symlink and (b) diverges from the established inline idiom. The inline form is byte-identical to the old behavior on POSIX and differs on Windows only in the separator — which is the fix. It also adds no import lines, so committed architecture-inventory line counts stay aligned (except goal10b.py, net −1 line; see warning W-E).

## 5. Similar relative_to usages found and handled

Repo-wide sweep of `relative_to` under `src/`:
- 9 comparison sites against forward-slash allowlists (all fixed): workflow_status.py, goal10a, goal10b, goal10b1, goal10b2, goal10b3, goal10c, goal_risk_tiering01, goal_risk_tiering011.
- 3 evidence-content sites (fixed for cross-platform byte-identical regeneration): goal_quant_research03 panel part paths, goal_regime_label_research01 oversized-output names, runners/common.py written-file listing.
- `storage/policy.py` `_is_relative_to()` uses `relative_to` correctly as a containment check (try/except, no string comparison) — intentionally unchanged.
- `scripts/audit_github_only_source_policy.py:64` already self-normalizes via `.replace("\\", "/")` — unchanged (outside allowed file set) and exempted by the new scan.
- Zero `str(...relative_to(...))` occurrences remain under `src/`.

## 6. Tests added or updated

New file `tests/test_windows_path_normalization.py` (4 tests, all passing):
1. `test_relative_to_as_posix_returns_forward_slashes` — the normalization primitive yields forward slashes on every platform.
2. `test_relative_to_as_posix_matches_forward_slash_allowlist_entries` — a real allowlist entry round-trips exactly.
3. `test_committed_backtest_outputs_are_recognized_by_workflow_audit` — `_unexpected_goal10b_backtest_outputs(ROOT) == []` on the committed repo (the direct regression test for the smoke-test failure).
4. `test_no_unsafe_str_relative_to_pattern_under_src` — scans all of `src/` and fails if any `str(...relative_to(...))` pattern reappears (no exemptions).

## 7. Windows compatibility audit improvement

`scripts/audit_windows_compatibility_policy.py` now includes `_scan_source_path_comparisons()`: it scans every `.py` under `src/` and `scripts/` (excluding itself and `__pycache__`) and reports a failure for any `str(X.relative_to(...))` occurrence, exempting lines that already normalize via `as_posix` or `.replace("\\", "/")`; non-UTF-8 files are reported as failures rather than crashing the audit. The smoke test's W3 coverage gap is closed for the pattern class that caused this incident. Known limitations (from adversarial review, all display-only in current code): f-string interpolation of `relative_to` results and two-step `x = path.relative_to(root); str(x)` forms are not matched; the exemption is a line-substring check. `src/` is additionally covered by the stricter no-exemption test in section 6.

## 8. Validation command results

All final results from runs on this Windows environment with the repair applied (real, unpiped exit codes; temp redirected to a short local path outside the repo as documented in the smoke report):

| Command | Before repair | After repair |
| --- | --- | --- |
| python -m compileall -q . | PASS | PASS (exit 0) |
| python -m pytest tests -q | FAIL: 105 failed / 171 passed | **PASS: 280 passed** (276 pre-existing + 4 new; exit 0) |
| python scripts/audit_codex_operating_system01.py | PASS | PASS |
| python scripts/audit_github_only_source_policy.py | PASS | PASS |
| python scripts/audit_windows_compatibility_policy.py | PASS (gap W3) | PASS (with new source scan active) |
| python scripts/audit_destructive_changes.py | PASS | PASS |
| python scripts/check_latest_branch_state.py | BLOCKED pre-push (expected) | PASS after push (re-run recorded in handoff) |
| python scripts/audit_repository_checkpoint01.py | PASS | PASS (exit 0; see warning W-C on transient network flakes during intermediate attempts) |
| python scripts/run_program_validation_profile.py | FAIL: 79/115 non-PASS | **PASS: 115/115 PASS** (exit 0) |
| python scripts/run_safety_gate.py | PASS | PASS |
| python scripts/run_adapter_audit.py | PASS | PASS |
| python scripts/run_workflow_diagnostics.py | PASS | PASS |
| python scripts/audit_workflow_status.py | FAIL (exit 1) | **PASS (exit 0)** |
| python scripts/audit_feature_label_leakage.py | PASS | PASS |

An independent three-lens adversarial review (correctness / governance / completeness) of the repair diff was run before commit; its actionable findings (avoid `resolve()`-based helper, guard non-UTF-8 reads in the new scan, revert validation residue before commit) were applied, and its remaining notes are documented as warnings below.

## 9. Workflow lock verification

Verified from the committed HEAD `configs/project/workflow_status.csv` at base `86d36a17c3fa4943e8229ff625f6427cc809dd1a`: all 13 downstream gates remain `locked_future` (DataExpansion, Quant04, Rec Tiering, GOAL-10B.4, position-band validation, GOAL-10D, dashboard_daily_report, paper_trading_journal, broker_live_trading, production_db_writes, production_model_promotion, signal_backtest, portfolio_backtest); `dqn_rl_mainline` remains `deleted_from_active_mainline`; `v2_factor_research_upgrade` (factor mining) remains `planned_locked`. The commit does not touch `configs/project/workflow_status.csv` or any lock value.

## 10. Ready factor count verification

Ready factor count remains `0` (PROJECT_STATE.md and Quant02/Quant03 evidence unchanged). Nothing in this repair touches factor classifications or readiness.

## 11. Forbidden-output scan result

No recommendation rows, position rows, BUY/SELL/HOLD, target prices/weights, portfolio weights/returns/equity curves, order quantities, dashboard/frontend artifacts, or trading/broker/production/local-lake/factor-mining/DQN-RL outputs were created. No live data fetched. Checkpoint branch `checkpoint/arch03-stable-310559` and tag `checkpoint-arch03-stable-310559` remain at `310559ae18bbf203e795c1d66bc7181a6b11c14a`, untouched. `run_safety_gate.py` and `audit_destructive_changes.py` pass.

## 12. Credential exposure result

None. Remote is plain HTTPS; authentication stays in the OS credential manager. No token or credential was printed, saved, logged, echoed, requested, committed, or exposed; the three evidence files were pattern-scanned before commit.

## 13. Final git status

Clean after commit and push (only the intended repair, tests, audit coverage, and the three evidence files were committed; all validation-run residue was reverted before commit — see warning W-B). The post-push `check_latest_branch_state.py` result is recorded in the handoff.

## 14. Recommended next action for Main Codex review

Review and merge this repair branch, then re-run the smoke validation once on a Windows environment for independent confirmation. Follow-up candidates surfaced by this goal (for Main Codex to prioritize, not started here): (W-B) workflow-diagnostics runner regenerates goal10d/dashboard unlock-condition text at goal10c-era values, diverging from the committed arch03-era text — runner-embedded state needs a governance sync; consider a `.gitattributes` eol policy to eliminate Windows eol-only false-modified noise (W-D); optionally extend the pattern guard to f-string/two-step forms. After merge, GOAL-DATA-EXPANSION-RESEARCH-01 is unblocked from the Windows-validation standpoint.

## Warnings

- **W-A (guard blind spots, from adversarial review):** the new audit scan and regression test match the literal `str(...relative_to(...))` form only; f-string interpolation and two-step variants are not matched (all current instances are display-only). The audit's exemption is a line-substring check and could in principle be bypassed by a comment containing `as_posix`; `src/` is additionally covered by the no-exemption test.
- **W-B (validation is not read-only — pre-existing):** replayed gate runners rewrite tracked artifacts in place. On this machine, regenerated artifacts embed environment-dependent values: provider availability flags flip to false where optional packages (baostock/efinance/tushare/yfinance) are not installed; the storage manifest embeds the local data root; workflow diagnostics writes goal10c-era unlock-condition text for the goal10d/dashboard rows, diverging from the committed arch03-era text. All residue was reverted before commit; nothing outside the intended file set was committed.
- **W-C (network flakes):** intermediate `audit_repository_checkpoint01.py` attempts intermittently received empty `git ls-remote` responses (local GitHub connectivity resets); direct ls-remote verification returned correct refs 5/5 and the final audit run passed with exit 0.
- **W-D (eol-only status noise on Windows):** with `core.autocrlf=true`, files rewritten by runners with LF show as "modified" with empty content diffs (`git diff --numstat` empty). Verified content-identical; candidate for a future `.gitattributes` governance goal.
- **W-E (architecture inventory line counts):** the inline fix adds no lines, so committed arch03 module-inventory line counts stay aligned for 11 of 12 files; `goal10b.py` is net −1 line (redundant wrapper removed), leaving that single inventory row one line stale until a future goal regenerates the inventory (outside this goal's allowed file set).

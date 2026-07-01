# Codex Max Operating Protocol

Codex Max is a remote Windows-compatible executor, not the project planner.
`docs/governance/CODEX_MAX_REMOTE_WINDOWS_PROTOCOL.md` is the detailed runtime
protocol.

## Required Startup

1. Clone from GitHub.
2. Checkout `project-current`.
3. Read `CODEX.md` first.
4. Verify latest remote commit and branch against `CODEX.md` and
   `PROJECT_STATE.md`.
5. Read `PROJECT_STATE.md`.
6. Read `ROADMAP.md`.
7. Read `configs/project/workflow_status.csv`.
8. Read `docs/governance/GITHUB_ONLY_SOURCE_POLICY.md`.
9. Read `docs/governance/WINDOWS_COMPATIBILITY_POLICY.md`.
10. Read `docs/governance/GOAL_QUEUE.md`.
11. Read `docs/governance/LOCKED_BOUNDARIES.md`.
12. Create `codex-max/<goal-id>` unless explicitly authorized otherwise.
13. Execute only the explicitly assigned goal.
14. Preserve all locked boundaries.
15. Run required validation.
16. Push work to the review branch.
17. Produce the standardized handoff.
18. Leave clean git status.

## Prohibited Actions

Codex Max must not:

1. Start from stale `main` unless explicitly instructed.
2. Use local Mac paths.
3. Use `/Users/luxinyu` paths.
4. Use local bundle backup.
5. Use local uncommitted data.
6. Use local provider caches.
7. Use local-lake data.
8. Choose the next goal independently.
9. Unlock downstream stages.
10. Delete committed evidence without explicit destructive-change approval.
11. Rewrite previous scientific conclusions.
12. Change ready factor count.
13. Create recommendation, position, target price, order quantity, portfolio
    return, equity curve, dashboard, broker, trading, production, local-lake,
    factor-mining, or DQN/RL outputs.
14. Fetch full live data unless the assigned goal explicitly allows network
    opt-in.
15. Bypass provider registry, AKShare source catalog, safety gate, or
    no-lookahead policy.

## Required Handoff

Every handoff must name the goal, base branch, worker branch, base commit,
changed files, outputs, validation commands, scans, boundary confirmations,
GitHub-only source confirmation, Windows compatibility confirmation,
fresh-clone status when required, and any review questions.

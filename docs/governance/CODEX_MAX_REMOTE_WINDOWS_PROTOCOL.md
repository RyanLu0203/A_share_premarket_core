# Codex Max Remote Windows Protocol

Codex Max must operate from GitHub and remain Windows-compatible.

## Required Steps

1. Clone from GitHub.
2. Checkout `project-current`.
3. Verify current commit against `CODEX.md` and `PROJECT_STATE.md`.
4. Read `CODEX.md` first.
5. Read `PROJECT_STATE.md`.
6. Read `ROADMAP.md`.
7. Read `configs/project/workflow_status.csv`.
8. Read `docs/governance/GOAL_QUEUE.md`.
9. Read `docs/governance/LOCKED_BOUNDARIES.md`.
10. Execute only explicitly assigned goals.
11. Create a new remote branch for work: `codex-max/<goal-id>`.
12. Push work to that branch.
13. Never push directly to `project-current` unless explicitly authorized.
14. Produce handoff and validation report.
15. Leave clean working tree.
16. Avoid all local-only data and local-only paths.

## Prohibited Actions

Codex Max must not:

1. Use local Mac paths.
2. Use `/Users/luxinyu` paths.
3. Use local bundle backup.
4. Use local uncommitted data.
5. Use stale `main`.
6. Choose next goal independently.
7. Unlock downstream stages.
8. Delete committed evidence.
9. Rewrite scientific conclusions.
10. Bypass provider registry.
11. Bypass AKShare source catalog.
12. Bypass safety gate.
13. Bypass no-lookahead policy.
14. Fetch full live data unless explicitly assigned.
15. Create recommendation, position, dashboard, trading, broker, production,
    local-lake, factor-mining, or DQN/RL outputs.

## Command Style

Prefer cross-platform commands:

```bash
python -m compileall -q .
python -m pytest tests -q
python scripts/audit_codex_operating_system01.py
```

Avoid adding required Codex Max steps that depend on bash-only shell behavior.

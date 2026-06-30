# Codex Max Entrypoint

Codex Max should start from:

```bash
git fetch origin
git switch project-current
```

Codex Max must read `CODEX.md` first, then `PROJECT_STATE.md`, `ROADMAP.md`,
and `docs/governance/REPOSITORY_CHECKPOINTS.md`.

## Current Branch Policy

- Authoritative current branch: `project-current`
- Current stable checkpoint branch: `checkpoint/arch03-stable-310559`
- Current stable checkpoint tag: `checkpoint-arch03-stable-310559`
- Current stable commit: `310559ae18bbf203e795c1d66bc7181a6b11c14a`

`project-current` is an entrypoint branch. It may fast-forward from the stable
Arch03 commit to governance-only documentation commits so future sessions can
read checkpoint and rollback instructions. The frozen checkpoint branch and tag
remain the immutable rollback point.

## Boundaries

Codex Max must not start from stale `main` unless explicitly instructed.
Codex Max must not unlock DataExpansion, Quant04, Rec Tiering, GOAL-10B.4,
position-band validation, GOAL-10D, dashboard/frontend, trading, broker,
production, local-lake, factor-mining, or DQN/RL without a future explicit goal.

The next governance goal is `GOAL-CODEX-OPERATING-SYSTEM-01`. The next
research/data goal after governance is
`GOAL-DATA-EXPANSION-RESEARCH-01-MARKET-REGIME-DATA-EXPANSION-GATE`.

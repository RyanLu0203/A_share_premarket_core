# Repository Checkpoints

## GOAL-REPOSITORY-CHECKPOINT-01 Arch03 Stable Snapshot

- Checkpoint name: `GOAL-REPOSITORY-CHECKPOINT-01-ARCH03-STABLE-SNAPSHOT-AND-CODEX-MAX-ENTRYPOINT-GATE`
- Stable commit: `310559ae18bbf203e795c1d66bc7181a6b11c14a`
- Source branch: `codex/cloakbrowser-reference-tagging`
- Authoritative entrypoint branch: `project-current`
- Frozen checkpoint branch: `checkpoint/arch03-stable-310559`
- Annotated checkpoint tag: `checkpoint-arch03-stable-310559`
- Date generated: `2026-06-30`
- Validation status: `PASS_WITH_WARNINGS`
- Local bundle path: `/Users/luxinyu/Desktop/A_share_premarket_core_checkpoint_310559.bundle`
- Bundle verification status: `PASS`

The frozen checkpoint branch and annotated tag point to the exact Arch03 stable
commit. `project-current` was first created at that commit and is then allowed
to fast-forward to the governance documentation entrypoint commit so future
Codex Max sessions can clone the entrypoint docs directly.

## Rollback Command

```bash
git fetch origin
git switch -c recovery/arch03-stable checkpoint/arch03-stable-310559
```

Equivalent tag-based recovery:

```bash
git fetch origin --tags
git switch -c recovery/arch03-stable checkpoint-arch03-stable-310559
```

Bundle-based recovery:

```bash
git clone /Users/luxinyu/Desktop/A_share_premarket_core_checkpoint_310559.bundle A_share_premarket_core_recovery
cd A_share_premarket_core_recovery
git switch -c recovery/arch03-stable checkpoint/arch03-stable-310559
```

## Notes

- Do not develop on `checkpoint/arch03-stable-310559`.
- Do not move `checkpoint-arch03-stable-310559` without explicit user approval.
- Do not force-push protected or shared branches without explicit user approval.
- DataExpansion, Quant04, Rec Tiering, dashboard/frontend, trading, production,
  local-lake, factor-mining, broker, and DQN/RL remain locked.

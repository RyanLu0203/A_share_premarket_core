# Rollback Playbook

## Inspect Current State

```bash
git status --short --branch
git rev-parse HEAD
git branch --contains 310559ae18bbf203e795c1d66bc7181a6b11c14a
git tag --points-at 310559ae18bbf203e795c1d66bc7181a6b11c14a
```

## Switch To The Frozen Checkpoint Branch

```bash
git fetch origin
git switch checkpoint/arch03-stable-310559
```

This branch is read-only by convention. Do not develop directly on it.

## Create A Recovery Branch From The Checkpoint

```bash
git fetch origin
git switch -c recovery/arch03-stable checkpoint/arch03-stable-310559
```

## Restore From The Annotated Tag

```bash
git fetch origin --tags
git switch -c recovery/arch03-stable-tag checkpoint-arch03-stable-310559
```

## Restore From The Local Bundle

```bash
git bundle verify /Users/luxinyu/Desktop/A_share_premarket_core_checkpoint_310559.bundle
git clone /Users/luxinyu/Desktop/A_share_premarket_core_checkpoint_310559.bundle A_share_premarket_core_recovery
cd A_share_premarket_core_recovery
git switch -c recovery/arch03-stable checkpoint/arch03-stable-310559
```

## Warnings

- Do not force-push protected or shared branches without explicit user approval.
- Do not retag `checkpoint-arch03-stable-310559` without explicit user approval.
- Do not move `checkpoint/arch03-stable-310559`.
- Do not use rollback to unlock downstream goals.
- DataExpansion, Quant04, Rec Tiering, GOAL-10B.4, position-band validation,
  GOAL-10D, dashboard/frontend, trading, broker, production, local-lake,
  factor-mining, and DQN/RL remain locked after rollback.

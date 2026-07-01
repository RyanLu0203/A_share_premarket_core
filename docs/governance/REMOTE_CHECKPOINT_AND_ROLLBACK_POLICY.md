# Remote Checkpoint And Rollback Policy

Codex Max rollback sources are remote GitHub refs only.

## Codex Max Rollback Sources

- Remote checkpoint branch: `checkpoint/arch03-stable-310559`
- Remote checkpoint tag: `checkpoint-arch03-stable-310559`
- Stable Arch03 commit: `310559ae18bbf203e795c1d66bc7181a6b11c14a`

Recovery branch example:

```bash
git fetch origin --tags
git switch -c recovery/arch03-stable origin/checkpoint/arch03-stable-310559
```

Tag recovery example:

```bash
git fetch origin --tags
git switch -c recovery/arch03-stable-tag checkpoint-arch03-stable-310559
```

## User-Private Backup

The local Mac bundle exists only for user-private backup and is not accessible
to Codex Max. It is not part of Codex Max onboarding, validation, or required
rollback.

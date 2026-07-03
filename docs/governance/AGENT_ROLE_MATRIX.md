# Agent Role Matrix

Authoritative mapping of who may do what in GitHub-native AI collaboration on this repository. This matrix is governance only; it does not unlock any workflow stage or change any scientific conclusion. It restates and cross-references [PROJECT_AUTHORITY_MODEL.md](PROJECT_AUTHORITY_MODEL.md) and [MAIN_CODEX_REVIEW_PROTOCOL.md](MAIN_CODEX_REVIEW_PROTOCOL.md).

## Roles

| Role | Definition |
| --- | --- |
| **User** | Final authority. Owns the repository and the final unlock, approval, and merge decisions. |
| **Main Codex** | Program brain, reviewer, integrator, and workflow controller. Decides the next goal, reviews Codex Max output, and integrates. |
| **Codex Max** | High-capacity executor for explicitly assigned goals only. Does not choose the next goal and does not unlock stages. |
| **Reviewer agent (adversarial)** | An independent agent that verifies a diff against a single lens (correctness / governance / completeness). Advisory only; see [ADVERSARIAL_REVIEW_PROTOCOL.md](ADVERSARIAL_REVIEW_PROTOCOL.md). |

## Capability matrix

| Action | User | Main Codex | Codex Max | Reviewer agent |
| --- | --- | --- | --- | --- |
| Choose / prioritize the next goal | ✅ | ✅ | ❌ | ❌ |
| Open a goal Issue | ✅ | ✅ | ❌ (may draft only) | ❌ |
| Execute an explicitly assigned goal | — | ✅ | ✅ | ❌ |
| Create a `codex-max/<goal-id>` work branch | ✅ | ✅ | ✅ | ❌ |
| Push to a work branch | ✅ | ✅ | ✅ | ❌ |
| Push directly to `project-current` | ❌ (use PR) | ❌ (use PR) | ❌ | ❌ |
| Open a Pull Request | ✅ | ✅ | ✅ | ❌ |
| Approve a Pull Request | ✅ | ✅ | ❌ (never self-approve) | ❌ |
| Merge a Pull Request | ✅ | ❌ | ❌ | ❌ |
| Unlock a `locked_future` / `planned_locked` stage | ✅ | ❌ | ❌ | ❌ |
| Change scientific conclusions / `ready_factor_count` | ✅ | ❌ | ❌ | ❌ |
| Modify checkpoint refs | ⚠️ explicit approval only (destructive change) | ❌ | ❌ | ❌ |
| Run adversarial review on a diff | ✅ | ✅ | ✅ | ✅ |

## Hard invariants

1. **No self-approval.** The agent that authored or pushed a branch must not approve its own PR, even under a different account. Two-party review is mandatory (see [HUMAN_APPROVAL_GATE.md](HUMAN_APPROVAL_GATE.md)).
2. **Merge is a User action.** Only the User merges into `project-current`.
3. **Codex Max never chooses the next goal** and never unlocks a stage; it executes exactly the assigned Issue.
4. **Checkpoint refs are immutable to agents**: `checkpoint/arch03-stable-310559` and tag `checkpoint-arch03-stable-310559` are never modified by any agent. Only the User may move or retag them, with explicit approval, as a destructive change per [PROJECT_AUTHORITY_MODEL.md](PROJECT_AUTHORITY_MODEL.md).
5. **GitHub is the only source of truth**; no local Mac paths, local bundles, local lake, or local caches are dependencies (see [GITHUB_ONLY_SOURCE_POLICY.md](GITHUB_ONLY_SOURCE_POLICY.md)).

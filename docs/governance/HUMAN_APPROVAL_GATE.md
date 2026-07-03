# Human Approval Gate

Defines the mandatory human decision point before any AI-produced change enters `project-current`. Governance only.

## Principle

AI agents may draft, execute, validate, and review, but a **human (the User) makes the final approval and merge decision**. This preserves two-party control and prevents an agent from unilaterally landing its own work.

## Gate rules

1. **Merge is a User-only action.** Neither Main Codex nor Codex Max merges into `project-current`.
2. **No self-approval.** The agent that authored or pushed a branch must not approve its own PR — not through its own account and not through a second account it controls. Approval must come from a different party. This rule is enforced in practice: an automated agent attempting to approve a PR it pushed is expected to be blocked and must escalate to the User.
3. **Approving review required.** `project-current` requires at least one approving review from a reviewer with write access before merge (branch protection). "Review required / Merging is blocked" is the correct, healthy state until a human approves.
4. **Evidence before approval.** The User confirms the PR carries a complete handoff, report, and manifest, and that validation is PASS or PASS_WITH_WARNINGS with no boundary violation.
5. **Unlocks are User decisions.** Moving any stage out of `locked_future` / `planned_locked` requires explicit User authorization recorded in the goal Issue; no agent unlocks a stage.

## Recommended approval flow

1. Reviewer (a party other than the author) opens the PR's **Files changed** and applies [PR_REVIEW_CHECKLIST.md](PR_REVIEW_CHECKLIST.md).
2. Reviewer selects **Approve** and submits (e.g. "Approved evidence-only PR." with the checklist result).
3. The status changes from "Merging is blocked / Review required" to an enabled **Merge pull request**.
4. The **User** performs the merge (default merge commit preserves the evidence commit SHA referenced in the handoff/manifest; avoid squash when a goal's evidence pins a specific SHA).
5. A post-merge verification Issue confirms the merged `project-current` is green.

## What the human is NOT required to do

- Line-by-line code review is not required when validation is green and the diff is within the Issue's allowed scope; the human confirms boundaries and validation, not every line.
- Manual re-run of validation is optional; the recorded exit codes plus the attached logs are the primary evidence.

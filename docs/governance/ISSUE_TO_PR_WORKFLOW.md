# Issue-to-PR Workflow (GitHub-native AI collaboration)

The end-to-end path a governed goal follows, from GitHub Issue to merged Pull Request. Governance only; unlocks nothing.

## Stages

1. **Goal Issue opened** (User or Main Codex)
   - Use an issue template: `goal_request`, `verification_goal`, or `governance_goal`.
   - The Issue states: goal ID, objective, allowed scope, forbidden scope, required files, required validation, and whether User approval is needed.
   - Codex Max may draft an Issue but does not decide which goal proceeds.

2. **Assignment** (Main Codex)
   - Main Codex assigns the Issue to Codex Max only when it is the next allowed goal per [GOAL_QUEUE.md](GOAL_QUEUE.md).
   - Codex Max executes exactly what the Issue describes and nothing else.

3. **Execution on a work branch** (Codex Max)
   - Fetch latest; `git switch project-current`; verify HEAD equals the Issue's expected base commit.
   - Create `codex-max/<goal-id>`. Never start from stale `main`; never push to `project-current`.
   - Change only the files the Issue allows. Revert all validation residue before commit (see [HANDOFF_STANDARD.md](HANDOFF_STANDARD.md), note on non-read-only validation).

4. **Validation** (Codex Max)
   - Run the Issue's required validation on Windows. Record real exit codes.
   - If validation FAILs, stop and report; do not proceed to a dependent goal.

5. **Adversarial review** (optional but recommended for non-trivial diffs)
   - Run the multi-lens review in [ADVERSARIAL_REVIEW_PROTOCOL.md](ADVERSARIAL_REVIEW_PROTOCOL.md); apply actionable findings before opening the PR.

6. **Pull Request opened** (Codex Max)
   - Fill `.github/PULL_REQUEST_TEMPLATE.md` completely.
   - Attach the handoff, report, and manifest evidence files.
   - Target `project-current`.

7. **Review** (Main Codex + independent reviewer)
   - Main Codex applies [PR_REVIEW_CHECKLIST.md](PR_REVIEW_CHECKLIST.md).
   - The PR is approved by a party other than its author (no self-approval).

8. **Human approval gate** (User)
   - The User confirms the approval and performs the merge; see [HUMAN_APPROVAL_GATE.md](HUMAN_APPROVAL_GATE.md).

9. **Post-merge verification** (next assigned goal)
   - A verification-only Issue confirms `project-current` is green after merge (e.g. this workflow's post-merge check pattern).

## Branch protection expectations

- `project-current` requires at least one approving review with write access before merge.
- Direct pushes to `project-current` are not used.
- Merge is performed by the User.

## Boundaries carried through every stage

DataExpansion, Quant04, RecTiering, dashboard/frontend, trading, broker, production, local-lake, factor-mining, and DQN/RL remain locked or deleted from active mainline. `ready_factor_count`, scientific conclusions, recommendation/position outputs, and workflow locks are never changed by a workflow-mechanics goal.

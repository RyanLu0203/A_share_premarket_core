# GitHub-native AI Collaboration Workflow (GOAL-AI-COLLAB-OPS-01)

Umbrella document for how humans and AI agents collaborate on this repository entirely through GitHub Issues and Pull Requests, with GitHub as the only source of truth. Governance only: this workflow adds process and templates; it unlocks nothing and changes no scientific logic, model logic, workflow locks, or generated scientific evidence.

## Why

The project is governed by strict workflow locks and a three-role authority model. AI executors (Codex Max) are powerful but must remain subordinate to human authority and to Main Codex review. This workflow encodes that control in GitHub-native mechanics so collaboration is auditable, reproducible across Windows and macOS, and safe by construction.

## The three roles

See [AGENT_ROLE_MATRIX.md](AGENT_ROLE_MATRIX.md) for the full capability matrix.

- **User** — final authority; approves and merges; owns unlock decisions.
- **Main Codex** — program brain, reviewer, integrator, workflow controller; chooses the next goal.
- **Codex Max** — executor of explicitly assigned goals; never chooses goals, never unlocks, never self-approves.

Independent **reviewer agents** run adversarial verification and are advisory only.

## The lifecycle

Goal Issue → assignment → work branch → execution → validation → adversarial review → Pull Request → non-author review → human approval gate → User merge → post-merge verification.

Full stage detail: [ISSUE_TO_PR_WORKFLOW.md](ISSUE_TO_PR_WORKFLOW.md).

## Artifacts and where they live

| Purpose | Location |
| --- | --- |
| Goal / verification / governance Issue templates | `.github/ISSUE_TEMPLATE/` |
| Pull Request template | `.github/PULL_REQUEST_TEMPLATE.md` |
| Agent role matrix | `docs/governance/AGENT_ROLE_MATRIX.md` |
| Issue-to-PR workflow | `docs/governance/ISSUE_TO_PR_WORKFLOW.md` |
| PR review checklist | `docs/governance/PR_REVIEW_CHECKLIST.md` |
| Human approval gate | `docs/governance/HUMAN_APPROVAL_GATE.md` |
| Handoff standard | `docs/governance/HANDOFF_STANDARD.md` |
| Adversarial review protocol | `docs/governance/ADVERSARIAL_REVIEW_PROTOCOL.md` |
| Per-goal evidence | `outputs/audits/<goal-id>_report.md`, `outputs/audits/<goal-id>_manifest.json`, `outputs/handoffs/<goal-id>_handoff.md` |

## Non-negotiable invariants

1. GitHub is the only source of truth; no local Mac path, local bundle, local lake, or local cache is a dependency.
2. Work happens on `codex-max/<goal-id>`; nothing is pushed directly to `project-current`; no force push; no history rewrite.
3. Every change into `project-current` passes a non-author review and a User merge (no self-approval).
4. Checkpoint refs `checkpoint/arch03-stable-310559` / `checkpoint-arch03-stable-310559` are immutable.
5. Locked stages stay locked: DataExpansion, Quant04, RecTiering, GOAL-10B.4, position-band validation, GOAL-10D, dashboard/frontend, trading, broker, production, local-lake, factor-mining, DQN/RL. `ready_factor_count` and scientific conclusions are User-only to change.
6. No credential is ever printed, saved, logged, committed, echoed, or exposed.

## Cross-platform note

All mechanics use `git`, `gh`, and `python -m ...` commands that run identically on Windows and macOS. Repo-relative path comparisons use `Path.relative_to(root).as_posix()`; `audit_windows_compatibility_policy.py` guards against unsafe native-separator comparisons reappearing. This keeps Windows and macOS collaborators on one shared GitHub source of truth.

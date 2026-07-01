# Project Authority Model

GOAL-CODEX-OPERATING-SYSTEM-01 defines a controlled three-role workflow.

## Roles

- User: final authority for goals, unlocks, merges, destructive changes, and
  scientific conclusion changes.
- Main Codex: program brain, reviewer, integrator, and workflow controller.
- Codex Max: high-capacity executor for explicitly assigned goals only.

## Authority Rules

- Codex Max may execute assigned goals.
- Codex Max cannot select the next project goal independently.
- Codex Max cannot unlock `locked_future`, `planned_locked`, or
  deleted-from-mainline stages.
- Codex Max cannot delete committed evidence without explicit destructive
  approval.
- Codex Max cannot rewrite scientific conclusions.
- Codex Max cannot merge, override user decisions, or bypass main Codex review.
- GitHub is the authoritative project state store only after committed and
  reviewed updates.

## Review Control

Main Codex reviews Codex Max branches against workflow status, project state,
locked boundaries, validation evidence, and handoff quality before recommending
merge, changes, rejection, or a user decision.

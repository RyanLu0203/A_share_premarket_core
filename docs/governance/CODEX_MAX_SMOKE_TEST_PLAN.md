# Codex Max Smoke Test Plan

`GOAL-CODEX-MAX-ONBOARDING-SMOKE-01-REMOTE-WINDOWS-GITHUB-ONLY-COMPLIANCE-GATE`
is the first Codex Max goal after this operating-system gate.

## Scope

- Verify Codex Max starts from `project-current`.
- Verify Codex Max uses only GitHub committed sources.
- Verify Codex Max does not rely on local Mac paths, local bundle backups,
  local caches, local data lakes, or uncommitted local state.
- Verify Codex Max uses Windows-compatible commands and paths.
- Verify Codex Max reads `CODEX.md`, `PROJECT_STATE.md`, `ROADMAP.md`,
  `configs/project/workflow_status.csv`, `GITHUB_ONLY_SOURCE_POLICY.md`,
  `WINDOWS_COMPATIBILITY_POLICY.md`, `GOAL_QUEUE.md`, and `LOCKED_BOUNDARIES.md`.
- Make a small governance-only or documentation-only change assigned by the
  user.
- Run compileall, pytest if applicable, governance audits, workflow audit,
  GitHub-only source scan, Windows compatibility scan, forbidden-output scan,
  secret scan, and artifact-size scan.
- Produce a handoff using `docs/governance/HANDOFF_TEMPLATE.md`.

## Out Of Scope

The smoke test must not fetch data, change scientific outputs, unlock future
goals, create recommendations, positions, dashboards, trading outputs,
production outputs, local-lake outputs, factor-mining outputs, or DQN/RL
outputs.

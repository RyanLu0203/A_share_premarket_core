# Goal Acceptance Standard

Every goal handoff must prove completion with direct evidence.

## Required Validation

- `python -m compileall -q .`
- `python -m pytest tests -q`
- Specific goal runner when the goal has one.
- Specific goal audit.
- Upstream relevant runner and audit.
- `python scripts/run_program_validation_profile.py`
- `python scripts/run_safety_gate.py`
- `python scripts/run_adapter_audit.py`
- `python scripts/run_workflow_diagnostics.py`
- `python scripts/audit_workflow_status.py`
- Forbidden-output scan.
- Demo/stale fixture scan.
- Token/secret scan.
- No-lookahead scan.
- Artifact size scan.
- GitHub-only source scan for Codex Max tasks.
- Windows compatibility scan for Codex Max tasks.
- Fresh-clone verification for major goals.
- Clean final git status.

## Evidence Standard

Passing commands are evidence only when the command scope covers the
requirement. Unclear, indirect, stale, or partial evidence is not enough for
completion.

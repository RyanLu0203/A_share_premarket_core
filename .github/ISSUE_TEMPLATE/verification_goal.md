---
name: Verification goal
about: Request a verification-only goal (no source changes unless explicitly required)
title: "GOAL-VERIFY: "
labels: goal, verification
---

## Goal ID

## Purpose

Verification only. State what merged/branch state is being verified.

## Context

- Repository:
- Branch to verify:
- Expected HEAD / commit:

## Required checks

List the exact commands to run (e.g. compileall, pytest, the audit and validation scripts).

## Expected result

- HEAD equals the expected commit.
- pytest passes.
- validation profile passes.
- workflow audit passes.
- no forbidden outputs are created.
- final git status is clean after reverting any validation residue.

## Boundaries

- No workflow unlocks.
- No scientific output changes.
- No recommendation/position/dashboard/trading outputs.
- No credentials or local-path dependencies.

## Human action required

Review the final summary and confirm whether the state is green. No manual code review expected unless validation fails.

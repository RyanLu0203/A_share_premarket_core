# Adversarial Review Protocol

How independent reviewer agents adversarially verify a diff before it is proposed for merge. Advisory governance; a reviewer agent never approves, merges, or unlocks — it produces findings for Main Codex and the User.

## Purpose

A single author (human or agent) has blind spots. Independent reviewers, each prompted to *refute* rather than confirm, catch plausible-but-wrong changes, boundary violations, and missed cases before they reach the human approval gate.

## Lenses

Run at least the following independent lenses on any non-trivial diff. Each reviewer sees the diff and the goal Issue, and is told to look for problems, not to agree:

1. **Correctness** — Does the change do what it claims on all inputs/platforms? Off-by-one, path-separator, encoding, edge cases, behavioral drift versus the code it replaces.
2. **Governance** — Does it stay inside the Issue's allowed scope? Any lock touched, any scientific evidence changed, any forbidden output, any residue about to be committed, any hardcoded local path.
3. **Completeness** — What is missing? Unswept sibling call sites, a guard that does not cover a known variant, a claim in the report not backed by a validation command, a test that does not actually exercise the fix.

Add lenses as the change warrants (security, performance, reproducibility).

## Procedure

1. Capture the exact diff (e.g. `git diff` against the base commit) and the goal Issue.
2. Dispatch one independent reviewer per lens. Reviewers do not share state.
3. Each reviewer returns a verdict (APPROVE / CONCERNS / REJECT) with concrete, evidence-backed findings (file, line, failure scenario).
4. **Triage**: the author addresses every actionable finding, or records an explicit, justified decision not to. Findings that reveal a boundary or correctness defect block the PR until resolved.
5. Document the review outcome and how findings were handled in the goal report.

## Decision rule

- A finding that shows a real boundary violation or a real correctness defect **must** be fixed before the PR is opened (or the PR must be withdrawn).
- Findings that are latent/blind-spot only (no live bug) are recorded as known limitations in the report and may be deferred to a future goal, with the deferral stated.

## Relationship to the human gate

Adversarial review is **upstream** of and does not replace [HUMAN_APPROVAL_GATE.md](HUMAN_APPROVAL_GATE.md). Passing adversarial review does not authorize merge; only the User merges, after a non-author approval.

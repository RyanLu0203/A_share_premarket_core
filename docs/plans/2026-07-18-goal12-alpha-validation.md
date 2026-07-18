# GOAL-12 Alpha Validation Implementation Plan

> Authoritative specification: GitHub Issue #41. This plan records the frozen
> implementation sequence; it does not change the Issue's acceptance criteria.

1. Add source, label, and split contracts. Verify source hashes, qfq provenance,
   exact-calendar horizons, duplicate rejection, and purged fold boundaries.
2. Add deterministic statistics. Verify IC/RankIC, quantiles, NDCG, date-level
   bootstrap/sign-flip controls, seeded shuffles, and BH-FDR against hand-worked
   fixtures.
3. Add factor, OOS-model, robustness, and decision evaluators. Verify
   training-only preprocessing, no final-holdout tuning, every status boundary,
   and structural-missing abstention.
4. Add immutable local artifacts, runner, and GOAL-12 audit. Verify byte-for-byte
   replay, path confinement, checksums, provenance, no actionable fields, and
   unchanged interface/API topology.
5. Execute the governed close-only analysis, write concise findings, update
   project state/governance documents, and retain full evidence only under
   ignored `outputs/local/goal12`.
6. Run the complete Issue #41 validation matrix, including warnings-as-errors,
   canonical/GOAL audits, safety and leakage scans, fresh clone, and
   `core.autocrlf=true` byte-stability verification. Then create the single Draft
   PR and stop.

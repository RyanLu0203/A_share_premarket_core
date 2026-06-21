# Replace Do Not Duplicate Policy

GOAL-06C.5 keeps the workflow clear by allowing only one active builder for a
given artifact role.

When an engineering-grade artifact replaces a fixture path:

1. The upgraded builder becomes the canonical active path.
2. The old path is removed from active validation.
3. Any old fixture is retained only as a documented contract example.
4. Public wrappers, diagnostics, workflow status, README, roadmap, and audits
   are updated together.
5. The replacement must pass blocked-symbol, label-leakage, storage, and
   readiness gates before promotion.

The current Stage 6C engineering sample does not meet `engineering_pilot`.
Therefore `outputs/stage6c/STAGE6C_expanded_validation_dataset.csv` remains a
contract-demo review-only fixture path and is not promoted as engineering-grade
data.

Replacement evidence is written to:

```text
outputs/audits/active_path_replacement_audit.md
```

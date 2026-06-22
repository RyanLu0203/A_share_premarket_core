# Program Roadmap And Architecture

This document summarizes the clean active workflow after the private bootstrap.

See also:

- `docs/architecture/CANONICAL_WORKFLOW_STATUS.md`
- `docs/architecture/ACTIVE_WORKFLOW_THROUGH_GOAL06B.md`
- `docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md`

```mermaid
flowchart TD
    A["Project Operating System"] --> B["Universe / Symbol Governance"]
    B --> C["Source Health + Context Contracts"]
    C --> D["PIT Signal Store"]
    D --> E["Label Builder + Benchmark Contract"]
    E --> F["Feature-Label Merge"]
    F --> G["Leakage Audit"]
    G --> H["Stage 6A Repair Panel"]
    H --> I["Baseline Scoring Skeleton"]
    I --> J["GOAL-06B Review-Only Supervised Training"]
    J --> K["Verification / Validation / Diagnostics"]
    K -. "implemented review-only" .-> L["GOAL-06C Expanded Validation + Ranking"]
    L -. "implemented review-only data gate" .-> N["GOAL-06C.5 Storage + Coverage + Engineering Panel"]
    N -. "source-backed provider gate" .-> O["GOAL-06C.6 Source-Backed Engineering Pilot Bundle"]
    O -. "failure taxonomy gate" .-> P["GOAL-06C.6A Scoped Network + Failure Taxonomy"]
    P -. "provider ladder gate" .-> Q["GOAL-06C.7 Provider Ladder Engineering Data Base Expansion"]
    Q -. "blocked until engineering_pilot" .-> M["GOAL-06D Model Comparison / Calibration"]
```

Locked future modules are documented in the roadmap and are not imported by the
active trunk.

The canonical status contract is `configs/project/workflow_status.csv`.
Implemented active blocks use solid arrows. GOAL-06C and GOAL-06C.5 are
implemented as review-only dotted extensions; GOAL-06C.6 is also
implemented_review_only and network-disabled by default. GOAL-06C.6A is
implemented_review_only and classifies provider/network failures by specific
failure type, with a separate opt-in CloakBrowser reference probe for sanitized
tag-only access diagnostics. GOAL-06C.7 is implemented_review_only for a
provider ladder whose browser-assisted provider is explicit opt-in only and
counts only schema-valid finance rows. Future, design-only,
locked, and deleted-from-active-mainline blocks use dotted arrows or side-note
references.

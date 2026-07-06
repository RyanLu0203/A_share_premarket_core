# GOAL-FACTOR-READINESS-RESEARCH-01 Factor Readiness Research Gate

Status: `PASS_WITH_WARNINGS`

GOAL-FACTOR-READINESS-RESEARCH-01 Factor Readiness Research Gate: PASS_WITH_WARNINGS

## Readiness outcome (honest, evidence-driven)

- ready_factor_count before: `0`
- ready_factor_count after: `0`
- factors evaluated: 30; candidates evaluated (incl. refinements): 120
- conditionally_useful candidates: 63
- ready candidates: none

## Method

- Readiness requires the immovable in-sample bar AND an added out-of-sample holdout (last 20% of dates, never used to select transforms) AND walk-forward cross-fold sign stability. Thresholds (STRONG_IC=0.03, MIN_VALID_ROWS=500, sign-stability>=0.60, >=2 aligned horizons) are imported from Quant03/Quant04 and were NOT lowered.
- Candidate refinements are fixed, a-priori, PIT-safe per-date cross-sectional transforms (identity, z-score, rank, winsorized z-score) — no parameter search, no factor mining, no target-driven selection.
- Panel expansion is bounded by committed offline evidence; northbound/margin/real-time feeds are not available offline and are classified as a network-gated gap, not fabricated.

## Boundary

GOAL-REC-TIERING-01 remains `locked_future`. This gate does not unlock it, does not modify workflow_status.csv or locked_capabilities.json, and creates no recommendation/position/portfolio/dashboard/trading output. ready status is never fabricated.

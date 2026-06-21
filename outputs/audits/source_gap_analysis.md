# Source Gap Analysis

Status: `PASS_WITH_WARNINGS`

## Current Scope
- Approved symbols: `2`
- Proposed candidate symbols awaiting source evidence: `6`
- Stage 6C trading dates: `4`
- PIT-ready rows: `8`
- Label-ready rows: `8`
- Stage 6C rows: `8`

## Gap To Engineering Pilot
- Symbols needed: `48`
- Trading dates needed: `116`
- Rows needed: `5992`

## Expansion Path
1. Materialize a local bundle outside GitHub with at least 50 approved symbols and 120 exchange trading dates.
2. Populate OHLCV, benchmark, announcement metadata, and source coverage tables using optional network ingestion guarded by explicit flags.
3. Rebuild PIT and label panels from the local bundle, then promote only if audits reach `engineering_pilot` or higher.

# Engineering Label Panel Audit

Status: `PASS_WITH_WARNINGS`
Rows reviewed: `8`
Symbols reviewed: `2`
Trading dates reviewed: `4`
Logical grain: `trade_date + symbol`.
Only the existing 1d clean-bootstrap label is populated; 3d/5d fields stay blank instead of fabricated.

## Failures

## Warnings
- engineering label panel sample is fixture-backed and missing 3d/5d horizons

# GOAL-LIQUIDITY-EXTERNAL-HANDOFF-READINESS-01

Status: `PASS_WITH_WARNINGS` (`implemented_infrastructure_only`).

This gate makes two future external evidence paths directly testable without
placing source data in Git. Inputs may live outside the repository or below the
ignored repository `.local/` boundary:

1. An explicit absolute-path, SHA-256-anchored candidate CSV with complete
   symbol, exchange, A-share type, listing status, source and PIT availability
   fields. The source contract must still select exactly 100 eligible symbols.
2. An explicit absolute-path, SHA-256-anchored JSON file containing exactly the
   four governed Tushare/Baostock schema observations, one call each, zero
   retries, exact identities and field names, and no raw values.

The committed CSV and JSON files are zero-authority templates only. The JSON
template records all calls as `NOT_AUTHORIZED`; it is not an accepted result.
Files elsewhere in the tracked repository, symlinks, wrong checksums, extra
fields, raw values, partial matrices, retries, late rows and incomplete
universes fail closed.

A sanitized observation bundle can become review-eligible, but import alone
cannot prove provider provenance and therefore cannot set live schema
verification. No external bundle is currently present or accepted, no provider
call was made, and all factor and downstream boundaries remain locked.

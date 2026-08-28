# GOAL-LIQUIDITY-ACQUISITION-READINESS-BATCH-01

Status: `PASS_WITH_WARNINGS`; acquisition preflight `BLOCKED`.

Four offline workstreams are integrated: a fixed four-call schema-smoke design, strict Tushare/Baostock row normalizers, an explicit PIT availability contract, and an exact-100 deterministic universe contract.

Current committed evidence supplies `50` eligible symbols, including `41` with acquired deep history. Because fewer than 100 are available, no partial accepted universe is emitted. Both provider candidates also lack accepted row-level availability timestamps.

Synthetic field-name fixtures pass both provider parser contracts, but this is not live schema verification and accepts no provider row.

The schema smoke remains design-only and unauthorized. No provider call, credential read, raw payload, accepted row, factor construction, or downstream unlock occurred.

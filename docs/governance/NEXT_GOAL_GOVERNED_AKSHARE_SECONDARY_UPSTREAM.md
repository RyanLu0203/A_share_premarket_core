# Next-Goal Specification: Governed AKShare Run-Level Secondary Upstream

## Proposed Issue Title

`[NEXT GOAL] Governed AKShare Run-Level East Money-to-Tencent Secondary Upstream`

## Status And Boundary

Status: `SPECIFICATION_ONLY_NOT_IMPLEMENTED_NOT_ACTIVATED`

This goal is not part of PR #33 implementation. It must not activate Tencent,
change runtime provider selection, create a snapshot, or claim operational
deployment. It preserves TLS verification, bounded execution, fail-closed
evidence rules, and every recommendation, trading, broker, production,
factor-mining, and DQN/RL lock.

## Provider Roles

- Application provider library: AKShare.
- Primary: `stock_zh_a_hist` / East Money /
  `push2his.eastmoney.com/api/qt/stock/kline/get`.
- Candidate secondary: `stock_zh_a_hist_tx` / Tencent Securities /
  `proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get`.
- Selection grain: one complete refresh run, never individual symbols.

## Required Run-Level State Machine

1. Resolve the current target trading date and T-1 from the approved calendar.
2. Attempt the complete required-symbol batch through East Money and retain its
   request-level evidence, even if the batch is rejected.
3. Evaluate a versioned, explicitly approved primary-failure condition only
   after the bounded primary batch terminates.
4. If the condition is not met, finish with the primary batch result; do not
   invoke Tencent.
5. If the condition is met, record the run-level transition and acquire the
   complete required-symbol batch again through Tencent.
6. Choose at most one upstream batch as the candidate canonical live batch.
   East Money and Tencent rows must not be mixed in one snapshot unless a later
   explicit contract authorizes mixing.
7. Fail closed before snapshot creation if the selected batch lacks full T-1
   coverage, freshness, schema validity, PIT validity, provenance, or checksum
   integrity.

## Approved Primary-Failure Condition Contract

Implementation must propose and test a concrete condition for explicit review.
It must be based on bounded batch evidence such as transport failure rate,
missing required T-1 coverage, repeated endpoint-level remote closes, or an
approved provider-state classification. It must not use per-symbol opportunism,
identity rotation, TLS bypass, unbounded retrying, or an undocumented heuristic.

The condition, thresholds, observation window, total-attempt cap, wall-clock
cap, and source-selection reason must be written into the run manifest. Tencent
activation remains disabled until the condition and contract receive explicit
user approval.

## Normalization And Semantic Research

- Normalize SZSE/SSE symbols to the canonical `NNNNNN.SZ` / `NNNNNN.SH`
  contract and prove the Tencent request-code mapping for both exchanges.
- Define a complete normalized daily schema for trade date, open, high, low,
  close, volume, amount, source timestamp, adjustment mode, and provenance.
- Determine from AKShare implementation and bounded source evidence what
  Tencent's `amount` field represents, including unit and scaling. Do not infer
  volume from amount or silently substitute one for the other.
- Prove that Tencent `qfq` adjustment semantics match the primary contract, or
  reject activation. Corporate-action and date-boundary behavior require
  explicit fixtures.

## Cross-Source Consistency Contract

Before activation, build a bounded overlap audit at `trade_date + symbol`
grain covering both exchanges and representative corporate-action histories.

- Dates must align to the approved trading calendar.
- OHLC comparison must use explicit absolute and relative price tolerances.
- Amount comparison must use a separate tolerance only after units and scaling
  are resolved.
- Tolerances must be proposed from observed precision/rounding evidence,
  versioned, and approved; they must not be selected to force a pass.
- Duplicate keys, missing overlap, material OHLC conflicts, adjustment
  conflicts, and unresolved amount semantics block secondary approval.
- Cross-source comparison is an approval audit, not permission to mix rows in
  a canonical run.

## Provenance And Integrity

Every primary and secondary attempt must record:

- application provider and installed AKShare version;
- exact AKShare function and upstream source;
- normalized endpoint family and non-sensitive request parameters;
- required symbols, target date, T-1 date, request timestamps, result classes,
  HTTP evidence when available, row counts, and accepted/rejected counts;
- normalized-batch checksum, source dates, coverage result, PIT result, schema
  result, and source-consistency contract version;
- primary-failure condition evaluation and run-level activation decision;
- selected upstream and explicit reason;
- atomic-write result and final snapshot checksum when eligible.

No credential, token, cookie, private payload, or raw full provider response may
be committed.

## Acceptance Criteria

1. Primary East Money always receives the complete bounded required batch
   first.
2. Tencent activates only after an explicitly approved, test-covered
   primary-failure condition evaluates true.
3. Activation launches a complete Tencent batch, not retries for selected
   missing symbols.
4. A canonical snapshot contains rows from one upstream only; mixed-source
   snapshots remain prohibited.
5. Symbol normalization and request mapping pass for representative SSE and
   SZSE symbols.
6. The normalized Tencent schema is complete, and `amount` meaning, unit, and
   scaling are documented and tested.
7. Adjustment semantics and corporate-action behavior are verified against the
   approved contract.
8. A bounded overlap audit compares dates and OHLC fields across both sources.
9. Separate, evidence-backed price and amount tolerances are versioned and
   tested, including fail cases just outside each tolerance.
10. The selected secondary batch has full required-symbol T-1 coverage; no
    partial current snapshot is permitted.
11. Function, upstream, endpoint family, parameters, dates, checksums,
    provenance, PIT, and source-selection evidence are present and validated.
12. Source conflicts, unresolved semantics, incomplete coverage, stale rows,
    checksum mismatch, or atomic-write failure prevent snapshot creation.
13. Deterministic replay remains explicitly labeled replay and cannot satisfy
    live acceptance.
14. Retry/attempt and wall-clock limits are finite, TLS verification remains
    enabled, and identity rotation or access-control bypass is absent.
15. Unit, integration, full Python, canonical profile, and idempotency checks
    pass before any operational deployment claim.
16. All recommendation, trading, broker, production, factor-mining, and DQN/RL
    capabilities remain locked.

## Required Decision Before Implementation

The user must explicitly approve the primary-failure condition, Tencent schema
and amount semantics, adjustment contract, consistency tolerances, and
single-upstream run policy. Until then, the existing inactive proposal remains
non-callable and East Money failure remains fail-closed.

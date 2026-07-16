# Next-Goal Specification: Governed AKShare Run-Level Secondary Upstream

## Proposed Issue Title

`[NEXT GOAL] Governed AKShare Run-Level East Money-to-Tencent Secondary Upstream`

## Status And Boundary

Status: `ISSUE_34_IMPLEMENTED_RESEARCH_ONLY_PASS`

This goal was deliberately excluded from PR #33. GitHub Issue #34 now provides
the separate explicit authority to implement and validate the governed
secondary. The complete live acceptance and identical idempotency run now
pass. TLS verification, bounded execution,
fail-closed evidence rules, and every recommendation, trading, broker,
production, factor-mining, and DQN/RL lock remain mandatory.

## Provider Roles

- Application provider library: AKShare.
- Primary: `stock_zh_a_hist` / East Money /
  `push2his.eastmoney.com/api/qt/stock/kline/get`.
- Governed secondary: `stock_zh_a_hist_tx` / Tencent Securities /
  `web.ifzq.gtimg.cn` plus
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

Issue #34 approves activation only after a complete bounded primary batch has
less than 100% required T-1 coverage, at least one missing symbol is classified
as `BROWSER_NET_EMPTY_RESPONSE`, `CONNECTION_RESET`,
`HTTP_429_RATE_LIMITED`, or `HTTP_5XX_PROVIDER_ERROR`, and every missing symbol
is explained by an approved endpoint failure rather than a local or integrity
defect. Each upstream has one attempt per required symbol, a 30-second provider
timeout, and a 1,800-second batch wall-clock cap. No retry, per-symbol
opportunism, identity rotation, TLS bypass, or undocumented heuristic is used.

## Normalization And Semantic Research

- Normalize SZSE/SSE symbols to the canonical `NNNNNN.SZ` / `NNNNNN.SH`
  contract and prove the Tencent request-code mapping for both exchanges.
- The normalized daily schema carries trade date, symbol, open, high, low,
  close, volume, explicitly unavailable monetary amount, adjustment mode, and
  request/batch provenance.
- AKShare 1.18.64 truncates Tencent output to six columns and labels the sixth
  `amount`. Three-source overlap samples prove that this value exactly equals
  East Money `成交量`; it is source volume in `手` with canonical scale 1. The separate
  Tencent monetary-amount field exists in the raw endpoint at 10,000-CNY scale
  but is discarded by `stock_zh_a_hist_tx`. The adapter therefore maps the
  misleading export to volume and records monetary amount as unavailable; it
  never invents, substitutes, or zero-fills the missing value.
- Production adjustment is qfq only. Corporate-action and date-boundary
  behavior require versioned authoritative-company/exchange evidence,
  Tencent unadjusted/qfq rows, approved-calendar alignment, formula
  verification, and continuity checks. hfq is runtime-disabled research
  evidence and cannot block or satisfy the qfq production gate.

## Cross-Source Consistency Contract

Before activation, build a bounded overlap audit at `trade_date + symbol`
grain covering both exchanges and representative corporate-action histories.

- Dates must align to the approved trading calendar.
- OHLC comparison must use explicit absolute and relative price tolerances.
- Volume must match exactly in the shared provider unit. A diagnostic-only raw
  monetary-amount fixture may use `100 CNY` absolute or `1e-6` relative
  tolerance after applying the observed 10,000-CNY scale; this raw diagnostic
  is never promoted to canonical Tencent output.
- Tolerances must be proposed from observed precision/rounding evidence,
  versioned, and approved; they must not be selected to force a pass.
- Duplicate keys, missing ordinary qfq overlap, material OHLC conflicts, qfq
  adjustment conflicts, and unresolved amount semantics block secondary
  approval. When the bounded primary corporate window closes before HTTP/body
  evidence, the approved classification is
  `PRIMARY_CORPORATE_ACTION_EVIDENCE_UNAVAILABLE`; governed authoritative-terms
  triangulation is then required.
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
7. qfq adjustment semantics and corporate-action behavior are verified against
   the approved contract; hfq remains disabled and non-blocking.
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

## Implementation Evidence

- Policy: `configs/providers/akshare_governed_stock_history_v1.json`.
- State machine: `src/ashare_premarket/providers/governed_stock_history.py`.
- Versioned normalized fixture:
  `configs/providers/fixtures/eastmoney_tencent_consistency_v1.csv`.
- Versioned qfq corporate-action fixture:
  `configs/providers/fixtures/tencent_qfq_corporate_action_v2.json`.
- Bounded fresh-clone evidence: a 41-row T-1 canonical delta plus a versioned
  base+delta checksum commitment; the duplicate full canonical materialization
  remains local and ignored.
- Tests: `tests/test_governed_akshare_secondary_upstream.py`.

The approved qfq contract passes SSE `603836.SH` and required-universe SZSE
`000333.SZ` authoritative-terms triangulation as well as ordinary SSE/SZSE/
ChiNext direct overlap. Two identical full live runs selected Tencent for all
41 symbols with batch checksum
`a95459ff4be28e5acf48c7fb056490f470034d6949599119da8fa8277b95f5b5`
and snapshot checksum
`8bb115499856585595e1f6e625bbea3e8d6de7c89a067992c2af9fe62685e3d2`.
The 600036.SH hfq difference remains explicitly documented as non-production
research evidence and is never used by the runtime selector.

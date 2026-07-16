# Issue #36 Tencent primary operational hardening

## Decision

Issue #36 implements and validates Tencent as the direct operational primary
for canonical daily refresh. The feature branch is eligible for review into
`project-current`; no launchd agent, backend, frontend, or deployment state is
created by this work.

## Canonical provider contract

- Application provider/function: AKShare `stock_zh_a_hist_tx`.
- Upstream: Tencent, selected immediately for the complete batch.
- East Money canonical request count: exactly 0.
- East Money disposition: separately invoked, disabled-by-default bounded
  probe only; no automatic failback and no canonical influence.
- Source count per snapshot: exactly 1; per-symbol mixing is forbidden.
- Adjustment: qfq only; hfq is `UNSUPPORTED_DISABLED`.
- Tencent sixth exported field: volume in `手`.
- Monetary amount: `UNAVAILABLE_NULL_NOT_ZERO`; volume is never copied and
  null is never defaulted to zero.

The canonical batch fails closed on incomplete coverage, wrong or reordered
schema, symbol/exchange mismatch, malformed/empty response, timeout, DNS/TLS
failure, interruption, stale/future/duplicate data, non-finite or invalid OHLC
values, invalid volume, PIT/provenance failure, or final-symbol failure. Such a
failure cannot replace the last valid immutable snapshot.

## Independent verification and adjustment

Corporate-action and ordinary-symbol checks are bounded, checksummed, and
independent of canonical acquisition. They contribute zero rows to the Tencent
snapshot. qfq formula/continuity checks pass for the governed verification
fixtures. The enabled 41-symbol universe includes SSE, SZSE, and ChiNext but no
BJ symbol. BJ format mapping is explicit; because current AKShare Tencent calls
do not return the expected BJ schema, any future BJ universe admission is
classified `TENCENT_BJ_UPSTREAM_UNSUPPORTED` and fails closed.

## Genuine network acceptance

The remote environment had legitimate network access. No replay or fixture was
presented as live. The approved calendar dynamically resolved:

- target: `2026-07-16`;
- T-1: `2026-07-15`;
- accepted universe: 41/41;
- selected upstream count: 1 (Tencent);
- Tencent canonical requests: 41 per run;
- East Money canonical requests: 0;
- normalized batch SHA-256:
  `596b0861a3abff07a4fc0e7342bfc17934a7586328d259b810a718a105384f96`;
- canonical SHA-256:
  `51951e5d0c668df201492c03f14d6b5d166c2c5fe64c359e7ff6ad2c5ad8489f`;
- snapshot ID: `opm:2026-07-16:fa3ea3c250c3c317`;
- snapshot SHA-256:
  `fa3ea3c250c3c317d86906383f724079c1d338f89aa9a5df0adb8dbc0122fb25`;
- refresh manifest SHA-256:
  `bbbe7481d1510869c68bad200338e227a5304e8fb77fe3bb96e65e17642f98cc`.

Schema, current-T-1 freshness, unique keys, OHLC/finite/volume semantics,
coverage, PIT, provenance, amount, qfq, and independent verification all pass.
Both complete network runs reacquired all symbols and returned identical
normalized batch, canonical, and immutable snapshot checksums. Idempotency is
`PASS_IDENTICAL_NORMALIZED_BATCH_AND_IMMUTABLE_SNAPSHOT`; no
`already_refreshed` shortcut was used.

## Daily observability

Each operational run records selected source/function, canonical request
counts by upstream, accepted/rejected counts, target and T-1, amount and
adjustment status, independent-verification status, checksums, and immutable
write disposition. This is sufficient for the owner to observe five future
trading days manually; five-day observation is not an Issue #36 completion
gate.

Post-merge deployment-machine live acceptance command:

```bash
ASHARE_ALLOW_NETWORK_INGESTION=1 .venv/bin/python scripts/run_daily_incremental_evidence_refresh.py --allow-network
```

Run the command twice as complete network acquisitions and compare the batch,
canonical, snapshot, and refresh checksums. Do not use replay or
`already_refreshed` as proof.

## Boundaries

No deployment, launchd installation, port startup, merge, recommendation,
trading, broker, production-model, factor-mining, or DQN/RL unlock is part of
this issue.

# GOAL-DAILY-INCREMENTAL-EVIDENCE-REFRESH-01

## Daily flow

1. Resolve the governed target session and expected T-1 date with the OPM clock; missing calendar coverage blocks without guessing a session.
2. Replay committed evidence, import a bounded local increment, or explicitly opt into the existing provider adapter.
3. Validate freshness, required-symbol missingness, provider state, timestamps, PIT availability, quarantine state, and checksums.
4. Stop before OPM when any fail-closed check is blocked.
5. On success, call OPM with the validated canonical evidence and publish its immutable snapshot for the read-only workspace.

## Evidence semantics

The primary provider row is never averaged with another source. Cross-provider adjustment semantics remain explicitly unresolved when direct metadata is unavailable. Existing discrepancy quarantine rows remain excluded from risk fitting.

Text evidence checksums normalize CRLF to LF before SHA-256 so tracked CSV evidence remains reproducible across Windows and Unix checkouts. Immutable refresh and OPM snapshot files retain raw-byte checksums.

## Boundaries

This layer is research-only. Recommendation tiering, action labels, target prices, orders, broker connections, paper execution, production writes, and reinforcement learning remain outside the active workflow.

The refresh updates canonical evidence, readiness, and OPM snapshot lineage. It deliberately reuses validated predecessor portfolio-risk estimates; this goal does not duplicate or rerun the upstream risk estimators.

## Experiment readiness

Only the date-range, snapshot-lineage, evaluation-metadata, and baseline-reference contracts are prepared. No experiment is started and no performance statement is produced.

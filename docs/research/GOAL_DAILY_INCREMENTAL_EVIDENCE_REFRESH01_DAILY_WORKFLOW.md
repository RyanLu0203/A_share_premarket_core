# GOAL-DAILY-INCREMENTAL-EVIDENCE-REFRESH-01

## Daily flow

1. Resolve the governed target session and expected T-1 date with the OPM clock; missing calendar coverage blocks without guessing a session.
2. Replay committed evidence, import a bounded local increment, or explicitly opt into the governed AKShare provider ladder.
3. Validate freshness, required-symbol missingness, provider state, timestamps, PIT availability, quarantine state, and checksums.
4. Stop before OPM when any fail-closed check is blocked.
5. On success, call OPM with the validated canonical evidence and publish its immutable snapshot for the read-only workspace.

## Evidence semantics

The primary provider row is never averaged with another source. Cross-provider adjustment semantics remain explicitly unresolved when direct metadata is unavailable. Existing discrepancy quarantine rows remain excluded from risk fitting.

For an explicitly network-enabled daily run, `stock_zh_a_hist` remains the primary source and `stock_zh_a_daily` (AKShare/Sina) is a same-symbol, same-session fallback. A failed primary attempt remains in the provider audit. The run may continue only when the fallback returns and normalizes the expected T-1 row; validation then records `PROVIDER_FALLBACK_RECOVERED` as a warning. An unrecovered failure remains fail-closed.

The macOS operational runner synchronizes a source-backed runtime trading calendar before resolving T-1. The ignored runtime copy is selected through `ASHARE_TRADING_CALENDAR_PATH`; the committed deterministic calendar remains the offline default and is never rewritten by the daily job.

Text evidence checksums normalize CRLF to LF before SHA-256 so tracked CSV evidence remains reproducible across Windows and Unix checkouts. Immutable refresh and OPM snapshot files retain raw-byte checksums.

## Boundaries

This layer is research-only. Recommendation tiering, action labels, target prices, orders, broker connections, paper execution, production writes, and reinforcement learning remain outside the active workflow.

The refresh updates canonical evidence, readiness, and OPM snapshot lineage. It deliberately reuses validated predecessor portfolio-risk estimates; this goal does not duplicate or rerun the upstream risk estimators.

## Experiment readiness

Only the date-range, snapshot-lineage, evaluation-metadata, and baseline-reference contracts are prepared. No experiment is started and no performance statement is produced.

## macOS operation

Install the two user launch agents with `.venv/bin/python scripts/install_macos_launchd.py`. The workspace agent starts at login and is kept alive; the refresh agent runs Monday through Friday at 07:45 local time. Both use the project `.venv`, write only ignored runtime logs, and preserve the explicit network gates. Same-target successful immutable runs are skipped idempotently. See `docs/operations/MACOS_LAUNCHD_DAILY_REFRESH.md`.

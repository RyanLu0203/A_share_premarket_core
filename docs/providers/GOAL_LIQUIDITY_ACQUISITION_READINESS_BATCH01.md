# GOAL-LIQUIDITY-ACQUISITION-READINESS-BATCH-01

Status: `implemented_infrastructure_only`; `PASS_WITH_WARNINGS`; acquisition
preflight remains `BLOCKED`.

This batch advances four offline workstreams together:

1. A fixed schema-smoke plan for two symbols and two providers, capped at four
   calls with zero retries. It remains design-only and unauthorized.
2. Strict Tushare `daily_basic` and Baostock history row normalizers covering
   identity, dates, numeric domains, units, trade status, QFQ, and explicit
   availability.
3. A PIT availability contract that rejects missing or naive timestamps and
   refuses to infer a row timestamp from an update window.
4. A deterministic exact-100 A-share universe contract that prefers existing
   acquired symbols and otherwise sorts by symbol only. It never uses returns,
   factors, performance, or record order.

Current committed evidence contains 50 eligible candidates, of which 41 have
acquired deep history. Because 100 are required, the universe gate returns
`BLOCKED` and emits no partial accepted list. Both provider candidates also
lack accepted row-level availability timestamps.

Both sanitized synthetic field-name fixtures pass the offline provider schema
contracts. This proves parser-contract readiness only; it is not live schema
verification and does not authorize or record a provider call.

No provider call, credential read, raw payload, accepted row, factor
construction, recommendation, position, backtest, trading, broker, production,
factor mining, or DQN/RL unlock occurred.

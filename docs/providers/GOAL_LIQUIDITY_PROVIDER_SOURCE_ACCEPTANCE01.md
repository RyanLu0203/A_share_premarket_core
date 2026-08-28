# GOAL-LIQUIDITY-PROVIDER-SOURCE-ACCEPTANCE-01

Status: `implemented_infrastructure_only`; `PASS_WITH_WARNINGS` documentation
acceptance; acquisition preflight remains `BLOCKED`.

This offline gate selects two documentation-backed candidates:

- Tushare Pro `daily_basic` for historical `free_share` and
  free-float-based turnover. The official contract documents daily historical
  queries, `free_share` in ten-thousand-share units, and a trade-day update
  window of 15:00–17:00.
- Baostock `query_history_k_data_plus` for volume, turnover, trade status, and
  QFQ adjustment cross-checking.

Documentation acceptance is not live schema acceptance. Neither source
provides an accepted row-level provider `available_at`, neither was called by
this goal, and no token or credential was read. Tushare entitlement, both live
schemas, exact symbol/date coverage, provider availability, and cross-provider
reconciliation remain unverified.

Therefore the project still has only one live-verified partial source
(Tencent volume semantics), below the required two complete providers. The
live pilot, row acceptance, liquidity factor construction, recommendation
tiering, positions, backtests, trading, broker, production, factor mining, and
DQN/RL remain blocked.

Official references:

- <https://tushare.pro/document/2?doc_id=32>
- <https://pypi.org/project/baostock/>

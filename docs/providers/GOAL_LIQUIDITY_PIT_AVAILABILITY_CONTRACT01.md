# GOAL-LIQUIDITY-PIT-AVAILABILITY-CONTRACT-01

Status: `implemented_infrastructure_only`; contract `PASS`; both current
provider candidates remain `BLOCKED_ROW_AVAILABLE_AT_MISSING`.

The contract accepts only an explicit timezone-aware provider availability
timestamp that is no earlier than the local trade-date close and no later than
the decision cutoff. A documented daily update window is useful metadata but
cannot be converted into a row-level timestamp.

Tushare Pro `daily_basic` documents a trade-day update window, while the
reviewed Baostock contract does not provide an accepted row-level availability
timestamp. Neither source is PIT-accepted by this goal.

No provider was called, no credential was read, zero rows were accepted, and
no factor or downstream stage was unlocked.

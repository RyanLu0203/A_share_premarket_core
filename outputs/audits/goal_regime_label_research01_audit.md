# GOAL-REGIME-LABEL-RESEARCH-01 Audit

Status: `PASS`

## Checks
- Required files exist.
- Required schemas exist.
- Date-level grain is `trade_date`.
- Symbol-level grain is `trade_date + symbol`.
- Bridge grain is `trade_date + symbol + refined_factor_id`.
- No duplicate keys.
- Forward returns, benchmark-excess forward returns, label-ready fields, IC/RankIC, hit rates, recommendation labels, position fields, portfolio returns, and equity curves are excluded from the bridge and label construction evidence.
- Downstream locks are preserved.

## Failures

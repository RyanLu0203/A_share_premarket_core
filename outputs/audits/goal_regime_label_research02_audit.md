# GOAL-REGIME-LABEL-RESEARCH-02 Audit

Status: `PASS`

## Checks
- Required files exist.
- Required refined schemas exist and pass the forbidden-lookahead column scan.
- Date-level grain is `trade_date`.
- Symbol-level grain is `trade_date + symbol`.
- Bridge grain is `trade_date + symbol + refined_factor_id`.
- No duplicate keys.
- Forward returns, benchmark-excess forward returns, label-ready fields, IC/RankIC, hit rates, recommendation labels, position fields, portfolio returns, and equity curves are excluded from the bridge and refined label construction evidence.
- Expanded DataExpansion01 regime evidence is integrated without factor predictive validity evaluation.
- Downstream locks are preserved.

## Failures

# GOAL-LIQUIDITY-UNIVERSE100-CONTRACT-01

Status: `implemented_design_only`

This offline contract deterministically selects an exact 100-symbol universe
for a future liquidity-evidence gate. It does not acquire or accept market
data.

## Selection contract

1. Normalize symbols to uppercase and admit only canonical Shanghai or
   Shenzhen A-share code families with `.SH` or `.SZ` suffixes.
2. Deduplicate by symbol and exclude `000625.SZ`, `000858.SZ`, `601138.SH`,
   and `601208.SH`.
3. Select eligible symbols already present in the acquired cohort first, in
   symbol order.
4. Fill remaining slots from other eligible candidates in symbol order.
5. Return `PASS` only with exactly 100 accepted symbols. If fewer than 100
   eligible candidates exist, return `BLOCKED` and an empty accepted universe;
   an incomplete universe is never accepted.

Candidate order, future returns, labels, factor values, factor scores, and
performance metrics are forbidden selection inputs. The implementation reads
only each candidate's `symbol` field.

## Boundary

The contract performs no network access, provider call, credential read,
factor construction, evaluation, recommendation, position sizing, backtest,
dashboard, trading, or production action. It writes no output artifact and
does not unlock any downstream stage.

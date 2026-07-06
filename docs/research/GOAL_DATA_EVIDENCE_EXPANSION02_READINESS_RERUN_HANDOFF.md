# GOAL-DATA-EVIDENCE-EXPANSION-02 — Readiness Rerun Handoff

## Can GOAL-FACTOR-READINESS-RESEARCH-01 be rerun with materially stronger evidence?

**No — not offline.** This gate achieved no material offline expansion of temporal depth, cross-sectional breadth, or provider diversity. Rerunning readiness on the current evidence would still yield ready_factor_count = 0.

## Exact external requirements to enable a meaningful rerun

1. Authorize network ingestion (`ASHARE_ALLOW_NETWORK_INGESTION=1`) so cataloged-but-unfetched AKShare P0/P1 sources can be fetched into PIT-safe committed bundles.
2. Commit a broader A-share universe bundle (target >=300 symbols) with PIT-safe, non-survivorship-biased membership.
3. Commit longer history (target >=250 trading dates / 1-3 years) with trading-calendar alignment.
4. Add an independent crosscheck provider and per-symbol sector/industry + free-float market-cap classification.
5. Add northbound-flow / margin / index-futures / macro-FX context with publication-date-aligned PIT contracts.

Each item is user_authority_required or requires a new committed bundle; none is offline-derivable. Thresholds must remain unchanged and readiness must still be earned out-of-sample.

## Locks preserved

GOAL-REC-TIERING-01 and dashboard_daily_report remain locked_future. No self-unlock. No recommendation output.
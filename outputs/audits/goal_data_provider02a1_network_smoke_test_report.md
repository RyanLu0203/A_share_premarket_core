# GOAL-DATA-PROVIDER-02A.1 Network Opt-In Provider Smoke Test Report

GOAL-DATA-PROVIDER-02A.1 Network Opt-In Provider Smoke Test Gate: PASS_WITH_WARNINGS

Mode: `review_only_network_opt_in_provider_smoke_test`
Network opt-in present: `false`
Live provider access attempted count: `0`
Approved symbols tested: `002475.SZ;600036.SH`
Smoke window: `2026-05-11` to `2026-06-19` over `30` trading-day contract.

## Provider Results
- `tushare_pro`: status `SKIPPED`, live access attempted `false`, failure `tushare_unavailable_missing_token`, returned rows `0`.
- `baostock`: status `SKIPPED`, live access attempted `false`, failure `network_disabled_by_policy`, returned rows `0`.
- `akshare`: status `SKIPPED`, live access attempted `false`, failure `network_disabled_by_policy`, returned rows `0`.
- `efinance`: status `SKIPPED`, live access attempted `false`, failure `network_disabled_by_policy`, returned rows `0`.
- `qstock`: status `SKIPPED`, live access attempted `false`, failure `provider_package_unavailable`, returned rows `0`.
- `yfinance`: status `SKIPPED`, live access attempted `false`, failure `network_disabled_by_policy`, returned rows `0`.
- `local_import`: status `PASS_WITH_WARNINGS`, live access attempted `false`, failure `local_import_current_approved_ohlcv_rows_missing`, returned rows `0`.

## Boundary
- This gate creates provider smoke-test metadata only.
- Live provider access is attempted only when explicit environment opt-ins are present.
- Tushare Pro reads `TUSHARE_TOKEN` only from the environment and never persists it.
- No raw provider payloads are persisted.
- Smoke-test data is not final evaluation panel evidence.
- GOAL-DATA-PROVIDER-02B, GOAL-V1-DIAGNOSTIC-COVERAGE-03, and GOAL-10B.3 are implemented only by their own explicit review-only gates when valid evidence exists; GOAL-DATA-PANEL-02, GOAL-10D, dashboards, trading, production, broker, local-lake, factor-mining, and DQN/RL remain locked.

## Warnings
- approved_universe_too_small
- tushare_pro:tushare_unavailable_missing_token
- baostock:network_disabled_by_policy
- akshare:network_disabled_by_policy
- efinance:network_disabled_by_policy
- qstock:provider_package_unavailable
- yfinance:network_disabled_by_policy
- local_import:local_import_current_approved_ohlcv_rows_missing

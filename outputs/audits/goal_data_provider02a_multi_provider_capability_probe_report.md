# GOAL-DATA-PROVIDER-02A Multi-Provider Capability Probe Report

GOAL-DATA-PROVIDER-02A Multi-Provider Capability Probe Gate: PASS_WITH_WARNINGS

Mode: `review_only_multi_provider_capability_probe`
Network ingestion enabled: `false`
Approved symbols tested: `002475.SZ;600036.SH`
Probe date window: `2026-05-11` to `2026-06-19` over `30` trading-day contract.

## Provider Results
- `tushare_pro`: status `SKIPPED`, failure `tushare_unavailable_missing_token`, returned rows `0`, readiness `not_ready_missing_token`.
- `baostock`: status `SKIPPED`, failure `network_disabled_by_policy`, returned rows `0`, readiness `cannot_assess_without_network_opt_in`.
- `akshare`: status `SKIPPED`, failure `network_disabled_by_policy`, returned rows `0`, readiness `cannot_assess_without_network_opt_in`.
- `efinance`: status `SKIPPED`, failure `network_disabled_by_policy`, returned rows `0`, readiness `cannot_assess_without_network_opt_in`.
- `qstock`: status `SKIPPED`, failure `provider_package_unavailable`, returned rows `0`, readiness `not_ready_optional_dependency_missing`.
- `yfinance`: status `SKIPPED`, failure `network_disabled_by_policy`, returned rows `0`, readiness `cannot_assess_without_network_opt_in`.
- `local_import`: status `PASS_WITH_WARNINGS`, failure `local_import_current_approved_ohlcv_rows_missing`, returned rows `0`, readiness `fallback_engineering_pilot_sample_exists_but_current_approved_symbol_gap`.

## Boundary
- This gate creates provider capability metadata only.
- It does not create a final evaluation panel, recommendation diagnostics, position-band diagnostics, backtests, dashboards, trading, production, broker, local-lake, factor-mining, or DQN/RL outputs.
- Tushare Pro uses only `TUSHARE_TOKEN`, `ASHARE_ALLOW_TUSHARE=1`, and `ASHARE_ALLOW_NETWORK_INGESTION=1`; missing token is recorded as `tushare_unavailable_missing_token`.
- `qstock` is limited to data-module availability; backtest and strategy modules remain forbidden.
- `yfinance` is recorded as `auxiliary_not_primary`.

## Warnings
- approved_universe_has_fewer_than_5_symbols
- tushare_pro:tushare_unavailable_missing_token
- baostock:network_disabled_by_policy
- akshare:network_disabled_by_policy
- efinance:network_disabled_by_policy
- qstock:provider_package_unavailable
- yfinance:network_disabled_by_policy
- local_import:local_import_current_approved_ohlcv_rows_missing

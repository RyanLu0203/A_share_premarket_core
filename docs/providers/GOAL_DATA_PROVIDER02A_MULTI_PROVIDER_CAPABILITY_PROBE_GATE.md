# GOAL-DATA-PROVIDER-02A Multi-Provider Capability Probe Gate

GOAL-DATA-PROVIDER-02A is a review-only provider capability probe. It records whether Tushare Pro, Baostock, AkShare, efinance, qstock, yfinance, and local import can plausibly support a future source-backed 50-symbol x 120-trading-date evaluation panel.

It does not build that panel. It does not create recommendation diagnostics, position-band diagnostics, backtests, equity curves, portfolio returns, dashboards, trading, broker, production, local-lake, factor-mining, or DQN/RL outputs.

## Provider Rules

- Tushare Pro requires `TUSHARE_TOKEN`, `ASHARE_ALLOW_TUSHARE=1`, and `ASHARE_ALLOW_NETWORK_INGESTION=1`; missing token records `tushare_unavailable_missing_token`.
- Baostock checks package availability by default and, only with network opt-in, probes login/logout and `query_history_k_data_plus` using the required daily field set.
- AkShare checks package availability and, only with network opt-in, probes A-share daily OHLCV and benchmark/index history.
- efinance checks package availability and maps Chinese quote-history fields into the canonical OHLCV concepts.
- qstock checks data-module availability only; backtest and strategy modules are not used.
- yfinance is auxiliary only and is marked `auxiliary_not_primary`.
- local import is a fallback and cannot substitute fixture/demo rows for source-backed panel readiness.

## Outputs

- `outputs/providers/goal_data_provider02a_provider_capability_probe.csv`
- `outputs/providers/goal_data_provider02a_provider_schema_mapping.csv`
- `outputs/providers/goal_data_provider02a_provider_failure_taxonomy.csv`
- `outputs/audits/goal_data_provider02a_multi_provider_capability_probe_report.md`
- `outputs/audits/goal_data_provider02a_multi_provider_capability_probe_manifest.json`
- `outputs/audits/goal_data_provider02a_multi_provider_capability_probe_audit.md`
- `configs/providers/goal_data_provider02a_provider_ladder_contract.yaml`

## Current Result

- Status: `PASS_WITH_WARNINGS`
- Providers represented: `7`
- Network enabled during probe: `false`
- Tested symbols: `002475.SZ;600036.SH`

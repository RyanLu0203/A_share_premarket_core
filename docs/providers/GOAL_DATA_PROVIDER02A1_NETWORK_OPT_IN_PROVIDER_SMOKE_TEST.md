# GOAL-DATA-PROVIDER-02A.1 Network Opt-In Provider Smoke Test

GOAL-DATA-PROVIDER-02A.1 is a review-only network-opt-in provider smoke test. It may attempt live provider access only when `ASHARE_ALLOW_NETWORK_INGESTION=1` is present. Tushare Pro additionally requires `ASHARE_ALLOW_TUSHARE=1` and `TUSHARE_TOKEN` from the environment.

The gate records provider status, schema mapping status, failure taxonomy, live-access attempt flags, and row/date counts. It does not persist raw provider payloads, provider tokens, final evaluation panel rows, diagnostics, backtests, dashboards, trading, production, broker, local-lake, factor-mining, or DQN/RL outputs.

## Outputs

- `outputs/providers/goal_data_provider02a1_network_smoke_test_results.csv`
- `outputs/providers/goal_data_provider02a1_schema_mapping_results.csv`
- `outputs/providers/goal_data_provider02a1_failure_taxonomy.csv`
- `outputs/audits/goal_data_provider02a1_network_smoke_test_report.md`
- `outputs/audits/goal_data_provider02a1_network_smoke_test_manifest.json`
- `outputs/audits/goal_data_provider02a1_network_smoke_test_audit.md`
- `configs/providers/goal_data_provider02a1_network_smoke_test_contract.yaml`

## Current Result

- Status: `PASS_WITH_WARNINGS`
- Providers represented: `7`
- Network opt-in present: `false`
- Live provider access attempted count: `0`
- Tested symbols: `002475.SZ;600036.SH`

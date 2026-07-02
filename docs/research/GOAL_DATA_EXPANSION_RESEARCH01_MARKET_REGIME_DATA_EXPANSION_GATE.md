# GOAL-DATA-EXPANSION-RESEARCH-01 Market Regime Data Expansion Gate

This gate adds bounded, research-only market-regime data expansion artifacts from committed Arch03, Provider02B, and Regime01 evidence.

It is not a factor-evaluation, recommendation-tiering, position, portfolio, dashboard, trading, broker, production, local-lake, factor-mining, or DQN/RL gate.

## Network Policy

- Default run mode: `offline_dry_run`.
- Live AKShare fetches require `ASHARE_ALLOW_AKSHARE_NETWORK=1` and remain bounded.
- Fresh clone replay uses committed bounded artifacts and requires no live network access.

## Outputs

- `outputs/data_expansion/goal_data_expansion_research01/source_selection.csv`
- `outputs/data_expansion/goal_data_expansion_research01/provider_health.csv`
- `outputs/data_expansion/goal_data_expansion_research01/trading_calendar_status_context.csv`
- `outputs/data_expansion/goal_data_expansion_research01/broad_index_regime_panel.csv`
- `outputs/data_expansion/goal_data_expansion_research01/sector_concept_regime_panel.csv`
- `outputs/data_expansion/goal_data_expansion_research01/liquidity_capital_flow_panel.csv`
- `outputs/data_expansion/goal_data_expansion_research01/symbol_event_context.csv`
- `outputs/data_expansion/goal_data_expansion_research01/expanded_date_regime_feature_panel.csv`
- `outputs/data_expansion/goal_data_expansion_research01/expanded_symbol_context_panel.csv`
- `outputs/data_expansion/goal_data_expansion_research01/data_quality_summary.csv`
- `outputs/data_expansion/goal_data_expansion_research01/construction_warnings.csv`
- `outputs/audits/goal_data_expansion_research01_manifest.json`
- `outputs/audits/goal_data_expansion_research01_report.md`
- `outputs/audits/goal_data_expansion_research01_audit.md`
- `docs/research/GOAL_DATA_EXPANSION_RESEARCH01_MARKET_REGIME_DATA_EXPANSION_GATE.md`
- `configs/research/goal_data_expansion_research01_contract.yaml`

## Status

- Gate status: `PASS_WITH_WARNINGS`
- Recommended next goal: `GOAL-REGIME-LABEL-RESEARCH-02-EXPANDED-MARKET-REGIME-LABEL-REFINEMENT-GATE`

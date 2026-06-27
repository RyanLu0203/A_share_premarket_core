# GOAL-DATA-PROVIDER-02B Source-Backed Evaluation Panel Build Gate

GOAL-DATA-PROVIDER-02B is a review-only source-backed evaluation panel build gate. It may build a bounded normalized A-share panel from live providers when `ASHARE_ALLOW_NETWORK_INGESTION=1` is set, and it may validate committed normalized evidence in no-network replay mode.

The current canonical approved universe has fewer than 50 symbols, so this gate uses `provider_panel_candidate_universe_review_only` and does not alter `configs/universe/approved_symbols.csv`.

## Outputs

- `outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv`
- `outputs/diagnostics/goal_data_provider02b_panel_coverage_summary.csv`
- `outputs/providers/goal_data_provider02b_provider_usage_summary.csv`
- `outputs/providers/goal_data_provider02b_provider_failure_taxonomy.csv`
- `outputs/audits/goal_data_provider02b_source_backed_panel_report.md`
- `outputs/audits/goal_data_provider02b_source_backed_panel_manifest.json`
- `outputs/audits/goal_data_provider02b_source_backed_panel_audit.md`
- `configs/providers/goal_data_provider02b_panel_build_contract.yaml`

## Current Result

- Status: `PASS_WITH_WARNINGS`
- Panel contract status: `source_backed_evaluation_panel_ready_for_dc03`
- Rows: `6000`
- Unique symbols: `50`
- Unique trade dates: `120`
- Date range: `2025-11-19` to `2026-05-21`

## Locked Boundaries

GOAL-V1-DIAGNOSTIC-COVERAGE-03 and GOAL-10B.3 are not implemented by this panel gate; each may only be preserved when its own review-only evidence exists. GOAL-10D, dashboards, signal and portfolio backtests, trading, production, broker, local-lake, factor-mining, and DQN/RL remain locked. This panel is not a recommendation, position, portfolio, or execution output.

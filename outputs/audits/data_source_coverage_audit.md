# Data Source Coverage Audit

Status: `PASS_WITH_WARNINGS`

number of sources: `4`
number of approved symbols: `2`
number of candidate symbols: `6`
number of blocked symbols: `4`

current_approved_symbols: `2`
current_trading_dates: `4`
configured_trading_dates: `6`
current_pit_ready_rows: `8`
current_label_ready_rows: `8`
current_stage6c_rows: `8`
target_engineering_pilot_symbols: `50`
target_engineering_pilot_dates: `120`
target_engineering_pilot_rows: `6000`
coverage_gap_to_engineering_pilot: `symbols=48;dates=116;rows=5992`
source_x_field_availability: `outputs/audits/source_field_coverage_matrix.csv`

The current clean repository has deterministic fixture coverage only. Provider ingestion is contract-defined and network-disabled by default.

## Failures

## Warnings
- approved universe is below engineering_pilot symbol target
- Stage 6C validation dates are below engineering_pilot target
- Stage 6C rows are below engineering_pilot target

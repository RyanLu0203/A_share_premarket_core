# GOAL-NETWORK-EVIDENCE-INGESTION-01 — Readiness Rerun Handoff

## materially_expanded = True

The acquired evidence materially expands the raw panel. To rerun GOAL-FACTOR-READINESS-RESEARCH-01 on it:

- exact bundle: `outputs/research/network_ingestion/` (checksummed evidence_bundle_manifest.json)
- symbol universe: 50 symbols (see symbol_coverage.csv)
- date range: expanded to 843 trading dates (2023-01..2026-06)
- provider set: baostock (committed) + akshare_sina (live-acquired, independent)
- feature families: equity daily price/return + index market context (PIT-safe, trailing only)
- PIT contract: daily close available next session; forward returns to be computed POST-HOC only, never stored as features
- validation split compatibility: chronological walk-forward + holdout as in readiness gate; longer history enables more folds

## Guardrails

Do NOT lower thresholds. Do NOT auto-promote factors. Do NOT execute RecTiering. Readiness must still be earned out-of-sample.
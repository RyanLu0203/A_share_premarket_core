# Provider Ingestion Contract

GOAL-06C.5 defines provider ingestion contracts without enabling production or
network ingestion by default. GOAL-06C.6 adds a compliant AKShare ingestion gate
that remains disabled unless explicitly opted in.

## Categories

- `ohlcv_daily`
- `benchmark_daily`
- `announcement_metadata`
- `market_metadata`
- `sector_metadata`

## Providers

Expected providers are tracked in `configs/providers/provider_registry.yaml`.
Providers that are not implemented must be marked
`contract_defined_not_implemented`; the repository must not fake provider
success.

Network ingestion is optional and disabled by default. A provider run must use
`ASHARE_ALLOW_NETWORK_INGESTION=1` or `--allow-network`, write heavy/full data
only under the local data root, record checksums for local bundles, and keep
GitHub artifacts sanitized.

GOAL-06C.6 uses AKShare as the primary compliant route:

- `stock_info_a_code_name`
- `stock_zh_a_spot_em`
- `stock_zh_a_hist`
- `index_zh_a_hist`

Provider failures must be classified as policy disabled, dependency missing,
schema changed, empty response, HTTP 403/429, bot/captcha/verify challenge, or
other explicit classes. The repo does not use cloakbrowser, stealth browser
automation, captcha solving, proxy rotation, raw HTML storage, or provider
bypass logic.

## Audit

Run:

```bash
python scripts/audit_data_source_coverage.py
python scripts/audit_provider_failure_classification.py
python scripts/run_goal06c6_source_backed_engineering_pilot_bundle.py
```

The audit writes the provider ingestion contract report, source coverage
matrices, universe expansion audit, trading calendar audit, and source gap
analysis. The current clean bootstrap remains fixture-backed and below
`engineering_pilot`.

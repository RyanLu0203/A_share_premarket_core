# Provider Ingestion Contract

GOAL-06C.5 defines provider ingestion contracts without enabling production or
network ingestion by default.

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

Network ingestion is optional and disabled by default. Any future network run
must use an explicit flag, write raw payloads only under the local data root,
record checksums for local bundles, and keep GitHub artifacts sanitized.

## Audit

Run:

```bash
python scripts/audit_data_source_coverage.py
```

The audit writes the provider ingestion contract report, source coverage
matrices, universe expansion audit, trading calendar audit, and source gap
analysis. The current clean bootstrap remains fixture-backed and below
`engineering_pilot`.

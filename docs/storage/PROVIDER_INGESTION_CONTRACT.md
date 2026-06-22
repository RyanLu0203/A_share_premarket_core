# Provider Ingestion Contract

GOAL-06C.5 defines provider ingestion contracts without enabling production or
network ingestion by default. GOAL-06C.6 adds a compliant AKShare ingestion gate
that remains disabled unless explicitly opted in. GOAL-06C.6A adds scoped
finance-only network isolation evidence and a provider failure taxonomy.

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

Provider failures must be classified by specific failure type, not as a broad
generic network failure when a more precise class can be determined. Required
network and access mappings include:

- ProxyError: `EXTERNAL_PROXY_ENVIRONMENT_FAILURE`,
  `EXTERNAL_SYSTEM_PROXY_OR_VPN_ROUTE_FAILURE`, or
  `FINANCE_DIRECT_CHILD_ENV_CLEANED_BUT_PROVIDER_STILL_PROXY_FAILED`
- Timeout: `EXTERNAL_NETWORK_TIMEOUT`
- DNS failure: `DNS_RESOLUTION_FAILURE`
- TLS/certificate failure: `TLS_SSL_FAILURE`
- Connection reset/refused: `CONNECTION_RESET` or `CONNECTION_REFUSED`
- HTTP 403/429/5xx: `HTTP_403_FORBIDDEN`, `HTTP_429_RATE_LIMITED`, or
  `HTTP_5XX_PROVIDER_ERROR`
- Captcha, verify, bot, login, consent, JavaScript, or HTML challenge pages:
  anti-bot/access classes only, with raw HTML suppressed
- Schema, parser, data quality, PIT/label, storage, and workflow-governance
  failures: their corresponding non-network layers

The current GOAL-06C.6/GOAL-06C.6A provider ingestion gate does not use
browser-based bypass tooling, raw HTML storage, or provider bypass logic. Future
browser-ingestion work would require a separate explicit goal, compliance
review, and workflow-status update.

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

GOAL-06C.6A writes:

- `outputs/audits/provider_failure_events.csv`
- `outputs/audits/provider_failure_summary.md`
- `outputs/audits/goal06c6_network_isolation_report.md`
- `outputs/audits/goal06c6_failure_taxonomy_report.md`

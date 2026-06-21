# Data Storage Architecture

GOAL-06C.5 adds a local research storage contract. It is not a production
database, not a broker integration, and not a source of recommendation output.

## Local Root

The runtime data root is resolved from `ASHARE_PREMARKET_DATA_ROOT`. If the
environment variable is absent, scripts use the documented default
`/Users/luxinyu/data/ashare_premarket/`.

The data root must remain outside this Git repository. GitHub stores only code,
configs, schemas, tiny samples, manifest summaries, coverage summaries, audit
reports, readiness reports, and workflow docs.

## Local Directory Contract

```text
raw/
  akshare/
  eastmoney/
  cninfo/
  sina/
bundles/
  engineering_pilot/<bundle_id>/
lake/
  ohlcv_daily/
  benchmark_daily/
  announcements_metadata/
  source_coverage/
  pit_signal_panel/
  label_panel/
  stage6c_engineering_panel/
metadata/
  ashare_premarket.duckdb
  schema_registry/
exports/
  github_artifacts/
  audit_samples/
```

Parquet and DuckDB are allowed only in the local data root. If those runtimes
are unavailable, CSV may be used with the same logical schemas.

## GitHub Hygiene

Forbidden committed artifacts include raw provider payloads, raw HTML, full
announcement text, database files, Parquet lake files, notebooks, caches, logs,
private credentials, large model artifacts, and production model files.

The storage gate is:

```bash
python scripts/audit_storage_policy.py
```

The bundle summary gates are:

```bash
python scripts/build_data_bundle_manifest.py
python scripts/audit_data_bundle_manifest.py
```

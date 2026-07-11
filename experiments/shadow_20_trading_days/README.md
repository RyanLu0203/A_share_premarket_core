# Twenty-Trading-Day Shadow Observation Scaffold

Status: `PREPARED_NOT_STARTED`.

This directory prepares metadata and local folder boundaries for a future
owner-authorized, 20-trading-day shadow observation. It does not start the
experiment, backfill observations, calculate performance, or authorize paper
trading, broker access, orders, recommendations, or production use.

## Structure

- `config.template.yaml`: inert configuration template; dates remain unset.
- `metadata.schema.json`: schema for one future observation metadata record.
- `observations/`: local observation metadata; contents are ignored by Git.
- `snapshot_refs/`: local references to immutable OPM manifests; contents are
  ignored by Git.
- `logs/`: local operational logs; contents are ignored by Git.

Before any observation begins, the owner must authorize a start date and a
separate reviewed configuration must be frozen. Each future observation must
reference an existing immutable OPM manifest and checksum. No raw provider
payload, full market data, credential, private holding, or performance claim
belongs in this directory or in Git.

The authoritative existing preparation evidence remains:

- `outputs/research/goal_premarket_position_management_operational01_shadow_experiment_contract.csv`
- `outputs/research/goal_premarket_position_management_operational01_experiment_freeze_manifest.json`
- `outputs/research/goal_daily_incremental_evidence_refresh01_experiment_readiness_contract.csv`

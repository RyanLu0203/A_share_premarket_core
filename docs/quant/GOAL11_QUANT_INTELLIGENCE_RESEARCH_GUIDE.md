# GOAL-11 Quant Intelligence Research Guide

## Scope

GOAL-11 is a local, deterministic research foundation. It builds versioned
point-in-time features, an interpretable alpha, a fixed linear ranking
baseline, chronological evaluation, and risk-adjusted research scores. It
does not create recommendations, positions, portfolio weights, target prices,
orders, broker messages, or production predictions.

Generated data belongs only under `outputs/local/`, which is ignored by Git.
Do not move generated feature rows, labels, model diagnostics, or evaluation
files into committed output directories.

## Input Manifest

The loader accepts an explicit checksummed manifest. Paths are repository
relative and root-confined.

```json
{
  "schema_version": "goal11_governed_market_snapshot_v1",
  "snapshot_id": "local-snapshot-id",
  "cutoff_date": "YYYY-MM-DD",
  "generation_timestamp": "YYYY-MM-DDTHH:MM:SS+00:00",
  "code_commit": "40-character-feature-generation-commit",
  "source_path": "outputs/local/evidence/canonical_market_data.csv",
  "source_checksum": "sha256-of-source-csv",
  "adjustment": "qfq",
  "availability_policy": "OBSERVATION_DATE",
  "column_map": {
    "date": "trade_date",
    "symbol": "symbol",
    "close": "canonical_close",
    "open": "open",
    "high": "high",
    "low": "low",
    "volume": "volume",
    "index_close": "index_close"
  },
  "manifest_checksum": "canonical-json-checksum-excluding-this-field"
}
```

`date`, `symbol`, and `close` are required mappings. Other mappings are
optional. Missing high/low, volume, or index evidence is retained as missing
and produces explicit availability reasons. The committed historical
canonical baseline is close-only, so it cannot support ATR, volume, or full
index-regime features. The dated operational canonical CSV is local evidence;
a fresh clone must not claim it is present.

`market_breadth_1d` is snapshot breadth over identical observed symbol sets on
adjacent dates. It is not full-market breadth because the repository does not
currently provide PIT-safe full-market constituent metadata.

The `OBSERVATION_DATE` policy means an end-of-day row becomes available on its
observation date. If the source records a more precise governed availability
field, map it as `available_at` instead; its calendar date must still match the
observation date. Cross-date delayed availability is rejected by this v1
date-grain contract. Forward-return, label, future, and target columns are
forbidden in the feature source regardless of mapping.

## Python Workflow

```python
from pathlib import Path

from ashare_premarket.quant_foundation.features import load_feature_config
from ashare_premarket.quant_foundation.pipeline import run_quant_intelligence_pipeline
from ashare_premarket.quant_foundation.snapshot_loader import load_governed_snapshot_from_manifest
from ashare_premarket.quant_foundation.store import write_local_research_run

root = Path.cwd()
snapshot = load_governed_snapshot_from_manifest(
    root,
    root / "outputs/local/evidence/goal11_snapshot.json",
)
config = load_feature_config(root)

# Labels are a separate, checksummed list. Each row requires date, symbol,
# label_available_at, forward_return, label_version, source_snapshot_id,
# and checksum. They are never accepted by feature construction or persisted
# by the local feature store.
labels = load_labels_from_governed_local_source()

result = run_quant_intelligence_pipeline(snapshot, labels, config)
write_local_research_run(
    root,
    root / "outputs/local/goal11",
    "research-run-001",
    result,
)
```

The placeholder label-loading call above is intentionally owner-supplied. The
repository does not fabricate labels or download data implicitly.

## Output Files

An immutable local run contains:

- `features.csv`
- `alpha_scores.csv`
- `linear_scores.csv`
- `linear_ranker.json`
- `evaluation.json`
- `run_manifest.json`

The store refuses an existing run directory. Its manifests contain only
relative artifact names and deterministic checksums, so identical inputs
produce byte-identical files across output roots.

## Scientific Interpretation

- `alpha_score` is the pre-specified momentum plus trend plus volume-strength
  score less the first risk penalty.
- `risk_adjusted_score` applies the explicitly disclosed second risk penalty.
- The linear ranker is fixed-ridge, chronological, and out-of-sample. It does
  not tune on a final holdout.
- IC, Rank IC, Precision@K, Recall@K, feature stability, time stability, and
  top-K turnover are research diagnostics, not performance promises.
- Warm-up periods, incomplete cross-sections, and missing evidence abstain.

Run the read-only GOAL-11 governance audit with:

```bash
python scripts/audit_goal11_quant_intelligence_foundation.py
```

The optional research dashboard is deferred. Existing 14 canonical
interfaces, 22 GET routes, and all production/downstream locks remain
unchanged.

# GOAL-11 Quant Intelligence Foundation Design

## Decision

Build a self-contained `ashare_premarket.quant_foundation` research package
that accepts a governed snapshot object, computes evidence-aware point-in-time
features, produces interpretable and deterministic linear ranking research
scores, evaluates them chronologically, and optionally writes only immutable
local artifacts.

## Alternatives Considered

1. Extend the historical goal-specific factor modules. Rejected because their
   schemas and committed outputs encode earlier experiments rather than a
   reusable versioned feature-store contract.
2. Add new API routes and workspace pages. Rejected for GOAL-11 because the
   current 22-route interface and locked quant workspace are exact-parity
   contracts; Issue #39 makes dashboard work conditional.
3. Add LightGBM or XGBoost. Rejected because a fixed linear baseline satisfies
   the issue while preserving deterministic cross-platform installation.
4. Materialize a committed feature dataset. Rejected because Issue #39 and
   repository governance explicitly forbid committing generated datasets.

## Components

- `contracts.py`: immutable snapshot/feature/score contracts and forbidden
  action-field validation.
- `features.py`: deterministic point-in-time feature calculations and evidence
  availability codes.
- `alpha.py`: same-date interpretable alpha and risk-adjusted research score.
- `linear_ranker.py`: fixed-ridge chronological out-of-sample baseline.
- `evaluation.py`: chronological folds, IC/RankIC, top-K, stability, and
  turnover metrics.
- `store.py`: root-confined, immutable, local-only CSV/manifest persistence.
- `pipeline.py`: orchestration without network access or production side
  effects.

## Scientific Controls

- Features are generated before labels are accepted.
- Snapshot cutoff and per-row availability timestamps are mandatory.
- Fixed formulas, windows, weights, K, and ridge coefficient are versioned.
- Random splits, tuning, and future-data normalization are absent by design.
- Optional evidence yields explicit nulls or abstention, never imputation.
- All ordering and checksums are canonical.

## Acceptance Mapping

Issue #39 feature coverage maps to `features.py`; interpretable alpha and the
linear comparison map to `alpha.py` and `linear_ranker.py`; chronological and
walk-forward evaluation maps to `evaluation.py`; reproducibility, lineage, and
artifact cleanliness map to `contracts.py`, `store.py`, tests, and governance
audits. The optional dashboard is explicitly deferred in the architecture
review because current interface locks do not permit a safe surface change.

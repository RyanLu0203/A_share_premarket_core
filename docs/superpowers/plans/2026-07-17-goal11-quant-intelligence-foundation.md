# GOAL-11 Quant Intelligence Foundation Implementation Plan

**Goal:** Implement Issue #39 as a deterministic, auditable, research-only
feature store, alpha/ranking framework, and chronological evaluation layer.

**Architecture:** A standard-library `quant_foundation` package consumes only
validated governed snapshots. Feature construction is label-free; labels enter
only chronological evaluation. Runtime artifacts are confined to ignored local
paths, and existing API/UI/production locks remain unchanged.

**Tech Stack:** Python 3.12 standard library, pytest, existing repository audit
scripts.

### Task 1: Snapshot and feature contracts

**Files:** `tests/quant_foundation/test_contracts.py`,
`src/ashare_premarket/quant_foundation/contracts.py`, versioned JSON config.

1. Write tests for metadata, duplicate/future/label rejection, checksums, and
   forbidden action fields.
2. Run focused tests and confirm expected import failure.
3. Implement the minimal immutable contracts and validators.
4. Re-run focused tests to green.

### Task 2: Point-in-time feature store

**Files:** `tests/quant_foundation/test_features.py`,
`src/ashare_premarket/quant_foundation/features.py`.

1. Write deterministic synthetic-fixture tests for all five feature families,
   warm-up behavior, evidence absence, PIT use, and byte-identical rows.
2. Confirm red, implement close/OHLCV/market-context calculators, then confirm
   green.

### Task 3: Interpretable alpha and risk-adjusted score

**Files:** `tests/quant_foundation/test_alpha.py`,
`src/ashare_premarket/quant_foundation/alpha.py`.

1. Write tests for formula components, same-date ranking, risk inputs,
   abstention, determinism, and non-actionable schemas.
2. Confirm red, implement fixed formulas, then confirm green.

### Task 4: Deterministic linear ranking baseline

**Files:** `tests/quant_foundation/test_linear_ranker.py`,
`src/ashare_premarket/quant_foundation/linear_ranker.py`.

1. Write tests proving chronological fitting, no final-holdout leakage,
   deterministic coefficients/scores, and insufficient-history abstention.
2. Confirm red, implement fixed-ridge fitting, then confirm green.

### Task 5: Evaluation framework

**Files:** `tests/quant_foundation/test_evaluation.py`,
`src/ashare_premarket/quant_foundation/evaluation.py`.

1. Write tests for chronological folds, walk-forward ordering, IC/RankIC,
   Precision@K, Recall@K, feature stability, and ranking turnover.
2. Confirm red, implement metrics, then confirm green.

### Task 6: Local store and integrated pipeline

**Files:** `tests/quant_foundation/test_pipeline.py`,
`src/ashare_premarket/quant_foundation/store.py`,
`src/ashare_premarket/quant_foundation/pipeline.py`.

1. Write tests for immutable local writes, unsafe-path rejection,
   reproducible manifests, separation of labels, and complete pipeline output.
2. Confirm red, implement minimal persistence/orchestration, then confirm
   green.

### Task 7: Governance integration and documentation

**Files:** project capability/workflow documentation, architecture index,
GOAL-11 research guide, tests for locks and repository cleanliness.

1. Write governance tests proving `ready_factor_count == 0`, 22 API routes are
   unchanged, production locks remain false, and no generated artifacts are
   required or committed.
2. Confirm red where new GOAL-11 metadata is absent.
3. Add research documentation and narrowly scoped capability/workflow state.
4. Run focused governance tests.

### Task 8: Validation and publication

1. Run compileall and all GOAL-11 focused tests.
2. Run full pytest and the canonical validation profile.
3. Run architecture, workflow, safety, adapter, PIT/leakage, destructive,
   secret, and path audits.
4. Verify frontend/API deterministic parity remains unchanged.
5. Verify a fresh clone with the complete validation matrix.
6. Inspect `git diff`, ensure no forbidden generated artifacts, commit once,
   push the dedicated branch, open one PR into `project-current`, and stop.

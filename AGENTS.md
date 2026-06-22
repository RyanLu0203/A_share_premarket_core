# AGENTS

This file is long-term project memory for Codex and other coding agents.

## Operating Rules

- Work inside this clean target repository unless the user explicitly asks
  otherwise.
- Use GitHub as the durable source of truth.
- Treat `RyanLu0203/A_share_market_analysis_and_prediction` as historical
  legacy/evidence reference only.
- Never push raw payloads, quarantine files, SQLite DBs, credentials, `.env`,
  cache payloads, full news text, notebooks, production model artifacts,
  dashboards, or private logs.

## Current System Truth

- Approved symbols: `002475.SZ`, `600036.SH`.
- Blocked/pending: `000625.SZ`, `000858.SZ`, `601138.SH`, `601208.SH`.
- Active scoring boundary: project start through GOAL-06B.
- GOAL-06B supervised baseline training is review-only and pilot-only.
- GOAL-06C expanded validation and ranking baseline is implemented_review_only.
- GOAL-06C.5 storage, data bundle, source coverage, and engineering panel
  readiness is implemented_review_only.
- GOAL-06C.6 source-backed AKShare/provider ingestion is implemented_review_only
  and network-disabled by default.
- GOAL-06C.6A scoped finance network isolation and provider failure taxonomy is
  implemented_review_only. Network failures must be classified by specific
  failure type, not as a generic network bucket when the subtype is knowable.
- GOAL-06C.7 provider-ladder engineering data base expansion is
  implemented_review_only. Browser-assisted ingestion is optional,
  finance-domain-only, disabled by default, and requires
  `ASHARE_ENABLE_BROWSER_ASSISTED_PROVIDER=1 --enable-browser-assisted`.
- The current engineering panel tier is `contract_demo`; GOAL-06D remains
  blocked until GOAL-06C.7 reaches source-backed `engineering_pilot`.
- GOAL-06D is future_review_only only; no model comparison/calibration is
  implemented yet.
- Feature-label merge and leakage audit are active.
- Recommendation, risk overlay, dashboard, paper/live trading, production DB
  writes, production model promotion, and DQN/RL remain locked.
- The default GOAL-06C.6/GOAL-06C.6A provider ingestion gate uses direct
  AKShare/local-import paths. The explicit CloakBrowser reference probe is
  separate, opt-in, tag-only, sanitized, and does not unlock GOAL-06D or any
  downstream module by itself.
- Python `>=3.9` is supported for the clean GOAL-06B workflow.
- Committed validation summaries must be deterministic; volatile runtime timing
  belongs in ignored local diagnostics under `outputs/local/runtime/`.

## Required Agent Reading Order

1. `PROJECT_STATE.md`
2. `README.md`
3. `CODEX.md`
4. `docs/09_STEP_ITERATION_LOG.md`
5. `docs/02_DATA_ENGINE.md`
6. `ROADMAP.md`

## Update Discipline

Every meaningful program advance must update:

- `PROJECT_STATE.md`
- `docs/09_STEP_ITERATION_LOG.md`
- `CHANGELOG.md`
- relevant docs under `docs/`

Do not leave major state changes only in chat transcripts or local output files.

## Validation Habit

Minimum normal validation:

```bash
python -m compileall src scripts tests
python -m pytest tests -q
python scripts/run_goal06c_expanded_validation.py
python scripts/audit_storage_policy.py
python scripts/audit_data_bundle_manifest.py
python scripts/audit_data_source_coverage.py
python scripts/audit_provider_failure_classification.py
python scripts/run_goal06c7_provider_ladder_engineering_data_base_expansion.py
python scripts/audit_browser_assisted_provider.py
python scripts/audit_workflow_cleanliness.py
python scripts/run_goal06c6_source_backed_engineering_pilot_bundle.py
python scripts/rebuild_stage6c_from_engineering_panel.py
python scripts/audit_stage6c_expanded_validation.py
python scripts/audit_stage6c_ranking_baselines.py
python scripts/run_stage6c_walk_forward_validation.py
python scripts/run_safety_gate.py
python scripts/run_adapter_audit.py
```

For GOAL-06B active-trunk changes, also run:

```bash
python scripts/audit_workflow_status.py
python scripts/run_goal06b_regression_suite.py
python scripts/run_e2e_trunk_verification_through_goal06b.py
python scripts/run_e2e_trunk_validation_through_goal06b.py
python scripts/run_workflow_diagnostics.py
```

## Workflow Promotion Rule

A future workflow block can only be promoted from dotted/future to
solid/implemented if:

1. The corresponding goal has a readiness report.
2. The readiness report is `PASS` or acceptable `PASS_WITH_WARNINGS`.
3. Validation and verification commands pass.
4. `configs/project/workflow_status.csv` is updated.
5. README and architecture diagrams are updated.
6. `PROJECT_STATE.md` is updated.
7. Locked downstream modules remain locked unless explicitly unlocked by that
   goal.

Do not silently change the workflow diagram to make future stages look
implemented. Do not add new downstream blocks without updating
`workflow_status.csv`. Do not remove locks from risk, recommendation,
dashboard, paper/live trading, production, or DQN/RL unless a later explicit
gate allows it.

## Git Safety

- Branch from `main`; do not push directly to `main` unless the user has
  explicitly requested the clean bootstrap to land on `main`.
- Stage explicit files only.
- Keep generated runtime evidence out of commits unless it is a deliberately
  sanitized, tiny, review-facing fixture or required GOAL-06B audit output.
- Do not commit local-only runtime timing files.
- Report branch, commit hash, validation, excluded files, and review items.

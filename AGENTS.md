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
- The current source-backed GOAL-06C.7 provider-ladder panel tier is
  `engineering_pilot`: 50 symbols, 120 validation dates, and 6000 rows.
- GOAL-06D is implemented_review_only and currently `PASS_WITH_WARNINGS`.
  It selected `score_based_alpha_ranking` as a weak review-only baseline.
- GOAL-06D.1 is implemented_review_only and currently `PASS_WITH_WARNINGS`.
  It selected `raw_score_based_alpha_ranking` as a weak but bounded review-only
  baseline and allows GOAL-07A only as design-only preparation with warnings.
- GOAL-07A is implemented_design_only and currently `PASS_WITH_WARNINGS`. It
  defines design artifacts and audits only; no risk calculation is active.
- GOAL-07A.1 is implemented_review_only and currently `PASS_WITH_WARNINGS`. It reviews GOAL-07A design convertibility and records GOAL-07B readiness for an explicit review-only unlock request.
- GOAL-07B.0 is implemented_review_only and currently `PASS_WITH_WARNINGS`.
  It preserves GOAL-07B eligibility and does not itself calculate risk.
- GOAL-07B is implemented_review_only and currently `PASS_WITH_WARNINGS`. It
  produces deterministic, non-actionable risk diagnostics at
  `trade_date + symbol` grain.
- GOAL-08A is implemented_design_only and currently `PASS`. It defines a
  names-only future recommendation contract, warning propagation rules,
  HIGH-risk actionability blocking, and zero-row schema evidence only.
- GOAL-STORAGE-01 is implemented_infrastructure_only and currently `PASS`. It
  hardens the local research lake contract, `ASHARE_PREMARKET_DATA_ROOT`
  resolution, directory boundaries, placement rules, manifest/checksum
  requirements, schema registry governance, and GitHub hygiene only.
- GOAL-08B.0 is implemented_review_only and currently `PASS_WITH_WARNINGS`.
  It marks GOAL-08B review-only eligibility using only prior GOAL-07B,
  GOAL-08A, and GOAL-STORAGE-01 PASS/PASS_WITH_WARNINGS evidence. It does not
  itself create recommendation diagnostics rows.
- GOAL-08B is implemented_review_only and currently `PASS_WITH_WARNINGS`. It
  generates 100 deterministic, non-actionable recommendation diagnostic rows at
  `trade_date + symbol` grain from GOAL-07B risk diagnostics and GOAL-08A
  contract rules. `actionability_status` is always `never_actionable`.
- GOAL-09.0 is implemented_review_only and currently `PASS_WITH_WARNINGS`. It
  marks GOAL-09 position-band diagnostics `future_review_only` eligible only
  for a future explicit non-actionable prototype request.
- GOAL-09 is future_review_only eligible but not implemented.
- Feature-label merge and leakage audit are active.
- Actionable recommendation execution, position output, position sizing,
  dashboard, paper/live trading, production DB writes, production model
  promotion, V2 factor mining, and DQN/RL remain locked or not implemented.
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
python scripts/run_goal06d_model_comparison_calibration.py
python scripts/audit_goal06d_feature_contract.py
python scripts/audit_goal06d_split.py
python scripts/audit_goal06d_model_comparison.py
python scripts/audit_goal06d_calibration.py
python scripts/audit_goal06d_stability.py
python scripts/audit_goal06d_governance.py
python scripts/audit_goal06d_boundary_locks.py
python scripts/run_goal07b0_risk_overlay_review_only_unlock_gate.py
python scripts/audit_goal07b0_risk_overlay_review_only_unlock_gate.py
python scripts/run_goal07b_risk_overlay_calculation_prototype.py
python scripts/audit_goal07b_risk_overlay_calculation_prototype.py
python scripts/run_goal08a_recommendation_contract_design_gate.py
python scripts/audit_goal08a_recommendation_contract_design_gate.py
python scripts/run_goal_storage01_local_research_lake_hardening_gate.py
python scripts/audit_goal_storage01_local_research_lake_hardening_gate.py
python scripts/run_goal08b0_recommendation_review_only_unlock_gate.py
python scripts/audit_goal08b0_recommendation_review_only_unlock_gate.py
python scripts/run_goal08b_recommendation_diagnostics_prototype.py
python scripts/audit_goal08b_recommendation_diagnostics_prototype.py
python scripts/run_goal090_position_band_review_only_unlock_gate.py
python scripts/audit_goal090_position_band_review_only_unlock_gate.py
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
`workflow_status.csv`. Do not remove locks from downstream recommendation,
dashboard, paper/live trading, production, backtest, factor-mining, or DQN/RL
unless a later explicit gate allows it.

## Git Safety

- Branch from `main`; do not push directly to `main` unless the user has
  explicitly requested the clean bootstrap to land on `main`.
- Stage explicit files only.
- Keep generated runtime evidence out of commits unless it is a deliberately
  sanitized, tiny, review-facing fixture or required GOAL-06B audit output.
- Do not commit local-only runtime timing files.
- Report branch, commit hash, validation, excluded files, and review items.

## GOAL-06D.1 Agent Note

GOAL-06D.1 is implemented review-only warning repair. The repaired baseline may
remain weak but bounded; GOAL-07A has proceeded only as design-only governance
with warnings. Do not create recommendation, position, risk calculation,
dashboard, paper/live trading, production, factor-mining, or DQN/RL outputs.

## GOAL-07A Agent Note
## GOAL-07A.1 Agent Note

GOAL-07A.1 is review-only/design-review-only. It can maintain readiness reports, warning classifications, and unlock-readiness manifests, but must not itself implement GOAL-07B or create risk calculation, recommendation, position, dashboard, trading, production, backtest, factor-mining, broker, or DQN/RL outputs. GOAL-07B.0 can mark GOAL-07B `future_review_only` eligible or preserve an existing GOAL-07B `implemented_review_only` diagnostic state using prior PASS/PASS_WITH_WARNINGS design-review evidence only; it must not create any calculation or downstream output. GOAL-07B can produce only review-only, non-actionable risk diagnostics. GOAL-08A may define only names-only future recommendation contract evidence with zero rows. GOAL-STORAGE-01 may harden only local research lake governance and GitHub hygiene; it must not materialize a lake, expand data coverage, create diagnostics, or unlock GOAL-08B by itself. GOAL-08B.0 can mark GOAL-08B review-only eligible using prior evidence only, but must not itself create recommendation diagnostics rows. GOAL-08B can produce only review-only, non-actionable recommendation diagnostics at `trade_date + symbol` grain. GOAL-09.0 can mark GOAL-09 position-band diagnostics future_review_only eligible using prior evidence only, but must not itself implement GOAL-09 or create position-band, position sizing, portfolio weight, dashboard, trading, production, backtest, factor-mining, broker, local-lake, or DQN/RL outputs. All actionable recommendation/execution paths remain locked.



GOAL-07A is design-only. It may maintain contracts, schema definitions, rule
catalogs, state machine designs, warning mappings, governance docs, and audits.
It must not calculate risk overlay values, assign risk tags to real symbols,
produce recommendations or positions, create dashboards, write trading or
production data, activate factor mining, or implement GOAL-07B.

V2 factor research is planned but inactive. Keep
`configs/factors/v2_factor_research_contract.yaml` locked unless a future
explicit V2 goal authorizes activation.

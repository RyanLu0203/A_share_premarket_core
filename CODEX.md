# CODEX Project Memory

## Mission

Maintain a clean, PIT-safe, review-only A-share pre-market workflow through
GOAL-06B, plus the GOAL-06C review-only expanded validation extension, the
GOAL-06C.5/GOAL-06C.6/GOAL-06C.6A/GOAL-06C.7 engineering data foundation gates,
the GOAL-06D/GOAL-06D.1 review-only model comparison/calibration/stability
governance gates, and the GOAL-07A design-only risk governance gate. Preserve
reproducibility and source governance before any future risk calculation work.

## Current Reliable Facts

- This target repository is the active source of truth.
- The source repository is historical legacy/evidence reference only.
- The active scoring workflow stops at GOAL-06B supervised baseline training
  gate.
- GOAL-06B is review-only and pilot-only.
- GOAL-06C is implemented_review_only for expanded validation, ranking
  baselines, metrics, walk-forward diagnostics, and stability diagnostics.
- GOAL-06C.5 is implemented_review_only for storage policy, data bundle,
  source coverage, and engineering panel readiness.
- GOAL-06C.6 is implemented_review_only for provider failure classification,
  optional AKShare ingestion, local source-backed bundle creation, and
  source-backed Stage 6C engineering panel audits.
- GOAL-06C.6A is implemented_review_only for finance-only network isolation,
  provider failure events, and specific failure taxonomy reports.
- GOAL-06C.7 is implemented_review_only for provider-ladder engineering data
  base expansion. The ladder is direct finance provider, optional
  browser-assisted provider, local import, and future vendor placeholder.
- Browser-assisted ingestion is disabled by default, requires
  `ASHARE_ENABLE_BROWSER_ASSISTED_PROVIDER=1` plus `--enable-browser-assisted`,
  uses dynamic import only, and counts only schema-valid finance rows.
- Network failures must be classified by precise type, such as ProxyError,
  timeout, DNS, TLS, connection reset/refused, HTTP access, or anti-bot
  challenge, not as a broad generic network failure when a specific class is
  knowable.
- The current source-backed GOAL-06C.7 provider-ladder panel tier is
  `engineering_pilot`: 50 symbols, 120 validation dates, and 6000 rows.
- Network ingestion is disabled by default and requires
  `ASHARE_ALLOW_NETWORK_INGESTION=1` or `--allow-network`.
- The default GOAL-06C.6/GOAL-06C.6A provider ingestion gate uses direct
  AKShare/local-import paths. The explicit CloakBrowser reference probe is
  separate, opt-in, tag-only, sanitized, and does not unlock GOAL-06D or any
  downstream module by itself.
- GOAL-06D is implemented_review_only and currently `PASS_WITH_WARNINGS`.
  It selected `score_based_alpha_ranking` as a weak review-only baseline.
- GOAL-06D.1 is implemented_review_only and currently `PASS_WITH_WARNINGS`.
  It selected `raw_score_based_alpha_ranking` as a weak but bounded review-only
  baseline and allows GOAL-07A only as design-only preparation with warnings.
- GOAL-07A is implemented_design_only and currently `PASS_WITH_WARNINGS`. It
  defines contracts, future schema, rule catalog, state machine,
  upstream-warning mapping, governance boundary, and V2 lock audits only.
- GOAL-07A.1 is implemented_review_only and currently `PASS_WITH_WARNINGS`. It reviews GOAL-07A design convertibility and marks GOAL-07B ready only for a future explicit review-only unlock request; it does not implement GOAL-07B.
- Production model promotion is false.
- GOAL-07B risk calculation, recommendation, position output, dashboard, paper
  trading, broker/live trading, production DB writes, V2 factor mining, and
  DQN/RL are locked.
- Python `>=3.9` is supported for the clean GOAL-06B workflow; Python `3.9.21`
  passed fresh-clone verification.
- Stable committed reports intentionally use `runtime_seconds=local_only`;
  volatile timing details belong in ignored files under `outputs/local/runtime/`.

## Reading Order

1. `PROJECT_STATE.md`
2. `README.md`
3. `CODEX.md`
4. `docs/09_STEP_ITERATION_LOG.md`
5. `docs/02_DATA_ENGINE.md`
6. `ROADMAP.md`

## Validation Habit

```bash
python -m compileall src scripts tests
python -m pytest tests -q
python scripts/run_goal06c_expanded_validation.py
python scripts/audit_storage_policy.py
python scripts/build_data_bundle_manifest.py
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
python scripts/run_goal06c6_source_backed_engineering_pilot_bundle.py
python scripts/rebuild_stage6c_from_engineering_panel.py
python scripts/audit_stage6c_expanded_validation.py
python scripts/audit_stage6c_ranking_baselines.py
python scripts/run_stage6c_walk_forward_validation.py
python scripts/audit_workflow_status.py
python scripts/run_goal06b_regression_suite.py
python scripts/run_e2e_trunk_verification_through_goal06b.py
python scripts/run_e2e_trunk_validation_through_goal06b.py
python scripts/run_safety_gate.py
python scripts/run_adapter_audit.py
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
`workflow_status.csv`. Do not remove locks from risk calculation,
recommendation, dashboard, paper/live trading, production, or DQN/RL unless a
later explicit gate allows it.

## Do Not Drift

- Do not import legacy implementation code.
- Do not run legacy-only tests as active validation.
- Do not add absolute user-specific paths.
- Do not reintroduce volatile wall-clock timings into committed audit reports.
- Do not commit raw payloads, DBs, notebooks, caches, dashboards, or private
  logs.
- Do not implement GOAL-07B or risk calculations. GOAL-07A is already
  design-only; no risk overlay calculation is active.

## GOAL-06D.1 Agent Note

GOAL-06D.1 is review-only warning repair for GOAL-06D. It may compare target
horizons and PIT-safe score variants, but it must not generate recommendations,
positions, risk overlays, dashboards, trading outputs, production model
promotion, or factor-mining outputs.

## GOAL-07A Agent Note
## GOAL-07A.1 Agent Note

GOAL-07A.1 is a review-only design review gate. It may classify warnings and write GOAL-07B unlock-readiness evidence, but it must not implement GOAL-07B, calculate risk values, assign symbol-level risk rows, or generate recommendation, position, dashboard, trading, production, backtest, factor-mining, broker, or DQN/RL outputs.



GOAL-07A is implemented only as design governance. It may define input
contracts, future schemas, rule catalogs, state machines, warning mappings, and
audits. It must not calculate risk values, assign symbol-level risk tags,
generate recommendations or positions, create dashboards, write trading or
production data, activate factor mining, or implement GOAL-07B.

V2 factor research is `planned_locked` and disabled in V1. Do not create factor
mining, IC/RankIC mining, factor library generation, or factor integration
runners unless a future explicit V2 goal unlocks them.

# CODEX Project Memory

## Mission

Maintain a clean, PIT-safe, review-only A-share pre-market workflow through
GOAL-06B, plus the GOAL-06C review-only expanded validation extension. Preserve
reproducibility and source governance before adding any future model or risk
work.

## Current Reliable Facts

- This target repository is the active source of truth.
- The source repository is historical legacy/evidence reference only.
- The active scoring workflow stops at GOAL-06B supervised baseline training
  gate.
- GOAL-06B is review-only and pilot-only.
- GOAL-06C is implemented_review_only for expanded validation, ranking
  baselines, metrics, walk-forward diagnostics, and stability diagnostics.
- GOAL-06D is future_review_only; no model comparison/calibration is
  implemented yet.
- Production model promotion is false.
- Recommendation, risk overlay, dashboard, paper trading, broker/live trading,
  production DB writes, and DQN/RL are locked.
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
`workflow_status.csv`. Do not remove locks from risk, recommendation,
dashboard, paper/live trading, production, or DQN/RL unless a later explicit
gate allows it.

## Do Not Drift

- Do not import legacy implementation code.
- Do not run legacy-only tests as active validation.
- Do not add absolute user-specific paths.
- Do not reintroduce volatile wall-clock timings into committed audit reports.
- Do not commit raw payloads, DBs, notebooks, caches, dashboards, or private
  logs.
- Do not start GOAL-06D unless the Stage 6C readiness report explicitly
  unlocks it as future review-only work.

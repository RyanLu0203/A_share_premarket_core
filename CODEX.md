# CODEX Project Memory

## Mission

Maintain a clean, PIT-safe, review-only A-share pre-market workflow through
GOAL-06B. Preserve reproducibility and source governance before adding any
future model or risk work.

## Current Reliable Facts

- This target repository is the active source of truth.
- The source repository is historical legacy/evidence reference only.
- The active workflow stops at GOAL-06B supervised baseline training gate.
- GOAL-06B is review-only and pilot-only.
- Production model promotion is false.
- Recommendation, risk overlay, dashboard, paper trading, broker/live trading,
  production DB writes, and DQN/RL are locked.

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
python scripts/run_goal06b_regression_suite.py
python scripts/run_e2e_trunk_verification_through_goal06b.py
python scripts/run_e2e_trunk_validation_through_goal06b.py
python scripts/run_safety_gate.py
python scripts/run_adapter_audit.py
```

## Do Not Drift

- Do not import legacy implementation code.
- Do not run legacy-only tests as active validation.
- Do not add absolute user-specific paths.
- Do not commit raw payloads, DBs, notebooks, caches, dashboards, or private
  logs.
- Do not start GOAL-06C unless the readiness report explicitly unlocks it.

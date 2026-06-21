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
- Active boundary: project start through GOAL-06B.
- GOAL-06B supervised baseline training is review-only and pilot-only.
- Feature-label merge and leakage audit are active.
- Recommendation, risk overlay, dashboard, paper/live trading, production DB
  writes, production model promotion, and DQN/RL remain locked.

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
python scripts/run_safety_gate.py
python scripts/run_adapter_audit.py
```

For GOAL-06B active-trunk changes, also run:

```bash
python scripts/run_goal06b_regression_suite.py
python scripts/run_e2e_trunk_verification_through_goal06b.py
python scripts/run_e2e_trunk_validation_through_goal06b.py
python scripts/run_workflow_diagnostics.py
```

## Git Safety

- Branch from `main`; do not push directly to `main` unless the user has
  explicitly requested the clean bootstrap to land on `main`.
- Stage explicit files only.
- Keep generated runtime evidence out of commits unless it is a deliberately
  sanitized, tiny, review-facing fixture or required GOAL-06B audit output.
- Report branch, commit hash, validation, excluded files, and review items.

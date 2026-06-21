# Next Worker Runbook

1. Read `PROJECT_STATE.md`, `README.md`, `CODEX.md`, `AGENTS.md`, and `ROADMAP.md`.
2. Run `python scripts/run_goal06b_regression_suite.py`.
3. Run `python scripts/run_e2e_trunk_verification_through_goal06b.py` and `python scripts/run_e2e_trunk_validation_through_goal06b.py`.
4. Review `outputs/diagnostics/run_detail_manifest.csv` for the command, owning capability, status, and recommended action.
5. For GOAL-06C work, run `python scripts/run_goal06c_expanded_validation.py` and review `outputs/audits/stage6c_readiness_report.md`.
6. GOAL-06D may proceed only as future review-only model comparison/calibration if the Stage 6C readiness report unlocks it.
7. Do not unlock recommendation, risk overlay, dashboard, paper/live trading, production writes, model promotion, or DQN/RL.

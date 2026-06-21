# Next Worker Runbook

1. Read `PROJECT_STATE.md`, `README.md`, `CODEX.md`, `AGENTS.md`, and `ROADMAP.md`.
2. Run `python scripts/run_goal06b_regression_suite.py`.
3. Run `python scripts/run_e2e_trunk_verification_through_goal06b.py` and `python scripts/run_e2e_trunk_validation_through_goal06b.py`.
4. Review `outputs/diagnostics/run_detail_manifest.csv` for the command, owning capability, status, and recommended action.
5. Do not start GOAL-06C unless `outputs/audits/goal06b_clean_repo_bootstrap_readiness_report.md` explicitly unlocks it.

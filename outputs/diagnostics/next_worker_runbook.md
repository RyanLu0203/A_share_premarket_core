# Next Worker Runbook

1. Read `PROJECT_STATE.md`, `README.md`, `CODEX.md`, `AGENTS.md`, and `ROADMAP.md`.
2. Run `python scripts/run_goal06b_regression_suite.py`.
3. Run `python scripts/run_e2e_trunk_verification_through_goal06b.py` and `python scripts/run_e2e_trunk_validation_through_goal06b.py`.
4. Review `outputs/diagnostics/run_detail_manifest.csv` for the command, owning capability, status, and recommended action.
5. For GOAL-06C work, run `python scripts/run_goal06c_expanded_validation.py` and review `outputs/audits/stage6c_readiness_report.md`.
6. For GOAL-06C.5 work, run `python scripts/rebuild_stage6c_from_engineering_panel.py` and review `outputs/audits/engineering_panel_readiness_report.md`.
7. For GOAL-06C.6 source-backed ingestion, run `python scripts/audit_provider_failure_classification.py` first; provider ingestion requires `ASHARE_ALLOW_NETWORK_INGESTION=1` or `--allow-network`.
8. For GOAL-06C.7 provider-ladder expansion, run `python scripts/run_goal06c7_provider_ladder_engineering_data_base_expansion.py`; browser-assisted mode additionally requires `ASHARE_ENABLE_BROWSER_ASSISTED_PROVIDER=1 --enable-browser-assisted`.
9. For GOAL-06D, run `python scripts/run_goal06d_model_comparison_calibration.py` and then every `scripts/audit_goal06d_*.py` wrapper.
10. Current GOAL-06D is `PASS_WITH_WARNINGS`; fix calibration/stability/provider concentration warnings before GOAL-07A design-only preparation.
11. Do not unlock recommendation, risk overlay calculation, dashboard, paper/live trading, production writes, model promotion, or DQN/RL.

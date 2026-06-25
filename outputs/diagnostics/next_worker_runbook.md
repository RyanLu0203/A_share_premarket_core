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
10. For GOAL-06D.1, run `python scripts/run_goal06d1_calibration_stability_warning_repair.py` and then every `scripts/audit_goal06d1_*.py` wrapper.
11. For GOAL-07A, run `python scripts/run_goal07a_risk_overlay_design_gate.py` and then every `scripts/audit_goal07a_*.py` wrapper.
12. For GOAL-07A.1, run `python scripts/run_goal07a1_risk_overlay_design_review_gate.py` and then every `scripts/audit_goal07a1_*.py` wrapper.
13. For GOAL-07B, run `python scripts/run_goal07b_risk_overlay_calculation_prototype.py` and `python scripts/audit_goal07b_risk_overlay_calculation_prototype.py`; outputs must remain review-only diagnostics.
14. For GOAL-08A, run `python scripts/run_goal08a_recommendation_contract_design_gate.py` and `python scripts/audit_goal08a_recommendation_contract_design_gate.py`; schema evidence must stay names-only with zero rows.
15. For GOAL-STORAGE-01, run `python scripts/run_goal_storage01_local_research_lake_hardening_gate.py` and `python scripts/audit_goal_storage01_local_research_lake_hardening_gate.py`; it is infrastructure-only and does not unlock GOAL-08B by itself.
16. For GOAL-08B.0, run `python scripts/run_goal08b0_recommendation_review_only_unlock_gate.py` and `python scripts/audit_goal08b0_recommendation_review_only_unlock_gate.py`; it may mark GOAL-08B review-only eligible or preserve valid diagnostics but must not itself implement diagnostics.
17. For GOAL-08B, run `python scripts/run_goal08b_recommendation_diagnostics_prototype.py` and `python scripts/audit_goal08b_recommendation_diagnostics_prototype.py`; outputs must remain review-only and non-actionable.
18. For GOAL-09.0, run `python scripts/run_goal090_position_band_review_only_unlock_gate.py` and `python scripts/audit_goal090_position_band_review_only_unlock_gate.py`; it may mark GOAL-09 future_review_only eligible or preserve valid GOAL-09 diagnostics but must not itself create position-band rows.
19. For GOAL-09, run `python scripts/run_goal09_position_band_diagnostics_prototype.py` and `python scripts/audit_goal09_position_band_diagnostics_prototype.py`; outputs must remain review-only and non-actionable.
20. For GOAL-09.1, run `python scripts/run_goal091_position_band_warning_dashboard_readiness_gate.py` and `python scripts/audit_goal091_position_band_warning_dashboard_readiness_gate.py`; it may allow only a future explicit GOAL-DASHBOARD-00 design-only contract request and must not create dashboard outputs.
21. For GOAL-V1-INTEGRITY-01, run `python scripts/run_goal_v1_integrity01_artifact_lineage_structure_gate.py` and `python scripts/audit_goal_v1_integrity01_artifact_lineage_structure_gate.py`; it may verify only artifact lineage and source-of-truth structure before a future explicit dashboard design contract request.
22. V2 factor research is planned but inactive; do not create factor mining, IC/RankIC mining, factor libraries, or factor outputs in V1.
23. Do not unlock recommendation execution, actual positions, position sizing, dashboard, paper/live trading, production writes, model promotion, factor mining, broker, local-lake, or DQN/RL.

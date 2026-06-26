# Workflow Diagnostic Summary

Status: `PASS_WITH_WARNINGS`

The clean active workflow through GOAL-06B is deterministic and local.
GOAL-06C review-only validation status: `implemented with warnings`.
GOAL-06C.5 engineering data foundation status: `engineering panel ready`.
GOAL-06C.6 source-backed ingestion status: `blocked`.
GOAL-06C.7 provider ladder status: `provider-ladder engineering_pilot ready`.
Provider ladder panel tier: `engineering_pilot`.
Provider ladder approved symbols: `50`.
Provider ladder validation trading dates: `120`.
Provider ladder Stage 6C engineering rows: `6000`.
Browser-assisted provider project default: `false`.
GOAL-06D allowed by provider ladder: `true`.
GOAL-06D readiness: `PASS_WITH_WARNINGS`.
GOAL-06D selected review-only baseline: `score_based_alpha_ranking`.
GOAL-06D model comparison status: `PASS_WITH_WARNINGS`.
GOAL-06D calibration status: `PASS_WITH_WARNINGS`.
GOAL-06D stability status: `PASS_WITH_WARNINGS`.
GOAL-06D governance status: `PASS`.
GOAL-06D boundary lock status: `PASS`.
GOAL-06D.1 readiness: `PASS_WITH_WARNINGS`.
GOAL-06D.1 selected repaired review-only baseline: `raw_score_based_alpha_ranking`.
GOAL-06D.1 target horizon recommendation: `no_stable_target_horizon_selected`.
GOAL-06D.1 calibration repair status: `PASS_WITH_WARNINGS`.
GOAL-06D.1 feature sign stability status: `PASS_WITH_WARNINGS`.
GOAL-06D.1 provider concentration disclosure status: `PASS_WITH_WARNINGS`.
GOAL-06D.1 governance status: `PASS`.
GOAL-06D.1 boundary lock status: `PASS`.
GOAL-07A readiness: `PASS_WITH_WARNINGS`.
GOAL-07A allowed input contract status: `PASS`.
GOAL-07A future output schema status: `PASS`.
GOAL-07A risk rule catalog status: `PASS`.
GOAL-07A risk state machine status: `PASS`.
GOAL-07A upstream warning mapping status: `PASS`.
GOAL-07A governance boundary status: `PASS`.
GOAL-07A boundary lock status: `PASS`.
GOAL-07A V2 factor lock status: `PASS`.
GOAL-07A.1 design review status: `PASS_WITH_WARNINGS`.
GOAL-07A.1 input contract review status: `PASS`.
GOAL-07A.1 schema safety status: `PASS`.
GOAL-07A.1 rule convertibility status: `PASS`.
GOAL-07A.1 state machine review status: `PASS`.
GOAL-07A.1 boundary lock status: `PASS`.
GOAL-07B unlock readiness: `ready_for_explicit_review_only_unlock`.
GOAL-07A.1 allowed next action: `request_explicit_goal07b_review_only_unlock`.
GOAL-07B.0 unlock gate status: `PASS_WITH_WARNINGS`.
GOAL-07B.0 audit status: `PASS`.
GOAL-07B.0 unlock result: `eligible_for_future_review_only_prototype`.
GOAL-07B target status: `implemented_review_only`.
GOAL-07B calculation prototype status: `PASS_WITH_WARNINGS`.
GOAL-07B calculation audit status: `PASS`.
GOAL-07B risk overlay diagnostic rows: `100`.
GOAL-08A design gate status: `PASS`.
GOAL-08A design audit status: `PASS`.
GOAL-08A future schema rows generated: `0`.
GOAL-STORAGE-01 hardening status: `PASS`.
GOAL-STORAGE-01 audit status: `PASS`.
GOAL-STORAGE-01 forbidden tracked artifacts: `0`.
GOAL-08B.0 unlock gate status: `PASS_WITH_WARNINGS`.
GOAL-08B.0 audit status: `PASS`.
GOAL-08B.0 unlock result: `eligible_for_future_review_only_prototype`.
GOAL-08B target status: `implemented_review_only`.
GOAL-08B diagnostic prototype status: `PASS_WITH_WARNINGS`.
GOAL-08B diagnostic audit status: `PASS`.
GOAL-08B recommendation diagnostic rows: `100`.
GOAL-09.0 unlock gate status: `PASS_WITH_WARNINGS`.
GOAL-09.0 audit status: `PASS`.
GOAL-09.0 unlock result: `eligible_for_future_review_only_prototype`.
GOAL-09 target status: `implemented_review_only`.
GOAL-09 diagnostic prototype status: `PASS_WITH_WARNINGS`.
GOAL-09 diagnostic audit status: `PASS`.
GOAL-09 position-band diagnostic rows: `100`.
GOAL-09.1 warning/dashboard readiness status: `PASS_WITH_WARNINGS`.
GOAL-09.1 readiness audit status: `PASS`.
GOAL-DASHBOARD-00 request eligibility: `eligible_for_explicit_design_only_contract_gate`.
GOAL-V1-INTEGRITY-01 artifact-lineage status: `PASS_WITH_WARNINGS`.
GOAL-V1-INTEGRITY-01 audit status: `PASS`.
GOAL-V1-INTEGRITY-01 canonical lineage verified: `true`.
GOAL-DASHBOARD-00 request eligibility after V1 integrity: `eligible_for_explicit_design_only_contract_gate`.
GOAL-10A backtest contract design status: `PASS_WITH_WARNINGS`.
GOAL-10A audit status: `PASS`.
GOAL-10A source keys match: `true`.
GOAL-10A backtests run: `false`.
V2 factor placeholder status: `planned_locked_disabled`.
GOAL-07B workflow status: `implemented_review_only`.
GOAL-08A workflow status: `implemented_design_only`.
GOAL-STORAGE-01 workflow status: `implemented_infrastructure_only`.
GOAL-08B.0 workflow status: `implemented_review_only`.
GOAL-08B workflow status: `implemented_review_only`.
GOAL-09.0 workflow status: `implemented_review_only`.
GOAL-09 position-band diagnostics workflow status: `implemented_review_only`.
GOAL-09.1 dashboard-readiness workflow status: `implemented_review_only`.
GOAL-V1-INTEGRITY-01 workflow status: `implemented_infrastructure_only`.
GOAL-10A workflow status: `implemented_design_only`.
GOAL-10B workflow status: `locked_future`.
GOAL-10C workflow status: `locked_future`.
GOAL-10D workflow status: `locked_future`.
Dashboard lock status: `locked_future`.
Paper/live trading lock status: `locked_future;locked_future`.
Production lock status: `locked_future;locked_future`.
Downstream execution lock status: `locked_future_or_deleted_from_active_mainline`; GOAL-09 may produce review-only non-actionable position-band diagnostics only, GOAL-09.1 may produce warning/readiness evidence only, GOAL-V1-INTEGRITY-01 may produce only artifact-lineage integrity evidence, and GOAL-10A may define only future backtest contracts without running a backtest.
AKShare available: `true`.
Network ingestion opt-in active: `false`.
Source-backed bundle manifest: ``PASS``.
Known warnings are source-coverage gaps, `CLASS_D_UNCLEAR_KEEP_DOCUMENTED` missing historical GOAL-05/06 source docs, GOAL-06D calibration/stability/provider concentration warnings, and GOAL-06D.1 bounded weak-baseline warnings.
GOAL-06C.5/GOAL-06C.6 warnings are documented source limitations. GOAL-06C.7 has reached `engineering_pilot`; GOAL-06D and GOAL-06D.1 are implemented review-only; GOAL-07A is design-only and does not unlock calculation.
GOAL-07A.1 reviews GOAL-07A design readiness only; GOAL-07B.0 may mark GOAL-07B future_review_only eligible or preserve its implemented review-only diagnostic state, GOAL-07B may produce review-only non-actionable risk diagnostics, GOAL-08A may define names-only design contracts with zero recommendation rows, GOAL-STORAGE-01 hardens storage without unlocking GOAL-08B by itself, GOAL-08B.0 may mark GOAL-08B review-only eligible or preserve its implemented diagnostic state, GOAL-08B may produce only non-actionable review-only recommendation diagnostic rows, GOAL-09.0 may mark GOAL-09 position-band diagnostics future_review_only eligible, GOAL-09 may produce only non-actionable review-only position-band diagnostic rows, GOAL-09.1 may classify warnings for future dashboard design readiness only, GOAL-V1-INTEGRITY-01 may verify lineage/structure only before any explicit GOAL-DASHBOARD-00 design contract request, and GOAL-10A may define future backtest contracts only without performance rows.

Protected regression commands:
- `python scripts/audit_existing_modules.py`
- `python scripts/build_pit_signal_snapshot.py`
- `python scripts/audit_pit_signal_snapshot.py`
- `python scripts/build_label_snapshot.py`
- `python scripts/audit_label_snapshot.py`
- `python scripts/build_model_ready_candidate_dataset.py`
- `python scripts/audit_feature_label_leakage.py`
- `python scripts/run_stage6a_blocker_repair.py --no-network`
- `python scripts/run_baseline_scoring_skeleton.py`
- `python scripts/audit_baseline_scoring_skeleton.py`
- `python scripts/run_supervised_baseline_training.py`
- `python scripts/audit_supervised_baseline_training.py`
- `python scripts/run_workflow_diagnostics.py`
- `python scripts/run_goal06c_expanded_validation.py`
- `python scripts/audit_storage_policy.py`
- `python scripts/audit_provider_failure_classification.py`
- `python scripts/run_goal06c7_provider_ladder_engineering_data_base_expansion.py --allow-network`
- `ASHARE_ENABLE_BROWSER_ASSISTED_PROVIDER=1 python scripts/run_goal06c7_provider_ladder_engineering_data_base_expansion.py --allow-network --enable-browser-assisted`
- `python scripts/audit_browser_assisted_provider.py`
- `python scripts/audit_workflow_cleanliness.py`
- `python scripts/audit_data_source_coverage.py`
- `python scripts/run_goal06c6_source_backed_engineering_pilot_bundle.py --allow-network`
- `python scripts/rebuild_stage6c_from_engineering_panel.py`
- `python scripts/run_goal06d_model_comparison_calibration.py`
- `python scripts/audit_goal06d_feature_contract.py`
- `python scripts/audit_goal06d_split.py`
- `python scripts/audit_goal06d_model_comparison.py`
- `python scripts/audit_goal06d_calibration.py`
- `python scripts/audit_goal06d_stability.py`
- `python scripts/audit_goal06d_governance.py`
- `python scripts/audit_goal06d_boundary_locks.py`
- `python scripts/run_goal06d1_calibration_stability_warning_repair.py`
- `python scripts/audit_goal06d1_target_horizon.py`
- `python scripts/audit_goal06d1_score_repair.py`
- `python scripts/audit_goal06d1_calibration_repair.py`
- `python scripts/audit_goal06d1_feature_sign_stability.py`
- `python scripts/audit_goal06d1_provider_concentration_disclosure.py`
- `python scripts/audit_goal06d1_governance.py`
- `python scripts/audit_goal06d1_boundary_locks.py`
- `python scripts/run_goal07a_risk_overlay_design_gate.py`
- `python scripts/audit_goal07a_allowed_input_contract.py`
- `python scripts/audit_goal07a_output_schema.py`
- `python scripts/audit_goal07a_risk_rule_catalog.py`
- `python scripts/audit_goal07a_state_machine.py`
- `python scripts/audit_goal07a_upstream_warning_mapping.py`
- `python scripts/audit_goal07a_governance_boundary.py`
- `python scripts/audit_goal07a_boundary_locks.py`
- `python scripts/audit_goal07a_v2_factor_lock.py`
- `python scripts/run_goal07a1_risk_overlay_design_review_gate.py`
- `python scripts/audit_goal07a1_input_contract_readiness.py`
- `python scripts/audit_goal07a1_output_schema_safety.py`
- `python scripts/audit_goal07a1_rule_convertibility.py`
- `python scripts/audit_goal07a1_state_machine_review.py`
- `python scripts/audit_goal07a1_warning_policy.py`
- `python scripts/audit_goal07a1_boundary_locks.py`
- `python scripts/run_goal07b0_risk_overlay_review_only_unlock_gate.py`
- `python scripts/audit_goal07b0_risk_overlay_review_only_unlock_gate.py`
- `python scripts/run_goal07b_risk_overlay_calculation_prototype.py`
- `python scripts/audit_goal07b_risk_overlay_calculation_prototype.py`
- `python scripts/run_goal08a_recommendation_contract_design_gate.py`
- `python scripts/audit_goal08a_recommendation_contract_design_gate.py`
- `python scripts/run_goal_storage01_local_research_lake_hardening_gate.py`
- `python scripts/audit_goal_storage01_local_research_lake_hardening_gate.py`
- `python scripts/run_goal08b0_recommendation_review_only_unlock_gate.py`
- `python scripts/audit_goal08b0_recommendation_review_only_unlock_gate.py`
- `python scripts/run_goal08b_recommendation_diagnostics_prototype.py`
- `python scripts/audit_goal08b_recommendation_diagnostics_prototype.py`
- `python scripts/run_goal090_position_band_review_only_unlock_gate.py`
- `python scripts/audit_goal090_position_band_review_only_unlock_gate.py`
- `python scripts/run_goal09_position_band_diagnostics_prototype.py`
- `python scripts/audit_goal09_position_band_diagnostics_prototype.py`
- `python scripts/run_goal091_position_band_warning_dashboard_readiness_gate.py`
- `python scripts/audit_goal091_position_band_warning_dashboard_readiness_gate.py`
- `python scripts/run_goal_v1_integrity01_artifact_lineage_structure_gate.py`
- `python scripts/audit_goal_v1_integrity01_artifact_lineage_structure_gate.py`
- `python scripts/run_goal10a_backtest_contract_design_gate.py`
- `python scripts/audit_goal10a_backtest_contract_design_gate.py`

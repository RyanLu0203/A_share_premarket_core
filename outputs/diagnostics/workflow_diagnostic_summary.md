# Workflow Diagnostic Summary

Status: `PASS_WITH_WARNINGS`

The clean active workflow through GOAL-06B is deterministic and local.
GOAL-06C review-only validation status: `not yet promoted`.
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
GOAL-07A lock status: `future_design_only; locked until GOAL-06D warnings are resolved`.
Downstream lock status: `locked_future_or_deleted_from_active_mainline`.
AKShare available: `true`.
Network ingestion opt-in active: `false`.
Source-backed bundle manifest: ``PASS``.
Known warnings are source-coverage gaps, `CLASS_D_UNCLEAR_KEEP_DOCUMENTED` missing historical GOAL-05/06 source docs, and GOAL-06D calibration/stability/provider concentration warnings.
GOAL-06C.5/GOAL-06C.6 warnings are documented source limitations. GOAL-06C.7 has reached `engineering_pilot`; GOAL-06D is implemented review-only with warnings and does not unlock GOAL-07A execution.

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

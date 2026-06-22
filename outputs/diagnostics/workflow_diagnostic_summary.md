# Workflow Diagnostic Summary

Status: `PASS_WITH_WARNINGS`

The clean active workflow through GOAL-06B is deterministic and local.
GOAL-06C review-only validation status: `implemented with warnings`.
GOAL-06C.5 engineering data foundation status: `implemented with warnings; GOAL-06D blocked`.
GOAL-06C.6 source-backed ingestion status: `blocked`.
AKShare available: `true`.
Network ingestion opt-in active: `false`.
Source-backed bundle manifest: ``BLOCKED``.
Known warnings are source-coverage gaps, the contract-demo Stage 6C panel size, and `CLASS_D_UNCLEAR_KEEP_DOCUMENTED` missing historical GOAL-05/06 source docs.
GOAL-06C.5/GOAL-06C.6 warnings are limited to documented source limitations, no-network/provider availability, and the panel not yet reaching `engineering_pilot`.

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
- `python scripts/audit_data_source_coverage.py`
- `python scripts/run_goal06c6_source_backed_engineering_pilot_bundle.py --allow-network`
- `python scripts/rebuild_stage6c_from_engineering_panel.py`

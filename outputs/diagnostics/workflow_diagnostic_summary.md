# Workflow Diagnostic Summary

Status: `PASS_WITH_WARNINGS`

The clean active workflow through GOAL-06B is deterministic and local.
Known warnings are source-coverage gaps inherited as context, plus Class D missing historical GOAL-05/06 source docs.

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

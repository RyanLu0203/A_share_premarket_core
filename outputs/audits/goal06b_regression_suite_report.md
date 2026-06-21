# GOAL-06B Regression Suite Report

Status: `PASS`

Runtime timing is stored in local-only diagnostics and is not part of the committed stable report.

- `python scripts/audit_existing_modules.py`: `PASS`; runtime `local_only`
- `python scripts/build_pit_signal_snapshot.py`: `PASS`; runtime `local_only`
- `python scripts/audit_pit_signal_snapshot.py`: `PASS`; runtime `local_only`
- `python scripts/build_label_snapshot.py`: `PASS`; runtime `local_only`
- `python scripts/audit_label_snapshot.py`: `PASS`; runtime `local_only`
- `python scripts/build_model_ready_candidate_dataset.py`: `PASS`; runtime `local_only`
- `python scripts/audit_feature_label_leakage.py`: `PASS`; runtime `local_only`
- `python scripts/run_stage6a_blocker_repair.py --no-network`: `PASS`; runtime `local_only`
- `python scripts/run_baseline_scoring_skeleton.py`: `PASS`; runtime `local_only`
- `python scripts/audit_baseline_scoring_skeleton.py`: `PASS`; runtime `local_only`
- `python scripts/run_supervised_baseline_training.py`: `PASS`; runtime `local_only`
- `python scripts/audit_supervised_baseline_training.py`: `PASS`; runtime `local_only`
- `python scripts/run_workflow_diagnostics.py`: `PASS`; runtime `local_only`

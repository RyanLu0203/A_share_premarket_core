# Workflow Diagnostics Runbook

Run:

```bash
python scripts/run_workflow_diagnostics.py
```

Outputs:

- `outputs/diagnostics/workflow_diagnostic_summary.md`
- `outputs/diagnostics/command_failure_catalog.csv`
- `outputs/diagnostics/capability_health_matrix.csv`
- `outputs/diagnostics/run_detail_manifest.csv`
- `outputs/diagnostics/known_warnings_and_non_blockers.md`
- `outputs/diagnostics/next_worker_runbook.md`

The run detail manifest includes:

- command
- stage or goal
- capability id
- status
- runtime seconds
- input and output artifacts
- error or warning message
- blocking classification
- recommended action
- owner module
- verification link
- validation link

Diagnostics is an operator aid. It must not unlock downstream functionality or
replace the verification, validation, regression, safety, or adapter gates.

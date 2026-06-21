# E2E Validation Through GOAL-06B

Supported runtime: Python `>=3.9`. Python `3.9.21` was verified during the
fresh-clone audit for the clean GOAL-06B workflow.

The active validation command is:

```bash
python scripts/run_e2e_trunk_validation_through_goal06b.py
```

It validates:

- project operating system files
- universe and symbol governance
- trading calendar
- module health gate
- source health and context contracts
- PIT signal snapshot
- label snapshot
- feature-label merge
- leakage audit
- Stage 6A repair panel
- baseline scoring skeleton with labels excluded
- GOAL-06B supervised training gate
- review-only and pilot-only flags
- locked downstream capabilities remain false
- diagnostics reports are generated
- workflow status governance passes

Verification is separate:

```bash
python scripts/run_e2e_trunk_verification_through_goal06b.py
```

Regression is separate:

```bash
python scripts/run_goal06b_regression_suite.py
```

The final readiness evidence is:

`outputs/audits/goal06b_clean_repo_bootstrap_readiness_report.md`

Workflow status governance is checked by:

```bash
python scripts/audit_workflow_status.py
```

Runtime timing policy:

- committed validation and regression summaries are stable;
- `runtime_seconds` in committed reports uses `local_only`;
- volatile timing details are written to ignored local diagnostics under
  `outputs/local/runtime/`.

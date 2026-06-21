# Runtime Artifact Determinism Report

Status: `PASS`

Stable committed reports:

- `outputs/audits/goal06b_regression_suite_report.csv`
- `outputs/audits/goal06b_regression_suite_report.md`
- `outputs/audits/program_validation_profile_results.csv`

Determinism fix:

- Stable report `runtime_seconds` fields now use `local_only`.
- Volatile timing is preserved in ignored local files under
  `outputs/local/runtime/`.
- `.gitignore` excludes `outputs/local/` and local runtime diagnostic patterns.

Expected behavior:

- Re-running `python scripts/run_goal06b_regression_suite.py` should not dirty
  tracked files only because wall-clock timings changed.
- Re-running `python scripts/run_program_validation_profile.py` should not dirty
  tracked files only because wall-clock timings changed.

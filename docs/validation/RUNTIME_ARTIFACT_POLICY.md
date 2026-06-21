# Runtime Artifact Policy

## Stable Committed Artifacts

Committed GOAL-06B reports under `outputs/audits/` and
`outputs/diagnostics/` must be deterministic enough that normal validation
reruns do not dirty Git only because wall-clock runtime changed.

Stable committed summaries include:

- `outputs/audits/goal06b_regression_suite_report.csv`
- `outputs/audits/goal06b_regression_suite_report.md`
- `outputs/audits/program_validation_profile_results.csv`
- `outputs/audits/program_validation_profile_report.md`

These summaries keep command identity, status, blocking errors, and diagnostic
references. Their `runtime_seconds` value is `local_only`.

## Volatile Local-Only Artifacts

Wall-clock timing, stdout tails, stderr tails, and interpreter-specific runtime
details are useful for debugging but should not pollute Git state. They are
written under ignored paths such as:

- `outputs/local/runtime/goal06b_regression_suite_runtime.csv`
- `outputs/local/runtime/program_validation_profile_runtime.csv`

The local files may change on every run and are intentionally excluded from
GitHub.

## Why Runtime Seconds Are Local-Only

Runtime measurements depend on machine load, Python executable path, filesystem
cache state, and test runner timing. They are evidence for local debugging, not
durable scientific artifacts. Keeping them out of committed summaries prevents
fresh-clone validation from producing meaningless `runtime_seconds` diffs.

## Future Agent Guidance

Future GPT/Codex workers should:

- treat committed reports as stable evidence;
- inspect `outputs/local/runtime/` only for local debugging;
- never commit local runtime timing files;
- keep Class A GOAL-06B command status and blocking errors in committed reports;
- document any non-deterministic artifact before adding it to Git.

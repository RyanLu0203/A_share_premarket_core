# Windows Compatibility Policy

Codex Max may run in a remote Windows-compatible environment.

## Required Practices

- Use Python `pathlib` for filesystem paths.
- Do not hardcode owner-specific absolute home paths.
- Do not hardcode POSIX-only absolute paths.
- Do not require bash-only commands for Codex Max.
- Do not require `chmod`.
- Do not require symlink behavior.
- Do not rely on case-sensitive filesystem assumptions.
- Avoid Windows-reserved filenames.
- Use UTF-8 for docs and outputs.
- Use cross-platform Python scripts for audits and scans.
- Validation commands should use `python -m` where possible.
- Git repository paths may use forward slashes.
- Filesystem logic inside Python must use `pathlib`.
- Long paths and oversized filenames should be avoided.
- Any future script required for Codex Max must pass Windows compatibility
  audit.

## Windows-Reserved Names

Avoid output filenames that equal `CON`, `PRN`, `AUX`, `NUL`, `COM1` through
`COM9`, or `LPT1` through `LPT9`, with or without an extension.

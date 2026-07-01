from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SCAN_PATHS = [
    "CODEX.md",
    "AGENTS.md",
    "PROJECT_STATE.md",
    "ROADMAP.md",
    "README.md",
    "configs/project/workflow_status.csv",
    "docs/governance",
    "scripts",
]

SCRIPT_EXEMPTIONS = {
    "scripts/audit_github_only_source_policy.py",
    "scripts/audit_windows_compatibility_policy.py",
}


def main() -> int:
    failures: list[str] = []
    required = ROOT / "docs/governance/GITHUB_ONLY_SOURCE_POLICY.md"
    if not required.exists():
        failures.append("GITHUB_ONLY_SOURCE_POLICY.md is missing")
    else:
        text = required.read_text(encoding="utf-8")
        for marker in [
            "GitHub is the only authoritative source for Codex Max",
            "project-current",
            "outputs/audits/**",
            "Codex Max must not rely on",
            "local bundle backups",
            "local-lake data",
            "Provider registry network remains disabled",
        ]:
            if marker not in text:
                failures.append(f"GITHUB_ONLY_SOURCE_POLICY.md missing marker: {marker}")

    for file_path in _iter_scan_files():
        _scan_file(file_path, failures)

    if failures:
        print("GitHub-only source policy audit: BLOCKED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("GitHub-only source policy audit: PASS")
    return 0


def _iter_scan_files() -> list[Path]:
    files: list[Path] = []
    for item in SCAN_PATHS:
        path = ROOT / item
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(p for p in path.rglob("*") if p.is_file()))
    return [p for p in files if str(p.relative_to(ROOT)).replace("\\", "/") not in SCRIPT_EXEMPTIONS]


def _scan_file(path: Path, failures: list[str]) -> None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return
    rel = path.relative_to(ROOT)
    for lineno, line in enumerate(lines, start=1):
        lower = line.lower()
        context = _context(lines, lineno)
        if "/users/luxinyu" in lower and not _negative_or_private(context):
            failures.append(f"{rel}:{lineno} local Mac path is not marked user-private/prohibited")
        if "local bundle" in lower and "codex max" in context and not _negative_or_private(context):
            failures.append(f"{rel}:{lineno} local bundle appears as Codex Max dependency")
        if "local-lake" in lower and "codex max" in context and not _negative_or_private(context):
            failures.append(f"{rel}:{lineno} local-lake appears as Codex Max dependency")
        if "stale main" in lower and "must not" not in context and "unless explicitly instructed" not in context:
            failures.append(f"{rel}:{lineno} stale main appears as an allowed default")
        if "fetch live" in lower and not _negative_or_future_opt_in(context):
            failures.append(f"{rel}:{lineno} live fetch is not gated by future opt-in")
        if "provider cache" in lower and not _negative_or_private(context):
            failures.append(f"{rel}:{lineno} provider cache appears as dependency")


def _negative_or_private(text: str) -> bool:
    return any(
        phrase in text
        for phrase in [
            "must not",
            "not rely",
            "not a codex max",
            "not accessible",
            "not part of codex max",
            "user-private",
            "user_private",
            "outside github",
            "prohibited",
            "do not",
            "creates no",
            "does not fetch",
            "does not unlock",
            "remains locked",
            "without explicit",
            "future explicit",
            "disabled by default",
        ]
    )


def _negative_or_future_opt_in(text: str) -> bool:
    return _negative_or_private(text) or "future goal explicitly allows" in text or "network opt-in" in text


def _context(lines: list[str], lineno: int) -> str:
    start = max(0, lineno - 7)
    end = min(len(lines), lineno + 4)
    return " ".join(lines[start:end]).lower()


if __name__ == "__main__":
    raise SystemExit(main())

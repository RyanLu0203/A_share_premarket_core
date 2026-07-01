from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}

SCAN_FILES = [
    "CODEX.md",
    "AGENTS.md",
    "PROJECT_STATE.md",
    "ROADMAP.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    "docs/governance/WINDOWS_COMPATIBILITY_POLICY.md",
    "docs/governance/CODEX_MAX_REMOTE_WINDOWS_PROTOCOL.md",
    "docs/governance/CODEX_MAX_OPERATING_PROTOCOL.md",
    "docs/governance/GITHUB_ONLY_SOURCE_POLICY.md",
]


def main() -> int:
    failures: list[str] = []
    policy = ROOT / "docs/governance/WINDOWS_COMPATIBILITY_POLICY.md"
    if not policy.exists():
        failures.append("WINDOWS_COMPATIBILITY_POLICY.md is missing")
    else:
        text = policy.read_text(encoding="utf-8")
        for marker in [
            "pathlib",
            "Do not hardcode `/Users/luxinyu` paths",
            "Do not require bash-only commands",
            "Do not require `chmod`",
            "Do not require symlink behavior",
            "Use UTF-8",
            "python -m",
        ]:
            if marker not in text:
                failures.append(f"WINDOWS_COMPATIBILITY_POLICY.md missing marker: {marker}")

    for file_name in SCAN_FILES:
        path = ROOT / file_name
        if path.exists():
            _scan_text(path, failures)

    for path in (ROOT / "docs/governance").rglob("*"):
        if path.is_file():
            stem = path.stem.upper()
            if stem in WINDOWS_RESERVED:
                failures.append(f"Windows-reserved governance filename: {path.relative_to(ROOT)}")

    if failures:
        print("Windows compatibility policy audit: BLOCKED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Windows compatibility policy audit: PASS")
    return 0


def _scan_text(path: Path, failures: list[str]) -> None:
    rel = path.relative_to(ROOT)
    lines = path.read_text(encoding="utf-8").splitlines()
    for lineno, line in enumerate(lines, start=1):
        lower = line.lower()
        context = _context(lines, lineno)
        if "/users/luxinyu" in lower and not _allowed_local_path_note(context):
            failures.append(f"{rel}:{lineno} hardcoded local Mac path in Codex Max protocol")
        if "codex max" in context and "bash-only" in lower and not _allowed_windows_prohibition(context):
            failures.append(f"{rel}:{lineno} bash-only command appears required")
        if "codex max" in context and "chmod" in lower and not _allowed_windows_prohibition(context):
            failures.append(f"{rel}:{lineno} chmod appears required")
        if "codex max" in context and "symlink" in lower and not _allowed_windows_prohibition(context):
            failures.append(f"{rel}:{lineno} symlink behavior appears required")


def _allowed_local_path_note(text: str) -> bool:
    return any(
        phrase in text
        for phrase in [
            "must not",
            "do not",
            "user-private",
            "not rely",
            "not a codex max",
            "avoid",
            "prohibited",
        ]
    )


def _allowed_windows_prohibition(text: str) -> bool:
    return any(phrase in text for phrase in ["must not", "do not", "avoid", "not require", "prohibited"])


def _context(lines: list[str], lineno: int) -> str:
    start = max(0, lineno - 7)
    end = min(len(lines), lineno + 4)
    return " ".join(lines[start:end]).lower()


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import re
import subprocess
from pathlib import Path


_CONTENT_PATTERNS = {
    "absolute_user_home": re.compile(
        rb"(?:/Users|/home)/[A-Za-z0-9._-]+(?:/|$)|[A-Za-z]:\\Users\\[^\\\s]+"
    ),
    "aws_access_key": re.compile((rb"AK" + rb"IA" + rb"[0-9A-Z]{16}")),
    "github_token": re.compile(
        rb"gh" + rb"[pousr]_[A-Za-z0-9]{30,255}|github_" + rb"pat_[A-Za-z0-9_]{30,255}"
    ),
    "openai_style_key": re.compile(rb"s" + rb"k-[A-Za-z0-9_-]{20,}"),
    "private_key": re.compile(
        rb"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE " + rb"KEY-----"
    ),
}

_FORBIDDEN_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".ipynb"}


def audit_public_release(root: Path) -> list[str]:
    """Return sanitized public-release blockers from the tracked tree."""

    failures: list[str] = []
    for relative in _tracked_files(root):
        path = root / relative
        lowered = path.name.lower()
        if path.suffix.lower() in _FORBIDDEN_SUFFIXES:
            failures.append(f"forbidden_tracked_file:{relative.as_posix()}")
        if lowered == ".env" or (lowered.startswith(".env.") and lowered != ".env.example"):
            failures.append(f"forbidden_tracked_environment_file:{relative.as_posix()}")
        try:
            payload = path.read_bytes()
        except OSError:
            failures.append(f"unreadable_tracked_file:{relative.as_posix()}")
            continue
        for label, pattern in _CONTENT_PATTERNS.items():
            if pattern.search(payload):
                failures.append(f"{label}:{relative.as_posix()}")
    return sorted(set(failures))


def _tracked_files(root: Path) -> tuple[Path, ...]:
    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return tuple(
        Path(value.decode("utf-8"))
        for value in completed.stdout.split(b"\0")
        if value
    )

"""Local-only guard against duplicate top-level project checkouts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def audit_local_workspace_boundary(repository_root: Path) -> Dict[str, Any]:
    """Return a bounded audit of same-prefix siblings beside the repository."""

    root = Path(repository_root).resolve()
    parent = root.parent
    forbidden = sorted(
        child.name
        for child in parent.iterdir()
        if child.name.startswith(root.name) and child.resolve() != root
    )
    return {
        "status": "PASS" if not forbidden else "BLOCKED",
        "repository_name": root.name,
        "sibling_count": len(forbidden),
        "forbidden_siblings": forbidden,
        "local_archive_policy": "store_under_repository_dot_local",
    }

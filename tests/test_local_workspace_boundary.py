from pathlib import Path

from ashare_premarket.ops.local_workspace_boundary import (
    audit_local_workspace_boundary,
)


def test_local_workspace_boundary_allows_only_the_primary_top_level_directory(
    tmp_path: Path,
) -> None:
    root = tmp_path / "A_share_premarket_core"
    root.mkdir()
    (tmp_path / "unrelated").mkdir()

    assert audit_local_workspace_boundary(root)["status"] == "PASS"

    sibling = tmp_path / "A_share_premarket_core_runtime"
    sibling.mkdir()
    blocked = audit_local_workspace_boundary(root)
    assert blocked["status"] == "BLOCKED"
    assert blocked["forbidden_siblings"] == ["A_share_premarket_core_runtime"]

    archive = root / ".local" / "legacy-checkouts"
    archive.mkdir(parents=True)
    sibling.rename(archive / sibling.name)
    assert audit_local_workspace_boundary(root)["status"] == "PASS"

from __future__ import annotations

from pathlib import Path

from ashare_premarket.runners.common import RunContext, build_manifest, write_partitioned_csv


def test_common_runner_helpers_build_manifest_and_partitions(tmp_path: Path) -> None:
    context = RunContext(root=tmp_path, goal_id="TEST-GOAL", mode="unit_test")
    manifest = build_manifest(context, "PASS", ["outputs/test.csv"], row_count=2)
    assert manifest["goal_id"] == "TEST-GOAL"
    assert manifest["row_count"] == 2
    written = write_partitioned_csv(
        tmp_path,
        "outputs/parts",
        "bucket",
        [{"bucket": "a", "value": 1}, {"bucket": "b", "value": 2}],
        ["bucket", "value"],
    )
    assert len(written) == 2
    assert all((tmp_path / path).exists() for path in written)


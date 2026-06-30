from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from ashare_premarket.core.io import write_csv, write_json


@dataclass(frozen=True)
class RunContext:
    root: Path
    goal_id: str
    mode: str
    network_policy: str = "disabled_by_default"
    evidence_policy: str = "committed_evidence_only"


def build_manifest(context: RunContext, status: str, output_artifacts: list[str], **extra: object) -> dict[str, object]:
    manifest: dict[str, object] = {
        "goal_id": context.goal_id,
        "mode": context.mode,
        "status": status,
        "network_policy": context.network_policy,
        "evidence_policy": context.evidence_policy,
        "output_artifacts": output_artifacts,
    }
    manifest.update(extra)
    return manifest


def write_manifest(path: Path, manifest: dict[str, object]) -> None:
    write_json(path, manifest)


def write_partitioned_csv(root: Path, base_dir: str, partition_field: str, rows: Iterable[dict[str, object]], fieldnames: list[str]) -> list[str]:
    partitions: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        partitions.setdefault(str(row.get(partition_field, "unknown")), []).append(row)
    written: list[str] = []
    for partition_value, partition_rows in sorted(partitions.items()):
        path = root / base_dir / f"{partition_field}={partition_value}.csv"
        write_csv(path, partition_rows, fieldnames)
        written.append(str(path.relative_to(root)))
    return written


from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Mapping, Sequence

from ashare_premarket.quant_foundation.contracts import canonical_checksum

_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")


def write_local_research_run(
    repository_root: Path,
    output_root: Path,
    run_id: str,
    pipeline_result: Mapping[str, object],
) -> dict[str, object]:
    repository = repository_root.resolve()
    allowed_root = (repository / "outputs" / "local").resolve()
    destination_root = output_root.resolve()
    if destination_root != allowed_root and allowed_root not in destination_root.parents:
        raise ValueError("goal11_output_must_be_under_outputs_local")
    if not _RUN_ID.fullmatch(str(run_id)):
        raise ValueError("invalid_goal11_run_id")
    expected = canonical_checksum(
        {key: value for key, value in pipeline_result.items() if key != "checksum"}
    )
    if pipeline_result.get("checksum") != expected:
        raise ValueError("goal11_pipeline_checksum_mismatch")
    run_directory = destination_root / run_id
    if run_directory.exists():
        raise ValueError("goal11_run_directory_already_exists")
    run_directory.mkdir(parents=True)

    features = list(pipeline_result["feature_rows"])
    alpha = list(pipeline_result["alpha_rows"])
    linear = dict(pipeline_result["linear_ranker"])
    linear_scores = list(linear["scores"])
    evaluation = dict(pipeline_result["evaluation"])
    linear_metadata = {key: value for key, value in linear.items() if key != "scores"}

    _write_csv(run_directory / "features.csv", features)
    _write_csv(run_directory / "alpha_scores.csv", alpha)
    _write_csv(run_directory / "linear_scores.csv", linear_scores)
    _write_json(run_directory / "linear_ranker.json", linear_metadata)
    _write_json(run_directory / "evaluation.json", evaluation)

    artifact_names = (
        "alpha_scores.csv",
        "evaluation.json",
        "features.csv",
        "linear_ranker.json",
        "linear_scores.csv",
    )
    artifacts = {
        name: {
            "sha256": _file_checksum(run_directory / name),
            "size_bytes": (run_directory / name).stat().st_size,
        }
        for name in artifact_names
    }
    manifest: dict[str, object] = {
        "goal_id": "GOAL-11",
        "run_id": run_id,
        "status": "COMPLETE_RESEARCH_ONLY",
        "research_only": True,
        "artifact_policy": "LOCAL_IGNORED_RESEARCH_ONLY",
        "source_snapshot_id": pipeline_result["source_snapshot_id"],
        "generation_timestamp": pipeline_result["generation_timestamp"],
        "code_commit": pipeline_result["code_commit"],
        "feature_version": pipeline_result["feature_version"],
        "feature_row_count": len(features),
        "alpha_row_count": len(alpha),
        "linear_score_row_count": len(linear_scores),
        "label_rows_persisted": 0,
        "model_binary_persisted": False,
        "ready_factor_count": 0,
        "pipeline_checksum": pipeline_result["checksum"],
        "artifacts": artifacts,
    }
    manifest["manifest_checksum"] = canonical_checksum(manifest)
    _write_json(run_directory / "run_manifest.json", manifest)
    return manifest


def _write_csv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    fieldnames = list(rows[0]) if rows else []
    if any(list(row) != fieldnames for row in rows):
        raise ValueError(f"inconsistent_local_csv_schema:{path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(
            {key: _csv_value(row[key]) for key in fieldnames}
            for row in rows
        )


def _csv_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
    return str(value)


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    path.write_text(
        json.dumps(value, allow_nan=False, ensure_ascii=True, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )


def _file_checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

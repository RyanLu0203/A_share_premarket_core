from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Mapping, Sequence

from ashare_premarket.quant_foundation.contracts import canonical_checksum

_JSON_ARTIFACTS = {
    "combined_models.json": "combined_models",
    "data_audit.json": "data_audit",
    "decisions.json": "decisions",
    "fdr_results.json": "fdr_results",
    "folds.json": "splits",
    "null_controls.json": "null_controls",
    "robustness.json": "robustness",
    "single_factor_results.json": "single_factor_results",
}


def write_local_validation_run(
    repository_root: Path,
    output_root: Path,
    run_id: str,
    result: Mapping[str, object],
) -> dict[str, object]:
    repository = repository_root.resolve()
    output = output_root.resolve()
    required_root = (repository / "outputs" / "local").resolve()
    if output != required_root and required_root not in output.parents:
        raise ValueError("goal12_output_must_be_under_outputs_local")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", str(run_id)):
        raise ValueError("invalid_goal12_run_id")
    expected = canonical_checksum(
        {key: value for key, value in result.items() if key != "checksum"}
    )
    if result.get("checksum") != expected:
        raise ValueError("goal12_pipeline_checksum_mismatch")
    if (
        result.get("production_ready") is not False
        or result.get("ready_factor_count") != 0
        or result.get("production_model_promoted") is not False
    ):
        raise ValueError("goal12_result_production_lock_violation")
    run_directory = output / str(run_id)
    if run_directory.exists():
        raise ValueError("goal12_run_directory_already_exists")
    run_directory.mkdir(parents=True)

    _write_csv(run_directory / "features.csv", list(result["feature_rows"]))
    _write_csv(run_directory / "labels.csv", list(result["label_rows"]))
    if "alpha_rows" in result:
        _write_csv(run_directory / "alpha_scores.csv", list(result["alpha_rows"]))
    for filename, key in sorted(_JSON_ARTIFACTS.items()):
        _write_json(run_directory / filename, result[key])
    artifact_paths = sorted(
        path for path in run_directory.iterdir() if path.name != "run_manifest.json"
    )
    manifest: dict[str, object] = {
        "goal_id": "GOAL-12",
        "code_commit": str(result["code_commit"]),
        "run_id": str(run_id),
        "artifact_policy": "LOCAL_IGNORED_RESEARCH_ONLY",
        "production_ready": False,
        "ready_factor_count": 0,
        "result_checksum": str(result["checksum"]),
        "artifacts": [
            {
                "path": path.name,
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in artifact_paths
        ],
    }
    manifest["checksum"] = canonical_checksum(manifest)
    _write_json(run_directory / "run_manifest.json", manifest)
    return manifest


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_csv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    fields = sorted({str(field) for row in rows for field in row})
    preferred = [field for field in ("date", "symbol", "horizon_trading_days") if field in fields]
    fields = preferred + [field for field in fields if field not in preferred]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in sorted(
            rows,
            key=lambda item: (
                str(item.get("date", "")),
                str(item.get("symbol", "")),
                int(item.get("horizon_trading_days", 0)),
            ),
        ):
            writer.writerow({field: _csv_value(row.get(field)) for field in fields})


def _csv_value(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
    return value

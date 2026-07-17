from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Mapping

from ashare_premarket.quant_foundation.contracts import GovernedSnapshot, canonical_checksum

SCHEMA_VERSION = "goal11_governed_market_snapshot_v1"
_REQUIRED_COLUMNS = ("date", "symbol", "close")
_OPTIONAL_COLUMNS = ("available_at", "open", "high", "low", "volume", "index_close")
_LEAKY_PREFIXES = ("forward_return", "future_", "label", "target")


def load_governed_snapshot_from_manifest(
    repository_root: Path,
    manifest_path: Path,
) -> GovernedSnapshot:
    root = repository_root.resolve()
    manifest_file = _confined_path(root, manifest_path, "governed_manifest_path_outside_repository")
    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("governed_manifest_file_missing") from exc
    except json.JSONDecodeError as exc:
        raise ValueError("invalid_governed_snapshot_manifest_json") from exc
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("governed_snapshot_manifest_schema_mismatch")
    expected_manifest = canonical_checksum(
        {key: value for key, value in manifest.items() if key != "manifest_checksum"}
    )
    if manifest.get("manifest_checksum") != expected_manifest:
        raise ValueError("governed_snapshot_manifest_checksum_mismatch")

    source = _confined_path(
        root,
        Path(str(manifest.get("source_path", ""))),
        "governed_source_path_outside_repository",
    )
    if not source.is_file():
        raise ValueError("governed_source_file_missing")
    observed_source_checksum = hashlib.sha256(source.read_bytes()).hexdigest()
    if observed_source_checksum != manifest.get("source_checksum"):
        raise ValueError("governed_source_checksum_mismatch")

    column_map = manifest.get("column_map")
    if not isinstance(column_map, dict):
        raise ValueError("governed_snapshot_column_map_required")
    mapping = {str(key): str(value) for key, value in column_map.items()}
    if any(not mapping.get(name) for name in _REQUIRED_COLUMNS):
        raise ValueError("governed_snapshot_required_column_mapping_missing")
    availability_policy = str(manifest.get("availability_policy", ""))
    if not mapping.get("available_at") and availability_policy != "OBSERVATION_DATE":
        raise ValueError("governed_snapshot_availability_policy_required")

    with source.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = tuple(reader.fieldnames or ())
        leaky = sorted(
            header
            for header in headers
            if header.strip().lower().startswith(_LEAKY_PREFIXES)
        )
        if leaky:
            raise ValueError(
                f"label_column_forbidden_in_feature_source:{','.join(leaky)}"
            )
        missing_required = [
            mapping[name] for name in _REQUIRED_COLUMNS if mapping[name] not in headers
        ]
        if missing_required:
            raise ValueError(
                "governed_snapshot_source_columns_missing:"
                + ",".join(sorted(missing_required))
            )
        rows = [
            _mapped_row(raw, mapping, availability_policy)
            for raw in reader
        ]
    if not rows:
        raise ValueError("governed_source_has_no_rows")
    return GovernedSnapshot.from_rows(
        snapshot_id=str(manifest.get("snapshot_id", "")),
        cutoff_date=str(manifest.get("cutoff_date", "")),
        generation_timestamp=str(manifest.get("generation_timestamp", "")),
        code_commit=str(manifest.get("code_commit", "")),
        source_checksum=str(manifest.get("source_checksum", "")),
        adjustment=str(manifest.get("adjustment", "")),
        rows=rows,
    )


def _mapped_row(
    raw: Mapping[str, str],
    column_map: Mapping[str, str],
    availability_policy: str,
) -> dict[str, object]:
    trade_date = raw[column_map["date"]]
    result: dict[str, object] = {
        "date": trade_date,
        "symbol": raw[column_map["symbol"]],
        "close": raw[column_map["close"]],
        "available_at": (
            raw.get(column_map["available_at"], "")
            if column_map.get("available_at")
            else trade_date
        ),
    }
    for name in _OPTIONAL_COLUMNS:
        if name == "available_at":
            continue
        source_name = column_map.get(name)
        result[name] = raw.get(source_name, "") if source_name else None
    return result


def _confined_path(root: Path, path: Path, reason: str) -> Path:
    candidate = path if path.is_absolute() else root / path
    resolved = candidate.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(reason)
    return resolved

from __future__ import annotations

import json
from pathlib import Path

from ashare_premarket.core.io import read_csv
from ashare_premarket.storage.policy import resolve_data_root

LOCAL_IMPORT_CONFIG = "configs/providers/local_import_provider_config.yaml"


def local_import_paths(root: Path) -> dict[str, Path]:
    payload = json.loads((root / LOCAL_IMPORT_CONFIG).read_text(encoding="utf-8"))
    data_root = resolve_data_root(root)
    contract = payload.get("file_contract", {})
    return {name: data_root / str(path) for name, path in contract.items()}


def read_local_import_table(root: Path, role: str) -> list[dict[str, str]]:
    path = local_import_paths(root).get(role)
    if not path or not path.exists():
        return []
    return read_csv(path)


def local_import_status(root: Path) -> dict[str, object]:
    paths = local_import_paths(root)
    return {
        "available_roles": sorted(role for role, path in paths.items() if path.exists()),
        "missing_roles": sorted(role for role, path in paths.items() if not path.exists()),
    }

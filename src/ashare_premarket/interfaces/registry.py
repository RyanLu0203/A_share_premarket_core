from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REGISTRY_PATH = "configs/project/canonical_interfaces.json"


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_interface_registry(root: Path | None = None) -> dict[str, Any]:
    base = (root or repository_root()).resolve()
    payload = json.loads((base / REGISTRY_PATH).read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.0":
        raise ValueError("unsupported canonical interface registry schema")
    return payload


def api_paths(root: Path | None = None) -> dict[str, str]:
    registry = load_interface_registry(root)
    return {str(row["name"]): str(row["path"]) for row in registry["api_routes"]}


def api_path(name: str, root: Path | None = None) -> str:
    try:
        return api_paths(root)[name]
    except KeyError as exc:
        raise KeyError(f"unknown canonical API route: {name}") from exc


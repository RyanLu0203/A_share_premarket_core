from __future__ import annotations

import json
import os
from pathlib import Path

from ashare_premarket.storage.policy import resolve_data_root

AKSHARE_CONFIG = "configs/providers/akshare_provider_config.yaml"
INGESTION_CONFIG = "configs/ingestion/engineering_pilot_ingestion_config.yaml"


def load_provider_config(root: Path) -> dict[str, object]:
    return _load_json(root / AKSHARE_CONFIG)


def load_ingestion_config(root: Path) -> dict[str, object]:
    return _load_json(root / INGESTION_CONFIG)


def network_enabled(allow_network: bool = False) -> bool:
    return allow_network or os.environ.get("ASHARE_ALLOW_NETWORK_INGESTION", "") in {"1", "true", "TRUE", "yes", "YES"}


def engineering_bundle_root(root: Path, bundle_id: str) -> Path:
    return resolve_data_root(root) / "bundles" / "engineering_pilot" / bundle_id


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))

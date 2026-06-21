from __future__ import annotations

import json
from pathlib import Path

from ashare_premarket.storage.policy import audit_data_bundle_manifest, audit_storage_policy, build_data_bundle_manifest, resolve_data_root

ROOT = Path(__file__).resolve().parents[1]


def test_storage_policy_exists_and_data_root_is_outside_repo() -> None:
    assert (ROOT / "configs/storage/storage_policy.yaml").exists()
    assert (ROOT / "configs/storage/data_bundle_schema.yaml").exists()
    data_root = resolve_data_root(ROOT)
    assert not data_root.is_relative_to(ROOT)


def test_heavy_data_patterns_are_ignored() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for pattern in ["*.duckdb", "*.sqlite", "*.parquet", "*.pkl", "*.joblib", "*.zip", "*.html", "*.ipynb"]:
        assert pattern in gitignore


def test_storage_and_bundle_audits_pass_with_documented_warnings() -> None:
    assert audit_storage_policy(ROOT)
    build_data_bundle_manifest(ROOT)
    assert audit_data_bundle_manifest(ROOT)
    manifest = json.loads((ROOT / "outputs/audits/data_bundle_manifest_summary.json").read_text(encoding="utf-8"))
    assert manifest["bundle_tier"] == "contract_demo"
    assert manifest["blocked_symbol_rows"] == 0

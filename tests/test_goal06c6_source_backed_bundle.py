from __future__ import annotations

import json
import shutil
from pathlib import Path

from ashare_premarket.providers.ingestion import audit_source_backed_local_bundle, build_source_backed_local_bundle

ROOT = Path(__file__).resolve().parents[1]


def _tmp_repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    shutil.copytree(ROOT / "configs", root / "configs")
    return root


def test_no_network_source_backed_bundle_outputs_are_safe(monkeypatch, tmp_path) -> None:
    root = _tmp_repo_root(tmp_path)
    monkeypatch.delenv("ASHARE_ALLOW_NETWORK_INGESTION", raising=False)
    monkeypatch.setenv("ASHARE_PREMARKET_DATA_ROOT", str(tmp_path / "data"))
    assert build_source_backed_local_bundle(root, allow_network=False)
    assert audit_source_backed_local_bundle(root)
    summary = json.loads((root / "outputs/audits/source_backed_bundle_manifest_summary.json").read_text(encoding="utf-8"))
    assert summary["bundle_tier"] == "not_available"
    assert summary["health_status"] == "PASS_WITH_WARNINGS"
    assert summary["local_bundle_path"].startswith(str(tmp_path / "data"))
    for path in (root / "outputs").rglob("*"):
        assert path.suffix not in {".parquet", ".duckdb", ".sqlite", ".db", ".pkl", ".joblib", ".zip"}


def test_source_backed_samples_are_bounded() -> None:
    for path in (ROOT / "outputs/samples").glob("source_backed_*_sample.csv"):
        rows = path.read_text(encoding="utf-8").splitlines()
        assert len(rows) <= 101

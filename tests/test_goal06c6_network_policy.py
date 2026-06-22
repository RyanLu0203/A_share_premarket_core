from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

from ashare_premarket.providers.ingestion import build_source_backed_local_bundle
from ashare_premarket.providers.provider_registry import network_enabled

ROOT = Path(__file__).resolve().parents[1]


def _tmp_repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    shutil.copytree(ROOT / "configs", root / "configs")
    return root


def test_network_ingestion_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("ASHARE_ALLOW_NETWORK_INGESTION", raising=False)
    assert network_enabled(False) is False


def test_network_ingestion_requires_explicit_opt_in(monkeypatch) -> None:
    monkeypatch.setenv("ASHARE_ALLOW_NETWORK_INGESTION", "1")
    assert network_enabled(False) is True
    monkeypatch.delenv("ASHARE_ALLOW_NETWORK_INGESTION", raising=False)
    assert network_enabled(True) is True


def test_no_network_bundle_run_records_policy_without_provider_call(monkeypatch, tmp_path) -> None:
    root = _tmp_repo_root(tmp_path)
    monkeypatch.delenv("ASHARE_ALLOW_NETWORK_INGESTION", raising=False)
    monkeypatch.setenv("ASHARE_PREMARKET_DATA_ROOT", str(tmp_path / "data"))
    assert build_source_backed_local_bundle(root, allow_network=False)
    summary = json.loads((root / "outputs/audits/source_backed_bundle_manifest_summary.json").read_text(encoding="utf-8"))
    assert summary["network_status"] == "network_disabled_by_policy"
    with (root / "outputs/audits/akshare_provider_attempt_summary.csv").open(newline="", encoding="utf-8") as handle:
        attempts = list(csv.DictReader(handle))
    assert attempts
    assert {row["failure_class"] for row in attempts} == {"NETWORK_DISABLED_BY_POLICY"}

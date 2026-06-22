from __future__ import annotations

import json
import shutil
from pathlib import Path

from ashare_premarket.core.io import read_csv
from ashare_premarket.providers.provider_ladder import run_goal06c7_provider_ladder_expansion

ROOT = Path(__file__).resolve().parents[1]


def _tmp_repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    shutil.copytree(ROOT / "configs", root / "configs")
    return root


def test_provider_ladder_no_network_generates_safe_readiness(monkeypatch, tmp_path) -> None:
    root = _tmp_repo_root(tmp_path)
    monkeypatch.delenv("ASHARE_ALLOW_NETWORK_INGESTION", raising=False)
    monkeypatch.delenv("ASHARE_ENABLE_BROWSER_ASSISTED_PROVIDER", raising=False)
    monkeypatch.setenv("ASHARE_PREMARKET_DATA_ROOT", str(tmp_path / "data"))
    assert run_goal06c7_provider_ladder_expansion(root, allow_network=False, enable_browser_assisted=True)
    manifest = json.loads((root / "outputs/audits/source_backed_bundle_manifest_summary.json").read_text(encoding="utf-8"))
    assert manifest["bundle_id"] == "goal06c7_provider_ladder_engineering_pilot_current"
    assert manifest["bundle_tier"] == "below_contract_demo"
    assert manifest["goal06d_allowed_to_proceed"] is False
    assert manifest["raw_html_stored"] is False
    assert manifest["raw_payload_stored"] is False
    browser_audit = json.loads((root / "outputs/audits/browser_assisted_provider_audit.json").read_text(encoding="utf-8"))
    assert browser_audit["browser_assisted_enabled"] is False
    assert browser_audit["browser_assisted_project_default"] is False


def test_provider_ladder_writes_required_bundle_files(monkeypatch, tmp_path) -> None:
    root = _tmp_repo_root(tmp_path)
    data_root = tmp_path / "data"
    monkeypatch.setenv("ASHARE_PREMARKET_DATA_ROOT", str(data_root))
    assert run_goal06c7_provider_ladder_expansion(root, allow_network=False)
    bundle = data_root / "bundles/engineering_pilot/goal06c7_provider_ladder_engineering_pilot_current"
    for name in [
        "manifest.json",
        "universe.csv",
        "trading_calendar.csv",
        "ohlcv_daily.csv",
        "benchmark_daily.csv",
        "provider_attempt_log.csv",
        "provider_failure_events.csv",
        "source_coverage.csv",
        "pit_signal_panel.csv",
        "label_panel.csv",
        "stage6c_engineering_panel.csv",
        "checksums.sha256",
    ]:
        assert (bundle / name).exists()
    assert read_csv(bundle / "provider_failure_events.csv")[0]["primary_failure_class"] == "NETWORK_DISABLED_BY_POLICY"

from __future__ import annotations

import csv
import json
import shutil
from datetime import date, timedelta
from pathlib import Path

import ashare_premarket.providers.provider_ladder as ladder

ROOT = Path(__file__).resolve().parents[1]


def _tmp_repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    shutil.copytree(ROOT / "configs", root / "configs")
    return root


def _dates(count: int) -> list[str]:
    start = date(2023, 1, 1)
    return [(start + timedelta(days=offset)).isoformat() for offset in range(count)]


def _ohlcv(symbol: str, data_role: str, dates: list[str]) -> list[dict[str, object]]:
    rows = []
    for idx, trade_date in enumerate(dates):
        close = 10.0 + idx * 0.1
        base = {
            "trade_date": trade_date,
            "open": close - 0.1,
            "high": close + 0.2,
            "low": close - 0.2,
            "close": close,
            "volume": 1000 + idx,
            "amount": 100000 + idx,
            "provider_id": "mock_source",
            "provider_mode": "akshare_direct",
            "source_bundle_id": ladder.BUNDLE_ID,
            "ingest_ts": "test",
            "schema_version": "goal06c7.ohlcv.v1",
            "data_quality_flags": "SOURCE_BACKED",
        }
        if data_role == "benchmark_ohlcv_daily":
            rows.append({"benchmark_symbol": symbol, **base})
        else:
            rows.append({"symbol": symbol, **base})
    return rows


def test_mocked_provider_ladder_can_reach_engineering_pilot(monkeypatch, tmp_path) -> None:
    root = _tmp_repo_root(tmp_path)
    monkeypatch.setenv("ASHARE_PREMARKET_DATA_ROOT", str(tmp_path / "data"))
    dates = _dates(190)

    def fake_fetch_role(root: Path, data_role: str, symbol: str, start: str, end: str, browser_enabled: bool):
        rows = _ohlcv(symbol, data_role, dates)
        event = ladder._attempt(
            "mock_source",
            "akshare_direct",
            "stock_zh_a_hist",
            data_role,
            "mock.finance.local",
            "PASS",
            "PROVIDER_OK",
            "unknown",
            rows_returned=len(rows),
            schema_valid=True,
        )
        return rows, [event]

    monkeypatch.setattr(ladder, "_fetch_role", fake_fetch_role)
    assert ladder.run_goal06c7_provider_ladder_expansion(root, allow_network=True)
    manifest = json.loads((root / "outputs/audits/source_backed_bundle_manifest_summary.json").read_text(encoding="utf-8"))
    assert manifest["bundle_tier"] == "engineering_pilot"
    assert manifest["approved_symbols"] == 50
    assert manifest["validation_trading_dates"] == 120
    assert manifest["stage6c_engineering_rows"] == 6000
    assert manifest["goal06d_allowed_to_proceed"] is True
    coverage_path = root / "outputs/stage6c/STAGE6C_source_backed_engineering_panel_coverage_summary.csv"
    with coverage_path.open(newline="", encoding="utf-8") as handle:
        coverage = list(csv.DictReader(handle))[0]
    assert coverage["panel_tier"] == "engineering_pilot"
    assert coverage["goal06d_allowed"] == "true"

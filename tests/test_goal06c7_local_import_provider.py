from __future__ import annotations

import shutil
from pathlib import Path

from ashare_premarket.providers.local_import_provider import local_import_status, read_local_import_table

ROOT = Path(__file__).resolve().parents[1]


def _tmp_repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    shutil.copytree(ROOT / "configs", root / "configs")
    return root


def test_local_import_provider_reads_source_backed_csv(monkeypatch, tmp_path) -> None:
    root = _tmp_repo_root(tmp_path)
    data_root = tmp_path / "data"
    local_import = data_root / "local_import"
    local_import.mkdir(parents=True)
    (local_import / "ohlcv_daily.csv").write_text(
        "trade_date,symbol,open,high,low,close,volume,amount,provider_id,provider_mode,source_bundle_id,ingest_ts,schema_version,data_quality_flags\n"
        "2023-01-01,600036.SH,10,11,9,10.5,1000,100000,manual_csv,local_import,bundle,test,v1,SOURCE_BACKED\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("ASHARE_PREMARKET_DATA_ROOT", str(data_root))
    rows = read_local_import_table(root, "ohlcv_daily")
    assert len(rows) == 1
    assert rows[0]["symbol"] == "600036.SH"
    status = local_import_status(root)
    assert "ohlcv_daily" in status["available_roles"]
    assert "benchmark_daily" in status["missing_roles"]

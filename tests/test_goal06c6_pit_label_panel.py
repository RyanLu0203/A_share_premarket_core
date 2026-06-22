from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import shutil

from ashare_premarket.core.io import read_csv, write_csv
from ashare_premarket.providers.ingestion import (
    BUNDLE_ID,
    SOURCE_BACKED_LABEL_FIELDS,
    SOURCE_BACKED_PIT_FIELDS,
    build_source_backed_label_panel,
    build_source_backed_pit_signal_panel,
    rebuild_stage6c_source_backed_engineering_panel,
)
from ashare_premarket.providers.provider_registry import engineering_bundle_root

ROOT = Path(__file__).resolve().parents[1]


def _tmp_repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    shutil.copytree(ROOT / "configs", root / "configs")
    return root


def test_pit_panel_excludes_label_fields_and_uses_prior_close(monkeypatch, tmp_path) -> None:
    root = _tmp_repo_root(tmp_path)
    monkeypatch.setenv("ASHARE_PREMARKET_DATA_ROOT", str(tmp_path / "data"))
    bundle_root = engineering_bundle_root(root, BUNDLE_ID)
    dates = [(date(2024, 1, 2) + timedelta(days=idx)).isoformat() for idx in range(35)]
    stock_rows = [
        {
            "trade_date": trade_date,
            "symbol": "600036.SH",
            "open": 10 + idx,
            "high": 11 + idx,
            "low": 9 + idx,
            "close": 10 + idx,
            "volume": 1000 + idx,
            "amount": 10000 + idx,
            "turnover_rate": 1,
            "source_id": "fixture",
            "quality_flags": "SOURCE_BACKED",
        }
        for idx, trade_date in enumerate(dates)
    ]
    benchmark_rows = [
        {
            "trade_date": trade_date,
            "benchmark_symbol": "000300",
            "open": 100 + idx,
            "high": 101 + idx,
            "low": 99 + idx,
            "close": 100 + idx,
            "volume": 1000,
            "amount": 10000,
            "source_id": "fixture",
            "quality_flags": "SOURCE_BACKED",
        }
        for idx, trade_date in enumerate(dates)
    ]
    write_csv(bundle_root / "ohlcv_daily.csv", stock_rows)
    write_csv(bundle_root / "benchmark_daily.csv", benchmark_rows)
    write_csv(bundle_root / "trading_calendar.csv", [{"trade_date": value} for value in dates[22:28]])

    pit_rows = build_source_backed_pit_signal_panel(root, bundle_root)
    label_rows = build_source_backed_label_panel(root, bundle_root)
    stage_rows = rebuild_stage6c_source_backed_engineering_panel(root, pit_rows, label_rows)

    assert pit_rows
    assert label_rows
    assert stage_rows
    assert not (set(SOURCE_BACKED_PIT_FIELDS) & {"fwd_1d_return", "fwd_3d_return", "fwd_5d_return", "label_ready"})
    assert {"fwd_1d_return", "fwd_3d_return", "fwd_5d_return"} <= set(SOURCE_BACKED_LABEL_FIELDS)
    first_pit = pit_rows[0]
    assert first_pit["as_of_date"] < first_pit["target_trading_date"]
    pit_sample_header = set(read_csv(root / "outputs/samples/source_backed_pit_signal_panel_sample.csv")[0])
    assert "fwd_1d_return" not in pit_sample_header
    assert "leakage_flags" in stage_rows[0]

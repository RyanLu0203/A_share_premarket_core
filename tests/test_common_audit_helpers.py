from __future__ import annotations

from pathlib import Path

from ashare_premarket.audit.common import duplicate_key_failures, forbidden_lookahead_columns, scan_artifact_sizes
from ashare_premarket.core.io import write_csv


def test_common_audit_helpers_detect_schema_and_key_risks(tmp_path: Path) -> None:
    path = tmp_path / "sample.csv"
    write_csv(path, [{"trade_date": "2026-01-01", "symbol": "600036.SH"}, {"trade_date": "2026-01-01", "symbol": "600036.SH"}])
    assert duplicate_key_failures(tmp_path, "sample.csv", ("trade_date", "symbol"))
    assert forbidden_lookahead_columns(["trade_date", "future_return_1d"]) == ["future_return_1d"]
    assert scan_artifact_sizes(tmp_path, ["sample.csv"], limit_bytes=1)


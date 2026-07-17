from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from ashare_premarket.quant_foundation.contracts import canonical_checksum
from ashare_premarket.quant_foundation.snapshot_loader import (
    load_governed_snapshot_from_manifest,
)


def _write_manifest(root: Path, *, source_body: str) -> Path:
    source = root / "evidence" / "market.csv"
    source.parent.mkdir(parents=True)
    source.write_text(source_body, encoding="utf-8")
    manifest: dict[str, object] = {
        "schema_version": "goal11_governed_market_snapshot_v1",
        "snapshot_id": "snapshot-fixture-001",
        "cutoff_date": "2026-07-16",
        "generation_timestamp": "2026-07-16T22:00:00+00:00",
        "code_commit": "e" * 40,
        "source_path": "evidence/market.csv",
        "source_checksum": hashlib.sha256(source.read_bytes()).hexdigest(),
        "adjustment": "qfq",
        "availability_policy": "OBSERVATION_DATE",
        "column_map": {
            "date": "trade_date",
            "symbol": "symbol",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
            "index_close": "index_close",
        },
    }
    manifest["manifest_checksum"] = canonical_checksum(manifest)
    path = root / "snapshot.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def test_loader_verifies_manifest_source_and_explicit_column_mapping(tmp_path: Path) -> None:
    path = _write_manifest(
        tmp_path,
        source_body=(
            "trade_date,symbol,open,high,low,close,volume,index_close\n"
            "2026-07-15,600036.SH,41.8,42.4,41.5,42.0,1000000,3100\n"
            "2026-07-16,600036.SH,42.0,42.8,41.9,42.5,1200000,3110\n"
        ),
    )
    snapshot = load_governed_snapshot_from_manifest(tmp_path, path)

    assert snapshot.snapshot_id == "snapshot-fixture-001"
    assert snapshot.adjustment == "qfq"
    assert len(snapshot.rows) == 2
    assert snapshot.rows[-1].available_at == snapshot.rows[-1].date
    assert snapshot.rows[-1].volume == 1_200_000.0


def test_loader_fails_closed_on_source_checksum_or_path_escape(tmp_path: Path) -> None:
    path = _write_manifest(
        tmp_path,
        source_body="trade_date,symbol,close\n2026-07-16,600036.SH,42\n",
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["source_checksum"] = "0" * 64
    payload["manifest_checksum"] = canonical_checksum(
        {key: value for key, value in payload.items() if key != "manifest_checksum"}
    )
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="governed_source_checksum_mismatch"):
        load_governed_snapshot_from_manifest(tmp_path, path)
    payload["source_path"] = "../outside.csv"
    payload["manifest_checksum"] = canonical_checksum(
        {key: value for key, value in payload.items() if key != "manifest_checksum"}
    )
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="governed_source_path_outside_repository"):
        load_governed_snapshot_from_manifest(tmp_path, path)


def test_loader_rejects_label_columns_even_when_not_mapped(tmp_path: Path) -> None:
    path = _write_manifest(
        tmp_path,
        source_body=(
            "trade_date,symbol,close,forward_return_1d\n"
            "2026-07-16,600036.SH,42,0.1\n"
        ),
    )
    with pytest.raises(ValueError, match="label_column_forbidden_in_feature_source"):
        load_governed_snapshot_from_manifest(tmp_path, path)

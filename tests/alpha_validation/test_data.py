from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest

from ashare_premarket.alpha_validation.data import load_historical_bundle


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _fixture(root: Path) -> dict[str, object]:
    bundle = root / "evidence"
    daily = bundle / "daily.csv"
    index = bundle / "index.csv"
    coverage = bundle / "coverage.csv"
    _write_csv(
        daily,
        ["symbol", "trade_date", "close", "return_1d", "source_provider", "no_lookahead_status"],
        [
            {"symbol": symbol, "trade_date": trade_date, "close": close, "return_1d": "", "source_provider": "akshare_sina", "no_lookahead_status": "passed_current_or_past_only"}
            for trade_date, close in (("2026-01-05", 10), ("2026-01-06", 11), ("2026-01-07", 12))
            for symbol in ("600036.SH", "000002.SZ")
        ],
    )
    _write_csv(
        index,
        ["index_id", "index_name", "trade_date", "close", "return_1d", "source_provider", "no_lookahead_status"],
        [
            {"index_id": "sh000300", "index_name": "csi300", "trade_date": trade_date, "close": close, "return_1d": "", "source_provider": "akshare_sina", "no_lookahead_status": "passed_current_or_past_only"}
            for trade_date, close in (("2026-01-05", 4000), ("2026-01-06", 4010), ("2026-01-07", 4020))
        ],
    )
    _write_csv(
        coverage,
        ["symbol", "first_date", "last_date", "n_dates", "status"],
        [
            {"symbol": symbol, "first_date": "2026-01-05", "last_date": "2026-01-07", "n_dates": 3, "status": "acquired"}
            for symbol in ("600036.SH", "000002.SZ")
        ],
    )
    manifest = {
        "goal": "GOAL-NETWORK-EVIDENCE-INGESTION-01",
        "provider": "akshare_sina",
        "acquisition_timestamp": "2026-01-08T08:00:00+08:00",
        "checksums": {
            "daily.csv": hashlib.sha256(daily.read_bytes()).hexdigest(),
            "index.csv": hashlib.sha256(index.read_bytes()).hexdigest(),
            "coverage.csv": hashlib.sha256(coverage.read_bytes()).hexdigest(),
        },
    }
    (bundle / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    script = root / "acquire.py"
    script.write_text(
        "def acquire(ak, symbol):\n"
        "    return ak.stock_zh_a_daily(symbol=symbol, adjust=\"qfq\")\n",
        encoding="utf-8",
    )
    return {
        "adjustment": "qfq",
        "amount_semantics": "UNAVAILABLE_NULL_NOT_ZERO",
        "availability_semantics": "TRADE_DATE_CLOSE_CONSUMABLE_NEXT_SESSION_OPEN",
        "benchmark_index_id": "sh000300",
        "bundle_manifest_path": "evidence/manifest.json",
        "daily_panel_path": "evidence/daily.csv",
        "expected_goal": "GOAL-NETWORK-EVIDENCE-INGESTION-01",
        "expected_provider": "akshare_sina",
        "index_panel_path": "evidence/index.csv",
        "qfq_contract_evidence_path": "acquire.py",
        "symbol_coverage_path": "evidence/coverage.csv",
        "survivorship_semantics": "CURRENT_LISTING_UNIVERSE_DISCLOSED_NOT_PIT_CONSTITUENTS",
    }


def test_bundle_loader_verifies_lineage_and_builds_close_only_snapshot(tmp_path: Path) -> None:
    config = _fixture(tmp_path)
    bundle = load_historical_bundle(tmp_path, config, code_commit="a" * 40)

    assert bundle.trading_calendar == ("2026-01-05", "2026-01-06", "2026-01-07")
    assert bundle.feature_available_at["2026-01-05"] == "2026-01-06"
    assert bundle.feature_available_at["2026-01-07"] is None
    assert bundle.snapshot.adjustment == "qfq"
    assert len(bundle.snapshot.rows) == 6
    assert bundle.snapshot.rows[0].index_close == 4000.0
    assert bundle.metadata["amount_semantics"] == "UNAVAILABLE_NULL_NOT_ZERO"
    assert bundle.metadata["source_fields_available"] == ("close", "index_close")
    assert bundle.metadata["survivorship_risk_disclosed"] is True


def test_bundle_loader_fails_closed_on_checksum_provider_or_qfq_contract_drift(tmp_path: Path) -> None:
    config = _fixture(tmp_path)
    (tmp_path / "evidence/daily.csv").write_text("drift", encoding="utf-8")
    with pytest.raises(ValueError, match="goal12_source_checksum_mismatch"):
        load_historical_bundle(tmp_path, config, code_commit="a" * 40)

    config = _fixture(tmp_path)
    config["expected_provider"] = "other"
    with pytest.raises(ValueError, match="goal12_provider_mismatch"):
        load_historical_bundle(tmp_path, config, code_commit="a" * 40)

    config = _fixture(tmp_path)
    (tmp_path / "acquire.py").write_text("def acquire(): return None\n", encoding="utf-8")
    with pytest.raises(ValueError, match="goal12_qfq_contract_not_proven"):
        load_historical_bundle(tmp_path, config, code_commit="a" * 40)


def test_bundle_loader_rejects_duplicate_keys_labels_and_fabricated_amount(tmp_path: Path) -> None:
    config = _fixture(tmp_path)
    daily = tmp_path / "evidence/daily.csv"
    body = daily.read_text(encoding="utf-8")
    daily.write_text(body + body.splitlines()[1] + "\n", encoding="utf-8")
    manifest = json.loads((tmp_path / "evidence/manifest.json").read_text(encoding="utf-8"))
    manifest["checksums"]["daily.csv"] = hashlib.sha256(daily.read_bytes()).hexdigest()
    (tmp_path / "evidence/manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate_goal12_daily_key"):
        load_historical_bundle(tmp_path, config, code_commit="a" * 40)

    config = _fixture(tmp_path)
    daily = tmp_path / "evidence/daily.csv"
    rows = list(csv.DictReader(daily.open(encoding="utf-8", newline="")))
    rows[0]["amount"] = "0"
    _write_csv(daily, list(rows[0]), rows)
    manifest = json.loads((tmp_path / "evidence/manifest.json").read_text(encoding="utf-8"))
    manifest["checksums"]["daily.csv"] = hashlib.sha256(daily.read_bytes()).hexdigest()
    (tmp_path / "evidence/manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="goal12_amount_must_remain_unavailable"):
        load_historical_bundle(tmp_path, config, code_commit="a" * 40)

    config = _fixture(tmp_path)
    daily = tmp_path / "evidence/daily.csv"
    rows = list(csv.DictReader(daily.open(encoding="utf-8", newline="")))
    rows[0]["forward_return_5d"] = "0.1"
    _write_csv(daily, list(rows[0]), rows)
    manifest = json.loads((tmp_path / "evidence/manifest.json").read_text(encoding="utf-8"))
    manifest["checksums"]["daily.csv"] = hashlib.sha256(daily.read_bytes()).hexdigest()
    (tmp_path / "evidence/manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="goal12_label_field_in_feature_source"):
        load_historical_bundle(tmp_path, config, code_commit="a" * 40)

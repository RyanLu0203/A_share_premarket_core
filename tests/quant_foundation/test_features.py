from __future__ import annotations

from pathlib import Path

import pytest

from ashare_premarket.quant_foundation.contracts import GovernedSnapshot, canonical_checksum
from ashare_premarket.quant_foundation.features import (
    FEATURE_COLUMNS,
    _ema,
    _macd,
    build_feature_rows,
    load_feature_config,
)
from .conftest import make_snapshot

ROOT = Path(__file__).resolve().parents[2]


def test_optimized_macd_matches_the_original_prefix_definition() -> None:
    values = [100.0 + index * 0.3 + (index % 5) * 0.1 for index in range(80)]
    lines = [
        _ema(values[:end], 12) - _ema(values[:end], 26)
        for end in range(26, len(values) + 1)
    ]
    signal = _ema(lines, 9)

    assert _macd(values) == (lines[-1], signal, lines[-1] - signal)


def _latest(rows: list[dict[str, object]], symbol: str = "600036.SH") -> dict[str, object]:
    return [row for row in rows if row["symbol"] == symbol][-1]


def _snapshot_with_rows(
    base: GovernedSnapshot,
    rows: list[dict[str, object]],
) -> GovernedSnapshot:
    return GovernedSnapshot.from_rows(
        snapshot_id=base.snapshot_id,
        cutoff_date=base.cutoff_date,
        generation_timestamp=base.generation_timestamp,
        code_commit=base.code_commit,
        source_checksum=base.source_checksum,
        adjustment=base.adjustment,
        rows=rows,
    )


def test_builds_all_prespecified_feature_families_with_required_lineage() -> None:
    snapshot = make_snapshot()
    config = load_feature_config(ROOT)
    rows = build_feature_rows(snapshot, config)
    row = _latest(rows)

    assert config["feature_version"] == "goal11_features_v1"
    assert len(rows) == len(snapshot.rows)
    assert row["feature_version"] == "goal11_features_v1"
    assert row["source_snapshot_id"] == snapshot.snapshot_id
    assert row["generation_timestamp"] == snapshot.generation_timestamp
    assert row["code_commit"] == snapshot.code_commit
    assert row["source_checksum"] == snapshot.source_checksum
    assert row["adjustment"] == "qfq"
    assert row["feature_status"] == "COMPLETE"
    assert row["available_feature_families"] == (
        "market_regime",
        "price",
        "technical",
        "volatility",
        "volume",
    )
    assert row["availability_reasons"] == ()
    assert all(row[name] is not None for name in FEATURE_COLUMNS)
    assert row["return_1d"] == pytest.approx(
        snapshot.rows[-1].close / snapshot.rows[-3].close - 1.0
    )
    assert row["momentum_5d"] > 0
    assert row["trend_strength_20d"] > 0
    assert row["volatility_20d"] >= 0
    assert row["rsi_14"] > 50
    assert row["atr_14"] > 0
    assert row["market_regime"] in {"BULL_CALM", "BULL_HIGH_VOL", "BEAR_CALM", "BEAR_HIGH_VOL"}
    assert row["checksum"] == canonical_checksum(
        {key: value for key, value in row.items() if key != "checksum"}
    )


def test_missing_optional_evidence_is_explicit_and_never_fabricated() -> None:
    rows = build_feature_rows(make_snapshot(include_ohlcv=False, include_index=False), load_feature_config(ROOT))
    row = _latest(rows)

    assert row["momentum_20d"] is not None
    assert row["rsi_14"] is not None
    assert row["atr_14"] is None
    assert row["volume_change_1d"] is None
    assert row["abnormal_volume_20d"] is None
    assert row["index_trend_20d"] is None
    assert row["market_volatility_20d"] is None
    assert row["feature_status"] == "PARTIAL"
    assert "ATR_REQUIRES_HIGH_LOW" in row["availability_reasons"]
    assert "VOLUME_FEATURES_REQUIRE_VOLUME" in row["availability_reasons"]
    assert "MARKET_INDEX_REQUIRES_INDEX_CLOSE" in row["availability_reasons"]


def test_feature_generation_is_deterministic() -> None:
    snapshot = make_snapshot()
    config = load_feature_config(ROOT)
    assert build_feature_rows(snapshot, config) == build_feature_rows(snapshot, config)


def test_features_at_a_date_do_not_change_when_only_future_rows_change() -> None:
    base = build_feature_rows(make_snapshot(days=90), load_feature_config(ROOT))
    shocked = build_feature_rows(
        make_snapshot(days=90, future_price_shock_after=70),
        load_feature_config(ROOT),
    )
    date_at_cut = str(base[70 * 2]["date"])
    base_row = next(row for row in base if row["date"] == date_at_cut and row["symbol"] == "600036.SH")
    shocked_row = next(row for row in shocked if row["date"] == date_at_cut and row["symbol"] == "600036.SH")

    assert {name: base_row[name] for name in FEATURE_COLUMNS} == {
        name: shocked_row[name] for name in FEATURE_COLUMNS
    }


def test_warmup_rows_abstain_per_feature_with_deterministic_reasons() -> None:
    row = _latest(
        build_feature_rows(make_snapshot(days=10), load_feature_config(ROOT))
    )
    assert row["return_1d"] is not None
    assert row["momentum_5d"] is not None
    assert row["momentum_20d"] is None
    assert row["volatility_20d"] is None
    assert row["feature_status"] == "PARTIAL"
    assert "INSUFFICIENT_HISTORY:MOMENTUM_20D" in row["availability_reasons"]
    assert tuple(row["availability_reasons"]) == tuple(sorted(row["availability_reasons"]))


def test_market_breadth_requires_consecutive_complete_cross_sections() -> None:
    complete = make_snapshot(days=3)
    missing_date = complete.rows[2].date
    rows = [
        row.as_canonical_dict()
        for row in complete.rows
        if not (row.date == missing_date and row.symbol == "600036.SH")
    ]
    snapshot = _snapshot_with_rows(complete, rows)

    latest = _latest(build_feature_rows(snapshot, load_feature_config(ROOT)))

    assert latest["market_breadth_1d"] is None
    assert latest["return_1d"] is None
    assert "MARKET_BREADTH_REQUIRES_ALIGNED_CROSS_SECTION" in latest["availability_reasons"]
    assert "SYMBOL_HISTORY_GAP_RESET" in latest["availability_reasons"]


def test_future_symbol_addition_does_not_change_historical_breadth() -> None:
    base = make_snapshot(days=3)
    dates = sorted({row.date for row in base.rows})
    rows = [row.as_canonical_dict() for row in base.rows]
    last_date = dates[-1]
    rows.append(
        {
            "date": last_date,
            "available_at": last_date,
            "symbol": "000001.SZ",
            "open": 10.0,
            "high": 10.5,
            "low": 9.5,
            "close": 10.1,
            "volume": 800_000.0,
            "index_close": rows[-1]["index_close"],
        }
    )
    config = load_feature_config(ROOT)
    before = build_feature_rows(base, config)
    after = build_feature_rows(_snapshot_with_rows(base, rows), config)

    historical_date = dates[-2]
    before_row = next(
        row for row in before if row["date"] == historical_date and row["symbol"] == "600036.SH"
    )
    after_row = next(
        row for row in after if row["date"] == historical_date and row["symbol"] == "600036.SH"
    )

    assert after_row["market_breadth_1d"] == before_row["market_breadth_1d"]


def test_single_symbol_snapshot_does_not_claim_market_breadth() -> None:
    base = make_snapshot(days=25)
    rows = [
        row.as_canonical_dict()
        for row in base.rows
        if row.symbol == "600036.SH"
    ]

    latest = _latest(
        build_feature_rows(_snapshot_with_rows(base, rows), load_feature_config(ROOT))
    )

    assert latest["market_breadth_1d"] is None
    assert latest["market_regime"] is None
    assert "MARKET_BREADTH_REQUIRES_ALIGNED_CROSS_SECTION" in latest["availability_reasons"]


def test_index_gap_blocks_regime_window_instead_of_bridging_missing_evidence() -> None:
    base = make_snapshot(days=25)
    dates = sorted({row.date for row in base.rows})
    missing_date = dates[-5]
    rows = []
    for observation in base.rows:
        row = observation.as_canonical_dict()
        if observation.date == missing_date:
            row["index_close"] = None
        rows.append(row)

    latest = _latest(
        build_feature_rows(_snapshot_with_rows(base, rows), load_feature_config(ROOT))
    )

    assert latest["index_trend_20d"] is None
    assert latest["market_volatility_20d"] is None
    assert "MARKET_INDEX_REQUIRES_INDEX_CLOSE" in latest["availability_reasons"]


def test_expired_volume_gap_does_not_leave_stale_availability_warning() -> None:
    base = make_snapshot(days=30)
    first_date = min(row.date for row in base.rows)
    rows = []
    for observation in base.rows:
        row = observation.as_canonical_dict()
        if observation.date == first_date and observation.symbol == "600036.SH":
            row["volume"] = None
        rows.append(row)

    latest = _latest(
        build_feature_rows(_snapshot_with_rows(base, rows), load_feature_config(ROOT))
    )

    assert latest["volume_change_1d"] is not None
    assert latest["abnormal_volume_20d"] is not None
    assert latest["price_volume_correlation_20d"] is not None
    assert "VOLUME_FEATURES_REQUIRE_VOLUME" not in latest["availability_reasons"]


def test_zero_volume_suspension_has_explicit_feature_reasons() -> None:
    base = make_snapshot(days=25)
    dates = sorted({row.date for row in base.rows})
    suspended_date = dates[-2]
    rows = []
    for observation in base.rows:
        row = observation.as_canonical_dict()
        if observation.date == suspended_date and observation.symbol == "600036.SH":
            row["volume"] = 0.0
        rows.append(row)

    latest = _latest(
        build_feature_rows(_snapshot_with_rows(base, rows), load_feature_config(ROOT))
    )

    assert latest["volume_change_1d"] is None
    assert latest["price_volume_correlation_20d"] is None
    assert "VOLUME_CHANGE_REQUIRES_NONZERO_PRIOR_VOLUME" in latest["availability_reasons"]
    assert (
        "PRICE_VOLUME_CORRELATION_REQUIRES_POSITIVE_VOLUME"
        in latest["availability_reasons"]
    )

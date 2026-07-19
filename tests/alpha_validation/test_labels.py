from __future__ import annotations

from typing import Iterable

import pytest

from ashare_premarket.alpha_validation.labels import (
    available_label_rows,
    build_forward_labels,
)
from ashare_premarket.quant_foundation.contracts import GovernedSnapshot, canonical_checksum


CALENDAR = (
    "2026-01-05",
    "2026-01-06",
    "2026-01-07",
    "2026-01-08",
    "2026-01-09",
    "2026-01-12",
)


def _snapshot(
    rows: Iterable[tuple[str, str, float]], *, adjustment: str = "qfq"
) -> GovernedSnapshot:
    return GovernedSnapshot.from_rows(
        snapshot_id="goal12-label-fixture",
        cutoff_date=CALENDAR[-1],
        generation_timestamp="2026-01-12T16:00:00+08:00",
        code_commit="a" * 40,
        source_checksum="b" * 64,
        adjustment=adjustment,
        rows=[
            {
                "date": trade_date,
                "available_at": trade_date,
                "symbol": symbol,
                "close": close,
            }
            for trade_date, symbol, close in rows
        ],
    )


def _config(horizons: tuple[int, ...] = (1, 5, 20)) -> dict[str, object]:
    return {
        "horizons": horizons,
        "label_version": "goal12_qfq_forward_return_v1",
        "calendar_contract": "fixture_calendar",
        "missing_future_policy": "EXPLICIT_MISSING_NO_SHORTEN_NO_ZERO_FILL",
    }


def test_exact_calendar_horizons_have_no_off_by_one_error() -> None:
    snapshot = _snapshot(
        (trade_date, "600036.SH", float(100 + index * 10))
        for index, trade_date in enumerate(CALENDAR)
    )

    labels = build_forward_labels(snapshot, CALENDAR, _config((1, 5)))
    by_key = {
        (row["date"], row["symbol"], row["horizon_trading_days"]): row
        for row in labels
    }

    one_day = by_key[(CALENDAR[0], "600036.SH", 1)]
    assert one_day["target_date"] == CALENDAR[1]
    assert one_day["feature_available_at"] == CALENDAR[1]
    assert one_day["label_available_at"] == CALENDAR[1]
    assert one_day["forward_return"] == 0.1
    five_day = by_key[(CALENDAR[0], "600036.SH", 5)]
    assert five_day["target_date"] == CALENDAR[5]
    assert five_day["forward_return"] == 0.5


def test_missing_exact_future_price_is_explicit_and_never_shortened_or_zero_filled() -> None:
    snapshot = _snapshot(
        [
            (CALENDAR[0], "600036.SH", 100.0),
            (CALENDAR[2], "600036.SH", 120.0),
            (CALENDAR[3], "600036.SH", 130.0),
        ]
    )

    rows = build_forward_labels(snapshot, CALENDAR, _config((1,)))
    first = next(row for row in rows if row["date"] == CALENDAR[0])
    assert first["target_date"] == CALENDAR[1]
    assert first["forward_return"] is None
    assert first["label_available_at"] is None
    assert first["label_status"] == "MISSING_TARGET_PRICE"
    assert first["missing_reason"] == "EXACT_CALENDAR_TARGET_PRICE_UNAVAILABLE"
    assert available_label_rows(rows, horizon=1) == [
        row for row in rows if row["label_status"] == "AVAILABLE"
    ]


def test_calendar_end_is_missing_not_shortened_and_every_row_has_lineage_checksum() -> None:
    snapshot = _snapshot([(CALENDAR[-1], "600036.SH", 100.0)])
    row = build_forward_labels(snapshot, CALENDAR, _config((1,)))[0]

    assert {
        "symbol",
        "feature_date",
        "horizon",
        "label_date",
        "forward_return",
        "label_version",
        "source_snapshot_id",
        "source_data_checksum",
        "calendar_version",
        "code_commit",
        "eligibility_status",
        "exclusion_reason",
    } <= row.keys()
    assert row["feature_date"] == CALENDAR[-1]
    assert row["horizon"] == 1
    assert row["label_date"] is None
    assert row["source_data_checksum"] == snapshot.source_checksum
    assert row["calendar_version"] == "fixture_calendar"
    assert row["code_commit"] == snapshot.code_commit
    assert row["eligibility_status"] == "MISSING_FUTURE_CALENDAR_DATE"
    assert row["exclusion_reason"] == "EXACT_CALENDAR_HORIZON_UNAVAILABLE"
    assert row["target_date"] is None
    assert row["forward_return"] is None
    assert row["label_status"] == "MISSING_FUTURE_CALENDAR_DATE"
    assert row["adjustment"] == "qfq"
    assert row["source_snapshot_id"] == snapshot.snapshot_id
    assert row["source_checksum"] == snapshot.source_checksum
    assert row["checksum"] == canonical_checksum(
        {key: value for key, value in row.items() if key != "checksum"}
    )


def test_labels_fail_closed_for_non_qfq_or_ambiguous_calendar() -> None:
    snapshot = _snapshot([(CALENDAR[0], "600036.SH", 100.0)], adjustment="unknown")
    with pytest.raises(ValueError, match="goal12_labels_require_qfq"):
        build_forward_labels(snapshot, CALENDAR, _config((1,)))

    qfq = _snapshot([(CALENDAR[0], "600036.SH", 100.0)])
    with pytest.raises(ValueError, match="duplicate_trading_calendar_date"):
        build_forward_labels(qfq, (CALENDAR[0], CALENDAR[0]), _config((1,)))

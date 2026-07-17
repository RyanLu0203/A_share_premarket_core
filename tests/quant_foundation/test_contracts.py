from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from ashare_premarket.quant_foundation.contracts import (
    FORBIDDEN_ACTION_FIELDS,
    GovernedSnapshot,
    canonical_checksum,
    validate_research_output_fields,
)


def _metadata() -> dict[str, str]:
    return {
        "snapshot_id": "snapshot-2026-07-16",
        "cutoff_date": "2026-07-16",
        "generation_timestamp": "2026-07-16T22:00:00+00:00",
        "code_commit": "a" * 40,
        "source_checksum": "b" * 64,
        "adjustment": "qfq",
    }


def _row(date: str, symbol: str, close: float) -> dict[str, object]:
    return {
        "date": date,
        "available_at": date,
        "symbol": symbol,
        "open": close - 0.2,
        "high": close + 0.5,
        "low": close - 0.5,
        "close": close,
        "volume": 1_000_000.0,
        "index_close": 3_100.0,
    }


def test_snapshot_is_immutable_sorted_and_has_deterministic_row_checksum() -> None:
    snapshot = GovernedSnapshot.from_rows(
        **_metadata(),
        rows=[
            _row("2026-07-16", "600036.SH", 42.0),
            _row("2026-07-15", "002475.SZ", 35.0),
        ],
    )

    assert [(row.date, row.symbol) for row in snapshot.rows] == [
        ("2026-07-15", "002475.SZ"),
        ("2026-07-16", "600036.SH"),
    ]
    assert snapshot.snapshot_id == "snapshot-2026-07-16"
    assert snapshot.row_checksum == canonical_checksum(
        [row.as_canonical_dict() for row in snapshot.rows]
    )
    assert GovernedSnapshot.from_rows(
        **_metadata(),
        rows=list(reversed([_row("2026-07-16", "600036.SH", 42.0), _row("2026-07-15", "002475.SZ", 35.0)])),
    ).row_checksum == snapshot.row_checksum
    with pytest.raises(FrozenInstanceError):
        snapshot.snapshot_id = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("rows", "reason"),
    [
        (
            [_row("2026-07-16", "600036.SH", 42.0)] * 2,
            "duplicate_observation_key",
        ),
        (
            [_row("2026-07-17", "600036.SH", 42.0)],
            "observation_after_snapshot_cutoff",
        ),
        (
            [{**_row("2026-07-16", "600036.SH", 42.0), "available_at": "2026-07-17"}],
            "observation_available_after_snapshot_cutoff",
        ),
        (
            [{**_row("2026-07-16", "600036.SH", 42.0), "forward_return_1d": 0.1}],
            "label_field_forbidden_in_feature_snapshot",
        ),
        (
            [{**_row("2026-07-16", "600036.SH", 42.0), "close": float("nan")}],
            "non_finite_observation_value",
        ),
    ],
)
def test_snapshot_fails_closed_on_invalid_or_leaky_rows(
    rows: list[dict[str, object]], reason: str
) -> None:
    with pytest.raises(ValueError, match=reason):
        GovernedSnapshot.from_rows(**_metadata(), rows=rows)


def test_snapshot_metadata_must_be_auditable() -> None:
    metadata = _metadata()
    metadata["source_checksum"] = "not-a-checksum"
    with pytest.raises(ValueError, match="invalid_source_checksum"):
        GovernedSnapshot.from_rows(**metadata, rows=[_row("2026-07-16", "600036.SH", 42.0)])


def test_date_grain_features_reject_cross_date_observation_availability() -> None:
    metadata = _metadata()
    metadata["cutoff_date"] = "2026-07-17"
    metadata["generation_timestamp"] = "2026-07-17T22:00:00+00:00"
    row = {
        **_row("2026-07-16", "600036.SH", 42.0),
        "available_at": "2026-07-17T08:00:00+08:00",
    }

    with pytest.raises(ValueError, match="observation_not_available_on_observation_date"):
        GovernedSnapshot.from_rows(**metadata, rows=[row])


def test_research_output_contract_rejects_actionable_fields() -> None:
    assert {
        "recommendation",
        "target_weight",
        "position",
        "quantity",
        "order",
        "action",
    }.issubset(FORBIDDEN_ACTION_FIELDS)
    validate_research_output_fields({"symbol", "date", "alpha_score", "risk_adjusted_score"})
    with pytest.raises(ValueError, match="actionable_output_fields_forbidden"):
        validate_research_output_fields({"symbol", "alpha_score", "target_weight"})

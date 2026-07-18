from __future__ import annotations

from datetime import date
from typing import Mapping, Sequence

from ashare_premarket.quant_foundation.contracts import (
    GovernedSnapshot,
    canonical_checksum,
    validate_research_output_fields,
)


def build_forward_labels(
    snapshot: GovernedSnapshot,
    trading_calendar: Sequence[str],
    config: Mapping[str, object],
) -> list[dict[str, object]]:
    if snapshot.adjustment != "qfq":
        raise ValueError("goal12_labels_require_qfq")
    calendar = _validated_calendar(trading_calendar)
    position = {trade_date: index for index, trade_date in enumerate(calendar)}
    horizons = tuple(int(value) for value in config.get("horizons", ()))
    if not horizons or any(value <= 0 for value in horizons) or len(set(horizons)) != len(horizons):
        raise ValueError("invalid_goal12_label_horizons")
    label_version = str(config.get("label_version", "")).strip()
    calendar_contract = str(config.get("calendar_contract", "")).strip()
    if not label_version or not calendar_contract:
        raise ValueError("incomplete_goal12_label_config")

    prices: dict[tuple[str, str], float] = {}
    for observation in snapshot.rows:
        if observation.date not in position:
            raise ValueError("observation_date_not_in_trading_calendar")
        key = (observation.date, observation.symbol)
        if key in prices:
            raise ValueError("duplicate_goal12_label_source_key")
        prices[key] = observation.close

    rows: list[dict[str, object]] = []
    for observation in snapshot.rows:
        source_index = position[observation.date]
        feature_available_at = (
            calendar[source_index + 1] if source_index + 1 < len(calendar) else None
        )
        for horizon in sorted(horizons):
            target_index = source_index + horizon
            target_date = calendar[target_index] if target_index < len(calendar) else None
            target_price = (
                prices.get((target_date, observation.symbol))
                if target_date is not None
                else None
            )
            if target_date is None:
                status = "MISSING_FUTURE_CALENDAR_DATE"
                reason = "EXACT_CALENDAR_HORIZON_UNAVAILABLE"
                label_available_at = None
                forward_return = None
            elif target_price is None:
                status = "MISSING_TARGET_PRICE"
                reason = "EXACT_CALENDAR_TARGET_PRICE_UNAVAILABLE"
                label_available_at = None
                forward_return = None
            else:
                status = "AVAILABLE"
                reason = None
                label_available_at = target_date
                forward_return = _clean(target_price / observation.close - 1.0)
            row: dict[str, object] = {
                "adjustment": snapshot.adjustment,
                "calendar_contract": calendar_contract,
                "calendar_version": calendar_contract,
                "code_commit": snapshot.code_commit,
                "date": observation.date,
                "eligibility_status": status,
                "exclusion_reason": reason,
                "feature_date": observation.date,
                "feature_available_at": feature_available_at,
                "forward_return": forward_return,
                "horizon": horizon,
                "horizon_trading_days": horizon,
                "label_date": target_date,
                "label_available_at": label_available_at,
                "label_status": status,
                "label_version": label_version,
                "missing_reason": reason,
                "source_data_checksum": snapshot.source_checksum,
                "source_checksum": snapshot.source_checksum,
                "source_snapshot_id": snapshot.snapshot_id,
                "symbol": observation.symbol,
                "target_date": target_date,
            }
            validate_research_output_fields(row)
            row["checksum"] = canonical_checksum(row)
            rows.append(row)
    return sorted(
        rows,
        key=lambda row: (
            str(row["date"]),
            str(row["symbol"]),
            int(row["horizon_trading_days"]),
        ),
    )


def available_label_rows(
    rows: Sequence[Mapping[str, object]], *, horizon: int
) -> list[Mapping[str, object]]:
    return [
        row
        for row in rows
        if int(row.get("horizon_trading_days", -1)) == horizon
        and row.get("label_status") == "AVAILABLE"
    ]


def _validated_calendar(values: Sequence[str]) -> tuple[str, ...]:
    calendar = tuple(map(str, values))
    if len(calendar) != len(set(calendar)):
        raise ValueError("duplicate_trading_calendar_date")
    if tuple(sorted(calendar)) != calendar:
        raise ValueError("trading_calendar_not_chronological")
    try:
        for value in calendar:
            date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("invalid_trading_calendar_date") from exc
    if not calendar:
        raise ValueError("empty_trading_calendar")
    return calendar


def _clean(value: float) -> float:
    rounded = round(value, 12)
    return 0.0 if rounded == 0 else rounded

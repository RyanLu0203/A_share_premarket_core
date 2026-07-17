from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Iterable, Mapping, Sequence

FORBIDDEN_ACTION_FIELDS = frozenset(
    {
        "action",
        "broker",
        "buy",
        "execution",
        "hold",
        "order",
        "portfolio_weight",
        "position",
        "quantity",
        "recommendation",
        "sell",
        "target_price",
        "target_weight",
        "trade",
    }
)
_LEAKY_INPUT_PREFIXES = ("forward_return", "future_", "label", "target")
_SYMBOL_PATTERN = re.compile(r"^[0-9]{6}\.(?:SH|SZ|BJ)$")
_CHECKSUM_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def canonical_checksum(value: object) -> str:
    payload = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_research_output_fields(fields: Iterable[str]) -> None:
    normalized = {str(name).strip().lower() for name in fields}
    forbidden = sorted(normalized & FORBIDDEN_ACTION_FIELDS)
    if forbidden:
        raise ValueError(f"actionable_output_fields_forbidden:{','.join(forbidden)}")


@dataclass(frozen=True)
class MarketObservation:
    date: str
    available_at: str
    symbol: str
    close: float
    open: float | None = None
    high: float | None = None
    low: float | None = None
    volume: float | None = None
    index_close: float | None = None

    @classmethod
    def from_mapping(cls, raw: Mapping[str, object], cutoff_date: str) -> MarketObservation:
        leaky = sorted(
            str(key)
            for key in raw
            if str(key).strip().lower().startswith(_LEAKY_INPUT_PREFIXES)
        )
        if leaky:
            raise ValueError(f"label_field_forbidden_in_feature_snapshot:{','.join(leaky)}")

        observation_date = _iso_date(raw.get("date"), "invalid_observation_date")
        cutoff = _iso_date(cutoff_date, "invalid_snapshot_cutoff_date")
        if observation_date > cutoff:
            raise ValueError("observation_after_snapshot_cutoff")
        available_at = str(raw.get("available_at", "")).strip()
        available_date = _available_date(available_at)
        if available_date > cutoff:
            raise ValueError("observation_available_after_snapshot_cutoff")
        if available_date < observation_date:
            raise ValueError("observation_available_before_observation_date")
        if available_date > observation_date:
            raise ValueError("observation_not_available_on_observation_date")

        symbol = str(raw.get("symbol", "")).strip().upper()
        if not _SYMBOL_PATTERN.fullmatch(symbol):
            raise ValueError("invalid_canonical_symbol")
        numeric = {
            name: _optional_number(raw.get(name), required=name == "close")
            for name in ("open", "high", "low", "close", "volume", "index_close")
        }
        close = numeric["close"]
        assert close is not None
        if close <= 0 or any(
            numeric[name] is not None and numeric[name] <= 0
            for name in ("open", "high", "low", "index_close")
        ):
            raise ValueError("non_positive_observation_price")
        if numeric["volume"] is not None and numeric["volume"] < 0:
            raise ValueError("negative_observation_volume")
        if numeric["high"] is not None and numeric["low"] is not None:
            compared = [close, numeric["low"]]
            if numeric["open"] is not None:
                compared.append(numeric["open"])
            if numeric["high"] < max(compared) or numeric["low"] > min(compared):
                raise ValueError("invalid_observation_ohlc_relationship")
        return cls(
            date=observation_date.isoformat(),
            available_at=available_at,
            symbol=symbol,
            close=close,
            open=numeric["open"],
            high=numeric["high"],
            low=numeric["low"],
            volume=numeric["volume"],
            index_close=numeric["index_close"],
        )

    def as_canonical_dict(self) -> dict[str, object]:
        return {
            "available_at": self.available_at,
            "close": self.close,
            "date": self.date,
            "high": self.high,
            "index_close": self.index_close,
            "low": self.low,
            "open": self.open,
            "symbol": self.symbol,
            "volume": self.volume,
        }


@dataclass(frozen=True)
class GovernedSnapshot:
    snapshot_id: str
    cutoff_date: str
    generation_timestamp: str
    code_commit: str
    source_checksum: str
    adjustment: str
    rows: tuple[MarketObservation, ...]
    row_checksum: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "row_checksum",
            canonical_checksum([row.as_canonical_dict() for row in self.rows]),
        )

    @classmethod
    def from_rows(
        cls,
        *,
        snapshot_id: str,
        cutoff_date: str,
        generation_timestamp: str,
        code_commit: str,
        source_checksum: str,
        adjustment: str,
        rows: Sequence[Mapping[str, object]],
    ) -> GovernedSnapshot:
        if not str(snapshot_id).strip():
            raise ValueError("missing_snapshot_id")
        cutoff = _iso_date(cutoff_date, "invalid_snapshot_cutoff_date").isoformat()
        _aware_timestamp(generation_timestamp)
        commit = str(code_commit).strip().lower()
        if not re.fullmatch(r"[0-9a-f]{7,64}", commit):
            raise ValueError("invalid_code_commit")
        checksum = str(source_checksum).strip().lower()
        if not _CHECKSUM_PATTERN.fullmatch(checksum):
            raise ValueError("invalid_source_checksum")
        normalized_adjustment = str(adjustment).strip().lower()
        if normalized_adjustment not in {"qfq", "hfq", "unadjusted", "unknown"}:
            raise ValueError("invalid_adjustment_semantics")
        observations = tuple(
            sorted(
                (MarketObservation.from_mapping(row, cutoff) for row in rows),
                key=lambda row: (row.date, row.symbol),
            )
        )
        keys = [(row.date, row.symbol) for row in observations]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate_observation_key")
        return cls(
            snapshot_id=str(snapshot_id).strip(),
            cutoff_date=cutoff,
            generation_timestamp=str(generation_timestamp).strip(),
            code_commit=commit,
            source_checksum=checksum,
            adjustment=normalized_adjustment,
            rows=observations,
        )


def _optional_number(value: object, *, required: bool) -> float | None:
    if value in {None, ""}:
        if required:
            raise ValueError("missing_required_observation_value")
        return None
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid_observation_value") from exc
    if not math.isfinite(number):
        raise ValueError("non_finite_observation_value")
    return number


def _iso_date(value: object, reason: str) -> date:
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError as exc:
        raise ValueError(reason) from exc


def _available_date(value: str) -> date:
    if not value:
        raise ValueError("missing_observation_available_at")
    try:
        if "T" in value:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                raise ValueError
            return parsed.date()
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("invalid_observation_available_at") from exc


def _aware_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid_generation_timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError("generation_timestamp_requires_timezone")
    return parsed

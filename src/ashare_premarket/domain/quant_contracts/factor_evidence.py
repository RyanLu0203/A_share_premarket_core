from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol, Sequence


@dataclass(frozen=True)
class FactorEvidenceRow:
    factor_id: str
    factor_version: str
    asof_timestamp: str
    universe_id: str
    horizon: str
    construction_lineage: tuple[str, ...]
    pit_status: str
    ic: float | None
    rank_ic: float | None
    oos_metrics: Mapping[str, float | str | None]
    regime_metrics: Mapping[str, float | str | None]
    stability_metrics: Mapping[str, float | str | None]
    readiness_status: str
    warning_codes: tuple[str, ...]
    evidence_checksum: str


@dataclass(frozen=True)
class FactorEvidenceSnapshot:
    ready_factor_count: int
    readiness_status: str
    factor_rows: tuple[FactorEvidenceRow, ...]


class FactorEvidenceProvider(Protocol):
    def snapshot(self) -> FactorEvidenceSnapshot:
        """Return evidence-backed factor readiness without constructing Alpha."""


class LockedFactorEvidenceProvider:
    def snapshot(self) -> FactorEvidenceSnapshot:
        return FactorEvidenceSnapshot(
            ready_factor_count=0,
            readiness_status="LOCKED_NO_READY_FACTORS",
            factor_rows=(),
        )


def materialize_factor_rows(rows: Sequence[FactorEvidenceRow]) -> tuple[FactorEvidenceRow, ...]:
    return tuple(rows)

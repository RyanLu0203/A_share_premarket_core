from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.io import read_csv


def source_health_rows(root: Path) -> list[dict[str, str]]:
    return read_csv(root / "configs/providers/source_health_contract.csv")


def source_health_score(root: Path, symbol: str) -> float:
    rows = [row for row in source_health_rows(root) if row["symbol"] == symbol]
    if not rows:
        return 0.0
    ready_count = sum(1 for row in rows if row["pit_ready"] == "true")
    return round(ready_count / len(rows), 4)


def active_source_count(root: Path, symbol: str) -> int:
    return sum(1 for row in source_health_rows(root) if row["symbol"] == symbol and row["pit_ready"] == "true")

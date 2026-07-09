from __future__ import annotations

from datetime import date
from pathlib import Path

from ashare_premarket.core.io import read_csv


def trading_calendar(root: Path) -> list[dict[str, str]]:
    return read_csv(root / "configs/project/trading_calendar.csv")


def is_trading_day(root: Path, value: str) -> bool:
    for row in trading_calendar(root):
        if row["date"] == value:
            return row["is_trading_day"] == "true"
    return False


def next_trading_day(root: Path, value: str) -> str:
    current = date.fromisoformat(value)
    for row in trading_calendar(root):
        candidate = date.fromisoformat(row["date"])
        if candidate > current and row["is_trading_day"] == "true":
            return row["date"]
    raise ValueError(f"No next trading day configured after {value}")


def previous_trading_day(root: Path, value: str) -> str:
    current = date.fromisoformat(value)
    for row in reversed(trading_calendar(root)):
        candidate = date.fromisoformat(row["date"])
        if candidate < current and row["is_trading_day"] == "true":
            return row["date"]
    raise ValueError(f"No previous trading day configured before {value}")


def resolve_target_trading_day(root: Path, execution_date: str) -> str:
    if is_trading_day(root, execution_date):
        return execution_date
    return next_trading_day(root, execution_date)

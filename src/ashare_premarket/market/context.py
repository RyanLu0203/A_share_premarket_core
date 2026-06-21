from __future__ import annotations


def market_trend_5d(as_of_date: str) -> float:
    values = {
        "2026-06-15": 0.12,
        "2026-06-16": 0.08,
        "2026-06-17": -0.03,
        "2026-06-18": 0.05,
    }
    return values[as_of_date]

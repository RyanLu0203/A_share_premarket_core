from __future__ import annotations


def pit_event_count(symbol: str, as_of_date: str) -> int:
    counts = {
        "002475.SZ": {"2026-06-15": 1, "2026-06-16": 2, "2026-06-17": 1, "2026-06-18": 2},
        "600036.SH": {"2026-06-15": 2, "2026-06-16": 1, "2026-06-17": 2, "2026-06-18": 1},
    }
    return counts[symbol][as_of_date]

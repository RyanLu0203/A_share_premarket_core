from __future__ import annotations


def sector_momentum_5d(symbol: str, as_of_date: str) -> float:
    base = {
        "002475.SZ": {"2026-06-15": 0.07, "2026-06-16": 0.06, "2026-06-17": 0.02, "2026-06-18": 0.04},
        "600036.SH": {"2026-06-15": 0.03, "2026-06-16": 0.05, "2026-06-17": -0.01, "2026-06-18": 0.02},
    }
    return base[symbol][as_of_date]

from __future__ import annotations


def review_only_nlp_contract_score(symbol: str, as_of_date: str) -> float:
    """Return deterministic metadata-level contract scores, not real text NLP."""
    scores = {
        "002475.SZ": {"2026-06-15": 0.10, "2026-06-16": 0.16, "2026-06-17": 0.08, "2026-06-18": 0.12},
        "600036.SH": {"2026-06-15": 0.05, "2026-06-16": 0.07, "2026-06-17": 0.06, "2026-06-18": 0.09},
    }
    return scores[symbol][as_of_date]

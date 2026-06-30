from __future__ import annotations

from ashare_premarket.providers.akshare.catalog import safe_introspect_akshare_functions
from ashare_premarket.providers.source_catalog import (
    ALLOWED_APPROVED_USAGE,
    CATALOG_FIELDS,
    PRIORITY_BANDS,
    REQUIRED_TOP_LEVEL_CATEGORIES,
    akshare_source_catalog_rows,
    akshare_source_catalog_summary,
)


def test_akshare_source_catalog_covers_required_categories_and_policies() -> None:
    rows = akshare_source_catalog_rows()
    assert len(rows) >= 50
    assert list(rows[0]) == CATALOG_FIELDS
    assert REQUIRED_TOP_LEVEL_CATEGORIES.issubset({row["akshare_category"] for row in rows})
    assert {row["approved_usage"] for row in rows}.issubset(ALLOWED_APPROVED_USAGE)
    assert {row["priority_band"] for row in rows}.issubset(PRIORITY_BANDS)
    assert any(row["priority_band"] == "P0_market_regime_core" for row in rows)
    assert any(row["priority_band"] == "P1_symbol_context_and_event" for row in rows)
    assert any(row["priority_band"] == "P2_macro_fundamental_medium_term" for row in rows)
    assert any(row["priority_band"] == "P3_context_only_or_experimental" for row in rows)
    assert any(row["approved_usage"] == "blocked" for row in rows)
    assert all(
        row["approved_usage"] in {"blocked", "future_review_only"}
        for row in rows
        if row["akshare_category"] == "blocked_or_future_only"
    )
    assert akshare_source_catalog_summary(rows)


def test_akshare_function_introspection_is_import_only() -> None:
    status = safe_introspect_akshare_functions(["stock_zh_a_hist", "definitely_missing_function"])
    assert set(status) == {"stock_zh_a_hist", "definitely_missing_function"}
    assert status["definitely_missing_function"] in {"not_found", "akshare_not_importable"}


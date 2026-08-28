import ast
from pathlib import Path

from ashare_premarket.providers.liquidity_schema_smoke_plan import (
    FAILURE_TAXONOMY,
    PROVIDER_CALLS_AUTHORIZED,
    SANITIZED_METADATA_FIELDS,
    schema_smoke_calls,
    sanitized_observation_template,
    validate_plan,
    validate_sanitized_metadata,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src/ashare_premarket/providers/liquidity_schema_smoke_plan.py"


def test_plan_is_exact_four_call_zero_retry_matrix() -> None:
    calls = schema_smoke_calls()

    assert validate_plan(calls)
    assert len(calls) == 4
    assert {call["canonical_symbol"] for call in calls} == {
        "002475.SZ",
        "600036.SH",
    }
    assert {(call["provider"], call["endpoint"]) for call in calls} == {
        ("tushare_pro", "daily_basic"),
        ("baostock", "query_history_k_data_plus"),
    }
    assert all(call["max_calls"] == 1 for call in calls)
    assert all(call["max_retries"] == 0 for call in calls)
    assert all(call["provider_calls_authorized"] is False for call in calls)
    assert PROVIDER_CALLS_AUTHORIZED is False


def test_expected_fields_and_units_are_explicit() -> None:
    calls = schema_smoke_calls()
    tushare = next(call for call in calls if call["provider"] == "tushare_pro")
    baostock = next(call for call in calls if call["provider"] == "baostock")

    assert "free_share" in tushare["expected_fields"]
    assert tushare["units"]["free_share"] == "ten_thousand_shares"
    assert tushare["units"]["turnover_rate_f"] == "percent"
    assert baostock["expected_fields"] == (
        "date",
        "code",
        "volume",
        "adjustflag",
        "turn",
        "tradestatus",
    )
    assert baostock["units"]["volume"] == "shares"
    assert baostock["units"]["turn"] == "percent"


def test_only_sanitized_metadata_shape_is_accepted() -> None:
    metadata = sanitized_observation_template(schema_smoke_calls()[0])

    assert set(metadata) == set(SANITIZED_METADATA_FIELDS)
    assert validate_sanitized_metadata(metadata)
    assert metadata["status"] == "NOT_AUTHORIZED"
    assert "NOT_AUTHORIZED" in FAILURE_TAXONOMY
    assert not validate_sanitized_metadata({**metadata, "raw_payload": "forbidden"})


def test_module_has_no_provider_or_network_imports() -> None:
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    imports = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert imports.isdisjoint(
        {"tushare", "baostock", "requests", "httpx", "urllib", "socket", "keyring"}
    )

from __future__ import annotations

from ashare_premarket.providers.failure_classification import (
    classify_parser_exception,
    classify_provider_failure,
    classify_schema_contract,
)


def test_missing_target_function_is_dependency_contract_failure() -> None:
    result = classify_provider_failure(exc=AttributeError("module 'akshare' has no attribute 'stock_missing'"))
    assert result.failure_class == "TARGET_FUNCTION_MISSING"
    assert result.failure_layer == "dependency"


def test_signature_mismatch_is_specific() -> None:
    result = classify_provider_failure(exc=TypeError("unexpected keyword argument 'start_date'"))
    assert result.failure_class == "TARGET_FUNCTION_SIGNATURE_UNSUPPORTED"
    assert result.requires_code_fix is True


def test_missing_required_column_is_schema_contract_failure() -> None:
    result = classify_schema_contract(required_columns={"trade_date", "close"}, observed_columns={"trade_date"})
    assert result.failure_class == "REQUIRED_COLUMN_MISSING"
    assert result.failure_layer == "provider_contract"
    assert result.requires_schema_update is True


def test_wrong_column_type_is_schema_contract_failure() -> None:
    result = classify_schema_contract(type_errors={"close": "expected numeric"})
    assert result.failure_class == "COLUMN_TYPE_MISMATCH"
    assert result.requires_code_fix is True


def test_parser_exception_is_project_code_failure() -> None:
    result = classify_parser_exception(ValueError("could not parse provider payload"))
    assert result.failure_class == "IMPLEMENTATION_PARSER_FAILURE"
    assert result.failure_layer == "parser_implementation"

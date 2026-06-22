from __future__ import annotations

from ashare_premarket.providers.failure_classification import classification_for_class


def test_pit_cutoff_violation_blocks_as_project_logic() -> None:
    result = classification_for_class("PIT_CUTOFF_VIOLATION")
    assert result.failure_layer == "pit_calendar_label"
    assert result.requires_code_fix is True
    assert result.goal06d_allowed_after_failure is False


def test_label_leakage_risk_blocks_as_project_logic() -> None:
    result = classification_for_class("LABEL_LEAKAGE_RISK")
    assert result.failure_layer == "pit_calendar_label"
    assert result.requires_code_fix is True


def test_calendar_and_feature_label_join_failures_are_specific() -> None:
    assert classification_for_class("TRADING_CALENDAR_INSUFFICIENT").failure_layer == "pit_calendar_label"
    assert classification_for_class("TRADING_DAY_ALIGNMENT_FAILURE").failure_layer == "pit_calendar_label"
    assert classification_for_class("FEATURE_LABEL_JOIN_FAILURE").failure_layer == "pit_calendar_label"

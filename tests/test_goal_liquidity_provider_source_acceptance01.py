import json
from pathlib import Path

from ashare_premarket.providers.liquidity_source_acceptance import (
    MANIFEST,
    audit_goal,
    free_float_source_rows,
    provider_schema_rows,
    readiness_row,
    run_goal,
    temporal_unit_rows,
)

ROOT = Path(__file__).resolve().parents[1]


def test_documented_sources_are_selected_without_live_acceptance() -> None:
    schema = provider_schema_rows()
    free_float = free_float_source_rows()
    decision = readiness_row()

    assert {row["provider"] for row in schema} == {
        "tushare_pro",
        "baostock",
        "tencent_akshare",
    }
    assert all(
        row["live_schema_verified"] == "false"
        for row in schema
        if row["provider"] in {"tushare_pro", "baostock"}
    )
    selected = [row for row in free_float if row["selected_primary_candidate"] == "true"]
    assert len(selected) == 1
    assert selected[0]["candidate"] == "tushare_pro.daily_basic"
    assert decision["acquisition_preflight_status"] == "BLOCKED"
    assert decision["live_pilot_authorized"] == "false"
    assert decision["accepted_rows"] == 0


def test_units_and_temporal_rules_fail_closed() -> None:
    rules = {
        (row["provider_endpoint"], row["source_field"]): row
        for row in temporal_unit_rows()
    }
    assert rules[("tushare_pro.daily_basic", "free_share")]["normalization"] == (
        "multiply_by_10000"
    )
    assert rules[("baostock.query_history_k_data_plus", "turn")][
        "normalization"
    ] == "divide_by_100"
    assert all(row["silent_inference_allowed"] == "false" for row in rules.values())


def test_goal_outputs_and_manifest_are_auditable() -> None:
    assert run_goal(ROOT)
    manifest = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    assert manifest["goal_status"] == "PASS_WITH_WARNINGS"
    assert manifest["selected_free_float_candidate"] == "tushare_pro.daily_basic"
    assert manifest["provider_calls_performed"] is False
    assert manifest["accepted_rows"] == 0
    assert audit_goal(ROOT)

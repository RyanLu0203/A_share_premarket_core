import json
from pathlib import Path

from ashare_premarket.providers.liquidity_readiness_batch import (
    MANIFEST,
    audit_goal,
    normalizer_contract_rows,
    readiness_row,
    run_goal,
)

ROOT = Path(__file__).resolve().parents[1]


def test_batch_readiness_integrates_four_blocked_safe_workstreams() -> None:
    readiness = readiness_row(ROOT)
    assert readiness["schema_smoke_call_budget"] == 4
    assert readiness["normalizer_state"] == "IMPLEMENTED_OFFLINE"
    assert readiness["pit_availability_state"] == (
        "BLOCKED_ROW_AVAILABLE_AT_MISSING"
    )
    assert readiness["universe100_state"] == "BLOCKED"
    assert readiness["current_eligible_symbol_count"] == 50
    assert readiness["provider_calls_authorized"] == "false"
    assert readiness["accepted_rows"] == 0


def test_both_normalizer_contracts_are_registered() -> None:
    rows = normalizer_contract_rows()
    assert {row["provider_endpoint"] for row in rows} == {
        "tushare_pro.daily_basic",
        "baostock.query_history_k_data_plus",
    }
    assert all(row["implementation_state"] == "implemented_offline" for row in rows)


def test_batch_outputs_are_auditable_and_non_actionable() -> None:
    assert run_goal(ROOT)
    manifest = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    assert manifest["goal_status"] == "PASS_WITH_WARNINGS"
    assert manifest["accepted_universe_symbol_count"] == 0
    assert manifest["partial_universe_emitted"] is False
    assert manifest["provider_calls_performed"] is False
    assert manifest["factor_construction_unlocked"] is False
    assert audit_goal(ROOT)

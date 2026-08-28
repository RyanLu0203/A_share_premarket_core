from pathlib import Path

from ashare_premarket.research.liquidity_candidate_source_contract import (
    MANIFEST,
    audit_goal,
    evaluate_candidate_source,
    run_goal,
)


ROOT = Path(__file__).resolve().parents[1]


def _row(index: int, **updates: object) -> dict[str, object]:
    row: dict[str, object] = {
        "symbol": f"600{index:03d}.SH",
        "exchange": "SH",
        "security_type": "A_share",
        "listing_status": "listed",
        "source_id": "synthetic_official_contract_fixture",
        "available_at": "2026-08-27T18:00:00+08:00",
    }
    row.update(updates)
    return row


def test_accepts_exact_100_pit_safe_symbols_without_outcome_fields() -> None:
    decision = evaluate_candidate_source(
        [_row(index) for index in range(110)],
        source_class="official_exchange_listing",
        decision_cutoff="2026-08-28T08:00:00+08:00",
    )
    assert decision.status == "PASS"
    assert decision.accepted_symbol_count == 100
    assert len(decision.accepted_symbols) == 100
    assert not decision.provider_calls_performed


def test_blocks_incomplete_source_without_partial_universe() -> None:
    decision = evaluate_candidate_source(
        [_row(index) for index in range(50)],
        source_class="owner_supplied_governed_bundle",
        decision_cutoff="2026-08-28T08:00:00+08:00",
    )
    assert decision.status == "BLOCKED"
    assert decision.reason == "INSUFFICIENT_PIT_SAFE_ELIGIBLE_SYMBOLS"
    assert decision.eligible_symbol_count == 50
    assert decision.accepted_symbols == ()


def test_blocks_outcome_like_fields_at_schema_level() -> None:
    rows = [_row(index, future_return_5d="") for index in range(100)]
    decision = evaluate_candidate_source(
        rows,
        source_class="licensed_security_master",
        decision_cutoff="2026-08-28T08:00:00+08:00",
    )
    assert decision.reason == "FORBIDDEN_SELECTION_FIELDS_PRESENT"
    assert decision.forbidden_fields == ("future_return_5d",)


def test_blocks_missing_contract_fields_and_late_rows() -> None:
    missing = evaluate_candidate_source(
        [{"symbol": "600000.SH"}],
        source_class="official_exchange_listing",
        decision_cutoff="2026-08-28T08:00:00+08:00",
    )
    late = evaluate_candidate_source(
        [_row(index, available_at="2026-08-28T09:00:00+08:00") for index in range(100)],
        source_class="official_exchange_listing",
        decision_cutoff="2026-08-28T08:00:00+08:00",
    )
    assert missing.reason == "REQUIRED_SOURCE_FIELDS_MISSING"
    assert "available_at" in missing.missing_fields
    assert late.reason == "INSUFFICIENT_PIT_SAFE_ELIGIBLE_SYMBOLS"
    assert late.late_record_count == 100


def test_current_committed_source_remains_blocked_and_deterministic() -> None:
    assert run_goal(ROOT)
    first = (ROOT / MANIFEST).read_bytes()
    assert run_goal(ROOT)
    assert (ROOT / MANIFEST).read_bytes() == first
    assert audit_goal(ROOT)

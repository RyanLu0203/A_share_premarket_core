from ashare_premarket.research.liquidity_universe_100_contract import (
    BLOCKED_SYMBOLS,
    select_liquidity_universe_100,
)


def _sh_symbol(number: int) -> str:
    return f"600{number:03d}.SH"


def test_selects_exactly_100_with_acquired_symbols_first_and_sorted() -> None:
    symbols = [_sh_symbol(number) for number in range(130)]
    acquired = list(reversed(symbols[40:81]))  # 41 governed acquired symbols
    candidates = [
        {
            "symbol": symbol,
            # These deliberately conflicting values must never affect selection.
            "forward_return_5d": 1000 - index,
            "factor_score": (-1) ** index,
            "performance_rank": 130 - index,
        }
        for index, symbol in reversed(list(enumerate(symbols)))
    ]

    decision = select_liquidity_universe_100(
        candidates,
        acquired_symbols=acquired,
    )

    expected = tuple(sorted(acquired) + sorted(set(symbols) - set(acquired))[:59])
    assert decision.status == "PASS"
    assert decision.is_accepted
    assert decision.accepted_symbols == expected
    assert len(decision.accepted_symbols) == 100
    assert decision.preferred_acquired_count == 41
    assert not decision.provider_calls_performed


def test_deduplicates_and_excludes_blocked_and_non_a_share_symbols() -> None:
    eligible = [_sh_symbol(number) for number in range(101)]
    candidates = [{"symbol": symbol} for symbol in eligible]
    candidates += [
        {"symbol": eligible[0]},
        {"symbol": "000625.SZ"},
        {"symbol": "601138.SH"},
        {"symbol": "900901.SH"},
        {"symbol": "430047.BJ"},
        {"symbol": "NOT_A_SYMBOL"},
    ]

    decision = select_liquidity_universe_100(candidates)

    assert decision.status == "PASS"
    assert len(decision.accepted_symbols) == 100
    assert not (set(decision.accepted_symbols) & BLOCKED_SYMBOLS)
    assert decision.duplicate_record_count == 1
    assert decision.blocked_symbols_removed == ("000625.SZ", "601138.SH")
    assert set(decision.invalid_symbols_removed) == {
        "430047.BJ",
        "900901.SH",
        "NOT_A_SYMBOL",
    }


def test_blocks_without_returning_partial_accepted_universe() -> None:
    candidates = [{"symbol": _sh_symbol(number)} for number in range(99)]

    decision = select_liquidity_universe_100(candidates)

    assert decision.status == "BLOCKED"
    assert not decision.is_accepted
    assert decision.eligible_symbol_count == 99
    assert decision.accepted_symbols == ()


def test_selection_is_independent_of_record_order_and_non_symbol_fields() -> None:
    symbols = [_sh_symbol(number) for number in range(120)]
    first = [{"symbol": symbol, "future_return": index} for index, symbol in enumerate(symbols)]
    second = [
        {"symbol": symbol, "future_return": -index, "factor": 999}
        for index, symbol in enumerate(reversed(symbols))
    ]

    assert (
        select_liquidity_universe_100(first).accepted_symbols
        == select_liquidity_universe_100(second).accepted_symbols
    )

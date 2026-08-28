"""Deterministic, offline contract for a 100-symbol liquidity universe."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Mapping


GOAL_ID = "GOAL-LIQUIDITY-UNIVERSE100-CONTRACT-01"
REQUIRED_SYMBOL_COUNT = 100
BLOCKED_SYMBOLS = frozenset(
    {"000625.SZ", "000858.SZ", "601138.SH", "601208.SH"}
)

# The contract intentionally excludes Beijing-listed securities and B shares.
# It covers canonical Shanghai/Shenzhen A-share code families only.
_A_SHARE_SYMBOL = re.compile(
    r"^(?:(?:000|001|002|003|300|301)\d{3}\.SZ|"
    r"(?:600|601|603|605|688|689)\d{3}\.SH)$"
)


@dataclass(frozen=True)
class LiquidityUniverse100Decision:
    """Result of evaluating the exact-100 universe contract.

    ``accepted_symbols`` is deliberately empty when the contract is blocked;
    callers must never treat an eligible but incomplete universe as accepted.
    """

    goal_id: str
    status: str
    accepted_symbols: tuple[str, ...]
    eligible_symbol_count: int
    preferred_acquired_count: int
    required_symbol_count: int
    blocked_symbols_removed: tuple[str, ...]
    invalid_symbols_removed: tuple[str, ...]
    duplicate_record_count: int
    selection_rule: str
    provider_calls_performed: bool = False

    @property
    def is_accepted(self) -> bool:
        return self.status == "PASS"


def _canonical_a_share(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    symbol = value.strip().upper()
    return symbol if _A_SHARE_SYMBOL.fullmatch(symbol) else None


def select_liquidity_universe_100(
    candidates: Iterable[Mapping[str, object]],
    *,
    acquired_symbols: Iterable[str] = (),
) -> LiquidityUniverse100Decision:
    """Select exactly 100 governed symbols without using outcome information.

    Existing acquired symbols are selected first in symbol order. Remaining
    slots are filled from all other eligible candidates in symbol order. Only
    the ``symbol`` field is read from candidate records; future returns,
    factors, performance metrics, and record order cannot influence selection.
    """

    raw_symbols: list[object] = []
    for candidate in candidates:
        raw_symbols.append(candidate.get("symbol"))

    canonical_symbols = [_canonical_a_share(value) for value in raw_symbols]
    invalid_symbols = sorted(
        {str(value) for value, symbol in zip(raw_symbols, canonical_symbols) if symbol is None}
    )
    valid_symbols = [symbol for symbol in canonical_symbols if symbol is not None]
    duplicate_record_count = len(valid_symbols) - len(set(valid_symbols))
    blocked_removed = tuple(sorted(set(valid_symbols) & BLOCKED_SYMBOLS))
    eligible = sorted(set(valid_symbols) - BLOCKED_SYMBOLS)

    acquired = {
        symbol
        for value in acquired_symbols
        if (symbol := _canonical_a_share(value)) is not None
        and symbol not in BLOCKED_SYMBOLS
    }
    preferred = sorted(set(eligible) & acquired)
    remainder = sorted(set(eligible) - set(preferred))

    if len(eligible) < REQUIRED_SYMBOL_COUNT:
        accepted: tuple[str, ...] = ()
        status = "BLOCKED"
    else:
        accepted = tuple((preferred + remainder)[:REQUIRED_SYMBOL_COUNT])
        status = "PASS"

    return LiquidityUniverse100Decision(
        goal_id=GOAL_ID,
        status=status,
        accepted_symbols=accepted,
        eligible_symbol_count=len(eligible),
        preferred_acquired_count=min(len(preferred), REQUIRED_SYMBOL_COUNT),
        required_symbol_count=REQUIRED_SYMBOL_COUNT,
        blocked_symbols_removed=blocked_removed,
        invalid_symbols_removed=tuple(invalid_symbols),
        duplicate_record_count=duplicate_record_count,
        selection_rule="acquired_first_then_symbol_ascending",
    )

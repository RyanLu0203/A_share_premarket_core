from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.constants import APPROVED_SYMBOLS, BLOCKED_SYMBOLS
from ashare_premarket.core.io import read_csv


def load_approved_symbols(root: Path) -> list[str]:
    path = root / "configs/universe/approved_symbols.csv"
    if path.exists():
        return [row["symbol"] for row in read_csv(path)]
    return list(APPROVED_SYMBOLS)


def load_blocked_symbols(root: Path) -> list[str]:
    path = root / "configs/universe/blocked_symbols.csv"
    if path.exists():
        return [row["symbol"] for row in read_csv(path)]
    return list(BLOCKED_SYMBOLS)


def validate_symbol_governance(root: Path) -> tuple[bool, list[str]]:
    approved = set(load_approved_symbols(root))
    blocked = set(load_blocked_symbols(root))
    messages: list[str] = []
    if approved != set(APPROVED_SYMBOLS):
        messages.append(f"Approved symbols differ from protected set: {sorted(approved)}")
    if blocked != set(BLOCKED_SYMBOLS):
        messages.append(f"Blocked symbols differ from protected set: {sorted(blocked)}")
    overlap = sorted(approved & blocked)
    if overlap:
        messages.append(f"Symbols are both approved and blocked: {overlap}")
    return not messages, messages


def require_approved_symbol(root: Path, symbol: str) -> None:
    if symbol not in load_approved_symbols(root):
        raise ValueError(f"{symbol} is not approved for active workflow use")
    if symbol in load_blocked_symbols(root):
        raise ValueError(f"{symbol} is blocked and cannot be used")

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ashare_premarket.core.io import read_csv

SIZE_LIMIT_BYTES = 95 * 1024 * 1024

FORBIDDEN_LOOKAHEAD_COLUMNS = {
    "future_return_1d",
    "future_return_5d",
    "future_return_20d",
    "benchmark_excess_return",
    "benchmark_excess_return_1d",
    "benchmark_excess_return_5d",
    "benchmark_excess_return_20d",
    "label_ready",
    "label_ready_1d",
    "label_ready_5d",
    "label_ready_20d",
    "ic",
    "rank_ic",
    "hit_rate",
}

FORBIDDEN_OUTPUT_TERMS = {
    "buy",
    "sell",
    "hold",
    "target_price",
    "position_size",
    "portfolio_weight",
    "target_weight",
    "order_quantity",
    "portfolio_return",
    "equity_curve",
    "broker",
    "live_trading",
    "production_db",
    "factor_mining",
    "dqn",
    "reinforcement_learning",
}


@dataclass(frozen=True)
class SchemaContract:
    name: str
    fields: tuple[str, ...]
    primary_key: tuple[str, ...] = ()


def validate_schema(headers: list[str], contract: SchemaContract) -> list[str]:
    failures: list[str] = []
    if headers != list(contract.fields):
        failures.append(f"{contract.name}_schema_mismatch")
    missing_key = [field for field in contract.primary_key if field not in headers]
    if missing_key:
        failures.append(f"{contract.name}_primary_key_missing:{','.join(missing_key)}")
    return failures


def validate_csv_schema(path: Path, contract: SchemaContract) -> list[str]:
    rows = read_csv(path) if path.exists() else []
    headers = list(rows[0]) if rows else _csv_header(path)
    return validate_schema(headers, contract)


def _csv_header(path: Path) -> list[str]:
    if not path.exists():
        return []
    first_line = path.read_text(encoding="utf-8").splitlines()[0:1]
    return first_line[0].split(",") if first_line else []


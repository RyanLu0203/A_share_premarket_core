from __future__ import annotations

from datetime import date, timedelta

from ashare_premarket.quant_foundation.contracts import GovernedSnapshot


def make_snapshot(
    *,
    days: int = 90,
    include_ohlcv: bool = True,
    include_index: bool = True,
    future_price_shock_after: int | None = None,
) -> GovernedSnapshot:
    start = date(2026, 1, 2)
    rows: list[dict[str, object]] = []
    for index in range(days):
        trade_date = (start + timedelta(days=index)).isoformat()
        index_close = 3_000.0 + 2.0 * index
        for symbol_index, symbol in enumerate(("002475.SZ", "600036.SH")):
            close = 30.0 + (symbol_index * 15.0) + (0.12 + symbol_index * 0.03) * index
            close += ((index % 5) - 2) * 0.02
            if future_price_shock_after is not None and index > future_price_shock_after:
                close += 100.0 + index
            row: dict[str, object] = {
                "date": trade_date,
                "available_at": trade_date,
                "symbol": symbol,
                "close": round(close, 6),
            }
            if include_ohlcv:
                row.update(
                    {
                        "open": round(close - 0.1, 6),
                        "high": round(close + 0.4, 6),
                        "low": round(close - 0.4, 6),
                        "volume": 1_000_000.0
                        + symbol_index * 200_000.0
                        + index * 12_000.0
                        + (index % 3) * 7_500.0,
                    }
                )
            if include_index:
                row["index_close"] = index_close
            rows.append(row)
    cutoff = (start + timedelta(days=days - 1)).isoformat()
    return GovernedSnapshot.from_rows(
        snapshot_id=f"synthetic-governed-{cutoff}",
        cutoff_date=cutoff,
        generation_timestamp=f"{cutoff}T22:00:00+00:00",
        code_commit="c" * 40,
        source_checksum="d" * 64,
        adjustment="qfq",
        rows=rows,
    )

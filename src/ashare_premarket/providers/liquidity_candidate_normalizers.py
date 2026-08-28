"""Fail-closed row normalizers for candidate liquidity providers.

The functions in this module are pure: they do not import provider clients,
read credentials, access the network, or invent point-in-time availability.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, InvalidOperation
import re
from typing import Mapping


TUSHARE_SOURCE = "tushare_pro.daily_basic"
BAOSTOCK_SOURCE = "baostock.query_history_k_data_plus"

_CANONICAL_SYMBOL = re.compile(r"^[0-9]{6}\.(?:SH|SZ)$")
_BAOSTOCK_SYMBOL = re.compile(r"^(?:sh|sz)\.[0-9]{6}$")
_CHINA_STANDARD_TIME = timezone(timedelta(hours=8))


class LiquidityCandidateNormalizationError(ValueError):
    """A candidate provider row failed a governed normalization contract."""


def normalize_tushare_daily_basic_row(
    row: Mapping[str, object],
    *,
    available_at: str | datetime | None = None,
    expected_symbol: str | None = None,
    expected_trade_date: str | None = None,
) -> dict[str, object]:
    """Normalize one Tushare ``daily_basic`` row without inferring availability.

    ``free_share`` is documented in ten-thousand shares and is converted to
    shares. ``turnover_rate_f`` is documented as a percentage and is converted
    to a fraction.
    """

    _require_fields(
        row,
        ("ts_code", "trade_date", "free_share", "turnover_rate_f"),
    )
    symbol = _canonical_tushare_symbol(row["ts_code"])
    trade_date = _tushare_trade_date(row["trade_date"])
    _enforce_expected_scope(symbol, trade_date, expected_symbol, expected_trade_date)

    free_share = _decimal(row["free_share"], "free_share", strictly_positive=True)
    free_float_shares = free_share * Decimal("10000")
    if free_float_shares != free_float_shares.to_integral_value():
        _fail(
            "INVALID_FREE_SHARE_PRECISION",
            "free_share does not resolve to whole shares",
        )
    turnover_percent = _decimal(
        row["turnover_rate_f"], "turnover_rate_f", non_negative=True
    )

    return {
        "symbol": symbol,
        "trade_date": trade_date.isoformat(),
        "free_float_shares": int(free_float_shares),
        "turnover_rate": float(turnover_percent / Decimal("100")),
        "source_provider": TUSHARE_SOURCE,
        "available_at": _availability(available_at, trade_date),
    }


def normalize_baostock_history_row(
    row: Mapping[str, object],
    *,
    available_at: str | datetime | None = None,
    expected_symbol: str | None = None,
    expected_trade_date: str | None = None,
) -> dict[str, object]:
    """Normalize one Baostock ``query_history_k_data_plus`` row.

    Baostock volume is already shares. ``turn`` is converted from percent to
    fraction, trade status is mapped to the canonical enum, and only forward
    adjustment (provider flag ``2`` / canonical ``qfq``) is accepted.
    """

    _require_fields(
        row,
        ("code", "date", "volume", "turn", "tradestatus", "adjustflag"),
    )
    symbol = _canonical_baostock_symbol(row["code"])
    trade_date = _iso_trade_date(row["date"], "date")
    _enforce_expected_scope(symbol, trade_date, expected_symbol, expected_trade_date)

    volume = _decimal(row["volume"], "volume", non_negative=True)
    if volume != volume.to_integral_value():
        _fail("INVALID_VOLUME", "volume must be a whole number of shares")
    turnover_percent = _decimal(row["turn"], "turn", non_negative=True)
    trade_status = _trade_status(row["tradestatus"])
    _require_qfq(row["adjustflag"])

    return {
        "symbol": symbol,
        "trade_date": trade_date.isoformat(),
        "volume": int(volume),
        "turnover_rate": float(turnover_percent / Decimal("100")),
        "trade_status": trade_status,
        "adjustment": "qfq",
        "source_provider": BAOSTOCK_SOURCE,
        "available_at": _availability(available_at, trade_date),
    }


# Short aliases keep call sites readable while the endpoint-specific names
# above remain explicit for audits and discovery.
normalize_tushare_daily_basic = normalize_tushare_daily_basic_row
normalize_baostock_history = normalize_baostock_history_row


def _require_fields(row: Mapping[str, object], fields: tuple[str, ...]) -> None:
    if not isinstance(row, Mapping):
        _fail("INVALID_ROW", "row must be a mapping")
    missing = [field for field in fields if field not in row or row[field] in (None, "")]
    if missing:
        _fail("REQUIRED_FIELD_MISSING", ";".join(missing))


def _canonical_tushare_symbol(value: object) -> str:
    if not isinstance(value, str) or not _CANONICAL_SYMBOL.fullmatch(value):
        _fail("INVALID_SYMBOL", "Tushare ts_code must be canonical CODE.SH or CODE.SZ")
    _validate_exchange_prefix(value)
    return value


def _canonical_baostock_symbol(value: object) -> str:
    if not isinstance(value, str) or not _BAOSTOCK_SYMBOL.fullmatch(value):
        _fail("INVALID_SYMBOL", "Baostock code must be sh.CODE or sz.CODE")
    exchange, code = value.split(".")
    symbol = f"{code}.{exchange.upper()}"
    _validate_exchange_prefix(symbol)
    return symbol


def _validate_exchange_prefix(symbol: str) -> None:
    code, exchange = symbol.split(".")
    valid = (
        exchange == "SH" and code.startswith(("5", "6", "9"))
    ) or (
        exchange == "SZ" and code.startswith(("0", "2", "3"))
    )
    if not valid:
        _fail("SYMBOL_EXCHANGE_MISMATCH", symbol)


def _tushare_trade_date(value: object) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{8}", value):
        _fail("INVALID_TRADE_DATE", "Tushare trade_date must be YYYYMMDD")
    try:
        return datetime.strptime(value, "%Y%m%d").date()
    except ValueError as exc:
        raise LiquidityCandidateNormalizationError(
            "INVALID_TRADE_DATE:invalid calendar date"
        ) from exc


def _iso_trade_date(value: object, field: str) -> date:
    if not isinstance(value, str) or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value
    ):
        _fail("INVALID_TRADE_DATE", f"{field} must be YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise LiquidityCandidateNormalizationError(
            "INVALID_TRADE_DATE:invalid calendar date"
        ) from exc


def _enforce_expected_scope(
    symbol: str,
    trade_date: date,
    expected_symbol: str | None,
    expected_trade_date: str | None,
) -> None:
    if expected_symbol is not None:
        if (
            not isinstance(expected_symbol, str)
            or not _CANONICAL_SYMBOL.fullmatch(expected_symbol)
        ):
            _fail("INVALID_EXPECTED_SYMBOL", "expected_symbol must be canonical")
        _validate_exchange_prefix(expected_symbol)
        if symbol != expected_symbol:
            _fail("SYMBOL_SCOPE_MISMATCH", f"expected {expected_symbol}, observed {symbol}")
    if expected_trade_date is not None:
        expected = _iso_trade_date(expected_trade_date, "expected_trade_date")
        if trade_date != expected:
            _fail(
                "TRADE_DATE_SCOPE_MISMATCH",
                f"expected {expected.isoformat()}, observed {trade_date.isoformat()}",
            )


def _decimal(
    value: object,
    field: str,
    *,
    non_negative: bool = False,
    strictly_positive: bool = False,
) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        _fail("INVALID_NUMERIC", f"{field} is not numeric")
    if isinstance(value, str) and (not value or value != value.strip()):
        _fail("INVALID_NUMERIC", f"{field} is empty or padded")
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise LiquidityCandidateNormalizationError(
            f"INVALID_NUMERIC:{field} is not numeric"
        ) from exc
    if not parsed.is_finite():
        _fail("INVALID_NUMERIC", f"{field} must be finite")
    if strictly_positive and parsed <= 0:
        _fail("INVALID_NUMERIC_DOMAIN", f"{field} must be positive")
    if non_negative and parsed < 0:
        _fail("INVALID_NUMERIC_DOMAIN", f"{field} must be non-negative")
    return parsed


def _trade_status(value: object) -> str:
    if isinstance(value, bool):
        _fail("INVALID_TRADE_STATUS", "boolean status is forbidden")
    if value in ("1", 1):
        return "trading"
    if value in ("0", 0):
        return "suspended"
    _fail("INVALID_TRADE_STATUS", "tradestatus must be 0 or 1")


def _require_qfq(value: object) -> None:
    if isinstance(value, bool) or value not in ("2", 2, "qfq"):
        _fail("ADJUSTMENT_NOT_QFQ", "adjustflag must be 2 or qfq")


def _availability(value: str | datetime | None, trade_date: date) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value and value == value.strip():
        candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
        try:
            parsed = datetime.fromisoformat(candidate)
        except ValueError as exc:
            raise LiquidityCandidateNormalizationError(
                "INVALID_AVAILABLE_AT:timestamp must be ISO 8601"
            ) from exc
    else:
        _fail("INVALID_AVAILABLE_AT", "timestamp must be an explicit ISO 8601 value")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail("INVALID_AVAILABLE_AT", "timestamp must include a timezone")
    market_close = datetime.combine(
        trade_date,
        time(15, 0),
        tzinfo=_CHINA_STANDARD_TIME,
    )
    if parsed <= market_close:
        _fail("INVALID_AVAILABLE_AT", "timestamp must be later than trade-date close")
    return parsed.isoformat()


def _fail(code: str, detail: str) -> None:
    raise LiquidityCandidateNormalizationError(f"{code}:{detail}")

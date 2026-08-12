from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence
from zoneinfo import ZoneInfo

from ashare_premarket.providers.ifind_http import IfindProviderError
from ashare_premarket.storage.policy import resolve_data_root


IFIND_NORMALIZED_SCHEMA_VERSION = "ifind-normalized-v1"
IFIND_LICENSE_STORAGE_CLASS = "paid_provider_local_only"
IFIND_BUSINESS_TIMEZONE = ZoneInfo("Asia/Shanghai")

MODULE_SCHEMAS: dict[str, dict[str, tuple[str, ...]]] = {
    "security_master": {
        "required": ("symbol", "as_of_date", "available_at"),
        "primary_key": ("symbol", "as_of_date"),
        "allowed": (
            "symbol",
            "as_of_date",
            "listing_date",
            "delisting_date",
            "entity_name",
            "trading_status",
            "total_shares",
            "float_shares",
            "free_float_shares",
            "industry_code",
            "industry_name",
            "classification_version",
            "unit",
            "currency",
        ),
    },
    "daily_market_and_calendar": {
        "required": (
            "symbol",
            "trade_date",
            "available_at",
            "data_cutoff",
            "adjustment_mode",
        ),
        "primary_key": ("trade_date", "symbol"),
        "allowed": (
            "symbol",
            "trade_date",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "amount",
            "turnover",
            "adjustment_mode",
            "unit",
            "currency",
        ),
    },
    "pit_fundamentals_and_valuation": {
        "required": (
            "symbol",
            "metric_id",
            "report_period",
            "announcement_date",
            "revision_at",
            "available_at",
            "value",
            "unit",
            "currency",
        ),
        "primary_key": ("symbol", "metric_id", "report_period", "revision_at"),
        "allowed": (
            "symbol",
            "metric_id",
            "report_period",
            "announcement_date",
            "revision_at",
            "value",
            "unit",
            "currency",
        ),
    },
    "industry_and_constituents": {
        "required": (
            "symbol",
            "industry_code",
            "classification_version",
            "effective_from",
            "effective_to",
            "available_at",
        ),
        "primary_key": ("symbol", "industry_code", "effective_from"),
        "allowed": (
            "symbol",
            "industry_code",
            "industry_name",
            "classification_version",
            "effective_from",
            "effective_to",
        ),
    },
    "corporate_events_and_announcements": {
        "required": (
            "symbol",
            "event_id",
            "event_type",
            "publication_time",
            "available_at",
        ),
        "primary_key": ("symbol", "event_id"),
        "allowed": (
            "symbol",
            "event_id",
            "event_type",
            "title",
            "report_period",
            "publication_time",
        ),
    },
    "macro_and_edb": {
        "required": (
            "series_id",
            "observation_period",
            "release_date",
            "revision_at",
            "available_at",
            "value",
            "unit",
        ),
        "primary_key": ("series_id", "observation_period", "revision_at"),
        "allowed": (
            "series_id",
            "series_name",
            "observation_period",
            "release_date",
            "revision_at",
            "value",
            "unit",
            "currency",
        ),
    },
    "market_structure_crosscheck": {
        "required": (
            "entity_id",
            "metric_id",
            "trade_date",
            "available_at",
            "value",
            "unit",
            "vendor_definition_version",
        ),
        "primary_key": ("trade_date", "entity_id", "metric_id"),
        "allowed": (
            "entity_id",
            "metric_id",
            "trade_date",
            "value",
            "unit",
            "currency",
            "vendor_definition_version",
        ),
    },
}

MODULE_SOURCE_FUNCTIONS = {
    "security_master": {"basic_data", "basic_data_service", "get_stock_info"},
    "daily_market_and_calendar": {
        "history_quotation",
        "cmd_history_quotation",
        "trade_dates",
        "get_trade_dates",
        "get_stock_performance",
    },
    "pit_fundamentals_and_valuation": {
        "basic_data",
        "basic_data_service",
        "date_sequence",
    },
    "industry_and_constituents": {"data_pool", "basic_data", "basic_data_service"},
    "corporate_events_and_announcements": {"report_query"},
    "macro_and_edb": {"edb", "edb_service"},
    "market_structure_crosscheck": {
        "basic_data",
        "basic_data_service",
        "date_sequence",
        "data_pool",
    },
}

TRADING_CALENDAR_SCHEMA: dict[str, tuple[str, ...]] = {
    "required": ("trade_date", "market_code", "available_at", "data_cutoff"),
    "primary_key": ("trade_date", "market_code"),
    "allowed": ("trade_date", "market_code", "is_trading_day"),
}

_ENVELOPE_FIELDS = {
    "provider_id",
    "source_function",
    "request_digest",
    "schema_version",
    "available_at",
    "data_cutoff",
    "license_storage_class",
    "quality_flags",
    "normalized_checksum",
}
_NUMERIC_FIELDS = {
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
    "turnover",
    "value",
    "total_shares",
    "float_shares",
    "free_float_shares",
}

_BUNDLE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,95}$")
_SYMBOL_RE = re.compile(r"^[0-9]{6}\.(?:SH|SZ|BJ)$")
_QUALITY_FLAG_RE = re.compile(r"^[A-Z0-9][A-Z0-9_:-]{0,79}$")
_NULL_STRINGS = {"", "--", "none", "null", "nan", "n/a", "na"}


@dataclass(frozen=True)
class IfindNormalizedBatch:
    module_id: str
    source_function: str
    request_digest: str
    rows: tuple[dict[str, Any], ...]
    normalized_checksum: str
    schema_version: str = IFIND_NORMALIZED_SCHEMA_VERSION

    def manifest(self) -> dict[str, Any]:
        dates = sorted(
            {
                str(row[field])
                for row in self.rows
                for field in (
                    "trade_date",
                    "as_of_date",
                    "report_period",
                    "observation_period",
                )
                if row.get(field) not in {None, ""}
            }
        )
        symbols = sorted({str(row["symbol"]) for row in self.rows if row.get("symbol")})
        return {
            "provider_id": "ifind",
            "module_id": self.module_id,
            "source_function": self.source_function,
            "schema_version": self.schema_version,
            "license_storage_class": IFIND_LICENSE_STORAGE_CLASS,
            "request_digest": self.request_digest,
            "normalized_checksum": self.normalized_checksum,
            "row_count": len(self.rows),
            "symbol_count": len(symbols),
            "date_min": dates[0] if dates else None,
            "date_max": dates[-1] if dates else None,
            "raw_payload_persisted": False,
            "credentials_persisted": False,
            "recommendation_outputs_created": False,
            "trading_outputs_created": False,
        }


def flatten_ifind_tables(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Explode iFinD table arrays without retaining the original payload."""

    tables = payload.get("tables")
    if not isinstance(tables, list):
        raise IfindProviderError(
            "IFIND_RESPONSE_SCHEMA_MISMATCH", "response tables must be a list"
        )
    flattened: list[dict[str, Any]] = []
    for table in tables:
        if not isinstance(table, Mapping):
            raise IfindProviderError(
                "IFIND_RESPONSE_SCHEMA_MISMATCH",
                "each response table must be an object",
            )
        lengths = [len(value) for value in table.values() if isinstance(value, list)]
        width = max(lengths, default=1)
        if any(length not in {1, width} for length in lengths):
            raise IfindProviderError(
                "IFIND_RESPONSE_SCHEMA_MISMATCH",
                "table arrays have incompatible lengths",
            )
        for index in range(width):
            row: dict[str, Any] = {}
            for field, value in table.items():
                if isinstance(value, list):
                    row[str(field)] = value[0] if len(value) == 1 else value[index]
                else:
                    row[str(field)] = value
            flattened.append(row)
    return flattened


def normalize_ifind_payload(
    *,
    module_id: str,
    payload: Mapping[str, Any],
    field_mapping: Mapping[str, str],
    source_function: str,
    available_at: str,
    decision_cutoff: str,
    request_descriptor: Mapping[str, Any],
    quality_flags: Sequence[str] = (),
    static_fields: Optional[Mapping[str, Any]] = None,
    naive_timezone: Optional[str] = None,
) -> IfindNormalizedBatch:
    if module_id not in MODULE_SCHEMAS:
        raise IfindProviderError(
            "IFIND_MODULE_NOT_ALLOWED", "module is outside the governed data contract"
        )
    if source_function not in MODULE_SOURCE_FUNCTIONS[module_id]:
        raise IfindProviderError(
            "IFIND_SOURCE_FUNCTION_NOT_ALLOWED",
            "source function is outside the approved module contract",
        )
    schema = _module_schema(module_id, source_function)
    _validate_field_mapping(schema, field_mapping, static_fields or {})
    normalized_flags = _validate_quality_flags(quality_flags)
    availability = _normalized_timestamp(available_at, naive_timezone=naive_timezone)
    cutoff = _normalized_timestamp(decision_cutoff, naive_timezone=naive_timezone)
    if availability > cutoff:
        raise IfindProviderError(
            "IFIND_PIT_CUTOFF_VIOLATION",
            "provider data became available after the decision cutoff",
        )
    request_digest = _digest_json(request_descriptor)
    raw_rows = flatten_ifind_tables(payload)
    if not raw_rows:
        raise IfindProviderError(
            "IFIND_EMPTY_RESPONSE", "provider response contained no table rows"
        )

    normalized_rows: list[dict[str, Any]] = []
    for raw_row in raw_rows:
        row = {
            canonical: _clean_value(raw_row.get(source))
            for source, canonical in field_mapping.items()
            if source in raw_row
        }
        row.update(
            {
                field: _clean_value(value)
                for field, value in (static_fields or {}).items()
            }
        )
        row.update(
            {
                "provider_id": "ifind",
                "source_function": source_function,
                "request_digest": request_digest,
                "schema_version": IFIND_NORMALIZED_SCHEMA_VERSION,
                "available_at": availability,
                "data_cutoff": cutoff,
                "license_storage_class": IFIND_LICENSE_STORAGE_CLASS,
                "quality_flags": ";".join(normalized_flags),
            }
        )
        _normalize_row_types(row, naive_timezone=naive_timezone)
        _validate_module_row(module_id, row, schema=schema, cutoff=cutoff)
        normalized_rows.append(row)

    primary_key = schema["primary_key"]
    normalized_rows.sort(
        key=lambda row: tuple(str(row.get(field, "")) for field in primary_key)
    )
    keys = [tuple(row.get(field) for field in primary_key) for row in normalized_rows]
    if len(set(keys)) != len(keys):
        raise IfindProviderError(
            "IFIND_DUPLICATE_NORMALIZED_KEY",
            "normalized rows contain duplicate primary keys",
        )

    checksum = _digest_json(normalized_rows)
    for row in normalized_rows:
        row["normalized_checksum"] = checksum
    return IfindNormalizedBatch(
        module_id=module_id,
        source_function=source_function,
        request_digest=request_digest,
        rows=tuple(normalized_rows),
        normalized_checksum=checksum,
    )


def write_ifind_normalized_bundle(
    root: Path, batch: IfindNormalizedBatch, bundle_id: str
) -> Path:
    """Write normalized paid data outside Git; immutable bundle ids cannot be overwritten."""

    if not _BUNDLE_ID_RE.fullmatch(bundle_id):
        raise IfindProviderError(
            "IFIND_BUNDLE_ID_INVALID",
            "bundle id does not match the immutable bundle contract",
        )
    if batch.module_id not in MODULE_SCHEMAS:
        raise IfindProviderError(
            "IFIND_MODULE_NOT_ALLOWED",
            "bundle module is outside the governed data contract",
        )
    if not os.environ.get("ASHARE_PREMARKET_DATA_ROOT", "").strip():
        raise IfindProviderError(
            "IFIND_STORAGE_ROOT_ENV_REQUIRED",
            "paid normalized data requires an explicit external ASHARE_PREMARKET_DATA_ROOT",
        )
    data_root = resolve_data_root(root)
    if _is_relative_to(data_root, root.resolve()):
        raise IfindProviderError(
            "IFIND_STORAGE_POLICY_VIOLATION",
            "local paid-data root must be outside the repository",
        )
    ifind_root = data_root / "normalized" / "ifind"
    module_root = ifind_root / batch.module_id
    bundle_root = module_root / bundle_id
    if bundle_root.exists():
        raise IfindProviderError(
            "IFIND_BUNDLE_IMMUTABLE",
            "an existing normalized bundle cannot be overwritten",
        )
    module_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(ifind_root, 0o700)
    os.chmod(module_root, 0o700)
    temporary_root = Path(
        tempfile.mkdtemp(prefix=f".{bundle_id}.tmp-", dir=module_root)
    )
    try:
        rows_path = temporary_root / "rows.jsonl"
        manifest_path = temporary_root / "manifest.json"
        with rows_path.open("w", encoding="utf-8", newline="\n") as handle:
            for row in batch.rows:
                handle.write(
                    json.dumps(
                        row, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                    )
                )
                handle.write("\n")
        os.chmod(rows_path, 0o600)
        manifest = {
            **batch.manifest(),
            "bundle_id": bundle_id,
            "rows_sha256": _sha256_file(rows_path),
        }
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.chmod(manifest_path, 0o600)
        temporary_root.rename(bundle_root)
    except Exception:
        shutil.rmtree(temporary_root, ignore_errors=True)
        raise
    return bundle_root / "manifest.json"


def _validate_module_row(
    module_id: str,
    row: Mapping[str, Any],
    *,
    schema: Mapping[str, tuple[str, ...]],
    cutoff: str,
) -> None:
    missing = [
        field
        for field in schema["required"]
        if row.get(field) is None or row.get(field) == ""
    ]
    if missing:
        raise IfindProviderError(
            "IFIND_NORMALIZED_REQUIRED_FIELD_MISSING",
            f"normalized row is missing required fields: {','.join(missing)}",
        )
    symbol = row.get("symbol")
    if symbol is not None and not _SYMBOL_RE.fullmatch(str(symbol).upper()):
        raise IfindProviderError(
            "IFIND_SYMBOL_FORMAT_MISMATCH", "normalized symbol is not canonical"
        )
    for field in schema["allowed"]:
        value = row.get(field)
        if isinstance(value, (Mapping, list, tuple, set)):
            raise IfindProviderError(
                "IFIND_COLUMN_TYPE_MISMATCH",
                "canonical fields must contain scalar values",
            )
    _validate_temporal_consistency(module_id, row, cutoff=cutoff)
    _validate_numeric_domains(row)
    if module_id == "daily_market_and_calendar":
        _validate_ohlcv(row)


def _validate_ohlcv(row: Mapping[str, Any]) -> None:
    prices = {
        field: _optional_float(row.get(field))
        for field in ("open", "high", "low", "close")
    }
    available_prices = [value for value in prices.values() if value is not None]
    if available_prices and any(
        value <= 0 or not math.isfinite(value) for value in available_prices
    ):
        raise IfindProviderError(
            "IFIND_INVALID_PRICE_VALUE",
            "normalized market prices must be positive and finite",
        )
    if all(prices[field] is not None for field in prices):
        if prices["high"] < max(prices["open"], prices["close"]) or prices["low"] > min(
            prices["open"], prices["close"]
        ):
            raise IfindProviderError(
                "IFIND_INVALID_OHLC_RELATION",
                "normalized OHLC values violate price bounds",
            )
    for field in ("volume", "amount", "turnover"):
        value = _optional_float(row.get(field))
        if value is not None and (value < 0 or not math.isfinite(value)):
            raise IfindProviderError(
                "IFIND_INVALID_MARKET_VALUE",
                f"normalized {field} must be non-negative and finite",
            )


def _normalize_row_types(row: dict[str, Any], *, naive_timezone: Optional[str]) -> None:
    if row.get("symbol") is not None:
        row["symbol"] = str(row["symbol"]).upper()
    for field in (
        "trade_date",
        "as_of_date",
        "report_period",
        "announcement_date",
        "effective_from",
        "effective_to",
        "observation_period",
        "release_date",
    ):
        if row.get(field) is not None:
            row[field] = _normalized_date(str(row[field]))
    for field in ("publication_time", "revision_at"):
        if row.get(field) is not None:
            row[field] = _normalized_timestamp(
                str(row[field]), naive_timezone=naive_timezone
            )
    for field in _NUMERIC_FIELDS:
        if row.get(field) is not None:
            row[field] = _optional_float(row[field])


def _validate_field_mapping(
    schema: Mapping[str, tuple[str, ...]],
    field_mapping: Mapping[str, str],
    static_fields: Mapping[str, Any],
) -> None:
    allowed = set(schema["allowed"])
    canonical_fields = [str(field) for field in field_mapping.values()]
    if not field_mapping or len(set(canonical_fields)) != len(canonical_fields):
        raise IfindProviderError(
            "IFIND_FIELD_MAPPING_INVALID",
            "field mapping must be non-empty and map each canonical field once",
        )
    if any(
        field not in allowed or field in _ENVELOPE_FIELDS for field in canonical_fields
    ):
        raise IfindProviderError(
            "IFIND_FIELD_MAPPING_INVALID",
            "field mapping contains a field outside the canonical module schema",
        )
    static_names = {str(field) for field in static_fields}
    if canonical_fields and static_names.intersection(canonical_fields):
        raise IfindProviderError(
            "IFIND_FIELD_MAPPING_INVALID",
            "static fields must not overwrite mapped canonical fields",
        )
    if any(field not in allowed or field in _ENVELOPE_FIELDS for field in static_names):
        raise IfindProviderError(
            "IFIND_FIELD_MAPPING_INVALID",
            "static fields contain a field outside the canonical module schema",
        )


def _validate_quality_flags(quality_flags: Sequence[str]) -> tuple[str, ...]:
    values = tuple(
        sorted({str(flag).strip() for flag in quality_flags if str(flag).strip()})
    )
    if any(not _QUALITY_FLAG_RE.fullmatch(flag) for flag in values):
        raise IfindProviderError(
            "IFIND_QUALITY_FLAG_INVALID",
            "quality flags must use bounded stable reason-code syntax",
        )
    return values


def _validate_temporal_consistency(
    module_id: str, row: Mapping[str, Any], *, cutoff: str
) -> None:
    cutoff_time = _parse_normalized_timestamp(cutoff)
    availability = _parse_normalized_timestamp(str(row["available_at"]))
    cutoff_business_date = cutoff_time.astimezone(IFIND_BUSINESS_TIMEZONE).date()
    availability_business_date = availability.astimezone(IFIND_BUSINESS_TIMEZONE).date()
    if availability > cutoff_time:
        raise IfindProviderError(
            "IFIND_PIT_CUTOFF_VIOLATION", "availability is after the decision cutoff"
        )

    for field in ("trade_date", "as_of_date", "report_period", "observation_period"):
        if (
            row.get(field)
            and date.fromisoformat(str(row[field])) > cutoff_business_date
        ):
            raise IfindProviderError(
                "IFIND_PIT_CUTOFF_VIOLATION",
                f"{field} is after the decision cutoff",
            )
    for field in ("announcement_date", "release_date"):
        if (
            row.get(field)
            and date.fromisoformat(str(row[field])) > availability_business_date
        ):
            raise IfindProviderError(
                "IFIND_TEMPORAL_INCONSISTENCY",
                f"{field} is after provider availability",
            )
    for field in ("publication_time", "revision_at"):
        if (
            row.get(field)
            and _parse_normalized_timestamp(str(row[field])) > availability
        ):
            raise IfindProviderError(
                "IFIND_TEMPORAL_INCONSISTENCY",
                f"{field} is after provider availability",
            )
    if module_id == "industry_and_constituents":
        effective_from = date.fromisoformat(str(row["effective_from"]))
        effective_to = date.fromisoformat(str(row["effective_to"]))
        if effective_from > cutoff_business_date:
            raise IfindProviderError(
                "IFIND_PIT_CUTOFF_VIOLATION",
                "classification effective_from is after the decision cutoff",
            )
        if effective_to < effective_from:
            raise IfindProviderError(
                "IFIND_TEMPORAL_INCONSISTENCY",
                "classification effective_to is before effective_from",
            )


def _validate_numeric_domains(row: Mapping[str, Any]) -> None:
    for field in _NUMERIC_FIELDS:
        value = row.get(field)
        if value is not None and not math.isfinite(float(value)):
            raise IfindProviderError(
                "IFIND_INVALID_NUMERIC_VALUE",
                f"normalized {field} must be finite",
            )
    shares = [
        row.get(field)
        for field in ("free_float_shares", "float_shares", "total_shares")
    ]
    if any(value is not None and float(value) < 0 for value in shares):
        raise IfindProviderError(
            "IFIND_INVALID_SHARE_VALUE", "normalized share counts must be non-negative"
        )
    free_float, float_shares, total_shares = shares
    if (
        free_float is not None
        and float_shares is not None
        and float(free_float) > float(float_shares)
    ):
        raise IfindProviderError(
            "IFIND_INVALID_SHARE_RELATION", "free-float shares exceed float shares"
        )
    if (
        float_shares is not None
        and total_shares is not None
        and float(float_shares) > float(total_shares)
    ):
        raise IfindProviderError(
            "IFIND_INVALID_SHARE_RELATION", "float shares exceed total shares"
        )


def _clean_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return None if stripped.lower() in _NULL_STRINGS else stripped
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def _optional_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise IfindProviderError(
            "IFIND_COLUMN_TYPE_MISMATCH", "boolean values are not valid numeric fields"
        )
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise IfindProviderError(
            "IFIND_COLUMN_TYPE_MISMATCH", "numeric field could not be parsed"
        ) from exc


def _normalized_date(value: str) -> str:
    text = value.strip()
    for pattern in ("%Y-%m-%d", "%Y%m%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, pattern).date().isoformat()
        except ValueError:
            continue
    raise IfindProviderError(
        "IFIND_DATE_FORMAT_MISMATCH", "date field is not a supported calendar date"
    )


def _normalized_timestamp(value: str, *, naive_timezone: Optional[str] = None) -> str:
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        try:
            parsed = datetime.combine(date.fromisoformat(text), datetime.min.time())
        except ValueError as exc:
            raise IfindProviderError(
                "IFIND_DATE_FORMAT_MISMATCH", "timestamp is not ISO-8601"
            ) from exc
    if parsed.tzinfo is None:
        if naive_timezone != "Asia/Shanghai":
            raise IfindProviderError(
                "IFIND_TIMEZONE_REQUIRED",
                "naive provider timestamps require an explicit Asia/Shanghai contract",
            )
        parsed = parsed.replace(tzinfo=ZoneInfo("Asia/Shanghai"))
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_normalized_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _module_schema(
    module_id: str, source_function: str
) -> Mapping[str, tuple[str, ...]]:
    if module_id == "daily_market_and_calendar" and source_function in {
        "trade_dates",
        "get_trade_dates",
    }:
        return TRADING_CALENDAR_SCHEMA
    return MODULE_SCHEMAS[module_id]


def _digest_json(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False

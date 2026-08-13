from __future__ import annotations

import hashlib
import json
import math
import os
import re
import stat
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence, Tuple
from zoneinfo import ZoneInfo

from ashare_premarket.providers.ifind_acceptance import (
    IFIND_DUAL_STOCK_IDENTITIES,
    IFIND_DUAL_STOCK_SYMBOLS,
)
from ashare_premarket.providers.ifind_normalization import (
    IFIND_LICENSE_STORAGE_CLASS,
    IFIND_NORMALIZED_SCHEMA_VERSION,
    MODULE_SCHEMAS,
)
from ashare_premarket.providers.ifind_s2 import (
    IFIND_S2_ACCEPTANCE_STATE,
    IFIND_S2_ADJUSTMENT_MODE,
    IFIND_S2_DATA_CALL_BUDGET,
    IFIND_S2_DAILY_SESSION_COUNT,
    IFIND_S2_STAGE_ID,
    expected_ifind_s2_trade_dates,
    ifind_s2_request_digest,
)
from ashare_premarket.providers.ifind_http import IfindProviderError


IFIND_S2_BUNDLE_MODE = "local_s2_accepted_bundle_read_only"
IFIND_S2_BUNDLE_ARTIFACT_COUNT = 4
IFIND_S2_BUNDLE_ROW_COUNT = 242

_BUNDLE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,95}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_MAX_MANIFEST_BYTES = 128 * 1024
_MAX_ARTIFACT_BYTES = 8 * 1024 * 1024
_MAX_JSONL_LINE_BYTES = 256 * 1024
_MODULES = ("security_master", "daily_market_and_calendar")
_SOURCE_FUNCTIONS = {
    "security_master": "get_stock_info",
    "daily_market_and_calendar": "get_stock_performance",
}
_EXPECTED_ROWS = {
    "security_master": 1,
    "daily_market_and_calendar": IFIND_S2_DAILY_SESSION_COUNT,
}
_EXPECTED_ARTIFACTS = {
    (
        module_id,
        symbol,
    ): f"{module_id}__{symbol.replace('.', '_')}.jsonl"
    for symbol in IFIND_DUAL_STOCK_SYMBOLS
    for module_id in _MODULES
}
_MANIFEST_FIELDS = {
    "bundle_id",
    "provider_id",
    "stage_id",
    "acceptance_state",
    "license_storage_class",
    "symbols",
    "data_call_count",
    "retries_per_request",
    "decision_timestamp",
    "cutoff_date",
    "raw_payload_persisted",
    "credentials_persisted",
    "artifacts",
}
_ARTIFACT_FIELDS = {
    "file",
    "module_id",
    "symbol",
    "provider_id",
    "source_function",
    "schema_version",
    "license_storage_class",
    "request_digest",
    "row_count",
    "symbol_count",
    "date_min",
    "date_max",
    "normalized_checksum",
    "file_sha256",
    "raw_payload_persisted",
    "credentials_persisted",
    "recommendation_outputs_created",
    "trading_outputs_created",
}
_ROW_ENVELOPE_FIELDS = {
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
_SECURITY_CONTENT_FIELDS = {
    "symbol",
    "as_of_date",
    "listing_date",
    "entity_name",
    "trading_status",
    "total_shares",
    "float_shares",
}
_MARKET_CONTENT_FIELDS = {
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
}
_NUMERIC_FIELDS = {
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
    "turnover",
    "total_shares",
    "float_shares",
    "free_float_shares",
}
_COMPANY_NAMES = {
    symbol: company_name
    for symbol, company_name, _exchange in IFIND_DUAL_STOCK_IDENTITIES
}
_BUSINESS_TIMEZONE = ZoneInfo("Asia/Shanghai")


@dataclass(frozen=True)
class IfindS2AcceptedBundle:
    """Fail-closed, read-only view of one status-anchored S2 bundle."""

    safe_status: Mapping[str, Any]
    rows: Tuple[Mapping[str, Any], ...] = ()

    @property
    def accepted(self) -> bool:
        return self.safe_status.get("status") == "PASS"

    def rows_for_module(self, module_id: str) -> Tuple[Mapping[str, Any], ...]:
        if module_id not in _MODULES:
            return ()
        return tuple(row for row in self.rows if row.get("module_id") == module_id)


class _BundleValidationError(Exception):
    def __init__(self, failure_code: str) -> None:
        super().__init__(failure_code)
        self.failure_code = failure_code


def load_ifind_s2_accepted_bundle(
    repository_root: Path,
    status: Mapping[str, Any],
    *,
    environ: Optional[Mapping[str, str]] = None,
) -> IfindS2AcceptedBundle:
    """Load exactly one accepted local bundle without discovery or fallback.

    The caller supplies an already-sanitized S2 status. The status must anchor
    both the immutable bundle id and the exact manifest digest. Any status,
    path, manifest, artifact, schema, or checksum failure returns no rows.
    """

    try:
        bundle_id, manifest_anchor = _validate_accepted_status(status)
        source = os.environ if environ is None else environ
        data_root = _explicit_data_root(repository_root, source)
        bundle_root = data_root / "normalized" / "ifind" / "s2_acceptance" / bundle_id
        _require_private_directory(bundle_root)
        manifest_path = bundle_root / "manifest.json"
        _require_private_regular_file(manifest_path)
        manifest_bytes = _read_bounded_file(
            manifest_path,
            maximum_bytes=_MAX_MANIFEST_BYTES,
            failure_code="IFIND_S2_BUNDLE_MANIFEST_READ_FAILED",
        )
        if _sha256_bytes(manifest_bytes) != manifest_anchor:
            raise _BundleValidationError("IFIND_S2_BUNDLE_MANIFEST_HASH_MISMATCH")
        manifest = _parse_json_object(
            manifest_bytes,
            failure_code="IFIND_S2_BUNDLE_MANIFEST_INVALID",
        )
        decision_timestamp, cutoff_date = _validate_manifest(
            manifest, bundle_id=bundle_id
        )
        artifacts = _validate_artifact_descriptors(
            manifest["artifacts"], cutoff_date=cutoff_date
        )
        try:
            expected_market_dates = expected_ifind_s2_trade_dates(
                repository_root, cutoff_date
            )
        except IfindProviderError as exc:
            raise _BundleValidationError("IFIND_S2_BUNDLE_CALENDAR_MISMATCH") from exc
        expected_names = {"manifest.json", *(_EXPECTED_ARTIFACTS.values())}
        actual_names = _directory_entry_names(bundle_root)
        if actual_names != expected_names:
            raise _BundleValidationError("IFIND_S2_BUNDLE_FILE_SET_MISMATCH")

        loaded_rows: list[dict[str, Any]] = []
        market_dates: dict[str, Tuple[str, ...]] = {}
        for key in sorted(artifacts):
            module_id, symbol = key
            descriptor = artifacts[key]
            artifact_path = bundle_root / str(descriptor["file"])
            _require_private_regular_file(artifact_path)
            rows = _load_artifact_rows(
                artifact_path,
                descriptor=descriptor,
                module_id=module_id,
                symbol=symbol,
                decision_timestamp=decision_timestamp,
                cutoff_date=cutoff_date,
            )
            if module_id == "daily_market_and_calendar":
                market_dates[symbol] = tuple(str(row["trade_date"]) for row in rows)
            loaded_rows.extend({"module_id": module_id, **row} for row in rows)

        if len(loaded_rows) != IFIND_S2_BUNDLE_ROW_COUNT:
            raise _BundleValidationError("IFIND_S2_BUNDLE_TOTAL_ROW_COUNT_MISMATCH")
        date_sets = {dates for dates in market_dates.values()}
        shared_dates = next(iter(date_sets), ())
        if (
            set(market_dates) != set(IFIND_DUAL_STOCK_SYMBOLS)
            or len(date_sets) != 1
            or len(shared_dates) != IFIND_S2_DAILY_SESSION_COUNT
            or shared_dates != expected_market_dates
        ):
            raise _BundleValidationError("IFIND_S2_BUNDLE_CALENDAR_MISMATCH")

        safe_status = _safe_result(
            status="PASS",
            failure_code=None,
            bundle_id=bundle_id,
            manifest_sha256=manifest_anchor,
            artifact_count=IFIND_S2_BUNDLE_ARTIFACT_COUNT,
            row_count=IFIND_S2_BUNDLE_ROW_COUNT,
        )
        return IfindS2AcceptedBundle(
            safe_status=safe_status,
            rows=tuple(loaded_rows),
        )
    except _BundleValidationError as exc:
        return IfindS2AcceptedBundle(
            safe_status=_safe_result(status="BLOCKED", failure_code=exc.failure_code)
        )
    except Exception:
        # Disk and parser errors are intentionally collapsed to a stable code;
        # no local path, licensed value, or raw exception text is exposed.
        return IfindS2AcceptedBundle(
            safe_status=_safe_result(
                status="BLOCKED",
                failure_code="IFIND_S2_BUNDLE_VALIDATION_FAILED",
            )
        )


def _validate_accepted_status(status: Mapping[str, Any]) -> Tuple[str, str]:
    bundle_id = status.get("bundle_id")
    manifest_sha256 = status.get("bundle_manifest_sha256")
    required = {
        "status": "PASS",
        "acceptance_state": IFIND_S2_ACCEPTANCE_STATE,
        "data_call_count": IFIND_S2_DATA_CALL_BUDGET,
        "normalized_row_count": IFIND_S2_BUNDLE_ROW_COUNT,
        "bundle_persisted": True,
        "live_handshake_verified": True,
        "input_schemas_verified": True,
        "provider_schema_accepted": True,
        "canonical_accepted": True,
        "raw_payload_persisted": False,
        "credential_exposed": False,
    }
    if any(status.get(key) != value for key, value in required.items()):
        raise _BundleValidationError("IFIND_S2_BUNDLE_STATUS_NOT_ACCEPTED")
    if not isinstance(bundle_id, str) or not _BUNDLE_ID_RE.fullmatch(bundle_id):
        raise _BundleValidationError("IFIND_S2_BUNDLE_STATUS_ANCHOR_INVALID")
    if not isinstance(manifest_sha256, str) or not _SHA256_RE.fullmatch(
        manifest_sha256
    ):
        raise _BundleValidationError("IFIND_S2_BUNDLE_STATUS_ANCHOR_INVALID")
    return bundle_id, manifest_sha256


def _explicit_data_root(repository_root: Path, environ: Mapping[str, str]) -> Path:
    raw_value = environ.get("ASHARE_PREMARKET_DATA_ROOT")
    if not isinstance(raw_value, str) or not raw_value.strip():
        raise _BundleValidationError("IFIND_STORAGE_ROOT_ENV_REQUIRED")
    candidate = Path(raw_value.strip()).expanduser()
    if not candidate.is_absolute() or ".." in candidate.parts:
        raise _BundleValidationError("IFIND_S2_BUNDLE_PATH_INVALID")
    _reject_symlink_components(candidate)
    try:
        data_root = candidate.resolve(strict=True)
        repository = Path(repository_root).resolve(strict=True)
    except OSError as exc:
        raise _BundleValidationError("IFIND_S2_BUNDLE_PATH_UNAVAILABLE") from exc
    if data_root == repository or _is_relative_to(data_root, repository):
        raise _BundleValidationError("IFIND_STORAGE_POLICY_VIOLATION")
    if not data_root.is_dir():
        raise _BundleValidationError("IFIND_S2_BUNDLE_PATH_UNAVAILABLE")
    return data_root


def _validate_manifest(
    manifest: Mapping[str, Any], *, bundle_id: str
) -> Tuple[str, str]:
    if set(manifest) != _MANIFEST_FIELDS:
        raise _BundleValidationError("IFIND_S2_BUNDLE_MANIFEST_SCHEMA_MISMATCH")
    required = {
        "bundle_id": bundle_id,
        "provider_id": "ifind",
        "stage_id": IFIND_S2_STAGE_ID,
        "acceptance_state": IFIND_S2_ACCEPTANCE_STATE,
        "license_storage_class": IFIND_LICENSE_STORAGE_CLASS,
        "symbols": list(IFIND_DUAL_STOCK_SYMBOLS),
        "data_call_count": IFIND_S2_DATA_CALL_BUDGET,
        "retries_per_request": 0,
        "raw_payload_persisted": False,
        "credentials_persisted": False,
    }
    if any(manifest.get(key) != value for key, value in required.items()):
        raise _BundleValidationError("IFIND_S2_BUNDLE_MANIFEST_CONTRACT_MISMATCH")
    decision_timestamp_value = manifest.get("decision_timestamp")
    decision_time = _parse_normalized_timestamp(decision_timestamp_value)
    cutoff_date = _normalized_date(manifest.get("cutoff_date"))
    if (
        decision_time is None
        or not isinstance(decision_timestamp_value, str)
        or cutoff_date is None
        or cutoff_date > decision_time.date().isoformat()
    ):
        raise _BundleValidationError("IFIND_S2_BUNDLE_MANIFEST_TIME_INVALID")
    return decision_timestamp_value, cutoff_date


def _validate_artifact_descriptors(
    value: Any,
    *,
    cutoff_date: str,
) -> dict[Tuple[str, str], Mapping[str, Any]]:
    if not isinstance(value, list) or len(value) != IFIND_S2_BUNDLE_ARTIFACT_COUNT:
        raise _BundleValidationError("IFIND_S2_BUNDLE_ARTIFACT_SET_MISMATCH")
    indexed: dict[Tuple[str, str], Mapping[str, Any]] = {}
    for descriptor in value:
        if not isinstance(descriptor, Mapping) or set(descriptor) != _ARTIFACT_FIELDS:
            raise _BundleValidationError("IFIND_S2_BUNDLE_ARTIFACT_SCHEMA_MISMATCH")
        module_id = descriptor.get("module_id")
        symbol = descriptor.get("symbol")
        key = (str(module_id), str(symbol))
        if key not in _EXPECTED_ARTIFACTS or key in indexed:
            raise _BundleValidationError("IFIND_S2_BUNDLE_ARTIFACT_SET_MISMATCH")
        if (
            descriptor.get("file") != _EXPECTED_ARTIFACTS[key]
            or descriptor.get("provider_id") != "ifind"
            or descriptor.get("source_function") != _SOURCE_FUNCTIONS[key[0]]
            or descriptor.get("schema_version") != IFIND_NORMALIZED_SCHEMA_VERSION
            or descriptor.get("license_storage_class") != IFIND_LICENSE_STORAGE_CLASS
            or descriptor.get("row_count") != _EXPECTED_ROWS[key[0]]
            or descriptor.get("symbol_count") != 1
            or not isinstance(descriptor.get("request_digest"), str)
            or not _SHA256_RE.fullmatch(str(descriptor["request_digest"]))
            or descriptor.get("request_digest")
            != ifind_s2_request_digest(
                _SOURCE_FUNCTIONS[key[0]],
                key[1],
                cutoff_date=(
                    cutoff_date if key[0] == "daily_market_and_calendar" else None
                ),
            )
            or not isinstance(descriptor.get("normalized_checksum"), str)
            or not _SHA256_RE.fullmatch(str(descriptor["normalized_checksum"]))
            or not isinstance(descriptor.get("file_sha256"), str)
            or not _SHA256_RE.fullmatch(str(descriptor["file_sha256"]))
            or descriptor.get("raw_payload_persisted") is not False
            or descriptor.get("credentials_persisted") is not False
            or descriptor.get("recommendation_outputs_created") is not False
            or descriptor.get("trading_outputs_created") is not False
        ):
            raise _BundleValidationError("IFIND_S2_BUNDLE_ARTIFACT_CONTRACT_MISMATCH")
        indexed[key] = descriptor
    if set(indexed) != set(_EXPECTED_ARTIFACTS):
        raise _BundleValidationError("IFIND_S2_BUNDLE_ARTIFACT_SET_MISMATCH")
    return indexed


def _load_artifact_rows(
    path: Path,
    *,
    descriptor: Mapping[str, Any],
    module_id: str,
    symbol: str,
    decision_timestamp: str,
    cutoff_date: str,
) -> list[dict[str, Any]]:
    raw = _read_bounded_file(
        path,
        maximum_bytes=_MAX_ARTIFACT_BYTES,
        failure_code="IFIND_S2_BUNDLE_ARTIFACT_READ_FAILED",
    )
    if _sha256_bytes(raw) != descriptor["file_sha256"]:
        raise _BundleValidationError("IFIND_S2_BUNDLE_ARTIFACT_HASH_MISMATCH")
    if not raw.endswith(b"\n"):
        raise _BundleValidationError("IFIND_S2_BUNDLE_ARTIFACT_FORMAT_INVALID")
    encoded_lines = raw.splitlines()
    if len(encoded_lines) != descriptor["row_count"] or any(
        not line or len(line) > _MAX_JSONL_LINE_BYTES for line in encoded_lines
    ):
        raise _BundleValidationError("IFIND_S2_BUNDLE_ARTIFACT_ROW_COUNT_MISMATCH")
    rows = [
        _parse_json_object(
            line,
            failure_code="IFIND_S2_BUNDLE_ARTIFACT_FORMAT_INVALID",
        )
        for line in encoded_lines
    ]
    _validate_rows(
        rows,
        descriptor=descriptor,
        module_id=module_id,
        symbol=symbol,
        decision_timestamp=decision_timestamp,
        cutoff_date=cutoff_date,
    )
    return rows


def _validate_rows(
    rows: Sequence[dict[str, Any]],
    *,
    descriptor: Mapping[str, Any],
    module_id: str,
    symbol: str,
    decision_timestamp: str,
    cutoff_date: str,
) -> None:
    schema = MODULE_SCHEMAS[module_id]
    allowed_fields = set(schema["allowed"]) | _ROW_ENVELOPE_FIELDS
    content_required = (
        _SECURITY_CONTENT_FIELDS
        if module_id == "security_master"
        else _MARKET_CONTENT_FIELDS
    )
    required_fields = set(schema["required"]) | _ROW_ENVELOPE_FIELDS | content_required
    expected_source = _SOURCE_FUNCTIONS[module_id]
    expected_quality = (
        {"S2_TYPED_PROVIDER_SCHEMA"}
        if module_id == "security_master"
        else {"S2_TYPED_PROVIDER_SCHEMA", "GOVERNED_CALENDAR_ALIGNED"}
    )
    primary_key = tuple(schema["primary_key"])
    primary_keys: list[Tuple[str, ...]] = []
    checksum_rows: list[dict[str, Any]] = []
    available_timestamps: set[str] = set()
    for row in rows:
        if set(row) - allowed_fields or any(
            field not in row or row[field] is None or row[field] == ""
            for field in required_fields
        ):
            raise _BundleValidationError("IFIND_S2_BUNDLE_ROW_SCHEMA_MISMATCH")
        if (
            row.get("symbol") != symbol
            or row.get("provider_id") != "ifind"
            or row.get("source_function") != expected_source
            or row.get("request_digest") != descriptor["request_digest"]
            or row.get("schema_version") != IFIND_NORMALIZED_SCHEMA_VERSION
            or row.get("license_storage_class") != IFIND_LICENSE_STORAGE_CLASS
            or row.get("data_cutoff") != decision_timestamp
            or row.get("normalized_checksum") != descriptor["normalized_checksum"]
            or not isinstance(row.get("request_digest"), str)
            or not _SHA256_RE.fullmatch(str(row["request_digest"]))
        ):
            raise _BundleValidationError("IFIND_S2_BUNDLE_ROW_CONTRACT_MISMATCH")
        quality_flags = row.get("quality_flags")
        if (
            not isinstance(quality_flags, str)
            or set(value for value in quality_flags.split(";") if value)
            != expected_quality
        ):
            raise _BundleValidationError("IFIND_S2_BUNDLE_ROW_QUALITY_MISMATCH")
        available_at = _parse_normalized_timestamp(row.get("available_at"))
        decision_time = _parse_normalized_timestamp(decision_timestamp)
        if (
            available_at is None
            or decision_time is None
            or available_at > decision_time
        ):
            raise _BundleValidationError("IFIND_S2_BUNDLE_ROW_TIME_INVALID")
        data_date_field = (
            "as_of_date" if module_id == "security_master" else "trade_date"
        )
        if (
            date.fromisoformat(str(row[data_date_field]))
            > available_at.astimezone(_BUSINESS_TIMEZONE).date()
        ):
            raise _BundleValidationError("IFIND_S2_BUNDLE_ROW_TIME_INVALID")
        available_timestamps.add(str(row["available_at"]))
        _validate_row_values(row, module_id=module_id, cutoff_date=cutoff_date)
        key = tuple(str(row[field]) for field in primary_key)
        primary_keys.append(key)
        checksum_row = dict(row)
        checksum_row.pop("normalized_checksum")
        checksum_rows.append(checksum_row)
    date_field = "as_of_date" if module_id == "security_master" else "trade_date"
    if len(available_timestamps) != 1:
        raise _BundleValidationError("IFIND_S2_BUNDLE_ROW_TIME_INVALID")
    dates = tuple(sorted({str(row[date_field]) for row in rows}))
    if (
        not dates
        or descriptor.get("date_min") != dates[0]
        or descriptor.get("date_max") != dates[-1]
    ):
        raise _BundleValidationError("IFIND_S2_BUNDLE_ARTIFACT_DATE_RANGE_MISMATCH")
    if len(set(primary_keys)) != len(primary_keys) or primary_keys != sorted(
        primary_keys
    ):
        raise _BundleValidationError("IFIND_S2_BUNDLE_PRIMARY_KEY_INVALID")
    if _digest_json(checksum_rows) != descriptor["normalized_checksum"]:
        raise _BundleValidationError("IFIND_S2_BUNDLE_NORMALIZED_CHECKSUM_MISMATCH")


def _validate_row_values(
    row: Mapping[str, Any], *, module_id: str, cutoff_date: str
) -> None:
    for key, value in row.items():
        if isinstance(value, (Mapping, list, tuple, set)):
            raise _BundleValidationError("IFIND_S2_BUNDLE_ROW_SCHEMA_MISMATCH")
        if key in _NUMERIC_FIELDS and value is not None:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise _BundleValidationError("IFIND_S2_BUNDLE_ROW_TYPE_MISMATCH")
            if not math.isfinite(float(value)):
                raise _BundleValidationError("IFIND_S2_BUNDLE_ROW_TYPE_MISMATCH")
    if module_id == "security_master":
        as_of_date = _normalized_date(row.get("as_of_date"))
        listing_date = _normalized_date(row.get("listing_date"))
        if (
            as_of_date is None
            or listing_date is None
            or as_of_date > cutoff_date
            or listing_date > as_of_date
            or row.get("entity_name") != _COMPANY_NAMES[row["symbol"]]
        ):
            raise _BundleValidationError("IFIND_S2_BUNDLE_ROW_CONTENT_INVALID")
        total_shares = float(row["total_shares"])
        float_shares = float(row["float_shares"])
        if total_shares < 0 or float_shares < 0 or float_shares > total_shares:
            raise _BundleValidationError("IFIND_S2_BUNDLE_ROW_CONTENT_INVALID")
        return

    trade_date = _normalized_date(row.get("trade_date"))
    if (
        trade_date is None
        or trade_date > cutoff_date
        or row.get("adjustment_mode") != IFIND_S2_ADJUSTMENT_MODE
    ):
        raise _BundleValidationError("IFIND_S2_BUNDLE_ROW_CONTENT_INVALID")
    prices = {field: float(row[field]) for field in ("open", "high", "low", "close")}
    if (
        any(value <= 0 for value in prices.values())
        or prices["high"] < max(prices["open"], prices["close"])
        or prices["low"] > min(prices["open"], prices["close"])
        or any(float(row[field]) < 0 for field in ("volume", "amount", "turnover"))
    ):
        raise _BundleValidationError("IFIND_S2_BUNDLE_ROW_CONTENT_INVALID")


def _directory_entry_names(path: Path) -> set[str]:
    try:
        entries = tuple(path.iterdir())
    except OSError as exc:
        raise _BundleValidationError("IFIND_S2_BUNDLE_PATH_UNAVAILABLE") from exc
    for entry in entries:
        if entry.is_symlink():
            raise _BundleValidationError("IFIND_S2_BUNDLE_SYMLINK_REJECTED")
    return {entry.name for entry in entries}


def _require_private_directory(path: Path) -> None:
    _reject_symlink_components(path)
    try:
        metadata = path.stat()
    except OSError as exc:
        raise _BundleValidationError("IFIND_S2_BUNDLE_PATH_UNAVAILABLE") from exc
    if not stat.S_ISDIR(metadata.st_mode):
        raise _BundleValidationError("IFIND_S2_BUNDLE_PATH_INVALID")
    if stat.S_IMODE(metadata.st_mode) & 0o077:
        raise _BundleValidationError("IFIND_S2_BUNDLE_PERMISSIONS_INVALID")


def _require_private_regular_file(path: Path) -> None:
    _reject_symlink_components(path)
    try:
        metadata = path.stat()
    except OSError as exc:
        raise _BundleValidationError("IFIND_S2_BUNDLE_PATH_UNAVAILABLE") from exc
    if not stat.S_ISREG(metadata.st_mode):
        raise _BundleValidationError("IFIND_S2_BUNDLE_PATH_INVALID")
    if stat.S_IMODE(metadata.st_mode) & 0o077:
        raise _BundleValidationError("IFIND_S2_BUNDLE_PERMISSIONS_INVALID")


def _reject_symlink_components(path: Path) -> None:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        try:
            metadata = current.lstat()
        except OSError as exc:
            raise _BundleValidationError("IFIND_S2_BUNDLE_PATH_UNAVAILABLE") from exc
        if stat.S_ISLNK(metadata.st_mode):
            raise _BundleValidationError("IFIND_S2_BUNDLE_SYMLINK_REJECTED")


def _read_bounded_file(path: Path, *, maximum_bytes: int, failure_code: str) -> bytes:
    try:
        if path.stat().st_size > maximum_bytes:
            raise _BundleValidationError(failure_code)
        return path.read_bytes()
    except _BundleValidationError:
        raise
    except OSError as exc:
        raise _BundleValidationError(failure_code) from exc


def _parse_json_object(raw: bytes, *, failure_code: str) -> dict[str, Any]:
    try:
        parsed = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise _BundleValidationError(failure_code) from exc
    if not isinstance(parsed, dict):
        raise _BundleValidationError(failure_code)
    return parsed


def _unique_object(pairs: Sequence[Tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _reject_json_constant(_value: str) -> Any:
    raise ValueError("non-finite JSON numeric value")


def _normalized_date(value: Any) -> Optional[str]:
    if not isinstance(value, str):
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    return parsed.isoformat() if parsed.isoformat() == value else None


def _parse_normalized_timestamp(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    normalized = parsed.astimezone(timezone.utc)
    if normalized.isoformat().replace("+00:00", "Z") != value:
        return None
    return normalized


def _digest_json(value: Any) -> str:
    return _sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _safe_result(
    *,
    status: str,
    failure_code: Optional[str],
    bundle_id: Optional[str] = None,
    manifest_sha256: Optional[str] = None,
    artifact_count: int = 0,
    row_count: int = 0,
) -> Mapping[str, Any]:
    accepted = status == "PASS"
    return {
        "status": "PASS" if accepted else "BLOCKED",
        "mode": IFIND_S2_BUNDLE_MODE,
        "failure_code": None if accepted else failure_code,
        "bundle_id": bundle_id if accepted else None,
        "bundle_manifest_sha256": manifest_sha256 if accepted else None,
        "artifact_count": artifact_count if accepted else 0,
        "normalized_row_count": row_count if accepted else 0,
        "symbols": list(IFIND_DUAL_STOCK_SYMBOLS) if accepted else [],
        "modules": list(_MODULES) if accepted else [],
        "license_storage_class": IFIND_LICENSE_STORAGE_CLASS if accepted else None,
        "provider_schema_accepted": accepted,
        "canonical_accepted": accepted,
        "network_accessed": False,
        "keychain_accessed": False,
        "raw_payload_persisted": False,
        "credential_exposed": False,
    }

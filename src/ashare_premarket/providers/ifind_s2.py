from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence, Tuple

from ashare_premarket.providers.ifind_acceptance import (
    IFIND_DUAL_STOCK_IDENTITIES,
    IFIND_DUAL_STOCK_SYMBOLS,
    load_ifind_dual_stock_acceptance_config,
    _run_seven_service_handshake,
)
from ashare_premarket.data.trading_calendar import trading_calendar
from ashare_premarket.providers.ifind_http import IfindProviderError
from ashare_premarket.providers.ifind_mcp import (
    IFIND_MCP_S2_QUERY_TEMPLATES,
    IfindMcpCallScope,
    IfindMcpClient,
    IfindMcpNetworkPolicy,
)
from ashare_premarket.providers.ifind_normalization import (
    IfindNormalizedBatch,
    normalize_ifind_payload,
)
from ashare_premarket.storage.policy import resolve_data_root


IFIND_S2_STAGE_ID = "S2_SECURITY_MASTER_AND_DAILY_MARKET"
IFIND_S2_FIXED_TOOLS = ("get_stock_info", "get_stock_performance")
IFIND_S2_DATA_CALL_BUDGET = 4
IFIND_S2_DAILY_SESSION_COUNT = 120
IFIND_S2_ADJUSTMENT_MODE = "qfq"
IFIND_S2_PREFLIGHT_STATE = "S2_OFFLINE_FOUNDATION_READY_AUTHORIZATION_REQUIRED"
IFIND_S2_LOCAL_STATUS = "outputs/local/ifind/mcp_s2_status.json"
IFIND_S2_ACCEPTANCE_STATE = "S2_SECURITY_MASTER_AND_DAILY_MARKET_ACCEPTED"

_S2_QUERY_TEMPLATES = IFIND_MCP_S2_QUERY_TEMPLATES

_SECURITY_REQUIRED_COLUMNS = (
    "证券代码",
    "证券简称",
    "数据日期",
    "数据可用时间",
    "上市日期",
    "交易状态",
    "总股本",
    "流通股本",
)
_MARKET_REQUIRED_COLUMNS = (
    "证券代码",
    "证券简称",
    "交易日期",
    "开盘",
    "最高",
    "最低",
    "收盘",
    "成交量",
    "成交额",
    "换手率",
    "复权方式",
    "数据可用时间",
)


@dataclass(frozen=True)
class IfindS2Call:
    symbol: str
    company_name: str
    tool_name: str
    query: str
    expected_row_count: int

    def safe_summary(self) -> Mapping[str, Any]:
        return {
            "symbol": self.symbol,
            "tool_name": self.tool_name,
            "query_sha256": hashlib.sha256(self.query.encode("utf-8")).hexdigest(),
            "expected_row_count": self.expected_row_count,
        }


@dataclass(frozen=True)
class IfindS2Plan:
    calls: Tuple[IfindS2Call, ...]
    scope: IfindMcpCallScope
    cutoff_date: str

    def safe_summary(self) -> Mapping[str, Any]:
        return {
            "status": "PASS",
            "mode": "offline_stage_s2_preflight",
            "stage_id": IFIND_S2_STAGE_ID,
            "preflight_state": IFIND_S2_PREFLIGHT_STATE,
            "symbols": list(IFIND_DUAL_STOCK_SYMBOLS),
            "fixed_tools": list(IFIND_S2_FIXED_TOOLS),
            "data_call_budget": IFIND_S2_DATA_CALL_BUDGET,
            "retries_per_request": 0,
            "daily_session_count": IFIND_S2_DAILY_SESSION_COUNT,
            "adjustment_mode": IFIND_S2_ADJUSTMENT_MODE,
            "calls": [call.safe_summary() for call in self.calls],
            "separate_authorization_required": True,
            "data_calls_authorized": False,
            "network_accessed": False,
            "keychain_accessed": False,
            "data_tool_called": False,
            "raw_payload_persisted": False,
            "canonical_accepted": False,
        }


@dataclass(frozen=True)
class IfindS2LiveResult:
    safe_result: Mapping[str, Any]
    batches: Tuple[IfindNormalizedBatch, ...] = ()


S2ClientFactory = Callable[[IfindMcpNetworkPolicy, IfindMcpCallScope], IfindMcpClient]


def run_ifind_s2_live_acceptance(
    repository_root: Path,
    *,
    decision_timestamp: str,
    cutoff_date: str,
    s1_status: Mapping[str, Any],
    environ: Optional[Mapping[str, str]] = None,
    client_factory: Optional[S2ClientFactory] = None,
) -> IfindS2LiveResult:
    """Run same-client S0 plus at most four fixed S2 calls with zero retry."""

    plan = build_ifind_s2_offline_plan(
        repository_root, cutoff_date=cutoff_date, s1_status=s1_status
    )
    decision_cutoff = _validate_decision_timestamp(decision_timestamp)
    expected_dates = _expected_trade_dates(repository_root, plan.cutoff_date)
    source = environ if environ is not None else os.environ
    policy = IfindMcpNetworkPolicy.from_environment(source)
    policy.require_data_call_access()
    factory = client_factory or _keychain_s2_client_factory
    client = factory(policy, plan.scope)
    handshake = _run_seven_service_handshake(client)
    batches: list[IfindNormalizedBatch] = []
    summaries: list[dict[str, Any]] = []
    for call_index, call in enumerate(plan.calls, start=1):
        try:
            staged = client.call_s2_stock_tool(
                call.symbol, call.tool_name, plan.cutoff_date
            )
            if call.tool_name == "get_stock_info":
                batch = normalize_ifind_s2_security_master(
                    staged=staged,
                    symbol=call.symbol,
                    company_name=call.company_name,
                    decision_cutoff=decision_cutoff,
                )
            else:
                batch = normalize_ifind_s2_daily_market(
                    staged=staged,
                    symbol=call.symbol,
                    company_name=call.company_name,
                    decision_cutoff=decision_cutoff,
                    expected_trade_dates=expected_dates,
                )
        except IfindProviderError as exc:
            return IfindS2LiveResult(
                safe_result={
                    "status": "BLOCKED",
                    "mode": "live_stage_s2",
                    "stage_id": IFIND_S2_STAGE_ID,
                    "acceptance_state": "NOT_ACCEPTED",
                    "failure_code": exc.failure_code,
                    "http_status": exc.http_status,
                    "failed_symbol": call.symbol,
                    "failed_tool": call.tool_name,
                    "data_call_count": call_index,
                    "data_call_budget": IFIND_S2_DATA_CALL_BUDGET,
                    "retries_per_request": 0,
                    "live_handshake_verified": True,
                    "input_schemas_verified": True,
                    "normalized_batch_count": len(batches),
                    "normalized_row_count": sum(len(item.rows) for item in batches),
                    "raw_payload_persisted": False,
                    "canonical_accepted": False,
                }
            )
        batches.append(batch)
        summaries.append(
            {
                "symbol": call.symbol,
                "tool_name": call.tool_name,
                "module_id": batch.module_id,
                "row_count": len(batch.rows),
                "normalized_checksum": batch.normalized_checksum,
            }
        )
    return IfindS2LiveResult(
        safe_result={
            "status": "PASS",
            "mode": "live_stage_s2",
            "stage_id": IFIND_S2_STAGE_ID,
            "acceptance_state": IFIND_S2_ACCEPTANCE_STATE,
            "decision_timestamp": decision_cutoff,
            "cutoff_date": plan.cutoff_date,
            "data_call_count": len(plan.calls),
            "data_call_budget": IFIND_S2_DATA_CALL_BUDGET,
            "retries_per_request": 0,
            "service_count": len(handshake),
            "live_handshake_verified": True,
            "input_schemas_verified": True,
            "normalized_batch_count": len(batches),
            "normalized_row_count": sum(len(item.rows) for item in batches),
            "batch_summaries": summaries,
            "raw_payload_persisted": False,
            "provider_schema_accepted": True,
            "canonical_accepted": False,
        },
        batches=tuple(batches),
    )


def build_ifind_s2_offline_plan(
    repository_root: Path,
    *,
    cutoff_date: str,
    s1_status: Mapping[str, Any],
) -> IfindS2Plan:
    """Build the exact four-call S2 plan without creating a provider client."""

    config = load_ifind_dual_stock_acceptance_config(repository_root)
    _validate_s1_status(s1_status)
    stage = next(
        row
        for row in config.call_plan["stages"]
        if row["stage_id"] == IFIND_S2_STAGE_ID
    )
    if (
        tuple(stage.get("fixed_tools", ())) != IFIND_S2_FIXED_TOOLS
        or tuple(stage.get("fixed_symbols", ())) != IFIND_DUAL_STOCK_SYMBOLS
        or stage.get("data_call_budget") != IFIND_S2_DATA_CALL_BUDGET
        or stage.get("calls_per_tool_per_symbol") != 1
    ):
        raise _s2_contract_error()
    normalized_cutoff = _validate_cutoff_date(cutoff_date)
    names = {
        symbol: company for symbol, company, _exchange in IFIND_DUAL_STOCK_IDENTITIES
    }
    calls = tuple(
        IfindS2Call(
            symbol=symbol,
            company_name=names[symbol],
            tool_name=tool_name,
            query=_S2_QUERY_TEMPLATES[tool_name].format(
                symbol=symbol,
                company_name=names[symbol],
                cutoff_date=normalized_cutoff,
            ),
            expected_row_count=(
                1 if tool_name == "get_stock_info" else IFIND_S2_DAILY_SESSION_COUNT
            ),
        )
        for symbol in IFIND_DUAL_STOCK_SYMBOLS
        for tool_name in IFIND_S2_FIXED_TOOLS
    )
    if (
        len(calls) != IFIND_S2_DATA_CALL_BUDGET
        or len({(call.symbol, call.tool_name) for call in calls})
        != IFIND_S2_DATA_CALL_BUDGET
    ):
        raise _s2_contract_error()
    scope = IfindMcpCallScope(
        cohort_id=str(config.pilot["cohort_id"]),
        allowed_symbols=IFIND_DUAL_STOCK_SYMBOLS,
        company_names=tuple(
            (symbol, names[symbol]) for symbol in IFIND_DUAL_STOCK_SYMBOLS
        ),
        allowed_services=("stock",),
        allowed_tools=IFIND_S2_FIXED_TOOLS,
    )
    return IfindS2Plan(calls=calls, scope=scope, cutoff_date=normalized_cutoff)


def normalize_ifind_s2_security_master(
    *,
    staged: Mapping[str, Any],
    symbol: str,
    company_name: str,
    decision_cutoff: str,
) -> IfindNormalizedBatch:
    rows = _require_markdown_rows(staged, _SECURITY_REQUIRED_COLUMNS, exact_rows=1)
    row = rows[0]
    _validate_identity(row, symbol, company_name)
    provider_available_at = _required_text(row, "数据可用时间")
    table = _columnar_table(rows)
    mapping = {
        "证券代码": "symbol",
        "数据日期": "as_of_date",
        "上市日期": "listing_date",
        "证券简称": "entity_name",
        "交易状态": "trading_status",
        "总股本": "total_shares",
        "流通股本": "float_shares",
    }
    if "所属行业" in row:
        mapping["所属行业"] = "industry_name"
    return normalize_ifind_payload(
        module_id="security_master",
        payload={"tables": [table]},
        field_mapping=mapping,
        source_function="get_stock_info",
        available_at=provider_available_at,
        decision_cutoff=decision_cutoff,
        request_descriptor={
            "stage_id": IFIND_S2_STAGE_ID,
            "tool_name": "get_stock_info",
            "symbol": symbol,
        },
        quality_flags=("S2_TYPED_PROVIDER_SCHEMA",),
    )


def normalize_ifind_s2_daily_market(
    *,
    staged: Mapping[str, Any],
    symbol: str,
    company_name: str,
    decision_cutoff: str,
    expected_trade_dates: Sequence[str],
) -> IfindNormalizedBatch:
    expected_dates = tuple(str(value) for value in expected_trade_dates)
    if len(expected_dates) != IFIND_S2_DAILY_SESSION_COUNT or len(
        set(expected_dates)
    ) != len(expected_dates):
        raise IfindProviderError(
            "IFIND_MCP_S2_CALENDAR_INVALID",
            "S2 requires exactly 120 unique governed trading dates",
        )
    rows = _require_markdown_rows(
        staged, _MARKET_REQUIRED_COLUMNS, exact_rows=IFIND_S2_DAILY_SESSION_COUNT
    )
    for row in rows:
        _validate_identity(row, symbol, company_name)
        if _required_text(row, "复权方式").lower() not in {"前复权", "qfq"}:
            raise IfindProviderError(
                "IFIND_MCP_S2_ADJUSTMENT_MISMATCH",
                "S2 market rows must explicitly report qfq adjustment",
            )
        row["复权方式"] = IFIND_S2_ADJUSTMENT_MODE
    actual_dates = tuple(sorted(_required_text(row, "交易日期") for row in rows))
    if actual_dates != tuple(sorted(expected_dates)):
        raise IfindProviderError(
            "IFIND_MCP_S2_CALENDAR_MISMATCH",
            "S2 market rows do not exactly match the governed 120-session calendar",
        )
    available_values = {_required_text(row, "数据可用时间") for row in rows}
    if len(available_values) != 1:
        raise IfindProviderError(
            "IFIND_MCP_S2_AVAILABILITY_AMBIGUOUS",
            "S2 market batch requires one explicit provider availability timestamp",
        )
    return normalize_ifind_payload(
        module_id="daily_market_and_calendar",
        payload={"tables": [_columnar_table(rows)]},
        field_mapping={
            "证券代码": "symbol",
            "交易日期": "trade_date",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
            "成交额": "amount",
            "换手率": "turnover",
            "复权方式": "adjustment_mode",
        },
        source_function="get_stock_performance",
        available_at=next(iter(available_values)),
        decision_cutoff=decision_cutoff,
        request_descriptor={
            "stage_id": IFIND_S2_STAGE_ID,
            "tool_name": "get_stock_performance",
            "symbol": symbol,
            "session_count": IFIND_S2_DAILY_SESSION_COUNT,
            "adjustment_mode": IFIND_S2_ADJUSTMENT_MODE,
        },
        quality_flags=("S2_TYPED_PROVIDER_SCHEMA", "GOVERNED_CALENDAR_ALIGNED"),
    )


def write_ifind_s2_acceptance_bundle(
    repository_root: Path,
    result: IfindS2LiveResult,
    *,
    bundle_id: str,
) -> Path:
    """Atomically persist all four normalized batches outside the repository."""

    if (
        result.safe_result.get("status") != "PASS"
        or result.safe_result.get("acceptance_state") != IFIND_S2_ACCEPTANCE_STATE
        or len(result.batches) != IFIND_S2_DATA_CALL_BUDGET
        or not bundle_id
        or len(bundle_id) > 96
        or any(
            character not in "abcdefghijklmnopqrstuvwxyz0123456789-._"
            for character in bundle_id
        )
    ):
        raise IfindProviderError(
            "IFIND_MCP_S2_BUNDLE_INVALID",
            "S2 bundle requires one complete accepted four-batch result",
        )
    if not os.environ.get("ASHARE_PREMARKET_DATA_ROOT", "").strip():
        raise IfindProviderError(
            "IFIND_STORAGE_ROOT_ENV_REQUIRED",
            "S2 paid normalized data requires an explicit external data root",
        )
    root = Path(repository_root).resolve()
    data_root = resolve_data_root(root)
    if data_root == root or root in data_root.parents:
        raise IfindProviderError(
            "IFIND_STORAGE_POLICY_VIOLATION",
            "S2 paid normalized data root must remain outside the repository",
        )
    parent = data_root / "normalized" / "ifind" / "s2_acceptance"
    target = parent / bundle_id
    if target.exists():
        raise IfindProviderError(
            "IFIND_BUNDLE_IMMUTABLE", "S2 acceptance bundle already exists"
        )
    parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(parent, 0o700)
    temporary = Path(tempfile.mkdtemp(prefix=f".{bundle_id}.tmp-", dir=parent))
    try:
        artifacts = []
        for batch in result.batches:
            symbols = sorted({str(row.get("symbol")) for row in batch.rows})
            if len(symbols) != 1 or symbols[0] not in IFIND_DUAL_STOCK_SYMBOLS:
                raise IfindProviderError(
                    "IFIND_MCP_S2_BUNDLE_INVALID",
                    "S2 batch does not map to one fixed cohort symbol",
                )
            file_name = f"{batch.module_id}__{symbols[0].replace('.', '_')}.jsonl"
            path = temporary / file_name
            with path.open("w", encoding="utf-8", newline="\n") as handle:
                for row in batch.rows:
                    handle.write(
                        json.dumps(
                            row,
                            ensure_ascii=False,
                            sort_keys=True,
                            separators=(",", ":"),
                        )
                    )
                    handle.write("\n")
            os.chmod(path, 0o600)
            artifacts.append(
                {
                    "file": file_name,
                    "module_id": batch.module_id,
                    "symbol": symbols[0],
                    "row_count": len(batch.rows),
                    "normalized_checksum": batch.normalized_checksum,
                    "file_sha256": _sha256_file(path),
                }
            )
        manifest = {
            "bundle_id": bundle_id,
            "provider_id": "ifind",
            "stage_id": IFIND_S2_STAGE_ID,
            "acceptance_state": IFIND_S2_ACCEPTANCE_STATE,
            "license_storage_class": "paid_provider_local_only",
            "symbols": list(IFIND_DUAL_STOCK_SYMBOLS),
            "data_call_count": IFIND_S2_DATA_CALL_BUDGET,
            "retries_per_request": 0,
            "decision_timestamp": result.safe_result.get("decision_timestamp"),
            "cutoff_date": result.safe_result.get("cutoff_date"),
            "raw_payload_persisted": False,
            "credentials_persisted": False,
            "artifacts": artifacts,
        }
        manifest_path = temporary / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.chmod(manifest_path, 0o600)
        temporary.rename(target)
        return target / "manifest.json"
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def write_ifind_s2_status(repository_root: Path, payload: Mapping[str, Any]) -> Path:
    target = Path(repository_root).resolve() / IFIND_S2_LOCAL_STATUS
    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(target.parent, 0o700)
    safe = _sanitize_s2_status(
        {
            **payload,
            "observed_at": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }
    )
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(safe, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.chmod(temporary, 0o600)
    os.replace(temporary, target)
    os.chmod(target, 0o600)
    return target


def read_ifind_s2_status(repository_root: Path) -> Mapping[str, Any]:
    target = Path(repository_root).resolve() / IFIND_S2_LOCAL_STATUS
    try:
        raw = target.read_bytes()
        if len(raw) > 64 * 1024:
            raise ValueError("oversized")
        parsed = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return _sanitize_s2_status({"status": "NOT_RUN"})
    if not isinstance(parsed, Mapping):
        return _sanitize_s2_status({"status": "INVALID_LOCAL_STATUS"})
    return _sanitize_s2_status(parsed)


def _sanitize_s2_status(value: Mapping[str, Any]) -> Mapping[str, Any]:
    status = str(value.get("status", "INVALID_LOCAL_STATUS"))
    if status not in {"PASS", "BLOCKED", "NOT_RUN", "INVALID_LOCAL_STATUS"}:
        status = "INVALID_LOCAL_STATUS"
    acceptance_state = (
        IFIND_S2_ACCEPTANCE_STATE
        if status == "PASS"
        and value.get("acceptance_state") == IFIND_S2_ACCEPTANCE_STATE
        else "NOT_ACCEPTED"
    )
    count = value.get("data_call_count")
    if isinstance(count, bool) or not isinstance(count, int) or not 0 <= count <= 4:
        count = 0
    row_count = value.get("normalized_row_count")
    if (
        isinstance(row_count, bool)
        or not isinstance(row_count, int)
        or not 0 <= row_count <= 242
    ):
        row_count = 0
    failure_code = value.get("failure_code")
    if not isinstance(failure_code, str) or not failure_code.startswith("IFIND_"):
        failure_code = None
    failed_symbol = value.get("failed_symbol")
    if failed_symbol not in IFIND_DUAL_STOCK_SYMBOLS:
        failed_symbol = None
    failed_tool = value.get("failed_tool")
    if failed_tool not in IFIND_S2_FIXED_TOOLS:
        failed_tool = None
    bundle_id = value.get("bundle_id")
    if not isinstance(bundle_id, str) or len(bundle_id) > 96:
        bundle_id = None
    accepted = (
        status == "PASS"
        and acceptance_state == IFIND_S2_ACCEPTANCE_STATE
        and count == 4
        and row_count == 242
        and value.get("bundle_persisted") is True
        and bundle_id is not None
    )
    return {
        "status": status,
        "mode": "live_stage_s2" if status in {"PASS", "BLOCKED"} else "none",
        "acceptance_state": acceptance_state,
        "failure_code": None if status == "PASS" else failure_code,
        "failed_symbol": None if status == "PASS" else failed_symbol,
        "failed_tool": None if status == "PASS" else failed_tool,
        "data_call_count": count,
        "data_call_budget": IFIND_S2_DATA_CALL_BUDGET,
        "retries_per_request": 0,
        "normalized_row_count": row_count,
        "bundle_id": bundle_id if accepted else None,
        "bundle_persisted": accepted,
        "live_handshake_verified": value.get("live_handshake_verified") is True,
        "input_schemas_verified": value.get("input_schemas_verified") is True,
        "provider_schema_accepted": accepted,
        "canonical_accepted": accepted,
        "observed_at": (
            value.get("observed_at")
            if isinstance(value.get("observed_at"), str)
            else None
        ),
        "credential_exposed": False,
        "raw_payload_persisted": False,
    }


def _validate_s1_status(status: Mapping[str, Any]) -> None:
    required = {
        "status": "PASS",
        "mode": "live_stage_s1",
        "acceptance_state": "S1_IDENTITY_ACCEPTANCE_METADATA_VERIFIED",
        "data_call_count": 2,
        "staged_symbol_count": 2,
        "live_handshake_verified": True,
        "input_schemas_verified": True,
        "data_tool_called": True,
        "s1_identity_acceptance_verified": True,
        "s2_requires_separate_authorization": True,
        "canonical_accepted": False,
    }
    if any(status.get(key) != value for key, value in required.items()):
        raise IfindProviderError(
            "IFIND_MCP_S2_PREREQUISITE_UNVERIFIED",
            "S2 requires the exact accepted non-canonical S1 status",
        )


def _require_markdown_rows(
    staged: Mapping[str, Any],
    required_columns: Sequence[str],
    *,
    exact_rows: int,
) -> list[dict[str, Any]]:
    if (
        staged.get("canonical_accepted") is not False
        or staged.get("staging_format") != "provider_markdown_tables_v1"
    ):
        raise IfindProviderError(
            "IFIND_MCP_S2_RESPONSE_SCHEMA_MISMATCH",
            "S2 accepts only bounded non-canonical provider Markdown staging",
        )
    tables = staged.get("tables")
    if not isinstance(tables, list):
        raise IfindProviderError(
            "IFIND_MCP_S2_RESPONSE_SCHEMA_MISMATCH", "S2 tables are missing"
        )
    matches = []
    required = set(required_columns)
    for table in tables:
        if not isinstance(table, Mapping) or not isinstance(table.get("columns"), list):
            continue
        columns = tuple(str(value) for value in table["columns"])
        if required.issubset(columns):
            matches.append(table)
    if len(matches) != 1 or not isinstance(matches[0].get("rows"), list):
        raise IfindProviderError(
            "IFIND_MCP_S2_RESPONSE_SCHEMA_MISMATCH",
            "S2 response must contain exactly one reviewed table",
        )
    rows = matches[0]["rows"]
    if len(rows) != exact_rows or any(not isinstance(row, Mapping) for row in rows):
        raise IfindProviderError(
            "IFIND_MCP_S2_ROW_COUNT_MISMATCH",
            "S2 response row count does not match the fixed request contract",
        )
    return [dict(row) for row in rows]


def _validate_identity(row: Mapping[str, Any], symbol: str, company_name: str) -> None:
    if symbol not in IFIND_DUAL_STOCK_SYMBOLS:
        raise IfindProviderError(
            "IFIND_MCP_DATA_SCOPE_VIOLATION", "S2 symbol is outside the fixed cohort"
        )
    if (
        _required_text(row, "证券代码").upper() != symbol
        or _required_text(row, "证券简称") != company_name
    ):
        raise IfindProviderError(
            "IFIND_MCP_S2_IDENTITY_MISMATCH",
            "S2 provider identity does not match the fixed symbol and company",
        )


def _required_text(row: Mapping[str, Any], field: str) -> str:
    value = row.get(field)
    if not isinstance(value, (str, int, float)) or isinstance(value, bool):
        raise IfindProviderError(
            "IFIND_MCP_S2_RESPONSE_SCHEMA_MISMATCH",
            f"S2 field {field} must be a scalar value",
        )
    text = str(value).strip()
    if not text:
        raise IfindProviderError(
            "IFIND_MCP_S2_RESPONSE_SCHEMA_MISMATCH",
            f"S2 field {field} must not be empty",
        )
    return text


def _columnar_table(rows: Sequence[Mapping[str, Any]]) -> Mapping[str, list[Any]]:
    columns = tuple(str(key) for key in rows[0])
    if any(tuple(str(key) for key in row) != columns for row in rows):
        raise IfindProviderError(
            "IFIND_MCP_S2_RESPONSE_SCHEMA_MISMATCH",
            "S2 rows must expose one stable column order and schema",
        )
    return {column: [row.get(column) for row in rows] for column in columns}


def _validate_cutoff_date(value: str) -> str:
    text = str(value).strip()
    parts = text.split("-")
    if len(parts) != 3 or tuple(len(part) for part in parts) != (4, 2, 2):
        raise IfindProviderError(
            "IFIND_MCP_S2_CUTOFF_INVALID", "S2 cutoff must use YYYY-MM-DD"
        )
    try:
        year, month, day = (int(part) for part in parts)
        return date(year, month, day).isoformat()
    except ValueError as exc:
        raise IfindProviderError(
            "IFIND_MCP_S2_CUTOFF_INVALID", "S2 cutoff is not a calendar date"
        ) from exc


def _validate_decision_timestamp(value: str) -> str:
    text = str(value).strip()
    if not text or ("+" not in text[10:] and not text.endswith("Z")):
        raise IfindProviderError(
            "IFIND_MCP_DECISION_TIMESTAMP_INVALID",
            "S2 decision timestamp must include an explicit timezone",
        )
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise IfindProviderError(
            "IFIND_MCP_DECISION_TIMESTAMP_INVALID",
            "S2 decision timestamp is not valid ISO-8601",
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise IfindProviderError(
            "IFIND_MCP_DECISION_TIMESTAMP_INVALID",
            "S2 decision timestamp must include an explicit timezone",
        )
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _expected_trade_dates(repository_root: Path, cutoff_date: str) -> Tuple[str, ...]:
    cutoff = _validate_cutoff_date(cutoff_date)
    try:
        rows = trading_calendar(Path(repository_root).resolve())
    except (OSError, ValueError) as exc:
        raise IfindProviderError(
            "IFIND_MCP_S2_CALENDAR_INVALID",
            "S2 governed trading calendar is unavailable or invalid",
        ) from exc
    dates = tuple(
        row["date"]
        for row in rows
        if row.get("is_trading_day") == "true" and row.get("date", "") <= cutoff
    )[-IFIND_S2_DAILY_SESSION_COUNT:]
    if len(dates) != IFIND_S2_DAILY_SESSION_COUNT or dates[-1] != cutoff:
        raise IfindProviderError(
            "IFIND_MCP_S2_CALENDAR_INVALID",
            "S2 cutoff must be the latest governed session in an exact 120-day window",
        )
    return dates


def _keychain_s2_client_factory(
    policy: IfindMcpNetworkPolicy, scope: IfindMcpCallScope
) -> IfindMcpClient:
    return IfindMcpClient.from_keychain(policy=policy, call_scope=scope)


def s2_bundle_id(result: IfindS2LiveResult) -> str:
    if result.safe_result.get("status") != "PASS" or not result.batches:
        raise IfindProviderError(
            "IFIND_MCP_S2_BUNDLE_INVALID", "S2 bundle id requires an accepted result"
        )
    cutoff = str(result.safe_result.get("cutoff_date", "")).replace("-", "")
    digest = hashlib.sha256(
        "|".join(batch.normalized_checksum for batch in result.batches).encode("utf-8")
    ).hexdigest()[:16]
    return f"s2-{cutoff}-{digest}"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _s2_contract_error() -> IfindProviderError:
    return IfindProviderError(
        "IFIND_MCP_S2_CONTRACT_INVALID",
        "committed S2 call-plan fields are inconsistent",
    )

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass


AKSHARE_NETWORK_ENV = "ASHARE_ALLOW_AKSHARE_NETWORK"
VALID_RUN_MODES = {"offline_dry_run", "live_bounded_fetch", "committed_evidence_replay"}


@dataclass(frozen=True)
class SourceReplayStats:
    source_id: str
    artifact_name: str
    row_count: int
    column_count: int
    date_min: str
    date_max: str
    schema_fields: tuple[str, ...]
    status: str = "committed_evidence_replay_available"


def akshare_network_enabled() -> bool:
    return os.environ.get(AKSHARE_NETWORK_ENV, "") in {"1", "true", "TRUE", "yes", "YES"}


def resolve_run_mode(requested_mode: str | None = None) -> str:
    if requested_mode:
        if requested_mode not in VALID_RUN_MODES:
            raise ValueError(f"invalid run_mode:{requested_mode}")
        if requested_mode == "live_bounded_fetch" and not akshare_network_enabled():
            return "offline_dry_run"
        return requested_mode
    return "live_bounded_fetch" if akshare_network_enabled() else "offline_dry_run"


def schema_hash(fields: list[str] | tuple[str, ...]) -> str:
    digest = hashlib.sha256(",".join(fields).encode("utf-8")).hexdigest()
    return digest[:16]


def provider_health_rows(
    selected_sources: list[dict[str, str]],
    run_mode: str,
    replay_stats: dict[str, SourceReplayStats],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    network_enabled = akshare_network_enabled() and run_mode == "live_bounded_fetch"
    for source in selected_sources:
        if source.get("selected_for_goal") != "true":
            continue
        source_id = source["source_id"]
        stats = replay_stats.get(source_id)
        if stats:
            fetch_status = stats.status
            row_count = stats.row_count
            column_count = stats.column_count
            date_min = stats.date_min
            date_max = stats.date_max
            sample_schema_hash = schema_hash(stats.schema_fields)
            health_status = "PASS_WITH_WARNINGS"
            warning = "committed_evidence_replay_no_live_fetch"
            notes = f"replayed_from:{stats.artifact_name}"
        else:
            fetch_status = "fetch_unavailable_network_disabled" if not network_enabled else "fetch_unavailable_provider_error"
            row_count = 0
            column_count = 0
            date_min = ""
            date_max = ""
            sample_schema_hash = ""
            health_status = "WARN"
            warning = fetch_status
            notes = "source_selected_but_no_committed_bounded_artifact_available"
        rows.append(
            {
                "provider_name": "akshare",
                "source_id": source_id,
                "run_mode": run_mode,
                "network_enabled": network_enabled,
                "fetch_attempted": network_enabled,
                "fetch_status": fetch_status,
                "error_class": "" if stats else ("network_disabled" if not network_enabled else "provider_error"),
                "row_count": row_count,
                "column_count": column_count,
                "date_min": date_min,
                "date_max": date_max,
                "sample_schema_hash": sample_schema_hash,
                "provider_latency_ms": 0,
                "provider_warning": warning,
                "health_status": health_status,
                "notes": notes,
            }
        )
    return rows


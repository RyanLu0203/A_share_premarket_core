from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderSourceContract:
    source_id: str
    provider_id: str
    expected_grain: str
    expected_time_field: str
    expected_primary_keys: tuple[str, ...]
    approved_usage: str
    priority_band: str
    storage_policy: str
    commit_policy: str


@dataclass(frozen=True)
class ProviderRegistryEntry:
    provider_id: str
    provider_name: str
    current_role: str
    planned_role: str
    provider_priority: str
    network_opt_in_policy: str
    offline_replay_policy: str
    raw_data_commit_policy: str

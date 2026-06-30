from __future__ import annotations

from ashare_premarket.providers.registry import REGISTRY_FIELDS, provider_registry_config, provider_registry_rows


def test_provider_registry_contains_required_policies() -> None:
    rows = provider_registry_rows()
    providers = {row["provider_id"]: row for row in rows}
    assert {"baostock", "akshare", "local_import"}.issubset(providers)
    assert list(rows[0]) == REGISTRY_FIELDS
    assert providers["baostock"]["current_role"].startswith("committed_provider02b")
    assert providers["akshare"]["network_opt_in_policy"].startswith("network_disabled_by_default")
    assert all(row["raw_data_commit_policy"] != "" for row in rows)
    assert all(row["forbidden_production_write_policy"] == "production_db_writes_forbidden" for row in rows)
    assert provider_registry_config()["network_default"] == "disabled"


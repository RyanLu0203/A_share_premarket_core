from __future__ import annotations

from pathlib import Path

from ashare_premarket.providers.tencent_operational_audit import audit_tencent_primary_operational_contract


ROOT = Path(__file__).resolve().parents[1]


def test_tencent_primary_operational_contract_audit_passes() -> None:
    result = audit_tencent_primary_operational_contract(ROOT)
    assert result["status"] == "PASS"
    assert all(result["checks"].values())
    assert all(item["status"] == "PASS" for item in result["amount_consumer_inventory"])
    assert result["independent_verification"]["canonical_row_contribution_count"] == 0
    assert result["deployment_performed"] is False
    assert result["services_started"] is False

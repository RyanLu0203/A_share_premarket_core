from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.core.io import write_json
from ashare_premarket.providers.tencent_operational_audit import audit_tencent_primary_operational_contract


if __name__ == "__main__":
    result = audit_tencent_primary_operational_contract(ROOT)
    write_json(ROOT / "outputs/audits/tencent_primary_operational_hardening_audit.json", result)
    print(f"Tencent primary operational audit: {result['status']}")
    raise SystemExit(0 if result["status"] == "PASS" else 1)

from __future__ import annotations

import json

from _bootstrap import ROOT
from ashare_premarket.quant_foundation.audit import audit_goal11_foundation


if __name__ == "__main__":
    result = audit_goal11_foundation(ROOT)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 1)

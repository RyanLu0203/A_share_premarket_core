from __future__ import annotations

import json

from _bootstrap import ROOT
from ashare_premarket.alpha_validation.audit import audit_goal12_framework


if __name__ == "__main__":
    result = audit_goal12_framework(ROOT)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 1)

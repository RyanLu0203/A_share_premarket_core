from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.risk_design.goal07a import audit_goal07a_risk_rule_catalog


if __name__ == "__main__":
    raise SystemExit(0 if audit_goal07a_risk_rule_catalog(ROOT) else 1)

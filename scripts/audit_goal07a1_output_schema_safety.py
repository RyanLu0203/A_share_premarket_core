from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.risk_design.goal07a1 import audit_goal07a1_output_schema_safety


if __name__ == "__main__":
    raise SystemExit(0 if audit_goal07a1_output_schema_safety(ROOT) else 1)

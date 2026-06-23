from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.risk_design.goal07a import audit_goal07a_output_schema


if __name__ == "__main__":
    raise SystemExit(0 if audit_goal07a_output_schema(ROOT) else 1)

from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.risk_design.goal07a import run_goal07a_risk_overlay_design_gate


if __name__ == "__main__":
    raise SystemExit(0 if run_goal07a_risk_overlay_design_gate(ROOT) else 1)

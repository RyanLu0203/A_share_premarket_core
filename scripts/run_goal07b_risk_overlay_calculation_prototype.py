from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.risk_overlay.goal07b import run_goal07b_risk_overlay_calculation_prototype


if __name__ == "__main__":
    raise SystemExit(0 if run_goal07b_risk_overlay_calculation_prototype(ROOT) else 1)

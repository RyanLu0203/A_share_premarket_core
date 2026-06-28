from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ashare_premarket.risk_tiering.goal_risk_tiering011 import run_goal_risk_tiering011_downside_risk_repair_gate


if __name__ == "__main__":
    raise SystemExit(0 if run_goal_risk_tiering011_downside_risk_repair_gate(Path(__file__).resolve().parents[1]) else 1)

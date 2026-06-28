from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ashare_premarket.research.goal_quant_research01 import run_goal_quant_research01_factor_research_lab_gate


if __name__ == "__main__":
    raise SystemExit(0 if run_goal_quant_research01_factor_research_lab_gate(Path(__file__).resolve().parents[1]) else 1)

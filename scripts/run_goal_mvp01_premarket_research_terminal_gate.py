from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ashare_premarket.mvp.goal_mvp01 import run_goal_mvp01_premarket_research_terminal_gate


if __name__ == "__main__":
    raise SystemExit(0 if run_goal_mvp01_premarket_research_terminal_gate(Path(__file__).resolve().parents[1]) else 1)

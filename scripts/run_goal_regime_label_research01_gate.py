from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ashare_premarket.research.goal_regime_label_research01 import run_goal_regime_label_research01_gate


if __name__ == "__main__":
    raise SystemExit(0 if run_goal_regime_label_research01_gate(Path(__file__).resolve().parents[1]) else 1)

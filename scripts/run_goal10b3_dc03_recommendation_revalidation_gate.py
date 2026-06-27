from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ashare_premarket.backtest.goal10b3 import run_goal10b3_dc03_recommendation_revalidation_gate


if __name__ == "__main__":
    raise SystemExit(0 if run_goal10b3_dc03_recommendation_revalidation_gate(Path(__file__).resolve().parents[1]) else 1)

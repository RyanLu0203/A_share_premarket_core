from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ashare_premarket.backtest.goal10b2 import run_goal10b2_recommendation_backtest_revalidation


if __name__ == "__main__":
    raise SystemExit(0 if run_goal10b2_recommendation_backtest_revalidation(Path(__file__).resolve().parents[1]) else 1)

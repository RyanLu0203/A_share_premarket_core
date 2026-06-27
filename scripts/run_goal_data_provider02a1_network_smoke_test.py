from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ashare_premarket.providers.goal_data_provider02a1 import run_goal_data_provider02a1_network_smoke_test


if __name__ == "__main__":
    raise SystemExit(0 if run_goal_data_provider02a1_network_smoke_test(Path(__file__).resolve().parents[1]) else 1)

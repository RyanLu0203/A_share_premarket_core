from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ashare_premarket.backtest.goal10c import audit_goal10c_cost_slippage_sensitivity_gate


if __name__ == "__main__":
    raise SystemExit(0 if audit_goal10c_cost_slippage_sensitivity_gate(Path(__file__).resolve().parents[1]) else 1)

from __future__ import annotations

import sys
from _bootstrap import ROOT
from ashare_premarket.backtest.goal10b1 import audit_goal10b1_backtest_coverage_repair_gate


if __name__ == "__main__":
    sys.exit(0 if audit_goal10b1_backtest_coverage_repair_gate(ROOT) else 1)

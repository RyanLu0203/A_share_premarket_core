from __future__ import annotations

import argparse

from _bootstrap import ROOT
from ashare_premarket.portfolio_risk.goal_premarket_position_management_operational01 import (
    run_goal_premarket_position_management_operational01,
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run daily premarket position-management checks.")
    parser.add_argument("--execution-time", help="Explicit Asia/Shanghai execution timestamp for operational testing.")
    parser.add_argument("--target-trading-date", help="Explicit governed target trading date.")
    parser.add_argument("--replay-date", help="Explicit deterministic replay target trading date.")
    args = parser.parse_args()
    raise SystemExit(
        0
        if run_goal_premarket_position_management_operational01(
            ROOT,
            print_summary=True,
            execution_time=args.execution_time,
            target_trading_date=args.target_trading_date,
            replay_date=args.replay_date,
        )
        else 1
    )

from __future__ import annotations

import argparse

from _bootstrap import ROOT
from ashare_premarket.portfolio_risk.goal_premarket_position_management_operational01 import (
    DEFAULT_REPLAY_TARGET_TRADING_DATE,
    run_goal_premarket_position_management_operational01,
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run deterministic OPM01 review artifacts.")
    parser.add_argument("--replay-date")
    parser.add_argument("--execution-time")
    parser.add_argument("--target-trading-date")
    args = parser.parse_args()
    replay_date = args.replay_date
    if replay_date is None and not args.execution_time and not args.target_trading_date:
        replay_date = DEFAULT_REPLAY_TARGET_TRADING_DATE
    raise SystemExit(
        0
        if run_goal_premarket_position_management_operational01(
            ROOT,
            execution_time=args.execution_time,
            target_trading_date=args.target_trading_date,
            replay_date=replay_date,
        )
        else 1
    )

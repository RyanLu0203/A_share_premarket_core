from __future__ import annotations

import argparse
import os

from _bootstrap import ROOT
from ashare_premarket.daily_refresh.goal_daily_incremental_evidence_refresh01 import (
    run_goal_daily_incremental_evidence_refresh01,
)
from ashare_premarket.data.runtime_calendar import RUNTIME_CALENDAR, sync_runtime_trading_calendar
from ashare_premarket.ops.macos_launchd import already_refreshed
from ashare_premarket.portfolio_risk.goal_premarket_position_management_operational01 import resolve_run_context


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync the source-backed runtime calendar and run one bounded T-1 refresh.")
    parser.add_argument("--allow-network", action="store_true", help="Required explicit provider-network authorization.")
    args = parser.parse_args()
    if not args.allow_network:
        parser.error("--allow-network is required")
    os.environ["ASHARE_ALLOW_NETWORK_INGESTION"] = "1"
    os.environ["ASHARE_TRADING_CALENDAR_PATH"] = RUNTIME_CALENDAR
    calendar = sync_runtime_trading_calendar(ROOT, allow_network=True)
    print(f"runtime trading calendar: {calendar.relative_to(ROOT)}")
    context = resolve_run_context(ROOT)
    if already_refreshed(ROOT, context):
        print(
            "Daily evidence refresh: ALREADY_SUCCEEDED | "
            f"target={context['target_trading_date']} | "
            f"expected_t_minus_one={context['expected_previous_trading_date']}"
        )
        return 0
    passed = run_goal_daily_incremental_evidence_refresh01(
        ROOT,
        print_summary=True,
        replay_date=None,
        allow_network=True,
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

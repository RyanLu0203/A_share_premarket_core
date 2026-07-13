from __future__ import annotations

import argparse
import os

from _bootstrap import ROOT
from ashare_premarket.data.runtime_calendar import RUNTIME_CALENDAR, sync_runtime_trading_calendar
from ashare_premarket.data.trading_calendar import previous_trading_day
from ashare_premarket.ops.observation_basket import refresh_observation_basket
from ashare_premarket.portfolio_risk.goal_premarket_position_management_operational01 import resolve_run_context


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh bounded, observation-only T-1 evidence for selected symbols.")
    parser.add_argument("--symbols", nargs="+", required=True)
    parser.add_argument("--allow-network", action="store_true")
    args = parser.parse_args()
    if not args.allow_network:
        parser.error("--allow-network is required")
    os.environ["ASHARE_ALLOW_NETWORK_INGESTION"] = "1"
    os.environ["ASHARE_TRADING_CALENDAR_PATH"] = RUNTIME_CALENDAR
    sync_runtime_trading_calendar(ROOT, allow_network=True)
    context = resolve_run_context(ROOT)
    expected = context["expected_previous_trading_date"]
    payload = refresh_observation_basket(
        ROOT,
        args.symbols,
        previous_trading_day(ROOT, expected),
        expected,
        allow_network=True,
    )
    for row in payload["rows"]:
        print(row)
    return 0 if all(row["observation_status"] == "AVAILABLE" for row in payload["rows"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())

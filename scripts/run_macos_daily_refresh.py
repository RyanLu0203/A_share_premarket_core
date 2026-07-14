from __future__ import annotations

import argparse
import importlib.util
import os
import platform

from _bootstrap import ROOT
from ashare_premarket.daily_refresh.goal_daily_incremental_evidence_refresh01 import (
    resolve_daily_refresh_context,
    run_goal_daily_incremental_evidence_refresh01,
)
from ashare_premarket.data.runtime_calendar import runtime_calendar_environment, sync_runtime_trading_calendar
from ashare_premarket.ops.macos_launchd import already_refreshed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync approved calendar evidence, refresh bounded T-1 evidence, and write one research-only OPM snapshot."
    )
    parser.add_argument("--allow-network", action="store_true", help="Required explicit provider-network authorization.")
    parser.add_argument("--check", action="store_true", help="Check runner prerequisites without network access or writes.")
    args = parser.parse_args()
    if args.check:
        required = [ROOT / ".venv/bin/python", ROOT / "configs/project/trading_calendar.csv"]
        passed = (
            platform.system() == "Darwin"
            and all(path.exists() for path in required)
            and importlib.util.find_spec("akshare") is not None
        )
        print(f"macOS daily refresh check: {'PASS' if passed else 'BLOCKED'}")
        return 0 if passed else 1
    if not args.allow_network:
        parser.error("--allow-network is required")

    os.environ["ASHARE_ALLOW_NETWORK_INGESTION"] = "1"
    os.environ.update(runtime_calendar_environment(ROOT))
    calendar = sync_runtime_trading_calendar(ROOT, allow_network=True)
    context = resolve_daily_refresh_context(ROOT)
    if context.get("calendar_status") != "PASS":
        print(f"Daily evidence refresh: BLOCKED | reason={context.get('calendar_reason')}")
        return 1
    print(
        "runtime trading calendar: "
        f"{calendar.relative_to(ROOT)} | source={context['calendar_source']} | "
        f"coverage_end={context['calendar_coverage_end']} | freshness={context['calendar_freshness_status']}"
    )
    if already_refreshed(ROOT, context):
        print(
            "Daily evidence refresh: ALREADY_SUCCEEDED | "
            f"target={context['target_trading_date']} | "
            f"expected_t_minus_one={context['expected_previous_trading_date']}"
        )
        return 0
    passed = run_goal_daily_incremental_evidence_refresh01(ROOT, print_summary=True, allow_network=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

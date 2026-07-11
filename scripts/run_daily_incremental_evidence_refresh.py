from __future__ import annotations

import argparse

from _bootstrap import ROOT
from ashare_premarket.daily_refresh.goal_daily_incremental_evidence_refresh01 import (
    run_goal_daily_incremental_evidence_refresh01,
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the controlled daily T-1 research evidence refresh.")
    parser.add_argument("--execution-time", help="Explicit Asia/Shanghai execution timestamp.")
    parser.add_argument("--target-trading-date", help="Explicit governed target trading date.")
    parser.add_argument("--replay-date", help="Explicit deterministic replay target date.")
    parser.add_argument("--evidence-file", help="Bounded normalized incremental evidence CSV.")
    parser.add_argument("--expected-checksum", help="Expected SHA-256 for the supplied evidence source.")
    parser.add_argument("--allow-network", action="store_true", help="Explicitly opt into the existing bounded provider adapter.")
    args = parser.parse_args()
    raise SystemExit(
        0
        if run_goal_daily_incremental_evidence_refresh01(
            ROOT,
            print_summary=True,
            execution_time=args.execution_time,
            target_trading_date=args.target_trading_date,
            replay_date=args.replay_date,
            evidence_file=args.evidence_file,
            expected_checksum=args.expected_checksum,
            allow_network=args.allow_network,
        )
        else 1
    )

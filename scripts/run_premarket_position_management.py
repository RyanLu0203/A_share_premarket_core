from __future__ import annotations

import argparse
import json

from _bootstrap import ROOT
from ashare_premarket.portfolio_risk.goal_premarket_position_management_operational01 import (
    run_goal_premarket_position_management_operational01,
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run daily premarket position-management checks.")
    parser.add_argument("--execution-time", help="Explicit Asia/Shanghai execution timestamp for operational testing.")
    parser.add_argument("--target-trading-date", help="Explicit governed target trading date.")
    parser.add_argument("--replay-date", help="Explicit deterministic replay target trading date.")
    parser.add_argument("--canonical-evidence-path", help="Validated repository-local canonical evidence CSV.")
    parser.add_argument("--refresh-manifest-path", help="Validated repository-local daily refresh manifest JSON.")
    args = parser.parse_args()
    refresh_metadata = None
    if args.refresh_manifest_path:
        manifest_path = (ROOT / args.refresh_manifest_path).resolve()
        if ROOT.resolve() not in manifest_path.parents:
            parser.error("refresh manifest path must remain inside repository root")
        refresh_metadata = json.loads(manifest_path.read_text(encoding="utf-8"))
    raise SystemExit(
        0
        if run_goal_premarket_position_management_operational01(
            ROOT,
            print_summary=True,
            execution_time=args.execution_time,
            target_trading_date=args.target_trading_date,
            replay_date=args.replay_date,
            canonical_evidence_path=args.canonical_evidence_path,
            refresh_metadata=refresh_metadata,
        )
        else 1
    )

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from _bootstrap import ROOT
from ashare_premarket.core.io import write_json
from ashare_premarket.providers.governed_stock_history import run_east_money_probe


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the disabled-by-default East Money probe-only health check.")
    parser.add_argument("--trade-date", required=True, help="Expected governed T-1 date (YYYY-MM-DD).")
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=["600036.SH", "000002.SZ", "300015.SZ", "920002.BJ"],
        help="At most four representative canonical symbols.",
    )
    parser.add_argument("--allow-network", action="store_true", help="Explicit authorization for this separate probe.")
    args = parser.parse_args()
    if not args.allow_network:
        parser.error("--allow-network is required; the East Money probe is disabled by default")
    report = run_east_money_probe(ROOT, set(args.symbols), args.trade_date, True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = ROOT / "outputs/local/runtime/east_money_probe" / f"{stamp}.json"
    write_json(path, report)
    print(f"East Money probe: {report['health_status']} | report={path}")

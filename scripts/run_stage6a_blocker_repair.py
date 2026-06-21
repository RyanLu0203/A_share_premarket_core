from __future__ import annotations

import argparse

from _bootstrap import ROOT
from ashare_premarket.scoring.baseline import run_stage6a_blocker_repair


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-network", action="store_true")
    args = parser.parse_args()
    run_stage6a_blocker_repair(ROOT, no_network=args.no_network)

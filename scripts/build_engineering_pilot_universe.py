from __future__ import annotations

import argparse

from _bootstrap import ROOT
from ashare_premarket.providers.ingestion import build_engineering_pilot_universe


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the GOAL-06C.6 engineering pilot universe sample.")
    parser.add_argument("--allow-network", action="store_true", help="Allow provider network calls for this run.")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    build_engineering_pilot_universe(ROOT, allow_network=args.allow_network)

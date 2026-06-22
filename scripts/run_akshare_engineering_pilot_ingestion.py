from __future__ import annotations

import argparse

from _bootstrap import ROOT
from ashare_premarket.providers.ingestion import build_source_backed_local_bundle


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run AKShare source-backed engineering pilot ingestion.")
    parser.add_argument("--allow-network", action="store_true", help="Allow provider network calls for this run.")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    raise SystemExit(0 if build_source_backed_local_bundle(ROOT, allow_network=args.allow_network) else 1)

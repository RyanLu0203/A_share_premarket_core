from __future__ import annotations

import argparse

from _bootstrap import ROOT
from ashare_premarket.providers.ingestion import run_goal06c6_source_backed_engineering_pilot_bundle
from ashare_premarket.storage.policy import audit_storage_policy


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the GOAL-06C.6 source-backed engineering pilot bundle gate.")
    parser.add_argument("--allow-network", action="store_true", help="Allow provider network calls for this run.")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    ok = audit_storage_policy(ROOT)
    ok = run_goal06c6_source_backed_engineering_pilot_bundle(ROOT, allow_network=args.allow_network) and ok
    raise SystemExit(0 if ok else 1)

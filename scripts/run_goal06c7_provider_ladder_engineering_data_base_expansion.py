from __future__ import annotations

import argparse

from _bootstrap import ROOT
from ashare_premarket.providers.provider_ladder import run_goal06c7_provider_ladder_expansion
from ashare_premarket.storage.policy import audit_storage_policy


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the GOAL-06C.7 provider-ladder engineering data base expansion gate.")
    parser.add_argument("--allow-network", action="store_true", help="Allow finance provider network calls for this run.")
    parser.add_argument("--enable-browser-assisted", action="store_true", help="Allow the optional browser-assisted provider when the matching env opt-in is also set.")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    ok = audit_storage_policy(ROOT)
    ok = run_goal06c7_provider_ladder_expansion(
        ROOT,
        allow_network=args.allow_network,
        enable_browser_assisted=args.enable_browser_assisted,
    ) and ok
    raise SystemExit(0 if ok else 1)

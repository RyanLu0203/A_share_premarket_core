from __future__ import annotations

import argparse

from _bootstrap import ROOT
from ashare_premarket.providers.browser_provider_events import audit_browser_assisted_provider
from ashare_premarket.providers.provider_ladder import run_goal06c7_provider_ladder_expansion


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run optional browser-assisted finance ingestion under GOAL-06C.7 policy.")
    parser.add_argument("--allow-network", action="store_true", help="Allow finance provider network calls for this run.")
    parser.add_argument("--enable-browser-assisted", action="store_true", help="Enable optional browser-assisted provider only with ASHARE_ENABLE_BROWSER_ASSISTED_PROVIDER=1.")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    ok = run_goal06c7_provider_ladder_expansion(
        ROOT,
        allow_network=args.allow_network,
        enable_browser_assisted=args.enable_browser_assisted,
    )
    ok = audit_browser_assisted_provider(ROOT) and ok
    raise SystemExit(0 if ok else 1)

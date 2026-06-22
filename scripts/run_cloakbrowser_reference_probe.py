from __future__ import annotations

import argparse

from _bootstrap import ROOT
from ashare_premarket.providers.browser_reference_probe import run_browser_reference_probe


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tag provider access failures against an optional CloakBrowser reference probe.")
    parser.add_argument("--allow-network", action="store_true", help="Allow scoped finance-domain browser probes for this run.")
    parser.add_argument("--use-browser", action="store_true", help="Attempt the optional browser runtime if dependencies are installed.")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    raise SystemExit(0 if run_browser_reference_probe(ROOT, allow_network=args.allow_network, use_browser=args.use_browser) else 1)

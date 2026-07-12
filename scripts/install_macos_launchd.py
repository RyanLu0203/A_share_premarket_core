from __future__ import annotations

import argparse

from _bootstrap import ROOT
from ashare_premarket.ops.macos_launchd import install, status, uninstall


def main() -> int:
    parser = argparse.ArgumentParser(description="Install or remove A-Share Premarket macOS LaunchAgents.")
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--run-refresh-now", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    if args.status:
        for label, loaded in status().items():
            print(f"{label}: {'LOADED' if loaded else 'NOT_LOADED'}")
        return 0
    if args.uninstall:
        uninstall()
        print("macOS LaunchAgents removed")
        return 0
    paths = install(ROOT, kickstart_refresh=args.run_refresh_now)
    for path in paths:
        print(f"installed: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

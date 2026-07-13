from __future__ import annotations

import argparse
from pathlib import Path

from ashare_premarket.interfaces.cli.doctor import print_doctor_report


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m ashare_premarket")
    commands = parser.add_subparsers(dest="command", required=True)
    doctor = commands.add_parser("doctor", help="print canonical local interfaces and evidence state")
    doctor.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    doctor.add_argument("--root", type=Path, help="repository root; defaults to the installed source tree")
    args = parser.parse_args()
    if args.command == "doctor":
        print_doctor_report(args.root, as_json=args.json)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())


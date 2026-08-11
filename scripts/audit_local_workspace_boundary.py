#!/usr/bin/env python3
"""Fail closed when duplicate project siblings appear beside this checkout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import ROOT
from ashare_premarket.ops.local_workspace_boundary import (
    audit_local_workspace_boundary,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = audit_local_workspace_boundary(args.repository_root)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

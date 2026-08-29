from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import ROOT
from ashare_premarket.providers.liquidity_external_handoff import (
    LiquidityHandoffError,
    validate_schema_observation_file,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--sha256", required=True)
    args = parser.parse_args()
    try:
        result = validate_schema_observation_file(
            args.bundle,
            expected_sha256=args.sha256,
            repository_root=ROOT,
        )
        print(json.dumps(result, sort_keys=True))
        return 0
    except LiquidityHandoffError as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, sort_keys=True))
        return 1
    except OSError:
        print(json.dumps({"status": "BLOCKED", "reason": "EXTERNAL_FILE_UNAVAILABLE"}, sort_keys=True))
        return 1
    except ValueError:
        print(json.dumps({"status": "BLOCKED", "reason": "INVALID_ARGUMENT"}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

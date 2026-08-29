from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import ROOT
from ashare_premarket.providers.liquidity_external_handoff import (
    LiquidityHandoffError,
    validate_candidate_bundle_file,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--source-class", required=True)
    parser.add_argument("--decision-cutoff", required=True)
    args = parser.parse_args()
    try:
        decision = validate_candidate_bundle_file(
            args.bundle,
            expected_sha256=args.sha256,
            source_class=args.source_class,
            decision_cutoff=args.decision_cutoff,
            repository_root=ROOT,
        )
        result = {
            "status": decision.status,
            "reason": decision.reason,
            "supplied_record_count": decision.supplied_record_count,
            "eligible_symbol_count": decision.eligible_symbol_count,
            "accepted_symbol_count": decision.accepted_symbol_count,
            "invalid_record_count": decision.invalid_record_count,
            "late_record_count": decision.late_record_count,
            "provider_calls_performed": False,
        }
        print(json.dumps(result, sort_keys=True))
        return 0 if decision.status == "PASS" else 1
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

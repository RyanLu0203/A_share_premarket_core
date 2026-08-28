from __future__ import annotations

import json

from _bootstrap import ROOT
from ashare_premarket.validation.public_release import audit_public_release


def main() -> int:
    failures = audit_public_release(ROOT)
    print(
        json.dumps(
            {
                "status": "PASS" if not failures else "BLOCKED",
                "tracked_tree_failures": failures,
                "history_scan_required_before_visibility_change": True,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
